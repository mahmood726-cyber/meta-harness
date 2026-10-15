"""Review 17 sweep: the comparator denominator before/after `seed_candidate_n` for every topic, with the G1 status before
and after, recomputed by g1_tracker.g1_status on the stored tracker outputs (outputs/k_gap/g1/<slug>.json). Read-only.

    python scripts/g1_comparator_n_sweep.py -> outputs/k_gap/comparator_n_sweep.md
"""
from __future__ import annotations

import copy
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]


def main():
    import g1_tracker as gt
    rows = ["# Comparator N from the INCLUDED set (review 17) -- sweep over every topic; nothing applied", "",
            "| topic | set state | N before | N after | basis after | stated k | G1 before | G1 after |", "|---|---|---|---|---|---|---|---|"]
    for p in sorted(glob.glob(os.path.join(ROOT, "outputs", "k_gap", "g1", "*.json"))):
        o = json.load(open(p, encoding="utf-8"))
        if "N_comparator_trials" not in o:
            continue
        before = gt.g1_status(copy.deepcopy(o))["state"]
        sk = (o.get("comparator_stated_k") or {}).get("k")
        sspan = (o.get("comparator_stated_k") or {}).get("span")
        n0 = o["N_comparator_trials"]
        o2 = gt.seed_candidate_n(copy.deepcopy(o), sk, sspan, o.get("comparator_pmid"))
        after = gt.g1_status(o2)["state"]
        rows.append(f"| {o['slug']} | {(o.get('comparator_set') or {}).get('state')} | {n0} | {o2['N_comparator_trials']} | "
                    f"{o2['N_comparator_trials_basis']} | {sk} | {before} | {after}{' **CHANGED**' if after != before else ''} |")
    out = os.path.join(ROOT, "outputs", "k_gap", "comparator_n_sweep.md")
    open(out, "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
