"""Sweep live topic pages for membership-consumer disagreements.

Writes docs/membership_consistency_sweep.json with one row per live topic.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import membership  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path):
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _parity_rows() -> dict[str, dict]:
    path = ROOT / "docs" / "parity.json"
    if not path.exists():
        return {}
    return {str(row.get("slug")): row for row in _load_json(path)}


def _primary(review: dict) -> dict:
    return next((o for o in review.get("outcomes", []) or [] if o.get("primary")), {})


def _row(slug: str, review: dict, raw_parity: dict | None) -> dict:
    prim = _primary(review)
    mem = membership.outcome_membership(prim, review) if prim else {}
    annotated_parity = membership.annotate_parity(raw_parity, review)
    check_review = dict(review)
    if annotated_parity:
        repro = dict(check_review.get("reproduction") or {})
        repro["parity"] = annotated_parity
        check_review["reproduction"] = repro
    violations = membership.consistency_violations(check_review)
    stale_conflicts = membership.parity_conflicts(raw_parity, prim, mem) if raw_parity and prim else []
    if violations:
        verdict = "DISAGREE: " + ", ".join(v["code"] for v in violations)
    elif stale_conflicts:
        verdict = "OK_STALE_PARITY_UNRENDERABLE"
    else:
        verdict = "OK"
    return {
        "slug": slug,
        "outcome": prim.get("name"),
        "pooled_k": len(mem.get("pooled") or []),
        "integrity_n_pooled": (review.get("integrity") or {}).get("n_pooled"),
        "rob_levels_rated": (review.get("rob_sensitivity") or {}).get("n_rob_rated"),
        "parity_text_k": (raw_parity or {}).get("our_k"),
        "verdict": verdict,
        "violations": violations,
        "stale_parity_suppressed": bool(stale_conflicts),
    }


def main() -> int:
    parity = _parity_rows()
    rows = []
    for review_path in sorted((ROOT / "docs" / "reviews").glob("*/review.json")):
        slug = review_path.parent.name
        review = _load_json(review_path)
        rows.append(_row(slug, review, parity.get(slug)))
    n_disagree = sum(1 for row in rows if row["violations"])
    out = {
        "summary": {
            "topics_disagreeing": n_disagree,
            "topics_total": len(rows),
            "statement": f"{n_disagree} topics disagreeing of {len(rows)}",
        },
        "rows": rows,
    }
    dest = ROOT / "docs" / "membership_consistency_sweep.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out["summary"]["statement"])
    return 1 if n_disagree else 0


if __name__ == "__main__":
    raise SystemExit(main())

