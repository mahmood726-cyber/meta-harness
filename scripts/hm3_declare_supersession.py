"""Declare V15-B supersessions from rendered HM3 pages.

Static: landing, reason, delegation. Dynamic: rendered screening records and
unresolved harm IDs. Pinned pages and original harm decisions are preserved.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence/hm3-held-source-audit'
LANDING = 'V15-B (#99, land #99r)'
REASON = '#65 screening rule change (reason/rule/span re-derived; V15-B-01 decisions)'
DECIDED = "Dispatch on Mahmood's explicit delegation, 15 Oct 2026 (option A)"


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    baseline_path = EVIDENCE / 'primary-baseline-f6f7b14c.json'
    decisions_path = EVIDENCE / 'decisions.json'
    baseline = read(baseline_path)
    original = read(decisions_path)
    declared = {'decisions': original} if isinstance(original, list) else original
    slugs = sorted({row['slug'] for row in read(EVIDENCE / 'baseline-debt.json')})
    reviews = {slug: read(ROOT / 'docs/reviews' / slug / 'review.json') for slug in slugs}
    screening = baseline.setdefault('screening_superseded', {})
    changed = []
    for slug in slugs:
        records = reviews[slug]['screening']['records']
        if baseline['pages'][slug]['screening_records'] != records:
            screening[slug] = dict(landing=LANDING, reason=REASON, decided=DECIDED,
                                   screening_records_after=records)
            changed.append(slug)

    superseded = declared.setdefault('harms_superseded', [])
    harm_keys = sorted({(d['topic'], d['outcome']) for d in declared['decisions']})
    added = []
    for slug, name in harm_keys:
        outcome = next(o for o in reviews[slug]['outcomes'] if o['name'] == name)
        if not outcome['result'].get('harms_incomplete'):
            continue
        ids = [row['id'] for row in outcome['result']['known_reported_not_yet_extracted']]
        if not ids:
            raise ValueError(f'{slug}: {name}: incomplete without unresolved IDs')
        entry = dict(topic=slug, outcome=name, landing=LANDING,
                     reason=REASON + '; newly included source-reporting trials have harms not yet extracted',
                     decided=DECIDED, known_reported_not_yet_extracted=ids)
        existing = [s for s in superseded if (s['topic'], s['outcome']) == (slug, name)]
        if existing and existing != [entry]:
            raise ValueError(f'{slug}: {name}: conflicting existing harm supersession')
        if not existing:
            superseded.append(entry)
        added.append(entry)

    pinned = read(baseline_path)
    assert {k: v for k, v in baseline.items() if k != 'screening_superseded'} == {
        k: v for k, v in pinned.items() if k != 'screening_superseded'}
    for path, data in ((baseline_path, baseline), (decisions_path, declared)):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Screening supersessions: {len(changed)}')
    for slug in changed:
        print(f'  {slug}')
    print(f'Harm supersessions: {len(added)} outcomes across {len({s["topic"] for s in added})} slugs')
    for entry in added:
        print(f'  {entry["topic"]}: {entry["outcome"]}: {entry["known_reported_not_yet_extracted"]}')
    print(f'Preserved {len(baseline["pages"])} pinned pages and {len(declared["decisions"])} harm decisions')


if __name__ == '__main__':
    main()
