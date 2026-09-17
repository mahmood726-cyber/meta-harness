import hashlib
import json
import subprocess
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import envelope, claimgraph
from harness.known_missing import _study_from_trial
from grade_arithmetic_sweep import LANE_BASE

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

reviews = sorted((ROOT / 'docs/reviews').glob('*/review.json'))
unchanged = []
for path in reviews:
    old = json.loads(subprocess.check_output(['git', 'show', LANE_BASE + ':' + path.relative_to(ROOT).as_posix()]))
    new = read(path)
    for field in ['outcomes', 'screening', 'search', 'comparator']:
        assert old[field] == new[field], (new['slug'], field)
    unchanged.append(new['slug'])
assert not subprocess.check_output(['git', 'diff', '--', 'harness/synth.py'])
alts = envelope._regulatory_alternatives(ROOT)
source_checks = []
for alt in alts:
    row = alt['row']
    verdict = claimgraph.verify_fact(row)
    assert verdict['verified'], verdict
    source_checks.append({'name': alt['name'], 'choice': alt['choice'], 'id': row['id'],
                          'effect': row['effect'], 'ci': [row['ci_low'], row['ci_high']],
                          'document_sha256': verdict['document_sha256'], 'verified': True,
                          'span': verdict['span']})
r = read(ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json')
p = envelope.primary(r)
result = envelope.calculate([_study_from_trial(t, 'HR') for t in p['trials']], 'HR')
sweep = read(ROOT / 'docs/grade_arithmetic_sweep.json')
envs = [read(ROOT / 'cache' / p.parent.name / 'envelope.json') for p in reviews]
obj = {'measurement': 'MEASURED', 'baseline_commit': LANE_BASE, 'pages': len(reviews), 'unchanged_membership_search_screening_comparator_pages': len(unchanged),
       'synth_unchanged': True, 'source_checks': source_checks,
       'computable_envelope_specs': sum(s['computable'] for e in envs for s in e['specifications']),
       'enumerated_envelope_specs': sum(len(e['specifications']) for e in envs),
       'baseline_d3_cap_pages': sum(bool((x['before'] or {}).get('certainty_capped_d3_unassessed')) for x in sweep['rows']),
       'glp1_numerical_diagnostic_only': {'warning': 'recalculation from legacy typed input rows; not a FACT-certified research result',
           'result': result, 'stored_page_estimate': p['result']['estimate'],
           'absolute_difference_unrounded': abs(result['estimate']-p['result']['estimate']),
           'absolute_difference_after_stored_four_decimal_rounding': abs(round(result['estimate'],4)-p['result']['estimate']),
           'concordant_below_null_trials': sum(t['effect'] < 1 for t in p['trials']),
           'n_trials': len(p['trials'])},
       'glp1_grade': r['grade']}
(ROOT / 'docs/gs_validation.json').write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({k: v for k, v in obj.items() if k not in {'source_checks', 'glp1_grade', 'glp1_numerical_diagnostic_only'}}, indent=2))
print('Regulatory controls:', [(a['name'], a['choice'], a['effect'], a['ci']) for a in source_checks])
