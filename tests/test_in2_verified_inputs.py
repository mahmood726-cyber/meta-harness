"""Synthetic schema plants; these are never clinical inputs."""
import json
import pytest


@pytest.mark.parametrize('legacy', [
    {'absent': True, 'provenance': 'REFUSED_ON_EVIDENCE'},
    {'absent_kind': 'adjudicated_absent', 'reason_code': 'REFUSED_ON_EVIDENCE'},
    {'typed_refusal': True, 'refusal_provenance': 'REFUSED_ON_EVIDENCE'},
    {'override': True, 'absent': True, 'provenance': 'REFUSED_ON_EVIDENCE'},
])
def test_legacy_refusals_normalise_identically(legacy):
    from harness.verified_inputs import normalise
    common = dict(outcome='Synthetic harm', reason='No counts reported',
                  source_span='Synthetic narrative.', source_level=1,
                  document_ref='records.json')
    expected = dict(common, kind='typed_refusal', provenance='REFUSED_ON_EVIDENCE')
    assert normalise(dict(common, **legacy)) == expected


def test_fabricated_span_is_refused(tmp_path):
    from harness.verified_inputs import load
    topic = tmp_path / 'synthetic'
    topic.mkdir()
    (topic / 'records.json').write_text(json.dumps({'records': [
        {'id': 'fixture', 'abstract': 'Synthetic narrative.'}]}), encoding='utf-8')
    (topic / 'verified_arms.json').write_text(json.dumps({'fixture': {
        'outcome': 'Synthetic harm', 'kind': 'typed_refusal',
        'provenance': 'REFUSED_ON_EVIDENCE', 'reason': 'No counts',
        'source_span': 'Fabricated quotation.', 'source_level': 1,
        'document_ref': 'records.json'}}), encoding='utf-8')
    with pytest.raises(ValueError, match='source_span'):
        load('synthetic', cache_root=tmp_path)


def test_canonical_entry_cannot_omit_span(tmp_path):
    from harness.verified_inputs import load
    topic = tmp_path / 'synthetic'
    topic.mkdir()
    (topic / 'verified_effects.json').write_text(json.dumps({'fixture': {
        'outcome': 'Synthetic harm', 'kind': 'typed_refusal',
        'provenance': 'REFUSED_ON_EVIDENCE', 'reason': 'No counts'}}), encoding='utf-8')
    with pytest.raises(ValueError, match='requires source_span'):
        load('synthetic', cache_root=tmp_path)


def test_design_failure_remains_eligibility_failure():
    from harness import eligibility_chain, pipeline
    cfg = {'include': {'design_double_blind': True, 'comparator_any': ['placebo']},
           'primary_outcome': {'population': 'intention-to-treat', 'timepoint': 'trial end'}}
    contract = eligibility_chain.compile_contract('synthetic', cfg,
        'Double-blind OR placebo-controlled.\n**Population** - intention-to-treat.\n**Timepoint** - trial end.')
    out = pipeline._build_outcome({'name': 'Synthetic harm', 'keywords': ['harm'], 'estimand': 'RR'},
        'harm', [{'id': 'fixture', 'id_type': 'pmid'}],
        {'fixture': {'abstract': 'Randomized open-label comparison with usual care.'}},
        ['drug'], ['usual care'], verified_arms={'fixture': {
            'outcome': 'Synthetic harm', 'override': True, 'ai': 1, 'n1i': 20,
            'ci': 2, 'n2i': 20, 'source': 'Synthetic 1/20 versus 2/20'}},
        eligibility_contract=contract)
    assert not out['trials']
    assert 'design_masking' in out['declared_absent_trials'][0]['eligibility_chain_rationale']


def test_regulatory_refusal_revalidates_held_output_text(tmp_path, monkeypatch):
    from harness import absence, verified_inputs
    monkeypatch.setattr(verified_inputs, 'ROOT', tmp_path)
    path = tmp_path / 'outputs' / 'handover' / 'regulatory.txt'
    path.parent.mkdir(parents=True)
    path.write_text('Synthetic regulatory table: separate symptoms only.', encoding='utf-8')
    row = {'id': 'fixture', 'typed_refusal': True,
           'refusal_provenance': 'REFUSED_ON_EVIDENCE',
           'reason_code': 'REFUSED_ON_EVIDENCE', 'reason': 'No aggregate harm count.',
           'source_span': path.read_text(encoding='utf-8'),
           'document_ref': 'outputs/handover/regulatory.txt', 'source_level': 2}
    result = absence.classify_reason([], 'Synthetic abstract.', row=row, reason=row['reason'])
    assert result['reason_code'] == 'REFUSED_ON_EVIDENCE'
    row['source_span'] = 'Fabricated regulatory sentence.'
    with pytest.raises(ValueError, match='source_span absent'):
        absence.classify_reason([], 'Synthetic abstract.', row=row, reason=row['reason'])
