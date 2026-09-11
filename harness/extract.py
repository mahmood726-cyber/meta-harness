"""Conservative, deterministic outcome extractor over committed abstract text.

Fails CLOSED: if a number is not corroborated it is declared absent, never guessed.
  * arm-level counts: "N (P%) of M ... <intervention> ... N2 (P2%) of M2 ... <comparator>"
    accepted only when P ~= N/M (within 1.5 percentage points) for BOTH arms, and the
    number is not immediately negated ("not"/"non"/"never").
  * effect+CI fallback: "RR/OR/HR [reduction] X (95% CI L-U)"; a stated relative-risk
    *reduction* is converted RRR -> RR = 1-X, CI flipped.
No hand-typed numbers: everything comes from the cached source text.
"""
from __future__ import annotations
import re

NEG = ("not ", "non-", "non ", "never ", "no ")
_ARM = re.compile(r"(\d+)\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)\s*(?:of|/)\s*(\d+)")
_ARM2 = re.compile(r"(\d+)\s*/\s*(\d+)\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)")
# "N of M [patients] (P%)" — NEJM/Lancet order: count, denominator, then percentage.
_ARM3 = re.compile(r"(\d+)\s+of\s+(\d+)\s+(?:patients?|participants?|women|men|subjects?|people)?\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)")
# "N [patients] (P%)" with the denominator stated elsewhere in the sentence/abstract.
# "N [patients] (P%)" or "N [patients] [P%]" — parentheses OR square brackets.
_ARMP = re.compile(r"(\d+)\s+(?:patients?|participants?|cases?|subjects?)?\s*[\(\[]\s*(\d+(?:\.\d+)?)\s*%\s*[\)\]]")
# "P% (N/M)" — percentage FIRST, then the explicit fraction, e.g. "9% (7/78)". Unambiguous
# (explicit numerator/denominator; the % corroborates), so safe to accept like _ARM2/_ARM3.
_ARM4 = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*[\(\[]\s*(\d+)\s*/\s*(\d+)\s*[\)\]]")
_DENOM_EACH = re.compile(r"(\d+)\s+(?:patients?\s+|were\s+)?(?:randomly\s+)?(?:assigned|allocated|randomi[sz]ed)\s+to\s+each", re.I)
_NEQ = re.compile(r"n\s*=\s*(\d+)", re.I)
_WORDNUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
            "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
            "nineteen": 19, "twenty": 20}


def _norm(text: str) -> str:
    # Lancet et al. use a middle dot as the decimal separator (21·6%). Normalise.
    return (text or "").replace("·", ".").replace("‧", ".").replace("∙", ".")
_EFFECT = re.compile(
    # The abbreviations RR/OR/HR are matched CASE-SENSITIVELY via (?-i:...): papers always
    # capitalise them, and matching them case-insensitively let the CONJUNCTION "or" in
    # "CV death or HF hospitalisation (RR 0.83...)" be read as an odds-ratio scale label,
    # mislabelling a comparator RR as OR. The full words stay case-insensitive.
    r"(relative risk reduction|relative risk|risk ratio|incidence rate ratio|rate ratio|(?-i:\bRR\b)|odds ratio|(?-i:\bOR\b)|hazard ratio|(?-i:\bHR\b))"
    r"[^0-9]{0,25}?(\d+(?:\.\d+)?)[^0-9]{0,28}?(?:\d{2}\s*(?:%|percent|per cent)\s*)?(?:confidence intervals?|\bCI\b)"
    r"[^0-9]{0,10}?(\d+(?:\.\d+)?)\s*(?:to|[-–—,])\s*(\d+(?:\.\d+)?)", re.I)
_K = re.compile(r"(\d+|[A-Za-z]+)\s+(?:randomi[sz]ed\s+(?:controlled\s+)?trials|controlled\s+(?:clinical\s+)?trials|RCTs)", re.I)


def _sentences(text: str):
    # Split on sentence-ending period only. NOT on ';' — a ';' separates sub-clauses
    # (e.g. "recurrence rate ...; relative risk reduction, 0.56 [CI 0.27 to 0.73]") and
    # splitting there orphans the effect from its outcome keyword, letting a later
    # sentence's number be mis-attributed (right number, wrong endpoint).
    return re.split(r"(?<=\.)\s+(?=[A-Z(])", text or "")


def _outcome_sentences(abstract, kws):
    out = [s for s in _sentences(abstract) if any(k.lower() in s.lower() for k in kws)]
    return out


def _negated(s, pos):
    pre = s[max(0, pos - 18):pos].lower()
    return any(n in pre for n in NEG)


