"""Contextual 'probably' answers (outputs/robgrade/CONTEXTUAL_POLICY.md; Mahmood 12 Oct, signing item 3).

Pure logic, no model call: which questions a contextual pass may read (ni_targets), how a reading is verified
(verify), how two blind readings and an adjudication combine (combine), and how the result is applied to a v3.1 object
(apply). The model calls live in scripts/rob2_contextual.py. Only an asked NI answer may change, only to PY or PN, only
with a verbatim context quote from an open source that the rationale refers to; the answer is stored as contextual,
never silently, with every reader's context.
"""
import copy
import re
import unicodedata

from robgrade import rob2_formal as rf

CONTEXTUAL = ("PY", "PN")
QUOTE_MAX = 300
HOW = "contextual (Cochrane Handbook 8.2.3): the sources give context, not a direct statement"
# Not context (C3): reasoning from what trials usually do (codex round 1), or EXPLICITLY from memory or outside
# sources (codex rounds 2-3). Narrowed in round 3: "are known" etc. also word legitimate mechanisms, so they are not
# listed; the mechanical guards are that the rationale refers to the quote AND the quote is about the question.
# Split in round 6 (codex): MEMORY (from outside the shown sources) is never context; USUAL ("what trials usually
# do") is not context for a question about this trial's own CONDUCT, but the setting-based questions (below) reason
# from the clinical setting and may word a mechanism with "commonly" etc.
USUAL = re.compile(r"\b(?:usually|typically|generally|commonly|most (?:trials|studies)|standard practice|in general|"
                   r"as is (?:usual|common)|tend to|are often|is often|likely in (?:most|such) trials)\b", re.I)
MEMORY = re.compile(r"\b(?:remember|recall|from memory|training data|my training|i know|from the literature|"
                    r"prior knowledge|knowledge of this trial|this trial is known|previously reported|"
                    r"published (?:elsewhere|protocol|report)|other (?:reports|publications|sources)|"
                    r"(?:an? )?(?:earlier|another|previous|separate) (?:article|paper|report|publication))\b", re.I)
GENERIC = re.compile(f"(?:{USUAL.pattern})|(?:{MEMORY.pattern})", re.I)          # both (kept for reference)
_WORD = re.compile(r"[a-z0-9]{5,}")
# The quote must be ABOUT the signalling question (codex round 3): it contains at least one of the question's topic
# stems (substring match on the normalised quote). Pre-registered; conservative -- a context that does not name the
# question's topic stays NI.
QUESTION_TERMS = {
    # 1.1 and 1.2 also take TRIAL-CONDUCT context: the Handbook's own 8.2.3 example is a large trial run by an
    # experienced clinical trials unit (codex round 4 -- the round-3 gate rejected exactly that example)
    "1.1": ("random", "sequence", "computer", "block", "stratif", "minimi", "coin", "trials unit", "ctu", "regulator",
            "coordinating cent", "multicent", "multi-cent", "sponsor", "contract research"),
    "1.2": ("conceal", "allocation", "central", "envelope", "opaque", "sealed", "pharmacy", "interactive", "ivrs",
            "iwrs", "web", "telephone", "randomi", "trials unit", "ctu", "regulator", "coordinating cent", "multicent",
            "multi-cent", "sponsor", "contract research"),
    "1.3": ("baseline", "characteristic", "balanc", "similar", "comparable", "differ"),
    "2.1": ("blind", "mask", "placebo", "open-label", "open label", "aware", "double", "single", "identical", "sham"),
    "2.2": ("blind", "mask", "placebo", "open-label", "open label", "aware", "double", "single", "identical", "sham",
            "investigator", "staff", "clinician", "physician", "nurse"),
    "2.3": ("deviat", "protocol", "crossover", "cross-over", "switch", "adheren", "complian", "contamin", "co-interven",
            "rescue"),
    "2.4": ("deviat", "affect", "outcome", "crossover", "cross-over", "switch", "rescue"),
    "2.5": ("balanc", "deviat", "both groups", "similar", "crossover", "switch"),
    "2.6": ("intention", "itt", "analys", "randomi", "modified", "per-protocol", "per protocol", "full analysis"),
    "2.7": ("exclu", "analys", "randomi", "withdr", "missing", "per-protocol", "per protocol"),
    "3.1": ("follow", "lost", "missing", "complet", "withdr", "dropout", "drop-out", "drop out", "retention", "available",
            "attrition", "discontinu"),
    "3.2": ("sensitivity", "imput", "missing", "robust"),
    "3.3": ("missing", "withdr", "dropout", "drop-out", "lost", "reason", "discontinu", "adverse", "worsen", "death",
            "follow"),
    "3.4": ("missing", "withdr", "dropout", "drop-out", "lost", "reason", "discontinu", "adverse", "worsen", "death",
            "follow"),
    "4.1": ("measur", "assess", "instrument", "scale", "valid", "definition", "defined", "criteria"),
    "4.2": ("measur", "assess", "ascertain", "schedule", "both groups", "same", "differ", "visit"),
    "4.3": ("assessor", "blind", "mask", "adjudicat", "committee", "aware", "independent", "evaluat"),
    "4.4": ("objective", "subjective", "mortality", "death", "judgement", "judgment", "self-report", "assess",
            "adjudicat", "laboratory", "influenc"),
    "4.5": ("objective", "subjective", "mortality", "death", "judgement", "judgment", "self-report", "assess",
            "adjudicat", "laboratory", "influenc"),
    "5.1": ("plan", "protocol", "prespecif", "pre-specif", "predefin", "pre-defin", "regist", "statistical analysis"),
    "5.2": ("outcome", "measur", "primary", "prespecif", "pre-specif", "regist", "protocol", "time point", "scale"),
    "5.3": ("analys", "prespecif", "pre-specif", "protocol", "plan", "adjust", "model", "subgroup"),
}


