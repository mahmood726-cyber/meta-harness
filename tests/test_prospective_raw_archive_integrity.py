"""Synthetic byte-integrity regressions for actual acquisition raw snapshots.

These run the repository's RawRecorder and prospective gate, not a live API
search, independent study discovery, blinded review, or scientific validation.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

import pytest

from harness import acquisition
from harness import prospective
from scripts import run_prospective_topic as runner


def _snapshot(tmp_path: Path) -> tuple[Path, dict]:
    slug = "synthetic-archive"
    record = {"id": "101"}
    ledger = acquisition.new_ledger(slug)
    sid = acquisition.add_source(
        ledger, "PUBMED_LEGACY_QUERY", "concept[tiab]", "2026-10-24",
        "RAN_OK", None,
        {
            "hits": 1, "fetched": 1, "retained": 1,
            "cap": {"kind": "none", "n": None, "remainder": None},
        },
        ["101"], True,
    )
    acquisition.attach_records(ledger, sid, ["101"])
    acquisition.finalize(ledger, [record], "2026-10-24", "REFRESH")
    recorder = acquisition.RawRecorder()
    recorder.record(
        sid, "https://example.invalid/api", {"q": "concept"},
        200, b'{"mock_response":true}', "harness.acquisition.esearch_all",
    )
    snapshot = Path(acquisition.write_snapshot(
        slug,
        {"slug": slug, "records": [record], "_raw_recorder": recorder},
        ledger,
        root=str(tmp_path),
    ))
    return snapshot, ledger


def _index(snapshot: Path) -> list[dict]:
    return json.loads((snapshot / "raw" / "INDEX.json").read_text(encoding="utf-8"))


def _rewrite_index(snapshot: Path, ledger: dict, entries: list[dict]) -> None:
    raw = json.dumps(entries, indent=2).encode("utf-8")
    (snapshot / "raw" / "INDEX.json").write_bytes(raw)
    ledger["snapshot"]["raw_index_sha256"] = hashlib.sha256(raw).hexdigest()


def test_actual_recorder_archive_passes_byte_verification(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    paths = runner._verify_prospective_raw_archive(snapshot, ledger)
    assert len(paths) == 2
    assert paths[0] == snapshot / "raw" / "INDEX.json"
    assert all(path.is_file() for path in paths)


def test_refuses_tampered_index_before_consuming_sources(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    (snapshot / "raw" / "INDEX.json").write_bytes(b'[]')
    with pytest.raises(prospective.ProspectiveRefusal, match="index SHA256 mismatch"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_missing_recorded_body(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    (snapshot / _index(snapshot)[0]["path"]).unlink()
    with pytest.raises(prospective.ProspectiveRefusal, match="body missing"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_tampered_body_file_sha(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    path = snapshot / _index(snapshot)[0]["path"]
    path.write_bytes(path.read_bytes() + b" ")
    with pytest.raises(prospective.ProspectiveRefusal, match="file SHA256 mismatch"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_modified_body_even_when_outer_receipts_rehashed(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    entries = _index(snapshot)
    path = snapshot / entries[0]["path"]
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["body_bytes_b64"] = base64.b64encode(b'{"changed":true}').decode("ascii")
    new_raw = json.dumps(payload).encode("utf-8")
    path.write_bytes(new_raw)
    entries[0]["file_sha256"] = hashlib.sha256(new_raw).hexdigest()
    _rewrite_index(snapshot, ledger, entries)
    with pytest.raises(prospective.ProspectiveRefusal, match="body SHA256 mismatch"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_index_metadata_drift_even_if_index_rehashed(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    entries = _index(snapshot)
    entries[0]["url"] = "https://example.invalid/altered"
    _rewrite_index(snapshot, ledger, entries)
    with pytest.raises(prospective.ProspectiveRefusal, match="provenance mismatch: url"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_no_recorded_api_calls(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    ledger["snapshot"]["raw_calls"] = 0
    with pytest.raises(prospective.ProspectiveRefusal, match="no recorded API calls"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_duplicate_index_paths_even_with_updated_index_sha(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    entries = _index(snapshot)
    _rewrite_index(snapshot, ledger, entries + entries)
    ledger["snapshot"]["raw_calls"] = 2
    with pytest.raises(prospective.ProspectiveRefusal, match="unsafe/duplicate body path"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_refuses_body_path_escape_even_when_index_sha_updated(tmp_path: Path) -> None:
    snapshot, ledger = _snapshot(tmp_path)
    entries = _index(snapshot)
    entries[0]["path"] = "raw/../outside.json"
    _rewrite_index(snapshot, ledger, entries)
    with pytest.raises(prospective.ProspectiveRefusal, match="unsafe/duplicate body path"):
        runner._verify_prospective_raw_archive(snapshot, ledger)


def test_failed_raw_archive_retained_in_actual_topic_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A failed integrity gate must keep and name the frozen raw evidence."""
    monkeypatch.setattr(
        runner.prospective, "load_declaration",
        lambda *_args: {"time_limit_s": 60, "invariants": []},
    )
    monkeypatch.setattr(
        runner.prospective, "check_declaration_frozen", lambda *_args: None
    )
    config_path = tmp_path / "released-config.json"
    config_path.write_text(
        '{"slug":"synthetic-archive","topic_identifier":"synthetic-held-out"}',
        encoding="utf-8",
    )

    acquired = {}

    def synthetic_acquire(_config: dict, _day: str, *, root: str) -> str:
        snapshot, _ledger = _snapshot(Path(root))
        body_path = snapshot / _index(snapshot)[0]["path"]
        body_path.write_bytes(body_path.read_bytes() + b"tampered")
        acquired["snapshot"] = snapshot
        return str(snapshot)

    monkeypatch.setattr(runner.acquisition, "refresh", synthetic_acquire)
    result = runner.run_topic(
        "synthetic-batch", str(config_path), str(tmp_path / "run-package")
    )
    assert result["outcome"] == "FAILED_CRASH"
    snapshot = acquired["snapshot"]
    assert snapshot.is_dir()
    assert (snapshot / "raw" / "INDEX.json").is_file()
    record = json.loads(Path(result["run_record"]).read_text(encoding="utf-8"))
    assert snapshot.relative_to(tmp_path / "run-package").as_posix() in record["artefact_paths"]
    assert "failure.json" in record["artefact_paths"]
    failure = json.loads((tmp_path / "run-package" / "failure.json").read_text(encoding="utf-8"))
    assert "file SHA256 mismatch" in failure["message"]
