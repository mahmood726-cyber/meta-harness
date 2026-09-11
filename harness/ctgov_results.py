"""Structured arm-level extraction from ClinicalTrials.gov v2 resultsSection.

This is the AACT/registry-results adapter: for a trial with posted results, it reads the
outcome-measure tables (event counts + denominators per arm) directly, so a trial whose
abstract reports only a bare % or a composite no longer depends on prose parsing. Highest
in the extraction source hierarchy for count data (structured primary-source results).
"""
from __future__ import annotations


def _num(x):
    try:
        return float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None


def extract_ctgov(outcome_measures, outcome_kws, interv_terms, comp_terms):
    """Return dict {ai,n1i,ci,n2i,source} for the outcome measure matching our outcome, else None.

    Chooses the outcome measure whose TITLE contains one of our outcome keywords (so we do not
    read a trial's PRIMARY when its primary is a different endpoint than ours). Assigns the two
    arms to intervention/comparator by group title. Accepts only integer counts <= denominator.
    """
    if not outcome_measures:
        return None
    kws = [k.lower() for k in outcome_kws if len(k) > 3]
    comp_l = [c.lower() for c in comp_terms]
    interv_l = [i.lower() for i in interv_terms]

    def title_matches(t):
        # Substring match only. A looser content-word match was tried and REJECTED: it picked a
        # 15-event secondary OM over EMPEROR's 361-event composite primary. Do not loosen without
        # a guard against selecting the wrong outcome measure.
        tl = (t or "").lower()
        return any(k in tl for k in kws)

    # Prefer a title-keyword match; among those prefer type PRIMARY.
    cands = [om for om in outcome_measures if title_matches(om.get("title"))]
    cands.sort(key=lambda om: 0 if om.get("type") == "PRIMARY" else 1)
    for om in cands:
        # only participant-count style measures (skip means/medians/rates)
        ptype = (om.get("paramType") or "").upper()
        if ptype and ptype not in ("COUNT_OF_PARTICIPANTS", "NUMBER", "COUNT_OF_UNITS"):
            continue
        groups = om.get("groups", [])
        if len(groups) < 2:
            continue
        # per-group event count (first class/category measurements)
        events = {}
        classes = om.get("classes", [])
        if classes and classes[0].get("categories"):
            for m in classes[0]["categories"][0].get("measurements", []):
                events[m.get("groupId")] = _num(m.get("value"))
        # per-group denominator
        denoms = {}
        for d in om.get("denoms", []):
            for c in d.get("counts", []):
                denoms[c.get("groupId")] = _num(c.get("value"))
        if not denoms:  # fall back to group-level "seriousNumAffected"? no — need denom
            continue
        # classify each group as intervention or comparator by title
        interv_gid = comp_gid = None
        for g in groups:
            tl = (g.get("title") or "").lower()
            if any(c in tl for c in comp_l):
                comp_gid = g.get("id")
            elif any(i in tl for i in interv_l):
                interv_gid = g.get("id")
        # 2-arm fallback: the placebo/control arm is comparator, the other is intervention
        if len(groups) == 2 and (interv_gid is None or comp_gid is None):
            ids = [g.get("id") for g in groups]
            if comp_gid and interv_gid is None:
                interv_gid = [i for i in ids if i != comp_gid][0]
            elif interv_gid and comp_gid is None:
                comp_gid = [i for i in ids if i != interv_gid][0]
        if not (interv_gid and comp_gid):
            continue
        ai, n1i = events.get(interv_gid), denoms.get(interv_gid)
        ci, n2i = events.get(comp_gid), denoms.get(comp_gid)
        if None in (ai, n1i, ci, n2i):
            continue
        if not (0 <= ai <= n1i and 0 <= ci <= n2i and n1i > 0 and n2i > 0):
            continue
        gi = next(g.get("title") for g in groups if g.get("id") == interv_gid)
        gc = next(g.get("title") for g in groups if g.get("id") == comp_gid)
        return {"ai": int(ai), "n1i": int(n1i), "ci": int(ci), "n2i": int(n2i),
                "source": (f"ClinicalTrials.gov results (structured): outcome '{om.get('title','')[:80]}' "
                           f"{int(ai)}/{int(n1i)} ({gi[:24]}) vs {int(ci)}/{int(n2i)} ({gc[:24]})")}
    return None
