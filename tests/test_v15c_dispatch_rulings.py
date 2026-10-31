"""16 Oct item rulings: source-derived effects, never publishing signatures."""
import copy
import hashlib
import json
from pathlib import Path

import pytest

from harness import enforcement, pipeline, served_pool_additions
from scripts import v15c_decisions as generator
from test_ncsrc_v15c import baseline

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / 'outputs/m2_pretriage/ncsrc-2026-10-16/pretriage.json'


def rereads():
    return json.loads(PRE.read_text(encoding='utf8'))


def test_v15c_dispatch_item_decisions():
    doc = generator.build()
    for i, source in enumerate(rereads(), 1):
        row = next(r for r in doc['rows'] if (r['slug'], r['outcome'], r['id']) ==
                   (source['slug'], source['outcome'], source['id']))
        assert row['ruling']['item_id'] == f'R{i}'
        assert row['ruling']['state'] == 'DECIDED_BY_DISPATCH_ON_DELEGATION'
        assert row['decision'] == ('ADMIT' if i <= 5 else 'REFUSE')
        if i != 5:
            assert row['source_ref'] == source['source_ref']
            assert row['source_sha256'] == source['source_sha256']
        if i <= 3:
            assert row['span'] == source['proposal']['span']
            assert row['served'] == source['served']
        if i == 6:
            assert row['class'] == 'NOT_ADMISSIBLE_LICENCE'
            assert row['licence_statement'] == source['licence_statement']


def outcome(monkeypatch, slug):
    old = copy.deepcopy(baseline(slug)['outcomes'][0])
    monkeypatch.setattr(served_pool_additions, 'admitted_rows', lambda *a: old['trials'])
    spec = json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf8'))['primary_outcome']
    records = json.loads((ROOT / "cache" / slug / "records.json").read_text(encoding="utf8"))["records"]
    rec_by_id = {str(r["id"]): r for r in records}
    return pipeline._build_outcome(spec, 'continuous' if slug.startswith('esketamine') else 'efficacy',
                                   [], rec_by_id, [], [], slug=slug)


def test_v15c_conversion_and_unchanged_madrs(monkeypatch):
    out = outcome(monkeypatch, 'esketamine-trd-madrs')
    assert {k: out['result'][k] for k in ('estimate', 'ci_low', 'ci_high', 'k')} == {
        'estimate': -3.3436, 'ci_low': -6.0691, 'ci_high': -0.618, 'k': 4}
    t = next(t for t in out['trials'] if t['id'] == 'NCT02417064')
    c = t['declared_conversion']
    assert '6.5.2.10' in c['reference']
    assert len(c['inputs']) == 3
    assert c['output'] == pytest.approx({k: t[k] for k in ('mean1','sd1','nc1','mean2','sd2','nc2')}, abs=1e-12, rel=0)
    page = (ROOT / 'harness/page.py').read_text(encoding='utf8')
    assert '_declared_conversion_block(t)' in page
    assert 'single_trial_results' in page


def test_v15c_licence_await_single_trials(monkeypatch):
    out = outcome(monkeypatch, 'tocilizumab-covid19-mortality')
    assert out['result']['present'] is False
    assert out['result']['reason'] == ('No admissible pooled result: 1 of 3 eligible trials '
                                      '(TOCIBRAS) awaits an open-licence source')
    assert not {'estimate','ci_low','ci_high'}.intersection(out['result'])
    assert [r['label'] for r in out['single_trial_results']] == ['RECOVERY', 'COVACTA']
    assert out['single_trial_results'][0]['result']['k'] == 1
    covacta = next(t for t in out['trials'] if t['id'] == 'NCT04320615')
    assert covacta['provenance'] == 'published_rate'
    assert 'source_acquisitions/' in covacta['source']
    assert covacta['declared_conversion']['output'] == {k: covacta[k] for k in ('ai','n1i','ci','n2i')}
    assert all(t['result']['k'] == 1 for t in out['single_trial_results'])


def test_v15c_licence_rule_does_not_touch_evidence_refusals():
    absent = [{'id':'a', 'state':'REFUSED_ON_EVIDENCE', 'enforcement':{'decision':'REFUSE',
               'class':'NOT_ADMISSIBLE_LICENCE', 'kind':'refused_on_evidence'}}]
    assert enforcement.licence_await([], absent) is None
    assert enforcement.licence_await([], [{'id':'a','reason_code':'NOT_ADMISSIBLE_LICENCE'}]) is None


def test_v15c_dispatch_blast_radius():
    rows = generator.build()['rows']
    touched = sorted({(r['slug'], r['outcome']) for r in rows if r['decision']=='REFUSE'
                      and r.get('class')=='NOT_ADMISSIBLE_LICENCE' and r.get('kind')!='refused_on_evidence'})
    assert touched == [('tocilizumab-covid19-mortality','28-day all-cause mortality')]


def test_v15c_dispatch_provenance_and_v6_01_ack():
    doc = json.loads((ROOT / 'registry/v15c_dispatch_rulings_2026-10-16.json').read_text(encoding='utf8'))
    assert set(doc['items']) == {*(f'R{i}' for i in range(1,7)), 'V6-01'}
    assert doc['pretriage_sha256'] == hashlib.sha256(PRE.read_bytes()).hexdigest()
    for item in doc['items'].values():
        assert item['state'] == 'DECIDED_BY_DISPATCH_ON_DELEGATION'
        assert item['basis'] == "Dispatch relay, 16 Oct, item-by-item ruling on Mahmood's delegation"
    ack = doc['items']['V6-01']
    assert ack['after'] == {'estimate':1.0074, 'ci_low':0.8391, 'ci_high':1.2094, 'k':3}
    assert ack['conclusion_changed'] is False
    assert ack['reviewer_countersignature']['state'] == 'OPEN'


def test_v15c_dispatch_enforcement_never_claims_mahmood_signed():
    for source in rereads():
        trial = dict(source['served'], id=source['id'], label=source['label'],
                     endpoint_admissibility='UNBOUND_LEGACY')
        kept, absent = enforcement.apply(source['slug'], {'name':source['outcome']}, [trial])
        row = (kept + absent)[0]
        assert row['enforcement']['ruling']['state'] == 'DECIDED_BY_DISPATCH_ON_DELEGATION'
        assert not row['enforcement'].get('signed')
        if absent:
            assert row['reason'].startswith('Dispatch item ruling refusal: ')
        else:
            assert row['endpoint_binding'] == 'dispatch_source_binding'
