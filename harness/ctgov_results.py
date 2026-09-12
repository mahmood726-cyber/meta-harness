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


def _classify_arms(groups, interv_l, comp_l):
    """Assign the two arms to (intervention_gid, comparator_gid) by group title, with the standard
    2-arm fallback (the placebo/control arm is the comparator, the other is the intervention)."""
    interv_gid = comp_gid = None
    for g in groups:
        tl = (g.get("title") or "").lower()
        if any(c in tl for c in comp_l):
            comp_gid = g.get("id")
        elif any(i in tl for i in interv_l):
            interv_gid = g.get("id")
    if len(groups) == 2 and (interv_gid is None or comp_gid is None):
        ids = [g.get("id") for g in groups]
        if comp_gid and interv_gid is None:
            interv_gid = [i for i in ids if i != comp_gid][0]
        elif interv_gid and comp_gid is None:
            comp_gid = [i for i in ids if i != interv_gid][0]
    return interv_gid, comp_gid


def _extract_ctgov_continuous(om, interv_l, comp_l):
    """Per-arm mean/SD/n from a MEAN outcome measure with dispersion 'Standard Deviation' → a
    mean-difference input {mean1,sd1,nc1,mean2,sd2,nc2,scale:'MD',source}. Refuses (None) on any
    other dispersion type, missing value/spread/denom, non-positive SD or n, or <2 arms — the number
    is taken verbatim from the structured table, never inferred."""
    disp = (om.get("dispersionType") or "").lower()
    if "standard deviation" not in disp:
        return None  # SE / 95% CI / inter-quartile range / full range: refuse here (no silent conversion)
    groups = om.get("groups", [])
    if len(groups) < 2:
        return None
    # MULTI-ARM GUARD (continuous): a fixed-dose multi-arm trial (e.g. esketamine 56 mg / 84 mg / placebo)
    # posts >2 arms; picking one intervention dose without a pre-specified rule is arbitrary selection.
    # If more than one arm matches the intervention terms (or the comparator terms), REFUSE — the
    # dose/arm to pool is ambiguous, exactly the CANTOS/TRANSFORM-1 class the multi-arm rule forbids.
    _iv = [g for g in groups if any(i in (g.get("title") or "").lower() for i in interv_l)]
    _cp = [g for g in groups if any(c in (g.get("title") or "").lower() for c in comp_l)]
    if len(_iv) > 1 or len(_cp) > 1:
        return None
    if len(groups) > 2 and not (len(_iv) == 1 and len(_cp) == 1):
        return None
    classes = om.get("classes", [])
    if not (classes and classes[0].get("categories")):
        return None
    means, sds = {}, {}
    for m in classes[0]["categories"][0].get("measurements", []):
        means[m.get("groupId")] = _num(m.get("value"))
        sds[m.get("groupId")] = _num(m.get("spread"))
    denoms = {}
    for d in om.get("denoms", []):
        for c in d.get("counts", []):
            denoms[c.get("groupId")] = _num(c.get("value"))
    interv_gid, comp_gid = _classify_arms(groups, interv_l, comp_l)
    if not (interv_gid and comp_gid):
        return None
    mean1, sd1, n1 = means.get(interv_gid), sds.get(interv_gid), denoms.get(interv_gid)
    mean2, sd2, n2 = means.get(comp_gid), sds.get(comp_gid), denoms.get(comp_gid)
    if None in (mean1, sd1, n1, mean2, sd2, n2):
        return None
    if not (sd1 > 0 and sd2 > 0 and n1 > 0 and n2 > 0):
        return None
    gi = next((g.get("title") for g in groups if g.get("id") == interv_gid), "")
    gc = next((g.get("title") for g in groups if g.get("id") == comp_gid), "")
    unit = om.get("unitOfMeasure") or ""
    # Carry the measure's population description verbatim (e.g. "Pre-planned analysis on ITT population
    # age 65-80") so a pre-specified subgroup is disclosed on the page, not silently pooled as the trial.
    popd = (om.get("populationDescription") or "").strip()
    return {"mean1": mean1, "sd1": sd1, "nc1": int(n1),
            "mean2": mean2, "sd2": sd2, "nc2": int(n2), "scale": "MD",
            "source": (f"ClinicalTrials.gov results (structured, continuous): outcome "
                       f"'{om.get('title','')[:70]}' mean {mean1} (SD {sd1}, n={int(n1)}) [{gi[:22]}] "
                       f"vs {mean2} (SD {sd2}, n={int(n2)}) [{gc[:22]}]" + (f" {unit}" if unit else "")
                       + (f" — population: {popd[:80]}" if popd else ""))}


