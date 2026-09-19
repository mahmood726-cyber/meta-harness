from pathlib import Path
import difflib

root = Path.cwd()
changes = {
    'harness/known_missing.py': ('missing-family', lambda s: s.replace('return str(value or "").replace("PMID ", "").strip()', 'return str(value or "").replace("PMID ", "").split(" · ")[-1].strip()')),
    'harness/comparator_second_pass.py': ('comparator-overlap', lambda s: s.replace('    out["overlap"] = ov', '''    else:
        ov["shared_k"] = "UNMEASURED_CURRENT_POOL"
        ov["shared_k_measurement"] = "NOT_MEASURED"
        ov["shared_trials"] = []
        ov["only_ours"] = []
        ov["only_theirs"] = []
        ov["method"] = "current-pool intersection not supplied"
        ov["note"] = "Comparator enumeration alone cannot establish current-pool overlap."
    out["overlap"] = ov''')),
}
for rel, (name, transform) in changes.items():
    old = (root / rel).read_text(encoding='utf-8')
    p = root / '.tmp/prefix/patched' / rel
    new = transform(p.read_text(encoding='utf-8'))
    p.write_text(new, encoding='utf-8')
    (root / '.tmp/patches' / (name + '.diff')).write_text(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/' + rel, tofile='b/' + rel)), encoding='utf-8')
