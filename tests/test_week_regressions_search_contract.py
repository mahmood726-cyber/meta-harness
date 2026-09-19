"""A cached known-item query cannot silently satisfy a requested concept query."""
import json
import pytest
from harness import fetch
from test_week_regressions_audit import load_pin


def requirement(module, tmp_path, monkeypatch):
    path = tmp_path / 'records.json'
    path.write_text(json.dumps({'records': [], 'pubmed_queries': ['12345678[uid]']}), encoding='utf-8')
    monkeypatch.setattr(module, 'cache_path', lambda slug: str(path))
    monkeypatch.setattr(module, 'run', lambda config: pytest.fail('network acquisition attempted'))
    with pytest.raises(ValueError, match='query contract'):
        module.ensure({'slug': 'plant', 'pubmed_queries': ['diabetes AND liraglutide']}, '2031-02-03')


def test_cached_queries_must_match_requested_contract(tmp_path, monkeypatch):
    requirement(fetch, tmp_path, monkeypatch)


def test_search_contract_patch_holds(tmp_path, monkeypatch):
    requirement(load_pin('patched/harness/fetch.py'), tmp_path, monkeypatch)


def test_search_contract_plant_fires_on_base(tmp_path, monkeypatch):
    with pytest.raises(pytest.fail.Exception, match='DID NOT RAISE'):
        requirement(load_pin('base/harness/fetch.py'), tmp_path, monkeypatch)
