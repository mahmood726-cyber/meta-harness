"""Primary metric: registry-first RECALL per topic — how many of a topic's KNOWN trials the
committed registry-first enumeration query recovers. This is HARNESS OUTPUT: it regenerates by
re-running the committed query (topics/<slug>.json -> registry_first:{cond,intr}) against the live
registries, NOT a hand-tabulated number.

    python scripts/recall.py            # every topic that declares registry_first
    python scripts/recall.py <slug>     # one topic

For each topic it runs harness.registry_first.registry_first_pmids(cond,intr), forms the KNOWN set
(currently-pooled trial PMIDs from docs/reviews/<slug>/review.json UNION positive_control_pmids), and
reports recall = |KNOWN ∩ enumerated| / |KNOWN| plus the four-state status. Recall is the reach
measurement; whether a recovered trial is eligible/poolable is then the screen's and extractor's job
(a candidate is not an include). Requires network (registries); the number is reproducible by re-running.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from harness import registry_first  # noqa: E402


def _known(slug):
    pmids = set()
    tp = os.path.join(ROOT, "topics", slug + ".json")
    if os.path.exists(tp):
        cfg = json.load(open(tp, encoding="utf-8"))
        pmids.update(str(p) for p in cfg.get("positive_control_pmids", []))
    rp = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
    if os.path.exists(rp):
        rev = json.load(open(rp, encoding="utf-8"))
        for o in rev.get("outcomes", []):
            for t in o.get("trials", []) or []:
                pmids.add(str(t.get("id", "")).replace("PMID ", ""))
    return {p for p in pmids if p.isdigit()}


def _topics_with_registry_first(argv):
    if argv:
        return argv
    out = []
    for f in sorted(os.listdir(os.path.join(ROOT, "topics"))):
        if f.endswith(".json"):
            cfg = json.load(open(os.path.join(ROOT, "topics", f), encoding="utf-8"))
            if cfg.get("registry_first"):
                out.append(f[:-5])
    return out


def recall(slug):
    cfg = json.load(open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8"))
    rf = cfg.get("registry_first") or {}
    if not rf.get("cond") and not rf.get("intr"):
        return {"slug": slug, "status": "NO_REGISTRY_FIRST_QUERY"}
    res = registry_first.registry_first_pmids(rf.get("cond", ""), rf.get("intr", ""))
    enum = set(res.get("pmids", []))
    known = _known(slug)
    found = sorted(known & enum)
    return {"slug": slug, "status": res.get("status"), "enumerated": len(enum),
            "known": len(known), "recovered": len(found),
            "recall": (round(len(found) / len(known), 3) if known else None),
            "missed": sorted(known - enum)}


def main(argv):
    rows = [recall(s) for s in _topics_with_registry_first(argv)]
    if not rows:
        print("no topics declare registry_first:{cond,intr} yet")
        return 0
    print(f"{'topic':40} {'status':10} {'enum':6} {'recall':8} recovered/known")
    for r in rows:
        if r["status"] == "NO_REGISTRY_FIRST_QUERY":
            print(f"{r['slug']:40} (no registry_first query)")
            continue
        print(f"{r['slug']:40} {r['status']:10} {r['enumerated']:<6} "
              f"{str(r['recall']):8} {r['recovered']}/{r['known']}"
              + (f"  missed {r['missed']}" if r.get('missed') else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
