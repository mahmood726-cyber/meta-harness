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


# ---------------------------------------------------------------------------------------------------------------------------
# (3) A PUBLISHED HR STAYS AN HR (CAP-corticosteroids review, 2026-09-26). SONIA (NEJM 2025, PMID 41159889) reports a site-
# stratified Cox HR 0.84 (0.73-0.97) with 98 (4.5%) missing day-30 vital status. Dividing deaths by randomised would produce an
# "RR" the trial never estimated, over denominators that are not ascertained. A published HR on an RR outcome is never
# re-expressed from counts: it routes to a separately specified TIME-TO-EVENT analysis, or waits until source-supported 30-day
# risks with ASCERTAINED denominators exist (a typed `ascertained_denominators` record with its span; never inferred).
def _input_measure(t: dict[str, Any]) -> str | None:
    if t.get("effect") is not None and t.get("scale"):
        return str(t["scale"]).upper()
    if t.get("e1i") is not None:
        return "IRR"
    if t.get("mean1") is not None:
        return "MD"
    return "RR" if t.get("ai") is not None else None


def hr_route(row: dict[str, Any], outcome_estimand: str | None, pool: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    """Only when the pool IS a risk pool: the declared estimand does not name HR, AND another admitted input of the same pool is a
    non-HR ratio. A pool of HRs alone is already a time-to-event analysis (omega3, statins); moving its HRs out would empty a
    coherent pool for nothing. `pool` None = judge the row alone (a trial not yet in any pool, e.g. SONIA)."""
    if str(row.get("scale") or "").upper() != "HR" or row.get("effect") is None:
        return None
    if "HR" in str(outcome_estimand or "").upper().replace("/", " ").split():
        return None
    if pool is not None and not any(_input_measure(t) in ("RR", "OR") for t in pool if t is not row):
        return None
    asc = row.get("ascertained_denominators")
    if isinstance(asc, dict) and asc.get("span") and asc.get("n1") and asc.get("n2"):
        return {"route": "RISK_FROM_ASCERTAINED_DENOMINATORS", "hr_retained": {k: row.get(k) for k in ("effect", "ci_low", "ci_high")},
                "ascertained_denominators": asc}
    return {"route": "TIME_TO_EVENT_SEPARATE", "hr_retained": {k: row.get(k) for k in ("effect", "ci_low", "ci_high")},
            "reason": (f"a published hazard ratio on an {outcome_estimand} outcome: never converted to a risk ratio by dividing events "
                       "by randomised (the trial did not estimate it, and outcome ascertainment is not shown complete). It enters a "
                       "separately specified time-to-event analysis, or waits for source-supported risks with ascertained denominators")}


# (4) RECONSTRUCTION ROUTE for an incompatible published OR whose arm counts are held (STEP hyperglycaemia needing insulin:
# 76 [19%] vs 43 [11%], OR 1.96 (1.31-2.93), arms n=392 / n=393 -> RR 1.772 (1.253-2.507)). Counts come from the effect's OWN
# sentence, denominators from the held abstract's randomisation sentence, arms matched by the topic's terms, and every count is
# corroborated against its own stated percentage; any failure refuses the reconstruction (the row stays as published).
_PAIR = __import__("re").compile(r"\(\s*(\d{1,6})\s*\[\s*(\d{1,3}(?:\.\d+)?)\s*%\s*\]\s*vs\.?\s*(\d{1,6})\s*\[\s*(\d{1,3}(?:\.\d+)?)\s*%\s*\]")
_ARM_N = r"(?:the\s+)?{term}\s+group\s*\(\s*n\s*=\s*(\d{{1,6}})\s*\)"


# "2104 patients were assigned to receive dexamethasone and 4321 to receive usual care" (RECOVERY)
_ARM_N_ASSIGNED = r"(\d[\d,]*)\s+(?:patients\s+)?(?:were\s+)?(?:(?:randomly\s+)?assigned|randomi[sz]ed)?\s*to\s+(?:receive\s+)?{term}\b"
# "482 patients (22.9%) in the dexamethasone group and 1110 patients (25.7%) in the usual care group" (RECOVERY)
_NAMED_PAIR = __import__("re").compile(
    r"(\d[\d,]*)\s+(?:patients?|participants?)?\s*\((\d{1,3}(?:\.\d+)?)\s*%\)\s+in\s+the\s+([\w\s-]{1,40}?)\s+group\s+and\s+"
    r"(\d[\d,]*)\s+(?:patients?|participants?)?\s*\((\d{1,3}(?:\.\d+)?)\s*%\)\s+in\s+the\s+([\w\s-]{1,40}?)\s+group", __import__("re").I)


def _arm_n(abstract: str, terms: list[str]) -> int | None:
    import re as _re
    hits = set()
    for term in terms:
        for pat in (_ARM_N, _ARM_N_ASSIGNED):
            for m in _re.finditer(pat.format(term=_re.escape(term)), abstract or "", _re.I):
                hits.add(int(m.group(1).replace(",", "")))
    return hits.pop() if len(hits) == 1 else None


def reconstruct_from_counts(row: dict[str, Any], abstract: str | None, interv: list[str], comp: list[str],
                            measure: str = "RR") -> dict[str, Any] | None:
    """Rebuild the TARGET measure (RR or OR) from held arm counts. Two sentence shapes: '(n [p%] vs n [p%])' after a named arm
    (STEP), and 'n (p%) in the <arm> group and n (p%) in the <arm> group' (RECOVERY). Every count must reproduce its own stated
    percentage; any failure returns a typed reason and the row stays as published."""
    import re as _re
    src = (row.get("source") or "").replace("·", ".")
    side = lambda text: (("I" if interv and _re.search("|".join(_re.escape(t) for t in interv), text, _re.I) else "")
                         + ("C" if comp and _re.search("|".join(_re.escape(t) for t in comp), text, _re.I) else ""))
    nm = _NAMED_PAIR.search(src)
    if nm:
        s1, s2 = side(nm.group(3)), side(nm.group(6))
        if {s1, s2} != {"I", "C"}:
            return {"state": "NOT_RECONSTRUCTED", "why": f"the named groups ({nm.group(3)!r}, {nm.group(6)!r}) are not one intervention and "
                    "one comparator arm in this topic's vocabulary"}
        a, pa, c, pc = int(nm.group(1).replace(",", "")), nm.group(2), int(nm.group(4).replace(",", "")), nm.group(5)
        first_is_interv, first_is_comp = s1 == "I", s1 == "C"
    else:
        m = _PAIR.search(src)
        if not m:
            return {"state": "NOT_RECONSTRUCTED", "why": "the effect's own sentence gives no arm counts with percentages"}
        a, pa, c, pc = int(m.group(1)), m.group(2), int(m.group(3)), m.group(4)   # percentages kept AS WRITTEN: their precision is the source's
        first_is_interv = bool(_re.search("|".join(_re.escape(t) for t in interv), src[:m.start()], _re.I)) if interv else False
        first_is_comp = bool(_re.search("|".join(_re.escape(t) for t in comp), src[:m.start()], _re.I)) if comp else False
    if first_is_interv == first_is_comp:
        return {"state": "NOT_RECONSTRUCTED", "why": ("the sentence names " + ("both arms" if first_is_interv else "no arm this topic's vocabulary knows")
                + " before the counts, so which count is which arm is not stated -- check the topic's intervention/comparator terms")}
    n_i, n_c = _arm_n(abstract or "", interv), _arm_n(abstract or "", comp)
    if not n_i or not n_c:
        return {"state": "NOT_RECONSTRUCTED", "why": "no single '<arm> group (n=N)' denominator for each arm in the held abstract"}
    ai, ci = (a, c) if first_is_interv else (c, a)
    p_i, p_c = (pa, pc) if first_is_interv else (pc, pa)
    dec = lambda p: len(p.split(".")[1]) if "." in p else 0
    if round(100 * ai / n_i, dec(p_i)) != float(p_i) or round(100 * ci / n_c, dec(p_c)) != float(p_c):
        return {"state": "NOT_RECONSTRUCTED", "why": f"a count does not reproduce its own stated percentage ({ai}/{n_i} vs {p_i}%, {ci}/{n_c} vs {p_c}%)"}
    rr = counts_tuple(ai, n_i, ci, n_c, measure)
    if rr is None:
        return {"state": "NOT_RECONSTRUCTED", "why": "a zero cell"}
    return {"state": "RECONSTRUCTED", "derivation": "RECONSTRUCTED_FROM_COUNTS", "measure": measure, "ai": ai, "n1i": n_i, "ci": ci, "n2i": n_c,
            ("rr" if measure == "RR" else "or"): {k: round(v, 4) for k, v in rr.items()},
            "published_effect_retained": {k: row.get(k) for k in ("effect", "ci_low", "ci_high", "scale")},
            "corroboration": f"{ai}/{n_i} = {p_i}% and {ci}/{n_c} = {p_c}% as stated; denominators from the held randomisation sentence"}


# (5) ENDPOINT-DEFINITION COMPATIBILITY IS ADJUDICATED, NOT ASSUMED: once measures agree, rows whose own quotations define the
# endpoint differently (insulin-requiring vs laboratory-defined hyperglycaemia) do not pool until an adjudication record says so.
_INSULIN = __import__("re").compile(r"(?i)(?:needing|requiring|required|treated\s+with)\s+insulin|insulin[- ](?:requiring|treated|dependent)")


def definition_class(row: dict[str, Any]) -> str:
    return "INSULIN_REQUIRING" if _INSULIN.search(row.get("source") or "") else "DEFINITION_NOT_STATED_IN_QUOTATION"


# ---------------------------------------------------------------------------------------------------------------------------
# (6) OUTCOME POLARITY (COVID-corticosteroids review): REMAP-CAP reports adjusted ORs oriented so that >1 = BENEFIT ("the odds of
# improvement"). The ordered contrast must carry WHICH EVENT is modelled; a benefit-event effect entering a death / mortality pool
# is inverted in meaning. It is refused (EVENT_POLARITY_MISMATCH) unless the outcome DECLARES the normalisation
# (spec.polarity_normalisation.reciprocal_for_benefit_event: true), in which case the reciprocal is applied and recorded.
_BENEFIT_EVENT = __import__("re").compile(
    r"(?i)odds\s+of\s+(?:improvement|a\s+better\s+outcome|better\s+outcomes?|survival|being\s+alive|recovery)|"
    r"(?:probabilit(?:y|ies)\s+of\s+)?superiority\s+with\s+regard\s+to\s+the\s+odds\s+of\s+improvement|"
    r"odds\s+ratio\s+greater\s+than\s+1\s*\(?\s*(?:threshold\s+for\s+)?(?:trial\s+conclusion\s+of\s+)?superiority")
_DEATH_EVENT = __import__("re").compile(r"(?i)\b(?:died|deaths?|mortality|dead)\b")
_DEATH_OUTCOME = __import__("re").compile(r"(?i)\b(?:mortality|death|died|survival)\b")


def event_modelled(text: str | None) -> str:
    t = text or ""
    if _BENEFIT_EVENT.search(t):
        return "BENEFIT_EVENT"          # >1 favours the intervention
    if _DEATH_EVENT.search(t):
        return "DEATH"                  # <1 favours the intervention
    return "NOT_STATED"


def polarity_check(row: dict[str, Any], outcome_name: str | None, spec: dict[str, Any] | None) -> dict[str, Any] | None:
    """None when the outcome is not a death outcome or the row states death. A benefit-event effect in a death pool is refused,
    or -- only under a declared normalisation -- re-oriented by the reciprocal (CI ends swapped) with the original kept."""
    if row.get("effect") is None or not _DEATH_OUTCOME.search(outcome_name or ""):
        return None
    ev = event_modelled(row.get("source"))
    if ev != "BENEFIT_EVENT":
        return {"event_modelled": ev, "state": "CONSISTENT" if ev == "DEATH" else "NOT_STATED"}
    decl = ((spec or {}).get("polarity_normalisation") or {}).get("reciprocal_for_benefit_event") is True
    if not decl:
        return {"event_modelled": ev, "state": "EVENT_POLARITY_MISMATCH", "resolution": "HOLD",
                "reason": ("the effect models a BENEFIT event (>1 favours the intervention) and this is a death outcome; pooled as it "
                           "stands its direction is inverted. Refused: no declared polarity normalisation")}
    e, lo, hi = float(row["effect"]), float(row["ci_low"]), float(row["ci_high"])
    return {"event_modelled": ev, "state": "NORMALISED", "resolution": "RECIPROCAL_DECLARED",
            "original": {"effect": e, "ci_low": lo, "ci_high": hi},
            "normalised": {"effect": round(1 / e, 4), "ci_low": round(1 / hi, 4), "ci_high": round(1 / lo, 4)}}


# (7) MULTI-ARM SHARED CONTROL (COVID-corticosteroids review): REMAP-CAP's two hydrocortisone strategies (41/137 fixed, 37/141
# shock-dependent) share ONE control (33/99). Entered as two independent comparisons the control is counted twice. A DECLARED rule
# (spec.multi_arm_rule) resolves it before pooling: COMBINE_ARMS (one comparison, experimental arms summed) or SPLIT_CONTROL (the
# control's events and patients divided equally among the comparisons, Cochrane Handbook 23.3.4). Undeclared -> the group is HELD.
def _family(t: dict[str, Any]) -> str:
    return str(t.get("trial_family_id") or t.get("trial_id") or t.get("id") or "").split("#")[0]


def multi_arm_groups(trials: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    by: dict[tuple, list] = {}
    for t in trials:
        if t.get("ai") is None or t.get("ci") is None:
            continue
        by.setdefault((_family(t), t.get("ci"), t.get("n2i")), []).append(t)
    return [g for g in by.values() if len(g) >= 2]


def apply_multi_arm_rule(trials: list[dict[str, Any]], spec: dict[str, Any] | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Returns (trials to pool, held records). Rows outside any shared-control group pass through unchanged."""
    rule = str((spec or {}).get("multi_arm_rule") or "").upper()
    groups = multi_arm_groups(trials)
    if not groups:
        return trials, []
    grouped = {id(t) for g in groups for t in g}
    out = [t for t in trials if id(t) not in grouped]
    held = []
    for g in groups:
        k = len(g)
        shared = {"ci": g[0]["ci"], "n2i": g[0]["n2i"]}
        record = {"rule": rule or None, "arms": [{"id": t.get("id"), "label": t.get("label"), "ai": t["ai"], "n1i": t["n1i"]} for t in g],
                  "shared_control": shared}
        if rule == "COMBINE_ARMS":
            row = dict(g[0])
            row.update(ai=sum(t["ai"] for t in g), n1i=sum(t["n1i"] for t in g), multi_arm=dict(record, applied="COMBINE_ARMS"))
            out.append(row)
        elif rule == "SPLIT_CONTROL":
            for t in g:
                r = dict(t)
                r.update(ci=shared["ci"] / k, n2i=shared["n2i"] / k, multi_arm=dict(record, applied="SPLIT_CONTROL", split_into=k))
                out.append(r)
        else:
            held.append({"label": g[0].get("label"), "id": g[0].get("id"), "absent_kind": "machine_absent",
                         "state": "MULTI_ARM_SHARED_CONTROL_UNDECLARED", "reason_code": "MULTI_ARM_SHARED_CONTROL_UNDECLARED",
                         "endpoint_admissibility": "MULTI_ARM_SHARED_CONTROL_UNDECLARED", "multi_arm": record,
                         "reason": (f"{k} comparisons share one control ({shared['ci']}/{shared['n2i']}); entered independently the "
                                    "control would be counted {k} times. Held until the outcome declares multi_arm_rule "
                                    "(COMBINE_ARMS or SPLIT_CONTROL)").replace("{k}", str(k))})
    return out, held


# (9) COUNTS UNDER AN HR TARGET (dapagliflozin HFpEF review): PRESERVED-HF reports HF events descriptively (HF hospitalisation or
# urgent HF visit 9/162 vs 9/162, 12-week treatment). A count-RR (1.000, 0.407-2.454) is NOT a hazard ratio: it is never labelled
# one and never mixed into an HR primary. State: clinical-event counts recovered; protocol-compatible HR not established. The
# count-RR may enter only an EXPLICITLY DEFINED secondary analysis (spec.secondary_count_analysis with its definition).
COUNTS_HR_NOT_ESTABLISHED = "CLINICAL_EVENT_COUNTS_RECOVERED_HR_NOT_ESTABLISHED"


def count_only_under_hr(row: dict[str, Any], target: str | None, spec: dict[str, Any] | None) -> dict[str, Any] | None:
    if "HR" not in str(target or "").upper().replace("/", " ").split():
        return None
    if row.get("effect") is not None or row.get("ai") is None:
        return None
    rr = counts_tuple(row.get("ai"), row.get("n1i"), row.get("ci"), row.get("n2i"), "RR")
    sec = (spec or {}).get("secondary_count_analysis")
    defined = isinstance(sec, dict) and bool(sec.get("definition"))
    return {"state": COUNTS_HR_NOT_ESTABLISHED, "counts": [row.get(k) for k in ("ai", "n1i", "ci", "n2i")],
            "count_rr": rr and {k: round(v, 4) for k, v in rr.items()}, "is_hazard_ratio": False,
            "allowed_in": "SECONDARY_COUNT_ANALYSIS" if defined else None,
            "reason": ("clinical-event counts recovered; a protocol-compatible HR is not established. The count-based RR is not a "
                       "hazard ratio and does not enter the HR primary"
                       + ("; it enters the explicitly defined secondary count analysis" if defined else
                          "; no secondary count analysis is defined for this outcome, so it is reported, not pooled"))}



# ---------------------------------------------------------------------------------------------------------------------------
# (10) PREFER THE PUBLISHED MODEL (denosumab review): FREEDOM's vertebral RR 0.32 (0.26-0.41) is age-stratified Mantel-Haenszel and
# its nonvertebral / hip HRs are age-adjusted Cox. A published model estimate is KEPT with its model recorded; a same-measure crude
# count reconstruction (RR 0.32479, 0.25573-0.41249) is CORROBORATION ONLY, never a replacement. The model is read from held text,
# or from a typed record (`published_model` with its span); otherwise it is stated as not established -- never asserted.
_MODEL = (
    ("MANTEL_HAENSZEL", r"mantel[- ]haenszel"),
    ("STRATIFIED", r"\bstratified\b"),
    ("COX", r"\bcox\b|proportional[- ]hazards?"),
    ("LOGISTIC", r"logistic\s+regression"),
    ("POISSON", r"poisson"),
    ("ADJUSTED", r"(?<![-\w])adjusted\s+(?:hazard|relative|risk|odds|rate)|(?<![-\w])adjust(?:ed|ing)?\s+for\b|\bmultivariab?le\b"
                 r"|\bmultivariate\b|\b(?:age|sex|risk|baseline|fully|covariate)[- ]adjusted\b"),
)


def published_model(row: dict[str, Any], abstract: str | None = None) -> dict[str, Any]:
    import re as _re
    typed = row.get("published_model")
    if isinstance(typed, dict) and typed.get("model") and typed.get("span") and typed.get("basis") == "typed record":
        return typed
    if isinstance(typed, dict) and typed.get("model") and typed.get("span") and not typed.get("basis"):
        return {"model": typed["model"], "basis": "typed record", "span": typed["span"]}
    for text, where in ((row.get("source") or "", "row quotation"), (abstract or "", "held abstract")):
        found = [name for name, rx in _MODEL if _re.search(rx, text, _re.I)]
        if found:
            return {"model": "+".join(found), "basis": where}
    return {"model": "NOT_STATED_IN_HELD_TEXT", "basis": "neither the quotation nor the held abstract states the estimation model"}


def model_documented(row: dict[str, Any], abstract: str | None = None) -> bool:
    """A documented estimation model (stratified / Mantel-Haenszel / Cox / adjusted) explains why a crude count ratio differs: the
    published estimate is kept and the difference disclosed -- never held for it, never replaced by the crude ratio."""
    return adjusted_documented(row) or published_model(row, abstract)["model"] != "NOT_STATED_IN_HELD_TEXT"


def crude_corroboration(row: dict[str, Any]) -> dict[str, Any] | None:
    """Same-measure crude counts beside a published estimate: recorded as CORROBORATION ONLY."""
    counts = _counts_of(row)
    scale = str(row.get("scale") or "").upper()
    if counts is None or row.get("effect") is None or scale not in RATIO:
        return None
    t = counts_tuple(*counts, scale)
    return t and {"role": "CORROBORATION_ONLY", "counts": list(counts), "crude": {k: round(v, 5) for k, v in t.items()},
                  "note": "a crude count ratio never replaces the published model estimate"}
