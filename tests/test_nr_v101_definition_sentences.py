"""Endpoint definitions bind only to DEFINITION-BEARING sentences (methods / outcome definitions), never to background or
introduction text (lane NR, V1.0.1; PCSK9 review, hash f7132bc2...).

VESALIUS-CV (PMID 41211925): HR 0.75 (0.65-0.86) was refused RESULT_INCOMPATIBLE 'no CV death' because its bound
'definition' was the BACKGROUND sentence ('The effect of evolocumab on the risk of MACE among patients without a previous
myocardial infarction or stroke is unknown') -- a population qualifier read as components. The METHODS sentence defines
both co-primaries: 3-point MACE (CHD death, MI, ischemic stroke) -> 0.75; 4-point MACE (+ ischemia-driven arterial
revascularization) -> 0.81. CHD death vs CV death and ischemic vs all stroke are VISIBLE compatibility judgments (the
2026-09-16 amendment permits them), not silent equalities."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness import target_endpoint as te

ROOT = Path(__file__).resolve().parents[1]
RECS = json.loads((ROOT / "cache/pcsk9-mace/records.json").read_text(encoding="utf-8"))
VESALIUS = next(r for r in RECS["records"] if str(r.get("id")) == "41211925")["abstract"]
SPEC = json.loads((ROOT / "topics/pcsk9-mace.json").read_text(encoding="utf-8"))["primary_outcome"]
BACKGROUND = ("The effect of evolocumab on the risk of MACE among patients without a previous myocardial infarction or stroke "
              "is unknown.")
R3 = ("A 3-point MACE event occurred in 336 patients (5-year Kaplan-Meier estimate, 6.2%) in the evolocumab group, as "
      "compared with 443 (8.0%) in the placebo group (hazard ratio, 0.75; 95% confidence interval [CI], 0.65 to 0.86; "
      "P<0.001).")
R4 = ("A 4-point MACE event occurred in 747 patients (5-year Kaplan-Meier estimate, 13.4%) in the evolocumab group, as "
      "compared with 907 (16.2%) in the placebo group (hazard ratio, 0.81; 95% CI, 0.73 to 0.89; P<0.001).")


def _bound(rs):
    b = te.bind_result_span(VESALIUS, rs)
    return b, te._classify(SPEC, b["endpoint_definition_span"], components=b["components"],
                           excluded=b.get("excluded_components"), result_span=rs)


def test_a_background_sentence_fails_the_definition_check():
    assert te._definition_sentences(BACKGROUND + " " + BACKGROUND) == []
    assert BACKGROUND not in {d["span"] for d in te._definition_sentences(VESALIUS)}


def test_vesalius_binds_its_3_point_result_to_the_methods_definition():
    b, c = _bound(R3)
    assert b["endpoint_definition_span"].startswith("composite of death from coronary heart disease")
    assert "3-point MACE" in b["endpoint_definition_span"] and "4-point" not in b["endpoint_definition_span"]
    assert c["target_endpoint_class"] == te.EXACT_TARGET


def test_the_4_point_result_binds_to_its_own_definition_and_is_a_superset():
    b, c = _bound(R4)
    assert "4-point MACE" in b["endpoint_definition_span"]
    assert c["target_endpoint_class"] == te.NEAR_MATCH and "coronary revascularization" in c["extra_components"]


def test_component_substitutions_are_visible_judgments_not_silent_equalities():
    _, c = _bound(R3)
    j = {(x["target"], x["trial"]) for x in c.get("compatibility_judgments") or []}
    assert ("cardiovascular death", "coronary heart disease death") in j
    assert ("stroke", "ischemic stroke") in j
    assert all(x.get("basis") for x in c["compatibility_judgments"])
    row = te.row_from_candidate({**c, "source": R3})
    assert row["endpoint_compatibility_judgments"] == c["compatibility_judgments"]


@pytest.mark.parametrize("sentence", [
    # definition forms the gate must keep (corpus radius, lane NR)
    "The key secondary composite outcome, also assessed in a time-to-event analysis, was death from cardiovascular causes, "
    "nonfatal myocardial infarction, nonfatal stroke, or hospitalization for heart failure.",
    "All-cause death was the primary end point, whereas cardiovascular death, myocardial infarction and stroke were "
    "secondary end points.",
    "MAIN OUTCOMES AND MEASURES A composite outcome of myocardial infarction, stroke, and cardiovascular death.",
    "Subgroup analyses of the primary MACE (a composite endpoint including cardiovascular death, nonfatal myocardial "
    "infarction or nonfatal stroke) outcome were done.",
    "The trial was designed to determine whether rivaroxaban was noninferior to warfarin for the primary end point of "
    "stroke or systemic embolism.",
])
def test_genuine_definition_forms_still_bind(sentence):
    assert te._definition_sentences(sentence), sentence


@pytest.mark.parametrize("sentence", [
    BACKGROUND,
    "CONCLUSIONS: Among patients with type 2 diabetes, the rates of major adverse cardiovascular events were not increased "
    "with saxagliptin, although hospitalization for heart failure was increased.",
    "Whether sPA is associated with major adverse cardiovascular events (MACE) prior to overt hypertension remains "
    "incompletely characterized.",
])
def test_background_and_conclusion_text_never_defines(sentence):
    assert te._definition_sentences(sentence) == []
