"""Synthetic tar prefix-collision and end-of-archive regressions.

No cached publication inputs, network calls, or protected evidence are involved.
"""
import hashlib
import importlib.util
import io
import json
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "production_record.py"


def _verifier(monkeypatch):
    spec = importlib.util.spec_from_file_location("production_record_prefix_fixture", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_artifact_target",
                        lambda *_: "TARGET production_record.check_artifact: synthetic")
    return module


def _check(tmp_path, monkeypatch, added_directory):
    module = _verifier(monkeypatch)

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


def _synthetic_artifact(tmp_path, files, reverse=False):
    manifest = tmp_path / "verified.json"
    manifest.write_text(json.dumps({
        "commit_sha": "a" * 40,
        "files": {name: hashlib.sha256(body).hexdigest() for name, body in files.items()},
    }), encoding="utf-8")
    archive = tmp_path / "site.tar"
    members = list(files.items()) + [("_production/manifest.json", manifest.read_bytes())]
    if reverse:
        members.reverse()
    with tarfile.open(archive, "w", format=tarfile.GNU_FORMAT) as tar:
        for name in ("./", "./_production/"):
            entry = tarfile.TarInfo(name)
            entry.type = tarfile.DIRTYPE
            tar.addfile(entry)
        for name, body in members:
            entry = tarfile.TarInfo("./" + name)
            entry.size = len(body)
            tar.addfile(entry, io.BytesIO(body))
        end_of_members = tar.offset
    return SimpleNamespace(manifest=str(manifest), tar=str(archive)), end_of_members


@pytest.mark.parametrize("reverse", [False, True], ids=["parent-first", "child-first"])
@pytest.mark.parametrize("parent,child", [
    ("index.html", "index.html/forged"),
    ("assets/page.html", "assets/page.html/nested/forged"),
])
def test_artifact_refuses_listed_file_beneath_listed_file(monkeypatch, tmp_path, capsys,
                                                       reverse, parent, child):
    args, _ = _synthetic_artifact(tmp_path, {parent: b"page", child: b"forged"}, reverse)
    assert _verifier(monkeypatch).cmd_check_artifact(args) == 1
    assert "ARTIFACT REFUSED: file shadows verified file" in capsys.readouterr().out


@pytest.mark.parametrize("padding", [2 * tarfile.BLOCKSIZE, tarfile.RECORDSIZE],
                         ids=["after-two-zero-blocks", "after-record-padding"])
def test_artifact_refuses_member_after_end_marker(monkeypatch, tmp_path, capsys, padding):
    args, end = _synthetic_artifact(tmp_path, {"index.html": b"page"})
    hidden = io.BytesIO()
    with tarfile.open(fileobj=hidden, mode="w", format=tarfile.GNU_FORMAT) as tar:
        entry = tarfile.TarInfo("./forged.html")
        entry.size = 6
        tar.addfile(entry, io.BytesIO(b"forged"))
    archive = Path(args.tar)
    archive.write_bytes(archive.read_bytes()[:end] + b"\0" * padding + hidden.getvalue())
    # Establish the blind spot: ordinary tar iteration sees only verified members.
    with tarfile.open(archive) as tar:
        assert "./forged.html" not in tar.getnames()
    with tarfile.open(archive, ignore_zeros=True) as tar:
        assert "./forged.html" in tar.getnames()
    assert _verifier(monkeypatch).cmd_check_artifact(args) == 1
    assert "ARTIFACT REFUSED: non-zero data after tar end marker" in capsys.readouterr().out


@pytest.mark.parametrize("padding", [0, (1 << 20) + tarfile.RECORDSIZE],
                         ids=["record-tail", "beyond-first-read-chunk"])
def test_artifact_refuses_non_member_bytes_after_end_marker(monkeypatch, tmp_path,
                                                         capsys, padding):
    args, _ = _synthetic_artifact(tmp_path, {"index.html": b"page"})
    with open(args.tar, "ab") as out:
        out.write(b"\0" * padding + b"!")
    assert _verifier(monkeypatch).cmd_check_artifact(args) == 1
    assert "ARTIFACT REFUSED: non-zero data after tar end marker" in capsys.readouterr().out


@pytest.mark.parametrize("extra_padding", [0, tarfile.RECORDSIZE])
def test_artifact_accepts_upload_pages_style_tar(monkeypatch, tmp_path, extra_padding):
    files = {
        "index.html": b"<p>synthetic upload</p>",
        ".nojekyll": b"",
        "assets/zeros.bin": b"\0" * (4 * tarfile.BLOCKSIZE) + b"payload, not a header",
        "index.html.backup": b"a shared text prefix is not a path collision",
    }
    args, _ = _synthetic_artifact(tmp_path, files)
    site = tmp_path / "site"
    for name, body in {**files, "_production/manifest.json": Path(args.manifest).read_bytes()}.items():
        path = site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    # Match the upload action's uncompressed, dereferenced GNU tar of '.':
    # root/nested directories, ./ names, empty .nojekyll, embedded receipt,
    # two zero end blocks and zero padding to the tar record size.
    with tarfile.open(args.tar, "w", format=tarfile.GNU_FORMAT, dereference=True) as tar:
        tar.add(site, arcname=".")
    with open(args.tar, "ab") as out:
        out.write(b"\0" * extra_padding)
    assert Path(args.tar).stat().st_size % tarfile.RECORDSIZE == 0
    assert _verifier(monkeypatch).cmd_check_artifact(args) == 0
