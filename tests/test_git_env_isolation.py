"""PLANT (fired pre-fix on main 9d4f4894, 2026-09-19): under a git hook's environment (GIT_DIR and
GIT_INDEX_FILE exported), the harness's and the test-suite's temporary-repository helpers act on the
repository being committed. The pre-commit hook run from the linked worktree C:/mh-ws-AFF put eleven
fixture commits ("base", "initial clean fixture", "mention zz-plant-alpha-beta-gamma ...") on ws/AFF, and
that pointer was pushed. The victim repository here is a throwaway; the assertion is that its HEAD and
its index are byte-identical after every helper that spawns git in a temporary directory has run."""
from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from harness import gitenv  # noqa: E402


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=gitenv.clean_env()).stdout.strip()


def _victim(tmp_path: Path) -> Path:
    """The repository a hook would be committing: a LINKED WORKTREE (as the workshop branches are) with one
    real commit and a clean index. A plain repository's gitdir refuses a stray `git add` ('must be run in a
    work tree'); a linked worktree's gitdir accepts it, and that is the configuration that was hit."""
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q", "-b", "main")
    _git(main, "config", "user.name", "Victim")
    _git(main, "config", "user.email", "victim@example.test")
    (main / "real.txt").write_text("the branch being committed\n", encoding="utf-8", newline="\n")
    _git(main, "add", "real.txt")
    _git(main, "commit", "-q", "-m", "real commit")
    victim = tmp_path / "victim"
    _git(main, "worktree", "add", "-q", victim.as_posix(), "-b", "ws/victim")
    return victim


def _gitdir(victim: Path) -> str:
    """The linked worktree's gitdir, forward slashes, as git itself exports GIT_DIR to a hook."""
    return (victim / ".git").read_text(encoding="utf-8").split("gitdir:", 1)[1].strip().replace("\\", "/")


def _state(victim: Path) -> tuple[str, str, str]:
    head = _git(victim, "rev-parse", "HEAD")
    index = hashlib.sha256(Path(_gitdir(victim), "index").read_bytes()).hexdigest()
    log = _git(victim, "log", "--format=%s")
    return head, index, log


def _hook_env(monkeypatch, victim: Path) -> None:
    """What git exports to a pre-commit hook run in a linked worktree (and so to everything it spawns)."""
    gitdir = _gitdir(victim)
    monkeypatch.setenv("GIT_DIR", gitdir)
    monkeypatch.setenv("GIT_INDEX_FILE", gitdir + "/index")
    monkeypatch.delenv("GIT_WORK_TREE", raising=False)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tests" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_clean_env_removes_every_repository_location_variable(monkeypatch):
    for name in gitenv.REPO_LOCATION_VARS:
        monkeypatch.setenv(name, "x")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "kept")
    env = gitenv.clean_env(extra="y")
    assert not any(name in env for name in gitenv.REPO_LOCATION_VARS)
    assert env["GIT_AUTHOR_NAME"] == "kept" and env["extra"] == "y"


def test_hook_environment_is_the_mechanism(tmp_path, monkeypatch):
    """The control: an UNCLEANED git in a stray directory under the hook environment commits the stray
    directory's contents onto the victim branch. If this stops firing, git changed behaviour and the
    plant below proves nothing."""
    victim = _victim(tmp_path)
    before = _state(victim)
    _hook_env(monkeypatch, victim)
    stray = tmp_path / "stray"
    stray.mkdir()
    (stray / "probe.txt").write_text("probe\n", encoding="utf-8")
    for cmd in (["git", "init", "-q"], ["git", "add", "probe.txt"],
                ["git", "-c", "user.name=s", "-c", "user.email=s@example.test", "commit", "-q", "-m", "stray"]):
        subprocess.run(cmd, cwd=stray, check=True, capture_output=True)
    after = _state(victim)
    assert after[0] != before[0] and "stray" in after[2], "the hook environment no longer redirects git; re-derive the plant"
    assert "probe.txt" in _git(victim, "ls-tree", "--name-only", "HEAD").split(), "the stray file was committed onto the victim branch"


@pytest.mark.parametrize("helper", [
    "test_target:_repo",
    "test_heldout:_temp_repo_commit",
    "test_fixstate:_temp_repo_commit",
    "test_honest_ratchet:_temp_repo_commit",
    "test_gate_scorecard:_temp_repo_commit",
    "test_search_completeness:_temp_repo_init",
])
def test_temporary_repository_helpers_never_touch_the_hook_repository(tmp_path, monkeypatch, helper):
    victim = _victim(tmp_path)
    before = _state(victim)
    _hook_env(monkeypatch, victim)
    mod_name, fn_name = helper.split(":")
    fn = getattr(_load(mod_name), fn_name)
    work = tmp_path / "work"
    work.mkdir()
    fn(work)
    assert _state(victim) == before, f"{helper} acted on GIT_DIR's repository instead of its own"


def test_heldout_self_test_never_stages_the_canary_into_the_hook_repository(tmp_path, monkeypatch):
    from harness import heldout
    victim = _victim(tmp_path)
    before = _state(victim)
    _hook_env(monkeypatch, victim)
    key = "k" * 32
    registry = {"tokens": [heldout.canary_token(key)], "enforced_since": None}
    ok, detail = heldout.self_test(key, registry)
    assert ok, detail
    assert _state(victim) == before, "heldout.self_test staged its canary into GIT_DIR's index"
    assert "probe.txt" not in _git(victim, "ls-files")


def test_verify_all_scrubs_its_own_process(tmp_path, monkeypatch):
    victim = _victim(tmp_path)
    _hook_env(monkeypatch, victim)
    removed = gitenv.scrub_process_env()
    assert set(removed) == {"GIT_DIR", "GIT_INDEX_FILE"}
    assert not any(name in os.environ for name in gitenv.REPO_LOCATION_VARS)
    src = (ROOT / "scripts" / "verify_all.py").read_text(encoding="utf-8")
    assert "gitenv.scrub_process_env()" in src and "env=gitenv.clean_env()" in src


def test_pre_commit_hook_unsets_the_repository_location_variables():
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE" in hook
