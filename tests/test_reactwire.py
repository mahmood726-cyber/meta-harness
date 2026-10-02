"""REACTWIRE plants; synthetic edits never become research data."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from harness import recovery_binding as rb, recovery_excerpt as rx, recovery_map, page
from scripts.react_figure_proposal import bacc_note, binding_bytes, verify_binding

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'tocilizumab-covid19-mortality'
# Regenerating the binding verifies the recorded readings against the held WHO REACT figure image, which is JAMA
# copyright and held locally only (not redistributed; sha256 in HELD.json). Where it is absent the replay cannot run:
# skip VISIBLY (repo convention), never fail as if the artifact were stale, never pass silently.
FIGURE = ROOT / 'evidence/acquisition_cascade/held/WHO-REACT/jama-e2111330-g001.jpg'
needs_figure = pytest.mark.skipif(not FIGURE.exists(), reason='WHO REACT figure image is held locally only')


def artifact():
    return json.loads((ROOT / rb.FIGURE_BINDING).read_text(encoding='utf-8'))


def review():
    data = json.loads((ROOT / 'docs/reviews' / SLUG / 'review.json').read_text(encoding='utf-8'))
    recovery_map.attach(data, SLUG, root=ROOT)
    return data


def intercept(monkeypatch, data):
    read = Path.read_text
    monkeypatch.setattr(Path, 'read_text', lambda p, *a, **kw:
                        json.dumps(data) if p.as_posix().endswith(rb.FIGURE_BINDING) else read(p, *a, **kw))


@needs_figure
def test_committed_artifact_replays_byte_for_byte():
    assert verify_binding(ROOT)
    assert binding_bytes(ROOT) == binding_bytes(ROOT)
    data = artifact()
    assert all(r['reasons'] for r in data['gate_rows'] if r['status'] != 'ADMITTED')


@pytest.mark.parametrize('old,new', [(b'Safety Population', b'Unknown Population'),
                                    (b'33085857', b'00000000')])
def test_own_paper_schema_or_identifier_defect_refused(monkeypatch, old, new):
    read = Path.read_bytes
    monkeypatch.setattr(Path, 'read_bytes', lambda p:
                        read(p).replace(old, new) if p.name == 'ft_33085857.txt' else read(p))
    with pytest.raises(ValueError, match='BACC_PAPER_REFUSED'):
        bacc_note(ROOT)


@needs_figure
def test_stale_edited_count_fails_regeneration(monkeypatch):
    data = artifact()
    data['entries'][0]['figure_counts']['ai'] += 1
    original = Path.read_bytes
    monkeypatch.setattr(Path, 'read_bytes', lambda p:
                        json.dumps(data).encode() if p.as_posix().endswith(rb.FIGURE_BINDING) else original(p))
    with pytest.raises(ValueError, match='STALE_FIGURE_BINDING'):
        verify_binding(ROOT)


@pytest.mark.parametrize('defect,reason', [
    ('ids', 'record_ids'), ('entry_ids', 'record_ids'), ('count', 'conflict state'),
    ('float', 'typed figure counts'), ('pool', 'nonpoolability'),
    ('population', 'population'), ('excerpt', 'gate witness/excerpt'),
    ('inventory', 'inventory'), ('refused', 'unnamed refusal'),
])
def test_artifact_defects_fail_closed(monkeypatch, defect, reason):
    data = artifact()
    first = data['entries'][0]
    if defect == 'ids': data['record_ids'] = []
    elif defect == 'entry_ids': first['record_ids'] = []
    elif defect == 'count': first['figure_counts']['ai'] += 1
    elif defect == 'float': first['figure_counts']['ai'] = 9.0
    elif defect == 'pool': first['poolable'] = True
    elif defect == 'population': first['population_equivalence'] = 'ADJUDICATED'
    elif defect == 'excerpt':
        for row in data['gate_rows']: row['table1_evidence'] = {}
    elif defect == 'inventory': data['entries'].pop()
    elif defect == 'refused': first.update(state='REFUSED', reasons=[])
    intercept(monkeypatch, data)
    with pytest.raises(ValueError, match='FIGURE_BINDING_REFUSED:.*' + reason):
        rb.attach(review(), SLUG, root=ROOT)


def test_conflict_and_refusal_remain_visible_and_never_poolable(monkeypatch):
    data = artifact()
    # Synthetic changed figure count, consistently represented by its gate witness.
    entry = data['entries'][1]
    entry['figure_counts']['ai'] += 1
    entry.update(state='CONFLICT', conflicts=['ai'])
    for row in data['gate_rows']:
        if row['row']['trial'] == entry['trial']:
            row['row']['ai'] += 1
    refused = data['entries'][2]
    refused.update(state='REFUSED', reasons=['SYNTHETIC_PLANT: unreadable figure row'])
    refused.pop('figure_counts')
    intercept(monkeypatch, data)
    bindings = rb.attach(review(), SLUG, root=ROOT)
    assert next(b for b in bindings if b['trial'] == entry['trial'])['state'] == 'CONFLICT'
    assert next(b for b in bindings if b['trial'] == refused['trial'])['state'] == 'REFUSED'
    for bound in bindings:
        with pytest.raises(ValueError): rb.require_poolable(bound)
    assert 'SYNTHETIC_PLANT' in page._recovery_html(next(b for b in bindings if b['state'] == 'REFUSED'))


def test_poolable_forgery_refused_and_correct_display_does_not_change_inputs():
    data = review()
    before = deepcopy(data)
    ledger = rb.attach(data, SLUG, root=ROOT)
    assert ledger and all(b['state'] == 'CROSS_PROVIDER_VERIFIED' and b['poolable'] is False for b in ledger)
    for old, new in zip(before['outcomes'], data['outcomes']):
        assert old.get('result') == new.get('result')
        assert old.get('trials') == new.get('trials')
        if '28-day' not in new['name']:
            assert old == new
    for row in ledger:
        with pytest.raises(ValueError, match='RELAYED_COUNTS_NOT_BOUND'):
            rb.require_poolable(dict(row, poolable=True, state='ANALYSIS_READY'))
    html = page.render_page(data)
    assert html.count("data-recovery-figure='CROSS_PROVIDER_VERIFIED'") == len(artifact()['entries'])
    unmatched = data['outcomes'][0]['recovery_figure_unmatched']
    assert [e['figure_binding']['trial'] for e in unmatched] == ['REMAP-CAP']
    assert 'NO_MATCHING_REVIEW_ROW' in unmatched[0]['reason']
    assert 'model-transcribed from the held figure; arithmetic and reading-consensus checked; not independently cell-verified' in html
    assert '9/161 vs 4/82' in html and '9/161 vs 3/81' in html
    assert artifact()['entries'][0]['own_paper']['explanation'] in html
    assert 'never pooled: population not adjudicated' in html
    assert 'relayed:' in html
    assert rb.attach(data, 'unrelated-topic', root=ROOT) == []


def test_display_escapes_held_text():
    entry = artifact()['entries'][0]
    entry['own_paper']['explanation'] = '<script>synthetic plant</script>'
    html = page._recovery_html({'figure_binding': entry})
    assert '<script>' not in html and '&lt;script&gt;' in html


def test_model_import_and_held_access_barrier_in_real_build():
    code = r'''
import builtins, json
from pathlib import Path
original_import = builtins.__import__
def blocked(name, *a, **kw):
    if name == 'reproducible_ai' or name.startswith('reproducible_ai.'):
        raise ImportError('MODEL_IMPORT_REFUSED: ' + name)
    return original_import(name, *a, **kw)
builtins.__import__ = blocked
try:
    import reproducible_ai
except ImportError as e:
    assert 'MODEL_IMPORT_REFUSED' in str(e)
else:
    raise AssertionError('barrier plant did not fire')
from harness import recovery_binding as rb, recovery_map, page
original_open = Path.open
def guarded(p, *a, **kw):
    if any(x in p.as_posix() for x in ('evidence/model_calls', 'acquisition_cascade/held', 'ft_33085857')):
        raise AssertionError('HELD_ONLY_READ_REFUSED: ' + str(p))
    return original_open(p, *a, **kw)
Path.open = guarded
root = Path.cwd()
slug = 'tocilizumab-covid19-mortality'
review = json.loads((root / 'docs/reviews' / slug / 'review.json').read_text(encoding='utf-8'))
recovery_map.attach(review, slug, root=root)
rb.attach(review, slug, root=root)
assert 'model-transcribed from the held figure; arithmetic and reading-consensus checked; not independently cell-verified' in page.render_page(review)
print('MODEL_IMPORT_REFUSED plant; build/render PASS without model package, records, image or own-paper reads')
'''
    result = subprocess.run([sys.executable, '-c', code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_base_harness_pre_fix_ignores_missing_ids_and_stale_counts(monkeypatch):
    source = subprocess.run(['git', '--no-optional-locks', 'show', 'HEAD:harness/recovery_binding.py'],
                            cwd=ROOT, capture_output=True, text=True, check=True).stdout
    namespace = {'__name__': 'harness._reactwire_base', '__package__': 'harness'}
    exec(compile(source, 'base recovery_binding.py', 'exec'), namespace)
    data = artifact()
    data['record_ids'] = []
    data['entries'][0]['figure_counts']['ai'] += 1
    intercept(monkeypatch, data)
    old = namespace['attach'](review(), SLUG, root=ROOT)
    summary = [{k: b[k] for k in ('trial', 'state', 'binding', 'numerator', 'denominator', 'poolable')} for b in old]
    print('PRE_FIX=' + json.dumps(summary, sort_keys=True))
    assert all(b['binding'] == 'PARTIAL' and b['numerator'] == 'RELAYED' for b in old)
    with pytest.raises(ValueError, match='record_ids'):
        rb.attach(review(), SLUG, root=ROOT)
