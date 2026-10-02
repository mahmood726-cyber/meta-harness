"""Offline display-binding census; every topic is examined."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from harness import table_binding as tb
from harness.trial_family import load_registry
from scripts.disperse2_figure_proposal import verify_binding


def census():
    verify_binding(ROOT)
    topics, rows, matched, missing, poolable, unavailable = [], [], [], [], [], []
    artifact = tb.load_disperse_binding()
    for path in sorted((ROOT / 'topics').glob('*.json')):
        slug = path.stem
        topics.append(slug)
        load_registry(ROOT, slug)
        review_path = ROOT / 'docs/reviews' / slug / 'review.json'
        if not review_path.is_file():
            unavailable.append(slug + ': review.json not held; review rows not examined')
            continue
        review = json.loads(review_path.read_text(encoding='utf-8'))
        for outcome in review['outcomes']:
            for row in outcome.get('trials', []) + outcome.get('declared_absent_trials', []):
                if artifact['pmid'] not in str(row.get('id', '')) or slug != artifact['topic']:
                    continue
                item = slug + '/' + outcome['name'] + '/' + str(row['id'])
                rows.append(item)
                binding = tb.disperse(outcome)
                (matched if binding['rows'] else missing).append(item)
                if binding['poolable'] is not False:
                    poolable.append(item)
    def rule(items, total):
        return dict(n=len(items), N=total, n_of_N=f'{len(items)} of {total}', items=items)
    return dict(topics_examined=topics, rules={
        'TABLE_TRANSCRIBED_GATED': rule(matched, len(rows)),
        'OUTCOME_TABLE_NOT_HELD': rule(missing, len(rows)),
        'POOLABLE_VIOLATION': rule(poolable, len(rows)),
        'STALE_BINDING': rule([], 1),
        'REVIEW_NOT_HELD': rule(unavailable, len(topics)),
        'TOPIC_DISPLAY_CHANGED': rule([artifact['topic']] if rows else [], len(topics))})

if __name__ == '__main__':
    print(json.dumps(census(), ensure_ascii=False, indent=2))
