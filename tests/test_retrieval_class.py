from harness.pipeline import (
    CONCEPT_SEARCH_LABEL,
    HAND_WRITTEN_KEYWORD_SEARCH_LABEL,
    KNOWN_ITEM_RETRIEVAL_LABEL,
    RETRIEVAL_RETRACTION,
    RETRIEVAL_UNAUDITABLE_DISTINCTION,
    TITLE_SEEDED_RETRIEVAL_LABEL,
    classify_query,
    classify_retrieval,
)


def test_structural_query_classifier_kinds():
    assert classify_query("12345678[uid] OR 23456789[uid]") == "PMID_ENUMERATION"
    assert classify_query("10.1016/S0140-6736(22)02083-9") == "IDENTIFIER_SEEDED"
    assert classify_query("40159390") == "IDENTIFIER_SEEDED"
    assert classify_query("Dapagliflozin[Title] randomized placebo") == "TITLE_ANCHORED"
    assert classify_query("FAIR-HF2 JAMA 2025 randomized clinical trial ferric carboxymaltose") == "NAME_SEEDED"
    assert (
        classify_query("hydrocortisone severe community-acquired pneumonia randomized placebo mortality")
        == "FREE_TEXT_KEYWORD"
    )


def test_all_uid_queries_are_known_item_retrieval():
    rc = classify_retrieval({"pubmed_queries": ["123[uid] OR 456[uid]"]})
    assert rc["class"] == "KNOWN_ITEM_RETRIEVAL"
    assert rc["label"] == KNOWN_ITEM_RETRIEVAL_LABEL
    assert rc["basis"] == [
        {"query": "123[uid] OR 456[uid]", "kind": "PMID_ENUMERATION", "features": ["uid_field:[uid]"]}
    ]
    assert rc["screening_auditable"] is True
    assert rc["retrieval_auditable"] is False
    assert rc["distinction"] == RETRIEVAL_UNAUDITABLE_DISTINCTION
    assert rc["retraction"] == RETRIEVAL_RETRACTION


def test_mixed_uid_and_seeded_queries_are_title_seeded_retrieval():
    rc = classify_retrieval({"pubmed_queries": ["123[uid]", '"named trial"[Title]']})
    assert rc["class"] == "TITLE_SEEDED_RETRIEVAL"
    assert rc["label"] == TITLE_SEEDED_RETRIEVAL_LABEL
    assert rc["basis"] == [
        {"query": "123[uid]", "kind": "PMID_ENUMERATION", "features": ["uid_field:[uid]"]},
        {"query": '"named trial"[Title]', "kind": "TITLE_ANCHORED", "features": ["title_field_tag:[Title]"]},
    ]
    assert rc["retrieval_auditable"] is False
    assert rc["distinction"] == RETRIEVAL_UNAUDITABLE_DISTINCTION
    assert rc["retraction"] == RETRIEVAL_RETRACTION


def test_all_non_uid_free_text_queries_are_hand_written_keyword_search():
    rc = classify_retrieval({
        "pubmed_queries": [
            "hydrocortisone severe community-acquired pneumonia randomized placebo mortality",
            "methylprednisolone severe community-acquired pneumonia randomized placebo mortality NOT macrolides NOT post-hoc NOT lymphopenia NOT biomarkers",
        ]
    })
    assert rc["class"] == "HAND_WRITTEN_KEYWORD_SEARCH"
    assert rc["label"] == HAND_WRITTEN_KEYWORD_SEARCH_LABEL
    assert [row["kind"] for row in rc["basis"]] == ["FREE_TEXT_KEYWORD", "FREE_TEXT_KEYWORD"]
    assert all(row["features"] == [] for row in rc["basis"])
    assert rc["retrieval_auditable"] is False
    assert rc["distinction"] == RETRIEVAL_UNAUDITABLE_DISTINCTION
    assert rc["retraction"] == RETRIEVAL_RETRACTION


def test_ran_ok_pubmed_concept_ledger_makes_concept_search():
    ledger = {
        "sources": [
            {"kind": "PUBMED_CONCEPT_QUERY", "state": "RAN_OK", "query": "condition AND drug"},
            {"kind": "PUBMED_PMID_ENUMERATION", "state": "RAN_OK", "query": "123[uid]"},
        ]
    }
    rc = classify_retrieval({"pubmed_queries": ["123[uid]"]}, ledger)
    assert rc["class"] == "CONCEPT_SEARCH"
    assert rc["label"] == CONCEPT_SEARCH_LABEL
    assert rc["basis"] == [
        {
            "query": "condition AND drug",
            "kind": "CONCEPT",
            "features": ["concept_source_ran_ok:PUBMED_CONCEPT_QUERY"],
        },
        {"query": "123[uid]", "kind": "PMID_ENUMERATION", "features": ["uid_field:[uid]"]},
    ]
    assert rc["screening_auditable"] is True
    assert rc["retrieval_auditable"] is True
    assert "distinction" not in rc
    assert "retraction" not in rc
