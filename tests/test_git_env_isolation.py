"""Tests never write into the repository that runs them (2026-09-27: under the pre-commit hook, test_heldout/test_target inherited
GIT_DIR/GIT_INDEX_FILE and committed fixtures onto the real branch, and set core.bare=true in its config).

The plant: an OUTER sacrificial repo stands in for the real one; an inner test does `git init` + `git commit` in its own tmp dir while
GIT_DIR / GIT_INDEX_FILE point at the outer repo, exactly as a hook exports them. Without tests/conftest.py (--noconftest) the commit
lands in the OUTER repo -- the plant fires; with it, the outer repo is untouched."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
INNER = '''
import subprocess
def test_inner(tmp_path):
    for cmd in (["init", "-q"], ["-c", "user.name=Plant", "-c", "user.email=plant@example.test", "commit", "-q", "--allow-empty", "-m", "plant"]):
        subprocess.run(["git", *cmd], cwd=tmp_path, check=True)
'''


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True).stdout.strip()


def _run_inner(tmp_path, with_conftest):
    outer = tmp_path / "outer"
    outer.mkdir()
    subprocess.run(["git", "init", "-q", str(outer)], check=True)
    subprocess.run(["git", "-C", str(outer), "-c", "user.name=Outer", "-c", "user.email=outer@example.test", "commit", "-q",
                    "--allow-empty", "-m", "outer base"], check=True)
    head0 = _git(outer, "rev-parse", "HEAD")
    suite = tmp_path / "suite"
    suite.mkdir()
    (suite / "test_inner_git.py").write_text(INNER, encoding="utf-8")
    if with_conftest:
        shutil.copyfile(HERE / "conftest.py", suite / "conftest.py")
    # The inner pytest must NOT inherit PYTEST_ADDOPTS: a shared --basetemp would make it CLEAR the outer run's temp dir (this
    # test's own outer repo included) at start -- a flake seen whenever the suite ran with --basetemp set. It gets its own.
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env.update(GIT_DIR=str(outer / ".git"), GIT_INDEX_FILE=str(outer / ".git" / "index"))
    cfg0 = (outer / ".git" / "config").read_bytes()
    # the program is sys.executable, stated inline so the model-call inventory can read it statically
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", *([] if with_conftest else ["--noconftest"]), "-p", "no:cacheprovider",
                        "--basetemp", str(tmp_path / "inner_basetemp"), str(suite / "test_inner_git.py")],
                       cwd=suite, env=env, capture_output=True, text=True, timeout=600)
    touched = _git(outer, "rev-parse", "HEAD") != head0 or (outer / ".git" / "config").read_bytes() != cfg0
    return touched, (outer / ".git" / "config").read_text(encoding="utf-8"), (p.stdout + p.stderr)[-3000:]


def test_PLANT_without_the_guard_the_inner_git_writes_into_the_outer_repo(tmp_path):
    # The 2026-09-27 incident, reproduced: 'git init' under an inherited GIT_DIR re-initialises the OUTER repository (its config was
    # rewritten -- core.bare=true there) and a following commit lands on its branch. Either change is the defect.
    touched, config, out = _run_inner(tmp_path, with_conftest=False)
    assert touched, (config, out)


def test_with_the_guard_the_outer_repo_is_untouched(tmp_path):
    touched, config, out = _run_inner(tmp_path, with_conftest=True)
    assert not touched, (config, out)
