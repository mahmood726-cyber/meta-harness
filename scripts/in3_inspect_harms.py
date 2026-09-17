import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact
sys.stdout.reconfigure(encoding='utf-8')
p = ROOT / 'outputs/handover/in3/aact'
manifest = json.loads((p/'manifest.json').read_text())
groups = {r['id']: r for r in aact._iter_rows(str(p/'result_groups.txt'))}
events = list(aact._iter_rows(str(p/'reported_events.txt')))
totals = list(aact._iter_rows(str(p/'reported_event_totals.txt')))
terms = ['amput', 'ketoacidosis', 'genital', 'pancreatitis', 'hypogly', 'major bleed', 'total']
for item in manifest['identities']:
    print('\n',item)
    for r in totals:
        if r['nct_id'] in item['ncts']:
            print('TOTAL', r, groups.get(r.get('result_group_id'),{}).get('title'))
    for r in events:
        if r['nct_id'] in item['ncts'] and any(t in r.get('adverse_event_term','').lower() for t in terms):
            print('EVENT',r['event_type'],r['adverse_event_term'],r['subjects_affected'],r['subjects_at_risk'],groups.get(r['result_group_id'],{}).get('title'),r['time_frame'])
