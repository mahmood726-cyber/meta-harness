"""G1 finish line (3 Oct): two harness classes found while closing topics, each with its failing input.
1. binding_verdict names a registry outcome by the topic's own outcome NAME (all content words, plural folded): iv-iron's
   keywords all say 'worsening', so HEART-FID's 'Number of Hospitalizations for Heart Failure' was OUTCOME_NOT_NAMED.
2. Every comparator trial we do not pool is seeded through our screen, whatever its route: the seeding was gated on route
   NO_ROW, so a trial with a comparator row joined (UNVERIFIED) never saw our screen -- 45 trials in 12 topics -- and
   sglt2-primary-prevention-hf's Radholm (9) lost its same-trial match to the CANVAS pool row."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_tracker as gt  # noqa: E402

REGENERATED = ["sglt2-primary-prevention-hf", "omega3-cardiovascular-events", "iv-iron-hfref-hosp",
               "melatonin-primary-insomnia-sol", "metformin-pcos-ovulation", "esketamine-trd-madrs",
               "dapagliflozin-hfpef-hosp", "colchicine-secondary-cv-prevention", "glp1-ra-mace-t2d",
               "balanced-crystalloids-vs-saline-mortality"]
KW = ["hospitalization for worsening HF", "hospitalizations for worsening heart failure"]


def test_a_registry_title_is_named_by_the_topics_outcome_name():
    v = gt.binding_verdict("Heart-failure hospitalization", KW, "Number of Hospitalizations for Heart Failure", 2, True)
    assert v["verdict"] == "BINDABLE" and v["named_by"] == ["Heart-failure hospitalization"]


def test_the_name_rule_needs_every_content_word_and_keeps_the_estimand_gate():
    assert gt.binding_verdict("Heart-failure hospitalization", KW, "HF Hospitalizations and CV Death", 2)["gate"] == "OUTCOME_NOT_NAMED"
    assert gt.binding_verdict("Heart-failure hospitalization", KW, "Number of Participants With Heart Failure", 2)["gate"] == "OUTCOME_NOT_NAMED"
    v = gt.binding_verdict("Hospitalization for heart failure", [], "Composite of CV Death or Hospitalization for Heart Failure", 2)
    assert v["gate"] == "ESTIMAND"                                   # named, then refused as a different composite
