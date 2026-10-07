"""Plants for V9-01Q (Mahmood 7 Oct, 'yes to all'; decision D7a): a comparator trial kept OUT of the served pool by a
recorded decision is a NAMED divergence -- a comparator finding citing the decision, never a scope difference (it does
not leave the eligible denominator) -- and only when the register entry is signed and the decision exists."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402
import render_g1_tracker as rg  # noqa: E402

REG = json.load(open(os.path.join(ROOT, "registry", "g1_decision_named_divergences.json"), encoding="utf-8"))
DEC = json.load(open(os.path.join(ROOT, "registry", "g1_decisions.json"), encoding="utf-8"))
TRIALS = [{"label": "EXAMINE", "in_our_pool": False}, {"label": "TECOS", "in_our_pool": True}]


def test_PLANT_a_signed_decision_exclusion_is_named_with_the_decision_as_its_span():
    f = gt.decision_named_divergences("dpp4-mace-t2d", TRIALS, reg=REG, decisions=DEC)
    assert len(f) == 1 and f[0]["trial"] == "EXAMINE" and f[0]["finding"] == "DECISION_EXCLUDED_FROM_SERVED_POOL"
    assert f[0]["gate"] == "D7-REEXPRESSED-CI-MATCHING-ONLY" and "matching only" in f[0]["span"]["text"].lower()
    assert gt.decision_named_divergences("esketamine-trd-madrs", TRIALS, reg=REG, decisions=DEC) == []


def test_PLANT_unsigned_entries_missing_decisions_and_pooled_trials_are_never_named():
    r = copy.deepcopy(REG)
    r["entries"][0]["signed"]["state"] = "OPEN"
    assert gt.decision_named_divergences("dpp4-mace-t2d", TRIALS, reg=r, decisions=DEC) == []
    d = copy.deepcopy(DEC)
    d["decisions"] = [x for x in d["decisions"] if not x["id"].startswith("D7-")]
    assert gt.decision_named_divergences("dpp4-mace-t2d", TRIALS, reg=REG, decisions=d) == []
    pooled = [{"label": "EXAMINE", "in_our_pool": True}]
    assert gt.decision_named_divergences("dpp4-mace-t2d", pooled, reg=REG, decisions=DEC) == []


def test_PLANT_the_page_recount_counts_a_decision_named_trial_as_named():
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "dpp4-mace-t2d.json"), encoding="utf-8"))
    o = copy.deepcopy(o)
    o["comparator_findings"] = [f for f in o.get("comparator_findings") or []
                                if f.get("finding") != "DECISION_EXCLUDED_FROM_SERVED_POOL"]
    assert "EXAMINE" in rg.recompute(o)["unnamed"]
    o["comparator_findings"] += gt.decision_named_divergences("dpp4-mace-t2d", o["trials"], reg=REG, decisions=DEC)
    r = rg.recompute(o)
    assert "EXAMINE" not in r["unnamed"] and r["criteria"]["DIVERGENCES_NAMED"]


def test_PLANT_unknown_pool_membership_is_never_an_exclusion():
    """codex v9-apply-r9 #1: a missing / null in_our_pool counted as 'outside the pool'."""
    for t in ({"label": "EXAMINE"}, {"label": "EXAMINE", "in_our_pool": None}):
        assert gt.decision_named_divergences("dpp4-mace-t2d", [t], reg=REG, decisions=DEC) == []
