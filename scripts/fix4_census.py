"""Read-only FIX4 census over every topic; fresh builds only for ontology debt."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def metric(items, total):
    return dict(n=len(items), N=total, n_of_N=f'{len(items)} of {total}', items=items)


def census():
    from regex_layer.inventory import sites, planted
    from regex_layer.lanes import OWNED
    from regex_layer.specs import FIX4_SPECS
    from scripts.error_rate_blind_v2 import census as blind
    topics = sorted((ROOT / 'topics').glob('*.json'))
    missing, debt, affected = [], [], set()
    absent_total = 0
    for path in topics:
        # Read every topic, including those with no review; malformed input fails closed.
        json.loads(path.read_text(encoding='utf-8'))
        rp = ROOT / 'docs/reviews' / path.stem / 'review.json'
        if not rp.is_file():
            missing.append(path.stem)
            continue
        review = json.loads(rp.read_text(encoding='utf-8'))
        for outcome in review['outcomes']:
            for row in outcome.get('declared_absent_trials', []):
                absent_total += 1
                if not row.get('state'):
                    debt.append(f"{path.stem}::{outcome['name']}::{row['id']}")
                    affected.add(path.stem)
    # build_review_core returns objects; it does not write served artifacts.
    from harness.pipeline import build_review_core
    fresh_debt, fresh_n, failures = [], 0, []
    for slug in sorted(affected):
        cfg = json.loads((ROOT / 'topics' / (slug + '.json')).read_text(encoding='utf-8'))
        records = json.loads((ROOT / 'cache' / slug / 'records.json').read_text(encoding='utf-8'))
        try:
            review = build_review_core(slug, cfg, records, 'fix4-offline')
        except Exception as exc:
            failures.append(dict(topic=slug, error=f'{type(exc).__name__}: {exc}'))
            continue
        for outcome in review['outcomes']:
            for row in outcome.get('declared_absent_trials', []):
                fresh_n += 1
                if not row.get('state'):
                    fresh_debt.append(f"{slug}::{outcome['name']}::{row['id']}")
    inv = [s for s in sites() if s['file'] in OWNED]
    unplanted = [s['site'] for s in inv if s['site'] not in planted()]
    summary, rows, pop = blind(new_only=True)
    return dict(coverage=dict(topics=len(topics), reviews=len(topics)-len(missing),
                             fresh_build_topics=sorted(affected), fresh_build_failures=failures),
                rules=dict(saved_reviews_missing=metric(missing, len(topics)),
                           saved_absence_state_missing=metric(debt, absent_total),
                           fresh_absence_state_missing=metric(fresh_debt, fresh_n),
                           owned_regex_sites_without_plants=metric(unplanted, len(inv)),
                           uncensused_live_row_ids=metric([r['row_id'] for r in rows], len(pop))),
                new_regex_sites=sorted(FIX4_SPECS), blind_additions=summary, blind_rows=rows)


if __name__ == '__main__':
    result = census()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result['coverage']['fresh_build_failures']:
        raise SystemExit(1)