def extract_arm_counts(sentence, interv_terms, comp_terms, denom_each=None, arm_ns=None):
    """Return (ai,n1i,ci,n2i) if two corroborated arm groups are found, else None.

    arm_ns: optional {"i": n_intervention, "c": n_comparator} per-arm sizes with ARM IDENTITY. When
    present, an inferred-denominator count is paired ONLY with its OWN arm's size (decided by whether
    the count sits nearer the intervention or the comparator term), never with the other arm's size.
    This is what makes near-equal arms safe: LoDoCo2 (2762 vs 2760) or SELECT (8803 vs 8801) can no
    longer cross, because the placebo count is only ever tested against the placebo size. A wrong
    per-arm size still just fails corroboration and the count is declared absent — never mispooled."""
    groups = []
    for m in _ARM.finditer(sentence):
        ev, pct, n = int(m.group(1)), float(m.group(2)), int(m.group(3))
        if n > 0 and abs(ev / n * 100 - pct) <= 1.5 and not _negated(sentence, m.start()):
            groups.append((m.start(), ev, n))
    for m in _ARM2.finditer(sentence):
        ev, n, pct = int(m.group(1)), int(m.group(2)), float(m.group(3))
        if n > 0 and abs(ev / n * 100 - pct) <= 1.5 and not _negated(sentence, m.start()):
            groups.append((m.start(), ev, n))
    for m in _ARM3.finditer(sentence):
        ev, n, pct = int(m.group(1)), int(m.group(2)), float(m.group(3))
        if n > 0 and ev <= n and abs(ev / n * 100 - pct) <= 1.5 and not _negated(sentence, m.start()):
            groups.append((m.start(), ev, n))
    for m in _ARM4.finditer(sentence):  # "P% (N/M)" percentage-first
        pct, ev, n = float(m.group(1)), int(m.group(2)), int(m.group(3))
        if n > 0 and ev <= n and abs(ev / n * 100 - pct) <= 1.5 and not _negated(sentence, m.start()):
            groups.append((m.start(), ev, n))
    if len(groups) < 2 and (denom_each or arm_ns):
        # "N [patients] (P%)"/"[P%]" with the denominator inferred from the abstract; accept only if a
        # candidate denominator corroborates the stated percentage for that arm. With per-arm arm_ns
        # the count is paired ONLY with its OWN arm's size (by proximity to the arm term) so near-equal
        # arms cannot cross; the flat denom_each remains a fallback ONLY when arm_ns lacks that arm.
        low_s = sentence.lower()
        cands = denom_each if isinstance(denom_each, (list, tuple, set)) else [denom_each]
        cands = [int(c) for c in cands if c]
        arm_ns = arm_ns or {}
        armp = [(m.start(), int(m.group(1)), float(m.group(2)))
                for m in _ARMP.finditer(sentence) if not _negated(sentence, m.start())]
        ipos = min((low_s.find(t.lower()) for t in interv_terms if t.lower() in low_s), default=-1)
        cpos = min((low_s.find(t.lower()) for t in comp_terms if t.lower() in low_s), default=-1)
        used_reading_order = False
        # PREFERRED: identity-safe reading-order pairing. When we have per-arm sizes for BOTH arms and
        # exactly two inferred-denominator counts, pair the first-mentioned arm's count with its OWN
        # size and the second with the other's — robust to whether the arm label precedes or follows
        # its count (Hernández: "high-flow group (13 ... vs 32 ... conventional group)"; LoDoCo2:
        # "187 ... colchicine group and 264 ... placebo group"). Each still must corroborate its %, so
        # near-equal arms (2762 vs 2760) cannot cross and a wrong size just fails (declared absent).
        if len(armp) == 2 and arm_ns.get("i") and arm_ns.get("c") and ipos >= 0 and cpos >= 0:
            first_arm = "i" if ipos <= cpos else "c"
            order = [first_arm, "c" if first_arm == "i" else "i"]
            paired = []
            for (pos, ev, pct), arm in zip(armp, order):
                d = int(arm_ns[arm])
                if d > 0 and ev <= d and abs(ev / d * 100 - pct) <= 1.0:
                    paired.append((pos, ev, d))
            if len(paired) == 2:
                groups.extend(paired)
                used_reading_order = True
        # FALLBACK (backward compatible): flat best-corroborating candidate per count.
        if not used_reading_order:
            for pos, ev, pct in armp:
                best = None
                for den in cands:
                    if den > 0 and ev <= den and abs(ev / den * 100 - pct) <= 1.0:
                        if best is None or abs(ev / den * 100 - pct) < abs(ev / best * 100 - pct):
                            best = den
                if best:
                    groups.append((pos, ev, best))
    # de-duplicate overlapping matches at the same position
    seen, uniq = set(), []
    for g in sorted(groups):
        if g[0] not in seen:
            seen.add(g[0]); uniq.append(g)
    groups = uniq
    if len(groups) < 2:
        return None
    groups.sort()
    low = sentence.lower()
    i_pos = min((low.find(t.lower()) for t in interv_terms if t.lower() in low), default=-1)
    c_pos = min((low.find(t.lower()) for t in comp_terms if t.lower() in low), default=-1)
    if i_pos < 0 or c_pos < 0:
        return None
    # assign the two arm-groups to intervention/comparator by reading order
    (p1, e1, n1), (p2, e2, n2) = groups[0], groups[1]
    if i_pos <= c_pos:
        return (e1, n1, e2, n2)
    return (e2, n2, e1, n1)


