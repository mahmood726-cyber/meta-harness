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
