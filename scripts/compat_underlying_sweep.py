from __future__ import annotations

import collections
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import compat_check  # noqa: E402


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _records(slug: str) -> dict:
    return _load(ROOT / "cache" / slug / "records.json")


def _owed_markers(review: dict) -> list[dict]:
    out = []
    for lim in review.get("limitations") or []:
        if not isinstance(lim, dict):
            continue
        ack = lim.get("unwired_acknowledged") or {}
        text = " ".join(str(x or "") for x in (lim.get("kind"), lim.get("evidence_state"), ack.get("reason")))
        if "OWED a consumer" in text or "owed a consumer" in text:
            out.append({
                "limitation_id": lim.get("limitation_id"),
                "kind": lim.get("kind"),
                "reason": ack.get("reason"),
            })
    return out


def _registry_unknown_rows(review: dict) -> list[dict]:
    rows = []
    for outcome in review.get("outcomes") or []:
        for trial in outcome.get("trials") or []:
            d = trial.get("design") or {}
            action = d.get("design_action") or {}
            if d.get("design") == "UNKNOWN" or "UNKNOWN is not PARALLEL" in str(action.get("reason")):
                rows.append({
                    "outcome": outcome.get("name"),
                    "trial_id": trial.get("id"),
                    "design": d.get("design"),
                    "reason": action.get("reason"),
                })
    return rows


def _harm_panels(review: dict) -> list[dict]:
    panels = []
    for outcome in review.get("outcomes") or []:
        if outcome.get("kind") != "harm":
            continue
        hi = outcome.get("harms_incomplete") or {}
        result = outcome.get("result") or {}
        if hi or result.get("state") == compat_check.HARMS_INCOMPLETE:
            panels.append({
                "outcome": outcome.get("name"),
                "state": compat_check.HARMS_INCOMPLETE,
                "n_reporting_pool_trials": hi.get("n_reporting_pool_trials") or result.get("n_reporting_pool_trials"),
                "n_pooled": hi.get("n_pooled") or result.get("n_pooled"),
                "unresolved": hi.get("unresolved") or result.get("known_eligible_outcome_reports_unresolved") or [],
            })
    return panels


def main() -> int:
    review_paths = sorted((ROOT / "docs" / "reviews").glob("*/review.json"))
    pages = []
    by_dimension = collections.Counter()
    underivable = 0
    harms = []
    unknown_rows = []
    owed = []
    for path in review_paths:
        review = _load(path)
        slug = review.get("slug") or path.parent.name
        records = _records(slug)
        violations = compat_check.check(review, records)
        asserted = [v for v in violations if v.get("code") == compat_check.ASSERTED_NOT_UNDERLYING]
        for v in asserted:
            by_dimension[v.get("dimension")] += 1
        underivable += sum(1 for v in violations if v.get("code") == compat_check.UNDERIVABLE)
        panels = _harm_panels(review)
        harms.extend({"slug": slug, **p} for p in panels)
        urows = _registry_unknown_rows(review)
        unknown_rows.extend({"slug": slug, **r} for r in urows)
        markers = _owed_markers(review)
        owed.extend({"slug": slug, **m} for m in markers)
        pages.append({
            "slug": slug,
            "n_violations": len(asserted),
            "violations_by_dimension": dict(collections.Counter(v.get("dimension") for v in asserted)),
            "n_underivable": sum(1 for v in violations if v.get("code") == compat_check.UNDERIVABLE),
            "harms_incomplete_panels": panels,
            "registry_unknown_rows": len(urows),
            "owed_consumer_markers": len(markers),
        })
    out = {
        "n_pages": len(pages),
        "n_pages_with_ge1_violation": sum(1 for p in pages if p["n_violations"]),
        "n_violations_by_dimension": dict(sorted(by_dimension.items())),
        "n_underivable": underivable,
        "pages": pages,
        "harms": {
            "n_panels_rendering_k_lt_reporting_pool_trials": len(harms),
            "panels": harms,
        },
        "registry_unknown": {
            "n_rows_where_unknown_design_is_visible": len(unknown_rows),
            "rows": unknown_rows,
        },
        "owed_consumer_markers": {
            "n_markers_outstanding": len(owed),
            "markers": owed,
        },
    }
    dest = ROOT / "docs" / "compat_underlying_sweep.json"
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)}")
    print(f"pages with >=1 violation: {out['n_pages_with_ge1_violation']} of {out['n_pages']}")
    print(f"violations by dimension: {out['n_violations_by_dimension']}")
    print(f"underivable: {out['n_underivable']}")
    print(f"harms incomplete panels: {out['harms']['n_panels_rendering_k_lt_reporting_pool_trials']}")
    print(f"owed markers: {out['owed_consumer_markers']['n_markers_outstanding']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
