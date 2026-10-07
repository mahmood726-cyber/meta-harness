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

from harness import honest_ratchet, notice_kinds, page, result_changes

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


def test_PLANT_every_committed_notice_states_which_claim_it_is_making():
    """A notice must say whether it is challenging the old number or only unable to bind it. Both, per kind.

    'the numbers are not asserted wrong' is the difference between 'we cannot verify this' and 'this is wrong'.
    Originally this test required that sentence on EVERY notice, which was right while every notice was a
    SET-ASIDE: a trial left the pool because its number could not be bound to held bytes, so the number was
    genuinely not challenged.

    It is false on a SUBSTITUTION. When a trial stays in the pool and contributes a different number because the
    previous one was the wrong quantity for the outcome -- J-EMPHASIS's CV-death/HHF composite HR served as
    all-cause mortality -- the old number IS asserted wrong, and writing 'not asserted wrong' beside it would put
    a false sentence on a served page. Satisfying the old assertion would have required exactly that.

    So the requirement is per kind, and each kind must carry its own claim AND NOT the other one. A notice that
    makes neither claim fails: silence about which claim is being made is the thing this plant exists to stop."""
    NOT_WRONG = "the numbers are not asserted wrong"
    AWAITING = "eligible evidence awaiting adjudication"
    IS_WRONG = "was the WRONG QUANTITY for this outcome, and is asserted wrong"
    ENTERED = "Entering trials are new evidence, not a correction"
    LIFTED = "a new claim on the page, not a correction of a served number"
    notices = result_changes.load()
    for n in notices:
        where = (n["slug"], n["outcome"])
        reason = n["reason"]
        # A REINSTATEMENT (V8-06, 7 Oct): the entering trial was SET ASIDE by an earlier signed notice for this outcome
        # ('eligible evidence awaiting adjudication') and this notice is that adjudication, reversing it by name. Its
        # claim is the reversal, which result_changes.reversed_setasides verifies against the record; it must not
        # assert the old number wrong (the set-aside already said it was not).
        if notice_kinds.reversed_setasides(n, notices):
            assert IS_WRONG not in reason, (where, "a reinstatement must not assert the old number wrong")
            continue
        # Three kinds, each with its own claim: a trial LEFT (set-aside: not asserted wrong, awaiting
        # adjudication); a trial ENTERED (new evidence: the old number is not asserted wrong); a row's number was
        # SUBSTITUTED with nobody leaving or entering (the old number was the wrong quantity: asserted wrong).
        if n.get("left_pool"):
            assert NOT_WRONG in reason, where
            assert AWAITING in reason, where
            assert IS_WRONG not in reason, (where, "a set-aside must not assert the number wrong")
        elif n.get("entered_pool"):
            assert ENTERED in reason, (where, "an entering trial must be described as new evidence")
            # A notice can carry two kinds at once (probiotics AAD, acq/k-gap integration 2026-10-03: 17604300 enters
            # AND McFarland's adjusted RR is substituted by its randomised counts). The wrong-quantity claim is then
            # allowed, but only beside the substitution it belongs to -- never on a notice that only adds evidence.
            substituted = "stayed in the pool but now contributes a different number" in reason
            assert IS_WRONG not in reason or substituted, (where, "new evidence must not assert the old number wrong")
            for tid in n["entered_pool"]:
                assert f"{tid} entered the pool contributing" in reason, (where, tid)
        elif "was withheld on the served page" in reason:
            # A LIFTED SUPPRESSION (omega3 AF, 2026-10-01): the estimate existed and was withheld; serving it is a new
            # claim, and asserts nothing about any served number.
            assert LIFTED in reason, (where, "a lifted suppression must say it is a new claim, not a correction")
            assert IS_WRONG not in reason and NOT_WRONG not in reason, where
            assert n["before"].get("estimate") is None, (where, "only a withheld (absent) estimate can be lifted")
        else:
            assert IS_WRONG in reason, (where, "a substitution must say the served number was wrong")
            assert NOT_WRONG not in reason, (where, "a substitution must not claim the number is unchallenged")
        assert "no trial leaving or entering" not in reason or not (n.get("left_pool") or n.get("entered_pool")),             (where, "the notice says nothing left or entered while its own pool lists say otherwise")


