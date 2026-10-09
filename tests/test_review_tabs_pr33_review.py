"""The captain's codex review of PR #33 (pva-tabs-r1, recorded on captain/review-pva-tabs b9134c12e): each finding planted.

g1#1  an extractor row citing a record not in the tree must not pass as EXTRACTOR
g1#2  a recorded read upgrades a hand-entered row only while its `served` snapshot equals the row's served numbers
g1#3  the page checks cited records against the committed held-record index, never a constant; unreadable -> UNKNOWN
g1#4  a registry the page cannot read renders UNKNOWN, never "none recorded"
g2#1  the inventory's included-studies check cannot pass on an empty tab for a trial with no PMID/NCT
g2#2  the inventory's screening check matches whole identifiers, not prefixes
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from harness import provenance_class as PC, review_tabs as T

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import provenance_census as pc  # noqa: E402
import review_tab_inventory as INV  # noqa: E402

GONE = "mc-" + "0" * 32


def _r(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------------------------------------------------ g1#1
def test_extractor_row_citing_a_missing_record_is_untraced():
    row = {"provenance": "abstract", "source": "a held span", "note": f"read by {GONE}"}
    assert PC.classify_served(row, lambda rid: False)[0] == "UNTRACED"
    assert PC.classify_served(row, lambda rid: True)[0] == "EXTRACTOR"
    assert PC.classify_served({"provenance": "abstract", "source": "a held span"}, lambda rid: False)[0] == "EXTRACTOR"


# ------------------------------------------------------------------------------------------------------------ g1#2
def test_recorded_read_must_agree_with_the_served_numbers_now():
    row = {"id": "PMID 1", "provenance": "fulltext_verified", "effect": 0.73, "ci_low": 0.61, "ci_high": 0.88}
    read = {"state": "AGREES", "record_id": GONE,
            "served": {"ai": None, "n1i": None, "ci": None, "n2i": None, "effect": 0.73, "ci_low": 0.61, "ci_high": 0.88}}
    reads = {"t|1|O": read}
    assert PC.served_class(row, "t", "O", lambda rid: True, reads)[0] == "RECORDED_MODEL_CALL"
    moved = dict(row, effect=0.74)                       # the served number changed after the read
    assert PC.served_class(moved, "t", "O", lambda rid: True, reads)[0] == "HAND_ENTERED"


# ------------------------------------------------------------------------------------------------------------ g1#3
def test_held_record_index_is_current_with_the_store():
    doc = json.loads((ROOT / "registry" / "held_record_ids.json").read_text(encoding="utf-8"))
    assert doc["ids"] == pc.held_record_ids(str(ROOT)) and doc["n"] == len(doc["ids"])


def test_page_checks_records_against_the_index_not_a_constant(monkeypatch):
    r = _r("sglt2-primary-prevention-hf")
    rows = T.extraction_rows(r)
    rmc = [x for x in rows if x["class"] == "RECORDED_MODEL_CALL"]
    assert rmc, "this review has a recorded-model-call row"
    real = T._registry

    def drop_index(name):
        if name == "held_record_ids.json":
            return {"ids": []}                            # plant: no record is held
        return real(name)
    monkeypatch.setattr(T, "_registry", drop_index)
    after = {(x["outcome"], x["trial"]): x["class"] for x in T.extraction_rows(r)}
    assert all(after[(x["outcome"], x["trial"])] != "RECORDED_MODEL_CALL" for x in rmc)

    def unreadable(name):
        if name == "held_record_ids.json":
            raise OSError("planted")
        return real(name)
    monkeypatch.setattr(T, "_registry", unreadable)
    assert {x["class"] for x in T.extraction_rows(r)} == {"UNKNOWN"}


# ------------------------------------------------------------------------------------------------------------ g1#4
@pytest.mark.parametrize("bad", ["result_change_reinstatements.json", "comparator_switch_signatures.json"])
def test_unreadable_registry_is_unknown_in_changes(monkeypatch, bad):
    real = T._registry

    def broken(name):
        if name == bad:
            raise OSError("planted")
        return real(name)
    monkeypatch.setattr(T, "_registry", broken)
    tab = T.changes_tab(_r("balanced-crystalloids-vs-saline-mortality"))
    assert 'data-state="UNKNOWN"' in tab and bad in tab
    assert "no withdrawal by a signer and no reinstatement is recorded" not in tab


def test_unreadable_decisions_is_unknown_for_d11(monkeypatch):
    real = T._registry

    def broken(name):
        if name == "g1_decisions.json":
            raise ValueError("planted")
        return real(name)
    monkeypatch.setattr(T, "_registry", broken)
    out = T.d11_status()
    assert 'data-state="UNKNOWN"' in out and "no D11 decision is recorded" not in out


# ------------------------------------------------------------------------------------------------------------ g2#1
def test_included_check_needs_a_label_for_a_trial_without_identifiers():
    review = {"outcomes": [{"name": "O", "trials": [{"id": "Smith 2001", "label": "Smith 2001", "effect": 1.0}]}]}
    page = "<meta name='tab-contract' content='rapidmeta-v1'>" \
           '<section class="tab" id="tab-included"><h3 class="tabname">Included studies</h3><table></table></section></main>'
    el = INV.check("x", page, review, [], [])["included"]["elements"]
    assert not any(el.values())
    shown = page.replace("<table></table>", "<table><tr><td>Smith 2001</td></tr></table>")
    assert all(INV.check("x", shown, review, [], [])["included"]["elements"].values())


# ------------------------------------------------------------------------------------------------------------ g2#2
def test_screening_check_matches_whole_identifiers_only():
    review = {"screening": {"records": [{"id": "1234"}]}}
    page = "<meta name='tab-contract' content='rapidmeta-v1'>" \
           '<section class="tab" id="tab-screening"><h3 class="tabname">Screening</h3><p>record 12345 excluded</p></section></main>'
    el = INV.check("x", page, review, [], [])["screening"]["elements"]
    assert not next(v for k, v in el.items() if k.startswith("every record"))
    shown = page.replace("12345", "1234")
    el2 = INV.check("x", shown, review, [], [])["screening"]["elements"]
    assert next(v for k, v in el2.items() if k.startswith("every record"))
