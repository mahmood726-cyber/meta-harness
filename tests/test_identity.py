"""Trial-identity resolution (NAMED_BUT_UNBOUND): union records sharing any identifier so a check
keyed on one identifier space resolves to the whole trial."""
import harness.identity as ID


def test_union_by_shared_nct():
    recs = [{"id": "111", "id_type": "pmid", "nct": "NCT9"},
            {"id": "NCT9", "id_type": "nct"},
            {"id": "222", "id_type": "pmid", "nct": "NCT8"}]
    ids = ID.build_identities(recs)
    # 111 and NCT9 collapse to one identity; 222 separate
    assert len(ids) == 2
    got = ID.resolve("111", ids)
    assert got and "NCT9" in got["nct"]
    # resolve by the OTHER identifier space reaches the same trial
    assert ID.resolve("NCT9", ids) is got


def test_resolve_by_acronym_and_doi():
    recs = [{"id": "333", "id_type": "pmid", "doi": "10.1/x", "acronym": "SoSTART"}]
    ids = ID.build_identities(recs)
    assert ID.resolve("sostart", ids) is not None
    assert ID.resolve("10.1/x", ids) is not None


def test_unlinked_pmid_stays_separate():
    # two PMIDs with no shared identifier are two trials (no false merge)
    recs = [{"id": "1", "id_type": "pmid", "doi": "10.1/a"},
            {"id": "2", "id_type": "pmid", "doi": "10.1/b"}]
    assert len(ID.build_identities(recs)) == 2
