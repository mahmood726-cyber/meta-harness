"""Independent audit checks for topic 29. Standard library only; no network.
Run: python audit.py [--output PATH]
Not a harness checkout, production-gate test, or full review replay.
"""
from pathlib import Path
import argparse,hashlib,json,math,random
from independent_math import meta
from endpoint_excerpt import _component_set,_registered_text,_outcome_match_detail

ROOT=Path(__file__).resolve().parent

def run():
    d=json.loads((ROOT/'inputs.json').read_text())
    checks=[]
    def check(name,condition):
        checks.append({'check':name,'passed':bool(condition)})
        if not condition:raise AssertionError(name)
    main=meta(d['primary'])
    v3=meta(d['primary']+[d['vesalius_three_point']])
    v4=meta(d['primary']+[d['vesalius_four_point']])
    check('Primary point estimate matches reference independent reconstruction',math.isclose(main['HR'],.826135182192134,abs_tol=1e-12))
    check('Primary rounds to displayed 0.8261',round(main['HR'],4)==.8261)
    check('Primary Q rounds to displayed 0.8575',round(main['Q'],4)==.8575)
    check('Primary PM tau squared is zero',main['tau2']==0)
    check('Primary I-squared is zero',main['I2_percent']==0)
    check('Primary reconstructed HKSJ interval spans null',main['ci_low']<1<main['ci_high'])
    check('VESALIUS three-point diagnostic point estimate',math.isclose(v3['HR'],.8106468572101903,abs_tol=1e-12))
    check('VESALIUS four-point diagnostic point estimate',math.isclose(v4['HR'],.8213481072296869,abs_tol=1e-12))
    hashes=[]
    for p in d['passages']:
        observed=hashlib.sha256(p['text'].encode('utf-8')).hexdigest()
        check('Displayed passage digest '+p['trial'],observed==p['sha256'])
        hashes.append({'trial':p['trial'],'expected':p['sha256'],'computed':observed})
    indices=sorted(random.Random(d['screening_seed']).sample(range(len(d['screening_ids'])),5))
    check('Seeded indices from manually transcribed screening order',indices==[1,3,4,5,6])
    selected=[d['screening_ids'][i] for i in indices]
    target=d['d5_generic_target']
    pri=d['odyssey_registered_primary'];death=d['odyssey_registered_chd_death']
    pc=sorted(_component_set(_registered_text(pri)));dc=sorted(_component_set(_registered_text(death)))
    check('Generic MACE expands to three components',sorted(_component_set(target))==['CV_DEATH','NONFATAL_MI','NONFATAL_STROKE'])
    check('Original primary definition loses CHD death in this parser',pc==['NONFATAL_MI','NONFATAL_STROKE','UNSTABLE_ANGINA'])
    check('CHD death alone produces no recognized components',dc==[])
    primary_default=_outcome_match_detail(target,pri,None)
    death_default=_outcome_match_detail(target,death,None)
    death_permissive=_outcome_match_detail(target,death,lambda a,b:True)
    primary_permissive=_outcome_match_detail(target,pri,lambda a,b:True)
    check('Generic target rejects actual four-component primary',primary_default['matched'] is False)
    check('Without supplied callback the CHD-death fixture is NOT matched',death_default['matched'] is False)
    check('Synthetic permissive callback permits death-only text-identity match',death_permissive['matched'] and death_permissive['method']=='text_identity')
    check('Nonempty incompatible component sets override permissive callback',primary_permissive['matched'] is False)
    explicit={'measure':'Cardiovascular death, nonfatal myocardial infarction, or stroke'}
    check('Explicit exact three-point synthetic control matches',_outcome_match_detail(target,explicit,None)['matched'])
    out={
      'scope':d['input_origin'],
      'primary_independent_reconstruction':dict(main,ci_publication_status='HKSJ interval withheld on pinned page; reconstructed here only for audit'),
      'vesalius_3point_known_gap_diagnostic':dict(v3,not_admitted=True,known_before_this_audit=True),
      'vesalius_4point_alternative_diagnostic':dict(v4,not_admitted=True),
      'passage_hashes':hashes,
      'screening_sample':{'seed':d['screening_seed'],'indices':indices,'ids':selected,'origin':'manually transcribed displayed order'},
      'isolated_component_checks':{'primary_components':pc,'death_components':dc,
       'primary_no_callback':primary_default,'death_no_callback':death_default,
       'death_synthetic_permissive_callback':death_permissive,'primary_synthetic_permissive_callback':primary_permissive,
       'limit':d['test_scope']},
      'checks':checks,'checks_passed':sum(x['passed'] for x in checks),'checks_total':len(checks)}
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'results.json')
    args=ap.parse_args()
    result=run()
    args.output.write_text(json.dumps(result,indent=2,ensure_ascii=False,sort_keys=True)+'\n')
    print(f"{result['checks_passed']}/{result['checks_total']} computational and fixture checks passed.")
    print('Primary HR:',result['primary_independent_reconstruction']['HR'])
    print('Output:',args.output)
