"""RECORDED probe: for every G1 topic, how many records each REGISTERED query returns today (PubMed esearch count per
query; CT.gov API v2 totalCount for query.cond + query.intr) against how many our search RETAINED
(cache/<slug>/records.json). Finds silent caps: a retained set smaller than the source's own count with no cap in the
retrieval ledger. Every request recorded (URL, HTTP, count, response sha256).

  python scripts/g1_search_volume_probe.py   -> outputs/search_audit/search_volume_probe.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import g1_search_miss_probe as p  # noqa: E402

ROOT, OUT = p.ROOT, p.OUT


def ctgov_total(q):
    prm = {"countTotal": "true", "pageSize": 1, "fields": "protocolSection.identificationModule.nctId"}
    if q.get("cond"):
        prm["query.cond"] = q["cond"]
    if q.get("intr"):
        prm["query.intr"] = q["intr"]
    st, b, u = p.get(p.CTG, prm)
    try:
        n = json.loads(b).get("totalCount")
    except Exception:  # noqa: BLE001
        n = None
    return n, p.rec(st, b, u, count=n)


def main():
    out = {}
    for f in sorted(os.listdir(os.path.join(ROOT, "outputs", "k_gap", "g1"))):
        s = f[:-5]
        r = json.load(open(os.path.join(ROOT, "cache", s, "records.json"), encoding="utf-8"))
        calls, pq = [], []
        for q in r.get("pubmed_queries") or []:
            n, c = p.esearch_count(q)
            calls.append(c)
            pq.append({"query": q, "count_today": n})
        cn, c = ctgov_total(r.get("ctgov_query") or {}) if r.get("ctgov_query") else (None, None)
        if c:
            calls.append(c)
        out[s] = {"search_run_utc": r.get("fetched_utc"), "pubmed_retained": len(r.get("records") or []),
                  "pubmed_queries": pq, "ctgov_query": r.get("ctgov_query"),
                  "ctgov_retained": len(r.get("ctgov") or []), "ctgov_count_today": cn,
                  "ctgov_truncated": bool(cn and cn > len(r.get("ctgov") or [])), "calls": calls}
        print(s, "pubmed", len(r.get("records") or []), [x["count_today"] for x in pq], "| ctgov", len(r.get("ctgov") or []),
              "of", cn, flush=True)
    json.dump({"topics": out}, open(os.path.join(OUT, "search_volume_probe.json"), "w", encoding="utf-8", newline="\n"),
              indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
