"""Sweep OR/RR-HR incompatibilities across committed review objects.

Outputs docs/or_class_sweep.json with:
  * any pooled outcome whose estmeasure labels mix OR with RR/HR;
  * any external comparator row where the comparator estimate is OR and ours is RR/HR.

The script is offline: it reads only committed/generated JSON already in the clone.
"""
from __future__ import annotations

import glob
import json
import os
from typing import Any


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RATIO_RISK_HAZARD = {"RR", "HR"}


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _norm(label: Any) -> str:
    return str(label or "").upper()


def _mixed_or_outcomes() -> tuple[list[dict[str, Any]], int]:
    rows: list[dict[str, Any]] = []
    paths = sorted(glob.glob(os.path.join(ROOT, "docs", "reviews", "*", "review.json")))
    for path in paths:
        slug = os.path.basename(os.path.dirname(path))
        review = _load_json(path)
        for outcome in review.get("outcomes") or []:
            result = outcome.get("result") or {}
            em = result.get("estmeasure") or {}
            labels = {_norm(x) for x in (em.get("labels") or [])}
            if "OR" not in labels or not (labels & RATIO_RISK_HAZARD):
                continue
            rows.append({
                "slug": slug,
                "outcome": outcome.get("name"),
                "primary": bool(outcome.get("primary")),
                "k": result.get("k"),
                "scale": result.get("scale"),
                "status": em.get("status"),
                "classes": em.get("classes") or [],
                "canonicals": em.get("canonicals") or [],
                "labels": sorted(labels),
                "suppressed_incompatible": bool(result.get("suppressed_incompatible")),
                "has_pooled_estimate": result.get("estimate") is not None,
            })
    return rows, len(paths)


def _external_or_vs_rrhr() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = os.path.join(ROOT, "docs", "external_agreement.json")
    data = _load_json(path)
    rows: list[dict[str, Any]] = []
    for row in data.get("rows") or []:
        ours = _norm(row.get("our_scale"))
        theirs = _norm(row.get("their_scale"))
        if theirs == "OR" and ours in RATIO_RISK_HAZARD:
            rows.append({
                "slug": row.get("slug"),
                "our_scale": row.get("our_scale"),
                "their_scale": row.get("their_scale"),
                "category": row.get("category"),
                "same_question": row.get("same_question"),
                "agree_within_12pct": row.get("agree_within_12pct"),
                "direction_consistent": row.get("direction_consistent"),
            })
    confirmation = {
        "external_rows": len(data.get("rows") or []),
        "or_comparator_vs_rrhr_pool": len(rows),
        "all_suppressed_as_cross_estimand": all(
            str(r.get("category") or "").startswith("cross_estimand")
            and r.get("same_question") is False
            and r.get("agree_within_12pct") is False
            for r in rows
        ),
        "same_estimand_agree": data.get("same_estimand_agree"),
        "agree_within_12pct": data.get("agree_within_12pct"),
    }
    return rows, confirmation


def build() -> dict[str, Any]:
    mixed, n_topics = _mixed_or_outcomes()
    external_rows, confirmation = _external_or_vs_rrhr()
    return {
        "_doc": (
            "OR class sweep: pooled outcome rows that mix OR with RR/HR, plus external comparator "
            "rows where the comparator reports OR against our RR/HR pool. OR-vs-RR/HR requires an "
            "explicit source-backed conversion; absent that, the pool or agreement claim is suppressed."
        ),
        "topics_scanned": n_topics,
        "mixed_or_with_rrhr_outcomes": mixed,
        "mixed_or_with_rrhr_outcome_count": len(mixed),
        "external_agreement_or_comparator_vs_rrhr_pool": external_rows,
        "external_agreement_confirmation": confirmation,
    }


def main() -> None:
    out = build()
    out_path = os.path.join(ROOT, "docs", "or_class_sweep.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(
        "OR class sweep: "
        f"{out['mixed_or_with_rrhr_outcome_count']} mixed pooled outcome(s) across "
        f"{out['topics_scanned']} topics; "
        f"{out['external_agreement_confirmation']['or_comparator_vs_rrhr_pool']} external OR-vs-RR/HR row(s); "
        "cross-estimand suppressed="
        f"{out['external_agreement_confirmation']['all_suppressed_as_cross_estimand']}"
    )


if __name__ == "__main__":
    main()
