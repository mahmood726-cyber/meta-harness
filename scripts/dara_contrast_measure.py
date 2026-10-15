"""Acquire role-preserving registry ingredients; no research values are entered."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact


def cohort():
    catalog = json.loads((ROOT/'registry/benchmarks/candidates_v1_1.json').read_text(encoding='utf8'))
    return [Path(x['file']).stem for x in catalog['topic_sources']
            if (ROOT/'docs/reviews'/Path(x['file']).stem/'review.json').exists()]


def main():
    slugs = cohort() + ['daratumumab-rrmm-pfs-bench']
    records = {s: json.loads((ROOT/'cache'/s/'records.json').read_text(encoding='utf8')) for s in slugs}
    pmids = {str(r['id']) for d in records.values() for r in d['records']}
    links = {}
    required = {'study_references': {'pmid', 'nct_id', 'reference_type'},
                'design_groups': {'id', 'nct_id', 'group_type', 'title', 'description'},
                'interventions': {'id', 'nct_id', 'name', 'intervention_type'},
                'design_group_interventions': {'nct_id', 'design_group_id', 'intervention_id'}}
    def rows(table):
        path = aact._table(table)
        if not path:
            raise ValueError('Missing AACT table: '+table)
        with open(path, encoding='utf8') as f:
            if not required[table] <= set(f.readline().strip().split('|')):
                raise ValueError('Missing AACT columns: '+table)
        yield from aact._iter_rows(path)
    for r in rows('study_references'):
        if r.get('pmid') in pmids and r['reference_type'].upper() in aact.OWN_PUB_TYPES:
            links.setdefault(r['pmid'], []).append(r)
    wants = {}
    for s, d in records.items():
        wants[s] = {r.get('nct') or r['id'] for r in d['records'] + d.get('ctgov', [])
                    if str(r.get('nct') or r['id']).startswith('NCT')}
        wants[s].update(r['nct_id'] for p in d['records'] for r in links.get(str(p['id']), []))
    want = set().union(*wants.values())
    data = {n: {} for n in want}
    print('registry trials',len(want),flush=True)
    for table in ('design_groups', 'interventions', 'design_group_interventions'):
        for r in rows(table):
            if r['nct_id'] in want:
                data[r['nct_id']].setdefault(table, []).append(r)
        print('read',table,flush=True)
    for s, d in records.items():
        doc = {'source':'AACT', 'snapshot':Path(aact.snapshot_dir()).name,
               'records':{n:data[n] for n in sorted(wants[s])},
               'report_links':{str(r['id']):links[str(r['id'])] for r in d['records'] if str(r['id']) in links}}
        (ROOT/'cache'/s/'registry_contrast.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print('cached',s,flush=True)


if __name__ == '__main__':
    main()
