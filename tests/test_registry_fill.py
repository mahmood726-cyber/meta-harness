"""K-gap fill phase 1 (CT.gov/AACT): the gates the registry-fill path adds beside g1_trial_acquire.gate, on the real
postings that exposed them (ASCEND NCT00135226, a 2x2 factorial; SALT NCT02345486)."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_registry_fill as rf  # noqa: E402

OMEGA = {"include": {"intervention_any": ["omega-3", "omega 3", "fish oil", "icosapent"], "comparator_any": ["placebo"]}}
CRYST = {"include": {"intervention_any": ["balanced crystalloid", "Plasma-Lyte", "lactated Ringer"],
                     "comparator_any": ["saline", "sodium chloride"]}}
ASCEND_G = [{"group": "a", "count": 658, "n": 7740}, {"group": "b", "count": 743, "n": 7740},
            {"group": "c", "count": 689, "n": 7740}, {"group": "d", "count": 712, "n": 7740}]
ASCEND_T = {"a": "Aspirin", "b": "Placebo Aspirin", "c": "Omega-3", "d": "Placebo Omega-3"}
SALT_G = [{"group": "s", "count": 68, "n": 454}, {"group": "b", "count": 72, "n": 520}]
SALT_T = {"s": "0.9% Sodium Chloride", "b": "Physiologically Balanced Fluid"}


def _held(groups, titles):
    return {"aact": {"NCTX": {"_reg": {"groups": {"1": groups}, "group_titles": titles}}}}


def _r(et, nt, ec, nc):
    return {"source_ref": "NCTX", "aact_outcome_id": "1", "events_t": et, "n_t": nt, "events_c": ec, "n_c": nc}


def test_PLANT_factorial_another_agents_arms_are_refused():
    # two readers took ASCEND's ASPIRIN pair for the omega-3 topic; the outcome gate passed it (13 Oct)
    assert rf.arm_identity(_r(658, 7740, 743, 7740), _held(ASCEND_G, ASCEND_T), OMEGA).startswith(
        "REFUSED:EXPERIMENTAL_ARM_NOT_THE_INTERVENTION")
    assert rf.arm_identity(_r(689, 7740, 743, 7740), _held(ASCEND_G, ASCEND_T), OMEGA).startswith(
        "REFUSED:CONTROL_IS_ANOTHER_AGENTS_PLACEBO")
    assert rf.arm_identity(_r(689, 7740, 712, 7740), _held(ASCEND_G, ASCEND_T), OMEGA) is None


def test_PLANT_short_arm_title_named_by_a_distinctive_token_and_orientation_checked():
    # 'Physiologically Balanced Fluid' names the balanced-crystalloid intervention (a whole-phrase match refused it)
    assert rf.arm_identity(_r(72, 520, 68, 454), _held(SALT_G, SALT_T), CRYST) is None
    assert rf.arm_identity(_r(68, 454, 72, 520), _held(SALT_G, SALT_T), CRYST).startswith(
        "REFUSED:EXPERIMENTAL_ARM_NOT_THE_INTERVENTION")


def test_ambiguous_or_effect_only_tuples_are_never_arm_checked_into_admission():
    twins = [{"group": "x", "count": 5, "n": 50}, {"group": "y", "count": 5, "n": 50}, {"group": "z", "count": 9, "n": 50}]
    assert rf.arm_identity(_r(5, 50, 9, 50), _held(twins, {"x": "Omega-3", "y": "Omega-3 high", "z": "Placebo"}),
                           OMEGA) == "REFUSED:ARM_AMBIGUOUS"
    assert rf.arm_identity({"source_ref": "NCTX", "aact_outcome_id": "1", "events_t": None, "n_t": None},
                           _held(ASCEND_G, ASCEND_T), OMEGA) == "REFUSED:ARM_IDENTITY_NOT_CHECKABLE_EFFECT_ONLY"


def test_answer_parser_takes_the_json_after_prose():
    from reproducible_ai import model_source as ms
    body = b'I have launched the test command.\n{"verdict": "FOUND", "events_t": 72}'
    rec = {"state": "RAN_OK"}
    orig = ms.replay
    ms.replay = lambda r: body
    try:
        assert rf._answer(rec) == {"verdict": "FOUND", "events_t": 72}
    finally:
        ms.replay = orig
