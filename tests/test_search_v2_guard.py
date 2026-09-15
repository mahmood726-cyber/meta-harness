"""Plants for the sealed-vocabulary exemption (docs/evidence/search-v2-guard-2026-09-15/PROTOCOL.md).

P1-P3 must fire BEFORE the rule and AFTER it (the detector stays armed; 01-plants-pre-fix.txt is the pre-fix
record); P4 is the change itself and records both answers: the guard alone (no slug, no seal) still refuses the five
sealed topics' queries, the sealed exemption allows them. A fix that clears every failure is a loosened test, so
P1-P3 are the proof this one is not. The benchmark-acronym collision check is exercised at SEAL time through
scripts/seal_search_vocabulary.py (harness/ never opens the benchmark: tests/test_search_benchmark_isolation.py).
"""
import json
import os
import subprocess

import pytest

from harness import search_v2
from harness.pipeline import classify_query
from scripts import seal_search_vocabulary as sealer

ROOT = search_v2.ROOT
SEAL_PATH = os.path.join(ROOT, search_v2.VOCABULARY_SEAL_PATH)

GUARD_REFUSED_TOPICS = {
    # slug: (offending token the guard alone refuses, the query it refuses)
    "colchicine-postop-af": ("CABG", "PUBMED_CONCEPT_QUERY"),
    "finerenone-ckd-t2d-renal": ("BAY94-8862", "CTGOV_CONDITION_INTERVENTION"),
    "pcsk9-mace": ("PCSK9", "CTGOV_CONDITION_INTERVENTION"),
    "sacubitril-valsartan-hfref": ("LCZ696", "CTGOV_CONDITION_INTERVENTION"),
    "ticagrelor-vs-clopidogrel-acs": ("NSTE-ACS", "PUBMED_CONCEPT_QUERY"),
}


def _config(slug):
    with open(os.path.join(ROOT, "topics", slug + ".json"), encoding="utf-8") as f:
        return json.load(f)


def _protocol(slug):
    with open(os.path.join(ROOT, "protocols", slug + ".md"), encoding="utf-8") as f:
        return f.read()


def _seal_row(cfg, collisions=None):
    return {"vocabulary_sha256": search_v2.vocabulary_sha(cfg),
            "benchmark_acronym_collision": {"coverage_text": "plant", "collisions": collisions or []}}


def test_p1_name_seeded_query_still_refused_with_sealed_exemption_context():
    with pytest.raises(search_v2.QueryRefusal) as exc:
        search_v2.assert_discovery_query_allowed("FAIR-HF2 JAMA 2025 randomized clinical trial", "plant", ["cabg", "pcsk9"])
    assert "NAME_SEEDED" in str(exc.value) and "FAIR-HF2" in str(exc.value)


def test_p2_benchmark_acronym_in_vocabulary_is_caught_at_seal_time_and_gets_no_exemption(tmp_path, monkeypatch):
    cfg = {
        "intervention_agents": {"balanced crystalloid": ["balanced crystalloid"]},
        "include": {"population_any": ["critically ill", "FISSH"]},
        "comparator_terms": ["saline"],
    }
    # the seal-time check, against a benchmark whose positive is registered as FISSH (name-only, acronym-shaped)
    bench_path = tmp_path / "search_benchmark.json"
    bench_path.write_text(json.dumps({"topics": {"plant": {"positives": [{"trial": "FISSH", "pmid": None, "nct": "NCT03677102"}]}}}), encoding="utf-8")
    bench = sealer.benchmark_acronyms(str(bench_path), record_paths=[])
    assert bench["coverage_text"] == "1 of 1 benchmark positives have a resolvable registered acronym"
    row = sealer.collision_row(cfg, bench)
    assert row["collisions"] == [{"term": "FISSH", "benchmark_positive": "plant:FISSH"}]
    # and a seal row carrying that collision grants no exemption: the guard alone runs and refuses FISSH
    monkeypatch.setattr(search_v2, "load_vocabulary_seal", lambda: {"slugs": {"plant-p2": _seal_row(cfg, row["collisions"])}})
    seal = search_v2.sealed_vocabulary("plant-p2", cfg)
    assert seal["sealed"] is False and "collides with a benchmark acronym" in seal["reason"]
    with pytest.raises(search_v2.QueryRefusal) as exc:
        search_v2.build_queries(cfg, "## PICO\n", lookup_mesh=False, slug="plant-p2")
    assert "NAME_SEEDED" in str(exc.value) and "FISSH" in str(exc.value)


def test_benchmark_acronym_resolves_pmid_through_cached_pubmed_nct(tmp_path):
    bench_path = tmp_path / "search_benchmark.json"
    bench_path.write_text(
        json.dumps({"topics": {"plant": {"positives": [{"trial": "positive", "pmid": "12345", "nct": None}]}}}),
        encoding="utf-8",
    )
    records_path = tmp_path / "records.json"
    records_path.write_text(
        json.dumps({"records": [
            {"id": "12345", "id_type": "pmid", "pmid": "12345", "nct": "NCT00000001"},
            {"id": "NCT00000001", "id_type": "nct", "nct": "NCT00000001", "acronym": "FOURIER"},
        ]}),
        encoding="utf-8",
    )

    bench = sealer.benchmark_acronyms(str(bench_path), record_paths=[str(records_path)])

    assert bench["coverage_text"] == "1 of 1 benchmark positives have a resolvable registered acronym"
    assert bench["acronyms"]["fourier"] == ["plant:positive"]


