"""Offline CGX coverage/debt census. Does not rebuild or promote pages."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import claimgraph, page, propositions


def compact_scan(scan, full=False):
    violations = scan['violations']
    return {k: v for k, v in scan.items() if k != 'violations'} | {
        'violation_counts': dict(Counter(v['code'] for v in violations)),
        'violation_examples': violations if full else violations[:10],
        'examples_of_violations': len(violations),
    }


def sweep(root=ROOT, slug=None):
    root = Path(root)
    pages = []
    cache_counts = Counter()
    cache_rows = []
    for path in sorted((root / 'cache').glob('*/verified_effects.json')):
        if slug and path.parent.name != slug:
            continue
        rows = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(rows, dict):
            raise ValueError(f'Expected row mapping: {path}')
        for key, value in sorted(rows.items()):
            for index, row in enumerate(value if isinstance(value, list) else [value]):
                if not isinstance(row, dict):
                    raise ValueError(f'Expected object row: {path}:{key}:{index}')
                status = claimgraph.verify_fact(row, root)
                cache_counts[status['class']] += 1
                cache_rows.append({'slug': path.parent.name, 'row': key, 'row_index': index,
                                   'class': status['class'], 'reason': status.get('reason'),
                                   'rendered': claimgraph.fact_render(dict(row, id=key), root)})
    for path in sorted((root / 'docs' / 'reviews').glob('*/review.json')):
        if slug and path.parent.name != slug:
            continue
        review = json.loads(path.read_text(encoding='utf-8'))
        graph = claimgraph.review_graph(review, root)
        served = claimgraph.scan_rendered((path.parent / 'index.html').read_text(encoding='utf-8'), graph)
        fresh = claimgraph.scan_rendered(page.render_page(review), graph)
        contradictions = claimgraph.certainty_violations(review)
        legacy = claimgraph.check(review) + claimgraph.legacy_scope_violations(
            review, (path.parent / 'index.html').read_text(encoding='utf-8'))
        prop_report = propositions.check_document(review)
        typed_violations = graph.check()
        classes = Counter(obj['class'] for obj in graph.objects.values())
        judgements = Counter(obj.get('adjudication', 'OWED') for obj in graph.objects.values() if obj['class'] == 'JUDGEMENT')
        pages.append({'slug': review['slug'], 'served': compact_scan(served, full=bool(slug)), 'fresh_renderer': compact_scan(fresh, full=bool(slug)),
                      'propositions_by_class': dict(classes),
                      'contradictions_caught': len(contradictions),
                      'of_propositions': len(graph.objects),
                      'contradictions_by_class': dict(Counter(v['kind'] for v in contradictions)),
                      'contradiction_scope': 'GRADE arithmetic over the migrated typed registry; legacy predicates reported separately; coverage is not universal',
                      'contradictions': contradictions,
                      'legacy_predicate_violations': legacy,
                      'typed_object_violations': typed_violations,
                      'existing_proposition_audit': prop_report,
                      'judgements': {k: judgements[k] for k in ('RULE', 'MODEL_SPAN_VERIFIED', 'HUMAN', 'OWED')},
                      'interpretation_objects': classes['INTERPRETATION'],
                      'interpretation_scope_complete': False})
    return {'schema': 'claim-scope-sweep/v1', 'network_used': False,
            'scope_complete': False,
            'count_contract': 'Conservative visible prose/table text runs, including labels; not a linguistic sentence census. Unmigrated text is refused, never silently classified.',
            'cache_effects': {'unverified': cache_counts['UNVERIFIED_FACT'],
                              'of_rows': sum(cache_counts.values()),
                              'by_class': dict(cache_counts), 'rows': cache_rows},
            'pages': pages}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--slug')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = sweep(slug=args.slug)
    target = args.output or ROOT / 'docs' / 'claim_scope_sweep.json'
    target.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    counts = result['cache_effects']
    print(f"UNVERIFIED_FACT: {counts['unverified']} of {counts['of_rows']} verified_effects rows")
    print(f"Pages scanned: {len(result['pages'])}; scope_complete=false")
