"""Only abbreviations defined for this outcome in the same abstract may bind."""
import json
from pathlib import Path

import pytest

from harness.extract import extract_trial


ROOT = Path(__file__).resolve().parents[1]
# User-supplied CC BY abstract excerpt, BMC Cardiovascular Diabetology.
ABSTRACT = (
    "The primary objective was to assess the cardiovascular safety of omarigliptin. "
    "Analyses included the primary composite cardiovascular endpoint (MACE, the composite of CV death, "
    "nonfatal myocardial infarction, and nonfatal stroke) and the analysis of first event of "
    "hospitalization for heart failure (hHF). The median follow-up was approximately 96 weeks "
    "(range 1.1-178.6 weeks). The primary MACE outcome occurred in 114/2092 patients in the "
    "omarigliptin group (5.45%; 2.96/100 patient-years) and 114/2100 patients in the placebo group "
    "(5.43%; 2.97/100 patient-years), with a hazard ratio (HR) of 1.00 (95% confidence interval "
    "[CI] 0.77, 1.29). The hHF outcome occurred in 20/2092 patients in the omarigliptin group "
    "(0.96%; 0.51/100 patient-years) and 33/2100 patients in the placebo group "
    "(1.57%; 0.85/100 patient-years), with an HR of 0.60 (95% CI 0.35, 1.05)."
)


@pytest.fixture
def topic():
    return json.loads((ROOT / "topics/dpp4-mace-t2d.json").read_text(encoding="utf-8"))


def extract_hhf(abstract, topic):
    outcome = next(o for o in topic["harm_outcomes"]
                   if o["name"] == "Hospitalization for heart failure")
    return extract_trial(
        abstract, outcome["keywords"], topic["intervention_terms"],
        topic["comparator_terms"], declared_composite=False,
        estimand=outcome["estimand"],
    )


def test_real_defined_hhf_prefers_reported_hr(topic):
    abstract = ABSTRACT
    result = extract_hhf(abstract, topic)
    assert not result.get("absent"), result
    assert (result["scale"], result["effect"], result["ci_low"], result["ci_high"]) == (
        "HR", 0.60, 0.35, 1.05,
    )
    assert "ai" not in result
    prefix = "abstract source-reported HR (registered estimand): "
    assert result["source"].startswith(prefix)
    span = result["source"][len(prefix):]
    assert "hHF" in span
    assert span in " ".join(abstract.split())
    # An abbreviation learned above must not leak into another abstract.
    assert extract_hhf(HHF_RESULT, topic).get("absent") is True


# Synthetic negative controls; these numbers are test stimuli, not research output.
HHF_RESULT = "The hHF outcome had an HR of 0.60 (95% CI 0.35, 1.05)."


def test_undefined_hhf_does_not_match(topic):
    assert extract_hhf(HHF_RESULT, topic).get("absent") is True


def test_unrelated_hhf_definition_does_not_match(topic):
    abstract = "We assessed hypoglycemia-related hospital fees (hHF). " + HHF_RESULT
    assert extract_hhf(abstract, topic).get("absent") is True


def test_same_abstract_mace_is_unchanged(topic):
    outcome = topic["primary_outcome"]
    result = extract_trial(
        ABSTRACT, outcome["keywords"], topic["intervention_terms"],
        topic["comparator_terms"], declared_composite=True,
        estimand=outcome["estimand"],
    )
    assert not result.get("absent"), result
    assert (result["scale"], result["effect"], result["ci_low"], result["ci_high"]) == (
        "HR", 1.00, 0.77, 1.29,
    )
    assert "ai" not in result


# Synthetic review-round regression inputs; counts are test stimuli.
def test_parenthetical_adjudicated_is_not_an_alias():
    from harness.extract import _outcome_sentences

    keyword_sentence = "Hospitalization for heart failure (adjudicated) was a secondary endpoint."
    abstract = (keyword_sentence + " Adjudicated myocardial infarction occurred in 20 patients "
                "receiving omarigliptin and 33 receiving placebo.")
    assert _outcome_sentences(abstract, ["hospitalization for heart failure"]) == [keyword_sentence]


def test_composite_dhhf_is_not_a_component_alias():
    from harness.extract import _outcome_sentences

    keyword_sentence = (
        "The primary endpoint was cardiovascular death or hospitalization for heart failure (DHHF)."
    )
    abstract = (keyword_sentence + " DHHF occurred in 20 patients receiving omarigliptin "
                "and 33 receiving placebo.")
    assert _outcome_sentences(abstract, ["hospitalization for heart failure"]) == [keyword_sentence]
