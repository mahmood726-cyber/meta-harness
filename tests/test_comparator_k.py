"""The comparator-k proposal verifier (reproducible_ai.model_source.verify_comparator_k): the count comes from the
source's own words, never from the model; a control's known answer is compared, never imposed."""
from __future__ import annotations

from reproducible_ai.model_source import needs_individual_signature, reverify, verify_comparator_k

ABSTRACT = "We included eight randomised controlled trials (n = 4,120). Six trials reported mortality."


def test_a_stated_count_is_parsed_from_the_quote():
    v = verify_comparator_k({"state": "STATED", "quote": "We included eight randomised controlled trials",
                             "count_text": "eight"}, ABSTRACT)
    assert v["state"] == "VERIFIER_PASS" and v["k"] == 8


def test_a_quote_not_in_the_source_is_refused():
    v = verify_comparator_k({"state": "STATED", "quote": "We included nine randomised controlled trials",
                             "count_text": "nine"}, ABSTRACT)
    assert v["state"] == "VERIFIER_REFUSED" and any(p.startswith("SPAN_NOT_IN_SOURCE") for p in v["problems"])


def test_a_count_the_model_supplied_is_refused():
    # the count must be copied from the quote: a model-computed '8' next to a quote saying 'eight' is not the source's
    v = verify_comparator_k({"state": "STATED", "quote": "We included eight randomised controlled trials",
                             "count_text": "8"}, ABSTRACT)
    assert v["state"] == "VERIFIER_REFUSED" and any(p.startswith("COUNT_NOT_IN_QUOTE") for p in v["problems"])


def test_not_stated_or_ambiguous_carries_no_count():
    assert verify_comparator_k({"state": "NOT_STATED", "quote": None, "count_text": None}, ABSTRACT)["state"] == "VERIFIER_PASS"
    v = verify_comparator_k({"state": "AMBIGUOUS", "quote": "Six trials reported mortality", "count_text": "Six"}, ABSTRACT)
    assert v["state"] == "VERIFIER_REFUSED" and "COUNT_WITHOUT_STATED" in v["problems"]


def test_a_control_answer_is_compared_and_every_data_proposal_needs_its_own_signature():
    claim = {"state": "STATED", "quote": "We included eight randomised controlled trials", "count_text": "eight"}
    agree = reverify({"task": "comparator_k", "claim": claim, "context": {"prior": 8}}, ABSTRACT)
    differ = reverify({"task": "comparator_k", "claim": claim, "context": {"prior": 28}}, ABSTRACT)
    data = reverify({"task": "comparator_k", "claim": claim, "context": {"prior": None}}, ABSTRACT)
    assert agree["agreement"] == "PRIOR_MODEL_AGREE" and differ["agreement"].startswith("PRIOR_MODEL_DISAGREE")
    assert differ["k"] == 8                              # the known answer never overwrites what the source says
    assert needs_individual_signature(data) and needs_individual_signature(differ)


def test_a_compound_count_word_is_parsed():
    # plant #19: the CONTROLS caught it -- omega3 ('Twenty-eight', verified 28) and probiotics ('Forty-two', verified 42)
    # were refused COUNT_NOT_PARSEABLE although the model had quoted the right count
    text = "Twenty-eight randomized controlled trials were included. Forty two studies were screened."
    v = verify_comparator_k({"state": "STATED", "quote": "Twenty-eight randomized controlled trials",
                             "count_text": "Twenty-eight"}, text)
    assert v["state"] == "VERIFIER_PASS" and v["k"] == 28
    assert verify_comparator_k({"state": "STATED", "quote": "Forty two studies", "count_text": "Forty two"}, text)["k"] == 42
    assert verify_comparator_k({"state": "STATED", "quote": "Twenty-eight randomized", "count_text": "Twenty-eight randomized"},
                               text)["state"] == "VERIFIER_REFUSED"          # a token that is not a count is still refused
