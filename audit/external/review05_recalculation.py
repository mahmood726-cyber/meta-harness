"""Review 5 independent arithmetic checks, not an offline harness replay.
Pinned repo: mahmood726-cyber/meta-harness @ 0730234d0b4f
Review SHA256: 49c4017dffdff19bdef08fcee0ac850e869a8e587771c19b17cb8a1872a2d10c

Inputs are the published rounded effect estimates in the pinned review.
This checks pooling arithmetic, NOT search completeness or source authenticity.
Requirements: Python 3.10+, numpy, scipy
Run: python doac_vte_review5_recalculation.py
"""
from __future__ import annotations
import json
import math
from dataclasses import dataclass
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm, t

@dataclass(frozen=True)
class Trial:
    name: str
    pmid: str
    measure: str
    effect: float
    lower: float
    upper: float

TRIALS = (
    Trial("RE-COVER", "19966341", "HR", 1.10, 0.65, 1.84),
    Trial("RE-COVER II", "24344086", "HR", 1.08, 0.64, 1.80),
    Trial("EINSTEIN-DVT", "21128814", "HR", 0.68, 0.44, 1.04),
    Trial("EINSTEIN-PE", "22449293", "HR", 1.12, 0.75, 1.68),
    Trial("Hokusai-VTE", "23991658", "HR", 0.89, 0.70, 1.13),
    Trial("AMPLIFY", "23808982", "RR", 0.84, 0.60, 1.18),
)

def pool(trials: tuple[Trial, ...]) -> dict:
    """Paule-Mandel tau2; modified HKSJ using max(1,Q/(k-1))."""
    if len(trials) < 2:
        raise ValueError("This pooling check requires at least two trials.")
    for trial in trials:
        if not (0 < trial.lower < trial.effect < trial.upper):
            raise ValueError(f"Invalid effect or interval for {trial.name}")
    y = np.log([x.effect for x in trials])
    v = ((np.log([x.upper for x in trials])
          - np.log([x.lower for x in trials])) / (2 * norm.ppf(0.975))) ** 2
    df = len(trials) - 1

    def q(tau2: float) -> float:
        weights = 1 / (v + tau2)
        mean = np.sum(weights * y) / np.sum(weights)
        return float(np.sum(weights * (y - mean)**2))

    q0 = q(0.0)
    if q0 <= df:
        tau2 = 0.0
    else:
        upper = max(1.0, float(np.var(y)))
        while q(upper) > df:
            upper *= 2
            if upper > 1e12:
                raise RuntimeError("Could not bracket the Paule-Mandel solution.")
        tau2 = float(brentq(lambda z: q(z) - df, 0.0, upper))
    weights = 1 / (v + tau2)
    mean = float(np.sum(weights * y) / np.sum(weights))
    variance_factor = max(1.0, q(tau2) / df)
    se = math.sqrt(variance_factor / np.sum(weights))
    critical = t.ppf(0.975, df)
    return {
        "k": len(trials),
        "measures": sorted(set(x.measure for x in trials)),
        "estimate": math.exp(mean),
        "ci_low": math.exp(mean - critical * se),
        "ci_high": math.exp(mean + critical * se),
        "tau_squared": tau2,
        "Q_at_zero": q0,
        "I_squared_percent": max(0.0, (q0-df)/q0)*100 if q0 else 0.0,
        "method": "PM + modified HKSJ, variance floor 1, t(k-1)",
    }

def matching_or_check() -> dict:
    """Recompute four-trial G1 comparator check using its count inputs.
    This normal-based interval is NOT the primary six-trial HKSJ interval.
    """
    counts = (
        (30, 1274, 27, 1265),  # RE-COVER
        (59, 2609, 71, 2635),  # AMPLIFY
        (130, 4118, 146, 4122), # Hokusai-VTE
        (30, 1279, 28, 1289),  # RE-COVER II
    )
    y, v = [], []
    for a, n1, c, n0 in counts:
        b, d = n1-a, n0-c
        if min(a,b,c,d) <= 0:
            raise ValueError("This check expects nonzero count cells.")
        y.append(math.log(a*d/(b*c)))
        v.append(1/a + 1/b + 1/c + 1/d)
    y, v = np.array(y), np.array(v)
    w = 1/v
    mean = float(np.sum(w*y)/np.sum(w))
    se = math.sqrt(1/np.sum(w))
    q = float(np.sum(w*(y-mean)**2))
    if q > len(y)-1:
        raise ValueError("Nonzero heterogeneity: simple matching check not applicable.")
    return {
        "k": 4, "measure": "OR",
        "estimate": math.exp(mean),
        "ci_low": math.exp(mean-norm.ppf(0.975)*se),
        "ci_high": math.exp(mean+norm.ppf(0.975)*se),
        "method": "Inverse variance, tau2=0, normal 95% interval",
    }

def main() -> None:
    results = {
        "commit": "0730234d0b4f",
        "review_sha256": "49c4017dffdff19bdef08fcee0ac850e869a8e587771c19b17cb8a1872a2d10c",
        "mixed_primary": pool(TRIALS),
        "hr_only_sensitivity": pool(tuple(x for x in TRIALS if x.measure=="HR")),
        "g1_four_trial_counts_check": matching_or_check(),
        "scope": "Independent arithmetic only; not source admission or full replay.",
    }
    primary = results["mixed_primary"]
    assert abs(primary["estimate"] - 0.9091) < 0.0001
    assert abs(primary["ci_low"] - 0.7479) < 0.0001
    assert abs(primary["ci_high"] - 1.1050) < 0.0001
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
