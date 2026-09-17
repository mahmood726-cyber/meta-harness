"""TY2 plants; numeric fixtures are synthetic and never research output."""
import json
import pytest
from pathlib import Path

from harness import effect_type as ty, page, pipeline

ROOT = Path(__file__).resolve().parents[1]


def test_no_declaration_pools_unknown_axes():
    target = ty.protocol_target({'estimand': 'HR', 'population': 'intention-to-treat'})
    kept, refused, effects = ty.type_rows([{'id': 'synthetic-A'}, {'id': 'synthetic-B'}], target)
    assert len(kept) == 2, f'accepted={len(kept)} refused={len(refused)} target={target}'
    html = page.typed_effects_html({'effect_types': effects, 'effect_type_target': target})
    assert 'UNKNOWN' in html and 'NO_ROW_EVIDENCE' in html
    assert 'all axes are non-binding' in html


def test_glp1_rebuild_membership():
    from scripts.reproduce_review import replay_core
    review = replay_core('glp1-ra-mace-t2d')
    pools = {s['strand']: s['k'] for s in review['strands']['strands']}
    assert pools == {'CONVENTIONAL_GLP1RA': 10, 'GLP1RA_ANY_DELIVERY': 11}, pools


def test_synthetic_second_topic_two_strands(tmp_path, monkeypatch):
    doc = {'slug': 'synthetic-second-topic', 'primary_strand': 'STANDARD', 'strands': [
        {'strand': 'STANDARD', 'members': [{'id': 'synthetic-A'}, {'id': 'synthetic-B'}]},
        {'strand': 'ALL', 'members': [{'id': 'synthetic-A'}, {'id': 'synthetic-B'}, {'id': 'synthetic-C'}]},
    ]}
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'docs/fixture_strands.json').write_text(json.dumps(doc), encoding='utf-8')
    monkeypatch.setattr(pipeline, 'ROOT', str(tmp_path))
    loaded = pipeline.primary_strand_declaration('synthetic-second-topic')
    assert loaded == doc
    rows = [{'id': x, 'label': x, 'effect': e, 'ci_low': e / 1.2, 'ci_high': e * 1.2}
            for x, e in [('synthetic-A', .8), ('synthetic-B', .9), ('synthetic-C', 1.1)]]
    from harness.synth import Study, pool
    for strand, k in [('STANDARD', 2), ('ALL', 3)]:
        selected = pipeline.strand_members(rows, loaded, strand)
        result = pool([Study(label=r['id'], effect=r['effect'], ci_low=r['ci_low'],
                             ci_high=r['ci_high'], measure='HR') for r in selected], scale='HR')
        assert result.k == k


def declaration(values):
    return '```effect-type-binding\n' + json.dumps(
        {'schema_version': 1, 'outcomes': {'fixture': values}}) + '\n```'


def test_protocol_declaration_overrides_config_and_preserves_unknown():
    spec = {'name': 'fixture', 'effect_type_target': {'binding_axes': []}}
    target = ty.protocol_target(spec, declaration({'censoring': 'end-of-study'}))
    assert target['binding_axes'] == ['censoring']
    effect = ty.build_effect({'id': 'synthetic'})
    assert ty.unify(target, effect)['status'] == 'UNKNOWN_FAILS_CLOSED'
    assert effect['axes']['censoring']['value'] == 'UNKNOWN'
    assert ty.protocol_target({'name': 'other'}, declaration({'censoring': 'end-of-study'}))['binding_axes'] == []


@pytest.mark.parametrize('text', [
    '```effect-type-binding\n{bad}\n```',
    declaration({'made_up': 'x'}),
    declaration({'censoring': 'made-up'}),
    declaration({'endpoint_components': '3-point MACE'}),
    declaration({'censoring': 'end-of-study'}) * 2,
    '```effect-type-binding\n{"schema_version":1,"outcomes":{},"outcomes":{}}\n```',
])
def test_invalid_declaration_refused(text):
    with pytest.raises(ValueError):
        ty.protocol_target({'name': 'fixture'}, text)


def test_binding_known_mismatch_refused_and_unbound_mismatch_disclosed():
    effect = ty.build_effect({'source': 'end-of-treatment'})
    target = ty.protocol_target({'name': 'fixture'}, declaration({'censoring': 'end-of-study'}))
    assert ty.unify(target, effect)['status'] == 'REFUSE'
    assert ty.unify(ty.protocol_target({'name': 'fixture'}), effect)['status'] == 'MATCH'


def test_strand_membership_invalid_declaration_refused():
    with pytest.raises(ValueError):
        pipeline.strand_members([], {'primary_strand': 'missing', 'strands': []})
