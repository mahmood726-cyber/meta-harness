"""Offline plants against copies of real HM3 decisions and outcomes."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
import test_hm3_pages as contract


def _first_decision():
    decision = json.loads((contract.EVIDENCE / 'decisions.json').read_text(encoding='utf-8'))[0]
    path = contract.ROOT / 'docs/reviews' / decision['topic'] / 'review.json'
    return decision, path


@pytest.fixture
def declarations(monkeypatch):
    """A constructed declaration over a copy of a real outcome made incomplete in memory.

    The committed list may legitimately be empty (every HM3 declaration resolved), so the
    plants must not depend on a live declaration existing.
    """
    decl_path = contract.EVIDENCE / 'harms_superseded.json'
    decision, review_path = _first_decision()
    review = json.loads(review_path.read_text(encoding='utf-8'))
    outcome = next(o for o in review['outcomes'] if o['name'] == decision['outcome'])
    outcome['result']['harms_incomplete'] = True
    outcome['result']['known_reported_not_yet_extracted'] = [{'id': '__control_plant_id', 'span': 'plant'}]
    data = [dict(topic=decision['topic'], outcome=decision['outcome'], landing='plant', reason='plant',
                 decided='plant', known_reported_not_yet_extracted=['__control_plant_id'])]
    original_read = Path.read_text

    def read(self, *args, **kwargs):
        if self == decl_path:
            return json.dumps(data)
        if self == review_path:
            return json.dumps(review)
        return original_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', read)
    return data


def test_constructed_declaration_passes_the_contract(declarations):
    # The control: an honest declaration over an incomplete outcome must PASS, or the plants
    # below prove nothing.
    contract.test_rebuilt_pages_account_for_every_baseline_harm()


def test_mismatched_declared_harm_ids_fail(declarations):
    entry = declarations[0]
    assert entry['known_reported_not_yet_extracted']
    entry['known_reported_not_yet_extracted'] = []
    with pytest.raises(AssertionError, match='declared harm IDs differ'):
        contract.test_rebuilt_pages_account_for_every_baseline_harm()


def test_declared_but_complete_harm_fails(declarations):
    entry = deepcopy(declarations[0])
    for decision in json.loads((contract.EVIDENCE / 'decisions.json').read_text(encoding='utf-8')):
        if (decision['topic'], decision['outcome']) == (entry['topic'], entry['outcome']):
            continue
        review = json.loads((contract.ROOT / 'docs/reviews' / decision['topic'] / 'review.json').read_text(encoding='utf-8'))
        outcome = next(o for o in review['outcomes'] if o['name'] == decision['outcome'])
        if not outcome['result'].get('harms_incomplete'):
            entry.update(topic=decision['topic'], outcome=decision['outcome'],
                         known_reported_not_yet_extracted=[r['id'] for r in outcome['result'].get('known_reported_not_yet_extracted', [])])
            declarations.append(entry)
            break
    else:
        pytest.fail('No real complete harm outcome available for the plant')
    with pytest.raises(AssertionError, match='declared but nothing moved'):
        contract.test_rebuilt_pages_account_for_every_baseline_harm()


@pytest.mark.parametrize('field', ['landing', 'reason', 'decided'])
def test_missing_harm_declaration_metadata_fails(declarations, field):
    del declarations[0][field]
    with pytest.raises(AssertionError):
        contract.test_rebuilt_pages_account_for_every_baseline_harm()


def load_script():
    import importlib.util
    spec = importlib.util.spec_from_file_location('hm3_declare', contract.ROOT / 'scripts/hm3_declare_supersession.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize('ensure_ascii', [False, True])
@pytest.mark.parametrize('suffix', ['', '\n'])
def test_baseline_roundtrip(ensure_ascii, suffix):
    module = load_script()
    obj = {'label': 'caf\u00e9'}
    raw = (json.dumps(obj, indent=1, ensure_ascii=ensure_ascii) + suffix).encode('utf-8')
    assert module.baseline_format(raw, obj) == (ensure_ascii, suffix)


@pytest.mark.parametrize('raw', [b'{"a": 1}\n', b'{\r\n "a": 1\r\n}\r\n'])
def test_baseline_format_mismatch_fails(raw):
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        load_script().baseline_format(raw, json.loads(raw))


def test_history_preserved_oldest_first_and_idempotent():
    module = load_script()
    oldest = dict(landing='oldest', reason='first change', screening_records_after=[])
    prior = dict(landing='prior', reason='second change', screening_records_after=[1], history=[oldest])
    untouched = deepcopy(prior)
    entry = module.screening_entry(prior, [2])
    assert prior == untouched
    assert entry['history'] == [oldest, {k: v for k, v in prior.items() if k != 'history'}]
    assert entry['screening_records_after'] == [2]
    assert module.screening_entry(entry, [2]) == entry


@pytest.mark.parametrize('history', [{}, [dict(landing='missing reason')]])
def test_invalid_screening_history_fails(monkeypatch, history):
    path = contract.EVIDENCE / 'primary-baseline-f6f7b14c.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    for entry in data['screening_superseded'].values():
        entry['history'] = history
    original_read = Path.read_text
    def read(self, *args, **kwargs):
        return json.dumps(data) if self == path else original_read(self, *args, **kwargs)
    monkeypatch.setattr(Path, 'read_text', read)
    with pytest.raises(AssertionError):
        contract.test_primary_trial_values_and_membership_are_unchanged()
