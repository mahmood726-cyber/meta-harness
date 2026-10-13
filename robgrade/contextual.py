"""Contextual 'probably' answers (outputs/robgrade/CONTEXTUAL_POLICY.md; Mahmood 12 Oct, signing item 3).

Pure logic, no model call: which questions a contextual pass may read (ni_targets), how a reading is verified
(verify), how two blind readings and an adjudication combine (combine), and how the result is applied to a v3.1 object
(apply). The model calls live in scripts/rob2_contextual.py. Only an asked NI answer may change, only to PY or PN, only
with a verbatim context quote from an open source that the rationale refers to; the answer is stored as contextual,
never silently, with every reader's context.
"""
import copy
import json
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
USUAL_TERMS = ("usually", "typically", "generally", "commonly", r"most (?:trials|studies)", "standard practice",
               "in general", r"as is (?:usual|common)", "tend to", "are often", "is often", r"likely in (?:most|such) trials")


def _usual(terms):
    return re.compile(r"\b(?:" + "|".join(terms) + r")\b", re.I)


USUAL = _usual(USUAL_TERMS)
MEMORY = re.compile(r"\b(?:remember|recall|from memory|training data|my training|i know|from the literature|"
                    r"prior knowledge|knowledge of this trial|this trial is known|previously reported|"
                    r"published (?:elsewhere|protocol|report)|other (?:reports|publications|sources)|"
                    r"(?:an? )?(?:earlier|another|previous|separate) (?:article|paper|report|publication))\b", re.I)
GENERIC = re.compile(f"(?:{USUAL.pattern})|(?:{MEMORY.pattern})", re.I)          # both (kept for reference)
# (A3, signed 13 Oct, codex candidate 1) A rationale may not rest on a DOCUMENT the readers were NOT SHOWN: "the
# original manuscript confirms ...", "according to the protocol ...". A document is named by kind; it is allowed only
# when a source of that kind was shown, or when the QUOTED SENTENCE of the shown source names the same document (the
# reader relies on that report, not on the unseen document -- the frozen r4 case: "A protocol was registered before
# enrolment and the statistical analysis plan published"; codex A3 r16: a mention in ANOTHER sentence is not that
# report). Documents are matched as words, with their aliases (SAP = statistical analysis plan, Fig. 1 = Figure 1,
# protocols = protocol; agy A3 r16). Kind None: never shown to a reader. "Protocol" as a concept (per-protocol,
# deviations from / adherence to the protocol) is not a document.
OTHER_REGISTERS = ("isrctn", "eudract", "euctr", "ctis", "anzctr", "actrn", "chictr", "ctri", "drks", "jprn", "umin",
                   "pactr", "irct", "ntr", "rebec", "slctr", "tctr", "kct", "cris", "who ictrp", "ictrp")
UNSEEN_DOCS = (
    (None, re.compile(r"\bprotocols?\b|statistical analysis plans?|\bsaps?\b|supplement(?:ary|al) (?:appendix|"
                      r"appendices|material|materials|data|table|file|information)|online supplement|\bappendix\b|"
                      r"\bappendices\b|online (?:material|data|content)|"
                      # another publication than the one shown: kind is not identity (codex A3 r19)
                      r"\b(?:original|main|primary|parent) (?:publication|paper|report|article|manuscript)\b|"
                      # a NAMED registry other than ClinicalTrials.gov: the shown registry is always ClinicalTrials.gov
                      # (an NCT record), so another register is another document (codex A3 r21)
                      r"\b(?:" + "|".join(OTHER_REGISTERS) + r")(?:[\s:#-]*[\d][\d-]*)?\b", re.I)),
    ("fulltext", re.compile(r"\bfull[- ]?(?:text|report|paper|article|publication)\b|\bmanuscripts?\b|\bmethods? section|"
                            r"\bresults? section|\bdiscussion section|\btables? \d+|\bfig(?:ure|s|ures|\.)? ?\d+|"
                            r"\bconsort\b|\bflow ?(?:chart|diagram)", re.I)),
    ("registry", re.compile(r"\bregist(?:ry|ries|ration|er)\b|clinicaltrials\.gov|\btrial register\b", re.I)),
    ("abstract", re.compile(r"\babstracts?\b", re.I)),
)
# (codex A3 r22) a TRIAL IDENTIFIER in the rationale must be one the readers were shown (in a shown source's text or
# its registry id): another trial's record is another document. RESIDUAL, stated: an unnumbered "record B" cannot be
# identified from its wording.
TRIAL_IDS = re.compile(r"\bNCT\d{8}\b|\bISRCTN\d{6,}\b|\bACTRN\d{10,}\b|\bChiCTR[-A-Za-z0-9]+\b|\b\d{4}-\d{6}-\d{2}\b|"
                       r"\bDRKS\d{5,}\b|\bCTRI/\d{4}/\d+/\d+\b|\bPACTR\d{6,}\b|\bIRCT[A-Za-z0-9]+\b|\bJPRN-[A-Za-z0-9]+\b|"
                       r"\bUMIN\d{6,}\b|\bNTR\d{3,}\b", re.I)
