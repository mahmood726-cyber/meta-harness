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
    assert not (snapshot / "ARCHIVE.json").exists()
    # Exercise the nested-path guard in CHECK after a synthetically declared
    # location; an unreceipted override is correctly refused sooner.
    (snapshot / "ARCHIVE.json").write_text(json.dumps({
        "archive_root": str(archive_root),
        "archived_relpath": archive._rel_snapshot(str(snapshot)),
        "index_sha256": hashlib.sha256((snapshot / "raw" / "INDEX.json").read_bytes()).hexdigest(),
    }), encoding="utf-8")
    with pytest.raises(SystemExit, match="outside the repository"):
        archive.check(str(snapshot), str(archive_root))
    assert (snapshot / rows[0]["path"]).is_file()
    assert not (redirected / "topic").exists()


def test_archive_body_path_refuses_in_tree_destination_even_without_symlinks(tmp_path, monkeypatch):
    """Run the resolved-root negative on platforms without symlink privileges."""
    snapshot, rows, _ = _fixture(tmp_path, monkeypatch)
    in_tree_destination = Path(archive.ROOT) / "other-archive"
    with pytest.raises(SystemExit, match="outside the repository"):
        archive._body_paths(str(snapshot), str(in_tree_destination), rows[0]["path"])
    assert (snapshot / rows[0]["path"]).is_file()


def test_archived_body_corruption_not_masked_by_restored_local_copy(tmp_path, monkeypatch):
    """Every extant body copy must verify, not just the first local match."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    local = snapshot / rows[0]["path"]
    original = local.read_bytes()
    archive.move(str(snapshot), str(archive_root))
    archived = archive_root / archive._rel_snapshot(str(snapshot)) / rows[0]["path"]
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(original)
    assert archive.check(str(snapshot), None) == (1, [])
    archived.write_bytes(b"damaged off-tree evidence")
    ok, problems = archive.check(str(snapshot), None)
    assert ok == 0
    assert len(problems) == 1 and "DIGEST MISMATCH" in problems[0]
    assert local.read_bytes() == original


def test_missing_declared_archive_not_masked_by_restored_local_copy(tmp_path, monkeypatch):
    """After move, an intact local backup cannot certify missing off-tree custody."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    local = snapshot / rows[0]["path"]
    original = local.read_bytes()
    archive.move(str(snapshot), str(archive_root))
    archived = archive_root / archive._rel_snapshot(str(snapshot)) / rows[0]["path"]
    local.parent.mkdir(parents=True, exist_ok=True)
    local.write_bytes(original)
    archived.unlink()
    ok, problems = archive.check(str(snapshot), None)
    assert ok == 0
    assert len(problems) == 1 and "NOT PRESERVED OFF-TREE" in problems[0]
    assert local.read_bytes() == original

def test_check_refuses_alternate_archive_that_masks_missing_declared_custody(tmp_path, monkeypatch):
    """A matching body elsewhere cannot stand in for the ARCHIVE.json destination."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    archive.move(str(snapshot), str(archive_root))
    relative = Path(archive._rel_snapshot(str(snapshot))) / rows[0]["path"]
    declared_copy = archive_root / relative
    substitute_root = tmp_path / "unregistered-second-archive"
    substitute_copy = substitute_root / relative
    substitute_copy.parent.mkdir(parents=True)
    substitute_copy.write_bytes(declared_copy.read_bytes())
    declared_copy.unlink()

    # Without the pinned-root guard, this explicit override would return (1, []).
    with pytest.raises(SystemExit, match="override differs from ARCHIVE.json"):
        archive.check(str(snapshot), str(substitute_root))
    ok, problems = archive.check(str(snapshot), None)
    assert ok == 0
    assert len(problems) == 1 and "NOT PRESERVED:" in problems[0]


def test_check_accepts_matching_root_and_refuses_malformed_pointer_root(tmp_path, monkeypatch):
    """Both explicit and implicit checks use one valid declared archive location."""
    snapshot, _, archive_root = _fixture(tmp_path, monkeypatch)
    archive.move(str(snapshot), str(archive_root))
    assert archive.check(str(snapshot), str(archive_root)) == (1, [])
    pointer_path = snapshot / "ARCHIVE.json"
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    pointer["archive_root"] = None
    pointer_path.write_text(json.dumps(pointer), encoding="utf-8")
    with pytest.raises(SystemExit, match="no valid archive_root"):
        archive.check(str(snapshot), None)


def test_repeat_move_same_root_cannot_rewrite_custody_receipt(tmp_path, monkeypatch):
    """A successful move is not an invitation to rewrite its time or claim."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    assert archive.move(str(snapshot), str(archive_root)) == 1
    receipt = snapshot / "ARCHIVE.json"
    original = receipt.read_bytes()
    with pytest.raises(SystemExit, match="ARCHIVE.json already exists"):
        archive.move(str(snapshot), str(archive_root))
    assert receipt.read_bytes() == original
    assert archive.check(str(snapshot), None) == (1, [])


