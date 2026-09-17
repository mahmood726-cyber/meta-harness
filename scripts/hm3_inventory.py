"""Offline HM3 inventory; no source mutations."""
import json
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import aact, gate, harms

BASE = 'f6f7b14c820bdadd258122ac0bb54c7e4d2a989a'
SLUGS = list(dict.fromkeys(r['slug'] for r in json.loads(
    (ROOT/'docs/evidence/hm3-held-source-audit/baseline-debt.json').read_text(encoding='utf-8'))))

def main():
    out = ROOT / '.tmp/hm3'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for slug in SLUGS:
        folder = ROOT / 'cache' / slug
        recs = {str(r['id']): r for r in json.loads((folder / 'records.json').read_text(encoding='utf-8'))['records']}
        review = json.loads(subprocess.check_output(
            ['git','show',f'{BASE}:docs/reviews/{slug}/review.json'],cwd=ROOT,encoding='utf-8'))
        cfg = json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf-8'))
        for o in review['outcomes']:
            for item in o.get('result', {}).get('known_reported_not_yet_extracted', []):
                pid = item['id']
                spec = next(s for s in cfg['harm_outcomes'] if s['name'] == o['name'])
                rows.append(dict(slug=slug, outcome=o['name'], id=pid, signal=item['span'],
                                 spec=spec, record=recs.get(pid),
                                 files=[str(p.relative_to(ROOT)).replace('\\', '/') for p in folder.rglob('*') if p.is_file()]))
    (out / 'baseline.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    print('AACT', aact.snapshot_dir())
    for r in rows:
        print('\n', r['slug'], r['id'], r['outcome'])
        print(r['spec'])
        print('SIGNAL:', r['signal'])
        print('ABSTRACT:', (r['record'] or {}).get('abstract'))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
