from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from harness.target import TargetUnresolvable, describe_target
from harness import gitenv


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=gitenv.clean_env(),
    ).stdout.strip()


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.email", "target@example.test")
    _git(repo, "config", "user.name", "Target Test")
    (repo / "probe.txt").write_text("probe\n", encoding="utf-8", newline="\n")
    _git(repo, "add", "probe.txt")
    _git(repo, "commit", "-m", "base")
    return repo


def test_describe_target_names_head_tree_and_files(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    head = _git(repo, "rev-parse", "HEAD")

    line = describe_target(repo, refs=("HEAD",), paths=("probe.txt",), label="plant")

    assert line.startswith(f"TARGET plant: head={head} base={head} tree=clean files=1 probe.txt")


def test_describe_target_refuses_unresolved_ref(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(TargetUnresolvable, match="ref not resolvable: no-such-ref"):
        describe_target(repo, refs=("no-such-ref",), paths=("probe.txt",), label="plant")


def test_describe_target_refuses_empty_file_set(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    with pytest.raises(TargetUnresolvable, match="file set is empty"):
        describe_target(repo, paths=(), label="plant")
