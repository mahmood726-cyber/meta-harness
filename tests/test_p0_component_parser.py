"""P0 (external audit reviews 18, 25, 28, 29): ONE component vocabulary; an unmapped component is NOT ESTABLISHED, never dropped;
a generic MACE label never expands over a stated definition; a composite is never matched by text identity to a registered outcome
that names no component. Each case below failed on main a8a7c4b66."""
import pytest

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


# ---------------------------------------------------------------- rob2 (D5): NOT in this landing
# The P0 render + rob2_build sweep (11 Oct) showed the shared parser applied to REGISTRY free text gives false NOT_ESTABLISHED
# (doac 'i.e.', HARMONY timing text, RE-LY/ENGAGE 'systemic embolic event', sglt2-ckd 'DoSC'/'renal', PLATO 'death from vascular
# causes'). Rob2 D5 moves to binding #67 rebased onto harness/components.py, with those registry texts as plants. These stay as
# strict xfails until #67 lands them.
_ROB2_PENDING = pytest.mark.xfail(strict=True, reason="rob2 D5 lands with binding #67 on harness/components.py")


@_ROB2_PENDING
def test_rob2_knows_chd_death():
    assert "CHD_DEATH" in rob2._component_set("CHD death")
    assert {"CHD_DEATH", "NONFATAL_MI", "NONFATAL_STROKE", "UNSTABLE_ANGINA"} <= rob2._component_set(ODYSSEY_4P)


@_ROB2_PENDING
def test_rob2_generic_label_does_not_expand_over_a_stated_definition():
    comps = rob2._component_set(ALPHA_OMEGA)
    assert not (rob2.STANDARD_3P_MACE <= comps)
    assert any(c.startswith(rob2.NOT_ESTABLISHED_PREFIX) and "cardiac interventions" in c for c in comps)


def test_rob2_bare_generic_label_still_expands():
    assert rob2._component_set("major adverse cardiovascular events") == rob2.STANDARD_3P_MACE


@_ROB2_PENDING
def test_rob2_do_health_hypertension_is_not_a_text_identity_match():
    d = rob2._outcome_match_detail("Major vascular events / MACE", _reg("Cardio-vascular: Incident Hypertension"),
                                   lambda a, b: True)
    assert d["matched"] is False and d["method"] == "components_not_established"


@_ROB2_PENDING
def test_rob2_odyssey_chd_death_secondary_is_not_the_pooled_mace():
    d = rob2._outcome_match_detail("Major adverse cardiovascular events", _reg("Time to Coronary Heart Disease Death"),
                                   lambda a, b: True)
    assert d["matched"] is False and d["method"] == "component_set"


def test_rob2_same_composite_still_matches():
    d = rob2._outcome_match_detail("Major adverse cardiovascular events", _reg(MACE3), None)
    assert d["matched"] is True


# ---------------------------------------------------------------- extraction
def test_extraction_alpha_omega_is_not_three_point_mace():
    comps = te._components_from_text(ALPHA_OMEGA, mark_unknown=True)
    assert not ({"cardiovascular death", "myocardial infarction", "stroke"} <= comps)
    assert any(c.startswith(te.NOT_ESTABLISHED_PREFIX) for c in comps)


def test_extraction_ascend_keeps_tia_and_odyssey_keeps_chd_death():
    assert "transient ischemic attack" in te._components_from_text(ASCEND)
    assert "coronary heart disease death" in te._components_from_text(ODYSSEY_4P)


def test_extraction_bare_mace_still_expands_and_a_population_sentence_grows_nothing():
    assert te._components_from_text("major adverse cardiovascular events") == {"cardiovascular death",
                                                                             "myocardial infarction", "stroke"}
    assert te._components_from_text("Diabetes was defined as HbA1c of 6.5% or higher or use of insulin.") == set()


# ---------------------------------------------------------------- codex p0-r1 (each failed on 59bbb9f99)
from harness import components as C  # noqa: E402


def test_four_point_label_does_not_override_an_enumerated_fourth_component():
    p = C.components("4-point MACE defined as cardiovascular death, myocardial infarction, stroke, and coronary revascularization.")
    assert p.components == {"cardiovascular death", "myocardial infarction", "stroke", "coronary revascularization"}
    assert p.unknown == []


def test_plain_includes_is_an_enumeration_cue():
    p = C.components("MACE includes cardiovascular death, myocardial infarction, stroke, and cardiac interventions.")
    assert p.enumerated and p.unknown == ["cardiac interventions"]


def test_a_long_parenthetical_does_not_hide_later_items():
    p = C.components("MACE defined as cardiovascular death, myocardial infarction (fatal or nonfatal), stroke, and cardiac "
                     "interventions.")
    assert p.unknown == ["cardiac interventions"]


def test_an_unrelated_renal_condition_is_not_a_known_component():
    p = C.components("MACE defined as cardiovascular death, myocardial infarction, stroke, and renal artery stenosis.")
    assert p.unknown == ["renal artery stenosis"]


def test_an_excluded_component_is_not_named():
    p = C.components("MACE defined as cardiovascular death and myocardial infarction, excluding stroke.")
    assert p.components == {"cardiovascular death", "myocardial infarction"}
    assert "stroke" not in te._components_from_text("MACE defined as cardiovascular death and myocardial infarction, "
                                                    "excluding stroke.")


# ---------------------------------------------------------------- codex p0-r2 / agy p0-r2-agy (each failed on cd4fa68c3)
def test_a_parenthesised_enumeration_is_read_not_deleted():
    p = C.components("MACE (defined as cardiovascular death, myocardial infarction, stroke, or cardiac interventions).")
    assert p.enumerated and p.unknown == ["cardiac interventions"]
    assert any(x.startswith(te.NOT_ESTABLISHED_PREFIX) for x in te._components_from_text("MACE (defined as cardiac interventions)", mark_unknown=True))


