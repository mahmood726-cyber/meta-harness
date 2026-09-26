"""REPORT ROLE IN SCREENING (external review of colchicine-postop-af, review hash 48741f59..., commit 6260e70c).

The COPPS AF substudy (PMID 22090167) was "screened in" in the page narrative but excluded X1 ("not a randomized
controlled trial") in the ledger, while its own publication type says Randomized Controlled Trial and the adjudicator
recommends inclusion. Cause: screen._is_rct rejected on the TITLE word 'substudy' before reading the design.

Screening is now THREE recorded decisions on ONE record per screened report:
  (1) parent-trial eligibility, (2) report relevance (primary / secondary report of a parent / no results),
  (3) result admissibility for this analysis (filled per outcome once outcomes are built).
The ledger row, the family object and the narrative all DERIVE from that record, and a consistency check fails when
any two disagree. Secondary reports link to their parent family (no double counting) instead of being rejected as
non-RCT. A held source whose own numbers cannot be reconciled is SOURCE_INTERNALLY_INCONSISTENT: held, not pooled,
not 'not retrieved'.

Written BEFORE the fix (see evidence/screening_roles/TESTS_PREFIX.txt).
"""
import copy
import json
import os
import subprocess

import pytest

from harness import fetch, pipeline, screen

ROOT = pipeline.ROOT
SLUG = "colchicine-postop-af"
COPPS, PARENT = "22090167", "NCT00128427"
CANDIDATE = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"


@pytest.fixture(scope="module")
def topic():
    config = json.load(open(os.path.join(ROOT, "topics", SLUG + ".json"), encoding="utf-8"))
    records = fetch.ensure(config, "")                # committed cache: no network
    merged = pipeline._dedup(records, config.get("pivotal_trials"))
    return config, records, merged


def _rec(merged, rid):
    return copy.deepcopy(next(r for r in merged if str(r.get("id")) == rid))


def _row(scr, rid):
    return next(d for d in scr["decisions"] if str(d["id"]) == rid)


# ------------------------------------------------------------------------------------------ the COPPS AF case
def test_copps_af_is_screened_in_as_a_secondary_report_of_its_parent(topic):
    config, records, _ = topic
    inp = pipeline.outcome_inputs(SLUG, config, records)
    row = _row(inp["scr"], COPPS)
    assert row["rule_id"] != "X1", row["reason"]
    assert row["decision"] == "include"
    sr = row["screening_record"]
    assert sr["report_relevance"]["state"] == "SECONDARY_REPORT"
    assert sr["parent_family"] == PARENT
    assert sr["parent_eligibility"]["state"] == "ELIGIBLE"
    assert (sr["ledger_decision"], sr["ledger_rule"]) == (row["decision"], row["rule_id"])


def test_the_second_screener_agrees_on_the_substudy(topic):
    config, _, merged = topic
    assert screen.screen_record_2(_rec(merged, COPPS), config.get("include", {})) == "include"


# ------------------------------------------------------------------------------------------ generic rules
def test_secondary_report_links_to_its_included_primary_report_and_is_not_counted_twice(topic):
    config, _, merged = topic
    sub = _rec(merged, COPPS)
    primary = dict(copy.deepcopy(sub), id="99999991",
                   title=sub["title"].replace("atrial fibrillation substudy", "trial").replace("substudy", "trial"))
    scr = screen.run([primary, sub], config)
    p, s = _row(scr, "99999991"), _row(scr, COPPS)
    assert p["decision"] == "include"
    assert (s["decision"], s["rule_id"]) == ("exclude", "X-LINKED"), s
    assert "not a randomized controlled trial" not in s["reason"]
    rec = s["screening_record"]
    assert rec["report_relevance"]["state"] == "SECONDARY_REPORT" and rec["report_relevance"]["linked_to"] == "99999991"
    assert rec["parent_eligibility"]["state"] == "ELIGIBLE"
    included_families = {d["screening_record"]["parent_family"] for d in scr["decisions"] if d["decision"] == "include"}
    assert included_families == {PARENT}


def test_protocol_or_design_paper_carries_no_results_and_is_not_called_non_rct(topic):
    config, _, merged = topic
    design = dict(_rec(merged, COPPS), id="99999992",
                  title="Rationale and design of the COPPS atrial fibrillation substudy")
    row = _row(screen.run([design], config), "99999992")
    assert (row["decision"], row["rule_id"]) == ("exclude", "X-NO-RESULTS"), row
    assert "not a randomized controlled trial" not in row["reason"]
    assert row["screening_record"]["report_relevance"]["state"] == "NO_RESULTS_REPORT"


def test_a_genuinely_non_randomised_report_is_still_X1(topic):
    config, _, merged = topic
    obs = dict(_rec(merged, COPPS), id="99999993", pubtypes=["Journal Article", "Observational Study"],
               title="Colchicine and atrial fibrillation after cardiac surgery: a cohort study",
               abstract="We studied a retrospective cohort of patients after cardiac surgery who received colchicine.")
    row = _row(screen.run([obs], config), "99999993")
    assert (row["decision"], row["rule_id"]) == ("exclude", "X1")
    assert row["screening_record"]["parent_eligibility"]["state"] == "INELIGIBLE"


