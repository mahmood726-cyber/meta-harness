"""PLANTS for REVIEW_REFERENCE_LIST (5 Oct decision, Cochrane Handbook: reference lists of related reviews are a standard
identification source). Identification from the comparator is allowed; ELIGIBILITY is our registered screen's alone;
DATA must come from a non-comparator source. Each plant asserts the requirement on synthetic items (slug namespace
__control_rrl), never on a live topic."""
import os
import sys

from harness import secondary_meta as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_identity_chain as gic  # noqa: E402
import g1_tracker as gt  # noqa: E402
import secondary_meta_build as smb  # noqa: E402

SLUG, COMP, OTHER = "__control_rrl", "11111111", "22222222"
R1 = {"reader": "READER_1", "model_decision": "ELIGIBLE"}
R2 = {"reader": "READER_2", "model_decision": "ELIGIBLE"}


def _row(meta):
    return sm.SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "figure", "id": "F1"}, source_digest="d" + meta,
                           provenance="MODEL_PROPOSAL_DUAL:x", trial_label="Smith 2010", measure="RR",
                           outcome_definition="all-cause mortality", effect="0.80", lower="0.60", upper="1.07",
                           family_id="PMID 99999901", state=sm.UNVERIFIED)


def _counted(se):
    return {"label": "Smith 2010", "in_our_pool": False, "route": "SECONDARY_SINGLE", "g1_countable": True,
            "scope_difference": None, "screen_eligibility": se}


def test_a_comparator_listed_trial_that_fails_our_screen_stays_out():
    x = {"in_our_pool": False, "seeded_funnel": {"stage": "SCREENED_OUT", "rule_id": "X1", "reason": "not an RCT",
                                                 "pmid": "99999901"}}
    se = gt.screen_eligibility(x, None, "99999901", [])
    assert se["state"] == "NOT_ELIGIBLE" and se["rule_id"] == "X1"
    assert not gt.is_matched(_counted(se))                    # an independent row is held, and it still does not count
    # one reader, or a dissenting reader, does not set the screen's exclusion aside
    assert not gt.is_matched(_counted(gt.screen_eligibility(x, None, "99999901", [R1])))
    assert not gt.is_matched(_counted(gt.screen_eligibility(
        x, None, "99999901", [R1, R2, {"reader": "READER_2", "model_decision": "INELIGIBLE"}])))
    o = {"trials": [_counted(se)]}
    gt.apply_coverage(o)
    assert o["trials"][0]["count_refusal"].startswith("NOT_SCREEN_ELIGIBLE:NOT_ELIGIBLE:X1")
    assert o["k_independent"] == 0


def test_never_screened_is_not_eligible_either():
    se = gt.screen_eligibility({"in_our_pool": False}, None, None, [R1, R2])
    assert se["state"] == "NOT_ASSESSED"
    assert not gt.is_matched(_counted(se))


def test_a_comparator_listed_trial_with_only_comparator_data_does_not_count():
    comp_row = _row(COMP)
    assert sm.g1_countable([comp_row], {COMP}) == []
    assert gt.secondary_single([comp_row], {COMP: {"usable": True, "positive_control": {"reproduced": True}}},
                               {COMP}, SLUG, None, {"pmids": ["99999901"]}) is None
    x = {"label": "Smith 2010", "in_our_pool": False, "route": "UNVERIFIED", "g1_countable": False,
         "scope_difference": None, "screen_eligibility": {"state": "ELIGIBLE", "basis": "OUR_SCREEN_INCLUDE"}}
    assert not gt.is_matched(x)                               # eligible by our screen, but no independent data


