"""G1 colchicine-postop-af: the exclusion audit gates OUR OWN screen's exclusions of comparator trials, not only seeded
ones (all 6 of this topic's sat SCREENED_OUT_UNAUDITED), and an X1 that came from a TITLE marker on an RCT-typed record is
told apart: a design/protocol paper is a true scope difference, a substudy/secondary/post-hoc results report of a
randomised trial is a screener error (the COPPS POAF substudy, PMID 22090167)."""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

import k_gap_exclusion_audit as audit  # noqa: E402

CPAF = "colchicine-postop-af"


def _rows():
    return {r["pmid"]: r for r in json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.json"),
                                                 encoding="utf-8"))["rows"] if r["slug"] == CPAF}


def test_every_colchicine_exclusion_is_audited_with_its_class():
    rows = _rows()
    want = {"29237033": ("TRUE_SCOPE_DIFFERENCE", "PROTOCOL_EXCLUDES_POPULATION:'lung resection'"),
            "23040570": ("TRUE_SCOPE_DIFFERENCE", "PROTOCOL_EXCLUDES_POPULATION:'pulmonary vein'"),
            "24508207": ("TRUE_SCOPE_DIFFERENCE", "PROTOCOL_EXCLUDES_POPULATION:'pulmonary vein'"),
            "27502857": ("TRUE_SCOPE_DIFFERENCE", "OPEN_LABEL_STATED (protocol requires double-blind)"),
            "27223641": ("INSUFFICIENT_RECORD", "BLINDING_NOT_STATED"),
            "22090167": ("SCREENER_ERROR", "SECONDARY_REPORT_OF_RCT:'substudy' (route to its trial family)")}
    assert {p: (rows[p]["class"], rows[p]["subclass"]) for p in want} == want


def test_pre_fix_audit_missed_the_substudy_screener_error():
    # pre-fix firing: the base audit (acq/k-gap, which since audits in-screen exclusions too) left the COPPS POAF
    # substudy a thin record -- the screener error it is went unseen
    raw = subprocess.check_output(["git", "show", "origin/acq/k-gap:outputs/k_gap/exclusion_audit.json"], cwd=ROOT)
    base = {r["pmid"]: r for r in json.loads(raw)["rows"] if r["slug"] == CPAF}
    assert (base["22090167"]["class"], base["22090167"]["subclass"]) == ("INSUFFICIENT_RECORD", "DESIGN_NOT_ESTABLISHED_BY_RECORD")


def _rec(title, abstract, pubtypes=("Journal Article", "Randomized Controlled Trial")):
    return {"id": "1", "id_type": "pmid", "title": title, "abstract": abstract, "pubtypes": list(pubtypes)}


CFG = json.load(open(os.path.join(ROOT, "topics", CPAF + ".json"), encoding="utf-8"))


def test_an_open_design_self_description_beats_a_cited_placebo_trial():
    # Zarpelon's PMC full text: 'This is a prospective, randomized, open, single-center clinical assay' ... and, citing
    # COPPS in its sample-size paragraph, 'a randomized, placebo-controlled study' -- the ruleset alone would INCLUDE it
    text = ("Methods Study Design and Participants This is a prospective, randomized, open, single-center clinical assay "
            "of patients undergoing myocardial revascularization surgery; the control group was not receiving the study "
            "medication. The AF rate was estimated based on the results of a randomized, placebo-controlled study of "
            "colchicine after cardiac surgery.")
    cls, sub, _ = audit.classify(_rec("Colchicine to Reduce Atrial Fibrillation after Myocardial Revascularization", text,
                                      ("Journal Article", "Randomized Controlled Trial")), CFG)
    assert (cls, sub.split(" (")[0]) == ("TRUE_SCOPE_DIFFERENCE", "OPEN_DESIGN_STATED_FOR_THIS_STUDY")
    assert not audit.OPEN_DESIGN_SELF.search("The trial was double-blind, followed by an open-label extension.")
    assert not audit.OPEN_DESIGN_SELF.search("patients undergoing open heart surgery were randomized")


