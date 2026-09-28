"""V1.0.1 plants from the DPP-4 review (Patoulias 2021).

(1) "Same question" requires CONTROL, ENDPOINT and EFFECT MEASURE to agree, not just class and population: Patoulias
    includes CAROLINA (vs glimepiride), pools individual outcomes, and reports RR -> related: trial-inventory map.
(2) Its trial list is explicit: the stated-k sentence cites references 10-15, each with a PMID in the held JATS.
(3) 52,520 stated vs 26,807 + 26,713 = 53,520 in its CV-mortality plot -> COMPARATOR_INTERNAL_MISMATCH (the plot is an
    image, so that side is REPORTED_NOT_HELD). Its abstract's "DPP-4 inhibitor or placebo" vs CAROLINA's glimepiride
    is a second, fully held, internal mismatch.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import comparator_models as cm, comparator_panel as cp, same_question as sq  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "dpp4-mace-t2d"


def _served():
    return json.load(open(ROOT / "docs/reviews" / SLUG / "review.json", encoding="utf-8"))


def test_patoulias_is_a_trial_inventory_map_not_the_same_question():
    s = _served()["comparator"]["scope"]
    assert s["scope_valid"] is False and s["intervention_level_match"] and s["population_match"]
    d = s["same_question"]
    assert d["label"] == "RELATED_TRIAL_INVENTORY_MAP"
    assert set(d["differs"]) == {"control", "endpoint", "effect_measure"}


_Y = {"contrast": "YES"}      # V1.0.1 (metformin review): the treatment contrast is a dimension of the same question


@pytest.mark.parametrize("agrees,label", [
    ({**_Y, "control": "YES", "endpoint": "YES", "effect_measure": "YES", "population": "YES", "intervention": "YES"}, "SAME_QUESTION"),
    ({**_Y, "control": "NO", "endpoint": "YES", "effect_measure": "YES", "population": "YES", "intervention": "YES"}, "RELATED_TRIAL_INVENTORY_MAP"),
    ({**_Y, "control": "YES", "endpoint": "YES", "effect_measure": "NO", "population": "YES", "intervention": "YES"}, "RELATED_TRIAL_INVENTORY_MAP"),
    ({**_Y, "control": "YES", "endpoint": "YES", "effect_measure": "YES", "population": "NO", "intervention": "YES"}, "RELATED_TRIAL_INVENTORY_MAP"),
    ({**_Y, "control": "NOT_ESTABLISHED", "endpoint": "NO", "effect_measure": "YES", "population": "YES", "intervention": "YES"}, "RELATED_TRIAL_INVENTORY_MAP"),
    ({**_Y, "control": "NOT_ESTABLISHED", "endpoint": "YES", "effect_measure": "YES", "population": "YES", "intervention": "YES"}, "NOT_ESTABLISHED"),
    ({"contrast": "NO", "control": "YES", "endpoint": "YES", "effect_measure": "YES", "population": "YES", "intervention": "YES"}, "RELATED_TRIAL_INVENTORY_MAP"),
    # every other dimension agreeing never makes it the same question while the contrast was not checked
    ({"control": "YES", "endpoint": "YES", "effect_measure": "YES", "population": "YES", "intervention": "YES"}, "NOT_ESTABLISHED"),
])
def test_PLANT_the_label_is_derived_from_the_dimensions(agrees, label):
    doc = {"dimensions": {k: {"agrees": v} for k, v in agrees.items()}}
    assert sq.decide(doc)["label"] == label


def test_PLANT_class_and_population_alone_never_make_the_same_question():
    scope = {"scope_valid": True, "intervention_level_match": True, "population_match": True, "note": "x"}
    out = sq.apply_to_scope(scope, sq.decide(None))
    assert out["scope_valid"] is False and out["same_question"]["label"] == "NOT_ESTABLISHED"


def test_PLANT_an_unlocated_quote_refuses_the_record(tmp_path):
    d = tmp_path / "cache" / "x"
    d.mkdir(parents=True)
    (tmp_path / "held.txt").write_text("the control was placebo", encoding="utf-8")
    dims = {k: {"agrees": "YES", "evidence": [{"document_ref": "held.txt", "quote": "the control was placebo"}]}
            for k in sq.DIMS}
    (d / "comparator_question.json").write_text(json.dumps({"dimensions": dims}), encoding="utf-8")
    assert sq.load(tmp_path, "x")
    dims["control"]["evidence"][0]["quote"] = "the control was glimepiride"
    (d / "comparator_question.json").write_text(json.dumps({"dimensions": dims}), encoding="utf-8")
    with pytest.raises(sq.QuestionRefused, match="not located"):
        sq.load(tmp_path, "x")


def test_the_trial_list_is_read_from_the_stated_k_citation():
    panel = json.load(open(ROOT / "cache" / SLUG / "comparators.json", encoding="utf-8"))[0]
    got = {(m["family_id"], m["aliases"][0]["id"]) for m in panel["trial_set"]}
    assert got == {("TECOS", "26052984"), ("CAROLINA", "31536101"), ("CARMELINA", "30418475"),
                   ("omarigliptin", "28893244"), ("SAVOR-TIMI", "23992601"), ("EXAMINE", "23992602")}
    cp.validate(panel, str(ROOT))
    ov = _served()["comparator"]["overlap_relation"]
    assert ov["relation"] == "SUBSET" and ov["theirs_k"] == 6 and ov["shared_k"] == 3


def test_PLANT_a_member_outside_the_cited_range_is_refused():
    panel = json.load(open(ROOT / "cache" / SLUG / "comparators.json", encoding="utf-8"))[0]
    bad = copy.deepcopy(panel)
    bad["trial_set"][0]["aliases"][0]["linked_rid"] = "B9"
    with pytest.raises(ValueError, match="cited range"):
        cp.validate(bad, str(ROOT))


@pytest.mark.parametrize("frag,rng", [
    ('six trials[<xref rid="B10" ref-type="bibr">10</xref>-<xref rid="B15" ref-type="bibr">15</xref>]',
     ["B10", "B11", "B12", "B13", "B14", "B15"]),
    ('trials[<xref rid="B3">3</xref>,<xref rid="B7">7</xref>]', ["B3", "B7"]),
    ("no citation here", None),
])
def test_PLANT_stated_k_range(frag, rng):
    assert cp.stated_k_range(frag) == rng


def test_both_internal_mismatches_are_kept():
    ms = {m["kind"]: m for m in _served()["comparator"]["internal_mismatches"]}
    p = ms["PARTICIPANT_COUNT_STATED_VS_FIGURE_TOTALS"]
    assert [s["state"] for s in p["sides"]] == ["HELD", "REPORTED_NOT_HELD"] and p["sides"][1]["value"] == 53520
    c = ms["STATED_CONTROL_VS_INCLUDED_TRIAL"]
    assert [s["state"] for s in c["sides"]] == ["HELD", "HELD"] and "Glimepiride" in c["sides"][1]["quote"]


# ---------------------------------------------------------------- the corpus rule (codex proposals, Claude review)
@pytest.mark.parametrize("ours,rep,agrees", [
    ("HR", [{"outcome": "x", "scale": "HR"}], "YES"),
    ("RR", [{"outcome": "x", "scale": "risk ratio"}], "YES"),
    ("RR", [{"outcome": "x", "scale": "OR"}], "NO"),          # tocilizumab: our RR vs WHO REACT's OR
    ("HR", [], "NOT_ESTABLISHED"),
    ("INCOMPATIBLE (HAZARD_RATIO_FIRST_EVENT + INCIDENCE_RATE_RATIO)", [{"outcome": "x", "scale": "OR"}], "NOT_ESTABLISHED"),
])
def test_PLANT_effect_measure_is_derived_from_served_data(ours, rep, agrees):
    assert sq.effect_measure(ours, rep, "x")["agrees"] == agrees


def test_PLANT_a_derived_unknown_never_overwrites_a_checked_value():
    doc = {"dimensions": {k: {"agrees": "YES"} for k in sq.DIMS}}
    doc["dimensions"]["effect_measure"] = {"agrees": "NO"}
    assert sq.decide(doc, {"agrees": "NOT_ESTABLISHED"})["label"] == "RELATED_TRIAL_INVENTORY_MAP"


def test_served_labels_follow_the_reviewed_records():
    def label(slug):
        return json.load(open(ROOT / "docs/reviews" / slug / "review.json", encoding="utf-8"))["comparator"]["scope"]["same_question"]["label"]
    assert label("finerenone-ckd-t2d-renal") == "SAME_QUESTION"          # all five checked; same two trials pooled
    assert label("tocilizumab-covid19-mortality") == "RELATED_TRIAL_INVENTORY_MAP"   # served RR vs comparator OR
    assert label("statins-primary-prevention-elderly") == "RELATED_TRIAL_INVENTORY_MAP"   # observational studies
    assert label("noac-vs-warfarin-af-stroke") == "NOT_ESTABLISHED"      # codex said all YES; dose arms not checked


def test_codex_found_mismatches_are_held_on_both_sides():
    for slug, kind in [("finerenone-ckd-t2d-renal", "ABSTRACT_VS_RESULTS_TUPLE"),
                       ("sacubitril-valsartan-hfref", "SAME_ESTIMATE_DIFFERENT_CONTROL"),
                       ("sglt2-hfref-hosp-cvdeath", "PARTICIPANT_COUNT_ABSTRACT_VS_RESULTS")]:
        d = cm.load_reported(str(ROOT), slug)
        m = next(x for x in d["mismatches"] if x["kind"] == kind)
        assert [s["state"] for s in m["sides"]] == ["HELD", "HELD"]
