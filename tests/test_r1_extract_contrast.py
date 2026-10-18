"""R1 adversarial prose fixtures; numerical research outputs are never entered here."""
import json
from pathlib import Path
import sys
import pytest
from harness import extract as e, registry_contrast as rc

ROOT = Path(__file__).resolve().parents[1]

def test_p0_1_overall_endpoint_is_not_itt():
    text = 'In the per-protocol population, overall survival was longer with drugx (HR 0.70, 95% CI 0.58-0.85). In the intention-to-treat population, overall survival with drugx was HR 0.90 (95% CI 0.78-1.04).'
    assert e.extract_trial(text, ['overall survival'], ['drugx'], [], estimand='HR')['effect'] == .90
    assert e._is_subgroup_sentence('In a post-hoc analysis, overall survival favoured drug (HR 0.80, 95% CI 0.70-0.91).')
    assert e._is_subgroup_sentence('In a sensitivity analysis of overall mortality, the HR was 0.80 (95% CI 0.70-0.91).')

def test_p0_2_trailing_subgroup():
    assert e._is_subgroup_sentence('The hazard ratio for death was 0.80 (95% CI 0.70-0.91) in the per-protocol population.')
    assert e._is_subgroup_sentence('The risk of death was reduced (HR 0.50, 95% CI 0.30-0.80), and was lowest in the HP+/AZ group.')
    text = 'Death occurred less often with drugx (HR 0.70, 95% CI 0.58-0.85) in the per-protocol population; in the intention-to-treat population the HR was 0.90 (95% CI 0.78-1.04).'
    assert e.extract_trial(text, ['death'], ['drugx'], [], estimand='HR').get('effect') != .70

@pytest.mark.parametrize('text', [
    'In transplant-ineligible patients, daratumumab plus VMP improved PFS (HR 0.42, 95% CI 0.34-0.51).',
    'In elderly patients, PFS was improved (HR 0.70, 95% CI 0.60-0.82).',
    'Mortality in HFrEF patients, compared to placebo was lower.'])
def test_p0_3_population_not_subgroup(text):
    assert not e.subgroup_refusal(text)

@pytest.mark.parametrize('text', [
    'Daratumumab reduced the risk of progression or death (PFS HR 0.56, 95% CI 0.44-0.71); PFS2 was also prolonged (HR 0.65, 95% CI 0.51-0.83).',
    'Median PFS was 20 vs 12 months (HR 0.56, 95% CI 0.44-0.71); time to second progression was not reached.',
    'PFS improved (HR 0.56, 95% CI 0.44-0.71), with benefit maintained through second progression.',
    'The progression-free survival 2-year rate was 70% vs 50% (HR 0.56, 95% CI 0.44-0.71).'])
def test_p0_4_pfs_effect_clause(text):
    assert e.extract_trial(text, ['PFS', 'progression-free survival'], ['daratumumab'], [], estimand='HR').get('effect') == .56

@pytest.mark.parametrize('description', ['Rd; dara permitted upon PD', 'Rd; daratumumab permitted at progression', 'Rd; patients with PD may receive daratumumab', None, '???'])
def test_p1_1_crossover_not_initial_exposure(description):
    arms = [dict(role='EXPERIMENTAL', label='Daratumumab Rd', description='Daratumumab Rd', interventions=['Daratumumab', 'Lenalidomide'], complete=True),
            dict(role='ACTIVECOMPARATOR', label='Rd', description=description, interventions=['Lenalidomide', 'Darატumumab'.replace('ატ','at')], complete=True)]
    assert rc.arm_verdict(arms, ['daratumumab', 'dara']) is (None if description in (None, '???') else True)

def test_p1_3_contrast_requires_declaration():
    cfg = dict(intervention_agents={'drug': []}, intervention='drug plus or minus backbone', question='adding drug to backbone')
    assert not rc.enabled(cfg)
    assert not rc.enabled(dict(cfg, registry_contrast=False))
    assert rc.enabled(dict(cfg, registry_contrast=True))

def test_p2_1_distinct_registry_rule():
    cfg = json.loads((ROOT/'topics/daratumumab-rrmm-pfs-bench.json').read_text())
    cfg['registry_contrast'] = True
    doc = rc.load(cfg)
    # Use the held linked arms, never fabricate a trial identifier.
    nct = next(n for n, r in doc['records'].items() if rc.arm_verdict(rc.aact_arms(r), rc.terms(cfg)) is False)
    assert rc.assess({'id':nct}, cfg, doc)['rule_id'] == 'X-CONTRAST-REGISTRY'

def test_p2_3_draft_writer_preserves_status(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT/'scripts'))
    import build_topic as b
    slug = 'daratumumab-rrmm-pfs-bench'
    (tmp_path/'topics').mkdir()
    (tmp_path/'topics'/f'{slug}.json').write_bytes((ROOT/'topics'/f'{slug}.json').read_bytes())
    monkeypatch.setattr(b, 'ROOT', str(tmp_path))
    monkeypatch.setattr(b, '_protocol_sha', lambda _: 'test')
    monkeypatch.setattr(b.fetch, 'ensure', lambda *a: {})
    monkeypatch.setattr(b, 'build_review_core', lambda *a: {'outcomes':[]})
    b.main(slug, '2026-10-16')
    assert json.loads((tmp_path/'docs/reviews'/slug/'review.json').read_text())['status'] == 'DRAFT_BOOTSTRAP'


def test_p0_3_served_hfref_population_spans():
    review = json.loads((ROOT/'docs/reviews/spironolactone-hfref-mortality/review.json').read_text(encoding='utf8'))
    def strings(obj):
        if isinstance(obj, str):
            yield obj
        elif isinstance(obj, dict):
            for value in obj.values():
                yield from strings(value)
        elif isinstance(obj, list):
            for value in obj:
                yield from strings(value)
    spans = [s for s in strings(review) if 'in hfref patients, compared to' in s.lower()]
    assert spans, 'requires the served source spans'
    assert all(not e.subgroup_refusal(s) for s in spans)
