#!/usr/bin/env python3
"""Independent arithmetic and passage-digest checks for Meta-harness review 9.

Python >=3.10 and scipy are required. Run:
    python finerenone_review9_checks.py > finerenone_review9_checks.json

This is not the harness replay or a scientific certification. Inputs are manually
transcribed from the pinned audit material and identified primary sources.
The calculated HKSJ interval is diagnostic: the review's K2_SINGLE_DF policy
withholds it. The FDA-based safety calculation is not an admitted harness row.
"""
from __future__ import annotations
import hashlib
import json
import math
from scipy.stats import norm, t

COMMIT = '0730234d0b4f'
REVIEW_HASH = '50e3e56b579aaea26e8dc830b457d6b0eae608b3303e05443a810ce08d2020cd'
TRIALS = [
    {'name': 'FIDELIO-DKD', 'pmid': '33264825', 'effect': .82, 'lower': .73, 'upper': .93},
    {'name': 'FIGARO-DKD', 'pmid': '34449181', 'effect': .87, 'lower': .76, 'upper': 1.01},
]
PASSAGES = {
    'FIDELIO-DKD': (
        'RESULTS: During a median follow-up of 2.6 years, a primary outcome event occurred in 504 of 2833 patients (17.8%) in the finerenone group and 600 of 2841 patients (21.1%) in the placebo group (hazard ratio, 0.82; 95% confidence interval [CI], 0.73 to 0.93; P\u2009=\u20090.001).',
        '64e2bda7355de6718a7fc208f272e14be549c6e7540583979b0a83a53ef2dea8'),
    'FIGARO-DKD': (
        'The secondary composite outcome occurred in 350 patients (9.5%) in the finerenone group and in 395 (10.8%) in the placebo group (hazard ratio, 0.87; 95% CI, 0.76 to 1.01).',
        'fb86b3ed69d2657aedbc15068e294690968480ca564b3b510bf3aefe58a4e3fb'),
}

def checked_ratio(a: int, n1: int, c: int, n0: int) -> dict:
    """Unadjusted RR with conventional log-Wald interval, no zero correction."""
    if not (0 < a < n1 and 0 < c < n0):
        raise ValueError('Positive event and non-event counts required.')
    rr = (a / n1) / (c / n0)
    se = math.sqrt(1/a - 1/n1 + 1/c - 1/n0)
    half = float(norm.ppf(.975)) * se
    return {'events_finerenone': a, 'n_finerenone': n1,
            'events_placebo': c, 'n_placebo': n0,
            'risk_finerenone': a/n1, 'risk_placebo': c/n0,
            'unadjusted_RR': rr,
            'log_wald_95_CI': [math.exp(math.log(rr)-half), math.exp(math.log(rr)+half)]}

def main() -> None:
    z = float(norm.ppf(.975))
    y, variances = [], []
    for row in TRIALS:
        if not 0 < row['lower'] <= row['effect'] <= row['upper'] or row['upper'] == row['lower']:
            raise ValueError('Invalid ratio/interval input.')
        y.append(math.log(row['effect']))
        variances.append(((math.log(row['upper'])-math.log(row['lower']))/(2*z))**2)
    w = [1/v for v in variances]
    sw = math.fsum(w)
    mu = math.fsum(wi*yi for wi, yi in zip(w,y))/sw
    q = math.fsum(wi*(yi-mu)**2 for wi,yi in zip(w,y))
    df = len(TRIALS)-1
    # For these data Q(0)<k-1, so the PM boundary solution is exactly tau^2=0.
    if q > df:
        raise ValueError('This audit-specific check requires the PM zero-heterogeneity boundary; changed inputs need a general PM solver.')
    se = math.sqrt(1/sw)
    hk_scale = max(1.0,q/df)
    hkse = math.sqrt(hk_scale/sw)
    tcrit = float(t.ppf(.975,df))
    common_ci = [math.exp(mu-z*se), math.exp(mu+z*se)]
    hkci = [math.exp(mu-tcrit*hkse), math.exp(mu+tcrit*hkse)]
    digests = {}
    for name,(passage,expected) in PASSAGES.items():
        actual = hashlib.sha256(passage.encode('utf-8')).hexdigest()
        digests[name] = {'passage':passage,'computed_sha256':actual,'expected_sha256':expected,'matches':actual==expected}
    result = {
        'audit_commit':COMMIT,
        'review_sha256_recorded_not_independently_rehashed':REVIEW_HASH,
        'source_reported_trial_inputs':TRIALS,
        'kidney_composite_recalculation':{
            'endpoint':'Kidney failure, sustained >=40% eGFR decrease, or renal death',
            'k':len(TRIALS),'estimate':math.exp(mu), 'log_estimate':mu,
            'study_variances':variances, 'study_weights_proportion':[wi/sw for wi in w],
            'Q':q,'tau2_Paule_Mandel':0.0,'I2_percent':0.0,
            'common_effect_z_95_CI':common_ci,
            'mathematical_HKSJ_95_CI_NOT_SERVED_UNDER_K2_POLICY':hkci,
            'HKSJ_df':df,'HKSJ_t_quantile':tcrit,'HKSJ_variance_scale':hk_scale,
            'recorded_publication_rule':'K2_SINGLE_DF: pooled point estimate may be displayed; registered interval withheld',
        },
        'passage_digest_checks':digests,
        'FDA_primary_source_hyperkalemia_recovery':{
            'source':'https://www.accessdata.fda.gov/drugsatfda_docs/label/2021/215341s000lbl.pdf',
            'locator':'July 2021 original FDA label, Table 3, printed page 4 (zero-based page 3)',
            'scope':'FIDELIO-DKD reported hyperkalemia adverse reaction, safety population; not laboratory-threshold hyperkalemia and not discontinuation',
            'calculation':checked_ratio(516,2827,255,2831),
            'admission_status':'AUDITOR_ILLUSTRATION_ONLY_NOT_ADMITTED_TO_HARNESS',
        },
        'limitations':[
            'No full offline reproduce_review.py execution or fresh deployment attestation.',
            'Matching displayed-passage digests does not verify the canonical review hash.',
            'Original trial HRs were checked against sources, not re-estimated from participant-level survival data.',
            'The HKSJ interval is a diagnostic computation, not a proposal to bypass the registered publication policy.',
            'The safety RR is reconstructed from exact FDA counts, not the trial-reported adjusted effect or a complete safety synthesis.',
        ],
    }
    assert round(result['kidney_composite_recalculation']['estimate'],4)==.8407
    assert round(q,4)==.3859
    assert all(row['matches'] for row in digests.values())
    print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))

if __name__ == '__main__':
    main()
