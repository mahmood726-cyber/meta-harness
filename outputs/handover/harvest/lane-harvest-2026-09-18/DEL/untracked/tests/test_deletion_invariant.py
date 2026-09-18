"""Deletion plants on real reviews; no clinical fixtures or network acquisition.

Spans, GRADE and limitations are deleted at the production core -> census boundary.
Cache rows are deleted before build_review_core. Search is a separate release gate.
"""
import copy
import json
import shutil
from pathlib import Path

import pytest

from harness import census, pipeline, registration, search_completeness
from harness.synth import method_text
from scripts.retraction_survival import MARKS, text

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ('glp1-ra-mace-t2d', 'sacubitril-valsartan-hfref')
OBJECTS = ('definition_span', 'result_span', 'grade_domain', 'trial_row',
           'search_candidate', 'retraction')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def core(slug):
    return pipeline.build_review_core(slug, read(ROOT / 'topics' / (slug + '.json')),
        read(ROOT / 'cache' / slug / 'records.json'), registration.protocol_sha(slug))


def publish(slug, review, directory):
    primary = next(o for o in review['outcomes'] if o.get('primary'))
    declared = review.get('method_declared', pipeline.METHOD)
    scale = primary.get('result', {}).get('scale')
    meta = dict(slug=slug, declared_method=declared,
                served_method=method_text(scale) if scale else declared,
                generator='harness', build_utc='2026-09-11',
                comparator={k: review['comparator'][k] for k in
                    ('name', 'year', 'journal', 'pmid', 'doi', 'url', 'open_access', 'overlap')})
    return census.build_review_dir(review, meta, str(directory),
        registration.protocol_sha(slug), from_cache=True, certify=True)


def no_increase(before, after):
    """Conservative equality contract: every published structured assurance stays fixed.

    Any decrease can be supported later by an explicit partial order; these plants
    accept equality or a named refusal, never an unclassified exception.
    """
    for key in ('outcomes', 'grade', 'claimgraph'):
        assert after.get(key) == before.get(key), key
    assert after['reproduction']['claim_check'] == before['reproduction']['claim_check']
    assert after['reproduction']['proposition_check'] == before['reproduction']['proposition_check']
    assert after['reproduction']['claimgraph_check'] == before['reproduction']['claimgraph_check']


@pytest.mark.parametrize('slug', TOPICS)
@pytest.mark.parametrize('obj', OBJECTS)
def test_deletion_invariant(slug, obj, tmp_path, monkeypatch):
    if obj == 'search_candidate':
        # A real registered artefact, but NOT consumed by build_topic.py.
        reg = read(ROOT / search_completeness.REGISTRY)
        candidate = reg['candidate_file']
        assert (ROOT / candidate).is_file()
        path = tmp_path / search_completeness.REGISTRY
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(reg), encoding='utf-8')
        # Copy then delete, so this is a deletion rather than a never-created fixture.
        dest = tmp_path / candidate
        dest.parent.mkdir(parents=True)
        shutil.copy2(ROOT / candidate, dest)
        dest.unlink()
        ok, reason = search_completeness.check(tmp_path)
        assert not ok
        assert reason == 'COULD-NOT-EXECUTE: registered file missing: ' + candidate
        pytest.skip('NOT_CONSTRUCTIBLE in topic production chain; real standalone search gate HELD')

    before = core(slug)
    changed = copy.deepcopy(before)
    baseline = tmp_path / 'baseline'
    publish(slug, before, baseline)  # baseline must build; unrelated failures are errors
    expected = None
    if obj in ('definition_span', 'result_span'):
        field = 'endpoint_' + obj
        trial = next(t for o in changed['outcomes'] for t in o.get('trials', []) if t.get(field))
        trial.pop(field)
        expected = 'MISSING_ENDPOINT_SUPPORT: ' + field + ': ' + trial['id']
    elif obj == 'grade_domain':
        assert 'indirectness' in changed['grade']['domains']
        del changed['grade']['domains']['indirectness']
        expected = 'MISSING_GRADE_DOMAIN: indirectness'
    elif obj == 'trial_row':
        cache = tmp_path / 'cache' / slug
        shutil.copytree(ROOT / 'cache' / slug, cache)
        path = cache / 'verified_effects.json'
        rows = read(path)
        # Preserve held documents referenced outside the cache in this isolated copy.
        for file in cache.glob('verified_*.json'):
            for value in read(file).values():
                for entry in value if isinstance(value, list) else [value]:
                    ref = (entry.get('document_ref') or '').split('#')[0]
                    if ref and (ROOT / ref).is_file():
                        held = tmp_path / ref
                        held.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(ROOT / ref, held)
        pid = '40162642' if slug == TOPICS[0] else '25176015'
        assert pid in rows
        del rows[pid]
        path.write_text(json.dumps(rows), encoding='utf-8')
        from harness import verified_inputs
        original = verified_inputs.load
        monkeypatch.setattr(verified_inputs, 'load',
            lambda s, cache_root=None: original(s, cache_root=tmp_path / 'cache'))
        expected = 'MISSING_VERIFIED_EFFECT: ' + slug + '/' + pid
    else:
        # Source object for the emitted REPRODUCTION_RETRACTION marking.
        rows = changed['limitations']
        removed = [r for r in rows if r.get('kind') == 'REPRODUCTION_RETRACTION']
        assert len(removed) == 1
        changed['limitations'] = [r for r in rows if r not in removed]

    try:
        if obj == 'trial_row':
            changed = core(slug)
        publish(slug, changed, tmp_path / 'after')
    except ValueError as exc:
        assert expected is not None and str(exc) == expected
        return
    after = read(tmp_path / 'after' / 'review.json')
    old = read(baseline / 'review.json')
    if obj == 'trial_row':
        old_k = next(o for o in old['outcomes'] if o.get('primary'))['result']['k']
        new_k = next(o for o in after['outcomes'] if o.get('primary'))['result']['k']
        assert new_k < old_k, 'FIRED: deleted verified trial but pooled k did not fall'
    elif obj in ('definition_span', 'result_span'):
        assert all(t.get('endpoint_' + obj) for o in after['outcomes']
                   for t in o.get('trials', []) if t.get('target_endpoint_class') == 'EXACT_TARGET'), \
            'FIRED: EXACT_TARGET survives deleted binding support'
    elif obj == 'grade_domain':
        assert 'indirectness' in after['grade']['domains'], 'FIRED: published GRADE silently lacks a domain'
    old_html = text((baseline / 'index.html').read_text(encoding='utf-8'))
    new_html = text((tmp_path / 'after' / 'index.html').read_text(encoding='utf-8'))
    for mark in MARKS:
        assert new_html.count(mark) >= old_html.count(mark), mark
    no_increase(old, after)
