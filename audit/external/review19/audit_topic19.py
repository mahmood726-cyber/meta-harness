#!/usr/bin/env python3
"""Independent Topic 19 checks, not the meta-harness production verifier.

Inputs are manually transcribed from the pinned page/cache and the user audit
pack. Source reports were read independently. No network or repository writes.
Requires Python 3.10+ and scipy. Run: python audit_topic19.py
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from scipy.optimize import brentq
from scipy.stats import chi2, norm, t

ROOT = Path(__file__).resolve().parent
IDENTITY = {
    'slug': 'sglt2-primary-prevention-hf',
    'repository_ref': '0730234d0b4f',
    'review_sha256_recorded_not_recomputed': '35134b4721fd1704c29aef2277a726d3bf3f12b3ca3e538d2a4c92004429fcbd',
    'audit_date': '2026-10-10',
    'input_provenance': 'Manual transcription, not automatic extraction or a complete repository replay',
}
TRIALS = [
    {'name': 'CANVAS Program', 'row_pmid':'28605608', 'source_pmid':'29526832', 'hr': .67, 'lower': .52, 'upper': .87},
    {'name': 'EMPA-REG OUTCOME', 'row_pmid':'26378978', 'source_pmid':'26819227', 'hr': .65, 'lower': .50, 'upper': .85},
    {'name': 'VERTIS CV', 'row_pmid':'32966714', 'source_pmid':'33026243', 'hr': .70, 'lower': .54, 'upper': .90},
    {'name': 'DECLARE-TIMI 58', 'row_pmid':'30415602', 'source_pmid':'30415602', 'hr': .73, 'lower': .61, 'upper': .88},
]
PASSAGES = [
    {'name': 'CANVAS Program', 'expected_sha256':'dc8726a5bddf8e5d0142c43a83a9f16ce6b2a4976d8ff92a13f15e380db194fb',
     'text': 'Overall, cardiovascular death or hospitalized HF was reduced in those treated with canagliflozin compared with placebo (16.3 versus 20.8 per 1000 patient-years; hazard ratio [HR], 0.78; 95% confidence interval [CI], 0.67-0.91), as was fatal or hospitalized HF (HR, 0.70; 95% CI, 0.55-0.89) and hospitalized HF alone (HR, 0.67; 95% CI, 0.52-0.87).'},
    {'name': 'EMPA-REG OUTCOME', 'expected_sha256':'4b164843e164451b83fa2a96eb2729c9dcc6249d8e928b147014710773d5f9a4',
     'text':'As previously reported, hospitalization for heart failure occurred in a significantly lower percentage of patients treated with empagliflozin [126/4687 patients (2.7%)] than with placebo [95/2333 patients (4.1%)] [HR: 0.65 (95% CI: 0.50–0.85); P = 0.002]. 19 The effect of empagliflozin on this outcome was consistent across doses, sensitivity analyses, and subgroups defined by baseline characteristics ( Figure 2 ; see Supplementary material online, Table S1 Supplementary Data ).'},
    {'name': 'DECLARE-TIMI 58', 'expected_sha256':'15623939f004ea9b779fb2d283b29b4cb0bf9d545701fe414b4eb544e5e873a1',
     'text':'In the two primary efficacy analyses, dapagliflozin did not result in a lower rate of MACE (8.8% in the dapagliflozin group and 9.4% in the placebo group; hazard ratio, 0.93; 95% CI, 0.84 to 1.03; P=0.17) but did result in a lower rate of cardiovascular death or hospitalization for heart failure (4.9% vs. 5.8%; hazard ratio, 0.83; 95% CI, 0.73 to 0.95; P=0.005), which reflected a lower rate of hospitalization for heart failure (hazard ratio, 0.73; 95% CI, 0.61 to 0.88); there was no between-group difference in cardiovascular death (hazard ratio, 0.98; 95% CI, 0.82 to 1.17).'},
]

def meta_analysis(rows: list[dict]) -> dict:
    """Generic inverse-variance PM analysis with modified/floored HK interval."""
    if len(rows) < 2:
        raise ValueError('At least two studies are required')
    for row in rows:
        if not (0 < row['lower'] < row['hr'] < row['upper']):
            raise ValueError(f'Invalid bounds: {row}')
    z = float(norm.ppf(.975))
    y = [math.log(row['hr']) for row in rows]
    v = [((math.log(row['upper'])-math.log(row['lower']))/(2*z))**2 for row in rows]
    k, df = len(rows), len(rows)-1
    def moments(tau2: float) -> tuple:
        w = [1/(vi+tau2) for vi in v]
        sw = sum(w)
        mu = sum(wi*yi for wi,yi in zip(w,y))/sw
        q = sum(wi*(yi-mu)**2 for wi,yi in zip(w,y))
        return mu,q,w,sw
    q0 = moments(0)[1]
    tau2 = 0.0
    if q0 > df:
        high = max(v)
        while moments(high)[1] > df:
            high *= 2
        tau2 = float(brentq(lambda x: moments(x)[1]-df, 0, high, xtol=1e-14))
    mu,q,w,sw = moments(tau2)
    hk_unfloored = q/df
    hk_used = max(1.0,hk_unfloored)
    se = math.sqrt(hk_used/sw)
    crit = float(t.ppf(.975,df))
    ci = [math.exp(mu-crit*se),math.exp(mu+crit*se)]
    pi_se = math.sqrt(tau2+se*se)
    pi = [math.exp(mu-crit*pi_se),math.exp(mu+crit*pi_se)]
    fe_mu,_,_,fe_sw = moments(0)
    return {
        'k_analysis_units': k,
        'pooled_hr': math.exp(mu),
        'hksj_floored_ci95': ci,
        'tau2_PM':tau2,'Q_common_effect':q0,
        'Q_p_value':float(chi2.sf(q0,df)),
        'I2_percent':max(0.0,(q0-df)/q0)*100 if q0 else 0.0,
        'hk_variance_factor_unfloored': hk_unfloored,
        'hk_variance_factor_used':hk_used,
        'prediction_interval_t_kminus1':pi,
        'prediction_interval_note':'Diagnostic reconstruction under t(k-1), not proof of generalisability or complete evidence',
        'weights_percent':{row['name']:wi/sw*100 for row,wi in zip(rows,w)},
        'common_effect_sensitivity':{'hr':math.exp(fe_mu),'ci95':[math.exp(fe_mu-z/math.sqrt(fe_sw)),math.exp(fe_mu+z/math.sqrt(fe_sw))]},
        'inputs':rows,
    }

def main() -> None:
    hashes = []
    for passage in PASSAGES:
        calculated = hashlib.sha256(passage['text'].encode('utf-8')).hexdigest()
        record = {**passage,'calculated_sha256':calculated,'matches':calculated==passage['expected_sha256']}
        hashes.append(record)
        if not record['matches']:
            raise AssertionError(f"Hash mismatch: {passage['name']}")
    result = meta_analysis(TRIALS)
    # Only assert values actually printed in the acquired pinned manuscript.
    assert round(result['pooled_hr'],2) == .70
    assert [round(x,2) for x in result['hksj_floored_ci95']] == [.58,.84]
    served_ids = {row['row_pmid'] for row in TRIALS}
    # Exact IDs manually transcribed from G1 in_our_pool:true entries.
    g1_pooled = {'26378978','28605608','32966714','30415602','28284707'}
    membership = {
        'fixture_type':'manual transcription of two pinned artifacts, not production gate execution',
        'current_forest_row_ids':sorted(served_ids),
        'g1_in_our_pool_true_ids':sorted(g1_pooled),
        'current_count':len(served_ids),
        'g1_count':len(g1_pooled),
        'extra_in_g1':sorted(g1_pooled-served_ids),
        'missing_in_g1':sorted(served_ids-g1_pooled),
        'sets_agree':served_ids==g1_pooled,
        'extra_report_source_fact':'PMID 28284707 is an HF-history subgroup pooled from five clinical trials, not one additional independent CVOT',
        'scope':'Finding concerns pinned comparison artifact; a fresh G1 run and full comparator tab were not obtained',
    }
    assert membership['extra_in_g1'] == ['28284707']
    leave_one_out = {row['name']:meta_analysis([other for other in TRIALS if other is not row]) for row in TRIALS}
    out = {'identity':IDENTITY,'primary':result,'passage_checks':hashes,'membership_check':membership,
           'leave_one_out_diagnostic':leave_one_out,
           'scope_limits':['Canonical review/HTML/certificate hashes were not regenerated',
                           'No full repository replay, production screening, or G1 gate run',
                           'No patient-level time-to-event calculation reconstructed',
                           'Not all 294 screening records adjudicated',
                           'No repository or website modifications']}
    (ROOT/'audit_results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (ROOT/'inputs_and_passages.json').write_text(json.dumps({'identity':IDENTITY,'trials':TRIALS,'passages':PASSAGES},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({'primary':result,'hashes_match':all(x['matches'] for x in hashes),'membership_check':membership},indent=2))

if __name__ == '__main__':
    main()
