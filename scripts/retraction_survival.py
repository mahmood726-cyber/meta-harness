"""Require every served review to retain each base retraction/scope marker."""
import html
import re
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
MARKS = ['We retract', 'RETRACTED', 'REPRODUCTION_RETRACTION', 'retracted claim',
         'is retracted', 'network meta-analysis', 'scope mismatch']

def text(value):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', value)))

def main(base):
    paths = sorted((ROOT / 'docs/reviews').glob('*/index.html'))
    kept = 0
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        before = text(subprocess.check_output(['git', 'show', f'{base}:{relative}'], cwd=ROOT).decode('utf-8'))
        after = text(path.read_text(encoding='utf-8'))
        drops = {m: (before.count(m), after.count(m)) for m in MARKS if after.count(m) < before.count(m)}
        if drops:
            print('LOST', path.parent.name, drops)
        else:
            kept += 1
    print(f'pages with every marking kept (count >= base): {kept} of {len(paths)}')
    return int(kept != len(paths))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'f6f7b14c'))
