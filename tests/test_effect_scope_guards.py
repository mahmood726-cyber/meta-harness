"""Plants from held CASTOR/POLLUX abstracts; effects are never invented."""
import json
from pathlib import Path
import pytest
from harness import extract, bench_routes
ROOT = Path(__file__).resolve().parents[1]
RECORDS = {r['id']:r for r in json.loads((ROOT/'cache/daratumumab-rrmm-pfs-bench/records.json').read_text(encoding='utf8'))['records']}
def effect(text, kws=None):
    return extract.extract_trial(text, kws or ['progression-free survival','PFS'], ['daratumumab'], ['dexamethasone'], estimand='HR')
def sentence(pid, starts):
    return next(s for s in extract._sentences(RECORDS[pid]['abstract']) if s.startswith(starts))
def test_population_words_alone_do_not_declare_subgroup():
    s = sentence('32482541','In lenalidomide-refractory')
    assert not extract.subgroup_refusal(s)
    assert effect(s)['effect'] == extract.extract_effect(s)[1]
def bench_rows():
    config = json.loads((ROOT/'topics/daratumumab-rrmm-pfs-bench.json').read_text(encoding='utf8'))
    return bench_routes.for_config(config)

def test_pfs2_sentence():
    # R3 architecture: the benchmark locator binds ITT; the shared extractor is frozen.
    row = bench_rows()['32001798']
    assert 'intent-to-treat population' in row['source_span']
    assert row['effect'] != extract.extract_effect(sentence('32001798','Median PFS on subsequent'))[1]
@pytest.mark.parametrize('pid,expected',[('32482541',.31),('32001798',.44)])
def test_whole_itt_effect_survives(pid,expected):
    assert effect(RECORDS[pid]['abstract']).get('effect') == expected
def test_explicit_pfs2_target():
    assert effect(sentence('32001798','Median PFS on subsequent'),['PFS2']).get('effect') == .53
@pytest.mark.parametrize('prefix',['Among lenalidomide-refractory patients','In the lenalidomide-refractory subgroup'])
def test_scope_variants(prefix):
    s=sentence('32482541','In lenalidomide-refractory')
    text = s.replace('In lenalidomide-refractory patients',prefix)
    if 'subgroup' in prefix:
        assert effect(text).get('absent')
    else:
        assert not extract.subgroup_refusal(text)
def test_second_progression():
    s=sentence('32001798','Median PFS on subsequent')
    assert effect(s.replace('PFS on subsequent line of therapy (PFS2)','PFS to second progression')).get('absent')

def test_spelled_out_pfs2_from_dreamm7():
    row = bench_rows()['40680754']
    assert row.get('absent') and 'effect' not in row
    assert 'PFS2' in row['reason']
