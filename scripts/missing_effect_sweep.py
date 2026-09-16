"""Count missing-effect invalidation classes across committed review pages.

Usage: python scripts/missing_effect_sweep.py [--out docs/missing_effect_sweep.json]
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

from harness import missing_effect  # noqa: E402


def _load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default


def sweep():
    reviews_dir = os.path.join(ROOT, "docs", "reviews")
    known = _load_json(os.path.join(ROOT, "docs", "known_eligible_missing.json"), {})
    topics = (known.get("topics") or {}) if isinstance(known, dict) else {}
    rows = []
    class_counts = Counter()
    pages_with_known_missing = 0
    pages_with_verifiable_effect = 0
    pages_with_reversal = 0
    known_missing_page_names = []
    verifiable_effect_page_names = []
    reversal_page_names = []

    for slug in sorted(os.listdir(reviews_dir)):
        review_path = os.path.join(reviews_dir, slug, "review.json")
        if not os.path.isfile(review_path):
            continue
        review = _load_json(review_path, {})
        raw = list(topics.get(slug) or [])
        if raw:
            pages_with_known_missing += 1
            known_missing_page_names.append(slug)
        enriched = missing_effect.enrich_from_cache(ROOT, slug, raw)
        annotated = missing_effect.annotate(review, enriched)
        if any(r.get("effect") is not None for r in annotated):
            pages_with_verifiable_effect += 1
            verifiable_effect_page_names.append(slug)
        if any(
            r.get("missing_evidence_effect")
            in {missing_effect.REVERSES_TO_EFFECT, missing_effect.REVERSES_TO_NULL}
            for r in annotated
        ):
            pages_with_reversal += 1
            reversal_page_names.append(slug)
        for row in annotated:
            klass = row.get("missing_evidence_effect") or missing_effect.NOT_ESTIMABLE
            class_counts[klass] += 1
            rows.append(
                {
                    "slug": slug,
                    "trial": row.get("trial"),
                    "status": row.get("status"),
                    "mechanism": row.get("mechanism"),
                    "class": klass,
                    "has_source_verified_effect": row.get("effect") is not None,
                    "basis": row.get("missing_evidence_basis"),
                    "repool": row.get("missing_evidence_repool"),
                }
            )

    pages_total = sum(
        1
        for slug in os.listdir(reviews_dir)
        if os.path.isfile(os.path.join(reviews_dir, slug, "review.json"))
    )
    return {
        "generated_utc": "2026-09-16",
        "pages_total": pages_total,
        "known_missing_entries": len(rows),
        "pages_with_known_missing": pages_with_known_missing,
        "pages_with_known_missing_names": known_missing_page_names,
        "entries_with_verifiable_effect": sum(1 for r in rows if r["has_source_verified_effect"]),
        "pages_with_verifiable_effect": pages_with_verifiable_effect,
        "pages_with_verifiable_effect_names": verifiable_effect_page_names,
        "pages_with_reversal": pages_with_reversal,
        "pages_with_reversal_names": reversal_page_names,
        "zero_verifiable_effect_reason": (
            "known-missing rows did not carry identifiers matching source-verified effect overrides in cache"
            if rows and not verifiable_effect_page_names else None
        ),
        "class_distribution": dict(sorted(class_counts.items())),
        "rows": rows,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("docs", "missing_effect_sweep.json"))
    args = ap.parse_args(argv)
    result = sweep()
    out = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(
        "missing-effect sweep: "
        f"{result['pages_total']} pages, {result['known_missing_entries']} entries, "
        f"{result['entries_with_verifiable_effect']} with source-verified effects, "
        f"{result['pages_with_reversal']} pages with reversal classes"
    )
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    raise SystemExit(main())
