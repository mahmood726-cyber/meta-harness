"""Endpoint-canonical lane plants and live controls."""
from __future__ import annotations

import json
import os
import subprocess

import harness.compat as CM
import harness.endpoint_canonical as EC


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "aa8ed28a"


def _review_from_git(slug: str) -> dict:
    data = subprocess.check_output(["git", "show", f"{BASE}:docs/reviews/{slug}/review.json"], cwd=ROOT)
    return json.loads(data)


def _live_review(slug: str) -> dict:
    with open(os.path.join(ROOT, "docs", "reviews", slug, "review.json"), encoding="utf-8") as f:
        return json.load(f)


def _primary(review: dict) -> dict:
    return next(o for o in review["outcomes"] if o.get("primary"))


def _codes(outcome: dict, slug: str) -> set[str]:
    return {v["code"] for v in EC.diagnose(outcome, slug)}


def test_doac_endpoint_underclaim_and_live_fix():
    pre = _primary(_review_from_git("doac-vte-recurrence"))
    assert "KEY_UNDER_CLAIMS" in _codes(pre, "doac-vte-recurrence")

    live = _primary(_live_review("doac-vte-recurrence"))
    assert live["endpoint_canonical"]["label"] == "SYMPTOMATIC_RECURRENT_VTE"
    assert live["compat_key"]["endpoint"] == "SYMPTOMATIC_RECURRENT_VTE"
    assert "KEY_UNDER_CLAIMS" not in _codes(live, "doac-vte-recurrence")


def test_sglt2_ckd_endpoint_overclaim_and_live_fix():
    pre = _primary(_review_from_git("sglt2-ckd-progression"))
    assert "KEY_OVER_CLAIMS" in _codes(pre, "sglt2-ckd-progression")

    live = _primary(_live_review("sglt2-ckd-progression"))
    assert live["endpoint_canonical"]["label"] == "TRIAL_DEFINED_PRIMARY_CARDIORENAL_COMPOSITE"
    assert live["endpoint_canonical"]["status"] == "HETEROGENEOUS_DECLARED"
    assert "KEY_OVER_CLAIMS" not in _codes(live, "sglt2-ckd-progression")


def test_mixed_effect_label_plant_and_live_labels():
    pre_doac = _primary(_review_from_git("doac-vte-recurrence"))
    pre_noac = _primary(_review_from_git("noac-vs-warfarin-af-stroke"))
    assert "LABEL_HIDES_MIX" in _codes(pre_doac, "doac-vte-recurrence")
    assert "LABEL_HIDES_MIX" in _codes(pre_noac, "noac-vs-warfarin-af-stroke")

    live_doac = _primary(_live_review("doac-vte-recurrence"))
    live_noac = _primary(_live_review("noac-vs-warfarin-af-stroke"))
    assert live_doac["result"]["effect_label"] == "pooled first-event ratio (5 HR + 1 RR)"
    assert live_noac["result"]["effect_label"] == "pooled first-event ratio (3 HR + 1 RR)"
    assert "LABEL_HIDES_MIX" not in _codes(live_doac, "doac-vte-recurrence")
    assert "LABEL_HIDES_MIX" not in _codes(live_noac, "noac-vs-warfarin-af-stroke")


def test_noac_harm_endpoint_not_forced_to_stroke_systemic_embolism():
    outcome = {
        "name": "Major bleeding",
        "result": {"k": 1},
        "trials": [{"id": "PMID 1", "label": "A", "components": ["major bleeding"]}],
    }
    EC.annotate_outcome(outcome, "noac-vs-warfarin-af-stroke")
    assert outcome["endpoint_canonical"]["label"] == "MAJOR_BLEEDING"


def test_analysis_set_superclass_plant_and_literal_retention():
    pre = _primary(_review_from_git("doac-vte-recurrence"))
    assert "ANALYSIS_SET_PROMOTED" in _codes(pre, "doac-vte-recurrence")

    live = _primary(_live_review("doac-vte-recurrence"))
    assert live["compat_key"]["analysis_set_superclass"] == EC.ANALYSIS_SUPERCLASS
    by_id = {str(t["id"]).replace("PMID ", ""): t for t in live["trials"]}
    assert by_id["23991658"]["analysis_set_literal"] == "mITT"
    assert "ANALYSIS_SET_PROMOTED" not in _codes(live, "doac-vte-recurrence")


def test_metformin_strategy_split_plant_and_live_fix():
    pre = _primary(_review_from_git("metformin-pcos-ovulation"))
    assert "STRATEGY_COLLAPSED" in _codes(pre, "metformin-pcos-ovulation")

    live = _primary(_live_review("metformin-pcos-ovulation"))
    strategies = {t.get("treatment_strategy") for t in live["trials"]}
    assert strategies == {"METFORMIN_ADDON_CC"}
    assert "added to clomifene" in _live_review("metformin-pcos-ovulation")["title"].lower()
    assert "STRATEGY_COLLAPSED" not in _codes(live, "metformin-pcos-ovulation")


def test_matched_rows_control_no_violation():
    o = {
        "name": "Stroke or systemic embolism",
        "timepoint": "trial end",
        "population": "intention-to-treat",
        "result": {
            "k": 2,
            "scale": "HR",
            "estmeasure": {
                "status": "homogeneous",
                "classes": ["FIRST_EVENT_RATIO"],
                "labels": ["HR"],
                "canonicals": ["HAZARD_RATIO_FIRST_EVENT"],
            },
        },
        "trials": [
            {
                "id": "PMID 1",
                "label": "A",
                "scale": "HR",
                "components": ["stroke any type", "non-CNS systemic embolism"],
                "analysis_set_literal": "ITT",
                "endpoint_event_time": "TIME_TO_FIRST_EVENT",
                "dose_regimen": "standard_dose",
            },
            {
                "id": "PMID 2",
                "label": "B",
                "scale": "HR",
                "components": ["stroke any type", "non-CNS systemic embolism"],
                "analysis_set_literal": "ITT",
                "endpoint_event_time": "TIME_TO_FIRST_EVENT",
                "dose_regimen": "standard_dose",
            },
        ],
    }
    EC.annotate_outcome(o, "noac-vs-warfarin-af-stroke")
    o["compat_key"] = CM.outcome_key(o, {"outcomes": [o]})
    assert EC.diagnose(o, "noac-vs-warfarin-af-stroke") == []
