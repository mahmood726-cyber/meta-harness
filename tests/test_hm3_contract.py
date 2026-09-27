"""Synthetic gate plant and outcome-specific verified input contracts."""
import json
from pathlib import Path

import pytest

from harness import absence, gate, harms, missing_effect, pipeline
from harness.verified_inputs import entries, for_outcome


def test_hm3_gate_plant(tmp_path):
    spec = {'name': 'Adverse events', 'keywords': ['adverse events'], 'estimand': 'RR'}
    out = {'name': spec['name'], 'kind': 'harm', 'trials': [],
           'declared_absent_trials': [{'id': 'fixture', 'reason_code': 'OUTCOME_NOT_IN_SOURCE'}],
           'result': {'present': False}}
    harms.annotate_outcome(out, spec, [{'id': 'fixture'}],
                           {'fixture': {'abstract': 'Adverse events were similar between groups.'}})
    (tmp_path / 'review.json').write_text(json.dumps({'outcomes': [out]}), encoding='utf-8')
    failure = gate.check_harms_complete(str(tmp_path))
    assert len(failure) == 1 and 'HARMS_INCOMPLETE' in failure[0]
    row = out['declared_absent_trials'][0]
    row.update(typed_refusal=True, refusal_provenance=absence.REFUSED_ON_EVIDENCE,
               source_span='Adverse events were similar between groups.')
    row.update(absence.classify_reason(spec['keywords'], row['source_span'],
        reason='Narrative comparison has no counts or effect with CI.', row=row))
    out['result'] = {'present': False}
    harms.annotate_outcome(out, spec, [{'id': 'fixture'}],
                           {'fixture': {'abstract': row['source_span']}})
    assert row['harm_absence_state'] == harms.RETRIEVED_REFUSED_WITH_REASON
    (tmp_path / 'review.json').write_text(json.dumps({'outcomes': [out]}), encoding='utf-8')
    assert gate.check_harms_complete(str(tmp_path)) == []


def test_spurious_signal_is_a_cited_refusal_not_certified_absence():
    span = 'Bleeding was excluded from the primary efficacy endpoint.'
    row = dict(id='fixture', typed_refusal=True, refusal_provenance=absence.SIGNAL_SPURIOUS,
               source_span=span)
    row.update(absence.classify_reason(['bleeding'], span, reason='Efficacy definition only.', row=row))
    out = dict(name='Bleeding', kind='harm', trials=[], declared_absent_trials=[row], result={'present': False})
    harms.annotate_outcome(out, {'name':'Bleeding'}, [{'id':'fixture'}], {'fixture':{'abstract':span}})
    assert row['harm_absence_state'] == harms.RETRIEVED_REFUSED_WITH_REASON
    assert not out['result'].get('harm_absence_certified')


@pytest.mark.parametrize('code,span', [('REFUSED_ON_EVIDENCE','invented'), ('made-up-code','Held text.')])
def test_typed_refusal_fails_closed(code, span):
    with pytest.raises(ValueError, match='held verbatim span'):
        absence.classify_reason([], 'Held text.', reason='Reason.', row={
            'typed_refusal':True, 'refusal_provenance':code, 'source_span':span})


def test_multiple_verified_outcomes_preserve_primary_and_harm(tmp_path, monkeypatch):
    folder = tmp_path / 'cache' / 'fixture'
    folder.mkdir(parents=True)
    primary = dict(outcome='Primary', override=True, ai=2,n1i=20,ci=4,n2i=20,source='2/20 versus 4/20')
    harm = dict(outcome='Harm', override=True, ai=1,n1i=20,ci=3,n2i=20,source='1/20 versus 3/20')
    data = {'fixture':[primary,harm]}
    (folder/'verified_arms.json').write_text(json.dumps(data),encoding='utf-8')
    monkeypatch.setattr(pipeline, 'ROOT', str(tmp_path))
    loaded = pipeline._load_verified_arms('fixture')
    for name, expected in [('Primary',2),('Harm',1)]:
        result = pipeline._build_outcome({'name':name,'keywords':[name],'estimand':'RR'},
            'harm' if name=='Harm' else 'efficacy', [{'id':'fixture','id_type':'pmid'}],
            {'fixture':{'abstract':'Randomized placebo comparison.'}}, ['drug'], ['placebo'],
            verified_arms=loaded)
        assert result['trials'][0]['ai'] == expected
    from harness.verified_inputs import normalise
    assert for_outcome({'fixture': primary}, 'Primary') == {'fixture': normalise(primary)}
    with pytest.raises(ValueError, match='Duplicate'):
        entries([primary,primary])


