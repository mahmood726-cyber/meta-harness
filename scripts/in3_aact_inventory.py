"""Retain exact-NCT candidate harm rows from the local snapshot; no network."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact

SLUGS = ['dapagliflozin-hfpef-hosp', 'doac-vte-recurrence',
         'dpp4-mace-t2d', 'sglt2-primary-prevention-hf']

def main():
    snapshot = Path(aact.snapshot_dir())
    out = ROOT / 'outputs/handover/in3/aact'
    out.mkdir(parents=True, exist_ok=True)
    identities = []
    for slug in SLUGS:
        review = json.loads((ROOT / f'docs/reviews/{slug}/review.json').read_text(encoding='utf-8'))
        included = {r['id'].replace('PMID ', '') for r in review['screening']['records'] if r['decision'] == 'include'}
        records = json.loads((ROOT / f'cache/{slug}/records.json').read_text(encoding='utf-8'))['records']
        for rec in records:
            if str(rec['id']) in included:
                identities.append(dict(slug=slug, pmid=rec['id'], ncts=sorted(set(re.findall(r'NCT\d{8}', json.dumps(rec))))))
    want = {n for r in identities for n in r['ncts']}
    manifest = dict(snapshot_folder=snapshot.name, identities=identities, tables={})
    for table in ('reported_events', 'reported_event_totals', 'result_groups'):
        source = snapshot / (table + '.txt')
        with source.open(encoding='utf-8') as f:
            header = f.readline()
            assert header.split('|')[1] == 'nct_id'
            selected = [line for line in f if line.split('|', 2)[1] in want]
        data = (header + ''.join(selected)).encode('utf-8')
        (out / source.name).write_bytes(data)
        manifest['tables'][source.name] = dict(rows=len(selected), sha256=hashlib.sha256(data).hexdigest())
        print(table, len(selected), flush=True)
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')

if __name__ == '__main__':
    main()
