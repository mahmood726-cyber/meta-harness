"""V1.0.1 plants from the GLP-1 review: the B-prime outcome-ascertainment clause is executed (harness/ascertainment.py).

STRUCTURAL_PASS -> FULL_ELIGIBLE needs held evidence that 3-point MACE (or its three components) was prospectively
specified (a source dated before the results) AND systematically ascertained. Unknown -> PENDING with a retrieval task,
never eligible, never excluded. A programme statement (Husain 2020) supports ascertainment only, and its pooled
post-hoc estimate never enters a pool.
"""
import copy
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harness import ascertainment as asc  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"

PRO = "The primary outcome is the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke."
ADJ = "All cardiovascular events were adjudicated by an independent blinded committee."


def _root(tmp_path, families, programmes=(), design_date="2014-01-01", results_date="2016-06-01"):
    (tmp_path / "cache" / "t").mkdir(parents=True)
    (tmp_path / "cache" / "t" / "design.txt").write_text("Design. " + PRO + " " + ADJ, encoding="utf-8")
    (tmp_path / "cache" / "t" / "results.txt").write_text("Results report.", encoding="utf-8")
    ev = {"documents": {"d": {"kind": "design paper", "document_ref": "cache/t/design.txt", "earliest_date": design_date},
                        "r": {"kind": "results", "document_ref": "cache/t/results.txt", "earliest_date": results_date}},
          "families": families, "programmes": list(programmes)}
    (tmp_path / "cache" / "t" / "ascertainment_evidence.json").write_text(json.dumps(ev), encoding="utf-8")
    return tmp_path


def _fam(pro=True, adj=True):
    f = {"results": {"doc": "r", "earliest_date": "2016-06-01"}, "completion_date": "2015-12-01"}
    if pro:
        f["prospective"] = {"doc": "d", "quote": PRO}
    if adj:
        f["ascertained"] = {"doc": "d", "quote": ADJ}
    return f


def test_PLANT_a_family_with_no_ascertainment_evidence_cannot_reach_FULL_ELIGIBLE(tmp_path):
    ev = asc.load(_root(tmp_path, {}), "t")
    d = asc.decide("NCT00000001", ["SOME TRIAL"], ev)
    assert d["state"] == "PENDING" and d["retrieval_task"] == asc.RETRIEVAL_TASK
    assert asc.decide("NCT00000001", [], None)["state"] == "PENDING"          # no evidence file at all


def test_PLANT_both_halves_evidenced_is_MET(tmp_path):
    ev = asc.load(_root(tmp_path, {"NCT1": _fam()}), "t")
    d = asc.decide("NCT1", [], ev)
    assert d["state"] == "MET" and d["prospective"]["date_tier"] == "DATED_BEFORE_COMPLETION"


@pytest.mark.parametrize("pro,adj", [(True, False), (False, True)])
def test_PLANT_one_half_is_not_enough(tmp_path, pro, adj):
    ev = asc.load(_root(tmp_path, {"NCT1": _fam(pro, adj)}), "t")
    assert asc.decide("NCT1", [], ev)["state"] == "PENDING"


def test_PLANT_programme_evidence_supports_ascertainment_only(tmp_path):
    prog = {"id": "p", "doc": "d", "quote": ADJ, "applies_to_acronyms": ["PIONEER 8"]}
    ev = asc.load(_root(tmp_path, {}, [prog]), "t")
    d = asc.decide("NCT03021187", ["PIONEER 8"], ev)
    assert d["ascertained"]["state"] == "YES" and d["ascertained"]["via_programme"] == "p"
    assert d["prospective"]["state"] == "UNKNOWN" and d["state"] == "PENDING"
    assert asc.decide("NCT9", ["PIONEER 6"], ev)["ascertained"]["state"] == "UNKNOWN"   # not named by the programme


@pytest.mark.parametrize("mutate,msg", [
    (lambda f: f["prospective"].update(quote="A sentence that is not in the document at all."), "not located"),
    (lambda f: f["prospective"].update(quote=ADJ), "names neither MACE"),
    (lambda f: f["ascertained"].update(quote=PRO), "states no adjudication"),
])
def test_PLANT_bad_evidence_refuses_the_file(tmp_path, mutate, msg):
    f = _fam()
    mutate(f)
    with pytest.raises(asc.EvidenceRefused, match=msg):
        asc.load(_root(tmp_path, {"NCT1": f}), "t")


