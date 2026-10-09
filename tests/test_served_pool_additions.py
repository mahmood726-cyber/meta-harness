"""Plants for the signed served-pool admission route (harness/served_pool_additions.py,
scripts/build_served_pool_additions.py): a row enters a served pool ONLY when a signed notice names it, its signature
names the hash the register recorded, and no hold covers it."""
import copy
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
from harness import served_pool_additions as spa  # noqa: E402

ROW = {"id": "NCT00000001", "label": "PLANT", "ai": 5, "n1i": 50, "ci": 10, "n2i": 50}
NOTICE = {"slug": "s", "outcome": "o", "when_utc": "2026-10-05T00:00:00Z", "entered_pool": ["NCT00000001"],
          "reason": "SERVED-POOL REFRESH ...",
          "reviewer_countersignature": {"state": "SEEN_AND_SIGNED", "by": "Mahmood", "when_utc": "x",
                                        "rendered_sha256": "a" * 64, "how_it_reached_the_reviewer": "relay"}}
REG = [{"slug": "s", "outcome": "o", "notice_when_utc": "2026-10-05T00:00:00Z", "rendered_sha256": "a" * 64,
        "rows": [ROW]}]


def _adm(reg=REG, notice=NOTICE, slug="s", outcome="o"):
    return spa.admitted_rows(slug, outcome, register=reg, notices=[notice])


def test_signed_notice_admits_its_row():
    assert [r["id"] for r in _adm()] == ["NCT00000001"]


def test_open_notice_admits_nothing():
    n = copy.deepcopy(NOTICE)
    n["reviewer_countersignature"] = {"state": "OPEN"}
    assert _adm(notice=n) == []


def test_resigned_or_rebuilt_notice_admits_nothing_until_regenerated():
    n = copy.deepcopy(NOTICE)
    n["reviewer_countersignature"]["rendered_sha256"] = "b" * 64
    assert _adm(notice=n) == []


def test_row_the_notice_does_not_name_is_refused():
    n = copy.deepcopy(NOTICE)
    n["entered_pool"] = ["NCT99999999"]
    assert _adm(notice=n) == []


def test_delegated_acceptance_is_not_a_signature():
    n = copy.deepcopy(NOTICE)
    n["reviewer_countersignature"]["status"] = "DELEGATED_BULK_ACCEPTANCE"
    assert _adm(notice=n) == []


def test_other_slug_or_outcome_admits_nothing():
    assert _adm(slug="t") == [] and _adm(outcome="p") == [] and spa.admitted_rows(None, "o", register=REG, notices=[NOTICE]) == []


def test_rows_are_copies():
    r = _adm()[0]
    r["ai"] = 999
    assert REG[0]["rows"][0]["ai"] == 5


def test_held_trial_excludes_the_notice_whole():
    import build_served_pool_additions as b
    adds, exc = b.build(notices=[NOTICE], holds=[{"slug": "s", "id": "NCT00000001", "code": "PLANT_HOLD"}])
    assert adds == [] and "PLANT_HOLD" in exc[0]["why"]


def test_committed_register_matches_the_generator():
    """registry/served_pool_additions.json is generated, never hand-edited: regenerating reproduces it."""
    import build_served_pool_additions as b
    adds, exc = b.build()
    reg = json.load(open(spa.REGISTER, encoding="utf-8"))
    assert reg["additions"] == json.loads(json.dumps(adds)) and reg["excluded"] == json.loads(json.dumps(exc))


def test_wenus_per_protocol_counts_are_held():
    holds = json.load(open(os.path.join(ROOT, "registry", "served_pool_holds.json"), encoding="utf-8"))["holds"]
    assert any(h["id"] == "PMID 17356555" and h["code"] == "PER_PROTOCOL_COUNTS_NOT_RANDOMISED" for h in holds)
    reg = json.load(open(spa.REGISTER, encoding="utf-8"))
    assert not any(r["id"] == "PMID 17356555" for a in reg["additions"] for r in a["rows"])


def _signed_row(**kw):
    return dict({"id": "NCT00000001", "provenance": "served_pool_signed_notice",
                 "served_pool_admission": {"report_ids": ["11111111"]}}, **kw)


def test_value_not_found_absence_is_superseded_and_disclosed():
    absent = [{"id": "PMID 11111111", "absent_kind": "machine_absent", "reason": "no arm counts found in the abstract"}]
    trials, left = spa.reconcile([_signed_row()], absent)
    assert [t["id"] for t in trials] == ["NCT00000001"] and left == []
    assert trials[0]["served_pool_admission"]["supersedes_absence"][0]["state"] == "MACHINE_ABSENT_VALUE_NOT_FOUND"


