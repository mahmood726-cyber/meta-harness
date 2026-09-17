"""Local browser E2E contract for the additive family consumer."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright
from harness import page, trial_family

ROOT = Path(__file__).resolve().parents[1]

def test_family_table_in_live_browser():
    slug = 'glp1-ra-mace-t2d'
    def read(p):
        return json.loads(p.read_text(encoding='utf8'))
    review = read(ROOT/'docs/reviews'/slug/'review.json')
    cfg = read(ROOT/'topics'/f'{slug}.json')
    recs = read(ROOT/'cache'/slug/'records.json')
    fs = trial_family.prepare(ROOT,slug,recs['records']+recs['ctgov'],cfg)
    trial_family.attach_review(review,fs)
    body = page.render_page(review).encode('utf8')
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(body)
        def log_message(self,*args):
            pass
    server = ThreadingHTTPServer(('127.0.0.1',8000),Handler)
    thread = Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(channel='chrome',headless=True)
            try:
                tab = browser.new_page()
                tab.route('**/*', lambda route: route.continue_()
                          if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors = []
                tab.on('pageerror',lambda e:errors.append(str(e)))
                response = tab.goto('http://127.0.0.1:8000/fnc-family-contract',wait_until='load')
                assert response.status == 200 and response.body() == body, 'Port 8000 served a different local test server'
                tab.locator('button[data-t="screening"]').click()
                table = tab.locator('#trial-families')
                assert table.is_visible()
                assert table.locator('tbody tr').count()==len(fs)
                assert table.locator('th').all_text_contents()==[
                    'Family ID','Acronym','Reports by role','Arms','Contrasts','Eligibility','Lifecycle','Per-outcome status']
                assert table.locator('.family-count-chain').inner_text()==trial_family.count_sentence(review['family_count_chain'])
                assert table.locator('tbody tr').filter(has_text='NCT03819153').count()==1
                assert table.locator('tbody tr').filter(has_text='NCT01455896').count()==1
                assert not errors
                out = ROOT/'.tmp/fn-family-ui.png'
                out.parent.mkdir(exist_ok=True)
                tab.screenshot(path=str(out),full_page=False)
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
