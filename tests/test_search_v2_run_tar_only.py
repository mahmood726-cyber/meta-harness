import hashlib
import json
import tarfile
from pathlib import Path

from scripts import archive_raw_bodies
from scripts import search_v2_run as runner


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_tar_only_archives_raw_bodies_and_keeps_local_tar(tmp_path, monkeypatch):
    monkeypatch.setattr(runner, "ROOT", str(tmp_path))
    monkeypatch.setattr(archive_raw_bodies, "ROOT", str(tmp_path))

    snapshot = tmp_path / "cache" / "plant" / "snapshots" / "2026-09-15r3-search_v2"
    body = snapshot / "raw" / "s1" / "001.txt"
    body.parent.mkdir(parents=True)
    body.write_text("tiny raw body\n", encoding="utf-8")
    digest = _sha256(body)
    (snapshot / "raw" / "INDEX.json").write_text(
        json.dumps([{"source_id": "s1", "path": "raw/s1/001.txt", "file_sha256": digest, "body_sha256": digest}]),
        encoding="utf-8",
    )

    archive_root = tmp_path / "archive"
    messages = []
    public = runner._archive_and_upload(
        "plant",
        str(snapshot),
        str(archive_root),
        None,
        messages.append,
        tar_only=True,
    )
    runner._write_archive_pointer(str(snapshot), public)

    asset = "raw-plant-2026-09-15r3-search_v2.tar.gz"
    tar_path = archive_root / asset
    expanded_root = archive_root / "cache" / "plant" / "snapshots" / "2026-09-15r3-search_v2"
    pointer = json.loads((snapshot / "ARCHIVE.json").read_text(encoding="utf-8"))

    assert public == {
        "status": "TAR-ONLY-UPLOAD-PENDING",
        "asset": asset,
        "tar_sha256": _sha256(tar_path),
        "tar_bytes": tar_path.stat().st_size,
        "local_tar": str(tar_path),
        "github_release": "raw-archive-2026-09-15r3-search_v2",
    }
    assert pointer["public_archive"] == public
    assert pointer["custody"] == "tarball held locally pending upload; digests in-tree are the authority"
    assert tar_path.is_file()
    assert not expanded_root.exists()
    assert (snapshot / "raw" / "INDEX.json").is_file()
    with tarfile.open(tar_path, "r:gz") as tf:
        names = set(tf.getnames())
    assert "cache/plant/snapshots/2026-09-15r3-search_v2/raw/s1/001.txt" in names


def test_registries_arg_parses_and_validates_supported_adapters():
    assert runner._registries_arg("ctgov,isrctn") == ("ctgov", "isrctn")
