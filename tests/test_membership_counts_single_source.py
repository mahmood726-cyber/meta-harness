import copy
import json
import os
from pathlib import Path

import pytest

from harness import consumer_consistency as cc
from harness import membership
from harness.page import render_page

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'glp1-ra-mace-t2d'


def artifact_root():
    return ROOT / os.environ.get('CNT_DOCS', '.tmp/cnt/docs') / 'reviews'


def glp1_artifact():
    folder = artifact_root() / SLUG
    if folder.exists() or 'CNT_DOCS' in os.environ:
        return (json.loads((folder / 'review.json').read_text(encoding='utf-8')),
                (folder / 'index.html').read_text(encoding='utf-8'))
    from scripts.reproduce_review import replay_core
    review = replay_core(SLUG)
    return review, render_page(review)


def test_rendered_glp1_counts_resolve_to_one_object():
    review, page = glp1_artifact()
    cc.check_membership_counts(review, page)
    assert membership.membership_sentence(review['outcomes'][0]) in page


def test_mutated_membership_refuses():
    review, _ = glp1_artifact()
    outcome = review['outcomes'][0]
    membership.outcome_membership(outcome, review)
    bad = copy.deepcopy(review)
    bad['outcomes'][0]['membership']['sets']['eligible_not_in_pool'].append('PLANTED_DRIFT')
    with pytest.raises(ValueError, match='MEMBERSHIP_COUNT_MISMATCH'):
        render_page(bad)


def test_rendered_sentence_drift_refuses():
    outcome = {'primary': True, 'trials': [], 'declared_absent_trials': [{'id': 'PMID 12345678'}]}
    review = {'outcomes': [outcome]}
    text = membership.membership_sentence(outcome)
    with pytest.raises(ValueError, match='MEMBERSHIP_RENDER_MISMATCH'):
        cc.check_membership_counts(review, text + ' 2 eligible families not in the pool')


def test_aliases_and_family_deduplication():
    outcome = {'trials': [{'id': 'PMID 12345678', 'trial_family_id': 'NCT12345678'},
                          {'id': 'PMID 12345679', 'trial_family_id': 'NCT12345678'}],
               'declared_absent_trials': [{'id': 'PMID 22345678', 'trial_family_id': 'NCT22345678'}],
               'known_missing_sensitivity': {'rows': [{'trial_key': '22345678'}, {'trial_key': 'FLOW'}]}}
    counts = membership.build_outcome_membership(outcome)['counts']
    assert counts == {'pooled': 1, 'screened_in_not_poolable': 1,
                      'eligible_not_retrieved': 1, 'eligible_not_in_pool': 2}


def test_all_rebuilt_pages_browser_contract():
    import functools
    import http.server
    import socket
    import threading
    pytest.importorskip('playwright')
    from playwright.sync_api import sync_playwright
    candidates = [Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe',
                  Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe']
    executable = next((p for p in candidates if p.is_file()), None)
    if executable is None:
        pytest.skip('No installed browser; downloads prohibited')
    paths = sorted(artifact_root().glob('*/review.json'))
    if not paths:
        pytest.skip('Run offline CNT rebuild before corpus browser check')
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8000),
        functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(artifact_root().parent)),
        bind_and_activate=False)
    server.allow_reuse_address = False
    if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
        server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    server.server_bind()
    server.server_activate()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(executable), headless=True)
            try:
                page = browser.new_page()
                page.route('**/*', lambda route: route.continue_()
                           if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                for path in paths:
                    assert page.goto(f'http://127.0.0.1:8000/reviews/{path.parent.name}/index.html').status == 200
                    review = json.loads(path.read_text(encoding='utf-8'))
                    check = page.content()
                    cc.check_membership_counts(review, check)
                    assert page.locator('nav button').count() > 0
                assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join()
