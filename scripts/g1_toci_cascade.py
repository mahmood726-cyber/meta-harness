"""G1 tocilizumab: the ACQUISITION CASCADE run and LOGGED per trial, so 'no open primary source held' is a measured
result, never an assumption. Lane-side runner (the shared cascade, harness/fetch.py, is the Captain lane's; defects
found here are reported, not patched there).

Per trial (REACT's 19 labels):
  discovery  D1 AACT study_references (RESULT/DERIVED) by NCT   D2 PubMed secondary-id by NCT and by every registry id
             AACT id_information holds (ISRCTN, EudraCT, CTRI ...)   D3 Europe PMC full-text search for the NCT
             D4 the trial's name in title/abstract (trials with no AACT registration only)
  per candidate report (a primary report: names tocilizumab / IL-6; not a review, protocol, comment or meta-analysis)
             R1 PMC           NCBI idconv (pmc.ncbi.nlm.nih.gov) -> PMCID -> efetch db=pmc JATS -> licence, body
             R2 Europe PMC    core record (isOpenAccess, licence, PMCID) -> fullTextXML when open
             R3 Unpaywall     DOI -> is_oa, best OA location (host, licence, version); LOCATED, never fetched here
  per trial  R4 AACT          posted results (local snapshot 2026-08-30): outcomes naming death/mortality + time frame
             R5 ISRCTN        registry record by ISRCTN id (from AACT id_information): results / publication links
             R6 preprints     Europe PMC SRC:PPR by registration; a candidate (the drug in its title, and the trial named or
                              a randomised comparison) is read through api.biorxiv.org: SUPERSEDED when the server records
                              its published version, else its JATS under the licence the bytes state, held only when it
                              states day-28 deaths (python scripts/g1_toci_cascade.py --preprints)
A full text is HELD (committed, g1/data/acquired/<pmid>.json) only under an open licence; otherwise it is recorded
VERIFIED_NOT_HELD with its PMCID and body sha256. Every rung's request and outcome go to g1/data/cascade/<label>.json.

  python scripts/g1_toci_cascade.py --aact          rebuild g1/data/cascade/aact_refs.json from the local snapshot
  python scripts/g1_toci_cascade.py --net [LABEL..] run the online rungs and write the logs (+ acquired texts)
  python scripts/g1_toci_cascade.py                 summarise the logs -> g1/data/cascade/CASCADE.md
"""
import csv
import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from g1 import tocilizumab as g  # noqa: E402

CAS = os.path.join(ROOT, "g1", "data", "cascade")
ACQ = os.path.join(ROOT, "g1", "data", "acquired")
AACT_REFS = os.path.join(CAS, "aact_refs.json")
EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
IDCONV = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
ISRCTN = "https://www.isrctn.com/api/query/format/default"
UA = {"User-Agent": "meta-harness-g1/1.0"}
OPEN = re.compile(r"creativecommons\.org/(?:licenses|publicdomain)|^cc[ -]?by|^cc0|ccby|public domain", re.I)
DRUG = re.compile(r"tocilizumab|interleukin[- ]?6|\bIL-?6\b|anti-IL", re.I)
NOT_PRIMARY = re.compile(r"\b(?:review|meta-analys|protocol|statistical analysis plan|rationale and design|comment|"
                         r"editorial|letter|reply|correspondence|cost-effective|economic)", re.I)
NAME_ONLY = {"COVINTOC": "COVINTOC[tiab] AND tocilizumab[tiab]", "PreToVid": "PreToVid[tiab]"}


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, params=None, tries=5):
    u = url + ("?" + urllib.parse.urlencode(params) if params else "")
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r:
                return r.status, r.read(), u
        except urllib.error.HTTPError as e:
            # 429/503 are the service throttling, not an answer: back off (Retry-After when given) and retry; the
            # first cascade run logged 429s from idconv as 'unparseable' -- a failed rung, never 'not in PMC'
            if e.code in (429, 503) and i < tries - 1:
                time.sleep(float(e.headers.get("Retry-After") or 0) or 3 * (i + 1) ** 2)
                last = e
                continue
            return e.code, e.read() or b"", u
        except Exception as exc:  # noqa: BLE001 -- retried, then reported as the rung's outcome
            last = exc
            time.sleep(2 * (i + 1))
    return None, f"{type(last).__name__}: {last}".encode(), u


# ------------------------------------------------------------------ AACT (local snapshot)

