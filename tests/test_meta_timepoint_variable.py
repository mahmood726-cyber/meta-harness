"""Plant (5 Oct night, forest lane): a meta whose OWN outcome is 'all-cause mortality at the longest follow-up, defined by
the individual trial' states no single timepoint, even when the only day-count in its text is another study's (33612824
cites REACT's '28-day all-cause mortality' in its background) -- meta_timepoint returned '28 days' and admitted CAPE
COVID (a day-21 trial), REMAP-CAP and Metcovid rows under a 28-day protocol."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import secondary_meta_build as smb  # noqa: E402

BACKGROUND = ("A prospective meta-analysis suggested that corticosteroid treatment was related to a lower 28-day "
              "all-cause mortality (odds ratio 0.66).")


def test_variable_timepoint_statement_means_no_single_timepoint():
    held = BACKGROUND + " The primary outcome was all-cause mortality at the longest follow-up, defined by the " \
                        "individual trial."
    assert smb.meta_timepoint(held) is None
    for phrase in ("mortality at the last follow-up", "mortality at the end of follow-up",
                   "mortality at the maximum follow-up", "the time point defined by each trial"):
        assert smb.meta_timepoint(BACKGROUND + " Primary outcome: " + phrase + ".") is None


def test_a_single_stated_timepoint_still_counts():
    assert smb.meta_timepoint("The primary outcome was 28-day all-cause mortality.") == "28 days"
    assert smb.meta_timepoint("Mortality at day 28 was the primary outcome; follow-up was complete in 98%.") \
        == "28 days"
