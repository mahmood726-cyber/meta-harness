"""Offline plants against copies of real HM3 decisions and outcomes."""
from copy import deepcopy
import json
from pathlib import Path

import pytest
import test_hm3_pages as contract


@pytest.fixture
def declarations(monkeypatch):
    path = contract.EVIDENCE / 'decisions.json'
    data = deepcopy(json.loads(path.read_text(encoding='utf-8')))
    original_read = Path.read_text

    def read(self, *args, **kwargs):
        if self == path:
            return json.dumps(data)
        return original_read(self, *args, **kwargs)

    monkeypatch.setattr(Path, 'read_text', read)
    return data


def test_mismatched_declared_harm_ids_fail(declarations):
    entry = declarations['harms_superseded'][0]
    assert entry['known_reported_not_yet_extracted']
    entry['known_reported_not_yet_extracted'] = []
    with pytest.raises(AssertionError, match='declared harm IDs differ'):
        contract.test_rebuilt_pages_account_for_every_baseline_harm()


def test_declared_but_complete_harm_fails(declarations):
    entry = deepcopy(declarations['harms_superseded'][0])
    for decision in declarations['decisions']:
        review = json.loads((contract.ROOT / 'docs/reviews' / decision['topic'] / 'review.json').read_text(encoding='utf-8'))
        outcome = next(o for o in review['outcomes'] if o['name'] == decision['outcome'])
        if not outcome['result'].get('harms_incomplete'):
            entry.update(topic=decision['topic'], outcome=decision['outcome'],
                         known_reported_not_yet_extracted=[r['id'] for r in outcome['result'].get('known_reported_not_yet_extracted', [])])
            declarations['harms_superseded'].append(entry)
            break
    else:
        pytest.fail('No real complete harm outcome available for the plant')
    with pytest.raises(AssertionError, match='declared but nothing moved'):
        contract.test_rebuilt_pages_account_for_every_baseline_harm()


@pytest.mark.parametrize('field', ['landing', 'reason', 'decided'])
def test_missing_harm_declaration_metadata_fails(declarations, field):
    del declarations['harms_superseded'][0][field]
    with pytest.raises(AssertionError):
        contract.test_rebuilt_pages_account_for_every_baseline_harm()
