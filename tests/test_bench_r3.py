import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from harness import registry_contrast as rc

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'daratumumab-rrmm-pfs-bench'

def config():
    return json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))

def test_extract_frozen_main_hash():
    expected = subprocess.check_output(['git', 'show', '0d95190c29:harness/extract.py'], cwd=ROOT)
    assert hashlib.sha256((ROOT/'harness/extract.py').read_bytes()).digest() == hashlib.sha256(expected).digest()

def test_contrast_randomisation_semicolon():
    text = 'randomized to receive daratumumab plus lenalidomide and dexamethasone (D-Rd) or Rd; daratumumab was given weekly.'
    assert rc.abstract_verdict({'abstract': text}, rc.terms(config()))[0] is not False

@pytest.mark.parametrize('suffix', ['free', 'naive', 'refractory'])
def test_contrast_nonexposure_suffix(suffix):
    assert not rc.active('daratumumab-' + suffix, rc.terms(config()))

def test_contrast_switch_after_progression():
    arms = [dict(role='EXPERIMENTAL', label='D-Rd', description='Daratumumab plus Rd', interventions=['daratumumab', 'Rd'], complete=True),
            dict(role='ACTIVECOMPARATOR', label='Rd', description='Rd. Patients who progress can switch to daratumumab.', interventions=['Rd', 'daratumumab'], complete=True)]
    assert rc.arm_verdict(arms, rc.terms(config())) is True

def test_contrast_lynx_held_description():
    cfg = config()
    doc = rc.load(cfg)
    rec = next(r for r in json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf8'))['records'] if r['id']=='41041907')
    assert rec['nct']=='NCT03871829'
    assert rc.assess(rec, cfg, doc)['decision']=='include'

@pytest.mark.parametrize('alias', ['Dara', 'Dara-SC'])
def test_contrast_declared_alias(alias):
    assert rc.active(alias, rc.terms(config()))

@pytest.mark.parametrize('pid', ['32482541', '32001798', '40680754'])
@pytest.mark.parametrize('mutation', ['anchor', 'value', 'none'])
def test_bench_route_bound_or_refused(pid, mutation, monkeypatch):
    from harness import bench_routes as br
    pins = br.load_pins(ROOT)
    if mutation == 'anchor':
        pins[pid]['anchor'] += ' MISSING'
    elif mutation == 'value':
        pins[pid]['value']['effect'] *= 2
    monkeypatch.setattr(br, 'load_pins', lambda root: pins)
    row = br.for_config(config(), root=ROOT)[pid]
    if mutation != 'none' or pins[pid]['refuse']:
        assert row.get('absent') and 'effect' not in row
    else:
        assert {k:row[k] for k in pins[pid]['value']} == pins[pid]['value']

def test_bench_routes_opt_in():
    from harness import bench_routes as br
    assert br.for_config({'slug': SLUG}) == {}


def test_bench_frozen_extractor_target_endpoint_compatibility():
    from harness import target_endpoint
    cfg = config()
    records = json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf8'))['records']
    rec = next(r for r in records if r['id']=='32001798')
    target_endpoint._published_effect_from_abstract(cfg['primary_outcome'], rec['abstract'], cfg['intervention_terms'], cfg['comparator_terms'])
