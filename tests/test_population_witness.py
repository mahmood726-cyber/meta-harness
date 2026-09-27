"""V1.0.1 entry-population axis read from source evidence (harness/population_witness.py), for a protocol whose
structured B-prime eligibility declares its population (glp1-ra-mace-t2d: "in adults with type 2 diabetes").

Fixtures from the auditor's GLP-1 finding: ELIXA (NCT01147250) and HARMONY Outcomes (NCT02465515) were
ENTRY_POPULATION_NOT_ESTABLISHED because the registry `conditions` label reads "Acute Coronary Syndrome" and
"Diabetes Mellitus"; SELECT (NCT03574597, semaglutide in obesity WITHOUT diabetes) was left UNKNOWN instead of
excluded, because the positive match was tested before the exclusions."""
import copy
import json
import os
from pathlib import Path

import pytest

from harness import population_witness as pw, trial_family

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"
T2D = ["type 2 diabetes", "type 2 diabetic", "type 2 diabetes mellitus", "diabetes mellitus, type 2", "t2d", "t2dm"]
NONE = ["without diabetes", "no diabetes", "obesity without diabetes", "overweight or obesity but without diabetes",
        "type 1 diabetes", "gestational diabetes"]


@pytest.fixture(scope="module")
def glp1():
    cfg = trial_family.protocol_requirements(ROOT, SLUG, json.load(open(ROOT / "topics" / f"{SLUG}.json", encoding="utf-8")))
    review = json.load(open(ROOT / "docs" / "reviews" / SLUG / "review.json", encoding="utf-8"))
    return cfg, {f["family_id"]: f for f in review["trial_families"]}


def _screen(fam, cfg):
    g = copy.deepcopy(fam)
    return trial_family.screen_family(g, cfg), g.get("population_decision")


def test_protocol_declares_the_population_so_the_evidence_route_applies(glp1):
    cfg, _ = glp1
    assert cfg["family_requirements"]["population"] == "type 2 diabetes"


@pytest.mark.parametrize("nct,acronym", [("NCT01147250", "ELIXA"), ("NCT02465515", "HARMONY Outcomes")])
def test_ELIXA_and_HARMONY_are_T2D_established_on_criteria_AND_primary_report(glp1, nct, acronym):
    cfg, fams = glp1
    elig, pop = _screen(fams[nct], cfg)
    assert pop["state"] == "ESTABLISHED", acronym
    by = {w["source"].split(" (")[0]: w for w in pop["witnesses"]}
    assert by["registry eligibility criteria"]["verdict"] == "ESTABLISHED"
    assert by["primary report abstract"]["verdict"] == "ESTABLISHED"
    assert "type 2 diabetes" in by["primary report abstract"]["quote"]
    assert elig["state"] == "ELIGIBLE"                       # population passage is one axis: the others passed too


def test_HARMONY_population_is_read_from_its_held_abstract(glp1):
    cfg, fams = glp1
    _, pop = _screen(fams["NCT02465515"], cfg)
    w = next(w for w in pop["witnesses"] if w["source"].startswith("primary report"))
    assert w["report_id"] == "30291013" and w["quote"].startswith("We randomly assigned patients aged 40 years and older with type 2 diabetes")


def test_SELECT_is_EXCLUDED_on_population_by_both_witnesses(glp1):
    cfg, fams = glp1
    elig, pop = _screen(fams["NCT03574597"], cfg)
    assert pop["state"] == "EXCLUDED" and elig["state"] == "INELIGIBLE" and elig["span"]["axis"] == "population"
    by = {w["source"].split(" (")[0]: w for w in pop["witnesses"]}
    assert by["registry eligibility criteria"]["section"] == "exclusion"
    assert by["registry eligibility criteria"]["quote"].startswith("History of type 1 or type 2 diabetes")
    assert "no history of diabetes" in by["primary report abstract"]["why"]


def test_PLANT_a_population_exclusion_is_decided_before_a_design_axis_abstains(glp1):
    cfg, fams = glp1
    fam = copy.deepcopy(fams["NCT03574597"])
    fam["registry_design"] = dict(fam.get("registry_design") or {}, intervention_model="CROSSOVER")   # would abstain
    elig, _ = _screen(fam, cfg)
    assert elig["state"] == "INELIGIBLE"


def test_PLANT_the_conditions_label_never_outvotes_an_entry_exclusion(glp1):
    cfg, fams = glp1
    fam = copy.deepcopy(fams["NCT03574597"])
    fam["population"]["conditions"]["value"] = ["Diabetes Mellitus, Type 2"]         # a label that says T2D
    _, pop = _screen(fam, cfg)
    assert pop["state"] == "CONFLICT" or pop["state"] == "EXCLUDED"
    assert pop["state"] != "ESTABLISHED"


def test_PLANT_conditions_fill_silence_only_and_are_marked_weak(glp1):
    cfg, fams = glp1
    fam = copy.deepcopy(fams["NCT02465515"])
    fam["population"]["criteria"]["value"] = "Inclusion Criteria:~* Age 40 or older~Exclusion Criteria:~* Pregnancy"
    fam["source_records"] = []
    _, pop = _screen(fam, cfg)
    assert pop["state"] == "NOT_ESTABLISHED"                        # 'Diabetes Mellitus' is not 'type 2 diabetes'
    fam["population"]["conditions"]["value"] = ["Diabetes Mellitus, Type 2"]
    _, pop = _screen(fam, cfg)
    assert pop["state"] == "ESTABLISHED"
    assert [w.get("strength") for w in pop["witnesses"] if w["verdict"] == "ESTABLISHED"] == ["WEAK"]


