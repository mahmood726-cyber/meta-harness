"""Prospective validation must not silently downgrade live discovery to cache replay.

These are offline, isolated assurance tests. They do NOT constitute an
independent, held-out review or a successful external retrieval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts import run_prospective_topic as runner


def _dump(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, sort_keys=True), encoding="utf-8")


def _live_snapshot(out_dir: Path, slug: str = "plant") -> Path:
    snapshot = out_dir / "cache" / slug / "snapshots" / "2026-10-23-plant"
    raw_path = snapshot / "raw" / "pubmed" / "001.json"
    raw = json.dumps({"source_id": "pubmed_concept_query#1", "status": 200, "body_bytes_b64": "e30=", "body_sha256": hashlib.sha256(b"{}").hexdigest()}).encode("utf-8")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(raw)
    index = [
        {
            "source_id": "pubmed_concept_query#1",
            "status": 200,
            "path": "raw/pubmed/001.json",
            "file_sha256": hashlib.sha256(raw).hexdigest(),
        }
    ]
    index_path = snapshot / "raw" / "INDEX.json"
    _dump(index_path, index)
    index_sha = hashlib.sha256(index_path.read_bytes()).hexdigest()
    _dump(
        snapshot / runner.acquisition.LEDGER_FILENAME,
        {"snapshot": {"mode": "REFRESH", "raw_calls": 1, "raw_index_sha256": index_sha},
         "sources": [{"source_id": "pubmed_concept_query#1", "kind": "PUBMED_CONCEPT_QUERY",
                      "discovery_capable": True, "query": "(plant) AND (intervention)",
                      "state": "RAN_ZERO", "funnel": {"cap": {"kind": "none"}}}]},
    )
    _dump(snapshot / "records.json", {"records": []})
    return snapshot


@pytest.mark.parametrize("relative", ["records.json", "cache/plant/records.json"])
def test_preseeded_replay_is_refused_before_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, relative: str
) -> None:
    out_dir = tmp_path / "run"
    _dump(out_dir / relative, {"records": []})
    refresh = Mock(side_effect=AssertionError("must not refresh/replay a pre-seeded run"))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)

    with pytest.raises(runner.prospective.ProspectiveRefusal, match="pre-existing records"):
        runner._load_or_refresh({"slug": "plant"}, out_dir, "2026-10-23")
    refresh.assert_not_called()


def test_fresh_raw_archived_snapshot_is_admitted_for_processing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out_dir = tmp_path / "run"
    snapshot = _live_snapshot(out_dir)
    refresh = Mock(return_value=str(snapshot))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)

    records, cache_dir, from_cache = runner._load_or_refresh(
        {"slug": "plant"}, out_dir, "2026-10-23"
    )
    refresh.assert_called_once_with({"slug": "plant"}, "2026-10-23", root=str(out_dir))
    assert records == {"records": []}
    assert cache_dir == snapshot
    assert from_cache is False  # a live fixture check, NOT external validation


@pytest.mark.parametrize(
    "mutate,refusal",
    [
        ("replay_mode", "must carry a REFRESH"),
        ("zero_raw", "no archived raw HTTP calls"),
        ("missing_index", "no raw/INDEX.json"),
        ("index_tampered", "raw index SHA256 differs"),
        ("wrong_count", "raw index count differs"),
        ("missing_raw", "raw response missing"),
        ("bad_raw_digest", "raw response SHA256 differs"),
        ("path_traversal", "raw response missing or outside"),
    ],
)
def test_freshness_provenance_fail_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mutate: str, refusal: str
) -> None:
    out_dir = tmp_path / "run"
    snapshot = _live_snapshot(out_dir)
    ledger_path = snapshot / runner.acquisition.LEDGER_FILENAME
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    raw_index = snapshot / "raw" / "INDEX.json"
    if mutate == "replay_mode":
        ledger["snapshot"]["mode"] = "REPLAY"
    elif mutate == "zero_raw":
        ledger["snapshot"]["raw_calls"] = 0
    elif mutate == "missing_index":
        raw_index.unlink()
    elif mutate == "index_tampered":
        raw_index.write_text("[]", encoding="utf-8")
    elif mutate == "wrong_count":
        ledger["snapshot"]["raw_calls"] = 2
    elif mutate == "missing_raw":
        (snapshot / "raw" / "pubmed" / "001.json").unlink()
    elif mutate == "bad_raw_digest":
        (snapshot / "raw" / "pubmed" / "001.json").write_text("edited", encoding="utf-8")
    elif mutate == "path_traversal":
        rows = json.loads(raw_index.read_text(encoding="utf-8"))
        rows[0]["path"] = "../elsewhere.json"
        _dump(raw_index, rows)
        ledger["snapshot"]["raw_index_sha256"] = hashlib.sha256(raw_index.read_bytes()).hexdigest()
    _dump(ledger_path, ledger)
    monkeypatch.setattr(runner.acquisition, "refresh", lambda *_args, **_kw: str(snapshot))

    with pytest.raises(runner.prospective.ProspectiveRefusal, match=refusal):
        runner._load_or_refresh({"slug": "plant"}, out_dir, "2026-10-23")


def test_runner_records_cached_input_as_failed_invariant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "topic.json"
    _dump(config_path, {"slug": "plant"})
    out_dir = tmp_path / "run"
    _dump(out_dir / "records.json", {"records": []})
    monkeypatch.setattr(
        runner.prospective, "load_declaration",
        lambda *_: {"invariants": [], "time_limit_s": 60},
    )
    monkeypatch.setattr(runner.prospective, "check_declaration_frozen", lambda *_: None)
    monkeypatch.setattr(
        runner.prospective, "run_record",
        lambda *args, **_kw: {"run_id": "run-plant", "outcome": args[5]},
    )
    refresh = Mock(side_effect=AssertionError("pre-seeded records must not trigger fetch"))
    monkeypatch.setattr(runner.acquisition, "refresh", refresh)

    result = runner.run_topic("batch-plant", str(config_path), str(out_dir))
    assert result["outcome"] == "FAILED_INVARIANT"
    assert json.loads((out_dir / "run_record.json").read_text())["outcome"] == "FAILED_INVARIANT"
    failure = json.loads((out_dir / "failure.json").read_text())
    assert failure["type"] == "ProspectiveRefusal"
    assert "pre-existing records" in failure["message"]
    refresh.assert_not_called()


@pytest.mark.parametrize("scenario", ["pmid_only", "failed_concept", "capped_concept", "unarchived_concept"])
def test_runner_rejects_nonconcept_or_incomplete_discovery(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, scenario: str
) -> None:
    out_dir = tmp_path / "run"
    snapshot = _live_snapshot(out_dir)
    ledger_path = snapshot / runner.acquisition.LEDGER_FILENAME
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    source = ledger["sources"][0]
    if scenario == "pmid_only":
        source["kind"] = "PUBMED_PMID_ENUMERATION"
        source["discovery_capable"] = False
    elif scenario == "failed_concept":
        source["state"] = "RAN_ERROR"
    elif scenario == "capped_concept":
        source["funnel"]["cap"] = {"kind": "hard_hits_cap", "n": 20, "remainder": 3}
    elif scenario == "unarchived_concept":
        source["source_id"] = "pubmed_concept_query#2"
    _dump(ledger_path, ledger)
    monkeypatch.setattr(runner.acquisition, "refresh", lambda *_args, **_kwargs: str(snapshot))
    with pytest.raises(runner.prospective.ProspectiveRefusal, match="prospective concept discovery refused"):
        runner._load_or_refresh({"slug": "plant"}, out_dir, "2026-10-23")
