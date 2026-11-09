"""C4 (external audit R8-1, review 13): leave-one-out reports POINT stability and INFERENCE stability separately, and never
claims "no single trial drives it" when a drop moves the 95% CI across the null. Before the fix the note was unconditional
and the rows carried no CI (14 of 32 served pages)."""
from __future__ import annotations

from harness import loo


def test_ci_position_relative_to_the_null():
    assert loo.ci_position(0.7, 0.9, 1.0) == "BELOW_NULL"
    assert loo.ci_position(0.7, 1.0, 1.0) == "INCLUDES_NULL"          # a limit ON the null is not strictly one side
    assert loo.ci_position(1.1, 1.4, 1.0) == "ABOVE_NULL"
    assert loo.ci_position(-6.1, -0.6, 0.0) == "BELOW_NULL"           # mean difference: null 0
    assert loo.ci_position(None, 0.9, 1.0) == "NO_CI"


def test_PLANT_a_drop_that_moves_the_ci_across_the_null_is_named_and_no_stability_is_claimed():
    rows = [{"dropped": "A", "estimate": 0.80, "inference": "INCLUDES_NULL"},
            {"dropped": "B", "estimate": 0.78, "inference": "BELOW_NULL"},
            {"dropped": "C", "estimate": 0.79, "inference": "BELOW_NULL"}]
    s = loo.inference_summary(rows, "BELOW_NULL", 1.0)
    assert s["inference_changed_by"] == ["A"]
    assert "dropping A changes the inference" in s["note"]
    assert "no single trial drives it" not in s["note"]


def test_stable_inference_is_stated_with_its_denominator_and_k2_drops_are_not_assessed():
    rows = [{"dropped": "A", "estimate": 0.80, "inference": "BELOW_NULL"},
            {"dropped": "B", "estimate": 0.78, "inference": "NOT_ASSESSED_K2"}]
    s = loo.inference_summary(rows, "BELOW_NULL", 1.0)
    assert s["inference_changed_by"] == [] and s["inference_assessed"] == 1
    assert "1 of 2" in s["note"] and "k=2: CI not served" in s["note"]


def test_no_served_ci_means_inference_is_not_assessed():
    s = loo.inference_summary([{"dropped": "A", "estimate": 1.0, "inference": "BELOW_NULL"}], "NO_CI", 1.0)
    assert "not assessed" in s["note"] and s["inference_changed_by"] == []
