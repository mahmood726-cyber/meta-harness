"""Git blob identities of working-tree files, AS GIT WOULD STORE THEM.

A seal or an architecture identity that hashes raw working-tree bytes is not portable: on a Windows
checkout 85 tracked files carry CRLF in the worktree while their index blobs are LF (attr text=auto
eol=lf), so a sha1 of the raw bytes differs from the blob CI sees on an LF checkout. That made a
freshness computed locally read CURRENT and the same computation on CI read STALE (fixstate-orthogonal,
2026-09-14: CI refused a branch whose local verify passed). The identity of a dependency is the blob
git stores after its clean filter -- so ask git, in one batched process per call, never Python's sha1
of the bytes on disk.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path


class BlobUnavailable(RuntimeError):
    """git could not produce blob identities (no git, not a repository, or a path git cannot read)."""


def _is_git_toplevel(repo: Path) -> bool:
    proc = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return False
    try:
        return Path(proc.stdout.strip()).resolve() == repo
    except OSError:
        return False


def _direct_hash_objects(repo: Path, present: list[tuple[str, str]]) -> dict[str, str]:
    out: dict[str, str] = {}
    for rel, native in present:
        proc = subprocess.run(
            ["git", "hash-object", "--", native],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            raise BlobUnavailable(
                f"git hash-object failed in {repo}: {(proc.stderr or proc.stdout).strip()}"
            )
        out[rel] = proc.stdout.strip()
    return out


def blob_shas(root: str | os.PathLike[str], relpaths: list[str]) -> dict[str, str | None]:
    """Return {relpath: blob sha1 or None} for working-tree files, normalised by git's clean filters.

    A path that is not a regular file maps to None (a missing dependency is a fact the caller reports,
    not a default). Relative paths use forward slashes; order of the input is preserved in the output.
    """
    repo = Path(root).resolve()
    out: dict[str, str | None] = {}
    present: list[tuple[str, str]] = []
    for raw in relpaths:
        rel = os.fspath(raw).replace("\\", "/")
        if (repo / rel).is_file():
            present.append((rel, rel.replace("/", os.sep)))
        else:
            out[rel] = None
    if not present:
        return {rel: out.get(rel) for rel in (os.fspath(r).replace("\\", "/") for r in relpaths)}
    if not _is_git_toplevel(repo):
        out.update(_direct_hash_objects(repo, present))
        return {rel: out.get(rel) for rel in (os.fspath(r).replace("\\", "/") for r in relpaths)}
    proc = subprocess.run(
        ["git", "hash-object", "--stdin-paths"],
        cwd=repo,
        input="\n".join(native for _, native in present) + "\n",
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        raise BlobUnavailable(f"git hash-object failed in {repo}: {(proc.stderr or proc.stdout).strip()}")
    shas = proc.stdout.split()
    if len(shas) != len(present):
        raise BlobUnavailable(f"git hash-object returned {len(shas)} identities for {len(present)} paths")
    for (rel, _native), sha in zip(present, shas):
        out[rel] = sha
    return {rel: out.get(rel) for rel in (os.fspath(r).replace("\\", "/") for r in relpaths)}


def blob_sha(root: str | os.PathLike[str], relpath: str) -> str | None:
    return blob_shas(root, [relpath])[os.fspath(relpath).replace("\\", "/")]
