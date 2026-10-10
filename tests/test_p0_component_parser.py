"""P0 (external audit reviews 18, 25, 28, 29): ONE component vocabulary; an unmapped component is NOT ESTABLISHED, never dropped;
a generic MACE label never expands over a stated definition; a composite is never matched by text identity to a registered outcome
that names no component. Each case below failed on main a8a7c4b66."""
from harness import rob2
from harness import target_endpoint as te

ALPHA_OMEGA = ("The primary end point was the rate of major cardiovascular events, which comprised fatal and nonfatal "
               "cardiovascular events and cardiac interventions.")
ODYSSEY_4P = ("death from coronary heart disease, non-fatal myocardial infarction, fatal and non-fatal ischemic stroke, or "
              "unstable angina requiring hospitalization")
ASCEND = ("a composite of nonfatal myocardial infarction, nonfatal stroke (excluding confirmed intracranial hemorrhage), "
          "transient ischemic attack, or vascular death")
MACE3 = "a composite of myocardial infarction, stroke, or death from cardiovascular causes"


def _reg(text):
    return {"measure": text, "title": "", "description": ""}


# ---------------------------------------------------------------- rob2 (D5)
def test_rob2_knows_chd_death():
    assert "CHD_DEATH" in rob2._component_set("CHD death")
    assert {"CHD_DEATH", "NONFATAL_MI", "NONFATAL_STROKE", "UNSTABLE_ANGINA"} <= rob2._component_set(ODYSSEY_4P)


def test_rob2_generic_label_does_not_expand_over_a_stated_definition():
    comps = rob2._component_set(ALPHA_OMEGA)
    assert not (rob2.STANDARD_3P_MACE <= comps)
    assert any(c.startswith(rob2.NOT_ESTABLISHED_PREFIX) and "cardiac interventions" in c for c in comps)


def test_rob2_bare_generic_label_still_expands():
    assert rob2._component_set("major adverse cardiovascular events") == rob2.STANDARD_3P_MACE


def test_rob2_do_health_hypertension_is_not_a_text_identity_match():
    d = rob2._outcome_match_detail("Major vascular events / MACE", _reg("Cardio-vascular: Incident Hypertension"),
                                   lambda a, b: True)
    assert d["matched"] is False and d["method"] == "components_not_established"


def test_rob2_odyssey_chd_death_secondary_is_not_the_pooled_mace():
    d = rob2._outcome_match_detail("Major adverse cardiovascular events", _reg("Time to Coronary Heart Disease Death"),
                                   lambda a, b: True)
    assert d["matched"] is False and d["method"] == "component_set"


def test_rob2_same_composite_still_matches():
    d = rob2._outcome_match_detail("Major adverse cardiovascular events", _reg(MACE3), None)
    assert d["matched"] is True


# ---------------------------------------------------------------- extraction
def test_extraction_alpha_omega_is_not_three_point_mace():
    comps = te._components_from_text(ALPHA_OMEGA)
    assert not ({"cardiovascular death", "myocardial infarction", "stroke"} <= comps)
    assert any(c.startswith(te.NOT_ESTABLISHED_PREFIX) for c in comps)


def test_extraction_ascend_keeps_tia_and_odyssey_keeps_chd_death():
    assert "transient ischemic attack" in te._components_from_text(ASCEND)
    assert "coronary heart disease death" in te._components_from_text(ODYSSEY_4P)


def test_extraction_bare_mace_still_expands_and_a_population_sentence_grows_nothing():
    assert te._components_from_text("major adverse cardiovascular events") == {"cardiovascular death",
                                                                             "myocardial infarction", "stroke"}
    assert te._components_from_text("Diabetes was defined as HbA1c of 6.5% or higher or use of insulin.") == set()
