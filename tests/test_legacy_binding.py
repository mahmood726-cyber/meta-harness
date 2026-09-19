import hashlib
import json
import os
from pathlib import Path

import pytest
from harness import legacy_binding as lb, pipeline
from harness import target_endpoint as te
from harness.page import _trial_inputs

SPEC = {'name': '3-point major adverse cardiovascular events', 'keywords': ['major adverse cardiovascular', 'primary outcome']}
DEFINITION = 'The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke.'
RESULT = 'The primary outcome occurred less frequently (hazard ratio, 0.86; 95% CI, 0.77 to 0.96).'
COMPONENT = 'Death from cardiovascular causes occurred less frequently (hazard ratio, 0.50; 95% CI, 0.30 to 0.80).'


def held(tmp_path, text):
    path = tmp_path / 'held.txt'
    path.write_text(text, encoding='utf8', newline='')
    return {'document_ref': 'held.txt', 'document_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def row():
    return {'id': 'PMID fixture', 'label': 'fixture', 'effect': .86, 'ci_low': .77, 'ci_high': .96, 'scale': 'HR', 'provenance': 'fulltext_verified'}


def test_component_refused_with_number_and_spans(tmp_path):
    entry = dict(held(tmp_path, DEFINITION + ' ' + COMPONENT), source='Quote: "' + COMPONENT + '"', outcome=SPEC['name'])
    r = dict(row(), source=entry['source'], effect=.5)
    kept, refused = lb.admit_legacy_rows(SPEC, [r], {}, {'fixture':entry}, {}, {}, tmp_path)
    assert not kept
    assert refused[0]['reason_code'] == 'RESULT_INCOMPATIBLE'
    assert refused[0]['refused_effect']['effect'] == .5
    assert refused[0]['endpoint_result_span'] == COMPONENT
    assert refused[0]['endpoint_definition_span'] == COMPONENT
    assert refused[0]['binding_document_sha256'] == entry['document_sha256']


@pytest.mark.parametrize('digest_key', ['document_sha256', 'extracted_text_sha256'])
def test_digest_mismatch_never_falls_back_or_refuses(tmp_path, digest_key):
    entry = dict(held(tmp_path, DEFINITION + ' ' + RESULT), source_span=RESULT, outcome=SPEC['name'], source='quote')
    entry[digest_key] = '0' * 64
    kept, refused = lb.admit_legacy_rows(SPEC, [dict(row(), source='quote')], {}, {'fixture':entry}, {}, {}, tmp_path)
    assert not refused
    assert kept[0]['endpoint_binding'] == 'unbound_legacy_unlocated'
    assert kept[0]['endpoint_binding_reason'] == 'DIGEST_MISMATCH'
    assert kept[0]['binding_offsets'] is None


@pytest.mark.parametrize('quote', ['"{}"', '“{}”', '‘{}’', "'{}'"])
def test_quotes_exact_and_offsets(tmp_path, quote):
    text = DEFINITION + '\n\n' + RESULT.replace('occurred ', 'occurred\n  ')
    entry = dict(held(tmp_path, text), source=quote.format(RESULT))
    r = lb.bind_entry(SPEC, row(), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'EXACT_TARGET'
    start, end = r['binding_offsets']
    assert text[start:end] == r['endpoint_result_span']
    assert r['endpoint_definition_span'] == DEFINITION


@pytest.mark.parametrize('span,reason', [(None, 'NO_VERBATIM_SPAN'), (RESULT.lower(), 'SPAN_NOT_FOUND'), ('Invented source sentence.', 'SPAN_NOT_FOUND')])
def test_no_paraphrase_or_case_folding(tmp_path, span, reason):
    entry = dict(held(tmp_path, DEFINITION + ' ' + RESULT), source='A hand-written description')
    if span:
        entry['source_span'] = span
    r = lb.bind_entry(SPEC, row(), entry, tmp_path)
    assert r['endpoint_binding'] == 'unbound_legacy_unlocated'
    assert r['endpoint_binding_reason'] == reason


def test_path_escape_and_identifier_mismatch(tmp_path):
    for ref, expected in [('../outside.txt', 'DOCUMENT_OUTSIDE_REPOSITORY'), ('records.json#PMID-other', 'DOCUMENT_IDENTIFIER_MISMATCH')]:
        r = lb.bind_entry(SPEC, row(), {'document_ref':ref, 'source_span':RESULT}, tmp_path)
        assert r['endpoint_binding_reason'] == expected


def test_explicit_missing_document_does_not_fallback(tmp_path):
    r = lb.bind_entry(SPEC, row(), {'document_ref':'missing.txt', 'source_span':RESULT}, tmp_path)
    assert r['endpoint_binding'] == 'unbound_legacy_unlocated'
    assert r['binding_searched'] == ['missing.txt']


def test_near_requires_declaration(tmp_path):
    sentence = 'Death from cardiovascular causes, myocardial infarction, stroke, or unstable angina occurred in 12 patients.'
    entry = dict(held(tmp_path, sentence), verbatim_span=sentence)
    assert lb.bind_entry(SPEC, row(), entry, tmp_path)['endpoint_admissibility'] == 'RESULT_INCOMPATIBLE'
    assert lb.bind_entry(dict(SPEC, allow_near_match=True), row(), entry, tmp_path)['endpoint_admissibility'] == 'NEAR_MATCH_DECLARED'


def test_soul_quoted_pipeline_plant():
    root = Path(pipeline.ROOT)
    topic = json.loads((root / 'topics/glp1-ra-mace-t2d.json').read_text(encoding='utf8'))
    records = json.loads((root / 'cache/glp1-ra-mace-t2d/records.json').read_text(encoding='utf8'))
    rec = next(r for r in records['records'] if r['id'] == '40162642')
    from harness import extract
    sentence = next(s.strip() for s in extract._sentences(rec['abstract']) if 'a primary-outcome event occurred' in s)
    entry = dict(outcome=topic['primary_outcome']['name'], effect=.86, ci_low=.77, ci_high=.96, scale='HR', override=True, source='SOUL: "' + sentence + '"')
    out = pipeline._build_outcome(topic['primary_outcome'], 'primary', [{'id':'40162642','id_type':'pmid'}], {'40162642':rec}, topic['intervention_terms'], topic['comparator_terms'], verified_effects={'40162642':entry})
    assert len(out['trials']) == 1
    r = out['trials'][0]
    assert r['endpoint_binding'] == 'located_in_held_bytes'
    assert r['endpoint_admissibility'] == 'EXACT_TARGET'
    assert r['endpoint_result_span'] == sentence


def test_repeat_is_ambiguous():
    assert lb.locate('abc abc', 'abc') is None


def test_binding_details_render_escaped():
    r = dict(row(), endpoint_binding='unbound_legacy_unlocated', endpoint_admissibility='UNBOUND_LEGACY',
             binding_document='<held>', binding_document_sha256='abc', binding_offsets=[0, 8],
             endpoint_binding_reason='DIGEST_MISMATCH', binding_searched=['<held>'])
    html = _trial_inputs({'trials':[r]})
    assert '&lt;held&gt;' in html and '<held>' not in html
    assert 'DIGEST_MISMATCH' in html and 'binding_offsets' in html


def test_whole_abstract_cannot_pollute_component_classification(tmp_path):
    text = DEFINITION + ' ' + COMPONENT
    entry = dict(held(tmp_path, text), source_span=text)
    r = lb.bind_entry(SPEC, dict(row(), effect=.5, ci_low=.3, ci_high=.8), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'RESULT_INCOMPATIBLE'
    assert r['endpoint_result_span'] == COMPONENT
    assert r['endpoint_definition_span'] == COMPONENT
    assert text[slice(*r['binding_offsets'])] == COMPONENT


def test_non_composite_uses_only_result_sentence(tmp_path):
    text = 'Stroke was the primary outcome. Diarrhea occurred in 4 patients and 8 controls.'
    entry = dict(held(tmp_path, text), source_span=text)
    r = lb.bind_entry({'name':'Diarrhea', 'keywords':['diarrhea']}, dict(row(), effect=None, ai=4, ci=8), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'EXACT_TARGET'
    assert r['endpoint_definition_span'] == 'Diarrhea occurred in 4 patients and 8 controls.'


def test_abstract_then_fulltext_fallback(tmp_path):
    directory = tmp_path / 'cache/topic'
    directory.mkdir(parents=True)
    (directory / 'records.json').write_text(json.dumps({'records':[{'id':'fixture', 'abstract':'No result.'}]}),encoding='utf8')
    (directory / 'ft_fixture.txt').write_text(DEFINITION + ' ' + RESULT,encoding='utf8')
    r = lb.bind_entry(SPEC, row(), {'source_span':RESULT}, tmp_path, {'abstract':'No result.'})
    assert r['endpoint_admissibility'] == 'EXACT_TARGET'
    assert r['binding_document'] == 'cache/topic/ft_fixture.txt'
    assert len(r['binding_searched']) == 2


def test_fragment_binds_containing_result_sentence(tmp_path):
    entry = dict(held(tmp_path, DEFINITION + ' ' + COMPONENT), source='Quote: "hazard ratio, 0.50"')
    r = lb.bind_entry(SPEC, dict(row(), effect=.5, ci_low=.3, ci_high=.8), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'RESULT_INCOMPATIBLE'
    assert r['endpoint_result_span'] == COMPONENT


def test_decimal_tail_is_not_an_integer_arm_count(tmp_path):
    wrong = 'Pericarditis occurred in 26 patients versus 51 controls (p=0' + chr(0xb7) + '0009).'
    text = wrong + ' Diarrhea occurred in nine patients in each group.'
    entry = dict(held(tmp_path, text), source_span=text)
    r = lb.bind_entry({'name':'Diarrhea','keywords':['diarrhea']}, dict(row(), effect=None, ai=9, ci=9), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'UNBOUND_LEGACY'
    assert r['endpoint_binding'] == 'located_unbindable'


def test_multi_outcome_xml_table_is_not_a_sentence(tmp_path):
    text = '<table><tr><td>Stroke</td><td>9</td></tr><tr><td>Diarrhea</td><td>9</td></tr></table>'
    entry = dict(held(tmp_path, text), source_span=text)
    r = lb.bind_entry(SPEC, row(), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'UNBOUND_LEGACY'
    assert r['endpoint_binding'] == 'located_unbindable'


def test_named_endpoint_without_definition_is_admitted_labelled(tmp_path):
    sentence = 'Major vascular events occurred less often (hazard ratio, 1.01; 95% CI, 0.90 to 1.14).'
    text = 'The primary outcome was death from cardiovascular causes. ' + sentence
    entry = dict(held(tmp_path, text), source_span=sentence, source='quote', outcome=SPEC['name'])
    kept, refused = lb.admit_legacy_rows(SPEC, [dict(row(), source='quote', effect=1.01, ci_low=.90, ci_high=1.14)],
                                        {}, {'fixture':entry}, {}, {}, tmp_path)
    assert not refused and len(kept) == 1
    r = kept[0]
    assert r['endpoint_binding'] == 'located_unbindable'
    assert r['endpoint_admissibility'] == 'UNBOUND_LEGACY'
    assert r['binding_reason'] == 'named endpoint has no definition span in the held text'
    assert r['endpoint_definition_span'] is None
    assert 'located_unbindable' in _trial_inputs({'trials':kept})


def test_rewind_binds_gi_sentence_from_held_record():
    root = Path(pipeline.ROOT)
    topic = json.loads((root / 'topics/glp1-ra-mace-t2d.json').read_text(encoding='utf8'))
    records = json.loads((root / 'cache/glp1-ra-mace-t2d/records.json').read_text(encoding='utf8'))
    rec = next(r for r in records['records'] if r['id'] == '31189511')
    spec = next(s for s in topic['harm_outcomes'] if s['name'] == 'Gastrointestinal adverse events')
    quote = rec['abstract'][rec['abstract'].index('All-cause mortality'):rec['abstract'].index(' INTERPRETATION:')]
    expected = quote[quote.index('2347'):]
    entry = dict(document_ref='cache/glp1-ra-mace-t2d/records.json#PMID-31189511', source_span=quote)
    r = lb.bind_entry(spec, dict(id='PMID 31189511', ai=2347, n1i=4949, ci=1687, n2i=4952), entry, root, rec)
    assert r['endpoint_admissibility'] == 'EXACT_TARGET'
    assert r['endpoint_result_span'] == expected
    assert r['endpoint_definition_span'] == expected
    assert rec['abstract'][slice(*r['binding_offsets'])] == expected


def test_multi_sentence_arm_selection_requires_denominators(tmp_path):
    text = 'Diarrhea occurred in 4 of 100 patients versus 8 of 100 controls. Stroke occurred in 4 of 200 patients versus 8 of 200 controls.'
    entry = dict(held(tmp_path, text), source_span=text)
    r = lb.bind_entry({'name':'Diarrhea', 'keywords':['diarrhea']},
                      dict(id='fixture', ai=4, n1i=100, ci=8, n2i=100), entry, tmp_path)
    assert r['endpoint_admissibility'] == 'EXACT_TARGET'
    assert r['endpoint_result_span'] == text.split('. ')[0] + '.'


def test_binding_evidence_browser_contract():
    playwright = pytest.importorskip('playwright.sync_api')
    r = dict(row(), endpoint_binding='unbound_legacy_unlocated', endpoint_admissibility='UNBOUND_LEGACY',
             binding_document='held.txt', binding_document_sha256='a' * 64, binding_offsets=[0, 8],
             endpoint_binding_reason='DIGEST_MISMATCH', binding_searched=['held.txt'])
    with playwright.sync_playwright() as p:
        candidates = [Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe',
                      Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe']
        exe = next((candidate for candidate in candidates if candidate.is_file()), None)
        assert exe, 'Local browser required; downloads forbidden'
        browser = p.chromium.launch(executable_path=str(exe), headless=True)
        try:
            page = browser.new_page()
            page.set_content(_trial_inputs({'trials':[r]}))
            assert page.locator('body').inner_text().count('DIGEST_MISMATCH') == 1
            assert page.get_by_text('binding_document_sha256:', exact=False).count() > 0
            assert 'unbound_legacy_unlocated' in page.locator('body').inner_text()
        finally:
            browser.close()
