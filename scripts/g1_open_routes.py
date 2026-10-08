"""OPEN ROUTES on the gap list's hard trials (search lane share, 8 Oct; D8 open sources only, D9 no CENTRAL/Embase).

Trials: statins ASCOT-LLA older (Collier 2011), MEGA older (Nakaya 2011); denosumab Bone 2008; melatonin James 1990;
iv-iron FAIR-HF. Routes: WHO ICTRP, ISRCTN, ANZCTR, jRCT, EU CTR, CTIS (registries) and IQWiG, NICE TA, TGA, PMDA
(HTA / regulatory) where the drug has a dossier.

Every route is RECORDED: the host's robots.txt verdict (fetched, sha256), then each request's url, HTTP status, bytes,
sha256 and content type. Bodies are kept OUTSIDE the tree (MH_ROUTES_STORE); committed: identifiers, offsets, counts,
and a span (<= 200 characters) only beside a candidate count. REGEX FIRST: each document is searched for the trial's identifiers; a hit's window is
searched for counts (n/N, 'x of y', percentages); a model read is never run here (the HTA/regulatory texts are not
licence-open under scripts/g1_licence.py, so they may not enter a committed prompt).

States: CANDIDATE_COUNT (a count beside a trial identifier AND the gap's outcome term -- a regex cannot say what the number refers to, so it is a candidate for a reader, never a verified count), FOUND_MENTION (identifier, no count), NOT_FOUND (document read,
identifier absent), NO_RECORD (registry searched, the trial is not there), NOT_APPLICABLE (with the reason),
ACCESS_BLOCKED (robots.txt / bot challenge / partner-only terms / host refuses the client -- never bypassed).

  python scripts/g1_open_routes.py          -> outputs/search_audit/open_routes/open_routes.json + .md
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "search_audit" / "open_routes"
STORE = Path(os.environ.get("MH_ROUTES_STORE", str(Path.home() / "mh-routes-store")))
UA = "meta-harness/1.0 (open-routes; mailto:meta-harness@example.org)"

TRIALS = {
    "ASCOT-LLA older": {"topic": "statins-primary-prevention-elderly", "pmid": "21297502",
                        # bare 'ASCOT' is also a social-care quality-of-life scale (ISRCTN listings): context required
                        "ids": [r"\bASCOT[- ]LLA\b", r"Anglo-Scandinavian Cardiac Outcomes",
                                r"\bASCOT\b(?=[^.]{0,80}(?:atorvastatin|lipid|hypertens|amlodipine|atenolol))",
                                r"ISRCTN\s?77890112"],
                        "drug": "atorvastatin"},
    "MEGA older": {"topic": "statins-primary-prevention-elderly", "pmid": "21815708", "nct": "NCT00211705",
                   "ids": [r"\bMEGA\b(?: [Ss]tudy| [Tt]rial)?", r"Management of Elevated Cholesterol in the Primary Prevention",
                           r"NCT00211705"], "drug": "pravastatin"},
    "Bone 2008": {"topic": "denosumab-vertebral-fracture", "pmid": "18381571", "nct": "NCT00091793",
                  "ids": [r"\b20040132\b", r"NCT00091793", r"\bBone\b[^.\n]{0,20}\b2008\b", r"\bDEFEND\b"], "drug": "denosumab"},
    "James 1990": {"topic": "melatonin-primary-insomnia-sol", "pmid": "2306332",
                   "ids": [r"\bJames\b[^.\n]{0,30}\b1990\b", r"Melatonin administration in insomnia"], "drug": "melatonin"},
    "FAIR-HF": {"topic": "iv-iron-hfref-hosp", "pmid": "19920054", "nct": "NCT00520780",
                "ids": [r"\bFAIR[- ]HF\b(?!\s?2)", r"NCT00520780"], "drug": "ferric carboxymaltose"},
}
# the outcome each trial's gap needs, for documents DEDICATED to the trial (its name need not recur in its own report)
OUTCOME = {
    "ASCOT-LLA older": r"(?:aged|age|older|elderly|>=?|≥)\s?(?:60|65|70)\b",
    "MEGA older": r"(?:aged|age|older|elderly|>=?|≥)\s?(?:60|65|70)\b",
    "Bone 2008": r"\bfractures?\b|骨折",
    "James 1990": r"sleep(?:[- ]onset)? latency|\bSOL\b|入眠潜時",
    "FAIR-HF": r"hospitali[sz]\w*[^.]{0,80}(?:heart failure|\bHF\b|cardiovascular)|(?:heart failure|\bHF\b)[^.]{0,40}hospitali[sz]\w*"
               r"|心不全[^。]{0,30}入院|入院[^。]{0,30}心不全",
}
COUNT = re.compile(r"\b\d{1,5}\s?/\s?\d{2,6}\b|\b\d{1,5}\s+(?:of|von)\s+\d{2,6}\b|\b\d{1,3}(?:[.,]\d)?\s?%", re.I)

def _counts(win):
    """Counts in a window, minus page furniture ('Page 142 of 303')."""
    return [c.group(0) for c in COUNT.finditer(win) if "page" not in win[max(0, c.start() - 8):c.start()].lower()]


_robots_cache: dict = {}
LOG: list = []


def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get(url, data=None, headers=None, timeout=90):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), r.headers.get("Content-Type", ""), r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, (e.read() if hasattr(e, "read") else b""), e.headers.get("Content-Type", "") if e.headers else "", url
    except Exception as e:  # noqa: BLE001 -- the failure is recorded, never treated as an empty result
        return None, repr(e).encode(), "", url


def robots(url):
    """(allowed, record) under the host's robots.txt for our agent; a missing robots.txt (404) allows."""
    p = urllib.parse.urlparse(url)
    host = f"{p.scheme}://{p.netloc}"
    if host not in _robots_cache:
        st, b, ct, _ = _get(host + "/robots.txt", timeout=40)
        rules, agent = [], None
        if st == 200 and b"<html" not in b[:300].lower():
            for line in b.decode("utf-8", "replace").splitlines():
                k, _, v = line.partition(":")
                k, v = k.strip().lower(), v.strip()
                if k == "user-agent":
                    agent = v
                elif k in ("disallow", "allow") and agent in ("*", "meta-harness"):
                    rules.append((k, v))
        _robots_cache[host] = {"url": host + "/robots.txt", "http": st, "sha256": hashlib.sha256(b).hexdigest(),
                               "rules_for_us": rules, "html_not_robots": st == 200 and b"<html" in b[:300].lower()}
    rec = _robots_cache[host]
    path = p.path or "/"
    best = None
    for k, v in rec["rules_for_us"]:
        if v and path.startswith(v) and (best is None or len(v) > len(best[1])):
            best = (k, v)
    allowed = (rec["http"] is not None) and (best is None or best[0] == "allow")
    return allowed, rec


