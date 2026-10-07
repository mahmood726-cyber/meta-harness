"""D11 sign-off verifier (7 Oct): a reader's RoB 2 / GRADE judgement stands only when its quote is found in the very
source text it names -- the bytes that were shown -- and the overall is derived, never taken from a model."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_d11_rob_grade as G  # noqa: E402

SHOWN = {"pubmed:1": "Patients were randomly assigned by a central computer system to drug or placebo.",
         "ctgov:NCT00000001": "Masking: QUADRUPLE; masked roles: subject=t, outcomes assessor=t"}


def _rob(**over):
    d = {k: {"judgement": "cannot_tell", "quote": "", "source": ""} for k in G.DOMAINS}
    d.update(over)
    return {"domains": d, "rationale": ""}


def test_a_quote_found_in_the_named_source_verifies():
    v = G.verify("rob", _rob(D1_randomisation={"judgement": "low", "source": "pubmed:1",
                                              "quote": "randomly assigned by a central computer system"}), SHOWN)
    assert v["domains"]["D1_randomisation"] == "low" and not v["problems"]


def test_a_true_quote_attributed_to_the_wrong_source_does_not_verify():
    v = G.verify("rob", _rob(D1_randomisation={"judgement": "low", "source": "ctgov:NCT00000001",
                                              "quote": "randomly assigned by a central computer system"}), SHOWN)
    assert v["domains"]["D1_randomisation"] == "UNVERIFIED"


def test_a_source_that_was_not_shown_does_not_verify():
    v = G.verify("rob", _rob(D2_deviations={"judgement": "low", "source": "pmc-cc:1", "quote": "double-blind"}), SHOWN)
    assert v["domains"]["D2_deviations"] == "UNVERIFIED" and "SOURCE_NOT_SHOWN" in v["problems"][0]


def test_the_overall_is_derived_by_the_rob2_algorithm():
    low = {d: "low" for d in G.DOMAINS}
    assert G.rob_overall(low) == "low"
    assert G.rob_overall(dict(low, D3_missing_outcome_data="some_concerns")) == "some_concerns"
    assert G.rob_overall(dict(low, D5_selective_reporting="high", D3_missing_outcome_data="cannot_tell")) == "high"
    assert G.rob_overall(dict(low, D3_missing_outcome_data="cannot_tell")) == "not_determined"


def test_grade_certainty_is_derived_from_the_downgrades():
    z = {d: 0 for d in G.GDOMAINS}
    assert G.certainty(z) == "high"
    assert G.certainty(dict(z, imprecision=1)) == "moderate"
    assert G.certainty(dict(z, imprecision=2, risk_of_bias=1)) == "very_low"
    assert G.certainty(dict(z, imprecision="UNVERIFIED")) == "not_determined"


def test_kappa_counts_only_decided_pairs():
    k, n = G.kappa([("low", "low"), ("high", "high"), ("low", "cannot_tell")], ("low", "some_concerns", "high"))
    assert n == 2 and k == 1.0
