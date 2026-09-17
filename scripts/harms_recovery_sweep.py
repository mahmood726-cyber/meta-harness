"""Write docs/harms_recovery_sweep.json from rebuilt review objects.

The sweep reads committed docs/reviews/*/review.json only. It does not search,
fetch, or infer a new trial set.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import harms  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> int:
    out_path = os.path.join(ROOT, "docs", "harms_recovery_sweep.json")
    out = harms.write_sweep(os.path.join(ROOT, "docs", "reviews"), out_path)
    print(
        f"OUT_WRITTEN {out_path} "
        f"incomplete={out['n_harm_outcomes_rendered_k_lt_reporting_trials']} of {out['N_harm_outcomes']} harm outcomes; "
        f"known_debt={out['n_trials_with_KNOWN_REPORTED_NOT_YET_EXTRACTED']} trials"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
