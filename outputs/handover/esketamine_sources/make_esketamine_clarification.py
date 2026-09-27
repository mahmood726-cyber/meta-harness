"""Esketamine-TRD review: Mahmood's RETROSPECTIVE protocol clarification on the oral antidepressant (OAD), recorded
with both messages verbatim, and the explicit eligibility field `oad_initiation` for TRANSFORM-1/-2/-3, Chen and
Takahashi, each from its own held source text (every span asserted before anything is written).
  PYTHONPATH=. python outputs/handover/esketamine_sources/make_esketamine_clarification.py"""
import hashlib, json

from harness.report_family import _witness_text

SLUG = "esketamine-trd-madrs"
PROTO = "protocols/esketamine-trd-madrs.md"
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def W(path, span):
    w = {"path": path, "sha256": sha(path), "span": span}
    assert " ".join(span.split()) in " ".join(_witness_text(".", w).split()), (path, span[:80])
    return w


proto_span = "- **Intervention:** intranasal esketamine, added to a newly-initiated oral antidepressant."
assert proto_span in open(PROTO, encoding="utf-8").read()
phase2_span = ("`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that the\n"
               "structured exclusion of phase 2 / phase II trials was declared in the protocol but\n"
               "not executable in the topic config.")
assert phase2_span in open(PROTO, encoding="utf-8").read()

clar = {
    "clarification_id": "esketamine-oad-initiation-2026-09-27",
    "topic": SLUG,
    "kind": "RETROSPECTIVE_PROTOCOL_CLARIFICATION",
    "decided_after_seeing_data": True,
    "label": "RETROSPECTIVE: decided after the trial set and its data had been seen",
    "clarifies": {"path": PROTO, "sha256": sha(PROTO), "span": proto_span},
    "messages": [
        {"order": 1, "by": "Mahmood", "how_it_reached_the_reviewer": "Dispatch chat relay",
         "verbatim": "newly started can be any time after randomisation as long as that is the intervention",
         "literal_reading": ("the oral antidepressant must be newly initiated at or after randomisation as part of the "
                             "randomised treatment strategy; under this reading Takahashi's study (OAD started in a "
                             "pre-randomisation lead-in) does NOT qualify"),
         "consequence_at_the_time": "Takahashi held PENDING_RULING_CONFIRMATION while the consequence was confirmed with Mahmood",
         "status": "REFINED_BY_MESSAGE_2"},
        {"order": 2, "by": "Mahmood", "how_it_reached_the_reviewer": "Dispatch chat relay",
         "verbatim": "I think include as esketamine is the intervention.",
         "reading": ("the randomised INTERVENTION is esketamine vs placebo; the oral antidepressant is background therapy "
                     "that may be newly initiated either at/after randomisation OR in a pre-randomisation lead-in, "
                     "provided it continues unchanged across arms"),
         "status": "GOVERNING"}],
    "field": "oad_initiation",
    "values": {
        "AT_OR_AFTER_RANDOMISATION": "QUALIFIES",
        "PRE_RANDOMISATION_LEAD_IN_CONTINUED_UNCHANGED": "QUALIFIES_DISCLOSED_DESIGN_DIFFERENCE",
        "NOT_NEWLY_INITIATED": "DOES_NOT_QUALIFY",
        "NOT_STATED": "UNRESOLVED"},
    "sensitivity_analysis": {"id": "exclude-lead-in-initiated",
                             "description": "the primary pool without trials whose OAD was initiated in a pre-randomisation lead-in",
                             "members_by_value": "PRE_RANDOMISATION_LEAD_IN_CONTINUED_UNCHANGED"},
}

TR = "evidence/acquisition_cascade/held/"
trials = [
    {"trial": "TRANSFORM-1", "ids": ["NCT02417064"], "value": "AT_OR_AFTER_RANDOMISATION",
     "witnesses": [W(TR + "NCT02417064/NCT02417064.json", "initiated on Day 1 and continued through the double-blind induction phase")]},
    {"trial": "TRANSFORM-2", "ids": ["PMID 31109201", "NCT02418585"], "value": "AT_OR_AFTER_RANDOMISATION",
     "witnesses": [W(TR + "TRANSFORM-2/NCT02418585.json", "participants will simultaneously initiate a new, open-label oral antidepressant"),
                   W(TR + "TRANSFORM-2/NCT02418585.json", "on Day 1 that will be continued for the duration of Double-Blind Induction Phase")]},
    {"trial": "TRANSFORM-3", "ids": ["NCT02422186"], "value": "AT_OR_AFTER_RANDOMISATION",
     "witnesses": [W(TR + "NCT02422186/NCT02422186.json", "initiated on Day 1 and continued through the double-blind induction Phase")]},
    {"trial": "Chen (China)", "ids": ["PMID 37025256"], "value": "AT_OR_AFTER_RANDOMISATION",
     "witnesses": [W("cache/esketamine-trd-madrs/ft_37025256.txt",
                     "Eligible patients were randomized 1:1 to receive intranasal esketamine or matching placebo, each in conjunction with a newly initiated oral antidepressant")]},
    {"trial": "Takahashi (Japan)", "ids": ["PMID 34696742"], "value": "PRE_RANDOMISATION_LEAD_IN_CONTINUED_UNCHANGED",
     "witnesses": [W("cache/esketamine-trd-madrs/ft_34696742.txt",
                     "Patients were treated with a new oral AD for 6 weeks (prospective lead-in phase); nonresponders were randomized (2:1:1:1) to placebo or esketamine (28-, 56-, or 84-mg) nasal spray along with the continued use of AD for 4 weeks"),
                   W("cache/esketamine-trd-madrs/ft_34696742.txt",
                     "received placebo or esketamine nasal spray on top of the oral AD that was continued unchanged from the prospective lead-in phase")],
     # the OAD rule is met under message 2, but the trial is ALSO excluded by a different, recorded rule
     "other_rule_conflict": {
         "state": "PENDING_PROTOCOL_CONFLICT",
         "screen_rule": "X-DESIGN",
         "rule": "X-DESIGN 'phase 2b' (topic config design_none, from the retrospective executable-screen amendment of 2026-09-16)",
         "amendment": {"path": PROTO, "sha256": sha(PROTO), "span": phase2_span},
         "why_pending": ("the amendment says the phase 2 exclusion 'was declared in the protocol', but the protocol as "
                         "registered (commit 5e2b43c6) contains no phase exclusion; Mahmood's ruling addresses the OAD "
                         "timing, not the phase. Takahashi is neither included nor excluded until Mahmood rules on the "
                         "phase 2 amendment for this trial."),
         "also_pending": "the trial randomises three fixed esketamine doses (28/56/84 mg) against one placebo arm: a multi-arm selection decision"}},
]

p = "docs/protocol_clarifications.json"
doc = {"_doc": ("Protocol clarifications decided AFTER the data were seen (RETROSPECTIVE), each with the verbatim messages, "
                "who sent them and how they reached the reviewer, and the explicit eligibility field they define. Read by "
                "harness/eligibility_field.py. Recorded by the evidence lane (Claude Opus 5.5), 2026-09-27."),
       "clarifications": [clar], "fields": {SLUG: trials}}
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print("wrote", p)
