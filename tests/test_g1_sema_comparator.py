"""Plants replay the unchanged native gate as well as the lane's typed rules."""
import copy
import json
import pytest
from scripts import g1_sema_comparator as lane

_manifest = lane.read(lane.ROOT / 'comparator_refs/MANIFEST.json')[lane.SLUG]
local_document = pytest.mark.skipif(
    not (lane.ROOT / 'comparator_refs' / _manifest['file']).is_file(),
    reason='Semaglutide CC BY-NC XML held locally only')


@pytest.fixture(scope='module')
def held():
    if not (lane.ROOT / 'comparator_refs' / _manifest['file']).is_file():
        pytest.skip('Semaglutide CC BY-NC XML held locally only')
    return lane.run()


def field(g, path):
    return next(f for f in g['fields'] if f['path'] == path)


def plants():
    p, e, g, c = lane.run()
    outputs = []
    first, second = [i for i,r in enumerate(p['trials']) if r['n_1'] is not None][:2]
    bad = copy.deepcopy(p)
    bad['trials'][first]['n_1'] = bad['trials'][second]['n_1']
    bad['trials'][first]['field_spans']['n_1'] = bad['trials'][second]['field_spans']['n_1']
    native = field(lane.gate.verify(bad, lane.ROOT), f'trials.{first}.n_1')
    try:
        lane.binding(e['trials'][first], 'Active (n)', e['trials'][second]['fields']['Active (n)'])
    except ValueError as ex:
        outputs.append(dict(plant='other_row', before=native, after=str(ex)))
    # Base literal gate accepts '+' as an outcome string, regardless of endpoint role.
    bad_endpoint = copy.deepcopy(p)
    bad_endpoint['primary_scope'].update(outcome_as_printed='+', span=e['trials'][0]['fields']['CV mortality']['span'])
    endpoint = field(lane.gate.verify(bad_endpoint, lane.ROOT), 'primary_scope.outcome_as_printed')
    try:
        lane.mace_flag('CV mortality', '+')
    except ValueError as ex:
        outputs.append(dict(plant='different_endpoint', before=endpoint, after=str(ex)))
    for drug in ('tirzepatide', 'liraglutide'):
        i = next(i for i,r in enumerate(e['trials']) if r['drug_scope'] == 'REFUSED_DIFFERENT_DRUG:' + drug)
        outputs.append(dict(plant=drug, before=field(g, f'trials.{i}.label'), after=lane.drug_scope(e['trials'][i]['fields']['Medication/type']['value'])))
    duplicate = copy.deepcopy(p)
    duplicate['trials'].append(copy.deepcopy(duplicate['trials'][0]))
    base_gate = lane.gate.verify(duplicate, lane.ROOT)
    try:
        lane.validate_ledger(e['all_rows'] + [e['all_rows'][0]], [r['path'] for r in e['all_rows']])
    except ValueError as ex:
        outputs.append(dict(plant='duplicate_denominator', before=field(base_gate, f"trials.{len(p['trials'])}.label"), after=str(ex)))
    return outputs


@local_document
def test_plants():
    results = plants()
    assert len(results) == 5
    assert all(r['after'].startswith('REFUSED_') for r in results)
    assert results[0]['before']['status'] == 'rejected'
    assert results[1]['before']['reason'] is None
    assert all(r['before']['status'] == 'accepted' for r in results[2:4])


def test_negative_plants(held):
    p, e, g, c = held
    row = next(r for r in e['trials'] if r['drug_scope'] == 'SEMAGLUTIDE_ONLY')
    assert lane.binding(row, 'Active (n)', row['fields']['Active (n)'])['value']
    assert lane.mace_flag('MACE', '+') is True
    assert lane.mace_flag('MACE', '') is False
    assert lane.drug_scope('Semaglutide or placebo') == 'SEMAGLUTIDE_ONLY'
    lane.validate_ledger(e['all_rows'], [r['path'] for r in e['all_rows']])


def test_every_physical_row_once(held):
    _, tree = lane.load()
    rows = held[1]['all_rows']
    assert len(rows) == len(tree.findall('.//table-wrap//tr'))
    assert len({r['path'] for r in rows}) == len(rows)
    with pytest.raises(ValueError, match='DENOMINATOR'):
        lane.validate_ledger(rows[:-1], [r['path'] for r in rows])


def test_mace_column_not_cv_death(held):
    _, tree = lane.load()
    for tr in tree.find('.//table-wrap').findall('.//tr')[1:]:
        list(tr)[8].text = ''
        list(tr)[10].text = '+'
    rows, _, _ = lane.extract(tree)
    assert not any(r['mace'] for r in rows)


def test_unknown_marker_refused():
    with pytest.raises(ValueError, match='OUTCOME_MARKER'):
        lane.mace_flag('MACE', '++')


def test_counts_are_not_fabricated(held):
    p, e, g, c = held
    assert all(r['n_2'] is None and r['events_1'] is None and r['events_2'] is None and r['effect'] is None for r in p['trials'])
    assert all(r['n_1'] is None for r,s in zip(p['trials'], e['trials']) if s['drug_scope'] != 'SEMAGLUTIDE_ONLY')
    assert all(r['n_1'] is None for r in g['accepted']['trials'])
    assert lane.drug_scope('semaglutide or liraglutide or placebo') == 'REFUSED_MIXED_DRUG_ARMS'


def test_source_and_native_gate(held):
    p, e, g, c = held
    assert g['reason'] is None
    assert all(f['reason'] == 'REFUSED_TABLE_ROW_HEADER_ARM_BINDING:n_1' for f in g['fields'] if f['status'] == 'rejected')
    assert g['accepted']['pooled']['k'] == e['pooled']['k']
    bad = copy.deepcopy(p)
    bad['document_sha256'] = '0' * 64
    assert lane.gate.verify(bad, lane.ROOT)['reason'] == 'REFUSED_DOCUMENT_SHA256_MISMATCH'


def test_reference_drug_and_k_contract(held):
    c = held[3]['comparison']
    assert c['membership_count_agrees']
    assert c['K_MATCH'] == ('yes' if c['comparator_k'] == c['our_served_k'] else 'no')
    assert len(c['comparator_only']) + c['our_served_k'] == c['comparator_k']
    assert c['ours_only'] == []
    for r in c['trials']:
        if r.get('our_label'):
            assert r['drug_scope'] == 'SEMAGLUTIDE_ONLY'
            assert any(j.get('key') in ('pmids', 'dois') for j in r['identity_joins'])


@local_document
def test_relayed():
    _, tree = lane.load()
    cell = tree.find('.//table-wrap').findall('.//tr')[1][4]
    cell.text = 'investigator-supplied'
    with pytest.raises(ValueError, match='RELAYED_NOT_DATA'):
        lane.extract(tree)


if __name__ == '__main__':
    print(json.dumps(plants(), ensure_ascii=False, indent=2))
