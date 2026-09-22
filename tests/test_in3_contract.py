import copy
import json
from pathlib import Path
import pytest
from harness import compat_check, manuscript, membership, scope_identity
from harness.page import _scope_identity_block
from harness.pipeline import _build_outcome
from _families import eligible_by_construction  # noqa: E402  (families ELIGIBLE by construction: the admission gate is on by default)

ROOT=Path(__file__).resolve().parents[1]

def test_verified_abstract_effect_retains_its_source_provenance():
    span='Major bleeding hazard ratio 0.7, 95% CI 0.5 to 0.9.'
    outcome=_build_outcome({'name':'Major bleeding','estimand':'HR','keywords':['major bleeding']},
        'harm',[{'id':'fixture','id_type':'pmid'}],{'fixture':{'abstract':span}},['drug'],['placebo'],
        verified_effects={'fixture':{'outcome':'Major bleeding','override':True,
            'effect':0.7,'ci_low':0.5,'ci_high':0.9,'scale':'HR',
            'provenance':'abstract_verified','source':span}},
        family_nodes=eligible_by_construction({'fixture': {}}))
    assert outcome['trials'][0]['provenance']=='abstract_verified'

def test_offline_integrity_missing_pmid_is_not_checked():
    integ=membership.integrity_with_membership(
        {'per_pmid': {'1': {'retracted': True}}},
        [{'trials':[{'id':'PMID 1'},{'id':'PMID 2'}]}])
    assert integ['n_pubmed_checked']==1
    assert integ['n_not_assessed']==1
    rows={v['pubmed_key']:v for v in integ['per_trial'].values()}
    assert rows['1']['retracted'] is True
    assert rows['2']['state']=='NOT_ASSESSED'
    assert rows['2']['pubmed_checked'] is False
    assert 'retracted' not in rows['2']

def test_scope_qualification_does_not_depend_on_pool_success():
    scope={'verdict':scope_identity.SCOPE_MISMATCH,'search_scope':{'retrieval_class':'KNOWN_ITEM_RETRIEVAL'}}
    review={'scope_identity':scope,'screening':{'records':[{'id':'fixture','decision':'include'}]},
            'outcomes':[{'primary':True,'result':{'pool_refused':{'reason':'fixture'}}}]}
    html=_scope_identity_block(review)
    assert scope_identity.qualification_text(scope,1) in html
    assert scope_identity.check_scope_identity(review,html)==[]

def test_compatibility_numbers_are_derived_not_whitelisted():
    review={'outcomes':[{'trials':[{'admission':{'follow_up_window':{'trial_value':'47 days'},
                           'endpoint_definition':{'trial_value':{'duration_threshold':'>=83 seconds'}}}}]}]}
    assert {'47','83'} <= manuscript.object_numerals(review)
    assert '14' not in manuscript.object_numerals(review)
    assert '30' not in manuscript.object_numerals(review)

def test_typed_harm_incompatibility_resolves_debt_only_with_valid_span():
    slug='doac-vte-recurrence'
    source=json.loads((ROOT/f'cache/{slug}/records.json').read_text(encoding='utf-8'))
    r=json.loads((ROOT/f'docs/reviews/{slug}/review.json').read_text(encoding='utf-8'))
    o=next(o for o in r['outcomes'] if o['name']=='Major bleeding')
    row=next(t for t in o['declared_absent_trials'] if '23808982' in t['id'])
    fixture={'slug':slug,'outcomes':[{'primary':True,'trials':[{'id':'PMID 23808982'}]},
              {'name':'Major bleeding','kind':'harm','trials':[],
               'declared_absent_trials':[copy.deepcopy(row)],'result':{'present':False}}]}
    compat_check._apply_harms_incomplete(fixture,source)
    assert not fixture['outcomes'][1].get('harms_incomplete')
    fixture['outcomes'][1]['declared_absent_trials'][0]['source_span']='invented source'
    with pytest.raises(ValueError):
        compat_check._apply_harms_incomplete(fixture,source)
