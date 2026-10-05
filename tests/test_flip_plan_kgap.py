"""PLANTS for the k-gap items of the 5 Oct flip plan (synthetic items; namespace __control_flip).
  #2  an acronym shared by several registrations resolves only to the one drug-vs-placebo registration; the scope is
      the registered drug (SCORED -> sotagliflozin)
  #5  a comparator row is checked against the trial's REGISTERED per-arm percentages: consistent / arms swapped
      (EMPA-REG 95/4687 vs 126/2333 against 2.7% / 4.1%) / inconsistent; a row the family join cannot place joins the
      comparator's own unit only on a surname unique within that comparator
  ticagrelor: one registered trial is one unit (PLATO and its invasive substudy, one NCT)"""
import os
import sys

from harness import secondary_meta as sm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_identity_chain as gic  # noqa: E402
import g1_tracker as gt  # noqa: E402


def test_a_shared_acronym_resolves_only_to_its_one_drug_vs_placebo_registration(tmp_path):
    (tmp_path / "studies.txt").write_text(
        "nct_id|acronym|brief_title\nNCT99999941|SCOREX|snoring device\nNCT99999942|SCOREX|sotagliflozin outcomes\n"
        "NCT99999943|SCOREX|transfusion\nNCT99999944|TWODRUG|a\nNCT99999945|TWODRUG|b\n", encoding="utf-8")
    (tmp_path / "interventions.txt").write_text(
        "id|nct_id|intervention_type|name|description\n1|NCT99999941|DEVICE|TRP|x\n2|NCT99999942|DRUG|Sotagliflozin|x\n"
        "3|NCT99999942|DRUG|Placebo|x\n4|NCT99999943|DIAGNOSTIC_TEST|ScvO2|x\n5|NCT99999944|DRUG|Agent A|x\n"
        "6|NCT99999944|DRUG|Placebo|x\n7|NCT99999945|DRUG|Agent B|x\n8|NCT99999945|DRUG|Placebo|x\n", encoding="utf-8")
    got = gic.registry_acronym_identity({"SCOREX": ["s::SCOREX"], "TWODRUG": ["s::TWODRUG"]}, str(tmp_path),
                                        lambda k: ["dapagliflozin"])
    assert got["s::SCOREX"]["nct"] == "NCT99999942" and got["s::SCOREX"]["scope"] == "OTHER_AGENT:sotagliflozin"
    assert got["s::SCOREX"]["basis"].endswith("ONLY_DRUG_VS_PLACEBO_REGISTRATION")
    assert got["s::TWODRUG"]["state"] == "AMBIGUOUS"                # two drug-vs-placebo registrations: never picked


def test_registry_scope_reads_the_registered_drug_not_the_placebo():
    v = gic.registry_scope("NCT1", [("DRUG", "Sotagliflozin"), ("DRUG", "Placebo")], ["dapagliflozin"])
    assert v["scope"] == "OTHER_AGENT:sotagliflozin" and "Sotagliflozin" in v["span"]["text"]
    assert gic.registry_scope("NCT1", [("DRUG", "Dapagliflozin 10 mg"), ("DRUG", "Placebo")], ["dapagliflozin"])["scope"] == "IN_SCOPE"


def _cr(et, nt, ec, nc):
    return {"events_t": et, "n_t": nt, "events_c": ec, "n_c": nc}


def test_a_comparator_row_is_checked_against_the_registered_arm_percentages(monkeypatch):
    rec = {"__control:1": {"state": "RECORDED", "nct": "NCT99999951", "outcome_title": "Percentage of Participants With "
                           "Heart Failure Requiring Hospitalisation", "snapshot": "s",
                           "groups": [{"title": "Placebo", "n_analysed": 2333, "value": "4.1"},
                                      {"title": "All Drug", "n_analysed": 4687, "value": "2.7"}]}}
    monkeypatch.setattr(gt, "_ARM_PCT", rec)
    kw = ["heart failure hospitalisation"]
    assert gt.registered_arm_check(_cr(95, 4687, 126, 2333), "NCT99999951", kw)["state"] == "ARMS_SWAPPED"
    assert gt.registered_arm_check(_cr(126, 4687, 95, 2333), "NCT99999951", kw)["state"] == "CONSISTENT"
    assert gt.registered_arm_check(_cr(60, 4687, 60, 2333), "NCT99999951", kw)["state"] == "INCONSISTENT"
    assert gt.registered_arm_check(_cr(95, 4000, 126, 2333), "NCT99999951", kw) is None     # no arm with that N
    assert gt.registered_arm_check(_cr(95, 4687, 126, 2333), "NCT99999951", ["stroke"]) is None   # another outcome
    o = {"trials": [{"label": "Zinman (8)", "comparator_row": _cr(95, 4687, 126, 2333),
                     "comparator_row_arm_check": {"state": "ARMS_SWAPPED", "basis": "b", "registry": {}}}]}
    assert [f["finding"] for f in gt.comparator_findings(o["trials"], "C")] == ["COMPARATOR_ROW_ARMS_SWAPPED"]


