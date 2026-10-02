"""Synthetic plants exercise the exact functions invoked by the build."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from harness import lane_integration as lane, pipeline, screening_record, result_status, fetch
ROOT=Path(__file__).resolve().parents[1]

def row(**kw):
    return dict(dict(id='plant-A',label='plant-A',effect=.8,ci_low=.6,ci_high=1.1,scale='RR',source='at 28 days'),**kw)

def outcome(rows, **kw):
    return dict(dict(name='event',kind='primary',trials=rows,declared_absent_trials=[]),**kw)

def prepare(o, **kw):
    spec=dict(name=o['name'],estimand='RR',timepoint='28 days',**kw)
    cfg={'primary_outcome':spec}
    lane.prepare(o,spec,cfg,{})
    return lane.finish(o,spec)

def codes(o): return {p['code'] for p in o['lane_problems']}

def test_time_mismatch_and_normalization():
    o=outcome([row(source='day 60')]); prepare(o)
    assert not o['trials'] and 'TIMEPOINT_MISMATCH' in codes(o)
    o=outcome([row(source='study day 29; day 1 = inclusion')]); prepare(o)
    assert len(o['trials'])==1 and o['trials'][0]['typed_timepoint']['elapsed_days']==28

def test_missing_time_target_preserves_numeric_inputs():
    o=outcome([row()]); spec={'name':'event','estimand':'RR'}
    o['result']={'k':1,'estimate':.8,'ci_low':.6,'ci_high':1.1}
    lane.prepare(o,spec,{},{});lane.finish(o,spec)
    assert len(o['trials'])==1 and o['result']['estimate']==.8
    assert o['result']['timepoint_target']=='MISSING'
    assert 'TARGET_TIMEPOINT_MISSING' not in screening_record.BLOCKING

def test_unknown_source_time_is_disclosed_not_positive_mismatch():
    o=outcome([row(source='at trial end')]);prepare(o)
    assert o['trials'][0]['typed_timepoint']['refusal']=='TIMEPOINT_UNSTATED'

def test_measure_mix_and_negative():
    o=outcome([row(),row(id='plant-B',scale='HR')]);prepare(o)
    assert len(o['trials']) == 2 and 'MEASURE_MIX_POOLED' in codes(o)
    assert not o['declared_absent_trials']
    assert o['measure_mix']['classes'] == ['HAZARD_RATIO', 'RISK_RATIO']
    assert 'MEASURE_MIX_POOLED' not in screening_record.BLOCKING
    o=outcome([row(),row(id='plant-B')]);prepare(o)
    assert len(o['trials'])==2
    assert 'measure_mix' not in o and 'MEASURE_MIX_POOLED' not in codes(o)

def test_odds_boundary_and_first_event_disclosure():
    o=outcome([row()]);spec={'name':'event','estimand':'OR'}
    lane.prepare(o,spec,{},{});assert 'TARGET_MEASURE_UNAVAILABLE' in codes(o)
    o=outcome([row(scale='HR')]);o['result']={'estimate':.8};prepare(o)
    assert len(o['trials']) == 1 and not o['declared_absent_trials']
    assert o['result']['served_measure'] == 'HAZARD_RATIO'
    assert o['result']['measure_disclosure']['target_measure'] == 'RISK_RATIO'

def test_explicit_or_reconstruction_keeps_numeric_transformation():
    r={'id':'plant','label':'plant','ai':3,'n1i':20,'ci':5,'n2i':20}
    assert lane.measure(r,{'estimand':'OR'}).value=='ODDS_RATIO'
    assert lane.measure(r,{'estimand':'RR'}).value=='RISK_RATIO'

def test_population_inconsistency_and_negative():
    o=outcome([row(source='safety population')],kind='harm',declared_absent_trials=[row(id='refused',source='safety population',reason_code='POPULATION_MISMATCH')])
    lane.prepare(o,{'name':'event'}, {'harm_outcomes':[{'name':'event'}]}, {})
    assert 'POPULATION_RULE_INCONSISTENT' in codes(o) and not o['trials']
    o=outcome([row(source='safety population')],kind='harm')
    lane.prepare(o,{'name':'event'}, {'harm_outcomes':[{'name':'event'}]}, {})
    assert len(o['trials'])==1 and o['population_rule']['safety']=='SAFETY_POPULATION'

def test_count_units_mix():
    a={'id':'a','ai':3,'n1i':20,'ci':4,'n2i':20,'source':'patients with events'}
    o=outcome([a,dict(a,id='b',source='5 episodes')]);prepare(o)
    assert 'UNIT_MIX_POOLED' in codes(o) and not o['trials']
    o=outcome([a,dict(a,id='b')]);prepare(o);assert len(o['trials'])==2

@pytest.mark.parametrize('name,flag',[('major bleeding','NON_CABG'),('dyspnoea','LEADING_TO_DISCONTINUATION')])
def test_variant_refusal_and_negative(name,flag):
    o=outcome([row(table_row={'variant_flags':[flag]})],name=name);prepare(o)
    assert 'VARIANT_ROW_MISMATCH' in codes(o) and not o['trials']
    o=outcome([row(table_row={'variant_flags':[]})],name=name);prepare(o);assert o['trials']

def test_relay_guard_and_source_negative():
    o=outcome([row(provenance='RELAYED')]);prepare(o)
    assert not o['trials'] and 'RELAYED_COUNTS_NOT_BOUND' in codes(o)
    o=outcome([row(recovery_map={'state':'ANALYSIS_READY','provenance':'RELAYED','relayed_counts':{'ai':3}})]);prepare(o)
    assert not o['trials'] and 'RELAYED_COUNTS_NOT_BOUND' in codes(o)
    o=outcome([row()]);prepare(o);assert o['trials']

def test_shared_control_and_km():
    a=dict(id='a',label='a',trial_id='trial',control_id='c',control_n=20,control_events=4,ai=3,n1i=20,ci=4,n2i=20)
    o=outcome([a,dict(a,id='b')]);prepare(o)
    assert 'SHARED_CONTROL_DOUBLE_COUNTED' in codes(o)
    o=outcome([dict(a)]);prepare(o);assert o['trials']
    o=outcome([dict(a,ai=2,source='Kaplan-Meier incidence 10%.')])
    lane.prepare(o,{'name':'event'}, {}, {'a':{'abstract':'Kaplan-Meier incidence 10%.'}})
    assert 'KM_PERCENT_TO_COUNT' in codes(o)

def test_table_parser_failure_is_typed(tmp_path):
    d=tmp_path/'cache'/'topic';d.mkdir(parents=True)
    (d/'bad.tables.txt').write_text('unparseable',encoding='utf-8')
    r=lane.table_entry(dict(row(),document_ref='bad.tables.txt'),d)
    assert r['table_binding']['state']=='REFUSED'
    o=outcome([r]);prepare(o);assert o['trials']  # prior source binder remains authoritative

def test_table_footnote_and_conflict(tmp_path):
    d=tmp_path/'cache'/'topic';d.mkdir(parents=True)
    text='# source sha256: '+'a'*64+'\n=== TABLES (excerpt) ===\nTABLE event\nOutcome | Odds ratio\nevent | 0.8 (0.6-1.1)\nFootnote: hazard ratio for all rows\n'
    (d/'x.tables.txt').write_text(text,encoding='utf-8')
    r=lane.table_entry(dict(row(),document_ref='x.tables.txt',source_span='event | 0.8 (0.6-1.1)'),d)
    assert r['scale']=='HR' and r['table_row']['measure_basis']=='footnote'
    r=lane.table_entry(dict(r,effect=.9),d);assert r['table_conflict']=='TABLE_VALUE_MISMATCH'

def test_published_preference_preserves_ratio_audit():
    counts=dict(id='plant',label='plant',ai=20,n1i=100,ci=40,n2i=100,source='at 28 days')
    hr=row(scale='HR');rr=row(scale='RR',effect=.5,ci_low=.3,ci_high=.8)
    selected=lane.select_estimator(counts,[hr,rr],'RR',['RR'])
    assert selected['scale']=='HR' and selected['effect']==hr['effect']
    assert any(a.get('scale')=='RR' and a.get('ratio_label_audit') for a in selected['alternatives'])

def test_recovery_status_preserved():
    r=row(recovery_map={'state':'COUNTS_RECOVERED','reason':'RELAYED_COUNTS_NOT_BOUND'})
    assert result_status.status_of(r,False,set())['state']=='COUNTS_RECOVERED'
    assert result_status.status_of(r,True,set())['state']=='ADMITTED'

def test_empty_build_and_gate():
    o=pipeline._build_outcome({'name':'event','keywords':['event'],'estimand':'RR'},'primary',[],{},[],[])
    assert o['result']['timepoint_target']=='MISSING'
    assert o['result']['target_measure']=='RISK_RATIO'
    assert any(p['kind']=='TARGET_TIMEPOINT_MISSING' for p in screening_record.consistency_problems({'outcomes':[o]}))

def test_held_build_uses_wiring():
    slug='tocilizumab-covid19-mortality'
    cfg=json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
    rv=pipeline.build_review_core(slug,cfg,fetch.ensure(cfg,''),'lane')
    assert all('target_measure' in o['result'] for o in rv['outcomes'])
    assert rv['recovery_map']
    from harness.page import render_page
    rendered=render_page(rv)
    assert 'typed_timepoint' in rendered and 'CROSS_PROVIDER_VERIFIED' in rendered
    assert 'model-transcribed from the held figure; arithmetic and reading-consensus checked; not independently cell-verified' in rendered and 'NOT_ADJUDICATED' in rendered
    bindings = rv['recovery_bindings']
    assert bindings and all(b['denominator'] == 'CROSS_PROVIDER_VERIFIED' and b['numerator'] == 'CROSS_PROVIDER_VERIFIED'
                            and not b['poolable'] for b in bindings)


def test_same_span_within_family_preserves_published_selection():
    selected=row(scale='RR',effect=.3)
    alternative=row(scale='HR',effect=.8)
    actual=lane.select_estimator(selected,[alternative],'HR',[])
    assert actual['effect']==.3 and actual['scale']=='RR'


def test_derived_safety_policy_does_not_amend_protocol_admission():
    o=outcome([row(source='intention-to-treat')],kind='harm')
    lane.prepare(o,{'name':'event'}, {'harm_outcomes':[{'name':'event'}]}, {})
    assert len(o['trials'])==1
    assert o['trials'][0]['population_decision']['allowed'] is False
    assert 'DISCLOSURE' in o['trials'][0]['population_decision']['scope']


def test_peer_preference_preserves_endpoint_components():
    selected=row(scale='IRR',source='total heart failure hospitalizations')
    alternative=row(scale='HR',source='cardiovascular death or heart failure hospitalization')
    actual=lane.select_estimator(selected,[alternative],'HR',['HR'])
    assert actual['scale']=='IRR'


def test_new_disclosures_in_browser():
    import os
    from harness import page as renderer
    pytest.importorskip('playwright')
    from playwright.sync_api import sync_playwright
    candidates=[Path(os.environ.get('PROGRAMFILES(X86)',''))/'Microsoft/Edge/Application/msedge.exe',
                Path(os.environ.get('PROGRAMFILES',''))/'Google/Chrome/Application/chrome.exe']
    exe=next((p for p in candidates if p.is_file()),None)
    assert exe, 'Local browser required; no downloads'
    r=row(result_status={'state':'ADMITTED'},table_binding={'state':'REFUSED','reason':'<script data-plant>bad()</script>'})
    o=outcome([r,row(id='<script data-mix>bad()</script>',scale='HR')],result={'k':2,'estimate':.8,'ci_low':.6,'ci_high':1.1,'scale':'RR'})
    spec={'name':'event','estimand':'RR'}
    lane.prepare(o,spec,{},{});lane.finish(o,spec)
    html=renderer._outcome_block(o,show_inputs=False)+renderer._status_html(r,o)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=str(exe),headless=True)
        try:
            page=browser.new_page()
            page.route('**/*',lambda route:route.abort())
            page.set_content(html)
            text=page.locator('body').inner_text()
            assert 'Protocol measure: RISK_RATIO' in text
            assert 'target timepoint: MISSING' in text
            assert 'typed_timepoint' in text and 'table_binding' in text
            assert page.locator('script[data-plant]').count()==0
            assert 'Mixed measures (advisory)' in text
            assert 'served measure: UNKNOWN' in text
            assert not o['declared_absent_trials']
            assert 'RISK_RATIO' in text
            assert page.locator('script[data-mix]').count()==0
        finally:
            browser.close()


def test_origin_binds_verbatim_span_even_when_source_is_a_citation():
    r=row(source='held abstract citation',source_span='Deaths at study day 29.',timepoint_span='study day 29')
    o=outcome([r]);spec={'name':'event','estimand':'RR','timepoint':'28 days'}
    lane.prepare(o,spec,{}, {'plant-A':{'abstract':'Day 1 is inclusion. Deaths at study day 29.'}})
    assert o['trials'] and r['typed_timepoint']['elapsed_days']==28
    assert 'TIMEPOINT_MISMATCH' not in codes(o)


def test_origin_respects_explicit_held_document(tmp_path, monkeypatch):
    monkeypatch.setattr(lane,'__file__',str(tmp_path/'harness'/'lane_integration.py'))
    (tmp_path/'source.txt').write_text('Day 0 is baseline. Deaths at day 28.',encoding='utf-8')
    r=row(source='citation',source_span='Deaths at day 28.',timepoint_span='day 28',document_ref='source.txt')
    o=outcome([r]);spec={'name':'event','estimand':'RR','timepoint':'28 days'}
    lane.prepare(o,spec,{}, {'plant-A':{'abstract':'Day 1 is inclusion. Deaths at day 28.'}})
    assert o['trials'] and r['typed_timepoint']['elapsed_days']==28
    assert r['typed_timepoint']['origin']=='DAY0_IS_BASELINE'
