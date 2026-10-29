import base64
import hashlib
import json
import tarfile
from pathlib import Path

from scripts import archive_raw_bodies
from scripts import search_v2_run as runner


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_tar_only_archives_raw_bodies_and_keeps_local_tar(tmp_path, monkeypatch):
    # The archive must physically reside outside the repository, and the
    # synthetic snapshot must have a REFRESH ledger bound to its raw index.
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    monkeypatch.setattr(runner, "ROOT", str(repo_root))
    monkeypatch.setattr(archive_raw_bodies, "ROOT", str(repo_root))

    snapshot = repo_root / "cache" / "plant" / "snapshots" / "2026-09-15r3-search_v2"
    body = snapshot / "raw" / "s1" / "001.json"
    body.parent.mkdir(parents=True)
    raw_http = b"tiny raw body"
    body_digest = hashlib.sha256(raw_http).hexdigest()
    call = {
        "source_id": "s1", "url": "https://example.invalid/concept",
        "params": {"q": "synthetic"}, "status": 200,
        "fetched_utc": "2026-09-15T12:00:00Z",
        "adapter": "synthetic.adapter", "adapter_blob_sha": "synthetic-only",
        "body_sha256": body_digest,
    }
    body.write_text(json.dumps(call | {
        "body_bytes_b64": base64.b64encode(raw_http).decode("ascii"),
    }), encoding="utf-8")
    digest = _sha256(body)
    index_bytes = json.dumps(
        [call | {"path": "raw/s1/001.json", "file_sha256": digest}]
    ).encode("utf-8")
    (snapshot / "raw" / "INDEX.json").write_bytes(index_bytes)
    (snapshot / "retrieval_ledger.json").write_text(json.dumps({
        "snapshot": {
            "mode": "REFRESH",
            "raw_calls": 1,
            "raw_index_sha256": hashlib.sha256(index_bytes).hexdigest(),
        },
    }), encoding="utf-8")

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
    assert "cache/plant/snapshots/2026-09-15r3-search_v2/raw/s1/001.json" in names


def test_registries_arg_parses_and_validates_supported_adapters():
    assert runner._registries_arg("ctgov,isrctn") == ("ctgov", "isrctn")