def _effect_from_match(m):
    kind, pt, lo, hi = m.group(1).lower(), float(m.group(2)), float(m.group(3)), float(m.group(4))
    if not (lo < hi and lo > 0 and pt > 0):
        return None
    if "reduction" in kind:  # RRR -> RR
        if not (0 < pt < 1 and 0 < lo < 1 and 0 < hi < 1):
            return None
        return ("RR", round(1 - pt, 4), round(1 - hi, 4), round(1 - lo, 4))
    if "rate ratio" in kind or "incidence rate" in kind:
        scale = "IRR"   # incidence-rate ratio (recurrent-event / person-time estimand)
    elif "odds" in kind or kind == "or":
        scale = "OR"
    elif "hazard" in kind or kind == "hr":
        scale = "HR"
    else:
        scale = "RR"
    if not (lo <= pt <= hi):
        return None
    return (scale, pt, lo, hi)


def extract_effect(sentence):
    """Return (scale, point, lo, hi) from the FIRST effect+CI phrase, else None."""
    m = _EFFECT.search(sentence)
    return _effect_from_match(m) if m else None


GENERIC_ANCHORS = {"primary outcome", "primary end point", "primary endpoint",
                   "primary study outcome", "primary study end point"}

# Recognises a primary/secondary OUTCOME-DEFINITION phrase even when an adjective is inserted
# between "primary" and the outcome noun. NEJM/Lancet routinely write "the primary COMPOSITE
# outcome" / "the primary composite end point", where the literal substring "primary outcome"
# is absent (the word "composite" splits it) — so a purely literal anchor check fails to
# recognise the definition sentence and the generic anchor is never enabled (FIDELIO-DKD:
# "The primary composite outcome ... was kidney failure, ... eGFR ..., or death from renal
# causes" was declared-absent for exactly this reason). This ONLY controls whether a sentence
# is treated as an outcome-DEFINITION sentence in _effective_kws; the disease-specificity gate
# there still decides whether the primary IS ours, so a CV primary (FIGARO-DKD) is unaffected.
# PRIMARY family ONLY: the generic anchors in GENERIC_ANCHORS are all "primary" anchors, so
# only a PRIMARY-definition sentence may enable them. Matching a "secondary ... outcome"
# definition sentence here would wrongly turn on the "primary outcome" anchor and let a
# trial whose SECONDARY is ours (but whose PRIMARY is a different composite) have its primary
# grabbed — FIGARO-DKD's CV primary (458/3686) being read as the kidney topic's outcome.
_ANCHOR_RX = re.compile(
    r"\b(?:co-?primary|primary)\s+"
    r"(?:composite\s+|study\s+|efficacy\s+|main\s+|clinical\s+)*"
    r"(?:outcome|end[\s-]?point)\b", re.I)
# A relaxed-anchor match counts as an outcome-DEFINITION sentence only when it also carries a
# definition cue ("the primary composite outcome ... WAS ...", "... DEFINED AS ...", "a
# COMPOSITE OF ..."). This distinguishes a genuine definition from a narrative RESULT mention
# ("ticagrelor reduced the primary composite endpoint of ...") that appears in a PLATO diabetes
# SUBSTUDY (PMID 20802246), where enabling the generic anchor would let a median-split subgroup
# HR (0.80, "patients with HbA1c above the median") be selected. A literal anchor keeps its
# original behaviour (unchanged); this cue is required ONLY for the relaxed path.
_DEF_CUE = re.compile(
    r"\b(?:was|were|is|are|defined|assessed|comprised|consisted|included)\b|"
    r"\bcomposite of\b|\ba composite\b", re.I)


