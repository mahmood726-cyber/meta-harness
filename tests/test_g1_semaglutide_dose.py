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
