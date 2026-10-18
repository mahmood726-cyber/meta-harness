"""Reproduce the R3 admission pins from held source bytes; never run during a build."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from harness import bench_routes as br, extract

def generate():
    records=json.loads((ROOT/'cache'/br.SLUG/'records.json').read_text(encoding='utf8'))['records']
    pins={}
    for pid, anchor in br.ROUTES.items():
        hits=[r for r in records if r['id']==pid]
        assert len(hits)==1
        text=hits[0]['abstract']; assert text.count(anchor)==1
        start=text.index(anchor)
        match=extract._EFFECT.search(extract._norm(text),start); assert match
        span=text[start:match.end()]
        value=extract._effect_from_match(match,span); assert value
        pins[pid]=dict(anchor=anchor,span=span,value=dict(zip(('scale','effect','ci_low','ci_high'),value)),refuse=pid=='40680754')
    return pins

if __name__=='__main__':
    pins=generate()
    target=ROOT/'tests/fixtures/r3_bench_route_pins.json'
    if '--write' in sys.argv:
        target.write_text(json.dumps(pins,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    else:
        assert pins==json.loads(target.read_text(encoding='utf8'))
        print('PASS: every pinned value and span reproduced from held records')
