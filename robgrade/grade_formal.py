"""FORMAL GRADE per served outcome (Cochrane Handbook v6.5 chapter 14; GRADE guidance 4-8): deterministic rules over
COMPUTED inputs, every downgrade citing the input it rests on. Randomised trials start at HIGH.

  risk of bias      the formal RoB 2 objects (robgrade/rob2_formal.py) of the pooled trials for THIS outcome, weighted
                    by each trial's random-effects weight 1/(se^2 + tau^2):
                      -1 (serious) when less than half the weight is from trials at LOW overall risk (GRADE: 'most
                      information from studies at moderate or high risk'); a NOT_ESTABLISHED trial is never counted as
                      LOW (a missing judgement is not a favourable one).
                      'very serious' (-2) is a judgement the tool does not automate: flagged when >= half the weight is
                      HIGH, for the recorded judgement step.
  inconsistency     k < 2: not applicable. Stale membership: not assessable. Otherwise
                      -1 when I^2 >= 50% AND (the prediction interval crosses the null while the CI does not, OR the
                      point estimates fall on both sides of the null); -2 when I^2 >= 75% AND two trials' CIs do not
                      overlap with their point estimates on opposite sides of the null. Leave-one-out crossing of the
                      null is reported as an input, not a rule.
  indirectness      the PICO-compatibility object (outcome.compat_key): -1 when it records a HARD mismatch (a
                      limitation with hard=True, or matched == False); dimension heterogeneity alone is listed, not
                      downgraded (the Handbook's 'indirectness of population/intervention/outcome' is a judgement when
                      the difference is soft: flagged for the recorded judgement step).
  imprecision       ratio measures: -2 when the 95% CI includes both appreciable benefit and appreciable harm (GRADE
                      default thresholds 0.75 and 1.25); -1 when the CI crosses the null; when the CI excludes the null,
                      -1 if the total sample is below the optimal information size (OIS: two-arm, alpha 0.05, power
                      0.80, relative risk reduction 25%, the pooled control-arm risk) -- OIS computed only from
                      structured arm counts, else stated NOT_COMPUTABLE (the CI rule still stands).
  publication bias  k >= 10: Egger's regression test (standardised effect on precision), -1 when p < 0.10;
                      k < 10: NOT_ASSESSABLE_K_LT_10 (small-study tests have too little power), no downgrade.

Arithmetic certainty = HIGH minus the downgrades, floored at VERY_LOW. The reported certainty remains provisional
while any domain is NOT_ASSESSABLE or PARTIAL, or any judgement flag remains unresolved. Publication bias at k < 10
alone does not block a category: not detected is not suspected. Arithmetic is retained separately for review.
"""
from __future__ import annotations

import math

FAMILY = "formal-grade-v1"
LEVELS = ["very_low", "low", "moderate", "high"]
RATIO = ("RR", "OR", "HR", "IRR", "RRR")
Z = 1.959963984540054


def _f(x):
    try:
        v = float(x)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def _dom(downgrade, state, basis, inputs, flags=()):
    return {"downgrade": downgrade, "state": state, "basis": basis, "inputs": inputs, "flags": list(flags)}


# ------------------------------------------------------------------------------------------------ risk of bias