# SETTING-BASED questions, where the RoB 2 guidance asks the assessor to reason from the trial's setting rather than
# from a reported procedure: 2.1/2.2 (awareness can follow from the interventions themselves, e.g. surgery v
# physiotherapy; codex round 6) and 3.3/3.4 (whether missingness could / is likely to depend on the outcome's true
# value; codex rounds 3-5). For them the topic gate and the USUAL markers are not applied; MEMORY still is.
SETTING_BASED = {"2.1", "2.2", "3.3", "3.4"}
TOPIC_GATE_EXEMPT = SETTING_BASED


def about_question(qid, quote):
    """The quote names the question's topic: at least one of QUESTION_TERMS[qid] occurs in it (3.3/3.4: exempt)."""
    if qid in TOPIC_GATE_EXEMPT:
        return True
    t = _norm(quote)
    return any(term in t for term in QUESTION_TERMS.get(qid, ()))


def ni_targets(obj):
    """The asked questions whose answer is NI, in question order: never 3.2 (no NI option), never a question in an
    INSUFFICIENT_OPEN_SOURCE domain."""
    out = []
    for d, dom in obj["domains"].items():
        if dom["judgement"] == rf.INSUFFICIENT:
            continue
        ans = rf.normalize_answers(d, dom["answers"])
        asked = rf.applicable(d, ans)
        out += [q for q in rf.DOMAINS[d] if q in asked and q not in rf.NI_NOT_AN_OPTION and rf._a(ans, q) == "NI"]
    return out


def _norm(s):
    """The SAME normalisation as scripts/rob2_dual._norm (NFKC, case, dashes, whitespace): one quote, one verdict."""
    s = unicodedata.normalize("NFKC", s or "").lower()
    s = s.replace("−", "-").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", s).strip()


def _text(src):
    """A source's text, whichever key holds it (an abstract is shown under 'abstract'; agy round 2)."""
    return src.get("text") or src.get("abstract") or ""


def refers_to(rationale, quote):
    """The rationale names at least one word of five or more letters from the quote: it argues FROM the quoted context."""
    return bool(set(_WORD.findall(_norm(rationale))) & set(_WORD.findall(_norm(quote))))


def verify(reading, sources, targets):
    """{qid: {answer, quote, source_id, source_sha256, rationale} | {answer: NI[, dropped]}} for every TARGET question.
    PY/PN only; the rationale is neither empty, generic nor from memory, and refers to the quote; the quote (8-300
    characters) is found verbatim (whitespace/case/dash-normalised) in the OPEN source it names."""
    srcs = {s["id"]: s for s in sources if s.get("open_for_prompt")}
    targets = list(targets)
    out = {}
    for a in (reading or {}).get("answers") or []:
        q, v = a.get("qid"), a.get("answer")
        if q not in targets or q in out:
            continue
        if v in ("Y", "N"):
            out[q] = {"answer": "NI", "dropped": {"answer": v, "why": "ONLY_PY_PN_MAY_BE_CONTEXTUAL"}}
            continue
        if v not in CONTEXTUAL:
            out[q] = {"answer": "NI", "rationale": a.get("rationale")}
            continue
        why, quote = (a.get("rationale") or "").strip(), a.get("quote") or ""
        if not why or MEMORY.search(why) or (q not in SETTING_BASED and USUAL.search(why)):
            out[q] = {"answer": "NI", "dropped": {"answer": v, "rationale": why[:300],
                                                  "why": "RATIONALE_EMPTY_GENERIC_OR_FROM_MEMORY (not context)"}}
            continue
        if len(quote) > QUOTE_MAX:
            out[q] = {"answer": "NI", "dropped": {"answer": v, "why": "QUOTE_OVER_300_CHARACTERS"}}
            continue
        s = srcs.get(a.get("source_id"))
        if s is None or len(_norm(quote)) < 8 or _norm(quote) not in _norm(_text(s)):
            out[q] = {"answer": "NI", "dropped": {"answer": v, "quote": quote[:300], "source_id": a.get("source_id"),
                                                  "why": "QUOTE_NOT_FOUND_IN_NAMED_OPEN_SOURCE"}}
            continue
        if not refers_to(why, quote):
            out[q] = {"answer": "NI", "dropped": {"answer": v, "rationale": why[:300],
                                                  "why": "RATIONALE_DOES_NOT_REFER_TO_THE_QUOTED_CONTEXT"}}
            continue
        if not about_question(q, quote):
            out[q] = {"answer": "NI", "dropped": {"answer": v, "quote": quote[:300],
                                                  "why": "QUOTE_NOT_ABOUT_THE_QUESTION"}}
            continue
        out[q] = {"answer": v, "quote": quote, "source_id": s["id"], "source_sha256": s["sha256"], "rationale": why}
    for q in targets:                                  # a target the reader did not answer stays NI (agy round 1)
        out.setdefault(q, {"answer": "NI", "rationale": None})
    return out


