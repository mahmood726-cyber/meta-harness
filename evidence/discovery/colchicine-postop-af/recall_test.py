"""V1.1 discovery recall test, colchicine-postop-af.

The registered PubMed queries are concept searches that require the words 'atrial fibrillation' (or the phrase
'colchicine prevention postoperative atrial fibrillation placebo randomized'). A cardiac-surgery colchicine trial that
reports postoperative AF only as a secondary outcome, without those words in its title/abstract fields, would be
missed. This test runs them and a second concept query (colchicine x cardiac surgery terms x randomised) through the
harness's own PubMed adapters and holds both results, plus every concept-query record, with sha256. Which records are
eligible trials is decided by a blind screen of the held records (screen/), verified against each record.

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
SLUG = "colchicine-postop-af"
RUN = os.path.join(HERE, "run")
BROAD = ('colchicine[tiab] AND ("cardiac surgery"[tiab] OR "heart surgery"[tiab] OR "coronary artery bypass"[tiab] '
         'OR CABG[tiab] OR valve[tiab] OR pericardiotomy[tiab] OR postpericardiotomy[tiab] OR "open heart"[tiab] '
         'OR "postoperative"[tiab]) AND (randomized controlled trial[pt] OR randomi*[tiab])')
NAMED = {"36747296": "non-CABG colchicine RCT", "25784519": "on-pump CABG myocardial damage RCT",
         "32175647": "constrictive physiology RCT", "12574898": "PPS prevention RCT (2002)"}
# pinned from screen/VERIFIED.json: a blind codex screen of the held records, each call verified against its record


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
    recs = []
    for i in range(0, len(broad), 100):
        recs += F._efetch(broad[i:i + 100])
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _efetch",
                                     "registered_queries": reg, "broad_query": BROAD, "broad_pmids": broad,
                                     "broad_records": recs})
    print(f"registered {sum(len(v) for v in reg.values())}; broad {len(broad)}; records {len(recs)}; sha256 {s[:12]}")


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    reg = set().union(*[set(v) for v in d["registered_queries"].values()])
    broad = set(d["broad_pmids"])
    recs = {str(r["id"]): r for r in d["broad_records"]}
    out = {"registered_queries": list(d["registered_queries"]), "registered_n": len(reg), "registered_pmids": sorted(reg),
           "broad_query": d["broad_query"], "broad_n": len(broad),
           "registered_not_in_broad": sorted(reg - broad),
           "named_cases": {p: {"trial": n, "title": (recs.get(p) or {}).get("title"),
                               "in_registered": p in reg, "in_broad": p in broad} for p, n in NAMED.items()}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "named_cases"}, indent=1))


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
