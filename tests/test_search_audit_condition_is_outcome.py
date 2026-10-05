"""Plants (search+screen audit, 2026-10-05): class CONDITION_IS_OUTCOME.

probiotics-aad-prevention registers 'antibiotic-associated diarr*' / 'AAD' as its population terms, but those words name
the OUTCOME it prevents; its registered population (pico.json) is 'patients receiving antibiotics'. A prevention trial's
title names whom it enrolled, so 10 comparator trials were X2 'population not on-topic'; the recorded dual review
(reader + adjudicator) judged them eligible. Fix: derived from the config (never edited) -- when no population term names
the registered population and they overlap the primary outcome's keywords, the population INCLUSION check may read the
abstract; the registered EXCLUSIONS keep their title/conditions haystack (a first draft widened both and turned 6
dual-review-eligible includes into X2). Radius over 3,201 held decisions: 17 records, all probiotics, none include->exclude.
Tests 1-3 fail on the old code (condition_is_outcome absent / X2 fires)."""
from __future__ import annotations

import json
import os

from harness import screen

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "topics", "probiotics-aad-prevention.json"), encoding="utf-8"))
TRIAL = {"id": "1", "id_type": "pmid", "pubtypes": ["Randomized Controlled Trial"],
         "title": "Lactobacillus rhamnosus GG in children receiving oral antibiotics: a randomized placebo-controlled trial.",
         "abstract": "We randomly assigned 188 children receiving antibiotics to Lactobacillus GG or placebo. The primary "
                     "outcome was antibiotic-associated diarrhea within 10 days."}


def _decide(rec, cfg=CFG):
    return screen.run([rec], cfg)["decisions"][0]


def test_the_rule_is_derived_for_probiotics_and_only_where_the_population_does_not_name_the_condition():
    assert screen.condition_is_outcome(CFG)
    covid = json.load(open(os.path.join(ROOT, "topics", "tocilizumab-covid19-mortality.json"), encoding="utf-8"))
    assert screen.condition_is_outcome(covid) == []          # its registered population names COVID-19


def test_a_prevention_trial_whose_title_names_whom_it_enrolled_is_included():
    d = _decide(TRIAL)
    assert d["decision"] == "include", d


def test_without_the_derived_rule_the_same_trial_is_x2():
    cfg = dict(CFG, slug="__control_no_pico__")             # no registered population -> rule not derived
    d = _decide(TRIAL, cfg)
    assert d["decision"] == "exclude" and d["rule_id"] == "X2"


def test_the_registered_exclusions_are_not_widened_to_the_abstract():
    rec = dict(TRIAL, abstract=TRIAL["abstract"] + " Earlier work examined the treatment of AAD in adults.")
    assert _decide(rec)["decision"] == "include"


def test_a_background_only_mention_of_the_outcome_never_qualifies():
    # the first draft read the whole abstract; the recorded radius review contradicted 4 of 12 such flips
    rec = dict(TRIAL, title="Bacillus spores and gut symptoms in healthy adults.",
               abstract="BACKGROUND: Antibiotic-associated diarrhea is common. METHODS: We randomly assigned 60 healthy "
                        "adults to Bacillus spores or placebo and recorded stool frequency.")
    assert _decide(rec)["rule_id"] == "X2"


def test_an_economic_evaluation_alongside_a_trial_is_not_the_trials_primary_report():
    rec = dict(TRIAL, title="Health economic evaluation alongside the PROSPECT randomized trial of probiotics.")
    d = _decide(rec)
    assert d["rule_id"] == "X1" and "economic evaluation" in d["reason"]
