"""Family-eligibility reconcile gate (reviews 7, 12, 13, 27): a family is ELIGIBLE only when its structural screen says so
AND the protocol's record-level screen INCLUDED at least one of its own records."""
from __future__ import annotations

import copy
import json
import os

from harness import trial_family as tf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fam(fid, state, reports, regs=()):
    return {"family_id": fid, "eligibility": {"state": state, "span": {"x": 1}} if state != "UNKNOWN" else
            {"state": "UNKNOWN", "absence_code": "NOT_HELD"},
            "reports": [{"report_id": r, "role": "PRIMARY"} for r in reports],
            "identity_basis": {"registry_ids": list(regs)}, "aliases": {"registry_ids": list(regs)}}


def test_PLANT_structural_eligible_with_no_included_record_is_demoted():
    nodes = [_fam("NCTA", "ELIGIBLE", ["111"], ["NCTA"]),          # its report was screened OUT
             _fam("NCTB", "ELIGIBLE", ["222"], ["NCTB"]),          # its report was screened IN
             _fam("NCTC", "UNKNOWN", ["333"], ["NCTC"]),           # never promoted by this gate
             _fam("NCTD", "INELIGIBLE", ["444"], ["NCTD"])]
    review = {"screening": {"records": [{"id": "111", "decision": "exclude"}, {"id": "222", "decision": "include"},
                                        {"id": "333", "decision": "include"}, {"id": "444", "decision": "include"}]}}
    assert tf.reconcile_family_eligibility(review, nodes) == ["NCTA"]
    a, b, c, d = nodes
    assert a["eligibility"]["state"] == "UNKNOWN" and a["eligibility"]["absence_code"] == "NO_RECORD_ELIGIBLE_UNDER_PROTOCOL"
    assert a["eligibility"]["structural"]["state"] == "ELIGIBLE"            # kept for audit, never deleted
    assert b["eligibility"]["state"] == "ELIGIBLE"
    assert c["eligibility"]["state"] == "UNKNOWN" and d["eligibility"]["state"] == "INELIGIBLE"


def test_a_registration_record_counts_as_the_familys_own_record():
    nodes = [_fam("NCTE", "ELIGIBLE", ["555"], ["NCTE"])]
    review = {"screening": {"records": [{"id": "555", "decision": "exclude"}, {"id": "NCTE", "decision": "include"}]}}
    assert tf.reconcile_family_eligibility(review, nodes) == []


def test_PLANT_noac_served_review_reproduces_12_to_7():
    """Review 13 on the served noac page: 12 structurally eligible families, 7 with an included record."""
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "noac-vs-warfarin-af-stroke", "review.json"), encoding="utf-8"))
    nodes = copy.deepcopy(r["trial_families"])
    before = sum((f.get("eligibility") or {}).get("state") == "ELIGIBLE" for f in nodes)
    demoted = tf.reconcile_family_eligibility(r, nodes)
    after = sum((f.get("eligibility") or {}).get("state") == "ELIGIBLE" for f in nodes)
    assert (before, after, len(demoted)) == (12, 7, 5)


def test_PLANT_no_record_level_screen_means_abstain_not_demote():
    """A review with no screening records gives the gate no evidence: absent data never demotes a family (the
    'missing field means ineligible' class; first draft of this gate demoted here)."""
    nodes = [_fam("NCTF", "ELIGIBLE", ["666"], ["NCTF"])]
    assert tf.reconcile_family_eligibility({"outcomes": []}, nodes) == []
    assert nodes[0]["eligibility"]["state"] == "ELIGIBLE"
