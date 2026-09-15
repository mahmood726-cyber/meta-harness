from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import measure_search_recall as recall  # noqa: E402


R2_FILE = ROOT / "outputs" / "search_v2" / "candidates-2026-09-15r2-all.json"
R3_FILE = ROOT / "outputs" / "search_v2" / "candidates-2026-09-15r3-all.json"
BENCHMARK_FILE = ROOT / "registry" / "search_benchmark.json"
SPLIT_FILE = ROOT / "registry" / "search_benchmark_split.json"
R2_SNAPSHOT = "2026-09-15r2-search_v2"
R3_SNAPSHOT = "2026-09-15r3-search_v2"


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def measurement_slugs() -> list[str]:
    benchmark = load_json(BENCHMARK_FILE)
    split = load_json(SPLIT_FILE)
    topics = benchmark.get("topics") or {}
    assignments = split.get("assignments") or {}
    return [
        slug
        for slug in sorted(topics)
        if (assignments.get(slug) or {}).get("set") == "MEASUREMENT"
    ]


def score_by_topic(candidate_file: Path) -> dict[str, dict[str, Any]]:
    data = recall._load_json(candidate_file)
    _, candidates = recall._candidate_payload(data)
    benchmark = load_json(BENCHMARK_FILE)
    topics = benchmark.get("topics") or {}
    return {
        slug: recall._score_topic(slug, topics[slug].get("positives") or [], candidates.get(slug, []))
        for slug in measurement_slugs()
    }


def isrctn_source(topic_meta: dict[str, Any]) -> dict[str, Any] | None:
    for source in topic_meta.get("sources") or []:
        if source.get("kind") == "ISRCTN_CONDITION_INTERVENTION":
            return source
    return None


def source_count_text(source: dict[str, Any] | None) -> str:
    if not source:
        return "NOT_RUN records 0 of 0"
    state = str(source.get("state") or "UNKNOWN")
    record_count = int(source.get("record_count") or 0)
    funnel = source.get("funnel") or {}
    hits = funnel.get("hits")
    denom = record_count if hits is None else int(hits or 0)
    if denom < record_count:
        denom = record_count
    return f"{state} records {record_count} of {denom}"


def isrctn_ids_from_ledger(slug: str, snapshot: str) -> set[str]:
    path = ROOT / "cache" / slug / "snapshots" / snapshot / "retrieval_ledger.json"
    if not path.is_file():
        return set()
    ledger = load_json(path)
    ids: set[str] = set()
    for source in ledger.get("sources") or []:
        if source.get("kind") != "ISRCTN_CONDITION_INTERVENTION":
            continue
        for record_id in source.get("record_ids") or []:
            value = str(record_id or "").strip().upper()
            if value:
                ids.add(value)
    return ids


def main() -> int:
    r2_data = load_json(R2_FILE)
    r3_data = load_json(R3_FILE)
    r2_scores = score_by_topic(R2_FILE)
    r3_scores = score_by_topic(R3_FILE)
    slugs = measurement_slugs()

    r2_total_found = sum(len(r2_scores[slug]["found"]) for slug in slugs)
    r3_total_found = sum(len(r3_scores[slug]["found"]) for slug in slugs)
    total_n = sum(r3_scores[slug]["N"] for slug in slugs)

    print("R2 VS R3 SEARCH_V2 COMPARISON")
    print(f"measurement topics: {len(slugs)} of {len(slugs)}")
    print(f"benchmark positives found r2 {r2_total_found} of {total_n} -> r3 {r3_total_found} of {total_n}")
    print("")
    print("PER-TOPIC MEASUREMENT RESULTS")
    for slug in slugs:
        n = r3_scores[slug]["N"]
        r2_found = len(r2_scores[slug]["found"])
        r3_found = len(r3_scores[slug]["found"])
        source = isrctn_source((r3_data.get("topics") or {}).get(slug) or {})
        r2_ids = isrctn_ids_from_ledger(slug, R2_SNAPSHOT)
        r3_ids = isrctn_ids_from_ledger(slug, R3_SNAPSHOT)
        new_ids = sorted(r3_ids - r2_ids)
        print(
            f"{slug}: r2 found {r2_found} of {n}; r3 found {r3_found} of {n}; "
            f"ISRCTN source {source_count_text(source)}; "
            f"ISRCTN records not in r2 {len(new_ids)} of {len(r3_ids)}"
        )
        if new_ids:
            print(f"  new_isrctn_ids: {', '.join(new_ids)}")

    print("")
    print("INPUTS")
    print(f"r2 candidate file: {R2_FILE.relative_to(ROOT)}")
    print(f"r3 candidate file: {R3_FILE.relative_to(ROOT)}")
    print(f"r2 snapshot: {R2_SNAPSHOT}")
    print(f"r3 snapshot: {R3_SNAPSHOT}")
    print(f"r2 topics present: {len((r2_data.get('topics') or {}))} of 32")
    print(f"r3 topics present: {len((r3_data.get('topics') or {}))} of 32")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
