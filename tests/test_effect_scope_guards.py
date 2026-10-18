"""Plants from held CASTOR/POLLUX abstracts; effects are never invented."""
import json
import hashlib
import shutil
import subprocess
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
@pytest.mark.xfail(strict=True, reason='KNOWN LIMIT (bench r3 ruling, review closed at three rounds): the SHARED extractor is frozen byte-identical to main; this correction lives in the topic-local typed routes (harness/bench_routes.py), proven by tests/test_bench_r3.py::test_bench_route_bound_or_refused')
@pytest.mark.parametrize('pid',['32482541','32001798'])
def test_whole_itt_effect_survives(pid, tmp_path):
    pin = bench_routes.load_pins(ROOT)[pid]
    assert effect(RECORDS[pid]['abstract']).get('effect') == pin['value']['effect']
    assert {k: bench_rows()[pid][k] for k in pin['value']} == pin['value']
    mutated = mutated_route(tmp_path, pid, RECORDS[pid]['abstract'].replace(pin['anchor'], 'Unbound endpoint'))
    assert mutated.get('absent') and 'effect' not in mutated

def mutated_route(root, pid, text):
    ref = Path('cache/daratumumab-rrmm-pfs-bench/records.json')
    doc = json.loads((ROOT/ref).read_text(encoding='utf8'))
    next(r for r in doc['records'] if r['id'] == pid)['abstract'] = text
    (root/ref).parent.mkdir(parents=True, exist_ok=True)
    (root/ref).write_text(json.dumps(doc), encoding='utf8')
    pinref = Path('tests/fixtures/r3_bench_route_pins.json')
    (root/pinref).parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/pinref, root/pinref)
    config = json.loads((ROOT/'topics/daratumumab-rrmm-pfs-bench.json').read_text(encoding='utf8'))
    return bench_routes.for_config(config, root=root)[pid]

def test_shared_extractor_byte_identical_to_main():
    baseline = subprocess.check_output(['git', 'show', '0d95190c29:harness/extract.py'], cwd=ROOT)
    assert hashlib.sha256((ROOT/'harness/extract.py').read_bytes()).digest() == hashlib.sha256(baseline).digest()
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
@pytest.mark.xfail(strict=True, reason='KNOWN LIMIT (bench r3 ruling, review closed at three rounds): the SHARED extractor is frozen byte-identical to main; this correction lives in the topic-local typed routes (harness/bench_routes.py), proven by tests/test_bench_r3.py::test_bench_route_bound_or_refused')
def test_second_progression(tmp_path):
    s=sentence('32001798','Median PFS on subsequent')
    assert effect(s.replace('PFS on subsequent line of therapy (PFS2)', 'PFS to second progression')).get('absent')
    row = mutated_route(tmp_path, '32001798', s.replace('PFS on subsequent line of therapy (PFS2)','PFS to second progression'))
    assert row.get('absent') and 'effect' not in row

def test_spelled_out_pfs2_from_dreamm7():
    row = bench_rows()['40680754']
    assert row.get('absent') and 'effect' not in row
    assert 'PFS2' in row['reason']
