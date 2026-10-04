"""A comparator label 'ACRONYM YYYY' must normalise to the acronym: omega3's Table 1 ('ASCEND 2018', 'ORIGIN 2012',
'GISSI-HF 2008') normalised to 'ASCEND2018'... and never met AACT (ORIGIN = NCT00069784's acronym; ASCEND, GISSI-HF the
title acronyms of NCT00135226, NCT00336336). Once the table's shifted xrefs were distrusted nothing else resolved them."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kgap import k_gap as kg  # noqa: E402


def test_a_year_after_a_space_is_stripped():
    assert [kg.norm_acronym(a) for a in ("ASCEND 2018", "ORIGIN 2012", "GISSI-HF 2008", "PCOSMIC 2010")] == \
        ["ASCEND", "ORIGIN", "GISSIHF", "PCOSMIC"]


def test_trial_numbers_and_glued_years_are_unchanged():
    assert kg.norm_acronym("RALES1999") == "RALES"
    assert kg.norm_acronym("PIONEER 6") == "PIONEER6" and kg.norm_acronym("DECLARE-TIMI 58") == "DECLARETIMI58"
    assert kg.norm_acronym("SUSTAIN-6") == "SUSTAIN6"