# Words excluded from the outcome-overlap test. Two groups:
#  - syntactic glue ("or", "for", "composite", "endpoint"...)
#  - GENERIC MEDICAL NOUNS that appear in many unrelated outcomes and therefore do NOT
#    discriminate one outcome from another: death, failure, causes, disease, mortality,
#    hospitalization... These are why plain bag-of-words is unsafe here: "death from
#    CARDIOVASCULAR causes / heart FAILURE" and "death from RENAL causes / kidney FAILURE"
#    share death/causes/failure while meaning opposite things. Only a DISCRIMINATING word
#    (cardiovascular vs renal/kidney) should count, so a trial's primary is treated as ours
#    only when a topic-specific term actually overlaps -- verified on FIGARO-DKD, whose CV
#    primary must NOT be read as the kidney-composite topic's outcome.
_KW_STOP = {"or", "and", "of", "for", "the", "to", "in", "with", "at", "a", "an", "due",
            "rate", "outcome", "endpoint", "end", "point", "composite", "least", "one",
            "study", "than", "from", "per", "first", "time", "event", "events",
            "death", "deaths", "cause", "causes", "disease", "failure", "mortality",
            "hospitalization", "hospitalisation", "hospitalized", "hospitalised",
            "patients", "risk", "treatment", "therapy", "clinical", "trial", "group",
            "groups", "placebo", "nonfatal", "fatal", "adverse", "serious", "major"}


def _content_words(phrases):
    return {w for p in phrases for w in p.lower().replace(",", " ").replace("-", " ").split()
            if len(w) > 4 and w not in _KW_STOP}


def _effective_kws(abstract, outcome_kws):
    """Generic 'primary outcome/endpoint' anchors are used ONLY when the trial's primary
    outcome IS our outcome. Linked either by (a) a full disease-keyword substring in a
    primary-definition sentence, or (b) that sentence sharing >=2 DISCRIMINATING content
    words with our outcome keywords (generic medical nouns like death/failure/causes are
    excluded via _KW_STOP). So a trial that phrases our outcome differently ('worsening
    heart failure ... or cardiovascular death' vs our 'cardiovascular death or
    hospitalisation for heart failure') still links on {worsening, heart, cardiovascular},
    while a genuinely different primary does NOT: COPPS-2's postpericardiotomy syndrome vs
    AF, and -- the case that broke plain bag-of-words -- FIGARO-DKD's CV primary (death
    from cardiovascular causes, MI, stroke, HF hosp) vs a kidney-composite topic, which
    now shares no renal/kidney term and is correctly rejected so its number is taken from
    the SECONDARY (kidney) sentence, not the CV primary. The anchor is enabled only when
    the primary IS ours; the number then comes from the 'primary outcome occurred in N of
    M' sentence, so there is no wrong-outcome selection."""
    disease = [k for k in outcome_kws if k.lower() not in GENERIC_ANCHORS]
    generic = [k for k in outcome_kws if k.lower() in GENERIC_ANCHORS]
    if not generic:
        return disease
    dwords = _content_words(disease)
    for s in _sentences(abstract):
        sl = s.lower()
        # A sentence is an outcome-DEFINITION sentence if it names a generic anchor literally
        # (original behaviour) OR matches the relaxed anchor pattern AND carries a definition
        # cue (so a narrative "reduced the primary endpoint of ..." result mention in a
        # substudy does not enable the anchor). Enabling still requires disease-keyword overlap.
        if not (any(g in sl for g in generic) or (_ANCHOR_RX.search(sl) and _DEF_CUE.search(sl))):
            continue
        if any(dk.lower() in sl for dk in disease):
            return disease + generic
        if sum(1 for w in dwords if w in sl) >= 2:
            return disease + generic
    return disease


def _rr_from_counts(ai, n1i, ci, n2i):
    if 0 in (n1i, n2i) or ci == 0:
        return None
    return (ai / n1i) / (ci / n2i)


def _or_from_counts(ai, n1i, ci, n2i):
    a, b, c, d = ai, n1i - ai, ci, n2i - ci
    if 0 in (a, b, c, d):  # Haldane-Anscombe 0.5 correction on any zero cell
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5
    if c == 0 or b == 0:
        return None
    return (a * d) / (b * c)


def _roundtrip_ok(ai, n1i, ci, n2i, scale, point):
    """Recompute the effect from the extracted 2x2 and check it against the effect the paper
    itself reports. Refuses the class that has nearly beaten us: counts that belong to a
    DIFFERENT outcome than the reported effect (EMPEROR 361 vs a 15-event OM), a wrong-outcome
    count table, or a mis-scaled number. Same-scale (RR/OR): the crude count-derived value must
    be within a factor of 2 of the reported point (generous enough for adjusted-vs-crude, tight
    enough to catch a gross mismatch). Reported HR: crude RR is a different estimand, so only the
    DIRECTION is checked (both must sit on the same side of 1 when both are clearly off 1)."""
    if point is None or point <= 0:
        return True  # nothing to check against
    comp = _or_from_counts(ai, n1i, ci, n2i) if scale == "OR" else _rr_from_counts(ai, n1i, ci, n2i)
    if not comp or comp <= 0:
        return True
    if scale in ("RR", "OR"):
        ratio = comp / point
        return 0.5 <= ratio <= 2.0
    # HR (or other): direction-only. Both clearly protective or both clearly harmful.
    if (comp - 1) * (point - 1) < 0 and abs(comp - 1) > 0.11 and abs(point - 1) > 0.11:
        return False
    return True


