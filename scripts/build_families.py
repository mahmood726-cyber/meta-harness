"""Rebuild full registry offline, verifying every source-row hash before writing."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.family_compact import regenerate, write_json, read_compact_registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.slug not in {p.stem for p in (root / 'topics').glob('*.json')}:
        parser.error('Unknown topic slug')
    try:
        doc = read_compact_registry(root / 'cache' / args.slug / 'family_registry.json')
        full = regenerate(doc, snapshot=args.snapshot)
    except (ValueError, KeyError, OSError) as exc:
        print('NOT PRESERVED: ' + str(exc), file=sys.stderr)
        return 1
    output = args.output or root / '.tmp' / args.slug / 'family_registry.full.json'
    write_json(output, full)
    print(f'PRESERVED: {len(doc["rows"])} of {len(doc["rows"])} referenced AACT rows verified; {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