def fetch(url, label, data=None, headers=None):
    ok, rb = robots(url)
    if not ok:
        e = {"url": url, "label": label, "state": "ACCESS_BLOCKED", "why": f"robots.txt ({rb['url']}, http {rb['http']})", "at": _now()}
        LOG.append(e)
        return None, e
    st, b, ct, final = _get(url, data=data, headers=headers)
    time.sleep(1.2)                                   # politeness (NICE asks for crawl-delay 1)
    h = hashlib.sha256(b).hexdigest()
    e = {"url": url, "final_url": final, "label": label, "http": st, "bytes": len(b), "sha256": h, "content_type": ct,
         "at": _now(), "method": "POST" if data else "GET"}
    LOG.append(e)
    if st != 200:
        return None, e
    STORE.mkdir(parents=True, exist_ok=True)
    (STORE / h).write_bytes(b)
    return b, e


def text_of(b, ct):
    if b[:4] == b"%PDF" or "pdf" in (ct or ""):
        # PyMuPDF (pdftotext reading stdin returned nothing on Windows: the FAIR-HF summary report read as 0 characters)
        try:
            import fitz
            with fitz.open(stream=b, filetype="pdf") as d:
                return "\n".join(p.get_text() for p in d)
        except Exception:  # noqa: BLE001
            return ""
    s = b.decode("utf-8", "replace")
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s))


def _span(txt, m, counts):
    """Committed context is kept to what the evidence needs: a span (<= 200 chars) only beside a candidate count; a
    mention keeps its match and offset (the document's sha256 re-derives the context). These texts are not licence-open."""
    return " ".join(txt[max(0, m.start() - 90):m.end() + 110].split())[:200] if counts else None


