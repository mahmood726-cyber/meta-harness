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
    try:
        reg = json.load(open(os.path.join(root or ROOT, "registry", registry), encoding="utf-8"))
    except (OSError, ValueError):
        return None
    sha = hashlib.sha256((text or "").encode("utf-8")).hexdigest()
    for e in reg.get("entries") or []:
        if str(e.get("pmid")) == str(pmid) and e.get("held_text_sha256") == sha and e.get("claim") == claim:
            return e
    return None
