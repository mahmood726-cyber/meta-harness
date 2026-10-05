"""RECORDED probe that TYPES every search miss of the G1 search+screen audit (scripts/g1_search_screen_audit.py).

For each ELIGIBLE comparator trial our registered search did not identify (search == NOT_IDENTIFIED):
  PubMed  esummary of each PMID (exists? entrez/publication dates); each registered query re-run restricted to the record
          ('(<query>) AND <pmid>[uid]'), and each of its top-level AND clauses alone, so a QUERY_GAP names the clause
          that drops the record
  CT.gov  for an NCT: does the registered CT.gov query (query.cond + query.intr) return it (API v2, filter.ids)?
Type (first that holds):
  DATABASE_NOT_SEARCHED   no PMID in PubMed and no NCT in CT.gov for the trial (a source outside the protocol's databases)
  DATE_WINDOW             a registered query matches the record today, and the record entered PubMed AFTER our search ran
  RETRIEVED_NOT_RETAINED  a registered query matches today and the record predates the run: the search matched it but our
                          retained set lacks it (cap / fetch / dedup) -- or MeSH indexing assigned since; said as such
  QUERY_GAP               no registered PubMed query (nor the CT.gov query, for an NCT) matches the record
Every request is recorded: URL, HTTP status, the count returned and the response sha256 (outputs/search_audit/
search_miss_probe.json). Re-running reproduces it subject to PubMed's own index changes (stated, not hidden).

  python scripts/g1_search_miss_probe.py [SLUG ...]   (online)
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "search_audit")
AUDIT = os.path.join(OUT, "SEARCH_SCREEN_AUDIT.json")
PROBE = os.path.join(OUT, "search_miss_probe.json")
EU = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
CTG = "https://clinicaltrials.gov/api/v2/studies"
UA = {"User-Agent": "meta-harness-search-audit/1.0"}


def get(url, params):
    u = url + "?" + urllib.parse.urlencode(params)
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r:
                b = r.read()
                time.sleep(0.36)
                return r.status, b, u
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < 4:
                time.sleep(2 * (i + 1) ** 2)
                continue
            return e.code, b"", u
        except Exception:  # noqa: BLE001 -- retried, then reported as a failed request
            time.sleep(2 * (i + 1))
    return None, b"", u


def rec(st, b, u, **kw):
    return {"url": u, "http": st, "sha256": hashlib.sha256(b).hexdigest(), **kw}


def esearch_count(term):
    st, b, u = get(f"{EU}/esearch.fcgi", {"db": "pubmed", "retmode": "json", "term": term})
    try:
        n = int(json.loads(b)["esearchresult"]["count"])
    except Exception:  # noqa: BLE001
        n = None
    return n, rec(st, b, u, count=n)


def top_level_and(q):
    """Split a PubMed query on its top-level ' AND ' (parentheses respected)."""
    parts, depth, cur, i = [], 0, "", 0
    while i < len(q):
        c = q[i]
        depth += c == "("
        depth -= c == ")"
        if depth == 0 and q[i:i + 5].upper() == " AND ":
            parts.append(cur.strip())
            cur, i = "", i + 5
            continue
        cur += c
        i += 1
    parts.append(cur.strip())
    return [p for p in parts if p]


def _date(s):
    m = re.match(r"(\d{4})/(\d{2})/(\d{2})", s or "")
    return datetime.date(*map(int, m.groups())) if m else None


def probe_pmid(pmid, queries, run_utc):
    st, b, u = get(f"{EU}/esummary.fcgi", {"db": "pubmed", "retmode": "json", "id": pmid})
    calls = [rec(st, b, u)]
    try:
        s = json.loads(b)["result"][pmid]
        exists = "error" not in s
        hist = {h.get("pubstatus"): h.get("date") for h in s.get("history") or []}
        edat = _date(hist.get("entrez") or hist.get("pubmed") or "")
    except Exception:  # noqa: BLE001
        exists, edat, s = False, None, {}
    out = {"pmid": pmid, "in_pubmed": exists, "entrez_date": str(edat) if edat else None,
           "title": (s.get("title") or "")[:200], "queries": []}
    for q in queries or []:
        n, c = esearch_count(f"({q}) AND {pmid}[uid]")
        calls.append(c)
        qr = {"query": q, "matches_record": bool(n)}
        if not n:
            fails = []
            for cl in top_level_and(q):
                m, c2 = esearch_count(f"({cl}) AND {pmid}[uid]")
                calls.append(c2)
                if not m:
                    fails.append(cl)
            qr["failing_clauses"] = fails
        out["queries"].append(qr)
    run = datetime.date.fromisoformat(run_utc[:10]) if run_utc else None
    out["entered_after_search_run"] = bool(edat and run and edat > run)
    return out, calls


def probe_nct(nct, ctq):
    st, b, u = get(f"{CTG}/{nct}", {"fields": "protocolSection.identificationModule.nctId"})
    calls = [rec(st, b, u)]
    exists = st == 200
    matched = None
    if exists and ctq:
        p = {"filter.ids": nct, "fields": "protocolSection.identificationModule.nctId", "pageSize": 5}
        if ctq.get("cond"):
            p["query.cond"] = ctq["cond"]
        if ctq.get("intr"):
            p["query.intr"] = ctq["intr"]
        st2, b2, u2 = get(CTG, p)
        try:
            matched = any((x["protocolSection"]["identificationModule"]["nctId"] == nct)
                          for x in json.loads(b2).get("studies") or [])
        except Exception:  # noqa: BLE001
            matched = None
        calls.append(rec(st2, b2, u2, matched=matched))
    return {"nct": nct, "in_ctgov": exists, "ctgov_query_matches": matched}, calls


def classify(pm, nc):
    if not any(p["in_pubmed"] for p in pm) and not any(n["in_ctgov"] for n in nc):
        return "DATABASE_NOT_SEARCHED"
    hit = [p for p in pm if any(q["matches_record"] for q in p["queries"])]
    if hit:
        return "DATE_WINDOW" if all(p["entered_after_search_run"] for p in hit) else "RETRIEVED_NOT_RETAINED"
    if any(n.get("ctgov_query_matches") for n in nc):
        return "RETRIEVED_NOT_RETAINED"
    return "QUERY_GAP"


def main(argv):
    a = json.load(open(AUDIT, encoding="utf-8"))
    prev = json.load(open(PROBE, encoding="utf-8")) if os.path.exists(PROBE) else {"topics": {}}
    for t in a["topics"]:
        if argv and t["slug"] not in argv:
            continue
        q = t["registered_queries"]
        res = {}
        for r in t["trials"]:
            if r["kind"] != "ELIGIBLE" or r["search"] != "NOT_IDENTIFIED":
                continue
            pm, nc, calls = [], [], []
            for p in r["pmids"]:
                x, c = probe_pmid(p, q.get("pubmed"), t["search_run_utc"])
                pm.append(x)
                calls += c
            for n in r["ncts"]:
                x, c = probe_nct(n, q.get("ctgov"))
                nc.append(x)
                calls += c
            res[r["label"]] = {"pmids": pm, "ncts": nc, "miss_type": classify(pm, nc), "calls": calls,
                               "probed_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
            print(t["slug"], "|", r["label"], "->", res[r["label"]]["miss_type"], flush=True)
        prev["topics"][t["slug"]] = res
    os.makedirs(OUT, exist_ok=True)
    json.dump(prev, open(PROBE, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
