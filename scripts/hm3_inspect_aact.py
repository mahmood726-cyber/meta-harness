"""Print outcome-matched candidate rows, without inferring aggregate counts."""
import json
import re
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact

sys.stdout.reconfigure(encoding='utf-8')
folder = ROOT / '.tmp/hm3/aact'
rows = json.loads((ROOT / 'docs/evidence/hm3-held-source-audit/baseline-debt.json').read_text(encoding='utf-8'))
for row in rows:
    records = json.loads((ROOT/'cache'/row['slug']/'records.json').read_text(encoding='utf-8'))['records']
    row['record'] = next(r for r in records if str(r['id']) == row['id'])
refs = json.loads((folder / 'references.json').read_text(encoding='utf-8'))
events = list(aact._iter_rows(str(folder / 'reported_events.txt')))
outcomes = list(aact._iter_rows(str(folder / 'outcomes.txt')))
groups = {r['id']: r for r in aact._iter_rows(str(folder / 'result_groups.txt'))}
for i, item in enumerate(rows):
    if len(sys.argv) > 1 and i not in {int(x) for x in sys.argv[1:]}:
        continue
    ncts = set(re.findall(r'NCT\d{8}', json.dumps(item['record'])))
    ncts.update(r['nct_id'] for r in refs if r['pmid'] == item['id'])
    terms = {'Serious adverse events': ['total', 'serious adverse'], 'Adverse events': ['total', 'any adverse', 'at least one', 'one or more'],
             'Bleeding': ['bleed', 'haemorr', 'hemorr'], 'Atrial fibrillation': ['atrial fib', 'atrial flutter'],
             'Acute kidney injury': ['kidney', 'renal'], 'Gastrointestinal adverse events': ['gastrointestinal'],
             'Hyperkalemia': ['hyperkal', 'potassium'], 'Gynecomastia or breast pain': ['gyn', 'breast pain'],
             'Hyperglycaemia': ['hypergly', 'glucose'], 'Gastrointestinal bleeding': ['gastrointestinal', 'gastric', 'haemorr', 'hemorr'],
             'Treatment discontinuation due to adverse events': ['discontin'], 'Lower-limb amputation': ['amputation'],
             'Volume depletion or hypotension': ['volume depletion', 'hypotension', 'dehydration'],
             'Diabetic ketoacidosis': ['ketoacidosis'], 'Muscle symptoms/myopathy': ['myalgia', 'myopathy', 'muscle'],
             'New-onset diabetes': ['diabetes'], 'Major bleeding': ['bleed'], 'Serious infection': ['infection']}[item['outcome']]
    print('\nITEM', i, item['slug'], item['id'], item['outcome'], sorted(ncts))
    for r in outcomes:
        if r['nct_id'] in ncts and any(t in (r.get('title','')+' '+r.get('description','')).lower() for t in terms):
            print('OUTCOME', json.dumps(r, ensure_ascii=False))
    matches = [r for r in events if r['nct_id'] in ncts and any(t in r.get('adverse_event_term','').lower() for t in terms)]
    for r in matches:
        print('EVENT',r['nct_id'], r['event_type'], r['adverse_event_term'], r['subjects_affected'], '/',r['subjects_at_risk'],
              groups.get(r['result_group_id'],{}).get('title'), r['time_frame'], 'group', r['result_group_id'])
    print('event matches', len(matches), 'total held event rows', sum(r['nct_id'] in ncts for r in events))
