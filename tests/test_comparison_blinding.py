"""Held-source comparisons, including the c15ed111 XXB750 registry plant."""
import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import comparison_blinding as cb, screen

PIN = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
BASE = "c15ed11156de6be09fe516cdf348aa247b07ea13"


def held(path, ref=PIN):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT).decode("utf-8")


@pytest.fixture(scope="module")
def source():
    data = json.loads(held("cache/sacubitril-valsartan-hfref/records.json"))
    rec = next(r for r in data["records"] if r["id"] == "41912806")
    config = json.loads(held("topics/sacubitril-valsartan-hfref.json"))
    return data, rec, config


def baseline():
    mod = types.ModuleType("harness._blinding_baseline")
    mod.__package__ = "harness"
    exec(compile(held("harness/screen.py", BASE), "screen@c15ed111", "exec"), mod.__dict__)
    return mod


def plant(rec):
    # A labelled metamorphic plant, NOT a claimed held registry record. The
    # identity and complete abstract come from held PMID 41912806.
    return dict(rec, id=rec["nct"], id_type="nct", allocation="RANDOMIZED",
                study_type="INTERVENTIONAL", masking="DOUBLE",
                interventions=["XXB750", "Placebo", "Sacubitril/valsartan"])


def test_registry_plant_was_include_and_now_names_the_open_comparison(source):
    _, rec, config = source
    assert rec["nct"] == "NCT06142383" and rec["nct"] in rec["abstract"]
    r = plant(rec)
    assert baseline().screen_record(r, config["include"], set())[:2] == ("include", "INCLUDE")
    d = screen.screen_record(r, config["include"], set())
    assert d[:2] == ("exclude", "X-DESIGN")
    assert "OPEN_LABEL" in d[2] and "sacubitril/valsartan" in d[2] and "placebo" in d[2]
    assert "angiotensin-converting enzyme inhibitor" in d[2]
    assert d[3] in rec["abstract"]
    assert screen.screen_record_2(r, config["include"]) == "exclude"


def test_abstract_groups_preserve_both_background_strata(source):
    _, rec, config = source
    text = rec["abstract"]
    reading = cb.read_blinding(text)
    assert reading["state"] == cb.MIXED
    assert [g["blinding"] for g in reading["groups"]] == [cb.BLINDED, cb.OPEN_LABEL, cb.BLINDED]
    assert len(reading["groups"][0]["arms"]) == 3
    assert reading["groups"][2]["background"] == "sacubitril/valsartan"
    assert cb.comparison_blinding(text, "sacubitril/valsartan", "placebo") == cb.OPEN_LABEL
    assert cb.comparison_blinding(text, "XXB750", "placebo", background="sacubitril/valsartan") == cb.BLINDED
    pairs = cb.eligible_comparisons(text, config["include"]["intervention_any"], config["include"]["comparator_any"])
    assert len(pairs) == 1 and pairs[0]["blinding"] == cb.OPEN_LABEL
    # The served abstract remains excluded at its earlier title gate.
    assert screen.screen_record(rec, config["include"], set())[:2] == ("exclude", "X3")
    served = json.loads(held("docs/reviews/sacubitril-valsartan-hfref/review.json"))
    assert next(r for r in served["screening"]["records"] if r["id"] == "41912806")["rule_id"] == "X3"


@pytest.mark.parametrize("nct", ["NCT01035255", "NCT02554890"])
def test_held_paradigm_and_pioneer_registry_unchanged(source, nct):
    data, _, config = source
    rec = next(r for r in data["ctgov"] if r["id"] == nct)
    old = baseline().screen_record(rec, config["include"], set())
    assert old[:2] == ("include", "INCLUDE")
    assert screen.screen_record(rec, config["include"], set()) == old


@pytest.mark.parametrize("word,state", [("blinded", cb.BLINDED), ("double-blind", cb.BLINDED),
                                       ("open-label", cb.OPEN_LABEL), ("unblinded", cb.OPEN_LABEL)])
def test_explicit_modes_and_unknown_pair_fail_closed(word, state):
    text = f"Patients were randomized to receive Alpha or placebo in a {word} fashion."
    assert cb.comparison_blinding(text, "Alpha", "placebo") == state
    assert cb.read_blinding(text)["groups"][0]["blinding"] == state
    assert cb.comparison_blinding("Patients received Alpha or placebo.", "Alpha", "placebo") == cb.NOT_STATED


def test_uniform_all_arms_blinding_unchanged(source):
    _, rec, config = source
    r = dict(plant(rec), abstract="Patients were randomized to receive sacubitril/valsartan or enalapril in a double-blind fashion.")
    assert screen.screen_record(r, config["include"], set()) == baseline().screen_record(r, config["include"], set())


def test_mixed_unresolved_cannot_borrow_registry_masking(source):
    _, rec, config = source
    r = dict(plant(rec), abstract="Patients received sacubitril/valsartan or enalapril. Some comparisons were double-blind; others were open-label.")
    assert cb.comparison_blinding(r["abstract"], "sacubitril/valsartan", "enalapril") == cb.MIXED
    d = screen.screen_record(r, config["include"], set())
    assert d[:2] == ("exclude", "X-DESIGN") and "cannot be established" in d[2]