def test_PLANT_a_prospective_source_dated_after_the_results_refuses(tmp_path):
    with pytest.raises(asc.EvidenceRefused, match="not before the results"):
        asc.load(_root(tmp_path, {"NCT1": _fam()}, design_date="2017-01-01"), "t")


# ---------------------------------------------------------------- the served GLP-1 page
def _served():
    return json.load(open(ROOT / "docs/reviews" / SLUG / "review.json", encoding="utf-8"))


def test_every_eligible_glp1_family_has_both_halves_evidenced():
    fams = _served()["trial_families"]
    elig = [f for f in fams if f["eligibility"]["state"] == "ELIGIBLE"]
    assert elig and all(f["eligibility"]["stage"] == "FULL_ELIGIBLE" and f["eligibility"]["ascertainment"]["state"] == "MET"
                        for f in elig)
    pend = [f for f in fams if f["eligibility"].get("absence_code") == "OUTCOME_ASCERTAINMENT_PENDING"]
    assert pend and all(f["eligibility"]["stage"] == "STRUCTURAL_PASS" and f["eligibility"]["ascertainment"]["retrieval_task"]
                        for f in pend)


def test_count_chain_derives_each_state_and_SUSTAIN_6_is_pooled_but_pending():
    ch = _served()["family_count_chain"]
    assert ch["structural_pass"] == ch["eligible_families"] + ch["ascertainment_pending"]
    assert ch["pooled_with_ascertainment_pending"] == ["NCT01720446"]           # no version-dated pre-results source held
    html = (ROOT / "docs/reviews" / SLUG / "index.html").read_text(encoding="utf-8")
    assert "B-prime eligibility states" in html and "conditional on it" in html


def test_PIONEER_8_is_linked_to_Zinman_and_its_ascertainment_comes_from_the_programme_statement():
    f = next(f for f in _served()["trial_families"] if f["family_id"] == "NCT03021187")
    assert "31530667" in {r["report_id"] for r in f["reports"]}
    a = f["eligibility"]["ascertainment"]
    assert a["ascertained"].get("via_programme") == "husain-2020-sustain-pioneer" and a["state"] == "PENDING"


def test_the_pooled_SUSTAIN_PIONEER_post_hoc_estimate_never_enters_as_a_trial():
    for o in _served()["outcomes"]:
        assert "31903692" not in json.dumps([t.get("id") or t.get("label") for t in o.get("trials") or []])


# ---------------------------------------------------------------- search execution records (one per declared source)
def test_every_declared_source_has_an_execution_record_and_unrun_ones_say_so():
    sx = _served()["search_execution"]
    rows = {r["source"]: r for r in sx["rows"]}
    assert set(sx["declared"]) <= set(rows)
    assert rows["Cochrane CENTRAL"]["state"] == "NOT_EXECUTED" and rows["WHO ICTRP"]["state"] == "NOT_EXECUTED"
    # Europe PMC's status-table RAN_OK was inferred; its only independent run has no held response bodies
    assert rows["Europe PMC"]["state"] != "EXECUTED"
    assert rows["Trial-family assembly"]["executions"][0]["entered_via"] == "MANUAL_ADDITION"     # PIONEER 8 link
    seeded = [x for x in rows["PubMed/MEDLINE"]["executions"] if x["entered_via"] == "SEEDED_IDENTIFIER"]
    assert seeded and all("[uid]" in x["query"] or "[si]" in x["query"] for x in seeded)
    html = (ROOT / "docs/reviews" / SLUG / "index.html").read_text(encoding="utf-8")
    assert "Search execution records" in html and "class='seeded'" in html and "class='manual'" in html


def test_PLANT_gate_refuses_a_declared_source_without_a_record_and_an_unevidenced_ELIGIBLE(tmp_path):
    from harness import gate
    rev = copy.deepcopy(_served())
    rev["search_execution"]["rows"] = [r for r in rev["search_execution"]["rows"] if r["source"] != "WHO ICTRP"]
    f = next(f for f in rev["trial_families"] if f["eligibility"].get("stage") == "STRUCTURAL_PASS")
    f["eligibility"]["state"] = "ELIGIBLE"
    (tmp_path / "review.json").write_text(json.dumps(rev), encoding="utf-8")
    bad = gate.check_eligibility_states_and_search_execution(str(tmp_path), "<html></html>")
    assert any("WHO ICTRP" in b for b in bad) and any(f["family_id"] in b for b in bad)
    assert any("not rendered" in b for b in bad)