def build_aact():
    from kgap import aact_adapter as a
    d = a.snapshot_dir()
    ncts = {v[0] for v in g.IDENTITY.values() if v[0]}
    out = {n: {"ids": [], "refs": [], "outcomes": [], "results_first_posted": None} for n in ncts}
    csv.field_size_limit(10 ** 8)

    def rows(name):
        with open(os.path.join(d, name), encoding="utf-8", errors="replace", newline="") as fh:
            for r in csv.DictReader(fh, delimiter="|", quoting=csv.QUOTE_NONE):
                if r.get("nct_id") in ncts:
                    yield r
    for r in rows("id_information.txt"):
        out[r["nct_id"]]["ids"].append({k: r[k] for k in ("id_source", "id_value", "id_type")})
    for r in rows("study_references.txt"):
        out[r["nct_id"]]["refs"].append({"pmid": r["pmid"], "type": r["reference_type"], "citation": r["citation"][:200]})
    for r in rows("outcomes.txt"):
        t = (r.get("title") or "") + " " + (r.get("description") or "")
        if g._DEATH_WORDS.search(t):
            out[r["nct_id"]]["outcomes"].append({"id": r["id"], "type": r.get("outcome_type"), "title": r["title"][:200],
                                                 "time_frame": (r.get("time_frame") or "")[:200]})
    for r in rows("studies.txt"):
        out[r["nct_id"]]["results_first_posted"] = r.get("results_first_posted_date") or None
    snap = a.snapshot()
    json.dump({"snapshot": snap["id"], "digest": snap["digest"], "ncts": out},
              open(AACT_REFS, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False, sort_keys=True)


# ------------------------------------------------------------------ discovery

def esearch(term):
    st, b, u = get(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", "retmode": "json", "retmax": 30, "term": term})
    time.sleep(0.35)
    try:
        return json.loads(b)["esearchresult"]["idlist"], {"rung": "PubMed esearch", "request": u, "http": st}
    except Exception:  # noqa: BLE001
        return [], {"rung": "PubMed esearch", "request": u, "http": st, "error": b[:200].decode("utf-8", "replace")}


def epmc_fulltext_search(nct):
    q = f'"{nct}" AND (tocilizumab OR "interleukin-6" OR "IL-6") AND SRC:MED'
    st, b, u = get(f"{EPMC}/search", {"query": q, "format": "json", "pageSize": 50, "resultType": "lite"})
    try:
        res = (json.loads(b).get("resultList") or {}).get("result") or []
        return [r["pmid"] for r in res if r.get("pmid")], {"rung": "Europe PMC search", "request": u, "http": st,
                                                            "hit_count": json.loads(b).get("hitCount"),
                                                            "page_size": 50}
    except Exception:  # noqa: BLE001
        return [], {"rung": "Europe PMC search", "request": u, "http": st, "error": b[:200].decode("utf-8", "replace")}


def efetch_meta(pmids):
    if not pmids:
        return {}
    st, b, _ = get(f"{EUTILS}/efetch.fcgi", {"db": "pubmed", "retmode": "xml", "id": ",".join(pmids)})
    time.sleep(0.35)
    out = {}
    for art in re.findall(r"<PubmedArticle>.*?</PubmedArticle>", b.decode("utf-8", "replace"), re.S):
        pm = re.search(r"<PMID[^>]*>(\d+)", art).group(1)
        t = lambda tag: re.sub(r"<[^>]+>", "", " ".join(re.findall(rf"<{tag}[^>]*>(.*?)</{tag}>", art, re.S)))  # noqa: E731
        doi = re.search(r'<ArticleId IdType="doi">([^<]+)', art)
        out[pm] = {"title": t("ArticleTitle"), "abstract": t("AbstractText"), "pub_types":
                   re.findall(r"<PublicationType[^>]*>([^<]+)", art), "doi": doi.group(1) if doi else None,
                   "year": (re.search(r"<PubDate>.*?<Year>(\d{4})", art, re.S) or [None, None])[1]}
    return out


def is_primary_report(m):
    kinds = " ".join(m.get("pub_types") or []) + " " + (m.get("title") or "")
    return bool(DRUG.search((m.get("title") or "") + " " + (m.get("abstract") or ""))) and not NOT_PRIMARY.search(kinds)


# ------------------------------------------------------------------ rungs per candidate

def rung_pmc(pmid):
    st, b, u = get(IDCONV, {"ids": pmid, "format": "json", "tool": "meta-harness-g1"})
    log = {"rung": "R1 PMC", "idconv": u, "idconv_http": st}
    if st != 200:          # an error body (even valid JSON) is a FAILED rung, never 'not in PMC' (codex cascade#7)
        log["outcome"] = f"RUNG_FAILED: idconv http {st}"
        return log, None
    try:
        rec = (json.loads(b).get("records") or [{}])[0]
    except Exception:  # noqa: BLE001
        log["outcome"] = f"RUNG_FAILED: idconv http {st}" + (" (rate limited after retries)" if st == 429 else "")
        return log, None
    time.sleep(0.4)
    pmcid = rec.get("pmcid")
    log["pmcid"] = pmcid
    if not pmcid:
        log["outcome"] = "NOT_IN_PMC"
        return log, None
    st, b, u = get(f"{EUTILS}/efetch.fcgi", {"db": "pmc", "id": pmcid.replace("PMC", ""), "retmode": "xml"})
    time.sleep(0.35)
    x = b.decode("utf-8", "replace")
    lic = re.search(r"<license[^>]*>.*?</license>", x, re.S)
    lic_s = re.sub(r"\s+", " ", lic.group(0))[:300] if lic else ""
    href = re.search(r'(?:xlink:href|>)\s*(https?://creativecommons\.org/[^"<\s]+)', lic_s)
    body = "<body" in x
    log.update(efetch=u, efetch_http=st, has_body=body, licence=(href.group(1) if href else
                                                                 re.sub(r"<[^>]+>", " ", lic_s).strip()[:160] or None))
    if not body:
        log["outcome"] = "IN_PMC_NO_BODY (publisher withholds XML full text)"
        return log, None
    open_ = bool(lic and OPEN.search(lic_s))
    log["outcome"] = "OPEN_FULL_TEXT" if open_ else "FULL_TEXT_NOT_OPEN_LICENCE"
    log["body_sha256"] = hashlib.sha256(b).hexdigest()
    return log, (x if open_ else None)


def rung_epmc(pmid):
    st, b, u = get(f"{EPMC}/search", {"query": f"EXT_ID:{pmid} AND SRC:MED", "resultType": "core", "format": "json"})
    log = {"rung": "R2 Europe PMC", "request": u, "http": st}
    if st != 200:
        log["outcome"] = f"RUNG_FAILED: http {st}"
        return log, None
    try:
        h = ((json.loads(b).get("resultList") or {}).get("result") or [{}])[0]
    except Exception:  # noqa: BLE001
        log["outcome"] = "UNPARSEABLE"
        return log, None
    log.update(pmcid=h.get("pmcid"), is_open_access=h.get("isOpenAccess"), licence=h.get("license"),
               in_epmc=h.get("inEPMC"), in_pmc=h.get("inPMC"))
    if not h.get("pmcid"):
        log["outcome"] = "NO_FULL_TEXT_IN_EPMC"
        return log, None
    if h.get("isOpenAccess") != "Y":
        log["outcome"] = "FULL_TEXT_NOT_OPEN_ACCESS"
        return log, None
    st, b, u = get(f"{EPMC}/{h['pmcid']}/fullTextXML")
    log.update(fulltext_request=u, fulltext_http=st)
    if st != 200 or b"<body" not in b:
        log["outcome"] = f"FULLTEXT_FETCH_FAILED http={st}"
        return log, None
    log["body_sha256"] = hashlib.sha256(b).hexdigest()
    # the licence the HELD BYTES state decides, not the index's metadata: COVIDSTORM's Europe PMC record says 'cc by'
    # while the XML it serves carries Elsevier's COVID-19 resource-centre permission (not an open licence)
    own = bytes_licence(b.decode("utf-8", "replace"))
    log["licence_in_bytes"] = own
    open_ = bool(OPEN.search(h.get("license") or "")) and (own is None or bool(OPEN.search(own)))
    log["outcome"] = ("OPEN_FULL_TEXT" if open_ else "FULL_TEXT_OA_BUT_LICENCE_IN_BYTES_NOT_OPEN"
                      if OPEN.search(h.get("license") or "") else "FULL_TEXT_OA_BUT_LICENCE_NOT_OPEN")
    return log, (b.decode("utf-8", "replace") if open_ else None)


def bytes_licence(x):
    """The licence statement inside a JATS document (<license> href or text), or None when it states none."""
    m = re.search(r"<license[^>]*>.*?</license>", x, re.S)
    if not m:
        return None
    href = re.search(r"https?://creativecommons\.org/[^\"<\s]+", m.group(0))
    return href.group(0) if href else re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(0))).strip()[:200]


