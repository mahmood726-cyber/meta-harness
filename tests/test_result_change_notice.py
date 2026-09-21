"""A served pooled result that changes is a claim about the previous claim (Mahmood, 2026-09-20: esketamine
k 4 -> 3, MD -3.34 (-6.07 to -0.62) -> -3.10 (-7.33 to 1.13) -- the interval now includes zero; a review that
reported a difference no longer does, and that page cannot quietly re-render with a new number).

Plants: (1) a rebuilt result that differs from the served one without an exact notice refuses the landing;
(2) an exact notice admits it; (3) an inexact or unsigned notice does not; (4) the page renders the notice, and
names a reversal of significance as a withdrawal of the conclusion; (5) an outcome whose estimate disappears
(k -> 0) is a change that needs a notice, not a vanishing."""
import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

from harness import honest_ratchet, page, result_changes

SLUG = "esketamine-trd-madrs"
OUT = "Observed-case Day-28 raw change-score MADRS MD"
BEFORE = {"k": 4, "estimate": -3.3445, "ci_low": -6.0701, "ci_high": -0.6189}
AFTER = {"k": 3, "estimate": -3.1004, "ci_low": -7.3323, "ci_high": 1.1315}
POOL_BEFORE = ["PMID 37025256", "PMID 31109201", "NCT02422186", "NCT02417064"]


def _review(result, pool, name=OUT, scale="MD"):
    return {"slug": SLUG, "outcomes": [{"name": name, "primary": True, "estimand": scale, "result": dict(result, scale=scale),
                                       "trials": [{"id": t} for t in pool]}]}


BASE = _review(BEFORE, POOL_BEFORE)
NEW = _review(AFTER, POOL_BEFORE[:-1])
GOOD = {"slug": SLUG, "outcome": OUT, "before": BEFORE, "after": AFTER, "left_pool": ["NCT02417064"], "entered_pool": [],
        "reason": "NCT02417064's hand-transcribed arm values are not located in the held record (KNOWN_REPORTED_NOT_YET_EXTRACTED); "
                  "the row is set aside for adjudication and the pool re-pooled without it",
        "by": "reviewer M.A.", "when_utc": "2026-09-20T23:00:00Z"}


def test_PLANT_changed_result_without_a_notice_refuses():
    reasons = honest_ratchet.compare_results(BASE, NEW, {"notices": []}, SLUG)
    assert len(reasons) == 1
    r = reasons[0]
    assert "NCT02417064" in r and "-3.3445" in r and "-3.1004" in r and "not acknowledged" in r
    assert "includes the null" in r, "a reversal of significance must be named as such in the refusal"


def test_exact_notice_admits():
    assert honest_ratchet.compare_results(BASE, NEW, {"notices": [GOOD]}, SLUG) == []


@pytest.mark.parametrize("bad", [
    {"before": dict(BEFORE, estimate=-3.3)},        # not the served number
    {"after": dict(AFTER, k=4)},
    {"left_pool": []},                               # the row that left is not named
    {"left_pool": ["NCT02417064", "NCT02422186"]},   # names a row that stayed
    {"by": ""}, {"reason": ""}, {"outcome": "other outcome"},
])
def test_PLANT_inexact_or_unsigned_notice_does_not_admit(bad):
    assert honest_ratchet.compare_results(BASE, NEW, {"notices": [dict(GOOD, **bad)]}, SLUG) != []


def test_unchanged_result_needs_nothing():
    assert honest_ratchet.compare_results(BASE, BASE, {}, SLUG) == []


def test_PLANT_an_estimate_that_disappears_is_a_change_not_a_vanishing():
    gone = _review({"k": None, "estimate": None, "ci_low": None, "ci_high": None}, [])
    reasons = honest_ratchet.compare_results(BASE, gone, {}, SLUG)
    assert len(reasons) == 1 and "no longer has a pooled estimate" in reasons[0]


def test_conclusion_change_is_named():
    assert "includes the null" in result_changes.conclusion_changed(BEFORE, AFTER, "MD")
    assert result_changes.conclusion_changed({"k": 6, "estimate": 0.95, "ci_low": 0.82, "ci_high": 1.10},
                                             {"k": 4, "estimate": 0.92, "ci_low": 0.72, "ci_high": 1.18}, "HR") is None
    assert "no longer has a pooled estimate" in result_changes.conclusion_changed(BEFORE, {"k": None}, "MD")


def test_PLANT_page_renders_the_notice_and_names_the_withdrawn_conclusion():
    r = dict(NEW, reproduction={"from_cache": True, "result_changes": [dict(GOOD, conclusion_changed=result_changes.conclusion_changed(BEFORE, AFTER, "MD"))]})
    html = page._reproduction(r, False)
    assert "Result changed" in html and "-3.34" in html and "-3.1" in html and "NCT02417064" in html
    assert "withdrawn" in html.lower() and "includes the null" in html


def _git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True, env=env)


