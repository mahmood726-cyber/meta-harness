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


def test_elixa_conflict_spans_primary_unchanged():
    review = read(ROOT / 'docs/reviews' / SLUG / 'review.json')
    outcome = primary(review)
    rows = outcome['known_missing_sensitivity']['rows']
    row = next(r for r in rows if r['trial_key'] == '26630143')
    assert row['value_status'] == 'EXTRACTED_SOURCE_CONFLICT'
    assert len(row['held_fact']['spans']) >= 8
    assert 'definition_3p' in {s['kind'] for s in row['held_fact']['spans']}
    page = html.unescape((ROOT / 'docs/reviews' / SLUG / 'index.html').read_text(encoding='utf-8'))
    assert row['held_fact']['document_sha256'] in page
    assert 'ADJ-GLP1-005 PROPOSED (not countersigned)' in page
    for span in row['held_fact']['spans']:
        assert span['span'] in page
        assert span['pdf_page'] > 0
    assert {s['kind']: s['pdf_page'] for s in row['held_fact']['spans']} == {
        'definition_3p': 24, 'text_unrounded_3p': 24, 'table8_onstudy_3p': 24,
        'table8_ontreatment_3p': 24, 'executive_summary_3p': 7,
        'primary_4p_table6': 22, 'primary_4p_text': 35, 'primary_4p_unrounded_text': 8}
    base = json.loads(subprocess.check_output(['git', 'show', f'237e9094:docs/reviews/{SLUG}/review.json']))
    assert outcome['result']['k'] == 8
    assert outcome['result'] == primary(base)['result']
    from harness.page import _stale_topic_overview
    assert '1.02' not in _stale_topic_overview(review)


def test_membership_demonstration_recomputed():
    outcome = primary(read(ROOT / 'docs/reviews' / SLUG / 'review.json'))
    demo = outcome['known_missing_sensitivity']['membership_demonstration']
    assert demo['state'] == 'HETEROGENEITY_MEMBERSHIP_SENSITIVE'
    studies = [Study(label=t['label'], effect=t['effect'], ci_low=t['ci_low'],
                     ci_high=t['ci_high'], measure='HR') for t in outcome['trials']]
    elixa = next(r for r in outcome['known_missing_sensitivity']['rows'] if r['trial_key'] == '26630143')
    effect = elixa['held_fact']['decision']['effect']
    added = Study(label='ELIXA', effect=effect['estimate'], ci_low=effect['ci_low'], ci_high=effect['ci_high'], measure='HR')
    for key, members in [('primary', studies), ('proposed', studies + [added])]:
        result = pool(members, scale='HR')
        for field in ('k', 'estimate', 'ci_low', 'ci_high', 'tau2', 'pi_low', 'pi_high'):
            assert demo[key][field] == pytest.approx(getattr(result, field), abs=1e-12)
        assert demo[key]['i2'] == pytest.approx(max(0, (result.Q - (result.k-1))/result.Q)*100)
    assert demo['proposed']['pi_high'] > 1
    page = (ROOT / 'docs/reviews' / SLUG / 'index.html').read_text(encoding='utf-8')
    assert demo['state'] in page
    assert 'under the PROPOSED adjudication -- not a result; the primary k=8 pool is unchanged' in page


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


def test_flow_and_freedom_held_but_not_admitted():
    outcome = primary(read(ROOT / 'docs/reviews' / SLUG / 'review.json'))
    rows = outcome['known_missing_sensitivity']['rows']
    for name in ('FLOW', 'FREEDOM-CVO'):
        row = next(r for r in rows if r['name'] == name)
        assert row['value_status'] == 'EXTRACTED_NOT_ADMISSIBLE'
        assert row['held_fact']['admissible'] is False
        assert not row.get('sensitivity')
        assert row['held_fact']['trial_key'] not in {t['id'].replace('PMID ', '') for t in outcome['trials']}
    flow = next(r['held_fact'] for r in rows if r['name'] == 'FLOW')
    assert flow['adjudication']['id'] == 'ADJ-GLP1-003'
    assert flow['adjudication']['state'] == 'PROPOSED'
    assert flow['spans'][0]['pdf_page'] == 25
    assert flow['spans'][0]['verbatim_located'] is True
