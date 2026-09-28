"""V1.1 discovery recall test, noac-vs-warfarin-af-stroke: J-ROCKET AF (NCT00494871) as a named recall case.

The registered search is UID retrieval of the four pivotal reports (RE-LY 19717844, ROCKET AF 21830957, ARISTOTLE
21870978, ENGAGE AF-TIMI 48 24251359) plus a registry-first query (condition 'atrial fibrillation' x intervention
'anticoagulant'), with comparator-reference seeding disabled. UID retrieval can only return what it enumerates, so a
randomised NOAC-vs-warfarin trial outside the four can never be found by it:
  J-ROCKET AF  PMID 22664783 (Hori, Circ J 2012): rivaroxaban vs warfarin in Japanese patients with AF
               (a second report of the same trial, PMID 23229461, is indexed with the same NCT)
The SERVED page's retrieval ledger records only the UID enumerations (the declared registry-first and CT.gov queries
have no execution record behind the served records, which hold no J-ROCKET report). Run now, the declared
registry-first query (AF x 'anticoagulant', PMIDs linked from registry records) does reach 22664783 but not its
subanalysis; the declared CT.gov query ('edoxaban warfarin') cannot, being drug-specific.
This test runs the registered PubMed queries, the registry-first and CT.gov adapters exactly as the build does, and a concept
query (any NOAC x warfarin x AF x RCT publication type), holds the results with sha256, and reports which reach the
named case. Retrieval is the question; eligibility (J-ROCKET's dose and population) is screening's.

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
SLUG = "noac-vs-warfarin-af-stroke"
RUN = os.path.join(HERE, "run")
BROAD = ('(rivaroxaban[tiab] OR apixaban[tiab] OR dabigatran[tiab] OR edoxaban[tiab]) AND warfarin[tiab] '
         'AND "atrial fibrillation"[tiab] AND randomized controlled trial[pt]')
NAMED = {"22664783": "J-ROCKET AF", "23229461": "J-ROCKET AF (second report)"}


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
    # the served ledger, read from the commit (a sparse worktree holds no cache/)
    import subprocess
    led = json.loads(subprocess.run(["git", "-C", ROOT, "show", f"HEAD:cache/{SLUG}/retrieval_ledger.json"],
                                    capture_output=True, check=True).stdout.decode("utf-8"))
    broad = F._esearch(BROAD, 1000)
    named = F._efetch(sorted(NAMED))
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _registry_first_result / _efetch",
                                     "registered_queries": reg, "registry_first": {"config": cfg["registry_first"],
                                     "state": rf["state"], "pmids": rf["ids"]},
                                     "ctgov": {"config": cfg["ctgov"], "ncts": [x["id"] for x in ct]},
                                     "served_ledger_sources": [{"source_id": x.get("source_id"), "kind": x.get("kind"),
                                                                "state": x.get("state"), "query": x.get("query")}
                                                               for x in led.get("sources") or []],
                                     "seed_comparator_refs": cfg.get("seed_comparator_refs"),
                                     "broad_query": BROAD, "broad_pmids": broad, "named_records": named})
    print(f"registered {sum(len(v) for v in reg.values())}; registry-first {len(rf['ids'])} ({rf['state']}); "
          f"broad {len(broad)}; named fetched {len(named)}; sha256 {s[:12]}")


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    rf = set(d["registry_first"]["pmids"])
    broad = set(d["broad_pmids"])
    recs = {str(r["id"]): r for r in d["named_records"]}
    out = {"registered_queries": list(d["registered_queries"]), "registered_n": len(reg),
           "registry_first_n": len(rf), "ctgov_n": len(d["ctgov"]["ncts"]),
           "ctgov_has_NCT00494871": "NCT00494871" in d["ctgov"]["ncts"],
           "served_ledger_kinds": sorted({x["kind"] for x in d["served_ledger_sources"]}), "broad_query": d["broad_query"], "broad_n": len(broad),
           "named_cases": {p: {"trial": n, "title": (recs.get(p) or {}).get("title"), "nct": (recs.get(p) or {}).get("nct"),
                               "in_registered": p in reg, "in_registry_first": p in rf, "in_broad": p in broad}
                           for p, n in NAMED.items()}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
