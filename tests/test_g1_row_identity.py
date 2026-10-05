"""Row identity mapping (scripts/g1_row_identity.py): the plants that keep it from guessing."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_row_identity as ri  # noqa: E402

REFS = [{"label": "35", "surname": "Can", "year": "2006", "pmid": "16572062", "doi": None, "title": "Probiotics", "text": "Can M"},
        {"label": "36", "surname": "Gao", "year": "2010", "pmid": "20145608", "doi": None, "title": "x", "text": "Gao XW"},
        {"label": "40", "surname": "Zinman", "year": "2015", "pmid": "26378978", "doi": None,
         "title": "Empagliflozin, cardiovascular outcomes, and mortality in type 2 diabetes (EMPA-REG OUTCOME)", "text": "Zinman B"},
        {"label": "41", "surname": "Zinman", "year": "2016", "pmid": "1", "doi": None, "title": "y", "text": "Zinman B"}]


def test_a_citation_number_is_taken_only_when_its_author_is_in_the_label():
    ref, how = ri.match_reference("Can et al35", REFS)
    assert ref["pmid"] == "16572062" and how == "META_REFERENCE_NUMBER:35"
    ref, how = ri.match_reference("Gao et al35", REFS)            # number 35 is Can: the surname decides, not the number
    assert ref["pmid"] == "20145608" and how.startswith("META_REFERENCE_SURNAME")


def test_an_acronym_with_a_typographic_dash_matches_whole_and_ambiguity_is_never_guessed():
    ref, how = ri.match_reference("EMPA–REG", REFS)
    assert ref["pmid"] == "26378978" and how == "META_REFERENCE_TITLE_ACRONYM"
    assert ri.match_reference("Zinman", REFS) == (None, "AMBIGUOUS_REFERENCE:2")


def test_a_shared_topic_word_without_a_year_never_attaches_a_comparator_trial():
    tracker = [{"label": "Dexamethasone in Hospitalized Patients with Covid-19", "family": "PMID 32678530",
                "pmid": "32678530", "nct": None, "acronyms": set(), "words": set(ri.words("Dexamethasone in Hospitalized "
                "Patients with Covid-19")), "compact": ri.compact("Dexamethasone in Hospitalized Patients with Covid-19"),
                "year": None, "in_our_pool": True, "route": "PRIMARY"}]
    t, why = ri.attach({"row_label": "COVID STEROID", "pmid": None, "nct": None}, tracker)
    assert t is None and why == "NOT_A_COMPARATOR_TRIAL"
    t, why = ri.attach({"row_label": "x", "pmid": "32678530", "nct": None}, tracker)
    assert why == "TRACKER_ID"