def test_repeat_move_cannot_retarget_original_archive_custody(tmp_path, monkeypatch):
    """No later invocation may silently replace a recorded archive root."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    archive.move(str(snapshot), str(archive_root))
    receipt = snapshot / "ARCHIVE.json"
    original = receipt.read_bytes()
    substitute_root = tmp_path / "unapproved-custody-root"
    with pytest.raises(SystemExit, match="ARCHIVE.json already exists"):
        archive.move(str(snapshot), str(substitute_root))
    assert receipt.read_bytes() == original
    assert not substitute_root.exists()
    assert archive.check(str(snapshot), None) == (1, [])


def test_unreceipted_override_cannot_certify_copied_body(tmp_path, monkeypatch):
    """An arbitrary off-tree copy cannot replace a missing registered receipt."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    local = snapshot / rows[0]["path"]
    substitute = archive_root / archive._rel_snapshot(str(snapshot)) / rows[0]["path"]
    substitute.parent.mkdir(parents=True)
    substitute.write_bytes(local.read_bytes())
    local.unlink()
    assert not (snapshot / "ARCHIVE.json").exists()

    # The old checker returned (1, []) for this unregistered matching copy.
    with pytest.raises(SystemExit, match="ARCHIVE.json custody receipt"):
        archive.check(str(snapshot), str(archive_root))
    ok, problems = archive.check(str(snapshot), None)
    assert ok == 0 and len(problems) == 1 and "NOT PRESERVED" in problems[0]


def test_unarchived_local_verification_unchanged_without_override(tmp_path, monkeypatch):
    """Local integrity remains checkable before a declared archive move."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    assert archive.check(str(snapshot), None) == (1, [])
    with pytest.raises(SystemExit, match="ARCHIVE.json custody receipt"):
        archive.check(str(snapshot), str(archive_root))
    assert not (snapshot / "ARCHIVE.json").exists()
    assert (snapshot / rows[0]["path"]).is_file()



def test_symlinked_receipt_cannot_claim_archive_custody(tmp_path, monkeypatch):
    """A self-consistent external pointer supplied through a link is not trusted."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    rel = Path(archive._rel_snapshot(str(snapshot))) / rows[0]["path"]
    copy = archive_root / rel
    copy.parent.mkdir(parents=True)
    copy.write_bytes((snapshot / rows[0]["path"]).read_bytes())
    outside = tmp_path / "replaceable-receipt.json"
    outside.write_text(json.dumps({
        "archive_root": str(archive_root),
        "archived_relpath": archive._rel_snapshot(str(snapshot)),
        "index_sha256": hashlib.sha256((snapshot / "raw" / "INDEX.json").read_bytes()).hexdigest(),
    }), encoding="utf-8")
    receipt = snapshot / "ARCHIVE.json"
    try:
        receipt.symlink_to(outside)
    except (OSError, NotImplementedError):
        pytest.skip("filesystem cannot create symlinks")
    with pytest.raises(SystemExit, match="regular non-symlink"):
        archive.check(str(snapshot), None)
    assert copy.is_file()


def test_dangling_receipt_link_not_treated_as_unarchived_local_pass(tmp_path, monkeypatch):
    """Do not silently downgrade a previously asserted custody receipt to none."""
    snapshot, rows, _ = _fixture(tmp_path, monkeypatch)
    receipt = snapshot / "ARCHIVE.json"
    try:
        receipt.symlink_to(tmp_path / "nonexistent-custody-receipt.json")
    except (OSError, NotImplementedError):
        pytest.skip("filesystem cannot create symlinks")
    assert (snapshot / rows[0]["path"]).is_file()
    with pytest.raises(SystemExit, match="regular non-symlink"):
        archive.check(str(snapshot), None)


def test_receipt_directory_not_treated_as_missing_receipt(tmp_path, monkeypatch):
    """Cross-platform regression even when symlink privileges are unavailable."""
    snapshot, rows, _ = _fixture(tmp_path, monkeypatch)
    (snapshot / "ARCHIVE.json").mkdir()
    assert (snapshot / rows[0]["path"]).is_file()
    with pytest.raises(SystemExit, match="regular non-symlink"):
        archive.check(str(snapshot), None)


def test_raw_directory_symlink_cannot_outsource_index_and_bodies(tmp_path, monkeypatch):
    """A linked raw/ tree must not pass as a locally held in-snapshot response."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    local_raw = snapshot / "raw"
    outside_raw = tmp_path / "external-raw"
    local_raw.rename(outside_raw)
    try:
        local_raw.symlink_to(outside_raw, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("filesystem cannot create directory symlinks")
    assert (outside_raw / "INDEX.json").is_file()
    assert (outside_raw / "pubmed_concept_query#1/001.json").is_file()
    with pytest.raises(SystemExit, match="raw evidence directory/index/ledger"):
        archive.check(str(snapshot), None)
    with pytest.raises(SystemExit, match="raw evidence directory/index/ledger"):
        archive.move(str(snapshot), str(archive_root))
    assert not (snapshot / "ARCHIVE.json").exists()
    assert (outside_raw / "pubmed_concept_query#1/001.json").is_file()


@pytest.mark.parametrize("linked_name", ["raw/INDEX.json", "retrieval_ledger.json"])
def test_linked_raw_control_file_refused_even_with_matching_bytes(tmp_path, monkeypatch, linked_name):
    """Matching JSON in an external control file is not a trustworthy local record."""
    snapshot, rows, archive_root = _fixture(tmp_path, monkeypatch)
    local = snapshot / linked_name
    external = tmp_path / ("external-" + local.name)
    local.rename(external)
    try:
        local.symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("filesystem cannot create file symlinks")
    with pytest.raises(SystemExit, match="raw evidence directory/index/ledger"):
        archive.check(str(snapshot), None)
    with pytest.raises(SystemExit, match="raw evidence directory/index/ledger"):
        archive.move(str(snapshot), str(archive_root))
    assert not (snapshot / "ARCHIVE.json").exists()
    assert external.is_file()
