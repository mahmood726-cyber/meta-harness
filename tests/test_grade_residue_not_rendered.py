"""Mahmood's review of the served glp1 page (edaf5f6b, 18 Sep 2026), item 5 (MODERATE): the page still said
"0 downgrade(s); starting arithmetic: high for randomized trials" and the manuscript "from 0 downgrade(s)" while certainty
is provisional -- residue that rebuilds the category B-prime forbids. Requirement: while `grade.certainty` is
provisional (unassessed domains), no downgrade count and no "starting arithmetic" phrase render anywhere; the domain
evidence rows stay. A fully assessed grade (no unassessed domains) renders its arithmetic. Plant: on 2a5e0ee9 the glp1
limitations block and manuscript carry both phrases.
"""
import json
import pathlib
import re

from harness import grade as grade_mod, limitations, manuscript, page

ROOT = pathlib.Path(__file__).resolve().parents[1]
RESIDUE = ("downgrade(s)", "starting arithmetic")


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_glp1_provisional_grade_renders_no_arithmetic_residue():
    review = _review("glp1-ra-mace-t2d")
    g = review["grade"]
    assert g.get("unassessed_domains"), "fixture assumption: glp1's certainty is provisional"
    assert grade_mod.render_certainty(g) == grade_mod.PROVISIONAL
    for surface in (_plain(page.render_page(review)), _plain(manuscript.render(review))):
        for phrase in RESIDUE:
            assert phrase not in surface, phrase
    # the domain evidence rows are kept
    assert "Domain" in _plain(page.render_page(review))


def test_fully_assessed_grade_keeps_its_arithmetic():
    review = _review("glp1-ra-mace-t2d")
    g = dict(review["grade"])
    g["unassessed_domains"] = []
    g["certainty"] = "moderate"
    g["certainty_state"] = "moderate"
    g["downgrades"] = 1
    text = _plain(limitations.grade_block(g)) if hasattr(limitations, "grade_block") else _plain(limitations._grade_block(g))
    assert "1 downgrade(s)" in text and "starting arithmetic" in text


def test_every_provisional_page_is_free_of_residue():
    residue_pages = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        g = review.get("grade") or {}
        if not g or not g.get("unassessed_domains"):
            continue
        surface = _plain(page.render_page(review)) + _plain(manuscript.render(review))
        if any(p in surface for p in RESIDUE):
            residue_pages.append(path.parent.name)
    assert residue_pages == []
