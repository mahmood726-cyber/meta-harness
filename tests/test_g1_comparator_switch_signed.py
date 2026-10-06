"""Plant: a topic matched against a comparator it does not SERVE counts on the G1 page (strict and K MATCHED) only once
Mahmood has signed that comparator switch (registry/comparator_switch_signatures.json; packet V8). The binding lane
replaced five comparators (5 Oct, pre-registered rules); until each switch is signed, a match against the replacement is
shown as pending and never counted."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts")]
import render_g1_tracker as rg  # noqa: E402


def _root(tmp_path, served="111", signed=None):
    d = tmp_path / "docs" / "reviews" / "t"
    d.mkdir(parents=True)
    (d / "review.json").write_text(json.dumps({"comparator": {"pmid": served}}), encoding="utf-8")
    if signed is not None:
        (tmp_path / "registry").mkdir()
        (tmp_path / rg.SWITCH_SIGNATURES).write_text(json.dumps({"switches": {"t": signed}}), encoding="utf-8")
    return tmp_path


REC = {"slug": "t", "comparator_pmid": "222", "trials": [], "N_eligible": 0, "k_matched": 0}


def test_served_comparator_needs_no_signature(tmp_path):
    assert rg.comparator_switch(dict(REC, comparator_pmid="111"), _root(tmp_path)) is None


def test_an_unsigned_switch_is_pending_and_not_counted(tmp_path):
    sw = rg.comparator_switch(REC, _root(tmp_path))
    assert sw == {"from": "111", "to": "222", "signed": False, "signature": None}
    assert rg.recompute(REC, _root(tmp_path / "x"))["criteria"]["COMPARATOR_SIGNED"] is False


def test_a_signed_switch_counts_only_for_exactly_that_switch(tmp_path):
    ok = {"from": "111", "to": "222", "state": "SEEN_AND_SIGNED"}
    assert rg.comparator_switch(REC, _root(tmp_path / "a", signed=ok))["signed"] is True
    assert rg.comparator_switch(REC, _root(tmp_path / "b", signed=dict(ok, to="333")))["signed"] is False
    assert rg.comparator_switch(REC, _root(tmp_path / "c", signed=dict(ok, state="OPEN")))["signed"] is False


def test_a_served_page_without_a_comparator_pmid_is_a_switch_and_unsigned(tmp_path):
    sw = rg.comparator_switch(REC, _root(tmp_path, served=""))
    assert sw["signed"] is False and sw["to"] == "222"


def test_an_unserved_topic_carries_no_switch(tmp_path):
    assert rg.comparator_switch(REC, tmp_path) is None