def licence_audit():
    """Offline: every held full text must state an open licence IN ITS OWN BYTES (or state none and carry an open
    metadata licence). One that does not is stripped to VERIFIED_NOT_HELD (PMCID + body sha256) and never committed."""
    out = []
    for f in sorted(os.listdir(ACQ)):
        if not re.match(r"(?:\d+|PPR\d+)\.json$", f):       # PubMed ids and Europe PMC preprint ids (cascade#6)
            continue
        fp = os.path.join(ACQ, f)
        a = json.load(open(fp, encoding="utf-8"))
        if not a.get("fulltext"):
            continue
        own = bytes_licence(a["fulltext"])
        if (own is not None and not OPEN.search(own)) or (own is None and not OPEN.search(a.get("license") or "")):
            sha = hashlib.sha256(a.pop("fulltext").encode("utf-8")).hexdigest()
            a.update(fulltext_state="VERIFIED_NOT_HELD (licence stated in the held bytes is not open: "
                                    + (own or a.get("license") or "none")[:80] + ")", fulltext_sha256=sha)
            open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(a, indent=1, ensure_ascii=False) + "\n")
            out.append(a["pmid"])
    return out


def rung_unpaywall(doi):
    log = {"rung": "R3 Unpaywall", "doi": doi}
    if not doi:
        log["outcome"] = "NO_DOI"
        return log
    from kgap import k_gap
    st, b, u = get("https://api.unpaywall.org/v2/" + urllib.parse.quote(doi, safe=""), {"email": k_gap.UPW_CONTACT})
    log.update(http=st)
    try:
        d = json.loads(b)
    except Exception:  # noqa: BLE001
        log["outcome"] = "UNPARSEABLE"
        return log
    bl = d.get("best_oa_location") or {}
    log.update(is_oa=d.get("is_oa"), oa_status=d.get("oa_status"), host=bl.get("host_type"), licence=bl.get("license"),
               version=bl.get("version"), url=bl.get("url_for_landing_page") or bl.get("url"),
               n_oa_locations=len(d.get("oa_locations") or []))
    log["outcome"] = "OA_LOCATED_NOT_FETCHED" if d.get("is_oa") else "NOT_OA"
    return log


