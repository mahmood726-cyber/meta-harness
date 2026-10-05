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