def test_estimand_mismatch_refusal_is_superseded():
    absent = [{"id": "PMID 11111111", "reason_code": "REFUSED_ON_EVIDENCE", "reason": "declared absent (estimand mismatch): ..."}]
    trials, left = spa.reconcile([_signed_row()], absent)
    assert len(trials) == 1 and left == []


def test_population_timepoint_or_eligibility_refusal_drops_the_row():
    for a in ({"reason_code": "REFUSED_ON_EVIDENCE", "reason": "per-protocol completers only"},
              {"reason_code": "REFUSED_ON_EVIDENCE", "reason": "timepoint mismatch: day 29"},
              {"reason_code": "REFUSED_ON_EVIDENCE", "reason": "Protocol eligibility contract not satisfied"},
              {"reason_code": "RESULT_WITHDRAWN", "reason": "withdrawn"},
              {"absent_kind": "machine_absent", "reason": "refused: unit of analysis"}):
        absent = [dict(a, id="PMID 11111111")]
        trials, left = spa.reconcile([_signed_row()], absent)
        assert trials == [] and left == absent, a


def test_unrelated_rows_and_absences_untouched():
    other = {"id": "PMID 2", "label": "x"}
    absent = [{"id": "PMID 3", "reason_code": "REFUSED_ON_EVIDENCE", "reason": "per-protocol"}]
    trials, left = spa.reconcile([other], absent)
    assert trials == [other] and left == absent


def test_withdrawn_outcome_signed_correction_supersedes_the_withdrawn_entry_only_when_flagged():
    absent = [{"id": "PMID 11111111", "reason_code": "RESULT_WITHDRAWN", "reason": "withdrawn",
               "withdrawn_effect": {"effect": 0.88}}]
    trials, left = spa.reconcile([_signed_row()], list(absent))
    assert trials == [] and left == absent                              # not flagged: the withdrawal stands
    trials, left = spa.reconcile([_signed_row()], list(absent), corrected_withdrawal=True)
    assert len(trials) == 1 and left == []
    assert trials[0]["served_pool_admission"]["supersedes_absence"][0]["withdrawn_effect"] == {"effect": 0.88}


def test_build_register_refuses_counts_in_the_wrong_arm_order():
    import build_served_pool_additions as b
    span = "Treatment: 20 deaths among 100 randomised. Control: 10 deaths among 100 randomised."
    assert b._arm_order_ok(span, 20, 10) and not b._arm_order_ok(span, 10, 20)
    assert b._arm_order_ok("Tocilizumab (N=294) ... Death at day 28 ... 58 (19.7) 28 (19.4)", 58, 28)


def test_a_notice_withdrawn_by_its_signer_or_superseded_never_applies_and_stays_on_the_record():
    from harness import result_changes as rc, page
    n = dict(NOTICE, before={"k": 1, "estimate": 1.0, "ci_low": 0.5, "ci_high": 2.0},
             after={"k": 2, "estimate": 0.9, "ci_low": 0.5, "ci_high": 1.5}, left_pool=[], by="b", outcome="o")
    assert rc.notice_for([n], "s", "o", n["before"], n["after"], [], ["NCT00000001"]) is n
    w = dict(n, withdrawal={"state": "WITHDRAWN_BY_SIGNER", "by": "Mahmood", "when_utc": "2026-10-06T00:00:00Z",
                            "quote": "withdraw v6-02", "reason_code": "PER_PROTOCOL_COUNTS_NOT_RANDOMISED"})
    assert rc.notice_for([w], "s", "o", n["before"], n["after"], [], ["NCT00000001"]) is None
    assert spa.admitted_rows("s", "o", register=REG, notices=[w]) == []
    assert page.result_changes_status(w)["state"] == "WITHDRAWN_BY_SIGNER"
    s = dict(n, superseded_by={"notice": "V7-01", "rendered_sha256": "e" * 64, "why": "x"})
    assert rc.notice_for([s], "s", "o", n["before"], n["after"], [], ["NCT00000001"]) is None
    assert page.result_changes_status(s)["state"] == "SUPERSEDED" and page.result_changes_status(n) is None
    # the signed block's bytes (what the signature hashes) are the same with or without the status
    assert page.result_change_block(w) == page.result_change_block(n)


def test_v6_02_is_withdrawn_by_its_signer_and_its_signature_is_kept():
    import json as _j
    d = _j.load(open(os.path.join(ROOT, "docs", "result_changes.json"), encoding="utf-8"))["notices"]
    v = [n for n in d if n["slug"] == "probiotics-aad-prevention" and n.get("entered_pool") == ["PMID 17356555"]]
    assert len(v) == 1 and v[0]["withdrawal"]["quote"] == "withdraw v6-02"
    assert v[0]["reviewer_countersignature"]["state"] == "BATCH_SEEN_AND_SIGNED"