def _row(label):
    return sm.SecondaryRow(meta_pmid="C", meta_doi="", location={}, source_digest="", provenance="", trial_label=label,
                           measure="RR", outcome_definition="")


def test_an_unplaced_comparator_row_joins_only_on_a_surname_unique_within_the_comparator():
    ents = [{"id": "Zinman (8)", "label": "Zinman (8)"}, {"id": "Cannon (11)", "label": "Cannon (11)"},
            {"id": "Smith (1)", "label": "Smith (1)"}, {"id": "Smith (2)", "label": "Smith (2)"}]
    rows = [_row("Zinman 2016"), _row("Smith 2010"), _row("Cannon 2020")]
    got = gt.same_comparator_surname_join(rows, ents, {"Cannon (11)": rows[2]})
    assert set(got) == {"Zinman (8)"} and got["Zinman (8)"] is rows[0]          # Smith: two units -> never joined
    assert got["Zinman (8)"].findings[-1]["finding"] == "JOINED_BY_UNIQUE_SURNAME_WITHIN_COMPARATOR"


def test_one_registered_trial_is_one_unit():
    ours = [{"id": "PMID 19717846", "pmid": "19717846", "nct": "NCT00391872"}]
    sub = {"label": "1 [21]", "pmids": ["20079528"], "ncts": ["NCT00391872"]}       # invasive substudy, listed first
    main = {"label": "9 [28]", "pmids": ["19717846"], "ncts": ["NCT00391872"]}
    other = {"label": "8 [27]", "pmids": ["17980250"], "ncts": []}
    dup = gt.one_trial_one_unit([sub, other, main], ours)
    assert list(dup) == [id(sub)] and dup[id(sub)][0] is main                   # the unit citing the pooled report wins
    x = {"same_trial_as": {"unit": "9 [28]", "nct": "NCT00391872", "this_row": "1 [21] | 2010 | 13408",
                           "kept_row": "9 [28] | 2009 | 18624"}}
    d = gt.scope_difference(x, {}, "__control_flip")
    assert d["kind"] == "SAME_TRIAL_AS_ANOTHER_UNIT" and "13408" in d["span"]["text"] and d["span_source"]


def test_one_paper_reporting_two_registered_trials_is_two_units():
    # ODYSSEY FH I and FH II: one paper (PMID 26330422), two registrations -- never one trial
    ours = [{"id": "PMID 26330422", "pmid": "26330422", "nct": "NCT01623115"}]
    fh1 = {"label": "ODYSSEY FH I", "pmids": ["26330422"], "ncts": ["NCT01623115"]}
    fh2 = {"label": "ODYSSEY FH II", "pmids": ["26330422"], "ncts": ["NCT01709500"]}
    pac = {"label": "PACMAN-AMI", "pmids": ["26330422"], "ncts": ["NCT03067844"]}
    assert gt.one_trial_one_unit([fh1, fh2, pac], ours) == {}


def test_a_lane_trial_named_by_its_nct_is_found_in_our_pool_keyed_by_its_report():
    # captain, 5 Oct: RECOVERY (lane family NCT04381936) is pooled by us as 'PMID 33933206' -- the join missed it
    import g1_import_lanes as gil
    core = {"outcomes": [{"primary": True, "trials": [{"id": "PMID 99999961", "trial_family_id": "NCT99999961"},
                                                      {"id": "PMID 99999962", "trial_family_id": "PMID:99999962"}]}]}
    o = {"trials": [{"label": "RECOVERY-X", "family": "NCT99999961", "in_our_pool": None},
                    {"label": "BY-PMID", "family": "PMID 99999962", "in_our_pool": None},
                    {"label": "NOT-POOLED", "family": "NCT99999963", "in_our_pool": None},
                    {"label": "LANE-SAYS-NO", "family": "NCT99999961", "in_our_pool": False}]}
    gil.attach_pool_membership(o, core)
    t = {x["label"]: x for x in o["trials"]}
    assert t["RECOVERY-X"]["in_our_pool"] is True and t["RECOVERY-X"]["pool_join"]["pool_row"] == "PMID 99999961"
    assert t["BY-PMID"]["in_our_pool"] is True and t["NOT-POOLED"]["in_our_pool"] is False
    assert t["LANE-SAYS-NO"]["in_our_pool"] is False and t["LANE-SAYS-NO"]["pool_join_conflict"]["our_pool_row"]


def test_a_section_header_row_is_not_a_trial_unit():
    from kgap import k_gap
    t = {"header": [[{"text": "Studies", "rids": []}, {"text": "Year", "rids": []}, {"text": "NCT", "rids": []}]],
         "rows": [{"cells": ["GLP-1 RA vs. placebo", "", ""], "rids": [], "row_text": "GLP-1 RA vs. placebo"},
                  {"cells": ["ELIXA", "2015", "NCT01147250"], "rids": ["B24"], "row_text": "ELIXA | 2015 | NCT01147250"},
                  {"cells": ["LEADER", "2016", "NCT01179048"], "rids": [], "row_text": "LEADER | 2016 | NCT01179048"}]}
    assert [u["label"] for u in k_gap._units_from_table(t)] == ["ELIXA", "LEADER"]
