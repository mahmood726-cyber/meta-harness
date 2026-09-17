from copy import deepcopy

import pytest

from harness import honest_ratchet
from harness.page import render_page
from harness.pipeline import (
    RETRIEVAL_RETRACTION,
    SEARCH_PROVENANCE_CLASS_STATEMENTS,
    SEARCH_PROVENANCE_DISCOVERY_STATEMENTS,
    SEARCH_PROVENANCE_HEADING,
    classify_retrieval,
)


@pytest.mark.parametrize(
    ("config", "ledger", "expected_class", "status"),
    [
        (
            {"pubmed_queries": ["12345678[uid] OR 23456789[uid]"]},
            None,
            "KNOWN_ITEM_RETRIEVAL",
            "RAN_ERROR",
        ),
        (
            {"pubmed_queries": ["12345678[uid]", "DAPA-HF[Title]"]},
            None,
            "TITLE_SEEDED_RETRIEVAL",
            "NOT_RUN",
        ),
        (
            {"pubmed_queries": ["hydrocortisone pneumonia randomized placebo mortality"]},
            None,
            "HAND_WRITTEN_KEYWORD_SEARCH",
            "RAN_ZERO",
        ),
    ],
)
def test_search_provenance_object_for_unauditable_classes(config, ledger, expected_class, status):
    rc = classify_retrieval(config, ledger, status)

    assert rc["class"] == expected_class
    assert rc["retrieval_auditable"] is False
    assert rc["search_provenance"] == {
        "heading": SEARCH_PROVENANCE_HEADING,
        "registry_first_status": status,
        "class_statement": SEARCH_PROVENANCE_CLASS_STATEMENTS[expected_class],
        "discovery_statement": SEARCH_PROVENANCE_DISCOVERY_STATEMENTS[expected_class],
        "retraction": RETRIEVAL_RETRACTION,
    }


def test_concept_search_has_no_search_provenance_object():
    ledger = {
        "sources": [
            {"kind": "PUBMED_CONCEPT_QUERY", "state": "RAN_OK", "query": "condition AND intervention"},
            {"kind": "PUBMED_PMID_ENUMERATION", "state": "RAN_OK", "query": "12345678[uid]"},
        ]
    }

    rc = classify_retrieval({"pubmed_queries": ["12345678[uid]"]}, ledger, "RAN_OK")

    assert rc["class"] == "CONCEPT_SEARCH"
    assert rc["retrieval_auditable"] is True
    assert "search_provenance" not in rc


def _review(rc):
    return {
        "slug": "__plant_search_provenance__",
        "title": "Synthetic search provenance",
        "question": "Does the provenance block render only from the object?",
        "method_declared": "synthetic method",
        "search": {
            "n_records": 1,
            "cache_ref": "cache/__plant_search_provenance__/records.json",
            "run_utc": "2026-09-14",
            "databases": ["PubMed", "ClinicalTrials.gov"],
            "source_status": {"Registry-first (AACT)": "RAN_ERROR"},
            "retrieval_class": rc,
        },
        "screening": {"records": []},
        "outcomes": [
            {
                "name": "Primary",
                "kind": "efficacy",
                "primary": True,
                "estimand": "RR",
                "result": {"present": False, "reason": "synthetic plant has no pooled result"},
                "trials": [],
                "declared_absent_trials": [],
            }
        ],
    }


def test_rendered_search_provenance_contains_heading_status_and_retraction():
    rc = classify_retrieval({"pubmed_queries": ["12345678[uid]"]}, None, "RAN_ERROR")

    html = render_page(_review(rc))

    assert SEARCH_PROVENANCE_HEADING in html
    from bs4 import BeautifulSoup
    spans = BeautifulSoup(html, 'html.parser').select('[data-claim-class="TRANSFORMATION"]')
    assert any("Recorded search provenance:" in span.get_text()
               and "The registry-first (AACT) adapter status for this topic is RAN_ERROR" in span.get_text()
               for span in spans)
    assert RETRIEVAL_RETRACTION in html


def test_search_provenance_plant_removing_object_removes_block_and_marker():
    rc = classify_retrieval({"pubmed_queries": ["12345678[uid]"]}, None, "RAN_ERROR")
    with_object = _review(rc)
    without_object = deepcopy(with_object)
    del without_object["search"]["retrieval_class"]["search_provenance"]

    html_with = render_page(with_object)
    html_without = render_page(without_object)

    assert "Search provenance" in html_with
    assert "Search provenance" not in html_without
    blocks_with = honest_ratchet.blocks(html_with)
    blocks_without = honest_ratchet.blocks(html_without)
    assert any("Search provenance" in block["text"] for block in blocks_with)
    assert not any("Search provenance" in block["text"] for block in blocks_without)
    refused = honest_ratchet.compare_blocks(
        blocks_with,
        blocks_without,
        {"acknowledgements": []},
        "docs/reviews/__plant_search_provenance__/index.html",
    )
    assert any("Search provenance" in reason for reason in refused)
