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


def test_the_adjudicator_is_verified_against_its_own_items_sources(monkeypatch):
    # 7 Oct: panel() verified every adjudicator claim against the sources of the LAST item of an earlier loop (a stale
    # variable), so 129 adjudicated domain quotes failed as SOURCE_NOT_SHOWN and the disputes stayed UNRESOLVED
    items = [{"item_id": "t1", "slug": "s", "src": "pubmed:1"}, {"item_id": "t2", "slug": "s", "src": "pubmed:2"}]
    texts = {"pubmed:1": "randomly assigned by a central computer system", "pubmed:2": "an open-label design"}

    def claim(d1, src, q):
        return _rob(D1_randomisation={"judgement": d1, "source": src, "quote": q})
    recs = {"A1": claim("low", "pubmed:1", "randomly assigned"), "B1": claim("some_concerns", "pubmed:1", "central computer"),
            "ADJ1": claim("low", "pubmed:1", "central computer system"),
            "A2": claim("high", "pubmed:2", "open-label"), "B2": claim("high", "pubmed:2", "open-label design")}
    pf = lambda it, r="A": ((r + it["item_id"][-1]).encode(), [])  # noqa: E731
    af = lambda it, ca, cb, dis: (("ADJ" + it["item_id"][-1]).encode(), [])  # noqa: E731
    monkeypatch.setattr(G, "_index", lambda: {G._sha(k.encode()): k for k in recs})
    monkeypatch.setattr(G, "_load", lambda name: (None, recs[name]))
    rows = G.panel("rob", items, pf, af, lambda it: {it["src"]: texts[it["src"]]}, 1, [], False)
    assert rows[0]["final"]["D1_randomisation"] == "low", rows[0]["adjudicator"]["v"]


def test_v2_a_disputed_domain_needs_both_adjudicators_to_agree(monkeypatch):
    # memo 5 option b (approved 8 Oct): two adjudicators from different model families; disagreement stays UNRESOLVED
    monkeypatch.setattr(G, "VERSION", 2)
    items = [{"item_id": "t1", "slug": "s", "src": "pubmed:1"}]
    text = {"pubmed:1": "randomly assigned by a central computer system"}

    def claim(d1, q):
        return _rob(D1_randomisation={"judgement": d1, "source": "pubmed:1", "quote": q})
    recs = {"A1": claim("low", "randomly assigned"), "B1": claim("some_concerns", "central computer"),
            "ADJUDICATOR SEAT 1 of 2.\nADJ1": claim("low", "central computer system"),
            "ADJUDICATOR SEAT 2 of 2.\nADJ1": claim("some_concerns", "randomly assigned")}
    pf = lambda it, r="A": ((r + "1").encode(), [])  # noqa: E731
    af = lambda it, ca, cb, dis: (b"ADJ1", [])  # noqa: E731
    monkeypatch.setattr(G, "_index", lambda: {G._sha(k.encode()): k for k in recs})
    monkeypatch.setattr(G, "_load", lambda name: (None, recs[name]))
    rows = G.panel("rob", items, pf, af, lambda it: text, 1, [], False)
    assert rows[0]["final"]["D1_randomisation"] == "UNRESOLVED"
    recs["ADJUDICATOR SEAT 2 of 2.\nADJ1"] = claim("low", "randomly assigned")
    rows = G.panel("rob", items, pf, af, lambda it: text, 1, [], False)
    assert rows[0]["final"]["D1_randomisation"] == "low"