ANOTHER_RECORD = re.compile(r"\b(?:another|a different|other|separate|second) (?:registry |trial |register )?"
                            r"(?:record|registration|entry)\b", re.I)
_PROTOCOL_CONCEPT = re.compile(r"\bper[- ]protocol\b|\bprotocol[- ](?:deviation|violation|adherence|non-adherence|"
                               r"compliance)s?\b|\b(?:deviat|violat|adheren|non-adheren|complian|departure)\w* "
                               r"(?:from|to|of|with) (?:the |trial |study )?protocols?\b", re.I)


_NOT_HAD = re.compile(r"(?:\bno|\bwithout(?: access to)?(?: the| a| any)?|\bnot (?:see|seen|have|had)(?: the| a| any)?)\s*$",
                      re.I)
# "the protocol was unavailable", and with the document's noun between ("the registry RECORD was unavailable";
# codex A3 r27)
_NOT_AVAILABLE = re.compile(r"^\s*(?:(?:record|entry|registration|report|document|plan|text|data|file)s?\s+)?"
                            r"(?:was|were|is|are)\s+(?:not (?:available|provided|accessible|seen)|unavailable)\b", re.I)


def _disclaimed(text, m):
    """The rationale says this document was NOT available to it ("no protocol was available", "without access to the
    protocol", "the protocol was not available"): a disclaimer, not reliance (codex A3 r17)."""
    return bool(_NOT_HAD.search(text[max(0, m.start() - 30):m.start()]) or _NOT_AVAILABLE.match(text[m.end():m.end() + 40]))


def _doc(d):
    """A document's canonical name: one name per document, whichever alias or form names it."""
    d = _norm(d)
    if re.fullmatch(r"saps?|statistical analysis plans?", d):
        return "statistical analysis plan"
    m = re.fullmatch(r"fig(?:ure|s|ures|\.)? ?(\d+)", d)
    if m:
        return f"figure {m.group(1)}"
    m = re.fullmatch(r"tables? (\d+)", d)
    if m:
        return f"table {m.group(1)}"
    if d.startswith("regist") or d in ("clinicaltrials.gov", "trial register"):
        return "registry"
    m = re.match(r"(" + "|".join(OTHER_REGISTERS) + r")\b|(" + "|".join(OTHER_REGISTERS) + r")(?=[\s:#-]*\d)", d)
    if m:                                              # ISRCTN12345678 / ISRCTN: the same register (codex A3 r21)
        return m.group(1) or m.group(2)
    return {"protocols": "protocol", "manuscripts": "manuscript", "abstracts": "abstract", "appendices": "appendix",
            "full-text": "full text", "fulltext": "full text"}.get(d, d)


def _docs_in(text):
    """The documents a shown text REPORTS: named, and not said to be unavailable (codex A3 r18)."""
    t = _PROTOCOL_CONCEPT.sub(" ", text or "")
    docs = {_doc(m.group(0)) for _, rx in UNSEEN_DOCS for m in rx.finditer(t) if not _disclaimed(t, m)}
    # a reported NAMED register is "the registry" the rationale may then name (codex A3 r21)
    return docs | ({"registry"} if docs & set(OTHER_REGISTERS) else set())


