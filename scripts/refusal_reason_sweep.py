"""Corpus-wide refusal-reason truth sweep.

Reads every docs/reviews/*/review.json declared_absent_trials row, re-reads the committed source
cache, classifies what the source actually contains, and writes docs/refusal_reason_sweep.json.
No search, fetch, or pooling is performed.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

import sys
sys.path.insert(0, str(ROOT))

from harness import absence  # noqa: E402
from harness.pipeline import _outcome_specs  # noqa: E402


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _records_by_id(slug: str) -> dict[str, dict[str, Any]]:
    path = ROOT / "cache" / slug / "records.json"
    if not path.exists():
        return {}
    raw = _load_json(path)
    records = raw.get("records") or raw.get("pubmed") or raw.get("items") or raw
    if isinstance(records, dict):
        iterable = records.values()
    else:
        iterable = records or []
    out = {}
    for rec in iterable:
        if isinstance(rec, dict) and rec.get("id") is not None:
            out[str(rec.get("id"))] = rec
    return out


def _fulltext(slug: str, pid: str) -> str | None:
    path = ROOT / "cache" / slug / f"ft_{pid}.txt"
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _canon_id(row: dict[str, Any]) -> str:
    raw = str(row.get("id") or row.get("label") or "")
    for pre in ("PMID ", "PMID:", "NCT"):
        if raw.upper().startswith(pre.upper()):
            return raw[len(pre):].strip()
    return raw.strip()


def _effect_text(effect: dict[str, Any] | None) -> str | None:
    if not effect:
        return None
    return (f"{effect.get('scale')} {effect.get('effect')} "
            f"[{effect.get('ci_low')}, {effect.get('ci_high')}], class={effect.get('class')}")


def _topic_specs(slug: str) -> dict[str, dict[str, Any]]:
    path = ROOT / "topics" / f"{slug}.json"
    if not path.exists():
        return {}
    cfg = _load_json(path)
    return {sp.get("name"): sp for sp, _ in _outcome_specs(cfg)}


def classify_row(slug: str, outcome: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    specs = _topic_specs(slug)
    spec = specs.get(outcome.get("name")) or {}
    recs = _records_by_id(slug)
    cid = _canon_id(row)
    rec = recs.get(cid) or {}
    abstract = rec.get("abstract") or ""
    actual = absence.classify_reason(
        spec.get("keywords") or [],
        abstract,
        _fulltext(slug, cid),
        outcome_name=outcome.get("name"),
        declared_estimand=spec.get("estimand") or outcome.get("estimand"),
        reason=row.get("reason"),
        absent_kind=row.get("absent_kind"),
        row=row,
    )
    verdict = absence.verdict_for_row(row, actual)
    return {
        "slug": slug,
        "outcome": outcome.get("name"),
        "trial_key": cid,
        "label": row.get("label"),
        "id": row.get("id"),
        "absent_kind": row.get("absent_kind"),
        "stated_reason": row.get("reason"),
        "stated_state": row.get("state"),
        "stated_reason_code": row.get("reason_code"),
        "source_contains": (actual.get("verbatim_span") or actual.get("source_span") or "")[:200],
        "verdict": verdict,
        "corrected_code": actual.get("reason_code"),
        "corrected_state_basis": actual.get("state_basis"),
        "observed_effect_text": _effect_text(actual.get("observed_effect")),
    }


def review_paths() -> list[Path]:
    return sorted((ROOT / "docs" / "reviews").glob("*/review.json"))


def run() -> dict[str, Any]:
    paths = review_paths()
    rows = []
    denominator = 0
    for rp in paths:
        slug = rp.parent.name
        review = _load_json(rp)
        for outcome in review.get("outcomes") or []:
            absent_rows = outcome.get("declared_absent_trials") or []
            denominator += len(absent_rows)
            for row in absent_rows:
                rows.append(classify_row(slug, outcome, row))
    counts = {k: sum(1 for r in rows if r["verdict"] == k) for k in ("TRUE", "FALSE", "NOT_CHECKABLE")}
    return {
        "denominator_source": "sum of declared_absent_trials in committed docs/reviews/*/review.json files",
        "topics": len(paths),
        "N": denominator,
        "n_rows_emitted": len(rows),
        "counts": counts,
        "n_false": counts["FALSE"],
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "refusal_reason_sweep.json"))
    args = ap.parse_args(argv)
    data = run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OUT_WRITTEN {out} FALSE={data['n_false']} N={data['N']} topics={data['topics']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
