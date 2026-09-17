"""Renderer and refusal contracts; all clinical inputs come from held records."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from harness import claimgraph as cg, remainder_prose as prose


@pytest.fixture(scope='module')
def review():
    root = Path(__file__).resolve().parents[1]
    return json.loads((root / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def registry(review):
    graph = cg.ClaimGraph()
    prose.register(review, graph)
    return graph


def test_migrated_surfaces_are_registered(review, registry):
    parts = [prose.header(review), prose.protocol_metadata(review), prose.strand_rows(review),
             prose.reason_audit(review), prose.reporting(review), prose.reproduction_metadata(review),
             prose.comparator_metadata(review), prose.comparator_assessments(review)]
    parts.extend([
        prose.receipt('snapshot', review['search']['retrieval']['snapshot']),
        prose.receipt('source_status', review['search']['source_status']),
        prose.receipt('retrieval_class', review['search']['retrieval_class']),
        prose.receipt('identifier_scope', review['identifier_scope']),
        prose.replay_boundary(),
    ])
    for outcome in review['outcomes']:
        parts.append(prose.typed_effects(outcome))
        parts.extend(prose.absent_trial(row) for row in outcome.get('declared_absent_trials') or [])
    assert not registry.check()
    for part in parts:
        scan = cg.scan_rendered(part, registry)
        assert not scan['violations'], scan['violations']


def test_numeric_plant_and_forged_markers_are_refused(review, registry):
    document = prose.typed_effects(review['outcomes'][0])
    plant = '<p>The pooled hazard ratio was 7.77.</p>'
    assert cg.scan_rendered(document + plant, registry)['violations'][0]['code'] == 'SENTENCE_WITHOUT_OBJECT'
    cid = next(cid for cid, obj in registry.objects.items() if obj['class'] == 'JUDGEMENT')
    forged = '<span data-claim-id="' + cid + '" data-claim-class="JUDGEMENT">7.77</span>'
    assert cg.scan_rendered(forged, registry)['violations'][0]['code'] == 'RENDERING_MISMATCH'
    # A numerical assertion in a header remains debt under the existing rule.
    assert cg.scan_rendered('<table><tr><th>The pooled HR was 7.77.</th></tr></table>', registry)['violations']


def test_changed_decision_does_not_match_old_registry(review, registry):
    changed = deepcopy(review['outcomes'][0])
    axis = next(iter(changed['effect_types'][0]['axes']))
    changed['effect_types'][0]['axes'][axis]['value'] = 'TEST_ONLY_CHANGED_DECISION'
    scan = cg.scan_rendered(prose.typed_effects(changed), registry)
    assert any(v['code'] == 'SENTENCE_WITHOUT_OBJECT' for v in scan['violations'])


def test_field_presence_recomputes_and_is_not_compliance(review, registry):
    graph = deepcopy(registry)
    obj = next(o for o in graph.objects.values() if o.get('operation') == 'reporting_presence')
    obj['inputs']['record'] = {}
    assert any(v['code'] == 'TRANSFORMATION_MISMATCH' for v in graph.check())
    assert 'does not certify PRISMA compliance' in prose.reporting(review)


def test_metadata_receipt_recomputes_recorded_states(registry):
    graph = deepcopy(registry)
    obj = next(o for o in graph.objects.values()
               if o.get('operation') == 'renderer_receipt' and o['inputs']['unit'] == 'source_status')
    obj['inputs']['record']['TEST_ONLY_ADAPTER'] = 'RAN_ERROR'
    assert any(v['code'] == 'TRANSFORMATION_MISMATCH' and v['claim_id'] == obj['claim_id']
               for v in graph.check())


def test_audit_counts_ignore_stale_summaries(review):
    changed = deepcopy(review)
    changed['reason_code_audit']['counts'] = {'TEST_ONLY_FAKE_SUMMARY': 987654}
    changed['reason_code_audit']['N'] = 987654
    assert prose.reason_audit(changed) == prose.reason_audit(review)
    changed['reason_code_audit']['rows'][0]['verdict'] = 'TEST_ONLY_CHANGED_STATE'
    assert prose.reason_audit(changed) != prose.reason_audit(review)


def test_sensitivity_source_refusal(review):
    changed = deepcopy(review)
    row = changed['strands']['sensitivity_values'][0]
    # The same sensitivity FACT ID is independently validated by the registry.
    evidence = cg._fact_evidence(row)
    evidence['document_sha256'] = '0' * 64
    graph = cg.ClaimGraph()
    prose.register(changed, graph)
    assert any(v['code'] == 'UNVERIFIED_FACT' for v in graph.check())
    assert 'data-claim-class="UNVERIFIED_FACT"' in prose.strand_rows(changed)


def test_json_roundtrip_and_other_topic_inheritance(review):
    canonical = json.loads(json.dumps(review, sort_keys=True))
    assert prose.typed_effects(review['outcomes'][0]) == prose.typed_effects(canonical['outcomes'][0])
    fixture = {'slug': 'test-only-topic', 'protocol': {'eligibility': 'test-only rule'}}
    graph = cg.ClaimGraph()
    prose.register(fixture, graph)
    assert not cg.scan_rendered(prose.reporting(fixture), graph)['violations']
    assert 'ABSENT' in prose.reporting(fixture)
