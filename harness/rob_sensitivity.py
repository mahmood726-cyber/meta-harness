"""RoB-stratified sensitivity re-pool of a review's PRIMARY outcome (Stage RISK OF BIAS, plan R2).

Operates on the finished review dict (outcomes + rob2 attached) and re-pools the primary outcome with the
SAME validated pooler (harness.synth.pool) restricted by risk-of-bias stratum:
  drop_high : exclude overall == 'high' (the standard RoB sensitivity)
  low_only  : keep only overall == 'low'  (strict)
An UNRATED pooled trial cannot be placed in a stratum, so it is excluded from low_only and disclosed via
n_rob_rated. The Study construction and pooled-scale selection are identical to harness.pipeline, and a
test asserts the 'full' re-pool reproduces the shipped primary result (so this cannot drift from it)."""
from __future__ import annotations

from .synth import Study, pool


def _norm(overall):
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


def _studies_and_scale(trials, declared_estimand):
    """Identical to harness.pipeline: Study build + pooled_scale selection."""
    meas = declared_estimand if declared_estimand in ("RR", "OR") else "RR"

    def _meas(t):
        if t.get("e1i") is not None:
            return "IRR"
        if t.get("mean1") is not None:
            return "MD"
        return meas

    studies = [Study(label=t["label"], ai=t.get("ai"), n1i=t.get("n1i"), ci=t.get("ci"),
                     n2i=t.get("n2i"), effect=t.get("effect"), ci_low=t.get("ci_low"),
                     ci_high=t.get("ci_high"), e1i=t.get("e1i"), t1i=t.get("t1i"),
                     e2i=t.get("e2i"), t2i=t.get("t2i"), mean1=t.get("mean1"), sd1=t.get("sd1"),
                     nc1=t.get("nc1"), mean2=t.get("mean2"), sd2=t.get("sd2"), nc2=t.get("nc2"),
                     source=t.get("source", ""), measure=_meas(t)) for t in trials]
    if trials and all(t.get("e1i") is not None for t in trials):
        scale = "IRR"
    elif trials and all(t.get("mean1") is not None for t in trials):
        scale = "MD"
    elif trials and all(t.get("scale") for t in trials) and len({t["scale"] for t in trials}) == 1:
        scale = trials[0]["scale"]
    else:
        scale = declared_estimand or "RR"
    return studies, scale


def _pool(trials, declared_estimand):
    if not trials:
        return None
    studies, scale = _studies_and_scale(trials, declared_estimand)
    r = pool(studies, scale=scale)
    return {"k": r.k, "estimate": round(r.estimate, 4), "scale": r.scale,
            "ci_low": round(r.ci_low, 4), "ci_high": round(r.ci_high, 4), "tau2": round(r.tau2, 5)}


def sensitivity(review):
    """Return the primary-outcome RoB-stratified sensitivity, or None if not applicable."""
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    if not prim or not prim.get("trials"):
        return None
    trials = prim["trials"]
    estimand = prim.get("estimand", "RR")
    rob = (review.get("rob2") or {}).get("trials") or {}

    def _lvl(t):
        return _norm((rob.get(str(t.get("label"))) or {}).get("overall"))

    levels = {str(t.get("label")): _lvl(t) for t in trials}
    n_rated = sum(1 for v in levels.values() if v)
    full = _pool(trials, estimand)
    drop_high = _pool([t for t in trials if _lvl(t) != "high"], estimand)
    low_only = _pool([t for t in trials if _lvl(t) == "low"], estimand)
    out = {"outcome": prim["name"], "estimand": estimand, "levels": levels,
           "n_trials": len(trials), "n_rob_rated": n_rated, "rob_covered": n_rated == len(trials),
           "any_high": any(v == "high" for v in levels.values()),
           "full": full, "drop_high": drop_high, "low_only": low_only,
           "drop_high_informative": bool(drop_high and full and drop_high["k"] < full["k"] and drop_high["k"] >= 1),
           "low_only_informative": bool(low_only and full and low_only["k"] < full["k"] and low_only["k"] >= 1)}
    return out
