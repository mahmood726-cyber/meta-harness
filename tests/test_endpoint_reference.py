"""Endpoint-REFERENCE resolution before component comparison (external audit, 2026-09-20, adopted as the rule).

The binder grouped candidate definitions by their component sets and, when one distinct set remained, took the
FIRST definition. Two endpoints can share every event type and differ in follow-up (30 days vs 36 months) or
population (all randomised vs >= 65 years): component equality does not make their definitions interchangeable,
and sentence order was acting as the selection rule. Acceptance criterion, verbatim: "The result is linked to the
endpoint it actually names, regardless of sentence order or other endpoints described nearby."

Synthetic passages, as in the audit; none of these is a claim about a served page (scripts/endpoint_reference_sweep.py
measures the served corpus separately). Positives are as mandatory as attacks: E04 exists so that a blanket
"refuse whenever several definitions exist" cannot pass as the cure.
"""
import pytest

from harness import target_endpoint as te

DEF_30D = ("The first primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial "
           "infarction, or nonfatal stroke within 30 days.")
DEF_36M = ("The second primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial "
           "infarction, or nonfatal stroke within 36 months.")
RESULT_SECOND = "The second primary outcome had a hazard ratio of 0.88 (95% CI, 0.79 to 0.99)."
RESULT_FIRST = "The first primary outcome had a hazard ratio of 0.95 (95% CI, 0.80 to 1.12)."
UNRELATED_SECONDARY = "The key secondary outcome was all-cause mortality at 36 months."


def _bind(*sentences, result):
    return te.bind_result_span(" ".join(sentences), result)


# ---------------------------------------------------------------- E01: same components, different follow-up
def test_PLANT_E01_result_naming_the_second_endpoint_binds_the_second_definition_not_the_first():
    b = _bind(DEF_30D, DEF_36M, result=RESULT_SECOND)
    assert b["binding"] == te.BINDING_DEFINITION
    assert b["endpoint_definition_span"] == DEF_36M, b
    assert b["endpoint_reference"]["ordinal"] == 2


def test_E01_the_first_result_binds_the_first_definition():
    b = _bind(DEF_30D, DEF_36M, result=RESULT_FIRST)
    assert b["endpoint_definition_span"] == DEF_30D


# ---------------------------------------------------------------- order invariance: the sentence order is not a rule
@pytest.mark.parametrize("order", [(DEF_30D, DEF_36M), (DEF_36M, DEF_30D)], ids=["first-def-first", "second-def-first"])
def test_PLANT_order_invariance_same_evidence_same_binding(order):
    b = _bind(*order, result=RESULT_SECOND)
    assert b["endpoint_definition_span"] == DEF_36M, (order[0][:40], b["endpoint_definition_span"])


# ---------------------------------------------------------------- E02: same components, different population
DEF_ALL = ("The primary outcome, in all randomized participants, was the composite of death from cardiovascular "
           "causes, nonfatal myocardial infarction, or nonfatal stroke.")
DEF_OLD = ("The primary outcome in participants aged 65 years or older was the composite of death from "
           "cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke.")
RESULT_OLD = ("Among participants aged 65 years or older, the primary outcome had a hazard ratio of 0.90 "
              "(95% CI, 0.81 to 1.00).")


def test_PLANT_E02_result_naming_a_population_binds_that_populations_definition():
    b = _bind(DEF_ALL, DEF_OLD, result=RESULT_OLD)
    assert b["binding"] == te.BINDING_DEFINITION
    assert b["endpoint_definition_span"] == DEF_OLD, b


# ---------------------------------------------------------------- E04: different components, explicit reference
DEF_CVD = "The first primary outcome was death from cardiovascular causes."
DEF_COMP = ("The second primary outcome was the composite of death from cardiovascular causes, nonfatal myocardial "
            "infarction, or nonfatal stroke.")


def test_PLANT_E04_explicit_reference_resolves_between_different_definitions_instead_of_refusing():
    """The mirror image: valid evidence must not be refused because two definitions differ -- the result says
    which one it is. A blanket refusal on 'several definitions' fails here."""
    b = _bind(DEF_CVD, DEF_COMP, result=RESULT_SECOND)
    assert b["binding"] == te.BINDING_DEFINITION
    assert b["endpoint_definition_span"] == DEF_COMP
    assert b["components"] == {"cardiovascular death", "myocardial infarction", "stroke"}