def test_every_ledger_row_derives_from_its_one_record(topic):
    config, _, merged = topic
    scr = screen.run(merged, config)
    assert scr["decisions"]
    for d in scr["decisions"]:
        sr = d["screening_record"]
        assert (sr["ledger_decision"], sr["ledger_rule"]) == (d["decision"], d["rule_id"]), d["id"]
        assert set(sr) >= {"parent_family", "parent_eligibility", "report_relevance", "result_admissibility"}


# ------------------------------------------------------------------------------------------ consistency check
def _served(sha, slug=SLUG):
    return json.loads(subprocess.run(["git", "show", f"{sha}:docs/reviews/{slug}/review.json"], cwd=ROOT,
                                     capture_output=True, check=True).stdout)


def test_the_served_v1_review_shows_the_copps_contradiction():
    from harness import screening_record
    probs = [p for p in screening_record.consistency_problems(_served(CANDIDATE)) if p["report_id"] == COPPS]
    kinds = {p["kind"] for p in probs}
    assert "NARRATIVE_VS_LEDGER" in kinds, probs          # 'screened in' vs X1 exclude
    assert "REASON_VS_SPAN" in kinds, probs               # 'not an RCT' vs its own pubtype span 'Randomized Controlled Trial'
    assert "ADJUDICATOR_VS_LEDGER" in kinds, probs        # adjudicator recommends include


def _mini_review():
    rec = {"parent_family": "NCT1", "parent_eligibility": {"state": "ELIGIBLE"},
           "report_relevance": {"state": "SECONDARY_REPORT"}, "result_admissibility": {},
           "ledger_decision": "include", "ledger_rule": "INCLUDE"}
    return {"slug": "t", "screening": {"records": [
                {"id": "11111111", "decision": "include", "rule_id": "INCLUDE", "reason": "", "span": "",
                 "screening_record": rec}]},
            "trial_families": [{"family_id": "NCT1", "reports": [
                {"report_id": "11111111", "role": "SUBGROUP", "screening_record": dict(rec)}]}],
            "screening_narrative": []}


def test_a_consistent_record_passes():
    from harness import screening_record
    assert screening_record.consistency_problems(_mini_review()) == []


def test_PLANT_narrative_says_screened_in_while_the_ledger_excludes():
    from harness import screening_record
    r = _mini_review()
    r["screening"]["records"][0].update(decision="exclude", rule_id="X1")
    r["screening"]["records"][0]["screening_record"].update(ledger_decision="exclude", ledger_rule="X1")
    r["trial_families"][0]["reports"][0]["screening_record"].update(ledger_decision="exclude", ledger_rule="X1")
    r["evidence_base_caveat"] = "The substudy (PMID 11111111) is screened in and declared absent."
    kinds = {p["kind"] for p in screening_record.consistency_problems(r)}
    assert "NARRATIVE_VS_LEDGER" in kinds


def test_PLANT_ledger_row_disagrees_with_its_record():
    from harness import screening_record
    r = _mini_review()
    r["screening"]["records"][0]["decision"] = "exclude"
    kinds = {p["kind"] for p in screening_record.consistency_problems(r)}
    assert "LEDGER_VS_RECORD" in kinds


def test_PLANT_family_object_disagrees_with_the_record():
    from harness import screening_record
    r = _mini_review()
    r["trial_families"][0]["reports"][0]["screening_record"]["report_relevance"] = {"state": "PRIMARY_REPORT"}
    kinds = {p["kind"] for p in screening_record.consistency_problems(r)}
    assert "FAMILY_VS_RECORD" in kinds


def test_PLANT_report_screened_under_one_family_listed_under_another():
    from harness import screening_record
    r = _mini_review()
    r["trial_families"][0]["family_id"] = "NCT2"
    kinds = {p["kind"] for p in screening_record.consistency_problems(r)}
    assert "FAMILY_VS_RECORD" in kinds


# ------------------------------------------------------------------------------------------ source state
MASHAYEKHI = "Mashayekhi 2020"


def _mashayekhi_fact():
    from harness import claimgraph
    return next(f for f in claimgraph.regulatory_facts(ROOT, SLUG) if f["trial"] == MASHAYEKHI)


def test_mashayekhi_is_held_and_source_internally_inconsistent():
    from harness import invalidation
    f = _mashayekhi_fact()
    assert f["document_path"].endswith("ipp-6-e11.pdf")
    assert invalidation.missing_state(f) == "SOURCE_INTERNALLY_INCONSISTENT"
    assert invalidation.missing_state(f) not in ("DISCOVERED_NOT_RETRIEVED", "NOT_DISCOVERED", "POOLABLE")
    assert f["admissible"] is False
    kinds = {s["kind"] for s in f["spans"]}
    assert {"flow_allocated_colchicine_29", "flow_allocated_placebo_52", "methods_120_per_arm",
            "af_row_7_vs_13_under_29_52"} <= kinds
    assert all(s["pdf_page"] >= 1 for s in f["spans"])


def test_PLANT_an_internally_inconsistent_source_is_never_promoted_to_poolable():
    from harness import invalidation
    f = copy.deepcopy(_mashayekhi_fact())
    f["admissible"] = True
    f["adjudication"] = {"state": "ACCEPTED", "countersigned": True}
    assert invalidation.missing_state(f) == "SOURCE_INTERNALLY_INCONSISTENT"
