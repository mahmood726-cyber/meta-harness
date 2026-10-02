import builtins
from copy import deepcopy
import json
from pathlib import Path
import pytest
from harness import table_binding as tb, page
from scripts import disperse2_figure_proposal as proposal

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'ticagrelor-vs-clopidogrel-acs'


def target():
    return json.loads((ROOT / 'topics' / (SLUG + '.json')).read_text(encoding='utf-8'))['primary_outcome']


def test_replay_and_stale_plant(tmp_path, monkeypatch):
    raw = proposal.binding_bytes()
    assert raw == (ROOT / proposal.BINDING).read_bytes()
    assert raw == proposal.binding_bytes()
    (tmp_path / 'docs').mkdir()
    data = json.loads(raw)
    data['gate']['rows'][0]['n'] += 1
    (tmp_path / proposal.BINDING).write_text(json.dumps(data), encoding='utf-8')
    monkeypatch.setattr(proposal, 'binding_bytes', lambda root: raw)
    with pytest.raises(ValueError, match='STALE_DISPERSE_BINDING'):
        proposal.verify_binding(tmp_path)
    (tmp_path / proposal.BINDING).write_bytes(raw)
    assert proposal.verify_binding(tmp_path)


@pytest.mark.parametrize('defect', ['poolable', 'count', 'reader', 'population'])
def test_artifact_defects(tmp_path, defect):
    data = tb.load_disperse_binding()
    if defect == 'poolable':
        data['poolable'] = True
    elif defect == 'count':
        data['gate']['rows'][0]['n'] = True
    elif defect == 'reader':
        data['gate']['groups'][0]['record_ids'] = []
    else:
        data['gate']['rows'][0]['population']['status'] = 'ADJUDICATED'
    (tmp_path / 'docs').mkdir()
    (tmp_path / proposal.BINDING).write_text(json.dumps(data), encoding='utf-8')
    with pytest.raises(ValueError, match='DISPERSE_BINDING_REFUSED'):
        tb.load_disperse_binding(tmp_path)


def test_outcome_scope_and_pool_refusal():
    binding = tb.disperse(target())
    assert binding['state'] == 'MODEL_TRANSCRIBED_CHECKED'
    assert binding['status'] == 'REFUSED' and binding['POOLABLE'] is False
    assert len(binding['rows']) == 3
    for cfg in ({'name': 'major bleeding'}, {'name': 'dyspnea'}, {'name': 'other'}, {}):
        result = tb.disperse(cfg)
        assert not result['rows'] and result['state'] == 'REFUSED'
        assert result['reason'] == 'no DISPERSE-2 table held for this outcome; recovery active'
    for forged in (binding, dict(binding, state='ANALYSIS_READY', poolable=True)):
        with pytest.raises(ValueError, match='POOL_REFUSED: DISPERSE-2'):
            tb.require_pool([forged])


def test_render_import_and_read_barrier(monkeypatch):
    review = json.loads((ROOT / 'docs/reviews' / SLUG / 'review.json').read_text(encoding='utf-8'))
    before = deepcopy(review)
    original_import = builtins.__import__
    original_open = Path.open
    def guarded_import(name, *args, **kwargs):
        if name.startswith('reproducible_ai'):
            raise AssertionError('MODEL_IMPORT_REFUSED')
        return original_import(name, *args, **kwargs)
    def guarded_open(path, *args, **kwargs):
        value = path.as_posix()
        if 'evidence/model_calls' in value or 'disperse2_images' in value or 'acquisition_cascade/held' in value:
            raise AssertionError('MODEL_EVIDENCE_READ_REFUSED')
        return original_open(path, *args, **kwargs)
    monkeypatch.setattr(builtins, '__import__', guarded_import)
    monkeypatch.setattr(Path, 'open', guarded_open)
    with pytest.raises(AssertionError, match='MODEL_IMPORT_REFUSED'):
        __import__('reproducible_ai')
    rendered = page.render_page(review)
    assert 'model-transcribed from the held figure; arithmetic and reading-consensus checked; not independently cell-verified' in rendered
    assert 'never pooled' in rendered and 'randomised 990 vs treated 984' in rendered
    assert 'post-lock MI events excluded' in rendered
    assert review == before
    assert rendered == page.render_page(review)
