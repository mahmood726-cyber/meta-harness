"""Promotion plant: adjudicated benchmark configs must reach the full build."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('slug', ['daratumumab-rrmm-pfs-bench', 'hcq-covid-prophylaxis-bench'])
def test_bench_adjudicated_promotion_leaves_draft(slug):
    config = json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf-8'))
    assert config['benchmark']['captain_adjudication']
    assert not config['benchmark']['status'].startswith('protocol_draft')


@pytest.mark.parametrize('slug', ['daratumumab-rrmm-pfs-bench', 'hcq-covid-prophylaxis-bench'])
def test_bench_reread_routes_have_extractor_provenance(slug):
    from harness import bench_routes
    from harness.provenance_class import classify_served
    config = json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf-8'))
    rows = bench_routes.for_config(config)
    admitted = [r for r in rows.values() if not r.get('absent')]
    assert admitted
    for row in admitted:
        assert classify_served(row, lambda _: False)[0] == 'EXTRACTOR'