def test_committed_rows_are_carried_forward_when_the_tracker_shows_them_in_our_pool(monkeypatch):
    # 6 Oct worker run 2: once the pipeline admitted the signed rows, the tracker saw them IN our pool, and a builder that
    # re-read them from the tracker dropped three signed notices. The committed rows are kept and re-checked instead.
    import build_served_pool_additions as b
    reg = json.load(open(spa.REGISTER, encoding="utf-8"))["additions"]
    assert reg, "the committed register must hold the signed additions"
    monkeypatch.setattr(b.sp, "candidates", lambda o: ([], []))       # the tracker now offers no row outside the pool
    adds, exc = b.build()
    assert sorted(a["slug"] for a in adds) == sorted(a["slug"] for a in reg)


def test_a_held_signed_notice_is_never_admitted_until_its_signer_lifts_it():
    # V6-01 (TECOS) was held 6 Oct (an unshown HHF consequence) and lifted by Mahmood 7 Oct ('lift v6-01 and agree').
    # The requirement, exercised with the real notice: while a hold applies the notice is excluded WHOLE; a signer's
    # lift (by + verbatim quote) admits it at its signed numbers.
    import build_served_pool_additions as b
    hold = {"slug": "dpp4-mace-t2d", "id": "PMID 26052984", "code": "SIGNED_CHANGE_HAS_AN_UNSHOWN_CONSEQUENCE"}
    adds, exc = b.build(holds=[hold])
    assert not any(a["slug"] == "dpp4-mace-t2d" for a in adds)
    assert any("dpp4-mace-t2d" in e["notice"] and "held" in e["why"] for e in exc)
    lifted = dict(hold, final={"state": "LIFTED_BY_SIGNER", "by": "Mahmood", "quote": "lift v6-01 and agree"})
    adds, _ = b.build(holds=[lifted])
    row = next(a for a in adds if a["slug"] == "dpp4-mace-t2d")
    assert row["after"] == {"k": 4, "estimate": 1.0007, "ci_low": 0.8998, "ci_high": 1.1129}



def test_PLANT_a_signed_admission_is_carried_by_a_later_signed_chain_to_the_served_result():
    """V13-02Q (signed) re-expressed tocilizumab's served pool as an OR. The V6-05 admission (COVACTA, TOCIBRAS; signed
    under RR) can no longer be re-derived from today's rows, so the generator dropped it -- regenerating the register would
    have silently removed two trials from a served pool. A signed admission is kept when a chain of LATER SIGNED notices for
    the same outcome links its 'after' to what is served now; a chain that does not reach the served result carries nothing."""
    import build_served_pool_additions as b
    adds, exc = b.build()
    toci = [a for a in adds if a["slug"] == "tocilizumab-covid19-mortality"]
    assert len(toci) == 1 and sorted(r["id"] for r in toci[0]["rows"]) == ["NCT04320615", "NCT04403685"]
    assert toci[0].get("carried_by_signed_chain"), toci[0]
    assert not any("tocilizumab" in e["notice"] for e in exc), exc


def test_PLANT_a_chain_that_does_not_reach_the_served_result_carries_nothing(monkeypatch):
    import build_served_pool_additions as b
    real = b.fn.served

    def drifted(slug):
        p = real(slug)
        if slug == "tocilizumab-covid19-mortality" and p:
            p = dict(p, result=dict(p.get("result") or {}, estimate=9.99))
        return p
    monkeypatch.setattr(b.fn, "served", drifted)
    adds, exc = b.build()
    assert not any(a["slug"] == "tocilizumab-covid19-mortality" for a in adds)


def test_PLANT_a_recurring_result_takes_the_chronologically_next_link(monkeypatch):
    """codex v13-apply-r3 P2: A->B->A->B->C stopped at the first link because two later notices matched B."""
    import build_served_pool_additions as b
    ns = [dict(slug="demo", outcome="m", when_utc=f"2026-10-0{i + 1}T00:00:00Z", before={"e": x}, after={"e": y},
               reviewer_countersignature={"state": "SIGNED"}) for i, (x, y) in enumerate([(1, 2), (2, 1), (1, 2), (2, 3)])]
    monkeypatch.setattr(b.rc, "SIGNED_STATES", {"SIGNED"})
    monkeypatch.setattr(b.rc, "not_applied", lambda n: False)
    monkeypatch.setattr(b.rc, "_same", lambda x, y: x == y)
    assert b._signed_chain(ns[0], ns) == ns[1:]
