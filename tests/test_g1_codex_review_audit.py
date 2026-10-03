"""Cross-vendor (codex) review of scripts/g1_exclusion_audit_tracker.py (registry/model_proposals/g1_codex_review.json,
group exclusion_audit_and_screen #6-#9): each finding's OWN failing input, asserting the expected behaviour. Each fails
on the pre-fix script and passes after it."""
import os
import sys
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, "scripts")]
import g1_exclusion_audit_tracker as m  # noqa: E402


def _key(slug, pmid):
    return m._key(slug, pmid) if hasattr(m, "_key") else str(pmid)


def test_6_rule_axis_met_does_not_outrank_another_axis_not_met():
    q = "Adults without diabetes were enrolled."
    it = {"slug": "test", "pmid": "1", "recorded_rule": "X1", "rec": {"title": "Randomized trial", "abstract": q}}
    with patch.object(m.xa, "_cfg", return_value={"include": {"population_any": ["diabetes"]}}), \
            patch.object(m, "consensus", return_value=({"design": "MET", "population": "NOT_MET"}, {})), \
            patch.object(m, "_full_text", return_value=None), \
            patch.dict(m.QUOTES, {_key("test", "1"): {"population": q}}, clear=True):
        cls, sc, by = m.refine(it, "INSUFFICIENT_RECORD", "design unclear", {"rule_id": "X1"})
    assert cls == "TRUE_SCOPE_DIFFERENCE" and sc.startswith("POPULATION_OUTSIDE_PROTOCOL"), (cls, sc)


def test_7_x1_is_answered_by_allocation_not_masking():
    it = {"slug": "test", "pmid": "1", "recorded_rule": "X1", "rec": {"title": "Study of a treatment"}}
    texts = ["Participants were randomly assigned to drug or usual care in an open-label trial.",
             "This double-blind placebo-controlled study assigned participants alternately, without randomization."]
    got = []
    with patch.object(m.xa, "_cfg", return_value={"include": {}}), patch.object(m, "consensus", return_value=({}, {})):
        for ft in texts:
            with patch.object(m, "_full_text", return_value=ft):
                got.append(m.refine(it, "INSUFFICIENT_RECORD", "design unclear", {"rule_id": "X1"})[0])
    assert got == ["SCREENER_ERROR", "TRUE_SCOPE_DIFFERENCE"]
    # ... and where the protocol DOES require double-blind, a randomised open-label trial is outside it
    with patch.object(m.xa, "_cfg", return_value={"include": {"design_double_blind": True}}), \
            patch.object(m, "consensus", return_value=({}, {})), patch.object(m, "_full_text", return_value=texts[0]):
        assert m.refine(it, "INSUFFICIENT_RECORD", "design unclear", {"rule_id": "X1"})[0] == "TRUE_SCOPE_DIFFERENCE"


def test_8_a_sentence_about_earlier_trials_says_nothing_about_this_one():
    it = {"slug": "test", "pmid": "1", "recorded_rule": "X-DESIGN", "rec": {"title": "Treatment trial"}}
    base = {"rule_id": "X-DESIGN", "reason": "not double-blind/placebo-controlled"}
    ft = "This randomized, double-blind, placebo-controlled trial enrolled adults. Earlier trials were open-label."
    with patch.object(m.xa, "_cfg", return_value={"include": {"design_double_blind": True}}), \
            patch.object(m, "consensus", return_value=({}, {})), patch.object(m, "_full_text", return_value=ft):
        assert m.refine(it, "INSUFFICIENT_RECORD", "masking unclear", base)[0] == "SCREENER_ERROR"
    # control: the same words about THIS trial still exclude it
    with patch.object(m.xa, "_cfg", return_value={"include": {"design_double_blind": True}}), \
            patch.object(m, "consensus", return_value=({}, {})), \
            patch.object(m, "_full_text", return_value="This randomized trial was open-label."):
        assert m.refine(it, "INSUFFICIENT_RECORD", "masking unclear", dict(base))[0] == "TRUE_SCOPE_DIFFERENCE"


def test_9_reader_verdicts_are_per_topic():
    q = "Adults with diabetes were enrolled."
    rows = [{"slug": slug, "pmid": "1",
             "verification": {"state": "VERIFIER_PASS", "axes": {"population": {"verdict": v, "located": {"match": "VERBATIM"}}}},
             "claim": {"axes": {"population": {"quote": q}}}}
            for slug, v in [("diabetes-topic", "MET"), ("non-diabetes-topic", "NOT_MET")]]
    it = {"slug": "diabetes-topic", "pmid": "1", "recorded_rule": "X1",
          "rec": {"title": "Randomized trial in adults with diabetes", "abstract": q}}
    with patch.dict(m.AXES, {}, clear=True), patch.dict(m.AXES2, {}, clear=True), patch.dict(m.QUOTES, {}, clear=True), \
            patch.object(m.os.path, "exists", return_value=True), patch.object(m.xa, "_j", return_value={"rows": rows}), \
            patch.object(m.xa, "_cfg", return_value={"include": {"population_any": ["diabetes"]}}):
        m.load_axes()
        assert m.refine(it, "SCREENER_ERROR", "BODY_RCT_MISSED", {"rule_id": "X1"})[0] == "SCREENER_ERROR"
        it2 = dict(it, slug="non-diabetes-topic")
        assert m.refine(it2, "SCREENER_ERROR", "BODY_RCT_MISSED", {"rule_id": "X1"})[0] == "TRUE_SCOPE_DIFFERENCE"
