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

from . import k2 as k2_mod

PROVISIONAL = "GRADE provisional -- not yet fully assessable"


def render_certainty(g):
    """The single display contract for the canonical overall certainty state."""
    if not g:
        return "GRADE not assessed"
    if g.get("unassessed_domains") or g.get("certainty") == "provisional":
        return g.get("certainty_state") or PROVISIONAL
    return g.get("certainty_state") or (g.get("certainty") or "not assessed").replace("_", " ")


def missing_family_count(review):
    """Count source-backed absent families; do not infer a count from reason prose."""
    primary = next((o for o in review.get("outcomes", []) if o.get("primary")), {})
    rows = (primary.get("known_missing_sensitivity") or {}).get("rows") or []
    if rows:
        return len({str(r.get("trial_key") or r.get("id") or r.get("name")) for r in rows})
    absent = primary.get("declared_absent_trials") or []
    return len(absent) if absent else None


def membership_incomplete(review):
    codes = {r.get("code") for r in (review.get("invalidation") or {}).get("reasons", [])}
    panels = [review.get("known_missing_sensitivity") or {}]
    panels.extend(o.get("known_missing_sensitivity") or {} for o in review.get("outcomes", []) if o.get("primary"))
    return bool(codes & {"eligible_declared_absent", "known_eligible_missing"}
                or any(p.get("rows") for p in panels))


def stale_heterogeneity(review):
    if not membership_incomplete(review):
        return ""
    n = missing_family_count(review)
    count = f"{n} eligible families not in the pool" if n is not None else "eligible families not in the pool; count not established"
    return f"STALE: pooled membership known incomplete ({count}); tau^2, I^2 and the prediction interval are descriptive only, not interpretable."


def machine_rob(review):
    rob = review.get("rob2") or {}
    flags = [str(rob.get("output_family") or ""), str(rob.get("rob_basis") or ""), str(rob.get("basis") or "")]
    flags.extend(str(d.get("rule_id") or "") for t in (rob.get("trials") or {}).values()
                 for d in (t.get("domains") or {}).values())
    return any("machine" in f.lower() or "registry-signal-restricted" in f.lower() for f in flags)


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


def _rob_entry(rob, trial):
    keys = [
        str(trial.get("label") or "").strip(),
        str(trial.get("id") or "").replace("PMID ", "").replace("PMID:", "").strip(),
    ]
    for key in keys:
        if key and key in rob:
            return rob[key]
    return {}


def _rob_domain(review):
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    trials = (prim or {}).get("trials", []) or []
    rob = (review.get("rob2") or {}).get("trials") or {}
    # Join by the trial identity (PMID/NCT), never the display label: acronym labels (SOUL, PHILO,
    # CLEAR SYNERGY) are rated in rob2 under their PMID and were invisible here (integration 2026-09-16).
    from .claimgraph import trial_key as _tk
    levels = [_norm_overall((rob.get(_tk(t)) or rob.get(str(t.get("label"))) or {}).get("overall")) for t in trials]
    n = len(levels)
    rated = [x for x in levels if x]
    n_rated = len(rated)
    n_high = sum(1 for x in rated if x == "high")
    n_some = sum(1 for x in rated if x == "some_concerns")
    down = 0
    assessed = n_rated > 0
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
    if machine_rob(review):
        assessed = False
        basis = "FORMAL RoB 2 NOT YET ASSESSED — machine signals shown below"
    return {"downgrade": down, "coverage_incomplete": coverage_incomplete, "assessed": assessed,
            "n_trials": n, "n_rated": n_rated, "n_high": n_high, "n_some": n_some, "basis": basis}


