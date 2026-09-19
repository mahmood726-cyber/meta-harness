"""Mahmood's review of the served glp1 page (98726cc1, 19 Sep 2026), increment 1 of the revision list: the Reproducibility
block states the prose protocol and executable config "agree on these checked dimensions: none", and PRISMA item 5
nevertheless claims "no protocol/config divergence on checked dimensions, so declared == enforced is backed". An empty
divergence list cannot establish compliance -- absence producing assurance, the deletion-invariant family.

Requirement: one derived state, `page.protocol_compliance_state(review)`: ESTABLISHED only when at least one dimension was
checked and none diverged; DISCLOSED_DIVERGENCE when divergences exist; NOT_ESTABLISHED when nothing was checked -- and
both render sites (Reproducibility, PRISMA item 5) print that state, never "declared == enforced is backed" over an empty
check. Plant: on bf2af50d the glp1 page carries "checked dimensions: none" and "declared == enforced is backed" (13 of 32
pages carry the same pair).
"""
import json
import pathlib
import re

from harness import page

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_glp1_compliance_not_established_when_no_dimension_checked():
    review = _review("glp1-ra-mace-t2d")
    pc = review.get("protocol_config") or {}
    assert not pc.get("divergences") and not pc.get("agreed_dimensions"), "fixture assumption: nothing checked on glp1"
    assert page.protocol_compliance_state(review)["state"] == "NOT_ESTABLISHED"
    text = _plain(page.render_page(review))
    assert "declared == enforced is backed" not in text
    assert "agree on these checked dimensions: none" not in text
    assert "NOT ESTABLISHED" in text


def test_states_are_derived_from_the_object():
    base = {"protocol_config": {"divergences": [], "agreed_dimensions": ["population", "design"]}}
    assert page.protocol_compliance_state(base)["state"] == "ESTABLISHED"
    div = {"protocol_config": {"divergences": [{"code": "X", "dimension": "population"}], "agreed_dimensions": ["design"]}}
    assert page.protocol_compliance_state(div)["state"] == "DISCLOSED_DIVERGENCE"
    empty = {"protocol_config": {"divergences": []}}
    assert page.protocol_compliance_state(empty)["state"] == "NOT_ESTABLISHED"
    assert page.protocol_compliance_state({})["state"] == "NOT_ESTABLISHED"


def test_no_page_claims_backed_compliance_over_an_empty_check():
    bad = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        if page.protocol_compliance_state(review)["state"] != "NOT_ESTABLISHED":
            continue
        text = _plain(page.render_page(review))
        if "declared == enforced is backed" in text or "checked dimensions: none" in text:
            bad.append(path.parent.name)
    assert bad == []
