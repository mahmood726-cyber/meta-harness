"""Offline lane command runner, with socket network access explicitly blocked."""
import json
import os
import runpy
import socket
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
os.chdir(ROOT)
def blocked(*args,**kwargs):
    raise RuntimeError('Network prohibited in IN3')
socket.socket.connect=blocked
socket.create_connection=blocked
if sys.argv[1]=='build':
    from scripts.build_topic import main
    slugs=sys.argv[2:] or [p.parent.name for p in sorted((ROOT/'docs/reviews').glob('*/review.json'))]
    for i,slug in enumerate(slugs,1):
        assert (ROOT/f'cache/{slug}/records.json').is_file(),slug
        main(slug,'2026-09-11')
        print(f'BUILT {i} of {len(slugs)} requested topics: {slug}',flush=True)
else:
    script=sys.argv[1]
    sys.argv=sys.argv[1:]
    runpy.run_path(script,run_name='__main__')
