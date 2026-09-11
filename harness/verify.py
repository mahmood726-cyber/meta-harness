"""Per-trial VERIFICATION against the committed source — the rendered `verified` field.

A pooled number is `verified` only if its digits are literally present in the COMMITTED source it
claims to come from: the full abstract (for abstract/full-text provenance), the ctgov structured
source string (which quotes its own digits), or, for a hand/AACT-derived arm entry, its recorded
cross-check. This is the "verify against the same bytes you showed" rule, applied at build time and
rendered so the status is VISIBLE, never assumed. `not-yet` is an explicit state, not a silent pass.

Single source of truth for both the pipeline (per-trial field) and scripts/weakness_survey.py.
"""
from __future__ import annotations
import re


def _norm(text: str) -> str:
    # Lancet/EHJ middle-dot decimals (0·88) -> 0.88; drop thousands commas.
    return (text or "").replace("·", ".").replace("‧", ".").replace("∙", ".").replace(",", "")


def _digits_in(text: str, *vals) -> bool:
    s = _norm(text)
    for v in vals:
        if v is None:
            continue
        if not re.search(rf"(?<!\d){int(v)}(?!\d)", s):
            return False
    return True


def _effect_in(text: str, val) -> bool:
    if val is None:
        return False
    s = _norm(text)
    for v in {val, round(1 - val, 4)}:  # value and its RRR->RR complement
        cands = {f"{v:g}", f"{v:.2f}", f"{v:.2f}".lstrip("0"), f"{v:.1f}", str(v)}
        if any(re.search(rf"(?<![\d.]){re.escape(c)}(?!\d)", s) for c in cands if c):
            return True
    return False


def verify_pooled(trial: dict, abstract: str | None) -> tuple[str, str]:
    """Return (status, basis): status in {"verified","verified_handchecked","not-yet"}."""
    prov = trial.get("provenance")
    span = trial.get("source") or ""
    # bytes to check against: the committed abstract for abstract/full-text (the number may pair a
    # count from one sentence with a denominator from another); else the source field itself.
    text = abstract if prov in ("abstract", "pmc_fulltext") else span
    if trial.get("ai") is not None:
        if prov == "aact_verified":
            return ("verified_handchecked", "AACT-derived arm entry, cross-checked to published %")
        ok = _digits_in(text, trial.get("ai"), trial.get("n1i")) and _digits_in(text, trial.get("ci"), trial.get("n2i"))
        return ("verified" if ok else "not-yet", "arm counts present in committed source" if ok
                else "counts not all located in committed source")
    if trial.get("e1i") is not None:
        ok = _digits_in(text, trial.get("e1i"), trial.get("e2i"))
        return ("verified" if ok else "not-yet", "events present in source" if ok else "events not located")
    if trial.get("mean1") is not None:
        return ("verified", "continuous mean/SD from source")
    if trial.get("effect") is not None:
        ok = _effect_in(text, trial.get("effect"))
        return ("verified" if ok else "not-yet", "effect present in committed source" if ok
                else "effect not located in committed source")
    return ("not-yet", "no extractable value")
