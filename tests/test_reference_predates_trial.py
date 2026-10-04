"""A paper published before a trial STARTED cannot report it (k_gap_table.resolve_unit): PACMAN-AMI (NCT03067844,
started 2017) lists ODYSSEY LONG TERM (2015) and ODYSSEY FH I/II (2015) among its RESULT references, so the tracker joined
it to LONG TERM's pool row. Corpus (offline, PubMed years + AACT start dates): 1 trial affected, 11 references dropped."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import k_gap_table as kt  # noqa: E402

IDX = {"study": {"NCT03067844": {"start_date": "2017-08-09"}, "NCTNODATE": {}}}
YEARS = {"25773378": 2015, "35368058": 2022, "26330422": 2015}


def test_a_reference_older_than_the_trial_is_not_its_report():
    assert kt.published_before_start("25773378", "NCT03067844", IDX, YEARS)
    assert not kt.published_before_start("35368058", "NCT03067844", IDX, YEARS)


def test_unknown_dates_never_drop_a_reference():
    assert not kt.published_before_start("99999999", "NCT03067844", IDX, YEARS)      # year unknown
    assert not kt.published_before_start("25773378", "NCTNODATE", IDX, YEARS)        # start unknown


def test_resolve_unit_drops_only_the_predating_references():
    kt._OFFLINE = True
    kt.YEARS.update(YEARS)
    idx = {"pmid_nct": {}, "acr_nct": {}, "acr_title_nct": {}, "agent_nct": {}, "study": IDX["study"],
           "nct_pmids": {"NCT03067844": ["25773378", "26330422", "35368058"]}}
    u = {"cited": [], "ncts": ["NCT03067844"], "author": None, "year": None, "acronyms": []}
    r = kt.resolve_unit(u, None, idx, None)
    assert r["pmids"] == ["35368058"] and any(b.startswith("nct_pmids_published_before_trial_start:2") for b in r["basis"])
