"""Offline exact-text inventory. Candidate classes are triage, never registration.

No heuristic here can turn prose into evidence or change the gate verdict.
"""
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def normalize(value):
    return ' '.join(str(value).split())


def leaves(value, path='$'):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from leaves(item, path + '.' + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            yield from leaves(item, path + f'[{i}]')
    elif value is not None:
        yield normalize(value), path


def classify(text, paths):
    """An explicitly INFERRED work queue, not a factual classification claim."""
    if re.search(r'\b(pooled|pooling|coverage|downgrades|of \d+|percent|percentage)\b', text, re.I):
        return 'TRANSFORMATION', ('No registered recomputation binds this entire text run to its '
                                  'per-item inputs. Matching stored totals or interpolated fields '
                                  'alone is not proof of the aggregate predicate.')
    if re.search(r'\b(eligible|eligibility|refused|risk of bias|judgement|judgment|INCLUDE|X[1-9]|assessed)\b', text, re.I):
        return 'JUDGEMENT', ('The rendered decision is not bound to a registered judgement with '
                             'a specific basis and adjudication. Existing prose or matching '
                             'review fields cannot substitute for that binding.')
    if re.search(r'\b(may|might|suggests?|interpretation|plausible|auditability|authority)\b', text, re.I):
        return 'INTERPRETATION', ('No registered interpretation with an explicit alternative '
                                  'formulation covers this text run; mixed factual clauses '
                                  'also require their own provenance.')
    if paths:
        return 'FACT', ('Exact review-field matches are listed, but this displayed assertion has '
                        'no registered field-to-source-span binding. A review field is not '
                        'independent evidence. Labels in data cells cannot be exempted by text whitelist.')
    return 'FACT', ('No exact scalar review-field match or registered source-span binding was '
                    'found for the whole run. Composite prose needs clause-level registration; '
                    'short data-cell values remain auditable until semantically typed.')


def main():
    scope = json.loads((ROOT / 'LANE-CGX2-SCOPE.json').read_text(encoding='utf-8'))
    review = json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    paths = defaultdict(list)
    for value, path in leaves(review):
        paths[value].append(path)
    page = scope['pages'][0]
    units = []
    for index, violation in enumerate(page['served']['violation_examples'], 1):
        text = violation['detail']
        matches = paths.get(normalize(text), [])
        candidate, reason = classify(text, matches)
        units.append({'name': violation.get('unit_id', f'debt-{index:04d}'),
                      'exact_text': text, 'context': violation.get('context'),
                      'code': violation['code'], 'candidate_class': candidate,
                      'classification_status': 'INFERRED_TRIAGE_ONLY',
                      'registration_status': 'UNREGISTERED_MIGRATION_REQUIRED',
                      'reason': reason, 'exact_review_field_matches': matches})
    result = {'schema': 'cgx2-debt-inventory/v1', 'finish_condition_met': False,
              'note': 'These units are not claimed inherently impossible to register. They remain unfinished migration work; this inventory is not an exemption.',
              'by_candidate_class': dict(Counter(u['candidate_class'] for u in units)),
              'units': units, 'structural_units': page['served']['structural_units']}
    (ROOT / 'LANE-CGX2-UNREGISTERED.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    lines = ['# CGX2 exact-text unresolved inventory', '', result['note'], '',
             'Candidate classes are INFERRED triage, not registered evidence.', '']
    for unit in units:
        lines += [f"## {unit['name']} — {unit['candidate_class']} (unregistered)", '',
                  'Exact rendered text:', '', '```text', unit['exact_text'], '```', '',
                  unit['reason'], '', 'DOM context: `' + str(unit['context']) + '`.', '']
        if unit['exact_review_field_matches']:
            lines += ['Exact scalar field matches: ' + ', '.join('`' + p + '`' for p in unit['exact_review_field_matches']) + '.', '']
    (ROOT / 'LANE-CGX2-UNREGISTERED.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f"Enumerated {len(units)} unresolved units; no exemptions asserted.")


if __name__ == '__main__':
    main()
