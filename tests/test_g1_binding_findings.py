"""PLANTS for F1 COMPARATOR_COUNTS_EQUAL_SUM_OF_COMPONENTS (scripts/g1_binding_findings.component_sum). The positive is
COLCOT's real posted shape (AACT 2026-08-30, NCT02551094): the comparator's 114 / 141 is CV death + MI + stroke."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_binding_findings as bf  # noqa: E402


def reg(outcomes):
    return {"outcomes": {o: {"title": t, "type": ty} for o, t, ty, _ in outcomes},
            "groups": {o: [{"count": c, "n": 2379}, {"count": t, "n": 2366}] for o, _, _, (t, c) in outcomes}}


COLCOT = reg([("p", "First Event of Cardiovascular Death, Resuscitated Cardiac Arrest, Acute Myocardial Infarction, Stroke, or Urgent Hospitalization",
               "PRIMARY", (131, 170)),
              ("d", "Cardiovascular Death", "SECONDARY", (20, 24)),
              ("a", "Resuscitated Cardiac Arrest", "SECONDARY", (5, 6)),
              ("m", "Myocardial Infarction", "SECONDARY", (89, 98)),
              ("s", "Stroke", "SECONDARY", (5, 19)),
              ("f", "First Event of Cardiovascular Death, Resuscitated Cardiac Arrest, Myocardial Infarction or Stroke.", "SECONDARY", (111, 130))])
ROW = {"events_t": 114, "n_t": 2366, "events_c": 141, "n_c": 2379}


def test_colcot_comparator_counts_are_the_sum_of_three_components():
    state, d = bf.component_sum(COLCOT, ROW)
    assert state == "COMPARATOR_COUNTS_EQUAL_SUM_OF_COMPONENTS"
    assert sorted(c["outcome_id"] for c in d["components"]) == ["d", "m", "s"]
    assert {c["outcome_id"] for c in d["trial_composites_posted"]} == {"p", "f"}


def test_a_row_equal_to_one_posted_outcome_is_not_a_sum():
    state, _ = bf.component_sum(COLCOT, {"events_t": 131, "n_t": 2366, "events_c": 170, "n_c": 2379})
    assert state == "COMPARATOR_COUNTS_EQUAL_ONE_POSTED_OUTCOME"


def test_no_decomposition_is_silent():
    assert bf.component_sum(COLCOT, {"events_t": 7, "n_t": 2366, "events_c": 9, "n_c": 2379})[0] == "NO_DECOMPOSITION"


def test_two_decompositions_are_ambiguous_never_asserted():
    r = reg([("x", "A", "SECONDARY", (1, 2)), ("y", "B", "SECONDARY", (2, 1)), ("z", "C", "SECONDARY", (1, 2)),
             ("w", "D", "SECONDARY", (2, 1))])
    assert bf.component_sum(r, {"events_t": 3, "n_t": 2366, "events_c": 3, "n_c": 2379})[0] == "F1_AMBIGUOUS"


def test_equal_arm_sizes_cannot_identify_arms():
    r = {"outcomes": {"d": {"title": "D"}}, "groups": {"d": [{"count": 1, "n": 50}, {"count": 2, "n": 50}]}}
    assert bf.component_sum(r, {"events_t": 1, "n_t": 50, "events_c": 2, "n_c": 50})[0] == "NOT_APPLICABLE"


def test_components_restricted_to_the_trials_own_declared_components():
    # COLCOT's real posted outcomes also hold a COINCIDENTAL decomposition: total death + urgent angina hospitalisation +
    # VTE + AF = 114 / 141. Only outcomes naming a declared component may be summed.
    r = reg([("d", "Cardiovascular Death", "SECONDARY", (20, 24)), ("m", "Myocardial Infarction", "SECONDARY", (89, 98)),
             ("s", "Stroke", "SECONDARY", (5, 19)), ("t", "Death (Total Mortality)", "SECONDARY", (43, 44)),
             ("u", "Urgent Hospitalization for Angina Requiring Coronary Revascularization", "SECONDARY", (25, 50)),
             ("v", "Deep Venous Thrombosis or Pulmonary Embolus", "OTHER_PRE_SPECIFIED", (10, 7)),
             ("af", "Atrial Fibrillation", "OTHER_PRE_SPECIFIED", (36, 40))])
    assert bf.component_sum(r, ROW)[0] == "F1_AMBIGUOUS"
    ok = bf.component_filter(["death from cardiovascular causes", "resuscitated cardiac arrest", "myocardial infarction",
                              "stroke", "urgent hospitalization for angina leading to coronary revascularization"])
    state, d = bf.component_sum(r, ROW, allowed=ok)
    assert state == "COMPARATOR_COUNTS_EQUAL_SUM_OF_COMPONENTS"
    assert sorted(c["outcome_id"] for c in d["components"]) == ["d", "m", "s"]


# ---- F2 / F3 (melatonin: ours -17.4 vs theirs +11.2) -------------------------------------------------------------------
def test_f2_reads_the_comparators_own_reduction_convention():
    t = ("Our primary outcome measure was mean improvement in sleep onset latency, total sleep time and quality. "
         "Melatonin demonstrated significant efficacy in reducing sleep latency (weighted mean difference (WMD) = 7.06 "
         "minutes [95% CI 4.37 to 9.75]).")
    conv, spans = bf.orientation_stated(t)
    assert conv == "POSITIVE_IS_REDUCTION_WITH_INTERVENTION" and len(spans) == 2


def test_f2_silent_when_the_comparator_states_no_convention():
    assert bf.orientation_stated("Melatonin was compared with placebo; MD and 95% CI were pooled.") == (None, [])


def test_f3_cited_report_and_same_registration():
    jats = ('<ref id="r1">21 Smith A ( 2010 ) Other trial. 11111111</ref>'
            '<ref id="r2">22 Wade AG , Crawford G ( 2011 ) Prolonged release melatonin: age cut-off . 21091391</ref>')
    assert bf.cited_report(jats, "Wade AG, 2011 [21]") == "21091391"
    db = {"21091391": {"databank": ["NCT00397189"]}, "20712869": {"databank": ["NCT00397189"]}}
    assert bf.same_trial_different_report("21091391", "20712869", db)["registration"] == ["NCT00397189"]
    assert bf.same_trial_different_report("21091391", "21091391", db) is None
    assert bf.same_trial_different_report("21091391", "99999999", {**db, "99999999": {"databank": ["NCT01111111"]}}) is None
