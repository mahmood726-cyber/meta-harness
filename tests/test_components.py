"""P0 (DISPATCH_REVIEW29): ONE component parser for extraction AND rob2. Every plant fails on main (a8a7c4b66).

Strings are copied from the held sources: the served rows' endpoint_definition_span and the registered outcomes in
cache/<slug>/rob2.json (AACT design_outcomes)."""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import components as C  # noqa: E402
from harness import rob2, target_endpoint as te  # noqa: E402

ODYSSEY_DEF = ("The primary end point was a composite of death from coronary heart disease, nonfatal myocardial "
               "infarction, fatal or nonfatal ischemic stroke, or unstable angina requiring hospitalization.")
ODYSSEY_PRIMARY = {"measure": "Time to First Occurrence of Major Adverse Cardiovascular Event (MACE); Percentage of "
                              "Observed Participants With Outcome Measure Events During the Study", "title": "",
                   "description": "All MACE positively adjudicated by Clinical Events Committee (CEC) in a blinded fashion, "
                                  "were used in the analysis of the composite cardiovascular (CV) outcome measure comprised "
                                  "of Coronary Heart Disease (CHD) death, non-fatal Myocardial Infarction (MI), fatal and "
                                  "non-fatal ischemic stroke (IS), or unstable angina (UA) requiring hospitalization. "
                                  "Kaplan Meier plots of the cumulative incidence rate by treatment groups were used to "
                                  "depict the first occurrence of MACE over time."}
ODYSSEY_CHD_DEATH = {"measure": "Time to Coronary Heart Disease Death; Percentage of Observed Participants With Outcome "
                                "Measure Events During the Study", "title": "",
                     "description": "Kaplan Meier plots of the cumulative incidence rate by treatment groups were used to "
                                    "depict the CHD death over time."}
ALPHA_OMEGA_DEF = ("The primary end point was the rate of major cardiovascular events, which comprised fatal and nonfatal "
                   "cardiovascular events and cardiac interventions.")
DAPA_PRIMARY = {"measure": "Subjects Included in the Composite Endpoint of CV Death, Hospitalization Due to Heart Failure "
                           "or Urgent Visit Due to Heart Failure.", "title": "", "description": "Primary efficacy"}
COLCOT_PRIMARY = {"measure": "First Event of Cardiovascular Death, Resuscitated Cardiac Arrest, Acute Myocardial "
                             "Infarction, Stroke, or Urgent Hospitalization for Angina Requiring Coronary "
                             "Revascularization", "title": "", "description": ""}
CLEAR_COPRIMARY2 = {"measure": "Composite of cardiovascular death, new or worsening heart failure, recurrent myocardial "
                               "infarction, or stroke (co-primary 2)", "title": "", "description": ""}
DO_HEALTH_HTN = {"measure": "Cardio-vascular: Incident Hypertension", "title": "", "description": ""}


# ------------------------------------------------------------------------------------------------- the vocabulary
def test_PLANT_chd_death_is_one_component_of_both_routes():
    assert "coronary heart disease death" in C.names(ODYSSEY_DEF)
    assert C.names("CHD death") == {"coronary heart disease death"}
    assert C.parse("CHD death").ids() == {"CHD_DEATH"}
    # the dispatch's reproduction on main: rob2 dropped it
    p = C.parse("death from coronary heart disease, non-fatal myocardial infarction, ischemic stroke, or unstable angina")
    assert p.components == {"coronary heart disease death", "myocardial infarction", "stroke", "unstable angina"}
    assert p.established


def test_PLANT_both_routes_read_the_same_components():
    for text in (ODYSSEY_DEF, DAPA_PRIMARY["measure"], COLCOT_PRIMARY["measure"], "CHD death"):
        assert te._components_from_text(text, expand_named_composites=False) == C.names(text), text
        assert {C.NAMES[i] for i in rob2._component_set_v3(text)} == C.names(text), text


def test_PLANT_an_unknown_component_is_reported_never_dropped():
    p = C.parse(ALPHA_OMEGA_DEF)                                   # Alpha Omega (28-01)
    assert "cardiac intervention" in p.components
    assert p.unrecognised and not p.established


def test_PLANT_a_generic_label_never_expands_from_source_text():
    p = C.parse("major adverse cardiovascular events")
    assert p.generic_only and not p.components
    assert te._components_from_text("major adverse cardiovascular events", expand_named_composites=True) == set()
    # an explicit 3-point label names the standard set
    assert C.names("3-point MACE") == set(C.STANDARD_3P)
    # the REVIEW's declared target still has its 3-point set (a protocol decision, not a source reading)
    assert set(te.canonical_components({"name": "Major vascular events / MACE"})) == set(C.STANDARD_3P)


