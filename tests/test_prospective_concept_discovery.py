"""Structural-only prospective gate tests; NOT an independent literature search."""
from __future__ import annotations

from copy import deepcopy

import pytest

from harness.prospective_discovery import concept_discovery_failures


def _source(**changes):
    source = {
        "source_id": "pubmed_concept_query#1",
        "kind": "PUBMED_CONCEPT_QUERY",
        "discovery_capable": True,
        "query": "(heart failure) AND (drug intervention)",
        "state": "RAN_OK",
        "funnel": {"cap": {"kind": "none"}},
    }
    source.update(changes)
    return source


def _raw(source_id="pubmed_concept_query#1", status=200):
    # Synthetic archive-index metadata only; not a real PubMed API response.
    return [{
        "source_id": source_id,
        "status": status,
        "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        "params": {"db": "pubmed", "term": "(heart failure) AND (drug intervention)"},
    }]


def test_completed_concept_query_with_preserved_success_response_is_structurally_admissible():
    assert concept_discovery_failures({"sources": [_source()]}, _raw()) == []


def test_true_zero_hits_with_archived_success_is_not_a_network_error():
    assert concept_discovery_failures({"sources": [_source(state="RAN_ZERO")]}, _raw()) == []


def test_registry_condition_intervention_is_an_explicit_concept_kind():
    source = _source(kind="CTGOV_CONDITION_INTERVENTION", source_id="ctgov_condition_intervention#1")
    assert concept_discovery_failures({"sources": [source]}, _raw(source_id=source["source_id"])) == []


@pytest.mark.parametrize("sources,raw,expected", [
    ([], _raw(), "no declared concept-query"),
    ([_source(kind="PUBMED_PMID_ENUMERATION")], _raw(), "no declared concept-query"),
    ([_source(kind="PUBMED_LEGACY_QUERY")], _raw(), "no declared concept-query"),
    ([_source(kind="MODEL_CALL")], _raw(), "no declared concept-query"),
    ([_source(discovery_capable=False)], _raw(), "not marked discovery-capable"),
    ([_source(query="  ")], _raw(), "concept query absent"),
    ([_source(state="NOT_RUN")], _raw(), "did not complete"),
    ([_source(state="RAN_ERROR")], _raw(), "did not complete"),
    ([_source(state="RAN_UNRECORDED")], _raw(), "did not complete"),
    ([_source(funnel={"cap": {"kind": "hard_hits_cap", "n": 20, "remainder": 10}})], _raw(), "capped"),
    ([_source(funnel={})], _raw(), "cap status is unknown"),
    ([_source()], _raw(source_id="extra_pmids#1"), "no archived successful"),
    ([_source()], _raw(status=500), "no archived successful"),
    ([_source()], _raw(status="200"), "no archived successful"),
    ([_source(source_id=None)], _raw(), "no archived successful"),
])
def test_incomplete_or_seeded_search_cannot_pass_as_prospective(sources, raw, expected):
    assert any(expected in item for item in concept_discovery_failures({"sources": deepcopy(sources)}, deepcopy(raw)))


def test_one_successful_source_cannot_hide_second_failed_planned_concept_source():
    other = _source(source_id="europepmc_concept_query#1", kind="EUROPEPMC_CONCEPT_QUERY", state="RAN_ERROR")
    failures = concept_discovery_failures({"sources": [_source(), other]}, _raw())
    assert any("europepmc_concept_query#1" in reason and "did not complete" in reason for reason in failures)


def test_malformed_source_ledger_fails_closed():
    assert concept_discovery_failures({"sources": None}, _raw())
    assert concept_discovery_failures({}, _raw())


@pytest.mark.parametrize("mutation", [
    "pmid_seed_instead_of_concept",
    "different_concept",
    "missing_term",
    "missing_params",
    "wrong_database",
    "wrong_endpoint",
])
def test_pubmed_request_must_match_declared_concept(mutation):
    # These cases previously passed because source_id + HTTP 200 was enough.
    raw = _raw()
    if mutation == "pmid_seed_instead_of_concept":
        raw[0]["params"]["term"] = "123456[uid]"
    elif mutation == "different_concept":
        raw[0]["params"]["term"] = "(asthma) AND (steroid)"
    elif mutation == "missing_term":
        raw[0]["params"].pop("term")
    elif mutation == "missing_params":
        raw[0].pop("params")
    elif mutation == "wrong_database":
        raw[0]["params"]["db"] = "protein"
    elif mutation == "wrong_endpoint":
        raw[0]["url"] = "https://example.org/search"
    failures = concept_discovery_failures({"sources": [_source()]}, raw)
    assert any("archived PubMed search request differs" in reason for reason in failures)


def test_all_pubmed_pagination_requests_must_use_the_declared_query():
    first, = _raw()
    second = deepcopy(first)
    second["params"]["retstart"] = 1000
    assert concept_discovery_failures({"sources": [_source()]}, [first, second]) == []
    second["params"]["term"] = "987654[uid]"
    assert any(
        "archived PubMed search request differs" in reason
        for reason in concept_discovery_failures({"sources": [_source()]}, [first, second])
    )
