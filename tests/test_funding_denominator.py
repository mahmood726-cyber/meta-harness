"""The visible funding denominator must distinguish all outcomes from primary."""
from test_screen_ascertainment_state import served_pair, visible_text


def test_served_funding_denominator_names_both_pools():
    review, page = served_pair()
    outcomes = review["outcomes"]
    union = {str(t["id"]).removeprefix("PMID ").strip()
             for o in outcomes for t in o.get("trials", [])}
    primary = next(o for o in outcomes if o.get("primary"))
    k = primary["result"]["k"]
    text = visible_text(page)
    expected = f"{len(union)} trials pooled across all outcomes; {k} in the primary pool"
    assert expected in text, f"served funding sentence omits scope: expected {expected!r}"


def test_scope_counts_union_once_and_ignores_stale_funding():
    from harness.funding import denominator_sentence, pooled_funding
    review = {"outcomes": [
        {"primary": True, "trials": [{"id": "PMID 1"}]},
        {"trials": [{"id": "1"}, {"id": "PMID 2"}]},
    ], "funding": [{"id": "PMID 1", "type": "industry"},
                   {"id": "PMID 3", "type": "industry"}]}
    assert denominator_sentence(review) == "2 trials pooled across all outcomes; 1 in the primary pool"
    assert pooled_funding(review) == [{"id": "PMID 1", "type": "industry"},
                                      {"id": "PMID 2", "status": "unknown"}]
