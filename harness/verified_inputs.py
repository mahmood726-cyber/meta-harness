"""Canonical verified inputs and fail-closed held-source validation.

Legacy entries without a verbatim span retain their existing verification path.
An explicit source_span is never treated as free-form citation commentary.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ('verified_arms.json', 'verified_effects.json')


def normalise(entry):
    if not isinstance(entry, dict) or not entry.get('outcome'):
        raise ValueError('Verified inputs require objects with an outcome')
    out = dict(entry)
    if out.get('kind') not in (None, 'extracted_counts', 'extracted_effect', 'typed_refusal'):
        raise ValueError('Unknown verified input kind')
    refusal = (out.get('kind') == 'typed_refusal' or out.get('absent') or
               out.get('typed_refusal') or out.get('absent_kind') == 'adjudicated_absent')
    out['kind'] = ('typed_refusal' if refusal else
                   'extracted_effect' if out.get('effect') is not None else 'extracted_counts')
    if refusal:
        out['provenance'] = (out.get('refusal_provenance') or out.get('reason_code') or
                             out.get('state') or out.get('provenance'))
        for key in ('override', 'absent', 'typed_refusal', 'absent_kind',
                    'reason_code', 'refusal_provenance', 'source_adjudicated'):
            out.pop(key, None)
    else:
        out.pop('absent', None)
    if out.get('source_level') in ('abstract', 'fulltext'):
        out['source_level'] = 1
    if not refusal and out.get('document_ref'):
        out.setdefault('reason', out.get('verification') or 'Transcription from the identified held source.')
        out.setdefault('provenance', 'abstract_verified' if 'records.json' in out['document_ref']
                       else 'fulltext_verified')
    return out


def runtime(entry):
    """Adapt canonical data to the existing extraction precedence contract."""
    out = normalise(entry)
    if out['kind'] == 'typed_refusal':
        out.update(absent=True, override=True)
    if out.get('source_span'):
        out.setdefault('source', out['source_span'])
    return out


def _validate(entry, directory, pid, canonical=False):
    span = entry.get('source_span')
    if span is None:
        if canonical:
            raise ValueError(f'{directory.name}/{pid}: canonical entry requires source_span')
        return  # legacy free-form source commentary; existing verifier remains authoritative
    if not isinstance(span, str) or not span:
        raise ValueError(f'{directory.name}/{pid}: empty source_span')
    ref = (entry.get('document_ref') or '').split('#')[0]
    candidates = []
    if ref:
        candidates = [directory / ref, directory.parent.parent / ref]
    else:
        candidates = [directory / 'records.json', directory / f'ft_{pid}.txt']
    found = False
    for path in candidates:
        if not path.is_file():
            continue
        text = path.read_text(encoding='utf-8')
        if path.name == 'records.json':
            data = json.loads(text)
            rec = next((r for r in data.get('records', []) if str(r.get('id')) == str(pid)), {})
            texts = [rec.get('abstract', ''), rec.get('fulltext', '')]
        else:
            texts = [text]
        if any(span in value for value in texts if isinstance(value, str)):
            found = True
            break
    if not found:
        raise ValueError(f'{directory.name}/{pid}: source_span absent from held document {ref}')
    if entry['kind'] == 'typed_refusal' and not entry.get('reason'):
        raise ValueError(f'{directory.name}/{pid}: typed refusal has no reason')
    if entry['kind'] == 'typed_refusal' and entry.get('provenance') not in {
            'REFUSED_ON_EVIDENCE', 'SIGNAL_SPURIOUS', 'MULTI_ARM_UNRESOLVED',
            'TIMEPOINT_MISMATCH', 'POPULATION_MISMATCH',
            'EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH'}:
        raise ValueError(f'{directory.name}/{pid}: unrecognized typed refusal provenance')


def load(slug, cache_root=None):
    directory = Path(cache_root or ROOT / 'cache') / slug
    result = {}
    for name in FILES:
        path = directory / name
        data = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
        result[name] = {}
        for pid, value in data.items():
            originals = entries(value)
            rows = [normalise(e) for e in originals]
            for old, row in zip(originals, rows):
                _validate(row, directory, pid, canonical='kind' in old)
            result[name][pid] = rows if isinstance(value, list) else rows[0]
    return result


def validate_referenced_span(row):
    """Recheck an explicitly cited held document during absence annotation."""
    ref = Path((row.get('document_ref') or '').split('#')[0])
    if (len(ref.parts) < 3 or ref.parts[0] not in ('cache', 'outputs')
            or not (ROOT / ref).resolve().is_relative_to(ROOT.resolve())):
        raise ValueError('Typed refusal requires a held verbatim span in an identified held document')
    entry = dict(row, kind='typed_refusal',
                 provenance=row.get('refusal_provenance') or row.get('reason_code'))
    _validate(entry, ROOT / 'cache' / ref.parts[1],
              str(row.get('id', '')).replace('PMID ', ''), canonical=True)


def entries(value):
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    if not all(isinstance(v, dict) and v.get('outcome') for v in values):
        raise ValueError('Verified inputs require objects with an outcome')
    names = [v['outcome'] for v in values]
    if len(names) != len(set(names)):
        raise ValueError('Duplicate verified input for one trial and outcome')
    return values


def for_outcome(data, name):
    return {pid: runtime(entry) for pid, value in (data or {}).items()
            for entry in entries(value) if entry['outcome'] == name}