def test_benchmark_acronyms_can_discover_records_from_root_override(tmp_path):
    bench_path = tmp_path / "search_benchmark.json"
    bench_path.write_text(
        json.dumps({"topics": {"plant": {"positives": [{"trial": "positive", "pmid": None, "nct": "NCT00000002"}]}}}),
        encoding="utf-8",
    )
    records_dir = tmp_path / "cache" / "plant" / "snapshots" / "2026-09-15r2-search_v2"
    records_dir.mkdir(parents=True)
    (records_dir / "records.json").write_text(
        json.dumps({"records": [{"id": "NCT00000002", "id_type": "nct", "nct": "NCT00000002", "acronym": "ROOTMAP"}]}),
        encoding="utf-8",
    )

    bench = sealer.benchmark_acronyms(str(bench_path), records_root=str(tmp_path))

    assert bench["coverage_text"] == "1 of 1 benchmark positives have a resolvable registered acronym"
    assert bench["acronyms"]["rootmap"] == ["plant:positive"]


def test_p3_unsealed_vocabulary_gets_no_exemption(monkeypatch):
    cfg = {
        "intervention_agents": {"drug": ["drug", "QZXV-77"]},
        "include": {"population_any": ["heart failure"]},
        "comparator_terms": ["placebo"],
    }
    monkeypatch.setattr(search_v2, "load_vocabulary_seal", lambda: {"slugs": {}})
    with pytest.raises(search_v2.QueryRefusal) as exc:
        search_v2.build_queries(cfg, "## PICO\n", lookup_mesh=False, slug="plant-p3")
    assert "NAME_SEEDED" in str(exc.value) and "QZXV-77" in str(exc.value)
    # and a drifted seal is the same as no seal
    monkeypatch.setattr(search_v2, "load_vocabulary_seal", lambda: {"slugs": {"plant-p3": {"vocabulary_sha256": "0" * 64}}})
    seal = search_v2.sealed_vocabulary("plant-p3", cfg)
    assert seal["sealed"] is False and "drifted" in seal["reason"]
    with pytest.raises(search_v2.QueryRefusal):
        search_v2.build_queries(cfg, "## PICO\n", lookup_mesh=False, slug="plant-p3")


@pytest.mark.parametrize("slug", sorted(GUARD_REFUSED_TOPICS))
def test_p4_both_answers_guard_alone_refuses_sealed_exemption_allows(slug):
    token, label = GUARD_REFUSED_TOPICS[slug]
    cfg = _config(slug)
    protocol = _protocol(slug)
    # the known answer: the guard alone (no slug -> no seal -> no exemption) refuses exactly this token
    with pytest.raises(search_v2.QueryRefusal) as exc:
        search_v2.build_queries(cfg, protocol, lookup_mesh=False)
    assert f"{label} refused NAME_SEEDED: {token}" in str(exc.value)
    # the intended change: with the committed seal, the same config builds
    queries = search_v2.build_queries(cfg, protocol, lookup_mesh=False, slug=slug)
    assert queries["structural_kinds"] == {
        "pubmed": "FREE_TEXT_KEYWORD",
        "europepmc": "FREE_TEXT_KEYWORD",
        "ctgov": "FREE_TEXT_KEYWORD",
        "isrctn": "FREE_TEXT_KEYWORD",
    }
    ex = queries["vocabulary_exemption"]
    assert ex["sealed"] is True
    assert token.lower() in [t.lower() for t in ex["exempted_tokens_in_queries"]]
    assert ex["benchmark_acronym_collision_check"].endswith("benchmark positives have a resolvable registered acronym")


def test_public_classifier_without_context_is_unchanged():
    assert classify_query("colchicine CABG randomized placebo trial") == "NAME_SEEDED"
    assert classify_query("colchicine CABG randomized placebo trial", ["cabg"]) == "FREE_TEXT_KEYWORD"
    assert classify_query("FAIR-HF2 JAMA 2025 randomized clinical trial ferric carboxymaltose") == "NAME_SEEDED"
    assert classify_query("hydrocortisone severe community-acquired pneumonia randomized placebo mortality") == "FREE_TEXT_KEYWORD"


def test_seal_registry_matches_working_tree_for_every_sealed_slug():
    with open(SEAL_PATH, encoding="utf-8") as f:
        seal = json.load(f)
    slugs = seal.get("slugs") or {}
    assert len(slugs) == 32, "the seal covers the 32 split topics"
    drift = []
    collisions = []
    for slug, row in slugs.items():
        working = search_v2.vocabulary_sha(_config(slug))
        if working != row["vocabulary_sha256"]:
            drift.append(slug)
        if row["benchmark_acronym_collision"]["collisions"]:
            collisions.append(slug)
    assert drift == [], f"vocabulary drifted from its seal (re-seal in its own commit): {drift}"
    assert collisions == [], f"sealed vocabulary collides with a benchmark acronym: {collisions}"
    reg = seal["benchmark_acronym_registry"]
    assert reg["coverage_text"].startswith(f"{reg['resolved']} of {reg['positives']}")
    assert reg["positives"] >= 278 and "fissh" in reg["acronyms"]


def test_seal_was_taken_from_the_split_seal_commit_not_the_working_tree():
    with open(SEAL_PATH, encoding="utf-8") as f:
        seal = json.load(f)
    commit = seal["sealed_from_commit"]
    assert commit.startswith("41a466fb"), commit
    for slug in sorted(GUARD_REFUSED_TOPICS):
        blob = subprocess.check_output(["git", "-C", ROOT, "rev-parse", f"{commit}:topics/{slug}.json"], text=True).strip()
        assert blob == seal["slugs"][slug]["config_blob_at_seal"]
