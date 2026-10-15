#!/usr/bin/env python3
"""Independent numerical/hash checks and isolated code test for topic 18.

Run: python audit.py
Dependencies: Python >=3.10, numpy, scipy. No network access or repository writes.
Inputs and code excerpts are manually transcribed and explicitly marked as such.
This is NOT an offline repository replay, canonical-hash audit or G1 gate run.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.stats import norm, t

from rob2_excerpt import _outcome_match_detail

ROOT = Path(__file__).resolve().parent
PIN = "0730234d0b4f"
REVIEW = "57e56790d978ea3d9bde6bc86021e9c6fb17d284d8eae5e8072c2398375f5127"


def pool(rows: list[dict]) -> dict:
    """Log-ratio PM inverse-variance pooling with residual HKSJ scale floor 1."""
    if len(rows) < 2:
        raise ValueError("This check requires at least two trial estimates.")
    for row in rows:
        if not 0 < row["lower"] <= row["effect"] <= row["upper"]:
            raise ValueError(f"Invalid ratio interval: {row}")
    y = np.log([r["effect"] for r in rows])
    z = norm.ppf(0.975)
    ses = (np.log([r["upper"] for r in rows]) - np.log([r["lower"] for r in rows])) / (2*z)
    variances = ses**2
    k = len(y)
    def values(tau2: float):
        w = 1/(variances+tau2)
        mu = float(np.dot(w,y)/w.sum())
        q = float(np.dot(w,(y-mu)**2))
        return w,mu,q
    w0,mu0,q0 = values(0.0)
    if q0 <= k-1:
        tau2 = 0.0
    else:
        upper = max(float(np.var(y)), 1e-5)
        while values(upper)[2] > k-1:
            upper *= 2
            if upper > 1e6:
                raise ArithmeticError("Could not bracket PM tau2.")
        tau2 = float(brentq(lambda x: values(x)[2]-(k-1), 0, upper))
    w,mu,q_tau = values(tau2)
    hksj_scale = max(1., q_tau/(k-1))
    se_mu = math.sqrt(hksj_scale/w.sum())
    critical = float(t.ppf(.975,k-1))
    return {
        "k":k,
        "standard_errors_from_printed_95_percent_bounds":ses.tolist(),
        "inverse_variance_weights_percent":(100*w/w.sum()).tolist(),
        "pooled_ratio":math.exp(mu),
        "tau2_PM":tau2,
        "Q_common_effect":q0,
        "I2_percent":max(0.,100*(q0-(k-1))/q0) if q0>0 else 0.,
        "HKSJ_floor_factor":hksj_scale,
        "HKSJ_t_critical":critical,
        "HKSJ_CI_DIAGNOSTIC_NOT_SERVED":[math.exp(mu-critical*se_mu),math.exp(mu+critical*se_mu)],
        "prediction_interval_DIAGNOSTIC_NOT_SERVED":[math.exp(mu-critical*math.sqrt(tau2+se_mu**2)),math.exp(mu+critical*math.sqrt(tau2+se_mu**2))],
        "common_effect_sensitivity":[math.exp(mu0),math.exp(mu0-z/math.sqrt(w0.sum())),math.exp(mu0+z/math.sqrt(w0.sum()))]
    }


def main() -> None:
    data=json.loads((ROOT/"inputs.json").read_text(encoding="utf-8"))
    results={"pin":PIN,"review_sha256_recorded_not_recomputed":REVIEW,"scipy_version":scipy.__version__}
    results["hashes"]={}
    for r in data["efficacy_inputs"]:
        digest=hashlib.sha256(r["passage"].encode("utf-8")).hexdigest()
        assert digest == r["passage_sha256"], f"Passage hash mismatch: {r['trial']}"
        results["hashes"][r["trial"]]={"sha256":digest,"matches_recorded":True}
    results["primary_reconstruction"]=pool(data["efficacy_inputs"])
    assert math.isclose(results["primary_reconstruction"]["pooled_ratio"],.75,abs_tol=1e-12)
    assert results["primary_reconstruction"]["tau2_PM"]==0.
    assert round(results["primary_reconstruction"]["common_effect_sensitivity"][1],2)==.68
    assert round(results["primary_reconstruction"]["common_effect_sensitivity"][2],2)==.83
    tests={}
    for name,reg in data["D5_match_fixtures"].items():
        tests[name]=_outcome_match_detail(data["target_name"],{"measure":reg},None)
    assert tests["broader_registered_primary"]["matched"] is True
    assert tests["selected_registered_secondary"]["matched"] is True
    assert tests["synthetic_unstable_angina_extra_component"]["matched"] is False
    results["isolated_D5_tests"]=tests
    results["D5_interpretation"]="The displayed component matcher loses urgent HF visits and falsely equates the broad primary with the selected secondary. Not a full D5/production run."
    results["abstract_source_compatibility_manual_input_check"]={
        "selected_DAPA_tuple":[.75,.65,.85],
        "DAPA_abstract_primary_tuple":[.74,.65,.85],
        "tuples_identical":False,
        "selected_tuple_present_in_checked_original_abstract":False,
        "scope":"Independent comparison of manually checked primary-source content, NOT execution of the repository's blind extractor."
    }
    results["manually_transcribed_family_conflicts"]=[r for r in data["family_states"] if r["record_decision"]=="include" and r["family_state"]!="ELIGIBLE"]
    assert len(results["manually_transcribed_family_conflicts"])==3
    results["limits"]=data["limits"]
    (ROOT/"results.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(results,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
