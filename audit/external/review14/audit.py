#!/usr/bin/env python3
"""Independent topic-14 numerical and transcription checks.

No network calls. No harness import, full replay, or production-gate execution.
Inputs are manually transcribed audit fixtures, not canonical repository bytes.
Requires Python 3.10+, numpy and scipy. Run: python audit.py
"""
from __future__ import annotations
import hashlib
import json
import math
import platform
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import brentq
from scipy.stats import chi2, norm, t


def synthesize(rows: list[dict]) -> dict:
    if len(rows) < 2:
        raise ValueError("This diagnostic expects at least two independent studies.")
    for row in rows:
        if not 0 < row['ci_low'] < row['effect'] < row['ci_high']:
            raise ValueError(f"Invalid effect interval: {row['trial']}")
    z = float(norm.ppf(.975))
    y = np.log([row['effect'] for row in rows])
    se = (np.log([row['ci_high'] for row in rows]) - np.log([row['ci_low'] for row in rows])) / (2*z)
    v = se**2
    df = len(rows)-1
    def q_at(tau2: float) -> float:
        w = 1/(v+tau2)
        mu = float(np.sum(w*y)/np.sum(w))
        return float(np.sum(w*(y-mu)**2))
    q0 = q_at(0.)
    if q0 <= df:
        tau2 = 0.
    else:
        upper = 1.
        while q_at(upper) > df:
            upper *= 2
        tau2 = float(brentq(lambda x:q_at(x)-df,0.,upper,xtol=1e-15))
    w = 1/(v+tau2)
    mu = float(np.sum(w*y)/np.sum(w))
    hk_factor = max(1.,q_at(tau2)/df)
    se_mu = math.sqrt(hk_factor/float(np.sum(w)))
    crit = float(t.ppf(.975,df))
    wf=1/v
    muf=float(np.sum(wf*y)/np.sum(wf))
    sef=math.sqrt(1/float(np.sum(wf)))
    lo=max(row['ci_low'] for row in rows)
    hi=min(row['ci_high'] for row in rows)
    # These expressions are independent diagnostic equivalents, NOT executed
    # functions from harness/k2.py and NOT an end-to-end publication-path test.
    opposite = len(rows)==2 and min(y)<0<max(y)
    disjoint = len(rows)==2 and lo>hi
    return {
        'k':len(rows),'estimate':math.exp(mu),
        'ci_low_hksj':math.exp(mu-crit*se_mu),'ci_high_hksj':math.exp(mu+crit*se_mu),
        'tau2_PM':tau2,'Q_common_effect':q0,'Q_p_value':float(chi2.sf(q0,df)),
        'I2_percent':max(0.,(q0-df)/q0*100) if q0 else 0.,
        'se_log_effects':se.tolist(),'random_effect_weights_percent':(w/w.sum()*100).tolist(),
        'df':df,'t_critical':crit,'hksj_variance_floor_factor':hk_factor,
        'common_effect_diagnostic_only':{'estimate':math.exp(muf),'ci_low':math.exp(muf-z*sef),'ci_high':math.exp(muf+z*sef)},
        'interval_overlap':[lo,hi] if lo<=hi else None,
        'independent_policy_condition_check':{
            'opposite_point_estimates':bool(opposite),'nonoverlapping_CIs':bool(disjoint),
            'would_trigger_pinned_direction_rule':bool(opposite or disjoint),
            'production_policy_executed':False}
    }


def main() -> None:
    root=Path(__file__).resolve().parent
    inputs=json.loads((root/'inputs.json').read_text())
    digest_checks=[]
    for row in inputs['trials']:
        actual=hashlib.sha256(row['passage'].encode('utf-8')).hexdigest()
        assert actual==row['expected_passage_sha256'], f"Passage digest mismatch: {row['trial']}"
        digest_checks.append({'trial':row['trial'],'actual_sha256':actual,'matches':True})
    analysis=synthesize(inputs['trials'])
    expected={'estimate':.8366390216231987,'ci_low_hksj':.2108198669398027,
              'ci_high_hksj':3.320203464043028,'tau2_PM':.011770288928076343}
    for key,val in expected.items():
        assert math.isclose(analysis[key],val,rel_tol=1e-9,abs_tol=1e-11),(key,analysis[key],val)
    a=set(inputs['eligibility_sets']['family_eligible'])
    b=set(inputs['eligibility_sets']['record_level_included_trial_families'])
    result={'identity':inputs['identity'],'checks_scope':inputs['input_origin'],
        'runtime':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
        'passage_digest_checks':digest_checks,'analysis':analysis,
        'eligibility_set_comparison':{'family_count':len(a),'record_family_count':len(b),
            'only_family_eligible':sorted(a-b),'only_record_included':sorted(b-a),
            'same_count':len(a)==len(b),'same_membership':a==b,
            'scope':'Set comparison of manual page transcriptions, not independent screening of all records.'},
        'full_review_replay_executed':False,'canonical_review_hash_recomputed':False,
        'html_hash_recomputed':False,'current_live_deployment_verified':False,
        'production_gate_executed':False,'all_screening_records_readjudicated':False}
    (root/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    print('\nPASS: two passage digests, independent analysis checks, and eligible-set comparison completed.\nNot a full harness verification.')

if __name__=='__main__':
    main()
