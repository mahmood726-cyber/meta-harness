"""Recorded, text-bound verifications: a claim about what a held source says (or does not say) that no pattern over prose
can establish reliably.

Codex review rounds (copps-r11..r16) found a new prose form each time a regex tried to decide such a claim -- that a
source does not state per-arm denominators, or that a source identifies ENGAGE's low-dose arm as 30 mg. So these claims
are recorded once, after a person or a recorded read has checked the text, and each record is bound to the sha256 of the
exact held text it was checked against: a changed text, or another record, inherits nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def verified(registry: str, pmid: str, text: str, claim: str, root: str | None = None) -> dict[str, Any] | None:
    """The entry of registry/<registry> recording `claim` for `pmid`, if its held_text_sha256 is this text's; else None."""
    path = os.path.join(root or ROOT, "registry", registry)
    try:
        reg = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        # an unreadable registry is a broken build, never a valid 'not verified' (codex copps-r17#2): fail loudly
        raise RuntimeError(f"verification registry {path} unreadable: {exc}") from exc
    entries = reg.get("entries") if isinstance(reg, dict) else None
    if not isinstance(entries, list):
        # malformed contents are a broken registry too, never an empty one (codex copps-r18#2)
        raise RuntimeError(f"verification registry {path} has no 'entries' list")
    sha = hashlib.sha256((text or "").encode("utf-8")).hexdigest()
    for e in entries:
        if str(e.get("pmid")) == str(pmid) and e.get("held_text_sha256") == sha and e.get("claim") == claim:
            return e
    return None
