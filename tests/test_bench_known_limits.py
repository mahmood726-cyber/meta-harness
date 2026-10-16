"""Open review items: executable failures, never silent skips."""
import copy
import json
from pathlib import Path
import pytest
from harness import extract, pipeline

ROOT = Path(__file__).resolve().parents[1]
REASON = 'KNOWN LIMIT (bench r3, review closed at three rounds): '

@pytest.mark.xfail(strict=True, reason=REASON + 'P2 automatic-family path bypasses _dedup without families.json')
def test_bench_automatic_family_preserves_dedup(monkeypatch):
    slug = 'daratumumab-rrmm-pfs-bench'
    cfg = json.loads((ROOT/'topics'/f'{slug}.json').read_text(encoding='utf8'))
    records = json.loads((ROOT/'cache'/slug/'records.json').read_text(encoding='utf8'))
    assert not (ROOT/'cache'/slug/'families.json').exists()
    original = pipeline._dedup
    def tagged(*args, **kwargs):
        return [dict(r, dedup_passed=True) for r in original(*args, **kwargs)]
    monkeypatch.setattr(pipeline, '_dedup', tagged)
    inp = pipeline.outcome_inputs(slug, copy.deepcopy(cfg), copy.deepcopy(records))
    assert inp['merged']
    assert all(r.get('dedup_passed') for r in inp['merged'])

@pytest.mark.xfail(strict=True, reason=REASON + 'PFS2 before OS contaminates a non-PFS target')
def test_bench_pfs2_not_os():
    text = 'PFS2 HR 0.70 (95% CI 0.60-0.82); overall survival HR 0.80 (95% CI 0.70-0.91).'
    matches = list(extract._EFFECT.finditer(text))
    expected = extract._effect_from_match(matches[-1], text)[1]
    assert extract.extract_trial(text, ['overall survival'], ['drug'], [], estimand='HR')['effect'] == expected
