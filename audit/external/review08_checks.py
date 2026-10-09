#!/usr/bin/env python3
"""Independent arithmetic and passage-digest audit of meta-harness review 8.

Requires numpy and scipy. Run:
    python esketamine_review8_checks.py --output esketamine_review8_checks.json

This is NOT a full harness replay, source-acquisition verification, risk-of-bias
assessment, or a recommended replacement clinical meta-analysis. It reproduces
the pinned observed-case, day-28 raw MADRS analysis and probes its sensitivity.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, asdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm, t

COMMIT = "0730234d0b4f"
REVIEW_SHA256 = "3a611e84724be5d575bb7f6d01608f50ba73e73482e4379d3664e68b284f9fc4"
SOURCE_BASE = f"https://github.com/mahmood726-cyber/meta-harness/blob/{COMMIT}/"

@dataclass(frozen=True)
class Trial:
    label: str
    mean_t: float
    sd_t: float
    n_t: int
    mean_c: float
    sd_c: float
    n_c: int

    def validate(self) -> None:
        if self.n_t < 2 or self.n_c < 2:
            raise ValueError(f"{self.label}: each arm must have at least two observations")
        if not all(math.isfinite(x) for x in
                   (self.mean_t, self.sd_t, self.mean_c, self.sd_c)):
            raise ValueError(f"{self.label}: non-finite input")
        if self.sd_t <= 0 or self.sd_c <= 0:
            raise ValueError(f"{self.label}: SDs must be positive")

    @property
    def difference(self) -> float:
        return self.mean_t - self.mean_c

    @property
    def variance(self) -> float:
        return self.sd_t**2 / self.n_t + self.sd_c**2 / self.n_c


def combine_independent_arms(
    n1: int, mean1: float, sd1: float, n2: int, mean2: float, sd2: float
) -> tuple[int, float, float]:
    """Combine independent active arms; the shared placebo is NOT duplicated."""
    if min(n1, n2) < 2 or min(sd1, sd2) <= 0:
        raise ValueError("Invalid arm input")
    n = n1 + n2
    mean = (n1 * mean1 + n2 * mean2) / n
    ss = (n1-1)*sd1**2 + (n2-1)*sd2**2
    ss += n1*n2/n * (mean1-mean2)**2
    return n, mean, math.sqrt(ss/(n-1))


def pool(trials: list[Trial]) -> dict:
    """Paule-Mandel tau^2; modified HKSJ variance floor; t_(k-1) 95% CI."""
    if len(trials) < 2:
        raise ValueError("This function requires at least two trials")
    for trial in trials:
        trial.validate()
    y = np.asarray([trial.difference for trial in trials], dtype=float)
    v = np.asarray([trial.variance for trial in trials], dtype=float)
    k = len(trials)
    df = k - 1

    def residual_q(tau2: float) -> float:
        w = 1.0 / (v + tau2)
        mu = float(np.sum(w*y)/np.sum(w))
        return float(np.sum(w*(y-mu)**2))

    q0 = residual_q(0.0)
    tau2 = 0.0
    if q0 > df:
        upper = float(np.max(v))
        while residual_q(upper) > df:
            upper *= 2.0
            if not math.isfinite(upper):
                raise ArithmeticError("Failed to bracket Paule-Mandel root")
        tau2 = float(brentq(lambda x: residual_q(x)-df, 0.0, upper))
    w = 1.0/(v+tau2)
    mu = float(np.sum(w*y)/np.sum(w))
    h = max(1.0, residual_q(tau2)/df)
    se = math.sqrt(h/float(np.sum(w)))
    tc = float(t.ppf(0.975, df))
    zc = float(norm.ppf(0.975))
    ci = [mu-tc*se, mu+tc*se]
    return {
        "k": k, "mean_difference": mu, "hksj_95_ci": ci,
        "crosses_zero": ci[0] < 0.0 < ci[1],
        "tau2": tau2, "Q_common_effect": q0,
        "I2_percent": 100.0*max(0.0, (q0-df)/q0) if q0 > 0 else 0.0,
        "hksj_variance_multiplier": h, "pooled_standard_error": se,
        "df": df, "t_critical": tc,
        "normal_95_ci_for_comparison_only": [mu-zc*se, mu+zc*se],
        "weights": {trial.label: float(wi/np.sum(w))
                    for trial, wi in zip(trials, w)}
    }


PASSAGES = [
    {
        "trial": "Chen 2023",
        "text": "ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery Asberg Depression Rating Scale (MAD' mean -10.1 (SD 10.8, n=109) [Intranasal Esketamine ] vs -8.1 (SD 10.26, n=106) [Intranasal Placebo + O] Units on a Scale — population: Full analysis set included all randomized participants who received a least 1 do",
        "expected": "1aac931b58c3ec8416cb09eaa70162e4e14b2b129ba3ca8d34ee1c0a234648fb"
    },
    {
        "trial": "TRANSFORM-2",
        "text": "ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery-Asberg Depression Rating Scale (MAD' mean -21.4 (SD 12.32, n=101) [Intranasal Esketamine ] vs -17.0 (SD 13.88, n=100) [Intranasal Placebo Plu] Units on a scale — population: Full analysis set (FAS) defined as all randomized participants who received at l",
        "expected": "258176b18bfaad182e6de2a2712eee480c5357a3d318fceeb11e2820c6fac725"
    },
    {
        "trial": "TRANSFORM-3",
        "text": "ClinicalTrials.gov results (structured, continuous): outcome 'Change From Baseline in Montgomery Asberg Depression Rating Scale (MAD' mean -10.0 (SD 12.74, n=63) [Intranasal Esketamine ] vs -6.3 (SD 8.86, n=60) [Oral AD Plus Intranasa] Units on a scale — population: The full analysis set (FAS) was defined as all randomized participants who recei",
        "expected": "04980393316f3befb5799b94c75b73de59fb60fb9c3c1ec36ca2f9be5aa2e68f"
    }
]


def run_checks() -> dict:
    n, mean, sd = combine_independent_arms(111,-19.0,13.86,98,-18.8,14.12)
    trials = [
        Trial("Chen 2023",-10.1,10.8,109,-8.1,10.26,106),
        Trial("TRANSFORM-2",-21.4,12.32,101,-17.0,13.88,100),
        Trial("TRANSFORM-3",-10.0,12.74,63,-6.3,8.86,60),
        Trial("TRANSFORM-1 combined",mean,sd,n,-14.8,15.07,108)
    ]
    primary = pool(trials)
    assert abs(primary["mean_difference"] - (-3.3436)) < 5e-5
    assert abs(primary["hksj_95_ci"][0] - (-6.0691)) < 5e-5
    assert abs(primary["hksj_95_ci"][1] - (-0.6180)) < 5e-5
    loo = []
    for i, trial in enumerate(trials):
        result = pool(trials[:i]+trials[i+1:])
        assert result["crosses_zero"]
        loo.append({"dropped": trial.label, **result})
    digest_checks = []
    for item in PASSAGES:
        actual = hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
        matches = actual == item["expected"]
        assert matches
        digest_checks.append({**item, "actual": actual, "matches": matches})
    zc = float(norm.ppf(.975))
    individual = []
    for trial in trials:
        se = math.sqrt(trial.variance)
        individual.append({
            **asdict(trial), "mean_difference": trial.difference, "standard_error": se,
            "unadjusted_normal_95_ci": [trial.difference-zc*se,trial.difference+zc*se]
        })
    # Comparator tuples are from the pinned typed G1 ledger, not an independent
    # visual re-reading of the original figure. Printed bounds introduce rounding.
    comp_y = np.array([-4.10,-4.40,-3.70])
    comp_v = ((np.array([-1.97,-0.86,0.03])-np.array([-6.23,-7.94,-7.43]))/(2*zc))**2
    comp_w = 1.0/comp_v
    comp_mu = float(np.sum(comp_w*comp_y)/np.sum(comp_w))
    comp_se = math.sqrt(1.0/float(np.sum(comp_w)))
    rounded = trials[:-1]+[Trial("TRANSFORM-1 rounded",-18.91,13.95,209,-14.8,15.07,108)]
    return {
        "audit_date": "2026-10-09", "commit": COMMIT, "review_sha256": REVIEW_SHA256,
        "scope": "Independent arithmetic and user-supplied passage-hash checks only; no full harness replay or canonical review hash verification.",
        "sources": [
            SOURCE_BASE+"protocols/esketamine-trd-madrs.md",
            SOURCE_BASE+"cache/esketamine-trd-madrs/verified_arms.json",
            SOURCE_BASE+"outputs/k_gap/g1/esketamine-trd-madrs.json",
            "https://pubmed.ncbi.nlm.nih.gov/31290965/",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC6822141/"
        ],
        "transform1_combined": {"n":n,"mean":mean,"sd":sd},
        "individual_studies": individual, "primary": primary, "leave_one_out": loo,
        "primary_using_rounded_combined_arm": pool(rounded),
        "three_transform_trials_correct_observed_n": pool(trials[1:]),
        "typed_comparator_reconstructed_normal": {
            "mean_difference":comp_mu,
            "normal_95_ci":[comp_mu-zc*comp_se,comp_mu+zc*comp_se],
            "not_a_visual_verification_of_figure": True
        },
        "sampled_passage_hashes":digest_checks,
        "all_assertions_passed": True
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("esketamine_review8_checks.json"))
    args = parser.parse_args()
    results = run_checks()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps({
        "primary":results["primary"],
        "all_leave_one_out_intervals_cross_zero":all(x["crosses_zero"] for x in results["leave_one_out"]),
        "passage_hashes_matching":sum(x["matches"] for x in results["sampled_passage_hashes"]),
        "output":str(args.output), "all_assertions_passed":True
    },indent=2))

if __name__ == "__main__":
    main()
