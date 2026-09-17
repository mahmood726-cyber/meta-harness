"""Offline, renderer-bound CGX3A census; no prose whitelist."""
import json
import sys
import subprocess
import types
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import claimgraph, page


class OwnedSummary(HTMLParser):
    """Exclude the sibling typed-effects renderer by its semantic section boundary."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'section' and (self.depth or 'typed-effects' in dict(attrs).get('class', '').split()):
            self.depth += 1
        if not self.depth:
            self.parts.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if self.depth:
            if tag == 'section':
                self.depth -= 1
        else:
            self.parts.append('</' + tag + '>')

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)

    def handle_entityref(self, name):
        self.handle_data('&' + name + ';')

    def handle_charref(self, name):
        self.handle_data('&#' + name + ';')


def sections(review, renderer=page):
    # CGX3C owns the stated-limitations list even when it shares Overview.
    # Keep it in the whole-page and CGX3C censuses, outside CGX3A's boundary.
    from bs4 import BeautifulSoup
    overview = BeautifulSoup(renderer.render_overview(review), 'html.parser')
    for limits in overview.select('ul.limits'):
        limits.decompose()
    yield 'overview', str(overview)
    for i, outcome in enumerate(review.get('outcomes') or []):
        parser = OwnedSummary()
        parser.feed(renderer._outcome_block(outcome, show_inputs=False))
        yield f'outcome-{i}-summary', ''.join(parser.parts)
        # The pooled rows are provenance; absent rows are sibling membership.
        if outcome.get('trials'):
            yield f'provenance-{i}', renderer._trial_inputs(dict(outcome, declared_absent_trials=[]))
    yield 'strands', renderer.render_strands_section(review.get('strands') or {})


def census(review, renderer=page):
    graph = claimgraph.review_graph(review)
    return {name: claimgraph.scan_rendered(body, graph) for name, body in sections(review, renderer)}


if __name__ == '__main__':
    mode = sys.argv[1]
    review = json.loads((ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    renderer = page
    if mode == 'BASE-OWNED':
        renderer = types.ModuleType('harness.base_page_cgx3a')
        renderer.__package__ = 'harness'
        source = subprocess.check_output(['git', 'show', 'HEAD:harness/page.py'], cwd=ROOT).decode('utf-8')
        exec(compile(source, 'BASE:harness/page.py', 'exec'), renderer.__dict__)
    result = census(review, renderer)
    (ROOT / f'LANE-CGX3A-{mode}-SCOPE.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for name, scan in result.items():
        print(f"{name}: {scan['with_object']} registered of {scan['rendered_units']}; structural={scan['structural_count']}")
    if mode == 'BASE':
        plant = '<p>The pooled hazard ratio is 0.123456.</p>'
        scan = claimgraph.scan_rendered(page.render_overview(review) + plant, claimgraph.review_graph(review))
        failure = next(v for v in scan['violations'] if v['detail'] == 'The pooled hazard ratio is 0.123456.')
        output = 'BASE PLANT: FAIL (expected rejection)\n' + json.dumps(failure, indent=2) + '\n'
        (ROOT / 'LANE-CGX3A-BASE-PLANT.txt').write_text(output, encoding='utf-8')
        print(output)