def _inconsistency_domain(res, review=None):
    if review and membership_incomplete(review):
        domain = _inconsistency_domain(res)
        domain.update(assessed=False, stale=True,
                      basis="not assessable: " + stale_heterogeneity(review))
        return domain
    k = res.get("k")
    tau2 = res.get("tau2")
    if tau2 is None:
        tau2 = (res.get("counterfactual") or {}).get("would_be_tau2")
    if k is None or k < 2:
        return {"downgrade": 0, "not_estimable": True, "assessed": False,
                "basis": "single trial (k=1): between-study inconsistency is not estimable"}
    i2 = res.get("i2")
    if i2 is None:
        i2 = k2_mod.i2_from_q(res.get("Q"), k)
    if k == 2:
        conflict = res.get("pool_refused", {}).get("code") == k2_mod.DIRECTION_CONFLICT_K2
        high_i2 = False
        try:
            high_i2 = i2 is not None and float(i2) > k2_mod.AUTO_INCONSISTENCY_I2_THRESHOLD
        except (TypeError, ValueError):
            high_i2 = False
        basis = f"k=2: inconsistency is not assessable automatically"
        if i2 is not None:
            basis += f"; Q-derived I^2={round(float(i2), 1)}%"
        if tau2 is not None:
            basis += f"; tau^2={tau2}"
        if conflict:
            basis += "; trial point estimates conflict in direction and/or their CIs do not overlap"
        elif high_i2:
            basis += f"; I^2 > {k2_mod.AUTO_INCONSISTENCY_I2_THRESHOLD:g}%"
        else:
            basis += "; two concordant trials"
        basis += "; prediction interval absence is not evidence of no inconsistency, so downgrade is left to human judgement"
        # Two CONCORDANT trials with low I^2 are an assessable state (direction and I^2 are computed);
        # only a direction conflict or high I^2 is genuinely unassessable by machine and draws the
        # conservative floor in grade(). The k=2 state is still not an automatic 'no inconsistency'.
        return {"downgrade": 0, "not_assessable_automatically": bool(conflict or high_i2),
                "k2_not_automatic": True, "assessed": False,
                "direction_conflict": conflict, "i2": round(float(i2), 1) if i2 is not None else None,
                "basis": basis}
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
    return {"downgrade": down, "not_estimable": False, "assessed": True, "basis": basis}


def _imprecision_domain(res, scale):
    """GRADE imprecision. External audit (C-GRADE-1): a CI that crosses the null is NOT automatically
    imprecise -- a tight interval around no-effect (e.g. RR 0.91-1.08) is PRECISION about no effect and
    excludes an appreciable effect in both directions. Downgrade only when the CI is wide enough to be
    consistent with BOTH an appreciable benefit AND an appreciable harm (a decision-relevant span), or
    for a single small trial. Appreciable effect on a ratio scale = a 25% relative change (0.75 / 1.25),
    a conventional GRADE default; the threshold is stated so a reader can substitute a topic-specific
    minimally-important difference."""
    k = res.get("k")
    if res.get("pool_refused"):
        return {"downgrade": 0, "assessed": False, "not_assessable_automatically": True,
                "basis": ("pooled row refused ("
                          f"{(res.get('pool_refused') or {}).get('code')}); imprecision cannot be "
                          "machine-rated from a non-served pooled CI")}
    if res.get("pooled_ci_refused"):
        return {"downgrade": 0, "assessed": False, "not_assessable_automatically": True,
                "basis": ("registered pooled CI refused at k=2 ("
                          f"{(res.get('pooled_ci_refused') or {}).get('code')}); imprecision requires "
                          "human judgement and is not read from the quarantined HKSJ interval")}
    cil, cih = res.get("ci_low"), res.get("ci_high")
    if cil is None or cih is None:
        return {"downgrade": 0, "assessed": False, "basis": "no confidence interval available"}
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
    return {"downgrade": min(down, 2), "crosses_null": crosses, "assessed": True, "basis": basis}


