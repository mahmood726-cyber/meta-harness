"""Regimen identity plants and held NOAC positive controls; no invented research effects."""
import json
from pathlib import Path
import sys
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import arm_object, arm_parse, pipeline

ARMS = ["edoxaban 30 mg twice daily", "edoxaban 60 mg once daily"]


def test_equal_daily_totals_are_not_equal_regimens():
    a, b = map(arm_parse.parse_regimen, ARMS)
    assert a == dict(agent="edoxaban", dose_mg=30, frequency="BID", daily_mg=60)
    assert b == dict(agent="edoxaban", dose_mg=60, frequency="QD", daily_mg=60)
    assert not arm_parse.same_regimen(a, b)
    assert arm_parse.same_regimen(ARMS[0], "Edoxaban 30 mg b.i.d.")
    assert not arm_parse.same_regimen(ARMS[0], "dabigatran 30 mg BID")
    assert not arm_parse.same_regimen("edoxaban 30 mg", "edoxaban 30 mg")


def test_held_weitz_snapshot_and_rule_identity():
    held = json.loads((ROOT / "evidence/dose_regimen/weitz_held.json").read_text(encoding="utf-8"))
    original = json.loads(subprocess.check_output([
        "git", "show", "3876a62dca66764dff1b4f84d6b43356a1a9e3bb:" + held["path"]], cwd=ROOT))
    record = next(r for r in original["records"] if r["id"] == held["id"])
    assert record["abstract"] == held["abstract"]
    assert arm_parse.select_regimen("edoxaban 60 mg/day", record)["state"] == "AMBIGUOUS_REGIMEN"
    selected = arm_parse.select_regimen(ARMS[1], record)
    assert selected["state"] == "SELECTED"
    assert selected["regimen"] == arm_parse.parse_regimen(ARMS[1])


@pytest.mark.parametrize("word,frequency,daily", [
    ("once daily", "QD", 30), ("q.d.", "QD", 30), ("daily", "QD", 30),
    ("twice daily", "BID", 60), ("b.i.d.", "BID", 60), ("every 12 h", "BID", 60),
    ("three times daily", "TID", 90), ("t.i.d.", "TID", 90), ("every 8 hours", "TID", 90),
    ("once weekly", "QW", 30 / 7), ("q.w.", "QW", 30 / 7), ("", "NOT_STATED", None),
])
def test_frequency_spellings(word, frequency, daily):
    r = arm_parse.parse_regimen("edoxaban 30 mg " + word)
    assert r["frequency"] == frequency
    assert r["daily_mg"] == pytest.approx(daily) if daily is not None else r["daily_mg"] is None


def test_daily_total_is_not_an_administration_dose():
    assert arm_parse.parse_regimen("edoxaban 60 mg/day") == dict(
        agent="edoxaban", dose_mg=None, frequency="NOT_STATED", daily_mg=None)
    assert arm_parse.same_regimen("edoxaban 60 mg/day in twice daily doses", ARMS[0])
    assert arm_parse.parse_regimen("edoxaban 30 mg twice weekly")["frequency"] == "NOT_STATED"
    assert arm_parse.parse_regimen("edoxaban 30 mg/kg BID")["dose_mg"] is None


@pytest.mark.parametrize("rule", ["edoxaban 60 mg/day", "edoxaban 60 mg", "standard dose"])
@pytest.mark.parametrize("record", [
    {"interventions": ARMS},
    {"abstract": "Patients were randomized to edoxaban 30 mg twice daily or edoxaban 60 mg once daily."},
])
def test_frequency_omission_is_refused_even_when_mg_matches_only_one_arm(rule, record):
    assert arm_parse.select_regimen(rule, record)["state"] == "AMBIGUOUS_REGIMEN"


def test_explicit_rule_selects_only_qd_arm():
    selected = arm_parse.select_regimen(ARMS[1], {"interventions": ARMS})
    assert selected["state"] == "SELECTED"
    assert selected["matched_arms"] == [ARMS[1]]
    assert arm_parse.select_regimen("edoxaban 60 mg BID", {"interventions": ARMS})["state"] == "AMBIGUOUS_REGIMEN"
    same_dose = {"interventions": ["edoxaban 30 mg QD", "edoxaban 30 mg BID"]}
    assert arm_parse.select_regimen("edoxaban 30 mg", same_dose)["state"] == "AMBIGUOUS_REGIMEN"
    assert arm_parse.select_regimen("edoxaban 30 mg", {"interventions": ["edoxaban 30 mg twice weekly"]})["state"] == "AMBIGUOUS_REGIMEN"


def test_arm_object_keeps_frequency():
    obj = arm_object.build({"interventions": ARMS})
    assert [a["dose"]["value"] for a in obj["randomised_arm"]] == ["30 mg BID", "60 mg QD"]
    assert arm_object._dose_of("edoxaban 60 mg/day") == "60 mg/day NOT_STATED"
    assert all(a["drug"]["value"] == "edoxaban" for a in obj["randomised_arm"])


def _held():
    folder = ROOT / "cache" / "noac-vs-warfarin-af-stroke"
    records = json.loads((folder / "records.json").read_text(encoding="utf-8"))
    rules = json.loads((folder / "dose_selection.json").read_text(encoding="utf-8"))
    return {r["id"]: r for r in records["records"] + records["ctgov"]}, rules


@pytest.mark.parametrize("rid,agent,dose,freq", [
    ("19717844", "dabigatran", 150, "BID"), ("24251359", "edoxaban", 60, "QD"),
])
def test_served_rules_resolve_from_held_frequency_without_changing_effect(rid, agent, dose, freq):
    records, rules = _held()
    selected = arm_parse.select_regimen(rules[rid]["dose"], records[rid])
    assert selected["state"] == "SELECTED"
    assert selected["regimen"] == arm_parse.parse_regimen(f"{agent} {dose} mg {freq}")
    out = _outcome(rid, records, rules)
    trial = next(t for t in out["trials"] if t["id"] == "PMID " + rid)
    assert trial["provenance"] == "pre_specified_dose"
    assert trial["regimen"] == selected["regimen"]
    assert all(trial[k] == rules[rid][k] for k in ("effect", "ci_low", "ci_high", "scale"))


def _outcome(rid, records, rules):
    return pipeline._build_outcome(
        {"name": rules[rid]["outcome"], "keywords": ["stroke", "systemic embolism"], "estimand": rules[rid]["scale"]},
        "benefit", [{"id": rid, "id_type": "pmid"}], records,
        ["edoxaban", "dabigatran"], ["warfarin"], dose_selection=rules)


@pytest.mark.parametrize("rule", ["edoxaban 60 mg/day", "edoxaban 60 mg", ARMS[1]])
def test_pipeline_override_cannot_bypass_regimen_check(rule):
    # Reuse a held effect solely as a plumbing fixture; this is not a Weitz effect.
    records, rules = _held()
    rid = "24251359"
    records = {rid: dict(records[rid], abstract="", interventions=ARMS)}
    rules = {rid: dict(rules[rid], dose=rule)}
    out = _outcome(rid, records, rules)
    if rule == ARMS[1]:
        assert len(out["trials"]) == 1
        assert out["trials"][0]["regimen"]["frequency"] == "QD"
    else:
        assert not out["trials"]
        assert out["declared_absent_trials"][0]["state"] == "AMBIGUOUS_REGIMEN"