def test_the_committed_full_text_verdict_reaches_the_tracker():
    import g1_tracker as gt
    rows = {r["pmid"]: r for r in json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_fulltext.json"),
                                                 encoding="utf-8"))["rows"] if r["slug"] == CPAF}
    assert rows["27223641"]["class_after"] == "TRUE_SCOPE_DIFFERENCE" and rows["27223641"]["fulltext"] == "PMC_OA"
    cls, sub = gt.exclusion_audit_class(CPAF, "27223641")
    assert cls == "TRUE_SCOPE_DIFFERENCE" and "full text: REGEX_ON_FULLTEXT" in sub


def test_substudy_of_an_rct_is_a_screener_error_and_a_protocol_paper_is_not():
    body = ("BACKGROUND: x. METHODS: 300 patients undergoing cardiac surgery in a multicenter, double-blind, randomized "
            "trial received colchicine or placebo. RESULTS: postoperative atrial fibrillation fell.")
    cls, sub, _ = audit.classify(_rec("Colchicine and postoperative atrial fibrillation: the X substudy", body), CFG)
    assert (cls, sub.split(":")[0]) == ("SCREENER_ERROR", "SECONDARY_REPORT_OF_RCT")
    cls, sub, _ = audit.classify(_rec("Rationale and design of the X trial of colchicine after cardiac surgery", body), CFG)
    assert (cls, sub.split(":")[0]) == ("INSUFFICIENT_RECORD", "DESIGN_PAPER_ONLY")      # the trial stays eligible


def test_a_full_text_span_names_zarpelon_only_when_verified_against_the_held_body(monkeypatch):
    # acq/k-gap 8de6953 requires a verbatim span for every named scope difference; Zarpelon's open design is stated only
    # in its PMC full text, so the span is the FULL TEXT's words, checked against the body whose sha256 was recorded
    import g1_tracker as gt
    sp = gt.exclusion_audit_span(CPAF, "27223641")
    assert sp["field"] == "fulltext" and sp["text"].startswith("Methods Study Design and Participants This is a prospective, randomized, open")
    assert sp["fulltext_sha256"].startswith("25981c8e")
    if gt.held_fulltext("27223641", sp["fulltext_sha256"], sp["fulltext_source"], CPAF) is not None:      # a clone holding the body verifies it
        assert gt.span_is_verbatim(CPAF, "27223641", sp)
    assert not gt.span_is_verbatim(CPAF, "27223641", dict(sp, fulltext_sha256="0" * 64))    # a different body: refused
    monkeypatch.setattr(gt, "held_fulltext", lambda *a, **k: None)                     # no body here: fails closed
    assert not gt.span_is_verbatim(CPAF, "27223641", sp)


def test_pre_merge_base_left_zarpelon_an_open_gap():
    base = json.loads(subprocess.check_output(["git", "show", f"origin/acq/k-gap:outputs/k_gap/g1/{CPAF}.json"], cwd=ROOT))
    assert "Zarpelon [20]" in base["open_gaps"]


def test_lane_named_exclusions_are_read_from_the_lanes_pinned_file():
    # the local tracker copy has SOLOIST-WHF already demoted; the audit must audit what the LANE named, so regenerating it
    # reproduces the committed row (it vanished when read from the local copy)
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "sglt2-hfref-hosp-cvdeath.json"), encoding="utf-8"))
    # a control pinned to an IMMUTABLE lane version (g1/tocilizumab b1c971d1, which named SOLOIST-WHF), not the live
    # pin: whatever the local copy says (here emptied, as a demotion leaves it), the naming comes from the pinned file
    pinned = dict(o["lane_source"], commit="b1c971d17a10245f234096372f2df97005b0ec89",
                  sha256="deca8615fab93ee8c0846c22a80f7fc51a65ddd264368a0f45834fdc7c96dd7f")
    o = dict(o, lane_source=pinned, named_differences=[])
    assert any(d.get("pmid") == "33200892" for d in audit.lane_named_differences(o))
    rows = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.json"), encoding="utf-8"))["rows"]
    assert any(r["slug"] == "sglt2-hfref-hosp-cvdeath" and r["pmid"] == "33200892" for r in rows)
    import pytest
    with pytest.raises(audit.LaneSourceUnreadable):
        audit.lane_named_differences(dict(o, lane_source=dict(o["lane_source"], sha256="0" * 64)))