def _pubbias_domain(ghost):
    if not ghost:
        return {"downgrade": 0, "not_assessable": True, "assessed": False,
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
        return {"downgrade": 0, "not_assessable": True, "assessed": False, "ghost_fraction": round(frac, 3),
                "basis": (f"registry census ({ghost_ub} of ~{completed} completed unpublished, {frac:.0%}) was "
                          "enumerated over a BROAD condition+drug universe, not the screened-eligible PICO -- a "
                          "contaminated denominator cannot be this PICO's publication-bias rate, so publication "
                          "bias is NOT downgraded here (descriptive only; a PICO-scoped census is the fix)")}
    down = 1 if frac >= 0.30 else 0
    basis = (f"PICO-scoped registry census: {ghost_ub} of ~{completed} completed screened-eligible trials have "
             f"no published result (upper bound {frac:.0%}); assessed from the registry, not a funnel plot")
    if down:
        basis += " -> downgraded"
    return {"downgrade": down, "ghost_fraction": round(frac, 3), "assessed": True, "basis": basis}


CERT = ["high", "moderate", "low", "very_low"]


def grade(review, ghost=None):
    """Compute a partial GRADE from the review object (+ optional ghost census)."""
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    if not prim or not prim.get("result"):
        return None
    res = prim["result"]
    scale = res.get("scale")
    rob = _rob_domain(review)
    inc = _inconsistency_domain(res, review)
    imp = _imprecision_domain(res, scale)
    pub = _pubbias_domain(ghost)
    _rob2_trials = (review.get("rob2") or {}).get("trials") or {}
    prim_trials = (prim or {}).get("trials", []) or []
    d3_levels = [((_rob2_trials.get(str(t.get("label"))) or {}).get("domains") or {}).get("D3_missing_outcome_data", {}).get("level")
                 for t in prim_trials]
    d3_unassessed_n = sum(1 for lv in d3_levels if lv == "not assessed")
    rob_basis = (f"machine-assessed domains only; D3 unassessed on {d3_unassessed_n} "
                 f"of {len(prim_trials)} trial(s)")
    # NOT RATEABLE on an incoherent evidence object (audit 21 #5 / refinement 2): if the primary pool mixes
    # INCOMPATIBLE estimand classes (a recurrent-event rate ratio pooled with a first-event ratio), the
    # pooled effect is not one coherent quantity, so imprecision/inconsistency are computed from an artefact
    # and an overall certainty CATEGORY would be meaningless. Show the domain signals; suppress the overall.
    if (res.get("estmeasure") or {}).get("status") == "incompatible":
        return {
            "start": "high",
            "domains": {"risk_of_bias": rob, "inconsistency": inc, "imprecision": imp,
                        "publication_bias": pub,
                        "indirectness": {"downgrade": 0, "not_auto_rated": True, "assessed": False,
                                         "basis": "not auto-rated (human judgement)"}},
            "downgrades": rob["downgrade"] + inc["downgrade"] + imp["downgrade"] + pub["downgrade"],
            "certainty": "provisional",
            "certainty_state": PROVISIONAL,
            "unassessed_domains": [name for name, dom in {"risk_of_bias": rob, "inconsistency": inc, "imprecision": imp, "publication_bias": pub, "indirectness": {"assessed": False}}.items() if not dom.get("assessed", True)],
            "rob_basis": rob_basis,
            "not_rateable_reason": ("the primary pool mixes INCOMPATIBLE estimand classes "
                                    f"({' + '.join((res.get('estmeasure') or {}).get('canonicals', []))}); an "
                                    "overall certainty cannot be produced from an incoherent effect object — "
                                    "the domain signals are shown, the overall is suppressed until the estimand "
                                    "is made coherent (harmonise the measure or split the outcome)"),
            "basis": "partial GRADE: overall certainty NOT RATEABLE (estimand-incompatible pool).",
        }
    # A domain the machine could NOT assess (k=2 refused CI; direction conflict) is counted as ONE
    # conservative downgrade pending human judgement. Refusing to serve an interval must never RAISE
    # certainty -- on corticosteroids-cap the refusal turned 'low' into 'moderate' before this floor
    # (integration 2026-09-16). The domain object keeps downgrade=0 and says why; the floor is here.
    conservative = []
    for name, dom in (("imprecision", imp), ("inconsistency", inc)):
        if dom.get("not_assessable_automatically") and not dom.get("downgrade"):
            dom["downgrade"] = 1
            dom["conservative"] = True
            dom["basis"] = (dom.get("basis") or "") + " | counted as ONE conservative downgrade pending human judgement (a check that could not run cannot raise certainty)"
            conservative.append(name)
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
    # D3-UNASSESSED CAP (audits 20/21): D3 (missing outcome data) is a required bias domain, and the
    # harness has no outcome-missingness evidence source, so it is permanently NOT ASSESSED for every
    # pooled trial. A body of evidence whose bias assessment is structurally incomplete on a required
    # domain cannot be certified HIGH certainty -- cap at moderate, with the named reason, until an
    # outcome-missingness source (AACT milestones / publication flow) makes D3 assessable. Data-driven:
    # if D3 is ever assessed for a pooled trial, the cap lifts automatically.
    _rob2_trials = (review.get("rob2") or {}).get("trials") or {}
    prim_trials = (prim or {}).get("trials", []) or []
    from .claimgraph import trial_key as _tk2
    d3_levels = [((_rob2_trials.get(_tk2(t)) or _rob2_trials.get(str(t.get("label"))) or {}).get("domains") or {}).get("D3_missing_outcome_data", {}).get("level")
                 for t in prim_trials]
    d3_all_unassessed = bool(d3_levels) and all(lv == "not assessed" for lv in d3_levels)
    d3_capped = False
    if d3_all_unassessed and idx == 0:
        idx = 1
        d3_capped = True
    # NOT_ASSESSED != NOT_DOWNGRADED (external audit, STATE root system item 2). A GRADE domain that was
    # not assessed contributes downgrade=0 to the sum, which is arithmetically identical to a domain that
    # WAS assessed and found clean -- so an unassessed domain silently reads as favourable and could let a
    # body of evidence be certified HIGH without publication bias or indirectness ever being evaluated.
    # `UNASSESSED NEVER COUNTS AS FAVOURABLE`: any unassessed domain caps certainty below HIGH (you cannot
    # certify the top rating on a domain you did not look at). Indirectness is structurally never
    # machine-assessed here, so this partial GRADE's honest ceiling is MODERATE until a human rates it --
    # the ceiling is now ENFORCED, not left to coincide with an incidental downgrade. Data-driven: if a
    # domain becomes assessable, it stops capping automatically.
    _dm = {"risk_of_bias": rob, "inconsistency": inc, "imprecision": imp,
           "publication_bias": pub, "indirectness": {"assessed": False}}
    unassessed = [name for name, d in _dm.items() if not d.get("assessed", True)]
    unassessed_cap = False
    if unassessed and idx == 0:
        idx = 1
        unassessed_cap = True
    return {
        "start": "high",
        "domains": {
            "risk_of_bias": rob,
            "inconsistency": inc,
            "imprecision": imp,
            "publication_bias": pub,
            "indirectness": {"downgrade": 0, "not_auto_rated": True, "assessed": False,
                             "basis": "directness of population/intervention/comparator/outcome is a human "
                                      "judgement; not auto-rated (the scope note on the page states the PICO)"},
        },
        "downgrades": downgrades,
        "conservative_downgrades_pending_human_judgement": conservative,
        "certainty": "provisional" if unassessed else CERT[idx],
        "certainty_state": PROVISIONAL if unassessed else CERT[idx].replace("_", " "),
        "certainty_capped_by_rob_coverage": capped,
        "certainty_capped_single_trial": single_trial_capped,
        "certainty_capped_d3_unassessed": d3_capped,
        "certainty_capped_unassessed_domain": unassessed_cap,
        "unassessed_domains": unassessed,
        "rob_basis": rob_basis,
        "basis": "partial GRADE: risk-of-bias, inconsistency, imprecision and (registry-based) publication "
                 "bias are computed from committed fields; indirectness is left to human judgement.",
    }
