import contextlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.build_topic import main
from harness import fetch

def no_network(*args, **kwargs):
    raise RuntimeError('ELX lane forbids network; required cache missing')

fetch.run = no_network
pages = sorted((ROOT / 'docs/reviews').glob('*/review.json'))
assert len(pages) == 32
for page in pages:
    assert (ROOT / 'topics' / (page.parent.name + '.json')).is_file()
    assert (ROOT / 'cache' / page.parent.name / 'records.json').is_file()
with (ROOT / '.tmp/elx/rebuild.txt').open('w', encoding='utf-8') as log:
    for n, page in enumerate(pages, 1):
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            main(page.parent.name, '2026-09-11')
        log.flush()
        print(f'{n}/{len(pages)} {page.parent.name}', flush=True)
