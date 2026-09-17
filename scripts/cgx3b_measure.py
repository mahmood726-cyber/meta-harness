"""Offline lane census; intentionally keeps all remaining prose debt visible."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import claimgraph, manuscript, page


def measure(review):
    graph = claimgraph.review_graph(review)
    return {name: claimgraph.scan_rendered(rendered, graph) for name, rendered in (
        ('manuscript', manuscript.render(review)),
        ('riskofbias', page._riskofbias(review, False)),
    )}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plant', action='store_true')
    parser.add_argument('--all', action='store_true')
    args = parser.parse_args()
    paths = sorted((ROOT / 'docs/reviews').glob('*/review.json')) if args.all else [
        ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json']
    results = {}
    for path in paths:
        review = json.loads(path.read_text(encoding='utf-8'))
        results[review['slug']] = measure(review)
        for name, scan in results[review['slug']].items():
            print(f"{review['slug']} {name}: {scan['with_object']} registered of {scan['rendered_units']}")
        if args.plant:
            plant = '<p>The pooled hazard ratio was 7.77.</p>'
            scan = claimgraph.scan_rendered(manuscript.render(review) + plant,
                                            claimgraph.review_graph(review))
            violations = [v for v in scan['violations'] if v['detail'] == 'The pooled hazard ratio was 7.77.']
            results[review['slug']]['plant'] = violations
            print(json.dumps(violations, ensure_ascii=True, indent=2))
            assert violations and violations[0]['code'] == 'SENTENCE_WITHOUT_OBJECT'
    args.output.write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
