"""A declared COMPOSITE is matched against its declared components, and the components must account for the title
(lane NR, V1.0.1; dapagliflozin HFmrEF/HFpEF review 02f77767).

DELIVER (PMID 36027570): the served primary was once the CARDIOVASCULAR-DEATH COMPONENT (HR 0.88, 0.74-1.05) presented as
the composite 'cardiovascular death or worsening heart failure'; the composite is 0.82 (0.73-0.92). The primary outcome
declared no components, so the classifier fell back to a keyword-family match and a component passed as the composite.
Declared composite = {cardiovascular death, heart failure hospitalisation, urgent heart failure visit}; 'worsening heart
failure' is HF hospitalisation or an urgent HF visit (the trial's own definition). A component-only result must FAIL the
composite; the all-patient result stays distinct from the ejection-fraction subgroups.
"""
from __future__ import annotations

import pytest

from harness import extract, target_endpoint as te

NAME = "Composite cardiovascular death or worsening heart failure"
COMPS = ["cardiovascular death", "heart failure hospitalization", "urgent heart failure visit"]
SPEC = {"name": NAME, "components": COMPS, "estimand": "HR"}
DELIVER = (
    "METHODS: We randomly assigned 6263 patients with heart failure and a left ventricular ejection fraction of more than "
    "40% to receive dapagliflozin (at a dose of 10 mg once daily) or matching placebo, in addition to usual therapy. "
    "The primary outcome was a composite of worsening heart failure (which was defined as either an unplanned "
    "hospitalization for heart failure or an urgent visit for heart failure) or cardiovascular death, as assessed in a "
    "time-to-event analysis. RESULTS: Over a median of 2.3 years, the primary outcome occurred in 512 of 3131 patients "
    "(16.4%) in the dapagliflozin group and in 610 of 3132 patients (19.5%) in the placebo group (hazard ratio, 0.82; 95% "
    "confidence interval [CI], 0.73 to 0.92; P<0.001). Worsening heart failure occurred in 368 patients (11.8%) in the "
    "dapagliflozin group and in 455 patients (14.5%) in the placebo group (hazard ratio, 0.79; 95% CI, 0.69 to 0.91); "
    "cardiovascular death occurred in 231 patients (7.4%) and 261 patients (8.3%), respectively (hazard ratio, 0.88; 95% "
    "CI, 0.74 to 1.05).")
PRIMARY_SRC = ("abstract effect: RESULTS: Over a median of 2.3 years, the primary outcome occurred in 512 of 3131 patients "
               "(16.4%) in the dapagliflozin group and in 610 of 3132 patients (19.5%) in the placebo group (hazard ratio, "
               "0.82; 95% confidence interval [CI], 0.73 to 0.92; P<0.001).")


def test_the_declared_components_account_for_the_title():
    assert te.composite_declaration_problem(SPEC) is None
    assert set(te.canonical_components(SPEC)) == set(COMPS)


def test_a_composite_title_without_declared_components_is_a_declaration_problem():
    assert te.composite_declaration_problem({"name": NAME}) is not None


def test_components_that_do_not_account_for_the_title_are_a_declaration_problem():
    assert te.composite_declaration_problem({"name": NAME, "components": ["cardiovascular death"]}) is not None


def test_worsening_heart_failure_in_a_title_is_hf_hospitalisation_or_an_urgent_hf_visit():
    # title vocabulary only -- the general reader is unchanged (trials define 'worsening heart failure' differently)
    assert {"heart failure hospitalization", "urgent heart failure visit"} <= te.title_components(NAME)


def test_the_cv_death_component_fails_the_composite():
    out = te._classify(SPEC, "cardiovascular death occurred in 231 patients (7.4%) and 261 patients (8.3%), "
                             "respectively (hazard ratio, 0.88; 95% CI, 0.74 to 1.05)")
    assert out["target_endpoint_class"] != te.EXACT_TARGET, out
    v = te._class_verdict(SPEC, out["target_endpoint_class"], out.get("extra_components"),
                          out.get("missing_components"), NAME)
    assert v["admissible"] is False, v


def test_the_full_population_composite_is_admitted_from_its_own_span():
    out = te.classify_bound(SPEC, DELIVER, PRIMARY_SRC)
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out
    assert "0.82" in out["endpoint_result_span"]


def test_the_extractor_takes_the_all_patient_hr_not_a_subgroup():
    ab = DELIVER + (" Among patients with a left ventricular ejection fraction of 60% or more, the hazard ratio for the "
                    "primary outcome was 0.87 (95% CI, 0.72 to 1.04).")
    kws = ["cardiovascular death or worsening heart failure", "primary outcome"]
    ex = extract.extract_trial(ab, kws, ["dapagliflozin"], ["placebo"], declared_composite=True, estimand="HR")
    assert (ex.get("effect"), ex.get("ci_low"), ex.get("ci_high")) == (0.82, 0.73, 0.92), ex


# ---- DPP-4 review: SAVOR-TIMI 53's heart-failure estimate was a false ENDPOINT_UNBOUND in the binder --------------------
SAVOR_HF = ("More patients in the saxagliptin group than in the placebo group were hospitalized for heart failure (3.5% vs. "
            "2.8%; hazard ratio, 1.27; 95% CI, 1.07 to 1.51; P=0.007).")
HHF = {"name": "Hospitalization for heart failure", "keywords": ["hospitalization for heart failure",
       "hospitalized for heart failure"], "estimand": "HR"}


@pytest.mark.xfail(strict=True, reason="NR-C03: SAVOR false-unbound -- the verb form hospitalized-for-heart-failure is not read yet")
def test_hospitalized_for_heart_failure_names_the_hf_hospitalisation_component():
    assert "heart failure hospitalization" in te._components_from_text(SAVOR_HF, expand_named_composites=False)


@pytest.mark.xfail(strict=True, reason="NR-C03: SAVOR false-unbound -- the verb form hospitalized-for-heart-failure is not read yet")
def test_savor_hf_estimate_binds_to_its_own_span():
    b = te.bind_result_span(SAVOR_HF, SAVOR_HF)
    assert b["binding"] == te.BINDING_SELF, b
    out = te._classify(HHF, b["endpoint_definition_span"], components=b["components"])
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out


@pytest.mark.parametrize("text", [
    "Patients hospitalized for heart failure within the previous 12 months were enrolled.",      # a POPULATION phrase
])
def test_a_population_phrase_is_not_the_outcome_result(text):
    # the component reader may name the concept, but a sentence with no result tuple never binds as a result span
    assert te.bind_result_span(text, None)["binding"] == te.BINDING_NONE
