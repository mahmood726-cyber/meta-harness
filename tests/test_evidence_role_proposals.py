"""A number's ROLE, where the regex cannot decide it (exposure vs outcome cues both present, or none), may come from a RECORDED,
replayable model proposal (registry/model_proposals/evidence_role.json, written by reproducible_ai) -- never a live call, and never
silently: the proposal must pass the same deterministic cue check, and the identity names its basis and record id."""
import pytest

from harness import evidence_identity as ei

# a real exposure cue ("received any volume of unassigned") AND a real outcome cue ("died") in one span: the regex cannot decide
BOTH = "Of the patients who received any volume of unassigned fluid, 60 died in the balanced group and 70 died in the saline group."


def test_conflicting_cues_are_undecided_by_regex():
    assert ei.lexical_role(BOTH) == "UNDECIDED"
    assert ei.resolve_role(BOTH, proposals={}) == ("UNDECIDED", "REGEX", None)


def test_a_supported_recorded_proposal_decides_and_says_so():
    quote = "60 died in the balanced group and 70 died in the saline group"
    props = {ei.span_key(BOTH): {"role": "OUTCOME_COUNT", "quote": quote, "record_id": "mc-test-1"}}
    assert ei.resolve_role(BOTH, proposals=props) == ("OUTCOME_COUNT", "RECORDED_PROPOSAL", "mc-test-1")


@pytest.mark.parametrize("prop", [
    {"role": "OUTCOME_COUNT", "record_id": "mc-2"},                                                  # no quote at all
    {"role": "OUTCOME_COUNT", "quote": "70 patients died of sepsis", "record_id": "mc-2"},           # quote not in the span
    {"role": "OUTCOME_COUNT", "quote": "received any volume of unassigned fluid, 60 died", "record_id": "mc-2"},  # exposure in quote
    {"role": "EFFECT_ESTIMATE", "quote": "60 died in the balanced group", "record_id": "mc-2"},       # no ratio + interval quoted
])
def test_a_proposal_the_text_does_not_support_is_refused(prop):
    role, basis, rid = ei.resolve_role(BOTH, proposals={ei.span_key(BOTH): prop})
    assert (role, basis, rid) == ("UNDECIDED", "RECORDED_PROPOSAL_REFUSED", "mc-2")


def test_a_span_the_regex_decides_never_consults_a_proposal():
    span = "A total of 426 patients received any volume of unassigned crystalloid in the balanced group and 343 in the saline group."
    prop = {"role": "OUTCOME_COUNT", "quote": "426 patients", "record_id": "x"}
    assert ei.resolve_role(span, proposals={ei.span_key(span): prop}) == ("EXPOSURE_COUNT", "REGEX", None)


def test_the_harness_reads_proposals_as_data_and_imports_no_model_client():
    src = (ei.ROOT / "harness" / "evidence_identity.py").read_text(encoding="utf-8")
    assert "reproducible_ai" not in src.split('"""', 2)[2] and "subprocess" not in src
