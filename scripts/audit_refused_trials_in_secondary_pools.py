"""FINDING (not a guard): non-primary pooled rows from trials the topic's refusal registry refuses.

docs/refusals.json names trials a topic refuses, with a reason written about the PRIMARY outcome, and
claimgraph._refused_and_pooled enforces it on the primary pool only. A refused trial can therefore still pool in a
secondary or harm outcome. Sometimes that is right (the refusal reason is specific to the primary composite or its
scale); sometimes the reason is scope that applies to every outcome (COLCHICINE-PCI, dropped from packet v3 on
2026-10-02). Widening the claimgraph check would silently refuse rows served on main whose refusal reasons do not
apply to them, so each row is listed for adjudication instead.

Usage: python scripts/audit_refused_trials_in_secondary_pools.py [--json OUT]
Prints one line per finding and "n of N" (N = pooled non-primary rows in the corpus).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import claimgraph  # noqa: E402


def findings(root: str = ROOT) -> tuple[list[dict], int]:
    registry = json.load(open(os.path.join(root, "docs", "refusals.json"), encoding="utf-8"))
    out, total = [], 0
    for path in sorted(glob.glob(os.path.join(root, "docs", "reviews", "*", "review.json"))):
        review = json.load(open(path, encoding="utf-8"))
        slug = review["slug"]
        rows = [r for r in (registry.get(slug) or []) if not r.get("unrenderable")]
        for outcome in review.get("outcomes") or []:
            if outcome.get("primary"):
                continue
            pooled = {claimgraph.trial_key(t): t for t in outcome.get("trials") or [] if claimgraph.trial_key(t)}
            total += len(pooled)
            for row in rows:
                for key in sorted(claimgraph._keys_from_registry_row(row) & set(pooled)):
                    out.append({"slug": slug, "outcome": outcome["name"], "kind": outcome.get("kind"), "trial": key,
                                "registry_trial": row.get("trial"),
                                "refusal_reason": row.get("not_pooled_because"),
                                "adjudication": "OWED"})
    return out, total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json")
    a = ap.parse_args(argv)
    found, total = findings()
    for f in found:
        print(f"FINDING {f['slug']} | {f['outcome']} ({f['kind']}) | {f['trial']} | refused because: {f['refusal_reason']}")
    print(f"{len(found)} of {total} pooled non-primary rows come from a trial the topic refuses for the primary")
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"findings": found, "n": len(found), "N": total}, fh, indent=1, ensure_ascii=False)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
