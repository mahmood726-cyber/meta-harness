"""Provenance mix of pooled numbers (tracked metric per the abstract-dominance weakness): how many pooled
values come from the abstract vs higher structured/full-text/verified tiers. Regenerable; consumed by the
index. Driving the abstract share DOWN (structured/full-text up) is the tracked goal."""
import glob
import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    prov = Counter()
    for f in glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json")):
        r = json.load(open(f, encoding="utf-8"))
        for o in r.get("outcomes", []):
            for t in o.get("trials", []):
                if t.get("effect") is not None or t.get("mean1") is not None or t.get("ai") is not None:
                    prov[t.get("provenance") or "unknown"] += 1
    tot = sum(prov.values())
    abstract = prov.get("abstract", 0)
    return {"_doc": "Provenance mix of pooled numbers. abstract = the authors' headline (weakest source, "
                    "safest default); the rest are higher tiers (CT.gov structured, PMC full text, hand-"
                    "verified). The tracked goal is to drive the abstract share down.",
            "total": tot, "abstract": abstract, "non_abstract": tot - abstract,
            "by_provenance": dict(prov.most_common())}


if __name__ == "__main__":
    d = build()
    json.dump(d, open(os.path.join(ROOT, "docs", "provenance.json"), "w", encoding="utf-8"), indent=1)
    print(f"abstract {d['abstract']}/{d['total']} ; non-abstract {d['non_abstract']}: {dict(d['by_provenance'])}")