@pytest.mark.parametrize("text,expect", [
    ("Inclusion Criteria:~* Diagnosis of type 2 diabetes.~Exclusion Criteria:~* Type 1 diabetes", "ESTABLISHED"),
    # an inline header and ' - ' bullets inside one registry line (LEADER's layout)
    ("Inclusion Criteria:~Type 2 diabetes - Age min. 50 years - HbA1c: 7.0% or above Exclusion Criteria: - Type 1 diabetes",
     "ESTABLISHED"),
    ("Inclusion Criteria:~* BMI >= 27~Exclusion Criteria:~* History of type 1 or type 2 diabetes", "EXCLUDED"),
    ("Inclusion Criteria:~* Dysglycemia requiring intervention (except type 1 or 2 diabetes)~Exclusion Criteria:~* x",
     "EXCLUDED"),
    ("Inclusion Criteria:~* Adults with no history of diabetes~Exclusion Criteria:~* x", "EXCLUDED"),
    ("Inclusion Criteria:~* Obesity~Exclusion Criteria:~* Diabetes mellitus", "EXCLUDED"),
    # NOT exclusions of the population
    ("Inclusion Criteria:~* Obesity~Exclusion Criteria:~* Any clinically significant disease other than type 2 diabetes",
     "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* Obesity~Exclusion Criteria:~* Type 1 diabetes, special types of diabetes, or gestational diabetes",
     "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* Obesity~Exclusion Criteria:~* Uncontrolled type 2 diabetes (HbA1c > 10%)", "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* Other than diabetes, subjects must be in good general health~Exclusion Criteria:~* x",
     "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* A1c 5.5-9.0% if on oral anti-diabetic medications, 6.0-10.0% if not on oral anti-diabetic "
     "medications~Exclusion Criteria:~* x", "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* Treated with/without metformin as only diabetes therapy apart from insulin~Exclusion Criteria:~* x",
     "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* No ocular treatment for diabetic retinopathy six months prior~Exclusion Criteria:~* x",
     "NOT_ESTABLISHED"),
    ("Inclusion Criteria:~* Type 1 or type 2 diabetes~Exclusion Criteria:~* x", "MIXED"),
    ("Inclusion Criteria:~* Men or women with diabetes mellitus Type 2~Exclusion Criteria:~* x", "ESTABLISHED"),
])
def test_PLANT_criteria_reader(text, expect):
    assert pw.criteria_witness(text, None, T2D, NONE, diabetes=True)["verdict"] == expect


def test_PLANT_diabetes_rules_do_not_apply_to_a_population_that_is_not_diabetes():
    # a topic whose population is obesity WITHOUT diabetes must not read 'no history of diabetes' as an exclusion
    txt = "Inclusion Criteria:~* Obesity with no history of diabetes~Exclusion Criteria:~* Diabetes mellitus"
    assert pw.criteria_witness(txt, None, ["obesity"], ["type 2 diabetes"], diabetes=False)["verdict"] == "ESTABLISHED"


def test_PLANT_topics_without_a_declared_population_keep_the_legacy_screen():
    cfg = json.load(open(ROOT / "topics" / "semaglutide-obesity-weight.json", encoding="utf-8"))
    cfg = trial_family.protocol_requirements(ROOT, "semaglutide-obesity-weight", cfg)
    assert not (cfg.get("family_requirements") or {}).get("population")
    fam = json.load(open(ROOT / "docs" / "reviews" / "semaglutide-obesity-weight" / "review.json", encoding="utf-8"))["trial_families"][0]
    g = copy.deepcopy(fam)
    trial_family.screen_family(g, cfg)
    assert "population_decision" not in g


def test_the_84_unresolved_on_the_live_release_resolve_on_population(glp1):
    """n of 84: population established 83, excluded 1 (SELECT); none left unresolved on population. The 81 that stay
    UNKNOWN stay so on a DESIGN axis (parallel / contrast / blinding), which this change does not touch."""
    cfg, fams = glp1
    live = json.load(open(ROOT / "evidence" / "v101_population" / "LIVE_UNRESOLVED_84.json", encoding="utf-8"))
    assert len(live["families"]) == 84
    pops, eligs = {}, {}
    for nct in live["families"]:
        elig, pop = _screen(fams[nct], cfg)
        pops[nct], eligs[nct] = pop["state"], elig
    assert sorted(set(pops.values())) == ["ESTABLISHED", "EXCLUDED"]
    assert [k for k, v in pops.items() if v == "EXCLUDED"] == ["NCT03574597"]
    still = {k: e.get("absence_code") for k, e in eligs.items() if e["state"] == "UNKNOWN"}
    assert len(still) == 81 and set(still.values()) == {"PARALLEL_DESIGN_NOT_PROVEN", "INTERVENTION_CONTRAST_NOT_PROVEN",
                                                         "BLINDING_NOT_PROVEN"}
