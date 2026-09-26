"""ELX plants: held custody must constrain missing-state decisions and rendering."""
import hashlib
import html
import json
from pathlib import Path
import subprocess

import pytest
from harness.synth import Study, pool

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'glp1-ra-mace-t2d'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def primary(review):
    return next(o for o in review['outcomes'] if o.get('primary'))


def test_no_held_trial_is_not_in_committed_source():
    held = []
    for path in (ROOT / 'outputs/handover').rglob('regulatory_sources*.json'):
        manifest = read(path)
        for source in manifest.get('sources', []):
            name = source.get('document_path') or (source.get('held') or {}).get('held_in_tree')
            if not name:
                continue
            data = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)
            assert hashlib.sha256(data).hexdigest() == source['document_sha256']
            held.extend((manifest['slug'], d) for d in source.get('decisions', []))
    failures = []
    for path in (ROOT / 'docs/reviews').glob('*/review.json'):
        for outcome in read(path)['outcomes']:
            for row in outcome.get('known_missing_sensitivity', {}).get('rows', []):
                if row.get('value_status') != 'NOT_IN_COMMITTED_SOURCE':
                    continue
                for slug, decision in held:
                    ids = {decision.get('trial'), decision.get('nct'),
                           str(decision.get('trial_key', '')).replace('PMID ', '')}
                    if slug == path.parent.name and row['trial_key'] in ids:
                        failures.append((slug, decision['trial']))
    assert not failures, failures


def test_elixa_conflict_spans_held_and_elixa_pooled_only_by_signed_adjudication():
    """V1.0.1: ELIXA's held regulatory fact (8 page-located spans of the conflicting renderings) stays verified in the
    review; ELIXA enters the primary pool ONLY through the signed result-level adjudication, at the unrounded text
    interval, and the page states the prespecification dispute. (V1 asserted 'primary k=8 unchanged'; that was the
    requirement until the admission, and is now the requirement's opposite.)"""
    review = read(ROOT / 'docs/reviews' / SLUG / 'review.json')
    outcome = primary(review)
    fact = next(f for f in review['held_regulatory_facts'] if f['trial_key'] == '26630143')
    assert len(fact['spans']) >= 8 and 'definition_3p' in {s['kind'] for s in fact['spans']}
    assert {s['kind']: s['pdf_page'] for s in fact['spans']} == {
        'definition_3p': 24, 'text_unrounded_3p': 24, 'table8_onstudy_3p': 24,
        'table8_ontreatment_3p': 24, 'executive_summary_3p': 7,
        'primary_4p_table6': 22, 'primary_4p_text': 35, 'primary_4p_unrounded_text': 8}
    row = next(t for t in outcome['trials'] if t['id'] == 'PMID 26630143')
    assert row['provenance'] == 'signed_result_adjudication'
    assert (row['effect'], row['ci_low'], row['ci_high']) == (1.02, 0.887, 1.172)
    assert outcome['result']['k'] == 10
    assert '26630143' not in {r['trial_key'] for r in outcome['known_missing_sensitivity']['rows']}
    page = html.unescape((ROOT / 'docs/reviews' / SLUG / 'index.html').read_text(encoding='utf-8'))
    assert 'ELIXA PRESPECIFICATION DISPUTE' in page and 'Previously served: k = 8' in page


def test_primary_pool_recomputed_from_its_rows():
    """The served k=10 result is exactly synth.pool over the served rows (the V1 membership demonstration for ELIXA
    is gone: it is no longer a proposal beside the pool but a member of it)."""
    outcome = primary(read(ROOT / 'docs/reviews' / SLUG / 'review.json'))
    assert 'membership_demonstration' not in outcome['known_missing_sensitivity']
    studies = [Study(label=t['label'], effect=t['effect'], ci_low=t['ci_low'],
                     ci_high=t['ci_high'], measure='HR') for t in outcome['trials']]
    result = pool(studies, scale='HR')
    assert result.k == outcome['result']['k'] == 10
    for field in ('estimate', 'ci_low', 'ci_high'):
        assert outcome['result'][field] == pytest.approx(getattr(result, field), abs=5e-5)


def test_state_derivation_proposed_cannot_promote():
    from harness.invalidation import missing_state
    assert missing_state(discovered=False) == 'NOT_DISCOVERED'
    assert missing_state() == 'DISCOVERED_NOT_RETRIEVED'
    assert missing_state({'document_path': 'held'}) == 'SOURCE_RETRIEVED_NOT_EXTRACTED'
    fact = {'decision': {'decision': 'EXTRACTED'}, 'admissible': True,
            'adjudication': {'state': 'PROPOSED', 'countersigned': True}}
    assert missing_state(fact) == 'EXTRACTED_NOT_ADMISSIBLE'
    fact['adjudication']['state'] = 'ACCEPTED'
    assert missing_state(fact) == 'POOLABLE'
    fact['decision']['source_conflict'] = {'state': 'SOURCE_CONFLICT'}
    assert missing_state(fact) == 'EXTRACTED_SOURCE_CONFLICT'


def test_freedom_held_but_not_admitted_and_flow_admitted_only_by_signed_adjudication():
    outcome = primary(read(ROOT / 'docs/reviews' / SLUG / 'review.json'))
    rows = outcome['known_missing_sensitivity']['rows']
    freedom = next(r for r in rows if r['name'] == 'FREEDOM-CVO')
    assert freedom['value_status'] == 'EXTRACTED_NOT_ADMISSIBLE'
    assert freedom['held_fact']['admissible'] is False
    assert not freedom.get('sensitivity')
    assert freedom['held_fact']['trial_key'] not in {t['id'].replace('PMID ', '') for t in outcome['trials']}
    assert 'FLOW' not in {r['name'] for r in rows}
    flow_row = next(t for t in outcome['trials'] if t['id'] == 'PMID 38785209')
    assert flow_row['provenance'] == 'signed_result_adjudication'
    assert (flow_row['effect'], flow_row['ci_low'], flow_row['ci_high']) == (0.82, 0.68, 0.98)
    review = read(ROOT / 'docs/reviews' / SLUG / 'review.json')
    flow = next(f for f in review['held_regulatory_facts'] if f['trial'] == 'FLOW')
    assert flow['adjudication']['id'] == 'ADJ-GLP1-003'
    assert flow['spans'][0]['pdf_page'] == 25
    assert flow['spans'][0]['verbatim_located'] is True