_FACTORIAL = re.compile(r"\bfactorial\b|\b2\s*[x×]\s*2\b|\btwo[- ]by[- ]two\b|\bpartial factorial\b", re.I)
_DOSE_ARM = re.compile(r"(\d+(?:\.\d+)?)\s*-?\s*mg\b(?:[^.]{0,20}?(?:group|arm|dose|daily|twice|once))?", re.I)

# Recurrent-event / incidence-rate extraction. A rate's UNIT is parsed EXPLICITLY: a number's
# scale does not tell you its unit (3.9 was once a rate per 100 person-years). We only accept a
# rate whose per-person-time unit is unambiguous, and only pool when per-arm events + person-time
# can be derived without guessing. Explicit events+person-time is unambiguous; an annualised rate
# needs per-arm N and follow-up, which we require to be explicit or we REFUSE.
_RATE_EVPT = re.compile(  # "N events ... M patient-years/person-years" (both explicit)
    r"(\d[\d,]*)\s+(?:events?|exacerbations?|episodes?|hospitali[sz]ations?)[^.]{0,40}?"
    r"(\d[\d,]*(?:\.\d+)?)\s+(?:patient|person)[-\s]?years?", re.I)
# rate + explicit per-person-time unit; group2 tells us the unit so we can normalise to /py.
_RATE_UNIT = re.compile(
    r"(\d+(?:\.\d+)?)\s*(%\s*(?:per|/)\s*(?:year|yr|patient[-\s]?year|person[-\s]?year)|"
    r"per\s+100\s+(?:patient|person)[-\s]?years?|per\s+(?:patient|person)[-\s]?years?|"
    r"per\s+patient\s+per\s+year)", re.I)


def _is_factorial(abstract):
    return bool(_FACTORIAL.search(abstract or ""))


_SUBGROUP = re.compile(
    r"\bper[-\s]?protocol\b|\bpost[-\s]?hoc\b|\bsubgroup\b|\bsensitivity analysis\b|"
    r"\bas[-\s]?treated\b|\blowest in\b|\bhighest in\b|\bamong (?:those|patients) (?:with|who)\b|"
    r"\brestricted to\b|\bexploratory analysis\b", re.I)


def _is_subgroup_sentence(sentence):
    """An effect from a subgroup / per-protocol / post-hoc / sensitivity sentence is NOT the main
    ITT comparison and must not be pooled as it (a trial full text is full of these — the azithromycin
    28558695 HR was 'lowest in the HP+/AZ group', a subgroup). Refuse extraction from such a sentence."""
    return bool(_SUBGROUP.search(sentence or ""))


# A COMPOSITE endpoint names two or more components joined ("CV death OR HF hospitalization",
# "composite of ...", a MACE). When the review's declared outcome is a SINGLE component, a number
# pulled from a composite sentence is the WRONG endpoint (FAIR-HF2's 0.79 is "cardiovascular death
# or first heart failure hospitalization", not "heart-failure hospitalization" alone). We skip such
# sentences for single-outcome topics; a later single-endpoint sentence may still match, else the
# trial is declared absent. NOT applied to composite-declared topics (there the composite IS ours).
_COMPOSITE_ENDPOINT = re.compile(
    r"\bcomposite\b|\bmajor adverse cardiovascular\b|\bMACE\b|"
    r"\bdeath or\b|\bor death\b|\bor first (?:heart failure |hf )?hospitali|"
    r"\bor (?:heart failure|hf) hospitali|\bor worsening (?:heart failure|hf)\b|"
    r"\bor hospitali[sz]ation for (?:heart failure|hf)\b", re.I)


def _names_composite(sentence):
    return bool(_COMPOSITE_ENDPOINT.search(sentence or ""))


def declared_is_composite(name: str) -> bool:
    """Is the review's declared primary-outcome NAME itself a composite? (Then the composite guard
    is OFF — the composite is exactly what we want.)"""
    n = (name or "").lower()
    return any(w in n for w in (" or ", "composite", "mace", "major adverse"))


def _multi_dose_arms(abstract):
    """Distinct intervention DOSE values reported (e.g. CANTOS '50-mg group ... 150-mg group ...
    300-mg group'). A trial with >1 dose arm vs one comparator is multi-arm: picking one dose's
    effect without a pre-specified rule is ambiguous, so we refuse unless the intervention is
    dose-specified. Returns the set of distinct doses seen with an arm/group/dose context."""
    doses = set()
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*-?\s*mg\b[^.]{0,25}?(?:group|arm|dose|daily|twice daily|once daily|regimen)", abstract or "", re.I):
        doses.add(m.group(1))
    return doses


def _intervention_dose_specified(interv_terms):
    return any(re.search(r"\d", t) for t in interv_terms)


