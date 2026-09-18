import json
import runpy
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))
helpers = runpy.run_path(str(root / 'tests/test_deletion_invariant.py'))
results = {}
for slug in helpers['TOPICS']:
    directory = root / 'docs/reviews' / slug
    before = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
    after = helpers['publish'](slug, helpers['core'](slug), directory)
    results[slug] = {key: {'before': before[key], 'after': after[key],
                         'moved': before[key] != after[key]}
                     for key in ('review_sha256', 'html_sha256')}
(root / '.tmp/del/rebuild_hashes.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print(json.dumps(results, indent=2))
