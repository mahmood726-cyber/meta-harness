"""Fail-closed scope comparison of independently supplied PICO objects.

Each axis is an explicit scope description (a nonempty string). Equality is
conservative: only case and whitespace are normalized, not clinical meaning.
Titles, keyword hits and stored verdicts cannot establish PICO equivalence.
"""
from __future__ import annotations

AXES = ("population", "intervention_level", "comparator", "outcome", "design")


def _known(value):
    if not isinstance(value, str):
        return None
    value = " ".join(value.casefold().split())
    if value in {"", "unknown", "not stated", "not reported", "not assessed",
                 "unclear", "n/a", "none", "null", "?"}:
        return None
    return value


def compare_pico(ours: dict | None, theirs: dict | None) -> dict:
    ours = ours if isinstance(ours, dict) else {}
    theirs = theirs if isinstance(theirs, dict) else {}
    matches = {}
    for axis in AXES:
        left, right = _known(ours.get(axis)), _known(theirs.get(axis))
        matches[axis] = ("UNKNOWN" if left is None or right is None else
                         "MATCH" if left == right else "MISMATCH")
    valid = all(status == "MATCH" for status in matches.values())
    return {"axis_matches": matches, "scope_valid": valid,
            "note": ("All PICO axes match." if valid else
                     "Scope equivalence is not established: differing or unknown PICO axes.")}


def assess(config: dict, comparator_title: str, comparator_abstract: str = "",
           comparator_pico: dict | None = None) -> dict:
    # Keep the bibliographic arguments for callers; they are not PICO evidence.
    return compare_pico(config.get("pico"), comparator_pico)
