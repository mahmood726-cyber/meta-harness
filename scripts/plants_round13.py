"""Plants for round 13 (the registry-match PAIRED plant, D5): two blind codex readers (d5_identity_v2 + reader2, 942
pairs from the round-12 served pages) agree with each other and against the rule on 83 pairs -- 43 false reassurance
(rule SAME, both readers DIFFERENT) and 40 false concern (rule DIFFERENT, both readers SAME). Each plant is one root
cause, built from a held registered text. FIRED = the harness under test still makes the error. On the pre-fix harness
every Q fires; on the fix none; every C holds on both.

  python scripts/plants_round13.py --harness-root <dir containing harness/> [--out <json>]
"""
from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path

# (pooled outcome, registered outcome text, kind, the right answer) -- texts copied from the served registry rows
FALSE_REASSURANCE = {
    "Q1_recurrent_VTE_plus_all_deaths_read_as_recurrent_VTE": (
        "Trial-reported recurrent VTE composite", "Number of Participants With Recurrent Symptomatic VTE and All Deaths",
        "secondary", False),
    "Q2_CV_death_only_read_as_CV_death_or_worsening_HF": (
        "Composite cardiovascular death or worsening heart failure",
        "Subjects Included in the Endpoint of Cardiovascular Death", "secondary", False),
    "Q3_stroke_component_read_as_stroke_or_systemic_embolism": (
        "Stroke or systemic embolism", "The Individual Components of the Composite Primary and Major Secondary Efficacy "
        "Outcome Measures: Stroke", "secondary", False),
    "Q4_stroke_SEE_all_cause_death_read_as_stroke_or_SE": (
        "Stroke or systemic embolism", "Yearly Event Rate for Composite Endpoint of Stroke/SEE/All Cause Death",
        "secondary", False),
    "Q11_recurrent_DVT_alone_read_as_recurrent_VTE_composite": (
        "Trial-reported recurrent VTE composite", {"measure": "Number of Participants With Recurrent Symptomatic DVT",
        "description": "Symptomatic DVT which occured from randomisation to end of ptp. All suspected recurrent VTEs and "
                       "all deaths and bleeding events were evaluated by an independent central adjudication committee"},
        "secondary", False),
    "Q12_description_boilerplate_read_as_the_measure": (
        "Trial-reported recurrent VTE composite", {"measure": "Number of Participants With Acute Coronary Syndrome (ACS)",
        "description": "Any ACS occurring during the conduct of the study (centrally adjudicated). All suspected recurrent "
                       "VTEs were evaluated by an independent central adjudication committee"}, "secondary", False),
    "Q5_all_cause_death_or_hospitalisation_read_as_all_cause_mortality": (
        "All-cause mortality", "Number of Participants With First Occurrence of All-Cause Mortality or All-Cause "
        "Hospitalization (Adjudicated)", "secondary", False),
}
FALSE_CONCERN = {
    "Q6_all_causes_mortality_wording_unread": ("All-cause mortality", "Day 28 all causes mortality", "primary", True),
    "Q7_atrial_fibrillation_unread": ("Postoperative atrial fibrillation", "Atrial fibrillation AF documented by EKG",
                                      "primary", True),
    "Q8_diarrhoea_spelling_and_hyphen": ("Antibiotic-associated diarrhoea", "Incidence of antibiotic associated diarrhea",
                                         "primary", True),
    "Q9_CV_related_death_unread_in_MACE": (
        "3-point major adverse cardiovascular events", "Number of Participants With an Event of MACE (Confirmed "
        "CV-Related Death, Fatal and Nonfatal MI, and Fatal and Nonfatal Stroke)", "primary", True),
    "Q10_worsening_HF_members_unread": (
        "Composite cardiovascular death or worsening heart failure", "Subjects Included in the Composite Endpoint of CV "
        "Death, Hospitalization Due to Heart Failure or Urgent Visit Due to Heart Failure.", "primary", True),
}
CONTROLS = {
    # round 8 (PLATO): a bleeding outcome never matches an efficacy composite
    "C1_bleeding_never_matches_MACE": ("Major adverse cardiovascular events: cardiovascular death, myocardial infarction, "
                                       "or stroke", "Participants With Any Major Bleeding Event", "primary", False),
    # the deliberate design rule: HF hospitalisation inside a registered secondary composite counts as prespecified
    "C2_HHF_inside_a_registered_secondary_composite_kept": (
        "Hospitalization for heart failure", "Time to Occurrence of Cardiovascular (CV) Death or Hospitalization for "
        "Heart Failure (HHF)", "secondary", True),
    # VTE-related death is part of recurrent VTE, never all-cause death
    "C3_VTE_related_death_is_not_all_cause_death": (
        "Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)",
        "Recurrent VTE or VTE-related death", "primary", True),
    # the English 'see' is never systemic embolism
    "C4_see_in_prose_is_not_embolism": ("Stroke", "Stroke (see protocol section 7)", "primary", True),
    # omega-3 (20929341): once 'fatal CVD' is read, a composite with cardiac arrest and cardiac interventions is still
    # not plain MACE
    "C6_arrest_and_PCI_CABG_are_extra_components": (
        "Major vascular events / MACE", "Major cardiovascular events, which comprises fatal cardiovascular diseases (CVD), "
        "non-fatal myocardial infarction, non-fatal cardiac arrest, non-fatal stroke and cardiac interventions (PCI and "
        "CABG)", "primary", False),
    # 'within the duration of the study' is the study period, not a duration-of-the-condition measure
    "C7_study_duration_is_not_another_measure": (
        "Antibiotic-associated diarrhea", "Incidence of antibiotic-associated diarrhea within the duration of the study",
        "primary", True),
    # a 3-point MACE registered with plain CV death still matches
    "C5_plain_3_point_MACE_still_matches": (
        "3-point major adverse cardiovascular events", "Time to first occurrence of cardiovascular death, non-fatal "
        "myocardial infarction or non-fatal stroke", "primary", True),
}


def run(harness_root: Path) -> dict:
    sys.path.insert(0, str(harness_root))
    for m in [k for k in sys.modules if k == "harness" or k.startswith("harness.")]:
        del sys.modules[m]
    rob2 = importlib.import_module("harness.rob2")
    out = {}
    for name, (pooled, reg, kind, right) in {**FALSE_REASSURANCE, **FALSE_CONCERN, **CONTROLS}.items():
        row = reg if isinstance(reg, dict) else {"measure": reg, "description": ""}
        d = rob2._outcome_match_detail(pooled, row, None,
                                       allow_secondary_component_subset=(kind == "secondary"))
        out[name] = {"fired": d["matched"] != right, "got": {"matched": d["matched"], "method": d["method"],
                                                            "pooled": d["pooled_components"],
                                                            "registered": d["registered_components"]}}
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