_SENTENCE_END = re.compile(r"(?<!\bfig)(?<!\bfigs)(?<!\bno)(?<!\bvs)(?<!\bal)(?<!\be\.g)(?<!\bi\.e)(?<!\bapprox)"
                           r"(?<!\bref)(?<!\bsuppl)(?<!\btab)[.!?] ")


def quoted_sentence(quote, text):
    """The sentence(s) of a shown source that contain the quote (normalised), or the quote alone if it is not found."""
    t, q = _norm(text), _norm(quote)
    i = t.find(q) if q else -1
    if i < 0:
        return q
    # a sentence ends at . ! ? followed by a space -- not an abbreviation's full stop ("Fig. 1", codex A3 r20)
    bounds = [m.start() for m in _SENTENCE_END.finditer(t)]
    a = max([x for x in bounds if x < i], default=-1)
    e = i + len(q) - (1 if q[-1:] in ".!?" else 0)     # a quote ending its sentence ends it (codex/agy A3 r17)
    ends = [x for x in bounds if x >= e]
    return t[(a + 2 if a >= 0 else 0):(min(ends) + 1 if ends else len(t))]


def _shown_kind(k):
    return "registry" if str(k or "").startswith("registry") else k     # registry_text / registry_row (agy A3 r16)


def unseen_identifier(why, shown, context="", ids=()):
    """(codex A3 r22) The first trial identifier, or "another record", in the rationale that the readers were not shown;
    "another record" the quoted sentence itself reports is reported context (codex A3 r23). An identifier is shown when
    it is a shown registry's own id, or a shown text names it WITHOUT saying it was unavailable (codex A3 r25)."""
    # the SAME rule as for documents (codex A3 r26): reported only by the shown registry's own id or by the QUOTED
    # SENTENCE (named there, not said to be unavailable); a rationale that disclaims an identifier does not rely on it
    c0 = _norm(context)
    seen = {_norm(i) for i in ids if i} | {_norm(x.group(0)) for x in TRIAL_IDS.finditer(c0) if not _disclaimed(c0, x)}
    for m in TRIAL_IDS.finditer(why):
        if _norm(m.group(0)) not in seen and not _disclaimed(why, m):
            return m.group(0)
    # a rationale that DISCLAIMS another record does not rely on it (codex A3 r25)
    m = next((x for x in ANOTHER_RECORD.finditer(why) if not _disclaimed(why, x)), None)
    c = _norm(context)
    # reported only where the sentence names it WITHOUT saying it was unavailable (codex A3 r24)
    reported = any(not _disclaimed(c, x) for x in ANOTHER_RECORD.finditer(c))
    return m.group(0) if m and not reported else None


def cites_unseen(why, quote, kinds, context=""):
    """A3: the first document the rationale names that the readers were not shown -- no source of its kind shown, and
    the quoted sentence (`context`, with the quote) does not report it -- or None."""
    kinds = {_shown_kind(k) for k in kinds}
    # from the quoted SENTENCE, which contains the quote AND any disclaimer before it: a quote cropped just after
    # "without access to the protocol," cannot report the protocol (codex A3 r19); the quote alone only when no source
    reported = _docs_in(context if context else quote)
    for kind, rx in UNSEEN_DOCS:
        if kind is not None and kind in kinds:
            continue
        w = _PROTOCOL_CONCEPT.sub(" ", why)
        for m in rx.finditer(w):
            if _doc(m.group(0)) not in reported and not _disclaimed(w, m):
                return m.group(0)
    return None


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
SETTING_BASED = frozenset({"2.1", "2.2", "3.3", "3.4"})
TOPIC_GATE_EXEMPT = SETTING_BASED