def rung_aact(nct, A):
    e = (A["ncts"].get(nct) or {}) if nct else {}
    log = {"rung": "R4 AACT", "snapshot": A["snapshot"], "nct": nct}
    if not nct:
        log["outcome"] = "NO_AACT_REGISTRATION"
        return log
    oc = e.get("outcomes") or []
    d28 = [o for o in oc if g._DAY28.search(o["title"] + " " + o["time_frame"])]
    # a composite ('Mechanical Ventilation or Death', 'High-flow Oxygen ... or Death') is not a mortality outcome
    pure = [o for o in d28 if not g._OTHER_EVENT.search(o["title"])]
    log.update(results_first_posted=e.get("results_first_posted"), death_outcomes=oc, day28_death_only=pure,
               day28_composites=[o for o in d28 if o not in pure])
    log["outcome"] = ("NO_POSTED_RESULTS" if not e.get("results_first_posted") else
                      "POSTED_DAY28_DEATH_OUTCOME" if pure else
                      "POSTED_DAY28_COMPOSITES_ONLY" if d28 else "POSTED_NO_DAY28_DEATH_OUTCOME")
    return log


def rung_isrctn(ids):
    isr = sorted({i["id_value"].replace(" ", "") for i in ids if re.match(r"ISRCTN\d{8}", i["id_value"].replace(" ", ""))})
    log = {"rung": "R5 ISRCTN", "ids": isr}
    if not isr:
        log["outcome"] = "NO_ISRCTN_ID"
        return log
    st, b, u = get(ISRCTN, {"q": isr[0]})
    x = b.decode("utf-8", "replace")
    log.update(request=u, http=st, results_basic_reporting=bool(re.search(r"basicResultsReporting|resultsBasic", x)),
               publication_pmids=sorted(set(re.findall(r"(?:pubmed|PMID)[^\d]{0,30}(\d{8})", x, re.I)))[:20],
               output_urls=sorted(set(re.findall(r"https?://[^\s\"<]*(?:doi\.org|ncbi\.nlm\.nih\.gov|thelancet|nejm)[^\s\"<]*",
                                                 x)))[:15])
    log["outcome"] = "RECORD_FOUND" if st == 200 and "<fullTrial" in x else f"NOT_FOUND http={st}"
    return log


# ------------------------------------------------------------------ driver

