"""G1 semaglutide-obesity-weight: the registered arm object requires semaglutide 2.4 mg (topics/...json
arm_object.dose.required). The dose parser read only whitelisted doses with '.'/',' decimals, so O'Neil 2018 (PMID
30122305; once-daily 0·05-0·4 mg, Lancet middle-dot decimals) stayed NOT_DERIVABLE and X-DOSE never fired.
Radius measured over every held record of every arm-object topic (1,139): 7 refusal changes, all semaglutide-weight;
1 reaches the served screen's arm stage (O'Neil, a seeded member record) -- served pool unchanged."""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, ROOT)

from harness import arm_object  # noqa: E402

CFG = json.load(open(os.path.join(ROOT, "topics", "semaglutide-obesity-weight.json"), encoding="utf-8"))
ONEIL = {"id": "30122305", "id_type": "pmid",
         "title": "Efficacy and safety of semaglutide compared with liraglutide and placebo for weight loss in patients with "
                  "obesity: a randomised, double-blind, placebo and active controlled, dose-ranging, phase 2 trial.",
         "abstract": "METHODS: We randomly assigned participants (6:1) to each active treatment group (ie, semaglutide [0·05 mg, "
                     "0·1 mg, 0·2 mg, 0·3 mg, or 0·4 mg; initiated at 0·05 mg per day and incrementally escalated every 4 "
                     "weeks] or liraglutide [3·0 mg]) or matching placebo group. All treatment doses were delivered "
                     "once-daily via subcutaneous injections. Eligible participants were adults without diabetes.",
         "pubtypes": ["Randomized Controlled Trial"]}


def _rec(title, abstract):
    return {"id": "1", "id_type": "pmid", "title": title, "abstract": abstract, "pubtypes": ["Randomized Controlled Trial"]}


def test_oneil_daily_doses_are_read_and_refused_by_the_registered_dose_rule():
    _, ref = arm_object.screen_refusal(ONEIL, CFG)
    assert ref["rule_id"] == "X-DOSE" and "0.05 mg, 0.1 mg, 0.2 mg, 0.3 mg, 0.4 mg" in ref["reason"]


def test_the_registered_dose_is_never_refused_in_either_decimal_style():
    for d in ("2.4 mg", "2·4 mg"):
        r = _rec("Once-weekly semaglutide in adults with overweight or obesity",
                 f"METHODS: Adults without diabetes were randomly assigned to once-weekly subcutaneous semaglutide {d} "
                 "or placebo, plus lifestyle intervention.")
        _, ref = arm_object.screen_refusal(r, CFG)
        assert not ref or ref["rule_id"] != "X-DOSE", d


def test_the_audit_rescreens_with_the_arm_object_stage_and_spans_the_stated_doses():
    import k_gap_exclusion_audit as audit
    cls, sub, d = audit.classify(ONEIL, CFG)
    assert (cls, sub.split(" (")[0]) == ("TRUE_SCOPE_DIFFERENCE", "DOSE_OUTSIDE_PROTOCOL_STATED")
    assert d["rule_id"] == "X-DOSE" and "semaglutide [0·05 mg" in d["span"]["text"]


def test_with_a_stale_recorded_rule_the_row_stays_inconsistent_never_named():
    # O'Neil's recorded funnel (counterfactual_members.json) still says X2 (the arm-name-as-population class acq fixed):
    # the current screen's X-DOSE does not reproduce it, so the row is INCONSISTENT and the trial stays ELIGIBLE until the
    # funnel is regenerated
    rows = json.load(open(os.path.join(ROOT, "outputs", "k_gap", "exclusion_audit.json"), encoding="utf-8"))["rows"]
    r = next(r for r in rows if r["slug"] == "semaglutide-obesity-weight" and r["pmid"] == "30122305")
    assert r["class"] == "INCONSISTENT" and r["subclass"].startswith("RULE_X-DOSE_NE_RECORDED_")


# --- plants from cross-vendor review NR-C23 (Codex; artefact F:/mh-nr101-codex/c23-g1-dose-parser/last_message.txt) ---
def _refused(abstract, title="Semaglutide in adults with obesity"):
    _, ref = arm_object.screen_refusal(_rec(title, "METHODS: Adults with obesity without diabetes were randomly assigned to "
                                                   + abstract + " RESULTS: x."), CFG)
    return bool(ref and ref["rule_id"] == "X-DOSE")


def test_c23_titration_and_run_in_text_never_refuses_a_2_4_mg_trial():
    assert not _refused("once-weekly semaglutide 0.25 mg escalated to 2.4 mg once weekly or placebo.")
    assert not _refused("semaglutide 0.25 mg during run-in. Participants were then randomly assigned to 2.4 mg once "
                        "weekly or placebo.")


def test_c23_arm_order_is_a_recorded_protocol_question_not_changed_here():
    # NR-C23: 'semaglutide 1.7 mg or 2.4 mg' is refused (first dose read) -- a known defect, KEPT deliberately: reading
    # every arm would also admit the 9-arm bimagrumab trial 41772149 to the served screen (population_none lists
    # 'bimagrumab'), a protocol decision for the registered owner. This plant pins the served behaviour until then.
    assert not _refused("semaglutide 2.4 mg or 1.7 mg once weekly, or placebo.")
    assert _refused("semaglutide 1.7 mg or 2.4 mg once weekly, or placebo.")


def test_c23_a_dose_is_a_whole_number():
    assert _refused("semaglutide 12.4 mg or 14 mg once weekly, or placebo.")       # 12.4 is not 2.4
