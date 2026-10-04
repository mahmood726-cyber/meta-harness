"""A comparator label 'Ben Ayed 2009' / 'van der Molen 2001' / 'de Vrese et al 2001' carried an author-year key the
label parser could not read (single capitalised surname only), so the trial was NO_KEY and never searched."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from kgap import k_gap  # noqa: E402


def _ay(label):
    t = k_gap._label_tokens(label)
    return t["author"], t["year"]


def test_two_word_and_particle_surnames_give_an_author_year_key():
    assert _ay("Ben Ayed 2009") == ("Ben Ayed", "2009")
    assert _ay("van der Molen 2001") == ("van der Molen", "2001")
    assert _ay("de Vrese et al 2001") == ("de Vrese", "2001")
    assert _ay("Almeida Montes 2003") == ("Almeida Montes", "2003")


def test_single_surnames_and_non_author_labels_are_unchanged():
    assert _ay("Nestler 1998") == ("Nestler", "1998")
    assert _ay("Palomba 2005a") == ("Palomba", "2005")
    assert _ay("O'Neil, 2018") == ("O'Neil", "2018")
    assert _ay("Trial B (2019) (20)") == ("", "")
    assert _ay("Trial E (2020) (25)") == ("", "")
    assert _ay("STEP 3 30") == ("", "")
