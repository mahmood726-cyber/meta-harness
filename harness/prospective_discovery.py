"""Fail-closed concept-discovery evidence check for prospective runs.

This is a structural acquisition gate, not proof of exhaustive retrieval or
independent clinical validation. Legacy replay and other workflows are unchanged.
"""
from __future__ import annotations

from typing import Any

CONCEPT_KINDS = frozenset({
    "PUBMED_CONCEPT_QUERY",
    "EUROPEPMC_CONCEPT_QUERY",
    "CTGOV_CONDITION_INTERVENTION",
    "ISRCTN_CONDITION_INTERVENTION",
})


def concept_discovery_failures(ledger: dict[str, Any], raw_rows: list[dict[str, Any]]) -> list[str]:
    """Check all declared concept sources and require an archived live query.

    A successful seeded PMID lookup, title search or citation chase cannot
    substitute for a concept search. RAN_ZERO is valid only with a recorded
    successful API response: zero evidence is not a failed request.
    """
    sources = ledger.get("sources") if isinstance(ledger, dict) else None
    if not isinstance(sources, list):
        return ["prospective discovery requires a source-level retrieval ledger"]
    if not isinstance(raw_rows, list):
        return ["prospective discovery requires a raw response index"]

    successful_raw_sources = {
        row.get("source_id")
        for row in raw_rows
        if isinstance(row, dict)
        and isinstance(row.get("source_id"), str)
        and type(row.get("status")) is int
        and 200 <= row["status"] < 300
    }
    concept_sources = [
        source for source in sources
        if isinstance(source, dict) and source.get("kind") in CONCEPT_KINDS
    ]
    if not concept_sources:
        return ["prospective discovery has no declared concept-query source"]

    failures: list[str] = []
    for source in concept_sources:
        source_id = source.get("source_id")
        label = source_id if isinstance(source_id, str) and source_id else "<unnamed>"
        if source.get("discovery_capable") is not True:
            failures.append(f"{label}: concept query not marked discovery-capable")
        if not isinstance(source.get("query"), str) or not source["query"].strip():
            failures.append(f"{label}: concept query absent")
        if source.get("state") not in {"RAN_OK", "RAN_ZERO"}:
            failures.append(f"{label}: concept query did not complete successfully")
        funnel = source.get("funnel")
        cap = funnel.get("cap") if isinstance(funnel, dict) else None
        if not isinstance(cap, dict) or cap.get("kind") != "none":
            failures.append(f"{label}: concept query was capped or cap status is unknown")
        if not isinstance(source_id, str) or not source_id or source_id not in successful_raw_sources:
            failures.append(f"{label}: concept query has no archived successful HTTP response")
    return failures