def scan(trial, txt):
    """Regex first: identifier hits, and counts within the identifier's window."""
    hits = []
    for pat in TRIALS[trial]["ids"]:
        for m in re.finditer(pat, txt):
            w0, w1 = max(0, m.start() - 400), min(len(txt), m.end() + 400)
            win = txt[w0:w1]
            # a count counts only when the gap's OUTCOME is named in the same window (a BMD percentage beside
            # '20040132' is not a fracture count; a diabetes-subgroup event count is not an older-subgroup count)
            oc = re.search(OUTCOME[trial], win, re.I)
            counts = _counts(win) if oc else []
            hits.append({"pattern": pat, "at": m.start(), "match": m.group(0), "outcome_in_window": oc.group(0)[:60] if oc else None,
                         "counts_in_window": counts[:12], "span": _span(txt, m, counts)})
            if len(hits) >= 40:
                return hits
    return hits


def outcome_scan(trial, txt):
    """Outcome-term hits and the counts beside them, for a document dedicated to the trial."""
    out = []
    for m in re.finditer(OUTCOME[trial], txt or "", re.I):
        win = txt[max(0, m.start() - 250):m.end() + 250]
        c = _counts(win)
        out.append({"match": m.group(0)[:80], "at": m.start(), "counts_in_window": c[:12], "span": _span(txt, m, c)})
        if len(out) >= 25:
            break
    return out


def doc_route(trial, route, url, label):
    b, e = fetch(url, label)
    if b is None:
        state = e.get("state") or ("ACCESS_BLOCKED" if e.get("http") in (401, 403, 429) else "FETCH_FAILED")
        return {"trial": trial, "route": route, "document": label, "state": state, "request": e}
    txt = text_of(b, e["content_type"])
    hits = scan(trial, txt)
    st = ("CANDIDATE_COUNT" if any(h["counts_in_window"] for h in hits) else "FOUND_MENTION" if hits else "NOT_FOUND")
    return {"trial": trial, "route": route, "document": label, "state": st, "request": e, "text_chars": len(txt),
            "hits": hits[:15]}


def not_run(trial, route, state, why, evidence=None):
    return {"trial": trial, "route": route, "state": state, "why": why, "evidence": evidence}


# ---------------------------------------------------------------- registries

def isrctn(trial, q):
    url = "https://www.isrctn.com/api/query/format/who?" + urllib.parse.urlencode({"q": q, "limit": 20})
    b, e = fetch(url, f"ISRCTN API q={q}")
    if b is None:
        return {"trial": trial, "route": "ISRCTN", "state": "FETCH_FAILED", "request": e}
    ids = sorted(set(re.findall(r"ISRCTN\d{8}", b.decode("utf-8", "replace"))))
    txt = text_of(b, "xml")
    hits = scan(trial, txt)
    # an ISRCTN listing is THIS trial only when one of its identifiers matches (an 'ASCOT' quality-of-life scale is not ASCOT)
    return {"trial": trial, "route": "ISRCTN", "query": q, "state": "FOUND_RECORD" if hits else "NO_RECORD",
            "request": e, "isrctn_ids_returned": ids[:20], "hits": hits[:10]}


def euctr(trial, q):
    """Search; IDENTIFY a hit as this trial only when its protocol page carries one of the trial's identifiers; for an
    identified trial read its results page and every posted result attachment (outcome terms + counts)."""
    url = "https://www.clinicaltrialsregister.eu/ctr-search/search?" + urllib.parse.urlencode({"query": q})
    b, e = fetch(url, f"EU CTR search query={q}")
    if b is None:
        return {"trial": trial, "route": "EU CTR", "state": "FETCH_FAILED", "request": e}
    s = b.decode("utf-8", "replace")
    eud = sorted(set(re.findall(r"\b(?:19|20)\d{2}-\d{6}-\d{2}\b", s)))
    n = re.search(r"([\d,]+)\s+result\(s\) found", s)
    out = {"trial": trial, "route": "EU CTR", "query": q, "request": e, "n_results": n.group(1) if n else None,
           "eudract_numbers": eud[:20], "identified": [], "state": "NO_RECORD"}
    for x in eud[:8]:
        cc = re.search(rf"/ctr-search/trial/{x}/([A-Z]{{2,3}})", s)
        pb, pe = fetch(f"https://www.clinicaltrialsregister.eu/ctr-search/trial/{x}/{cc.group(1) if cc else 'GB'}",
                       f"EU CTR protocol {x}")
        pt = text_of(pb, pe["content_type"]) if pb else ""
        # identity from the record's OWN title fields (A.3 full title, A.3.2 abbreviated title): a protocol that merely
        # cites the trial (FAIR-HF2 lists 'FAIR-HF' among trials to pool) is not the trial
        titles = " ".join(m.group(0) for m in re.finditer(r"A\.3(?:\.\d)?\s[^A]{0,40}title[^\n]{0,400}?(?=A\.\d|$)", pt))
        ids = scan(trial, titles)
        if not ids:
            continue
        rec = {"eudract": x, "identified_by": sorted({h["match"] for h in ids})[:5], "protocol_span": ids[0]["span"]}
        rb, re_ = fetch(f"https://www.clinicaltrialsregister.eu/ctr-search/trial/{x}/results", f"EU CTR results {x}")
        rs = rb.decode("utf-8", "replace") if rb else ""
        atts = sorted(set(re.findall(r"https?://www\.clinicaltrialsregister\.eu/ctr-search/rest/download/result/attachment/[^\"' ]+", rs)))
        rec["results_http"] = re_.get("http")
        rec["structured_outcomes"] = outcome_scan(trial, text_of(rb, re_["content_type"]))[:8] if rb else []
        rec["attachments"] = []
        for a in atts[:4]:
            ab, ae = fetch(a, f"EU CTR result attachment {x}")
            at = text_of(ab, ae["content_type"]) if ab else ""
            rec["attachments"].append({"url": a, "http": ae.get("http"), "sha256": ae.get("sha256"), "text_chars": len(at),
                                       "outcome_hits": outcome_scan(trial, at)[:15]})
        out["identified"].append(rec)
    if out["identified"]:
        got = any(h["counts_in_window"] for r in out["identified"]
                  for h in r["structured_outcomes"] + [h for a in r["attachments"] for h in a["outcome_hits"]])
        out["state"] = "CANDIDATE_COUNT" if got else "FOUND_RECORD"
    return out


