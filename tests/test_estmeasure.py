"""Effect-measure type system + three-field effect object (TIER-1 #2, audit 18).
Pooling compatibility is decided by CLASS, not reported label: mixing labels WITHIN a class (RALES's
Cox "relative risk" + EMPHASIS's "hazard ratio" — both first-event relative ratios) is compatible and
disclosed, not an alarm; mixing ACROSS classes (a recurrent-event rate ratio + a first-event hazard
ratio — the iv-iron defect) is a genuine incompatibility that must be flagged.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness import estmeasure as em  # noqa: E402


def test_three_field_object_labels_and_canonical():
    o = em.classify("RR", "relative risk of death, 0.70")
    assert o["reported_label"] == "RR" and o["canonical_estimand"] == "RISK_RATIO"
    assert o["statistical_model"] is None  # no model cue in this span -> not guessed


def test_cox_cue_recorded_but_does_not_change_class():
    # a Cox model cue is recorded informationally; the canonical stays by label. It does not matter for
    # mixing because a Cox "relative risk" and a "hazard ratio" are the SAME compatibility class anyway.
    o = em.classify("RR", "estimated with a Cox proportional-hazards model; relative risk 0.70")
    assert o["statistical_model"] == "cox_proportional_hazards"
    assert o["canonical_estimand"] == "RISK_RATIO"  # label-driven, never guessed to HR


def test_outcome_name_recurrent_does_not_upgrade_binary_rr():
    # 'recurrent VTE' is an OUTCOME NAME, not a recurrent-event model — must NOT become a rate ratio
    o = em.classify("RR", "recurrent symptomatic venous thromboembolism (RR 0.90)")
    assert o["canonical_estimand"] == "RISK_RATIO" and o["statistical_model"] is None


def test_within_class_label_mix_is_compatible_not_alarm():
    # RALES RR + EMPHASIS HR: both first-event relative ratios -> compatible_labels, NOT incompatible
    effs = [em.classify("RR", "relative risk of death 0.70"), em.classify("HR", "hazard ratio 0.63")]
    c = em.pool_compatibility(effs)
    assert c["status"] == "compatible_labels" and c["classes"] == ["FIRST_EVENT_RATIO"]


def test_across_class_mix_is_incompatible():
    # first-event hazard ratio + recurrent rate ratio -> incompatible (iv-iron defect)
    effs = [em.classify("HR", "hazard ratio, time to first event 0.39"),
            em.classify("IRR", "per 100 person-years, rate ratio 0.80")]
    c = em.pool_compatibility(effs)
    assert c["status"] == "incompatible"
    assert set(c["classes"]) == {"FIRST_EVENT_RATIO", "RATE"}


def test_single_estimand_is_homogeneous():
    effs = [em.classify("HR", "hazard ratio 0.82"), em.classify("HR", "hazard ratio 0.79")]
    assert em.pool_compatibility(effs)["status"] == "homogeneous"