def _refresh_in(tmp, monkeypatch, notices, before, after):
    """Run scripts/refresh_result_change_notices.refresh against synthetic before/after review objects."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("rrcn", str(Path(__file__).resolve().parents[1] / "scripts" / "refresh_result_change_notices.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    (tmp / "docs" / "reviews" / "t").mkdir(parents=True)
    path = tmp / "docs" / "result_changes.json"
    path.write_text(json.dumps({"_doc": "", "notices": notices}), encoding="utf-8")
    monkeypatch.setattr(mod, "ROOT", tmp)
    monkeypatch.setattr(mod, "PATH", path)
    monkeypatch.setattr(mod, "_before", lambda commit, slug: before)
    monkeypatch.setattr(mod, "_after", lambda slug: after)
    mod.refresh("BASE", "tester", "2026-10-01T00:00:00Z")
    return json.loads(path.read_text(encoding="utf-8"))["notices"]


def _rv(k, est, trial_ids, entered_row=None):
    trials = [{"id": t, "effect": 0.9, "ci_low": 0.8, "ci_high": 1.0, "scale": "RR", "provenance": "abstract"}
              for t in trial_ids]
    if entered_row:
        trials.append(entered_row)
    return {"outcomes": [{"name": "O", "result": {"k": k, "estimate": est, "ci_low": est - 0.1, "ci_high": est + 0.1},
                          "trials": trials, "declared_absent_trials": []}]}


def test_PLANT_a_signed_notice_is_never_rewritten_by_a_later_change(tmp_path, monkeypatch):
    """2026-10-01: the held-full-text enables changed two outcomes (omega3 MACE, probiotics AAD) whose notices
    Mahmood had countersigned on 2026-09-29. Notices were keyed one per outcome, so the refresher REBUILT the
    signed notices and reset their signatures to OPEN -- deleting a signature by overwriting it. A later change
    must get a NEW notice; the signed one must survive byte-identical."""
    signed = {"slug": "t", "outcome": "O", "before": {"k": 6, "estimate": 0.95, "ci_low": 0.85, "ci_high": 1.05},
              "after": {"k": 5, "estimate": 0.937, "ci_low": 0.837, "ci_high": 1.037}, "left_pool": ["PMID 1"],
              "entered_pool": [], "reason": "earlier change", "by": "x", "when_utc": "2026-09-21T00:00:00Z",
              "reviewer_countersignature": {"state": "BATCH_SEEN_AND_SIGNED", "by": "Mahmood",
                                            "when_utc": "2026-09-29T09:09:04Z", "rendered_sha256": "ab" * 32}}
    before = _rv(5, 0.937, ["PMID 2", "PMID 3"])
    entering = {"id": "PMID 9", "effect": 1.0, "ci_low": 0.64, "ci_high": 1.56, "scale": "HR",
                "provenance": "pmc_fulltext"}
    after = _rv(6, 0.9386, ["PMID 2", "PMID 3"], entering)
    out = _refresh_in(tmp_path, monkeypatch, [json.loads(json.dumps(signed))], before, after)
    assert signed in out, "the countersigned notice was rewritten or dropped"
    fresh = [n for n in out if n is not None and n != signed]
    assert len(fresh) == 1 and fresh[0]["reviewer_countersignature"]["state"] == "OPEN"
    assert fresh[0]["entered_pool"] == ["PMID 9"]
    assert "PMID 9 entered the pool contributing HR 1.0 (0.64 to 1.56)" in fresh[0]["reason"]
    assert "no trial leaving or entering" not in fresh[0]["reason"]


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


def test_PLANT_a_lifted_suppression_is_derived_not_left_unexplained(tmp_path, monkeypatch):
    """2026-10-01, omega3 Atrial fibrillation: the k=1 estimate was WITHHELD on the served page (compat_check: an
    isolated harm estimate is suppressed while a primary-pool trial's source-reported harm is unresolved -- VITAL's
    sentence about future ancillary studies). A held-source decision typed that hit SIGNAL_SPURIOUS, the suppression
    lifted, and the same estimate is now served. Nothing entered or left and no row moved, so the refresher said
    'the cause is not derivable'. It is derivable from the objects: the withheld state and the row that resolved it."""
    before = _rv(1, 1.2296, ["PMID 1"])
    res = before["outcomes"][0]["result"]
    res.update({"k": None, "estimate": None, "ci_low": None, "ci_high": None, "present": False,
                "state": "HARMS_INCOMPLETE",
                "known_eligible_outcome_reports_unresolved": [{"trial_id": "30415637", "terms": ["atrial fibrillation"]}]})
    before["outcomes"][0]["declared_absent_trials"] = [{"id": "PMID 30415637", "state": "OUTCOME_NOT_IN_SOURCE",
                                                         "absent_kind": "machine_absent"}]
    after = _rv(1, 1.2296, ["PMID 1"])
    after["outcomes"][0]["declared_absent_trials"] = [{"id": "PMID 30415637", "state": "SIGNAL_SPURIOUS",
                                                        "reason_code": "SIGNAL_SPURIOUS", "typed_refusal": True,
                                                        "absent_kind": "adjudicated_absent",
                                                        "reason": "The hit names future ancillary studies."}]
    out = _refresh_in(tmp_path, monkeypatch, [], before, after)
    assert len(out) == 1
    reason = out[0]["reason"]
    assert "not derivable" not in reason
    assert "was withheld on the served page (HARMS_INCOMPLETE" in reason
    assert "PMID 30415637 is now resolved as SIGNAL_SPURIOUS: The hit names future ancillary studies." in reason
    assert "a new claim on the page, not a correction" in reason
    assert "asserted wrong" not in reason


# ---------------------------------------------------------------- reinstatement: declared, then proved from the record
SIG = {"state": "SEEN_AND_SIGNED"}
ASIDE_REASON = "set aside; eligible evidence awaiting adjudication; the numbers are not asserted wrong."


def _n(when, left=(), entered=(), reason="r", sig=SIG, **kw):
    return dict({"slug": "s", "outcome": "o", "when_utc": when, "left_pool": list(left), "entered_pool": list(entered),
                 "reason": reason, "reviewer_countersignature": sig}, **kw)


def test_PLANT_a_declared_reinstatement_is_proved_from_the_record():
    aside = _n("2026-09-20T00:00:00Z", left=["T1"], reason=ASIDE_REASON)
    back = _n("2026-10-06T00:00:00Z", entered=["T1"], reason="anything at all")       # its wording is never read
    d = {"T1": "2026-09-20T00:00:00Z"}
    assert notice_kinds.reversed_setasides(back, [aside, back], declared=d) == {"T1": aside}
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={}) is None            # undeclared
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={"T1": "2026-09-21T00:00:00Z"}) is None


@pytest.mark.parametrize("bad", [
    {"outcome": "other"}, {"left_pool": ["T2"]}, {"left_pool": ["T1", "T2"]},                 # other outcome / trial / two trials
    {"reviewer_countersignature": {"state": "OPEN"}}, {"withdrawal": {"state": "WITHDRAWN_BY_SIGNER"}},
    {"reason": "CORRECTION: T1 is not randomized and is ineligible; the old result was wrong."},   # not a set-aside
])
def test_PLANT_the_reversed_notice_must_be_a_signed_applied_single_trial_setaside(bad):
    aside = dict(_n("2026-09-20T00:00:00Z", left=["T1"], reason=ASIDE_REASON), **bad)
    back = _n("2026-10-06T00:00:00Z", entered=["T1"])
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={"T1": "2026-09-20T00:00:00Z"}) is None


def test_PLANT_order_must_be_known_and_latest():
    aside = _n("2026-10-01T00:00:00Z", left=["T"], reason=ASIDE_REASON)
    d = {"T": "2026-10-01T00:00:00Z"}
    back = _n("2026-10-04T00:00:00Z", entered=["T"])
    later = _n("2026-10-03T00:00:00Z", left=["T"], reason="CORRECTION: T is ineligible")          # a later move
    assert notice_kinds.reversed_setasides(back, [aside, later, back], declared=d) is None
    same = _n("2026-10-01T00:00:00.000Z", left=["T"], reason="excluded")                          # tie at the instant
    assert notice_kinds.reversed_setasides(back, [aside, same, back], declared=d) is None
    twin = _n("2026-10-04T00:00:00Z", entered=["T"], reason="another reinstatement at the same instant", left=[])
    twin["entered_pool"] = ["T", "U"]
    assert notice_kinds.reversed_setasides(back, [aside, twin, back], declared=d) is None
    frac = _n("2026-10-01T00:00:00.500Z", left=["T"], reason="excluded")                         # instants, not strings
    assert notice_kinds.reversed_setasides(back, [aside, frac, back], declared=d) is None
    assert notice_kinds.reversed_setasides(dict(back, when_utc="not a time"), [aside, back], declared=d) is None


def test_PLANT_a_copy_of_the_notice_is_the_same_notice():
    """codex v8-apply-r7 #2: identity by content, never by object identity."""
    import copy
    aside = _n("2026-09-20T00:00:00Z", left=["T1"], reason=ASIDE_REASON)
    back = _n("2026-10-06T00:00:00Z", entered=["T1"])
    d = {"T1": "2026-09-20T00:00:00Z"}
    assert notice_kinds.reversed_setasides(copy.deepcopy(back), [aside, back], declared=d) == {"T1": aside}


