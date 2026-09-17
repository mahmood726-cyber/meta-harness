"""Corpus-wide RX unextracted-outcome sweep.

Reads committed review objects and cached sources, then writes
docs/unextracted_sweep.json. No extraction, pooling, search, or fetch is run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT))

from harness import reason_audit, unextracted  # noqa: E402
from harness.pipeline import _outcome_specs  # noqa: E402


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _topic_specs(slug: str) -> dict[str, dict[str, Any]]:
    cfg = _load_json(ROOT / "topics" / f"{slug}.json")
    return {sp.get("name"): sp for sp, _ in _outcome_specs(cfg)}


def classify_pair(slug: str, review: dict[str, Any], outcome: dict[str, Any], trial_key: str) -> dict[str, Any]:
    records = _load_json(ROOT / "cache" / slug / "records.json")
    sources = reason_audit.sources_by_trial(slug, records, ROOT)
    specs = _topic_specs(slug)
    absent = {
        reason_audit.canonical_trial_id(row.get("id") or row.get("label")): row
        for row in outcome.get("declared_absent_trials") or []
    }
    audit = unextracted.audit_pair(
        outcome,
        trial_key,
        sources.get(trial_key, []),
        specs.get(outcome.get("name")) or {},
        absent.get(trial_key),
    )
    return {
        "slug": slug,
        "trial_key": trial_key,
        "outcome": outcome.get("name"),
        "outcome_kind": "primary" if outcome.get("primary") else outcome.get("kind", "secondary"),
        **audit,
    }


def review_paths() -> list[Path]:
    return sorted((ROOT / "docs" / "reviews").glob("*/review.json"))


def run() -> dict[str, Any]:
    rows = []
    pages: dict[str, dict[str, Any]] = {}
    by_kind: dict[str, dict[str, int]] = {}
    statuses = [
        unextracted.EXTRACTED,
        unextracted.HELD_NOT_EXTRACTED,
        unextracted.NOT_IN_HELD_SOURCES,
        unextracted.ABSENT_BY_DESIGN,
    ]
    for rp in review_paths():
        slug = rp.parent.name
        review = _load_json(rp)
        records = _load_json(ROOT / "cache" / slug / "records.json")
        sources = reason_audit.sources_by_trial(slug, records, ROOT)
        specs = _topic_specs(slug)
        audit = unextracted.annotate_review(slug, review, specs, sources)
        page_rows = audit["rows"]
        rows.extend(page_rows)
        pages[slug] = {"N": len(page_rows), "counts": audit["counts"]}
        for row in page_rows:
            kind = row.get("outcome_kind") or "secondary"
            by_kind.setdefault(kind, {s: 0 for s in statuses})
            by_kind[kind][row["status"]] += 1
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in statuses}
    return {
        "denominator_source": "included screening records x registered outcomes across docs/reviews/*/review.json",
        "topics": len(review_paths()),
        "N": len(rows),
        "counts": counts,
        "n_held_not_extracted": counts[unextracted.HELD_NOT_EXTRACTED],
        "by_outcome_kind": by_kind,
        "by_page": pages,
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "unextracted_sweep.json"))
    args = ap.parse_args(argv)
    data = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"OUT_WRITTEN {out} HELD_NOT_EXTRACTED={data['n_held_not_extracted']} "
        f"N={data['N']} topics={data['topics']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
