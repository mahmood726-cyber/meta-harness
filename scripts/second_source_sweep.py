"""Sweep CT.gov second-source rows for endpoint identity.

Reads committed cache only: docs/reviews/* gives the served topic set, and
cache/<slug>/records.json supplies the offline CT.gov payloads.
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.pipeline import build_review_core  # noqa: E402
from harness.registration import protocol_sha  # noqa: E402
from harness.second_source import IDENTICAL_ENDPOINT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _slugs():
    review_root = os.path.join(ROOT, "docs", "reviews")
    return sorted(
        name for name in os.listdir(review_root)
        if os.path.exists(os.path.join(review_root, name, "review.json"))
    )


def _load_json(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return json.load(f)


def _core(slug):
    cfg = _load_json("topics", slug + ".json")
    records = _load_json("cache", slug, "records.json")
    return build_review_core(slug, cfg, records, protocol_sha(slug))


def build_sweep():
    rows = []
    slugs = _slugs()
    for slug in slugs:
        core = _core(slug)
        for outcome in core.get("outcomes", []) or []:
            for trial in outcome.get("trials", []) or []:
                cs = trial.get("cross_source") or {}
                if not cs:
                    continue
                identity = cs.get("identity") or {}
                verdict = identity.get("verdict") or cs.get("second_source_verdict") or "SECOND_SOURCE_NOT_CHECKABLE"
                row_id = f"{slug}::{outcome.get('name')}::{trial.get('id')}"
                rows.append({
                    "row_id": row_id,
                    "slug": slug,
                    "outcome": outcome.get("name"),
                    "trial_key": trial.get("id"),
                    "trial_label": trial.get("label"),
                    "pooled_value": cs.get("pooled_effect_for_endpoint_match"),
                    "pooled_scale": cs.get("pooled_scale_for_endpoint_match"),
                    "registry_title": cs.get("registry_title"),
                    "registry_type": cs.get("registry_type"),
                    "registry_param_type": cs.get("registry_param_type"),
                    "registry_measure_type": cs.get("registry_measure_type"),
                    "registry_effect_label": cs.get("registry_effect_label"),
                    "registry_timepoint": cs.get("registry_selected_timepoint") or cs.get("registry_timeframe"),
                    "registry_population": cs.get("registry_population"),
                    "registry_implied_value": cs.get("registry_implied_effect") or cs.get("ctgov_rr"),
                    "identity": identity,
                    "verdict": verdict,
                    "reason": cs.get("endpoint_match_reason"),
                    "counted_as_corroboration": bool(cs.get("corroborates_endpoint")),
                })
    bad_corroboration = [
        row for row in rows
        if row["counted_as_corroboration"] and row["verdict"] != IDENTICAL_ENDPOINT
    ]
    by_verdict = dict(collections.Counter(row["verdict"] for row in rows))
    by_page = {}
    for slug in slugs:
        page_rows = [row for row in rows if row["slug"] == slug]
        if not page_rows:
            continue
        by_page[slug] = {
            "cross_source_rows": len(page_rows),
            "by_verdict": dict(collections.Counter(row["verdict"] for row in page_rows)),
            "bad_corroboration_rows": [
                row["row_id"] for row in page_rows
                if row["counted_as_corroboration"] and row["verdict"] != IDENTICAL_ENDPOINT
            ],
        }
    agreement_rows = [row for row in rows if row["verdict"] == IDENTICAL_ENDPOINT]
    agreement_deltas = []
    for row in agreement_rows:
        pooled, registry = row.get("pooled_value"), row.get("registry_implied_value")
        if pooled and registry and pooled > 0 and registry > 0:
            agreement_deltas.append(abs(math.log(float(pooled) / float(registry))))
    return {
        "measurement": "MEASURED from committed cache via build_review_core; no network",
        "topics_examined": len(slugs),
        "cross_source_rows": len(rows),
        "cross_source_row_ids": [row["row_id"] for row in rows],
        "bad_corroboration_rows": len(bad_corroboration),
        "bad_corroboration_row_ids": [row["row_id"] for row in bad_corroboration],
        "summary": (
            f"{len(bad_corroboration)} rows labelled corroboration whose endpoint identity is "
            f"unverified or wrong of {len(rows)} cross-source rows over {len(slugs)} topics"
        ),
        "by_verdict": by_verdict,
        "by_page": by_page,
        "agreement_statistics": {
            "computed_only_for_verdict": IDENTICAL_ENDPOINT,
            "rows_considered": len(agreement_rows),
            "rows_excluded": len(rows) - len(agreement_rows),
            "max_abs_log_delta": max(agreement_deltas) if agreement_deltas else None,
        },
        "rows": rows,
    }


def main():
    sweep = build_sweep()
    out = os.path.join(ROOT, "docs", "second_source_sweep.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sweep, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(sweep["summary"])
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
