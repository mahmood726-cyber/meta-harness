"""MATCHED PLACEBO + crossover design in the arm contrast (empagliflozin-HFpEF review, 2026-09-27).

SAK-HFpEF (NCT05138575): A empagliflozin + KCl, B empagliflozin + KNO3, C KCl + "Placebo for Empagliflozin". It was
excluded X-CONTRAST ("empagliflozin appears in every arm") because a substring test read C as exposed. C is a placebo
MATCHED to empagliflozin; A vs C is the empagliflozin-vs-placebo contrast with KCl constant. It is a CROSSOVER: the design
rides on the contrast (within-person), never parallel arms. Served state is read at the pinned candidate 3876a62d; the
pre-fix screening code is read at 887fea85 (a missing commit fails, never skips)."""
import importlib.util
import json
import os
import subprocess
import sys
import types

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from harness import arm_object, arm_parse, screen   # noqa: E402

PINNED = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
PRE_FIX = "887fea85"
SAK = ["Empagliflozin + Potassium Chloride", "Empagliflozin + Potassium Nitrate", "Potassium Chloride + Placebo for Empagliflozin"]
EMPA = ["empagliflozin", "Jardiance"]


def _show(ref, path):
    p = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT, capture_output=True)
    if p.returncode != 0:
        pytest.fail(f"{ref[:8]}:{path} not in history (never a skip)", pytrace=False)
    return p.stdout.decode("utf-8")


def _sak_record():
    d = json.loads(_show(PINNED, "cache/empagliflozin-hfpef-hosp/records.json"))
    return next(r for r in d["ctgov"] if r["id"] == "NCT05138575")


def _topic(slug):
    return json.load(open(os.path.join(ROOT, "topics", f"{slug}.json"), encoding="utf-8"))


def _pre_fix_screen():
    """harness/screen.py exactly as it was before this fix, imported inside the harness package."""
    spec = importlib.util.spec_from_loader("harness._screen_pre_fix", loader=None)
    mod = types.ModuleType(spec.name)
    mod.__package__ = "harness"
    exec(compile(_show(PRE_FIX, "harness/screen.py"), "screen@887fea85", "exec"), mod.__dict__)
    return mod


# ------------------------------------------------------------------ plants (the defect, on the served state and the pre-fix code)
def test_plant_served_sak_is_excluded_because_a_matched_placebo_arm_read_as_empagliflozin():
    rv = _show(PINNED, "docs/reviews/empagliflozin-hfpef-hosp/review.json")
    d = next(x for x in json.loads(rv)["screening"]["records"] if "NCT05138575" in str(x.get("id")))
    assert d["rule_id"] == "X-CONTRAST" and "Placebo for Empagliflozin" in d["reason"]


def test_plant_the_pre_fix_fallback_calls_sak_background_and_the_fixed_one_does_not():
    rec = _sak_record()
    assert _pre_fix_screen()._record_arm_interventions_background_only(rec, EMPA)[0] is True       # the defect
    assert screen._record_arm_interventions_background_only(rec, EMPA) == (False, "")


def test_plant_the_arm_object_gave_the_placebo_arm_empagliflozin_as_its_drug():
    assert arm_object._drug_of(SAK[2]) == "empagliflozin"          # the raw substring still finds the word ...
    arm = arm_object._arm(SAK[2])
    assert arm["drug"]["value"] == "placebo" and arm["matched_placebo_for"]["value"] == "empagliflozin"   # ... it is not exposure


# ------------------------------------------------------------------ the parse
@pytest.mark.parametrize("label,state", [
    (SAK[0], "ACTIVE"), (SAK[1], "ACTIVE"), (SAK[2], "MATCHED_PLACEBO"),
    ("Empagliflozin-matching placebo", "MATCHED_PLACEBO"), ("Matching placebo for empagliflozin", "MATCHED_PLACEBO"),
    ("Placebo (empagliflozin)", "MATCHED_PLACEBO"), ("Placebo to match empagliflozin 10 mg", "MATCHED_PLACEBO"),
    ("Empagliflozin placebo", "MATCHED_PLACEBO"), ("Placebo", "ABSENT"), ("Potassium Chloride", "ABSENT"),
    ("Empagliflozin/empagliflozin placebo", "VARIES_WITHIN_ARM"), ("Empagliflozin 10 mg oral tablet", "ACTIVE"),
])
def test_placebo_for_x_is_placebo_matched_to_x_never_exposure_to_x(label, state):
    assert arm_parse.exposure(arm_parse.parse_arm(label), EMPA) == state