def ctis(trial, q):
    url = "https://euclinicaltrials.eu/ctis-public-api/search"
    body = json.dumps({"pagination": {"page": 1, "size": 20}, "sort": {"property": "decisionDate", "direction": "DESC"},
                       "searchCriteria": {"containAll": q}}).encode()
    b, e = fetch(url, f"CTIS public search containAll={q}", data=body, headers={"Content-Type": "application/json"})
    if b is None:
        return {"trial": trial, "route": "CTIS", "state": "FETCH_FAILED", "request": e}
    try:
        d = json.loads(b)
        n = (d.get("pagination") or {}).get("totalRecords")
        rows = [{"ctNumber": x.get("ctNumber"), "title": (x.get("ctTitle") or "")[:160]} for x in d.get("data") or []]
    except Exception:  # noqa: BLE001
        return {"trial": trial, "route": "CTIS", "state": "UNPARSEABLE", "request": e}
    mine = [r for r in rows if any(re.search(p, r["title"]) for p in TRIALS[trial]["ids"])]
    return {"trial": trial, "route": "CTIS", "query": q, "request": e, "n_results": n, "rows": rows[:10],
            "state": "FOUND_RECORD" if mine else "NO_RECORD",
            "note": "CTIS holds trials applied for under the CTR from 31 Jan 2023 or transitioned to it; the rows listed "
                    "are other trials of the same drug, none of them this trial"}


def jrct(trial, q):
    # the site's own search form redirects to this GET (free word, all recruitment states, all record types)
    url = "https://jrct.mhlw.go.jp/search?" + urllib.parse.urlencode(
        {"language": "en", "searched": 1, "page": 1, "rec": "1,2,3,4,5", "free": q, "free_op": 0})
    b, e = fetch(url, f"jRCT search {q}")
    if b is None:
        return {"trial": trial, "route": "jRCT", "state": "FETCH_FAILED", "request": e}
    s = b.decode("utf-8", "replace")
    ids = sorted(set(re.findall(r"\bjRCT[a-z]?\d{9,10}\b", s)))
    hits = scan(trial, text_of(b, "html"))
    return {"trial": trial, "route": "jRCT", "query": q, "request": e, "jrct_ids_returned": ids[:20], "hits": hits[:5],
            "state": "FOUND_RECORD" if hits else "NO_RECORD",
            "note": "jRCT opened in 2018 (Clinical Trials Act); older Japanese trials sit in UMIN-CTR / JAPIC, and UMIN's "
                    "robots.txt disallows AI agents"}


