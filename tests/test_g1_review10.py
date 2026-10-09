"""Review-10 F10-1: a 3-point MACE value is bound only from a definition with exactly CV death + MI + stroke
(scripts/g1_review10.three_point). ELIXA's 4-point primary -- which the comparator pooled as MACE -- must never pass."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_review10 as R  # noqa: E402


def test_flows_own_clause_is_three_point():
    got, why = R.three_point(R.FLOW_DEF, R.FLOW_RES)
    assert why is None and got == (0.82, 0.68, 0.98)


def test_PLANT_elixas_four_point_primary_is_never_three_point():
    d = ("cardiovascular death, non-fatal myocardial infarction, non-fatal stroke, or hospitalization for unstable "
         "angina")
    got, why = R.three_point(d, "HR 1.02 (0.89-1.17)")
    assert got is None and why.startswith("DEFINITION_HAS_A_FOURTH_COMPONENT")


def test_PLANT_a_definition_missing_a_component_or_two_results_is_refused():
    assert R.three_point("CV death or non-fatal MI", "HR 0.9 (0.8-1.0)")[1] == "DEFINITION_NOT_THREE_COMPONENTS"
    assert R.three_point(R.FLOW_DEF, "HR 0.82 (0.68-0.98) and HR 0.80 (0.67-0.95)")[1] == "RESULT_CLAUSE_HRS:2"
    assert R.three_point(R.FLOW_DEF, "HR 1.20 (0.68-0.98)")[1] == "HR_NOT_INSIDE_ITS_CI"


# ------------------------------------------------------------------------------------------- codex review10-r1
def test_PLANT_r1_1_any_component_beyond_the_three_refuses():
    for extra in ("resuscitated cardiac arrest", "coronary revascularization", "hospitalization for unstable angina"):
        got, why = R.three_point(f"CV death, non-fatal MI, non-fatal stroke, or {extra}", "HR 0.82 (95% CI 0.68-0.98)")
        assert got is None and why.startswith("DEFINITION_HAS_A_FOURTH_COMPONENT"), extra


def test_PLANT_r1_2_a_reader_quoting_another_endpoint_never_agrees():
    other = {"state": "FOUND", "quote": "In the renal subgroup, kidney failure had HR 0.82 (95% CI 0.68–0.98).",
             "hr": 0.82, "lower": 0.68, "upper": 0.98, "definition": "kidney failure"}
    txt = "x " + other["quote"] + " " + R.FLOW_RES + " y"
    assert R.reader_verdict(other, txt) == ("GATED_OTHER_CLAUSE", False)
    ok = dict(other, quote=R.FLOW_RES)
    assert R.reader_verdict(ok, txt) == ("GATED", True)


def test_PLANT_r1_3_the_ema_route_uses_the_same_three_point_rule():
    t = ("ELIXA: The primary composite comprised CV death, non-fatal MI, and non-fatal stroke or hospitalisation for "
         "unstable angina; HR 1.02 (95% CI 0.89-1.17).")
    assert R.ema_three_point_clauses(t) == []
    t3 = "In ELIXA the composite of CV death, non-fatal MI and non-fatal stroke gave HR 1.02 (95% CI 0.89-1.17)."
    assert len(R.ema_three_point_clauses(t3)) == 1


def test_PLANT_r1_4_a_three_point_label_endpoint_is_never_called_four_point():
    lbl = ("Table 12: Analysis of the Primary CV Endpoint (time to the first occurrence of the composite of CV death, "
           "non-fatal MI and non-fatal stroke) -- ITT Population Primary composite CV event 0.90 (0.80, 1.00)")
    d = R.label_primary(lbl)
    assert d["three_point"] is True and R.four_point_of(d) is None


def test_PLANT_r1_5_an_unreadable_held_document_is_not_checked_never_absent():
    assert R.doc_route_outcome(None, "EMA") .startswith("NOT_CHECKED")
