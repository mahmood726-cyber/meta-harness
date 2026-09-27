"""ONE component-by-component rule, applied identically to admitted and refused rows, decided from definitions only (external
review of colchicine-secondary-cv-prevention, 2026-09-26). Served rows at the pinned candidate 3876a62d (a missing commit fails)."""
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import composite_rule as cr, outcome_tiers as ot   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
SLUG = "colchicine-secondary-cv-prevention"


def _git_json(path):
    p = subprocess.run(["git", "show", f"{PINNED}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{PINNED[:8]}:{path} not in history (never a skip)", pytrace=False)
    return json.loads(p.stdout)


def _state(slug=SLUG):
    o = next(x for x in _git_json(f"docs/reviews/{slug}/review.json")["outcomes"] if x.get("primary"))
    spec = _git_json(f"topics/{slug}.json").get("primary_outcome") or {}
    recs = {str(r["id"]): r.get("abstract", "") for r in _git_json(f"cache/{slug}/records.json")["records"]}
    return o, spec, recs, _git_json("docs/refusals.json").get(slug)


def test_plant_the_served_state_refuses_cops_as_broader_while_admitting_broader_composites():
    o, spec, recs, reg = _state()
    assert "broader composite" in next(r for r in reg if "32862667" in r["trial"])["not_pooled_because"]
    assert {t["id"] for t in o["trials"]} == {"PMID 31733140", "PMID 32865380", "PMID 39555823"}   # COLCOT, LoDoCo2, CLEAR admitted
    cc = ot.composite_compatibility(o, o["trials"], spec, recs, reg)
    by = {r["id"]: r for r in cc["rows"]}
    for pid in ("PMID 31733140", "PMID 32865380", "PMID 39555823"):
        assert by[pid]["state"] == "SEPARATE_ANALYSIS" and any(d.startswith("ADDED:") for d in by[pid]["differences"])
    assert by["PMID 32862667"]["state"] == "SEPARATE_ANALYSIS"
    assert cc["refusals_judged_like_an_admitted_row"] == ["PMID 32862667"]      # the inconsistency is reported, not hidden
    assert sorted(cc["admission_changes"]) == ["PMID 31733140", "PMID 32865380", "PMID 39555823"]


def test_one_rule_either_flags_all_broader_composites_or_admits_cops():
    o, spec, recs, reg = _state()
    rows = {r["id"]: r for r in ot.composite_compatibility(o, o["trials"], spec, recs, reg)["rows"] if r["state"] != "NO_DEFINITION"}
    permissive = {"composite_component_policy": {"core": ["CV_DEATH", "MI", "STROKE"], "predeclared": True, "decided_by": "t",
                  "decided_on": "d", "rationale": "r", "allowed_in_primary": sorted({d for r in rows.values() for d in r["differences"]})}}
    cc = ot.composite_compatibility(o, o["trials"], permissive["composite_component_policy"] and {**spec, **permissive}, recs, reg)
    states = {r["id"]: r["state"] for r in cc["rows"] if r["state"] != "NO_DEFINITION"}
    assert set(states.values()) == {"PRIMARY"}                                    # allow what COPS has -> COPS is admitted too
    assert "PMID 32862667" in [r["id"] for r in cc["rows"] if r["admission_changes"]]


def test_substitution_is_a_different_difference_from_addition():
    cops = "The primary outcome was a composite of all-cause mortality, ACS, ischemia-driven (unplanned) urgent revascularization, and noncardioembolic ischemic stroke"
    d = cr.verdict(cops, {}, cr.DEFAULT_CORE)["differences"]
    assert d == ["SUBSTITUTED:ACS_FOR_MI", "SUBSTITUTED:ALL_CAUSE_DEATH_FOR_CV_DEATH", "ADDED:CORONARY_REVASC"]
    only_additions = {"composite_component_policy": {"core": ["CV_DEATH", "MI", "STROKE"], "allowed_in_primary": ["ADDED:CORONARY_REVASC"],
                                                     "predeclared": True, "decided_by": "t", "decided_on": "d", "rationale": "r"}}
    assert cr.verdict(cops, only_additions)["blocking"] == ["SUBSTITUTED:ACS_FOR_MI", "SUBSTITUTED:ALL_CAUSE_DEATH_FOR_CV_DEATH"]


@pytest.mark.parametrize("slug", ["glp1-ra-mace-t2d", "dpp4-mace-t2d", "omega3-cardiovascular-events", "pcsk9-mace", "ticagrelor-vs-clopidogrel-acs"])
def test_the_uniform_rule_agrees_with_every_other_composite_gate(slug):
    o, spec, recs, reg = _state(slug)
    cc = ot.composite_compatibility(o, o["trials"], spec, recs, reg)
    assert cc is not None and cc["admission_changes"] == [], cc["admission_changes"]


@pytest.mark.parametrize("text,expected", [
    ("CV death, nonfatal myocardial infarction, or nonfatal stroke", ["CV_DEATH", "MI", "STROKE"]),
    ("non-fatal myocardial infarction, stroke, or death from cardiovascular disease", ["CV_DEATH", "MI", "STROKE"]),
    ("myocardial infarction, stroke or death from vascular causes", ["CV_DEATH", "MI", "STROKE"]),
    ("death from coronary heart disease, nonfatal myocardial infarction, stroke, or unstable angina", ["CV_DEATH", "MI", "STROKE", "UA_HOSP"]),
    ("death from cardiovascular causes, resuscitated cardiac arrest, myocardial infarction, stroke, or urgent hospitalization for angina leading to coronary revascularization",
     ["CARDIAC_ARREST", "CV_DEATH", "MI", "STROKE", "UA_HOSP_REVASC"]),
])
def test_vocabulary_reads_the_served_wordings(text, expected):
    assert cr.components(text) == expected


def test_no_declared_core_means_not_judged_and_an_hf_outcome_is_never_measured_against_mace():
    assert ot.core_for({}, {"name": "Heart-failure hospitalisation or cardiovascular death"}) is None
    assert ot.core_for({}, {"name": "3-point major adverse cardiovascular events"}) == cr.DEFAULT_CORE