def run_trial(label, A):
    nct = g.IDENTITY[label][0]
    e = (A["ncts"].get(nct) or {}) if nct else {}
    disc, cands = [], {}

    def add(pmids, how):
        for p in pmids:
            cands.setdefault(p, set()).add(how)
    refs = [r["pmid"] for r in e.get("refs") or [] if r["type"] in ("RESULT", "DERIVED") and r["pmid"]]
    disc.append({"rung": "D1 AACT study_references", "returned": refs})
    add(refs, "D1")
    regs = ([nct] if nct else []) + [i["id_value"].replace(" ", "") for i in e.get("ids") or []
                                     if re.match(r"(?:ISRCTN\d{8}|\d{4}-\d{6}-\d{2}|CTRI/|EUCTR)", i["id_value"])]
    for r in regs:
        ids, lg = esearch(f"{r}[si]")
        disc.append(dict(lg, returned=ids))
        add(ids, "D2")
    if nct:
        ids, lg = epmc_fulltext_search(nct)
        disc.append(dict(lg, returned=ids))
        add(ids, "D3")
    if label in NAME_ONLY:
        ids, lg = esearch(NAME_ONLY[label])
        disc.append(dict(lg, returned=ids))
        add(ids, "D4")
    meta = efetch_meta(sorted(cands))
    reports = []
    for p in sorted(cands, key=lambda q: (-len(cands[q]), q)):
        m = meta.get(p) or {}
        rec = {"pmid": p, "found_by": sorted(cands[p]), "title": (m.get("title") or "")[:200], "year": m.get("year"),
               "pub_types": m.get("pub_types"), "doi": m.get("doi")}
        if not m:
            rec["screen"] = "NO_PUBMED_RECORD"
        elif not is_primary_report(m):
            rec["screen"] = "NOT_A_PRIMARY_REPORT"
        else:
            rec["screen"] = "PRIMARY_REPORT_CANDIDATE"
            l1, ft1 = rung_pmc(p)
            l2, ft2 = rung_epmc(p) if not ft1 else ({"rung": "R2 Europe PMC", "outcome": "SKIPPED (R1 held the open text)"}, None)
            l3 = rung_unpaywall(m.get("doi"))
            rec["rungs"] = [l1, l2, l3]
            ft = ft1 or ft2
            rec["held"] = bool(ft)
            vnh = next((x for x in (l1, l2) if x.get("body_sha256") and not ft), None)
            if vnh:
                rec["verified_not_held"] = {"pmcid": vnh.get("pmcid") or l1.get("pmcid"), "body_sha256": vnh["body_sha256"]}
            fp = os.path.join(ACQ, f"{p}.json")
            prev = json.load(open(fp, encoding="utf-8")) if os.path.exists(fp) else None
            if ft or not prev:
                a = {"pmid": p, "label_query": label, "query": "cascade:" + "+".join(sorted(cands[p])),
                     "title": m.get("title"), "abstract": m.get("abstract") or "", "pmcid": l1.get("pmcid") or l2.get("pmcid"),
                     "license": l1.get("licence") or l2.get("licence"), "pub_types": m.get("pub_types"),
                     "retrieved_utc": now()}
                if ft:
                    a.update(fulltext=ft, fulltext_sha256=hashlib.sha256(ft.encode("utf-8")).hexdigest())
                elif vnh:
                    a["fulltext_state"] = "VERIFIED_NOT_HELD (licence not open)"
                    a["fulltext_sha256"] = vnh["body_sha256"]
                if prev and prev.get("label_query") and prev["label_query"] != label:
                    rec["note"] = f"already acquired for {prev['label_query']}; not re-labelled"
                else:
                    open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(a, indent=1, ensure_ascii=False) + "\n")
        reports.append(rec)
    per_trial = [rung_aact(nct, A), rung_isrctn(e.get("ids") or [])]
    return {"label": label, "nct": nct, "run_utc": now(), "discovery": disc, "candidates": reports, "trial_rungs": per_trial}


# two REACT rows share NCT04331808 (CORIMUNO-TOCI-1 severe, CORIMUNO-TOCI-ICU critical): a paper bound to that registration
# is bound to ONE of them only when its title states the population ('...Moderate or Severe Pneumonia' / 'critically
# ill'); otherwise to neither (codex review cascade#3: a unique winning registration had bound a report to both)
TITLE_LABEL = g.TITLE_LABEL          # one rule with held_texts (g1/tocilizumab.py)
NON_RCT_TITLE = re.compile(r"\b(?:uncontrolled|single[- ]arm|non-?randomi[sz]ed|cohort|case series|case report|"
                           r"retrospective|observational|propensity)\b", re.I)


