"""A comparator's trial list labelled 'Helps et al52' / 'Mewton et al. (26)' (surname + reference number) never joined
the same comparator's forest row 'Helps 2015' / 'Mewton N-2019' (surname + year): the leading-token join compared
[helps, et, al52] with [helps, 2015]. The surname core (et al / reference number / year / initials removed, spacing
folded) now joins -- uniquely, and never across two different years."""
import os
import sys
from types import SimpleNamespace as NS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, "scripts"))
import secondary_meta_build as smb  # noqa: E402


def _fam(labels):
    return smb.family_of_factory([{"id": l, "label": l, "acronyms": [], "author_year": None} for l in labels])


def test_surname_with_reference_number_joins_surname_with_year():
    f = _fam(["Helps et al52", "Hempel et al53", "Mewton et al. (26)", "de Vrese et al33", "Refaie 2005", "Akrami et al. (12)"])
    assert f(NS(trial_label="Helps 2015")) == "Helps et al52"
    assert f(NS(trial_label="Mewton N-2019")) == "Mewton et al. (26)"
    assert f(NS(trial_label="DeVrese 2011")) == "de Vrese et al33"
    assert f(NS(trial_label="Re faie 2005")) == "Refaie 2005"
    # a forename leads: joins the UNIQUE surname (the ambiguous case is refused, see the forename-first plant below)
    assert f(NS(trial_label="Mehdi Akrami–2012")) == "Akrami et al. (12)"


def test_ambiguous_surnames_and_different_years_never_join():
    f = _fam(["Deftereos et al. (25)", "Deftereos et al. (19)", "Palomba 2004", "Palomba 2005a"])
    assert f(NS(trial_label="Deftereos 2013")) is None
    assert f(NS(trial_label="Palomba 2006")) is None
    assert f(NS(trial_label="Palomba 2004")) == "Palomba 2004"


def test_the_surname_tier_never_overrides_or_dilutes_an_existing_join():
    # balanced-crystalloids 4 Oct: 'Young [10]' / 'Young [17]' joined 'Young 2015' / 'Young 2014' by their PMIDs'
    # author-year; the surname tier hit BOTH and made each ambiguous. melatonin: 'Wade AG [28]' moved 2007 -> 2011.
    ents = [{"id": "Young [10]", "label": "Young [10]", "acronyms": [], "author_year": ("young", "2015")},
            {"id": "Young [17]", "label": "Young [17]", "acronyms": [], "author_year": ("young", "2014")},
            {"id": "Wade AG [22]", "label": "Wade AG [22]", "acronyms": [], "author_year": ("wade", "2011")},
            {"id": "Wade AG [28]", "label": "Wade AG [28]", "acronyms": [], "author_year": ("wade", "2007")}]
    f = smb.family_of_factory(ents)
    assert f(NS(trial_label="Young 2015")) == "Young [10]"
    assert f(NS(trial_label="Young 2014")) == "Young [17]"
    assert f(NS(trial_label="Wade AG, 2007 [26]")) == "Wade AG [28]"
    assert f(NS(trial_label="Wade AG, 2011 [21]")) == "Wade AG [22]"


def _ents(spec):
    return [{"id": l, "label": l, "acronyms": a, "author_year": ay} for l, a, ay in spec]


def test_accents_and_a_dropped_accented_letter_still_join():
    f = _fam(["Lönnermark et al58", "Alpérovitch et al. [25], 2015 (France)", "Lemaitre et al. [24], 2002 (USA)"])
    assert f(NS(trial_label="Lnnermark 2010")) == "Lönnermark et al58"
    assert f(NS(trial_label="Alperovitch et al 2015")) == "Alpérovitch et al. [25], 2015 (France)"


def test_an_acronym_tolerates_one_year_an_author_never_does():
    f = _fam(["RALES1999", "EPHESUS2003", "Palomba 2004", "Palomba 2005a"])
    assert f(NS(trial_label="RALES2000")) == "RALES1999"
    assert f(NS(trial_label="Palomba 2005")) == "Palomba 2005a"      # same year: unchanged
    assert f(NS(trial_label="Palomba 2003")) is None                # an author +-1 year is another paper


def test_a_forename_first_row_joins_the_unique_surname():
    f = _fam(["Akrami et al. (12)", "Nidorf et al. (13)", "Tardif et al. (8)"])
    assert f(NS(trial_label="Mehdi Akrami–2012")) == "Akrami et al. (12)"
    g = _fam(["Akrami et al. (12)", "Mehdi et al. (5)"])
    assert g(NS(trial_label="Mehdi Akrami–2012")) is None           # both names are trials: ambiguous