def _interv_in(sentence, interv_terms):
    sl = (sentence or "").lower()
    return any(t.lower() in sl for t in interv_terms)


_MEAN_SD = re.compile(  # "mean X (SD Y)" / "X (SD Y)" / "X +/- Y" / "X days (SD Y)"
    r"(\d+(?:\.\d+)?)\s*(?:days?|hours?|minutes?|min|points?)?\s*"
    r"(?:\(\s*(?:SD|standard deviation)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*\)|(?:±|\+/-|\+-)\s*(\d+(?:\.\d+)?))", re.I)
_MED_IQR = re.compile(  # "median X (IQR a-b)" / "median X (IQR a to b)"
    r"median\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*(?:days?|hours?|minutes?|min|points?)?\s*"
    r"[\(\[]\s*(?:IQR|interquartile range)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)", re.I)


def _arm_ns(abstract, interv_terms, comp_terms):
    """Per-arm randomised n, {i: n_intervention, c: n_comparator}, only when unambiguously stated
    for BOTH arms ('zinc (n=50)', 'N patients received zinc', 'assigned N to placebo'); else the
    missing arm is omitted so the continuous extractor refuses rather than guess a denominator."""
    out = {}
    for key, terms in (("i", interv_terms), ("c", comp_terms)):
        best = None
        for t in terms:
            tl = re.escape(t)
            for pat in (rf"{tl}[^.]{{0,12}}?\(\s*n\s*=\s*(\d+)\)",
                        rf"(\d+)\s+(?:patients?|participants?|adults?|subjects?)[^.]{{0,25}}?(?:received|randomi[sz]ed to|assigned to|in the)[^.]{{0,15}}?{tl}",
                        # prose arm size with the NOUN OPTIONAL and 'were' allowed: "264 received
                        # high-flow", "2762 were assigned to the colchicine group".
                        rf"(\d+)\s+(?:patients?\s+|participants?\s+|adults?\s+|subjects?\s+)?(?:were\s+|had\s+been\s+)?(?:received|assigned|allocated|randomi[sz]ed)(?:\s+to)?\s+(?:the\s+)?{tl}",
                        # ELLIPSIS: a second arm sharing the verb — "... and 2760 to the placebo group".
                        rf"(\d+)\s+to\s+(?:the\s+)?{tl}",
                        rf"(?:received|assigned to|randomi[sz]ed to)[^.]{{0,15}}?{tl}[^.]{{0,15}}?\(\s*(\d+)\)",
                        # BARE ADJACENCY (last resort): "... and 263 conventional oxygen therapy" — an
                        # arm size given as "N <arm label>" with the shared verb elided. Safe because
                        # the count path only accepts this size if it corroborates the arm's stated %.
                        rf"(\d+)\s+{tl}\b"):
                m = re.search(pat, abstract, re.I)
                if m:
                    best = int(m.group(1)); break
            if best:
                break
        if best:
            out[key] = best
    return out


def extract_continuous(sentence, interv_terms, comp_terms, n_by_arm=None):
    """Return (mean1,sd1,n1,mean2,sd2,n2) for a mean-difference outcome, or None. Accepts explicit
    'mean (SD)' / 'X +/- SD' per arm, or 'median (IQR a-b)' converted via Wan-2014
    (mean~=median, SD~=IQR/1.35). Refuses on ambiguity (needs two arms + per-arm n). SE (standard
    ERROR) is NOT treated as SD. n_by_arm: optional {intervention_n, comparator_n}."""
    vals = []
    for m in _MEAN_SD.finditer(sentence):
        mean = float(m.group(1))
        sd = float(m.group(2) or m.group(3))
        vals.append((m.start(), mean, sd))
    for m in _MED_IQR.finditer(sentence):
        mean = float(m.group(1))
        sd = (float(m.group(3)) - float(m.group(2))) / 1.35  # Wan 2014 IQR->SD
        if sd > 0:
            vals.append((m.start(), mean, sd))
    if len(vals) < 2 or not n_by_arm:
        return None
    n1, n2 = n_by_arm.get("i"), n_by_arm.get("c")
    if not (n1 and n2):
        return None
    low = sentence.lower()
    i_pos = min((low.find(t.lower()) for t in interv_terms if t.lower() in low), default=-1)
    c_pos = min((low.find(t.lower()) for t in comp_terms if t.lower() in low), default=-1)
    if i_pos < 0 or c_pos < 0:
        return None
    vals.sort()
    (_, m1, s1), (_, m2, s2) = vals[0], vals[1]
    return (m1, s1, n1, m2, s2, n2) if i_pos <= c_pos else (m2, s2, n2, m1, s1, n1)