def _ctx(who, x):
    return {"who": who, "quote": x["quote"], "source_id": x["source_id"], "source_sha256": x["source_sha256"],
            "rationale": x.get("rationale")}


def combine(a, b, adjudicated):
    """{qid: decision}. Both readers the same PY/PN -> it, with BOTH readers' contexts (they may cite different
    sources; codex/agy round 2); both NI -> NI; a disagreement -> the adjudicator's verified PY/PN/NI, recorded as its
    own. Agreement is never overridden."""
    out = {}
    for q in sorted(set(a) | set(b)):
        x, y = a.get(q) or {"answer": "NI"}, b.get(q) or {"answer": "NI"}
        if x["answer"] == y["answer"]:
            if x["answer"] in CONTEXTUAL:
                out[q] = dict(x, decided_by="both readers", context=[_ctx("reader 1", x), _ctx("reader 2", y)])
            else:
                out[q] = {"answer": "NI", "decided_by": "both readers: no context"}
        elif q in adjudicated:
            j = adjudicated[q]
            if j.get("answer") in CONTEXTUAL:
                out[q] = dict(j, decided_by="adjudicator", context=[_ctx("adjudicator", j)])
            else:
                out[q] = {"answer": "NI", "decided_by": "adjudicator", "rationale": j.get("rationale")}
        else:
            out[q] = {"answer": "NI", "decided_by": "no contextual answer agreed"}
    return out


def apply(obj, contextual, records):
    """A new assessment object. Each target decided PY/PN replaces its NI (stored as contextual, with every reader's
    context); every other answer is kept as is; a contextual answer on a question the new answers no longer ASK is NA
    (agy round 2); the same engine re-judges and re-labels. Every decision, an NI included, is kept in
    contextual_audit with its records (codex/agy round 2). Refuses a non-target or a Y/N."""
    targets = set(ni_targets(obj))
    answers, insufficient = {}, []
    for d, dom in obj["domains"].items():
        answers.update(copy.deepcopy(dom["answers"]))   # never share answer dicts with the v3.1 object (aliasing)
        if dom["judgement"] == rf.INSUFFICIENT:
            insufficient.append(d)
    audit = {}
    for q, c in contextual.items():
        if c["answer"] in ("Y", "N"):
            raise ValueError(f"{q}: a contextual answer is PY or PN, never {c['answer']}")
        if q not in targets:
            raise ValueError(f"{q} is not an asked NI question: a contextual answer may only replace NI")
        audit[q] = {"answer": c["answer"], "decided_by": c.get("decided_by"), "rationale": c.get("rationale"),
                    "records": list(records.get(q) or [])}
        if c["answer"] not in CONTEXTUAL:
            continue
        a = rf.answer(c["answer"], how=HOW, span=c["quote"], source_ref=c["source_id"], source_sha256=c["source_sha256"],
                      records=records.get(q) or [], note=f"{c.get('decided_by')}: {c.get('rationale') or ''}".strip())
        a["basis"] = "contextual"
        a["context"] = copy.deepcopy(c.get("context") or [])
        answers[q] = a
    for d, qs in rf.DOMAINS.items():                   # an upstream contextual answer can close a branch
        asked = rf.applicable(d, {q: answers.get(q) or {"answer": "NI"} for q in qs})
        for q in qs:
            if q not in asked and (answers.get(q) or {}).get("basis") == "contextual":
                answers[q] = rf.answer("NA", how="not asked once an upstream question was answered contextually")
    new = rf.assessment(obj["trial"], obj["outcome"], answers, insufficient_domains=insufficient)
    # EXTEND the incoming audit: a later pass must not erase an earlier pass's decisions
    new["contextual_audit"] = dict(copy.deepcopy(obj.get("contextual_audit") or {}), **audit)
    return new
