"""Partial, object-derived GRADE certainty rating (Stage GRADE, forward plan G1).

Computes the mechanical GRADE domains from what is already in the review object; leaves the two domains
that require human judgement explicitly UN-rated (labelled), never guessed. Starting certainty for a body
of RCTs is HIGH; each downgrade is justified from a committed field.

Domains:
  risk_of_bias   : from rob2 overall levels of the primary-outcome pooled trials + coverage.
                   any 'high' -> down 1; else 'some concerns' in >=half -> down 1; incomplete coverage
                   caps the rating (cannot be 'high certainty' if RoB is unassessed for pooled trials).
  inconsistency  : from tau2 / the I2 implied by the pool. k<2 -> not estimable (single trial: no
                   inconsistency, but see imprecision). tau2 large relative to effect / wide PI -> down 1.
  imprecision    : from k, total N (optimal information size) and whether the 95% CI crosses the null
                   (ratio 1.0 / MD 0). CI crosses null -> down 1; very wide CI or k==1 small N -> down 1.
  publication_bias: NOVEL — from the registry ghost census (ghost.json), NOT funnel asymmetry. a high
                   proportion of completed-but-unpublished registered trials -> down 1. Better than
                   funnel plots at our small k.
  indirectness   : NOT auto-rated (population/intervention/outcome directness is a judgement) -> labelled.

Returns a dict {domains:{...}, start, downgrades, certainty, basis}. certainty in
{high, moderate, low, very_low}. Object-derived: every number traces to a committed field, so the
anti-drift prose guard stays satisfied when rendered like _error_coverage_section.
"""
from __future__ import annotations


def _norm_overall(overall):
    if not overall:
        return None
    o = overall.lower()
    if o.startswith("high"):
        return "high"
    if o.startswith("low"):
        return "low"
    if "some concern" in o:
        return "some_concerns"
    return "other"


def _rob_domain(review):
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    trials = (prim or {}).get("trials", []) or []
    rob = (review.get("rob2") or {}).get("trials") or {}
    levels = [_norm_overall((rob.get(str(t.get("label"))) or {}).get("overall")) for t in trials]
    n = len(levels)
    rated = [x for x in levels if x]
    n_rated = len(rated)
    n_high = sum(1 for x in rated if x == "high")
    n_some = sum(1 for x in rated if x == "some_concerns")
    down = 0
    if n_rated == 0 and n > 0:
        # External audit (C-ROB-1): zero assessed CANNOT establish low risk. "No assessed trial at
        # high risk" is not a clean bill when nothing was assessed -- it is no information. Coverage
        # gates the judgement: with no machine-derived RoB signal for ANY pooled trial, downgrade for
        # unknown study limitations rather than defaulting to no-downgrade.
        down = 1
        basis = (f"risk of bias NOT ASSESSED for any of the {n} pooled trial(s) "
                 f"(no machine-derived risk-of-bias signal available) -> downgraded for unknown study limitations")
    elif n_high:
        down = 1
        basis = f"{n_high} of {n} pooled trial(s) at high risk of bias"
    elif n_some >= (n_rated + 1) // 2:
        down = 1
        basis = f"{n_some} of {n_rated} assessed trial(s) at 'some concerns'"
    else:
        basis = f"none of the {n_rated} assessed trial(s) at high risk; fewer than half at 'some concerns'"
    # incomplete coverage caps certainty (cannot claim high certainty on RoB we did not assess)
    coverage_incomplete = n_rated < n
    if coverage_incomplete and n_rated > 0:
        basis += (f"; risk-of-bias signal available for only {n_rated} of {n} pooled trials "
                  f"(registry-derived), so the rating is capped")
    return {"downgrade": down, "coverage_incomplete": coverage_incomplete,
            "n_trials": n, "n_rated": n_rated, "n_high": n_high, "n_some": n_some, "basis": basis}


def _inconsistency_domain(res):
    k = res.get("k")
    tau2 = res.get("tau2")
    if k is None or k < 2:
        return {"downgrade": 0, "not_estimable": True,
                "basis": "single trial (k=1): between-study inconsistency is not estimable"}
    # PI substantially wider than CI (on the log scale for ratios) signals real heterogeneity.
    down = 0
    basis = f"tau^2={tau2}"
    pil, pih = res.get("pi_low"), res.get("pi_high")
    cil, cih = res.get("ci_low"), res.get("ci_high")
    if tau2 and tau2 > 0 and pil is not None and cil is not None and cih:
        # ratio scales are positive; compare PI/CI width ratio on the same scale
        try:
            pi_w = pih - pil
            ci_w = cih - cil
            if ci_w > 0 and pi_w / ci_w >= 2.0:
                down = 1
                basis += f"; prediction interval [{pil}, {pih}] is >=2x the CI width -> real heterogeneity"
            else:
                basis += "; prediction interval not markedly wider than the CI"
        except TypeError:
            pass
    else:
        basis += " (no between-study heterogeneity detected)" if tau2 == 0 else ""
    return {"downgrade": down, "not_estimable": False, "basis": basis}


