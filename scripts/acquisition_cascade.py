"""HARNESS ACQUISITION CASCADE (V1.0.1): find a trial's arm-level counts through LEGITIMATE OPEN ROUTES ONLY, record
every attempt, and extract deterministically, with each count tagged by its PROVENANCE TIER.

Routes, in order, each attempt appended to evidence/acquisition_cascade/ATTEMPTS.jsonl (route, url, time, status,
bytes, sha256):
  1 unpaywall      the DOI's open-access locations (publisher bronze/gold, repository green); a location is FETCHED once
                   with the lane's own honest User-Agent; a 403/bot-check is recorded as BLOCKED and never retried with a
                   disguised client (no paywall circumvention, no unauthorised mirrors)
  2 europepmc      the paper's own open-access full text (PMC / Europe PMC)
  3 registry       ClinicalTrials.gov posted results (hasResults)
  4 regulatory     FDA / EMA / NICE: a document is used only where one exists for the drug + indication; the search is
                   recorded either way
  5 secondary      OPEN-ACCESS meta-analyses / reviews (Europe PMC OA subset) whose tables tabulate the trial's rows
Held documents: an open-access full text is stored under evidence/acquisition_cascade/held/<id>/ with its sha256.

Extraction (scan): deterministic. For every held document, table rows (and text sentences) that name a target trial's
alias are cut, and every n/N or "n (x%)" pair in them is recorded with the row label and the table's column headings.
A candidate is PRIMARY when the document IS the trial's own report or registry results, SECONDARY_SOURCE when it is a
citing paper (meta-analysis / review) -- recorded with the citing paper, its table and row. Tier and conflicts are
decided in harness.provenance_tiers, never here.
  python scripts/acquisition_cascade.py fetch [--targets <json>]   # network; appends attempts, stores held docs
  python scripts/acquisition_cascade.py scan  [--targets <json>]   # offline; writes CANDIDATES.json
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "evidence", "acquisition_cascade")
HELD = os.path.join(D, "held")
ATTEMPTS = os.path.join(D, "ATTEMPTS.jsonl")
UA = "meta-harness-evidence-lane/1 (acquisition cascade; mailto:mahmood726@gmail.com)"
# bot checks: recorded as BLOCKED_CHALLENGE_PAGE and never solved or worked around (PMC's file links answer 200 with a
# proof-of-work page, 'POW_CHALLENGE'; that is a block, not a document)
CHALLENGE = (b"Just a moment", b"Performing security verification", b"cf-challenge", b"captcha", b"Access Denied",
             b"POW_CHALLENGE", b"Preparing to download ...")


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class NonPublicHost(Exception):
    pass


def _public_url(url):
    """True only for an http(s) URL whose host is a public name or a global IP literal. URLs arrive from REMOTE
    metadata (Unpaywall locations, a repository's citation_pdf_url: one advertised http://localhost:4000/...), so a
    loopback / private / link-local / reserved address or a local name is never requested."""
    import ipaddress
    try:
        p = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    host = (p.hostname or "").rstrip(".").lower()
    if p.scheme not in ("http", "https") or not host:
        return False
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".lan", ".home.arpa")) or "." not in host.strip("[]"):
        try:
            ipaddress.ip_address(host.strip("[]"))
        except ValueError:
            return False
    try:
        return ipaddress.ip_address(host.strip("[]")).is_global
    except ValueError:
        return True


class _PublicOnlyRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _public_url(newurl):
            raise NonPublicHost(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _open(req, timeout):
    return urllib.request.build_opener(_PublicOnlyRedirect).open(req, timeout=timeout)


def _get(url, accept=None):
    """One honest request. Returns (status, bytes). Never retried with another client identity."""
    if not _public_url(url):
        return "REFUSED_NONPUBLIC_HOST", b""
    headers = {"User-Agent": UA}
    if accept:
        headers["Accept"] = accept
    try:
        with _open(urllib.request.Request(url, headers=headers), timeout=90) as r:
            body = r.read()
            if any(c.lower() in body[:20000].lower() for c in CHALLENGE):
                return "BLOCKED_CHALLENGE_PAGE", b""
            return r.status, body
    except urllib.error.HTTPError as e:
        return (f"BLOCKED_HTTP_{e.code}" if e.code in (401, 402, 403, 429, 451) else e.code), b""
    except NonPublicHost:
        return "REFUSED_NONPUBLIC_HOST", b""
    except Exception as e:  # noqa: BLE001
        return f"ERROR {type(e).__name__}", b""


def _record(route, target, url, status, body, note=""):
    os.makedirs(D, exist_ok=True)
    url = re.sub(r"([?&]email=)[^&]+", r"\1<contact>", url)      # the contact address is not part of the record
    row = {"route": route, "target": target, "url": url, "time_utc": _now(), "status": status,
           "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest() if body else None, **({"note": note} if note else {})}
    with open(ATTEMPTS, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def _hold(rel, body, meta):
    p = os.path.join(HELD, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    digest = hashlib.sha256(body).hexdigest()
    if os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() != digest:
        # written once, never overwritten: a LATER, different response (a live API record whose citation counts moved)
        # is held beside it under its own content address; both stay in the ledger
        stem, ext = os.path.splitext(rel)
        rel = f"{stem}.{digest[:12]}{ext}"
        p = os.path.join(HELD, rel)
    open(p, "wb").write(body)
    led = os.path.join(HELD, "HELD.json")
    ledger = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
    # the ORIGINAL retrieved bytes, held verbatim: their hash, source and retrieval time (excerpts are separate files)
    ledger[rel] = {**meta, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body), "retrieved_utc": _now(),
                   "representation": "ORIGINAL_VERBATIM"}
    json.dump(ledger, open(led, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, ensure_ascii=False)


# ------------------------------------------------------------------------------------------------ routes
def route_unpaywall(t):
    doi = t.get("doi")
    if not doi:
        return
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email=mahmood726@gmail.com"
    st, b = _get(url)
    _record("unpaywall", t["trial"], url, st, b)
    locs = (json.loads(b).get("oa_locations") or []) if b else []
    for loc in locs:
        for u in [loc.get("url_for_pdf"), loc.get("url")]:
            if not u:
                continue
            st2, b2 = _get(u)
            _record("unpaywall_location", t["trial"], u, st2, b2,
                    note=f"host_type={loc.get('host_type')} licence={loc.get('license')} version={loc.get('version')}")
            if b2 and (b2.startswith(b"%PDF") or b"<article" in b2[:5000]):
                ext = ".pdf" if b2.startswith(b"%PDF") else ".xml"
                _hold(f"{t['trial']}/unpaywall{ext}", b2, {"source": u, "route": "unpaywall", "licence": loc.get("license"),
                                                           "tier_document": "PRIMARY", "trial": t["trial"]})
                return
            # a free full-text HTML page on PMC (the NIH host) is the article itself: held as served
            # (only a page that IS the article: it carries the article's citation_title meta; an interstitial does not)
            if (b2 and re.match(r"https?://(www\.ncbi\.nlm\.nih\.gov/pmc|pmc\.ncbi\.nlm\.nih\.gov)/", u)
                    and b'name="citation_title"' in b2):
                _hold(f"{t['trial']}/pmc_article.html", b2, {"source": u, "route": "unpaywall_pmc_html",
                                                             "licence": loc.get("license"), "tier_document": "PRIMARY",
                                                             "trial": t["trial"], "what": "PMC full-text HTML page"})
            # a repository landing page names its own PDF in the standard citation_pdf_url meta tag: followed ONCE
            elif b2 and loc.get("host_type") == "repository":
                m = re.search(rb'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)', b2, re.I)
                if m:
                    pu = html.unescape(m.group(1).decode("utf-8", "replace"))
                    st3, b3 = _get(pu)
                    _record("repository_pdf", t["trial"], pu, st3, b3, note=f"citation_pdf_url of {u}; licence={loc.get('license')}")
                    if b3 and b3.startswith(b"%PDF"):
                        _hold(f"{t['trial']}/repository.pdf", b3, {"source": pu, "route": "repository_pdf",
                                                                   "licence": loc.get("license"), "tier_document": "PRIMARY",
                                                                   "trial": t["trial"], "what": f"repository copy ({loc.get('version')})"})
                        return


def route_europepmc(t):
    pid, doi = t.get("pmid"), t.get("doi")
    if not (pid or doi):
        return None
    q = f"EXT_ID:{pid} AND SRC:MED" if pid else f'DOI:"{doi}"'
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=core&query="
           + urllib.parse.quote(q))
    st, b = _get(url)
    r = ((json.loads(b).get("resultList") or {}).get("result") or [{}])[0] if b else {}
    # a report known only by DOI is resolved to its PMID here, and the resolution is part of the record
    _record("europepmc_record", t["trial"], url, st, b,
            note=f"resolved pmid={r.get('pmid')} pmcid={r.get('pmcid')} title={(r.get('title') or '')[:160]}")
    if b and r.get("pmid"):
        _hold(f"{t['trial']}/europepmc_record_{r['pmid']}.json", b,
              {"source": url, "route": "europepmc_record", "tier_document": "PRIMARY", "trial": t["trial"],
               "what": "bibliographic record + abstract (not full text)"})
    if r.get("pmcid") and r.get("isOpenAccess") == "Y":
        u = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{r['pmcid']}/fullTextXML"
        st2, b2 = _get(u)
        _record("europepmc_fulltext", t["trial"], u, st2, b2)
        if b2 and b"<article" in b2[:5000]:
            _hold(f"{t['trial']}/{r['pmcid']}.xml", b2, {"source": u, "route": "europepmc", "tier_document": "PRIMARY",
                                                        "trial": t["trial"]})
    else:
        _record("europepmc_fulltext", t["trial"], url, "NOT_OPEN_ACCESS", b"",
                note=f"pmcid={r.get('pmcid')} isOpenAccess={r.get('isOpenAccess')}")
    return r


def route_discover(t, query):
    """A report known only by description (a platform domain's report, a trial paper whose PMID is not in the cache):
    one recorded Europe PMC search; the hits are LISTED in the record (pmid, doi, title, OA flag), nothing is held
    and nothing is chosen here -- a hit becomes a report only when a declaration names it."""
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&resultType=lite&pageSize=25&query="
           + urllib.parse.quote(query))
    st, b = _get(url)
    hits = ((json.loads(b).get("resultList") or {}).get("result") or []) if b else []
    _record("discover", t["trial"], url, st, b, note=" || ".join(
        f"{h.get('pmid')}|{h.get('doi')}|{h.get('pubYear')}|OA={h.get('isOpenAccess')}|{(h.get('title') or '')[:110]}"
        for h in hits[:12]))
    return hits


def route_supplements(t, pmcid):
    """Supplementary material of an OPEN-ACCESS article (Europe PMC supplementaryFiles, a zip of the deposited files).
    The protocol-preferred analysis is sometimes only there (METCOVID: ITT-as-randomised in Supplementary Table 2)."""
    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/supplementaryFiles"
    st, b = _get(url)
    _record("supplements", t["trial"], url, st, b, note=f"pmcid={pmcid}")
    if b and b[:2] == b"PK":
        _hold(f"{t['trial']}/{pmcid}_supplementary.zip", b, {"source": url, "route": "supplements",
                                                              "tier_document": "PRIMARY", "trial": t["trial"],
                                                              "what": "supplementary files (zip)"})
    return st, b


def route_pmc_bin_supplements(t):
    """Supplements linked from a HELD PMC article page (its own /bin/ files on the NIH host), each fetched once. This is
    where a protocol-preferred analysis or a period-specific result often sits (COVIDICUS eTables in Supplement 2)."""
    page = os.path.join(HELD, t["trial"], "pmc_article.html")
    if not os.path.exists(page):
        return
    b = open(page, "rb").read()
    base = re.search(rb'<link rel="canonical" href="(https://[^"]+)"', b)
    pmcid = re.search(rb"/articles/(?:instance/)?(?:PMC)?(\d{6,8})", b)
    for href in sorted({m.decode() for m in re.findall(rb'href="(/articles/instance/\d+/bin/[^"]+)"', b)}):
        u = "https://pmc.ncbi.nlm.nih.gov" + href
        st, body = _get(u)
        _record("pmc_bin_supplement", t["trial"], u, st, body, note=f"linked from the held PMC page {t['trial']}/pmc_article.html")
        if body and (body.startswith(b"%PDF") or body[:2] == b"PK"):
            _hold(f"{t['trial']}/supplement_{os.path.basename(href)}", body,
                  {"source": u, "route": "pmc_bin_supplement", "tier_document": "PRIMARY", "trial": t["trial"],
                   "what": "supplementary file linked from the PMC article page"})
    return base, pmcid


def route_registry(t):
    nct = t.get("nct")
    if not nct:
        return
    url = f"https://clinicaltrials.gov/api/v2/studies/{nct}"
    st, b = _get(url)
    has = json.loads(b).get("hasResults") if b else None
    # a SCREENING target (hold_registration) holds the registration itself even with no posted results: for a trial
    # missing from the inventory, its design, arms, dates and status ARE the evidence (FIVE-STAR, CONFIDENCE)
    keep = bool(b) and (has or t.get("hold_registration"))
    _record("registry_results", t["trial"], url, st if keep else ("NO_POSTED_RESULTS" if b else st), b if keep else b"",
            note=f"hasResults={has}" + ("; held as the registration record" if keep and not has else ""))
    if keep:
        _hold(f"{t['trial']}/{nct}.json", b, {"source": url, "route": "registry", "tier_document": "PRIMARY", "trial": t["trial"],
                                             **({} if has else {"what": "registration record (no posted results)"})})


def route_regulatory(t, drug, indication):
    """Recorded searches; a regulatory document is used only where one exists for this drug + indication."""
    for name, url in (("fda_label_search", "https://api.fda.gov/drug/label.json?search="
                       + urllib.parse.quote(f'openfda.generic_name:"{drug}" AND indications_and_usage:"{indication}"') + "&limit=5"),
                      ("ema_search", "https://www.ema.europa.eu/en/search?search_api_fulltext="
                       + urllib.parse.quote(f"{drug} {indication}")),
                      ("nice_search", "https://www.nice.org.uk/search?q=" + urllib.parse.quote(f"{drug} {indication}"))):
        st, b = _get(url)
        hits = None
        if name == "fda_label_search" and b:
            try:
                hits = len(json.loads(b).get("results") or [])
            except ValueError:
                hits = None
        _record(name, t["trial"], url, st, b, note=f"results={hits}" if hits is not None else
                "search page recorded; no trial-level tabulation is taken from a search page")


def route_secondary(t, query, pmcids_seen):
    url = ("https://www.ebi.ac.uk/europepmc/webservices/rest/search?format=json&pageSize=40&resultType=lite&query="
           + urllib.parse.quote(query))
    st, b = _get(url)
    _record("secondary_search", t["trial"], url, st, b, note=query)
    for r in ((json.loads(b).get("resultList") or {}).get("result") or []) if b else []:
        pmc = r.get("pmcid")
        if not pmc or pmc in pmcids_seen:
            continue
        pmcids_seen.add(pmc)
        u = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
        st2, b2 = _get(u)
        _record("secondary_fulltext", t["trial"], u, st2, b2, note=(r.get("title") or "")[:120])
        if b2 and b"<article" in b2[:5000]:
            _hold(f"_secondary/{pmc}.xml", b2, {"source": u, "route": "secondary", "tier_document": "SECONDARY_SOURCE",
                                                "citing_pmid": r.get("pmid"), "title": r.get("title")})
        time.sleep(0.3)


# ------------------------------------------------------------------------------------------------ scan (offline)
_PAIR = re.compile(r"(?<![\d.])(\d{1,4})\s*/\s*(\d{1,4})(?![\d.])|(?<![\d.])(\d{1,4})\s*\(\s*(\d{1,3}(?:[.·]\d+)?)\s*%\s*\)")


def _cells(tr):
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
            for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]


def scan_document(rel, meta, targets):
    """Candidate rows: every table row (with its table label, caption and header cells) and text sentence that names
    a target trial's alias and carries a count pair."""
    p = os.path.join(HELD, rel)
    raw = open(p, "rb").read()
    if not raw.lstrip().startswith(b"<"):
        return []                                             # PDFs are recorded but not parsed here
    t = raw.decode("utf-8", "replace")
    out = []
    for tw in re.findall(r"<table-wrap[^>]*>.*?</table-wrap>", t, re.S):
        label = re.sub(r"<[^>]+>", "", (re.findall(r"<label>(.*?)</label>", tw, re.S) or [""])[0]).strip()
        caption = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", (re.findall(r"<caption>(.*?)</caption>", tw, re.S) or [""])[0]))).strip()
        rows = [_cells(r) for r in re.findall(r"<tr[^>]*>(.*?)</tr>", tw, re.S)]
        header = rows[0] if rows else []
        for cells in rows[1:]:
            line = " | ".join(cells)
            for tg in targets:
                if any(re.search(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z-])", line) for a in tg["aliases"]):
                    pairs = [m.group(0) for m in _PAIR.finditer(line)]
                    # separate-column layout: 'Imazio 2013 | 11 | 120 | 25 | 120' under Events/Total headings
                    hdr = " ".join(header).lower()
                    if not pairs and re.search(r"event|total|\bn\b|patients", hdr):
                        ints = [c for c in cells if re.fullmatch(r"\d{1,4}", c)]
                        if len(ints) >= 2:
                            pairs = ["COLUMNS:" + "|".join(ints)]
                    if pairs:
                        out.append({"document": rel, "document_sha256": hashlib.sha256(raw).hexdigest(),
                                    "tier": meta.get("tier_document"), "citing_pmid": meta.get("citing_pmid"),
                                    "trial": tg["trial"], "where": "table", "table": label, "caption": caption[:200],
                                    "column_headings": header, "row": cells, "pairs": pairs})
    body = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<(ref-list|table-wrap)\b.*?</\1>", " ", t, flags=re.S)))
    for sent in re.split(r"(?<=[.;])\s+", re.sub(r"\s+", " ", body)):
        for tg in targets:
            if any(re.search(r"(?<![A-Za-z])" + re.escape(a) + r"(?![A-Za-z-])", sent) for a in tg["aliases"]):
                pairs = [m.group(0) for m in _PAIR.finditer(sent)]
                if pairs:
                    out.append({"document": rel, "document_sha256": hashlib.sha256(raw).hexdigest(),
                                "tier": meta.get("tier_document"), "citing_pmid": meta.get("citing_pmid"),
                                "trial": tg["trial"], "where": "text", "sentence": sent[:600], "pairs": pairs})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=("fetch", "scan"))
    ap.add_argument("--targets", default=os.path.join(D, "targets.json"))
    ap.add_argument("--only", default=None, help="comma-separated trial labels to fetch")
    a = ap.parse_args(argv)
    default_targets = os.path.abspath(a.targets) == os.path.abspath(os.path.join(D, "targets.json"))
    spec = json.load(open(a.targets, encoding="utf-8"))
    trials = spec["trials"]
    if a.mode == "fetch":
        seen = set()
        only = set(a.only.split(",")) if a.only else None
        for t in trials:
            if only and t["trial"] not in only:
                continue
            for q in t.get("discovery_queries") or []:
                route_discover(t, q)
            run_start = _now()
            route_unpaywall(t)
            epmc = route_europepmc(t) or {}
            # SOURCE IDENTITY (2026-09-28): a DOI that is not the PMID's own DOI names ANOTHER publication (EMPERIAL:
            # a DOI typed from memory made Unpaywall hand over a different paper's PMC page). Recorded, and every file
            # the DOI route held for this target in this run is QUARANTINED in the ledger -- never used.
            if t.get("doi") and epmc.get("doi") and t["doi"].lower() != str(epmc["doi"]).lower():
                _record("identity_check", t["trial"], f"doi:{t['doi']}", "IDENTITY_MISMATCH", b"",
                        note=f"target DOI {t['doi']} is not PMID {epmc.get('pmid')}'s DOI {epmc.get('doi')}")
                led = os.path.join(HELD, "HELD.json")
                ledger = json.load(open(led, encoding="utf-8")) if os.path.exists(led) else {}
                for rel, meta in ledger.items():
                    if (rel.startswith(t["trial"] + "/") and meta.get("route", "").startswith(("unpaywall", "repository"))
                            and str(meta.get("retrieved_utc", "")) >= run_start):
                        meta["identity_quarantine"] = (f"held via DOI {t['doi']}, which is not PMID {epmc.get('pmid')}'s "
                                                       f"DOI {epmc.get('doi')}: another publication; never used")
                json.dump(ledger, open(led, "w", encoding="utf-8", newline="\n"), indent=1, sort_keys=True, ensure_ascii=False)
            # SUPPLEMENTS BY DEFAULT (sacubitril-HFrEF, 2026-09-28): LIFE's clinical outcomes are only in its
            # supplement, and this route used to run only when a target opted in AND the article was open access --
            # so no attempt was made or recorded. Now: whenever a PMCID is known (from Europe PMC, or declared on the
            # target when Europe PMC answers 503), the supplement route is attempted; a response with no archive is
            # recorded as SUPPLEMENT_NOT_HELD with its reason, never skipped in silence.
            pmcid = epmc.get("pmcid") or t.get("pmcid")
            if pmcid and not t.get("no_supplements"):
                _st, _b = route_supplements(t, pmcid)
                if not (_b and _b[:2] == b"PK"):
                    _record("supplements_state", t["trial"], f"pmcid:{pmcid}", "SUPPLEMENT_NOT_HELD", b"",
                            note=(f"supplementaryFiles answered {_st} with {len(_b or b'')} bytes and no archive "
                                  f"(isOpenAccess={epmc.get('isOpenAccess')}); the PMC article page itself is "
                                  "needed for its /bin/ files (route_pmc_bin_supplements)"))
            if not t.get("no_supplements"):
                route_pmc_bin_supplements(t)
            route_registry(t)
            if not spec.get("skip_regulatory"):
                route_regulatory(t, spec["drug"], spec["indication"])
            # further reports of the SAME trial (a longer follow-up, a companion): fetched as that trial's reports,
            # held under the trial, never a second trial
            for rep in t.get("reports") or []:
                # '__', never '#': '#' is the fragment separator of a document reference (records.json#PMID-...),
                # so a held path containing it is cut short where it is cited
                rt = {**rep, "trial": f"{t['trial']}__{rep['report_label']}"}
                route_unpaywall(rt)
                route_europepmc(rt)
            for q in spec.get("secondary_queries") or []:
                route_secondary(t, q, seen)
        print("attempts ->", os.path.relpath(ATTEMPTS, ROOT))
        return 0
    ledger = json.load(open(os.path.join(HELD, "HELD.json"), encoding="utf-8")) if os.path.exists(os.path.join(HELD, "HELD.json")) else {}
    cands = []
    for rel, meta in sorted(ledger.items()):
        cands += scan_document(rel, meta, trials)
    # PRIMARY: each trial's OWN abstract, already committed in the topic cache (the trial's own report)
    rec_path = os.path.join(ROOT, "cache", spec["topic"], "records.json")
    raw = open(rec_path, "rb").read()
    recs = {str(r.get("id")): r for r in json.loads(raw.decode("utf-8")).get("records") or []}
    for t in trials:
        r = recs.get(str(t.get("pmid")))
        if not r:
            continue
        for sent in re.split(r"(?<=[.;])\s+", re.sub(r"\s+", " ", (r.get("title") or "") + ". " + (r.get("abstract") or ""))):
            if _PAIR.search(sent) or re.search(r"\d+\s*\(\s*\d", sent):
                cands.append({"document": f"cache/{spec['topic']}/records.json#PMID-{t['pmid']}",
                              "document_sha256": hashlib.sha256(raw).hexdigest(), "tier": "PRIMARY",
                              "trial": t["trial"], "where": "text", "sentence": sent[:600],
                              "pairs": [m.group(0) for m in _PAIR.finditer(sent)]})
    json.dump({"generated_utc": _now(), "documents_scanned": len(ledger), "candidates": cands},
              open(os.path.join(D, "CANDIDATES.json" if default_targets else f"CANDIDATES.{spec['topic']}.json"), "w",
                   encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    print(f"scanned {len(ledger)} held documents; {len(cands)} candidate rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
