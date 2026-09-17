"""Local browser contract for every IN3 refusal-repair page, without network."""
import functools
import http.server
import json
import os
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
SLUGS=['dapagliflozin-hfpef-hosp','doac-vte-recurrence','dpp4-mace-t2d',
       'sglt2-primary-prevention-hf','iv-iron-hfref-hosp','sacubitril-valsartan-hfref',
       'ticagrelor-vs-clopidogrel-acs','colchicine-postop-af']

def test_in3_pages_render_resolved_harms_scope_and_offline_integrity():
    candidates=[Path(os.environ.get('PROGRAMFILES(X86)',''))/'Microsoft/Edge/Application/msedge.exe',
                Path(os.environ.get('PROGRAMFILES',''))/'Google/Chrome/Application/chrome.exe']
    exe=next((p for p in candidates if p.is_file()),None)
    assert exe,'Local browser required; downloads prohibited'
    server=http.server.ThreadingHTTPServer(('127.0.0.1',8000),
        functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=str(exe),headless=True)
            try:
                page=browser.new_page()
                page.route('**/*',lambda route: route.continue_() if route.request.url.startswith('http://127.0.0.1:8000/') else route.abort())
                errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                for slug in SLUGS:
                    review=json.loads((ROOT/f'docs/reviews/{slug}/review.json').read_text(encoding='utf-8'))
                    assert page.goto(f'http://127.0.0.1:8000/docs/reviews/{slug}/index.html').status==200
                    if review['scope_identity']['verdict']=='SCOPE_MISMATCH':
                        assert 'pre-identified set met eligibility' in page.locator('#tab-overview').inner_text()
                    page.locator('button[data-t="harms"]').click()
                    panel=page.locator('#tab-harms')
                    assert panel.is_visible()
                    text=panel.inner_text()
                    assert 'HARMS_INCOMPLETE' not in text
                    assert '{{' not in text
                    for outcome in review['outcomes']:
                        if outcome['kind']=='harm':
                            assert outcome['name'] in text
                    if review.get('integrity',{}).get('n_not_assessed'):
                        assert 'NOT_ASSESSED (offline lane)' in page.content()
                    assert not errors,errors
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
