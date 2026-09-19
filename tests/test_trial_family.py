"""Behavioral plants. Fallback exercises the landing-3 implementation before FN exists."""
import importlib.util
import json
from pathlib import Path
import pytest
from harness import identity

ROOT = Path(__file__).resolve().parents[1]

def build(records, **kwargs):
    if importlib.util.find_spec('harness.trial_family'):
        from harness.trial_family import families
        return families(records, **kwargs)
    units = identity.build_publication_units(records, kwargs.get('companion_reports'))
    groups = {}
    for r in records:
        u = units[str(r['id'])]
        f = groups.setdefault(u['trial_family_id'], {'family_id': u['trial_family_id'], 'reports': []})
        f['reports'].append({'report_id': r['id'], 'role': u['publication_role']})
    return list(groups.values())

@pytest.mark.parametrize('slug,child,parent', [
    ('colchicine-secondary-cv-prevention', '32407460', '31733140'),
    ('colchicine-secondary-cv-prevention', '34446156', '32865380'),
])
def test_held_companion_attaches_to_registry_parent(slug, child, parent):
    records = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))['records']
    subset = [r for r in records if r['id'] in {child, parent}]
    assert len(subset) == 2
    companions = json.loads((ROOT/'docs/study_families.json').read_text(encoding='utf8'))['topics'][slug]
    fs = build(subset, companion_reports=companions)
    assert len(fs) == 1, 'two publications must count as one trial family'
    parent_record = next(r for r in subset if r['id'] == parent)
    if parent_record.get('nct'):
        assert fs[0]['family_id'] == parent_record['nct']
    else:
        # LoDoCo2 has no NCT but its held abstract names its ANZCTR registration.
        import re
        registry_id = re.search(r'ACTRN\d+',parent_record['abstract']).group()
        assert fs[0]['family_id']==registry_id
        assert fs[0]['identity_flag']=='IDENTITY_FROM_HELD_TEXT'
        assert next(r for r in fs[0]['reports'] if r['report_id']==child)['role']=='SUBGROUP'

def test_synthetic_three_reports_one_node_three_roles():
    records = [dict(id='fixture-primary', nct='NCT00000001', pubtypes=['Randomized Controlled Trial']),
               dict(id='fixture-subgroup', nct='NCT00000001', title='A subgroup analysis'),
               dict(id='fixture-protocol', nct='NCT00000001', title='Trial protocol')]
    fs = build(records)
    assert len(fs) == 1
    assert {r['role'] for r in fs[0]['reports']} == {'PRIMARY', 'SUBGROUP', 'PROTOCOL'}

@pytest.mark.parametrize('title,expected', [
    ('FREEDOM open-label extension', 'EXTENSION'),
    ('DIRECT 3-year open-label continuation', 'EXTENSION'),
    ('FREEDOM-CVO randomized controlled trial', 'PRIMARY'),
    ('STEP 6 post-hoc analysis', 'SECONDARY_ANALYSIS'),
    ('PLATO subgroup analysis', 'SUBGROUP'),
    ('EMPA-KIDNEY post-trial follow-up', 'EXTENSION'),
])
def test_publication_role_plants(title, expected):
    # Explicitly synthetic text plants, not source validation of these trials.
    r = build([dict(id='fixture-report', title=title)])[0]['reports'][0]
    assert r['role'] == expected
    if 'open-label' in title:
        assert r['randomised_contrast_preserved'] is False

def test_unknown_role_is_not_primary():
    assert build([{'id': 'fixture-unknown'}])[0]['reports'][0]['role'] == 'ROLE_UNRESOLVED'

def test_acronym_without_shared_arms_does_not_merge_trials():
    assert len(build([{'id':'fixture-a','acronym':'SAME'}, {'id':'fixture-b','acronym':'SAME'}])) == 2

