"""STRATEGY CONTINUITY (sacubitril-HFrEF review, 2026-09-28, hash 0d5f8f77; retrospective, Dispatch under Mahmood's delegation).

"Longest follow-up" means the longest follow-up while the randomised strategies are unchanged. A result past a stated switch
belongs to a later period with its own contrast and is never served as the randomised comparison.
"""
from harness import strategy_periods as sp

# PIONEER-like plant: the switch sentence as a trial report would state it (PIONEER-HF's own switch text is NOT held in the
# corpus -- its registry record carries only the 8-week double-blind measures -- so this is synthetic, not a corpus quote).
PIONEER_LIKE = ("Patients hospitalized for acute decompensated heart failure were randomized to sacubitril/valsartan or enalapril "
                "for 8 weeks in a double-blind fashion. After week 8, patients in the enalapril group were switched to open-label "
                "sacubitril/valsartan for 4 weeks.")


def test_plant_pioneer_like_12_week_row_is_refused_as_strategy_changed():
    pr = sp.periods(PIONEER_LIKE)
    assert pr["state"] == "SWITCH_STATED" and pr["switch_week"] == 8
    assert [p["from_week"] for p in pr["periods"]] == [0, 8]
    assert pr["periods"][1]["contrast"].startswith("EARLY vs DELAYED")
    c = sp.continuity({"id": "PIONEER-like", "timeframe_weeks": 12}, PIONEER_LIKE)
    assert c["state"] == "STRATEGY_CHANGED" and "not the randomised comparison" in c["reason"]


def test_within_period_row_is_kept():
    c = sp.continuity({"id": "PIONEER-like", "timeframe_weeks": 8}, PIONEER_LIKE)
    assert c["state"] == "WITHIN_RANDOMISED_PERIOD"


def test_row_with_no_timepoint_is_not_placed():
    c = sp.continuity({"id": "PIONEER-like", "source": "registry primary outcome"}, PIONEER_LIKE)
    assert c["state"] == "TIMEPOINT_NOT_STATED"


def test_no_switch_stated_returns_none_never_assumed():
    assert sp.continuity({"timeframe_weeks": 52}, "A randomized double-blind trial over 52 weeks.") is None
    assert sp.periods(None)["state"] == "NOT_STATED"


def test_open_label_extension_following_randomised_period_in_any_unit():
    t = "a 36-week, open-label extension of therapy following a 16-week, randomized, placebo-controlled, double-blind period"
    pr = sp.periods(t)
    assert pr["state"] == "SWITCH_STATED" and pr["switch_week"] == 16
    assert sp.continuity({"timeframe_weeks": 52}, t)["state"] == "STRATEGY_CHANGED"
    d = sp.periods("a 7-day, randomized, double-blind, placebo-controlled trial with a 6-month open-label extension phase")
    assert d["state"] == "SWITCH_STATED" and d["switch_week"] == 1.0


def test_untimed_switch_fails_closed_as_continuity_not_established():
    t = "Subsequently, patients will be switched to placebo in the experimental arm until a total of 35 days."
    assert sp.periods(t)["state"] == "SWITCH_STATED_TIMING_NOT_STATED"
    c = sp.continuity({"timeframe_weeks": 5}, t)
    assert c["state"] == "CONTINUITY_NOT_ESTABLISHED" and c["row_week"] is None


def test_a_device_change_is_not_a_change_of_strategy():
    # STEP 8 registry arm text (held): a pen-injector change, both arms, same drug and regimen
    t = ("In week 44, all participants switched from the PDS290 pen-injector to the DV3396 single-dose pen-injector. "
         "A follow-up visit (end of trial) for safety assessments was scheduled 7 weeks after end of treatment.")
    assert sp.periods(t)["state"] == "NOT_STATED"
    assert sp.continuity({"timeframe_weeks": 68}, t) is None
