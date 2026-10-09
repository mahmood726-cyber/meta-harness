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
