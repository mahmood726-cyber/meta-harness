"""V1.1 discovery recall test, sglt2-hfref-hosp-cvdeath: DEFINE-HF and EMPERIAL-Reduced as named recall cases.

The registered PubMed queries are a UID enumeration of DAPA-HF (31535829), EMPEROR-Reduced (32865377) and the comparator
(35112512); the declared registry queries are CT.gov 'HFrEF' x 'SGLT2 inhibitor' and registry-first 'heart failure' x
'SGLT2'. Two randomised placebo-controlled trials of the protocol's drugs in HFrEF are absent from our inventory:
  DEFINE-HF         NCT02653482, PMID 31524498 (dapagliflozin, 12 weeks; PubMed types it 'Clinical Trial', not RCT)
  EMPERIAL-Reduced  PMID 33351892 (empagliflozin, 12 weeks; its PubMed record carries no registration)
Whether either reports the review's outcome is screening's and extraction's question, not retrieval's. This test runs
the registered queries and the registry adapters exactly as the build does, and a concept query (dapagliflozin or
empagliflozin x HFrEF x randomised, text-filtered because DEFINE-HF is not typed RCT), holding results with sha256.

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
SLUG = "sglt2-hfref-hosp-cvdeath"
RUN = os.path.join(HERE, "run")
BROAD = ('(dapagliflozin[tiab] OR empagliflozin[tiab]) AND ("reduced ejection fraction"[tiab] OR HFrEF[tiab]) '
         'AND (randomized[tiab] OR randomised[tiab] OR placebo[tiab])')
NAMED = {"31524498": "DEFINE-HF", "33351892": "EMPERIAL-Reduced"}


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
    rf = F._registry_first_result(cfg["registry_first"])
    ct = F._ctgov_search(cfg["ctgov"]["cond"], cfg["ctgov"]["intr"], 1000)
    broad = F._esearch(BROAD, 2000)
    named = F._efetch(sorted(NAMED))
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _registry_first_result / _ctgov_search / _efetch",
                                     "registered_queries": reg, "registry_first": {"config": cfg["registry_first"], "state": rf["state"], "pmids": rf["ids"]},
                                     "ctgov": {"config": cfg["ctgov"], "ncts": [x["id"] for x in ct]},
                                     "broad_query": BROAD, "broad_pmids": broad, "named_records": named})
    print(f"registered {sum(len(v) for v in reg.values())}; registry-first {len(rf['ids'])} ({rf['state']}); ctgov {len(ct)}; "
          f"broad {len(broad)}; named {len(named)}; sha256 {s[:12]}")


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    rf, broad = set(d["registry_first"]["pmids"]), set(d["broad_pmids"])
    recs = {str(r["id"]): r for r in d["named_records"]}
    out = {"registered_n": len(reg), "registry_first_n": len(rf), "ctgov_n": len(d["ctgov"]["ncts"]),
           "ctgov_has_NCT02653482": "NCT02653482" in d["ctgov"]["ncts"], "broad_n": len(broad),
           "named_cases": {p: {"trial": n, "title": (recs.get(p) or {}).get("title"), "nct": (recs.get(p) or {}).get("nct"),
                               "pubtypes": (recs.get(p) or {}).get("pubtypes"), "in_registered": p in reg,
                               "in_registry_first": p in rf, "in_broad": p in broad} for p, n in NAMED.items()}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
