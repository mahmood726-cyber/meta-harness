"""Corpus-wide RX reason-code audit.

Reads committed review objects and cached sources, then writes
docs/reason_audit_sweep.json. No extraction, pooling, search, or fetch is run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT))

from harness import reason_audit  # noqa: E402
from harness.pipeline import _outcome_specs  # noqa: E402


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _topic_specs(slug: str) -> dict[str, dict[str, Any]]:
    cfg = _load_json(ROOT / "topics" / f"{slug}.json")
    return {sp.get("name"): sp for sp, _ in _outcome_specs(cfg)}


def classify_row(
    slug: str,
    outcome: dict[str, Any],
    row: dict[str, Any],
    *,
    sources: dict[str, list[dict[str, str]]] | None = None,
    specs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if sources is None:
        records = _load_json(ROOT / "cache" / slug / "records.json")
        sources = reason_audit.sources_by_trial(slug, records, ROOT)
    if specs is None:
        specs = _topic_specs(slug)
    key = reason_audit.canonical_trial_id(row.get("id") or row.get("label"))
    audit = reason_audit.audit_reason_row(outcome, row, sources.get(key, []), specs.get(outcome.get("name")) or {})
    return {
        "slug": slug,
        "outcome": outcome.get("name"),
        "outcome_kind": "primary" if outcome.get("primary") else outcome.get("kind", "secondary"),
        "trial_key": key,
        "label": row.get("label"),
        "id": row.get("id"),
        **audit,
    }


def review_paths() -> list[Path]:
    return sorted((ROOT / "docs" / "reviews").glob("*/review.json"))


def run() -> dict[str, Any]:
    rows = []
    pages: dict[str, dict[str, Any]] = {}
    by_code: dict[str, dict[str, int]] = {}
    verdicts = [
        reason_audit.REASON_TRUE,
        reason_audit.REASON_FALSE_VALUE_HELD,
        reason_audit.REASON_WRONG_KIND,
        reason_audit.NOT_VERIFIABLE,
    ]
    for rp in review_paths():
        slug = rp.parent.name
        review = _load_json(rp)
        records = _load_json(ROOT / "cache" / slug / "records.json")
        sources = reason_audit.sources_by_trial(slug, records, ROOT)
        specs = _topic_specs(slug)
        page_rows = []
        for outcome in review.get("outcomes") or []:
            for row in outcome.get("declared_absent_trials") or []:
                classified = classify_row(slug, outcome, row, sources=sources, specs=specs)
                rows.append(classified)
                page_rows.append(classified)
                code = classified.get("stated_reason_code") or "UNSPECIFIED"
                by_code.setdefault(code, {v: 0 for v in verdicts})
                by_code[code][classified["verdict"]] += 1
        pages[slug] = {
            "N": len(page_rows),
            "counts": {v: sum(1 for r in page_rows if r["verdict"] == v) for v in verdicts},
        }
    counts = {v: sum(1 for r in rows if r["verdict"] == v) for v in verdicts}
    return {
        "denominator_source": "reason_code/state rows in declared_absent_trials across docs/reviews/*/review.json",
        "topics": len(review_paths()),
        "N": len(rows),
        "counts": counts,
        "n_false_value_held": counts[reason_audit.REASON_FALSE_VALUE_HELD],
        "n_not_verifiable": counts[reason_audit.NOT_VERIFIABLE],
        "by_code_kind": by_code,
        "by_page": pages,
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "reason_audit_sweep.json"))
    args = ap.parse_args(argv)
    data = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"OUT_WRITTEN {out} FALSE_VALUE_HELD={data['n_false_value_held']} "
        f"NOT_VERIFIABLE={data['n_not_verifiable']} N={data['N']} topics={data['topics']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
