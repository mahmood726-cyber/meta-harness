"""Integration plants use synthetic defects or the held committed excerpt."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
from harness import recovery_binding as rb, recovery_excerpt as rx, recovery_map, lane_integration as lane, page
from scripts.make_react_excerpt import OUTPUT, HELD
from test_integrate2 import row, outcome, prepare

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'tocilizumab-covid19-mortality'


def review_fixture(root=ROOT):
    block = recovery_map.load_map(root)[SLUG]
    rows = [dict(id='PMID ' + e['pmid'], label=e['trial'], state='UNEXTRACTED')
            for e in block['entries'] if e.get('pmid')]
    review = dict(outcomes=[dict(name='28-day all-cause mortality', trials=[],
                                declared_absent_trials=rows, result=dict(k=0, present=False))])
    recovery_map.attach(review, SLUG, root=root)
    return review


def test_missing_held_file_binds_excerpt_and_never_pools(tmp_path):
    rels = [OUTPUT, rb.FIGURE_BINDING, 'docs/recovery_maps.json', f'cache/{SLUG}/records.json']
    rels += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'cache' / SLUG).glob('family_registry*')]
    for rel in rels:
        dest = tmp_path / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / rel).read_bytes())
    assert not (tmp_path / HELD).exists()
    review = review_fixture(tmp_path)
    numeric_before = deepcopy(review['outcomes'][0]['result'])
    rows = rb.attach(review, SLUG, root=tmp_path)
    assert len(rows) == len(review['outcomes'][0]['declared_absent_trials'])
    assert rows
    for binding in rows:
        assert (binding['state'], binding['binding'], binding['denominator'], binding['numerator']) == (
            'CROSS_PROVIDER_VERIFIED', 'CROSS_PROVIDER_VERIFIED', 'CROSS_PROVIDER_VERIFIED', 'CROSS_PROVIDER_VERIFIED')
        assert binding['evidence']['mode'] == 'COMMITTED_EXCERPT'
        assert binding['evidence']['parent_bytes_verified'] is False
        assert binding['evidence']['declared_parent_sha256'] == rx.SHA256
        assert set(binding['bound_values']) == {'n1i', 'n2i'}
        with pytest.raises(ValueError, match='RELAYED_COUNTS_NOT_BOUND'):
            rb.require_poolable(dict(binding, poolable=True, state='ANALYSIS_READY'))
    assert not review['outcomes'][0]['trials']
    assert review['outcomes'][0]['result'] == numeric_before
    assert all(r['result_status']['state'] == 'CROSS_PROVIDER_VERIFIED'
               for r in review['outcomes'][0]['declared_absent_trials'])


def test_corrupt_present_html_does_not_fall_back(tmp_path):
    path = tmp_path / HELD
    path.parent.mkdir(parents=True)
    path.write_bytes(b'<html>synthetic corrupt source</html>')
    with pytest.raises(ValueError, match='HELD_SHA256_MISMATCH'):
        rx.verify_local_html(tmp_path)


def test_excerpt_fallback_needs_no_optional_html_dependency(tmp_path):
    import subprocess
    import sys
    from scripts import make_react_excerpt as generator
    assert (rx.HELD, rx.OUTPUT, rx.SHA256) == (generator.HELD, generator.OUTPUT, generator.SHA256)
    path = tmp_path / OUTPUT
    path.parent.mkdir(parents=True)
    path.write_bytes((ROOT / OUTPUT).read_bytes())
    code = """import sys,json
