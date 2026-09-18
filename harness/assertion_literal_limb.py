"""Fail-closed assertion-literal verification, evaluated against current source."""
from pathlib import Path
import json
from scripts.assertion_literal_sweep import blockers, sweep


def limb_assertion_literals(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    try:
        current = sweep(root)
        saved = json.loads((root / 'docs/assertion_literal_sweep.json').read_text(encoding='utf8'))
        bad = blockers(current)
        details = [f"{f['file']}:{f['line']} {f['verdict']}: {f['literal']!r}" for f in bad]
        if saved != current:
            details.insert(0, 'STALE_ASSERTION_SWEEP: saved report differs from current source/registry')
        return ('REFUSED' if details else 'PASS', '\n'.join(details) or 'Current sweep has no unresolved assertions.')
    except Exception as exc:
        return 'REFUSED', f'ASSERTION_SWEEP_FAILED: {type(exc).__name__}: {exc}'


if __name__ == '__main__':
    verdict, detail = limb_assertion_literals()
    print(verdict)
    print(detail)
    raise SystemExit(verdict != 'PASS')
