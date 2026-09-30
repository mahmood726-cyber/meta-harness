"""Synthetic table plants and executable offline census (no evidence writes)."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy

import pytest
from harness import proposal_gate as gate

helpers = runpy.run_path(str(Path(__file__).with_name('test_proposal_gate_documents.py')))
field = helpers['field']


def plant(root, kind='correct', media='text/html'):
    p, registry = helpers['registered'](root, media)
    topic_path = root / 'topics/plant.json'
    topic = json.loads(topic_path.read_text())
    topic['registry_first'] = {'intr': 'tocilizumab'}
    if kind == 'unbound_scope':
        topic.pop('registry_first')
    topic_path.write_text(json.dumps(topic), encoding='utf-8')
    header = ('<tr><th rowspan="2">Trial</th><th rowspan="2">Trial registration No.</th>'
              '<th rowspan="2">Treatment group</th><th colspan="2">Baseline</th></tr>'
              '<tr><th>No. of patients</th><th>Age</th></tr>')
    body = ('<tr><td colspan="5">Tocilizumab</td></tr>'
            '<tr><td rowspan="2">ALPHA</td><td rowspan="2">NCT00000001</td>'
            '<td>Anti–IL-6</td><td>20</td><td>77</td></tr>'
            '<tr><td>Usual care</td><td>21</td><td>78</td></tr>'
            '<tr><td>BETA</td><td>NCT00000002</td><td>Anti–IL-6</td><td>99</td><td>80</td></tr>'
            '<tr><td colspan="5">Sarilumab</td></tr>'
            '<tr><td>ALPHA</td><td>NCT00000001</td><td>Anti–IL-6</td><td>88</td><td>79</td></tr>')
    if kind == 'malformed':
        body = body.replace('rowspan="2"', 'rowspan="bad"', 1)
    if kind == 'relayed':
        body = body.replace('Tocilizumab</td>', 'Investigator-supplied Tocilizumab</td>')
    if kind == 'range':
        body = body.replace('rowspan="2"', 'rowspan="999"', 1)
    if kind == 'overlap':
        header = header.replace('rowspan="2">Trial</th>', '>Trial</th>')
        header = header.replace('<tr><th>No. of patients', '<tr><th colspan="2">No. of patients')
    if kind == 'ambiguous':
        body += ('<tr><td colspan="5">Tocilizumab</td></tr>'
                 '<tr><td>ALPHA</td><td>NCT00000001</td><td>Anti–IL-6</td><td>20</td><td>77</td></tr>')
    raw = '<article><p>Outcome: Mortality at 28 days.</p><table>' + header + body + '</table></article>'
    (root / p['document_ref']).write_text(raw, encoding='utf-8')
    p['document_sha256'] = hashlib.sha256(raw.encode()).hexdigest()
    data = json.loads(registry.read_text()); data['documents'][0]['sha256'] = p['document_sha256']
    registry.write_text(json.dumps(data), encoding='utf-8')
    rows = gate.parse_html(raw).find_all('tr')
    text = lambda r: gate.flat(r.get_text(' ', strip=True))
    row = dict.fromkeys(gate.TRIAL)
    row.update(label='ALPHA', registration='NCT00000001', n_1=20, n_2=21,
               span=' '.join(text(r) for r in rows[3:5]),
               field_spans={'n_1': text(rows[3]), 'n_2': text(rows[4])})
    if kind in ('other_row', 'sarilumab'):
        index = 5 if kind == 'other_row' else 7
        row['n_1'] = 99 if kind == 'other_row' else 88
        row['span'] = ' '.join(text(r) for r in rows[3:])
        row['field_spans']['n_1'] = text(rows[index])
    elif kind == 'wrong_header':
        row['n_1'] = 77
    elif kind == 'wrong_identity':
        row['registration'] = 'NCT00000002'
        row['span'] = ' '.join(text(r) for r in rows[3:])
    elif kind == 'wrong_arm':
        row['n_1'] = 21
        row['field_spans']['n_1'] = text(rows[4])
    elif kind == 'ambiguous':
        row['span'] = ' '.join(text(r) for r in rows[3:])
    p['trials'] = [row]
    return p


@pytest.mark.parametrize('media', ['text/html', 'application/jats+xml'])
def test_correct_rowspan_and_header_tiers(tmp_path, media):
    got = gate.verify(plant(tmp_path, media=media), tmp_path)
    assert got['status'] == 'accepted'
    for key in ('n_1', 'n_2'):
        binding = field(got, 'trials.0.' + key)['table_path']
        assert binding['headers'] == ['Baseline', 'No. of patients']
        assert binding['column'] == 3
        assert binding['label_origin'] == [3, 0]
    assert field(got, 'trials.0.n_2')['table_path']['row'] == 4


@pytest.mark.parametrize('kind', ['other_row', 'sarilumab', 'wrong_header', 'wrong_identity',
                                 'wrong_arm', 'malformed', 'relayed', 'range', 'overlap',
                                 'ambiguous', 'unbound_scope'])
def test_refusal_plants(tmp_path, kind):
    got = field(gate.verify(plant(tmp_path, kind), tmp_path), 'trials.0.n_1')
    assert got['status'] == 'rejected'
    assert got['reason'].startswith('REFUSED_TABLE_')


def test_nested_table_scope_and_header_footnotes():
    raw = ('<table><tr><th>No. of patients<sup>a</sup><xref>b</xref></th></tr>'
           '<tr><th scope="row">ALPHA</th><td>20 &amp; 21'
           '<table><tr><td>inner</td></tr></table></td></tr></table>')
    rows, errors = gate._table_rows(raw, 'text/html')
    assert not errors
    assert [(r['table'], r['row']) for r in rows] == [(0, 1), (1, 0)]
    assert rows[0]['headers'] == {0: ['No. of patients']}
    assert rows[0]['cells'][1]['text'] == '20 & 21 inner'
    assert rows[1]['span'] == 'inner'


@pytest.mark.skipif(
    not (gate.ROOT / 'evidence/acquisition_cascade/held/WHO-REACT/PMC8261689.local.html').is_file(),
    reason='WHO REACT AMA page held locally only')
def test_corpus_proposal():
    p = helpers['rebuild_toci']()
    result = gate.verify(p)
    assert result['status'] == 'accepted'
    assert sum(f['status'] == 'accepted' for f in result['fields']) == 78
    assert sum('table_path' in f for f in result['fields']) == 36


def census():
    """Scan every topic and every registered table; replay the held lane proposal.

    Kept in the permitted test file because this lane's write list does not
    authorize a new scripts/ file. This is also the executable census entrypoint.
    """
    import tempfile
    records = []
    for kind in ('correct', 'other_row', 'sarilumab', 'wrong_header', 'wrong_identity',
                 'wrong_arm', 'malformed', 'relayed', 'range', 'overlap', 'ambiguous', 'unbound_scope'):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            p = plant(root, kind)
            records.append({'plant': kind, 'result': field(gate.verify(p, root), 'trials.0.n_1')})
    p = helpers['rebuild_toci']()
    after = gate.verify(p)
    # Replay the pre-table gate route, which was the applied GATEDOC baseline
    # (HEAD predates GATEDOC and would reject the whole registered document).
    original = gate._table_count
    try:
        gate._table_count = lambda *args: ('REFUSED_NUMBER_ROLE_NOT_IN_OWN_SPAN', None)
        before = gate.verify(p)
    finally:
        gate._table_count = original
    proposed = [f for f in after['fields'] if f['status'] != 'not_proposed']
    changed = []
    for old, new in zip(before['fields'], after['fields']):
        if old['status'] == 'rejected':
            _, index, key = old['path'].split('.')
            item = p['trials'][int(index)]
            changed.append(dict(path=old['path'], label=item['label'], value=item[key],
                                classification='b' if new['status'] == 'accepted' else 'unresolved',
                                before=old['reason'], after=new))
    documents = json.loads((gate.ROOT / gate.DOCUMENT_REGISTRY).read_text())['documents']
    coverage = []
    for path in sorted((gate.ROOT / 'topics').glob('*.json')):
        topic = json.loads(path.read_text(encoding='utf-8'))
        docs = []
        for entry in documents:
            if entry['slug'] != path.stem:
                continue
            probe = deepcopy(p)
            probe.update(slug=path.stem, comparator_pmid=str(topic['comparator_pmid']),
                         document_ref=entry['document_ref'], document_sha256=entry['sha256'])
            try:
                _, _, _, normalise = gate._source(probe, gate.ROOT)
                rows, errors = gate._table_rows(*normalise.table_source) if hasattr(normalise, 'table_source') else ([], [])
                docs.append(dict(document_ref=entry['document_ref'], rows_examined=len(rows),
                                 table_errors=errors))
            except (ValueError, OSError) as exc:
                docs.append(dict(document_ref=entry['document_ref'], refusal=str(exc)))
        coverage.append(dict(topic=path.stem, documents=docs,
                             proposal_replayed=path.stem == p['slug']))
    def metric(items, total):
        return dict(n=len(items), N=total, n_of_N=f'{len(items)} of {total}', items=items)
    return dict(plants=records,
                before=metric([f['path'] for f in before['fields'] if f['status']=='accepted'], len(proposed)),
                after=metric([f['path'] for f in proposed if f['status']=='accepted'], len(proposed)),
                rules={'TABLE_ROLE_RECOVERED': metric([r['path'] for r in changed if r['classification']=='b'], len(proposed)),
                       'REMAINING_REFUSED': metric([f for f in proposed if f['status']=='rejected'], len(proposed)),
                       'TOPICS_WITH_REGISTERED_TABLE_SOURCE': metric([r['topic'] for r in coverage if r['documents']], len(coverage)),
                       'REGISTERED_DOCUMENT_TABLE_ERRORS': metric([dict(topic=r['topic'], **d) for r in coverage for d in r['documents'] if d.get('refusal') or d.get('table_errors')], sum(len(r['documents']) for r in coverage))},
                classifications=changed, topic_coverage=coverage)


if __name__ == '__main__':
    print(json.dumps(census(), indent=2))
