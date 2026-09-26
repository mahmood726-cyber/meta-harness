"""EFFECT IDENTITY BEFORE SOURCE PREFERENCE (external review of colchicine-recurrent-pericarditis, 2026-09-26).

(1) SOURCE_EFFECT_CONFLICT. The source hierarchy preferred CORP-2's published "relative risk 0.49; 95% CI 0.24-0.65" over its own
counts, 26/120 vs 51/120, which give RR 0.5098 (0.342-0.760). 0.49 = 1 - 0.51 and 1 - the count CI = 0.240-0.658: the published
number is the RELATIVE RISK REDUCTION under an RR label (the abstract itself says "relative risk 0.49"). When a published ratio sits
beside counts for the same result, conflict_check() recomputes the count-implied tuple and tests named mislabel hypotheses against
point AND both CI ends: AS_LABELLED, RRR_AS_RR (1-x, ends swapped), OR_AS_RR / RR_AS_OR, RECIPROCAL (1/x, ends swapped). Disagreement
is SOURCE_EFFECT_CONFLICT with the hypotheses that match. NOTHING IS RELABELLED: the row is HELD unless its own text documents a
model that explains the difference (an adjusted estimate), in which case the published effect is kept and the conflict disclosed.
An HR is not comparable to crude counts and is recorded as NOT_COMPARABLE, never tested.

(2) TRANSFORMATION PROVENANCE. CORP's "relative risk reduction, 0.56 [CI, 0.27 to 0.73]" is correctly converted to RR 0.44
(0.27-0.73) by extract._effect_from_match, but the row said KEEP_REPORTED_EFFECT / reported_label RR. transform_provenance() reads
the row's own quotation with the extractor's own regex and records {reported_measure, reported, transform, derived}. The recurrence
CI looks unchanged (0.27-0.73 both before and after) only because its ends sum to 1 -- which is exactly why it must be recorded.
"""
from __future__ import annotations

import math
from typing import Any

from . import extract

Z95 = 1.959963984540054
RATIO = ("RR", "OR")


def counts_tuple(ai, n1i, ci, n2i, measure: str) -> dict[str, float] | None:
    """RR (Katz log) or OR (Woolf log) with a 95% CI from a 2x2. None when a cell is zero or a count is missing (no continuity
    correction here: a conflict check must not invent a number)."""
    try:
        a, n1, c, n2 = (int(x) for x in (ai, n1i, ci, n2i))
    except (TypeError, ValueError):
        return None
    b, d = n1 - a, n2 - c
    if min(a, b, c, d) <= 0:
        return None
    if measure == "RR":
        est, se = (a / n1) / (c / n2), math.sqrt(1 / a - 1 / n1 + 1 / c - 1 / n2)
    else:
        est, se = (a * d) / (b * c), math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    lo, hi = est * math.exp(-Z95 * se), est * math.exp(Z95 * se)
    return {"estimate": est, "ci_low": lo, "ci_high": hi}


def _decimals(x) -> int:
    s = f"{x}"
    return len(s.split(".")[1]) if "." in s else 0


def _close(pub: tuple, hyp: tuple) -> tuple[bool, list[float]]:
    """Every published number within its own rounding (half a unit in its last place) plus a small method slack (0.006: the
    source may use a different CI method than Katz/Woolf)."""
    deltas = [abs(p - h) for p, h in zip(pub, hyp)]
    tol = [0.5 * 10 ** -max(_decimals(p), 1) + 0.006 for p in pub]
    return all(dv <= t for dv, t in zip(deltas, tol)), [round(dv, 4) for dv in deltas]


