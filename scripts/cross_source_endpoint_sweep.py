"""Sweep registry cross-source rows for endpoint identity.

Reads committed cache only: docs/reviews/* gives the 32 served topics, and
cache/<slug>/records.json supplies the offline CT.gov payloads.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness.pipeline import build_review_core  # noqa: E402
from harness.registration import protocol_sha  # noqa: E402

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
                verdict = cs.get("endpoint_match") or "NOT_CHECKABLE"
                rows.append({
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
                    "registry_timepoint": cs.get("registry_selected_timepoint") or cs.get("registry_timeframe"),
                    "registry_population": cs.get("registry_population"),
                    "registry_implied_value": cs.get("registry_implied_effect") or cs.get("ctgov_rr"),
                    "verdict": verdict,
                    "reason": cs.get("endpoint_match_reason"),
                    "counted_as_corroboration": bool(cs.get("corroborates_endpoint")),
                })
    mismatched = sum(1 for row in rows if row["verdict"] != "SAME_ENDPOINT")
    return {
        "measurement": "MEASURED from committed cache via build_review_core; no network",
        "topics_examined": len(slugs),
        "cross_source_rows": len(rows),
        "mismatched_rows": mismatched,
        "summary": f"{mismatched} mismatched of {len(rows)} cross-source registry rows over {len(slugs)} topics",
        "rows": rows,
    }


def main():
    sweep = build_sweep()
    out = os.path.join(ROOT, "docs", "cross_source_endpoint_sweep.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sweep, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(sweep["summary"])
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
