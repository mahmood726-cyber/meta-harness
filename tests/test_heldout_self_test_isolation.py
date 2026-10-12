"""Plant: the held-out detector's self-test runs git in a SCRATCH repository, and must never write into the repository
whose hook exported GIT_INDEX_FILE (2026-10-11: verify_all runs heldout.self_test in-process under the pre-commit hook,
outside tests/conftest.py's scrub; the scratch 'git init' made its own repository, but 'git add probe.txt' wrote into
the index file the hook had exported -- 'AD probe.txt' appeared staged in a lane worktree)."""
import os
import subprocess

from harness import heldout


def _clean():
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True, env=_clean(), check=True).stdout


def _setup(tmp_path, monkeypatch):
    outer = tmp_path / "outer"
    outer.mkdir()
    _git(outer, "init", "-q")
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setenv("GIT_INDEX_FILE", str(outer / ".git" / "index"))      # what the pre-commit hook exports
    return outer, scratch


def test_PLANT_without_isolation_the_scratch_add_lands_in_the_hooked_index(tmp_path, monkeypatch):
    outer, scratch = _setup(tmp_path, monkeypatch)
    heldout._run_git(str(scratch), ["init"])
    (scratch / "probe.txt").write_text("x\n", encoding="utf-8")
    heldout._run_git(str(scratch), ["add", "probe.txt"])
    assert "probe.txt" in _git(outer, "ls-files", "--stage")                  # the 11 Oct defect, reproduced


def test_isolated_scratch_git_never_touches_the_hooked_index(tmp_path, monkeypatch):
    outer, scratch = _setup(tmp_path, monkeypatch)
    heldout._run_git(str(scratch), ["init"], isolate=True)
    (scratch / "probe.txt").write_text("x\n", encoding="utf-8")
    heldout._run_git(str(scratch), ["add", "probe.txt"], isolate=True)
    assert _git(outer, "ls-files", "--stage") == ""                           # the hooked index is untouched
    assert heldout._run_git(str(scratch), ["ls-files"], isolate=True).strip() == "probe.txt"
