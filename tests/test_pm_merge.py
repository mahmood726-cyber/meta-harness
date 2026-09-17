"""Cross-lane integration: preserve C's limitations inside A's overview."""
import json

from bs4 import BeautifulSoup

from harness import claimgraph, page, section_claims


def test_migrated_overview_keeps_limitations_and_all_boundary_objects():
    review = json.loads((claimgraph.ROOT / 'docs/reviews/glp1-ra-mace-t2d/review.json').read_text(encoding='utf-8'))
    rendered = page.render_overview(review)
    assert page._stated_limitations(review) in rendered
    soup = BeautifulSoup(rendered, 'html.parser')
    assert len(soup.select('ul.limits')) == 1
    for key in ('small-k', 'oa', 'screening'):
        expected = BeautifulSoup(section_claims.boundary(review, key), 'html.parser').span
        assert soup.select_one('ul.limits').find('span', attrs={'data-claim-id': expected['data-claim-id']}) == expected
    scan = claimgraph.scan_rendered(str(soup.select_one('ul.limits')), claimgraph.review_graph(review))
    assert scan['with_object_by_class']['INTERPRETATION'] == 3
    assert scan['violations']  # Existing unresolved prose must remain visible debt.
    assert 'ul class=' not in page.render_overview(review, neutral=True)
