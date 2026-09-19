from pathlib import Path
import subprocess
import json
import hashlib
import runpy

root = Path.cwd()
out = root / '.tmp/prefix'
full = (out / 'full-suite-final.txt').read_text(encoding='utf-8')
assert 'short test summary' in full or ' passed in ' in full or ' xfailed in ' in full, 'full suite not finished'

# Restore only this task's known test-produced line-ending side effect.
p = root / 'docs/compat_direction_sweep.json'
p.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:docs/compat_direction_sweep.json']))

def run(name, args):
    result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out / name).write_bytes(result.stdout)
    print(name, result.returncode, result.stdout.decode('utf-8')[-300:])
    return result.returncode

args = ['python', '-X', 'utf8', '-m', 'pytest'] + [str(p.relative_to(root)) for p in sorted((root / 'tests').glob('test_week_regressions_*.py'))] + ['-q', '-p', 'no:cacheprovider']
assert run('regressions-final.txt', args) == 0
run('search-completeness.txt', ['python', '-X', 'utf8', '-c', 'import scripts.verify_all as v; print(v.limb_search_completeness())'])

checks = []
for p in sorted((root / '.tmp/patches').glob('*.diff')):
    # Unified patches are LF text even on Windows; source evidence is never normalized.
    p.write_bytes(p.read_bytes().replace(bytes([13, 10]), bytes([10])))
    r = subprocess.run(['git', 'apply', '--check', str(p)], capture_output=True, text=True)
    checks.append(p.name + ': ' + str(r.returncode) + ' ' + r.stdout + r.stderr)
    assert r.returncode == 0, checks[-1]
(out / 'patch-checks.txt').write_text(chr(10).join(checks), encoding='utf-8')

p = out / 'base/docs/model_stage_inventory.json'
p.parent.mkdir(parents=True, exist_ok=True)
p.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:docs/model_stage_inventory.json']))
manifest = json.loads((out / 'MANIFEST.json').read_text(encoding='utf-8'))
manifest['sha256'][str(p.relative_to(out))] = hashlib.sha256(p.read_bytes()).hexdigest()
manifest['patch_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root / '.tmp/patches').glob('*.diff'))}
(out / 'MANIFEST.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

run('diff-check.txt', ['git', 'diff', '--check'])
run('status-final.txt', ['git', 'status', '--short'])
runpy.run_path(str(out / 'write_report.py'), run_name='__main__')

summary = next(line for line in reversed(full.splitlines()) if ' passed' in line or ' failed' in line)
focused = (out / 'regressions-final.txt').read_text(encoding='utf-8').strip().splitlines()[-1]
if 'FAILED tests/test_fixstate.py::test_real_store_validates' in full:
    path = root / 'STUCK_FAILURES.md'
    existing = path.read_text(encoding='utf-8') if path.exists() else ''
    note = '\n## RG 2026-09-18 — generated fixstate views outside ownership\n\nMEASURED: ' + summary + '\n\n`tests/test_fixstate.py::test_real_store_validates` refuses stale `docs/fix_ledger.json` and the search measurement evidence README fix-state line. Production-generated proposal: `.tmp/patches/fixstate-generated.diff`. The owner must regenerate views after integrating source changes; do not weaken the currency test. See `LANE-RG-REPORT.md` for the exact failure. No bypass or commit.\n'
    if '## RG 2026-09-18' not in existing:
        path.write_text(existing + note, encoding='utf-8', newline=chr(10))
(root / 'PROGRESS.md').write_text('# RG checkpoint\n\nReport: LANE-RG-REPORT.md. No commit/network/reset/checkout/stash.\n\nFocused: ' + focused + '\nFull suite: ' + summary + '\n\nImplemented permitted source fixes; owner patches and pre-fix pins retained under .tmp/patches and .tmp/prefix. Search-completeness result and all raw outputs are embedded in the report. Remaining work belongs to integration: apply/review owner patches, regenerate fixstate views, rerun full standard.\n\n| Static | Dynamic |\n|---|---|\n| Synthetic counterexamples and authored requirements | Production/pinned execution and physical-byte digests |\n| Sealed historical date | Explicit live UTC input validation |\n', encoding='utf-8', newline=chr(10))
