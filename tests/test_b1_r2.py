"""Review plants: deliberately altered source layouts are synthetic test inputs."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
import pytest
from harness import extract, typed_routes as tr, target_endpoint as te
from harness.table_rows import read_row

ROOT = Path(__file__).resolve().parents[1]

def table(header, row='10 (10.0)', extra=''):
    return ('<table-wrap><label>T</label><table><thead>' + header + '</thead><tbody>'
            '<tr><td>Any AE</td><td>' + row + '</td><td>' + row + '</td>' + extra +
            '</tr></tbody></table></table-wrap>')

def read(text, **kw):
    return read_row(text, table_label='T', row_label='Any AE', intervention='Drug', comparator='Placebo', **kw)[0]

def test_r1_frozen_bytes():
    assert (ROOT/'harness/target_endpoint.py').read_bytes() == subprocess.check_output(['git','show','0d95190c29:harness/target_endpoint.py'])

@pytest.mark.parametrize('field,value', [('ci_pct',90), ('analysis_set','per protocol'), ('comparator_direction','placebo vs empagliflozin'), ('scale','OR')])
def test_r1_typed_identity_checks(field, value):
    key = ('sglt2-primary-prevention-hf',tr.HF,'26378978')
    row = dict(tr.extract_bound(*key), id='PMID '+key[2])
    row[field] = value
    from harness import pipeline
    admit = getattr(pipeline, '_admit_rows', te.admit_rows)
    kept, refused = admit({'name':tr.HF}, [row])
    assert not kept and refused

def test_r2_rowspan():
    key = ('melatonin-primary-insomnia-sol','Adverse events','20712869')
    text = (ROOT/f'cache/{key[0]}/ft_{key[2]}.txt').read_text(encoding='utf-8')
    t = next(t for t in re.findall(r'<table-wrap\b.*?</table-wrap>',text,re.S) if '<label>Table 8</label>' in t)
    h = re.search(r'<thead>.*?</thead>',t,re.S).group()
    changed = '<tr><th rowspan="3">Category of AE</th><th colspan="2">Treatment period</th><th colspan="2">Extension period</th></tr><tr><th colspan="4"><hr/></th></tr><tr><th>PRM</th><th>Placebo</th><th>PRM</th><th>Placebo</th></tr>'
    text = t.replace(h,'<thead>'+changed+'</thead>')
    got,_ = read_row(text, **tr.ROUTES[key])
    assert got == dict(ai=136,n1i=394,ci=142,n2i=395)

def test_r2_km_is_not_count():
    h='<tr><th>Outcome</th><th>Drug N=100 KM estimate (%)</th><th>Placebo N=100 KM estimate (%)</th></tr>'
    with pytest.raises(ValueError): read(table(h))

def test_r2_dual_n():
    h='<tr><th>Outcome</th><th>Drug randomised N=100; safety N=99 n (%)</th><th>Placebo randomised N=100; safety N=99 n (%)</th></tr>'
    assert read(table(h,'0 (0.0)'))['n1i'] == 99

def test_r2_effect_period():
    h='<tr><th></th><th colspan="2">Year 1</th><th>Year 2</th></tr><tr><th>Outcome</th><th>Drug N=100 n (%)</th><th>Placebo N=100 n (%)</th><th>Hazard ratio (95% CI)</th></tr>'
    with pytest.raises(ValueError): read(table(h,extra='<td>1.43 (0.80-2.57)</td>'),period='Year 1',effect=True)

def test_r2_ascii_and_dash():
    assert (ROOT/'harness/table_rows.py').read_bytes().isascii()
    h='<tr><th>Outcome</th><th>Drug N=100 n (%)</th><th>Placebo N=100 n (%)</th><th>Hazard ratio (95% CI)</th></tr>'
    assert read(table(h,extra='<td>1.43 (0.80\u20132.57)</td>'),effect=True)['effect'] == 1.43

def test_r3_local_arm_order():
    s='Among probiotic and placebo recipients, adverse events occurred in 10/564 (1.8%): 3/279 (1.1%) in the placebo group and 7/285 (2.5%) in the probiotic group.'
    assert extract.extract_arm_counts(s,['probiotic'],['placebo']) == (7,285,3,279)

def test_r3_multiple_outcomes():
    s='Diarrhoea occurred in 30/100 (30%) probiotic and 10/100 (10%) placebo patients, and nausea in 5/100 (5%) and 2/100 (2%), respectively.'
    assert extract.extract_arm_counts(s,['probiotic'],['placebo']) == (30,100,10,100)

@pytest.mark.parametrize('s',[
    'Empagliflozin reduced hospitalization for heart failure by 35%, and the primary outcome occurred less often (hazard ratio, 0.86; 95% CI, 0.74 to 0.99).',
    'Hospitalization for heart failure or urgent heart failure visit (HR 0.70; 95% CI, 0.60 to 0.90).'])
def test_r4_hr_clause(s):
    with pytest.raises(ValueError): tr.sentence_hr(s)

def test_r5_missing_file(tmp_path):
    got=tr.for_outcome('probiotics-aad-prevention','Any adverse events',root=tmp_path)
    assert len(got)==2
    assert all(v['absent'] and v['kind']=='typed_refusal' and 'No such file' in v['reason'] for v in got.values())

def test_r6_abstract_permission(monkeypatch):
    monkeypatch.setattr(tr.copy_licence,'typed_may_read',lambda licence:False)
    with pytest.raises(ValueError,match='OPEN'):
        tr.extract_bound('sglt2-primary-prevention-hf',tr.HF,'28605608')

def test_r6_held_response():
    data=json.loads((ROOT/'registry/typed_source_licences.json').read_text())['26819227']
    raw=(ROOT/'registry/typed_source_licences/26819227.europepmc.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==data['response_sha256']
    assert json.loads(raw)['resultList']['result'][0]['id']=='26819227'

def test_r7_pinned_fixture():
    p=ROOT/'tests/fixtures/b1_served_values_0d95190c29.json'
    assert p.is_file()
    source=(ROOT/'tests/test_extract_b1_typed.py').read_text()
    assert 'read(f"docs/reviews/' not in source
    assert 'read("docs/reviews/' not in source

def test_r3_other_outcome_not_reused():
    s='Diarrhoea occurred in 30/100 (30%) probiotic and 10/100 (10%) placebo patients, and nausea in 5/100 (5%) and 2/100 (2%), respectively.'
    got=extract.extract_trial(s,['nausea'],['probiotic'],['placebo'])
    assert got.get('absent')

def test_typed_replay_traces_served_legacy_value():
    from harness.provenance_class import served_class
    data=json.loads((ROOT/'tests/fixtures/b1_served_values_0d95190c29.json').read_text())
    slug='dapagliflozin-hfpef-hosp'
    row=next(t for o in data['reviews'][slug]['outcomes'] if o['name']=='Adverse events' for t in o['trials'] if t['id']=='PMID 34711976')
    row=dict(row,provenance='abstract_verified',source='legacy hand-entered value')
    assert served_class(row,slug,'Adverse events',lambda _:False,{},str(ROOT))[0]=='EXTRACTOR'

def test_r2_generic_caption_is_not_count_type():
    h='<tr><th>Outcome</th><th>Drug N=100</th><th>Placebo N=100</th></tr>'
    text=table(h).replace('<table>', '<caption>Adverse events</caption><table>')
    with pytest.raises(ValueError): read(text)

def test_r2_unknown_analysis_set_refuses():
    h='<tr><th>Outcome</th><th>Drug randomised N=100; safety N=99 n (%)</th><th>Placebo randomised N=100; safety N=99 n (%)</th></tr>'
    with pytest.raises(ValueError): read(table(h,'0 (0.0)'),analysis_set='per protocol')

def test_r5_changed_source_is_row_refusal(tmp_path):
    import shutil
    slug='probiotics-aad-prevention'
    for ref in ['topics/'+slug+'.json','registry/typed_source_licences.json']+['cache/'+slug+'/ft_'+pid+'.txt' for pid in ('39529939','41699149')]:
        dest=tmp_path/ref
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/ref,dest)
    with (tmp_path/f'cache/{slug}/ft_39529939.txt').open('ab') as f: f.write(b' ')
    got=tr.for_outcome(slug,'Any adverse events',root=tmp_path)
    assert got['39529939']['absent'] and 'DIGEST_CHANGED' in got['39529939']['reason']
    assert got['41699149']['ai']==64

def test_r7_fixture_matches_pinned_blob():
    doc=json.loads((ROOT/'tests/fixtures/b1_served_values_0d95190c29.json').read_text())
    for slug, fixture in doc['reviews'].items():
        raw=subprocess.check_output(['git','show',doc['commit']+':'+fixture['source']])
        assert hashlib.sha256(raw).hexdigest()==fixture['sha256']
        original=json.loads(raw)
        for outcome in fixture['outcomes']:
            o=next(o for o in original['outcomes'] if o['name']==outcome['name'])
            for row in outcome['trials']:
                t=next(t for t in o['trials'] if t['id']==row['id'])
                assert row=={k:t[k] for k in row}
