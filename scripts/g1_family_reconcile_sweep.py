"""Sweep for harness.trial_family.reconcile_family_eligibility over every served topic: eligible families before/after
and the demoted family ids, from the served review.json (read-only; the captain's regeneration applies it).

    python scripts/g1_family_reconcile_sweep.py -> outputs/k_gap/family_reconcile_sweep.md
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def main():
    from harness import trial_family as tf
    ab = {t["slug"] for t in json.load(open(os.path.join(ROOT, "registry", "g1_abandoned.json"), encoding="utf-8"))
          .get("topics", [])}
    rows = ["# Family-eligibility reconcile gate: 32-topic sweep (served review.json; nothing applied)", "",
            "| topic | active | eligible families before | after | demoted (structural-only, no included record) |",
            "|---|---|---|---|---|"]
    for slug in sorted(os.listdir(os.path.join(ROOT, "docs", "reviews"))):
        p = os.path.join(ROOT, "docs", "reviews", slug, "review.json")
        if not os.path.exists(p):
            continue
        r = json.load(open(p, encoding="utf-8"))
        nodes = copy.deepcopy(r.get("trial_families") or [])
        before = sum((f.get("eligibility") or {}).get("state") == "ELIGIBLE" for f in nodes)
        dem = tf.reconcile_family_eligibility(r, nodes)
        rows.append(f"| {slug} | {'no' if slug in ab else 'yes'} | {before} | {before - len(dem)} | "
                    f"{', '.join(dem) if len(dem) <= 8 else ', '.join(dem[:8]) + f' (+{len(dem) - 8})'} |")
    out = os.path.join(ROOT, "outputs", "k_gap", "family_reconcile_sweep.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
