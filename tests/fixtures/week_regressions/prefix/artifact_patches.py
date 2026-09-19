from pathlib import Path
import difflib
import json
from unittest.mock import patch
from harness import fixstate

root = Path.cwd()

def write_patch(name, changes):
    parts = []
    for rel, new in changes.items():
        old = (root / rel).read_text(encoding='utf-8')
        if old == new:
            continue
        parts.extend(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/' + rel, tofile='b/' + rel))
        p = root / '.tmp/prefix/patched' / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(new, encoding='utf-8')
    (root / '.tmp/patches' / (name + '.diff')).write_text(''.join(parts), encoding='utf-8')

rel = 'docs/model_stage_inventory.json'
old = (root / rel).read_text(encoding='utf-8')
new = ''.join(line for line in old.splitlines(True) if '"generated_on"' not in line)
write_patch('generated-on', {rel: new})

ledger, readmes = fixstate._expected_views(root)
updates = {'docs/fix_ledger.json': json.dumps(ledger, ensure_ascii=False, indent=1) + chr(10), **readmes}
updates = {rel: text for rel, text in updates.items() if (root / rel).read_text(encoding='utf-8') != text}
write_patch('fixstate-generated', updates)
original = Path.read_text

def replacement(path, *args, **kwargs):
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return original(path, *args, **kwargs)
    return updates[rel] if rel in updates else original(path, *args, **kwargs)

original_load_json = fixstate._load_json

def replacement_json(path):
    if Path(path) == root / 'docs/fix_ledger.json':
        return ledger
    return original_load_json(path)

with patch.object(Path, 'read_text', replacement), patch.object(fixstate, '_load_json', replacement_json):
    result = fixstate.check(root)
    print('fixstate.check with generated patch overlaid:', result)
    (root / '.tmp/prefix/generated-view-proof.txt').write_text('fixstate.check with generated patch overlaid: ' + repr(result) + chr(10), encoding='utf-8')
    assert result[0], result[1]
