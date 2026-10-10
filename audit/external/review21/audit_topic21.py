#!/usr/bin/env python3
"""Independent topic 21 audit. No network or repository modifications.
Requires NumPy and SciPy. Values and metadata are transcribed in inputs.json.
This is NOT the meta-harness production implementation or a replay of its gates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any
import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.stats import norm, t, chi2

def meta_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Inverse-variance log-HR PM with HK factor max(1,Q_RE/(k-1))."""
    if len(rows) < 2:
        raise ValueError("This implementation requires at least two rows.")
    x = np.array([[r["estimate"], r["low"], r["high"]] for r in rows], dtype=float)
    if not np.isfinite(x).all() or (x <= 0).any():
        raise ValueError("All effect and interval values must be positive and finite.")
    if not ((x[:, 1] < x[:, 0]) & (x[:, 0] < x[:, 2])).all():
        raise ValueError("Every point must lie strictly within its interval.")
    z = float(norm.ppf(0.975))
    y = np.log(x[:, 0])
    se = (np.log(x[:, 2]) - np.log(x[:, 1])) / (2*z)
    v = se**2
    k, df = len(rows), len(rows)-1
    def q(tau2: float) -> float:
        w = 1/(v+tau2)
        mu = float(np.dot(w, y)/w.sum())
        return float(np.dot(w, (y-mu)**2))
    q0 = q(0.0)
    tau2 = 0.0
    if q0 > df:
        upper = max(float(v.max()), 0.001)
        for _ in range(100):
            if q(upper) <= df:
                break
            upper *= 2
        else:
            raise ArithmeticError("Failed to bracket PM root.")
        tau2 = float(brentq(lambda u: q(u)-df, 0, upper, xtol=1e-14))
    w = 1/(v+tau2)
    mu = float(np.dot(w, y)/w.sum())
    floor = max(1.0, q(tau2)/df)
    mu_se = math.sqrt(floor/float(w.sum()))
    crit = float(t.ppf(.975, df))
    fw = 1/v
    fm = float(np.dot(fw, y)/fw.sum())
    fs = math.sqrt(1/float(fw.sum()))
    return {
        "k": k, "estimate": math.exp(mu),
        "hksj_95_ci": [math.exp(mu-crit*mu_se), math.exp(mu+crit*mu_se)],
        "hksj_ci_status": "Auditor diagnostic; current k=2 interval is NOT served by harness",
        "tau2": tau2, "Q": q0,
        "I2_percent": max(0.0, 100*(q0-df)/q0) if q0 else 0.0,
        "Q_p": float(chi2.sf(q0, df)),
        "se_log_inputs": [float(a) for a in se],
        "weights_percent": [float(a) for a in 100*w/w.sum()],
        "common_effect": math.exp(fm),
        "common_effect_95_ci": [math.exp(fm-z*fs), math.exp(fm+z*fs)],
        "prediction_interval_t_k_minus_1": [
            math.exp(mu-crit*math.sqrt(tau2+mu_se**2)),
            math.exp(mu+crit*math.sqrt(tau2+mu_se**2))
        ]
    }

def run(data: dict[str, Any]) -> dict[str, Any]:
    base = meta_analysis(data["current_inputs"])
    candidate = meta_analysis(data["current_inputs"]+[data["diagnostic_candidate"]])
    hashes = []
    for row in data["passages"]:
        computed = hashlib.sha256(row["text"].encode("utf-8")).hexdigest()
        hashes.append({"id":row["id"],"computed":computed,
                       "expected":row["expected_sha256"],
                       "match":computed == row["expected_sha256"]})
    f = data["manual_inspection_fixtures"]
    assertions = {
        "two_passage_hashes_match": all(r["match"] for r in hashes),
        "pooled_hr_rounds_to_served_0_68": format(base["estimate"], ".2f") == "0.68",
        "base_pm_tau2_zero": base["tau2"] == 0.0,
        "base_hksj_interval_contains_one": base["hksj_95_ci"][0] < 1 < base["hksj_95_ci"][1],
        "candidate_moves_point_toward_one": base["estimate"] < candidate["estimate"] < 1,
        "candidate_hksj_interval_contains_one": candidate["hksj_95_ci"][0] < 1 < candidate["hksj_95_ci"][1],
        "manual_subgroup_timing_conflict_present": (
            f["jupiter_config_evidence_unit"] == "prespecified_subgroup"
            and "after trial completion" in f["jupiter_cache_limitation"]),
        "manual_prosper_blacklist_literal_matches_title": (
            f["prosper_blacklist_phrase"].casefold() in f["prosper_title"].casefold()),
        "manual_protocol_rendered_measure_mismatch": f["protocol_measure"] != f["rendered_measure"],
        "manual_comparator_ids_differ": f["protocol_comparator_pmid"] != f["g1_comparator_pmid"],
    }
    if not all(assertions.values()):
        raise AssertionError(f"Self-check failure: {assertions}")
    return {
        "audit_identity": {k:data[k] for k in ("audit_date","topic","slug","ref","review_sha256_recorded")},
        "runtime":{"numpy":np.__version__,"scipy":scipy.__version__},
        "current_two_inputs":base,
        "diagnostic_only_add_prosper_primary_prevention":candidate,
        "diagnostic_limit":"Not an admitted or complete corrected meta-analysis. Endpoint, subgroup policy and source admission remain unresolved.",
        "passage_hashes":hashes,"checks":assertions,
        "checks_summary":{"passed":sum(assertions.values()),"total":len(assertions)},
        "execution_scope":"Independent calculation; manual fixtures; no full hash/certificate/G1/screener replay."
    }

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    root=Path(__file__).resolve().parent
    p.add_argument("--inputs",type=Path,default=root/"inputs.json")
    p.add_argument("--output",type=Path,default=root/"results.json")
    args=p.parse_args()
    data=json.loads(args.inputs.read_text(encoding="utf-8"))
    result=run(data)
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"checks":result["checks_summary"],
                      "base_hr":result["current_two_inputs"]["estimate"],
                      "candidate_hr":result["diagnostic_only_add_prosper_primary_prevention"]["estimate"],
                      "output":str(args.output)},indent=2))

if __name__ == "__main__":
    main()
