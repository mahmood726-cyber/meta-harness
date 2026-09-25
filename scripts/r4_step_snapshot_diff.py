"""Combined radius of r4_ambiguity_step.py: diff two regex_layer.radius snapshots (unpatched tree vs stepped tree) and
check every differing extraction against (a) the served rows of the committed pages and (b) the union of the per-site
radius rows the step's sites were measured to have (outputs/regex_layer/RADIUS_r4_<site>.json).

  REGEX_LAYER_DATA_ROOT=<data> python scripts/r4_step_snapshot_diff.py <before.json> <after.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from regex_layer import radius  # noqa: E402

STEP_SITES = ["arm_den", "arm_samepos", "cont_pairs", "rate_pairs", "denom_each", "sent_arm", "sent_rate",
              "sent_cont"]


def main(b: str, a: str) -> int:
    before = json.loads(Path(b).read_text(encoding="utf-8"))
    after = json.loads(Path(a).read_text(encoding="utf-8"))
    assert set(before) == set(after), "snapshots cover different extractions"
    diff = sorted(k for k in before if before[k] != after[k])
    served = set()
    for k in diff:
        slug, rid, src, outc = k.split("|", 3)
        if (rid, src, outc) in radius.served_keys(slug):
            served.add(k)
    union = set()
    for s in STEP_SITES:
        for r in json.loads((ROOT / "outputs" / "regex_layer" / f"RADIUS_r4_{s}.json").read_text(encoding="utf-8"))["rows"]:
            union.add("|".join((r["slug"], r["id"], r["source"], r["outcome"])))
    print(f"extractions {len(before)}; differ {len(diff)}; served {len(served)}; per-site union {len(union)}; "
          f"differ not in union {len(set(diff) - union)}; union not in differ {len(union - set(diff))}")
    for k in diff:
        print(("SERVED " if k in served else "") + k, "|", before[k][:160], "->", after[k][:160])
    return 1 if served else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