def binding(a):
    """WHICH trial's report is an acquired paper? Being FOUND for a trial is not enough: the Europe PMC full-text rung
    (D3) and AACT's auto-matched DERIVED references return papers that merely cite a registration (ARCHITECTS and
    COVIDOSE2 returned the same two papers). A paper binds to the REACT trial(s) whose registration its OWN text (full
    text + abstract + title) names strictly more often than any other registration -- the rule g1.tocilizumab already
    applies to held cache papers -- independent of which search found it. A trial with no AACT registration binds a
    paper only by its name in the paper's title. Returns (labels, reason)."""
    text = g._fold((a.get("fulltext") or "") + "\n" + (a.get("abstract") or "") + "\n" + (a.get("title") or ""))
    # a title that DECLARES a non-randomised design is no REACT trial's report, on every binding path (codex NR-C26: the
    # title-population path returned before the trial-type screen)
    if NON_RCT_TITLE.search(a.get("title") or ""):
        return [], "UNBOUND: the title declares a non-randomised design"
    by_name = [l for l, (n, _) in g.IDENTITY.items() if not n and re.search(re.escape(l), a.get("title") or "", re.I)]
    if by_name:
        return by_name, "BOUND_BY_NAME_IN_TITLE"
    names = re.findall(r"NCT\d{8}", text)
    if not names:
        return [], "UNBOUND: names no registration"
    top = max(set(names), key=names.count)
    tied = sorted(n for n in set(names) if names.count(n) == names.count(top))
    # the paper's STATED registration ('Trial registration: NCT...') decides before frequency: a references list can
    # outvote it (codex review toci_match#10 -- the same rule as g1.tocilizumab.own_registration)
    stated = set(g._REG_STATED.findall(text))
    stated_own = len(stated) == 1
    if len(stated) == 1:
        top, tied = stated.pop(), []
    if len(tied) > 1:
        # a paper reporting TWO trials names both registrations equally (CORIMUNO-19's ICU paper, 35115337: TOCI-ICU
        # NCT04331808 and SARI-ICU NCT04324073). The tie is resolved only when the TITLE names the trial family AND the
        # population of exactly one REACT row among the tied registrations
        by_title = [l for l, rx in TITLE_LABEL.items() if g.IDENTITY[l][0] in tied and re.search(rx, a.get("title") or "", re.I)]
        if len(by_title) == 1:
            return by_title, f"BOUND_BY_TITLE_POPULATION (registrations tied at {names.count(top)}x: {', '.join(tied)})"
        return [], f"UNBOUND: registrations tied at {names.count(top)}x: {', '.join(tied)}"
    labels = [l for l, (n, _) in g.IDENTITY.items() if n == top]
    if not labels:
        return [], f"UNBOUND: names {top} most, not a REACT trial"
    if len(labels) > 1:
        pick = [l for l in labels if l in TITLE_LABEL and re.search(TITLE_LABEL[l], a.get("title") or "", re.I)]
        if len(pick) != 1:
            return [], f"UNBOUND: {top} is shared by {labels}; the title states no single population ({pick})"
        labels = pick
    # ... AND it is a TRIAL report: PubMed types it a randomised/clinical trial, or its title/abstract names the trial.
    # A case report, a mechanism paper or a cohort that cites the registration once is not the trial's report (a
    # cohort's own day-28 deaths would otherwise read as a conflicting trial row).
    rct_type = re.search(r"Randomized Controlled Trial", " ".join(a.get("pub_types") or []))
    trial_type = rct_type or re.search(r"Clinical Trial", " ".join(a.get("pub_types") or []))
    named = [l for l in labels if re.search(re.escape(l.split("-TOCI")[0]), (a.get("title") or "") + " " +
                                             (a.get("abstract") or ""), re.I)]
    if not (trial_type or named):
        return [], f"UNBOUND: names {top} most but is not a trial report (types {a.get('pub_types')})"
    # a GENERIC 'Clinical Trial' type is any trial, including another, uncontrolled one: it binds by frequency only when
    # the paper states the registration as its own or names the trial (codex NR-C26: PMID 33075713, an uncontrolled
    # study citing CORIMUNO's NCT04331808 twice in its discussion, had bound to CORIMUNO-TOCI-1 '+ RCT type')
    if not rct_type and not named and not stated_own:
        return [], (f"UNBOUND: names {top} most, but only a generic 'Clinical Trial' type, no registration stated as its "
                    f"own and the trial is not named")
    return labels, "BOUND_BY_REGISTRATION_MAJORITY" + (" + RCT type" if rct_type else " + trial type, registration stated"
                                                       if stated_own else " + trial named")


def rebind():
    """Offline pass over EVERY acquired paper: bound_labels decides which trial(s) may read it (held_texts); found_for
    keeps which trial's search found it. Returns {pmid: (found_for, bound_labels, reason)}."""
    out = {}
    for f in sorted(os.listdir(ACQ)):
        if not re.match(r"(?:\d+|PPR\d+)\.json$", f):       # PubMed ids and Europe PMC preprint ids (cascade#6)
            continue
        fp = os.path.join(ACQ, f)
        a = json.load(open(fp, encoding="utf-8"))
        found = a.get("found_for") or a.get("label_query") or a.get("candidate_for")
        labels, why = binding(a)
        a.pop("candidate_for", None)
        a.update(found_for=found, bound_labels=labels, binding=why, label_query=None)
        if not labels and a.get("fulltext"):
            # bound to no trial: nothing reads it, so its text is not kept (its sha256 is)
            sha = hashlib.sha256(a.pop("fulltext").encode("utf-8")).hexdigest()
            a.update(fulltext_state="NOT_KEPT (open, but bound to no REACT trial)", fulltext_sha256=sha)
        open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(a, indent=1, ensure_ascii=False) + "\n")
        out[a["pmid"]] = (found, labels, why)
    return out


REACT_PREPRINT_TITLE = re.compile(r"Association between tocilizumab, sarilumab and all-cause mortality at 28 days", re.I)


