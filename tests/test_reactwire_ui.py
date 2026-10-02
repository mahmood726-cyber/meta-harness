"""Served-page E2E from held review bytes; no published files are overwritten."""
import http.server
import json
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from harness import recovery_map, recovery_binding, page

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'tocilizumab-covid19-mortality'


def test_served_recovery_panel():
    review = json.loads((ROOT / 'docs/reviews' / SLUG / 'review.json').read_text(encoding='utf-8'))
    recovery_map.attach(review, SLUG, root=ROOT)
    ledger = recovery_binding.attach(review, SLUG, root=ROOT)
    rendered = page.render_page(review).encode('utf-8')

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/reactwire':
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(rendered)

        def log_message(self, *args):
            pass

    candidates = [Path(os.environ.get('PROGRAMFILES(X86)', '')) / 'Microsoft/Edge/Application/msedge.exe',
                  Path(os.environ.get('PROGRAMFILES', '')) / 'Google/Chrome/Application/chrome.exe']
    exe = next((p for p in candidates if p.is_file()), None)
    assert exe, 'Installed browser required; no downloads'
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 8000), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=str(exe), headless=True)
            try:
                tab = browser.new_page()
                tab.route('**/*', lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors = []
                tab.on('pageerror', lambda error: errors.append(str(error)))
                assert tab.goto('http://127.0.0.1:8000/reactwire').status == 200
                tab.locator('button[data-t="outcomes"]').click()
                panels = tab.locator('[data-recovery-figure]')
                total = len(ledger) + sum(len(o.get('recovery_figure_unmatched', [])) for o in review['outcomes'])
                assert panels.count() == total
                assert panels.filter(has_text='REMAP-CAP').count() == 1
                for panel in panels.all():
                    assert panel.is_visible()
                    text = panel.inner_text()
                    assert 'model-transcribed from the held figure; arithmetic and reading-consensus checked; not independently cell-verified' in text
                    assert 'relayed:' in text
                    assert 'never pooled: population not adjudicated' in text
                bacc = panels.filter(has_text='BACC-Bay').inner_text()
                assert '9/161 vs 4/82' in bacc and '9/161 vs 3/81' in bacc
                assert 'One patient who died was intubated before receiving placebo' in bacc
                assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
