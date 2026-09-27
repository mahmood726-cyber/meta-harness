"""EXCLUSION POLARITY in the PRODUCER (lane NR, V1.0.1). The producer read 'stroke' as a component whenever the word
appeared, so 'cardiovascular death or nonfatal MI; nonfatal stroke was excluded from the primary outcome' classified as
3-point MACE (EXACT_TARGET) -- M2 battery W4a (SOUL, hand row) / W4b (SUSTAIN-6, abstract row), WRONG_ADMISSION.

Requirement: an endpoint is typed relations INCLUDES(x) / EXCLUDES(x). The included set is built from positive relations
only; an explicitly excluded TARGET component is ENDPOINT_COMPONENT_EXCLUDED (refused). The relations are the verifier's
own (scripts/verify_bundle.py split_exclusions / analysis_exclusions -- one semantic module, producer and verifier).
Meaning-preserving controls must still classify EXACT_TARGET: a POPULATION exclusion, a qualifier on a component
('nonfatal MI excluding silent infarction'), and '3-point MACE excluding unstable angina'.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

from harness import target_endpoint as te

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_bundle as vb  # noqa: E402

SPEC = {"name": "3-point major adverse cardiovascular events"}
T = "(hazard ratio, 0.87; 95% CI, 0.78 to 0.97)"


def _cls(text):
    return te._classify(SPEC, text)["target_endpoint_class"]


# ---- the defect: an excluded component read as included -------------------------------------------------------------
@pytest.mark.parametrize("text", [
    # W4b's wording (SUSTAIN-6 edit)
    "The primary composite outcome was the first occurrence of cardiovascular death or nonfatal myocardial infarction; "
    "nonfatal stroke was excluded from the primary composite outcome.",
    # W4a's wording (SOUL edit)
    "a composite of death from cardiovascular causes or nonfatal myocardial infarction; nonfatal stroke was excluded "
    "from the primary outcome",
    # an exclusion SCOPE, not a statement
    "The primary outcome was cardiovascular death only, excluding nonfatal myocardial infarction and nonfatal stroke.",
    "The primary outcome was any cardiovascular event other than nonfatal myocardial infarction or nonfatal stroke.",
])
def test_an_excluded_target_component_is_refused_not_matched(text):
    out = te._classify(SPEC, text)
    assert out["target_endpoint_class"] == te.ENDPOINT_COMPONENT_EXCLUDED, out
    assert "stroke" in out["excluded_components"]
    assert "stroke" not in out["target_components"]                  # mentioning what is excluded never includes it


def test_an_exclusion_in_the_NEXT_sentence_cuts_the_bound_definition():
    abstract = ("The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial "
                "infarction, or nonfatal stroke. The primary outcome occurred in fewer patients " + T + ". "
                "*Nonfatal stroke was excluded from the primary analysis.")
    source = "abstract effect: The primary outcome occurred in fewer patients " + T + "."
    out = te.classify_bound(SPEC, abstract, source)
    assert out["target_endpoint_class"] == te.ENDPOINT_COMPONENT_EXCLUDED, out


def test_the_class_is_refused_by_admissibility_with_its_own_code():
    v = te._class_verdict(SPEC, te.ENDPOINT_COMPONENT_EXCLUDED, [], [], SPEC["name"])
    assert v["admissible"] is False and v["verdict"] == te.ENDPOINT_COMPONENT_EXCLUDED


# ---- meaning-preserving controls: must stay EXACT_TARGET -------------------------------------------------------------
@pytest.mark.parametrize("text", [
    "The primary composite outcome was cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. "
    "Patients with prior stroke were excluded from enrolment.",
    "The primary composite outcome was cardiovascular death, nonfatal myocardial infarction excluding silent "
    "infarction, or nonfatal stroke.",
    "The primary composite outcome was cardiovascular death, nonfatal myocardial infarction (excluding silent "
    "infarction), or nonfatal stroke.",
    "The primary outcome was 3-point MACE excluding unstable angina.",
    "The primary composite outcome of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke was "
    "assessed in patients without prior stroke.",
])
def test_controls_keep_the_target(text):
    out = te._classify(SPEC, text)
    assert out["target_endpoint_class"] == te.EXACT_TARGET, out
    assert not (set(out.get("excluded_components") or []) & {"cardiovascular death", "myocardial infarction", "stroke"})


# ---- the shared module: the verifier reads the same controls the same way --------------------------------------------
@pytest.mark.parametrize("defn", [
    "The primary composite outcome was cardiovascular death, nonfatal myocardial infarction excluding silent "
    "infarction, or nonfatal stroke.",
    "The primary composite outcome of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke was "
    "assessed in patients without prior stroke.",
])
def test_the_verifier_passes_the_same_controls(defn):
    span = defn + " The primary outcome occurred less often " + T + "."
    out = vb.span_target_mention(span, [0.87, 0.78, 0.97], defn, ["CARDIOVASCULAR_DEATH", "MYOCARDIAL_INFARCTION", "STROKE"])
    assert out["state"] == "PASS", out


# ---- found by the corpus radius: a cue that is NOT an endpoint exclusion must include what it names ------------------
@pytest.mark.parametrize("text,must", [
    # population in the cue's own clause (37952131, served in three topics)
    ("In patients with preexisting cardiovascular disease and overweight or obesity but without diabetes, semaglutide "
     "reduced death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke.",
     {"cardiovascular death", "myocardial infarction", "stroke"}),
    # 'with or without' / 'with and without' (36673114, 30882238)
    ("Iron deficiency with or without anemia increased hospitalization for heart failure.", {"heart failure hospitalization"}),
    ("Dapagliflozin reduced HHF in patients with and without HFrEF and reduced cardiovascular death.",
     {"heart failure hospitalization", "cardiovascular death"}),
    # a short contrast cue ends at its comma (41766708)
    ("Except for statins, most patients were not receiving target doses after myocardial infarction.", {"myocardial infarction"}),
    # a non-event object (29576113)
    ("Images were read without knowledge of whether the patient had suffered a myocardial infarction.", {"myocardial infarction"}),
    # a RESULTS contrast carries its own tuple (42316327, 19717846, 20828843)
    ("Reductions in cardiovascular death (RR, 0.81; 95% CI [0.72-0.93]), but not stroke (RR, 0.86; 95% CI [0.73-1.00]; "
     "p = 0.056).", {"cardiovascular death", "stroke"}),
    ("Superior for death, MI or stroke (OR=0.83 [0.77-0.89]), without any significant difference in stroke or major "
     "bleeding (both p>0.05).", {"myocardial infarction", "stroke"}),
])
def test_a_cue_that_is_not_an_endpoint_exclusion_cuts_nothing(text, must):
    rel = te.endpoint_relations(text)
    assert must <= rel["includes"], rel
    assert not (must & rel["excludes"]), rel


def test_a_temporal_restriction_is_not_a_component_exclusion():
    # VITAL registry measure #12 (NCT01169259), found by the full rebuild: the 'excluding' scope ran into the description
    t = ("Number of Participants With a Major Cardiovascular Event, Excluding First 2 Years of Follow-up Major "
         "cardiovascular event = a composite endpoint of myocardial infarction, stroke, and death from cardiovascular "
         "causes; excluding first 2 years of follow-up")
    rel = te.endpoint_relations(t)
    assert rel["excludes"] == set() and {"myocardial infarction", "stroke", "cardiovascular death"} <= rel["includes"], rel
    assert te._classify(SPEC, t)["target_endpoint_class"] == te.EXACT_TARGET
    assert te.endpoint_relations("MACE, excluding events in the first 30 days after randomization")["excludes"] == set()
