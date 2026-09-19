"""Synthetic safety plants; none of these fixture records enter research caches."""
import importlib.util
import pytest
from harness import membership, page


def attach(review, nodes):
    if importlib.util.find_spec('harness.trial_family'):
        from harness.trial_family import attach_review
        attach_review(review, nodes)


def fixture():
    records = [{'id': key, 'nct': 'NCT00000001', 'title': 'Synthetic randomized controlled trial'}
               for key in ('fixture-a', 'fixture-b')]
    if importlib.util.find_spec('harness.trial_family'):
        from harness.trial_family import families
        nodes = families(records, config={'primary_outcome': {'name': 'synthetic outcome'}})
    else:
        nodes = [{'family_id': 'NCT00000001', 'source_records': records,
                  'eligibility': {'state': 'ELIGIBLE'}}]
    return records, nodes


def test_two_reports_of_one_nct_pooled_as_two_trials_refused():
    records, nodes = fixture()
    review = {'outcomes': [{'name': 'synthetic outcome', 'primary': True, 'trials': records}]}
    with pytest.raises(ValueError, match='DUPLICATE_FAMILY'):
        attach(review, nodes)
        membership.build_outcome_membership(review['outcomes'][0])


def test_eligible_family_without_poolable_value_is_named_in_missing_panel():
    _, nodes = fixture()
    nodes[0]['eligibility'] = {'state': 'ELIGIBLE', 'span': {'fixture': 'synthetic decision'}}
    review = {'outcomes': [{'name': 'synthetic outcome', 'primary': True, 'trials': []}]}
    attach(review, nodes)
    render = getattr(page, '_trial_families', lambda r: '')
    html = render(review)
    assert 'missing-evidence' in html and 'NCT00000001' in html and 'UNKNOWN' in html


def test_deleting_source_record_degrades_ledger_state():
    records, nodes = fixture()
    review = {'outcomes': [{'name': 'synthetic outcome', 'primary': True, 'trials': records[:1]}]}
    attach(review, nodes)
    nodes[0]['source_records'] = []
    attach(review, nodes)
    assert nodes[0]['eligibility']['state'] == 'UNKNOWN'
    assert nodes[0]['eligibility']['absence_code'] == 'SOURCE_RECORD_DELETED'


def test_mixed_primary_pooled_report_requires_source_localized_parent():
    import json
    from pathlib import Path
    from harness import trial_family
    root = Path(__file__).resolve().parents[1]
    slug = 'doac-vte-recurrence'
    records = json.loads((root/'cache'/slug/'records.json').read_text(encoding='utf8'))
    config = json.loads((root/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    nodes = trial_family.prepare(root,slug,records['records']+records['ctgov'],config)
    node = next(f for f in nodes if any(r['report_id']=='24344086' for r in f['reports']))
    source = next(r for r in node['source_records'] if r['id']=='24344086')
    evidence = source['family_parent_evidence']
    assert evidence['quote'] in source['abstract']
    assert evidence['registry_row']['nct_id'] == node['family_id'] == 'NCT00680186'
    assert evidence['registry_row']['acronym'] in evidence['quote']
    assert 'NCT00291330' in source['mentioned_registry_ids']


def test_family_render_is_stable_under_canonical_json_roundtrip():
    import json
    from pathlib import Path
    from harness.canonical import canonical_json
    from harness.page import render_page
    root = Path(__file__).resolve().parents[1]
    review = json.loads((root/'docs/reviews/tocilizumab-covid19-mortality/review.json').read_text(encoding='utf8'))
    review.pop('reproduction', None)
    def reverse_keys(value):
        if isinstance(value, dict):
            return {key: reverse_keys(value[key]) for key in reversed(value)}
        if isinstance(value, list):
            return [reverse_keys(item) for item in value]
        return value
    for family in review['trial_families']:
        family['eligibility'] = reverse_keys(family['eligibility'])
        family['lifecycle'] = reverse_keys(family['lifecycle'])
    assert render_page(review) == render_page(json.loads(canonical_json(review)))


def test_refused_pool_is_not_claimed_as_pooled_family():
    records, nodes = fixture()
    nodes[0]['eligibility'] = {'state':'ELIGIBLE','span':{'fixture':'synthetic decision'}}
    review = {'outcomes':[{'name':'synthetic outcome','primary':True,'trials':records[:1],
                          'result':{'pool_refused':{'code':'SYNTHETIC_REFUSAL'}}}]}
    attach(review,nodes)
    assert review['family_count_chain']['contributing'] == 1
    assert review['family_count_chain']['pooled'] == 0
    assert nodes[0]['poolability'][0]['state'] != 'POOLED'
    assert review['outcomes'][0]['membership']['pooled_family_count'] == 0
    assert review['family_missing_evidence'][0]['family_id'] == 'NCT00000001'