# ---------------------------------------------------------------- genuine ambiguity abstains, never picks a winner
RESULT_BARE = "The primary outcome had a hazard ratio of 0.88 (95% CI, 0.79 to 0.99)."


def test_PLANT_unresolved_reference_between_two_endpoints_is_an_explicit_ambiguity_state():
    b = _bind(DEF_30D, DEF_36M, result=RESULT_BARE)
    assert b["binding"] == te.BINDING_NONE
    assert b["endpoint_definition_span"] is None
    assert len(b["definition_candidates"]) == 2 and len(b["unresolved_alternatives"]) == 2
    assert "reference" in b["binding_reason"] and "2" in b["binding_reason"]


# ---------------------------------------------------------------- benign controls
def test_control_an_unrelated_secondary_definition_does_not_disrupt():
    b = _bind(DEF_30D, UNRELATED_SECONDARY, result=RESULT_FIRST)
    assert b["endpoint_definition_span"] == DEF_30D
    b2 = _bind(UNRELATED_SECONDARY, DEF_36M, result=RESULT_BARE)
    assert b2["binding"] == te.BINDING_DEFINITION and b2["endpoint_definition_span"] == DEF_36M


def test_control_an_identical_repeated_definition_is_a_harmless_duplicate_not_ambiguity():
    d = ("The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, "
         "or nonfatal stroke.")
    b = _bind(d, "Methods were as previously described.", d, result=RESULT_BARE)
    assert b["binding"] == te.BINDING_DEFINITION and b["endpoint_definition_span"] == d
    assert b["unresolved_alternatives"] == []


def test_control_reordering_components_within_one_definition_still_binds():
    d = ("The primary outcome was a composite of nonfatal stroke, nonfatal myocardial infarction, or death from "
         "cardiovascular causes.")
    b = _bind(d, result=RESULT_BARE)
    assert b["binding"] == te.BINDING_DEFINITION
    assert b["components"] == {"cardiovascular death", "myocardial infarction", "stroke"}


# ---------------------------------------------------------------- auditability: the record says what happened
def test_PLANT_record_exposes_candidates_reference_selection_and_alternatives():
    b = _bind(DEF_30D, DEF_36M, result=RESULT_SECOND)
    assert [c["span"] for c in b["definition_candidates"]] == [DEF_30D, DEF_36M]
    assert b["endpoint_reference"] == {"ordinal": 2, "qualifier": "primary", "timepoint": None, "population": None}
    assert b["selected_definition"] == DEF_36M
    assert b["unresolved_alternatives"] == []
    assert "one definition span found" not in b["binding_reason"], \
        "a report that says 'one definition found' when it means 'one component list' misleads the reader"
    assert "ordinal" in b["binding_reason"]


# ---------------------------------------------------------------- compatibility, from the corpus sweep
EXSCEL_DEF = ("The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal "
              "myocardial infarction, or nonfatal stroke.")
EXSCEL_DISCUSSION = ("In trials that assessed cardiovascular outcomes in patients with type 2 diabetes who had "
                     "cardiovascular disease, the composite of death from cardiovascular causes, nonfatal myocardial "
                     "infarction, or nonfatal stroke was the primary outcome.")
EXSCEL_RESULT = "The primary composite outcome occurred in 839 patients (hazard ratio, 0.91; 95% CI, 0.83 to 1.00)."


def test_PLANT_a_restatement_that_mentions_the_trial_population_is_the_same_endpoint_not_a_second_one():
    """scripts/endpoint_reference_sweep.py on the served corpus: the strict rule (merge only identical text) would
    have set EXSCEL and VITAL aside because a discussion sentence restating the composite mentioned a population
    while the definition stated none. 'Stated' versus 'not stated' is not a conflict; a blanket refusal on
    'several definitions' is exactly the cure E04 exists to prevent."""
    b = _bind(EXSCEL_DEF, EXSCEL_DISCUSSION, result=EXSCEL_RESULT)
    assert b["binding"] == te.BINDING_DEFINITION, b["binding_reason"]
    assert b["endpoint_definition_span"] == EXSCEL_DEF
    assert b["components"] == {"cardiovascular death", "myocardial infarction", "stroke"}


def test_two_stated_populations_that_differ_still_conflict():
    b = _bind(DEF_ALL, DEF_OLD, result=RESULT_BARE)
    assert b["binding"] == te.BINDING_NONE and len(b["unresolved_alternatives"]) == 2