# --- plants from the cross-vendor adversarial review NR-C21 (Codex; C:/mh-lanes/nr/codex/CALL_LOG.jsonl, artefact
# F:/mh-nr101-codex/c21-g1-scope-spans/last_message.txt); each failed against the code before its fix
_BODY = ("METHODS: 300 patients undergoing cardiac surgery in a multicenter, double-blind trial were randomized to "
         "colchicine or placebo. RESULTS: AF fell.")


def test_c21_a_protocol_paper_titled_substudy_is_a_protocol_paper_not_a_screener_error():
    cls, sub, d = audit.classify(_rec("Substudy design and protocol of a randomized trial of colchicine after cardiac surgery",
                                      _BODY), CFG)
    # a protocol paper is not a screener error -- and it never removes the TRIAL: the trial stays eligible
    assert (cls, sub.split(":")[0]) == ("INSUFFICIENT_RECORD", "DESIGN_PAPER_ONLY")


def test_c21_a_non_randomised_substudy_is_not_a_randomised_report():
    cls, sub, _ = audit.classify(_rec("Non-randomised substudy of a randomized trial of colchicine after cardiac surgery",
                                      "METHODS: In the parent trial, patients were randomized to colchicine or placebo; "
                                      "this substudy was non-randomized. RESULTS: x."), CFG)
    assert cls != "SCREENER_ERROR"


def test_c21_a_post_hoc_per_protocol_report_is_still_a_screener_error():
    cls, sub, _ = audit.classify(_rec("Post hoc per-protocol analysis of a randomized trial of colchicine after cardiac "
                                      "surgery", _BODY), CFG)
    assert (cls, sub.split(":")[0]) == ("SCREENER_ERROR", "SECONDARY_REPORT_OF_RCT")


def test_c21_a_background_open_study_is_not_this_studys_design():
    assert not audit.OPEN.search("Unlike the earlier randomized, open, single-center study, we used placebo.")
    assert audit.OPEN_DESIGN_SELF.search("This is a prospective, randomized, open, single-center clinical assay")


def test_c21_a_control_group_given_dummy_tablets_is_a_placebo_control():
    assert not audit.OTHER_COMP.search("the control group not receiving the study medication received identical dummy tablets.")
    assert audit.OTHER_COMP.search("the control group, not receiving the study medication, was followed as usual.")


def test_c21_the_full_text_pass_reads_the_whole_audit_population():
    import k_gap_exclusion_fulltext as eft
    assert ("colchicine-postop-af", "27223641") in {(i["slug"], i["pmid"]) for i in eft.items(False)}


def test_c21_a_pinned_lane_file_for_another_topic_is_refused():
    import pytest
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "sglt2-hfref-hosp-cvdeath.json"), encoding="utf-8"))
    with pytest.raises(audit.LaneSourceUnreadable):
        audit.lane_named_differences(dict(o, slug="tocilizumab-covid19-mortality"))


def test_a_design_paper_never_removes_its_trial_from_the_denominator():
    # spironolactone 25678098: 'Rationale and design of the ARTS-HF ...' -- the report is a design paper, the TRIAL
    # (ARTS-HF) has a results report we do not hold; naming it out of scope would shrink the denominator
    cls, sub, _ = audit.classify(_rec("Rationale and design of a randomized trial of colchicine after cardiac surgery", _BODY), CFG)
    assert cls != "TRUE_SCOPE_DIFFERENCE"
