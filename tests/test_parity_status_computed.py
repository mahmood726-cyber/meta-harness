"""Parity status is COMPUTED, and a CHANGED relation needs a recorded acknowledgement (ruling 2026-09-20).

The hand-written `status` in docs/parity.json describes the computed trial-set relation -- a second
source for one quantity -- so it went stale the moment the evidence moved (glp1: SOUL set aside, 8 -> 7,
'SUPERSET' vs OVERLAPPING; esketamine: 'IDENTICAL_SET' vs OVERLAPPING) and the whole topic refused to
build. Two defects with two fixes, and taking only the first trades one for the other:

  1. the served status is the computed relation; the hand word is rendered as `hand_status`, marked
     `hand_status_stale`, exactly as `our_k` / `hand_our_k_stale` already works -- a stale hand status
     NEVER refuses a build;
  2. a relation that differs from the one SERVED (the ratchet base) is a landing refusal until an
     acknowledgement names the topic, the old relation, the new relation, EVERY row that entered or left
     the pool, why, and who -- so a degradation against an external benchmark cannot pass silently.
"""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from harness import honest_ratchet, page, parity_relation

SLUG = "glp1-ra-mace-t2d"
HAND_ROW = {
    "slug": SLUG, "our_k": 8, "comparable_comparator_k": 7, "status": "SUPERSET",
    "reason": "8 pooled including SOUL (PMID 40162642, 2025) which postdates the comparator meta (k=7); "
              "the remaining gap ELIXA is a 4-point MACE (estimand) correctly declared-absent",
}
POOL_8 = ["PMID 31185157", "PMID 27633186", "PMID 27295427", "PMID 34215025", "PMID 31189511",
          "PMID 30291013", "PMID 28910237", "PMID 40162642"]


def _review(pool, shared_k, only_ours, only_theirs):
    return {
        "outcomes": [{"name": "3-point MACE", "primary": True, "result": {"k": len(pool)},
                      "trials": [{"id": t} for t in pool]}],
        "comparator": {"overlap": {"ours_k": len(pool), "theirs_k": 8, "shared_k": shared_k,
                                   "only_ours": only_ours, "only_theirs": only_theirs}},
    }


REVIEW_SERVED = _review(POOL_8, 7, ["SOUL"], ["ELIXA"])            # hand SUPERSET agrees
REVIEW_MOVED = _review(POOL_8[:-1], 6, ["EXSCEL"], ["ELIXA", "SOUL"])  # SOUL set aside: OVERLAPPING


# ---------------------------------------------------------------- 1. computed status never refuses
def test_PLANT_stale_hand_status_is_rendered_stale_not_refused():
    out = parity_relation.enrich(dict(HAND_ROW), REVIEW_MOVED, strict=True)   # strict must NOT raise
    assert out["parity_relation"]["relation"] == "OVERLAPPING"
    assert out["status"] == "OVERLAPPING", "the served status word is the computed relation"
    assert out["hand_status"] == "SUPERSET", "the hand word stays visible under its own name"
    assert out["hand_status_stale"] is True
    assert out["our_k"] == 7 and out["hand_our_k"] == 8 and out["hand_our_k_stale"] is True


def test_hand_status_that_agrees_is_not_stale():
    out = parity_relation.enrich(dict(HAND_ROW), REVIEW_SERVED, strict=True)
    assert out["status"] == "SUPERSET" and out["hand_status"] == "SUPERSET"
    assert out["hand_status_stale"] is False


def test_PLANT_page_names_the_stale_hand_status():
    stale = parity_relation.enrich(dict(HAND_ROW), REVIEW_MOVED)
    html = page._reproduction({"reproduction": {"parity": stale, "from_cache": True}}, False)
    assert "OVERLAPPING" in html
    assert "hand-written status" in html and "SUPERSET" in html and "stale" in html.lower(), \
        "the page must say the hand word is stale and what it said, never render it as the status"
    fresh = parity_relation.enrich(dict(HAND_ROW), REVIEW_SERVED)
    assert "stale" not in page._reproduction({"reproduction": {"parity": fresh, "from_cache": True}}, False).lower()


# ---------------------------------------------------------------- 2. a changed relation needs an ack
def _served_json(row, review):
    enriched = parity_relation.enrich(dict(row), review, strict=False)
    return {"outcomes": review["outcomes"], "reproduction": {"parity": enriched}}


