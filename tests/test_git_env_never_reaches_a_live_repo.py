"""A test's scratch `git init` must never reach the LIVE repository through a hook's environment.

Under a pre-commit / pre-push hook git exports GIT_DIR (and GIT_INDEX_FILE, GIT_WORK_TREE). A test that runs
`git init` + `git config user.name ...` in a temp dir while inheriting GIT_DIR re-initialises the repository the hook
belongs to: C:\\mh-lanes\\acq/.git/config gained `core.bare = true` and `user.name = Heldout Test` at 18:11 on 4 Oct 2026
(the g1/repro-ai-audit lane's `git commit` in the linked worktree rai-audit-commit ran this suite from its hook;
tests/test_heldout.py::_init_repo is the only writer of that identity). Same class as 2026-09-19 (C:\\mh-int) and
2026-09-27 (rai-land, 'Target Test').

PLANT: run tests/test_heldout.py in a child pytest with GIT_DIR pointing at a sentinel repository and assert the
sentinel's config is untouched. Before the fix this fires (the sentinel became bare and took the test identity)."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _clean():
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def test_PLANT_heldout_tests_under_a_hook_GIT_DIR_leave_the_live_repo_alone(tmp_path):
    live = tmp_path / "live"
    live.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=live, check=True, env=_clean())
    cfg = live / ".git" / "config"
    before = cfg.read_text(encoding="utf-8")
    env = dict(_clean(), GIT_DIR=str(live / ".git"), GIT_INDEX_FILE=str(live / ".git" / "index"),
               PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp",
                        str(tmp_path / "bt"), "tests/test_heldout.py", "-k", "short_form_hit"],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=600)
    after = cfg.read_text(encoding="utf-8")
    assert "Heldout Test" not in after and "bare = true" not in after, (r.stdout[-800:], after)
    assert after == before
