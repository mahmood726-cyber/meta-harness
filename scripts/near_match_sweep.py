"""Corpus sweep for target-endpoint near-match defects.

Outputs docs/near_match_sweep.json from committed topic configs, cached source
records, and the currently served review objects. No network.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(ROOT))
from harness import protocol_compiler as PC  # noqa: E402
from harness import target_endpoint as TE  # noqa: E402


def _load_json(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _outcome_specs(config: dict) -> dict[str, dict]:
    specs = {}
    for spec in [config.get("primary_outcome")] + list(config.get("secondary_outcomes") or []) + list(config.get("harm_outcomes") or []):
        if isinstance(spec, dict) and spec.get("name"):
            specs[spec["name"]] = spec
    return specs


def _records_by_id(records: dict) -> dict[str, dict]:
    return {str(r.get("id")): r for r in records.get("records") or []}


def _served_class(spec: dict, row: dict) -> dict:
    if row.get("target_endpoint_class"):
        return {
            "target_endpoint_class": row.get("target_endpoint_class"),
            "extra_components": row.get("target_endpoint_extra_components") or [],
            "missing_components": row.get("target_endpoint_missing_components") or [],
            "target_components": row.get("target_endpoint_components") or row.get("components") or [],
        }
    comps = set(row.get("components") or [])
    text = row.get("source") or ""
    return TE._classify(spec, text, comps or None)


def main() -> int:
    review_paths = sorted((ROOT / "docs" / "reviews").glob("*/review.json"))
    rows = []
    by_page: dict[str, dict] = {}
    protocols_no_pref = []
    multi_primary_rows = []
    near_while_exact = []
    pooled_with_primary_check = 0

    for review_path in review_paths:
        slug = review_path.parent.name
        topic_path = ROOT / "topics" / f"{slug}.json"
        records_path = ROOT / "cache" / slug / "records.json"
        protocol_path = ROOT / "protocols" / f"{slug}.md"
        if not topic_path.exists() or not records_path.exists():
            continue
        review = _load_json(review_path)
        config = _load_json(topic_path)
        records = _load_json(records_path)
        rec_by_id = _records_by_id(records)
        specs = _outcome_specs(config)
        page = by_page.setdefault(slug, {
            "pooled_rows": 0,
            "near_match_while_exact_exists": 0,
            "multiple_registered_primary_trials": 0,
        })

        if protocol_path.exists():
            md = protocol_path.read_text(encoding="utf-8")
            div = PC.compare(slug, md, config)
            if any(d.get("code") == "ESTIMAND_PREFERENCE_UNDECLARED" for d in div):
                protocols_no_pref.append(slug)

        for outcome in review.get("outcomes") or []:
            spec = specs.get(outcome.get("name"))
            if not spec:
                continue
            for row in outcome.get("trials") or []:
                page["pooled_rows"] += 1
                pid = str(row.get("id") or "").replace("PMID ", "").strip()
                rec = rec_by_id.get(pid, {})
                nct = rec.get("nct") or (pid if pid.upper().startswith("NCT") else None)
                ctgov_oms = (records.get("ctgov_results") or {}).get(nct) if nct else None
                selection = TE.select_target_endpoint(
                    spec,
                    rec.get("abstract", ""),
                    ctgov_oms,
                    config.get("intervention_terms") or [],
                    config.get("comparator_terms") or [],
                )
                served = _served_class(spec, row)
                candidates = TE.enumerate_candidates(
                    spec,
                    rec.get("abstract", ""),
                    ctgov_oms,
                    config.get("intervention_terms") or [],
                    config.get("comparator_terms") or [],
                )
                primary_titles = {
                    c.get("registry_title")
                    for c in candidates
                    if c.get("source_type") == "ctgov_results"
                    and str(c.get("registry_type") or "").upper() == "PRIMARY"
                    and c.get("target_endpoint_class") in (TE.EXACT_TARGET, TE.NEAR_MATCH)
                }
                if candidates:
                    pooled_with_primary_check += 1
                multi_primary = len(primary_titles) > 1
                if multi_primary:
                    page["multiple_registered_primary_trials"] += 1
                    multi_primary_rows.append({
                        "slug": slug,
                        "outcome": outcome.get("name"),
                        "trial": row.get("id"),
                        "n_registered_primaries_in_family": len(primary_titles),
                        "primary_titles": sorted(t for t in primary_titles if t),
                    })
                defect = (
                    served.get("target_endpoint_class") == TE.NEAR_MATCH
                    and selection.get("exact_target_in_held_source")
                )
                if defect:
                    page["near_match_while_exact_exists"] += 1
                    near_while_exact.append({
                        "slug": slug,
                        "outcome": outcome.get("name"),
                        "trial": row.get("id"),
                        "served_class": served.get("target_endpoint_class"),
                        "served_extra_components": served.get("extra_components") or [],
                        "served_missing_components": served.get("missing_components") or [],
                    })
                rows.append({
                    "slug": slug,
                    "outcome": outcome.get("name"),
                    "trial": row.get("id"),
                    "served_class": served.get("target_endpoint_class"),
                    "exact_target_exists_in_held_source": bool(selection.get("exact_target_in_held_source")),
                    "selected_class_by_rule": ((selection.get("selected") or {}).get("target_endpoint_class")),
                    "selected_source_rank": ((selection.get("selected") or {}).get("target_endpoint_source_rank")),
                    "multiple_registered_primaries_in_family": multi_primary,
                })

    n_topics = len({r["slug"] for r in rows})
    n_pooled = len(rows)
    out = {
        "schema": "near_match_sweep.v1",
        "n_topics": n_topics,
        "n_pooled_rows": n_pooled,
        "rows": rows,
        "by_page": by_page,
        "near_match_while_exact_exists": {
            "n": len(near_while_exact),
            "N_pooled_rows": n_pooled,
            "rows": near_while_exact,
        },
        "protocols_with_no_estimand_preference": {
            "n": len(protocols_no_pref),
            "N_topics": n_topics,
            "slugs": protocols_no_pref,
        },
        "trials_with_multiple_registered_primaries_in_outcome_family": {
            "n": len(multi_primary_rows),
            "N_pooled_rows_checked": pooled_with_primary_check,
            "rows": multi_primary_rows,
        },
    }
    out_path = ROOT / "docs" / "near_match_sweep.json"
    out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "near-match sweep: "
        f"{len(near_while_exact)} NEAR_MATCH rows with an exact held target among {n_pooled} pooled rows; "
        f"{len(protocols_no_pref)} protocols lack estimand preference among {n_topics} topics; "
        f"{len(multi_primary_rows)} pooled rows have >1 registered primary in-family"
    )
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
