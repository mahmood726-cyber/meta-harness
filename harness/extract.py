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


def extract_arm_counts(sentence, interv_terms, comp_terms, denom_each=None):
    """Return (ai,n1i,ci,n2i) if two corroborated arm groups are found, else None."""
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
    if len(groups) < 2 and denom_each:
        # "N [patients] (P%)"/"[P%]" with the denominator inferred from the abstract; accept
        # only if some candidate denominator corroborates the stated percentage for that arm.
        cands = denom_each if isinstance(denom_each, (list, tuple, set)) else [denom_each]
        cands = [int(c) for c in cands if c]
        for m in _ARMP.finditer(sentence):
            ev, pct = int(m.group(1)), float(m.group(2))
            if _negated(sentence, m.start()):
                continue
            best = None
            for den in cands:
                if den > 0 and ev <= den and abs(ev / den * 100 - pct) <= 1.0:
                    if best is None or abs(ev / den * 100 - pct) < abs(ev / best * 100 - pct):
                        best = den
            if best:
                groups.append((m.start(), ev, best))
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
        if not any(g in sl for g in generic):
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


def _is_factorial(abstract):
    return bool(_FACTORIAL.search(abstract or ""))


def _interv_in(sentence, interv_terms):
    sl = (sentence or "").lower()
    return any(t.lower() in sl for t in interv_terms)


def extract_trial(abstract, outcome_kws, interv_terms, comp_terms):
    """Best conservative extraction for one trial's outcome. Returns dict or a reason."""
    abstract = _norm(abstract)
    dm = _DENOM_EACH.search(abstract)
    cand = [int(x) for x in _NEQ.findall(abstract)]
    if dm:
        cand.append(int(dm.group(1)))
    denom_each = sorted(set(cand)) or None
    # FACTORIAL-DESIGN GUARD: a trial with more than one randomised comparison (e.g. SU.FOL.OM3
    # randomised B vitamins AND n-3) can have the extractor bind the WRONG factor's effect (it
    # bound the B-vitamin HR 0.9 instead of the omega-3 HR 1.08). When the design is factorial we
    # only accept an extraction from a sentence that explicitly names OUR intervention, so the
    # number is provably for our comparison, not the co-randomised one.
    factorial = _is_factorial(abstract)
    sents = _outcome_sentences(abstract, _effective_kws(abstract, outcome_kws))
    for s in sents:
        if factorial and not _interv_in(s, interv_terms):
            continue
        arms = extract_arm_counts(s, interv_terms, comp_terms, denom_each)
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
        if factorial and not _interv_in(s, interv_terms):
            continue
        eff = extract_effect(s)
        if eff:
            return {"effect": eff[1], "ci_low": eff[2], "ci_high": eff[3], "scale": eff[0],
                    "source": f"abstract effect+CI ({eff[0]}): " + s.strip()[:200]}
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
