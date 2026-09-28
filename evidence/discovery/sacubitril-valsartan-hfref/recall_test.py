"""V1.1 discovery recall test, sacubitril-valsartan-hfref: LIFE (NCT02816736) as a named recall case.

The registered PubMed queries are a UID enumeration of PARADIGM-HF (25176015) and two PARADIGM-HF title/name strings,
plus a CT.gov query (condition 'Heart Failure With Reduced Ejection Fraction' x intervention 'LCZ696'). None can
retrieve a later randomised sacubitril/valsartan trial published under another title:
  LIFE  PMID 34730769 (Mann, JAMA Cardiol 2022): sacubitril/valsartan vs valsartan, advanced HFrEF, 335 randomised
        (design paper 32641226 and run-in analysis 35772853 are reports of the SAME trial)
LIFE's primary endpoint is a biomarker (NT-proBNP AUC), and its report STILL states clinical events -- the clinical
composite of days alive, out of hospital and free from heart-failure events, and hyperkalaemia by arm. "Biomarker
trial" must never be read as "no clinical events reported": that is decided per outcome from the source.
This test runs the registered queries and the CT.gov adapter exactly as the build does, and a concept query
(sacubitril/LCZ696 x heart failure x RCT publication type), holds the results with sha256, and reports which reach the
named case. Retrieval is the question; eligibility (valsartan as the RAS-inhibitor control) is screening's.

usage: python recall_test.py fetch   (network, once; writes run/)
       python recall_test.py check   (offline; writes run/RECALL_RESULT.json)
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
SLUG = "sacubitril-valsartan-hfref"
RUN = os.path.join(HERE, "run")
BROAD = '(sacubitril[tiab] OR LCZ696[tiab]) AND "heart failure"[tiab] AND randomized controlled trial[pt]'
NAMED = {"34730769": "LIFE", "32641226": "LIFE (design paper)", "35772853": "LIFE (run-in analysis)"}


def _write(name, obj):
    os.makedirs(RUN, exist_ok=True)
    b = (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    open(os.path.join(RUN, name), "wb").write(b)
    return hashlib.sha256(b).hexdigest()


def fetch():
    from harness import fetch as F
    cfg = json.load(open(os.path.join(ROOT, "topics", f"{SLUG}.json"), encoding="utf-8"))
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    reg = {q: F._esearch(q, 200) for q in cfg["pubmed_queries"]}
    ct = F._ctgov_search(cfg["ctgov"]["cond"], cfg["ctgov"]["intr"], 1000)
    broad = F._esearch(BROAD, 1000)
    named = F._efetch(sorted(NAMED))
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _ctgov_search / _efetch",
                                     "registered_queries": reg, "ctgov": {"config": cfg["ctgov"], "ncts": [x["id"] for x in ct]},
                                     "broad_query": BROAD, "broad_pmids": broad, "named_records": named})
    print(f"registered {sum(len(v) for v in reg.values())}; ctgov {len(ct)}; broad {len(broad)}; named fetched {len(named)}; "
          f"sha256 {s[:12]}")


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    broad = set(d["broad_pmids"])
    recs = {str(r["id"]): r for r in d["named_records"]}
    out = {"registered_queries": list(d["registered_queries"]), "registered_n": len(reg),
           "ctgov_n": len(d["ctgov"]["ncts"]), "ctgov_has_NCT02816736": "NCT02816736" in d["ctgov"]["ncts"],
           "broad_query": d["broad_query"], "broad_n": len(broad),
           "named_cases": {p: {"trial": n, "title": (recs.get(p) or {}).get("title"), "nct": (recs.get(p) or {}).get("nct"),
                               "in_registered": p in reg, "in_broad": p in broad} for p, n in NAMED.items()}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
