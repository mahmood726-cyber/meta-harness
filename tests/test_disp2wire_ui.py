"""Served-page E2E from held review bytes; no published files are overwritten."""
import http.server
import json
import os
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright
from harness import page

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'ticagrelor-vs-clopidogrel-acs'


def test_served_recovery_panel():
    review = json.loads((ROOT / 'docs/reviews' / SLUG / 'review.json').read_text(encoding='utf-8'))
    rendered = page.render_page(review).encode('utf-8')

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/disp2wire':
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
                assert tab.goto('http://127.0.0.1:8000/disp2wire').status == 200
                tab.locator('button[data-t="outcomes"]').click()
                panels = tab.locator('[data-disperse-table]')
                assert panels.count() == 3
                gated = tab.locator('[data-disperse-table="MODEL_TRANSCRIBED_CHECKED"]')
                assert gated.count() == 1 and gated.is_visible()
                text = gated.inner_text()
                for expected in ('16/334', '10/329', '16/327', 'model-transcribed from the held figure; arithmetic and reading-consensus checked; not independently cell-verified',
                                 'never pooled', 'NOT_ADJUDICATED', 'overall study (not 12 months)',
                                 'post-lock MI', 'MI excludes silent MI'):
                    assert expected in text
                refused = tab.locator('[data-disperse-table="REFUSED"]')
                assert refused.count() == 2
                for panel in refused.all():
                    assert 'no DISPERSE-2 table held for this outcome' in panel.inner_text()
                    assert '16/334' not in panel.inner_text()
                assert not errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