def _imprecision_domain(res, scale):
    """GRADE imprecision. External audit (C-GRADE-1): a CI that crosses the null is NOT automatically
    imprecise -- a tight interval around no-effect (e.g. RR 0.91-1.08) is PRECISION about no effect and
    excludes an appreciable effect in both directions. Downgrade only when the CI is wide enough to be
    consistent with BOTH an appreciable benefit AND an appreciable harm (a decision-relevant span), or
    for a single small trial. Appreciable effect on a ratio scale = a 25% relative change (0.75 / 1.25),
    a conventional GRADE default; the threshold is stated so a reader can substitute a topic-specific
    minimally-important difference."""
    k = res.get("k")
    cil, cih = res.get("ci_low"), res.get("ci_high")
    if cil is None or cih is None:
        return {"downgrade": 0, "basis": "no confidence interval available"}
    is_md = (scale or "").upper() == "MD"
    null = 0.0 if is_md else 1.0
    # ROUNDED-CI precision hierarchy (tranexamic-acid cold audit): a CI bound printed EXACTLY on the null
    # (RR/OR/HR upper or lower limit == 1.00; MD == 0.00) is almost always a ROUNDED publication limit --
    # WOMAN prints 0.65-1.00 while the count-recomputed interval is 0.6544-0.9961, which does NOT cross 1.
    # A limit exactly on the null is treated as uncertain-due-to-rounding, NOT a definite crossing: require
    # a STRICT cross (cil < null < cih) to flag imprecision, so a rounded boundary no longer forces a
    # spurious downgrade. (The stronger fix, preferring count-recomputed CIs, is in extraction.)
    eps = 1e-9
    strict_cross = bool(cil < null - eps and cih > null + eps)
    touches_null = bool(abs(cih - null) <= eps or abs(cil - null) <= eps)
    crosses = strict_cross
    down = 0
    basis = f"95% CI [{cil}, {cih}]"
    if touches_null and not strict_cross:
        basis += ("; a CI limit is printed exactly on the null -> null_crossing=uncertain_due_to_rounding "
                  "(likely a rounded publication limit; not treated as crossing, not downgraded for it)")
    if is_md:
        # No committed minimally-important difference for continuous outcomes -> retain the
        # conservative crossing rule but DISCLOSE that a clinical threshold was not applied.
        if crosses:
            down += 1
            basis += (f"; crosses the null ({null:g}) and no minimally-important difference is committed "
                      f"for this continuous outcome, so imprecision is flagged conservatively")
    else:
        t_benefit, t_harm = 0.75, 1.25  # appreciable = 25% relative change
        includes_benefit = cil < t_benefit
        includes_harm = cih > t_harm
        if crosses and (includes_benefit or includes_harm):
            down += 1
            side = ("an appreciable benefit (<=%g)" % t_benefit) if includes_benefit else ""
            side2 = ("an appreciable harm (>=%g)" % t_harm) if includes_harm else ""
            span = " and ".join(s for s in (side, side2) if s)
            basis += (f"; crosses the null AND is compatible with {span} -> imprecise "
                      f"(the estimate is consistent with both no effect and an appreciable effect)")
        elif crosses:
            basis += (f"; crosses the null but excludes an appreciable effect on BOTH sides "
                      f"(within {t_benefit:g}-{t_harm:g}) -> precise about the absence of an appreciable effect")
        elif cil > 0 and (cih / cil) > 3.0:
            # Excludes the null but the interval is very wide (bounds differ by >3x): the DIRECTION is
            # clear but the magnitude is highly uncertain (e.g. a small single trial, OR 8.25 [1.45-46.9])
            # -> still imprecise, even though it does not cross the null.
            down += 1
            basis += f"; excludes the null but is very wide (upper/lower bound ratio > 3) -> imprecise magnitude"
        else:
            basis += "; excludes the null with a reasonably tight interval -> precise"
    if k == 1:
        # External audit: a single LARGE trial with a tight CI that excludes the null (SELECT:
        # 17,604 patients, CI 0.72-0.90) is PRECISION, not imprecision — do NOT downgrade automatically
        # for being one trial. Imprecision follows the CI (handled above): a single trial whose CI
        # crosses the null and reaches an appreciable effect is still downgraded; a tight null-excluding
        # CI is not. (A narrow CI is itself evidence the information size was adequate.)
        basis += "; single trial — imprecision judged from the CI, not downgraded merely for k=1"
    return {"downgrade": min(down, 2), "crosses_null": crosses, "basis": basis}


