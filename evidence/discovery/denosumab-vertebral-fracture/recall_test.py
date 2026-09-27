"""V1.1 discovery recall test, denosumab-vertebral-fracture: does the registered TITLE query miss BMD-focused trials that
report vertebral fractures?

The registered PubMed query is
    denosumab[Title] AND prevention[Title] AND fractures[Title] AND postmenopausal[Title] AND osteoporosis[Title]
(plus FREEDOM by uid). A trial whose title is about bone mineral density -- Koh 2016 (PMID 27189284, NCT01457950), a
Korean placebo-controlled denosumab RCT with a BMD primary endpoint that also reports new vertebral fractures -- can
never match five title terms. This test runs the registered query and a broader one (denosumab x postmenopausal x
osteoporosis/BMD, randomized controlled trial publication type) through the harness's own PubMed adapters, holds
both results with sha256, and lists the records the broad query finds that the registered one misses, restricted to
placebo-controlled denosumab RCTs whose abstract reports vertebral fractures.

usage: python recall_test.py fetch   (network, once; writes run/)
       python recall_test.py check   (offline; writes run/RECALL_RESULT.json)
"""
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, ROOT)
SLUG = "denosumab-vertebral-fracture"
RUN = os.path.join(HERE, "run")
REGISTERED = ("denosumab[Title] AND prevention[Title] AND fractures[Title] AND postmenopausal[Title] AND "
              "osteoporosis[Title]")
BROAD = ("denosumab[tiab] AND (postmenopausal[tiab] OR osteoporosis[tiab] OR \"bone mineral density\"[tiab] OR "
         "osteopenia[tiab]) AND randomized controlled trial[pt]")
NAMED_CASE = "27189284"      # Koh 2016, NCT01457950: BMD-focused, reports vertebral fractures


def _write(name, obj):
    os.makedirs(RUN, exist_ok=True)
    b = (json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    open(os.path.join(RUN, name), "wb").write(b)
    return hashlib.sha256(b).hexdigest()


def fetch():
    from harness import fetch as F
    t0 = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    reg = F._esearch(REGISTERED, 200)
    broad = F._esearch(BROAD, 500)
    extra = sorted(set(broad) - set(reg))
    recs = F._efetch(extra) if extra else []
    s = _write("recall_fetch.json", {"retrieved_utc": t0, "adapter": "harness.fetch._esearch / _efetch",
                                     "registered_query": REGISTERED, "registered_pmids": reg,
                                     "broad_query": BROAD, "broad_pmids": broad, "records_broad_only": recs})
    print(f"registered {len(reg)}; broad {len(broad)}; broad-only fetched {len(recs)}; sha256 {s[:12]}")


_VF = re.compile(r"\bvertebral fractures?\b|\bnew (?:radiographic |morphometric )?vertebral\b", re.I)


def check():
    d = json.load(open(os.path.join(RUN, "recall_fetch.json"), encoding="utf-8"))
    hits = []
    for r in d["records_broad_only"]:
        text = f"{r.get('title') or ''} {r.get('abstract') or ''}"
        rct = "Randomized Controlled Trial" in (r.get("pubtypes") or [])
        pbo = bool(re.search(r"\bplacebo\b", text, re.I))
        vf = _VF.search(text)
        if rct and pbo and vf:
            hits.append({"pmid": str(r["id"]), "title": r.get("title"), "year": r.get("year"), "nct": r.get("nct"),
                         "vertebral_fracture_span": text[max(0, vf.start() - 120): vf.end() + 120]})
    out = {"registered_query": d["registered_query"], "registered_n": len(d["registered_pmids"]),
           "broad_query": d["broad_query"], "broad_n": len(d["broad_pmids"]),
           "missed_by_registered_query": hits, "missed_n": len(hits),
           "named_case": {"pmid": NAMED_CASE, "in_registered": NAMED_CASE in d["registered_pmids"],
                          "in_broad": NAMED_CASE in d["broad_pmids"],
                          "reports_vertebral_fracture": any(h["pmid"] == NAMED_CASE for h in hits)}}
    _write("RECALL_RESULT.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "missed_by_registered_query"}, indent=1))
    for h in hits:
        print(" ", h["pmid"], h["year"], (h["title"] or "")[:110])


if __name__ == "__main__":
    {"fetch": fetch, "check": check}[sys.argv[1]]()