def test_ascend_tia_is_unchanged():
    assert "transient ischemic attack" in C.names(
        "serious vascular event (nonfatal myocardial infarction, nonfatal stroke, transient ischemic attack, or vascular "
        "death)")


# --------------------------------------------------------------------------------------------- extraction route
def test_PLANT_alpha_omega_is_not_established_not_exact():
    abstract = ALPHA_OMEGA_DEF + (" Neither EPA-DHA nor ALA reduced this primary end point (hazard ratio with EPA-DHA, "
                                  "1.01; 95% confidence interval [CI], 0.87 to 1.17; P=0.93).")
    cls = te.classify_bound({"name": "Major vascular events / MACE"}, abstract,
                            "abstract: Neither EPA-DHA nor ALA reduced this primary end point (hazard ratio with EPA-DHA, 1.01")
    assert cls["target_endpoint_class"] == te.ENDPOINT_UNBOUND, cls
    assert cls.get("components_not_established")
    assert "NOT_ESTABLISHED" in cls["endpoint_binding_reason"]


def test_PLANT_bare_mace_binds_to_the_trials_own_listed_definition():
    abstract = ("Major adverse cardiovascular events (MACE) were defined as cardiovascular death, myocardial "
                "infarction, stroke, or coronary revascularization. MACE occurred in 120 of 2000 patients in the drug "
                "group and 160 of 2000 in the placebo group (hazard ratio, 0.75; 95% CI, 0.59 to 0.95).")
    cls = te.classify_bound({"name": "Major vascular events / MACE"}, abstract,
                            "abstract: MACE occurred in 120 of 2000 patients in the drug group")
    assert "coronary revascularization" in cls["target_components"]
    assert cls["target_endpoint_class"] != te.EXACT_TARGET


def test_odyssey_binds_chd_death():
    cls = te.classify_bound({"name": "Major adverse cardiovascular events"},
                            ODYSSEY_DEF + " The primary end point occurred in 903 patients (9.5%) in the alirocumab group "
                            "and 1052 (11.1%) in the placebo group (hazard ratio, 0.85; 95% CI, 0.78 to 0.93).",
                            "abstract: The primary end point occurred in 903 patients (9.5%) in the alirocumab group")
    assert "coronary heart disease death" in cls["target_components"]


# ---------------------------------------------------------------------------------------------------- rob2 route
def _d5(selected, primaries=(), secondaries=()):
    return rob2.derive_d5_v3(list(primaries), list(secondaries), selected)


def test_PLANT_odyssey_d5_matches_its_primary_by_components_not_chd_death_by_title():
    d = _d5({"pooled_outcome": "Major adverse cardiovascular events", "definition_span": ODYSSEY_DEF},
            [ODYSSEY_PRIMARY], [ODYSSEY_CHD_DEATH])
    c = d["inputs"]["comparison"]
    assert d["level"] == "low" and c["registered_type"] == "primary" and c["method"] == "component_set", d["basis"]


def test_PLANT_do_health_mace_is_never_text_identical_to_incident_hypertension():
    d = _d5({"pooled_outcome": "Major vascular events / MACE"}, [], [DO_HEALTH_HTN])
    assert d["level"] != "low" or d["inputs"]["comparison"].get("method") != "text_identity", d


def test_PLANT_text_identity_is_by_terms_never_by_similarity():
    # DO-HEALTH (28-02): an empty registered description never licenses a loose match -- identity is by TERMS only
    assert rob2.outcome_match_v3("Major vascular events / MACE", DO_HEALTH_HTN)["method"] != "text_identity"
    for a, b in (("Recurrent pericarditis", "Symptom persistence at 72 hours"),
                 ("28-day all-cause mortality", "Ventilator-Free Days to Day 28"),
                 ("Major vascular events", "Major cardiovascular events")):
        assert not rob2._term_identity(a, b), (a, b)
    # the same terms after folding synonyms / plurals / neutral qualifiers are identity, whatever the description
    for a, b in (("Mortality", "Death from all causes"), ("All-cause mortality", "Day 28 all causes mortality"),
                 ("Antibiotic-associated diarrhoea", "Incidence of Antibiotic-Associated diarrhea (AAD)"),
                 ("New vertebral fracture", "Number of Participants With New Vertebral Fractures")):
        assert rob2._term_identity(a, b), (a, b)


def test_PLANT_r18_dapa_hf_secondary_is_not_the_broader_primary():
    out = rob2.outcome_match_v3("Composite of cardiovascular death or hospitalisation for heart failure", DAPA_PRIMARY)
    assert out["matched"] is not True


@pytest.mark.parametrize("registered", [COLCOT_PRIMARY, CLEAR_COPRIMARY2])
def test_PLANT_r25_a_generic_target_never_matches_a_wider_registered_composite(registered):
    d = _d5({"pooled_outcome": "Major adverse cardiovascular events"}, [registered])
    assert d["level"] != "low", (registered["measure"], d["basis"])


