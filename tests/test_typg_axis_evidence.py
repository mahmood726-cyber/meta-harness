import hashlib
from pathlib import Path

from harness import effect_type as ty

ROOT = Path(__file__).resolve().parents[1]


def test_unlocated_censoring_span_is_refused():
    path = 'cache/glp1-ra-mace-t2d/records.json'
    row = {'id': 'plant', 'effect_type_evidence': {'censoring': {
        'value': 'end-of-study', 'basis': {
            'source': path, 'document_path': path,
            'document_sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            'span': 'THIS CENSORING SPAN DOES NOT EXIST IN THE HELD DOCUMENT'}}}}
    target = {'binding_axes': ['censoring'], 'axes': {
        'censoring': ty.field('end-of-study', rule_id='fixture:binding')}}
    effect = ty.build_effect(row)
    assert ty.unify(target, effect)['status'] == 'UNKNOWN_FAILS_CLOSED'


def test_located_span_with_wrong_digest_is_refused():
    path = 'cache/glp1-ra-mace-t2d/records.json'
    row = {'id': 'plant', 'effect_type_evidence': {'censoring': {
        'value': 'end-of-study', 'basis': {
            'document_path': path, 'document_sha256': '0' * 64,
            'span': (ROOT / path).read_text(encoding='utf8')[:30]}}}}
    assert ty.build_effect(row)['axes']['censoring']['value'] == 'UNKNOWN'


def test_all_registered_spans_locate_and_only_binding_axes_are_curated():
    import json
    register = json.loads((ROOT / 'cache/glp1-ra-mace-t2d/axis_evidence.json').read_text(encoding='utf8'))
    for row in register['rows'].values():
        assert set(row['axes']) == {'endpoint_components', 'censoring', 'effect_measure'}
        for field in row['axes'].values():
            if ty.known(field):
                assert ty.held_axis(field) == field


def test_evidence_cannot_transfer_to_another_effect_or_document():
    from scripts import glp1_sources as glp1
    row = dict(glp1.entries()['27295427'], id='PMID 27295427')
    assert ty.registered_axes(row)['censoring']['value'] == 'end-of-study'
    changed = dict(row, source=row['source'] + ' altered')
    assert ty.registered_axes(changed) == {}
    changed = dict(row, document_sha256='0' * 64)
    assert ty.registered_axes(changed) == {}
    changed = dict(row, effect=row['effect'] + 1)
    assert ty.registered_axes(changed) == {}


def test_flow_does_not_borrow_component_censoring():
    from scripts import glp1_sources as glp1
    row = dict(glp1.entries()['38785209'], id='PMID 38785209')
    e = ty.build_effect(row)
    assert ty.known(e['axes']['endpoint_components'])
    assert e['axes']['censoring']['value'] == 'UNKNOWN'
    assert 'FLOW_COMPOSITE' in e['axes']['censoring']['basis']['absence_code']
