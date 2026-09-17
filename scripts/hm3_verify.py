"""Build and gate only HM3 pages; block network and retain shared-file bytes."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.gate import gate_page, check_harms_complete

sys.stdout.reconfigure(encoding='utf-8')
folder = ROOT / 'docs/evidence/hm3-held-source-audit'
baseline = json.loads((folder / 'baseline-debt.json').read_text(encoding='utf-8'))
slugs = list(dict.fromkeys(r['slug'] for r in baseline))
if len(sys.argv) > 1:
    assert set(sys.argv[1:]) <= set(slugs), 'Only HM3 pages may be built'
    slugs = [s for s in slugs if s in sys.argv[1:]]
guard = ROOT / '.tmp/hm3/offline'
guard.mkdir(parents=True, exist_ok=True)
(guard / 'sitecustomize.py').write_text(
    'import socket\ndef refused(*args, **kwargs):\n    raise RuntimeError("HM3 offline: network is disabled")\nsocket.socket.connect = refused\nsocket.create_connection = refused\n', encoding='utf-8')
env = dict(os.environ, PYTHONIOENCODING='utf-8', PYTHONPATH=str(guard))
shared = [ROOT/'docs/index.html', ROOT/'registry/blind_map.json']
before = {p: p.read_bytes() if p.exists() else None for p in shared}
results = []
try:
    for slug in slugs:
        assert (ROOT/'cache'/slug/'records.json').is_file()
        proc = subprocess.run([sys.executable,'scripts/build_topic.py',slug,'--now','2026-09-11'],
                              cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',timeout=180)
        (folder/(slug+'.build.txt')).write_text(proc.stdout+proc.stderr,encoding='utf-8')
        ok, reasons = gate_page(str(ROOT/'docs/reviews'/slug))
        hm = check_harms_complete(str(ROOT/'docs/reviews'/slug))
        results.append(dict(slug=slug,build_exit=proc.returncode,gate_ok=ok,reasons=reasons,harms_violations=hm))
        print(slug+': '+('PASS' if ok and proc.returncode==0 else '; '.join(reasons) or f'BUILD EXIT {proc.returncode}'),flush=True)
        if proc.returncode:
            print(proc.stderr[-1600:],flush=True)
finally:
    for p, data in before.items():
        if data is None:
            p.unlink(missing_ok=True)
        else:
            p.write_bytes(data)
    result_path = folder/'gate-results.json'
    prior = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else []
    by_slug = {r['slug']:r for r in prior+results}
    ordered = [by_slug[s] for s in dict.fromkeys(r['slug'] for r in baseline) if s in by_slug]
    result_path.write_text(json.dumps(ordered,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
