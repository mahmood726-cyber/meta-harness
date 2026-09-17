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
    # Published prose can spell small integer counts (e.g. "Eighteen of 245").
    # This is lexical normalization only; never derive a count from a percentage.
    words = ("zero one two three four five six seven eight nine ten eleven twelve "
             "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
    for number, word in enumerate(words):
        s = re.sub(r"\b" + word + r"\b", str(number), s, flags=re.I)
    for v in vals:
        if v is None:
            continue
        words = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
                 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"}
        word = words.get(int(v)) if v == int(v) else None
        if not re.search(rf"(?<!\d){int(v)}(?!\d)", s) and not (
                word and re.search(rf"\b{word}\b", s, re.I)):
            return False
    return True


def _rate_pct_in(text: str, events, n) -> bool:
    """A binary arm count RECOVERED FROM A PUBLISHED RATE (many trials report '64% of 111', not the
    raw count): the count is grounded when the percentage it implies, 100*events/n, appears as a
    '<x>%' token in the committed source at 0- or 1-decimal precision. Non-circular -- the rate and
    denominator are the abstract's own reported values, and only the unique integer consistent with
    that rate+denominator round-trips (e.g. 71/111 -> 63.96% -> '64%'; 10/16 -> '62.5%')."""
    if not text or not n:
        return False
    s = _norm(text)
    r = 100.0 * events / n
    cands = {f"{round(r)}", f"{r:.1f}"}
    return any(re.search(rf"(?<![\d.]){re.escape(c)}\s*%", s) for c in cands)


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
    if trial.get('source_level') or trial.get('document_sha256'):
        from .verified_source import refusal
        reason = refusal(trial)
        return ('not-yet', reason) if reason else ('verified', 'effect and CI in digest-verified committed span')
    prov = trial.get("provenance")
    span = trial.get("source") or ""
    # bytes to check against: the committed abstract for abstract/full-text (the number may pair a
    # count from one sentence with a denominator from another); else the source field itself.
    text = abstract if prov in ("abstract", "pmc_fulltext") else span
    if trial.get("ai") is not None:
        if prov == "aact_verified":
            return ("verified_handchecked", "AACT-derived arm entry, cross-checked to published %")
        if prov == "published_rate":
            # counts recovered from a published percentage + denominator: verify each count round-trips
            # to a '<x>%' token in the abstract AND the denominator (or the equally-allocated total) is
            # grounded in the abstract -- so a wrong count or denominator fails, not a trusted pass.
            n1, n2 = trial.get("n1i"), trial.get("n2i")
            tot = (n1 or 0) + (n2 or 0)
            ok = (_rate_pct_in(abstract, trial.get("ai"), n1) and _rate_pct_in(abstract, trial.get("ci"), n2)
                  and (_digits_in(abstract, n1) or _digits_in(abstract, tot))
                  and (_digits_in(abstract, n2) or _digits_in(abstract, tot)))
            return ("verified_handchecked" if ok else "not-yet",
                    "arm counts recovered from the published rate + denominator (percentage round-trip matches the committed abstract)"
                    if ok else "recovered counts do not round-trip to a published percentage in the source")
        ok = _digits_in(text, trial.get("ai"), trial.get("n1i")) and _digits_in(text, trial.get("ci"), trial.get("n2i"))
        return ("verified" if ok else "not-yet", "arm counts present in committed source" if ok
                else "counts not all located in committed source")
    if trial.get("mean1") is not None:
        # Continuous (mean-difference) input: verify each arm's mean AND SD digits appear in the
        # committed source span, exactly as the count path does — was previously trusted unconditionally.
        ok = (_digits_in(text, trial.get("mean1"), trial.get("sd1"))
              and _digits_in(text, trial.get("mean2"), trial.get("sd2")))
        return ("verified" if ok else "not-yet",
                "continuous per-arm mean/SD present in committed source" if ok
                else "mean/SD not all located in committed source")
    if trial.get("e1i") is not None:
        ok = _digits_in(text, trial.get("e1i"), trial.get("e2i"))
        return ("verified" if ok else "not-yet", "events present in source" if ok else "events not located")
    if trial.get("effect") is not None:
        ok = _effect_in(text, trial.get("effect"))
        return ("verified" if ok else "not-yet", "effect present in committed source" if ok
                else "effect not located in committed source")
    return ("not-yet", "no extractable value")
