"""CGX3A integration: source objects -> renderer -> independent registry scan."""
import copy
import html
import json
import re

import pytest

from harness import claimgraph, page, page_claims, section_claims
from scripts.cgx3a_scope import census


@pytest.fixture(scope='module')
def review():
    return json.loads((claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))


def test_owned_sections_have_no_unregistered_or_mismatched_units(review):
    for name, scan in census(review).items():
        assert not scan['violations'], (name, scan['violations'])
        assert scan['with_object'] == scan['rendered_units']


def test_canonical_json_key_order_does_not_change_html(review):
    canonical = json.loads(json.dumps(review, sort_keys=True))
    assert page.render_page(review) == page.render_page(canonical)


def test_numeric_plant_and_laundered_number_are_rejected(review):
    graph = claimgraph.review_graph(review)
    body = page_claims.overview(review)
    planted = body + '<p>The pooled hazard ratio is 0.123456.</p>'
    assert any(v['code'] == 'SENTENCE_WITHOUT_OBJECT' for v in claimgraph.scan_rendered(planted, graph)['violations'])
    changed = body.replace('0.8884', '0.123456')
    assert changed != body
    assert any(v['code'] == 'RENDERING_MISMATCH' for v in claimgraph.scan_rendered(changed, graph)['violations'])


def test_pool_claim_recomputes_and_refuses_stored_estimate_change(review):
    outcome = copy.deepcopy(review['outcomes'][0])
    outcome['result']['estimate'] = 9.8765
    rendered = page_claims.outcome_summary(outcome)
    assert 'TRANSFORMATION_MISMATCH' in rendered
    assert '9.8765' not in rendered


def test_missing_aggregate_reads_rows_not_stored_headline(review):
    outcome = copy.deepcopy(review['outcomes'][0])
    panel = outcome['known_missing_sensitivity']
    panel['headline_conclusion_effect'] = 'PLANTED_AGGREGATE'
    panel['rows'] = [{'trial_key': 'test-only', 'missing_class': 'EXTRACTION_DEBT', 'value_status': 'UNRESOLVED'}]
    rendered = page_claims.known_missing(outcome)
    assert 'PLANTED_AGGREGATE' not in rendered
    assert "'EXTRACTION_DEBT': 1" in html.unescape(rendered)
    assert 'Alternative:' in rendered


def test_provenance_tamper_is_not_verified(review):
    outcome = review['outcomes'][0]
    trial = copy.deepcopy(outcome['trials'][0])
    trial['document_sha256'] = '0' * 64
    rendered = page_claims.provenance_trial(trial, outcome)
    assert '[UNVERIFIED_FACT]' in rendered


def test_all_interpretations_have_a_rendered_alternative(review):
    graph = claimgraph.review_graph(review)
    for cid, obj in graph.objects.items():
        if obj['class'] == 'INTERPRETATION':
            assert obj['alternatives']
            assert 'Alternative:' in graph.render(cid)


def test_served_owned_fragments_match_fresh_renderer(review):
    served = (claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/index.html').read_text(encoding='utf-8')
    assert page.render_overview(review) in served
    for outcome in review['outcomes']:
        if outcome.get('kind') == 'harm' and not outcome.get('trials') and outcome.get('declared_absent_trials'):
            # C owns the complete unpooled-harms renderer in the merged page.
            summary = section_claims.harms_unpooled(outcome)
        else:
            summary = page_claims.outcome_summary(outcome) or page_claims.harm_summary(outcome)
        if summary:
            assert summary in served
        for trial in outcome.get('trials') or []:
            provenance = page_claims.provenance_trial(trial, outcome)
            if provenance:
                # The page's existing HTML normalisation preserves the evidence
                # object but normalises FDA extraction CRLF and trailing spaces.
                canonical = re.sub(r'[ \t]+\n', '\n', provenance.replace('\r\n', '\n'))
                assert canonical in served