def test_a_comparator_listed_trial_passing_our_screen_with_an_independent_row_counts(monkeypatch):
    monkeypatch.setattr(gt, "primary_open", lambda *a, **k: [])   # no open primary held: the SS tier applies
    metas = {OTHER: {"usable": True, "positive_control": {"reproduced": True}, "provenance": "FOREST_READER_DUAL",
                     "figure": "F1", "record_id": "x"}}
    ss = gt.secondary_single([_row(COMP), _row(OTHER)], metas, {COMP}, SLUG, None, {"pmids": ["99999901"]})
    assert ss and ss["row"].meta_pmid == OTHER                # the non-comparator row, never the comparator's
    se = gt.screen_eligibility({"in_our_pool": False}, {"decision": "include", "rule_id": "I1"}, "99999901", [])
    assert se["state"] == "ELIGIBLE"
    assert gt.is_matched(_counted(se))
    # the screen excluded it, and BOTH readers judge it eligible on verified quotes: it counts, basis recorded
    x = {"in_our_pool": False, "seeded_funnel": {"stage": "SCREENED_OUT", "rule_id": "X3", "pmid": "99999901"}}
    se2 = gt.screen_eligibility(x, None, "99999901", [R1, R2])
    assert se2["basis"] == "TWO_READERS_JUDGE_ELIGIBLE" and gt.is_matched(_counted(se2))


def test_identity_from_a_reference_list_needs_a_reference_method_and_one_answer():
    base = {"slug": SLUG, "comparator_label": "GISSI-X [3]", "mapped": True}
    rows = [dict(base, meta_pmid=OTHER, pmid="99999901", methods=["META_REFERENCE_TITLE_ACRONYM", "TRACKER_NAME_EXACT"]),
            dict(base, meta_pmid=COMP, pmid="99999901", methods=["META_REFERENCE_SURNAME_YEAR"])]
    v = gic.reference_list_identity(SLUG, "GISSI-X [3]", rows)
    assert v["state"] == "RESOLVED" and v["pmid"] == "99999901" and v["basis"] == "REVIEW_REFERENCE_LIST"
    v = gic.reference_list_identity(SLUG, "GISSI-X [3]", rows + [dict(rows[0], pmid="99999902")])
    assert v["state"] == "AMBIGUOUS"
    # a tracker join alone is not a reference-list identity
    assert gic.reference_list_identity(SLUG, "GISSI-X [3]", [dict(rows[0], methods=["TRACKER_NAME_EXACT"])]) is None


def test_lane_rows_come_only_from_accepted_non_comparator_metas_and_never_at_99_percent(monkeypatch):
    acc = {"state": "ACCEPTED", "methods_reproducing": ["FE"]}
    row = {"meta_pmid": OTHER, "meta_doi": "", "location": {"kind": "figure", "id": "F1"}, "source_digest": "d",
           "provenance": "MODEL_PROPOSAL_DUAL:a+b", "trial_label": "Smith 2010", "measure": "RATE RATIO",
           "outcome_definition": "mortality", "effect": "0.8", "lower": "0.6", "upper": "1.07"}
    d = {"meta_results": {
        f"{SLUG}::{OTHER}": {"pmid": OTHER, "role": "meta", "acceptance": acc, "secondary_rows": [row, dict(row, trial_label="Jones 2011", ci_level="99%")]},
        f"{SLUG}::{COMP}": {"pmid": COMP, "role": "comparator", "acceptance": acc, "secondary_rows": [dict(row, meta_pmid=COMP)]},
        f"{SLUG}::33333333": {"pmid": "33333333", "role": "meta", "acceptance": {"state": "REFUSED"},
                              "secondary_rows": [dict(row, meta_pmid="33333333")]}}}
    monkeypatch.setattr(smb, "forest_lane_results", lambda fmt="forest_reader_v1": (d, {"commit": "c" * 40}))
    rows, metas = smb.forest_lane_metas(SLUG, COMP, have=set())
    assert set(metas) == {OTHER}                              # comparator and the refused meta never enter
    assert metas[OTHER]["positive_control"]["reproduced"] and metas[OTHER]["usable"]
    lv = {r.trial_label: why for r, why in rows}
    assert lv["Smith 2010"] is None and lv["Jones 2011"] == "CI_LEVEL_99%_NOT_95"
    assert {r.measure for r, _ in rows} == {smb.normalize_measure("RATE RATIO")} == {"IRR"}   # as our own reads
    # a meta we already read ourselves is never read twice
    assert smb.forest_lane_metas(SLUG, COMP, have={OTHER})[1] == {}


