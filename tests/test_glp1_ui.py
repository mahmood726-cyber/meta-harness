"""GLP1 end-to-end UI contract against the locally served built page."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def test_glp1_page_strands_provenance_and_tabs():
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(('127.0.0.1', 8000), partial(QuietHandler, directory=str(ROOT)))
    worker = Thread(target=server.serve_forever, daemon=True)
    worker.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, channel='chrome')
            try:
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.route('**/*', lambda route: route.continue_()
                           if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto('http://127.0.0.1:8000/docs/reviews/glp1-ra-mace-t2d/index.html')
                assert page.get_by_role('heading', name='Declared strands: primary and any delivery').is_visible()
                assert page.locator('[data-claim-id="glp1-freedom-sensitivity"]').is_visible()
                assert page.locator('[data-claim-class="UNVERIFIED_FACT"]').count() == 0
                assert 'UNKNOWN' in page.locator('[data-claim-id="glp1-flow-caveat"]').inner_text()
                for button in page.locator('nav button').all():
                    button.click()
                    tab = button.get_attribute('data-t')
                    assert page.locator('#tab-' + tab).is_visible()
                assert not errors
                (ROOT / '.tmp').mkdir(exist_ok=True)
                page.screenshot(path=str(ROOT / '.tmp' / 'glp1-page.png'), full_page=False)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
