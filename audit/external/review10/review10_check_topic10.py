#!/usr/bin/env python3
"""Independent GLP-1 numerical and audit-pack passage checks.
Not a replay of meta-harness and not a release-byte verification.
Requires numpy and scipy. Inputs are transcribed from primary trial reports.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq
from scipy.stats import t

TRIALS = [
    {'trial':'LEADER','pmid':'27295427','hr':0.87,'low':0.78,'high':0.97},
    {'trial':'SUSTAIN-6','pmid':'27633186','hr':0.74,'low':0.58,'high':0.95},
    {'trial':'EXSCEL','pmid':'28910237','hr':0.91,'low':0.83,'high':1.00},
    {'trial':'PIONEER 6','pmid':'31185157','hr':0.79,'low':0.57,'high':1.11},
    {'trial':'REWIND','pmid':'31189511','hr':0.88,'low':0.79,'high':0.99},
    {'trial':'HARMONY Outcomes','pmid':'30291013','hr':0.78,'low':0.68,'high':0.90},
    {'trial':'AMPLITUDE-O','pmid':'34215025','hr':0.73,'low':0.58,'high':0.92},
    {'trial':'SOUL','pmid':'40162642','hr':0.86,'low':0.77,'high':0.96},
]
# The passages below are USER-SUPPLIED pack strings (HTML entities decoded).
# A match proves internal integrity of those strings, not byte identity of a source.
PASSAGES = [
    ('REWIND', 'During a median follow-up of 5.4 years (IQR 5.1-5.9), the primary composite outcome occurred in 594 (12.0%) participants at an incidence rate of 2.4 per 100 person-years in the dulaglutide group and in 663 (13.4%) participants at an incidence rate of 2.7 per 100 person-years in the placebo group (hazard ratio [HR] 0.88, 95% CI 0.79-0.99; p=0.026).', 'a6727b8f1c568f521dcd0af47eb282d92c4d4d74549f4c0117d1ff6a8babdd21'),
    ('HARMONY Outcomes', 'The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years in the placebo group (hazard ratio 0.78, 95% CI 0.68-0.90), which indicated that albiglutide was superior to placebo (p<0.0001 for non-inferiority; p=0.0006 for superiority).', '84bffc37208ed47a6a27b221ee0541074acda0b976f5365920e61c7ace9ac490'),
    ('SOUL', 'Among the 9650 participants who had undergone randomization, a primary-outcome event occurred in 579 of the 4825 participants (12.0%) in the oral semaglutide group, as compared with 668 of the 4825 participants (13.8%) in the placebo group (hazard ratio, 0.86; 95% confidence interval, 0.77 to 0.96; P = 0.006).', 'f35b4ae15e44ab12d463106384f7b6845f09aef61ceac28f00b281b2a94866be'),
]

def pool(rows: list[dict]) -> dict:
    """Paule-Mandel tau2, modified Hartung-Knapp with variance floor 1."""
    k = len(rows)
    if k < 2:
        raise ValueError('At least two independent trials required.')
    a=np.array([[r['hr'],r['low'],r['high']] for r in rows],dtype=float)
    if (not np.all(np.isfinite(a)) or np.any(a <= 0) or
        np.any(a[:,1] >= a[:,2]) or np.any(a[:,0] < a[:,1]) or
        np.any(a[:,0] > a[:,2])):
        raise ValueError('Invalid positive ratio estimate or confidence interval.')
    y=np.log(a[:,0]); v=((np.log(a[:,2])-np.log(a[:,1]))/(2*1.96))**2
    def calc(tau: float):
        w=1/(v+tau); m=float(np.sum(w*y)/sum(w)); q=float(np.sum(w*(y-m)**2))
        return w,m,q
    q0=calc(0)[2]; df=k-1
    if q0 <= df:
        tau=0.
    else:
        hi=.01
        while calc(hi)[2] > df: hi *= 2
        tau=float(brentq(lambda x:calc(x)[2]-df,0,hi,xtol=1e-15))
    w,mu,q=calc(tau)
    scale=max(1.,q/df)
    se=float(math.sqrt(scale/sum(w)))
    crit=float(t.ppf(.975,df))
    ci=[float(math.exp(mu-crit*se)),float(math.exp(mu+crit*se))]
    # This follows the PINNED PROTOCOL's t(k-1) prediction-interval rule.
    # It is descriptive for this subset, not a complete-evidence prediction claim.
    pse=math.sqrt(tau+se*se)
    pi=[math.exp(mu-crit*pse),math.exp(mu+crit*pse)]
    return {'k':k,'hr':math.exp(mu),'ci95_modified_HKSJ':ci,'tau2_PM':tau,
            'Q_fixed':q0,'I2_percent':max(0.,(q0-df)/q0)*100 if q0 else 0.,
            'HK_scale_floor1':scale,'prediction_interval_protocol_t_kminus1':pi,
            'weights_percent':{r['trial']:float(100*x/sum(w)) for r,x in zip(rows,w)}}

def main() -> None:
    checks=[]
    for name, passage, expected in PASSAGES:
        digest=hashlib.sha256(passage.encode('utf-8')).hexdigest()
        checks.append({'trial':name,'sha256':digest,'expected':expected,'matches':digest==expected})
    report={'scope':'Independent numerical reconstruction, not repository replay',
            'requested_review_sha256':'24ee84995837c07894748a8056c9fc95b1d17140b96686b858b9f1107a9dcfd2',
            'trials':TRIALS,'pack_passage_checks':checks,'eight_trial_pool':pool(TRIALS),
            'FLOW_sensitivity_warning':'Illustrative addition only; not the complete corrected pool and not a served result.',
            'FLOW_sensitivity_source':'https://pubmed.ncbi.nlm.nih.gov/39211948/',
            'FLOW_added_pool':pool(TRIALS+[{'trial':'FLOW','pmid':'39211948','hr':0.82,'low':0.68,'high':0.98}])}
    folder=Path(__file__).resolve().parent
    (folder/'calculation_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))
    if not all(x['matches'] for x in checks):
        raise SystemExit('One or more USER-SUPPLIED passage digests do not match.')
if __name__ == '__main__':main()
