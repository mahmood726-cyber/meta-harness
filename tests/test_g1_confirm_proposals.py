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