def risk_of_bias(trials, rob, tau2):
    """trials: [{id, se}] of the pooled trials; rob: {trial id: formal RoB 2 object for THIS outcome}."""
    if not trials:
        return _dom(0, "NOT_APPLICABLE", "no pooled trial", {})
    w, share, missing = {}, {"LOW": 0.0, "SOME_CONCERNS": 0.0, "HIGH": 0.0, "NOT_ESTABLISHED": 0.0}, []
    t2 = _f(tau2) or 0.0
    for t in trials:
        se = _f(t.get("se"))
        w[t["id"]] = 1 / (se * se + t2) if se else 0.0
    tot = sum(w.values())
    if tot <= 0:
        return _dom(0, "NOT_ASSESSABLE", "trial weights not computable (no standard errors)", {"trials": [t["id"] for t in trials]})
    per = {}
    for t in trials:
        o = rob.get(t["id"])
        j = ((o or {}).get("overall") or {}).get("judgement") or "NOT_ESTABLISHED"
        if o is None:
            missing.append(t["id"])
        share[j if j in share else "NOT_ESTABLISHED"] += w[t["id"]] / tot
        per[t["id"]] = {"overall": j, "weight_share": round(w[t["id"]] / tot, 4)}
    sh = {k: round(v, 4) for k, v in share.items()}
    inputs = {"weight_share_by_overall": sh, "per_trial": per, "no_formal_assessment": missing, "tau2": t2}
    flags = ["VERY_SERIOUS_FOR_JUDGEMENT"] if sh["HIGH"] >= 0.5 else []
    if missing:
        return _dom(None, "NOT_ASSESSABLE", f"{len(missing)} pooled trial(s) have no formal RoB 2 object for this outcome",
                    inputs, flags)
    # Use unrounded shares: even a tiny positive unjudged weight is not favourable evidence.
    state = "PARTIAL" if share["NOT_ESTABLISHED"] > 0 else "ASSESSED"
    if sh["LOW"] < 0.5:
        return _dom(1, state, f"{100 * (1 - sh['LOW']):.0f}% of the weight is from trials not at low risk "
                                   f"(some concerns {100 * sh['SOME_CONCERNS']:.0f}%, high {100 * sh['HIGH']:.0f}%, "
                                   f"not established {100 * sh['NOT_ESTABLISHED']:.0f}%)", inputs, flags)
    return _dom(0, state, f"{100 * sh['LOW']:.0f}% of the weight is from trials at low risk of bias" +
                ("; some weight has no established judgement" if state == "PARTIAL" else ""), inputs, flags)


# ------------------------------------------------------------------------------------------------ inconsistency

def _null(scale):
    return 1.0 if scale in RATIO else 0.0


def _side(x, null):
    return 0 if x is None else (1 if x > null else -1 if x < null else 0)


def inconsistency(result, trials, scale, stale=False):
    k = int(result.get("k") or 0)
    null = _null(scale)
    i2, lo, hi, plo, phi = (_f(result.get(x)) for x in ("i2", "ci_low", "ci_high", "pi_low", "pi_high"))
    loo = result.get("leave_one_out") or {}
    loo_cross = None
    if loo.get("min") is not None and loo.get("max") is not None:
        loo_cross = _side(_f(loo["min"]), null) != _side(_f(loo["max"]), null)
    inputs = {"k": k, "i2": i2, "ci": [lo, hi], "pi": [plo, phi], "loo_range": [loo.get("min"), loo.get("max")],
              "loo_crosses_null": loo_cross}
    if k < 2:
        return _dom(0, "NOT_APPLICABLE", "a single trial: inconsistency does not apply", inputs)
    if stale:
        return _dom(None, "NOT_ASSESSABLE", "pooled membership is known incomplete (STALE): heterogeneity is descriptive only", inputs)
    if i2 is None:
        return _dom(None, "NOT_ASSESSABLE", "I^2 not computed for this pool", inputs)
    pts = [_f(t.get("effect")) for t in trials]
    sides = {_side(p, null) for p in pts if p is not None} - {0}
    both_sides = sides == {1, -1}
    ci_excl = lo is not None and hi is not None and (hi < null or lo > null)
    pi_cross = plo is not None and phi is not None and plo < null < phi
    # non-overlapping CIs on opposite sides of the null
    sep = False
    cis = [(_f(t.get("ci_low")), _f(t.get("ci_high")), _f(t.get("effect"))) for t in trials]
    for a in cis:
        for b in cis:
            if None not in a + b and a[1] < b[0] and _side(a[2], null) == -1 and _side(b[2], null) == 1:
                sep = True
    inputs.update({"point_estimates_both_sides_of_null": both_sides, "pi_crosses_null_while_ci_excludes": pi_cross and ci_excl,
                   "opposite_non_overlapping_cis": sep})
    if i2 >= 75 and sep:
        return _dom(2, "ASSESSED", f"I^2 {i2:.0f}% with non-overlapping trial CIs on opposite sides of the null", inputs)
    if i2 >= 50 and ((pi_cross and ci_excl) or both_sides):
        why = "the prediction interval crosses the null while the CI excludes it" if (pi_cross and ci_excl) else \
              "point estimates fall on both sides of the null"
        return _dom(1, "ASSESSED", f"I^2 {i2:.0f}% and {why}", inputs)
    return _dom(0, "ASSESSED", f"I^2 {i2:.0f}%; " + ("no rule met" if i2 >= 50 else "below 50%"), inputs)


# ------------------------------------------------------------------------------------------------ indirectness

