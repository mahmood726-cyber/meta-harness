"""Refusal plants for generated instructions, wheel integrity and offline execution."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from scripts import generate_replay as guides
from scripts.replay_offline import snapshot_reader

ROOT = Path(__file__).resolve().parents[1]


def test_snapshot_adapter_only_reads_pinned_matching_bytes(tmp_path):
    document = tmp_path / "held.txt"
    data = b"explicit integrity-control document, not scientific output"
    document.write_bytes(data)
    read = snapshot_reader(tmp_path, [{"ref": "held.txt", "sha256": hashlib.sha256(data).hexdigest()}])
    assert read(["git", "show", "HEAD:held.txt"], cwd=tmp_path) == data
    for command in (["git", "fetch", "origin"], ["git", "show", "HEAD:other.txt"],
                    ["git", "show", "HEAD:../held.txt"]):
        with pytest.raises(RuntimeError, match="REFUSED"):
            read(command, cwd=tmp_path)
    document.write_bytes(data + b" altered")
    with pytest.raises(RuntimeError, match="digest mismatch"):
        read(["git", "show", "HEAD:held.txt"], cwd=tmp_path)


def test_corpus_guides_are_current():
    assert guides.check(ROOT) == []


@pytest.fixture
def package(tmp_path):
    # Real topic objects, small local wheel fixture; no network or scientific fake data.
    source = ROOT / "docs/reviews/glp1-ra-mace-t2d"
    directory = tmp_path / "docs/reviews" / source.name
    directory.mkdir(parents=True)
    for name in ("manifest.json", "CERTIFICATE.json", "BUNDLE.json", "EXECUTION_RECORD.json"):
        shutil.copyfile(source / name, directory / name)
    offline = tmp_path / "docs/offline"
    (offline / "wheels").mkdir(parents=True)
    wheel = b"integrity-test-only; never used as an installable wheel"
    (offline / "wheels/control.whl").write_bytes(wheel)
    digest = hashlib.sha256(wheel).hexdigest()
    (offline / "requirements.lock").write_text(f"# integrity fixture\ncontrol==1.0 --hash=sha256:{digest}\n",
                                               encoding="utf-8")
    (offline / "wheels.json").write_text(json.dumps([
        {"name": "control", "version": "1.0", "target": "any", "file": "control.whl", "sha256": digest,
         "bytes": len(wheel), "url": "https://example.invalid/control.whl"}
    ]), encoding="utf-8")
    assert guides.check(tmp_path, write=True) == []
    return tmp_path, directory


@pytest.mark.parametrize("plant", ["guide", "missing", "digest", "bundle", "wheel", "lock", "lock_wheel_mismatch"])
def test_refuses_drift(package, plant):
    root, directory = package
    if plant == "guide":
        with (directory / "REPLAY.md").open("ab") as out:
            out.write(b"hand edit\n")
    elif plant == "missing":
        (directory / "REPLAY.md").unlink()
    elif plant == "digest":
        path = directory / "manifest.json"
        obj = guides.read(path)
        obj["review_sha256"] = "0" * 64
        path.write_text(json.dumps(obj), encoding="utf-8")
    elif plant == "bundle":
        path = directory / "BUNDLE.json"
        obj = guides.read(path)
        obj["offline_replay"]["lock"]["sha256"] = "0" * 64
        path.write_text(json.dumps(obj), encoding="utf-8")
    elif plant == "wheel":
        (root / "docs/offline/wheels/control.whl").write_bytes(b"corrupt")
    elif plant == "lock_wheel_mismatch":
        # the lock names other bytes than wheels.json: pip would accept a wheel the guides never named
        (root / "docs/offline/requirements.lock").write_text("control==1.0 --hash=sha256:" + "1" * 64 + "\n",
                                                             encoding="utf-8")
    else:
        (root / "docs/offline/requirements.lock").write_bytes(b"changed")
    assert guides.check(root), "a damaged replay package must refuse"


def test_regeneration_is_byte_identical(package):
    root, directory = package
    before = {p.name: p.read_bytes() for p in directory.iterdir()}
    assert guides.check(root, write=True) == []
    assert before == {p.name: p.read_bytes() for p in directory.iterdir()}


def test_check_command_refuses_a_planted_guide(package):
    root, directory = package
    (root / "scripts").mkdir()
    script = root / "scripts/generate_replay.py"
    shutil.copyfile(ROOT / "scripts/generate_replay.py", script)
    with (directory / "REPLAY.md").open("ab") as out:
        out.write(b"planted hand edit\n")
    result = subprocess.run([sys.executable, str(script), "--check"],
                            cwd=root, capture_output=True, text=True)
    assert result.returncode == 1
    assert "REFUSED: REPLAY.md stale or absent" in result.stdout


def test_each_guide_uses_own_objects_and_offline_commands():
    for directory in guides.topics(ROOT):
        text = guides.render(directory)
        assert f"scripts/replay_offline.py {directory.name}" in text
        for key in ("review_sha256", "html_sha256"):
            assert guides.read(directory / "manifest.json")[key] in text
        assert guides.read(directory / "CERTIFICATE.json")["release_sha256"] in text
        for held in guides.read(directory / "CERTIFICATE.json")["held_documents"]:
            assert held["ref"] in text and held["sha256"] in text
        assert "--no-index --require-hashes" in text
        assert "--basetemp=scratch/" in text
        assert "git clone" not in text and "ls-remote" not in text and "--url" not in text


@pytest.mark.parametrize("operation", [
    "socket.create_connection(('127.0.0.1', 9))",
    "subprocess.run([sys.executable, '-c', 'pass'])",
])
def test_offline_guard_refuses_network_and_children(operation):
    code = ("import socket, subprocess, sys; from scripts.replay_offline import deny_network; "
            "sys.addaudithook(deny_network); " + operation)
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert "REFUSED: offline replay attempted" in result.stderr
