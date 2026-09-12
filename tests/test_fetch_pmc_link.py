from harness.fetch import _select_pmc_link


# Linkset shapes below are the exact structures NCBI elink (dbfrom=pubmed, db=pmc) returned
# on 2026-09-12 for the PMIDs named in each test.

def test_direct_pubmed_pmc_link_selected_over_citing_refs():
    # PMID 25176939 (CONFIRM-HF): has BOTH the own-article link and a citing-refs link.
    # The own-article PMC id (4359359) must win regardless of ordering.
    linksetdbs = [
        {"linkname": "pubmed_pmc", "dbto": "pmc", "links": ["4359359"]},
        {"linkname": "pubmed_pmc_refs", "dbto": "pmc", "links": ["13557134"]},
    ]
    assert _select_pmc_link(linksetdbs) == "4359359"


def test_citing_refs_never_returned_as_the_articles_fulltext():
    # PMID 33197395 (AFFIRM-AHF) and 11451717 (Nilsen 2001): NOT in PMC, so elink returns
    # ONLY pubmed_pmc_refs (articles that CITE the target). Must fail closed to None so the
    # pipeline falls back to the abstract, NEVER serving a citing paper's full text.
    linksetdbs = [
        {"linkname": "pubmed_pmc_refs", "dbto": "pmc", "links": ["13557134", "9999999"]},
    ]
    assert _select_pmc_link(linksetdbs) is None


def test_refs_first_ordering_does_not_leak_when_direct_link_present():
    # Ordering trap: even if the citing-refs linkset appears FIRST, the direct link must win.
    linksetdbs = [
        {"linkname": "pubmed_pmc_refs", "dbto": "pmc", "links": ["13489779"]},
        {"linkname": "pubmed_pmc", "dbto": "pmc", "links": ["6098635"]},
    ]
    assert _select_pmc_link(linksetdbs) == "6098635"


def test_empty_linksetdbs_returns_none():
    assert _select_pmc_link([]) is None
