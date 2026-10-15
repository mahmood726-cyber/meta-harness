"""Declare V15-B supersessions from rendered HM3 pages.

Static: landing, reason, delegation. Dynamic: rendered screening records and
unresolved harm IDs. Pinned pages and original harm decisions are preserved.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/evidence/hm3-held-source-audit'
LANDING = 'V15-B (#99, land #99r)'
REASON = '#65 screening rule change (reason/rule/span re-derived; V15-B-01 decisions)'
DECIDED = "Dispatch on Mahmood's explicit delegation, 15 Oct 2026 (option A)"


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def baseline_format(raw, baseline):
    """Fail closed unless unchanged indent=1 serialization matches exactly."""
    suffix = '\n' if raw.endswith(b'\n') else ''
    for ensure_ascii in (False, True):
        encoded = (json.dumps(baseline, indent=1, ensure_ascii=ensure_ascii) + suffix).encode('utf-8')
        if encoded == raw and hashlib.sha256(encoded).digest() == hashlib.sha256(raw).digest():
            print(f'Baseline unchanged serialization SHA-256 PASS: {hashlib.sha256(raw).hexdigest()}')
            return ensure_ascii, suffix
    raise ValueError('Baseline unchanged serialization SHA-256 mismatch; no files written')


def screening_entry(previous, records):
    entry = dict(landing=LANDING, reason=REASON, decided=DECIDED,
                 screening_records_after=records)
    if previous is not None:
        if {k: v for k, v in previous.items() if k != 'history'} == entry:
            return deepcopy(previous)
        prior = deepcopy(previous)
        history = prior.pop('history', [])
        if not isinstance(history, list):
            raise ValueError('Screening history must be a list')
        entry['history'] = history + [prior]
    return entry


def main():
    baseline_path = EVIDENCE / 'primary-baseline-f6f7b14c.json'
    decisions_path = EVIDENCE / 'decisions.json'
    raw = baseline_path.read_bytes()
    baseline = json.loads(raw)
    ensure_ascii, suffix = baseline_format(raw, baseline)
    original = read(decisions_path)
    if not isinstance(original, list):
        raise ValueError('decisions.json must remain a list')
    harms_path = EVIDENCE / 'harms_superseded.json'
    superseded = read(harms_path) if harms_path.exists() else []
    if not isinstance(superseded, list):
        raise ValueError('harms_superseded.json must be a list')
    slugs = sorted({row['slug'] for row in read(EVIDENCE / 'baseline-debt.json')})
    reviews = {slug: read(ROOT / 'docs/reviews' / slug / 'review.json') for slug in slugs}
    screening = baseline.setdefault('screening_superseded', {})
    changed = []
    archived = []
    for slug in slugs:
        records = reviews[slug]['screening']['records']
        if baseline['pages'][slug]['screening_records'] != records:
            previous = screening.get(slug)
            entry = screening_entry(previous, records)
            if previous is not None and entry != previous:
                archived.append(slug)
            screening[slug] = entry
            changed.append(slug)

    harm_keys = sorted({(d['topic'], d['outcome']) for d in original})
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
    baseline_path.write_text(json.dumps(baseline, ensure_ascii=ensure_ascii, indent=1) + suffix,
                             encoding='utf-8', newline='\n')
    harms_path.write_text(json.dumps(superseded, ensure_ascii=False, indent=1) + '\n',
                          encoding='utf-8', newline='\n')
    print('Prior entries moved to history: ' + ', '.join(archived))
    print(f'Screening supersessions: {len(changed)}')
    for slug in changed:
        print(f'  {slug}')
    print(f'Harm supersessions: {len(added)} outcomes across {len({s["topic"] for s in added})} slugs')
    for entry in added:
        print(f'  {entry["topic"]}: {entry["outcome"]}: {entry["known_reported_not_yet_extracted"]}')
    print(f'Preserved {len(baseline["pages"])} pinned pages and {len(original)} harm decisions')


if __name__ == '__main__':
    main()
