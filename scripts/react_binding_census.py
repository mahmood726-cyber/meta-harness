"""Read-only census across every topic; JSON output, no persisted review edits."""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import recovery_map
from harness.recovery_binding import bind, acronym
from harness.trial_family import load_registry
from scripts.make_react_excerpt import parse, HELD


def metric(items, total):
    return {'n': len(items), 'N': total, 'n_of_N': f'{len(items)} of {total}', 'items': items}


def census():
    evidence = parse((ROOT / HELD).read_bytes())
    maps = recovery_map.load_map(ROOT)
    topics = sorted(p.stem for p in (ROOT / 'topics').glob('*.json'))
    bindings, changes, comparisons, missing, review_total, proposal_total = [], [], [], [], 0, 0
    for slug in topics:
        # Read every topic, even when there is no map to bind.
        json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf-8'))
        if slug not in maps:
            continue
        block = copy.deepcopy(maps[slug])
        registry = load_registry(ROOT, slug)
        for e in block['entries']:
            ids = [n for n, v in registry.items() if any(acronym(s.get('acronym')) == acronym(e['trial'])
                   for s in v.get('raw', {}).get('studies', []))]
            if len(ids) == 1:
                e['nct'] = ids[0]
        bound = bind(block, evidence)
        bindings.extend(dict(slug=slug, **b) for b in bound)
        review = json.loads((ROOT / 'docs/reviews' / slug / 'review.json').read_text(encoding='utf-8'))
        for outcome in review.get('outcomes', []):
            for kind in ('trials', 'declared_absent_trials'):
                for row in outcome.get(kind, []):
                    review_total += 1
                    matches = [b for e, b in zip(block['entries'], bound) if
                               (e.get('pmid') and e['pmid'] in re.findall(r'\b\d+\b', str(row.get('id', ''))))
                               or acronym(row.get('label')) == acronym(e['trial'])]
                    if len(matches) != 1 or kind == 'trials' or not re.search(r'28[- ]day.*mortality', outcome['name'], re.I):
                        continue
                    b = matches[0]
                    before = row.get('result_status', {}).get('state', row.get('state'))
                    if before != b['state']:
                        changes.append({'trial': b['trial'], 'id': row['id'], 'outcome': outcome['name'],
                                        'before': before, 'after': b['state'], 'binding': b['binding']})
        proposal = json.loads((ROOT / 'evidence/g1_proposals' / (slug + '.json')).read_text(encoding='utf-8'))
        proposal_total += len(proposal['trials'])
        for e, b in zip(block['entries'], bound):
            candidates = [r for r in proposal['trials'] if
                          (b['nct'] and r.get('nct') == b['nct']) or acronym(r.get('trial', r.get('label'))) == acronym(e['trial'])]
            if len(candidates) == 1 and all(candidates[0].get(k) == e[k] for k in recovery_map.COUNT_KEYS):
                comparisons.append({'trial': e['trial'], 'denominator': b['denominator'], 'numerator': b['numerator']})
            else:
                missing.append({'trial': e['trial'], 'reason': 'NO_UNAMBIGUOUS_COMPARATOR_COUNT_MATCH'})
    return {'topics_examined': len(topics), 'topics_with_map': metric([s for s in topics if s in maps], len(topics)),
            'denominator': {state: metric([b['trial'] for b in bindings if b['denominator'] == state], len(bindings))
                            for state in ('BOUND', 'CONFLICT', 'RELAYED')},
            'numerators_relayed': metric([b['trial'] for b in bindings if b['numerator'] == 'RELAYED'], len(bindings)),
            'review_rows_changed': metric(changes, review_total),
            'g1_count_matches': metric(comparisons, proposal_total), 'g1_missing_by_map_entry': missing,
            'source_population': evidence['population'], 'held_sha256': evidence['sha256'],
            'death_pairs_extracted': len(evidence['deaths']),
            'table_trials_with_text_deaths': metric([d['trial'] for d in evidence['deaths']], len(evidence['rows']))}


if __name__ == '__main__':
    print(json.dumps(census(), indent=2, ensure_ascii=False))
