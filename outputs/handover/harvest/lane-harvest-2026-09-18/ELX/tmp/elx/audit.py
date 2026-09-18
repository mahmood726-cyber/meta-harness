import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from harness.honest_ratchet import inventory, check

def old(path):
    return subprocess.check_output(['git', 'show', '237e9094:' + path.relative_to(ROOT).as_posix()], cwd=ROOT)

def diff(a, b, path=''):
    if type(a) is not type(b):
        return [{'path': path, 'before': a, 'after': b}]
    if isinstance(a, dict):
        out = []
        for key in sorted(a.keys() | b.keys()):
            out.extend(diff(a.get(key), b.get(key), path + '/' + key))
        return out
    if isinstance(a, list) and len(a) == len(b):
        return [item for i, (x, y) in enumerate(zip(a, b)) for item in diff(x, y, path + '/' + str(i))]
    return [] if a == b else [{'path': path, 'before': a, 'after': b}]

pages = []
for review in sorted((ROOT / 'docs/reviews').glob('*/review.json')):
    manifest = review.parent / 'manifest.json'
    before = json.loads(old(manifest))
    after = json.loads(manifest.read_text(encoding='utf-8'))
    fields = diff(json.loads(old(review)), json.loads(review.read_text(encoding='utf-8')))
    page = review.parent / 'index.html'
    before_markers = inventory(old(page).decode('utf-8'))
    after_markers = inventory(page.read_text(encoding='utf-8'))
    pages.append({'slug': review.parent.name,
                  'hashes': {key: [before.get(key), after.get(key)] for key in ('review_sha256', 'html_sha256')},
                  'review_fields_changed': fields,
                  'marker_changes': {k: [before_markers[k], after_markers[k]] for k in before_markers if before_markers[k] != after_markers[k]}})
(ROOT / '.tmp/elx/page_diffs.json').write_text(json.dumps(pages, indent=2, ensure_ascii=False), encoding='utf-8')
print('Changed reviews:', [p['slug'] for p in pages if p['review_fields_changed']])
print('Changed HTML:', [p['slug'] for p in pages if p['hashes']['html_sha256'][0] != p['hashes']['html_sha256'][1]])
ok, reasons = check(ROOT, base_ref='237e9094')
(ROOT / '.tmp/elx/ratchet.txt').write_text('\n'.join(reasons), encoding='utf-8')
print('Ratchet', ok)
print('\n'.join(reasons))
