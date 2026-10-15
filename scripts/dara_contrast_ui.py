"""Browser contract on the served screening table, using only a local server."""
from pathlib import Path
import functools,http.server,threading,json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
SLUG='daratumumab-rrmm-pfs-bench'
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',8000),functools.partial(Quiet,directory=str(ROOT/'docs')))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(channel='chrome',headless=True)
  try:
   page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:8000/reviews/{SLUG}/index.html',wait_until='networkidle')
   page.locator("nav button[data-t=screening]").click()
   assert 'registry dates, sponsors and arm contrasts are unavailable' not in page.locator('body').inner_text()
   panel=page.locator('#tab-screening');assert panel.is_visible()
   for summary in panel.locator('details > summary').all():
    if summary.is_visible() and not summary.evaluate('(s)=>s.parentElement.open'): summary.click()
   assert panel.get_by_text('UNRESOLVED eligibility (not pooled)',exact=True).is_visible()
   review=json.loads((ROOT/f'docs/reviews/{SLUG}/review.json').read_text(encoding='utf8'))
   for d in review['screening']['records']:
    if d['rule_id'] not in {'X-CONTRAST','UNRESOLVED-CONTRAST'}:continue
    rows=panel.locator('tr').filter(has=page.locator('td',has_text=d['id']))
    assert any(d['rule_id'] in t and d['decision'] in t for t in rows.all_text_contents()),d['id']
   assert not errors,errors
   print('PASS: Screening tab opens; unresolved count visible; every contrast exclusion/unresolved decision rendered; no JavaScript errors.')
  finally:browser.close()
finally:
 server.shutdown();server.server_close()
