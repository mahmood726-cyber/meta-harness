"""Served DOM count contract, plus a visible injected failure in the same page."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading
from unittest.mock import patch

from playwright.sync_api import sync_playwright
from harness import census, page as renderer

ROOT = Path(__file__).resolve().parents[1]


def test_served_counts_and_failure():
    candidates = [Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe',
                  Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe']
    exe = next(p for p in candidates if p.is_file())
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8000), functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(exe), headless=True)
            try:
                page = browser.new_page()
                page.route('**/*', lambda r: r.continue_() if r.request.url.startswith('http://127.0.0.1:8000/') else r.abort())
                for directory in sorted((ROOT / 'docs/reviews').iterdir()):
                    core = json.loads((directory / 'review.json').read_text(encoding='utf-8'))
                    cc = core['reproduction']['claim_check']
                    n = sum(r['state'] == 'COMPLETED' for r in cc['receipts'])
                    assert page.goto(f'http://127.0.0.1:8000/docs/reviews/{directory.name}/index.html').status == 200
                    page.get_by_role('button', name='Reproducibility', exact=True).click()
                    block = page.locator('strong').filter(has_text=f'Claims checked: {n};')
                    assert block.count() == 1
                    assert block.is_visible()
                core = json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
                with patch.object(renderer, 'render_overview', side_effect=RuntimeError('CHK DOM failure')):
                    core['reproduction']['claim_check'] = census._claim_check(core)
                page.set_content(renderer.render_page(core))
                page.get_by_role('button', name='Reproducibility', exact=True).click()
                assert page.get_by_text('failed: 1, not attempted: 0', exact=False).is_visible()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
