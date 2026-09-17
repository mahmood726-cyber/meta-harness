"""Corpus sweep for executable eligibility-chain failures."""
from __future__ import annotations

from collections import Counter
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import eligibility_chain  # noqa: E402


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _read_text(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def _slugs():
    base = os.path.join(ROOT, "docs", "reviews")
    return sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))


def main() -> int:
    topics = []
    by_code = Counter()
    divergence_by_dimension = Counter()
    pooled_total = 0
    pooled_failing_total = 0
    excluded_total = 0
    for slug in _slugs():
        config = _load_json("topics", f"{slug}.json")
        protocol = _read_text("protocols", f"{slug}.md")
        review = _load_json("docs", "reviews", slug, "review.json")
        try:
            records = _load_json("cache", slug, "records.json")
        except OSError:
            records = {"records": []}
        row = eligibility_chain.sweep_topic(slug, config, protocol, review, records)
        topics.append(row)
        by_code.update(row["counts"])
        divergence_by_dimension.update(row["divergence_dimensions"])
        pooled_total += row["pooled_rows"]
        pooled_failing_total += row["pooled_rows_failing_contract"]
        excluded_total += row["excluded_rows"]
    n_topics = len(topics)
    out = {
        "topic_denominator": n_topics,
        "pooled_row_denominator": pooled_total,
        "excluded_row_denominator": excluded_total,
        "pages_with_protocol_config_divergence": {
            "n": sum(1 for t in topics if t["counts"].get("PROTOCOL_CONFIG_DIVERGENCE")),
            "N": n_topics,
        },
        "protocol_config_divergence_by_dimension": dict(sorted(divergence_by_dimension.items())),
        "pooled_trials_failing_contract": {
            "n": pooled_failing_total,
            "N": pooled_total,
        },
        "eligibility_state_inconsistent": {
            "n": by_code.get("ELIGIBILITY_STATE_INCONSISTENT", 0),
            "N": excluded_total,
        },
        "counts_by_code": dict(sorted(by_code.items())),
        "topics": topics,
    }
    out_path = os.path.join(ROOT, "docs", "eligibility_chain_sweep.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(
        "eligibility_chain_sweep: "
        f"PROTOCOL_CONFIG_DIVERGENCE pages={out['pages_with_protocol_config_divergence']['n']} of {n_topics}; "
        f"TRIAL_FAILS_CONTRACT rows={out['pooled_trials_failing_contract']['n']} of {pooled_total}; "
        f"ELIGIBILITY_STATE_INCONSISTENT={out['eligibility_state_inconsistent']['n']} of {excluded_total}; "
        f"OUT_WRITTEN {out_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
