"""Record-to-served-text contract; ASC_DOCS_ROOT selects an actual replay."""
import html
import json
import os
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"


def served_pair():
    if os.environ.get("ASC_DOCS_ROOT"):
        directory = Path(os.environ["ASC_DOCS_ROOT"]) / "reviews" / SLUG
        return (json.loads((directory / "review.json").read_text(encoding="utf-8")),
                (directory / "index.html").read_text(encoding="utf-8"))
    from harness.pipeline import build_review_core
    from harness.page import render_page
    from harness.registration import protocol_sha
    config = json.loads((ROOT / "topics" / (SLUG + ".json")).read_text(encoding="utf-8"))
    records = json.loads((ROOT / "cache" / SLUG / "records.json").read_text(encoding="utf-8"))
    review = build_review_core(SLUG, config, records, protocol_sha(SLUG))
    return review, render_page(review)


def visible_text(page):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", page)).split())


def test_served_ascertainment_claim_matches_records():
    review, page = served_pair()
    text = visible_text(page)
    records = review["screening"]["records"]
    n = sum(row.get("outcome_ascertainment", {}).get("state") == "UNRESOLVED" for row in records)
    if "records as UNRESOLVED per record" in text:
        assert n == len(records), f"served claim says per record, but UNRESOLVED is recorded on {n} of {len(records)}"
    assert all("outcome_ascertainment" in row for row in records)
    assert f"records as UNRESOLVED on {n} of {len(records)} records" in text


def test_axis_state_is_protocol_derived_and_does_not_change_decisions():
    from harness.pipeline import _record_outcome_ascertainment
    protocol = (ROOT / "protocols" / (SLUG + ".md")).read_text(encoding="utf-8")
    rows = [{"id": "fixture-include", "decision": "include"},
            {"id": "fixture-exclude", "decision": "exclude"}]
    result = _record_outcome_ascertainment(rows, protocol)
    assert [r["decision"] for r in result] == [r["decision"] for r in rows]
    assert all(r["outcome_ascertainment"] == {"state": "UNRESOLVED", "basis": "B-prime"} for r in result)
    assert all("outcome_ascertainment" not in r for r in rows)
    assert result[0]["outcome_ascertainment"] is not result[1]["outcome_ascertainment"]


def test_undeclared_axis_and_unparsable_protocol_are_distinct():
    from harness.screen import outcome_ascertainment
    assert outcome_ascertainment("- **Eligibility.** Population and design only.") == {
        "state": "NOT_AN_AXIS", "basis": "registered"}
    assert outcome_ascertainment("") == {
        "state": "UNRESOLVED", "basis": "ELIGIBILITY_CLAUSE_NOT_PARSABLE"}


def test_sentence_recounts_mixed_or_missing_states():
    from harness.page import _eligibility_screen_sentence
    protocol = (ROOT / "protocols" / (SLUG + ".md")).read_text(encoding="utf-8")
    review = {"protocol": {"text": protocol}, "screening": {"records": [
        {"outcome_ascertainment": {"state": "UNRESOLVED", "basis": "B-prime"}},
        {},
    ]}}
    assert "UNRESOLVED on 1 of 2 records" in _eligibility_screen_sentence(review)
