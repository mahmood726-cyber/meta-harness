#!/usr/bin/env python3
"""Independent, offline topic-25 diagnostics. Python >=3.10; standard library only.
Run: python audit.py [--output results.json]
Neither a repository replay nor a production gate test. See README.md.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import NormalDist
from endpoint_excerpt import _component_set, _outcome_match_detail

ROOT = Path(__file__).resolve().parent
Z975 = NormalDist().inv_cdf(0.975)
# Two-sided 95% quantiles, only degrees of freedom needed by this audit.
T975 = {1: 12.7062047361747, 2: 4.302652729749464}

def meta(rows: list[dict]) -> dict:
    if len(rows) not in (2, 3):
        raise ValueError('This bounded audit supports two or three inputs.')
    y, v = [], []
    for r in rows:
        e,l,h = (float(r[k]) for k in ('estimate','lower','upper'))
        if not (0 < l < h and l <= e <= h):
            raise ValueError(f'Invalid ratio or interval: {r}')
        y.append(math.log(e))
        v.append(((math.log(h)-math.log(l))/(2*Z975))**2)
    k=len(y)
    def at(tau2):
        w=[1/(vv+tau2) for vv in v]
        mu=sum(ww*yy for ww,yy in zip(w,y))/sum(w)
        q=sum(ww*(yy-mu)**2 for ww,yy in zip(w,y))
        return w,mu,q
    wf,muf,qf=at(0.0)
    tau2=0.0
    if qf>k-1:
        left,right=0.,max(v)
        while at(right)[2]>k-1:
            right*=2
            if right>1e6: raise ArithmeticError('Failed to bracket PM root.')
        for _ in range(100):
            mid=(left+right)/2
            if at(mid)[2]>k-1: left=mid
            else: right=mid
        tau2=(left+right)/2
    w,mu,q=at(tau2)
    h=max(1.,q/(k-1))
    se=math.sqrt(h/sum(w)); t=T975[k-1]
    p=math.exp(-qf/2) if k==3 else math.erfc(math.sqrt(qf/2))
    return {'k':k,'estimate':math.exp(mu),'lower':math.exp(mu-t*se),'upper':math.exp(mu+t*se),
            'tau2':tau2,'Q':qf,'I2_percent':100*max(0.,(qf-(k-1))/qf) if qf else 0.,
            'Q_p':p,'HK_variance_factor':h,
            'prediction_lower':math.exp(mu-t*math.sqrt(tau2+se*se)),
            'prediction_upper':math.exp(mu+t*math.sqrt(tau2+se*se)),
            'common_effect':{'estimate':math.exp(muf),'lower':math.exp(muf-Z975/math.sqrt(sum(wf))),
                             'upper':math.exp(muf+Z975/math.sqrt(sum(wf)))},
            'weights':{r['id']:ww/sum(w) for r,ww in zip(rows,w)},
            'method':'Independent PM random effects, floored HKSJ, PI using t_(k-1); SE from printed 95% CIs.'}

def run() -> dict:
    data=json.loads((ROOT/'inputs.json').read_text())
    checks=[]
    def check(name,ok):
        checks.append({'name':name,'pass':bool(ok)})
        if not ok: raise AssertionError(name)
    rows=data['trials']; pooled=meta(rows)
    check('pooled estimate matches displayed four-decimal rounding', round(pooled['estimate'],4)==.8134)
    check('lower CI matches displayed rounding', round(pooled['lower'],4)==.5074)
    check('upper CI matches reported four-decimal value', round(pooled['upper'],4)==1.3039)
    check('tau2 matches displayed five-decimal value',round(pooled['tau2'],5)==.02669)
    check('Q matches displayed three-decimal value',round(pooled['Q'],3)==9.057)
    check('I2 matches displayed one-decimal percentage',round(pooled['I2_percent'],1)==77.9)
    hashes=[]
    for r in rows:
        actual=hashlib.sha256(r['passage'].encode('utf-8')).hexdigest()
        hashes.append({'id':r['id'],'expected':r['passage_sha256'],'computed':actual})
        check('passage digest '+r['id'],actual==r['passage_sha256'])
    f=data['endpoint_fixtures']; generic=f['stored_pooled_outcome']
    tests={
        'CLEAR_generic_to_correct_colchicine':(generic,f['clear_colchicine'],False),
        'CLEAR_generic_to_wrong_spironolactone':(generic,f['clear_spironolactone'],True),
        'COLCOT_generic_to_correct_primary':(generic,f['colcot_primary'],False),
        'COLCOT_generic_to_wrong_secondary':(generic,f['colcot_secondary'],True),
        'CLEAR_explicit_to_correct_colchicine':(f['clear_colchicine']['measure'],f['clear_colchicine'],True),
        'CLEAR_explicit_to_wrong_spironolactone':(f['clear_colchicine']['measure'],f['clear_spironolactone'],False),
        'COLCOT_explicit_to_correct_primary':(f['colcot_primary']['measure'],f['colcot_primary'],True),
        'COLCOT_explicit_to_wrong_secondary':(f['colcot_primary']['measure'],f['colcot_secondary'],False),
    }
    matcher={}
    for name,(target,reg,expected) in tests.items():
        result=_outcome_match_detail(target,reg,None)
        matcher[name]={'target':target,'registered':reg,'result':result,
                       'expected_observed_algorithm_output':expected}
        check('isolated matcher '+name,result['matched']==expected)
    # These passing tests reproduce defects; they do not endorse the defective matches.
    comps=_component_set(f['clear_spironolactone']['measure'])
    check('new or worsening HF is omitted by inspected component parser',comps=={'CV_DEATH','NONFATAL_MI','NONFATAL_STROKE'})
    ids=data['screening']['ids']
    check('manually transcribed screen has 120 unique IDs',len(ids)==120 and len(set(ids))==120)
    pick=sorted(random.Random(data['screening']['seed']).sample(range(len(ids)),5))
    check('seeded sample indices',pick==[3,11,96,99,109])
    loo=[]
    for r in rows:
        result=meta([x for x in rows if x['id']!=r['id']])
        loo.append({'omitted_id':r['id'],'diagnostic_only_k2':True,**result})
    return {'identity':{k:data[k] for k in ('audit_date','topic_number','slug','repository_ref','review_sha256','status')},
            'scope':'Independent computation plus manually transcribed isolated matcher; no complete production replay.',
            'pooled':pooled,'leave_one_out':loo,'passage_hashes':hashes,'endpoint_match_tests':matcher,
            'screening_sample':{'origin':data['screening']['origin'],'indices':pick,'ids':[ids[i] for i in pick]},
            'checks':checks,'passed_checks':sum(c['pass'] for c in checks),'total_checks':len(checks)}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results.json')
    args=parser.parse_args()
    result=run()
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed_checks':result['passed_checks'],'total_checks':result['total_checks'],
                      'pooled':result['pooled'],'output':str(args.output)},indent=2))
