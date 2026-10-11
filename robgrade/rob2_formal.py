"""FORMAL RoB 2 (Cochrane Handbook v6.5, chapter 8; RoB 2 guidance, 22 Aug 2019): per trial per served outcome, the five
domains of the tool for individually randomised parallel-group trials, effect of ASSIGNMENT to intervention (the
intention-to-treat effect every served pool estimates).

This module is pure and deterministic: the signalling questions, the answer vocabulary, and the published algorithms
that map answers to a domain judgement and the domain judgements to an overall one. It never reads a source and never
calls a model. Answers come from:
  robgrade/rob2_typed.py   typed rules over structured data and regex over held text (each answer a verbatim span + the
                          sha256 of the source it was found in)
  scripts/rob2_dual.py    the recorded dual-model reading (codex + agy, blind to each other) and a recorded adjudicator,
                          for the questions no typed rule answers
and an answer without a source span is never used: it is 'NI' (no information), never guessed.

Answer vocabulary (RoB 2): Y yes, PY probably yes, PN probably no, N no, NI no information, NA not applicable.
Judgements: LOW, SOME_CONCERNS, HIGH. A domain whose answers cannot be obtained at all (no open source, D8) is
INSUFFICIENT_OPEN_SOURCE -- never folded into a judgement as if it were 'no information' read from a source.
"""
from __future__ import annotations

import hashlib
import json

FAMILY = "formal-rob2-v1"            # rob2.canonical() serves verdicts only for a family other than the machine one
ANSWERS = ("Y", "PY", "PN", "N", "NI", "NA")
LOW, SOME, HIGH = "LOW", "SOME_CONCERNS", "HIGH"
INSUFFICIENT = "INSUFFICIENT_OPEN_SOURCE"
ORDER = {LOW: 0, SOME: 1, HIGH: 2}

# The signalling questions, verbatim in substance from the RoB 2 tool (individually randomised, effect of assignment).
QUESTIONS = {
    "1.1": "Was the allocation sequence random?",
    "1.2": "Was the allocation sequence concealed until participants were enrolled and assigned to interventions?",
    "1.3": "Did baseline differences between intervention groups suggest a problem with the randomisation process?",
    "2.1": "Were participants aware of their assigned intervention during the trial?",
    "2.2": "Were carers and people delivering the interventions aware of participants' assigned intervention during the trial?",
    "2.3": "If Y/PY/NI to 2.1 or 2.2: Were there deviations from the intended intervention that arose because of the trial context?",
    "2.4": "If Y/PY to 2.3: Were these deviations likely to have affected the outcome?",
    "2.5": "If Y/PY/NI to 2.4: Were these deviations from intended intervention balanced between groups?",
    "2.6": "Was an appropriate analysis used to estimate the effect of assignment to intervention?",
    "2.7": "If N/PN/NI to 2.6: Was there potential for a substantial impact (on the result) of the failure to analyse "
           "participants in the group to which they were randomized?",
    "3.1": "Were data for this outcome available for all, or nearly all, participants randomized?",
    "3.2": "If N/PN/NI to 3.1: Is there evidence that the result was not biased by missing outcome data?",
    "3.3": "If N/PN to 3.2: Could missingness in the outcome depend on its true value?",
    "3.4": "If Y/PY/NI to 3.3: Is it likely that missingness in the outcome depended on its true value?",
    "4.1": "Was the method of measuring the outcome inappropriate?",
    "4.2": "Could measurement or ascertainment of the outcome have differed between intervention groups?",
    "4.3": "If N/PN/NI to 4.1 and 4.2: Were outcome assessors aware of the intervention received by study participants?",
    "4.4": "If Y/PY/NI to 4.3: Could assessment of the outcome have been influenced by knowledge of intervention received?",
    "4.5": "If Y/PY/NI to 4.4: Is it likely that assessment of the outcome was influenced by knowledge of intervention received?",
    "5.1": "Were the data that produced this result analysed in accordance with a pre-specified analysis plan that was "
           "finalized before unblinded outcome data were available for analysis?",
    "5.2": "Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple "
           "eligible outcome measurements (e.g. scales, definitions, time points) within the outcome domain?",
    "5.3": "Is the numerical result being assessed likely to have been selected, on the basis of the results, from multiple "
           "eligible analyses of the data?",
}
DOMAINS = {"D1": ("1.1", "1.2", "1.3"), "D2": ("2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"),
           "D3": ("3.1", "3.2", "3.3", "3.4"), "D4": ("4.1", "4.2", "4.3", "4.4", "4.5"), "D5": ("5.1", "5.2", "5.3")}