def indirectness(compat):
    if not compat:
        return _dom(None, "NOT_ASSESSABLE", "no PICO-compatibility object for this outcome", {})
    hard = [l for l in compat.get("limitations") or [] if isinstance(l, dict) and l.get("hard")]
    inputs = {"matched": compat.get("matched"), "mismatches": compat.get("mismatches"), "hard_limitations": hard,
              "dimension_matches": compat.get("dimension_matches"), "limitation_code": compat.get("limitation_code")}
    if compat.get("matched") is False or hard:
        what = ", ".join(sorted({str(l.get("dimension") or l.get("code")) for l in hard})) or "the compatibility object is unmatched"
        return _dom(1, "ASSESSED", f"hard PICO mismatch: {what}", inputs)
    soft = [d for d, ok in (compat.get("dimension_matches") or {}).items() if ok is False]
    # Conservative policy, including k=1: compat_check compares declared outcome
    # dimensions with extracted trial values, not just one trial with another.
    # Melatonin's declared ITT versus extracted completers therefore remains flagged.
    flags = ["SOFT_HETEROGENEITY_FOR_JUDGEMENT"] if soft else []
    return _dom(0, "ASSESSED", "no hard PICO mismatch" + (f"; unresolved compatibility dimensions (conservative policy): {', '.join(soft)}" if soft else ""),
                inputs, flags)


# ------------------------------------------------------------------------------------------------ imprecision

def ois(p0, rrr=0.25, alpha=0.05, power=0.80):
    """Total optimal information size, two equal arms, for a relative risk reduction rrr at control risk p0."""
    if p0 is None or not (0 < p0 < 1):
        return None
    p1 = p0 * (1 - rrr)
    za, zb = 1.959963984540054, 0.8416212335729143
    n = (za + zb) ** 2 * (p0 * (1 - p0) + p1 * (1 - p1)) / (p0 - p1) ** 2
    return 2 * math.ceil(n)


def imprecision(result, scale, counts=None):
    """counts: [{events_t, n_t, events_c, n_c}] structured arm counts of the pooled trials, or None."""
    lo, hi, est = _f(result.get("ci_low")), _f(result.get("ci_high")), _f(result.get("estimate"))
    null = _null(scale)
    inputs = {"ci": [lo, hi], "estimate": est, "scale": scale}
    if lo is None or hi is None or result.get("pooled_ci_refused") or result.get("pool_refused"):
        return _dom(None, "NOT_ASSESSABLE", "no pooled confidence interval", inputs)
    if scale in RATIO and lo <= 0.75 and hi >= 1.25:
        return _dom(2, "ASSESSED", f"the 95% CI {lo:.2f} to {hi:.2f} includes both appreciable benefit (0.75) and harm "
                                   f"(1.25) -- GRADE default thresholds", inputs)
    if lo < null < hi:
        return _dom(1, "ASSESSED", f"the 95% CI {lo:.4g} to {hi:.4g} crosses the null ({null:g})", inputs)
    if counts:
        ec = sum(c["events_c"] for c in counts)
        nc = sum(c["n_c"] for c in counts)
        n = sum(c["n_t"] + c["n_c"] for c in counts)
        need = ois(ec / nc if nc else None)
        inputs.update({"total_n": n, "control_risk": round(ec / nc, 4) if nc else None, "ois": need})
        if need and n < need:
            return _dom(1, "ASSESSED", f"total sample {n} is below the optimal information size {need} "
                                       f"(control risk {ec / nc:.3f}, RRR 25%, alpha 0.05, power 0.80)", inputs)
        return _dom(0, "ASSESSED", f"CI excludes the null and total sample {n} meets the OIS {need}", inputs)
    inputs["ois"] = "NOT_COMPUTABLE: no structured arm counts"
    return _dom(0, "PARTIAL", "the CI excludes the null; the optimal information size is not computable (no structured "
                              "arm counts)", inputs, ["OIS_NOT_COMPUTABLE"])


# ------------------------------------------------------------------------------------------------ publication bias