def test_PLANT_ratchet_check_refuses_an_unnoticed_result_change_in_the_working_tree():
    with tempfile.TemporaryDirectory(prefix="result-change-test-", ignore_cleanup_errors=True) as raw:
        repo = Path(raw) / "repo"
        (repo / "docs" / "reviews" / SLUG).mkdir(parents=True)
        _git(repo, "init")
        _git(repo, "config", "user.email", "test@example.test")
        _git(repo, "config", "user.name", "Test User")
        (repo / "docs" / "ratchet_acknowledgements.json").write_text(json.dumps({"_doc": "t", "acknowledgements": []}) + "\n", encoding="utf-8")
        (repo / "docs" / "index.html").write_text("<html><body>index</body></html>", encoding="utf-8")
        rj = repo / "docs" / "reviews" / SLUG / "review.json"
        rj.write_text(json.dumps(BASE), encoding="utf-8")
        (repo / "docs" / "reviews" / SLUG / "index.html").write_text("<html><body>page</body></html>", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-m", "base")
        rj.write_text(json.dumps(NEW), encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is False and any("result changed" in x for x in reasons), reasons
        (repo / "docs" / "result_changes.json").write_text(json.dumps({"_doc": "t", "notices": [GOOD]}) + "\n", encoding="utf-8")
        ok, reasons = honest_ratchet.check(repo, "HEAD")
        assert ok is True, reasons


# ---------------------------------------------------------------- reviewer countersignature: an act on bytes
def _block(notice):
    html = page.result_change_block(notice)
    return html[:html.rfind("<p class='muted'>Reviewer countersignature")]


WITHDRAWN = dict(GOOD, conclusion_changed=result_changes.conclusion_changed(BEFORE, AFTER, "MD"))
PRESERVED = {"slug": "omega3-cardiovascular-events", "outcome": "Major vascular events / MACE",
             "before": {"k": 6, "estimate": 0.9505, "ci_low": 0.8207, "ci_high": 1.1009},
             "after": {"k": 4, "estimate": 0.9202, "ci_low": 0.7153, "ci_high": 1.1839},
             "left_pool": ["PMID 21115589", "PMID 22686415"], "entered_pool": [], "reason": "two rows set aside",
             "by": "lane", "when_utc": "2026-09-20T23:30:00Z", "conclusion_changed": None}


def _signed(notice, state, **extra):
    sig = {"state": state, "by": "Mahmood", "when_utc": "2026-09-21T09:00:00Z",
           "rendered_sha256": result_changes.rendered_sha256(_block(notice)),
           "how_it_reached_the_reviewer": "read the rendered block"}
    sig.update(extra)
    return dict(notice, reviewer_countersignature=sig)


def test_PLANT_open_or_missing_countersignature_holds_the_page():
    assert "not been put in front" in result_changes.signature_problem(WITHDRAWN, _block(WITHDRAWN))
    opened = dict(WITHDRAWN, reviewer_countersignature={"state": "OPEN"})
    assert "OPEN" in result_changes.signature_problem(opened, _block(opened))


def test_PLANT_agreed_in_advance_is_not_a_state():
    for bogus in ("AGREED_IN_ADVANCE", "AUTHORISED_IN_PRINCIPLE", "APPROVED"):
        n = dict(WITHDRAWN, reviewer_countersignature={"state": bogus, "by": "Mahmood", "when_utc": "2026-09-21T09:00:00Z",
                                                        "rendered_sha256": result_changes.rendered_sha256(_block(WITHDRAWN))})
        assert "not a recognised act" in result_changes.signature_problem(n, _block(n))


def test_PLANT_signature_binds_the_rendered_bytes():
    signed = _signed(WITHDRAWN, "SEEN_AND_SIGNED")
    assert result_changes.signature_problem(signed, _block(signed)) is None
    # the numbers change after the signature: the signature names a rendering that is not this one
    moved = dict(signed, after=dict(AFTER, estimate=-2.9))
    assert "sha256 mismatch" in result_changes.signature_problem(moved, _block(moved))


def test_PLANT_withdrawn_conclusion_refuses_a_batch_signature_but_a_preserved_change_accepts_one():
    batch = _signed(WITHDRAWN, "BATCH_SEEN_AND_SIGNED", batch_id="batch-2026-09-21")
    assert "per-notice signature" in result_changes.signature_problem(batch, _block(batch))
    ok = _signed(PRESERVED, "BATCH_SEEN_AND_SIGNED", batch_id="batch-2026-09-21")
    assert result_changes.signature_problem(ok, _block(ok)) is None
    nobatch = _signed(PRESERVED, "BATCH_SEEN_AND_SIGNED")
    assert "batch_id" in result_changes.signature_problem(nobatch, _block(nobatch))


def test_PLANT_gate_holds_a_page_with_an_unsigned_notice(tmp_path, monkeypatch):
    from harness import gate
    root = tmp_path / "root"
    d = root / "docs" / "reviews" / "esketamine-trd-madrs"
    d.mkdir(parents=True)
    monkeypatch.setattr(result_changes, "ROOT", str(root))

    def _file(notices):   # the committed file the page's embedded notices must equal
        (root / "docs" / "result_changes.json").write_text(json.dumps({"_doc": "t", "notices": notices}) + chr(10), encoding="utf-8")

    opened = dict(WITHDRAWN, reviewer_countersignature={"state": "OPEN"})
    _file([opened])
    rev = dict(NEW, reproduction={"result_changes": [opened]})
    (d / "review.json").write_text(json.dumps(rev), encoding="utf-8")
    reasons = gate.check_result_change_countersigned(str(d))
    assert reasons == [r for r in reasons if "OPEN" in r] and reasons
    signed = _signed(WITHDRAWN, "SEEN_AND_SIGNED")
    _file([signed])
    rev["reproduction"]["result_changes"] = [signed]
    (d / "review.json").write_text(json.dumps(rev), encoding="utf-8")
    assert gate.check_result_change_countersigned(str(d)) == []


def test_page_renders_the_signature_state():
    html = page.result_change_block(dict(WITHDRAWN, reviewer_countersignature={"state": "OPEN"}))
    assert "OPEN" in html and "not yet been seen and signed" in html
    html = page.result_change_block(_signed(WITHDRAWN, "SEEN_AND_SIGNED"))
    assert "SEEN_AND_SIGNED by Mahmood" in html


def test_PLANT_a_signature_without_its_basis_holds_the_page():
    """An approval whose basis is not recorded is an override wearing a signature: how_it_reached_the_reviewer is
    as mandatory as the hash. A relay is an honest basis when it is recorded; a hidden relay is the defect."""
    signed = _signed(WITHDRAWN, "SEEN_AND_SIGNED")
    del signed["reviewer_countersignature"]["how_it_reached_the_reviewer"]
    assert "how_it_reached_the_reviewer missing" in result_changes.signature_problem(signed, _block(signed))
    blank = _signed(WITHDRAWN, "SEEN_AND_SIGNED", how_it_reached_the_reviewer="  ")
    assert "how_it_reached_the_reviewer missing" in result_changes.signature_problem(blank, _block(blank))
    relay = _signed(WITHDRAWN, "SEEN_AND_SIGNED", how_it_reached_the_reviewer="relayed by the orchestrating lane; figures conveyed in full")
    assert result_changes.signature_problem(relay, _block(relay)) is None


def test_PLANT_page_renders_the_basis_and_the_basis_is_outside_the_signed_bytes():
    relay = _signed(WITHDRAWN, "SEEN_AND_SIGNED", how_it_reached_the_reviewer="relayed by the orchestrating lane; figures conveyed in full")
    html = page.result_change_block(relay)
    assert "How it reached the reviewer: relayed by the orchestrating lane; figures conveyed in full" in html
    assert _block(relay) == _block(WITHDRAWN)          # the basis line sits under the block; the signed hash does not move


def test_PLANT_every_committed_notice_keeps_the_not_asserted_wrong_sentence():
    """'the numbers are not asserted wrong' is the difference between 'we cannot verify this' and 'this is wrong';
    it must survive every edit of every notice in docs/result_changes.json."""
    for n in result_changes.load():
        assert "the numbers are not asserted wrong" in n["reason"], (n["slug"], n["outcome"])
        assert "eligible evidence awaiting adjudication" in n["reason"], (n["slug"], n["outcome"])


def test_PLANT_a_page_carrying_a_notice_the_file_no_longer_has_is_held(tmp_path, monkeypatch):
    """regen #4: the notice refresh DROPPED sglt2-ckd's notice (its primary came back to the served pool) after the
    page had embedded it -- the page claimed a change that no longer existed. The gate compares the embedded notices
    with the file and holds the page until it is rebuilt."""
    from harness import gate
    root = tmp_path / "root"
    (root / "docs" / "reviews" / SLUG).mkdir(parents=True)
    (root / "docs" / "result_changes.json").write_text(json.dumps({"_doc": "t", "notices": []}) + chr(10), encoding="utf-8")
    monkeypatch.setattr(result_changes, "ROOT", str(root))
    rev = dict(NEW, reproduction={"result_changes": [_signed(WITHDRAWN, "SEEN_AND_SIGNED")]})
    d = root / "docs" / "reviews" / SLUG
    (d / "review.json").write_text(json.dumps(rev), encoding="utf-8")
    reasons = gate.check_result_change_countersigned(str(d))
    assert reasons and "differ from docs/result_changes.json" in reasons[0]
    (root / "docs" / "result_changes.json").write_text(json.dumps({"_doc": "t", "notices": [_signed(WITHDRAWN, "SEEN_AND_SIGNED")]}) + chr(10), encoding="utf-8")
    assert gate.check_result_change_countersigned(str(d)) == []
