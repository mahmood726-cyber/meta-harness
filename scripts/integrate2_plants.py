"""Exact synthetic defect inputs, baseline gate output and wired gate output."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
if '--baseline' in sys.argv:
    from integrate2_helper import enable_baseline
    enable_baseline()
from harness import lane_integration as lane, screening_record, pipeline
from harness.synth import Study
from copy import deepcopy

def r(**kw):
    return dict(dict(id='plant-A',label='plant-A',effect=.8,ci_low=.6,ci_high=1.1,scale='RR',source='at 28 days'),**kw)
c={'id':'plant-A','label':'plant-A','ai':2,'n1i':20,'ci':4,'n2i':20,'source':'patients with events'}
cases={
 'TIMEPOINT_MISMATCH':([r(source='day 60')],{},[]),
 'TARGET_TIMEPOINT_MISSING':([r()],{'timepoint':None},[]),
 'MEASURE_MIX_POOLED':([r(),r(id='plant-B',scale='HR')],{},[]),
 'TARGET_MEASURE_REWRITTEN':([r()],{'estimand':'OR'},[]),
 'POPULATION_RULE_INCONSISTENT':([r(source='safety population')],{'kind':'harm'},[r(id='refused',source='safety population',reason_code='POPULATION_MISMATCH')]),
 'UNIT_MIX_POOLED':([c,dict(c,id='plant-B',source='5 episodes')],{},[]),
 'VARIANT_ROW_MISMATCH':([r(table_row={'variant_flags':['NON_CABG']})],{'name':'major bleeding'},[]),
 'RELAYED_COUNTS_NOT_BOUND':([r(provenance='RELAYED')],{},[]),
 'KM_PERCENT_TO_COUNT':([dict(c,source='Kaplan-Meier incidence 10%.')],{},[]),
 'SHARED_CONTROL_DOUBLE_COUNTED':([dict(c,trial_id='trial',control_id='control',control_n=20,control_events=4),dict(c,id='plant-B',trial_id='trial',control_id='control',control_n=20,control_events=4)],{},[]),
 'NEGATIVE_MATCH':([r(source='day 29; day 1 = inclusion')],{},[]),
}
results={}
for code,(rows,override,absent) in cases.items():
    spec=dict(name='event',estimand='RR',timepoint='28 days');spec.update(override)
    out=dict(name=spec['name'],kind=spec.get('kind','primary'),trials=deepcopy(rows),declared_absent_trials=deepcopy(absent))
    cfg={'harm_outcomes':[spec]} if out['kind']=='harm' else {'primary_outcome':spec}
    if '--baseline' not in sys.argv:
        lane.prepare(out,spec,cfg,{})
    issues=screening_record.consistency_problems({'outcomes':[out]})
    results[code]={'pooled_candidates':len(out['trials']), 'gate_kinds':[p['kind'] for p in issues],
                   'named_refusals':[t.get('lane_refusals') for t in out['declared_absent_trials'] if t.get('lane_refusals')]}
print(json.dumps(results,indent=2))
