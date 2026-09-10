"""Synthesis engine (declared method).

Binary outcomes pooled on log(RR):
  * per-study yi = log RR, vi = 1/a - 1/n1 + 1/c - 1/n2
    0.5 continuity correction applied to ALL FOUR cells of a study ONLY when that
    study has a zero cell (unconditional correction biases OR/RR toward 1).
  * Paule-Mandel random-effects tau^2 (moment estimator; no DL, which is forbidden
    for k<10).
  * HKSJ confidence interval on t_{k-1}, with the variance-inflation factor floored
    at max(1, Q_gen/(k-1)) so HKSJ cannot narrow the CI below the RE model.
  * Prediction interval mu +/- t_{k-1} * sqrt(tau2 + se^2), matching metafor's
    predict() under test="knha".

Validated against metafor 5.0.1 by scripts/validate_synth.py (dataset dat.bcg):
tau2, mu, se, CI and PI all agree to < 1e-6. Do not change formulas without re-running
that validation.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Sequence

from scipy.stats import t as _t


@dataclass
class Study:
    label: str
    ai: float  # events, treatment
    n1i: float  # n, treatment
    ci: float  # events, control
    n2i: float  # n, control


@dataclass
class PoolResult:
    scale: str
    k: int
    tau2: float
    mu_log: float
    se_log: float
    ci_low: float
    ci_high: float
    pi_low: float
    pi_high: float
    Q: float
    estimate: float  # back-transformed (RR)


def _effects(studies: Sequence[Study]):
    yi, vi = [], []
    for s in studies:
        a, n1, c, n2 = s.ai, s.n1i, s.ci, s.n2i
        if min(a, c, n1 - a, n2 - c) == 0:  # a zero cell in this study
            a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1.0, n2 + 1.0
        y = math.log((a / n1) / (c / n2))
        v = 1.0 / a - 1.0 / n1 + 1.0 / c - 1.0 / n2
        yi.append(y)
        vi.append(v)
    return yi, vi


def _wmean(yi, vi, tau2):
    w = [1.0 / (v + tau2) for v in vi]
    sw = sum(w)
    mu = sum(wi * y for wi, y in zip(w, yi)) / sw
    return mu, w, sw


def _paule_mandel_tau2(yi, vi, tol=1e-10, max_iter=200):
    """Solve F(tau2)=sum w_i (yi-mu)^2 - (k-1) = 0, w_i=1/(vi+tau2). tau2 >= 0."""
    k = len(yi)
    if k < 2:
        return 0.0
    target = k - 1

    def F(tau2):
        mu, w, _ = _wmean(yi, vi, tau2)
        return sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi)) - target

    # At tau2=0, if F<=0 there is no positive root -> tau2=0.
    if F(0.0) <= 0:
        return 0.0
    lo, hi = 0.0, 1.0
    while F(hi) > 0 and hi < 1e6:
        hi *= 2.0
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        fm = F(mid)
        if abs(fm) < tol:
            return mid
        if fm > 0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def pool_rr(studies: Sequence[Study], alpha: float = 0.05) -> PoolResult:
    yi, vi = _effects(studies)
    k = len(yi)
    tau2 = _paule_mandel_tau2(yi, vi)
    mu, w, sw = _wmean(yi, vi, tau2)
    se_re = math.sqrt(1.0 / sw)

    # generalized Q at the RE weights (used both for HKSJ factor and reported Q at tau2=0)
    Q_gen = sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi))
    # HKSJ: inflate se by sqrt(Q_gen/(k-1)), floored at 1 so it cannot narrow below RE.
    factor = max(1.0, Q_gen / (k - 1)) if k > 1 else 1.0
    se_hksj = se_re * math.sqrt(factor)

    tcrit = _t.ppf(1 - alpha / 2, df=k - 1) if k > 1 else float("nan")
    ci_low = mu - tcrit * se_hksj
    ci_high = mu + tcrit * se_hksj
    # PI uses the model se (knha se == se_hksj) and adds tau2, on t_{k-1}.
    pi_half = tcrit * math.sqrt(tau2 + se_hksj ** 2)
    pi_low = mu - pi_half
    pi_high = mu + pi_half

    # Fixed-effect Q for reporting (tau2=0 weights).
    mu0, w0, _ = _wmean(yi, vi, 0.0)
    Q = sum(wi * (y - mu0) ** 2 for wi, y in zip(w0, yi))

    return PoolResult(
        scale="RR", k=k, tau2=tau2, mu_log=mu, se_log=se_hksj,
        ci_low=math.exp(ci_low), ci_high=math.exp(ci_high),
        pi_low=math.exp(pi_low), pi_high=math.exp(pi_high),
        Q=Q, estimate=math.exp(mu),
    )
