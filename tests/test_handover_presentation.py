"""Presentation fixes for the review-tabs handover (outputs/pva-2026-10-08/REVIEW_TABS_HANDOVER.md), each planted on the
committed review it was found in. Presentation only: these change rendered words, never a review.json field.
(The items that would change a stored object or a served count are written as V12 items for the Captain instead.)"""
from __future__ import annotations

import json
import re
from pathlib import Path

from harness import comparator_panel, page, review_tabs as T

ROOT = Path(__file__).resolve().parents[1]


def _r(slug):
    return json.loads((ROOT / "docs" / "reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _outcome(r, primary=True):
    return next(o for o in r["outcomes"] if bool(o.get("primary")) == primary)


def test_H13_single_trial_is_not_described_as_pooled():
    o = _outcome(_r("tranexamic-acid-pph"))
    assert o["result"]["k"] == 1
    html = page._outcome_block(o)
    assert "were pooled" not in html and "single trial, not pooled" in html


def test_H19_suppressed_pool_is_not_described_as_pooled():
    o = _outcome(_r("iv-iron-hfref-hosp"))
    assert o["result"].get("suppressed_incompatible")
    html = page._outcome_block(o)
    assert "were pooled" not in html and "no pooled estimate is served" in html


def test_H13_overview_reconciliation_does_not_call_a_single_trial_pooled():
    """codex review (job B): the Overview sentence was a second renderer of 'were pooled'."""
    html = page._overview(_r("tranexamic-acid-pph"), False)
    assert "and were pooled" not in html and "a single trial, not pooled" in html


def test_H13_a_real_pool_still_says_pooled():
    o = _outcome(_r("dpp4-mace-t2d"))
    assert o["result"]["k"] >= 2 and o["result"].get("estimate") is not None
    assert "were pooled" in page._outcome_block(o)


def test_H11_hand_checked_rows_are_not_called_aact_derived():
    html = page.render_page(_r("metformin-pcos-ovulation"))
    assert "AACT-derived" not in html


def test_H12_absence_label_does_not_deny_an_outcome_sentence():
    label = page._ABSENCE_STATE_LABEL["OUTCOME_NOT_IN_SOURCE"]
    assert "no outcome sentence" not in label and "poolable" in label


def test_H17_empty_panel_field_is_not_called_not_extracted():
    r = _r("finerenone-ckd-t2d-renal")
    html = comparator_panel.render(r) if hasattr(comparator_panel, "render") else page.render_page(r)
    assert "NOT EXTRACTED from held text" not in html


def test_H18_unpopulated_trial_set_is_not_called_not_enumerated():
    html = page.render_page(_r("esketamine-trd-madrs"))
    assert "Trial set NOT ENUMERATED" not in html
    assert "Trial membership is not populated in this panel" in html


def test_A1_no_heading_level_is_skipped_inside_an_outcome_block():
    for slug in ("dpp4-mace-t2d", "empagliflozin-hfpef-hosp"):
        html = page.render_page(_r(slug))
        tab = re.search(r'<section class="tab" id="tab-outcomes">(.*?)</section>(?=<section class="tab")', html, re.S).group(1)
        levels = [int(x) for x in re.findall(r"<h([1-6])[\s>]", tab)]
        jumps = [(a, b) for a, b in zip(levels, levels[1:]) if b > a + 1]
        assert not jumps, (slug, jumps[:3])


def test_presentation_fixes_change_no_review_object():
    """The renderer reads review.json; nothing here writes it. Pin that the outcome objects are untouched by rendering."""
    r = _r("tranexamic-acid-pph")
    before = json.dumps(r, sort_keys=True)
    page.render_page(r)
    T.included_tab(r)
    assert json.dumps(r, sort_keys=True) == before
