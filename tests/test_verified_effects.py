"""verified_effects: a committed full-text-verified EFFECT entry (the effect analogue of
verified_arms) is pooled for a declared-absent trial ONLY for the matching outcome, carries
fulltext_verified provenance, and verifies against its own committed source span. Reproducible:
the entry is committed source, rendered deterministically (no model call at build)."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.pipeline import _build_outcome  # noqa: E402

SPEC = {"name": "Heart-failure hospitalization", "keywords": ["heart failure hospitali"],
        "estimand": "RR", "primary": True}
# a trial whose ABSTRACT yields no extractable HF-hospitalisation number
INCLUDED = [{"id": "25176939", "id_type": "pmid", "label": "CONFIRM-HF"}]
REC = {"25176939": {"id": "25176939", "abstract": "CONFIRM-HF improved 6MWT distance; safety was similar."}}
VE = {"25176939": {"outcome": "Heart-failure hospitalization", "effect": 0.39, "ci_low": 0.19,
                   "ci_high": 0.82, "scale": "HR",
                   "source": "PMC4359359 Table 2: HF hospitalisation HR 0.39 (0.19-0.82), P=0.009"}}


def test_verified_effect_pooled_and_verified():
    o = _build_outcome(SPEC, "efficacy", INCLUDED, REC, ["ferric", "FCM"], ["placebo"],
                       verified_effects=VE)
    assert len(o["trials"]) == 1, o
    t = o["trials"][0]
    assert t["effect"] == 0.39 and t["scale"] == "HR" and t["provenance"] == "fulltext_verified"
    # verifies against its own committed span (0.39 is present there), not the abstract
    assert t["verified"] == "verified", t


def test_verified_effect_ignored_for_wrong_outcome():
    ve = {"25176939": dict(VE["25176939"], outcome="Some other outcome")}
    o = _build_outcome(SPEC, "efficacy", INCLUDED, REC, ["ferric"], ["placebo"], verified_effects=ve)
    assert o["trials"] == [] and len(o["declared_absent_trials"]) == 1, o


def test_no_verified_effects_leaves_trial_absent():
    o = _build_outcome(SPEC, "efficacy", INCLUDED, REC, ["ferric"], ["placebo"], verified_effects=None)
    assert o["trials"] == [] and len(o["declared_absent_trials"]) == 1, o


# --- pre-specified dose selection (approved-dose rule) ---
DSEL = {"19717844": {"outcome": "Stroke or systemic embolism", "dose": "dabigatran 150 mg",
                     "effect": 0.66, "ci_low": 0.53, "ci_high": 0.82, "scale": "RR",
                     "source": "RE-LY: 150 mg of dabigatran (relative risk, 0.66; 95% CI, 0.53 to 0.82)"}}
DSPEC = {"name": "Stroke or systemic embolism", "keywords": ["stroke or systemic embolism"],
         "estimand": "HR", "primary": True}
# the ABSTRACT reports the WRONG (110 mg) dose 0.91 — the pre-specified rule must override it
DINC = [{"id": "19717844", "id_type": "pmid", "label": "RE-LY"}]
DREC = {"19717844": {"id": "19717844",
                     "abstract": "the primary outcome relative risk with dabigatran 110 mg was 0.91 (95% CI, 0.74 to 1.11)"}}


def test_dose_selection_overrides_abstract_dose_and_verifies():
    o = _build_outcome(DSPEC, "efficacy", DINC, DREC, ["dabigatran"], ["warfarin"], dose_selection=DSEL)
    assert len(o["trials"]) == 1
    t = o["trials"][0]
    # the approved 150 mg effect (0.66), NOT the abstract's 110 mg 0.91
    assert t["effect"] == 0.66 and t["provenance"] == "pre_specified_dose"
    assert t["verified"] == "verified"  # 0.66 present in its own source span
    assert "150 mg" in (t.get("dose") or "")


def test_dose_selection_only_for_matching_outcome():
    other = {"name": "Major bleeding", "keywords": ["major bleeding"], "estimand": "HR", "primary": True}
    o = _build_outcome(other, "harm", DINC, DREC, ["dabigatran"], ["warfarin"], dose_selection=DSEL)
    # dose_selection is for "Stroke or systemic embolism"; must NOT fire on a different outcome
    assert all(t.get("provenance") != "pre_specified_dose" for t in o["trials"])
