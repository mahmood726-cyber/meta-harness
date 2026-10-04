"""secondary_meta_build.family_of_factory: a comparator's figure row joins its trial-list entry by label. The trial
list's trailing reference number is stripped like the row's ('Zinman (8)' leads 'Zinman 2016'; before, 8 accepted rows
of sglt2-primary-prevention-hf's figure joined none); reference numbers are not compared (a figure may be numbered differently from the list); a first
author + year confirmation outranks a bare name; and a
tie is broken only by a LONGER name the others lead ('Semler (SALT trial)' over 'Semler [15]'), never across two
different trials (a combined 'SOLOIST-WHF/SCORED' row binds to neither). Each case fails as built before the fix or is
the control that must not change."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import secondary_meta_build as smb  # noqa: E402


class R:
    def __init__(self, label):
        self.trial_label = label


def _fam(*labels):
    return smb.family_of_factory([{"id": l, "label": l, "acronyms": [], "author_year": None} for l in labels])


def test_a_reference_numbered_list_label_joins_the_figure_row():
    f = _fam("Zinman (8)", "Radholm (9)", "Cannon (11)")
    assert f(R("Zinman 2016")) == "Zinman (8)" and f(R("Radholm 2018")) == "Radholm (9)"


def test_a_figure_numbered_differently_from_the_list_still_joins_by_name():
    # melatonin's comparator numbers its figure and its list differently ('Wade AG, 2011 [21]' is list 'Wade AG [22]')
    f = _fam("Almeida Montes LG [31]", "Dawson D [35]")
    assert f(R("Almeida Montes LG, 2002 [30]")) == "Almeida Montes LG [31]"
    assert f(R("Dawson D, 1998 [35]")) == "Dawson D [35]"


def test_first_author_and_year_outrank_a_bare_name():
    f = smb.family_of_factory([{"id": "Young [10]", "label": "Young [10]", "acronyms": [], "author_year": ("young", "2015")},
                               {"id": "Young [17]", "label": "Young [17]", "acronyms": [], "author_year": ("young", "2014")}])
    assert f(R("Young 2015")) == "Young [10]" and f(R("Young 2014")) == "Young [17]"
    assert f(R("Young 2016")) is None                                   # two name matches, no year: ambiguous


def test_the_longer_name_wins_only_when_the_shorter_leads_it():
    f = _fam("Semler (SALT trial)", "Semler (SMART trial)", "Semler [15]")
    assert f(R("Semler (SALT trial) 2016")) == "Semler (SALT trial)"
    assert f(R("Semler (SMART trial) 2018")) == "Semler (SMART trial)"


def test_a_combined_row_naming_two_trials_binds_to_neither():
    f = _fam("SOLOIST-WHF", "SCORED")
    assert f(R("SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF")) is None
