"""INTEGRATE3 policy plants: disclosure retains pools; decided refusals remain."""
from copy import deepcopy
from test_integrate2 import row, outcome, prepare, codes
from harness import lane_integration as lane, screening_record, page


def test_within_family_mismatch_is_disclosed_without_refusal():
    o = outcome([row(), row(id='<script data-mix>bad()</script>', scale='HR')])
    prepare(o)
    assert len(o['trials']) == 2 and not o['declared_absent_trials']
    assert o['measure_mix']['classes'] == ['HAZARD_RATIO', 'RISK_RATIO']
    assert 'MEASURE_MIX_POOLED' in codes(o)
    assert 'MEASURE_MIX_POOLED' not in screening_record.BLOCKING


def test_mixed_pool_cannot_waive_odds_target():
    o = outcome([row(), row(id='B',scale='HR')])
    spec = dict(name='event',estimand='OR',timepoint='28 days')
    lane.prepare(o,spec,{}, {})
    lane.finish(o,spec)
    assert not o['trials'] and o['result']['state'] == 'LANE_REFUSED'
    assert all(t['lane_refusals'] == ['TARGET_MEASURE_UNAVAILABLE'] for t in o['declared_absent_trials'])
    assert 'TARGET_MEASURE_UNAVAILABLE' in screening_record.BLOCKING


def test_same_measure_has_no_mix_disclosure():
    o = outcome([row(),row(id='B')],result=dict(k=2,estimate=.8))
    prepare(o)
    assert 'MEASURE_MIX_POOLED' not in codes(o)
    assert 'measure_mix' not in o and 'measure_mix' not in o['result']
    assert o['result']['estimate'] == .8


def test_positive_timepoint_mismatch_blocks_gate_but_missing_target_does_not():
    o = outcome([row(source='day 60')])
    prepare(o)
    issues = screening_record.consistency_problems({'outcomes':[o]})
    assert next(p for p in issues if p['kind']=='TIMEPOINT_MISMATCH')['blocking'] is True
    o = outcome([row()])
    lane.prepare(o,dict(name='event',estimand='RR'),{}, {})
    issues = screening_record.consistency_problems({'outcomes':[o]})
    assert next(p for p in issues if p['kind']=='TARGET_TIMEPOINT_MISSING')['blocking'] is False
    assert len(o['trials']) == 1


def test_held_odds_counts_preserve_registered_k2_ci_refusal():
    import json
    from pathlib import Path
    from harness import pipeline
    root = Path(__file__).resolve().parents[1]
    slug = 'corticosteroids-covid19-mortality'
    cfg = json.loads((root/'topics'/f'{slug}.json').read_text(encoding='utf-8'))
    records = json.loads((root/'cache'/slug/'records.json').read_text(encoding='utf-8'))
    review = pipeline.build_review_core(slug,cfg,records,'lane')
    primary = next(o for o in review['outcomes'] if o.get('primary'))
    assert primary['result']['k'] == 2
    assert primary['result']['served_measure'] == 'ODDS_RATIO'
    assert primary['result']['pooled_ci_refused']['code'] == 'K2_SINGLE_DF'
    assert {r['id'] for r in primary['trials']} == {'PMID 32678530', 'PMID 32876695'}
