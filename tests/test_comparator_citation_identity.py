"""A comparator trial with no identity (pre-registry, acronym label) takes the PMID its comparator's OWN text cites
where it DEFINES the acronym (g1_tracker.resolve_by_comparator_citation). spironolactone-hfref-mortality's comparator
(40959489) writes 'RALES (The Effect of Spironolactone ...) (ref 1)' and 'EPHESUS (Eplerenone, a Selective Aldosterone
Blocker ...) (ref 14)'; its reference list gives 1 = PMID 10471456 (our pooled RALES) and 14 = 12668699."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402


def test_the_comparators_own_text_defines_rales_and_ephesus_with_citations():
    c = gt.comparator_acronym_citations("40959489")
    assert c["RALES"] == {"10471456"} and c["EPHESUS"] == {"12668699"} and c["EMPHASIS-HF"] == {"21073363"}


def test_unresolved_acronym_labels_resolve_and_resolved_ones_are_untouched():
    rows = [{"label": "RALES1999"}, {"label": "EPHESUS 2003 [14]"}, {"label": "EMPHASIS-HF2011", "pmids": ["x"]},
            {"label": "Aldo-DHF2013"}]
    gt.resolve_by_comparator_citation(rows, "40959489")
    assert rows[0]["pmids"] == ["10471456"] and rows[1]["pmids"] == ["12668699"]
    assert rows[0]["identity_basis"] == ["COMPARATOR_TEXT_DEFINES_ACRONYM_WITH_CITATION:RALES"]
    assert rows[2]["pmids"] == ["x"]                                  # an existing identity is never overwritten
    assert "pmids" not in rows[3]                                     # an acronym the text never defines stays open


def test_a_comparator_without_held_text_resolves_nothing():
    rows = [{"label": "RALES1999"}]
    gt.resolve_by_comparator_citation(rows, "no-such-comparator")
    assert "pmids" not in rows[0]
