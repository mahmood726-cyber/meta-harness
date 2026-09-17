"""Offline, section-bounded census and adversarial plant for lane CGX3C."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bs4 import BeautifulSoup
from harness import claimgraph


def fragments(rendered):
    soup = BeautifulSoup(rendered, 'html.parser')
    selected = {name: str(soup.select_one('#tab-' + name) or '')
                for name in ('search', 'screening', 'comparator', 'harms')}
    selected['limitations'] = str(soup.select_one('ul.limits') or '')
    heading = next((h for h in soup.select('#tab-reproduction h4')
                    if h.get_text() == 'Parity with the published comparator'), None)
    selected['parity'] = str(heading.find_next_sibling()) if heading else ''
    return selected


def census(rendered, review):
    graph = claimgraph.review_graph(review)
    return {name: claimgraph.scan_rendered(fragment, graph)
            for name, fragment in fragments(rendered).items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--plant', action='store_true')
    args = parser.parse_args()
    folder = ROOT / 'docs/reviews/glp1-ra-mace-t2d'
    review = json.loads((folder / 'review.json').read_text(encoding='utf-8'))
    rendered = (folder / 'index.html').read_text(encoding='utf-8')
    if args.plant:
        rendered = rendered.replace("<ul class='limits'>", "<ul class='limits'><li>There were 987654 screened records.</li>", 1)
    result = census(rendered, review)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for name, scan in result.items():
        print(f"{name}: {scan['with_object']} registered of {scan['rendered_units']}; {scan['structural_count']} structural")
    if args.plant:
        plant = [v for v in result['limitations']['violations'] if '987654' in v['detail']]
        assert plant and plant[0]['code'] == 'SENTENCE_WITHOUT_OBJECT'
        print('FAIL (expected plant): ' + json.dumps(plant[0], ensure_ascii=True))
        sys.exit(1)
