#!/usr/bin/env python3
"""Independent topic-27 numerical checks and isolated fixtures (Python stdlib).

Run: python audit.py [--output results.json]
This is NOT a repository replay, production screener, licence guard or G1 test.
Inputs are explicitly manual transcriptions. No network calls or external writes.
Diagnostic implementation is intentionally bounded to 2-4 positive-cell trials.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import NormalDist
from screen_excerpt import has

HERE = Path(__file__).resolve().parent
Z = NormalDist().inv_cdf(0.975)
T975 = {1: 12.7062047361747, 2: 4.302652729749464, 3: 3.182446305284263}

def log_or(row: dict) -> tuple[float, float]:
    a, n, c, m = (row[k] for k in ('events_t','n_t','events_c','n_c'))
    if any(not isinstance(x,int) for x in (a,n,c,m)) or not (0<a<n and 0<c<m):
        raise ValueError('This audit requires integer counts and all four cells positive.')
    b, d = n-a, m-c
    return math.log(a/b)-math.log(c/d), 1/a+1/b+1/c+1/d

def single(row: dict) -> dict:
    y,v = log_or(row)
    return {'id':row['id'],'OR':math.exp(y),'ci_low':math.exp(y-Z*math.sqrt(v)),
            'ci_high':math.exp(y+Z*math.sqrt(v)),'log_OR':y,'variance':v}

def q_survival(q: float, df: int) -> float:
    if q <= 0:
        return 1.0
    if df == 1:
        return math.erfc(math.sqrt(q/2))
    if df == 2:
        return math.exp(-q/2)
    if df == 3:
        return math.erfc(math.sqrt(q/2)) + 2/math.sqrt(math.pi)*math.sqrt(q/2)*math.exp(-q/2)
    raise ValueError('Chi-square helper supports df 1-3 only.')

def meta(rows: list[dict]) -> dict:
    k = len(rows)
    if k not in (2,3,4):
        raise ValueError('This bounded diagnostic supports k=2,3,4 only.')
    data = [log_or(r) for r in rows]
    y,v = zip(*data)
    def at(tau2):
        w = [1/(vi+tau2) for vi in v]
        sw = math.fsum(w)
        mu = math.fsum(wi*yi for wi,yi in zip(w,y))/sw
        q = math.fsum(wi*(yi-mu)**2 for wi,yi in zip(w,y))
        return w,sw,mu,q
    _,sw0,mu0,q0 = at(0)
    df=k-1
    tau2=0.0
    if q0>df:
        lo,hi=0.0,1.0
        while at(hi)[3]>df:
            hi*=2
            if hi>1e6:
                raise ArithmeticError('Paule-Mandel root failed to bracket.')
        for _ in range(120):
            mid=(lo+hi)/2
            if at(mid)[3]>df: lo=mid
            else: hi=mid
        tau2=(lo+hi)/2
    w,sw,mu,q=at(tau2)
    factor=max(1.0,q/df)
    se=math.sqrt(factor/sw)
    tc=T975[df]
    pi_se=math.sqrt(tau2+se*se)
    return {'k':k,'OR':math.exp(mu),'ci_low':math.exp(mu-tc*se),
            'ci_high':math.exp(mu+tc*se),'tau2':tau2,'Q':q0,
            'I2_percent':max(0,(q0-df)/q0)*100 if q0 else 0,
            'Q_p':q_survival(q0,df),'HKSJ_factor':factor,'HKSJ_SE':se,
            'prediction_low':math.exp(mu-tc*pi_se),'prediction_high':math.exp(mu+tc*pi_se),
            'weights':{r['id']:wi/sw for r,wi in zip(rows,w)},
            'common_effect_OR':math.exp(mu0),'common_effect_ci_low':math.exp(mu0-Z/math.sqrt(sw0)),
            'common_effect_ci_high':math.exp(mu0+Z/math.sqrt(sw0)),
            'note':'Independent calculation; k=2 HKSJ intervals are diagnostic, not authorized served intervals.'}

def run() -> dict:
    inputs=json.loads((HERE/'inputs.json').read_text(encoding='utf-8'))
    rows=inputs['trials']
    pool=meta(rows)
    hashes=[{'id':r['id'],'expected':r['passage_sha256'],
             'computed':hashlib.sha256(r['passage'].encode('utf-8')).hexdigest()} for r in rows]
    # One displayed record per line; acronym-prefixed registry rows end in the NCT ID.
    ids=[line.strip().split()[-1] for line in (HERE/'screening_ids.txt').read_text().splitlines() if line.strip()]
    seed='20261008:metformin-pcos-ovulation:screen'
    indices=sorted(random.Random(seed).sample(range(len(ids)),5))
    picked=[ids[i] for i in indices]
    lexical={key:has(text,inputs['comparator_terms'],plural=True)
             for key,text in inputs['lexical_fixtures'].items()}
    synthetic_bare=has(inputs['lexical_fixtures']['legro_source_informed'],
                       inputs['comparator_terms']+['placebo'],plural=True)
    legro=inputs['legro_diagnostic']
    added=meta(rows+[legro])
    safety=single(inputs['moll_safety'])
    eligible=inputs['family_eligible_ids']
    after=[x for x in eligible if x not in inputs['confirmed_wrong_context_ivf']]
    checks=[]
    def check(name,ok):
        checks.append({'name':name,'passed':bool(ok)})
        if not ok: raise AssertionError(name)
    def near(a,b,tol=1e-9): return math.isclose(a,b,rel_tol=tol,abs_tol=tol)
    for h in hashes: check('Passage hash '+h['id'],h['computed']==h['expected'])
    check('Primary point reconstruction',near(pool['OR'],2.0733340554658115))
    check('Primary HKSJ limits',near(pool['ci_low'],.09224551476994274) and near(pool['ci_high'],46.60079263772509))
    check('Paule-Mandel tau2',near(pool['tau2'],1.1587214548618145))
    check('Q and I2',near(pool['Q'],9.259221231343448) and near(pool['I2_percent'],78.39991128811366))
    check('Prediction interval convention',near(pool['prediction_low'],.007820241924982384) and near(pool['prediction_high'],549.6906805174056))
    check('Ben Ayed percentage arithmetic',10/16==.625 and 6/16==.375)
    check('Moll rates round to printed whole percentages',round(100*71/111)==64 and round(100*82/114)==72)
    check('Screening transcribed count',len(ids)==154 and len(set(ids))==154)
    check('Seeded indices',indices==[9,25,26,35,46])
    check('Seeded IDs',picked==['28118681','19692630','19552904','17287476','42002670'])
    check('Manual family baseline count',len(eligible)==8)
    check('Two-confirmed-IVF local removal',len(after)==6)
    check('Legro paraphrase misses configured comparator phrases',lexical['legro_source_informed'] is None)
    check('Retracted Kazerooni paraphrase misses phrases',lexical['kazerooni_source_informed_retracted'] is None)
    check('Positive phrase controls',lexical['placebo_group_control']=='placebo group' and lexical['placebo_controlled_control']=='placebo-controlled')
    check('No-comparator and negation controls',lexical['no_placebo_control'] is None and lexical['negation_control'] is None)
    check('Synthetic bare-placebo recognition only',synthetic_bare=='placebo')
    check('Legro participant complement',legro['n_t']-legro['no_documented_ovulation_t']==legro['events_t'] and legro['n_c']-legro['no_documented_ovulation_c']==legro['events_c'])
    check('Legro diagnostic added-pool point',near(added['OR'],1.803050660218671))
    check('Retraction not admitted to any computed pool',inputs['retraction']['pmid'] not in [r['id'] for r in rows+[legro]])
    check('Moll discontinuation OR',near(safety['OR'],3.4838709677419355))
    return {'identity':{x:inputs[x] for x in ['topic','slug','commit','review_sha256','status']},
            'scope':'Independent numerical audit and explicitly manual fixtures. No full repository or production gate replay.',
            'primary':pool,'individual_inputs':[single(r) for r in rows],
            'leave_one_out_diagnostics':[{'omitted':r['id'],'result':meta(rows[:i]+rows[i+1:])} for i,r in enumerate(rows)],
            'passage_hashes':hashes,'screening_sample':{'source':'Manual transcription of displayed row order','seed':seed,'indices':indices,'ids':picked},
            'lexical_paraphrase_tests':lexical,'synthetic_bare_placebo_extension':synthetic_bare,
            'legro_candidate_not_admitted':single(legro),'legro_added_diagnostic_not_admitted':added,
            'moll_safety_not_admitted':safety,
            'ivf_local_count_reconciliation':{'before':len(eligible),'after':len(after),'removed':inputs['confirmed_wrong_context_ivf'],'not_a_final_census':True},
            'integrity_notice_manual_source_check':inputs['retraction'],
            'checks':checks,'checks_passed':len(checks)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=HERE/'results.json')
    args=p.parse_args()
    try:
        result=run()
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
        print(f"PASS: {result['checks_passed']} computational/fixture checks; not production gates.")
        print(f"Primary OR {result['primary']['OR']:.6f} ({result['primary']['ci_low']:.6f}-{result['primary']['ci_high']:.6f}).")
        print(f"Results: {args.output}")
    except (OSError,ValueError,ArithmeticError,AssertionError) as exc:
        p.exit(1,f'FAIL: {exc}\n')
