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


def test_a_trial_with_a_comparator_row_is_still_seeded_through_our_screen():
    o = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "g1", "sglt2-primary-prevention-hf.json"), encoding="utf-8"))
    x = next(t for t in o["trials"] if t["label"].startswith("Radholm"))
    assert x["comparator_row"] and x["comparator_row"]["events_t"] == 87          # its row joined (label-join fix)
    assert x["route"] == "PRIMARY" and x["matched_via_other_report"]["pool_row"] == "PMID 28605608"
    assert not o["open_gaps"]


def test_no_comparator_trial_with_a_held_record_is_left_as_an_identification_gap():
    """The defect's symptom: Radholm (9) read blocker IDENTIFICATION although its record was held (it never reached our
    screen). A trial our screen INCLUDED but could not extract carries an extraction blocker, not a funnel -- by design."""
    mem = {str(v.get("id")) for v in json.load(open(os.path.join(ROOT, "outputs", "k_gap", "member_records.json"),
                                                     encoding="utf-8")).values()}
    d = os.path.join(ROOT, "outputs", "k_gap", "g1")
    left = []
    # the topics regenerated with the fix on this branch; pcsk9-mace's ODYSSEY FH II is a DIFFERENT class (in our own
    # build, not pooled, no refusal recorded -> IDENTIFICATION), listed in outputs/k_gap/FINISH_LINE.md
    for f in [s_ + ".json" for s_ in REGENERATED]:
        o = json.load(open(os.path.join(d, f), encoding="utf-8"))
        for x in o.get("trials") or []:
            fam = str(x.get("family") or "").replace("PMID ", "")
            if not x.get("in_our_pool") and fam in mem and x.get("blocker") == "IDENTIFICATION" and not x.get("seeded_funnel"):
                left.append(f"{o['slug']}::{x['label']}")
    assert not left, left