def _pubbias_domain(ghost):
    if not ghost:
        return {"downgrade": 0, "not_assessable": True,
                "basis": "no registry ghost census available for this topic"}
    enum = ghost.get("enumerated") or 0
    ongoing = ghost.get("ongoing_or_recent") or 0
    ghost_ub = ghost.get("ghost_upper_bound") or 0
    completed = max(enum - ongoing, 0)
    frac = (ghost_ub / completed) if completed else 0.0
    # CONTAMINATED DENOMINATOR (repeated across the cold audits: statins, tranexamic, +others -- now the
    # single most-repeated GRADE defect). The ghost census enumerates a BROAD condition+drug registry
    # universe ("Elderly + Atorvastatin", "postpartum haemorrhage") full of trials our PICO screens OUT
    # (wrong population, prophylaxis-not-treatment, unrelated interventions). A ghost FRACTION computed on
    # that universe is NOT this PICO's publication-bias rate, so it must NOT downgrade. Until the census is
    # recomputed on the SCREENED-ELIGIBLE universe (marked ghost['pico_scoped']==True), do not downgrade;
    # report the fraction as descriptive only.
    pico_scoped = bool(ghost.get("pico_scoped"))
    if not pico_scoped:
        return {"downgrade": 0, "not_assessable": True, "ghost_fraction": round(frac, 3),
                "basis": (f"registry census ({ghost_ub} of ~{completed} completed unpublished, {frac:.0%}) was "
                          "enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a "
                          "contaminated denominator cannot be this PICO's publication-bias rate, so publication "
                          "bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)")}
    down = 1 if frac >= 0.30 else 0
    basis = (f"PICO-scoped registry census: {ghost_ub} of ~{completed} completed screened-eligible trials have "
             f"no published result (upper bound {frac:.0%}); assessed from the registry, not a funnel plot")
    if down:
        basis += " -> downgraded"
    return {"downgrade": down, "ghost_fraction": round(frac, 3), "basis": basis}


CERT = ["high", "moderate", "low", "very_low"]


def grade(review, ghost=None):
    """Compute a partial GRADE from the review object (+ optional ghost census)."""
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    if not prim or not prim.get("result"):
        return None
    res = prim["result"]
    scale = res.get("scale")
    rob = _rob_domain(review)
    inc = _inconsistency_domain(res)
    imp = _imprecision_domain(res, scale)
    pub = _pubbias_domain(ghost)
    # NOT RATEABLE on an incoherent evidence object (audit 21 #5 / refinement 2): if the primary pool mixes
    # INCOMPATIBLE estimand classes (a recurrent-event rate ratio pooled with a first-event ratio), the
    # pooled effect is not one coherent quantity, so imprecision/inconsistency are computed from an artefact
    # and an overall certainty CATEGORY would be meaningless. Show the domain signals; suppress the overall.
    if (res.get("estmeasure") or {}).get("status") == "incompatible":
        return {
            "start": "high",
            "domains": {"risk_of_bias": rob, "inconsistency": inc, "imprecision": imp,
                        "publication_bias": pub,
                        "indirectness": {"downgrade": 0, "not_auto_rated": True,
                                         "basis": "not auto-rated (human judgement)"}},
            "downgrades": rob["downgrade"] + inc["downgrade"] + imp["downgrade"] + pub["downgrade"],
            "certainty": "not_rateable",
            "not_rateable_reason": ("the primary pool mixes INCOMPATIBLE estimand classes "
                                    f"({' + '.join((res.get('estmeasure') or {}).get('canonicals', []))}); an "
                                    "overall certainty cannot be produced from an incoherent effect object — "
                                    "the domain signals are shown, the overall is suppressed until the estimand "
                                    "is made coherent (harmonise the measure or split the outcome)"),
            "basis": "partial GRADE: overall certainty NOT RATEABLE (estimand-incompatible pool).",
        }
    downgrades = rob["downgrade"] + inc["downgrade"] + imp["downgrade"] + pub["downgrade"]
    idx = min(downgrades, 3)  # high -> moderate -> low -> very_low
    # RoB coverage incompleteness caps at 'moderate' (cannot certify high on unassessed bias)
    if rob.get("coverage_incomplete") and idx == 0:
        idx = 1
        capped = True
    else:
        capped = False
    # A single trial cannot mechanically reach 'high': consistency is not estimable (k=1) and the
    # optimal information size cannot be confirmed from one trial, so cap at 'moderate'. This still
    # lets a large, precise single RCT (e.g. SELECT) rise to moderate rather than being wrongly pushed
    # to low by an automatic single-trial imprecision downgrade (the external-audit fix).
    single_trial_capped = False
    if (res.get("k") or 0) <= 1 and idx == 0:
        idx = 1
        single_trial_capped = True
    return {
        "start": "high",
        "domains": {
            "risk_of_bias": rob,
            "inconsistency": inc,
            "imprecision": imp,
            "publication_bias": pub,
            "indirectness": {"downgrade": 0, "not_auto_rated": True,
                             "basis": "directness of population/intervention/comparator/outcome is a human "
                                      "judgement; not auto-rated (the scope note on the page states the PICO)"},
        },
        "downgrades": downgrades,
        "certainty": CERT[idx],
        "certainty_capped_by_rob_coverage": capped,
        "certainty_capped_single_trial": single_trial_capped,
        "basis": "partial GRADE: risk-of-bias, inconsistency, imprecision and (registry-based) publication "
                 "bias are computed from committed fields; indirectness is left to human judgement.",
    }
