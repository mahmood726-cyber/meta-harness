"""Plants for round 14 (condition-as-outcome in SCREENING, the PubMed side of harness/condition_role.py). A topic whose
question enrols people WITHOUT the condition and asks whether the intervention prevents it (probiotics: "In patients
receiving antibiotics, do probiotics reduce antibiotic-associated diarrhoea") screens population by that condition's
words -- so a trial that names it only as what it PREVENTS ("probiotics for the prevention of antibiotic-associated
diarrhoea" in the abstract, not in the title) is excluded as "population not on-topic". FIRED = the harness under test
does not surface it. Controls: a topic that ENROLS people with the condition (doac-vte: "In adults with acute
symptomatic VTE") never turns a VTE-prevention trial into a candidate; a record whose abstract only mentions the
condition in passing is not one.

  python scripts/plants_round14.py --harness-root <dir containing harness/> [--out <json>]
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

PROBIOTICS = {"slug": "plant-probiotics", "question": "In patients receiving antibiotics, do probiotics reduce antibiotic-"
              "associated diarrhoea versus placebo or no probiotic?",
              "include": {"population_any": ["antibiotic-associated diarr*", "antibiotic associated diarr*", "AAD"]}}
DOAC = {"slug": "plant-doac", "question": "In adults with acute symptomatic venous thromboembolism (VTE), do direct oral "
        "anticoagulants change recurrent VTE versus warfarin / vitamin-K antagonist therapy?",
        "include": {"population_any": ["venous thromboembolism", "VTE", "pulmonary embolism"]}}
X2 = "population not on-topic: title/conditions do not mention any of [...] (an incidental abstract mention does not qualify)."


def _case(cfg, rid, title, abstract):
    scr = {"decisions": [{"id": rid, "id_type": "pmid", "decision": "exclude", "rule_id": "X2", "reason": X2}]}
    return scr, [{"id": rid, "id_type": "pmid", "title": title, "abstract": abstract}]


def run(harness_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    cr = importlib.import_module("harness.condition_role")
    fn = getattr(cr, "outcome_condition_candidates", None)
    out = {}

    def cands(cfg, *case):
        return fn(*_case(cfg, *case), cfg) if fn else []

    got = cands(PROBIOTICS, "p1", "Lactobacillus in hospitalised adults: a randomised trial",
                "We tested whether a probiotic drink given with antibiotics could prevent antibiotic-associated diarrhoea "
                "in 135 inpatients.")
    out["Q1_prevented_condition_named_only_in_the_abstract_not_surfaced"] = {"fired": not got, "got": got}
    got = cands(DOAC, "d1", "Apixaban after knee replacement",
                "Apixaban for the prevention of venous thromboembolism after total knee replacement.")
    out["C1_a_topic_that_enrols_people_with_the_condition_never_proposes"] = {"fired": bool(got), "got": got}
    got = cands(PROBIOTICS, "p2", "Yogurt and bowel habit", "Stool frequency was recorded; no antibiotic-associated "
                "diarrhoea was seen in either group.")
    out["C2_a_passing_mention_is_not_a_prevention_frame"] = {"fired": bool(got), "got": got}
    # Q2 (comparator trial identity): a forest-plot membership row printed as a trial acronym we hold for exactly ONE
    # family (tocilizumab's REACT plot: 'RECOVERY' = NCT04381936) is left unbound -- that path bound only by a report PMID
    orl = importlib.import_module("harness.overlap_relation")
    review = {"comparator": {"analysis": {"membership": {"figure": {"caption": {"quote": "plant"}}, "endpoint": "28-day mortality",
              "members": [{"label": "RECOVERY", "counts": [1, 2, 3, 4]}, {"label": "Trial A", "counts": [1, 2, 3, 4]}]}}},
              "trial_families": [{"family_id": "NCT04381936", "aliases": {"acronym": ["RECOVERY"]}}]}
    src, ins, _ = orl._members(review, None, "28-day mortality", {orl.norm_name("RECOVERY"): {"NCT04381936"}}, set())
    fam = {m["name"]: m["family"] for m in ins}
    out["Q2_forest_plot_row_named_by_a_held_acronym_left_unbound"] = {"fired": fam.get("RECOVERY") != "NCT04381936", "got": fam}
    # control: a generic row label never binds by name
    out["C3_a_generic_row_label_never_binds_by_name"] = {"fired": fam.get("Trial A") is not None, "got": fam.get("Trial A")}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness-root", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    s = json.dumps(run(Path(a.harness_root)), indent=1)
    print(s)
    if a.out:
        Path(a.out).write_text(s + "\n", encoding="utf-8", newline="\n")
