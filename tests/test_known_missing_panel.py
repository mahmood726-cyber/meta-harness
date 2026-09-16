from __future__ import annotations

import copy
import json
import os
import subprocess

from harness import known_missing
from harness.gate import check_known_missing_panel
from harness.synth import Study, pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "aa8ed28a"


def _prefix_review(slug: str) -> dict:
    data = subprocess.check_output(
        ["git", "-C", ROOT, "show", f"{BASE}:docs/reviews/{slug}/review.json"],
        text=True,
        encoding="utf-8",
    )
    return json.loads(data)


def _cache(slug: str) -> dict:
    with open(os.path.join(ROOT, "cache", slug, "records.json"), encoding="utf-8") as f:
        return json.load(f)


def _rec_by_id(records: dict) -> dict:
    return {str(r.get("id")): r for r in records.get("records", []) if r.get("id")}


def _write_review(tmp_path, review: dict):
    path = tmp_path / "review"
    path.mkdir()
    (path / "review.json").write_text(json.dumps(review), encoding="utf-8")
    return str(path)


def test_gate_fires_on_prefix_glp1_named_missing_without_panel(tmp_path):
    review = _prefix_review("glp1-ra-mace-t2d")
    reasons = check_known_missing_panel(_write_review(tmp_path, review))
    assert any("known_missing_sensitivity panel" in r for r in reasons), reasons


def test_gate_fires_on_prefix_colchicine_eligible_declared_absent_without_panel(tmp_path):
    review = _prefix_review("colchicine-postop-af")
    reasons = check_known_missing_panel(_write_review(tmp_path, review))
    assert any("known_missing_sensitivity panel" in r for r in reasons), reasons


def test_glp1_rows_report_cache_measured_statuses_without_numbers():
    slug = "glp1-ra-mace-t2d"
    review = _prefix_review(slug)
    records = _cache(slug)
    signals = {"known_eligible_missing": [
        {"trial": "FLOW", "mechanism": "concept-query"},
        {"trial": "FREEDOM-CVO", "mechanism": "concept-query"},
    ]}
    known_missing.build(review, signals, _rec_by_id(records), records)
    panel = next(o for o in review["outcomes"] if o.get("primary"))["known_missing_sensitivity"]
    by_name = {r["trial_key"]: r for r in panel["rows"]}
    assert by_name["FLOW"]["value_status"] == "NOT_IN_COMMITTED_SOURCE"
    assert by_name["FREEDOM-CVO"]["value_status"] == "NOT_IN_COMMITTED_SOURCE"
    assert "sensitivity" not in by_name["FLOW"]
    assert "components" in panel and panel["components"] == "CV_DEATH | NONFATAL_MI | NONFATAL_STROKE"


def test_colchicine_panel_passes_and_combined_sensitivity_changes_null_crossing(tmp_path):
    slug = "colchicine-postop-af"
    review = _prefix_review(slug)
    records = _cache(slug)
    known_missing.build(review, {"known_eligible_missing": [{"trial": "five audit-named trials"}]},
                        _rec_by_id(records), records)
    panel = next(o for o in review["outcomes"] if o.get("primary"))["known_missing_sensitivity"]
    rows = {r["trial_key"]: r for r in panel["rows"]}
    assert rows["36286314"]["value_status"] == "IN_COMMITTED_SOURCE"
    assert rows["22090167"]["value_status"] == "IN_COMMITTED_SOURCE"
    assert panel["combined"]["k"] == 6
    assert panel["combined"]["estimate"] == 0.6488
    assert panel["combined"]["ci_low"] == 0.4782
    assert panel["combined"]["ci_high"] == 0.8802
    assert panel["combined"]["conclusion_effect"] == "CHANGES_CI_NULL_CROSSING"
    assert check_known_missing_panel(_write_review(tmp_path, review)) == []


def test_uncommitted_missing_trial_has_no_numeric_fields():
    review = {
        "slug": "synthetic",
        "invalidation": {"stale": True, "reasons": [{"code": "known_eligible_missing", "detail": "PHILO"}]},
        "outcomes": [{
            "primary": True,
            "name": "Primary",
            "estimand": "RR",
            "result": {"k": 1, "estimate": 0.8, "scale": "RR", "ci_low": 0.7, "ci_high": 0.9},
            "trials": [{"label": "A", "id": "PMID 1", "effect": 0.8, "ci_low": 0.7, "ci_high": 0.9, "scale": "RR"}],
        }],
    }
    known_missing.build(review, {"known_eligible_missing": [{"trial": "PHILO"}]}, {}, {"records": []})
    row = review["outcomes"][0]["known_missing_sensitivity"]["rows"][0]
    assert row["value_status"] == "NOT_IN_COMMITTED_SOURCE"
    assert "sensitivity" not in row
    assert not any(row.get(k) is not None for k in ("estimate", "ci_low", "ci_high", "ai", "n1i", "ci", "n2i"))


def test_committed_counts_sensitivity_equals_direct_synth_pool():
    slug = "colchicine-postop-af"
    review = _prefix_review(slug)
    records = _cache(slug)
    known_missing.build(review, {}, _rec_by_id(records), records)
    primary = next(o for o in review["outcomes"] if o.get("primary"))
    cocs = next(r for r in primary["known_missing_sensitivity"]["rows"] if r["trial_key"] == "36286314")
    direct_studies = [
        Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"), n2i=t.get("n2i"),
              effect=t.get("effect"), ci_low=t.get("ci_low"), ci_high=t.get("ci_high"), measure="RR")
        for t in primary["trials"]
    ]
    direct_studies.append(Study(label="COCS", ai=cocs["ai"], n1i=cocs["n1i"], ci=cocs["ci"], n2i=cocs["n2i"],
                                measure="RR"))
    direct = pool(direct_studies, scale="RR")
    sens = cocs["sensitivity"]
    assert sens["k"] == direct.k
    assert sens["estimate"] == round(direct.estimate, 4)
    assert sens["ci_low"] == round(direct.ci_low, 4)
    assert sens["ci_high"] == round(direct.ci_high, 4)
