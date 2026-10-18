"""Held-source plants for the declared benchmark repairs; no entered estimates."""
import json
from pathlib import Path
import pytest
from harness import pipeline, bench_routes

ROOT = Path(__file__).resolve().parents[1]
DARA = 'daratumumab-rrmm-pfs-bench'
HCQ = 'hcq-covid-prophylaxis-bench'
def load(slug):
    return (json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8')),
            json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8')))

@pytest.fixture(scope='module')
def dara():
    cfg, data = load(DARA)
    cfg['report_selection'] = 'as_comparator_cited'
    return pipeline.outcome_inputs(DARA, cfg, data)

@pytest.mark.parametrize('pid', ['32001798','32482541','32682484','34087126','34108127'])
def test_comparator_cited_report_selected(dara, pid):
    decision = next(d for d in dara['scr']['decisions'] if d['id'] == pid)
    assert decision['decision'] == 'include', decision
    assert not dara['rec_by_id'][pid].get('automatic_family_refusal')
    assert 'comparator lenalidomide' not in decision['reason'] if pid == '32482541' else True

def test_mitja_declared_design_effect():
    cfg, _ = load(HCQ)
    cfg['design_effect_conversion'] = {'method':'effective_sample_size','icc':1.0,'rounding':'nearest_integer'}
    row = bench_routes.for_config(cfg)['33289973']
    assert row['kind'] == 'extracted_counts'
    assert row['design_adjustment']['kind'] == 'ICC_DESIGN_EFFECT'
    assert row['design_adjustment']['raw_counts']

def test_rajasingham_does_not_pair_randomized_n_with_analysis_events():
    cfg, _ = load(HCQ)
    row = bench_routes.for_config(cfg)['33068425']
    assert not row.get('absent')
    comparison = row['analysis_set_comparison']
    assert comparison['analysis_set'] == 'posted_outcome_analysed_N'
    assert {r['table'] for r in comparison['evidence']} >= {'outcomes', 'outcome_counts', 'outcome_measurements', 'result_groups'}


def test_effective_counts_bind_verify_and_render():
    from harness import hand_binding, verify, page
    cfg, _ = load(HCQ)
    row = dict(bench_routes.for_config(cfg)['33289973'], id='PMID 33289973', label='Mitja')
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], row)['hand_binding_state'] == 'BOUND'
    assert verify.verify_pooled(row, None)[0] == 'verified'
    rendered = page._trial_inputs({'trials':[row]})
    assert 'Declared effective sample size' in rendered
    assert 'unrounded' in rendered
    mutated = dict(row, ai=row['ai']+1)
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], mutated)['hand_binding_state'] == 'ABSTAIN'


def test_maia_excluded_by_population():
    from harness import screen
    cfg, data = load(DARA)
    rec = next(r for r in data['records'] if r['id'] == cfg['negative_control_pmids'][0])
    decision = screen.screen_record(rec, screen.effective_include(cfg), set())
    assert decision[0] == 'exclude' and decision[1] == 'X2'


def test_selection_declaration_gate_and_identity_mutation():
    from harness.bench_report_selection import apply
    from copy import deepcopy
    cfg, data = load(DARA)
    undeclared = dict(cfg)
    undeclared.pop('report_selection')
    assert apply(undeclared, data, ROOT) == (undeclared, data)
    bad = deepcopy(data)
    next(r for r in bad['records'] if r['id'] == '32001798')['doi'] = ''
    with pytest.raises(ValueError, match='IDENTITY_MISMATCH'):
        apply(cfg, bad, ROOT)
    with pytest.raises(ValueError, match='SCOPE_MISMATCH'):
        apply(dict(cfg, slug=HCQ), data, ROOT)


def test_effective_counts_recompute_from_raw_witness():
    cfg, _ = load(HCQ)
    row = bench_routes.for_config(cfg)['33289973']
    adjustment = row['design_adjustment']
    from harness.hcq_routes import round_half_up
    for key, raw in adjustment['raw_counts'].items():
        assert row[key] == round_half_up(raw/adjustment['design_effect'])
        assert adjustment['unrounded_counts'][key] == raw/adjustment['design_effect']
    from harness import hand_binding
    from copy import deepcopy
    mutated = deepcopy(row)
    mutated['id'] = '33289973'
    mutated['design_adjustment']['icc'] = 0
    assert hand_binding.bind_hand_row(cfg['primary_outcome'], mutated)['hand_binding_state'] == 'ABSTAIN'


def test_cached_figure_has_source_identity_and_hash():
    import hashlib
    manifest = json.loads((ROOT/'cache/comparators/33406138/hcq_figure2.source.json').read_text(encoding='utf8'))
    assert manifest['pmid'] == load(HCQ)[0]['comparator_pmid']
    assert hashlib.sha256((ROOT/manifest['source_ref']).read_bytes()).hexdigest() == manifest['sha256']
    assert 'creativecommons.org/licenses/by/' in manifest['license_evidence']


def test_effective_sample_size_not_adjusted_twice():
    from harness import design_variance
    cfg, _ = load(HCQ)
    row = dict(bench_routes.for_config(cfg)['33289973'], id='PMID 33289973')
    before = {k: row[k] for k in ('ai','n1i','ci','n2i')}
    assert design_variance.apply_design_adjustment(row, 'RR') is False
    assert before == {k: row[k] for k in before}


def test_any_grade_does_not_pool_serious_pneumonia(dara):
    cfg, _ = load(DARA)
    spec = next(s for s in cfg['harm_outcomes'] if s['name'] == 'Pneumonia')
    outcome = pipeline.build_outcome_from_inputs(dara, spec, 'harm', DARA)
    assert not any(t['id'] == 'PMID 34087126' for t in outcome['trials'])


def test_posted_denominators_replace_refusal_with_typed_divergence():
    from harness import verified_inputs, absence
    cfg, data = load(HCQ)
    row = bench_routes.for_config(cfg)['33068425']
    normalized = verified_inputs.normalise(row)
    assert normalized['provenance'] == 'aact_verified'
    assert not normalized.get('absent')
    assert normalized['analysis_set_comparison']['status'] == 'DIVERGENT_NAMED'
    assert normalized['analysis_set_comparison']['reason_code'] == 'ANALYSIS_SET'


def test_effective_sample_size_requires_arm_headers():
    import xml.etree.ElementTree as ET
    from harness.hcq_routes import effective_counts
    cfg, _ = load(HCQ)
    raw = (ROOT/'cache/hcq-covid-prophylaxis-bench/PMC7722693.xml').read_bytes()
    doc = ET.fromstring(raw)
    header = doc.find('.//table-wrap[@id="t2"]//tr')
    left, right = header[1], header[2]
    header.remove(right)
    header.remove(left)
    header.insert(1, right)
    header.insert(2, left)
    base = dict(document_ref='cache/hcq-covid-prophylaxis-bench/PMC7722693.xml', document_sha256='')
    with pytest.raises(ValueError, match='arm headers'):
        effective_counts(cfg, ROOT, raw, doc, base)
