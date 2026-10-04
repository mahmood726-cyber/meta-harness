"""Plants from cross-vendor adversarial review NR-C22 (Codex; C:/mh-lanes/nr/codex/CALL_LOG.jsonl, artefact
F:/mh-nr101-codex/c22-g1-doac-membership/last_message.txt) of the denominator-shrinking gate NOT_AN_INCLUDED_TRIAL and
the event-total check. Each failed against the code before its fix."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from harness import comparator_membership as cm  # noqa: E402
from harness import event_total_check as ec  # noqa: E402

UNIT = ("METHODS AND RESULTS: Two independent investigators reviewed bleeding reports from 1034 individuals with 1121 "
        "major bleeds enrolled in 5 phase III trials comparing dabigatran with warfarin in 27 419 patients.")
META = ["Journal Article", "Meta-Analysis"]


def _gate(comp, unit=UNIT, k=6, pubtypes=META, title="Management and outcomes of major bleeding", matched=None):
    return cm.not_an_included_trial(comp, k, unit, "REFERENCE_SEED", unit_pubtypes=pubtypes, unit_title=title,
                                    unit_pmid="1", matched_pmids=matched or ["2", "3", "4", "5", "6", "7"])


def test_c22_background_screening_and_superseded_counts_are_never_the_reviews_count():
    for comp in ["BACKGROUND: A previous meta-analysis pooled 6 trials involving 27023 patients. METHODS: We included four eligible trials.",
                 "We identified 6 trials involving 27023 patients before screening; four were eligible for inclusion.",
                 "We identified 6 trials involving 27023 patients, of which four were included.",
                 "Earlier reviews included 4-6 trials involving 27023 patients. We included four trials."]:
        assert _gate(comp) is None, comp


def test_c22_a_subgroup_count_is_not_the_reviews_count():
    comp = "Six trials were included overall. In the cancer subgroup, 3 trials involving 1200 patients contributed data."
    assert _gate(comp, k=3) is None


def test_c22_a_single_trial_report_is_never_removed():
    comp = "In the last 4 years, 6 phase 3 trials including a total of 27,023 patients with VTE compared a DOAC with VKAs."
    for unit, pt in [("Investigators participating in 3 trials designed this single randomized trial.", ["Randomized Controlled Trial"]),
                     ("BACKGROUND: A pooled analysis of earlier trials suggested benefit. METHODS: This single randomized trial "
                      "enrolled 2000 patients.", ["Randomized Controlled Trial"]),
                     ("We performed a pooled analysis of the two treatment arms of this single randomized trial.", ["Randomized Controlled Trial"]),
                     # a real member's report that ALSO pools (RE-COVER II style), not typed as a meta-analysis
                     ("Pooled analysis of RE-COVER and RE-COVER II: patients enrolled in 2 phase III trials.", ["Randomized Controlled Trial"])]:
        assert _gate(comp, unit=unit, pubtypes=pt, title="Treatment of acute VTE with dabigatran") is None, unit


def test_c22_the_unit_must_not_be_a_matched_trials_report():
    comp = "In the last 4 years, 6 phase 3 trials including a total of 27,023 patients with VTE compared a DOAC with VKAs."
    assert _gate(comp, matched=["1", "3", "4", "5", "6", "7"]) is None


def test_c22_event_tokens_are_events():
    s = "The primary outcome occurred in {}."
    assert ec.trial_event_counts("The primary outcome was assessed in 75 year-old patients and 65 year-old patients.") is None
    assert ec.trial_event_counts(s.format("1 of 2 patients receiving dabigatran and 1 of 2 patients receiving warfarin"))["events"] == [1, 1]
    assert ec.trial_event_counts("Recurrent VTE was assessed in a subgroup comprising 130 patients receiving edoxaban "
                                 "and 146 patients receiving warfarin.") is None
    assert ec.trial_event_counts("Secondary recurrent bleeding occurred in 4 patients and 5 patients. The primary outcome "
                                 "occurred in 30 patients and 27 patients.")["events"] == [30, 27]
    assert ec.trial_event_counts("Recurrent VTE occurred in 2.0% of 13 500 patients and 2.2% of 13 523 patients.") is None
    assert ec.trial_event_counts("The primary outcome occurred in 30 patients receiving dabigatran vs. Warfarin "
                                 "recipients had 27 events.")["events"] == [30, 27]


def test_c22_the_event_check_reports_an_incompatibility_not_a_cause():
    t = {"1": "RESULTS: The primary outcome occurred in 30 of 1000 patients and 27 of 1000 patients."}
    comp = "Recurrent VTE occurred in 1.0% of DOAC recipients compared with 1.2% in VKA recipients (RR 0.9)."
    r = ec.check(comp, ["recurrent VTE"], 2000, t)
    assert r["state"] == "EVENTS_INCOMPATIBLE_WITH_COMPARATOR_RATES" and "not resolved here" in r["basis"]
    assert r["comparator_max_events_unrounded"] == 1.25 / 100 * 2000
