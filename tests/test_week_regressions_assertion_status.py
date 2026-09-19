"""Successful-check fields must follow the actual contradiction results."""
from harness import compat_check, propositions


def test_proposition_status_reflects_contradictions(monkeypatch):
    monkeypatch.setattr(propositions, 'check_propositions', lambda review: [{'code': 'PLANT_CONTRADICTION'}])
    result = propositions.check_document({})
    assert result['contradictions']
    assert result['checked'] is False


def test_compatibility_status_reflects_remaining_violations(monkeypatch):
    monkeypatch.setattr(compat_check, 'check', lambda *args: [{'code': 'PLANT_CONTRADICTION'}])
    result = compat_check.enrich({})['compat_underlying']
    assert result['post_fix_violations']
    assert result['checked'] is False


def test_clean_statuses_remain_true(monkeypatch):
    monkeypatch.setattr(propositions, 'check_propositions', lambda review: [])
    monkeypatch.setattr(compat_check, 'check', lambda *args: [])
    assert propositions.check_document({})['checked'] is True
    assert compat_check.enrich({})['compat_underlying']['checked'] is True
