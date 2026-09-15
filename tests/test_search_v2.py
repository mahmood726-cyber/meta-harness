import json
from pathlib import Path

import pytest

from harness import search_v2
from harness.pipeline import RETRIEVAL_RETRACTION, classify_retrieval


@pytest.mark.parametrize(
    ("query", "kind", "token"),
    [
        ("FAIR-HF2 JAMA 2025 randomized clinical trial", "NAME_SEEDED", "FAIR-HF2"),
        ("10.1056/NEJMoa000000", "IDENTIFIER_SEEDED", "10.1056/NEJMoa000000"),
        ("40159390", "IDENTIFIER_SEEDED", "40159390"),
        ("NCT01234567", "IDENTIFIER_SEEDED", "NCT01234567"),
        ("Dapagliflozin[Title] randomized placebo", "TITLE_ANCHORED", "[Title]"),
        ("12345678[uid]", "PMID_ENUMERATION", "[uid]"),
    ],
)
def test_search_v2_refuses_seeded_queries_with_offending_token(query, kind, token):
    with pytest.raises(search_v2.QueryRefusal) as exc:
        search_v2.assert_discovery_query_allowed(query, "plant")
    message = str(exc.value)
    assert kind in message
    assert token in message


def test_search_v2_builder_allows_development_drug_codes_without_seeded_trial_names():
    cfg = {
        "intervention_agents": {
            "dabigatran": ["dabigatran", "BIBR 1048", "BIBR1048"],
            "rivaroxaban": ["rivaroxaban", "BAY 59-7939"],
            "apixaban": ["apixaban", "BMS-562247"],
            "edoxaban": ["edoxaban", "DU-176b", "DU 176b"],
        },
        "intervention_class_terms": ["direct oral anticoagulant", "DOAC", "NOAC"],
        "include": {"population_any": ["venous thromboembolism", "VTE", "DVT", "PE"]},
        "comparator_terms": ["warfarin", "VKA"],
    }
    queries = search_v2.build_queries(cfg, "## PICO\n- P adults with VTE\n", lookup_mesh=False)

    assert queries["structural_kinds"] == {
        "pubmed": "FREE_TEXT_KEYWORD",
        "europepmc": "FREE_TEXT_KEYWORD",
        "ctgov": "FREE_TEXT_KEYWORD",
    }
    assert "bibr 1048" in queries["pubmed"]
    assert queries["rct_filter"] == search_v2.COCHRANE_RCT_FILTER_NAME


def test_search_v2_replay_reads_records_json_bit_identically(tmp_path, monkeypatch):
    monkeypatch.setattr(search_v2, "ROOT", str(tmp_path))
    snapshot = tmp_path / "cache" / "plant" / "snapshots" / "2026-09-15-search_v2"
    snapshot.mkdir(parents=True)
    original = b'{\n  "records": [\n    {"id": "1", "found_by": ["pubmed_concept_query#1"]}\n  ]\n}\n'
    (snapshot / "records.json").write_bytes(original)

    assert search_v2.replay_snapshot("plant", str(snapshot)) == original
    assert search_v2.replay_snapshot("plant") == original


def test_search_v2_concept_sources_make_retrieval_auditable_without_retraction():
    ledger = {
        "sources": [
            {"kind": "EUROPEPMC_CONCEPT_QUERY", "state": "RAN_OK", "query": "TITLE_ABS:condition"},
            {"kind": "CTGOV_CONDITION_INTERVENTION", "state": "RAN_ZERO", "query": "condition intervention"},
        ]
    }
    rc = classify_retrieval({"pubmed_queries": []}, ledger)

    assert rc["class"] == "CONCEPT_SEARCH"
    assert rc["retrieval_auditable"] is True
    assert RETRIEVAL_RETRACTION not in json.dumps(rc)


def test_single_name_seeded_search_v2_ledger_is_not_concept_search():
    ledger = {"sources": [{"kind": "COMPARATOR_REFERENCE_LIST", "state": "RAN_OK", "query": "FAIR-HF2 JAMA 2025"}]}

    rc = classify_retrieval({"pubmed_queries": []}, ledger)

    assert rc["class"] == "TITLE_SEEDED_RETRIEVAL"
    assert rc["retrieval_auditable"] is False
