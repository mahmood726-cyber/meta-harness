"""Regenerate docs/spec_curve.json: the specification curve (RE+HKSJ / RE+z / fixed-effect) per primary
outcome. Deterministic from each review.json; single implementation in harness/spec_curve.py."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.spec_curve import spec_curve  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build():
    out = {"_doc": "Specification curve per primary outcome (RE+HKSJ default / RE+z / fixed-effect). "
                   "Direction & significance stability across the model/interval axis. "
                   "Regenerate via scripts/spec_curve.py; consumed by the index summary."}
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(f))
        sc = spec_curve(json.load(open(f, encoding="utf-8")))
        if sc:
            out[slug] = sc
    return out


if __name__ == "__main__":
    d = build()
    json.dump(d, open(os.path.join(ROOT, "docs", "spec_curve.json"), "w", encoding="utf-8"), indent=1)
    topics = [v for k, v in d.items() if not k.startswith("_") and not v.get("not_applicable")]
    ds = sum(1 for v in topics if v.get("direction_stable"))
    ss = sum(1 for v in topics if v.get("significance_stable"))
    print(f"wrote docs/spec_curve.json: {len(topics)} topics k>=2; direction stable {ds}/{len(topics)}; "
          f"significance stable {ss}/{len(topics)}")