# PRE-REGISTERED VARIANTS (Mahmood via Dispatch, 13 Oct, codex candidates 2 and 3; outputs/robgrade/
# CONTEXTUAL_VARIANT_<name>.md). Each changes exactly one thing, is selected only by an explicit argument and is never
# the default; each is scored separately on TEST.
VARIANTS = {
    "v43_setting": {"setting_based": SETTING_BASED | {"4.3"}, "usual": USUAL},           # 4.3 is setting-based
    "vcommonly": {"setting_based": SETTING_BASED,                                        # "commonly" is not USUAL
                  "usual": _usual(tuple(t for t in USUAL_TERMS if t != "commonly"))},
}
_BASE_RULE = {"setting_based": SETTING_BASED, "usual": USUAL}


def rule(variant=None):
    """The rule's variable parts: the base, or a registered variant (an unknown name is a KeyError, never the base)."""
    return _BASE_RULE if variant is None else VARIANTS[variant]


def about_question(qid, quote, exempt=TOPIC_GATE_EXEMPT):
    """The quote names the question's topic: at least one of QUESTION_TERMS[qid] occurs in it (setting-based: exempt)."""
    if qid in exempt:
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


def parse_reply(raw):
    """THE parser for a model's reply (amendment A2, signed 13 Oct): the JSON object in the reply, whatever prose or
    code fence surrounds it, if it carries an "answers" list; else None. The pipeline, the scorer and the dual reading
    all call this one function, so they can never disagree about what a model said (agy prefixed 15 of 58 contextual
    replies with prose, which the old strict parser read as no answer at all)."""
    t = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw or "")
    # every JSON object that decodes at a '{' (prose and braces around it are skipped -- codex A2 review); a duplicate
    # key makes an object ambiguous; exactly ONE distinct answer object is an answer, two or more are ambiguous
    plain, strict = json.JSONDecoder(), json.JSONDecoder(object_pairs_hook=_no_duplicate_keys)
    found, spans, failed, i = [], [], [], 0
    while True:
        i = t.find("{", i)
        if i < 0:
            break
        try:
            obj, end = plain.raw_decode(t, i)
        except ValueError:
            if _starts_answers_envelope(t, i):        # a broken answer envelope: the reply is unreadable (codex A2 r9)
                return None
            failed.append(i)                           # an object that does not decode (codex A2 r14)
            i += 1
            continue
        if not (isinstance(obj, dict) and "answers" in obj):
            i += 1                                     # not an answer envelope: an answer object may sit inside it
            continue
        # an answer ENVELOPE: it must be well formed, or the whole reply is unreadable (codex A2 review, round 8) --
        # no duplicate key anywhere in it, an answers LIST, every row an object; scanning resumes AFTER it, never inside
        try:
            strict.raw_decode(t[i:end])
        except (ValueError, _DuplicateKey):
            return None
        if not isinstance(obj["answers"], list) or not all(isinstance(r, dict) for r in obj["answers"]):
            return None
        # (codex A2 r12) a row field of the wrong type (an answer that is a list, ...) is a malformed reply, never a
        # crash in verify and never a guess
        if any(not isinstance(r.get(k), (str, type(None))) for r in obj["answers"] for k in _ROW_TEXT):
            return None
        if obj not in found:
            found.append(obj)
        spans.append((i, end))
        i = end
    # (codex A2 r10) an "answers" key OUTSIDE every well-formed envelope is a broken envelope, whatever key it starts
    # with ({"notes": "", "answers": ... cut off): the reply is unreadable rather than read from a fragment of it
    # (codex A2 r14) ... it is part of a broken object when an object opened BEFORE it failed to decode; with no
    # failed '{' before it, it is a key merely MENTIONED in prose and is ignored (the signed promise to ignore prose)
    if any(not any(s <= k < e for s, e in spans) and any(f < k for f in failed) for k in _answers_keys(t)):
        return None
    return found[0] if len(found) == 1 else None


class _DuplicateKey(ValueError):
    pass


# a JSON object KEY: a string literal followed by ':' -- compared DECODED, so an escaped spelling ("answers") is
# the same key (codex A2 r11)
_ROW_TEXT = ("qid", "answer", "quote", "source_id", "rationale")     # text fields of an answer row (or absent/null)
_KEY = re.compile(r'"((?:[^"\\]|\\.)*)"\s*:')


