import copy
import hashlib
import pytest
from harness import recovery_map, recovery_excerpt
from harness.recovery_binding import bind, require_poolable
from scripts.make_react_excerpt import ROOT, HELD, parse, render, witness


@pytest.fixture
def held():
    return recovery_excerpt.load(ROOT)


@pytest.fixture
def block():
    return copy.deepcopy(recovery_map.load_map(ROOT)['tocilizumab-covid19-mortality'])


def test_matching_trials_bind_and_relay_is_never_poolable(block, held):
    for row in bind(block, held):
        assert row['denominator'] == 'BOUND'
        assert row['numerator'] == 'RELAYED'
        assert row['state'] == 'COUNTS_RECOVERED'
        assert row['binding'] == 'PARTIAL'
        with pytest.raises(ValueError, match='RELAYED_COUNTS_NOT_BOUND'):
            require_poolable(dict(row, state='ANALYSIS_READY', poolable=True))


def test_differing_size_conflicts_without_substitution(block, held):
    block['entries'][0]['n1i'] += 1
    row = bind(block, held)[0]
    assert row['denominator'] == 'CONFLICT'
    assert row['conflict_detail'][0]['field'] == 'n1i'
    assert row['bound_values'] == {}
    assert row['relayed_counts']['n1i'] == block['entries'][0]['n1i']


def test_acronym_ambiguity_abstains(block, held):
    held['rows'].append(copy.deepcopy(held['rows'][1]))
    row = bind(block, held)[0]
    assert row['denominator'] == 'RELAYED'
    assert 'AMBIGUOUS_TRIAL_IDENTITY' in row['reason']


def test_nct_authoritative_and_no_fallback(block, held):
    row = next(r for r in held['rows'] if r['trial'] == 'COVACTA')
    block['entries'] = [dict(block['entries'][1], nct=row['nct'], trial='different acronym')]
    assert bind(block, held)[0]['denominator'] == 'BOUND'
    block['entries'][0]['nct'] = 'NCT00000000'
    assert bind(block, held)[0]['denominator'] == 'RELAYED'


def test_remdacta_selected_population(block, held):
    block['entries'] = [e for e in block['entries'] if e['trial'] == 'REMDACTA']
    assert bind(block, held)[0]['denominator'] == 'BOUND'
    block['entries'][0].update(n1i=429, n2i=213)
    assert bind(block, held)[0]['denominator'] == 'CONFLICT'
    block['selected_outcome'] = {'name': 'Serious adverse events'}
    row = bind(block, held)[0]
    assert row['denominator'] == 'RELAYED'
    assert 'SELECTED_OUTCOME_POPULATION_NOT_HELD' in row['reason']


def test_population_mismatch_abstains(block, held):
    block['selected_outcome'] = {'name': '28-day mortality', 'population': 'all randomized'}
    assert all(r['state'] == 'POPULATION_UNRESOLVED' and r['denominator'] == 'RELAYED' for r in bind(block, held))


def test_deterministic_excerpt_and_source_integrity(held):
    if not (ROOT / HELD).exists():
        pytest.skip('optional local HTML verification: source not held; build uses committed excerpt')
    raw = (ROOT / HELD).read_bytes()
    held = parse(raw)
    assert render(held) == render(parse(raw))
    assert held['population']['state'] == 'OUTCOMES_RECORDED'
    assert {d['trial'] for d in held['deaths']} == {'COVIDSTORM', 'COVITOZ-01', 'TOCOVID'}
    assert all(d['total_deaths'] == 0 for d in held['deaths'])
    assert len(held['footnotes']) == 12
    with pytest.raises(ValueError, match='HELD_SHA256_MISMATCH'):
        parse(raw + b' ')
    assert witness('A &amp; B', '<p>A &amp; B</p>')['quote'] == 'A & B'
    with pytest.raises(ValueError, match='VERBATIM_NOT_HELD'):
        witness('invented count', raw.decode())


def test_multiarm_abstains(block, held):
    held['rows'][1]['intervention'].append(copy.deepcopy(held['rows'][1]['intervention'][0]))
    assert 'AMBIGUOUS_TABLE1_ARMS' in bind(block, held)[0]['reason']


def test_base_harness_pre_fix(block):
    e = dict(block['entries'][0], n1i=162)
    old = recovery_map.classify(e, block['population'], {'name': '28-day mortality'}, '')
    assert old['state'] == 'COUNTS_RECOVERED'
    assert old['provenance'] == 'RELAYED'
    assert 'denominator' not in old
    with pytest.raises(ValueError, match='RELAYED_COUNTS_NOT_BOUND'):
        recovery_map.require_poolable(old)


def test_explicit_deaths_and_unstated_population(block):
    if not (ROOT / HELD).exists():
        pytest.skip('optional local HTML verification: source not held; build uses committed excerpt')
    raw = (ROOT / HELD).read_bytes()
    raw = raw.replace(b'</body>', b'<p>COVACTA 28-day mortality: 58 deaths with tocilizumab and 28 deaths with placebo.</p></body>')
    data = parse(raw, hashlib.sha256(raw).hexdigest())
    row = bind(block, data)[1]
    assert row['numerator'] == 'BOUND'
    assert row['binding'] == 'COUNTS_BOUND_NOT_ADMITTED'
    with pytest.raises(ValueError):
        require_poolable(row)
    block['entries'][1]['ai'] += 1
    assert bind(block, data)[1]['numerator'] == 'RELAYED'
    raw = raw.replace(b'participants with outcomes recorded', b'participants in this analysis')
    assert parse(raw, hashlib.sha256(raw).hexdigest())['population']['state'] == 'UNSTATED'


def test_excluded_trial_and_short_acronym(block, held):
    source = next(r for r in held['rows'] if r['trial'] == 'STORM')
    block['entries'] = [dict(block['entries'][0], trial=source['trial'])]
    assert 'TRIAL_EXCLUDED_FROM_META_ANALYSIS' in bind(block, held)[0]['reason']
    block['entries'][0]['trial'] = 'AB'
    assert 'TRIAL_NOT_HELD' in bind(block, held)[0]['reason']


def test_excerpt_compatible_with_existing_table_parser(held, tmp_path):
    from harness.table_rows import parse as parse_table
    path = tmp_path / 'react.tables.txt'
    path.write_bytes((ROOT / recovery_excerpt.OUTPUT).read_bytes())
    tables = parse_table(path)
    assert len(tables) == 1
    assert len(tables[0]['rows']) == len(held['rows'])