def read_preprint(ppr, label):
    """A candidate preprint, through the server's own API (api.biorxiv.org): SUPERSEDED when the server records its
    published version (RECOVERY's tocilizumab preprint -> the Lancet paper we hold; reading both would add an earlier
    data cut as a second report). Otherwise its JATS (the API's jatsxml link) is read under the licence the bytes state,
    and held only when it states deaths at day 28."""
    st, b, u = get(f"{EPMC}/search", {"query": f"EXT_ID:{ppr} AND SRC:PPR", "format": "json", "resultType": "core"})
    try:
        r = ((json.loads(b).get("resultList") or {}).get("result") or [{}])[0]
    except Exception:  # noqa: BLE001
        return {"outcome": f"RUNG_FAILED: EPMC http {st}"}
    doi = r.get("doi") or ""
    if not doi.startswith("10.1101/"):
        return {"outcome": "NOT_A_BIORXIV_MEDRXIV_PREPRINT (no API to read it)", "doi": doi}
    st, b, u = get(f"https://api.biorxiv.org/details/medrxiv/{doi}")
    try:
        c = ((json.loads(b).get("collection")) or [{}])[-1]
    except Exception:  # noqa: BLE001
        return {"outcome": f"RUNG_FAILED: biorxiv api http {st}", "doi": doi}
    out = {"doi": doi, "version": c.get("version"), "licence": c.get("license"), "published": c.get("published")}
    if c.get("published") and c["published"] != "NA":
        out["outcome"] = f"SUPERSEDED_BY_PUBLISHED_VERSION {c['published']} (the published report is the source)"
        return out
    st, b, u = get(c.get("jatsxml") or "")
    x = b.decode("utf-8", "replace") if st == 200 else ""
    if "<article" not in x:
        out["outcome"] = f"JATS_NOT_FETCHED http={st}"
        return out
    own = bytes_licence(x)
    out.update(jats_sha256=hashlib.sha256(b).hexdigest(), licence_in_bytes=own)
    t = g._fold(re.sub(r"<[^>]+>", " ", x))
    d28 = [m.start() for m in g._DAY28.finditer(t) if g._DEATH_WORDS.search(t[max(0, m.start() - 200): m.end() + 200])]
    if not d28:
        out["outcome"] = "READ: no day-28 death statement (held: no)"
        return out
    if not (own and OPEN.search(own)):
        out["outcome"] = "READ: states day-28 deaths, licence in bytes not open -> VERIFIED_NOT_HELD"
        return out
    fp = os.path.join(ACQ, f"{ppr}.json")
    open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(
        {"pmid": ppr, "found_for": label, "query": f"cascade:R6 preprint {doi}", "title": r.get("title"),
         "abstract": r.get("abstractText") or "", "license": own, "pub_types": ["Preprint"], "fulltext": x,
         "fulltext_sha256": out["jats_sha256"], "retrieved_utc": now()}, indent=1, ensure_ascii=False) + "\n")
    out["outcome"] = "HELD: states day-28 deaths (open licence in bytes)"
    return out


def rung_preprints(label, nct):
    """R6 Europe PMC PREPRINTS (SRC:PPR: medRxiv, Research Square, ...) for the trial's registration, or its name when it
    has none. A hit is the trial's own report only if it is not a review/meta-analysis by title; REACT's own preprint is
    the comparator (anti-circularity) and is named as such."""
    q = f'"{nct}" AND SRC:PPR' if nct else f'({label}) AND tocilizumab AND SRC:PPR'
    st, b, u = get(f"{EPMC}/search", {"query": q, "format": "json", "pageSize": 25, "resultType": "core"})
    log = {"rung": "R6 Europe PMC preprints", "request": u, "http": st}
    if st != 200:
        log["outcome"] = f"RUNG_FAILED: http {st}"
        return log
    try:
        d = json.loads(b)
    except Exception:  # noqa: BLE001
        log["outcome"] = f"RUNG_FAILED: http {st}"
        return log
    hits = []
    for r in (d.get("resultList") or {}).get("result") or []:
        t = r.get("title") or ""
        stem = label.split("-TOCI")[0].split("-SS")[0]
        # the trial's tocilizumab / IL-6 report: the drug in the title AND (the trial named or a randomised comparison) --
        # RECOVERY's preprints for its other arms (sotrovimab, aspirin, ...) name RECOVERY but not tocilizumab
        names_trial = DRUG.search(t) and (re.search(re.escape(stem), t, re.I) or re.search(r"randomi[sz]", t, re.I))
        kind = ("COMPARATOR_PREPRINT (REACT)" if REACT_PREPRINT_TITLE.search(t) else
                "NOT_A_TRIAL_REPORT (review / meta-analysis)" if re.search(r"review|meta-analys", t, re.I) else
                "CANDIDATE_TRIAL_REPORT" if names_trial else
                "NOT_THIS_TRIAL (title names neither the trial nor a randomised tocilizumab / IL-6 comparison)")
        hits.append({"id": r.get("id"), "year": r.get("pubYear"), "licence": r.get("license"), "title": t[:160], "kind": kind})
    log.update(hit_count=d.get("hitCount"), hits=hits)
    cands = [h for h in hits if h["kind"] == "CANDIDATE_TRIAL_REPORT"]
    for h in cands:
        h["read"] = read_preprint(h["id"], label)
    log["outcome"] = (f"CANDIDATE_TRIAL_PREPRINTS: {[h['id'] for h in cands]}" if cands else
                      f"NO_TRIAL_PREPRINT ({len(hits)} hits: reviews / meta-analyses / the comparator's own preprint)"
                      if hits else "NO_PREPRINT_HIT")
    return log


