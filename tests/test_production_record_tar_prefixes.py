"""Synthetic tar file/directory prefix-collision regression for production_record.

No cached publication inputs, network calls, or protected evidence are involved.
"""
import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "production_record.py"


def _check(tmp_path, monkeypatch, added_directory):
    spec = importlib.util.spec_from_file_location("production_record_prefix_fixture", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_artifact_target",
                        lambda *_: "TARGET production_record.check_artifact: synthetic")

    page = b"<p>deterministic synthetic page</p>"
    manifest = tmp_path / "verified.json"
    manifest.write_text(json.dumps({
        "commit_sha": "a" * 40,
        "files": {"index.html": hashlib.sha256(page).hexdigest()},
    }), encoding="utf-8")
    archive = tmp_path / "site.tar"
    with tarfile.open(archive, "w") as tar:
        for name, payload in (
            ("index.html", page),
            ("_production/manifest.json", manifest.read_bytes()),
        ):
            entry = tarfile.TarInfo(name)
            entry.size = len(payload)
            tar.addfile(entry, io.BytesIO(payload))
        directory = tarfile.TarInfo(added_directory)
        directory.type = tarfile.DIRTYPE
        tar.addfile(directory)

    return module.cmd_check_artifact(SimpleNamespace(
        manifest=str(manifest), tar=str(archive)))


def test_artifact_refuses_directory_nested_beneath_verified_page(monkeypatch, tmp_path):
    # Pre-fix all unmatched directory members were skipped; this passed.
    assert _check(tmp_path, monkeypatch, "index.html/forged/") == 1


def test_artifact_refuses_directory_nested_beneath_production_receipt(monkeypatch, tmp_path):
    # The embedded manifest is itself a verified regular file.
    assert _check(tmp_path, monkeypatch, "_production/manifest.json/forged/") == 1


def test_artifact_accepts_noncolliding_directory_member(monkeypatch, tmp_path):
    # Directory entries not under a verified file remain permitted.
    assert _check(tmp_path, monkeypatch, "_production/") == 0
