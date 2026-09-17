"""Write the design-refusal consumption sweep over served review objects.

Usage: python scripts/design_refusal_sweep.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"
OUT = ROOT / "docs" / "design_refusal_sweep.json"


def _primary(review: dict[str, Any]) -> dict[str, Any]:
    outcomes = review.get("outcomes") or []
    return next((o for o in outcomes if o.get("primary")), outcomes[0] if outcomes else {})


def _declared_protocol_estimand(review: dict[str, Any], outcome: dict[str, Any]) -> str:
    return str(
        outcome.get("estimand")
        or (review.get("protocol") or {}).get("estimand")
        or (review.get("method_declared") or "")
    ).upper()


def _mixes_estimands(review: dict[str, Any], outcome: dict[str, Any]) -> bool:
    res = outcome.get("result") or {}
    em = res.get("estmeasure") or {}
    declared = _declared_protocol_estimand(review, outcome)
    labels = {str(x).upper() for x in (em.get("labels") or []) if x}
    if em.get("status") == "incompatible":
        return True
    if declared and labels and any(label != declared for label in labels):
        return True
    canonicals = {str(x).upper() for x in (em.get("canonicals") or []) if x}
    return len(canonicals) > 1


def _has_design_adjusted_effect(row: dict[str, Any]) -> bool:
    design = row.get("design") if isinstance(row.get("design"), dict) else {}
    corr = design.get("correlation_handling") or {}
    alt = design.get("published_alternative") or row.get("published_alternative") or {}
    method = str(corr.get("method") or "")
    return bool(
        row.get("design_adjusted_variance")
        or row.get("selected_estimator") == "published_adjusted"
        or (alt.get("adjusted") and alt.get("span"))
        or method in {"published_model", "published_adjusted_SE", "reconstructed_with_ICC"}
    )


def _page_row(path: Path) -> dict[str, Any]:
    review = json.loads(path.read_text(encoding="utf-8"))
    slug = path.parent.name
    primary = _primary(review)
    dc = primary.get("design_consumption") or {}
    refused = primary.get("design_refusals") or []
    by_design = Counter(str(r.get("design") or "UNKNOWN") for r in refused)
    adjusted = Counter("held" if _has_design_adjusted_effect(r) else "not_held" for r in refused)
    eligible = dc.get("eligible_with_outcome")
    if eligible is None:
        eligible = len(primary.get("trials") or []) + len(refused)
    consumable = dc.get("consumable_k")
    if consumable is None:
        consumable = len(primary.get("trials") or [])
    return {
        "slug": slug,
        "eligible_with_outcome": eligible,
        "consumable_k": consumable,
        "design_refused": len(refused),
        "by_design": dict(sorted(by_design.items())),
        "by_design_adjusted_effect_held": dict(sorted(adjusted.items())),
        "headline_k_is_consumable_subset": "subset this engine can safely consume" in str(dc.get("headline") or ""),
        "mixes_estimands_against_declared_protocol_estimand": _mixes_estimands(review, primary),
    }


def main() -> int:
    pages = [_page_row(path) for path in sorted(REVIEWS.glob("*/review.json"))]
    total_refused = sum(row["design_refused"] for row in pages)
    total_eligible = sum(int(row["eligible_with_outcome"] or 0) for row in pages)
    by_design: Counter[str] = Counter()
    by_adjusted: Counter[str] = Counter()
    for row in pages:
        by_design.update(row["by_design"])
        by_adjusted.update(row["by_design_adjusted_effect_held"])
    payload = {
        "n_pages": len(pages),
        "design_refused_trials_of_eligible_with_outcome_trials": {
            "n": total_refused,
            "N": total_eligible,
        },
        "by_design": dict(sorted(by_design.items())),
        "by_design_adjusted_effect_held": dict(sorted(by_adjusted.items())),
        "n_pages_headline_k_is_consumable_subset_of_32": {
            "n": sum(1 for row in pages if row["headline_k_is_consumable_subset"]),
            "N": len(pages),
        },
        "n_pages_mixing_estimands_against_declared_protocol_estimand_of_32": {
            "n": sum(1 for row in pages if row["mixes_estimands_against_declared_protocol_estimand"]),
            "N": len(pages),
        },
        "pages": pages,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