def _is_answers(literal):
    try:
        return json.loads('"' + literal + '"') == "answers"
    except ValueError:
        return False


def _answers_keys(t):
    """Positions of every key-like string in `t` that decodes to "answers" (whether it belongs to a broken object or
    is merely mentioned in prose is decided by the caller, codex A2 r13-r14)."""
    return [m.start() for m in _KEY.finditer(t) if _is_answers(m.group(1))]


def _starts_answers_envelope(t, i):
    """`t[i]` is '{' and its first key decodes to "answers"."""
    m = _KEY.match(t, i + 1 + (len(t[i + 1:]) - len(t[i + 1:].lstrip())))
    return bool(m and _is_answers(m.group(1)))


def _no_duplicate_keys(pairs):
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise _DuplicateKey(f"duplicate keys {sorted({k for k in keys if keys.count(k) > 1})}")
    return dict(pairs)


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


def verify(reading, sources, targets, variant=None, check_unseen=True):
    """{qid: {answer, quote, source_id, source_sha256, rationale} | {answer: NI[, dropped]}} for every TARGET question.
    PY/PN only; the rationale is neither empty, generic nor from memory, and refers to the quote; the quote (8-300
    characters) is found verbatim (whitespace/case/dash-normalised) in the OPEN source it names."""
    r = rule(variant)
    srcs = {s["id"]: s for s in sources if s.get("open_for_prompt")}
    kinds = {s.get("kind") for s in srcs.values()}          # what the readers were SHOWN (A3)
    targets = list(targets)
    out = {}
    rows = [a for a in (reading or {}).get("answers") or [] if isinstance(a, dict)]
    # two rows for one question with different answers are ambiguous: NI, whichever comes first (codex A2 review)
    for q in targets:
        if len({a.get("answer") for a in rows if a.get("qid") == q}) > 1:
            out[q] = {"answer": "NI", "dropped": {"why": "AMBIGUOUS_CONFLICTING_ROWS"}}
    for a in rows:
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
        if not why or MEMORY.search(why) or (q not in r["setting_based"] and r["usual"].search(why)):
            out[q] = {"answer": "NI", "dropped": {"answer": v, "rationale": why[:300],
                                                  "why": "RATIONALE_EMPTY_GENERIC_OR_FROM_MEMORY (not context)"}}
            continue
        qs = quote if isinstance(quote, str) else ""
        named = srcs.get(a.get("source_id"))
        sent = quoted_sentence(qs, _text(named)) if named else ""
        doc = (cites_unseen(why, qs, kinds, sent) or
               unseen_identifier(why, " ".join(_text(x) for x in srcs.values()), sent,
                                 [x.get("nct") for x in srcs.values()])) \
            if check_unseen else None
        if doc:                                        # A3: rests on a document the readers were not shown
            out[q] = {"answer": "NI", "dropped": {"answer": v, "rationale": why[:300], "document": doc,
                                                  "why": "RATIONALE_CITES_A_SOURCE_NOT_SHOWN"}}
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
        if not about_question(q, quote, r["setting_based"]):
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
        if c.get("context"):                           # the quotes stay with the decision (codex A2 review, round 8)
            audit[q]["context"] = copy.deepcopy(c["context"])
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
                closed = answers[q]
                answers[q] = rf.answer("NA", how="not asked once an upstream question was answered contextually")
                # never silent: the contextual decision on a branch since closed stays visible (codex A2 review)
                answers[q]["closed_contextual"] = {"answer": closed["answer"], "context": closed.get("context") or [],
                                                   "span": closed.get("span")}
    new = rf.assessment(obj["trial"], obj["outcome"], answers, insufficient_domains=insufficient)
    # EXTEND the incoming audit: a later pass must not erase an earlier pass's decisions
    new["contextual_audit"] = dict(copy.deepcopy(obj.get("contextual_audit") or {}), **audit)
    return new
