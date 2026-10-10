"""Bind each definition-audit row to the served row VERSION it judged (external audit 26-A / 28-C / 29: STRENGTH,
REDUCE-IT and FOURIER rows still said "5-point primary" after those pooled rows became 3-point outcomes, and
compat_check took the audit row FIRST, so the served compatibility panel repeated the stale text).

A row applies only while the served trial row is the version it judged: same effect, CI, scale and source span
(sha256). Otherwise it is AUDIT_ROW_STALE and is never rendered as the definition; a row with no recorded version is
UNBOUND and is not used either (fail closed).
"""
from __future__ import annotations

import hashlib
from typing import Any

BOUND_CURRENT, AUDIT_ROW_STALE, UNBOUND = "BOUND_CURRENT", "AUDIT_ROW_STALE", "UNBOUND"
FIELDS = ("effect", "ci_low", "ci_high", "scale")


def trial_fingerprint(trial: dict[str, Any]) -> dict[str, Any]:
    src = str(trial.get("source") or "")
    return {**{f: trial.get(f) for f in FIELDS}, "source_sha256": hashlib.sha256(src.encode("utf-8")).hexdigest()}


def audit_state(row: dict[str, Any] | None, trial: dict[str, Any]) -> str | None:
    if not row:
        return None
    judged = row.get("judged")
    if not isinstance(judged, dict) or not all(k in judged for k in (*FIELDS, "source_sha256")):
        return UNBOUND
    now = trial_fingerprint(trial)
    return BOUND_CURRENT if all(judged.get(k) == now.get(k) for k in now) else AUDIT_ROW_STALE