def test_background_stratum_cannot_become_interest_contrast(source):
    _, rec, config = source
    sentence = next(g["span"] for g in cb.read_blinding(rec["abstract"])["groups"]
                    if g["background"] == "sacubitril/valsartan")
    r = dict(plant(rec), abstract=sentence,
             interventions=["XXB750 + sacubitril/valsartan", "Placebo + sacubitril/valsartan", "ACE inhibitor"])
    assert cb.eligible_comparisons(sentence, ["sacubitril"], ["placebo"]) == []
    assert screen.screen_record(r, config["include"], set())[:2] == ("exclude", "X-CONTRAST")


def test_blinded_comparison_is_not_vetoed_by_another_open_arm():
    text = "Patients were randomized to receive Alpha or placebo in a blinded fashion or Beta in an open-label fashion."
    r = dict(id="trial", id_type="nct", allocation="RANDOMIZED", title="Trial", abstract=text, masking="NONE")
    inc = dict(intervention_any=["Alpha"], comparator_any=["placebo"], design_double_blind=True)
    assert screen.screen_record(r, inc, set())[:2] == ("include", "INCLUDE")
    inc["intervention_any"] = ["Beta"]
    assert screen.screen_record(r, inc, set())[:2] == ("exclude", "X-DESIGN")


def test_cross_stratum_pair_is_not_a_randomized_comparison():
    text = ("Patients on background First treatment were randomized to receive Alpha or placebo in a blinded fashion. "
            "Patients on background Second treatment were randomized to receive Beta or Gamma in an open-label fashion.")
    assert cb.comparison_blinding(text, "Alpha", "Gamma") == cb.MIXED


def test_prefix_fashion_keeps_dabigatran_warfarin_open():
    data = json.loads(held("cache/noac-vs-warfarin-af-stroke/records.json"))
    rec = next(r for r in data["records"] if r["id"] == "19717844")
    assert cb.comparison_blinding(rec["abstract"], "dabigatran", "warfarin") == cb.OPEN_LABEL


def test_endpoint_blinding_does_not_blind_the_open_treatment():
    text = "Patients were randomized to receive Alpha or placebo in an open-label fashion. Endpoint adjudication was blinded."
    assert cb.comparison_blinding(text, "Alpha", "placebo") == cb.OPEN_LABEL


# Held shapes the bounded grammar does not read. The record-shaped branches that once "resolved" these were written against the
# same records the census reads (in-sample), and were removed: an unread comparison must FAIL CLOSED, never borrow a state.
# The hand readings of these records stay in evidence/comparison_blinding/README.md as readings, not as parser validation.
@pytest.mark.parametrize("slug,rid,experimental,control", [
    ("doac-vte-recurrence", "20886185", "TAK-442", "enoxaparin"),
    ("probiotics-aad-prevention", "30439760", "probiotic yogurt", "no yogurt"),
    ("probiotics-aad-prevention", "35418412", "L. reuteri", "placebo"),
])
def test_unread_held_shapes_fail_closed(slug, rid, experimental, control):
    data = json.loads(held(f"cache/{slug}/records.json"))
    rec = next(r for r in data["records"] if r["id"] == rid)
    assert cb.comparison_blinding(rec["abstract"], experimental, control) != cb.BLINDED


def test_matched_placebo_is_an_eligible_blinded_comparator():
    text = "Patients were randomized to receive Alpha or placebo for Alpha in a blinded fashion or Beta in an open-label fashion."
    pairs = cb.eligible_comparisons(text, ["Alpha"], ["placebo"])
    assert len(pairs) == 1 and pairs[0]["blinding"] == cb.BLINDED


def test_rerandomization_does_not_turn_earlier_interest_into_blinded_contrast():
    data = json.loads(held("cache/semaglutide-obesity-weight/records.json"))
    rec = next(r for r in data["records"] if r["id"] == "42473259")
    text = rec["abstract"]
    assert cb.comparison_blinding(text, "dapagliflozin", "placebo", background="semaglutide") == cb.BLINDED
    assert cb.eligible_comparisons(text, ["semaglutide"], ["placebo"]) == []
    pairs = cb.eligible_comparisons(text, ["semaglutide"], ["insulin"])
    assert len(pairs) == 1 and pairs[0]["blinding"] == cb.OPEN_LABEL


def test_census_denominator_and_named_records():
    m = json.loads((ROOT / "evidence/comparison_blinding/measurement.json").read_text(encoding="utf-8"))
    assert m["pin"] == PIN and m["topic_count"] == 38
    assert m["total"] == sum(sum(n.values()) for n in m["counts"].values()) == 4080
    assert any(r["id"] == "41912806" for r in m["candidates"])


def test_a_cue_about_other_studies_is_not_this_records_blinding():
    # review correction (2026-09-28): replaces a record-shaped branch. Written after reading melatonin 22346363 (in-sample
    # there); it changes 2 of 4,080 readings corpus-wide, both named here.
    mel = ("Post hoc analysis of pooled subpopulations from four randomized, double-blind trials of PRM and placebo. "
           "Safety measures included subpopulations from these four and three additional single-blind and open-label PRM studies.")
    assert cb.read_blinding(mel)["state"] == cb.BLINDED
    zinc = "Between then and 2004, 10 other double-blind, placebo-controlled clinical trials showed widely varying results."
    assert cb.read_blinding(zinc)["state"] == cb.NOT_STATED
    own = "Patients were randomized to receive Alpha or placebo in an open-label fashion."
    assert cb.read_blinding(own)["state"] == cb.OPEN_LABEL
