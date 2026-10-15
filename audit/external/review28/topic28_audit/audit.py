#!/usr/bin/env python3
"""Independent topic-28 numerical reconstruction (not a repository replay).
All trial inputs and displayed screening order are manual transcriptions.
Only Python standard library is required. No network access or repository writes.
"""
from __future__ import annotations
import argparse, hashlib, json, math, random
from pathlib import Path
from statistics import NormalDist
from target_excerpt import tests as component_tests
HERE=Path(__file__).resolve().parent
Z=NormalDist().inv_cdf(.975)
T975={1:12.7062047361747,2:4.302652729749464,3:3.182446305284263,
      4:2.7764451051977987,5:2.570581835636314}

def effect(row):
    x,l,h=[float(row[k]) for k in ('effect','ci_low','ci_high')]
    if not 0<l<x<h: raise ValueError('Positive ratio effect strictly inside its interval required.')
    return math.log(x),((math.log(h)-math.log(l))/(2*Z))**2

def q_survival(q,df):
    if q<=0:return 1.0
    if not 1<=df<=5:raise ValueError('df outside bounded helper.')
    x=q/2
    if df%2==0:
        a=1.;s=math.exp(-x)
    else:
        a=.5;s=math.erfc(math.sqrt(x))
    while a<df/2:
        s+=math.exp(a*math.log(x)-x-math.lgamma(a+1));a+=1
    return min(1.,max(0.,s))

def meta(rows):
    k=len(rows)
    if not 2<=k<=6:raise ValueError('Supports k=2..6.')
    data=[effect(r) for r in rows];y,v=zip(*data)
    def at(tau):
        w=[1/(vi+tau) for vi in v];sw=math.fsum(w)
        mu=math.fsum(wi*yi for wi,yi in zip(w,y))/sw
        q=math.fsum(wi*(yi-mu)**2 for wi,yi in zip(w,y))
        return w,sw,mu,q
    _,s0,m0,q0=at(0);df=k-1;tau=0.
    if q0>df:
        lo,hi=0.,1.
        while at(hi)[3]>df:
            hi*=2
            if hi>1e6:raise ArithmeticError('Could not bracket PM root.')
        for _ in range(120):
            mid=(lo+hi)/2
            if at(mid)[3]>df:lo=mid
            else:hi=mid
        tau=(lo+hi)/2
    w,sw,mu,q=at(tau);factor=max(1.,q/df);se=math.sqrt(factor/sw);tc=T975[df]
    return {'k':k,'HR':math.exp(mu),'ci_low':math.exp(mu-tc*se),'ci_high':math.exp(mu+tc*se),
            'tau2':tau,'Q':q0,'I2_percent':max(0.,(q0-df)/q0)*100 if q0 else 0.,
            'Q_p':q_survival(q0,df),'HKSJ_factor':factor,'se':se,
            'prediction_low':math.exp(mu-tc*math.sqrt(tau+se*se)),
            'prediction_high':math.exp(mu+tc*math.sqrt(tau+se*se)),
            'weights':{r['id']:wi/sw for r,wi in zip(rows,w)},
            'common_effect_HR':math.exp(m0),'common_effect_ci_low':math.exp(m0-Z/math.sqrt(s0)),
            'common_effect_ci_high':math.exp(m0+Z/math.sqrt(s0))}

def rr(a,n,c,m):
    if not all(isinstance(v,int) for v in (a,n,c,m)) or not (0<a<n and 0<c<m):
        raise ValueError('Positive integer binomial counts required.')
    y=math.log(a/n)-math.log(c/m);se=math.sqrt(1/a-1/n+1/c-1/m)
    return {'RR':math.exp(y),'ci_low':math.exp(y-Z*se),'ci_high':math.exp(y+Z*se),
            'source_counts':[a,n,c,m], 'not_admitted':True}

def run():
    obj=json.loads((HERE/'inputs.json').read_text());rows=obj['trials'];pooled=meta(rows)
    hashes=[{'id':r['id'],'expected':r['passage_sha256'],
             'computed':hashlib.sha256(r['passage'].encode('utf-8')).hexdigest()} for r in rows]
    ids=(HERE/'screening_ids.txt').read_text().splitlines();seed='20261008:omega3-cardiovascular-events:screen'
    ix=sorted(random.Random(seed).sample(range(len(ids)),5));picked=[ids[i] for i in ix]
    checks=[]
    def ck(n,c):
        checks.append({'name':n,'passed':bool(c)})
        if not c:raise AssertionError(n)
    for h in hashes:ck('Passage '+h['id'],h['expected']==h['computed'])
    components=component_tests()
    for name,ok in components['checks'].items():ck(name,ok)
    ck('Displayed pooled HR precision',round(pooled['HR'],4)==.9386)
    ck('Displayed HKSJ lower precision',round(pooled['ci_low'],4)==.8026)
    ck('Displayed HKSJ upper precision',round(pooled['ci_high'],4)==1.0977)
    ck('Displayed Q precision',round(pooled['Q'],2)==19.29)
    ck('Displayed I2 precision',round(pooled['I2_percent'],1)==74.1)
    ck('Displayed tau2 precision',round(pooled['tau2'],5)==.01292)
    ck('Weights sum',math.isclose(math.fsum(pooled['weights'].values()),1.))
    ck('Manual screening count and uniqueness',len(ids)==len(set(ids))==114)
    ck('Seeded positions',ix==[17,21,35,54,59])
    ck('Seeded identifiers',picked==['23351824','21145429','39059357','34468792','32745277'])
    return {'identity':{k:obj[k] for k in ('topic','slug','commit','review_sha256','status')},
            'scope':'Independent calculations using manually transcribed inputs. No production gates/replay.',
            'primary':pooled,'hashes':hashes,'component_recognition_tests':components,
            'leave_one_out_diagnostics':[{'omitted':r['id'],'result':meta(rows[:i]+rows[i+1:])} for i,r in enumerate(rows)],
            'screening_sample':{'source':'manual row-order transcription','seed':seed,'indices':ix,'ids':picked},
            'strength_bleeding_recovery_not_admitted':{
                'any_bleeding':rr(322,6532,322,6535),'TIMI_major_bleeding':rr(52,6532,46,6535)},
            'checks':checks,'checks_passed':len(checks)}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=HERE/'results.json');a=p.parse_args()
    try:
        r=run();a.output.write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
        print(json.dumps(r['primary'],indent=2));print('PASS',r['checks_passed'],'computational/fixture checks, not production gates')
    except (ValueError,AssertionError,OSError,ArithmeticError) as e:p.exit(1,f'FAIL: {e}\n')