def _tdist_two_sided_p(t, df):
    """Two-sided p for Student's t (regularised incomplete beta via continued fraction; no scipy needed)."""
    x = df / (df + t * t)
    a, b = df / 2.0, 0.5

    def betacf(a, b, x):
        qab, qap, qam = a + b, a + 1, a - 1
        c, d = 1.0, 1 - qab * x / qap
        d = 1 / d if abs(d) > 1e-300 else 1e300
        h = d
        for m in range(1, 300):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1 + aa * d
            d = 1 / d if abs(d) > 1e-300 else 1e300
            c = 1 + aa / c if abs(c) > 1e-300 else 1e300
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1 + aa * d
            d = 1 / d if abs(d) > 1e-300 else 1e300
            c = 1 + aa / c if abs(c) > 1e-300 else 1e300
            de = d * c
            h *= de
            if abs(de - 1) < 1e-12:
                break
        return h
    lbeta = math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)
    bt = math.exp(a * math.log(x) + b * math.log(1 - x) - lbeta) if 0 < x < 1 else 0.0
    ib = bt * betacf(a, b, x) / a if x < (a + 1) / (a + b + 2) else 1 - bt * betacf(b, a, 1 - x) / b
    return min(1.0, max(0.0, ib))


def egger(trials, scale):
    """Egger's regression: z_i = y_i/se_i on precision 1/se_i; the intercept tests asymmetry (t, k-2 df)."""
    pts = []
    for t in trials:
        e, se = _f(t.get("effect")), _f(t.get("se"))
        if e is None or not se:
            continue
        y = math.log(e) if scale in RATIO else e
        if scale in RATIO and e <= 0:
            continue
        pts.append((1 / se, y / se))
    k = len(pts)
    if k < 3:
        return None
    mx = sum(x for x, _ in pts) / k
    my = sum(y for _, y in pts) / k
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    slope = sum((x - mx) * (y - my) for x, y in pts) / sxx
    icpt = my - slope * mx
    rss = sum((y - (icpt + slope * x)) ** 2 for x, y in pts)
    s2 = rss / (k - 2)
    se_i = math.sqrt(s2 * (1 / k + mx * mx / sxx))
    t = icpt / se_i if se_i > 0 else float("inf")
    return {"k": k, "intercept": round(icpt, 4), "se": round(se_i, 4), "t": round(t, 3),
            "p": round(_tdist_two_sided_p(t, k - 2), 4)}


def publication_bias(trials, scale):
    k = len(trials)
    if k < 10:
        return _dom(0, "NOT_ASSESSABLE_K_LT_10", f"k = {k} < 10: small-study tests have too little power", {"k": k})
    e = egger(trials, scale)
    if e is None:
        return _dom(None, "NOT_ASSESSABLE", "effects/standard errors not available for the test", {"k": k})
    if e["p"] < 0.10:
        return _dom(1, "ASSESSED", f"Egger's test p = {e['p']} < 0.10 (intercept {e['intercept']})", {"egger": e})
    return _dom(0, "ASSESSED", f"Egger's test p = {e['p']} >= 0.10", {"egger": e})


# ------------------------------------------------------------------------------------------------ certainty

def grade(outcome, rob, stale=False, counts=None):
    """outcome: the served outcome object (result, trials, compat_key); rob: {trial id: formal RoB 2 object}."""
    res = outcome.get("result") or {}
    scale = res.get("scale")
    trials = [{"id": t.get("id"), "effect": t.get("effect"), "ci_low": t.get("ci_low"), "ci_high": t.get("ci_high"),
               "se": (t.get("study_effect") or {}).get("standard_error")} for t in outcome.get("trials") or []]
    doms = {"risk_of_bias": risk_of_bias(trials, rob, res.get("tau2")),
            "inconsistency": inconsistency(res, trials, scale, stale=stale),
            "indirectness": indirectness(outcome.get("compat_key")),
            "imprecision": imprecision(res, scale, counts),
            "publication_bias": publication_bias(trials, scale)}
    down = sum(d["downgrade"] or 0 for d in doms.values())
    unassessed = sorted(n for n, d in doms.items() if d["state"] == "NOT_ASSESSABLE")
    level = LEVELS[max(0, 3 - down)]
    pb_k = doms["publication_bias"]["state"] == "NOT_ASSESSABLE_K_LT_10"
    flags = sorted({f for d in doms.values() for f in d["flags"]})
    provisional = bool(unassessed or flags or any(d["state"] == "PARTIAL" for d in doms.values()))
    return {"family": FAMILY, "outcome": outcome.get("name"), "start": "high", "domains": doms, "downgrades": down,
            "unassessed_domains": unassessed, "judgement_flags": flags,
            "certainty": "provisional" if provisional else level,
            # NOT a forecast: unassessed domains count 0 here (probiotics I^2 73% read 'high' under the old name)
            "certainty_from_assessed_domains_only": level,
            "certainty_if_pubbias_k_lt_10_counts_as_undetected": level if pb_k else None}
