from harness.fetch import _select_nct


def test_abstract_nct_order_beats_pubmed_databank_order_for_multi_trial_papers():
    abstract = "Unique identifiers: NCT00680186 and NCT00291330."
    assert _select_nct(abstract, ["NCT00291330", "NCT00680186"]) == "NCT00680186"


def test_databank_nct_used_when_abstract_has_no_trial_id():
    assert _select_nct("No registry id in this abstract.", ["NCT12345678"]) == "NCT12345678"
