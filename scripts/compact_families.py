"""Migrate held full registries and family artifacts to the reference representation."""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.family_compact import compact_registry, write_registry, write_families, write_json


def main():
    root = Path(__file__).resolve().parents[1]
    sizes = {}
    for path in sorted((root / 'cache').glob('*/family_registry.json')):
        slug = path.parent.name
        before = sum(p.stat().st_size for p in path.parent.glob('famil*.json'))
        doc = json.loads(path.read_text(encoding='utf8'))
        if 'format' in doc:
            raise ValueError('Already compact: ' + slug)
        write_registry(path, compact_registry(doc))
        families = path.with_name('families.json')
        write_families(families, json.loads(families.read_text(encoding='utf8')))
        for name in ('family_query.json', 'family_discovery.json'):
            other = path.with_name(name)
            if other.exists():
                write_json(other, json.loads(other.read_text(encoding='utf8')))
        after = sum(p.stat().st_size for p in path.parent.glob('famil*') if p.is_file())
        sizes[slug] = {'before_bytes': before, 'after_bytes': after}
        print(slug, before, after, flush=True)
    write_json(root / 'docs/trial_family_compaction.json', {'classification': 'MEASURED', 'topics': sizes})


if __name__ == '__main__':
    main()
