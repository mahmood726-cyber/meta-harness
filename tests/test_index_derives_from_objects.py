import json
from pathlib import Path

from harness import index as idx

DOCS = Path(__file__).resolve().parents[1] / 'docs'


def put(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf8')


def test_method_gate_state():
    page = idx.build_index(str(DOCS))
    assert 'every rendered interval is gate-checked' not in page
    assert 'Interval provenance gate: UNVALIDATED' in page


def test_recovery_topic_mismatch_is_refused(tmp_path):
    put(tmp_path, 'recovery_log.json', {'attempts': [
        {'trial': 'Sarzaeem', 'topic': 'wrong', 'status': 'UNVERIFIED'}]})
    put(tmp_path, 'parity.json', [{'slug': 'right', 'reason': 'Sarzaeem 2014 reach limit'}])
    page = idx._recovery_section(str(tmp_path))
    assert 'TOPIC_MISMATCH' in page
    assert '&rarr; wrong' not in page


def test_recovery_uses_current_review(tmp_path):
    put(tmp_path, 'recovery_log.json', {'attempts': [
        {'trial': 'COCS', 'pmid': '36286314', 'topic': 'topic', 'status': 'BLOCKED_BY_MATCHER'}]})
    put(tmp_path, 'reviews/topic/review.json', {
        'screening': {'records': [{'id': '36286314', 'decision': 'include'}]},
        'outcomes': [{'primary': True, 'declared_absent_trials': [
            {'id': 'PMID 36286314', 'state': 'COUNTS_PRESENT_NOT_CORROBORATED'}]}]})
    page = idx._recovery_section(str(tmp_path))
    assert 'DECLARED_ABSENT' in page and 'COUNTS_PRESENT_NOT_CORROBORATED' in page
    assert '<code>BLOCKED_BY_MATCHER</code>' not in page


def test_recall_identifiers_are_not_scope_exclusions():
    row = next(r for r in json.loads((DOCS / 'search_recall_regression_corpus.json').read_text())['per_topic']
               if r['slug'] == 'tranexamic-acid-pph')
    assert set(row['missed_pmids']) == {'28456509', '36243576'}
    assert set(row['missed_pmids']).isdisjoint({'39461792', '30134136', '33913639'})


def test_semaglutide_refusal_and_missing_claim(tmp_path):
    result = {'k': 2, 'estimate': -1, 'ci_low': -2, 'ci_high': 1,
              'claim': {'present': False}, 'ci_provenance': 'untrusted'}
    put(tmp_path, 'reviews/semaglutide-obesity-weight/review.json',
        {'outcomes': [{'primary': True, 'result': result}]})
    page = idx._continuous_section(str(tmp_path))
    assert 'no pooled significance or null-crossing claim' in page
    assert 'interval that now crosses zero' not in page
    result['estimate'] = 1.25
    put(tmp_path, 'reviews/semaglutide-obesity-weight/review.json',
        {'outcomes': [{'primary': True, 'result': result}]})
    assert 'MD 1.25%' in idx._continuous_section(str(tmp_path))


def test_fix_ledger_counts_are_recounted(tmp_path):
    put(tmp_path, 'fix_ledger.json', {'fixes': [{'verification': 'NONE'}, {'verification': 'INTERNAL'}],
                                    'summary': {'by_verification': {'NONE': 900}}})
    page = idx._error_coverage_section(str(tmp_path))
    assert '2 ledger entries' in page
    assert 'NONE: 1' in page and '900' not in page


def test_comparator_k_uses_parity(tmp_path):
    put(tmp_path, 'reviews/topic/manifest.json', {'slug': 'topic', 'comparator': {
        'overlap': {'theirs_k': 'not stated in the comparator abstract/full text'}}})
    put(tmp_path, 'parity.json', [{'slug': 'topic', 'comparable_comparator_k': 7, 'status': 'SUBSET'}])
    page = idx.build_index(str(tmp_path))
    assert 'not stated in the comparator abstract/full text' not in page
    assert '7 (comparable; parity status SUBSET)' in page


def test_index_browser_contract(tmp_path):
    import functools
    import http.server
    import os
    import threading
    import pytest
    playwright = pytest.importorskip('playwright.sync_api')
    candidates = [Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe',
                  Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe']
    executable = next((p for p in candidates if p.is_file()), None)
    assert executable, 'Installed browser required; no download'
    (tmp_path / 'index.html').write_text(idx.build_index(str(DOCS)), encoding='utf8')
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8000),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(tmp_path)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with playwright.sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(executable), headless=True,
                                         args=['--disable-background-networking'])
            try:
                page = browser.new_page()
                page.route('**/*', lambda route: route.continue_()
                           if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                assert page.goto('http://127.0.0.1:8000/index.html').status == 200
                text = page.locator('main').inner_text()
                assert 'Interval provenance gate: UNVALIDATED' in text
                assert 'COCS → colchicine-postop-af: DECLARED_ABSENT' in text
                assert 'Sarzaeem → colchicine-postop-af' in text
                assert 'every rendered interval is gate-checked' not in text
                assert '{{' not in text
                assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