@pytest.mark.parametrize('plant,agent,left,right', [
    ('MIRO-CKD','dapagliflozin',['dapagliflozin','balcinrenone'],['dapagliflozin']),
    ('PYY1875','semaglutide',['semaglutide','pyy1875'],['semaglutide']),
    ('CRUSADERS','saline',['saline','balanced fluid'],['saline','balanced fluid']),
    ('COVID STEROID 2','dexamethasone',['dexamethasone 12 mg'],['dexamethasone 6 mg']),
    ('RECOVERY high-dose','dexamethasone',['dexamethasone 20 mg'],['dexamethasone 6 mg']),
])
def test_structural_negative_contrasts(plant, agent, left, right):
    from harness.trial_family import randomised_contrasts
    arms = [{'arm_id':str(i),'linkage_complete':True,'active_interventions':v,'span':{'fixture':plant}}
            for i,v in enumerate([left,right])]
    assert randomised_contrasts(arms,[agent],True) == []

def test_positive_contrast_and_missing_linkage_fail_closed():
    from harness.trial_family import randomised_contrasts
    arms = [{'arm_id':'a','linkage_complete':True,'active_interventions':['drug a','metformin'],'span':'synthetic a'},
            {'arm_id':'b','linkage_complete':True,'active_interventions':['metformin'],'span':'synthetic b'}]
    assert len(randomised_contrasts(arms,['drug a'],True)) == 1
    assert not randomised_contrasts(arms,['drug a'],False)
    arms[1]['linkage_complete'] = False
    assert not randomised_contrasts(arms,['drug a'],True)

def test_family_graph_key_membership_and_source_join():
    from harness import claimgraph
    row = {'id':'PMID 12345678','family_id':'NCT00000001','state':'NOT_REPORTED'}
    assert claimgraph._family_key(row) == 'NCT00000001'
    assert claimgraph.trial_key(row) == '12345678'  # source joins remain report-keyed
    assert claimgraph.lookup_trial({'12345678':{'overall':'low'}}, row) == {'overall':'low'}
    _, obj = claimgraph.membership_object({'name':'fixture','declared_absent_trials':[row,dict(row,id='PMID 22345678')]})
    assert obj['value'] == {'NOT_REPORTED':1}

def test_held_step6_attaches_to_registry_and_is_secondary():
    from harness.trial_family import prepare
    slug = 'semaglutide-obesity-weight'
    d = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    f = next(f for f in prepare(ROOT,slug,d['records']+d['ctgov'],cfg)
             if any(r['report_id']=='40189961' for r in f['reports']))
    assert f['family_id']=='NCT03811574'
    assert next(r for r in f['reports'] if r['report_id']=='40189961')['role']=='SECONDARY_ANALYSIS'

def test_discovered_glp1_families_and_source_validation():
    from harness.trial_family import prepare
    slug = 'glp1-ra-mace-t2d'
    d = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    fs = prepare(ROOT,slug,d['records']+d['ctgov'],cfg)
    by_report = {r['report_id']:f for f in fs for r in f['reports']}
    assert '34526024' not in by_report
    for rid,nct in [('38785209','NCT03819153'),('34873344','NCT01455896'),('40162642','NCT03914326')]:
        assert by_report[rid]['family_id']==nct
        raw = json.loads((ROOT/'cache'/slug/'family_registry.json').read_text(encoding='utf8'))
        assert raw['report_links'][rid][0]['nct_id']==nct
    assert next(r for r in by_report['34873344']['reports'] if r['report_id']=='34873344')['role']=='PRIMARY'
    assert all(len(f['outcome_status'])==3 for f in fs)

def test_outcome_availability_does_not_change_family_eligibility():
    from harness.trial_family import screen_family
    f = {'registry_design':{'allocation':'RANDOMIZED'},
         'population':{'conditions':{'value':['type 2 diabetes'],'span':'synthetic condition'}},
         'arms':[{'drug':{'value':['placebo']}}], 'randomised_contrasts':[{'fixture':'contrast'}]}
    cfg = {'include':{'population_any':['type 2 diabetes'],'comparator_any':['placebo']}}
    decision = screen_family(f,cfg)
    f['outcome_status'] = [{'reported':{'state':'NO'}}]
    assert screen_family(f,cfg)==decision
    assert decision['state']=='ELIGIBLE'

def test_page_family_table_escapes_held_text_and_counts_nodes():
    from harness.trial_family import attach_review
    from harness.page import _trial_families
    fs = build([{'id':'fixture-primary','title':'randomized controlled trial <script>','nct':'NCT00000001'}])
    review = {'screening':{'records':[{'id':'fixture-primary','decision':'include'}]},'outcomes':[]}
    attach_review(review,fs)
    html = _trial_families(review)
    assert 'id="trial-families"' in html and 'NCT00000001' in html
    assert '<script>' not in html
    assert 'Families screened 1 of 1' in html

