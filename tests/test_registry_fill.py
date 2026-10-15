"""K-gap fill phase 1 (CT.gov/AACT): the gates the registry-fill path adds beside g1_trial_acquire.gate, on the real
postings that exposed them (ASCEND NCT00135226, a 2x2 factorial; SALT NCT02345486)."""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(ROOT, "scripts"))
import g1_registry_fill as rf  # noqa: E402

OMEGA = {"include": {"intervention_any": ["omega-3", "omega 3", "fish oil", "icosapent"], "comparator_any": ["placebo"]}}
# the topic's REAL intervention terms (PR #100 r1): a 3-term subset passed SALT only via ONE shared token, which r1-2 rules out
CRYST = {"include": {"intervention_any": ["balanced crystalloid", "balanced crystalloids", "balanced solution",
                                          "balanced multielectrolyte", "buffered crystalloid", "Plasma-Lyte",
                                          "Plasmalyte", "Ringer's acetate", "lactated Ringer"],
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


# ---- PR #100 review round 1 (captain, 13 Oct): one plant per finding, each failing before its fix ----

def test_PLANT_r1_1_control_arm_must_be_the_comparator_not_an_active_factorial_arm():
    # ASCEND 2x2: omega-3 v the ACTIVE aspirin arm passed every check ('Aspirin' is neither the intervention nor placebo)
    assert rf.arm_identity(_r(689, 7740, 658, 7740), _held(ASCEND_G, ASCEND_T), OMEGA).startswith(
        "REFUSED:CONTROL_ARM_NOT_THE_COMPARATOR")


def test_PLANT_r1_2_one_shared_token_is_not_identity():
    # two compounds sharing 'sodium': the arm must carry a WHOLE intervention term, not any one token of one
    bicarb = {"include": {"intervention_any": ["sodium bicarbonate"], "comparator_any": ["saline", "sodium chloride"]}}
    g = [{"group": "x", "count": 10, "n": 100}, {"group": "y", "count": 12, "n": 100}]
    assert rf.arm_identity(_r(10, 100, 12, 100), _held(g, {"x": "Sodium Chloride 0.9%", "y": "Saline"}),
                           bicarb).startswith("REFUSED:EXPERIMENTAL_ARM_NOT_THE_INTERVENTION")
    assert rf.arm_identity(_r(10, 100, 12, 100), _held(g, {"x": "Sodium Bicarbonate 8.4%", "y": "Saline"}), bicarb) is None


def test_SALT_passes_under_its_real_topic_config():
    cfg = rf.config("balanced-crystalloids-vs-saline-mortality")
    assert rf.arm_identity(_r(72, 520, 68, 454), _held(SALT_G, SALT_T), cfg) is None


def test_PLANT_r1_3_failed_abstract_fetch_is_not_evidence_of_no_registration():
    assert rf.identity_why("FETCH_FAILED", "", "123") == "FETCH_FAILED:PUBMED_ABSTRACT"
    assert rf.identity_why("NO_ABSTRACT", "", "123") == "NO_ABSTRACT_TO_READ"
    assert rf.identity_why("FETCHED", "We randomised 200 adults.", "123") == "NO_REGISTRATION_STATED"
    assert rf.identity_why(None, "", None) == "NO_PMID_NO_REGISTRATION"


def test_PLANT_r1_4_no_posted_results_needs_a_source_that_answered():
    # 1 of 38 'no posted results' rows had its CT.gov fetch FAIL (captain, measured)
    assert rf.results_why({"NCT1": "NO_POSTED_RESULTS"}, {"NCT1": {"state": "FETCH_FAILED"}}).startswith(
        "RESULTS_STATE_UNESTABLISHED:NCT1")
    assert rf.results_why({"NCT1": "NO_POSTED_RESULTS"},
                          {"NCT1": {"state": "OK", "has_results": False}}) == "NO_POSTED_RESULTS"
    assert rf.results_why({"NCT1": "NO_POSTED_RESULTS"}, {"NCT1": {"state": "OK", "has_results": True}}) == \
        "RESULTS_POSTED_AFTER_SNAPSHOT:NCT1"


def test_PLANT_r1_5_a_prior_trial_named_in_an_abstract_is_not_the_reports_registration():
    ab = ("Background: The earlier FOURIER trial (NCT01764633) showed benefit. Methods: we randomised 300 patients. "
          "Trial registration: ClinicalTrials.gov NCT02000000.")
    own, other = rf.registration_ncts(ab)
    assert own == ["NCT02000000"] and other == ["NCT01764633"]
    own, other = rf.registration_ncts("Previous work (NCT01764633) is extended here. We randomised 300 adults.")
    assert own == [] and other == ["NCT01764633"]


def test_PLANT_r1_6_excerpt_test_is_not_vacuous_on_short_text():
    import g1_abstract_census as cen
    full = "Background: aspirin reduced events in a large randomised trial of adults. Results: HR 0.80 (0.70-0.90)."
    assert cen.classify("No abstract available.", full) == "DIFFERS"
    assert cen.classify("Results: HR 0.80 (0.70-0.90).", full) == "EXCERPT"
    assert cen.classify(full, full) == "FULL_ABSTRACT"


def test_PLANT_an_nct_the_registry_does_not_hold_is_not_a_resolved_identity(monkeypatch):
    # 'ODYSSEY JAPAN NCT02017898' (label typo; the trial is NCT02107898): CT.gov answers 404 'not found'. That is an
    # ANSWER about the identity, not a fetch failure, and the trial stays unresolved (13 Oct)
    import urllib.error
    from harness import http

    def boom(*_a, **_k):
        try:
            raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)
        except urllib.error.HTTPError as e:
            raise RuntimeError("GET failed after 3 tries") from e
    monkeypatch.setattr(http, "get_raw", boom)
    rf._CTG.pop("NCT02017898", None)
    assert rf.ctgov_has_results("NCT02017898")["state"] == "NCT_NOT_IN_REGISTRY"
    rf._CTG.pop("NCT02017898", None)
    assert rf.results_why({"NCT02017898": "NO_POSTED_RESULTS"},
                          {"NCT02017898": {"state": "NCT_NOT_IN_REGISTRY"}}) == "NCT_NOT_IN_REGISTRY:NCT02017898"
