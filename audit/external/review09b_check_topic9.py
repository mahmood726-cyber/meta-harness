#!/usr/bin/env python3
"""Independent audit of the two supplied finerenone extraction rows.

Python standard library only. This does NOT execute the meta-harness and does
NOT verify downloaded release bytes, search completeness, or risk of bias.
Source strings are the HTML-decoded passages supplied in the user's audit pack.
The modified HKSJ interval is an auditor calculation, NOT a served primary CI.
"""
from __future__ import annotations
import hashlib
import json
import math

REVIEW_SHA256 = '50e3e56b579aaea26e8dc830b457d6b0eae608b3303e05443a810ce08d2020cd'
ROWS = [
    {
        'trial': 'FIDELIO-DKD', 'pmid': '33264825', 'hr': .82, 'lower': .73, 'upper': .93,
        'source': 'https://pubmed.ncbi.nlm.nih.gov/33264825/',
        'passage': 'RESULTS: During a median follow-up of 2.6 years, a primary outcome event occurred in 504 of 2833 patients (17.8%) in the finerenone group and 600 of 2841 patients (21.1%) in the placebo group (hazard ratio, 0.82; 95% confidence interval [CI], 0.73 to 0.93; P\u2009=\u20090.001).',
        'expected_sha256': '64e2bda7355de6718a7fc208f272e14be549c6e7540583979b0a83a53ef2dea8',
    },
    {
        'trial': 'FIGARO-DKD', 'pmid': '34449181', 'hr': .87, 'lower': .76, 'upper': 1.01,
        'source': 'https://pubmed.ncbi.nlm.nih.gov/34449181/',
        'passage': 'The secondary composite outcome occurred in 350 patients (9.5%) in the finerenone group and in 395 (10.8%) in the placebo group (hazard ratio, 0.87; 95% CI, 0.76 to 1.01).',
        'expected_sha256': 'fb86b3ed69d2657aedbc15068e294690968480ca564b3b510bf3aefe58a4e3fb',
    },
]

def main() -> None:
    results = []
    for row in ROWS:
        low, hr, high = row['lower'], row['hr'], row['upper']
        if not 0 < low < hr < high:
            raise ValueError(f"Invalid confidence interval for {row['trial']}")
        digest = hashlib.sha256(row['passage'].encode('utf-8')).hexdigest()
        if digest != row['expected_sha256']:
            raise ValueError(f"Passage hash mismatch for {row['trial']}")
        se = (math.log(high) - math.log(low)) / (2 * 1.96)
        results.append({'trial': row['trial'], 'pmid': row['pmid'],
                        'passage_sha256': digest, 'digest_matches': True,
                        'log_hr': math.log(hr), 'se_log_hr': se,
                        'weight': 1 / se**2})
    sw = sum(r['weight'] for r in results)
    mu = sum(r['weight'] * r['log_hr'] for r in results) / sw
    q = sum(r['weight'] * (r['log_hr'] - mu)**2 for r in results)
    df = len(results) - 1
    # With Q(0) <= k-1 the Paule-Mandel nonnegative estimate is tau^2 = 0.
    if q > df:
        raise ValueError('This two-row check expects the PM boundary tau^2=0.')
    for r in results:
        r['weight_percent'] = 100 * r['weight'] / sw
    se_mu = math.sqrt(max(1., q / df) / sw)
    # t(.975, df=1) is the Cauchy .975 quantile.
    tcrit = math.tan(math.pi * (.975 - .5))
    out = {
        'declared_review_sha256_NOT_independently_rehashed': REVIEW_SHA256,
        'scope': 'Two supplied extraction strings and independent aggregate arithmetic only',
        'rows': results,
        'k': len(results), 'pooled_hr': math.exp(mu), 'Q': q,
        'tau2_PM': 0, 'I2_percent': max(0., (q - df) / q) * 100,
        'normal_95_ci_sensitivity': [math.exp(mu - 1.96 / math.sqrt(sw)), math.exp(mu + 1.96 / math.sqrt(sw))],
        'modified_HKSJ_95_ci_NOT_served': [math.exp(mu - tcrit * se_mu), math.exp(mu + tcrit * se_mu)],
        'replay_executed': False,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
