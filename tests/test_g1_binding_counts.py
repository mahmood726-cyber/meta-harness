"""K2 abstract counts (scripts/g1_binding_counts.py): the three phrasings of the DOAC trials' own primary results, copied
as FIXED strings (a control must never read a mutable artefact), 8 Oct."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_binding_counts as bc  # noqa: E402

AMPLIFY = ("The primary efficacy outcome was recurrent symptomatic venous thromboembolism or death related to venous "
           "thromboembolism. RESULTS: The primary efficacy outcome occurred in 59 of 2609 patients (2.3%) in the apixaban "
           "group, as compared with 71 of 2635 (2.7%) in the conventional-therapy group (relative risk, 0.84).")
EINSTEIN = ("The primary efficacy outcome for both studies was recurrent venous thromboembolism. "
            "RESULTS: The study of rivaroxaban for acute DVT included 3449 patients: 1731 given rivaroxaban and 1718 given "
            "enoxaparin plus a vitamin K antagonist. Rivaroxaban had noninferior efficacy with respect to the primary outcome "
            "(36 events [2.1%], vs. 51 events with enoxaparin-vitamin K antagonist [3.0%]; hazard ratio, 0.68).")
HOKUSAI = ("The primary efficacy outcome was recurrent symptomatic venous thromboembolism. "
           "Edoxaban was noninferior to warfarin with respect to the primary efficacy outcome, which occurred in 130 patients "
           "in the edoxaban group (3.2%) and 146 patients in the warfarin group (3.5%) (hazard ratio, 0.89).")


def test_x_of_n_with_hyphenated_control_arm():
    b, why = bc.abstract_counts(AMPLIFY, "doac-vte-recurrence")
    assert why is None and b["values"] == {"events_t": 59, "n_t": 2609, "events_c": 71, "n_c": 2635}


def test_events_with_arm_n_printed_elsewhere_and_the_arm_inside_the_match():
    b, why = bc.abstract_counts(EINSTEIN, "doac-vte-recurrence")
    assert why is None and b["values"] == {"events_t": 36, "n_t": 1731, "events_c": 51, "n_c": 1718}
    assert b["n_source"] == "abstract"


def test_events_without_n_take_the_posted_denominator_only_when_percentages_corroborate():
    b, why = bc.abstract_counts(HOKUSAI, "doac-vte-recurrence")
    assert b is None and why == "N_NOT_PRINTED"
    b, why = bc.abstract_counts(HOKUSAI, "doac-vte-recurrence", (4118, 4122, "AACT N"))
    assert b["values"] == {"events_t": 130, "n_t": 4118, "events_c": 146, "n_c": 4122} and b["n_source"] == "AACT N"
    b, why = bc.abstract_counts(HOKUSAI, "doac-vte-recurrence", (2000, 4122, "AACT N"))      # 130/2000 is 6.5%, not 3.2%
    assert b is None and why.startswith("PERCENT_DOES_NOT_CORROBORATE")


def test_a_served_comparator_result_for_another_outcome_is_not_our_comparison():
    # 8 Oct (gap list, tranexamic): the tracker took the served review's comparator.reported[0] -- 'Life-threatening
    # postpartum bleeding', the COMPARATOR's primary -- as the result for OUR primary 'Death due to bleeding'
    import g1_tracker as gt
    tx_kw = ["death due to bleeding", "death from post-partum haemorrhage", "death from postpartum haemorrhage"]
    assert not gt.reported_is_our_outcome("Life-threatening postpartum bleeding", "Death due to bleeding", tx_kw)
    assert gt.reported_is_our_outcome("Death due to bleeding", "Death due to bleeding", tx_kw)
    assert gt.reported_is_our_outcome("Recurrent VTE", "Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or "
                                      "VTE-related death)", ["recurrent VTE", "recurrent venous thromboembolism"])
    assert not gt.reported_is_our_outcome(None, "Death due to bleeding", tx_kw)  # an UNNAMED result cannot be verified


def test_only_a_results_row_with_two_arm_cells_is_the_comparators_result():
    import g1_comparator_table_result as tr
    assert tr.is_result_row("Death due to bleeding | WOMAN, 1 WOMAN-2, 10 TRAAP | 159/27 307 | 194/27 097 | 0·81 (0·66–1·00) | 0·52 |")
    assert not tr.is_result_row("Diagnosis of postpartum haemorrhage at baseline | Yes | No † | No | No | No |")
    assert tr._n("27 307") == 27307 and tr._f("0·81") == 0.81


def test_the_generic_primary_outcome_phrase_counts_only_when_the_trial_defines_it_as_ours():
    # 8 Oct: K2 read 'primary outcome' as naming OUR outcome; for sglt2-pp (ours = HHF) the trials' primary is MACE
    empa = ("The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, or "
            "nonfatal stroke. RESULTS: The primary outcome occurred in 490 of 4687 patients (10.5%) in the pooled "
            "empagliflozin group, as compared with 282 of 2333 patients (12.1%) in the placebo group (hazard ratio, 0.86).")
    b, why = bc.abstract_counts(empa, "sglt2-primary-prevention-hf")
    assert b is None
    b, why = bc.abstract_counts(AMPLIFY, "doac-vte-recurrence")             # its definition names recurrent VTE
    assert b is not None