def test_a_vs_c_is_the_clean_empagliflozin_vs_placebo_contrast_with_kcl_constant_and_b_vs_c_is_not():
    design = arm_parse.design_object(json.loads(_show(PINNED, "cache/empagliflozin-hfpef-hosp/registry_designs.json"))["NCT05138575"])
    cs = {(c["experimental_arm"], c["comparator_arm"]): c for c in arm_parse.ordered_contrasts(SAK, EMPA, design)}
    ac = cs[(SAK[0], SAK[2])]
    assert ac["state"] == "CLEAN" and ac["comparator"] == "matched placebo" and ac["held_constant"] == ["potassium chloride"]
    bc = cs[(SAK[1], SAK[2])]
    assert bc["state"] == "CONFOUNDED" and bc["differs_also"] == ["potassium chloride", "potassium nitrate"]
    assert len(cs) == 2                      # A vs B is not a contrast for empagliflozin: both arms are exposed


def test_the_crossover_design_rides_on_the_contrast_and_only_held_facts_are_filled():
    rec = _sak_record()
    obj = arm_object.build(rec, dict(_topic("empagliflozin-hfpef-hosp"), slug="empagliflozin-hfpef-hosp"))
    d = obj["ordered_contrasts"][0]["design"]
    assert d["design"] == "CROSSOVER" and d["within_person"] is True and d["source"] == "registry intervention_model"
    assert "never independent parallel arms" in d["analysis_requirement"]
    # periods (3), 6-week periods, ~2-week washouts are the reviewer's reading of the protocol; the held bytes do not carry
    # them, so they are NOT asserted -- never filled from memory
    assert (d["periods"], d["period_length"], d["washout"], d["carryover"]) == (arm_parse.NOT_IN_HELD_BYTES,) * 4
    assert arm_parse.design_object({"intervention_model": "PARALLEL"})["within_person"] is False
    assert arm_parse.design_object(None)["design"] == arm_parse.NOT_IN_HELD_BYTES


# ------------------------------------------------------------------ the rule's other cases, and what must NOT change
@pytest.mark.parametrize("arms,kws,every", [
    (["placebo Circadin", "Circadin"], ["melatonin", "circadin"], False),                                # Neu I: matched placebo
    (["Vitamin D3 + fish oil/fish oil placebo", "Vitamin D3 placebo + fish oil/fish oil placebo"], ["fish oil"], False),  # VITAL-Echo
    (["Colchicine 0.5 mg", "Colchicine 0.25 mg", "Placebo"], ["colchicine"], False),                     # DRC-04: a placebo ARM
    (["Balcinrenone 15 mg + Dapagliflozin 10 mg", "Placebo + Dapagliflozin 10 mg"], ["dapagliflozin"], True),  # MIRO-CKD stays background
    (["Dabigatran Etexilate Oral Capsule", "Rivaroxaban Oral Tablet"], ["dabigatran", "rivaroxaban"], True),  # DOAC vs DOAC stays
])
def test_every_arm_means_every_arm_actively_exposed(arms, kws, every):
    assert arm_parse.interest_in_every_arm(arms, kws) is every


def test_corpus_n_of_n_matches_the_recorded_measurement():
    sys.path.insert(0, os.path.join(ROOT, "evidence", "matched_placebo"))
    import measure
    m = measure.measure(PINNED)
    assert (m["x_contrast_exclusions"], m["by_arm_list_fallback"], m["no_longer_every_arm"]) == (15, 7, 6)
    assert {k: v["n"] for k, v in m["by_cause"].items()} == {"MATCHED_PLACEBO": 2, "VARIES_WITHIN_ARM": 1, "ABSENT": 3}
    stored = json.load(open(os.path.join(ROOT, "evidence", "matched_placebo", "measure_3876a62d.json"), encoding="utf-8"))
    assert stored["by_cause"] == m["by_cause"]


# ------------------------------------------------------------------ arm-parse corpus fixture findings (Codex reading vs parser)
@pytest.mark.parametrize("label,kws,state", [
    ("sacubitril/valsartan (LCZ696) matching placebo", ["sacubitril/valsartan", "lcz696"], "MATCHED_PLACEBO"),   # NCT02554890
    ("Semaglutide 1.34 mg/ml placebo", ["semaglutide"], "MATCHED_PLACEBO"),                                   # NCT05078255
    ("Balcinrenone/dapagliflozin 15 mg/10 mg and matching placebo for dapagliflozin 10 mg", ["dapagliflozin"], "ACTIVE"),  # MIRO
    ("Balcinrenone/dapagliflozin 40 mg/10 mg and matching placebo for dapagliflozin 10 mg", ["dapagliflozin"], "ACTIVE"),
    ("Vitamin D3 + fish oil/fish oil placebo", ["fish oil"], "VARIES_WITHIN_ARM"),                             # the one real level split
])
def test_a_slash_is_a_level_split_only_in_the_x_slash_x_placebo_form_and_a_double_dummy_arm_is_exposed(label, kws, state):
    """Plants from the arm-parse corpus fixture: a fixed combination, a dose and a unit were read as two levels, and a
    double-dummy arm (active fixed combination + matching placebo for one ingredient) was read as varying, not exposed."""
    assert arm_parse.exposure(arm_parse.parse_arm(label), kws) == state
