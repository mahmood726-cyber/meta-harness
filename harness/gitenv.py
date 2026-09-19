"""The environment a git subprocess gets when the code names the repository it means.

A git hook runs with GIT_DIR (and, for pre-commit, GIT_INDEX_FILE) exported. Any `git` the hook's
descendants spawn inherits them, so `git init` in a temporary directory re-initialises the repository
being committed, `git add` in that directory stages the temporary file into the real index (with the
temporary directory as the work tree), and `git commit` moves the real branch. Nothing errors: every
command succeeds, against the wrong repository.

Observed 2026-09-19: the pre-commit hook ran scripts/verify_all.py from a linked worktree; the unit-test
limb's temporary fixture repositories (tests/test_target.py, test_heldout.py, test_fixstate.py) committed
eleven fixture commits ("base", "initial clean fixture", "mention zz-plant-alpha-beta-gamma ...") onto the
branch being committed, and the held-out canary self-test (harness/heldout.self_test) staged its canary
plaintext into the branch's index. The branch pointer, not the working tree, was overwritten.

Rule: a git command that targets an explicit root (cwd=root, -C root, or a fresh `init`) runs with the
repository-location variables REMOVED, so the repository it acts on is the one named by the code and
never the one named by the caller's environment. Author/committer identity variables are kept.
"""
from __future__ import annotations

import os

# Everything git reads to locate a repository, index, object store or work tree.
REPO_LOCATION_VARS = (
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_PREFIX",
    "GIT_NAMESPACE",
    "GIT_QUARANTINE_PATH",
    "GIT_IMPLICIT_WORK_TREE",
)


def clean_env(base: dict[str, str] | None = None, **extra: str) -> dict[str, str]:
    """A copy of `base` (default: os.environ) without the repository-location variables, plus `extra`."""
    src = os.environ if base is None else base
    env = {k: v for k, v in src.items() if k not in REPO_LOCATION_VARS}
    env.update(extra)
    return env


def scrub_process_env() -> list[str]:
    """Remove the repository-location variables from THIS process; return the names removed.

    For scripts that call git in-process on behalf of a hook (scripts/verify_all.py): every harness
    module that shells out to git inside that process then targets the root it was given."""
    removed = [k for k in REPO_LOCATION_VARS if k in os.environ]
    for k in removed:
        os.environ.pop(k, None)
    return removed
