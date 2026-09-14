from harness.pipeline import (
    CONCEPT_SEARCH_LABEL,
    KNOWN_ITEM_RETRIEVAL_LABEL,
    RETRIEVAL_UNAUDITABLE_DISTINCTION,
    TITLE_SEEDED_RETRIEVAL_LABEL,
    classify_retrieval,
)


def test_all_uid_queries_are_known_item_retrieval():
    rc = classify_retrieval({"pubmed_queries": ["123[uid] OR 456[uid]"]})
    assert rc["class"] == "KNOWN_ITEM_RETRIEVAL"
    assert rc["label"] == KNOWN_ITEM_RETRIEVAL_LABEL
    assert rc["basis"] == [{"query": "123[uid] OR 456[uid]", "kind": "PMID_ENUMERATION"}]
    assert rc["screening_auditable"] is True
    assert rc["retrieval_auditable"] is False
    assert rc["distinction"] == RETRIEVAL_UNAUDITABLE_DISTINCTION


def test_mixed_uid_and_seeded_queries_are_title_seeded_retrieval():
    rc = classify_retrieval({"pubmed_queries": ["123[uid]", '"named trial"[Title]']})
    assert rc["class"] == "TITLE_SEEDED_RETRIEVAL"
    assert rc["label"] == TITLE_SEEDED_RETRIEVAL_LABEL
    assert rc["basis"] == [
        {"query": "123[uid]", "kind": "PMID_ENUMERATION"},
        {"query": '"named trial"[Title]', "kind": "TITLE_OR_NAME_SEEDED"},
    ]
    assert rc["retrieval_auditable"] is False
    assert rc["distinction"] == RETRIEVAL_UNAUDITABLE_DISTINCTION


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
        {"query": "condition AND drug", "kind": "CONCEPT"},
        {"query": "123[uid]", "kind": "PMID_ENUMERATION"},
    ]
    assert rc["screening_auditable"] is True
    assert rc["retrieval_auditable"] is True
    assert "distinction" not in rc
