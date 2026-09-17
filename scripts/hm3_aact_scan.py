"""Filter held AACT rows for the HM3 trial identifiers, offline."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact

rows = json.loads((ROOT / 'docs/evidence/hm3-held-source-audit/baseline-debt.json').read_text(encoding='utf-8'))
for row in rows:
    records = json.loads((ROOT/'cache'/row['slug']/'records.json').read_text(encoding='utf-8'))['records']
    row['record'] = next(r for r in records if str(r['id']) == row['id'])
pids = {r['id'] for r in rows}
want = set()
for r in rows:
    want.update(re.findall(r'NCT\d{8}', json.dumps(r['record'])))
    ft = ROOT / 'cache' / r['slug'] / ('ft_' + r['id'] + '.txt')
    if ft.exists():
        # Full-text references can name other trials; these rows are only candidates.
        want.update(re.findall(r'NCT\d{8}', ft.read_text(encoding='utf-8')))
snapshot = Path(aact.snapshot_dir())
out = ROOT / '.tmp/hm3/aact'
out.mkdir(parents=True, exist_ok=True)
refs = []
for r in aact._iter_rows(str(snapshot / 'study_references.txt')):
    if r.get('pmid') in pids and r.get('reference_type', '').upper() in aact.OWN_PUB_TYPES:
        want.add(r['nct_id'])
        refs.append(r)
(out / 'references.json').write_text(json.dumps(refs, indent=2), encoding='utf-8')
print('linked NCTs', len(want), flush=True)
for table in ['reported_events', 'outcome_counts', 'outcomes', 'result_groups', 'outcome_measurements', 'reported_event_totals']:
    path = snapshot / (table + '.txt')
    selected = []
    # Check nct_id before parsing the remaining fields of the multi-GB table.
    with path.open(encoding='utf-8') as f:
        header = f.readline()
        names = header.rstrip('\n').split('|')
        assert names[1] == 'nct_id', (table, names)
        for line in f:
            if line.split('|', 2)[1] in want:
                selected.append(line)
    (out / (table + '.txt')).write_text(header + ''.join(selected), encoding='utf-8')
    print(table, len(selected), flush=True)
(out / 'provenance.json').write_text(json.dumps({'snapshot_folder': snapshot.name,
    'selection': 'Exact NCT matches from held records/full texts and RESULT/DERIVED publication links; candidate rows require endpoint and arm adjudication.',
    'ncts': sorted(want)}, indent=2), encoding='utf-8')
