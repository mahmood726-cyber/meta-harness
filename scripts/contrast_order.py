"""Ordered contrast: WHICH arm is the numerator of a ratio is a VALUE, recomputed from the tuple's own clause (lane OC, 2026-09-25).

The external audit's finding: "vs placebo (named in the result clause)" was emitted whenever 'placebo' appeared, with no ordering,
and the estimand check compared only the STATE of comparator_direction and estimator, never the value. 0.87 read as
placebo/liraglutide is a different clinical claim with every digit still present in the source.

Lives in scripts/ (not harness/): every harness/*.py is enumerated by the release certificates' scope, so a new harness module
is a certificate change. This is the PRODUCER's implementation (scripts/build_bundle.py emits its result into analysis_identity.comparator_direction.
ordered_contrast). scripts/verify_bundle.py carries its own standard-library copy of the same rules and imports nothing from
here -- the verifier recomputes and compares; agreement of the two on the served rows is a test (tests/test_ordered_contrast.py),
and a third, blind reading of every clause's orientation is recorded under evidence/ordered_contrast/.

Arm identities are F4's: "<NCT>:<AACT design_group id>", read from the certified cache/<slug>/families.json arms.
"""
from __future__ import annotations

import math
import re

RATIO_MEASURES = ("HR", "OR", "RR", "IRR")
_CLAUSE_MEASURE = (("HR", r"hazard ratio|(?-i:\bHR\b)"), ("OR", r"odds ratio|(?-i:\bOR\b)"),
                   ("RR", r"relative risk|risk ratio|(?-i:\bRR\b)"), ("IRR", r"(?:incidence[- ])?rate ratio|(?-i:\bIRR\b)"))
_ESTIMATOR_MEASURE = {"hazard ratio": "HR", "odds ratio": "OR", "risk ratio": "RR", "rate ratio": "IRR"}
_SCALE_ALIASES = {"HR": "HR", "OR": "OR", "RR": "RR", "IRR": "IRR", "RATE RATIO": "IRR", "RISK RATIO": "RR", "HAZARD RATIO": "HR", "ODDS RATIO": "OR"}
# the object of a comparison is the REFERENCE arm: "... than in the placebo group", "compared with placebo", "A versus B"
_REFERENCE_MARK = re.compile(r"\b(?:as\s+)?(?:compared\s+(?:with|to)|versus|vs\.?|relative\s+to|than|(?:non-?)?inferior\s+to|superior\s+to)\s+"
                             r"(?:(?:in|on|with|among|receiving|assigned\s+to(?:\s+receive)?|those|patients|participants|the)\s+){0,4}$", re.I)
# ... and a ratio 'for' an arm names that arm as the NUMERATOR: "hazard ratio for liraglutide, 0.87", "the hazard ratio for placebo versus ..."
_NUMERATOR_MARK = re.compile(r"\b(?:hazard|odds|risk|rate)\s+ratios?\s*(?:\([A-Z]{2,3}\)\s*|\[[A-Z]{2,3}\]\s*)?,?\s*(?:for|with|of)\s+"
                             r"(?:(?:the|patients|participants|those|in|receiving|assigned\s+to(?:\s+receive)?)\s+){0,4}$", re.I)
_PCT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent\b|per\s+cent\b)", re.I)   # RALES writes "(46 percent)"
_NOT_AN_ARM = re.compile(r"^-(?:controlled|matched|treated|based|like)", re.I)
# ... except the second half of a suspended hyphen: "ticagrelor- and clopidogrel-treated patients" names BOTH arms
_SUSPENDED_HYPHEN = re.compile(r"[\w)]-\s+(?:and|or|vs\.?|versus)\s+$", re.I)
_GENERIC_REFERENCE = ("control",)          # names an arm only as '<control> group|arm'; 'glycaemic control' is not an arm


def scale_measure(scale):
    """The measure a served label names (HR / OR / RR / IRR), None when unidentified. No class mapping: OR is not RR."""
    return _SCALE_ALIASES.get(str(scale or "").strip().upper())


def clause_measure(clause):
    """The ratio measure the tuple's OWN clause names: STATED (exactly one), UNRESOLVED (two differ), UNSTATED (none)."""
    found = {}
    for m, rx in _CLAUSE_MEASURE:
        hit = re.search(rx, clause or "", re.I)
        if hit:
            found[m] = hit.group(0)
    if len(found) == 1:
        (m, word), = found.items()
        return {"state": "STATED", "measure": m, "matched": word}
    return {"state": "UNRESOLVED" if found else "UNSTATED", "measure": None, "matched": sorted(found.values())}


