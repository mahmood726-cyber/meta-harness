from pathlib import Path
import subprocess
import difflib
import hashlib
import json

root = Path.cwd()
rel = 'harness/fetch.py'
old = (root / rel).read_text(encoding='utf-8')
needle = '        with open(path, encoding="utf-8") as f:\n            return json.load(f)'
replacement = '''        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if data.get("pubmed_queries") != config.get("pubmed_queries"):
            raise ValueError("cached query contract differs from requested PubMed queries; explicit refresh required")
        return data'''
assert needle in old
new = old.replace(needle, replacement)
(root / '.tmp/prefix/patched' / rel).write_text(new, encoding='utf-8')
(root / '.tmp/patches/search-contract.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/' + rel, tofile='b/' + rel)), encoding='utf-8')

paths = ['harness/compat_check.py', 'harness/propositions.py', 'harness/harms.py', 'harness/known_missing.py', 'harness/comparator_second_pass.py', 'harness/screen.py', 'harness/reason_audit.py', 'harness/fetch.py', 'harness/pipeline.py']
for rel in paths:
    p = root / '.tmp/prefix/base' / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:' + rel]))
manifest = {'base': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'historical_pins': {'adjustment/design_key.py': '3f8add72^:harness/design_key.py', 'publication/manuscript.py': '04902ecf^:harness/manuscript.py'}, 'sha256': {str(p.relative_to(root / '.tmp/prefix')): hashlib.sha256(p.read_bytes()).hexdigest() for p in (root / '.tmp/prefix').rglob('*.py') if 'base' in p.parts or 'adjustment' in p.parts or 'publication' in p.parts}}
(root / '.tmp/prefix/MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

def run(name, args):
    r = subprocess.run(['python', '-X', 'utf8'] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (root / '.tmp/prefix' / name).write_bytes(r.stdout)
    print(name, 'exit', r.returncode, r.stdout.decode('utf-8')[-220:])

run('owner-before.txt', ['-m', 'pytest', 'tests/test_week_regressions_audit.py', 'tests/test_week_regressions_custody.py', 'tests/test_week_regressions_composite.py', 'tests/test_week_regressions_search_contract.py', '-q', '--runxfail', '-p', 'no:cacheprovider'])
run('historical-adjustment-before.txt', ['-c', "import sys; sys.path.insert(0,'tests'); from test_week_regressions_audit import estimator_requirement,load_pin; estimator_requirement(load_pin('adjustment/design_key.py'))"])
run('historical-publication-before.txt', ['-c', "import sys; sys.path.insert(0,'tests'); from test_week_regressions_audit import load_pin; from test_week_regressions_publication_bias import requirement; requirement(load_pin('publication/manuscript.py'))"])
run('regressions-after.txt', ['-m', 'pytest'] + [str(p.relative_to(root)) for p in sorted((root / 'tests').glob('test_week_regressions_*.py'))] + ['-q', '-p', 'no:cacheprovider'])
