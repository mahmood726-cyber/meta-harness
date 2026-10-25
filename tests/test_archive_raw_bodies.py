"""A2 custody negatives for the off-tree raw-response archive helper.

Synthetic files only: passing these tests does not constitute a prospective
study search or independent validation of any clinical result.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import archive_raw_bodies as archive


def _fixture(tmp_path: Path, monkeypatch, count: int = 1):
    root = tmp_path / "repo"
    root.mkdir()
    monkeypatch.setattr(archive, "ROOT", str(root))
    snapshot = root / "cache" / "topic" / "snapshots" / "2026-10-25-a"
    raw = snapshot / "raw" / "pubmed_concept_query#1"
    raw.mkdir(parents=True)
    rows = []
    for number in range(1, count + 1):
        relative = f"raw/pubmed_concept_query#1/{number:03d}.json"
        blob = f'{{"response": {number}}}'.encode()
        (snapshot / relative).write_bytes(blob)
        rows.append({"source_id": "pubmed_concept_query#1", "path": relative,
                     "file_sha256": hashlib.sha256(blob).hexdigest(),
                     "body_sha256": hashlib.sha256(b"original bytes").hexdigest()})
    _seal(snapshot, rows)
    return snapshot, rows, tmp_path / "archive"


def _seal(snapshot: Path, rows: list[dict]):
    raw_bytes = json.dumps(rows, indent=2).encode()
    (snapshot / "raw" / "INDEX.json").write_bytes(raw_bytes)
    (snapshot / "retrieval_ledger.json").write_text(json.dumps({
        "snapshot": {"mode": "REFRESH", "raw_calls": len(rows),
                     "raw_index_sha256": hashlib.sha256(raw_bytes).hexdigest()},
    }), encoding="utf-8")


def test_preserved_before_and_after_off_tree_move(tmp_path, monkeypatch):
    snapshot, _, archive_root = _fixture(tmp_path, monkeypatch)
    assert archive.check(str(snapshot), None) == (1, [])
    assert archive.move(str(snapshot), str(archive_root)) == 1
    assert archive.check(str(snapshot), None) == (1, [])
    assert not (snapshot / "raw/pubmed_concept_query#1/001.json").exists()


def test_changed_index_cannot_be_repaired_by_rehashing_local_bodies(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    (snapshot / "raw" / "INDEX.json").write_text(json.dumps(rows), encoding="utf-8")
    with pytest.raises(SystemExit, match="INDEX digest/mode"):
        archive.check(str(snapshot), None)
    with pytest.raises(SystemExit, match="INDEX digest/mode"):
        archive.move(str(snapshot), str(archive_root))
    assert (snapshot / rows[0]["path"]).exists()


def test_escape_refused_even_when_index_digest_is_self_consistent(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    rows[0]["path"] = "raw/../secret.json"
    _seal(snapshot, rows)
    secret = snapshot / "secret.json"
    secret.write_text("PRIVATE", encoding="utf-8")
    with pytest.raises(SystemExit, match="unsafe or duplicate"):
        archive.check(str(snapshot), None)
    with pytest.raises(SystemExit, match="unsafe or duplicate"):
        archive.move(str(snapshot), str(archive_root))
    assert secret.read_text(encoding="utf-8") == "PRIVATE"


def test_repeated_index_path_refused(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    _seal(snapshot, rows + [rows[0]])
    with pytest.raises(SystemExit, match="unsafe or duplicate"):
        archive.move(str(snapshot), str(archive_root))


def test_late_corruption_cannot_move_earlier_body(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch, count=2)
    (snapshot / rows[1]["path"]).write_bytes(b"tampered")
    with pytest.raises(SystemExit, match="nothing moved"):
        archive.move(str(snapshot), str(archive_root))
    assert (snapshot / rows[0]["path"]).exists()
    assert not archive_root.exists()


def test_reject_symlink_to_file_outside_snapshot(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    outside = tmp_path / "secret.json"
    outside.write_bytes((snapshot / rows[0]["path"]).read_bytes())
    local = snapshot / rows[0]["path"]
    local.unlink()
    try:
        local.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("local filesystem does not permit symlinks")
    with pytest.raises(SystemExit, match="escapes the snapshot"):
        archive.move(str(snapshot), str(archive_root))


def test_changed_pointer_or_archived_body_not_marked_preserved(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    archive.move(str(snapshot), str(archive_root))
    archived = archive_root / archive._rel_snapshot(str(snapshot)) / rows[0]["path"]
    archived.write_bytes(b"tampered")
    ok, problems = archive.check(str(snapshot), None)
    assert ok == 0 and len(problems) == 1 and "DIGEST MISMATCH" in problems[0]
    pointer_path = snapshot / "ARCHIVE.json"
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    pointer["index_sha256"] = "0" * 64
    pointer_path.write_text(json.dumps(pointer), encoding="utf-8")
    with pytest.raises(SystemExit, match="archive pointer"):
        archive.check(str(snapshot), None)


def test_missing_ledger_is_not_accepted_as_preserved(tmp_path, monkeypatch):
    snapshot, _, _ = _fixture(tmp_path, monkeypatch)
    (snapshot / "retrieval_ledger.json").unlink()
    with pytest.raises(SystemExit, match="retrieval_ledger"):
        archive.check(str(snapshot), None)


def test_reject_archive_root_inside_repository_before_any_movement(tmp_path, monkeypatch):
    snapshot, rows, _ = _fixture(tmp_path, monkeypatch)
    repo_root = Path(archive.ROOT)
    with pytest.raises(SystemExit, match="outside the repository"):
        archive.move(str(snapshot), str(repo_root / "internal-archive"))
    assert (snapshot / rows[0]["path"]).exists()
    assert not (snapshot / "ARCHIVE.json").exists()
    assert not (repo_root / "internal-archive").exists()


def test_reject_symlinked_archive_root_back_into_repository(tmp_path, monkeypatch):
    snapshot, rows, _ = _fixture(tmp_path, monkeypatch)
    alias = tmp_path / "archive-alias"
    try:
        alias.symlink_to(Path(archive.ROOT), target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("local filesystem does not permit directory symlinks")
    with pytest.raises(SystemExit, match="outside the repository"):
        archive.move(str(snapshot), str(alias))
    assert (snapshot / rows[0]["path"]).exists()


def test_reject_snapshot_symlink_escaping_repository(tmp_path, monkeypatch):
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    escaped = tmp_path / "escaped-snapshot"
    snapshot.rename(escaped)
    try:
        snapshot.symlink_to(escaped, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("local filesystem does not permit directory symlinks")
    with pytest.raises(SystemExit, match="inside the repository"):
        archive.check(str(snapshot), None)
    with pytest.raises(SystemExit, match="inside the repository"):
        archive.move(str(snapshot), str(archive_root))
    assert (escaped / rows[0]["path"]).exists()


def test_reject_pointer_retargeted_to_local_repository_archive(tmp_path, monkeypatch):
    snapshot, _, archive_root = _fixture(tmp_path, monkeypatch)
    archive.move(str(snapshot), str(archive_root))
    pointer_path = snapshot / "ARCHIVE.json"
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    pointer["archive_root"] = str(Path(archive.ROOT) / "internal-archive")
    pointer_path.write_text(json.dumps(pointer), encoding="utf-8")
    with pytest.raises(SystemExit, match="outside the repository"):
        archive.check(str(snapshot), None)


def test_reject_nested_archive_symlink_redirecting_custody_back_in_tree(tmp_path, monkeypatch):
    """An off-tree top-level archive is insufficient if its cache/ entry points in-tree."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    redirected = Path(archive.ROOT) / "unexpected-in-tree-archive"
    redirected.mkdir()
    archive_root.mkdir()
    try:
        (archive_root / "cache").symlink_to(redirected, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("local filesystem does not permit directory symlinks")

    with pytest.raises(SystemExit, match="outside the repository"):
        archive.move(str(snapshot), str(archive_root))
    with pytest.raises(SystemExit, match="outside the repository"):
        archive.check(str(snapshot), str(archive_root))
    assert (snapshot / rows[0]["path"]).is_file()
    assert not (snapshot / "ARCHIVE.json").exists()
    assert not (redirected / "topic").exists()


def test_archive_body_path_refuses_in_tree_destination_even_without_symlinks(tmp_path, monkeypatch):
    """Run the resolved-root negative on platforms without symlink privileges."""
    snapshot, rows, _ = _fixture(tmp_path, monkeypatch)
    in_tree_destination = Path(archive.ROOT) / "other-archive"
    with pytest.raises(SystemExit, match="outside the repository"):
        archive._body_paths(str(snapshot), str(in_tree_destination), rows[0]["path"])
    assert (snapshot / rows[0]["path"]).is_file()
