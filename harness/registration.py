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
