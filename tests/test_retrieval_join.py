import json
import shutil
import uuid
from pathlib import Path

from harness import pipeline
from harness.canonical import canonical_json


def _config():
    return {
        "title": "Synthetic retrieval join",
        "question": "Does the ledger join?",
        "primary_outcome": {
            "name": "Mortality",
            "keywords": ["mortality"],
            "estimand": "RR",
            "population": "intention-to-treat",
        },
        "include": {
            "population_any": ["condition"],
            "intervention_any": ["drug"],
            "comparator_any": ["placebo"],
        },
        "intervention_terms": ["drug"],
        "comparator_terms": ["placebo"],
        "positive_control_pmids": [],
        "negative_control_pmids": [],
        "comparator_pmid": "999",
    }


def _records():
    return {
        "fetched_utc": "2026-09-14",
        "pubmed_queries": ["condition AND drug"],
        "ctgov_query": {"condition": "condition", "intervention": "drug"},
        "records": [
            {
                "id": "111",
                "id_type": "pmid",
                "title": "Drug versus placebo for condition: a randomized trial",
                "abstract": (
                    "This randomized controlled trial enrolled condition patients. "
                    "Drug was compared with placebo. Mortality was not reported."
                ),
                "pubtypes": ["Randomized Controlled Trial"],
                "acronym": "ALPHA",
                "year": "2020",
            },
            {
                "id": "222",
                "id_type": "pmid",
                "title": "Drug placebo condition randomized trial",
                "abstract": (
                    "A randomized trial in condition patients compared drug with placebo. "
                    "Mortality was not reported."
                ),
                "pubtypes": ["Randomized Controlled Trial"],
                "year": "2021",
            },
        ],
    }


def _ledger(slug):
    return {
        "version": 1,
        "slug": slug,
        "snapshot": {
            "records_sha256": "fedcba9876543210",
            "retrieved_utc": "2026-09-14",
            "mode": "REFRESH",
            "engine_sha": "engine",
        },
        "record_cap": {"retrieved": 2, "retained": 2, "n": 40, "remainder": 0},
        "sources": [
            {
                "source_id": "pubmed#1",
                "kind": "PUBMED_CONCEPT_QUERY",
                "query": "condition AND drug",
                "run_utc": "2026-09-14",
                "state": "RAN_OK",
                "error": None,
                "discovery_capable": True,
                "funnel": {"hits": 2, "fetched": 2, "retained": 2, "cap": {"kind": "none", "n": None, "remainder": None}},
                "record_ids": ["111", "222"],
            },
            {
                "source_id": "pubmed#2",
                "kind": "PUBMED_LEGACY_QUERY",
                "query": "broken query",
                "run_utc": "2026-09-14",
                "state": "RAN_ERROR",
                "error": "HTTP 500",
                "discovery_capable": True,
                "funnel": {"hits": None, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}},
                "record_ids": [],
            },
            {
                "source_id": "epmc#1",
                "kind": "EUROPEPMC_QUERY",
                "query": "zero query",
                "run_utc": "2026-09-14",
                "state": "RAN_ZERO",
                "error": None,
                "discovery_capable": True,
                "funnel": {"hits": 0, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}},
                "record_ids": [],
            },
            {
                "source_id": "ctgov#1",
                "kind": "CTGOV_SEARCH",
                "query": "condition/drug",
                "run_utc": "2026-09-14",
                "state": "NOT_RUN",
                "error": None,
                "discovery_capable": True,
                "funnel": {"hits": None, "fetched": 0, "retained": 0, "cap": {"kind": "none", "n": None, "remainder": None}},
                "record_ids": [],
            },
        ],
        "records": {"111": {"found_by": ["pubmed#1"]}},
    }


def _prepare_root(tmp_path, slug):
    (tmp_path / "protocols").mkdir(parents=True)
    (tmp_path / "cache" / slug).mkdir(parents=True)
    (tmp_path / "protocols" / f"{slug}.md").write_text(
        "**Estimand:** - risk ratio (RR)\n**Population:** - intention-to-treat\n",
        encoding="utf-8",
    )


def test_build_review_core_joins_retrieval_ledger(monkeypatch):
    slug = "__plant_join__"
    temp_root = Path.cwd() / ".tmp_retrieval_join" / uuid.uuid4().hex
    try:
        _prepare_root(temp_root, slug)
        monkeypatch.setattr(pipeline, "ROOT", str(temp_root))

        baseline = pipeline.build_review_core(slug, _config(), _records(), "proto-sha")
        assert "retrieval" not in baseline["search"]
        assert all("found_by" not in r for r in baseline["screening"]["records"])

        ledger_path = temp_root / "cache" / slug / "retrieval_ledger.json"
        ledger_path.write_text(json.dumps(_ledger(slug)), encoding="utf-8")
        core = pipeline.build_review_core(slug, _config(), _records(), "proto-sha")

        retrieval = core["search"]["retrieval"]
        assert retrieval["snapshot"]["records_sha256"] == "fedcba9876543210"
        assert retrieval["state_counts"] == {"RAN_OK": 1, "RAN_ZERO": 1, "RAN_ERROR": 1, "NOT_RUN": 1}
        assert retrieval["discovery_capable_sources"] == 4
        assert retrieval["enumeration_only"] is False
        assert all("record_ids" not in src for src in retrieval["sources"])
        assert core["search"]["source_status"]["PubMed"] == "RAN_ERROR"

        by_id = {r["id"]: r for r in core["screening"]["records"]}
        assert by_id["ALPHA · 111"]["found_by"] == ["pubmed#1"]
        assert by_id["222"]["found_by"] == ["UNRECORDED"]

        ledger_path.unlink()
        rebuilt_absent = pipeline.build_review_core(slug, _config(), _records(), "proto-sha")
        assert canonical_json(rebuilt_absent) == canonical_json(baseline)
        assert "retrieval" not in rebuilt_absent["search"]
        assert all("found_by" not in r for r in rebuilt_absent["screening"]["records"])
    finally:
        shutil.rmtree(temp_root.parent, ignore_errors=True)
