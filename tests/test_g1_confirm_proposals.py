"""PLANTS for the proposal gate (scripts/g1_confirm_proposals.gate_one): a model-located span is admitted only when the
held bytes themselves carry every fact; each negative is a way a plausible proposal is wrong."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.append(str(ROOT / "scripts"))

import g1_confirm_proposals as gp  # noqa: E402

TEXT = gp.norm("RESULTS: Antibiotic-associated diarrhoea occurred in 6/16 (37%) in the placebo group and 4/23 (17%) "
               "patients in the probiotic group.")
TEXTS = [("PMID 1 abstract", TEXT)]
CR = {"events_t": 4, "n_t": 23, "events_c": 6, "n_c": 16, "measure": "RR"}
TERMS = ["antibiotic-associated diarrhoea"]
IV, CP = ["probiotic"], ["placebo"]


def prop(**kw):
    p = {"verdict": "PRINTED_SAME",
         "quotes": [{"file": "f", "text": "Antibiotic-associated diarrhoea occurred in 6/16 (37%) in the placebo group "
                                          "and 4/23 (17%) patients in the probiotic group."}],
         "values_printed": {"events_t": 4, "n_t": 23, "events_c": 6, "n_c": 16},
         "arm_of_each_count": {"events_t": "probiotic group", "events_c": "placebo group"}}
    p.update(kw)
    return p


def g(p, cr=CR, texts=TEXTS):
    return gp.gate_one(p, cr, TERMS, IV, CP, texts)[:2]


def test_admits_a_verbatim_span_with_counts_outcome_and_arms():
    assert g(prop()) == ("ADMITTED", "all checks passed")


def test_refuses_a_quote_not_in_the_held_text():
    p = prop(quotes=[{"file": "f", "text": "Diarrhoea occurred in 4/23 vs 6/16."}])
    assert g(p)[1].startswith("QUOTE_NOT_IN_HELD_TEXT")


def test_refuses_values_that_are_not_the_comparator_tuple():
    assert g(prop(values_printed={"events_t": 4, "n_t": 23, "events_c": 7, "n_c": 16}))[1] == "NOT_THE_COMPARATOR_TUPLE"


def test_refuses_when_a_count_is_not_in_the_quotes():
    p = prop(quotes=[{"file": "f", "text": "4/23 (17%) patients in the probiotic group"}])
    assert g(p)[1] in ("VALUES_NOT_IN_QUOTES", "OUTCOME_NOT_NAMED")


def test_refuses_swapped_arm_labels():
    p = prop(arm_of_each_count={"events_t": "placebo group", "events_c": "probiotic group"})
    assert g(p)[1] == "ARMS_SWAPPED"


def test_refuses_arm_labels_absent_from_the_quotes():
    p = prop(arm_of_each_count={"events_t": "treatment arm", "events_c": "control arm"})
    assert g(p)[1] == "ARMS_NOT_ESTABLISHED"


def test_refuses_subgroup_language():
    t = gp.norm("In the subgroup of women, antibiotic-associated diarrhoea occurred in 6/16 in the placebo group and "
                "4/23 in the probiotic group.")
    p = prop(quotes=[{"file": "f", "text": t}])
    assert g(p, texts=[("PMID 1 abstract", t)])[1] == "SUBGROUP_OR_POST_HOC"


def test_refuses_outcome_not_named():
    t = gp.norm("Vomiting occurred in 6/16 in the placebo group and 4/23 in the probiotic group.")
    p = prop(quotes=[{"file": "f", "text": t}])
    assert g(p, texts=[("PMID 1 abstract", t)])[1] == "OUTCOME_NOT_NAMED"


def test_printed_different_is_a_discrepancy_candidate_never_a_binding():
    assert g(prop(verdict="PRINTED_DIFFERENT"))[0] == "DISCREPANCY_CANDIDATE"


def test_other_verdicts_are_not_proposals():
    assert g(prop(verdict="PERCENT_ONLY"))[0] == "NOT_PROPOSED"


def test_effect_ci_proposal_needs_all_three_numbers_verbatim():
    t = gp.norm("Antibiotic-associated diarrhoea: relative risk 0.46 (95% CI 0.16 to 1.38).")
    cr = {"effect": "0.46", "lower": "0.16", "upper": "1.38", "measure": "RR"}
    ok = prop(quotes=[{"file": "f", "text": t}], values_printed={"effect": "0.46", "lower": "0.16", "upper": "1.38"})
    assert g(ok, cr=cr, texts=[("x", t)]) == ("ADMITTED", "all checks passed")
    bad = prop(quotes=[{"file": "f", "text": t}], values_printed={"effect": "0.46", "lower": "0.16", "upper": "1.39"})
    assert g(bad, cr=cr, texts=[("x", t)])[1] == "NOT_THE_COMPARATOR_TUPLE"


# ---- own-tuple admission (Mahmood 3 Oct: matched = any verified typed tuple for the comparator's trial) ----------------
NID = gp.norm("The primary outcome (acute coronary syndrome) occurred in 15 of 282 patients (5.3%) who received colchicine and 40 of 250 patients "
              "(16.0%) assigned no colchicine (hazard ratio: 0.33; 95% CI 0.18 to 0.59).")


def own(text=NID, **kw):
    p = {"verdict": "PRINTED_DIFFERENT", "quotes": [{"file": "f", "text": text}],
         "values_printed": {"events_t": 15, "n_t": 282, "events_c": 40, "n_c": 250},
         "arm_of_each_count": {"events_t": "received colchicine", "events_c": "assigned no colchicine"}}
    p.update(kw)
    return p


def go(p, text=NID, terms=("primary outcome", "acute coronary syndrome")):
    return gp.gate_own_tuple(p, list(terms), ["colchicine"], ["placebo"], [("PMID 9 abstract", text)])[:2]


def test_own_tuple_admits_the_trials_printed_counts():
    assert go(own())[0] == "ADMITTED_OWN_TUPLE"


def test_own_tuple_refuses_a_percent_inconsistent_with_n():
    t = NID.replace("(5.3%)", "(8.3%)")
    assert go(own(text=t), text=t)[1].startswith("PERCENT_INCONSISTENT_WITH_N")


def test_own_tuple_refuses_adjusted_or_subgroup():
    t = NID.replace("The primary outcome (acute coronary syndrome) occurred", "In the adjusted model the primary outcome (acute coronary syndrome) occurred")
    assert go(own(text=t), text=t)[1] == "SUBGROUP_OR_POST_HOC_OR_ADJUSTED"


def test_own_tuple_refuses_event_counts_that_are_not_patients():
    t = gp.norm("A total of 26 hospitalizations for acute coronary syndrome occurred (13 in each group) in 86 receiving "
                "colchicine and 86 assigned no colchicine.")
    p = own(text=t, values_printed={"events_t": 13, "n_t": 86, "events_c": 13, "n_c": 86})
    assert go(p, text=t)[1] == "EVENT_COUNTS_NOT_PATIENTS"


def test_own_tuple_finds_an_arm_size_beside_its_own_label():
    full = gp.norm("Patients were assigned to EPA with statin (EPA group; n=9326) or statin only (controls; n=9319). "
                   "We detected the primary endpoint in 262 (2.8%) patients in the EPA group and 324 (3.5%) in controls.")
    q = gp.norm("We detected the primary endpoint (major coronary event) in 262 (2.8%) patients in the EPA group and 324 (3.5%) in controls.")
    p = {"verdict": "PRINTED_DIFFERENT", "quotes": [{"file": "f", "text": q}],
         "values_printed": {"events_t": 262, "n_t": 9326, "events_c": 324, "n_c": 9319},
         "arm_of_each_count": {"events_t": "EPA group", "events_c": "controls"}}
    v, why, src, parts = gp.gate_own_tuple(p, ["primary endpoint", "major coronary event"], ["EPA"], ["placebo"],
                                           [("x", full.replace("primary endpoint", "primary endpoint (major coronary event)"))])
    assert v == "ADMITTED_OWN_TUPLE" and any("9326" in s for s in parts) and any("9319" in s for s in parts)


def test_own_tuple_refuses_effect_only_proposals():
    p = own(values_printed={"effect": "0.89", "lower": "0.55", "upper": "1.45"})
    assert go(p)[1] == "OWN_TUPLE_NEEDS_TYPED_COUNTS"


def test_own_tuple_refuses_an_outcome_named_only_generically():
    t = gp.norm("The primary outcome occurred in 15 of 282 patients (5.3%) who received colchicine and 40 of 250 "
                "patients (16.0%) assigned no colchicine.")
    assert go(own(text=t), text=t)[1] == "OUTCOME_NAMED_ONLY_GENERICALLY"
