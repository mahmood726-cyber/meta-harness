#!/usr/bin/env python3
"""Independent arithmetic and displayed-passage checks for Meta-harness review 6.

This does NOT run or certify the Meta-harness pipeline, current deployment,
source completeness, or clinical eligibility. Restored-data scenarios are
illustrations, not admitted replacement review results.

Requires Python 3.10+, numpy and scipy:
    python -m pip install numpy scipy
    python dpp4_review6_checks.py
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import math
import numpy as np
from scipy.optimize import brentq
from scipy.stats import norm, t

COMMIT = "0730234d0b4f"
REVIEW_SHA256 = "9dc26d08dc031cffe1756ae00c2c06f198669ebac0dc2270879673918e89c1e3"

@dataclass(frozen=True)
class Effect:
    trial: str
    estimate: float
    lower: float
    upper: float
    source: str

    def validate(self) -> None:
        values = (self.estimate, self.lower, self.upper)
        if not all(math.isfinite(x) and x > 0 for x in values):
            raise ValueError(f"Nonpositive or nonfinite ratio: {self.trial}")
        if not self.lower <= self.estimate <= self.upper or self.lower == self.upper:
            raise ValueError(f"Invalid interval: {self.trial}")

def pool(effects: list[Effect]) -> dict:
    """Paule-Mandel tau^2; HKSJ t(k-1), variance scale floored at 1."""
    if len(effects) < 2:
        raise ValueError("This independent implementation needs at least two trials.")
    for effect in effects:
        effect.validate()
    k = len(effects)
    y = np.log([e.estimate for e in effects])
    v = np.square(
        (np.log([e.upper for e in effects]) - np.log([e.lower for e in effects]))
        / (2.0 * norm.ppf(0.975))
    )

    def q(tau2: float) -> float:
        w = 1.0 / (v + tau2)
        mu = float(np.dot(w, y) / w.sum())
        return float(np.dot(w, (y - mu) ** 2))

    q0 = q(0.0)
    tau2 = 0.0
    if q0 > k - 1:
        upper = 0.01
        for _ in range(100):
            if q(upper) <= k - 1:
                break
            upper *= 2
        else:
            raise RuntimeError("Unable to bracket the PM root.")
        tau2 = float(brentq(lambda z: q(z) - (k - 1), 0, upper, xtol=1e-14))

    w = 1.0 / (v + tau2)
    mu = float(np.dot(w, y) / w.sum())
    hk_scale = max(1.0, q(tau2) / (k - 1))
    sem = math.sqrt(hk_scale / w.sum())
    delta = float(t.ppf(0.975, k - 1) * sem)
    # The raw mathematical interval exists at k=2. The audited review's
    # separate K2_SINGLE_DF publication rule withholds it.
    return {
        "trials": [e.trial for e in effects],
        "k": k,
        "estimate": math.exp(mu),
        "calculated_hksj_95_ci": [math.exp(mu-delta), math.exp(mu+delta)],
        "k2_publication_rule": "WITHHOLD" if k == 2 else "NOT_TRIGGERED",
        "tau2": tau2,
        "Q": q0,
        "I2_percent": max(0.0, (q0-(k-1))/q0)*100 if q0 > 0 else 0,
    }

MACE = [
    Effect("SAVOR-TIMI 53", 1.00, .89, 1.12, "https://pubmed.ncbi.nlm.nih.gov/23992601/"),
    Effect("CARMELINA", 1.02, .89, 1.17, "https://pubmed.ncbi.nlm.nih.gov/30418475/"),
    Effect("Omarigliptin", 1.00, .77, 1.29, "https://pubmed.ncbi.nlm.nih.gov/28893244/"),
    Effect("TECOS: secondary 3-point MACE", .99, .89, 1.10,
           "https://clinicaltrials.gov/study/NCT00790205"),
]
HF_CURRENT = [
    Effect("SAVOR-TIMI 53", 1.27, 1.07, 1.51, "https://pubmed.ncbi.nlm.nih.gov/23992601/"),
    Effect("TECOS", 1.00, .83, 1.20, "https://pubmed.ncbi.nlm.nih.gov/26052984/"),
]
HF_OMAR = Effect("Omarigliptin", .60, .35, 1.05, "https://pubmed.ncbi.nlm.nih.gov/28893244/")
HF_CARM = Effect("CARMELINA", .90, .74, 1.08, "https://pubmed.ncbi.nlm.nih.gov/30586723/")

PASSAGES = {
    "carmelina_mace": (
        "During a median follow-up of 2.2 years, the primary outcome occurred in 434 of 3494 (12.4%) and 420 of 3485 (12.1%) in the linagliptin and placebo groups, respectively, (absolute incidence rate difference, 0.13 [95% CI, -0.63 to 0.90] per 100 person-years) (HR, 1.02; 95% CI, 0.89-1.17; P\u2009<\u2009.001 for noninferiority).",
        "f02ae5701aef3ee9cce323608d6792b0f1cd31584d24974a663c201edce6415b"),
    "tecos_mace": (
        "Percentage of Participants With First Confirmed CV Event of MACE (Intent to Treat Population) [Up to 5 years]: Hazard Ratio (HR) 0.99 (0.89, 1.1)",
        "ce9b69adae78f8445ac97297294fe69b04cbc85c664f063c0a70b5b8747d7356"),
    "savor_hf": (
        "More patients in the saxagliptin group than in the placebo group were hospitalized for heart failure (3.5% vs. 2.8%; hazard ratio, 1.27; 95% CI, 1.07 to 1.51; P=0.007).",
        "4c2db2004668933ebe5f295b119cd7a455244ad9618472a1b92a3e777275c186"),
}

def main() -> None:
    results = {
        "audit_commit": COMMIT,
        "review_sha256_as_recorded_not_independently_rehashed": REVIEW_SHA256,
        "mace_current": pool(MACE),
        "hf_current": pool(HF_CURRENT),
        "illustrative_hf_add_omarigliptin": pool(HF_CURRENT + [HF_OMAR]),
        "illustrative_hf_add_carmelina": pool(HF_CURRENT + [HF_CARM]),
        "illustrative_hf_add_both": pool(HF_CURRENT + [HF_OMAR, HF_CARM]),
        "displayed_passage_digests": {
            name: {
                "computed": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "expected": expected,
                "matches": hashlib.sha256(text.encode("utf-8")).hexdigest() == expected,
            }
            for name, (text, expected) in PASSAGES.items()
        },
        "limitations": [
            "Inputs transcribed by this independent auditor; no network fetching.",
            "Not an execution of reproduce_review.py or an end-to-end certificate check.",
            "Added-data analyses do not establish exhaustive eligible outcome coverage.",
            "EXAMINE and any other additional eligible results require separate adjudication.",
            "Nonsignificant pooled estimates do not establish equivalence, protection, or safety.",
        ],
    }
    assert round(results["mace_current"]["estimate"], 4) == 1.0007
    assert round(results["hf_current"]["estimate"], 4) == 1.1296
    assert all(x["matches"] for x in results["displayed_passage_digests"].values())
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
