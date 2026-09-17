"""Sweep funding disclosure recovery across committed review pages.

Offline only: reads docs/reviews/*/review.json, cache/*/records.json, and local AACT sponsor tables.
Writes docs/funding_sweep.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import aact, funding  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "docs" / "reviews"
BASE = os.environ.get("FUNDING_SWEEP_BASE", "ad5e7c66")


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _cache(slug: str) -> dict:
    return _load_json(ROOT / "cache" / slug / "records.json")


def _git_show_json(ref: str, path: str) -> dict:
    import subprocess

    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT, text=True, encoding="utf-8")
    return json.loads(raw)


def _rec_by_id(records: dict) -> dict[str, dict]:
    return {str(row["id"]): row for row in (records.get("records") or []) + (records.get("ctgov") or [])}


def _pooled_trials(review: dict) -> list[dict]:
    seen, out = set(), []
    for outcome in review.get("outcomes") or []:
        for trial in outcome.get("trials") or []:
            raw = str(trial.get("id", "")).replace("PMID ", "").strip()
            if raw and raw not in seen:
                seen.add(raw)
                out.append(trial)
    return out


def _collect_ncts(items: list[tuple[str, dict, dict, dict]]) -> set[str]:
    ncts = set()
    for _, _, review, records in items:
        recs = _rec_by_id(records)
        for trial in _pooled_trials(review):
            raw = str(trial.get("id", "")).replace("PMID ", "").strip()
            rec = recs.get(raw) or {}
            nct = funding._trial_nct(raw, trial, rec)
            if nct:
                ncts.add(nct)
    return ncts


def _summary_tuple(rows: list[dict]) -> dict:
    known = sum(1 for row in rows if funding.funding_known(row))
    industry = sum(1 for row in rows if funding.industry_tied(row))
    return {"industry_or_tied": industry, "known": known, "unknown": len(rows) - known, "total": len(rows)}


def main() -> int:
    items = []
    for review_path in sorted(REVIEWS.glob("*/review.json")):
        slug = review_path.parent.name
        review = _load_json(review_path)
        before_review = _git_show_json(BASE, f"docs/reviews/{slug}/review.json")
        records = _cache(slug)
        items.append((slug, before_review, review, records))

    registry_by_nct = aact.sponsor_records(_collect_ncts(items))
    pages = []
    pooled_rows = []
    global_distribution = {}
    total_trials = 0
    total_unknown_recovered = 0
    pages_sentence_changed = 0

    for slug, before_review, review, records in items:
        recs = _rec_by_id(records)
        before = before_review.get("funding") or []
        after = funding.scan_pooled(
            {"outcomes": review.get("outcomes") or []},
            recs,
            records.get("fulltext_by_pmid") or {},
            registry_by_nct=registry_by_nct,
        )
        recovered = funding.unknown_but_recovered(before, after)
        before_summary = _summary_tuple(before)
        after_summary = _summary_tuple(after)
        changed = before_summary != after_summary
        if changed:
            pages_sentence_changed += 1
        total_trials += len(after)
        total_unknown_recovered += len(recovered)
        dist = funding.class_distribution(after)
        for key, value in dist.items():
            global_distribution[key] = global_distribution.get(key, 0) + value
        pooled_rows.extend(
            {
                "slug": slug,
                "id": row.get("id"),
                "status": row.get("status"),
                "sponsor_class": row.get("sponsor_class"),
                "source_id": row.get("source_id"),
            }
            for row in after
        )
        pages.append({
            "slug": slug,
            "pooled_trials": len(after),
            "rendered_unknown_recovered": [
                {
                    "id": row.get("id"),
                    "sponsor_class": row.get("sponsor_class"),
                    "sponsors": row.get("sponsors") or [],
                    "source_id": row.get("source_id"),
                    "basis_span": row.get("basis_span"),
                }
                for row in recovered
            ],
            "sponsor_class_distribution": funding.class_distribution(after),
            "industry_sentence_before": before_summary,
            "industry_sentence_after": after_summary,
            "industry_sentence_changes": changed,
        })

    out = {
        "baseline_ref": BASE,
        "measured": True,
        "pages": pages,
        "pooled_trials": pooled_rows,
        "summary": {
            "affected_pages": [page["slug"] for page in pages if page["rendered_unknown_recovered"]],
            "global_sponsor_class_distribution": dict(sorted(global_distribution.items())),
            "pages_with_industry_sentence_changes": [
                page["slug"] for page in pages if page["industry_sentence_changes"]
            ],
            "rendered_funding_unknown_recovered": total_unknown_recovered,
            "pooled_trials": total_trials,
            "pages_industry_sentence_changes": pages_sentence_changed,
            "pages_total": len(items),
        },
    }
    dest = ROOT / "docs" / "funding_sweep.json"
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    s = out["summary"]
    print(
        f"{s['rendered_funding_unknown_recovered']} trials rendered funding-unknown recovered "
        f"of {s['pooled_trials']} pooled trials; {s['pages_industry_sentence_changes']} of "
        f"{s['pages_total']} pages change"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