def extract_ctgov(outcome_measures, outcome_kws, interv_terms, comp_terms, min_total=None,
                  judgments=None):
    """Return dict {ai,n1i,ci,n2i,source} for the outcome measure matching our outcome, else None.

    Chooses the outcome measure whose TITLE contains one of our outcome keywords (so we do not
    read a trial's PRIMARY when its primary is a different endpoint than ours). Assigns the two
    arms to intervention/comparator by group title. Accepts only integer counts <= denominator.

    min_total: if given, an outcome measure whose two arm denominators sum to less than min_total
    is REJECTED. This blocks a SUBGROUP registration from being pooled as the whole trial: the
    SMART paper (PMID 29485925, 15,802 patients / 7942 vs 7860) registers its medical-ICU cohort
    under NCT02444988, whose posted results are only 2735+2646 -- pooling those as SMART's
    mortality would be false against the trial. The caller passes ~0.6x the trial's abstract-stated
    enrollment as the floor.

    judgments: OUTCOME-IDENTITY GATE (the sanctioned model-as-source use). When None, selection is
    the deterministic substring match below (backward-compatible). When a dict is given
    (title -> {is_match, declared_outcome, candidate_population, candidate_timepoint,
    candidate_definition, ...}, produced by scripts/outcome_judgments.py and committed to
    cache/<slug>/outcome_judgments.json), an outcome measure is accepted ONLY if its title carries a
    committed judgment with is_match True -- i.e. the review's declared outcome and THIS measure share
    population + timepoint + definition. Any OM without an is_match=True judgment is REFUSED, even if
    its title substring-matches. This closes the azithromycin class (a broadened keyword matched an
    ED-visit OM / a subgroup HR that is NOT the review's outcome). The judgment is a checkable source
    (5 fields, rendered model-derived); it NEVER supplies the number -- the counts still come from the
    structured arm table below.
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

    def identity_ok(t):
        # Outcome-identity gate: when judgments are supplied, the OM title must carry an
        # is_match=True judgment. No judgment (or is_match False) => REFUSE this measure.
        if judgments is None:
            return True
        j = judgments.get(t) or judgments.get((t or "").strip())
        return bool(j and j.get("is_match") is True)

    # Prefer a title-keyword match AND (when gated) an is_match=True identity judgment;
    # among survivors prefer type PRIMARY.
    cands = [om for om in outcome_measures
             if title_matches(om.get("title")) and identity_ok(om.get("title"))]
    cands.sort(key=lambda om: 0 if om.get("type") == "PRIMARY" else 1)
    for om in cands:
        ptype = (om.get("paramType") or "").upper()
        # CONTINUOUS measure (MEAN + per-arm SD): structured mean-difference data, the AACT-equivalent
        # of a per-arm mean/SD table. Only paramType MEAN with dispersion "Standard Deviation" is taken
        # directly; SE/CI/median-range dispersions are REFUSED here (refuse-on-ambiguity — an SE needs
        # n and a range needs a Wan conversion that belongs in the prose extractor, not silently here).
        if ptype == "MEAN":
            cont = _extract_ctgov_continuous(om, interv_l, comp_l)
            if cont:
                return cont
            continue
        # only participant-count style measures (skip medians/rates)
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
        if min_total and (n1i + n2i) < min_total:
            continue  # this OM is a subgroup, not the whole trial — do not pool as the trial
        gi = next(g.get("title") for g in groups if g.get("id") == interv_gid)
        gc = next(g.get("title") for g in groups if g.get("id") == comp_gid)
        out = {"ai": int(ai), "n1i": int(n1i), "ci": int(ci), "n2i": int(n2i),
               "source": (f"ClinicalTrials.gov results (structured): outcome '{om.get('title','')[:80]}' "
                          f"{int(ai)}/{int(n1i)} ({gi[:24]}) vs {int(ci)}/{int(n2i)} ({gc[:24]})")}
        # Carry the model-derived identity judgment that admitted this OM, so the page can render it
        # (checkable, 5 fields). The judgment gated selection; it does NOT supply any number here.
        if judgments is not None:
            j = judgments.get(om.get("title")) or judgments.get((om.get("title") or "").strip())
            if j:
                out["identity_judgment"] = dict(j, candidate_title=om.get("title"))
        return out
    return None