def main(argv):
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    # WHO ICTRP / ANZCTR / UMIN: blocked by the host -- recorded, never bypassed
    for host, route, why in (("https://trialsearch.who.int/", "WHO ICTRP",
                              "robots.txt Disallow: / for all agents; web service and crawling service are partner-only "
                              "(open route: a person's Search Portal export or WHO's full-dataset request)"),
                             ("https://www.anzctr.org.au/", "ANZCTR", "Cloudflare managed challenge ('I'm Under Attack') served "
                              "to the harness client; a bot challenge is never bypassed")):
        ok, rb = robots(host)
        for t in TRIALS:
            rows.append(not_run(t, route, "ACCESS_BLOCKED", why, rb))
    for t in TRIALS:
        rows.append(not_run(t, "TGA AusPAR", "ACCESS_BLOCKED",
                            "www.tga.gov.au refuses the harness HTTP client (connection times out; health.gov.au likewise, "
                            "pbs.gov.au answers); in a browser the AusPAR PDFs are served only as file downloads, which need "
                            "a person's approval. Candidates: Prolia AusPAR 2010 (+ CER extract 2014), Ferinject AusPAR 2011 "
                            "and 2019, Circadin AusPAR 2009/2011. Not read."))
    rows += [isrctn("ASCOT-LLA older", "ASCOT"), isrctn("ASCOT-LLA older", "Anglo-Scandinavian Cardiac Outcomes Trial"),
             isrctn("MEGA older", "pravastatin"), isrctn("FAIR-HF", "ferric carboxymaltose heart failure"),
             isrctn("Bone 2008", "denosumab"), isrctn("James 1990", "melatonin insomnia")]
    rows += [euctr("FAIR-HF", "FAIR-HF"), euctr("FAIR-HF", "ferric carboxymaltose heart failure"),
             euctr("Bone 2008", "denosumab 20040132"), euctr("Bone 2008", "AMG 162 low bone mass"),
             euctr("ASCOT-LLA older", "ASCOT atorvastatin"), euctr("MEGA older", "pravastatin MEGA"),
             euctr("James 1990", "melatonin insomnia")]
    rows += [ctis(t, q) for t, q in (("FAIR-HF", "ferric carboxymaltose"), ("Bone 2008", "denosumab"),
                                      ("ASCOT-LLA older", "atorvastatin"), ("MEGA older", "pravastatin"), ("James 1990", "melatonin"))]
    rows += [jrct("MEGA older", "MEGA pravastatin"), jrct("MEGA older", "pravastatin"), jrct("Bone 2008", "denosumab"),
             jrct("FAIR-HF", "ferric carboxymaltose"), jrct("James 1990", "melatonin")]
    for t, route, url, label in DOCS:
        rows.append(doc_route(t, route, url, label))
    na = [("MEGA older", "PMDA", "pravastatin (Mevalotin) was approved in Japan in 1989, before PMDA's online review documents; MEGA "
                                  "(1994-2004) was a post-approval trial with no dossier of its own"),
          ("ASCOT-LLA older", "PMDA", "atorvastatin's Japanese approval dossier (2000) predates ASCOT-LLA's results (2003)"),
          ("Bone 2008", "IQWiG", "denosumab (Prolia, 2010) was authorised before the AMNOG early benefit assessment (2011): no IQWiG dossier"),
          ("FAIR-HF", "IQWiG", "ferric carboxymaltose has no AMNOG / IQWiG benefit assessment (authorised nationally, 2007)"),
          ("James 1990", "IQWiG", "melatonin for primary insomnia (Circadin, 2007) predates AMNOG; Slenyto's 2018 dossier concerns children"),
          ("FAIR-HF", "NICE TA", "no NICE technology appraisal of ferric carboxymaltose (heart failure is covered by guideline NG106)"),
          ("James 1990", "NICE TA", "no NICE technology appraisal of melatonin for insomnia")]
    rows += [not_run(t, r, "NOT_APPLICABLE", why) for t, r, why in na]
    out = {"schema": 1, "run_utc": _now(), "store_outside_tree": True, "trials": TRIALS and {k: {kk: vv for kk, vv in v.items()
           if kk != "ids"} | {"id_patterns": v["ids"]} for k, v in TRIALS.items()}, "robots": _robots_cache, "rows": rows,
           "requests": LOG}
    json.dump(out, open(OUT / "open_routes.json", "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    L = ["# Open routes on the gap list's hard trials (search lane, 8 Oct)", "",
         "Generated by scripts/g1_open_routes.py. Every request recorded (robots.txt verdict, url, HTTP, sha256); bodies held "
         "outside the tree; regex first; no model read (these HTA/regulatory texts are not licence-open).", "",
         "| Trial | Route | State | Document / query | Evidence |", "|---|---|---|---|---|"]
    for r in rows:
        ev = ""
        if r.get("identified"):
            ev = "; ".join(f"EudraCT {x['eudract']} ({', '.join(x['identified_by'])}), {len(x['attachments'])} result attachment(s)"
                           for x in r["identified"])
        elif r.get("hits"):
            h = next((h for h in r["hits"] if h.get("counts_in_window")), r["hits"][0])
            ev = f"`{h['match']}`" + (f": \"{h['span'][:160]}\"" if h.get("span") else f" at offset {h['at']}")
        elif r.get("why"):
            ev = r["why"][:200]
        L.append(f"| {r['trial']} | {r['route']} | {r['state']} | {r.get('document') or r.get('query') or ''} | {ev.replace('|', '/')} |")
    open(OUT / "open_routes.md", "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    for r in rows:
        print(f"{r['trial']:16} | {r['route']:10} | {r['state']:15} | {r.get('document') or r.get('query') or ''} "
              f"| http {(r.get('request') or {}).get('http')} | hits {len(r.get('hits') or [])}", flush=True)


# HTA / regulatory documents (the candidate list is fixed here, before reading; each read by regex)
DOCS = [
    ("Bone 2008", "NICE TA", "https://www.nice.org.uk/guidance/ta204/resources/denosumab-for-the-prevention-of-osteoporotic-fractures-in-postmenopausal-women-pdf-82600189194949", "NICE TA204 guidance"),
    ("Bone 2008", "NICE TA", "https://www.nice.org.uk/guidance/ta204/documents/osteoporotic-fractures-denosumab-manufacturer-response-to-clarification-february-20102", "NICE TA204 manufacturer response to clarification"),
    ("Bone 2008", "NICE TA", "https://www.nice.org.uk/guidance/ta204/documents", "NICE TA204 documents index"),
    ("ASCOT-LLA older", "NICE TA", "https://www.nice.org.uk/guidance/ta94/documents", "NICE TA94 documents index"),
    ("MEGA older", "NICE TA", "https://www.nice.org.uk/guidance/ta94/documents", "NICE TA94 documents index"),
    ("ASCOT-LLA older", "IQWiG", "https://www.iqwig.de/projekte/ga05-01.html", "IQWiG GA05-01 project page"),
    ("MEGA older", "IQWiG", "https://www.iqwig.de/projekte/ga05-01.html", "IQWiG GA05-01 project page"),
    # second pass (8 Oct): the documents each index lists by TYPE (submission / ERG / clarification / briefing / report),
    # chosen from the index before reading any of them
    *[("Bone 2008", "NICE TA", f"https://www.nice.org.uk/guidance/ta204/documents/{p}", f"NICE TA204 {lab}") for p, lab in (
        ("osteoporotic-fractures-denosumab-manufacturer-submission2", "manufacturer submission"),
        ("osteoporotic-fractures-denosumab-evidence-review-group-report2", "evidence review group report"),
        ("osteoporotic-fractures-denosumab-manufacturer-response-to-clarification-march-20102", "manufacturer response to clarification March 2010"),
        ("osteoporotic-fractures-denosumab-premeeting-briefing2", "pre-meeting briefing"),
        ("osteoporotic-fractures-denosumab-final-appraisal-determination-document2", "final appraisal determination"))],
    *[(t, "IQWiG", "https://www.iqwig.de/download/arbeitspapier_nutzenbewertung_der_statine_unter_beruecksichtigung_von_atorvastin.pdf",
       "IQWiG GA05-01 working paper (statins)") for t in ("ASCOT-LLA older", "MEGA older")],
    # PMDA application dossiers (Japanese; A100 = review report, G100 = CTD 2.5 clinical overview)
    *[("Bone 2008", "PMDA", f"https://www.pmda.go.jp/drugs/2013/P201300022/430574000_22500AMX00870_{c}.pdf", f"PMDA Pralia 2013 {c}")
      for c in ("A100_1", "A100_2", "G100_1", "G100_2")],
    *[("FAIR-HF", "PMDA", f"https://www.pmda.go.jp/drugs/2019/P20190314002/380077000_23100AMX00290_{c}.pdf", f"PMDA Ferinject 2019 {c}")
      for c in ("A100_1", "G100_1")],
    *[("James 1990", "PMDA", f"https://www.pmda.go.jp/drugs/2020/P20200408001/620095000_30200AMX00439_{c}.pdf", f"PMDA Melatobel 2020 {c}")
      for c in ("A100_1", "G100_1")],
]


if __name__ == "__main__":
    main(sys.argv[1:])