def test_a_held_definition_span_beats_a_title_match():
    # the selected row's definition is ODYSSEY's 4-point composite: the CHD-death secondary's title can never win
    d = _d5({"pooled_outcome": "Coronary heart disease death", "definition_span": ODYSSEY_DEF}, [], [ODYSSEY_CHD_DEATH])
    assert d["inputs"]["comparison"].get("method") != "text_identity"


def test_PLANT_label_identity_beats_a_description_that_enumerates_causes_of_death():
    """EMPHASIS-HF (28824029): the registered 'First Occurrence of All-Cause Mortality' describes all-cause mortality by
    its causes (CV death incl. MI, stroke, arrhythmia, PE; non-CV death). The description elaborates; the label names
    the same single component in the same terms, so it IS the selected outcome. A held definition span never takes
    this route (rule 4c), and a label whose terms differ never does (rule 4b)."""
    reg = {"title": "Number of Participants With With First Occurrence of All-Cause Mortality",
           "description": "All-cause mortality was defined as any CV mortality (death due to myocardial infarction, "
                          "stroke, cardiac arrhythmia, pulmonary embolism), Non-CV mortality, including malignant "
                          "tumor, pulmonary disease and trauma."}
    d = rob2.outcome_match_v3("All-cause mortality", reg)
    assert d["matched"] is True and d["method"] == "label_identity"
    assert rob2.outcome_match_v3("All-cause mortality", reg, is_definition=True)["matched"] is not True
    assert rob2.outcome_match_v3("Cardiovascular death", reg)["matched"] is not True


def test_PLANT_an_umbrella_hf_event_is_not_established_against_specific_hf_components():
    """DELIVER / EMPEROR-Preserved: the topic outcome 'cardiovascular death or worsening heart failure' names an
    UNSPECIFIED heart-failure event; the registered primary lists the specific events. With no held definition span the
    umbrella can neither match (rule 3: never expanded) nor be called a mismatch -- it is NOT_ESTABLISHED. The old
    v2 rule matched it to the 'CV death' secondary alone."""
    reg = {"title": "Subjects Included in the Composite Endpoint of CV Death, Hospitalization Due to Heart Failure or "
                    "Urgent Visit Due to Heart Failure.", "description": ""}
    d = rob2.outcome_match_v3("Composite cardiovascular death or worsening heart failure", reg)
    assert d["matched"] is None and d["method"] == "umbrella_not_established"
    cv = {"title": "Subjects Included in the Endpoint of Cardiovascular Death", "description": ""}
    assert rob2.outcome_match_v3("Composite cardiovascular death or worsening heart failure", cv)["matched"] is False


def test_PLANT_a_generic_label_without_a_definition_is_not_established_never_a_mismatch_or_a_similarity_match():
    """STAREE-type case: the pooled 'Major vascular events' v the registered 'Major cardiovascular events'. Main matched
    them by embedding similarity (rule 4: never). Neither side lists components, so neither identity nor mismatch is
    established (rule 3) -- NOT_ESTABLISHED; an unrelated registered outcome is still a plain mismatch."""
    d = rob2.outcome_match_v3("Major vascular events", {"title": "Major cardiovascular events", "description": ""})
    assert d["matched"] is None and d["method"] == "generic_not_established"
    other = {"title": "Disability free survival - death or development of dementia", "description": ""}
    assert rob2.outcome_match_v3("Major vascular events", other)["matched"] is False


def test_PLANT_a_generic_cv_label_v_a_death_or_disability_outcome_is_a_mismatch_not_unestablished():
    """All-cause death is not a cardiovascular component for this rule: STAREE's registered primary 'Disability free
    survival - death or development of dementia or development of persistent physical disability' is simply not
    'Major vascular events'."""
    reg = {"title": "Disability free survival - death or development of dementia or development of persistent physical "
                    "disability", "description": "Death from any cause, dementia, or persistent physical disability."}
    assert rob2.outcome_match_v3("Major vascular events", reg)["matched"] is False


def test_PLANT_the_basis_of_an_unestablished_generic_or_umbrella_label_says_so():
    d = rob2.derive_d5_v3([{"measure": "Major cardiovascular events"}], [],
                          {"pooled_outcome": "Major vascular events", "registered_title": None, "role": None})
    assert d["level"] == "not_assessable" and "unrecognised component(s) []" not in d["basis"]
    assert "generic" in d["basis"]
    u = rob2.derive_d5_v3([{"measure": "CV death, hospitalization for heart failure or urgent heart failure visit"}], [],
                          {"pooled_outcome": "Cardiovascular death or worsening heart failure", "registered_title": None,
                           "role": None})
    assert u["level"] == "not_assessable" and "unspecified heart-failure event" in u["basis"]
