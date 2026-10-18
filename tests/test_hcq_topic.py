"""Real held-source regression plants for the HCQ benchmark only."""
import json
from pathlib import Path
from harness import pipeline, bench_routes

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'hcq-covid-prophylaxis-bench'

def inputs():
    cfg = json.loads((ROOT/'topics'/f'{SLUG}.json').read_text(encoding='utf8'))
    data = json.loads((ROOT/'cache'/SLUG/'records.json').read_text(encoding='utf8'))
    return cfg, data

def test_prophylaxis_report_survives_shared_registry_identity():
    cfg, data = inputs()
    wanted = next(r for r in data['records'] if r.get('doi') == '10.1056/NEJMoa2016638')
    rows = [r for r in pipeline._dedup(data, cfg.get('pivotal_trials')) if r.get('nct') == wanted['nct']]
    assert len(rows) == 1
    assert rows[0]['id'] == wanted['id']

def test_held_primary_infection_counts_are_extracted():
    cfg, data = inputs()
    for doi in ('10.1056/NEJMoa2016638', '10.1001/jamainternmed.2020.6319'):
        rec = next(r for r in data['records'] if r.get('doi') == doi)
        effect = bench_routes.for_config(cfg).get(rec['id'], {'absent': True})
        assert not effect.get('absent'), (rec['id'], effect)
        assert all(k in effect for k in ('ai', 'n1i', 'ci', 'n2i'))

def test_final_primary_tables_have_one_route_each():
    cfg, data = inputs()
    routes = bench_routes.for_config(cfg)
    for doi in ('10.1093/cid/ciaa1571', '10.1056/NEJMoa2021801'):
        rec = next(r for r in data['records'] if r.get('doi') == doi)
        assert rec['id'] in routes
        assert routes[rec['id']]['source_level'] == 1
        if doi == '10.1093/cid/ciaa1571':
            assert not routes[rec['id']].get('absent')
            assert routes[rec['id']]['analysis_set_comparison']['reason_code'] == 'ANALYSIS_SET'
            assert routes[rec['id']]['typed_route'] == 'hcq_combined_dose_counts'
        else:
            assert not routes[rec['id']].get('absent')

def test_mitja_effect_binds_to_its_own_primary_result():
    from harness import hand_binding
    cfg, data = inputs()
    rec = next(r for r in data['records'] if r.get('doi') == '10.1056/NEJMoa2021801')
    route = bench_routes.for_config(cfg)[rec['id']]
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], dict(route, id=rec['id']))['hand_binding_state'] == 'BOUND'

def test_effective_counts_require_recomputed_primary_witness():
    from harness import hand_binding
    cfg, data = inputs()
    rec = next(r for r in data['records'] if r.get('doi') == '10.1056/NEJMoa2021801')
    row = dict(bench_routes.for_config(cfg)[rec['id']], id=rec['id'])
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], row)['hand_binding_state'] == 'BOUND'
    damaged = dict(row, ai=row['ai']+1)
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], damaged)['hand_binding_state'] == 'ABSTAIN'
    undeclared = dict(row)
    undeclared.pop('typed_route', None)
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], undeclared)['hand_binding_state'] == 'ABSTAIN'

def test_arithmetic_verification_rechecks_held_primary_cells():
    from harness import verify
    cfg, data = inputs()
    rec = next(r for r in data['records'] if r.get('doi') == '10.1056/NEJMoa2021801')
    row = dict(bench_routes.for_config(cfg)[rec['id']], id=rec['id'])
    assert verify.verify_pooled(row, rec['abstract'])[0] == 'verified'
    assert verify.verify_pooled(dict(row, ai=row['ai']+1), rec['abstract'])[0] == 'not-yet'

def test_source_adjustment_reaches_design_consumer():
    from harness import design_key
    cfg, data = inputs()
    rec = next(r for r in data['records'] if r.get('doi') == '10.1056/NEJMoa2021801')
    row = bench_routes.for_config(cfg)[rec['id']]
    carried = pipeline._hand_fields(row, SLUG, rec['id'], rec)
    assert 'design_adjustment' in carried
    assert design_key._correlation_for_trial(carried, estimator_source='PUBLISHED', alt=None)['method'] == 'reconstructed_with_ICC'