sys.modules['bs4'] = None
from harness import recovery_excerpt
data = recovery_excerpt.load(sys.argv[1])
print(json.dumps(data['evidence']))
"""
    proc = subprocess.run([sys.executable, '-c', code, str(tmp_path)], cwd=ROOT,
                          capture_output=True, text=True, check=True)
    assert json.loads(proc.stdout)['mode'] == 'COMMITTED_EXCERPT'
    held = tmp_path / HELD
    held.parent.mkdir(parents=True)
    held.write_bytes(b'<html>synthetic present source</html>')
    refused = subprocess.run([sys.executable, '-c', code, str(tmp_path)], cwd=ROOT,
                             capture_output=True, text=True)
    assert refused.returncode == 0
    assert json.loads(refused.stdout)['mode'] == 'COMMITTED_EXCERPT'


@pytest.mark.parametrize('old,new,code', [
    (rx.SHA256, '0' * 64, 'SOURCE_UNBOUND'),
    ('participants with outcomes recorded.', 'all randomized participants.', 'POPULATION_UNBOUND'),
    ('161 | 82', '161.5 | 82', 'ARM_SIZE_UNBOUND'),
    ('Trial | NCT (or printed registration)', 'Trial | guessed ID', 'SCHEMA_UNBOUND'),
])
def test_malformed_excerpt_refused(old, new, code):
    raw = (ROOT / OUTPUT).read_bytes()
    assert old.encode() in raw
    with pytest.raises(ValueError, match=code):
        rx.parse_excerpt(raw.replace(old.encode(), new.encode()))


def test_denominator_conflict_and_negative_correct_row():
    block = deepcopy(recovery_map.load_map()[SLUG])
    evidence = rx.load(ROOT)
    assert all(r['denominator'] == 'BOUND' for r in rb.bind(block, evidence))
    block['entries'][0]['n1i'] += 1
    old = recovery_map.classify(block['entries'][0], block['population'], {'name': '28-day mortality'}, '')
    assert old['state'] == 'COUNTS_RECOVERED' and 'denominator' not in old
    new = rb.bind(block, evidence)[0]
    assert new['state'] == 'POPULATION_UNRESOLVED' and new['denominator'] == 'CONFLICT'
    assert new['bound_values'] == {} and 'DENOMINATOR_CONFLICT' in new['reason']


def test_unknown_measure_explains_classes_and_escapes_identifiers():
    o = outcome([row(), row(id='<img src=x onerror=bad()>', scale='HR')],
                result=dict(k=2, estimate=.8, ci_low=.6, ci_high=1.1, scale='RR'))
    lane.finish(o, {'estimand': 'RR'})
    assert o['result']['served_measure'] == 'UNKNOWN'
    rendered = page._outcome_block(o, show_inputs=False)
    assert 'Served measure UNKNOWN because input measure classes' in rendered
    assert 'HAZARD_RATIO' in rendered and 'RISK_RATIO' in rendered
    assert '&lt;img src=x onerror=bad()&gt;' in rendered and '<img src=x' not in rendered
    assert o['result']['estimate'] == .8


def test_homogeneous_measure_has_no_unknown_disclosure():
    o = outcome([row(), row(id='B')], result=dict(k=2, estimate=.8))
    prepare(o)
    assert o['served_measure'] == 'RISK_RATIO'
    assert 'Served measure UNKNOWN because' not in page._outcome_block(o, show_inputs=False)


def test_recovery_display_and_out_of_scope_routes_unchanged():
    review = review_fixture()
    rb.attach(review, SLUG)
    o = review['outcomes'][0]
    rendered = page._status_html(o['declared_absent_trials'][0], o)
    assert 'CROSS_PROVIDER_VERIFIED' in rendered and 'relayed:' in rendered
    foreign = dict(outcomes=[dict(name='Major bleeding', trials=[row()])])
    before = deepcopy(foreign)
    assert rb.attach(foreign, 'ticagrelor-vs-clopidogrel-acs') == []
    assert before == foreign


def test_real_pipeline_binding_and_no_own_source_pool_promotion():
    from harness import pipeline
    cfg = json.loads((ROOT / 'topics' / f'{SLUG}.json').read_text(encoding='utf-8'))
    records = json.loads((ROOT / 'cache' / SLUG / 'records.json').read_text(encoding='utf-8'))
    review = pipeline.build_review_core(SLUG, cfg, records, 'lane')
    primary = next(o for o in review['outcomes'] if o.get('primary'))
    assert primary['result']['served_measure'] == 'ODDS_RATIO'
    assert [r['id'] for r in primary['trials']] == ['PMID 33933206']
    assert primary['trials'][0]['reconstruction_measure'] == 'OR'
    mapped = [r for r in primary['declared_absent_trials'] if r.get('recovery_map')]
    assert mapped and all(r['recovery_binding']['binding'] == 'CROSS_PROVIDER_VERIFIED' for r in mapped)
    assert all(r['result_status']['state'] == 'CROSS_PROVIDER_VERIFIED' for r in mapped)
    assert primary['population'] == 'intention-to-treat'
    assert all(r['recovery_binding']['population_equivalence'] == 'NOT_ADJUDICATED' for r in mapped)
