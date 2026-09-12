"""Specification curve (Stage ANALYSIS, forward plan A3). For each primary outcome, re-pool under a small
set of DEFENSIBLE analytic specifications and report whether the estimate's direction and its significance
are stable across them. Reuses the exposed per-study (yi, vi) and tau^2 from the production pooler, so the
alternative specs are computed on the identical data and log/raw scale — no re-extraction.

Specifications (the axes that are computable without new data):
  RE_HKSJ  : random-effects Paule-Mandel with the Hartung-Knapp interval (the harness default).
  RE_z     : random-effects Paule-Mandel with a Wald/z interval (HKSJ off).
  FE       : fixed-effect (common-effect) inverse-variance.
Estimand variants are NOT included (they need alternative extractions); this curve is the model/interval
axis, rendered as a sensitivity panel — honestly bounded."""
from __future__ import annotations

import math

from .synth import pool
from .rob_sensitivity import _studies_and_scale

try:
    from scipy.stats import norm as _norm
    _z = _norm.ppf(0.975)
except Exception:  # pragma: no cover
    _z = 1.959963984540054


def _bt(scale):
    return (lambda x: x) if (scale or "").upper() in ("MD", "SMD") else math.exp


def _null(scale):
    return 0.0 if (scale or "").upper() in ("MD", "SMD") else 1.0


def _sig(est, lo, hi, scale):
    """Significant iff the interval excludes the null on the natural scale."""
    n = _null(scale)
    return not (lo <= n <= hi)


def spec_curve(review):
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None)
    if not prim or not prim.get("trials"):
        return None
    studies, scale = _studies_and_scale(prim["trials"], prim.get("estimand", "RR"))
    try:
        pr = pool(studies, scale=scale)
    except ValueError:
        return None
    if pr.k < 2:
        return {"k": pr.k, "not_applicable": "specification curve needs k>=2", "scale": pr.scale}
    yi = [y for _, y, _ in pr.per_study]
    vi = [v for _, _, v in pr.per_study]
    tau2 = pr.tau2
    bt = _bt(scale)
    specs = {}
    # RE + HKSJ = the production result
    specs["RE_HKSJ"] = {"estimate": round(pr.estimate, 4), "ci_low": round(pr.ci_low, 4),
                        "ci_high": round(pr.ci_high, 4)}
    # RE + z (HKSJ off): random-effects weights, Wald interval
    wR = [1.0 / (v + tau2) for v in vi]
    muR = sum(w * y for w, y in zip(wR, yi)) / sum(wR)
    seR = math.sqrt(1.0 / sum(wR))
    specs["RE_z"] = {"estimate": round(bt(muR), 4), "ci_low": round(bt(muR - _z * seR), 4),
                     "ci_high": round(bt(muR + _z * seR), 4)}
    # FE (common-effect): inverse-variance, tau^2 = 0
    wF = [1.0 / v for v in vi]
    muF = sum(w * y for w, y in zip(wF, yi)) / sum(wF)
    seF = math.sqrt(1.0 / sum(wF))
    specs["FE"] = {"estimate": round(bt(muF), 4), "ci_low": round(bt(muF - _z * seF), 4),
                   "ci_high": round(bt(muF + _z * seF), 4)}
    ests = [s["estimate"] for s in specs.values()]
    null = _null(scale)
    same_side = all((e - null) > 0 for e in ests) or all((e - null) < 0 for e in ests)
    sigs = {name: _sig(s["estimate"], s["ci_low"], s["ci_high"], scale) for name, s in specs.items()}
    return {"k": pr.k, "scale": pr.scale, "specs": specs,
            "direction_stable": bool(same_side),
            "significance_stable": len(set(sigs.values())) == 1,
            "significance_by_spec": sigs,
            "estimate_range": [round(min(ests), 4), round(max(ests), 4)]}
