"""Plant: the verb form of heart-failure hospitalisation names the endpoint (SAVOR-TIMI 53's abstract result sentence was
ENDPOINT_UNBOUND while TECOS's noun form bound -- 6 Oct). 'hospitalized with heart failure' describes a population and is
not read as the endpoint."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import target_endpoint as te  # noqa: E402

SAVOR = ("More patients in the saxagliptin group than in the placebo group were hospitalized for heart failure "
         "(3.5% vs. 2.8%; hazard ratio, 1.27; 95% CI, 1.07 to 1.51; P=0.007).")


def test_the_verb_form_names_hhf():
    assert "heart failure hospitalization" in te._components_from_text(SAVOR, expand_named_composites=False)
    # a participle binds when the sentence states a result (an event with numbers), not when it only names a group
    assert "heart failure hospitalization" in te._components_from_text(
        "patients hospitalised because of worsening heart failure: 4.1% vs 5.2%")
    assert "heart failure hospitalization" not in te._components_from_text(
        "patients hospitalised because of worsening heart failure")


def test_the_noun_form_still_does():
    assert "heart failure hospitalization" in te._components_from_text(
        "Rates of hospitalization for heart failure did not differ (hazard ratio, 1.00; 95% CI, 0.83 to 1.20)")


def test_a_population_hospitalized_with_heart_failure_is_not_the_endpoint():
    assert "heart failure hospitalization" not in te._components_from_text(
        "We randomly assigned patients hospitalized with heart failure to the drug or placebo.")


def test_an_eligibility_sentence_is_not_an_hhf_endpoint():
    # codex captain-v8-groundwork g1#1: a participle describing who enrolled is not an event
    from harness.target_endpoint import _components_from_text
    assert "heart failure hospitalization" not in _components_from_text(
        "Patients hospitalized for heart failure were eligible for enrollment.")
    assert "heart failure hospitalization" not in _components_from_text(
        "Patients who were hospitalized for heart failure in the previous year were eligible.")
    assert "heart failure hospitalization" in _components_from_text(
        "Patients were hospitalized for heart failure (3.5% vs. 2.8%; hazard ratio, 1.27).")
