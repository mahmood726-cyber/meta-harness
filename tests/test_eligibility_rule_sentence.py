"""Mahmood's review of the served glp1 page (edaf5f6b, 18 Sep 2026), item 3 (blocking generator defect): the manuscript
stated the eligibility rule as "population, intervention, comparator and design only" while the registered B-prime clause
makes prospective, systematic OUTCOME ASCERTAINMENT an eligibility axis and outcome RESULT AVAILABILITY explicitly not one.

Requirement: the rendered rule sentence derives from the registered protocol's eligibility clause (parsed from the
committed prose by harness.protocol_compiler.eligibility_clause), never from a literal. A topic whose clause declares the
ascertainment axis renders the B-prime statement; a topic whose registered rule is P/I/C/design keeps that statement,
conditioned on the parsed clause. Plant: on main 2a5e0ee9 the glp1 manuscript carries the served fragment.
"""
import json
import pathlib
import re

from harness import manuscript, protocol_compiler as pc

ROOT = pathlib.Path(__file__).resolve().parents[1]
SERVED_FRAGMENT = "Eligibility is by population, intervention, comparator and design only"
BPRIME_SENTENCE = "Outcome ascertainment is an eligibility axis; outcome result availability is not."


def _review(slug):
    return json.loads((ROOT / "docs/reviews" / slug / "review.json").read_text(encoding="utf-8"))


def _plain(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def test_glp1_clause_parses_with_ascertainment_axis():
    clause = pc.eligibility_clause(_review("glp1-ra-mace-t2d")["protocol"]["text"])
    assert clause is not None
    assert clause["label"] == "B-prime"
    assert clause["ascertainment_axis"] is True
    assert clause["result_availability_not_axis"] is True
    assert "prospectively specified and systematically ascertained" in clause["text"]


def test_glp1_manuscript_renders_bprime_rule_not_the_served_sentence():
    text = _plain(manuscript.render(_review("glp1-ra-mace-t2d")))
    assert SERVED_FRAGMENT not in text
    assert BPRIME_SENTENCE in text
    assert "prospectively specified and systematically ascertained" in text


def test_topic_without_ascertainment_clause_keeps_pico_design_rule():
    # a registered rule-A topic keeps the P/I/C/design statement, now conditioned on its parsed clause
    review = _review("sglt2-hfref-hosp-cvdeath")
    clause = pc.eligibility_clause(review["protocol"]["text"])
    assert clause is None or clause["ascertainment_axis"] is False
    text = _plain(manuscript.render(review))
    assert BPRIME_SENTENCE not in text
    assert "population, intervention, comparator and design" in text


def test_clause_parser_fails_closed_on_prose_without_a_clause():
    assert pc.eligibility_clause("no eligibility bullet here") is None
    fake = "- **Eligibility (B-prime).** trials in which the outcome was prospectively specified and systematically ascertained. Eligibility does **not** depend on the published availability of the result."
    clause = pc.eligibility_clause(fake)
    assert clause["ascertainment_axis"] and clause["result_availability_not_axis"]
    weak = "- **Eligibility (B-prime).** trials of anything."
    assert pc.eligibility_clause(weak)["ascertainment_axis"] is False
