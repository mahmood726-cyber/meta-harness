"""Read every topic/review; report actual cell changes without mutating them."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if __name__ == '__main__':
    sys.path.insert(0, str(ROOT))
from harness import jupiter_safety as js


def census(root=ROOT):
    root = Path(root)
    evidence = js.inspect(root)
    topics = sorted((root/'topics').glob('*.json'))
    all_cells, statins_cells, missing = [], [], []
    changed = {k: [] for k in ('denominators_bound', 'definition_bound', 'count_unit_assessed',
                               'patient_count_unit_confirmed', 'rate_unit_bound', 'measure_label_bound',
                               'rr_refused_unknown_counts', 'provenance_conflict')}
    transitions = []
    for path in topics:
        config = json.loads(path.read_text(encoding='utf-8'))
        slug = config.get('slug', path.stem)
        rp = root/'docs/reviews'/slug/'review.json'
        if not rp.exists():
            missing.append(slug)
            continue
        review = json.loads(rp.read_text(encoding='utf-8'))
        seen = set()
        for outcome in review.get('outcomes', []):
            for key in ('trials', 'declared_absent_trials'):
                for trial in outcome.get(key, []):
                    name = f'{slug}::{outcome.get("name")}::{trial.get("id")}'
                    if name in seen:
                        continue
                    seen.add(name)
                    all_cells.append(name)
                    if slug == js.SLUG:
                        statins_cells.append(name)
                        if trial.get('id') in (evidence['pmid'], 'PMID '+evidence['pmid']):
                            if js.provenance_review(config, evidence)['conflict']:
                                changed['provenance_conflict'].append(name)
                    # Invoke the adapter for every examined cell; unsupported
                    # cells are explicit refusals and never count as bindings.
                    try:
                        bound = js.bind(slug, outcome.get('name'), trial.get('id'), evidence)
                    except ValueError:
                        continue
                    before = trial.get('table_binding') or {}
                    old_arms = (trial.get('table_row') or {}).get('arms', [])
                    old_denom = [a.get('n_denominator') for a in old_arms]
                    if not old_denom or any(n is None for n in old_denom):
                        changed['denominators_bound'].append(name)
                    if trial.get('definition') != bound['definition']:
                        changed['definition_bound'].append(name)
                    if not trial.get('count_unit_basis'):
                        changed['count_unit_assessed'].append(name)
                    if bound['count_unit'] == 'PATIENTS':
                        changed['patient_count_unit_confirmed'].append(name)
                    for rule in ('rate_unit_bound', 'measure_label_bound', 'rr_refused_unknown_counts'):
                        changed[rule].append(name)
                    transitions.append(dict(cell=name, before=dict(table_binding=before,
                        denominators=old_denom, count_unit=trial.get('count_unit'), definition=trial.get('definition')),
                        after=dict(state=bound['state'], denominators=[a['denominator'] for a in bound['arms']],
                                   count_unit=bound['count_unit'], definition=bound['definition'],
                                   selected_measure=bound['selected']['measure'], rr_admitted=False)))
    def rules(N):
        return {rule: dict(n=len(names), N=N, n_of_N=f'{len(names)} of {N}', items=names)
                for rule, names in changed.items()}
    return dict(topics_examined=len(topics), reviews_missing=missing,
                denominator_definition='Unique outcome x report/trial cells in trials and declared_absent_trials; no invented cells for missing reviews',
                corpus_rules=rules(len(all_cells)), statins_rules=rules(len(statins_cells)),
                transitions=transitions)


if __name__ == '__main__':
    print(json.dumps(census(), ensure_ascii=False, indent=2))
