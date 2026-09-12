"""Corpus-wide summary of the RoB-stratified sensitivity re-pool. The per-review data now lives IN each
review.json (harness.rob_sensitivity.sensitivity, computed in the pipeline and gate-reproduced); this
script just prints the corpus view for inspection. Single implementation in harness/rob_sensitivity.py."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import rob_sensitivity as rs  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    topics = 0
    rated = pooled = covered = anyhigh = 0
    informative = []
    for f in sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json"))):
        slug = os.path.basename(os.path.dirname(f))
        r = json.load(open(f, encoding="utf-8"))
        s = r.get("rob_sensitivity") or rs.sensitivity(r)
        if not s:
            continue
        topics += 1
        rated += s["n_rob_rated"]
        pooled += s["n_trials"]
        covered += 1 if s["rob_covered"] else 0
        anyhigh += 1 if s.get("any_high") else 0
        if s["low_only_informative"]:
            informative.append((slug, s["full"], s["low_only"]))
    print(f"topics with a primary-outcome sensitivity: {topics}")
    print(f"RoB coverage of pooled primary trials: {rated}/{pooled}; {covered}/{topics} topics fully covered; "
          f"topics with any 'high'-RoB trial: {anyhigh}")
    print("low-only re-pool (informative):")
    for slug, f, lo in informative:
        print(f"  {slug}: full k={f['k']} {f['estimate']} [{f['ci_low']},{f['ci_high']}] "
              f"-> low-only k={lo['k']} {lo['estimate']} [{lo['ci_low']},{lo['ci_high']}]")


if __name__ == "__main__":
    main()
