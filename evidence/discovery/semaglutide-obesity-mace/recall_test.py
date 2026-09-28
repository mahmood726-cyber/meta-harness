"""V1.1 discovery recall test, semaglutide-obesity-mace: the registered search is PMID/title anchors on ONE trial.

The registered PubMed queries are SELECT's PMID (37952131[uid]) and two reconstructions of SELECT's title; comparator-
reference seeding is off, so report expansion is restricted to what those anchors return. They can never retrieve any
other placebo-controlled semaglutide trial in adults with overweight or obesity without diabetes. The named recall
cases are the semaglutide RCTs the held comparator (Stefanou 2024) includes:
  STEP 1 33567185, STEP 3 33625476, STEP 4 33755728, STEP 5 36216945, STEP 6 35131037, STEP 8 35015037,
  OASIS 1 37385278, STEP 7 38330988
Whether each reports MACE (Stefanou's MACE plot contains none of them) and whether each is eligible is screening's
question, not retrieval's. A concept query (semaglutide x obesity/overweight x RCT publication type) is run beside the
registered queries through the harness's own adapters; results are held with sha256.

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
SLUG = "semaglutide-obesity-mace"
RUN = os.path.join(HERE, "run")
BROAD = 'semaglutide[tiab] AND (obesity[tiab] OR overweight[tiab]) AND randomized controlled trial[pt]'
NAMED = {"33567185": "STEP 1", "33625476": "STEP 3", "33755728": "STEP 4", "36216945": "STEP 5", "35131037": "STEP 6",
         "35015037": "STEP 8", "37385278": "OASIS 1", "38330988": "STEP 7", "37952131": "SELECT (the anchor)"}


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
    broad = F._esearch(BROAD, 2000)
    named = F._efetch(sorted(NAMED))
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _efetch",
                                     "registered_queries": reg, "seed_comparator_refs": cfg.get("seed_comparator_refs"),
                                     "broad_query": BROAD, "broad_pmids": broad, "named_records": named})
    print(f"registered {sum(len(v) for v in reg.values())}; broad {len(broad)}; named fetched {len(named)}; sha256 {s[:12]}")


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    broad = set(d["broad_pmids"])
    recs = {str(r["id"]): r for r in d["named_records"]}
    out = {"registered_queries": list(d["registered_queries"]), "registered_pmids": sorted(reg), "broad_n": len(broad),
           "named_cases": {p: {"trial": n, "title": (recs.get(p) or {}).get("title"), "in_registered": p in reg,
                               "in_broad": p in broad} for p, n in NAMED.items()}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