DOMAIN_NAMES = {"D1": "Bias arising from the randomization process",
                "D2": "Bias due to deviations from intended interventions (effect of assignment)",
                "D3": "Bias due to missing outcome data", "D4": "Bias in measurement of the outcome",
                "D5": "Bias in selection of the reported result"}


def side(a):
    """'Y' for Y/PY, 'N' for N/PN, else the answer itself (NI, NA, None)."""
    return "Y" if a in ("Y", "PY") else "N" if a in ("N", "PN") else a


def _a(ans, q):
    v = ans.get(q)
    v = v.get("answer") if isinstance(v, dict) else v
    return v if v in ANSWERS else "NI"          # an unanswered question is NO INFORMATION, never a favourable default


def _worst(*js):
    return max(js, key=lambda j: ORDER[j])


# ------------------------------------------------------------------------------------------------ domain algorithms
# Each returns (judgement, path): the path names the algorithm branch, so a reader can re-trace it.

def judge_d1(ans):
    a11, a12, a13 = (side(_a(ans, q)) for q in ("1.1", "1.2", "1.3"))
    if a12 == "N":
        return HIGH, "1.2 N/PN: allocation not concealed"
    if a12 == "NI":
        return (HIGH, "1.2 NI and 1.3 Y/PY: baseline imbalance with unknown concealment") if a13 == "Y" else \
               (SOME, "1.2 NI: concealment not reported")
    if a13 == "Y":
        return SOME, "1.2 Y/PY but 1.3 Y/PY: baseline differences suggest a problem"
    if a11 == "N":
        return SOME, "1.1 N/PN: sequence not random, though concealed"
    return LOW, "1.2 Y/PY, 1.3 N/PN/NI, 1.1 Y/PY/NI"


def judge_d2(ans):
    a21, a22, a23, a24, a25, a26, a27 = (side(_a(ans, q)) for q in DOMAINS["D2"])
    # Part 1: deviations from intended interventions
    if a21 == "N" and a22 == "N":
        p1, why1 = LOW, "2.1 and 2.2 N/PN: participants and carers unaware"
    elif a23 == "N":
        p1, why1 = LOW, "2.3 N/PN: no deviations arising from the trial context"
    elif a23 == "Y" and a24 == "Y" and a25 in ("N", "NI"):
        p1, why1 = HIGH, "2.3 Y/PY, 2.4 Y/PY, 2.5 N/PN/NI: unbalanced deviations affecting the outcome"
    else:
        p1, why1 = SOME, "awareness without information that excludes outcome-relevant deviations"
    # Part 2: analysis
    if a26 == "Y":
        p2, why2 = LOW, "2.6 Y/PY: appropriate analysis (ITT / modified ITT)"
    elif a27 == "Y":
        p2, why2 = HIGH, "2.6 N/PN/NI and 2.7 Y/PY: substantial impact of not analysing as randomised"
    else:
        p2, why2 = SOME, "2.6 N/PN/NI and 2.7 N/PN/NI"
    j = _worst(p1, p2)
    return j, f"part 1 {p1} ({why1}); part 2 {p2} ({why2})"


def judge_d3(ans):
    a31, a32, a33, a34 = (side(_a(ans, q)) for q in DOMAINS["D3"])
    if a31 == "Y":
        return LOW, "3.1 Y/PY: outcome data for (nearly) all randomised"
    if a32 == "Y":
        return LOW, "3.2 Y/PY: evidence the result is not biased by missing data"
    if a33 == "N":
        return LOW, "3.3 N/PN: missingness could not depend on the true value"
    if a34 == "N":
        return SOME, "3.3 Y/PY/NI, 3.4 N/PN"
    return HIGH, "3.3 Y/PY/NI and 3.4 Y/PY/NI: missingness likely depended on the true value"