BASE_JSON = _served_json(HAND_ROW, REVIEW_SERVED)      # served: SUPERSET, k=8
NEW_JSON = _served_json(HAND_ROW, REVIEW_MOVED)        # rebuilt: OVERLAPPING, k=7, SOUL left the pool
GOOD_ACK = {
    "slug": SLUG, "old_relation": "SUPERSET", "new_relation": "OVERLAPPING",
    "left_pool": ["PMID 40162642"], "entered_pool": [],
    "reason": "SOUL's hand row abstained (ENDPOINT_UNBOUND); the comparator now holds a trial we do not",
    "by": "reviewer M.A.", "when_utc": "2026-09-20T18:00:00Z",
}


def test_PLANT_changed_relation_without_acknowledgement_refuses():
    reasons = honest_ratchet.compare_parity(BASE_JSON, NEW_JSON, {"parity_acknowledgements": []}, SLUG)
    assert len(reasons) == 1
    r = reasons[0]
    assert "SUPERSET" in r and "OVERLAPPING" in r and "PMID 40162642" in r and "not acknowledged" in r


def test_exact_acknowledgement_admits_the_change():
    acks = {"parity_acknowledgements": [GOOD_ACK]}
    assert honest_ratchet.compare_parity(BASE_JSON, NEW_JSON, acks, SLUG) == []


@pytest.mark.parametrize("bad", [
    {"old_relation": "IDENTICAL_SET"},           # wrong old relation
    {"new_relation": "SUBSET"},                  # wrong new relation
    {"left_pool": []},                           # the row that moved is not named
    {"left_pool": ["PMID 40162642", "PMID 27295427"]},  # names a row that did not move
    {"entered_pool": ["PMID 99999999"]},
    {"by": ""},                                  # unsigned
    {"reason": ""},
    {"slug": "other-topic"},
])
def test_PLANT_inexact_or_unsigned_acknowledgement_does_not_admit(bad):
    acks = {"parity_acknowledgements": [dict(GOOD_ACK, **bad)]}
    assert honest_ratchet.compare_parity(BASE_JSON, NEW_JSON, acks, SLUG) != []


def test_unchanged_relation_needs_nothing():
    assert honest_ratchet.compare_parity(BASE_JSON, BASE_JSON, {}, SLUG) == []


def test_new_topic_with_no_served_relation_needs_nothing():
    assert honest_ratchet.compare_parity(None, NEW_JSON, {}, SLUG) == []


# ---------------------------------------------------------------- 3. the ratchet limb covers review.json
def _git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True, env=env)


def test_PLANT_ratchet_check_refuses_unacknowledged_parity_change_in_working_tree():
    with tempfile.TemporaryDirectory(prefix="parity-ratchet-test-", ignore_cleanup_errors=True) as raw:
        repo = Path(raw) / "repo"
        (repo / "docs" / "reviews" / SLUG).mkdir(parents=True)
        _git(repo, "init")
        _git(repo, "config", "user.email", "test@example.test")
        _git(repo, "config", "user.name", "Test User")
        ack_path = repo / "docs" / "ratchet_acknowledgements.json"
        ack_path.write_text(json.dumps({"_doc": "test", "acknowledgements": [], "parity_acknowledgements": []}) + "\n",
                            encoding="utf-8")
        (repo / "docs" / "index.html").write_text("<html><body>index</body></html>", encoding="utf-8")
        rj = repo / "docs" / "reviews" / SLUG / "review.json"
        rj.write_text(json.dumps(BASE_JSON), encoding="utf-8")
        (repo / "docs" / "reviews" / SLUG / "index.html").write_text("<html><body>page</body></html>", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-m", "base")

        rj.write_text(json.dumps(NEW_JSON), encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is False
        assert any("parity relation" in r and "SUPERSET" in r and "OVERLAPPING" in r for r in reasons), reasons

        ack_path.write_text(json.dumps({"_doc": "test", "acknowledgements": [],
                                        "parity_acknowledgements": [GOOD_ACK]}) + "\n", encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        # the parity change is acknowledged; the SAME pool change also moved the result (k 8 -> 7), and the
        # result-change ratchet refuses that on its own until a notice names it -- two claims, two acknowledgements
        assert ok is False and all("result changed" in r for r in reasons), reasons
        (repo / "docs" / "result_changes.json").write_text(json.dumps({"_doc": "test", "notices": [{
            "slug": SLUG, "outcome": "3-point MACE", "before": {"k": 8, "estimate": None, "ci_low": None, "ci_high": None},
            "after": {"k": 7, "estimate": None, "ci_low": None, "ci_high": None}, "left_pool": ["PMID 40162642"],
            "entered_pool": [], "reason": "SOUL set aside", "by": "reviewer M.A.", "when_utc": "2026-09-20T18:00:00Z"}]}) + "\n",
            encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is True, reasons
