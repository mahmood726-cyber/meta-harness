"""Synthesis engine (declared method).

Binary outcomes pooled on log(RR) by inverse-variance random effects:
  * A study contributes a per-study effect (yi = log RR) and variance (vi) built
    EITHER from a 2x2 table OR from a published effect + 95% CI. A trial that
    reports only an estimate is therefore poolable and is NOT dropped.
  * From a 2x2: yi = log((a/n1)/(c/n2)), vi = 1/a - 1/n1 + 1/c - 1/n2, with a 0.5
    continuity correction to all four cells ONLY when that study has a zero cell.
  * From effect+CI (ratio scale): yi = log(point), vi = ((log(hi)-log(lo))/(2*z))^2.
  * Paule-Mandel random-effects tau^2 (no DerSimonian-Laird, forbidden for k<10).
  * HKSJ confidence interval on t_{k-1}, variance-inflation floored at max(1, Q/(k-1)).
  * Prediction interval mu +/- t_{k-1} * sqrt(tau2 + se^2).

The 2x2 path is validated against metafor 5.0.1 (rma PM+knha + predict) on dat.bcg
to < 1e-6 by scripts/validate_synth.py. Do not change formulas without re-validating.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

from scipy.stats import norm as _norm, t as _t


@dataclass
class Study:
    """A poolable study. Provide EITHER a 2x2 (ai,n1i,ci,n2i) OR an effect+CI.
    measure selects the 2x2 log-effect: 'RR' (risk ratio) or 'OR' (odds ratio)."""
    label: str
    ai: Optional[float] = None
    n1i: Optional[float] = None
    ci: Optional[float] = None
    n2i: Optional[float] = None
    effect: Optional[float] = None      # point estimate on ratio scale (RR/OR/HR/IRR)
    ci_low: Optional[float] = None
    ci_high: Optional[float] = None
    # Rate data (recurrent-event / incidence): events + person-time per arm -> log rate ratio.
    e1i: Optional[float] = None         # intervention events
    t1i: Optional[float] = None         # intervention person-time
    e2i: Optional[float] = None         # comparator events
    t2i: Optional[float] = None         # comparator person-time
    # Continuous data: mean/SD/n per arm -> mean difference (raw scale).
    mean1: Optional[float] = None
    sd1: Optional[float] = None
    nc1: Optional[float] = None
    mean2: Optional[float] = None
    sd2: Optional[float] = None
    nc2: Optional[float] = None
    source: str = ""
    measure: str = "RR"

    def yi_vi(self) -> tuple[float, float]:
        # Mean difference from means/SDs/n per arm: yi = mean1 - mean2, vi = sd1^2/n1 + sd2^2/n2
        # (raw scale; pool() back-transforms with identity for scale MD). Standard continuous
        # meta-analysis (matches metafor measure='MD').
        if self.mean1 is not None and self.sd1 is not None and self.nc1 and self.mean2 is not None:
            y = self.mean1 - self.mean2
            v = (self.sd1 ** 2) / self.nc1 + (self.sd2 ** 2) / self.nc2
            return y, v
        # Rate ratio (IRR) from events + person-time: yi = log((e1/t1)/(e2/t2)),
        # vi = 1/e1 + 1/e2 (person-time is an offset, not a source of variance). Standard
        # incidence-rate meta-analysis (matches metafor measure='IRR'). 0.5 correction on a
        # zero event count only.
        if self.e1i is not None and self.t1i and self.e2i is not None and self.t2i:
            e1, e2 = self.e1i, self.e2i
            if min(e1, e2) == 0:
                e1, e2 = e1 + 0.5, e2 + 0.5
            y = math.log((e1 / self.t1i) / (e2 / self.t2i))
            v = 1.0 / e1 + 1.0 / e2
            return y, v
        if self.ai is not None:
            a, n1, c, n2 = self.ai, self.n1i, self.ci, self.n2i
            if min(a, c, n1 - a, n2 - c) == 0:  # zero cell in THIS study
                a, c, n1, n2 = a + 0.5, c + 0.5, n1 + 1.0, n2 + 1.0
            if self.measure.upper() == "OR":
                b, d = n1 - a, n2 - c          # odds ratio (a*d)/(b*c)
                y = math.log((a * d) / (b * c))
                v = 1.0 / a + 1.0 / b + 1.0 / c + 1.0 / d
            else:                               # risk ratio
                y = math.log((a / n1) / (c / n2))
                v = 1.0 / a - 1.0 / n1 + 1.0 / c - 1.0 / n2
            return y, v
        if self.effect is not None and self.ci_low and self.ci_high:
            z = _norm.ppf(0.975)
            y = math.log(self.effect)
            se = (math.log(self.ci_high) - math.log(self.ci_low)) / (2 * z)
            return y, se * se
        raise ValueError(f"study {self.label!r} has neither a 2x2 nor an effect+CI")


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
    estimate: float
    per_study: list = field(default_factory=list)  # [(label, yi, vi)]
    # Common-effect (fixed-effect, z-based) sensitivity. At k<=2 the HKSJ t multiplier is huge
    # (t_{k-1}=12.71 at k=2, 1 df) and can render a CI "compatible with no effect" even when both
    # trials agree with I^2=0; an external audit asked that the conventional CI be shown alongside so
    # the primary interval is not over-read. Always computed; the page shows it for k<=2.
    ci_low_fixed: float = None
    ci_high_fixed: float = None
    estimate_fixed: float = None


def _wmean(yi, vi, tau2):
    w = [1.0 / (v + tau2) for v in vi]
    sw = sum(w)
    mu = sum(wi * y for wi, y in zip(w, yi)) / sw
    return mu, w, sw


def _paule_mandel_tau2(yi, vi, tol=1e-10, max_iter=200):
    k = len(yi)
    if k < 2:
        return 0.0
    target = k - 1

    def F(tau2):
        mu, w, _ = _wmean(yi, vi, tau2)
        return sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi)) - target

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


def pool(studies: Sequence[Study], scale: str = "RR", alpha: float = 0.05) -> PoolResult:
    yv = [s.yi_vi() for s in studies]
    yi = [y for y, _ in yv]
    vi = [v for _, v in yv]
    k = len(yi)
    if k == 0:
        raise ValueError("no studies to pool")
    tau2 = _paule_mandel_tau2(yi, vi)
    mu, w, sw = _wmean(yi, vi, tau2)
    se_re = math.sqrt(1.0 / sw)
    if k > 1:
        Q_gen = sum(wi * (y - mu) ** 2 for wi, y in zip(w, yi))
        factor = max(1.0, Q_gen / (k - 1))
        se = se_re * math.sqrt(factor)
        tcrit = _t.ppf(1 - alpha / 2, df=k - 1)
    else:
        se = se_re
        tcrit = _norm.ppf(1 - alpha / 2)  # k=1: no between-study term; z fallback
    ci_low, ci_high = mu - tcrit * se, mu + tcrit * se
    pi_half = tcrit * math.sqrt(tau2 + se ** 2)
    mu0, w0, sw0 = _wmean(yi, vi, 0.0)
    Q = sum(wi * (y - mu0) ** 2 for wi, y in zip(w0, yi))
    # Common-effect (fixed-effect) z-based CI: the conventional small-k sensitivity shown alongside HKSJ.
    se_fixed = math.sqrt(1.0 / sw0)
    zc = _norm.ppf(1 - alpha / 2)
    ci_low_fixed, ci_high_fixed = mu0 - zc * se_fixed, mu0 + zc * se_fixed
    # Ratio scales (RR/OR/HR/IRR) pool on the log scale and back-transform with exp; additive
    # scales (mean difference / standardised mean difference) pool on the raw scale (identity).
    bt = (lambda x: x) if scale.upper() in ("MD", "SMD") else math.exp
    return PoolResult(
        scale=scale, k=k, tau2=tau2, mu_log=mu, se_log=se,
        ci_low=bt(ci_low), ci_high=bt(ci_high),
        pi_low=bt(mu - pi_half), pi_high=bt(mu + pi_half),
        Q=Q, estimate=bt(mu),
        per_study=[(s.label, y, v) for s, (y, v) in zip(studies, yv)],
        ci_low_fixed=bt(ci_low_fixed), ci_high_fixed=bt(ci_high_fixed), estimate_fixed=bt(mu0),
    )


# Back-compat: pool_rr(list-of-Study) used by the metafor validation script.
def pool_rr(studies: Sequence[Study], alpha: float = 0.05) -> PoolResult:
    return pool(studies, scale="RR", alpha=alpha)


def _effects(studies):  # kept for the existing unit test
    yv = [s.yi_vi() for s in studies]
    return [y for y, _ in yv], [v for _, v in yv]
