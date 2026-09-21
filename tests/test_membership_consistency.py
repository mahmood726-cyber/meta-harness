import json
import os
import subprocess

from harness import membership

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "aa8ed28a"


def _git_json(path):
    data = subprocess.check_output(
        ["git", "show", f"{BASE}:{path}"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )
    return json.loads(data)


def _prefix_review_and_parity():
    review = _git_json("docs/reviews/esketamine-trd-madrs/review.json")
    parity_rows = _git_json("docs/parity.json")
    parity = next(row for row in parity_rows if row.get("slug") == "esketamine-trd-madrs")
    return review, parity


def test_prefix_esketamine_plant_fires_three_membership_violations():
    review, parity = _prefix_review_and_parity()
    violations = membership.consistency_violations(review, parity)
    assert [v["code"] for v in violations] == [
        "INTEGRITY_COUNT_MISMATCH",
        "ROB_JOIN_MISS",
        "PARITY_TEXT_STALE",
    ]
    assert violations[0]["detail"] == "2 vs 4"
    assert violations[1]["detail"] == "2 rated-and-pooled trials invisible to levels"
    assert "TRANSFORM-1" in violations[2]["conflicts"][0]["sentence"]


def test_rebuilt_esketamine_membership_is_consistent_and_parity_row_current():
    review = json.load(open(
        os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "review.json"),
        encoding="utf-8",
    ))
    assert membership.consistency_violations(review) == []
    parity = (review.get("reproduction") or {}).get("parity") or {}
    assert parity.get("membership_status") is None
    # the parity row is CURRENT: its served our_k is the live primary k (derived, never the hand snapshot), and its
    # status word is the computed relation; the hand words, when stale, are shown as stale beside it. (Until
    # 2026-09-20 this asserted our_k == 4; k moved to 3 when TRANSFORM-1 was set aside, with a notice.)
    prim = next(o for o in review["outcomes"] if o.get("primary"))
    assert parity.get("our_k") == prim["result"]["k"] == len(prim["trials"])
    assert parity.get("status") == (parity.get("parity_relation") or {}).get("relation")
    if parity.get("hand_our_k") is not None and parity["hand_our_k"] != parity["our_k"]:
        assert parity.get("hand_our_k_stale") is True
    assert parity.get("comparable_comparator_k") == 4
    # the relation is COMPUTED from the live pool (IDENTICAL_SET while all four were pooled; OVERLAPPING since
    # TRANSFORM-1 was set aside, acknowledged in docs/ratchet_acknowledgements.json parity_acknowledgements)
    from harness import parity_relation
    hand_row = {k: parity.get(k) for k in ("slug", "our_k", "comparable_comparator_k", "status", "reason")}
    hand_row["status"] = parity.get("hand_status", parity.get("status"))
    assert (parity.get("parity_relation") or {}).get("relation") == parity_relation.compute(hand_row, review)["relation"]
    html = open(
        os.path.join(ROOT, "docs", "reviews", "esketamine-trd-madrs", "index.html"),
        encoding="utf-8",
    ).read()
    assert "STALE_VS_MEMBERSHIP" not in html
    assert "Comparator panel" in html
    assert "Trial set NOT ENUMERATED; overlap unknown." in html
    assert "Our pooled <em>k</em> = <strong>4</strong> vs the comparator <em>k</em> = <strong>4</strong>" not in html
    assert "We pool 2" not in html
    assert "The 2 gap trials (TRANSFORM-1 and the phase-2 dose-finding)" not in html


def test_synthetic_agreeing_membership_control_passes():
    review = {
        "outcomes": [{
            "name": "Clean outcome",
            "primary": True,
            "trials": [{"id": "PMID 12345678", "label": "CLEAN"}],
            "declared_absent_trials": [],
            "result": {"k": 1},
            "membership": {
                "pooled": ["PMID 12345678"],
                "declared_absent": [],
                "refused": [],
                "screened_in_not_pooled": [],
                "input_set_version": "synthetic",
            },
        }],
        "integrity": {"n_pooled": 1},
        "rob2": {"trials": {"12345678": {"overall": "low"}}},
        "rob_sensitivity": {"levels": {"PMID 12345678": "low"}, "n_rob_rated": 1},
        "reproduction": {"parity": {"our_k": 1, "reason": "Same-scope comparator agreement."}},
    }
    assert membership.consistency_violations(review) == []
