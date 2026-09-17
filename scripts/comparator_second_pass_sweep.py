from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "aa8ed28a"
sys.path.insert(0, str(ROOT))

from harness import comparator_second_pass  # noqa: E402


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _git_json(path: str) -> dict | None:
    try:
        raw = subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)
    except subprocess.CalledProcessError:
        return None
    return json.loads(raw.decode("utf-8"))


def _records(slug: str) -> dict:
    return _load_json(ROOT / "cache" / slug / "records.json")


def _topic(slug: str) -> dict:
    return _load_json(ROOT / "topics" / f"{slug}.json")


def _comp_rec(config: dict, records: dict) -> dict:
    by_id = {str(r.get("id")): r for r in records.get("records", [])}
    return by_id.get(str(config.get("comparator_pmid")), {})


def main() -> int:
    rows = []
    baseline_not_exposed = []
    stated_in_text = []
    review_dirs = sorted(p for p in (ROOT / "docs" / "reviews").iterdir() if p.is_dir())
    for review_dir in review_dirs:
        slug = review_dir.name
        topic_path = ROOT / "topics" / f"{slug}.json"
        records_path = ROOT / "cache" / slug / "records.json"
        if not topic_path.exists() or not records_path.exists():
            continue
        config = _topic(slug)
        records = _records(slug)
        analysis = comparator_second_pass.analyze(slug, config, records, _comp_rec(config, records))

        old = _git_json(f"docs/reviews/{slug}/review.json") or {}
        old_overlap = ((old.get("comparator") or {}).get("overlap") or {})
        old_shared = old_overlap.get("shared_k")
        old_not_exposed = (
            isinstance(old_shared, str)
            and "not exactly verifiable" in old_shared.lower()
        )
        if old_not_exposed:
            baseline_not_exposed.append(slug)
        if old_not_exposed and analysis["comparator_trial_set"].get("status") == "MEASURED":
            stated_in_text.append(slug)

        rows.append({
            "slug": slug,
            "baseline_shared_k": old_shared,
            "baseline_not_exposed": old_not_exposed,
            "comparator_trial_set": analysis["comparator_trial_set"],
            "quantity_match": analysis["quantity_match"],
            "comparator_recency": analysis["comparator_recency"],
            "treatment_strategy_match": analysis["treatment_strategy_match"],
            "outcome_match": analysis["outcome_match"],
            "scope_override": analysis["scope_override"],
        })

    out = {
        "base_commit": BASE,
        "summary": {
            "baseline_not_exposed_n": len(baseline_not_exposed),
            "baseline_not_exposed_pages": baseline_not_exposed,
            "stated_in_cached_text_n": len(stated_in_text),
            "stated_in_cached_text_pages": stated_in_text,
            "denominator": "baseline pages whose shared_k said not exactly verifiable",
        },
        "rows": rows,
    }
    out_path = ROOT / "docs" / "comparator_second_pass.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(
        f"comparator second-pass: {len(stated_in_text)} of {len(baseline_not_exposed)} "
        "baseline not-exposed pages have trial sets stated in cached text"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
