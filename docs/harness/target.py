"""Target assertions for checks that must name what they inspected.

A verifier that cannot name its tree/ref/file set has not measured anything
auditable. This helper centralizes the common git/worktree wording used by the
checks and raises before a caller can silently fall back to a default target.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Iterable


class TargetUnresolvable(RuntimeError):
    """Raised when a check cannot name its intended target."""


def _run_git(root: str | os.PathLike[str], args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _git_stdout(root: str | os.PathLike[str], args: list[str], reason: str) -> str:
    proc = _run_git(root, args)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise TargetUnresolvable(f"{reason}: {detail}")
    return proc.stdout.strip()


def _resolve_ref(root: str | os.PathLike[str], ref: str) -> str:
    if not isinstance(ref, str) or not ref.strip():
        raise TargetUnresolvable("empty ref")
    return _git_stdout(root, ["rev-parse", "--verify", f"{ref}^{{commit}}"], f"ref not resolvable: {ref}")


def _tree_state(root: str | os.PathLike[str]) -> str:
    proc = _run_git(root, ["status", "--porcelain"])
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise TargetUnresolvable(f"worktree status unavailable: {detail}")
    dirty = [line for line in proc.stdout.splitlines() if line.strip()]
    return "clean" if not dirty else f"dirty:{len(dirty)} files"


def _display_path(root: Path, raw: str | os.PathLike[str]) -> str:
    text = os.fspath(raw).replace("\\", "/")
    if "://" in text:
        return text
    path = Path(os.fspath(raw))
    try:
        if path.is_absolute():
            return path.resolve().relative_to(root).as_posix()
    except (OSError, ValueError):
        return text
    return text


def describe_target(
    root: str | os.PathLike[str],
    *,
    refs: Iterable[str] = (),
    paths: Iterable[str | os.PathLike[str]] = (),
    label: str,
) -> str:
    """Return a one-line ``TARGET`` statement for a check.

    ``refs`` are resolved as commits. The first resolved ref is displayed as
    ``base`` because most checks compare HEAD to one base; callers that need
    extra ref detail append it to the returned line. ``paths`` must be the
    explicit file/URL set the check intends to read and must not be empty.
    """

    if not isinstance(label, str) or not label.strip():
        raise TargetUnresolvable("target label is empty")
    root_path = Path(root).resolve()
    head = _resolve_ref(root_path, "HEAD")
    resolved_refs = [_resolve_ref(root_path, ref) for ref in refs]
    path_list = [os.fspath(path) for path in paths]
    if not path_list:
        raise TargetUnresolvable("file set is empty")
    tree = _tree_state(root_path)
    shown = [_display_path(root_path, path) for path in path_list[:3]]
    suffix = " ".join(shown)
    if len(path_list) > 3:
        suffix = (suffix + " ..." if suffix else "...")
    base = resolved_refs[0] if resolved_refs else "none"
    return f"TARGET {label}: head={head} base={base} tree={tree} files={len(path_list)} {suffix}".rstrip()


def refusal(label: str, reason: str) -> str:
    return f"TARGET {label}: COULD-NOT-EXECUTE {reason}"
