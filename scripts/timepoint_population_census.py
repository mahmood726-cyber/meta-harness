"""Offline census; stdout is JSON, no writes or import-time stream changes."""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from harness import population_rules as population
from harness import timepoint_identity as timepoint


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def census(root=ROOT):
    origins_by_path = {}
    metrics = {k: {'n': 0, 'N': 0, 'items': []} for k in (
        'outcomes_without_target_timepoint', 'rows_flipped_by_origin_normalisation',
        'outcomes_with_population_rule_inconsistencies', 'pools_mixing_patients_and_events')}
    coverage = {'topics': 0, 'reviews': 0, 'missing_reviews': [], 'rows_with_explicit_origin': 0,
                'rows_with_unresolved_timepoint': 0, 'pools_with_unknown_count_unit': []}
    for path in sorted((root / 'topics').glob('*.json')):
        config = read(path)
        slug = config.get('slug', path.stem)
        coverage['topics'] += 1
        specs = list(population.outcome_specs(config))
        for spec, _ in specs:
            m = metrics['outcomes_without_target_timepoint']
            m['N'] += 1
            if not str(spec.get('timepoint') or '').strip():
                m['items'].append(f"{slug}::{spec['name']}")
        review_path = root / 'docs' / 'reviews' / slug / 'review.json'
        if not review_path.exists():
            coverage['missing_reviews'].append(slug)
            continue
        review = read(review_path)
        coverage['reviews'] += 1
        inconsistent = population.consistency(review, config)
        for outcome in review.get('outcomes', []):
            name = f"{slug}::{outcome['name']}"
            spec = next((s for s, _ in specs if s['name'] == outcome['name']), {})
            m = metrics['outcomes_with_population_rule_inconsistencies']
            m['N'] += 1
            hits = [p for p in inconsistent if p['outcome'] == outcome['name']]
            if hits:
                m['items'].append({'outcome': name, 'problems': hits})
            rows = outcome.get('trials', [])
            if rows:
                m = metrics['pools_mixing_patients_and_events']
                m['N'] += 1
                problems = timepoint.pool_problems(rows)
                if any(p['code'] == 'UNIT_MIX_POOLED' for p in problems):
                    m['items'].append({'outcome': name, 'problems': problems})
                if any(p['code'] == 'COUNT_UNIT_UNKNOWN' for p in problems):
                    coverage['pools_with_unknown_count_unit'].append(name)
            for row in rows + outcome.get('declared_absent_trials', []):
                m = metrics['rows_flipped_by_origin_normalisation']
                m['N'] += 1
                span = timepoint.row_span(row)
                origin = ''
                pmid = re.fullmatch(r'PMID\s+(\d+)', str(row.get('id', '')))
                if pmid:
                    ft = root / 'cache' / slug / f'ft_{pmid.group(1)}.txt'
                    if ft not in origins_by_path:
                        origins_by_path[ft] = (' '.join(timepoint.origin_spans(ft.read_text(encoding='utf-8')))
                                               if ft.exists() else '')
                    origin = origins_by_path[ft]
                before = timepoint.parse(span)
                after = timepoint.parse(span, origin)
                if after.origin != 'UNSTATED':
                    coverage['rows_with_explicit_origin'] += 1
                if after.elapsed_days is None:
                    coverage['rows_with_unresolved_timepoint'] += 1
                old = timepoint.compare(spec.get('timepoint'), before)
                new = timepoint.compare(spec.get('timepoint'), after)
                if old != new:
                    m['items'].append({'row': f"{name}::{row.get('id')}", 'before': old,
                                       'after': new, 'origin_span': origin})
    for m in metrics.values():
        m['n'] = len(m['items'])
        m['n_of_N'] = f"{m['n']} of {m['N']}"
    return {'rules': metrics, 'coverage': coverage}


if __name__ == '__main__':
    print(json.dumps(census(), indent=2, ensure_ascii=True))
