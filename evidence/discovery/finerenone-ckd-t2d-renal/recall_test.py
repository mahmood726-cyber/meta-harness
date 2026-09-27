"""V1.1 discovery recall test, finerenone-ckd-t2d-renal: FIVE-STAR and CONFIDENCE as named recall cases.

The registered PubMed queries are title+year reconstructions of three known reports (FIDELIO-DKD 2020, FIGARO-DKD 2021,
ARTS-DN 2015). They can never retrieve a trial published later under another title, however eligible:
  FIVE-STAR   PMID 41351003 (2025): finerenone vs placebo, arterial stiffness and cardiorenal biomarkers, T2D + CKD
  CONFIDENCE  PMID 40470996 (N Engl J Med 2025): finerenone with empagliflozin in CKD and T2D (UACR)
This test runs the registered queries and a concept query (finerenone x kidney disease/albuminuria x RCT publication
type) through the harness's own PubMed adapters, holds both results with sha256, and reports which named cases each
retrieves. Retrieval is the question here; eligibility is screening's (CONFIDENCE's combination arm is a screening
decision, not a search one).

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
SLUG = "finerenone-ckd-t2d-renal"
RUN = os.path.join(HERE, "run")
BROAD = ('finerenone[tiab] AND ("chronic kidney disease"[tiab] OR "kidney disease"[tiab] OR "diabetic nephropathy"[tiab] '
         'OR "diabetic kidney disease"[tiab] OR albuminuria[tiab]) AND randomized controlled trial[pt]')
NAMED = {"41351003": "FIVE-STAR", "40470996": "CONFIDENCE"}


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
    broad = F._esearch(BROAD, 500)
    named = F._efetch(sorted(NAMED)) if NAMED else []
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _efetch",
                                     "registered_queries": reg, "broad_query": BROAD, "broad_pmids": broad,
                                     "named_records": named})
    print(f"registered {sum(len(v) for v in reg.values())}; broad {len(broad)}; named fetched {len(named)}; sha256 {s[:12]}")


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    broad = set(d["broad_pmids"])
    recs = {str(r["id"]): r for r in d["named_records"]}
    out = {"registered_queries": list(d["registered_queries"]), "registered_n": len(reg),
           "broad_query": d["broad_query"], "broad_n": len(broad),
           "named_cases": {p: {"trial": n, "title": (recs.get(p) or {}).get("title"),
                               "in_registered": p in reg, "in_broad": p in broad} for p, n in NAMED.items()}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