def test_missing_effect_does_not_borrow_a_harm(tmp_path):
    folder = tmp_path/'cache'/'fixture'
    folder.mkdir(parents=True)
    primary = dict(outcome='Primary', effect=0.8,ci_low=0.6,ci_high=0.9,scale='HR')
    harm = dict(outcome='Harm', effect=1.5,ci_low=1.1,ci_high=2.0,scale='HR')
    (folder/'verified_effects.json').write_text(json.dumps({'1':[primary,harm]}),encoding='utf-8')
    ambiguous = missing_effect.enrich_from_cache(str(tmp_path),'fixture',[{'id':'1'}])
    assert 'effect' not in ambiguous[0]
    matched = missing_effect.enrich_from_cache(str(tmp_path),'fixture',[{'id':'1','outcome':'Primary'}])
    assert matched[0]['effect'] == 0.8
    (tmp_path/'topics').mkdir()
    (tmp_path/'topics/fixture.json').write_text(json.dumps({'primary_outcome':{'name':'Primary'}}),encoding='utf-8')
    legacy_caller = missing_effect.enrich_from_cache(str(tmp_path),'fixture',[{'id':'1'}])
    assert legacy_caller[0]['effect'] == 0.8


def test_all_hm3_decisions_have_verbatim_source_and_digits():
    root = Path(__file__).resolve().parents[1]
    decisions = json.loads((root/'docs/evidence/hm3-held-source-audit/decisions.json').read_text(encoding='utf-8'))
    assert len(decisions) == 50
    for d in decisions:
        e = d['entry']
        source = root / e['document_ref']
        if source.name == 'records.json':
            recs = json.loads(source.read_text(encoding='utf-8'))['records']
            held = next(r['abstract'] for r in recs if str(r['id']) == d['trial'])
        else:
            held = source.read_text(encoding='utf-8')
        span = e.get('source_span') or e['source']
        assert span in held
        for field in ('ai','n1i','ci','n2i','effect','ci_low','ci_high'):
            if field in e:
                assert str(e[field]) in span or format(e[field], '.2f') in span
        assert _decision_present_or_declared_superseded(root, d, e, span), (d['topic'], d['trial'], e.get('outcome'))


def _decision_present_or_declared_superseded(root, d, e, span):
    """The requirement: an HM3 decision is either still in the cache verbatim, or it was superseded BY DECLARATION --
    named in the supersession file for its page AND the cache carries the superseding row, which points back to the
    decision it replaced (supersedes.provenance) and carries the declared values. An undeclared removal fails.
    (FREEDOM serious infection: REFUSED_ON_EVIDENCE superseded by the pooled companion-report row, 2026-09-27.)"""
    from harness.verified_inputs import normalise
    cached = json.loads((root/'cache'/d['topic']/d['file']).read_text(encoding='utf-8'))
    canonical = normalise(e)
    canonical.setdefault('source_span', span)
    if d['trial'] in cached and canonical in entries(cached[d['trial']]):
        return True
    p = root/'docs/evidence/hm3-held-source-audit/screening_roles_supersession.json'
    sup = json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
    declared = ((sup.get('pages') or {}).get(d['topic']) or {}).get('harm_decisions_superseded') or {}
    decl = declared.get(f"{e.get('outcome')}|{d['trial']}")
    if not decl or not str(decl.get('before', '')).startswith(str(e.get('provenance'))):
        return False
    for fname in ('verified_arms.json', 'verified_effects.json'):
        f = root/'cache'/d['topic']/fname
        if not f.exists():
            continue
        for r in entries(json.loads(f.read_text(encoding='utf-8')).get(d['trial']) or []):
            if (r.get('outcome') == e.get('outcome') and (r.get('supersedes') or {}).get('provenance') == e.get('provenance')
                    and all(r.get(k) == v for k, v in (decl.get('values_after') or {}).items())):
                return True
    return False


def test_an_undeclared_removal_of_an_hm3_decision_fails(tmp_path):
    # PLANT: the superseded FREEDOM decision with its declaration removed -> must fail; with it -> passes
    import shutil
    root = Path(__file__).resolve().parents[1]
    decisions = json.loads((root/'docs/evidence/hm3-held-source-audit/decisions.json').read_text(encoding='utf-8'))
    d = next(x for x in decisions if x['trial'] == '19671655')
    (tmp_path/'docs/evidence/hm3-held-source-audit').mkdir(parents=True)
    (tmp_path/'docs/evidence/hm3-held-source-audit/screening_roles_supersession.json').write_text('{"pages": {}}', encoding='utf-8')
    (tmp_path/'cache'/d['topic']).mkdir(parents=True)
    for fname in ('verified_arms.json', 'verified_effects.json'):
        shutil.copyfile(root/'cache'/d['topic']/fname, tmp_path/'cache'/d['topic']/fname)
    e = d['entry']
    span = e.get('source_span') or e['source']
    assert _decision_present_or_declared_superseded(root, d, e, span)
    assert not _decision_present_or_declared_superseded(tmp_path, d, e, span)
