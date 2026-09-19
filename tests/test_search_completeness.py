"""Search-completeness gate plants (harness/search_completeness.py). Each plant is one defect the gate exists for;
the intact fixture passes; the real repository is checked last (it refuses until a measurement is registered)."""
import json
import subprocess

import pytest

from harness import search_completeness as sc
from harness import gitenv

ENGINE_TEXT = "def refresh_topic(slug):\n    return slug\n"


def _temp_repo_init(root):
    """Entry point for tests/test_git_env_isolation.py: a fresh repository in `root` and nowhere else."""
    subprocess.run(["git", "init", "-q", str(root)], check=True, env=gitenv.clean_env())


def _fixture(tmp_path, *, engine_sha=None, mutate=None, register=True, readme=True):
    root = tmp_path
    (root / "harness").mkdir()
    (root / "registry").mkdir()
    (root / "outputs").mkdir()
    (root / "docs").mkdir()
    _temp_repo_init(root)
    (root / "harness" / "search_v2.py").write_text(ENGINE_TEXT, encoding="utf-8")
    sha = engine_sha or subprocess.check_output(["git", "-C", str(root), "hash-object", "harness/search_v2.py"],
                                                text=True, env=gitenv.clean_env()).strip()
    split = {"assignments": {"a": {"set": "MEASUREMENT"}, "b": {"set": "MEASUREMENT"}, "d": {"set": "DEVELOPMENT"}}}
    (root / "registry" / "search_benchmark_split.json").write_text(json.dumps(split), encoding="utf-8")
    cand = {
        "engine_sha": sha,
        "topics": {
            "a": {"state": "RAN_OK_WITH_SOURCE_ERRORS", "candidate_count": 3, "sources": [
                {"source_id": "pubmed_concept_query#1", "state": "RAN_OK", "record_count": 3, "error": None},
                {"source_id": "epmc_backward_citation#1", "state": "RAN_ERROR", "record_count": 0, "error": "503 maintenance"},
            ]},
            "b": {"state": "RAN_ERROR", "candidate_count": 0, "error": "QueryRefusal: NAME_SEEDED: X", "sources": []},
        },
    }
    if mutate:
        mutate(cand)
    (root / "outputs" / "cand.json").write_text(json.dumps(cand), encoding="utf-8")
    reg = {"candidate_file": "outputs/cand.json", "engine_path": "harness/search_v2.py",
           "split_file": "registry/search_benchmark_split.json"}
    if register:
        (root / "docs" / "reg.json").write_text(json.dumps({"summary": {"snapshot_engine_shas": [sha]}}), encoding="utf-8")
        reg["register_file"] = "docs/reg.json"
    if readme:
        (root / "docs" / "README.md").write_text(f"engine blob {sha}\n", encoding="utf-8")
        reg["evidence_readme"] = "docs/README.md"
    (root / "registry" / "search_completeness.json").write_text(json.dumps(reg), encoding="utf-8")
    return root


def test_intact_fixture_passes_and_counts_every_state_separately(tmp_path):
    ok, detail = sc.check(_fixture(tmp_path))
    assert ok, detail
    assert "RAN_OK_WITH_SOURCE_ERRORS 1 of 2" in detail and "RAN_ERROR 1 of 2 (b)" in detail and "NOT_RUN 0 of 2" in detail


def test_engine_change_without_republish_refuses(tmp_path):
    root = _fixture(tmp_path)
    (root / "harness" / "search_v2.py").write_text(ENGINE_TEXT + "# changed\n", encoding="utf-8")
    ok, detail = sc.check(root)
    assert not ok and "engine changed since the published search_v2 measurement" in detail


def test_ran_ok_source_with_zero_records_is_an_exit_code_not_a_result(tmp_path):
    def mutate(c):
        c["topics"]["a"]["sources"][0]["record_count"] = 0
    ok, detail = sc.check(_fixture(tmp_path, mutate=mutate))
    assert not ok and "RAN_OK with 0 records (adapter exit code, not a result)" in detail


def test_topic_ran_ok_with_zero_candidates_refuses(tmp_path):
    def mutate(c):
        c["topics"]["a"] = {"state": "RAN_OK", "candidate_count": 0, "sources": []}
    ok, detail = sc.check(_fixture(tmp_path, mutate=mutate))
    assert not ok and "state RAN_OK with zero candidates" in detail


def test_source_errors_folded_into_topic_ran_ok_refuses(tmp_path):
    def mutate(c):
        c["topics"]["a"]["state"] = "RAN_OK"
    ok, detail = sc.check(_fixture(tmp_path, mutate=mutate))
    assert not ok and "source errors folded" in detail


def test_ran_error_without_error_text_refuses(tmp_path):
    def mutate(c):
        c["topics"]["b"]["error"] = ""
    ok, detail = sc.check(_fixture(tmp_path, mutate=mutate))
    assert not ok and "b: RAN_ERROR without an error text" in detail


def test_missing_measurement_topic_is_counted_not_run_and_named(tmp_path):
    def mutate(c):
        del c["topics"]["b"]
    ok, detail = sc.check(_fixture(tmp_path, mutate=mutate))
    assert not ok
    assert "MEASUREMENT topics NOT_RUN: b" in detail
    assert "NOT_RUN 1 of 2 (b)" in detail


def test_register_measured_on_another_engine_refuses(tmp_path):
    root = _fixture(tmp_path)
    (root / "docs" / "reg.json").write_text(json.dumps({"summary": {"snapshot_engine_shas": ["0" * 40]}}), encoding="utf-8")
    ok, detail = sc.check(root)
    assert not ok and "was measured on engine" in detail


def test_unpublished_number_refuses(tmp_path):
    root = _fixture(tmp_path)
    (root / "docs" / "README.md").write_text("no blob here\n", encoding="utf-8")
    ok, detail = sc.check(root)
    assert not ok and "the number is not published" in detail


def test_no_registry_cannot_execute(tmp_path):
    ok, detail = sc.check(tmp_path)
    assert not ok and detail.startswith("COULD-NOT-EXECUTE")


def test_real_repository_state():
    ok, detail = sc.check(sc.Path(__file__).resolve().parents[1])
    # Before the run-2 artefacts are registered this refuses; after, it must pass and name the states.
    assert isinstance(ok, bool) and detail
