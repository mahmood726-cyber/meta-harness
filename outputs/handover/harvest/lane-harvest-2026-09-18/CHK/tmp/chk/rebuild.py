import json
import socket
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.build_topic import main
from harness import fetch

def forbidden(*args, **kwargs):
    raise RuntimeError('CHK offline run: network forbidden')
socket.socket.connect = forbidden
socket.create_connection = forbidden
slugs = sorted(p.parent.name for p in (ROOT / 'docs/reviews').glob('*/review.json'))
slugs = ['iv-iron-hfref-hosp', 'glp1-ra-mace-t2d'] + [s for s in slugs if s not in ('iv-iron-hfref-hosp', 'glp1-ra-mace-t2d')]
for slug in slugs:
    assert Path(fetch.cache_path(slug)).is_file(), slug
for slug in slugs:
    print('BUILD', slug, flush=True)
    main(slug, '2026-09-11')
print('BUILT', len(slugs), flush=True)
