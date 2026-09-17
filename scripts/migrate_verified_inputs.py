"""Idempotently migrate source-adjudicated lane inputs; no network or new evidence."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.verified_inputs import FILES, entries, load, normalise


def migrate():
    for directory in sorted((ROOT / 'cache').iterdir()):
        if not directory.is_dir():
            continue
        for name in FILES:
            path = directory / name
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding='utf-8'))
            changed = total = 0
            for pid, value in data.items():
                rows = []
                for old in entries(value):
                    total += 1
                    # Legacy commentary-only records remain readable, but cannot be
                    # promoted into verbatim evidence by a structural migration.
                    new = normalise(old) if old.get('source_span') or old.get('document_ref') else dict(old)
                    # Lane numeric transcriptions store their exact quotation as source.
                    if new.get('document_ref') and not new.get('source_span') and new.get('source'):
                        new['source_span'] = new['source']
                    changed += new != old
                    rows.append(new)
                data[pid] = rows if isinstance(value, list) else rows[0]
            if changed:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print(f'{path.relative_to(ROOT)}: {changed} entries migrated of {total}')
        load(directory.name)


if __name__ == '__main__':
    migrate()