def summarise():
    rows = ["# Acquisition cascade per REACT trial (generated by scripts/g1_toci_cascade.py)", "",
            "Rungs: D1 AACT study_references | D2 PubMed [si] by registration | D3 Europe PMC full-text search | "
            "D4 name search; per primary-report candidate R1 PMC, R2 Europe PMC, R3 Unpaywall; per trial R4 AACT posted "
            "results, R5 ISRCTN.", "",
            "| trial | discovered (D1/D2/D3/D4) | primary-report candidates | R1 PMC | R2 Europe PMC | R3 Unpaywall | "
            "held open text (read for this trial unless UNBOUND) | R4 AACT | R5 ISRCTN | R6 preprints |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for label in g.IDENTITY:
        fp = os.path.join(CAS, f"{label}.json")
        if not os.path.exists(fp):
            rows.append(f"| {label} | NOT RUN | | | | | | | |")
            continue
        c = json.load(open(fp, encoding="utf-8"))
        n = {k: 0 for k in ("D1", "D2", "D3", "D4")}
        for r in c["candidates"]:
            for k in r["found_by"]:
                n[k] += 1
        pc = [r for r in c["candidates"] if r["screen"] == "PRIMARY_REPORT_CANDIDATE"]
        cell = lambda i: "; ".join(f"{r['pmid']}:{r['rungs'][i]['outcome']}" for r in pc) or "-"  # noqa: E731
        def _b(p):
            f = os.path.join(ACQ, f"{p}.json")
            return label in (json.load(open(f, encoding="utf-8")).get("bound_labels") or []) if os.path.exists(f) else False
        held = ", ".join(r["pmid"] + ("" if _b(r["pmid"]) else " (UNBOUND: not read)") for r in pc if r.get("held")) or "none"
        a, s = c["trial_rungs"][0], c["trial_rungs"][1]
        pp = next((r for r in c["trial_rungs"] if r["rung"] == "R6 Europe PMC preprints"), {"outcome": "not run"})
        rows.append(f"| {label} | {n['D1']}/{n['D2']}/{n['D3']}/{n['D4']} ({len(c['candidates'])}) | "
                    f"{', '.join(r['pmid'] for r in pc) or 'none'} | {cell(0)} | {cell(1)} | {cell(2)} | {held} | "
                    f"{a['outcome']} | {s['outcome']} | {pp['outcome'][:120]} |")
    open(os.path.join(CAS, "CASCADE.md"), "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")


def main(argv):
    os.makedirs(CAS, exist_ok=True)
    if "--aact" in argv:
        build_aact()
    if "--net" in argv or "--rebind" in argv:
        pass
    if "--net" in argv:
        A = json.load(open(AACT_REFS, encoding="utf-8"))
        labels = [a for a in argv if not a.startswith("--")] or list(g.IDENTITY)
        for label in labels:
            c = run_trial(label, A)
            open(os.path.join(CAS, f"{label}.json"), "w", encoding="utf-8", newline="\n").write(
                json.dumps(c, indent=1, ensure_ascii=False) + "\n")
            pc = [r for r in c["candidates"] if r["screen"] == "PRIMARY_REPORT_CANDIDATE"]
            print(label, "candidates", len(c["candidates"]), "primary", [(r["pmid"], r.get("held")) for r in pc],
                  c["trial_rungs"][0]["outcome"], c["trial_rungs"][1]["outcome"], flush=True)
    if "--preprints" in argv:
        for label in [a for a in argv if not a.startswith("--")] or list(g.IDENTITY):
            fp = os.path.join(CAS, f"{label}.json")
            if os.path.exists(fp):
                c = json.load(open(fp, encoding="utf-8"))
                c["trial_rungs"] = [r for r in c["trial_rungs"] if r["rung"] != "R6 Europe PMC preprints"] + \
                    [rung_preprints(label, c["nct"])]
                open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=1, ensure_ascii=False) + "\n")
                print(label, c["trial_rungs"][-1]["outcome"], flush=True)
    # R4 reads only the local AACT extract: recomputed offline for every log, so a rule change never needs the network
    A = json.load(open(AACT_REFS, encoding="utf-8"))
    for label in g.IDENTITY:
        fp = os.path.join(CAS, f"{label}.json")
        if os.path.exists(fp):
            c = json.load(open(fp, encoding="utf-8"))
            c["trial_rungs"][0] = rung_aact(c["nct"], A)
            open(fp, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=1, ensure_ascii=False) + "\n")
    print("licence audit stripped:", licence_audit())
    rebind()
    summarise()


if __name__ == "__main__":
    main(sys.argv[1:])
