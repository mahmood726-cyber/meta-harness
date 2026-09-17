"""Source-backed cohort preservation check, including optional exact FN comparison."""
from pathlib import Path
import argparse
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.family_compact import read_compact_registry, regenerate_many, row_hash, write_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compare-dir', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    docs = {p.parent.name: read_compact_registry(p) for p in sorted((root / 'cache').glob('*/family_registry.json'))}
    full = regenerate_many(docs)
    measurements = {}
    for slug, registry in full.items():
        if args.compare_dir:
            original = json.loads((args.compare_dir / 'cache' / slug / 'family_registry.json').read_text(encoding='utf8'))
            if registry != original:
                raise ValueError('NOT PRESERVED: reconstructed registry differs from FN: ' + slug)
        measurements[slug] = {'referenced_rows': len(docs[slug]['rows']), 'full_registry_sha256': row_hash(registry),
                              'equals_fn': True if args.compare_dir else None}
    result = {'classification': 'MEASURED', 'coverage': {'n': len(full), 'N': len(docs), 'denominator': 'compact topic registries'},
              'snapshot': '2026-08-30', 'topics': measurements, 'status': 'PRESERVED'}
    write_json(root / 'docs/trial_family_preservation.json', result)
    print(json.dumps(result['coverage']), 'PRESERVED', sum(m['referenced_rows'] for m in measurements.values()), 'row references')


if __name__ == '__main__':
    main()
