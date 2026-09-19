"""Mahmood's adjudication (19 Sep 2026) of the RoB contradiction on the served glp1 page: "formal RoB 2 not assessed" x41
and "low (on assessed domains" x8 for the same trials -- one quantity rendered from two sources. Decision: the
not-assessed state is the true one; both renderings bind to ONE canonical object (rob2.canonical); the machine signals
stay visible, labelled as signals with their source; the verdict is stated separately; the bare judgement word never
stands in a verdict position because no verdict exists under the registry machine-signal family.

The gate (rob2.verify_rendered_verdicts, run by census before a page is written): a rendered RoB verdict that does not
resolve to an assessed judgement in the canonical object is REFUSED. Plant: against the served page (8c8874b4) the gate
reports 48 unresolved verdict cells -- the eight Overall cells quoting the aggregate and forty domain cells with no
binding -- i.e. the previous rendering passed silently because no gate existed.
"""
import json
import pathlib
import re
import subprocess

from harness import page, rob2

ROOT = pathlib.Path(__file__).resolve().parents[1]
SLUG = "glp1-ra-mace-t2d"
SERVED = "945e663ad945b58a99beeea4b8443a2cdce8795e"


def _review():
    return json.loads((ROOT / "docs/reviews" / SLUG / "review.json").read_text(encoding="utf-8"))


def test_PLANT_served_page_has_unresolved_verdict_cells():
    html = subprocess.run(["git", "show", f"{SERVED}:docs/reviews/{SLUG}/index.html"], cwd=ROOT,
                          capture_output=True, text=True, encoding="utf-8").stdout
    if not html:
        import pytest
        pytest.skip("served commit not available in this checkout")
    violations = rob2.verify_rendered_verdicts(html, _review()["rob2"])
    assert len(violations) >= 8, len(violations)
    assert all(v["code"] == "ROB_VERDICT_UNRESOLVED" for v in violations)


def test_rebuilt_page_resolves_every_verdict_and_keeps_the_signals():
    review = _review()
    assert review["rob2"].get("canonical"), "the review object carries the canonical RoB object"
    html = page.render_page(review)
    assert rob2.verify_rendered_verdicts(html, review["rob2"]) == []
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    assert "low (on assessed domains" not in text
    assert text.count("FORMAL RoB 2 NOT ASSESSED") == len(review["rob2"]["canonical"]["trials"])
    assert "machine signal: low" in text and "(from registry" in text  # the signals stay, labelled with their source


def test_gate_refuses_a_bare_judgement_in_a_verdict_position():
    review = _review()
    html = page.render_page(review)
    i = html.find("<th>Overall</th>")
    table = html[i: html.find("</table>", i)]
    mutated = table.replace("<td data-rob-verdict='NOT_ASSESSED'><strong class='rob-verdict'>FORMAL RoB 2 NOT ASSESSED</strong>",
                            "<td data-rob-verdict='NOT_ASSESSED'><strong>low (on assessed domains; some domains require human judgement)</strong>", 1)
    assert mutated != table
    violations = rob2.verify_rendered_verdicts(html.replace(table, mutated), review["rob2"])
    assert violations and violations[0]["code"] == "ROB_SIGNAL_IN_VERDICT_POSITION", violations[:2]
    stripped = re.sub(r" data-rob-verdict='[^']*'", "", table, count=1)
    violations = rob2.verify_rendered_verdicts(html.replace(table, stripped), review["rob2"])
    assert violations and violations[0]["code"] == "ROB_VERDICT_UNRESOLVED"


def test_canonical_object_is_derived_and_a_formal_family_would_carry_judgements():
    review = _review()
    canon = rob2.canonical(review["rob2"])
    assert canon["formal"] is False
    for trial in canon["trials"].values():
        assert trial["verdict"] == rob2.VERDICT_NOT_ASSESSED
        assert all(d["verdict"] == rob2.VERDICT_NOT_ASSESSED for d in trial["domains"].values())
    formal = rob2.canonical({"output_family": "rob2-formal", "trials": {"x": {"overall": "low", "domains": {"D1": {"level": "low", "basis": "adjudicated"}}}}})
    assert formal["trials"]["x"]["verdict"] == "low" and formal["trials"]["x"]["domains"]["D1"]["verdict"] == "low"
