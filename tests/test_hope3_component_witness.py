import copy
import json
import subprocess
import sys
from unittest.mock import patch

import pytest

from harness import component_typing, endpoint_policy
from scripts import make_hope3_definition_excerpt as lane


@pytest.fixture(scope='module')
def witness():
    return lane.build()


def original():
    return subprocess.check_output(['git', '--no-optional-locks', 'show', 'HEAD:docs/endpoint_policies.json'], cwd=lane.ROOT)


def test_held_sentence_and_qualified_components(witness):
    row = lane.pending(json.loads(original()))
    assert witness['components'] == sorted(row['component_set'])
    assert witness['base_typing']['untyped'] == []
    assert witness['poolable'] is False
    assert witness['state'] == 'HELD'
    assert witness['span'].count('.') == 1
    start, end = witness['first_clause_offsets']
    assert witness['span'][start:end] == witness['first_clause_span']


def test_base_leaves_second_clause_untyped_but_lane_separates(witness):
    base = component_typing.derive(witness['span'])
    assert base['components'] == witness['base_typing']['components']
    assert 'heart failure' in base['untyped']
    assert witness['base_typing']['untyped'] == []


def test_second_definition_cannot_bind(witness):
    second = 'The second coprimary outcome was the composite of death from cardiovascular causes, nonfatal myocardial infarction, nonfatal stroke, resuscitated cardiac arrest, heart failure, and revascularization.'
    assert component_typing.derive(second) is not None
    with pytest.raises(ValueError, match='FIRST_COPRIMARY_REQUIRED'):
        lane.bind(second, witness['components'])


@pytest.mark.parametrize('old,new', [('nonfatal stroke', 'fatal stroke'), ('nonfatal stroke', 'nonfatal stroke, heart failure'), ('nonfatal myocardial infarction, ', '')])
def test_bad_first_components_refused(witness, old, new):
    with pytest.raises(ValueError, match='COMPONENT_MISMATCH|UNTYPED_DEFINITION'):
        lane.bind(witness['span'].replace(old, new), witness['components'])


def test_relay_mismatch_refused(witness):
    with pytest.raises(ValueError, match='COMPONENT_MISMATCH'):
        lane.bind(witness['span'], ['stroke'])


def test_policy_every_original_byte_preserved(witness):
    before = original()
    after = lane.update_bytes(before, witness)
    # Removing ONLY the insertion must reproduce every byte, including decisions/diagnostic.
    pos = before.index(b'"input": "NCT00468923"')
    inserted = len(after) - len(before)
    assert after[:pos] + after[pos + inserted:] == before
    old = json.loads(before)
    new = json.loads(after)
    row = lane.pending(new)
    assert row.pop('component_basis_history') == [lane.pending(old)['component_basis']]
    assert row.pop('component_basis_held') == witness
    assert new == old
    assert lane.update_bytes(after, witness) == after


def test_conflicting_witness_refused(witness):
    after = lane.update_bytes(original(), witness)
    changed = copy.deepcopy(witness)
    changed['sha256'] = 'incorrect plant'
    with pytest.raises(ValueError, match='WITNESS_CONFLICT'):
        lane.update_bytes(after, changed)


def test_pdf_tamper_refused():
    real = lane.Path.read_bytes
    def tamper(path):
        return b'defective PDF plant' if path == lane.ROOT / lane.PDF else real(path)
    with patch.object(lane.Path, 'read_bytes', tamper):
        with pytest.raises(ValueError, match='PDF_HASH'):
            lane.build()


@pytest.mark.parametrize('arguments', [['--pooled-estimate', '0.8'], ['--pooled-estimate']])
def test_pooled_estimate_refused_without_writes(arguments):
    before = (lane.ROOT / lane.POLICY).read_bytes()
    with pytest.raises(ValueError, match='POOLING_DISABLED'):
        lane.refuse_pool({'estimate': 0.8})
    result = subprocess.run([sys.executable, str(lane.ROOT / 'scripts/make_hope3_definition_excerpt.py'), *arguments], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'POOLING_DISABLED' in result.stderr
    assert (lane.ROOT / lane.POLICY).read_bytes() == before


def test_base_policy_still_blocks_after_witness(witness):
    review = {'outcomes': [{'name': lane.OUTCOME, 'trials': [{'id': 'NCT00468923'}]}]}
    data = json.loads(lane.update_bytes(original(), witness))['topics']
    with patch.object(endpoint_policy, 'load', return_value=data):
        assert endpoint_policy.attach(review, lane.SLUG, {'NCT00468923': {'abstract': witness['first_clause_span'] + '.'}}) is None
    assert [p['kind'] for p in endpoint_policy.problems(review)] == ['ENDPOINT_POLICY_VIOLATION']


def test_options_keep_signoff_and_other_rows(witness):
    before = (lane.ROOT / 'docs/decisions/hope3_endpoint_policy_options.md').read_text(encoding='utf-8')
    after = lane.options(lane.ROOT, witness)
    assert [x for x in before.splitlines() if not x.startswith('| NCT00468923 |')] == [x for x in after.splitlines() if not x.startswith('| NCT00468923 |')]
    assert 'NOT_HELD >=70 subgroup RESULT' in after
    assert 'Historical basis:' in after


def test_census_all_topics():
    report = lane.census()
    assert report['topic_scope']['N'] == len(list((lane.ROOT / 'topics').glob('*.json')))
    assert report['topic_scope']['items'] == [lane.SLUG]
    for rule in report['rules'].values():
        assert rule['n'] == len(rule['items'])
        assert rule['N'] == report['topic_scope']['n']