def hypotheses(pub_scale: str, pub: tuple, rr: dict | None, orr: dict | None) -> list[dict[str, Any]]:
    out = []

    def add(name, basis):
        if basis is None:
            return
        ok, deltas = _close(pub, basis)
        out.append({"hypothesis": name, "matches": ok, "implied": [round(x, 4) for x in basis], "deltas": deltas})
    t = lambda d: (d["estimate"], d["ci_low"], d["ci_high"]) if d else None
    rr_t, or_t = t(rr), t(orr)
    if pub_scale == "RR":
        add("AS_LABELLED", rr_t)
        add("RRR_AS_RR", rr_t and (1 - rr_t[0], 1 - rr_t[2], 1 - rr_t[1]))
        add("OR_AS_RR", or_t)
    else:
        add("AS_LABELLED", or_t)
        add("RR_AS_OR", rr_t)
    base = rr_t if pub_scale == "RR" else or_t
    add("RECIPROCAL", base and (1 / base[0], 1 / base[2], 1 / base[1]))
    return out


def _counts_of(row: dict[str, Any]) -> tuple | None:
    if all(row.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
        return tuple(row[k] for k in ("ai", "n1i", "ci", "n2i"))
    for alt in row.get("alternatives") or []:
        if all(alt.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
            return tuple(alt[k] for k in ("ai", "n1i", "ci", "n2i"))
    return None


def conflict_check(row: dict[str, Any], adjusted_documented: bool = False) -> dict[str, Any] | None:
    """None when there is nothing to compare (no published ratio, or no counts for the same result). Otherwise a record:
    state CONSISTENT / NOT_COMPARABLE / SOURCE_EFFECT_CONFLICT, the tested hypotheses, and a resolution: KEEP (consistent),
    KEEP_DISCLOSED (conflict explained by a documented adjusted model) or HOLD."""
    if row.get("effect") is None or row.get("ci_low") is None or row.get("ci_high") is None:
        return None
    scale = str(row.get("scale") or "").upper()
    counts = _counts_of(row)
    if counts is None:
        return None
    pub = (float(row["effect"]), float(row["ci_low"]), float(row["ci_high"]))
    rec = {"published": {"scale": scale, "estimate": pub[0], "ci_low": pub[1], "ci_high": pub[2]}, "counts": list(counts)}
    if scale not in RATIO:
        return {**rec, "state": "NOT_COMPARABLE", "resolution": "KEEP",
                "reason": f"a published {scale or 'unlabelled'} is not the crude ratio its counts give; no mislabel test is defined"}
    rr, orr = counts_tuple(*counts, "RR"), counts_tuple(*counts, "OR")
    if (rr if scale == "RR" else orr) is None:
        return {**rec, "state": "NOT_COMPARABLE", "resolution": "KEEP", "reason": "a zero cell: no count-implied interval without a correction"}
    hyps = hypotheses(scale, pub, rr, orr)
    rec.update(counts_implied={"RR": rr and {k: round(v, 4) for k, v in rr.items()}, "OR": orr and {k: round(v, 4) for k, v in orr.items()}},
               hypotheses=hyps)
    if next(h for h in hyps if h["hypothesis"] == "AS_LABELLED")["matches"]:
        return {**rec, "state": "CONSISTENT", "resolution": "KEEP"}
    matching = [h["hypothesis"] for h in hyps if h["matches"]]
    rec.update(state="SOURCE_EFFECT_CONFLICT", code="SOURCE_EFFECT_CONFLICT", matching_hypotheses=matching)
    if adjusted_documented:
        rec.update(resolution="KEEP_DISCLOSED", reason="the published effect is documented as an ADJUSTED estimate in its own text; a "
                   "crude count ratio is expected to differ -- kept, conflict disclosed")
    else:
        rec.update(resolution="HOLD", reason=("the published effect disagrees with its own counts"
                   + (f"; it matches {', '.join(matching)} -- a mislabel hypothesis, never applied silently" if matching else
                      "; no named mislabel hypothesis explains it")
                   + ". Held until evidence resolves it (e.g. a documented adjusted model, or a reviewer's typed resolution)"))
    return rec


def transform_provenance(row: dict[str, Any], abstract: str | None = None) -> dict[str, Any] | None:
    """What the source REPORTED, when the served effect was transformed from it. Read with the extractor's own effect regex from
    the row's own quotation, then from the held abstract (a stored quotation is cut at 200 characters -- CORP's ends mid-CI);
    only a match that reproduces the served tuple EXACTLY through a known transform is recorded, so a nearby unrelated effect
    can never be taken for the reported one."""
    if row.get("effect") is None:
        return None
    served = (row.get("effect"), row.get("ci_low"), row.get("ci_high"))
    for src, where in ((row.get("source") or "", "row quotation"), (abstract or "", "held abstract")):
        hit = _transform_in(src, served)
        if hit:
            return {**hit, "read_from": where}
    return None


def _transform_in(src: str, served) -> dict[str, Any] | None:
    for m in extract._EFFECT.finditer(src):
        kind = m.group(1).lower()
        try:
            pt, lo, hi = float(m.group(2)), float(m.group(3)), float(m.group(4))
        except (TypeError, ValueError, IndexError):
            continue
        if "reduction" in kind:
            derived = (round(1 - pt, 4), round(1 - hi, 4), round(1 - lo, 4))
            if tuple(float(x) for x in served) == derived:
                return {"reported_measure": "RRR", "reported": {"estimate": pt, "ci_low": lo, "ci_high": hi},
                        "transform": "RR = 1 - RRR; CI endpoints swapped (RR_low = 1 - RRR_high, RR_high = 1 - RRR_low)",
                        "derived": {"measure": "RR", "estimate": derived[0], "ci_low": derived[1], "ci_high": derived[2]},
                        "reported_text": m.group(0),
                        "note": ("the interval is symmetric about 0.5, so its ends look unchanged by the transform"
                                 if abs((lo + hi) - 1) < 1e-9 else None)}
    return None


_ADJUSTED = __import__("re").compile(
    r"(?<![-\w])adjusted\s+(?:hazard|relative|risk|odds|rate|incidence|HR|RR|OR|IRR)\b|(?<![-\w])adjust(?:ed|ing)?\s+for\b"
    r"|\bmultivariab?le\b|\bmultivariate\b|\bcovariate[- ]adjusted\b"
    # a COVARIATE-prefixed "-adjusted" is adjustment ("age-adjusted rate ratio"); "multiplicity-" / "dose-adjusted" are not
    r"|\b(?:age|sex|risk|baseline|fully|covariate|stratum|strata)[- ]adjusted\b", __import__("re").I)


def adjusted_documented(row: dict[str, Any]) -> bool:
    """Evidence that the published effect comes from an ADJUSTED model, in the row's OWN quotation (never "multiplicity-adjusted"
    or "dose-adjusted"). The only evidence this module accepts on its own for keeping a published effect that disagrees with its
    counts; anything else is a reviewer's typed resolution."""
    return bool(_ADJUSTED.search(row.get("source") or ""))


def held_absence(t: dict[str, Any]) -> dict[str, Any]:
    """A HELD row stays visible, with the number, its counts, every tested hypothesis and the reason -- not pooled, not refused."""
    c = t.get("effect_conflict") or {}
    return {"label": t.get("label"), "id": t.get("id"), "absent_kind": "machine_absent", "state": "HELD_SOURCE_EFFECT_CONFLICT",
            "reason_code": "SOURCE_EFFECT_CONFLICT", "endpoint_admissibility": "HELD_SOURCE_EFFECT_CONFLICT",
            "candidate_tuple": {k: t.get(k) for k in ("effect", "ci_low", "ci_high", "scale") if t.get(k) is not None},
            "effect_conflict": c, "source": t.get("source", ""), "provenance": t.get("provenance"),
            "reason": c.get("reason"),
            "recovery": ("a reviewer records a typed resolution with evidence (which number the source means, and why), or the "
                         "published effect is shown to come from a documented adjusted model")}
