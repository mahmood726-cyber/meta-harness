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


def test_pre_fix_audit_never_saw_them():
    # the committed audit at the branch base had none of this topic's exclusions (pre-fix firing)
    raw = subprocess.check_output(["git", "show", "origin/acq/k-gap:outputs/k_gap/exclusion_audit.json"], cwd=ROOT)
    assert not [r for r in json.loads(raw)["rows"] if r["slug"] == CPAF]


def _rec(title, abstract, pubtypes=("Journal Article", "Randomized Controlled Trial")):
    return {"id": "1", "id_type": "pmid", "title": title, "abstract": abstract, "pubtypes": list(pubtypes)}


CFG = json.load(open(os.path.join(ROOT, "topics", CPAF + ".json"), encoding="utf-8"))


def test_substudy_of_an_rct_is_a_screener_error_and_a_protocol_paper_is_not():
    body = ("BACKGROUND: x. METHODS: 300 patients undergoing cardiac surgery in a multicenter, double-blind, randomized "
            "trial received colchicine or placebo. RESULTS: postoperative atrial fibrillation fell.")
    cls, sub, _ = audit.classify(_rec("Colchicine and postoperative atrial fibrillation: the X substudy", body), CFG)
    assert (cls, sub.split(":")[0]) == ("SCREENER_ERROR", "SECONDARY_REPORT_OF_RCT")
    cls, sub, _ = audit.classify(_rec("Rationale and design of the X trial of colchicine after cardiac surgery", body), CFG)
    assert (cls, sub.split(":")[0]) == ("TRUE_SCOPE_DIFFERENCE", "DESIGN_OR_PROTOCOL_PAPER_STATED")
