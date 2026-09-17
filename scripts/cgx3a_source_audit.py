"""Offline second-pass audit of the source identifiers, timestamps and statistics."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import claimgraph, page_claims


def audit():
    review = json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    cache = json.loads((ROOT / 'cache/glp1-ra-mace-t2d/records.json').read_text(encoding='utf-8'))
    records = {str(r['id']): r for r in cache['records']}
    rows = []
    for trial in review['outcomes'][0]['trials']:
        key = claimgraph.trial_key(trial)
        source = records.get(key)
        status = claimgraph.verify_fact(trial)
        evidence = claimgraph._fact_evidence(trial)
        rows.append({'id': trial['id'], 'source_record_found': source is not None,
                     'source_title': source.get('title') if source else None,
                     'source_nct': source.get('nct') if source else None,
                     'source_year': source.get('year') if source else None,
                     'document_path': evidence.get('document_path'),
                     'retrieved_utc': evidence.get('retrieved_utc'),
                     'fact_verification': status})
    graph = claimgraph.review_graph(review)
    pool_id = page_claims.pool_object(review['outcomes'][0], graph)
    return {'network_used': False, 'rows': rows,
            'all_source_ids_found': all(r['source_record_found'] for r in rows),
            'all_facts_verified': all(r['fact_verification']['verified'] for r in rows),
            'typed_object_violations': graph.check(),
            'primary_recomputed': graph.recompute(pool_id),
            'certainty': claimgraph.certainty_object(review['grade']),
            'date_note': 'Retrieval timestamps are validated evidence metadata, not inferred publication or trial dates. No identifiers or source dates were edited.'}


if __name__ == '__main__':
    result = audit()
    (ROOT / 'LANE-CGX3A-SOURCE-AUDIT.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print({k: result[k] for k in ('all_source_ids_found', 'all_facts_verified', 'typed_object_violations', 'primary_recomputed')})
    if not result['all_source_ids_found'] or not result['all_facts_verified'] or result['typed_object_violations']:
        raise SystemExit(1)
