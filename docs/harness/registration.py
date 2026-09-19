"""Registration SHA resolution for preregistered reviews."""
from __future__ import annotations

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = "PREREGISTRATION_v2.md"


def _git_log(path: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", ROOT, "log", "-1", "--format=%H", "--", path],
            text=True,
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def protocol_sha(slug: str) -> str | None:
    """Return the topic protocol SHA, or the expansion-batch preregistration SHA.

    The normal per-protocol commit remains authoritative. Expansion topics in
    PREREGISTRATION_v2.md were preregistered as one committed batch, so they can
    be built for human review before their generated artifacts are committed.
    """
    per_protocol = _git_log(f"protocols/{slug}.md")
    if per_protocol:
        return per_protocol

    prereg_path = os.path.join(ROOT, PREREG)
    try:
        prereg_text = open(prereg_path, encoding="utf-8").read()
    except OSError:
        return None
    if slug not in prereg_text:
        return None
    batch_sha = _git_log(PREREG)
    return batch_sha or None


_BUILD_PREFIXES = ("cache/", "docs/reviews/", "docs/m/")


def _files_in(sha: str) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", ROOT, "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            text=True, stderr=subprocess.DEVNULL)
        return [f for f in out.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []


def is_build_commit(sha: str) -> bool:
    """A commit is a BUILD commit (not a prospective registration) if it contains any generated artifact --
    fetched cache, extracted review, blind pages, or the index. A commit that adds a protocol/PICO
    ALONGSIDE those cannot demonstrate that the protocol preceded synthesis."""
    if not sha:
        return False
    return any(f.startswith(_BUILD_PREFIXES) or f == "docs/index.html" for f in _files_in(sha))


def _log_all(path: str) -> list[str]:
    try:
        return [s for s in subprocess.check_output(
            ["git", "-C", ROOT, "log", "--format=%H", "--", path], text=True).splitlines() if s]
    except subprocess.CalledProcessError:
        return []


def build_sha(slug: str) -> str | None:
    """The commit that produced the current review artifact (most recent protocols/<slug>.md commit, or the
    preregistration batch). The replay anchor -- NOT a proof of prospective registration."""
    return protocol_sha(slug)


def preregistration_sha(slug: str) -> dict:
    """Distinguish 'protocol registered BEFORE synthesis' from 'protocol committed WITH the build'.
    Returns {prospective, sha, kind, build_sha}. Prospective = the EARLIEST protocols/<slug>.md commit that
    contained ONLY protocol/PICO files; failing that, the PREREGISTRATION_v2.md batch if this topic is
    listed there and that batch is protocol-only. If neither exists, prospective is False (the protocol
    first entered the repo inside a build commit) -- reported honestly, never claimed."""
    bsha = build_sha(slug)
    for sha in reversed(_log_all(f"protocols/{slug}.md")):  # oldest first
        if not is_build_commit(sha):
            return {"prospective": True, "sha": sha, "kind": "protocol-file (earliest, protocol-only)",
                    "build_sha": bsha}
    try:
        prereg_text = open(os.path.join(ROOT, PREREG), encoding="utf-8").read()
    except OSError:
        prereg_text = ""
    batch = _git_log(PREREG)
    if slug in prereg_text and batch and not is_build_commit(batch):
        return {"prospective": True, "sha": batch, "kind": "PREREGISTRATION_v2 batch (protocol-only)",
                "build_sha": bsha}
    return {"prospective": False, "sha": None,
            "kind": "no protocol-only commit -- protocol first committed inside a build", "build_sha": bsha}
