"""Sweep included-trial outcome/funding consumer consistency.

For each served review page, inspect every included trial against every registered
outcome plus funding. The sweep uses only committed cache files; it does not
search, fetch, pool, or change screening decisions.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import consumer_consistency as cc  # noqa: E402


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _review_paths() -> list[Path]:
    return sorted((ROOT / "docs" / "reviews").glob("*/review.json"))


def _review_from_ref(ref: str, slug: str) -> dict[str, Any]:
    raw = subprocess.check_output(
        ["git", "show", f"{ref}:docs/reviews/{slug}/review.json"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(raw)


def run(ref: str | None = None) -> dict[str, Any]:
    pages = []
    totals = {
        "n_pages": 0,
        "n_cells": 0,
        "n_source_value_not_accounted": 0,
        "n_reason_code_false": 0,
    }
    for path in _review_paths():
        slug = path.parent.name
        review = _review_from_ref(ref, slug) if ref else _load_json(path)
        config = cc.load_topic_config(slug)
        records = cc.load_records_blob(slug)
        page = cc.sweep_review(slug, review, config, records)
        pages.append({
            k: v for k, v in page.items()
            if k in {"slug", "n_cells", "n_source_value_not_accounted", "n_reason_code_false", "summary"}
        })
        totals["n_pages"] += 1
        totals["n_cells"] += page["n_cells"]
        totals["n_source_value_not_accounted"] += page["n_source_value_not_accounted"]
        totals["n_reason_code_false"] += page["n_reason_code_false"]
    return {
        "source": ref or "current",
        "denominator": "included trial x registered outcome, plus one funding cell per included trial",
        "totals": totals,
        "pages": pages,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", help="read review.json objects from this git ref")
    ap.add_argument("--out", default=str(ROOT / "docs" / "consumer_consistency_sweep.json"))
    args = ap.parse_args(argv)
    data = run(args.ref)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    totals = data["totals"]
    print(
        "OUT_WRITTEN {out} source={source} value_not_accounted={bad} of {n} cells; "
        "reason_code_false={false} of {n} cells; pages={pages}".format(
            out=out,
            source=data["source"],
            bad=totals["n_source_value_not_accounted"],
            false=totals["n_reason_code_false"],
            n=totals["n_cells"],
            pages=totals["n_pages"],
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