def test_an_exclusion_survives_generic_expansion():
    assert C.components("MACE excluding stroke.").components == {"cardiovascular death", "myocardial infarction"}
    assert "stroke" not in te._components_from_text("MACE excluding stroke")


def test_fatal_coronary_heart_disease_is_a_known_item():
    p = C.components("MACE defined as fatal coronary heart disease, nonfatal myocardial infarction, and nonfatal stroke.")
    assert p.unknown == [] and "coronary heart disease death" in p.components


def test_a_definition_in_the_next_sentence_is_read():
    p = C.components("MACE. The endpoint comprised cardiac interventions.")
    assert p.unknown == ["cardiac interventions"] and not p.expanded_generic


def test_a_parenthetical_qualifier_is_not_an_enumeration():
    """LEADER full text: 'nonfatal (including silent) myocardial infarction' -- round 2 made 'silent' an unknown component."""
    s = ("The primary composite outcome in the time-to-event analysis was the first occurrence of death from cardiovascular "
         "causes, nonfatal (including silent) myocardial infarction, or nonfatal stroke.")
    assert C.components(s).unknown == []
    assert te._components_from_text(s) == {"cardiovascular death", "myocardial infarction", "stroke"}


# ---------------------------------------------------------------- KNOWN LIMITS (codex p0-r3 #1-#4), recorded at stop-at-three
# A regex enumerator over free text cannot close every synthetic phrasing; each review round found new ones. These four are NOT
# present in any of the 53 served definition spans (probe recorded in the PR). They are strict xfails: if one starts passing,
# the limit is gone and the marker must be removed. The architecture question (a recorded two-family reader for definition
# spans, regex as cross-check) is with Mahmood.
import pytest  # noqa: E402

_LIMITS = [
    ("MACE (cardiovascular death, myocardial infarction, stroke, and cardiac interventions).", "unkeyed parenthetical list"),
    ("The endpoint consisted of cardiovascular death, myocardial infarction, stroke, and cardiac interventions.",
     "'consisted of' is a subject cue but not an enumeration cue"),
    ("The composite of cardiovascular death, myocardial infarction, and stroke plus cardiac interventions.",
     "'plus' is not an item separator"),
]


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex p0-r3): see _LIMITS")
@pytest.mark.parametrize("text,why", _LIMITS)
def test_known_limit_unknown_component_found(text, why):
    assert C.components(text).unknown == ["cardiac interventions"], why


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex p0-r3 #4): excluding a SUBTYPE removes the whole component")
def test_known_limit_subtype_exclusion():
    s = "The composite of cardiovascular death, myocardial infarction, and stroke (excluding hemorrhagic stroke)."
    assert C.components(s).components == {"cardiovascular death", "myocardial infarction", "stroke"}


def test_major_vascular_events_is_not_expanded_to_three_point_mace():
    """statins-elderly: 'Major vascular events' is the CTT composite (coronary events, stroke AND revascularization); P0 first
    expanded it to 3-point MACE and refused both pooled trials (JUPITER for unstable angina)."""
    assert te._components_from_text("Major vascular events") == set()
    assert te.canonical_components({"name": "Major vascular events"}) == []
    assert rob2._component_set("Major vascular events") == frozenset()


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex p0-r4 #3): an eligibility exclusion ('excluding patients with prior "
                                       "stroke') is read as an endpoint exclusion; 0 of 321 served texts carry one (probe)")
def test_known_limit_population_exclusion():
    s = "The primary endpoint was MACE. Eligibility criteria: excluding patients with prior stroke."
    assert C.components(s).components == {"cardiovascular death", "myocardial infarction", "stroke"}


@_ROB2_PENDING
def test_rob2_excluded_component_is_not_named():
    assert "NONFATAL_STROKE" not in rob2._component_set("MACE defined as cardiovascular death and myocardial infarction, "
                                                         "excluding stroke.")


def test_d20_the_unknown_item_rule_is_off_for_registry_text():
    """D20 (Mahmood 'c'): the unknown-item rule applies ONLY to served abstract/full-text definition spans. A registry candidate
    ('Composite of Stroke and Systemic Embolic Events (SEE)') is parsed without it -- the render showed 'component not
    established: see' turning a G1 noac family's outcome from extractable to unknown."""
    reg = "Yearly Event Rate for Composite Endpoint of Stroke/SEE Time to first occurrence of stroke or systemic embolic event"
    assert not any(c.startswith(te.NOT_ESTABLISHED_PREFIX) for c in te._components_from_text(reg))
    assert any(c.startswith(te.NOT_ESTABLISHED_PREFIX) for c in te._components_from_text(ALPHA_OMEGA, mark_unknown=True))


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex p0-r5 #1): an item recognised only by the union list (e.g. pulmonary "
                                       "embolism) is accepted but not returned as a component (main dropped it entirely)")
def test_known_limit_union_list_item_not_returned():
    p = C.components("MACE defined as cardiovascular death, myocardial infarction, stroke, or pulmonary embolism.")
    assert p.components != {"cardiovascular death", "myocardial infarction", "stroke"} or p.unknown


@pytest.mark.xfail(strict=True, reason="KNOWN LIMIT (codex p0-r5 #4): an exclusion LIST stops at its first comma; 0 served texts "
                                       "carry an exclusion clause (probe of 321)")
def test_known_limit_exclusion_list():
    p = C.components("MACE excluding transient ischemic attack, unstable angina, and revascularization.")
    assert p.components == {"cardiovascular death", "myocardial infarction", "stroke"}
