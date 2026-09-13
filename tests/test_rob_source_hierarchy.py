"""Regression tests for the RoB source hierarchy (denosumab/FREEDOM cold audit): a trial-level masking
field (Double/Triple/Quadruple) overrides the generic per-role AACT Booleans, which were wrong for
FREEDOM and propagated a spurious GRADE -1; and D3 keys off between-arm DIFFERENTIAL missingness, not
overall study discontinuation. The override must fire ONLY for genuinely blinded trials.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import rob2  # noqa: E402

_MATCH = lambda a, b: True  # noqa: E731


def _assess(design):
    return rob2.assess(design, ["Primary outcome"], "Primary outcome", _MATCH)


def test_double_blind_masking_overrides_wrong_booleans():
    # FREEDOM shape: fully double-blind (masking Double) but the per-role Booleans read false.
    d = _assess({"allocation": "Randomized", "masking": "Double", "subject_masked": "t",
                 "caregiver_masked": "f", "outcomes_assessor_masked": "f",
                 "attrition": {"overall_pct": 17.0, "differential_pct": 1.8}})
    assert d["D2_deviations"]["level"] == "low"
    assert d["D4_outcome_measurement"]["level"] == "low"
    assert "FLAGGED" in d["D4_outcome_measurement"]["basis"]  # disagreement flagged, not silent
    assert d["D3_missing_outcome_data"]["level"] == "low"     # 1.8% differential, not 17% overall
    assert rob2.overall(d).startswith("low")


def test_open_label_still_downgrades():
    # A genuinely open-label trial (no masking) must STILL be flagged -- the override must not whitewash.
    d = _assess({"allocation": "Randomized", "masking": "None", "subject_masked": "f",
                 "caregiver_masked": "f", "outcomes_assessor_masked": "f",
                 "attrition": {"overall_pct": 5, "differential_pct": 1}})
    assert d["D2_deviations"]["level"] == "some concerns"
    assert d["D4_outcome_measurement"]["level"] == "some concerns"


def test_d3_keys_off_differential_not_overall():
    # High overall study discontinuation but small differential -> D3 low (outcome availability high).
    low = rob2.assess({"allocation": "Randomized", "masking": "Double",
                       "attrition": {"overall_pct": 30.0, "differential_pct": 2.0}}, ["x"], "x", _MATCH)
    assert low["D3_missing_outcome_data"]["level"] == "low"
    # Large between-arm differential -> a real signal.
    hi = rob2.assess({"allocation": "Randomized", "masking": "Double",
                      "attrition": {"overall_pct": 20.0, "differential_pct": 12.0}}, ["x"], "x", _MATCH)
    assert hi["D3_missing_outcome_data"]["level"] == "high"


def test_single_blind_does_not_trigger_override():
    # 'Single' masking is not enough to override an unmasked assessor.
    d = _assess({"allocation": "Randomized", "masking": "Single", "subject_masked": "t",
                 "caregiver_masked": "f", "outcomes_assessor_masked": "f",
                 "attrition": {"overall_pct": 3, "differential_pct": 1}})
    assert d["D4_outcome_measurement"]["level"] == "some concerns"


def test_d1_abstract_corrects_wrong_non_randomized_allocation():
    # EMPHASIS-HF (NCT00232180): AACT allocation reads NON_RANDOMIZED but the trial's own abstract states
    # random assignment -> D1 corrected to low with an abstract-corrected basis and the disagreement flagged.
    d = rob2.assess({"allocation": "NON_RANDOMIZED", "masking": "Double"}, ["Primary"], "Primary", _MATCH,
                    randomized_by_text=True)
    assert d["D1_randomisation"]["level"] == "low"
    assert "abstract-corrected" in d["D1_randomisation"]["basis"]
    assert "FLAGGED" in d["D1_randomisation"]["basis"]


def test_d1_non_randomized_without_abstract_signal_is_not_upgraded():
    # Negative control: a genuinely non-randomized study (no random-assignment text) must NOT be upgraded.
    d = rob2.assess({"allocation": "NON_RANDOMIZED", "masking": "None"}, ["Primary"], "Primary", _MATCH,
                    randomized_by_text=False)
    assert d["D1_randomisation"]["level"] == "some concerns"
    assert "abstract-corrected" not in d["D1_randomisation"]["basis"]
    # unstated allocation with no abstract signal stays 'not assessed', never silently 'low'
    d2 = rob2.assess({"allocation": "", "masking": "None"}, ["Primary"], "Primary", _MATCH,
                     randomized_by_text=False)
    assert d2["D1_randomisation"]["level"] == "not assessed"
