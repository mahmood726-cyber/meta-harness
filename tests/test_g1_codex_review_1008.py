"""Codex review of the lane range 96525f4a3..HEAD (8 Oct; records mc-03278c66 d10, mc-e6c67fca counts, mc-8914a3b0
gates). Each finding's failing input, adapted to this repository's import paths, as a plant: a test that FAILS while the
defect stands. Findings judged not real are recorded with the reason instead of a test."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_outcomes as go  # noqa: E402
import g1_binding_counts as bc  # noqa: E402
import g1_trial_acquire as ta  # noqa: E402
import g1_tracker as gt  # noqa: E402

INV0 = {"prespecified_secondaries": {"names": []}, "source_kind": "ABSTRACT_ONLY", "record_id": None, "outcomes": []}


# ------------------------------------------------------------------------------------------------------------- d10
def test_d10_1_mortality_elsewhere_in_the_sentence_does_not_label_a_bleeding_result():
    hits, _ = go.regex_inventory("All-cause mortality was not reported, but aspirin reduced bleeding (RR 0.70, 95% CI 0.50-0.90).")
    rows, _ = go.candidates({"R1_regex": {"hits": hits}, "R2_codex": INV0}, {"intervention_terms": ["aspirin"]})
    assert not [r for r in rows if r["family"] == "ALL_CAUSE_MORTALITY"]


def test_d10_2_non_hf_is_not_linked_to_hf():
    t = {"secondary_outcomes": [{"name": "HF hospitalizations"}], "harm_outcomes": []}
    assert go.linked_to("Non-HF hospitalizations", t) is None
    assert go.linked_to("HF hospitalizations", t) == "HF hospitalizations"


def test_d10_3_a_qualified_sae_outcome_never_takes_total_saes():
    assert not go.is_total_sae("Cardiac serious adverse events")
    assert go.is_total_sae("Incidence of serious adverse events") and go.is_total_sae("Serious adverse events")


def test_d10_4_r1_needs_our_intervention_in_the_numbers_clause():
    hits, _ = go.regex_inventory("Denosumab was not evaluated, but risedronate versus placebo reduced all-cause mortality "
                                 "(RR 0.80, 95% CI 0.70-0.90).")
    rows, _ = go.candidates({"R1_regex": {"hits": hits}, "R2_codex": INV0},
                            {"intervention_terms": ["denosumab"], "comparator_terms": ["placebo"]})
    assert rows == []


def test_d10_5_a_generic_control_is_ours_only_when_our_comparator_is_one():
    assert not go.contrast_is_ours("aspirin versus placebo", {"intervention_terms": ["aspirin"], "comparator_terms": ["clopidogrel"]})
    assert go.contrast_is_ours("aspirin versus placebo", {"intervention_terms": ["aspirin"], "comparator_terms": ["placebo"]})


def test_d10_6_an_empty_vocabulary_matches_nothing():
    assert not go.contrast_is_ours("risedronate versus placebo", {"intervention_terms": [], "comparator_terms": ["placebo"]})


def test_d10_7_a_negated_population_is_not_ours():
    t = {"question": "Does aspirin reduce mortality in adults with diabetes?", "eligibility_summary": "Adults with diabetes"}
    assert not go.population_is_ours("Adults without diabetes", t)
    assert go.population_is_ours("adults with diabetes", t)


def test_d10_8_fatal_and_nonfatal_are_different_outcomes():
    assert not go.is_our_primary("Nonfatal myocardial infarction", {"primary_outcome": {"name": "Fatal myocardial infarction",
                                                                                           "keywords": []}})


# ---------------------------------------------------------------------------------------------------------- counts
MORT = {"primary_outcome": {"name": "All-cause mortality", "keywords": ["all-cause mortality"]},
        "intervention_terms": ["DrugA"], "comparator_terms": ["placebo"]}


def _with_topic(monkeypatch, t=MORT):
    monkeypatch.setattr(bc, "topic", lambda _s: t)


def test_counts_1_a_keyword_in_another_clause_does_not_bind_its_counts(monkeypatch):
    _with_topic(monkeypatch)
    b, _ = bc.abstract_counts("All-cause mortality was not reported; stroke occurred in 10 of 100 DrugA patients (10%) "
                              "versus 20 of 100 placebo patients (20%).", "fixture")
    assert b is None


def test_counts_2_randomised_and_analysed_denominators_are_never_mixed(monkeypatch):
    _with_topic(monkeypatch)
    b, _ = bc.abstract_counts("All-cause mortality occurred in 10 of 100 randomised DrugA patients (10%) versus 20 of 80 "
                              "analysed placebo patients (25%).", "fixture")
    assert b is None


def test_counts_3_a_printed_trailing_zero_is_precision(monkeypatch):
    assert not bc._pct_ok(10, 1020, "1.00")
    assert bc._pct_ok(10, 1000, "1.00")


def test_counts_4_a_rate_with_a_people_word_in_its_units_is_not_a_count():
    assert not bc.people_count_units("events per 1000 participant-years")
    assert not bc.people_count_units("Participants/100 patient-years")
    assert bc.people_count_units("Participants") and bc.people_count_units("number or participants with an event")


def test_counts_5_a_paper_binds_to_an_nct_only_on_its_own_evidence():
    assert not bc.paper_names_nct({"nct": "NCT00000001", "abstract": "Trial registration: NCT00000001."}, "NCT00000002", [])
    assert bc.paper_names_nct({"nct": "NCT00000002"}, "NCT00000002", [])
    assert bc.paper_names_nct({"nct": None}, "NCT00000002", ["NCT00000002"])


def test_counts_6_a_header_search_never_crosses_a_table_caption():
    import g1_comparator_table_result as tr
    lines = ["Outcome | DrugA (n/N) | placebo (n/N) | OR (95% CI)", "Stroke | 10/100 | 20/100 | 0.44 (0.20–0.99)",
             "Table 2", "Outcome | placebo | DrugA | OR (95% CI)", "All-cause mortality | 30/100 | 10/100 | 3.86 (1.76–8.45)"]
    assert tr.header_above(lines, 4) is None
    assert tr.header_above(lines, 1) == 0


def test_counts_7_alignment_never_indexes_past_the_row():
    import g1_comparator_table_result as tr
    hc = ["Outcome", "OR (95% CI)", "DrugA (n/N)", "placebo (n/N)"]
    rc = ["All-cause mortality", "0.44 (0.20–0.99)", "10/100", "20/100"]
    fits = tr.aligned(rc, [2, 3], 1)
    assert len(fits) == 1


def test_counts_8_a_non_finite_count_is_none():
    assert bc._int("NaN") is None and bc._int("Infinity") is None


# ----------------------------------------------------------------------------------------------------------- gates
def test_gates_1_an_unnamed_comparator_result_cannot_be_verified_as_ours():
    assert not gt.reported_is_our_outcome(None, "Death due to bleeding", ["death due to bleeding"])


ARMS = {"interv_terms": ["Drug"], "comp_terms": ["Placebo"]}


def test_gates_0_positive_control_a_clean_row_under_a_named_header_is_read():
    # the five refusals below must be refusals OF THEIR OWN GATE, not of an unnamed header
    r = ta.table_tuple("Drug (N = 100) | Placebo (N = 100)\nDeath | 10 (10.0) | 20 (20.0)", ["Death"], **ARMS)
    assert r[1] == {"events_t": 10, "n_t": 100, "events_c": 20, "n_c": 100}
    r = ta.table_tuple("Drug (N = 100) | Placebo (N = 100)\nDeath at 30 days | 10 (10.0) | 20 (20.0)", ["Death"],
                       "30 days", **ARMS)
    assert r is not None


def test_gates_2_a_composite_with_death_is_not_death():
    assert ta.table_tuple("Drug (N = 100) | Placebo (N = 100)\nDeath or hospitalisation | 20 (20.0) | 10 (10.0)", ["Death"], **ARMS) is None


def test_gates_3_a_kaplan_meier_percentage_row_is_not_a_count():
    assert ta.table_tuple("Drug (N = 100) | Placebo (N = 100)\nDeath, Kaplan-Meier estimate % (standard error) | 10 (10.0) | "
                          "20 (20.0)", ["Death"], **ARMS) is None


def test_gates_4_a_placebo_first_header_is_oriented_not_assumed():
    r = ta.table_tuple("Placebo (N = 100) | Drug (N = 100)\nDeath | 20 (20.0) | 10 (10.0)", ["Death"],
                       interv_terms=["Drug"], comp_terms=["Placebo"])
    assert r is None or (r[1]["events_t"], r[1]["events_c"]) == (10, 20)


def test_gates_5_a_different_timepoint_is_not_ours():
    assert ta.table_tuple("Drug (N = 100) | Placebo (N = 100)\nDeath at 365 days | 20 (20.0) | 10 (10.0)", ["Death"],
                          timepoint="30 days", **ARMS) is None


def test_gates_6_a_safety_population_header_is_not_the_randomised_population():
    assert ta.table_tuple("200 participants were randomised, 100 per arm.\nSafety population | Drug (N = 95) | Placebo (N = 95)"
                          "\nDeath | 19 (20.0) | 38 (40.0)", ["Death"], **ARMS) is None


def test_gates_7_tuples_that_differ_in_denominators_are_ambiguous():
    assert ta.table_tuple("Drug (N = 1000) | Placebo (N = 2000)\nDeath | 10 (1.0) | 20 (1.0)\n\nDrug (N = 500) | Placebo "
                          "(N = 500)\nDeath | 10 (2.0) | 20 (4.0)", ["Death"], **ARMS) is None


def test_gates_8_pmc_text_must_be_the_held_paper():
    q = "Drug (N = 100) | Placebo (N = 100)\nDeath | 10 (10.0) | 20 (20.0)"
    resp = dict(verdict="FOUND", source="PMC_TEXT", source_ref="111", measure="COUNTS", events_t=10, n_t=100, events_c=20,
                n_c=100, effect=None, lower=None, upper=None, quote=q)
    held = dict(comp="333", pmid="222", text=q, terms=["Death"], sha="fixture")
    v, _ = ta.gate(resp, held, {"primary_outcome": {"name": "Death", "keywords": ["Death"], "estimand": "RR"}}, "fixture")
    assert v.startswith("REFUSED")


def test_gates_9_a_retrieval_error_is_not_absence(monkeypatch):
    from kgap import k_gap
    from reproducible_ai import record_licence as rl
    monkeypatch.setattr(rl, "pmid_doi", lambda p: "fixture-doi")

    def boom(*a, **k):
        raise TimeoutError("retrieval timed out")
    monkeypatch.setattr(k_gap, "unpaywall_text", boom)
    import pytest
    with pytest.raises(RuntimeError, match="UNPAYWALL_RETRIEVAL_ERROR"):
        ta.unpaywall_evidence("111", ["Death"])        # recorded upstream as EVIDENCE_ERROR, never NO_OPEN_SOURCE


def test_gates_5b_a_protocol_range_or_in_hospital_window_admits_a_label_inside_it():
    # SMART (balanced crystalloids): protocol '28-90 day or in-hospital'; label 'In-hospital death before 30 days' IS in it
    assert ta.label_time_ok("In-hospital death before 30 days — no. (%)", "28-90 day or in-hospital")
    assert not ta.label_time_ok("Death at 365 days", "30 days")
    assert ta.label_time_ok("Death", "30 days")                             # no labelled time: not refused here
    assert not ta.label_time_ok("Death at 180 days", "28-90 day or in-hospital")