def contrast_vocabulary(topic):
    """Arm vocabulary from the SERVED topic registration (digest-checked artefact): experimental = the intervention agents, their
    aliases and the class terms; reference = the comparator terms. Longest first so 'oral semaglutide' never loses to a fragment."""
    exp = set(topic.get("intervention_class_terms") or []) | set(topic.get("intervention_terms") or [])
    for k, v in (topic.get("intervention_agents") or {}).items():
        exp.add(k)
        exp.update(v or [])
    ref = set(topic.get("comparator_terms") or [])
    key = lambda s: (-len(s), s)
    return {"experimental": sorted({t.strip().lower() for t in exp if t and t.strip()}, key=key),
            "reference": sorted({t.strip().lower() for t in ref if t and t.strip()}, key=key)}


def side_of(text, vocab):
    """EXPERIMENTAL / REFERENCE / None for a free-text arm name. A name carrying a reference term is the reference ('placebo for X')."""
    low = (text or "").lower()
    if any(re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", low) for t in vocab.get("reference", [])):
        return "REFERENCE"
    if any(re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", low) for t in vocab.get("experimental", [])):
        return "EXPERIMENTAL"
    return None


def arm_mentions(clause, vocab):
    """Every non-overlapping arm mention in the clause, in order: (start, end, side, term)."""
    cands = []
    for side, terms in (("EXPERIMENTAL", vocab.get("experimental", [])), ("REFERENCE", vocab.get("reference", []))):
        for t in terms:
            for m in re.finditer(r"(?<![\w])" + re.escape(t) + r"(?![\w])", clause or "", re.I):
                if _NOT_AN_ARM.match((clause or "")[m.end():]) and not (
                        (clause or "")[m.end():].lower().startswith("-treated") and _SUSPENDED_HYPHEN.search((clause or "")[:m.start()])):
                    continue
                if t in _GENERIC_REFERENCE and not re.match(r"\s+(?:group|arm)\b", (clause or "")[m.end():], re.I):
                    continue
                cands.append((m.start(), m.end(), side, t))
    cands.sort(key=lambda c: (c[0], -(c[1] - c[0])))
    out, last = [], -1
    for c in cands:
        if c[0] >= last:
            out.append(c)
            last = c[1]
    return out


def family_arm_ids(fam, vocab):
    """F4 / families.json arm identities (<NCT>:<AACT design_group id>) by side, from the certified family's arm labels."""
    by = {"EXPERIMENTAL": [], "REFERENCE": []}
    for a in (fam or {}).get("arms") or []:
        s = side_of(((a.get("label") or {}).get("value")) or "", vocab)
        if s:
            by[s].append(a.get("arm_id"))
    return by


def rate_witness(clause, ms, num_side, estimate):
    """Second, NUMERIC witness of orientation: the two per-arm percentages stated before the tuple ('608 of 4668 [13.0%] ... 694 of 4672
    [14.9%]'), paired to their arms by position (all percentages precede their arm, or all follow it), must put the numerator arm on the
    same side of 1 as the estimate. Informative only when both the crude ratio and the estimate are at least 5% from 1 (an HR and a crude
    proportion ratio can straddle 1 near the null). CONTRADICTS makes the contrast UNORDERED: two witnesses that disagree order nothing."""
    tuple_at = min([m.start() for _, rx in _CLAUSE_MEASURE for m in [re.search(rx, clause, re.I)] if m] or [len(clause)])
    arms = []
    for m in ms:
        if m[0] < tuple_at and m[2] not in {a[2] for a in arms}:
            arms.append(m)
    pcts = [(m.start(), float(m.group(1))) for m in _PCT.finditer(clause[:tuple_at])]
    out = {"state": "NOT_INFORMATIVE"}
    if len(arms) != 2 or len(pcts) != 2 or estimate is None:
        return dict(out, reason=f"{len(arms)} arm(s) and {len(pcts)} percentage(s) before the tuple; estimate {'given' if estimate is not None else 'absent'}")
    (a1, a2), (p1, p2) = arms, pcts
    if not (p1[0] < a1[0] < p2[0] < a2[0] or a1[0] < p1[0] < a2[0] < p2[0]):
        return dict(out, reason="percentages and arms are not interleaved one-to-one")
    rate = {a1[2]: p1[1], a2[2]: p2[1]}
    ref_side = "REFERENCE" if num_side == "EXPERIMENTAL" else "EXPERIMENTAL"
    if not rate[ref_side] or not rate[num_side] or float(estimate) <= 0:
        return dict(out, reason="a zero rate or a non-positive estimate")
    crude = rate[num_side] / rate[ref_side]
    out.update(rates={"numerator": rate[num_side], "reference": rate[ref_side]}, crude_ratio=round(crude, 6), estimate=estimate)
    if abs(math.log(crude)) < math.log(1.05) or abs(math.log(float(estimate))) < math.log(1.05):
        return dict(out, reason="the crude ratio or the estimate is within 5% of 1")
    return dict(out, state="AGREES" if (crude < 1) == (float(estimate) < 1) else "CONTRADICTS")


def ordered_contrast(clause, values, vocab, fam=None):
    """Recompute the ordered contrast from the tuple's own clause.
    Rule 0 (NUMERATOR_NAMED): 'hazard ratio for X' names X as the numerator.
    Rule 1 (COMPARATIVE_CONNECTIVE): an arm introduced by 'than (in the)', 'compared with', 'versus', 'relative to',
      '(non)inferior/superior to' is the REFERENCE (the denominator).
    Rule 2 (ORDER_OF_MENTION): with neither, the first-named arm is the numerator ('X in the A group and Y in the B group (HR ...)'
      reports A/B) -- the reporting convention, recorded as a weaker witness.
    Conflicting marks (both arms named numerator, both marked reference, or one arm marked both ways) -> UNORDERED.
    Then the NUMERIC witness (rate_witness): per-arm percentages that contradict the ordering -> UNORDERED (fail closed)."""
    out = {"measure": clause_measure(clause), "experimental_arm": None, "reference_arm": None, "numerator_side": None,
           "estimate": values[0] if values else None, "ci_low": values[1] if values else None, "ci_high": values[2] if values else None,
           "direction_witness": None, "rate_witness": None, "state": "UNORDERED"}
    if not clause:
        out["reason"] = "no result clause holds the effect tuple"
        return out
    ms = arm_mentions(clause, vocab)
    sides = {m[2] for m in ms}
    ref_marked = {m[2]: m for m in ms if _REFERENCE_MARK.search(clause[:m[0]])}
    num_marked = {m[2]: m for m in ms if _NUMERATOR_MARK.search(clause[:m[0]])}
    first = {}
    for m in ms:
        first.setdefault(m[2], m)
    if len(ref_marked) == 2 or len(num_marked) == 2 or set(ref_marked) & set(num_marked):
        out["reason"] = "conflicting marks: " + "; ".join(clause[max(0, m[0] - 30):m[1]] for m in list(ref_marked.values()) + list(num_marked.values()))
        return out
    if num_marked:
        num_side = next(iter(num_marked))
        nm = num_marked[num_side]
        lead = _NUMERATOR_MARK.search(clause[:nm[0]])
        out["direction_witness"] = {"rule": "NUMERATOR_NAMED", "text": clause[lead.start():nm[1]], "clause_start": lead.start(), "clause_end": nm[1]}
    elif ref_marked:
        ref_side = next(iter(ref_marked))
        num_side = "EXPERIMENTAL" if ref_side == "REFERENCE" else "REFERENCE"
        rm = ref_marked[ref_side]
        lead = _REFERENCE_MARK.search(clause[:rm[0]])
        out["direction_witness"] = {"rule": "COMPARATIVE_CONNECTIVE", "text": clause[lead.start():rm[1]], "clause_start": lead.start(), "clause_end": rm[1]}
    elif sides == {"EXPERIMENTAL", "REFERENCE"}:
        a, b = sorted((first["EXPERIMENTAL"], first["REFERENCE"]))
        num_side = a[2]
        out["direction_witness"] = {"rule": "ORDER_OF_MENTION", "text": clause[a[0]:b[1]], "clause_start": a[0], "clause_end": b[1],
                                    "note": "no comparative connective; the first-named arm is the numerator by the reporting convention"}
    else:
        out["reason"] = f"the clause names {sorted(sides) or 'no arm'} and no comparative connective orders them"
        return out
    rw = rate_witness(clause, ms, num_side, out["estimate"])
    out["rate_witness"] = rw
    if rw["state"] == "CONTRADICTS":
        out["reason"] = (f"{out['direction_witness']['rule']} puts the {num_side} arm in the numerator, but the stated rates "
                         f"({rw['rates']['numerator']}% vs {rw['rates']['reference']}%, crude {rw['crude_ratio']}) and the estimate {rw['estimate']} disagree")
        out["direction_witness"] = None
        return out
    ids = family_arm_ids(fam, vocab)
    for s, key in (("EXPERIMENTAL", "experimental_arm"), ("REFERENCE", "reference_arm")):
        m = first.get(s)
        out[key] = {"side": s, "term": m[3] if m else None, "named_in_clause": bool(m), "arm_ids": ids[s],
                    "arm_id_basis": "certified families.json arm labels matched to the topic vocabulary" if ids[s] else "no certified arm label matches"}
    out["numerator_side"] = num_side
    out["state"] = "ORDERED"
    return out


def served_orientation(cd, vocab):
    """The numerator side a SERVED comparator_direction VALUE declares: 'A vs B', or a legacy 'vs B' that names only the reference
    (the numerator is then the other side). A typed ordered_contrast beside it is checked separately, never preferred to the value."""
    v = re.sub(r"\s*\(.*$", "", str((cd or {}).get("value") or "")).strip()
    m = re.match(r"^(?:(?P<a>.+?)\s+)?(?:vs\.?|versus)\s+(?P<b>.+)$", v, re.I)
    if not m:
        return None
    sa, sb = (side_of(m.group("a"), vocab) if m.group("a") else None), side_of(m.group("b"), vocab)
    if sa and sb:
        return sa if sa != sb else None
    if sb:
        return "EXPERIMENTAL" if sb == "REFERENCE" else "REFERENCE"
    return None


def normalisation_policy(regd):
    """The registered policy for re-orienting a ratio. Absent -> FORBIDDEN (a reversal nobody permitted is refused)."""
    pol = (regd or {}).get("contrast_normalisation") or {}
    return str(pol.get("reciprocal_for_ratio_measures") or "FORBIDDEN").upper()


def _dec(x):
    s = str(x)
    return len(s.split(".")[1]) if "." in s else 0


def reciprocal_reproduces(src, dst):
    """dst == 1/src with the interval's endpoints swapped, to the precision BOTH sides were printed at (|d(1/x)| = |dx|/x^2)."""
    pairs = ((src["estimate"], dst["estimate"]), (src["ci_high"], dst["ci_low"]), (src["ci_low"], dst["ci_high"]))
    for s, d in pairs:
        if s is None or d is None or float(s) <= 0:
            return False
        tol = 0.5 * 10 ** -_dec(d) + 0.5 * 10 ** -_dec(s) / float(s) ** 2 + 1e-12
        if abs(1.0 / float(s) - float(d)) > tol:
            return False
    return True


def contrast_value(oc):
    """The served comparator_direction value for an ORDERED contrast: '<numerator arm> vs <reference arm>'."""
    if oc.get("state") != "ORDERED":
        return None
    e = (oc.get("experimental_arm") or {}).get("term") or "the experimental arm"
    r = (oc.get("reference_arm") or {}).get("term") or "the reference arm"
    return f"{e} vs {r}" if oc.get("numerator_side") == "EXPERIMENTAL" else f"{r} vs {e}"


def registered_departures(oc, scale, regd, vocab, normalisation=None):
    """P11's contrast and estimator departures, producer side: what enters the pool must be the registered orientation and measure.
    A declared RECIPROCAL (policy permitting) moves the pooled orientation; an undeclared reversal cannot."""
    out = []
    num = oc.get("numerator_side") if oc.get("state") == "ORDERED" else None
    if normalisation and str(normalisation.get("operation") or "").upper() == "RECIPROCAL" and normalisation_policy(regd).startswith("PERMITTED"):
        n2 = served_orientation({"value": normalisation.get("orientation")}, vocab)
        if n2 and n2 != num:
            num = n2
    reg_num = served_orientation({"value": (regd or {}).get("contrast")}, vocab)
    if (regd or {}).get("contrast") not in (None, "UNSTATED"):
        if num is None:
            out.append(("contrast", "UNORDERED: " + str(oc.get("reason"))))
        elif reg_num is None:
            out.append(("contrast", "the registered contrast names no arm this topic's vocabulary resolves"))
        elif num != reg_num:
            out.append(("contrast", f"the pooled orientation puts the {num} arm in the numerator; registered {regd.get('contrast')!r}"))
    reg_measure = next((m for w, m in _ESTIMATOR_MEASURE.items() if w in str((regd or {}).get("estimator") or "").lower()), None)
    cm = (oc.get("measure") or {})
    permitted = [scale_measure(x) for x in ((regd or {}).get("estimators_permitted") or ([reg_measure] if reg_measure else []))]
    if permitted and scale_measure(scale) not in permitted:
        out.append(("estimator", f"served scale {scale!r}; registered {regd.get('estimator')!r}, permitted {permitted}"))
    elif cm.get("state") == "STATED" and scale_measure(scale) != cm.get("measure"):
        out.append(("estimator", f"served scale {scale!r}; the tuple's clause states {cm.get('matched')!r}"))
    return out
