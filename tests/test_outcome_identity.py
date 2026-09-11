"""Outcome-identity gate (harness.ctgov_results.extract_ctgov judgments=...): the sanctioned
model-as-source use. An OM is pooled only if its title carries an is_match=True judgment; None
keeps the deterministic substring behaviour (backward-compatible)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.ctgov_results import extract_ctgov  # noqa: E402


def _om(title, ai=100, n1=1000, ci=120, n2=1000, ptype="PRIMARY"):
    return {"title": title, "type": ptype, "paramType": "COUNT_OF_PARTICIPANTS",
            "groups": [{"id": "g1", "title": "Balanced crystalloid"},
                       {"id": "g2", "title": "Saline control"}],
            "classes": [{"categories": [{"measurements": [
                {"groupId": "g1", "value": str(ai)}, {"groupId": "g2", "value": str(ci)}]}]}],
            "denoms": [{"counts": [{"groupId": "g1", "value": str(n1)},
                                   {"groupId": "g2", "value": str(n2)}]}]}


ARGS = (["mortality"], ["balanced", "crystalloid"], ["saline", "control"])


def test_none_judgments_is_backward_compatible():
    r = extract_ctgov([_om("30-day mortality")], *ARGS)
    assert r and r["ai"] == 100


def test_is_match_true_admits_and_attaches_judgment():
    j = {"30-day mortality": {"is_match": True, "candidate_population": "in-hospital",
                              "candidate_timepoint": "30-day", "candidate_definition": "all-cause death",
                              "rationale": "same outcome"}}
    r = extract_ctgov([_om("30-day mortality")], *ARGS, judgments=j)
    assert r and r["ai"] == 100
    assert r["identity_judgment"]["is_match"] is True
    assert r["identity_judgment"]["candidate_title"] == "30-day mortality"


def test_is_match_false_refuses():
    j = {"30-day mortality": {"is_match": False, "candidate_population": "", "candidate_timepoint": "",
                              "candidate_definition": "", "rationale": "subgroup"}}
    assert extract_ctgov([_om("30-day mortality")], *ARGS, judgments=j) is None


def test_unjudged_title_refuses_when_gated():
    # gated (judgments is a dict) but this title has no judgment => refuse (refuse-otherwise)
    assert extract_ctgov([_om("30-day mortality")], *ARGS, judgments={}) is None


def test_icu_free_days_class_is_refused_but_mortality_admitted():
    # The real balanced-crystalloids case: an ICU-free-days OM substring-matches 'intensive care'
    # but is a different endpoint; the mortality OM is the true one.
    oms = [_om("Intensive Care Unit Free Days to Day 28", ai=10, n1=500, ci=9, n2=500, ptype="SECONDARY"),
           _om("30-day In-hospital Mortality", ai=200, n1=1000, ci=230, n2=1000, ptype="SECONDARY")]
    j = {"Intensive Care Unit Free Days to Day 28": {"is_match": False, "candidate_population": "ICU",
             "candidate_timepoint": "day 28", "candidate_definition": "days alive and ICU-free",
             "rationale": "continuous composite, not mortality"},
         "30-day In-hospital Mortality": {"is_match": True, "candidate_population": "in-hospital",
             "candidate_timepoint": "30-day", "candidate_definition": "all-cause death",
             "rationale": "matches declared mortality"}}
    r = extract_ctgov(oms, ["mortality", "intensive care"], ["balanced", "crystalloid"],
                      ["saline", "control"], judgments=j)
    assert r and r["ai"] == 200  # the mortality OM, not the ICU-free-days OM
    assert r["identity_judgment"]["candidate_title"] == "30-day In-hospital Mortality"