def test_the_committed_v8_06_reinstatement_is_declared_and_proved():
    notices = result_changes.load()
    n = next(x for x in notices if x["slug"] == "dpp4-mace-t2d" and x["outcome"] == "Hospitalization for heart failure"
             and x["entered_pool"] == ["PMID 23992601"])
    got = notice_kinds.reversed_setasides(n, notices)
    assert got and got["PMID 23992601"]["when_utc"] == "2026-09-20T23:30:00Z"


def test_PLANT_ineligible_evidence_is_not_eligible_evidence():
    """codex v8-apply-r8 #2: 'eligible evidence awaiting adjudication' is a substring of 'ineligible evidence ...'."""
    aside = _n("2026-09-20T00:00:00Z", left=["T1"],
               reason="ineligible evidence awaiting adjudication; the numbers are not asserted wrong.")
    back = _n("2026-10-06T00:00:00Z", entered=["T1"])
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={"T1": "2026-09-20T00:00:00Z"}) is None


def test_PLANT_negated_eligibility_and_broken_register_refuse(tmp_path):
    """codex v8-apply-r9 #2 ('not eligible evidence ...') and #3 (a declaration register that is not a file)."""
    aside = _n("2026-09-20T00:00:00Z", left=["T1"],
               reason="This is not eligible evidence awaiting adjudication; the numbers are not asserted wrong.")
    back = _n("2026-10-06T00:00:00Z", entered=["T1"])
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={"T1": "2026-09-20T00:00:00Z"}) is None
    (tmp_path / "registry" / "result_change_reinstatements.json").mkdir(parents=True)
    with pytest.raises(ValueError):
        notice_kinds._declared(back, str(tmp_path))


def test_PLANT_negation_with_words_between_refuses():
    """codex v8-apply-r11 #4: 'not currently eligible evidence ...'."""
    aside = _n("2026-09-20T00:00:00Z", left=["T1"],
               reason="not currently eligible evidence awaiting adjudication; the numbers are not asserted wrong.")
    back = _n("2026-10-06T00:00:00Z", entered=["T1"])
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={"T1": "2026-09-20T00:00:00Z"}) is None


def test_PLANT_asserted_wrong_in_any_case_refuses():
    """codex v8-apply-r12 #3: 'Asserted Wrong' in another case still asserts something wrong."""
    aside = _n("2026-09-20T00:00:00Z", left=["T1"],
               reason="eligible evidence awaiting adjudication; the numbers are not asserted wrong; denominators ASSERTED WRONG.")
    back = _n("2026-10-06T00:00:00Z", entered=["T1"])
    assert notice_kinds.reversed_setasides(back, [aside, back], declared={"T1": "2026-09-20T00:00:00Z"}) is None
