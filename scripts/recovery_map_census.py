"""Read-only corpus census; output is JSON, including named numerators."""
from __future__ import annotations
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import dose_arms, recovery_map


def census(root=ROOT):
    multi_n = rows_n = recovery_n = records_n = 0
    typed, products, changes, missing = [], [], [], []
    active, mi_flags, control_flags = [], [], []
    controls_n = 0
    topics = sorted((root / 'topics').glob('*.json'))
    for topic in topics:
        slug = topic.stem
        rp, vp = root / 'cache' / slug / 'records.json', root / 'docs/reviews' / slug / 'review.json'
        if not rp.exists():
            missing.append({'topic': slug, 'missing': 'records.json'})
            records = []
        else:
            records = json.loads(rp.read_text(encoding='utf-8'))['records']
        by_id = {str(r['id']): r for r in records}
        for r in records:
            records_n += 1
            if dose_arms.assess(r)["recovery"] == "ACTIVE":
                active.append({"topic": slug, "id": r["id"]})
            if dose_arms.is_multi_arm(r.get('abstract', '')):
                multi_n += 1
                arms = dose_arms.parse_arms(r.get('abstract', ''))
                if len(arms) >= 3:
                    typed.append({'topic': slug, 'id': r['id'], 'arms': arms})
        if not vp.exists():
            missing.append({'topic': slug, 'missing': 'review.json'})
            continue
        review = json.loads(vp.read_text(encoding='utf-8'))
        for o in review.get('outcomes', []):
            scoped = [r for r in o.get('trials', []) if all(r.get(k) for k in ('trial_id', 'outcome', 'control_id'))]
            controls_n += len(scoped)
            for problem in dose_arms.control_problems(scoped):
                control_flags.append(dict(topic=slug, outcome=o['name'], **problem))
            for r in o.get('trials', []):
                rows_n += 1
                if dose_arms.endpoint_problem(r.get('source', ''), o['name']):
                    mi_flags.append({'topic': slug, 'outcome': o['name'], 'id': r.get('id')})
                pid = str(r.get('id', '')).removeprefix('PMID ')
                source = by_id.get(pid)
                hits = dose_arms.km_products(r, source.get('abstract', '')) if source else []
                if hits:
                    products.append({'topic': slug, 'outcome': o['name'], 'id': r.get('id'), 'matches': hits})
        if slug in recovery_map.load_map(root):
            mortality = [o for o in review['outcomes'] if 'mortality' in o['name'].lower()]
            recovery_n += sum(len(o.get(k, [])) for o in mortality for k in ('trials', 'declared_absent_trials'))
            for item in recovery_map.attach(deepcopy(review), slug, root=root):
                if item['before'] != 'NO_ROW' and item['before'] != item['after']:
                    changes.append(dict(topic=slug, **item))
    def rule(items, n):
        return {'n': len(items), 'N': n, 'n_of_N': f'{len(items)} of {n}', 'items': items}
    return {'topics_examined': len(topics), 'records_examined': records_n,
            'multi_arm_with_typed_dose_arms': rule(typed, multi_n),
            'pooled_rows_matching_km_product': rule(products, rows_n),
            'tocilizumab_rows_changed': rule(changes, recovery_n),
            'active_full_table_recovery': rule(active, records_n),
            'mi_only_composite_candidates': rule(mi_flags, rows_n),
            'shared_control_flags': rule(control_flags, controls_n),
            'coverage_limits': ['Shared-control coverage requires explicit trial_id, outcome, control_id fields; zero examined is not a clean bill of health.','Multi-arm denominator: abstracts with allocation ratio of >=3 arms or explicit three/four/multi-arm wording.',
                                'KM numerator is arithmetic suspicion in held abstracts, not proof of derivation; registry-only rows lack abstract coverage.',
                                'Recovery denominator: all existing mortality trial and declared-absent rows; NO_ROW map entries excluded.'],
            'missing_files': missing}


if __name__ == '__main__':
    print(json.dumps(census(), indent=2, ensure_ascii=True))