def extract_rate(sentence, interv_terms, comp_terms):
    """Return (e1i,t1i,e2i,t2i) for an incidence-rate pooling ONLY when per-arm events AND
    person-time are BOTH explicitly stated (no inference). Annualised-rate cases that would need
    per-arm N x follow-up inference are intentionally NOT handled here — they are ambiguous and
    we refuse rather than guess a unit or a denominator. Returns None if not unambiguously present."""
    pairs = []
    for m in _RATE_EVPT.finditer(sentence):
        ev = int(m.group(1).replace(",", ""))
        pt = float(m.group(2).replace(",", ""))
        if pt > 0 and ev >= 0:
            pairs.append((m.start(), ev, pt))
    if len(pairs) < 2:
        return None
    low = sentence.lower()
    i_pos = min((low.find(t.lower()) for t in interv_terms if t.lower() in low), default=-1)
    c_pos = min((low.find(t.lower()) for t in comp_terms if t.lower() in low), default=-1)
    if i_pos < 0 or c_pos < 0:
        return None
    pairs.sort()
    (_, e1, t1), (_, e2, t2) = pairs[0], pairs[1]
    return (e1, t1, e2, t2) if i_pos <= c_pos else (e2, t2, e1, t1)


def extract_trial(abstract, outcome_kws, interv_terms, comp_terms, declared_composite=True):
    """Best conservative extraction for one trial's outcome. Returns dict or a reason.

    declared_composite: whether the review's declared outcome is itself a composite. When False
    (a SINGLE declared outcome), sentences that name a composite endpoint are skipped, so a
    composite number is never read as the single outcome (the FAIR-HF2 wrong-endpoint class).
    Defaults True (guard off) for backward compatibility / callers that do not pass it."""
    abstract = _norm(abstract)
    _skip_composite = not declared_composite
    dm = _DENOM_EACH.search(abstract)
    cand = [int(x) for x in _NEQ.findall(abstract)]
    if dm:
        cand.append(int(dm.group(1)))
    denom_each = sorted(set(cand)) or None
    # Per-arm sizes WITH ARM IDENTITY (intervention vs comparator), so an inferred-denominator count
    # is only ever paired with its own arm's size — the identity-safe fix for near-equal arms.
    arm_ns = _arm_ns(abstract, interv_terms, comp_terms)
    # FACTORIAL-DESIGN GUARD: a trial with more than one randomised comparison (e.g. SU.FOL.OM3
    # randomised B vitamins AND n-3) can have the extractor bind the WRONG factor's effect (it
    # bound the B-vitamin HR 0.9 instead of the omega-3 HR 1.08). When the design is factorial we
    # only accept an extraction from a sentence that explicitly names OUR intervention, so the
    # number is provably for our comparison, not the co-randomised one.
    factorial = _is_factorial(abstract)
    # MULTI-ARM GUARD: a dose-ranging trial (>1 intervention dose arm vs one comparator, e.g.
    # CANTOS 50/150/300 mg) makes picking one dose's effect ambiguous. Refuse unless the topic's
    # intervention is dose-specified (then the arm is pinned). Generalises the factorial guard.
    if len(_multi_dose_arms(abstract)) >= 2 and not _intervention_dose_specified(interv_terms):
        return {"absent": True, "reason": (
            "multi-arm dose-ranging trial (>1 intervention dose arm vs one comparator): the effect "
            "cannot be attributed to a single pre-specified comparison; refused (multi-arm guard). "
            "Specify the dose in the topic's intervention terms to pin the arm.")}
    sents = _outcome_sentences(abstract, _effective_kws(abstract, outcome_kws))
    for s in sents:
        if (_is_subgroup_sentence(s) or (factorial and not _interv_in(s, interv_terms))
                or (_skip_composite and _names_composite(s))):
            continue
        arms = extract_arm_counts(s, interv_terms, comp_terms, denom_each, arm_ns)
        if arms:
            # ROUND-TRIP (every outcome, not only same-sentence): the count-derived effect must
            # reconcile with the effect the paper reports for THIS outcome — first the same
            # sentence, else the outcome's reported effect anywhere in the abstract. Refuse a
            # count table we cannot reconcile with the paper's own number.
            rep = extract_effect(s)  # tuple (scale, point, lo, hi) or None
            if not rep:
                d = effect_in_outcome(abstract, outcome_kws)  # dict or None
                if d:
                    rep = (d["scale"], d["effect"], d.get("ci_low"), d.get("ci_high"))
            if rep and not _roundtrip_ok(arms[0], arms[1], arms[2], arms[3], rep[0], rep[1]):
                return {"absent": True,
                        "reason": (f"round-trip mismatch: extracted counts {arms[0]}/{arms[1]} vs "
                                   f"{arms[2]}/{arms[3]} imply "
                                   f"{round(_rr_from_counts(*arms) or 0, 3)} but the source reports "
                                   f"{rep[0]} {rep[1]} — counts likely belong to a different outcome; refused")}
            return {"ai": arms[0], "n1i": arms[1], "ci": arms[2], "n2i": arms[3],
                    "source": "abstract arm-level counts (percentage-corroborated): " + s.strip()[:200]}
    for s in sents:
        if (_is_subgroup_sentence(s) or (factorial and not _interv_in(s, interv_terms))
                or (_skip_composite and _names_composite(s))):
            continue
        eff = extract_effect(s)
        if eff:
            return {"effect": eff[1], "ci_low": eff[2], "ci_high": eff[3], "scale": eff[0],
                    "source": f"abstract effect+CI ({eff[0]}): " + s.strip()[:200]}
    # Incidence-rate fallback: explicit per-arm events + person-time (recurrent-event class).
    # Lowest priority so binary counts / ratio effects are preferred; refuses ambiguous rates.
    for s in sents:
        if (_is_subgroup_sentence(s) or (factorial and not _interv_in(s, interv_terms))
                or (_skip_composite and _names_composite(s))):
            continue
        rate = extract_rate(s, interv_terms, comp_terms)
        if rate:
            return {"e1i": rate[0], "t1i": rate[1], "e2i": rate[2], "t2i": rate[3],
                    "measure": "IRR",
                    "source": "abstract events + person-time (incidence-rate ratio): " + s.strip()[:200]}
    # Continuous fallback: mean-difference from per-arm mean+/-SD (+ per-arm n from the abstract).
    ns = _arm_ns(abstract, interv_terms, comp_terms)
    for s in sents:
        if (_is_subgroup_sentence(s) or (factorial and not _interv_in(s, interv_terms))
                or (_skip_composite and _names_composite(s))):
            continue
        cont = extract_continuous(s, interv_terms, comp_terms, ns)
        if cont:
            return {"mean1": cont[0], "sd1": cont[1], "nc1": cont[2],
                    "mean2": cont[3], "sd2": cont[4], "nc2": cont[5], "measure": "MD",
                    "source": "abstract mean+/-SD per arm (mean difference): " + s.strip()[:200]}
    if factorial:
        return {"absent": True, "reason": ("factorial-design trial: no extraction sentence explicitly "
                "names the intervention, so the effect cannot be attributed to our comparison "
                "rather than the co-randomised factor; refused (factorial guard)")}
    return {"absent": True, "reason": "no percentage-corroborated arm counts or effect+CI for this outcome found in the abstract"}


