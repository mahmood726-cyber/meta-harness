"""Leave-one-out INFERENCE stability (C4, external audit R8-1 and review 13).

A leave-one-out table of point estimates alone says nothing about inference: in esketamine every re-pooled HKSJ CI
crosses 0 while the points barely move. Point stability (the range of re-pooled estimates) and inference stability
(whether each re-pooled 95% CI keeps the full pool's position relative to the null) are reported separately, and no
"robust" / "no single trial drives it" wording is emitted when a drop changes the inference.
"""
from __future__ import annotations

POSITIONS = ("BELOW_NULL", "INCLUDES_NULL", "ABOVE_NULL")


def ci_position(lo, hi, null):
    """BELOW_NULL / ABOVE_NULL when the 95% CI lies strictly on one side of the null, INCLUDES_NULL when it touches or
    crosses it, NO_CI when an end is missing."""
    if lo is None or hi is None:
        return "NO_CI"
    if hi < null:
        return "BELOW_NULL"
    if lo > null:
        return "ABOVE_NULL"
    return "INCLUDES_NULL"


def inference_summary(rows, full, null):
    """{inference_changed_by, inference_assessed, note} -- the note never claims stability it has not shown."""
    assessed = [r for r in rows if r.get("inference") in POSITIONS]
    changed = [r["dropped"] for r in assessed if full in POSITIONS and r["inference"] != full]
    n_k2 = sum(1 for r in rows if r.get("inference") == "NOT_ASSESSED_K2")
    null_txt = "0" if null == 0.0 else "1"
    parts = ["each row drops one trial and re-pools with the same method (Paule-Mandel tau^2, HKSJ 95% CI); the "
             "range of re-pooled estimates is POINT stability, and whether each re-pooled CI keeps the full pool's "
             f"position relative to the null ({null_txt}) is INFERENCE stability"]
    if full not in POSITIONS:
        parts.append("inference stability is not assessed: the full pool has no served CI")
    elif not assessed:
        parts.append("inference stability is not assessed: every re-pool has k=2, whose CI is not served")
    elif changed:
        parts.append("dropping " + ", ".join(str(c) for c in changed) + " changes the inference (its re-pooled CI "
                     "is on a different side of, or crosses, the null)")
    else:
        parts.append(f"every assessed re-pooled CI ({len(assessed)} of {len(rows)}) keeps the full pool's position "
                     "relative to the null")
    if n_k2 and assessed:
        parts.append(f"{n_k2} re-pool(s) have k=2: CI not served, inference not assessed")
    return {"inference_changed_by": changed, "inference_assessed": len(assessed), "note": "; ".join(parts) + "."}
