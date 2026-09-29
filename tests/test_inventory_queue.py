"""PLANTS are in-memory mutations of held evidence, never research output."""
from copy import deepcopy
import json
import pytest

from harness import inventory_queue as iq
from harness.proposal_gate import verify as base_verify
from scripts.g1_proposal_census import census as base_census


@pytest.fixture(scope='module')
def corpus():
    base = base_census(iq.ROOT)
    topic = next(t for t in base['topics'] if t['slug'] == 'pcsk9-mace')
    return iq.build_queue(topic), base


def mutations(queue):
    """Named reproducible pre/post plant inputs used by the report."""
    cases = {}
    bad = deepcopy(queue)
    bad['missing'][0]['resolved']['nct'] = queue['missing'][1]['resolved']['nct']
    cases['identifier_not_in_own_span'] = bad
    bad = deepcopy(queue)
    bad['document_sha256'] = '0' * 64
    cases['sha_mismatch'] = bad
    bad = deepcopy(queue)
    bad['missing'][0]['resolved']['spans']['nct'] += ' NOT PRINTED'
    cases['span_not_held'] = bad
    bad = deepcopy(queue)
    bad['missing'][0]['resolved'] = deepcopy(queue['missing'][1]['resolved'])
    cases['borrowed_real_identifier_and_span'] = bad
    bad = deepcopy(queue)
    bad['missing'].pop()
    cases['dropped_missing_trial'] = bad
    bad = deepcopy(queue)
    bad['missing'][0]['why_missing_hypothesis'] = 'OUTSIDE_OUR_PROTOCOL_SCOPE'
    cases['unsupported_scope_exclusion'] = bad
    bad = deepcopy(queue)
    bad['missing'][0]['resolved']['year'] = 'recent'
    bad['missing'][0]['resolved']['spans']['year'] = 'recent'
    cases['unprinted_year'] = bad
    bad = deepcopy(queue)
    bad['comparator_pmid'] = '00000000'
    cases['wrong_comparator'] = bad
    bad = deepcopy(queue)
    bad['missing'][0]['scope_evidence'][0]['span'] = 'invented exclusion'
    cases['scope_span_not_held'] = bad
    bad = deepcopy(queue)
    bad['missing'][0]['resolution'] = 'UNRESOLVED'
    cases['wrong_resolution'] = bad
    return cases


def test_correct_entry_negative_plant(corpus):
    queue, base = corpus
    assert iq.verify(queue, baseline=base) is True


@pytest.mark.parametrize('name', list(mutations({'missing': [
    {'resolved': {'nct': 'NCT00000001', 'spans': {'nct': 'NCT00000001'}},
     'scope_evidence': [{'span': 'fixture'}]},
    {'resolved': {'nct': 'NCT00000002', 'spans': {'nct': 'NCT00000002'}}}]})))
def test_queue_plants(corpus, name):
    queue, base = corpus
    bad = mutations(queue)[name]
    # Base gate has no queue contract; a top-level queue extension is ignored.
    p = iq.read(iq.ROOT / 'evidence/g1_proposals/pcsk9-mace.json')
    p['inventory_queue'] = bad
    assert base_verify(p, iq.ROOT)['status'] == 'accepted'
    with pytest.raises(ValueError, match='REFUSED_'):
        iq.verify(bad, baseline=base)


@pytest.mark.parametrize('key,span,good,bad', [
    ('doi', 'doi: 10.1234/test.one.', '10.1234/test.one', '10.1234/test.two'),
    ('pmid', 'PUBMED: 12345678', '12345678', '87654321'),
    ('nct', 'NCT00000001', 'NCT00000001', 'NCT00000002'),
])
def test_identifier_regex_binding(key, span, good, bad):
    assert good in iq.identifiers(key, span)
    assert bad not in iq.identifiers(key, span)
    assert not iq.identifiers('pmid', 'Sample size 12345678')


def test_commentary_acronym_is_not_trial_citation():
    text = ('ALPHA trial 1 References 1. Smith A. Trial results. Journal 2020;1:2. '
            '2. Jones B. Will ALPHA work? Journal 2019;1:2. doi: 10.1234/commentary.')
    hits = iq.citation_candidates('ALPHA', text)
    assert len(hits) == 1
    assert 'Smith' in hits[0]
    assert not iq.parse_citation(hits[0])['doi']
    assert iq.citation_candidates('ALPHA', text.replace('ALPHA trial 1 ', '')) == []


def test_ambiguous_citation_refuses():
    text = 'ALPHA trial 1 ALPHA trial 2 References 1. Smith A. One. Journal 2020;1:2. 2. Jones B. Two. Journal 2021;1:2.'
    assert iq.citation_candidates('ALPHA', text) == []


def test_explicit_analysis_reference_precedes_trial_number():
    text = ('Smith et al 1 analysis of ALPHA trial 2 References '
            '1. Smith A. Analysis. Journal 2020;1:2. '
            '2. Jones B. Other drug trial. Journal 2021;1:2.')
    assert iq.citation_candidates('ALPHA', text) == ['Smith A. Analysis. Journal 2020;1:2.']


def test_citation_fields_negative_plant():
    got = iq.parse_citation('Smith A, Jones B. Randomized trial. Journal of Trials 2020;1:2. doi: 10.1234/trial.')
    assert {k: got[k] for k in ('author', 'year', 'journal', 'title', 'doi')} == dict(
        author='Smith A', year='2020', journal='Journal of Trials', title='Randomized trial', doi='10.1234/trial')


def test_missing_canonical_source_is_unresolved(corpus):
    _, base = corpus
    topic = next(t for t in base['topics'] if t['slug'] == 'sglt2-primary-prevention-hf')
    queue = iq.build_queue(topic)
    assert queue['source_refusal'] == 'REFUSED_CANONICAL_COMPARATOR_SOURCE_UNAVAILABLE'
    assert all(r['resolution'] == 'UNRESOLVED' for r in queue['missing'])
    assert iq.verify(queue, baseline=base)


def test_all_generated_queues_verify(corpus):
    _, base = corpus
    for topic in base['topics']:
        if any(t['status'] == 'MISSING_FROM_OURS' for t in topic['trials']):
            queue = iq.build_queue(topic)
            assert iq.verify(queue, baseline=base)
            assert len(queue['missing']) == sum(t['status'] == 'MISSING_FROM_OURS' for t in topic['trials'])


def test_changed_source_bytes_refuse(corpus, monkeypatch):
    queue, base = corpus
    original = iq.Path.read_bytes
    def changed(path):
        data = original(path)
        return data + b' PLANTED CHANGE' if path == iq.ROOT / queue['document_ref'] else data
    monkeypatch.setattr(iq.Path, 'read_bytes', changed)
    with pytest.raises(ValueError, match='SHA256_MISMATCH'):
        iq.verify(queue, baseline=base)


def test_unpublished_citation_is_relayed(corpus):
    _, base = corpus
    topic = next(t for t in base['topics'] if t['slug'] == 'metformin-pcos-ovulation')
    q = iq.build_queue(topic)
    entry = next(r for r in q['missing'] if r['label'] == 'Heathcote 2013')
    assert entry['evidence_kind'] == 'RELAYED'
    assert entry['resolved']['title']
    assert all(k not in entry for k in ('effect', 'n', 'events'))
