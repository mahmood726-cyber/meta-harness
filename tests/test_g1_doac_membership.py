"""G1 doac-vte-recurrence: a REFERENCE-SEEDED comparator unit leaves the eligible denominator only when the comparator's
OWN abstract states its trial count, our matched trials number exactly that count, and the unit's own record says it
pools several trials (harness/comparator_membership.py). Pre-fix (acq/k-gap f2fde38): Majeed 2013 (PMID 24081972, a
pooled bleeding analysis of 5 dabigatran trials) sat SCREENED_OUT_UNAUDITED as the 7th 'trial' of van Es 2014."""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from harness import comparator_membership as cm  # noqa: E402

SLUG = "doac-vte-recurrence"
COMP = ("In the last 4 years, 6 phase 3 trials including a total of 27,023 patients with venous thromboembolism (VTE) "
        "compared a direct oral anticoagulant (DOAC) with vitamin K antagonists (VKAs). We included the phase 3 trials.")
UNIT = ("METHODS AND RESULTS: Two independent investigators reviewed bleeding reports from 1034 individuals with 1121 "
        "major bleeds enrolled in 5 phase III trials comparing dabigatran with warfarin in 27 419 patients.")
TRIAL = ("METHODS: In this randomized, double-blind study, we compared apixaban with conventional therapy in 5395 patients "
         "with acute venous thromboembolism.")


KW = dict(unit_pubtypes=["Journal Article", "Meta-Analysis"], unit_title="Management and outcomes of major bleeding",
          unit_pmid="24081972", matched_pmids=["19966341", "24344086", "23991658", "23808982", "21128814", "22449293"])


def test_named_only_when_every_condition_holds():
    d = cm.not_an_included_trial(COMP, 6, UNIT, "REFERENCE_SEED", **KW)
    assert d["kind"] == "NOT_AN_INCLUDED_TRIAL" and d["comparator_stated_k"] == 6
    assert d["comparator_stated_patients"] == 27023
    assert d["span"]["match"].endswith("enrolled in 5 phase III trials")


def test_never_named_when_any_condition_fails():
    assert cm.not_an_included_trial(COMP, 5, UNIT, "REFERENCE_SEED", **KW) is None          # matched != stated k
    assert cm.not_an_included_trial(COMP, 6, UNIT, "COMPARATOR_TABLE", **KW) is None        # not a reference seed
    assert cm.not_an_included_trial(COMP, 6, TRIAL, "REFERENCE_SEED", **KW) is None         # a single trial: stays eligible
    assert cm.not_an_included_trial("We pooled the randomised trials.", 6, UNIT, "REFERENCE_SEED", **KW) is None  # no count
    two = COMP + " Of these, 4 trials including 12,000 patients reported bleeding."
    assert cm.not_an_included_trial(two, 6, UNIT, "REFERENCE_SEED", **KW) is None           # two different stated counts


def test_the_tracker_names_majeed_with_both_spans_and_keeps_the_denominator_honest():
    import g1_tracker as gt
    o = json.load(open(os.path.join(gt.G1_DIR, SLUG + ".json"), encoding="utf-8"))
    d = next(d for d in o["named_differences"] if d["pmid"] == "24081972")
    # since acq 2bf32a5 the protocol route names it first (X1: an analysis across several trials is no trial's report);
    # this lane's comparator-membership gate is the second line, used only when nothing else names the unit
    assert (d["kind"], d["rule_id"]) in {("PROTOCOL_SCOPE_DIFFERENCE", "X1"), ("NOT_AN_INCLUDED_TRIAL", "COMPARATOR_STATED_K")}
    assert gt.span_is_verbatim(SLUG, "24081972", d["span"])
    if d["kind"] == "NOT_AN_INCLUDED_TRIAL":
        assert gt.span_is_verbatim(SLUG, "24963045", d["comparator_span"])
    # the whole pools ARE comparable: the comparator states 6 trials == 6 matched, so the measure question is reached
    # state renamed by the HR/RR class (acq/k-gap f34580f9; 5 Oct decision 1): the whole-pool form carries its basis
    assert o["same_trials"]["state"] == "MEASURE_DIFFERENCE" and o["same_trials"]["basis"].startswith("COMPARATOR_STATES")
    assert o["N_eligible"] == 6 and o["k_matched"] == 6 and o["open_gaps"] == []
    assert gt.scope_citation_violations(o) == []


def test_pre_fix_majeed_was_an_unaudited_seventh_trial():
    base = json.loads(subprocess.check_output(["git", "show", f"752dc57bf7df13efc4f2acf5434893d313112c6c:outputs/k_gap/g1/{SLUG}.json"],
                                              cwd=ROOT))
    assert base["N_eligible"] == 7 and base["top_blocker"] == "SCREENED_OUT_UNAUDITED:X1"
