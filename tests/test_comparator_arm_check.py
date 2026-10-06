"""scripts/g1_comparator_arm_check.judge: a comparator row's arms against the trial's POSTED result. EMPA-REG's posted HHF
(CT.gov NCT01131676): placebo 4.1% of 2333, all empagliflozin 2.7% of 4687; the comparator (33519713) printed
95/4687 vs 126/2333 -- only the swapped arms reproduce the posted figures."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_comparator_arm_check as ac  # noqa: E402

OM = {"title": "Percentage of Participants With Heart Failure Requiring Hospitalisation (Adjudicated)",
      "unitOfMeasure": "percentage of participants",
      "groups": [{"id": "OG000", "title": "Placebo"}, {"id": "OG001", "title": "Empagliflozin 10 mg"},
                 {"id": "OG002", "title": "Empagliflozin 25 mg"}, {"id": "OG003", "title": "All Empagliflozin"}],
      "denoms": [{"counts": [{"groupId": "OG000", "value": "2333"}, {"groupId": "OG001", "value": "2345"},
                             {"groupId": "OG002", "value": "2342"}, {"groupId": "OG003", "value": "4687"}]}],
      "classes": [{"categories": [{"measurements": [{"groupId": "OG000", "value": "4.1"}, {"groupId": "OG001", "value": "2.6"},
                                                    {"groupId": "OG002", "value": "2.8"}, {"groupId": "OG003", "value": "2.7"}]}]}]}


def test_the_comparators_empa_reg_row_is_arm_swapped():
    assert ac.judge({"events_t": 95, "n_t": 4687, "events_c": 126, "n_c": 2333}, OM)[0] == "SWAPPED"


def test_the_right_way_round_is_consistent_and_a_wrong_count_undecided():
    assert ac.judge({"events_t": 126, "n_t": 4687, "events_c": 96, "n_c": 2333}, OM)[0] == "CONSISTENT"
    assert ac.judge({"events_t": 150, "n_t": 4687, "events_c": 96, "n_c": 2333}, OM)[0] == "UNDECIDED"
    assert ac.judge({"events_t": 126, "n_t": 4600, "events_c": 96, "n_c": 2333}, OM)[0] == "UNDECIDED"   # denominator


def test_ambiguous_arms_are_never_judged():
    om = dict(OM, groups=[g for g in OM["groups"] if g["id"] != "OG003"])     # two doses, no pooled group
    assert ac.judge({"events_t": 95, "n_t": 4687, "events_c": 126, "n_c": 2333}, om)[0] == "UNDECIDED"
