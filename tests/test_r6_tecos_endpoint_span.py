"""R6 (G1 TECOS span): a comparator row is adjudicated on its endpoint WORDING and its TUPLE together. Comparator
31462224's TECOS row names the 4-point composite ('... or hospitalisation for unstable angina') and prints 0.99
(0.89-1.10) -- TECOS's 3-point MACE result, the value we pool (AACT NCT00790205 outcome 258888999). It was a plain AGREE.
Synthetic fixtures carrying the held span's wording."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

SPAN_4PT = ("TECOS [ 23 ] 2015 NCT00790205 Sitagliptin vs. placebo 14,523 (7257/7266) A composite of the first confirmed "
            "event of cardiovascular death, nonfatal MI, nonfatal stroke, or hospitalisation for unstable angina 0.99 "
            "(0.89-1.10)")
CFG = {"primary_outcome": {"name": "3-point major adverse cardiovascular events", "trial_annotations": {}}}


def unit(span, agreement="AGREE", family="PMID 26052984"):
    return {"label": "TECOS", "family": family, "agreement_with_comparator_row": agreement,
            "comparator_row_provenance": {"span": span}, "comparator_row_findings": []}


def test_PLANT_tecos_4_point_wording_with_our_3_point_tuple_is_not_a_plain_agree():
    x = unit(SPAN_4PT)
    assert gt.endpoint_wording_adjudication([x], CFG) == 1
    assert x["agreement_with_comparator_row"] == "AGREE_ON_TUPLE:COMPARATOR_WORDING_NAMES_A_DIFFERENT_ENDPOINT"
    assert x["endpoint_wording"]["comparator_components"] == ["CV_DEATH", "MI", "STROKE", "UNSTABLE_ANGINA"]
    assert x["endpoint_wording"]["our_components"] == ["CV_DEATH", "MI", "STROKE"]
    assert x["comparator_row_findings"][0]["finding"] == "COMPARATOR_ROW_WORDING_MISLABELS_ITS_TUPLE"
    # and it surfaces as a finding ABOUT the comparator's row
    assert any(f["finding"] == "COMPARATOR_ROW_WORDING_MISLABELS_ITS_TUPLE" for f in gt.comparator_findings([x], "31462224"))


def test_PLANT_a_different_endpoint_whose_tuple_differs_is_not_a_disagreement():
    x = unit(SPAN_4PT, agreement="DISAGREE")
    gt.endpoint_wording_adjudication([x], CFG)
    assert x["agreement_with_comparator_row"] == "NOT_COMPARABLE:COMPARATOR_ROW_IS_A_DIFFERENT_ENDPOINT"


def test_PLANT_same_components_in_other_words_change_nothing():
    x = unit("SAVOR 2013 A composite of cardiovascular death, myocardial infarction, or ischemic stroke 1.00 (0.89-1.12)")
    assert gt.endpoint_wording_adjudication([x], CFG) == 0 and x["agreement_with_comparator_row"] == "AGREE"


def test_PLANT_a_span_with_no_composite_wording_is_not_adjudicated():
    for span in ("TECOS 2015 NCT00790205 Sitagliptin vs. placebo 0.99 (0.89-1.10)", "stroke 0.9 (0.7-1.1)", None):
        x = unit(span)
        assert gt.endpoint_wording_adjudication([x], CFG) == 0 and x["agreement_with_comparator_row"] == "AGREE"


def test_PLANT_the_trials_own_protocol_annotation_outranks_the_topic_name():
    cfg = {"primary_outcome": {"name": "3-point major adverse cardiovascular events", "trial_annotations": {
        "26052984": {"components": ["CV death", "nonfatal myocardial infarction", "nonfatal stroke",
                                    "hospitalisation for unstable angina"]}}}}
    x = unit(SPAN_4PT)
    assert gt.endpoint_wording_adjudication([x], cfg) == 0 and x["agreement_with_comparator_row"] == "AGREE"


def test_endpoint_components_expands_point_mace_shorthand():
    assert gt.endpoint_components("three-point MACE") == {"CV_DEATH", "MI", "STROKE"}
    assert gt.endpoint_components("4-point major adverse cardiovascular events") == {"CV_DEATH", "MI", "STROKE",
                                                                                    "UNSTABLE_ANGINA"}
    assert gt.endpoint_components("all-cause mortality") is None


def test_PLANT_adjudication_runs_after_every_comparator_row_and_span_is_attached():
    # the first wiring ran before apply_typed_comparator_rows attached TECOS's span, so the live topic was never
    # adjudicated while every unit plant passed: the ORDER inside topic() is part of the requirement
    import inspect
    src = inspect.getsource(gt.topic)
    assert src.index("apply_typed_comparator_rows(out)") < src.index("endpoint_wording_adjudication(out")
    assert src.index("endpoint_wording_adjudication(out") < src.index('out["g1_status"] = g1_status(out)')
