"""Limitation-object sweep over the committed review objects (evidence generator, read-only).

Writes the two tables the limitations-objects evidence bundle carries, from the tree as it is:
  01-object-counts-32.txt   slug | n objects | by kind | by severity | by evidence_state
  02-legacy-compare-32.txt  slug | blocks on page | objects | matched | unmatched
The comparison is the one tests/test_limitations_legacy_compare.py enforces: every absent/banner
block on the rendered page (honest_ratchet.blocks) must match exactly one limitation object by
rendered text, and vice versa. A row with unmatched != 0 is a finding, never rounded away.

Usage: python scripts/limitations_sweep.py [--out docs/evidence/limitations-objects-2026-09-14]
"""
from __future__ import annotations
import argparse
import io
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import honest_ratchet  # noqa: E402
from harness.limitations import build_limitations  # noqa: E402
from harness.page import render_page  # noqa: E402


def _counts(items) -> str:
    return ", ".join(f"{k}={v}" for k, v in sorted(Counter(items).items()))


def sweep() -> tuple[list[str], list[str], int]:
    counts_rows = ["slug | n objects | by kind | by severity | by evidence_state"]
    compare_rows = ["slug | blocks on page | objects | matched | unmatched"]
    total = 0
    reviews_dir = os.path.join(ROOT, "docs", "reviews")
    for slug in sorted(os.listdir(reviews_dir)):
        path = os.path.join(reviews_dir, slug, "review.json")
        if not os.path.isfile(path):
            continue
        review = json.load(open(path, encoding="utf-8"))
        objs = build_limitations(review)
        total += len(objs)
        counts_rows.append(
            f"{slug} | {len(objs)} | {_counts(o['kind'] for o in objs)} | "
            f"{_counts(o['severity'] for o in objs)} | {_counts(o['evidence_state'] for o in objs)}")
        page_texts = Counter(b["text"] for b in honest_ratchet.blocks(render_page(review)))
        obj_texts = Counter(b["text"] for o in objs for b in honest_ratchet.blocks(o["rendered_text"]))
        matched = sum((page_texts & obj_texts).values())
        unmatched = sum((page_texts - obj_texts).values()) + sum((obj_texts - page_texts).values())
        compare_rows.append(f"{slug} | {sum(page_texts.values())} | {len(objs)} | {matched} | {unmatched}")
    return counts_rows, compare_rows, total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("docs", "evidence", "limitations-objects-2026-09-14"))
    args = ap.parse_args(argv)
    counts_rows, compare_rows, total = sweep()
    out = os.path.join(ROOT, args.out)
    with open(os.path.join(out, "01-object-counts-32.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(counts_rows) + "\n")
    with open(os.path.join(out, "02-legacy-compare-32.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(compare_rows) + "\n")
    n_bad = sum(1 for r in compare_rows[1:] if not r.endswith("| 0"))
    print(f"limitations sweep: {len(counts_rows) - 1} topics, {total} objects, {n_bad} topics with unmatched blocks")
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
