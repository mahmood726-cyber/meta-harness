"""Rebuild full registry offline, verifying every source-row hash before writing."""
from pathlib import Path
import argparse
import json
import sys
import shutil
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.family_compact import regenerate, write_json, read_compact_registry


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('slug')
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--offline', action='store_true', help='Recompute family ledger from held cache and review membership, without AACT')
    parser.add_argument('--check', action='store_true', help='Compare regenerated family bytes without modifying caches (requires --offline)')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.offline:
        from harness import trial_family
        from harness.family_compact import write_families
        slugs = sorted(p.parent.name for p in (root/'cache').glob('*/families.json')) if args.slug=='all' else [args.slug]
        passed = 0
        for slug in slugs:
            if slug not in {p.stem for p in (root/'topics').glob('*.json')}:
                parser.error('Unknown topic slug')
            def load(path):
                return json.loads(path.read_text(encoding='utf8'))
            directory = root/'cache'/slug
            records = load(directory/'records.json')
            config = load(root/'topics'/f'{slug}.json')
            ledger = load(directory/'retrieval_ledger.json') if (directory/'retrieval_ledger.json').exists() else None
            nodes = trial_family.prepare(root,slug,records['records']+records.get('ctgov',[]),config,ledger)
            review = load(root/'docs/reviews'/slug/'review.json')
            chain = trial_family.attach_review(review,nodes)
            doc = {'schema_version':1,'count_chain':chain,'families':nodes}
            with tempfile.TemporaryDirectory(dir=root/'.tmp') as tmp:
                target = Path(tmp)
                for path in directory.glob('family_registry*'):
                    shutil.copyfile(path,target/path.name)
                write_families(target/'families.json',doc)
                same = all((directory/p.name).read_bytes()==p.read_bytes() for p in target.glob('families*'))
                if not args.check:
                    for p in target.glob('families*'):
                        shutil.copyfile(p,directory/p.name)
                passed += same
                print(slug, 'BYTE_IDENTICAL' if same else ('DIFFERENT' if args.check else 'REGENERATED'),flush=True)
        print(f'Byte-identical family caches: {passed} of {len(slugs)}')
        return int(args.check and passed!=len(slugs))
    if args.check:
        parser.error('--check requires --offline')
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
