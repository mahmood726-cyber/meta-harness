"""Offline all-topic census for the REACTWIRE display contract."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import recovery_binding as rb, recovery_excerpt as rx, recovery_map


def census(root=ROOT):
    root = Path(root)
    topics = sorted(p.stem for p in (root / 'topics').glob('*.json'))
    applicable, entries, gate_rows, refused = [], [], [], []
    for topic in topics:
        if topic != 'tocilizumab-covid19-mortality':
            continue
        applicable.append(topic)
        try:
            artifact = rb.load_figure_binding(root, recovery_map.load_map(root)[topic], rx.load(root))
            entries.extend(artifact['entries'])
            gate_rows.extend(artifact['gate_rows'])
        except ValueError as exc:
            refused.append({'topic': topic, 'reason': str(exc)})

    def rule(items, total, denominator):
        return dict(n=len(items), N=total, n_of_N=f'{len(items)} of {total}', items=items, denominator=denominator)

    rules = {'display_scope': rule(applicable, len(topics), 'all topic files'),
             'artifact_refused': rule(refused, len(applicable), 'applicable topics')}
    from scripts.react_figure_proposal import verify_binding
    stale = []
    for topic in applicable:
        try:
            verify_binding(root)
        except (OSError, ValueError) as exc:
            stale.append({'topic': topic, 'reason': str(exc)})
    rules['stale_artifact_refused'] = rule(stale, len(applicable), 'applicable artifacts replayed offline')
    for state in ('BOUND_TO_HELD_FIGURE', 'CONFLICT', 'REFUSED'):
        rules[state.lower()] = rule([e['trial'] for e in entries if e['state'] == state], len(entries), 'recovery-map trials')
    rules['record_ids_missing'] = rule([e['trial'] for e in entries if not e.get('record_ids')], len(entries), 'recovery-map trials')
    rules['pool_refused'] = rule([e['trial'] for e in entries if e['poolable'] is False], len(entries), 'recovery-map trials')
    rules['own_paper_population_distinction'] = rule([e['trial'] for e in entries if e.get('own_paper')], len(entries), 'recovery-map trials')
    for state in ('REFUSED', 'UNVERIFIABLE'):
        rules['gate_' + state.lower()] = rule([r['row']['agent'] + '::' + r['row']['trial'] for r in gate_rows if r['status'] == state], len(gate_rows), 'figure rows')
    return dict(topics_examined=topics, rules=rules,
                note='Display/state only; outside-scope topics unchanged; no population adjudication or pool admission. Staleness replay runs offline in this census, never in the build.')


if __name__ == '__main__':
    print(json.dumps(census(), indent=2))