def _poaf(meta, e, lo, hi, et, ec):
    return sm.SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "figure", "id": "F"}, source_digest="d" + meta,
                           provenance="MODEL_PROPOSAL_DUAL:x", trial_label="Tabbalat 2020", measure="RR",
                           outcome_definition="postoperative atrial fibrillation", effect=e, lower=lo, upper=hi,
                           events_t=et, n_t=81, events_c=ec, n_c=71, family_id="PMID 99999903")


def test_metas_that_disagree_are_settled_by_the_trials_own_report_and_only_by_it():
    text = ("Postoperative atrial fibrillation occurred in 13 of 81 patients in the colchicine group and 13 of 71 in the "
            "placebo group (relative risk 0.88, 95% CI 0.44 to 1.76).")
    rows = [_poaf("31111111", "0.88", "0.44", "1.76", 13, 13), _poaf("32222222", "0.88", "0.44", "1.76", 13, 13),
            _poaf("33333333", "0.81", "0.40", "1.66", 12, 13)]
    sm.cross_check(rows)
    assert {r.state for r in rows} == {sm.BLOCKED}            # the plant: one dissenting read blocks all three
    n = smb.settle_crosscheck_by_primary(rows, lambda fam: [("text", "ft_99999903", text)], ["atrial fibrillation"])
    assert n == 2
    assert [r.state for r in rows] == [sm.VERIFIED, sm.VERIFIED, sm.BLOCKED]
    assert rows[0].verification["dissenting_metas"] == ["33333333"]
    assert any(f["finding"] == "DISSENTS_FROM_PRIMARY" for f in rows[2].findings)
    # the trial's report confirms NONE of them: the disagreement stands
    rows2 = [_poaf("31111111", "0.88", "0.44", "1.76", 13, 13), _poaf("33333333", "0.81", "0.40", "1.66", 12, 13)]
    sm.cross_check(rows2)
    assert smb.settle_crosscheck_by_primary(rows2, lambda fam: [("text", "t", "No numbers here about AF.")],
                                            ["atrial fibrillation"]) == 0
    assert {r.state for r in rows2} == {sm.BLOCKED}


def test_a_disagreement_is_settled_by_our_extraction_of_the_report_when_the_text_has_no_typed_match():
    rows = [_poaf("31111111", "0.88", "0.44", "1.76", 13, 13), _poaf("33333333", "0.81", "0.40", "1.66", 12, 13)]
    sm.cross_check(rows)
    prim = {"measure": "RR", "events_t": 13, "n_t": 81, "events_c": 13, "n_c": 71,
            "span": "13 of 81 vs 13 of 71", "source": "our extraction"}
    n = smb.settle_crosscheck_by_primary(rows, lambda fam: [], ["atrial fibrillation"], primary_of=lambda fam: prim)
    assert n == 1 and [r.state for r in rows] == [sm.VERIFIED, sm.MISMATCH]   # dissent compared with the report


def test_every_row_finding_is_a_dict_whatever_wrote_it():
    assert smb.as_finding("ROW_CI_IS_99_PERCENT: the meta prints 99%") == {"finding": "ROW_CI_IS_99_PERCENT",
                                                                        "detail": "the meta prints 99%"}
    d = {"finding": "X", "printed_vs_arm_derived": 1}
    assert smb.as_finding(d) is d
    # the tracker's reader survives a legacy string all the same (second layer)
    out = gt.comparator_findings([{"label": "T", "comparator_row_findings": ["SOME_CODE: text", d]}], COMP)
    assert [f["finding"] for f in out if f.get("trial") == "T"][-2:] == ["SOME_CODE", "X"]


