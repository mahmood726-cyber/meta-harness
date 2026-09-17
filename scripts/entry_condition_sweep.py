from __future__ import annotations

import copy
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import pipeline, screen  # noqa: E402

TOPICS = ROOT / "topics"
CACHE = ROOT / "cache"
OUT = ROOT / "docs" / "entry_condition_sweep.json"
MEASURED_UTC = "2026-09-16"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _records(slug: str, cfg: dict) -> list[dict]:
    path = CACHE / slug / "records.json"
    if not path.exists():
        return []
    data = _load_json(path)
    return pipeline._dedup(data, cfg.get("pivotal_trials"))  # existing pipeline contract


def _legacy_config(cfg: dict) -> dict:
    old = copy.deepcopy(cfg)
    inc = old.get("include") or {}
    inc.pop("population_none_entry_condition_only", None)
    inc.pop("comparator_overrides", None)
    old.pop("completeness_states", None)
    old.pop("contrast_evictions", None)
    return old


def _by_id(rows: list[dict]) -> dict[str, dict]:
    return {str(r.get("id")): r for r in rows if r.get("id") is not None}


def _named_state(item: dict, rows: dict[str, dict]) -> str:
    for key in (item.get("pmid"), item.get("key"), item.get("nct")):
        if key is None:
            continue
        row = rows.get(str(key))
        if row and row.get("decision") == "include":
            return "SCREENED_IN"
        if row:
            return f"SCREENED_OUT({row.get('rule_id')})"
    return item.get("state") or "REACH_MISS(named)"


def main() -> None:
    topic_paths = sorted(TOPICS.glob("*.json"))
    topic_slugs = [p.stem for p in topic_paths]
    keyword_slugs: list[str] = []
    flips: list[dict] = []
    named: list[dict] = []
    total_records = 0

    for path in topic_paths:
        cfg = _load_json(path)
        slug = cfg.get("slug") or path.stem
        recs = _records(slug, cfg)
        if not recs:
            continue

        rows = screen.run(recs, cfg)["decisions"]
        total_records += len(rows)
        current = _by_id(rows)

        if (cfg.get("include") or {}).get("population_none"):
            keyword_slugs.append(slug)

        legacy = _by_id(screen.run(recs, _legacy_config(cfg))["decisions"])
        for rid, new in current.items():
            old = legacy.get(rid)
            if not old:
                continue
            if old.get("decision") == new.get("decision") and old.get("rule_id") == new.get("rule_id"):
                continue
            flips.append(
                {
                    "slug": slug,
                    "id": rid,
                    "before": {"decision": old.get("decision"), "rule_id": old.get("rule_id")},
                    "after": {"decision": new.get("decision"), "rule_id": new.get("rule_id")},
                    "reason": new.get("reason"),
                }
            )

        for item in cfg.get("named_eligible_misses") or []:
            state = _named_state(item, current)
            named.append(
                {
                    "slug": slug,
                    "trial": item.get("trial"),
                    "pmid": item.get("pmid"),
                    "state": state,
                    "detail": item.get("detail"),
                }
            )

    named_state_counts = Counter(n["state"] for n in named)
    payload = {
        "measured_utc": MEASURED_UTC,
        "topic_denominator": {"n": len(topic_slugs), "slugs": topic_slugs},
        "keyword_prohibition_population_screens": {
            "n": len(keyword_slugs),
            "of": len(topic_slugs),
            "slugs": keyword_slugs,
        },
        "decision_flips": {
            "n": len(flips),
            "of_screened_records": total_records,
            "records": flips,
        },
        "named_eligible_misses": {
            "n": len(named),
            "states": dict(sorted(named_state_counts.items())),
            "records": named,
        },
        "notes": [
            "Legacy comparison removes entry-condition exceptions, comparator overrides, completeness states, and explicit contrast evictions from the current config.",
            "No network calls are made; all records are read from committed cache/<slug>/records.json files.",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
