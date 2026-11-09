"""C1 (generated completeness claims; external audit r15): no generated text claims completeness unless the search is
recorded as systematic. No served review's search is (17 title-seeded, 11 known-item, 4 hand-written keyword)."""
from __future__ import annotations

import json
from pathlib import Path

from harness import review_tabs as T

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "docs" / "reviews").glob("*/review.json"))]


def test_PLANT_the_ledger_pointer_is_bounded_by_the_recorded_search():
    r = {"search": {"retrieval_class": {"class": "KNOWN_ITEM_RETRIEVAL", "label": "KNOWN-ITEM RETRIEVAL, NOT A SYSTEMATIC SEARCH"}}}
    c = T._search_scope_caveat(r)
    assert "KNOWN-ITEM RETRIEVAL" in c and "not a claim that the evidence is complete" in c
    assert T._search_scope_caveat({"search": {"retrieval_class": {"class": "SYSTEMATIC_SEARCH"}}}) == ""


def test_sweep_no_served_page_claims_every_eligible_trial_family():
    assert len(REVIEWS) == 32
    shown = 0
    for r in REVIEWS:
        html = T.included_tab(r)
        assert "with every eligible trial family" not in html, r["slug"]
        if "family-level ledger" in html:
            shown += 1
            assert T.search_is_systematic(r) or "not a claim that the evidence is complete" in html, r["slug"]
    assert shown > 0                                         # the pointer is rendered somewhere, so the sweep tests it