def judge_d4(ans):
    a41, a42, a43, a44, a45 = (side(_a(ans, q)) for q in DOMAINS["D4"])
    if a41 == "Y":
        return HIGH, "4.1 Y/PY: inappropriate measurement method"
    if a42 == "Y":
        return HIGH, "4.2 Y/PY: ascertainment could differ between groups"
    unclear = a41 == "NI" or a42 == "NI"
    base = SOME if unclear else LOW
    why = "4.1 or 4.2 NI" if unclear else "4.1 and 4.2 N/PN"
    if a43 == "N":
        return base, f"{why}; 4.3 N/PN: assessors unaware"
    if a44 == "N":
        return base, f"{why}; 4.3 Y/PY/NI, 4.4 N/PN: assessment could not be influenced"
    if a45 == "N":
        return SOME, "4.4 Y/PY/NI, 4.5 N/PN"
    return HIGH, "4.4 Y/PY/NI and 4.5 Y/PY/NI: assessment likely influenced"


def judge_d5(ans):
    a51, a52, a53 = (side(_a(ans, q)) for q in DOMAINS["D5"])
    if a52 == "Y" or a53 == "Y":
        return HIGH, "5.2 or 5.3 Y/PY: result likely selected"
    if a51 == "Y" and a52 == "N" and a53 == "N":
        return LOW, "5.1 Y/PY, 5.2 and 5.3 N/PN"
    return SOME, "5.1 N/PN/NI, or 5.2/5.3 NI"


JUDGE = {"D1": judge_d1, "D2": judge_d2, "D3": judge_d3, "D4": judge_d4, "D5": judge_d5}


def overall(domain_judgements):
    """RoB 2 overall: HIGH if any domain HIGH; SOME_CONCERNS if any SOME_CONCERNS; LOW only if every domain LOW.
    The tool also allows HIGH for 'some concerns in multiple domains in a way that substantially lowers confidence': a
    judgement, never automated -- such a trial is flagged MULTIPLE_SOME_CONCERNS_FOR_REVIEW and stays SOME_CONCERNS.
    Any domain INSUFFICIENT_OPEN_SOURCE makes the overall NOT_ESTABLISHED (a missing domain is not a favourable one)."""
    js = dict(domain_judgements)
    missing = sorted(d for d in DOMAINS if js.get(d) not in ORDER)
    if missing:
        return {"judgement": "NOT_ESTABLISHED", "flags": [], "missing_domains": missing}
    worst = _worst(*(js[d] for d in DOMAINS))
    flags = ["MULTIPLE_SOME_CONCERNS_FOR_REVIEW"] if worst == SOME and sum(js[d] == SOME for d in DOMAINS) >= 3 else []
    return {"judgement": worst, "flags": flags, "missing_domains": []}


# ------------------------------------------------------------------------------------------------ assessment object

def answer(value, *, how, span=None, source_ref=None, source_sha256=None, rule_id=None, records=None, note=None):
    """One signalling-question answer. A Y/PY/PN/N answer must carry its verbatim span and the sha256 of the source the
    span is in; NI may stand alone (it is the absence of information). NA only where the tool's branch skips it."""
    if value not in ANSWERS:
        raise ValueError(f"answer {value!r} not in {ANSWERS}")
    if value in ("Y", "PY", "PN", "N") and not (span and source_sha256):
        raise ValueError(f"a {value} answer needs a verbatim span and its source sha256 (how={how})")
    return {"answer": value, "how": how, "span": span, "source_ref": source_ref, "source_sha256": source_sha256,
            "rule_id": rule_id, "records": list(records or []), "note": note}


def domain_object(dom, answers, insufficient=False, why=None):
    if insufficient:
        return {"domain": dom, "name": DOMAIN_NAMES[dom], "judgement": INSUFFICIENT, "path": why or
                "no open source carries the information this domain needs (D8)", "answers": answers}
    j, path = JUDGE[dom](answers)
    return {"domain": dom, "name": DOMAIN_NAMES[dom], "judgement": j, "path": path, "answers": answers}


def assessment(trial_id, outcome, answers_by_q, insufficient_domains=()):
    """answers_by_q: {qid: answer(...)}. -> the per-trial per-outcome RoB 2 object (family FAMILY)."""
    doms = {}
    for d, qs in DOMAINS.items():
        doms[d] = domain_object(d, {q: answers_by_q.get(q) or answer("NI", how="unanswered") for q in qs},
                                insufficient=d in insufficient_domains)
    ov = overall({d: o["judgement"] for d, o in doms.items()})
    obj = {"family": FAMILY, "trial": trial_id, "outcome": outcome, "domains": doms, "overall": ov}
    obj["sha256"] = hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return obj