def test_a_bare_family_acronym_is_broken_by_the_one_label_the_row_leads():
    ents = _ents([("ODYSSEY FH I NCT01623115", ["ODYSSEY"], None), ("ODYSSEY FH II NCT01709500", ["ODYSSEY"], None),
                  ("ODYSSEY COMBO I NCT01644175", ["ODYSSEY"], None), ("PACMAN - AMI NCT03067844", [], None)])
    f = smb.family_of_factory(ents)
    assert f(NS(trial_label="ODYSSEY FH II")) == "ODYSSEY FH II NCT01709500"
    assert f(NS(trial_label="PACMAN – AMI")) == "PACMAN - AMI NCT03067844"
    assert f(NS(trial_label="ODYSSEY")) is None


def test_a_label_glued_by_table_extraction_joins_its_spaced_row():
    # semaglutide-mace 4 Oct: the comparator's table gives 'SCALEMaintenance25,38', 'SURMOUNT-1 39'; its figure prints
    # 'SCALE Maintenance, 2013', 'SURMOUNT-1, 2022' -- the same trials, spacing lost in extraction, ref numbers glued
    f = _fam(["SCALEMaintenance25,38", "SCALEObesity and Prediabetes26,37", "SCALESleep Apnea 27",
              "SURMOUNT-1 39", "SURMOUNT-3 17", "STEP 8 31", "STEP 1 29"])
    assert f(NS(trial_label="SCALE Maintenance, 2013")) == "SCALEMaintenance25,38"
    assert f(NS(trial_label="SCALE Obesity and Prediabetes, 2017")) == "SCALEObesity and Prediabetes26,37"
    assert f(NS(trial_label="SCALE Sleep Apnea, 2016")) == "SCALESleep Apnea 27"
    assert f(NS(trial_label="SURMOUNT-1, 2022")) == "SURMOUNT-1 39"
    assert f(NS(trial_label="SURMOUNT-3, 2023")) == "SURMOUNT-3 17"
    assert f(NS(trial_label="STEP 8")) == "STEP 8 31"                # a trial NUMBER is never stripped
    assert f(NS(trial_label="SURMOUNT, 2022")) is None               # two SURMOUNTs: never a pick


def test_the_compact_tier_keeps_the_year_rule_and_accented_authors_match_their_pmid_year():
    # melatonin 4 Oct: the compact tier (no years) joined 'Nagtegaal JE, 1995 [34]' to the trial whose PMID is a 1998
    # paper, and Almeida Montes 2002 / James 1989 to 2003 / 1990 papers -- an author's year is never relaxed
    ents = [{"id": "Nagtegaal JE [36]", "label": "Nagtegaal JE [36]", "acronyms": [], "author_year": ("nagtegaal", "1998")},
            {"id": "James SP [40]", "label": "James SP [40]", "acronyms": [], "author_year": ("james", "1990")},
            {"id": "Garzón C [26]", "label": "Garzón C [26]", "acronyms": [], "author_year": ("garzón", "2009")}]
    f = smb.family_of_factory(ents)
    assert f(NS(trial_label="Nagtegaal JE, 1995 [34]")) is None
    assert f(NS(trial_label="James SP, 1989 [39]")) is None
    assert f(NS(trial_label="Nagtegaal JE, 1998 [34]")) == "Nagtegaal JE [36]"
    assert f(NS(trial_label="Garzon C, 2009 [25]")) == "Garzón C [26]"


def test_a_generic_clinical_abbreviation_is_never_a_trial_acronym_in_the_join():
    # dapagliflozin-hfpef 4 Oct: our DELIVER entry carried acronyms ['DELIVER', 'HFPEF']; 'HFpEF' anywhere in a row
    # ('SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF') joined it to DELIVER and filled DELIVER with SOLOIST/SCORED numbers
    ents = [{"id": "D", "label": "DELIVER", "acronyms": ["DELIVER", "HFPEF"], "author_year": ("solomon", "2022")},
            {"id": "E", "label": "EMPEROR-Preserved", "acronyms": ["EMPEROR-PRESERVED", "MACE"], "author_year": None}]
    f = smb.family_of_factory(ents)
    assert f(NS(trial_label="SOLOIST-WHF/SCORED Bhatt et al (2021) HFpEF")) is None
    assert f(NS(trial_label="DELIVER Solomon et al (2022) HFmr/pEF")) == "D"
    assert f(NS(trial_label="Overall MACE")) is None