def _parse_k(abstract):
    m = _K.search(abstract)
    if m:
        tok = m.group(1).lower()
        return int(tok) if tok.isdigit() else _WORDNUM.get(tok)
    return None


def effect_in_outcome(abstract, kws):
    """Effect+CI associated with THIS outcome. Each effect is assigned to the outcome keyword
    in its CLAUSE = the text since the previous effect match (capped so a far-back keyword
    can't bind). This handles both a long single-outcome sentence (keyword far before its
    effect) and several effects packed in one sentence (recurrence RR, then AE RR, then
    withdrawal RR) — each effect binds to the keyword in its own clause, not the first."""
    abstract = _norm(abstract)
    low = abstract.lower()
    kl = [k.lower() for k in kws]
    prev_end = 0
    for m in _EFFECT.finditer(abstract):
        clause = low[prev_end:m.start()][-260:]
        if any(k in clause for k in kl):
            e = _effect_from_match(m)
            if e:
                return {"effect": e[1], "ci_low": e[2], "ci_high": e[3], "scale": e[0],
                        "source": abstract[prev_end:m.end()].strip()[-240:]}
        prev_end = m.end()
    return None


def comparator_effect(abstract, fulltext, kws):
    """SOURCE HIERARCHY for a published comparator's reported effect, explicit and testable:
      1. the ABSTRACT's headline effect for the outcome (what the authors chose to report), then
      2. the FULL TEXT — used ONLY to fill an outcome the abstract does not state.
    Full text must NOT override an abstract headline: full text carries many analyses
    (subgroups, sensitivity) and grabbing one silently substitutes the wrong figure (this is
    how topic 1's comparator primary became 0.46 instead of the abstract's 0.40)."""
    return effect_in_outcome(abstract or "", kws) or effect_in_outcome(fulltext or "", kws)


def extract_meta(abstract, outcome_kws):
    """Comparator meta: pooled effect+CI for the outcome, and k."""
    abstract = _norm(abstract)
    eff = None
    for pool_sents in (_outcome_sentences(abstract, outcome_kws), _sentences(abstract)):
        for s in pool_sents:
            e = extract_effect(s)
            if e:
                eff = {"effect": e[1], "ci_low": e[2], "ci_high": e[3], "scale": e[0], "source": s.strip()[:220]}
                break
        if eff:
            break
    return {"primary": eff, "k": _parse_k(abstract)}
