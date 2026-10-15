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


PRE_RECONCILE = "c715a5d59e5d2f246042776b1f16df0fcd34a3af"   # main before #81 landed: the noac page served 12


def test_PLANT_noac_served_review_reproduces_12_to_7():
    """Review 13 on the served noac page: 12 structurally eligible families, 7 with an included record.
    The control reads the page AS SERVED BEFORE THIS GATE (pinned by commit): read live, it retired itself the moment
    #81 landed and the served page became 7 (V15-B integration, 13 Oct) -- a control must be pinned, not live."""
    import subprocess
    out = subprocess.run(["git", "show", f"{PRE_RECONCILE}:docs/reviews/noac-vs-warfarin-af-stroke/review.json"],
                         cwd=ROOT, capture_output=True, check=True).stdout
    r = json.loads(out)
    nodes = copy.deepcopy(r["trial_families"])
    before = sum((f.get("eligibility") or {}).get("state") == "ELIGIBLE" for f in nodes)
    demoted = tf.reconcile_family_eligibility(r, nodes)
    after = sum((f.get("eligibility") or {}).get("state") == "ELIGIBLE" for f in nodes)
    assert (before, after, len(demoted)) == (12, 7, 5)


def test_the_served_noac_page_is_reconciled():
    """The landed state: the served page carries the reconciled count, and reconciling it again changes nothing."""
    r = json.load(open(os.path.join(ROOT, "docs", "reviews", "noac-vs-warfarin-af-stroke", "review.json"), encoding="utf-8"))
    nodes = copy.deepcopy(r["trial_families"])
    assert sum((f.get("eligibility") or {}).get("state") == "ELIGIBLE" for f in nodes) == 7
    assert tf.reconcile_family_eligibility(r, nodes) == []


def test_PLANT_no_record_level_screen_means_abstain_not_demote():
    """A review with no screening records gives the gate no evidence: absent data never demotes a family (the
    'missing field means ineligible' class; first draft of this gate demoted here)."""
    nodes = [_fam("NCTF", "ELIGIBLE", ["666"], ["NCTF"])]
    tf.reconcile_family_eligibility({"outcomes": []}, nodes)
    # never demoted (absent data is not ineligibility) -- but never left ELIGIBLE either: that half of this test asserted
    # the fail-open codex pr81-cap-r1 #1 named, and is rewritten to the requirement (typed abstention)
    assert nodes[0]["eligibility"].get("absence_code") != "NO_RECORD_ELIGIBLE_UNDER_PROTOCOL"
    assert nodes[0]["eligibility"].get("absence_code") == "RECONCILE_ABSTAINED"


def test_PLANT_no_record_level_screen_abstains_typed_never_eligible():
    """codex pr81-cap-r1 #1 (P1 FAIL-OPEN): with no record-level screen the gate returned [] and left {'state': 'ELIGIBLE'},
    so downstream read eligibility as established without any included own record. Abstaining is typed; the structural
    verdict is kept beside it, never deleted."""
    from harness import trial_family as tf
    nodes = [{"family_id": "NCT1", "eligibility": {"state": "ELIGIBLE", "span": {"fixture": "structural"}},
              "reports": [{"report_id": "111"}], "identity_basis": {"registry_ids": ["NCT1"]}, "aliases": {}}]
    out = tf.reconcile_family_eligibility({"screening": {"records": []}}, nodes)
    e = nodes[0]["eligibility"]
    assert e["state"] != "ELIGIBLE" and e["absence_code"] == "RECONCILE_ABSTAINED"
    assert e["structural"]["state"] == "ELIGIBLE" and out == ["NCT1"]
