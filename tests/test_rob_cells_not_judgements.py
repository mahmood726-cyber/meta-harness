"""Mahmood's review of the served glp1 page (edaf5f6b, 18 Sep 2026), item 2 (MAJOR): the B-prime amendment withdrew
RoB 2 judgements -- the page must render "machine signal consistent with low risk; formal RoB 2 not assessed" and
never a RoB 2 judgement word alone -- yet the table still printed D1/D2/D4/D5 as bare `low` and Overall as
`low (on assessed domains; ...)`. Suppressing the sensitivity re-pool (landing E) was necessary, not sufficient.

Requirement: while the rob2 object's output family is the registry machine signal (not a formal RoB 2 assessment),
every domain cell renders the qualified signal and the Overall cell renders FORMAL RoB 2 NOT ASSESSED, derived from the
object's `output_family`; a formal assessment object (output_family 'rob2-formal') would render its judgements.
Plant: on 2a5e0ee9 the glp1 table carries `<td ...>low</td>` cells and the 'low (on assessed domains' overall.
"""
import json
import pathlib
import re

from harness import page, rob2

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUALIFIED_LOW = "machine signal consistent with low risk — formal RoB 2 not assessed"
OVERALL = "FORMAL RoB 2 NOT ASSESSED"


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _rob_table(html):
    i = html.find("<th>Overall</th>")
    assert i > 0
    return html[i: html.find("</table>", i)]


def test_glp1_rob_cells_render_machine_signal_not_judgement():
    review = _review("glp1-ra-mace-t2d")
    assert review["rob2"]["output_family"] == rob2.OUTPUT_FAMILY  # the machine-signal family
    table = _rob_table(page.render_page(review))
    # verdict-position text = the first text node of every cell (the rendering binds signal and verdict to one object)
    cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)(?:<br>|</td>)", table, re.S)]
    assert "low" not in cells, "a bare RoB 2 judgement word rendered as a cell"
    assert not any(c.startswith("low (on assessed domains") for c in cells)
    assert "formal RoB 2 not assessed" in cells
    assert any(c.startswith(OVERALL) for c in cells)


def test_cell_text_is_derived_from_output_family():
    assert page.rob_cell_text("low", rob2.OUTPUT_FAMILY) == QUALIFIED_LOW
    assert page.rob_cell_text("not assessed", rob2.OUTPUT_FAMILY) == "not assessed"
    assert page.rob_cell_text("some concerns", rob2.OUTPUT_FAMILY).startswith("machine signal: some concerns")
    assert page.rob_overall_text("low (on assessed domains; some domains require human judgement)", rob2.OUTPUT_FAMILY).startswith(OVERALL)
    # a formal RoB 2 object (none exists yet) would render its judgement as such
    assert page.rob_cell_text("low", "rob2-formal") == "low"
    assert page.rob_overall_text("low", "rob2-formal") == "low"


def test_every_page_with_machine_signal_rob_renders_no_bare_judgement():
    bare = []
    for path in sorted((ROOT / "docs/reviews").glob("*/review.json")):
        review = json.loads(path.read_text(encoding="utf-8"))
        rb = review.get("rob2") or {}
        if not rb.get("trials") or rb.get("output_family") != rob2.OUTPUT_FAMILY:
            continue
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<td[^>]*>(.*?)(?:<br>|</td>)", _rob_table(page.render_page(review)), re.S)]
        if any(c in ("low", "some concerns", "high") or c.startswith("low (on assessed") for c in cells):
            bare.append(path.parent.name)
    assert bare == []