def test_a_lane_trial_takes_our_screen_state_by_identity_when_labels_differ():
    import g1_import_lanes as gil
    recs = [{"id": "99999911", "decision": "include", "rule_id": "INCLUDE", "trial_family_id": "NCT99999911"},
            {"id": "99999912", "decision": "exclude", "rule_id": "X1", "reason": "not an RCT", "trial_family_id": "NCT99999912"}]
    o = {"trials": [{"label": "ALPHA", "family": "NCT99999911"}, {"label": "BETA", "family": "NCT99999912"},
                    {"label": "GAMMA", "family": "NCT99999913"}, {"label": "DELTA", "family": "PMID 99999911"}]}
    gil.attach_screen_state(o, {"trials": [{"label": "Some other label"}]}, None, recs)
    st = {x["label"]: x["screen_eligibility"]["state"] for x in o["trials"]}
    assert st == {"ALPHA": "ELIGIBLE", "BETA": "NOT_ELIGIBLE", "GAMMA": "NOT_ASSESSED", "DELTA": "ELIGIBLE"}
    assert o["trials"][1]["screen_eligibility"]["rule_id"] == "X1"


def test_a_dissenting_row_gets_its_comparison_with_the_report_and_so_its_side():
    def hr(meta, hi):
        return sm.SecondaryRow(meta_pmid=meta, meta_doi="", location={"kind": "figure", "id": "F"}, source_digest="d" + meta,
                               provenance="MODEL_PROPOSAL_DUAL:x", trial_label="PIONEER 6", measure="HR",
                               outcome_definition="MACE", effect="0.79", lower="0.57", upper=hi,
                               family_id="PMID 99999904")
    rows = [hr("41111111", "1.10"), hr("42222222", "1.11")]
    sm.cross_check(rows)
    prim = {"measure": "HR", "effect": "0.79", "lower": "0.57", "upper": "1.11", "span": "HR 0.79 (0.57-1.11)",
            "source": "our extraction", "report_text": "HR 0.79 (95% CI 0.57-1.11)"}
    smb.settle_crosscheck_by_primary(rows, lambda fam: [], ["MACE"], primary_of=lambda fam: prim)
    assert rows[1].state == sm.VERIFIED
    assert rows[0].state == sm.MISMATCH and (rows[0].verification or {}).get("which_side")


def test_an_ambiguous_report_with_unanimous_other_agent_titles_is_another_agents_trial(tmp_path, monkeypatch):
    import json as _json
    ic = {"results": {f"{SLUG}::VERTIS-X": {"state": "AMBIGUOUS", "basis": "ACRONYM", "self_naming_pmids": ["1", "2"],
                                             "scope": "OTHER_AGENT:ertugliflozin"},
                      f"{SLUG}::MIXED-X": {"state": "AMBIGUOUS", "basis": "ACRONYM", "self_naming_pmids": ["3", "4"],
                                            "scope": "IN_SCOPE"}}}
    (tmp_path / "identity_chain.json").write_text(_json.dumps(ic), encoding="utf-8")
    monkeypatch.setattr(gt, "OUT", str(tmp_path))
    T = {"trials": [{"slug": SLUG, "label": "VERTIS-X", "pmids": [], "ncts": [], "drug": "AGENT_UNCONFIRMED"},
                    {"slug": SLUG, "label": "MIXED-X", "pmids": [], "ncts": [], "drug": "AGENT_UNCONFIRMED"}]}
    got = {t["label"]: t for t in gt.with_identity_chain(T)["trials"]}
    assert got["VERTIS-X"]["drug"] == "OTHER_AGENT" and got["VERTIS-X"]["pmids"] == []   # scope stated, report not guessed
    assert got["MIXED-X"]["drug"] == "AGENT_UNCONFIRMED"