@pytest.mark.parametrize('rid', ['25403903','28546097'])
def test_held_extensions_cannot_supply_standalone_comparison(rid):
    d = json.loads((ROOT/'docs/trial_family_held_plants.json').read_text(encoding='utf8'))
    r = dict(next(r for r in d['records'] if r['id']==rid))
    links = d['links'][rid]
    # Prefer the held report's explicit identifier; never arbitrarily choose
    # between multiple AACT registrations of the same cited publication.
    nct = r.get('nct') or (links[0]['nct_id'] if len(links)==1 else None)
    assert nct and any(link['nct_id']==nct for link in links)
    r['nct'] = nct
    fs = build([r, {'id':nct,'id_type':'nct'}])
    assert len(fs)==1 and fs[0]['family_id']==nct
    report = next(x for x in fs[0]['reports'] if x['report_id']==rid)
    assert report['role']=='EXTENSION'
    assert report['randomised_contrast_preserved'] is False
    assert report['standalone_pool_eligible'] is False

def test_held_empa_kidney_followup_attaches_without_guessing_role():
    d = json.loads((ROOT/'docs/trial_family_held_plants.json').read_text(encoding='utf8'))
    r = next(r for r in d['records'] if r['id']=='39453837')
    current = json.loads((ROOT/'cache/sglt2-ckd-progression/records.json').read_text(encoding='utf8'))['records']
    parents = [p for p in current if p.get('nct')==r['nct']]
    assert parents
    fs = build(parents+[r])
    assert len(fs)==1
    report = next(x for x in fs[0]['reports'] if x['report_id']==r['id'])
    assert report['role']=='ROLE_UNRESOLVED'  # held title alone is insufficient

def test_registry_priority_and_deterministic_synthetic_identity():
    from harness.trial_family import families
    r = {'id':'fixture','registry_ids':['jRCT123','ISRCTN12345','2010-123456-12','NCT00000001']}
    assert families([r])[0]['family_id']=='NCT00000001'
    assert families([{'id':'fixture','isrctn':'ISRCTN12345'}])[0]['identity_flag']=='IDENTITY_FROM_HELD_TEXT'
    rs = [{'id':'fixture-b','doi':'10.fixture/shared'}, {'id':'fixture-a','doi':'10.fixture/shared'}]
    assert families(rs)==families(list(reversed(rs)))

def test_doi_relation_collapses_parent_and_child():
    rs = [{'id':'fixture-parent','doi':'10.fixture/parent'},
          {'id':'fixture-child','doi':'10.fixture/child','related_dois':['10.fixture/parent']}]
    assert len(build(rs))==1

def test_multi_trial_report_never_bridges_distinct_registrations():
    rs = [{'id':'fixture-a','nct':'NCT00000001'}, {'id':'fixture-b','nct':'NCT00000002'},
          {'id':'fixture-combined','abstract':'Trials NCT00000001 and NCT00000002.'}]
    fs = build(rs)
    assert len(fs)==3
    combined = next(f for f in fs if any(r['report_id']=='fixture-combined' for r in f['reports']))
    assert combined['family_id'].startswith('SYN-')
    assert 'MULTIPLE_REGISTRY_PARENTS' in combined['flags']
    assert set(combined['aliases']['mentioned_registry_ids'])=={'NCT00000001','NCT00000002'}

def test_held_plato_subgroup_overrides_incompatible_registry_citation():
    from harness.trial_family import prepare
    slug = 'ticagrelor-vs-clopidogrel-acs'
    d = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    f = next(f for f in prepare(ROOT,slug,d['records']+d['ctgov'],cfg)
             if any(r['report_id']=='20802246' for r in f['reports']))
    assert f['family_id']=='NCT00391872'
    assert {'19717846','20802246'} <= {r['report_id'] for r in f['reports']}
    r = next(r for r in f['source_records'] if r['id']=='20802246')
    assert r['identity_source']['source']=='held acronym + shared registry arms'
    assert r['identity_link_conflicts']['rows'][0]['nct_id']=='NCT02748330'
