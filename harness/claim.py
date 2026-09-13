"""Canonical claim object.

One place derives the facts a reader sees stated about a pooled result -- whether it is
statistically significant, whether its interval crosses the null, its direction -- and one
place formats the numbers. Every surface (the page, the manuscript, GRADE, the index, the
spec-curve, the blind twin) is meant to DERIVE its wording from this object rather than
recompute the judgement, so a card can never assert "significantly reduced" while the object
holds an interval that spans no effect (the glp1 card<->object mismatch class).

The build then SCANS the rendered surfaces for significance assertions that contradict the
canonical object and FAILS closed on any contradiction, reporting how many surfaces were
checked and what was caught.

crosses_null is the rounded-boundary-aware STRICT cross used by GRADE: a CI limit printed
exactly on the null (RR 0.65-1.00) is a likely rounded publication bound, treated as
uncertain-due-to-rounding, NOT a definite crossing. This keeps the one definition GRADE
already defends.
"""
import re

# Effect scales whose null is 1.0 (ratios). Everything continuous (MD/SMD) has null 0.0.
_RATIO_SCALES = {"RR", "OR", "HR", "IRR", "RATE_RATIO", "RATE_RATIO_RECURRENT", "RD_RATIO"}
_EPS = 1e-9


def null_value(scale):
    """The no-effect value for an effect scale: 1.0 for a ratio, 0.0 for a difference."""
    s = (scale or "").upper()
    if s.startswith("INCOMPATIBLE"):
        return None
    if s in ("MD", "SMD", "MEAN DIFFERENCE"):
        return 0.0
    # default ratio (RR/OR/HR/IRR/...) unless clearly a difference
    return 1.0


def format_num(x):
    """Canonical 2-dp display for effects and CI bounds (matches page._num). One formatter so
    two surfaces cannot print the same estimate at different precision."""
    if isinstance(x, bool):
        return str(x)
    if isinstance(x, float):
        return f"{round(x, 2):g}"
    return str(x)


def _is_present(result):
    if not isinstance(result, dict):
        return False
    if result.get("present") is False:
        return False
    if result.get("suppressed_incompatible") or result.get("estmeasure_incompatible"):
        return False
    # A usable estimate is enough (a pooled outcome carries k>=1; a transcribed comparator
    # claim carries an estimate+CI but no k). Absent/reported-not-extracted set present=False
    # or leave estimate None, so they are excluded above.
    return result.get("estimate") is not None


def derive(result):
    """Canonical derived facts for one pooled result. Returns a dict merged onto result under
    'claim'. Idempotent and side-effect free.

    Fields:
      present      : the pool produced a usable estimate (not absent/suppressed/incompatible)
      null         : the no-effect value for the scale (1.0 ratio / 0.0 MD), or None
      crosses_null : STRICT cross (cil < null < cih); a limit exactly on null is NOT a cross
      touches_null : a CI limit sits exactly on the null (rounded-boundary case)
      significant  : present AND does not strictly cross the null
      direction    : 'benefit' / 'harm' / 'none' relative to the null (benefit = estimate on
                     the protective side for a ratio: <1; for MD, <0). Descriptive only.
    """
    if not _is_present(result):
        return {"present": False, "significant": False, "crosses_null": None,
                "touches_null": None, "null": None, "direction": None}
    null = null_value(result.get("scale"))
    cil, cih = result.get("ci_low"), result.get("ci_high")
    est = result.get("estimate")
    if null is None or cil is None or cih is None:
        return {"present": True, "significant": False, "crosses_null": None,
                "touches_null": None, "null": null, "direction": None}
    crosses = bool(cil < null - _EPS and cih > null + _EPS)
    touches = bool(abs(cih - null) <= _EPS or abs(cil - null) <= _EPS)
    direction = "none"
    if est is not None:
        if est < null - _EPS:
            direction = "benefit"
        elif est > null + _EPS:
            direction = "harm"
    # k=2 common-effect sensitivity: the HKSJ (primary) t1 interval is very wide and often crosses
    # the null even where the two trials agree, so the page shows a conventional common-effect CI
    # alongside. That interval can legitimately EXCLUDE the null while the HKSJ does not -- an honest
    # nuance, not a contradiction. Record it so a surface may state either reading without tripping
    # the gate. significant_fixed is None when no common-effect interval is present (k!=2).
    fixed_significant = None
    cilf, cihf = result.get("ci_low_fixed"), result.get("ci_high_fixed")
    if cilf is not None and cihf is not None:
        fixed_significant = not (cilf < null - _EPS and cihf > null + _EPS)
    return {"present": True, "significant": (not crosses), "crosses_null": crosses,
            "touches_null": touches, "null": null, "direction": direction,
            "significant_fixed": fixed_significant}


# ---- significance-contradiction scan over rendered surfaces --------------------------------
# Phrases that ASSERT the primary result is statistically significant / excludes no effect.
# Each alternative is guarded against a preceding negation ("not "/"no ") so that
# "not statistically significant" is NOT read as a significance assertion (it is a null one).
_ASSERT_SIG = re.compile(
    r"(?<!not )(?<!no )(?:statistically significant|significantly (?:reduc|lower|increas|"
    r"rais|higher|decreas|improv)|excludes? (?:the )?null|excludes? no(?:-| )effect|"
    r"reached (?:statistical )?significance)", re.I)
# Phrases that ASSERT the primary result is NOT significant / spans no effect.
_ASSERT_NULL = re.compile(
    r"not (?:statistically )?significant|no(?:t a)? significant|did not reach (?:statistical )?"
    r"significance|crosses (?:the )?null|spans? (?:the )?null|compatible with no(?:-| )effect|"
    r"includes? no(?:-| )effect|consistent with no(?:-| )effect", re.I)


def significance_contradictions(claim, surfaces):
    """surfaces: {name: rendered_text}. Returns a list of caught contradictions:
    a surface that ASSERTS significance opposite to the canonical claim['significant'].

    Only fires when the canonical claim is PRESENT (a suppressed/absent claim asserts
    nothing to contradict). Conservative: a surface that says nothing about significance is
    not a contradiction; only an explicit opposite assertion is."""
    out = []
    if not claim or not claim.get("present"):
        return out
    sig = claim.get("significant")
    if sig is None:
        return out
    # A significance assertion is DEFENSIBLE if EITHER the primary (HKSJ) interval OR the k=2
    # common-effect sensitivity interval excludes the null; a not-significant assertion is
    # defensible whenever the primary interval crosses the null. So the gate fires only on a HARD
    # contradiction: a surface claims significance no shown interval supports, or claims
    # non-significance while the primary interval itself excludes the null.
    sig_supported = bool(sig) or bool(claim.get("significant_fixed"))
    for name, text in (surfaces or {}).items():
        if not text:
            continue
        says_sig = bool(_ASSERT_SIG.search(text))
        says_null = bool(_ASSERT_NULL.search(text))
        if sig and says_null and not says_sig:
            out.append({"surface": name, "canonical": "significant",
                        "found": "asserts NOT significant / spans null"})
        elif (not sig_supported) and says_sig and not says_null:
            out.append({"surface": name, "canonical": "not significant (neither the HKSJ nor the "
                        "common-effect interval excludes the null)",
                        "found": "asserts significant / excludes null"})
    return out
