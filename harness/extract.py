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
    r"(relative risk reduction|relative risk|risk ratio|incidence rate ratio|rate ratio|\bRR\b|odds ratio|\bOR\b|hazard ratio|\bHR\b)"
    r"[^0-9]{0,25}?(\d+(?:\.\d+)?)[^0-9]{0,28}?(?:95%\s*(?:confidence interval|CI)|\bCI\b)"
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
    scale = "OR" if "odds" in kind or kind == "or" else ("HR" if "hazard" in kind or kind == "hr" else "RR")
    if not (lo <= pt <= hi):
        return None
    return (scale, pt, lo, hi)


def extract_effect(sentence):
    """Return (scale, point, lo, hi) from the FIRST effect+CI phrase, else None."""
    m = _EFFECT.search(sentence)
    return _effect_from_match(m) if m else None


GENERIC_ANCHORS = {"primary outcome", "primary end point", "primary endpoint",
                   "primary study outcome", "primary study end point"}


def _effective_kws(abstract, outcome_kws):
    """Generic 'primary outcome/endpoint' anchors are used ONLY when the trial's primary
    outcome IS our outcome (a sentence links a generic anchor to a disease keyword). This
    stops us reading a trial's PRIMARY result when its primary endpoint is a different
    outcome than ours (e.g. COPPS-2's primary is postpericardiotomy syndrome, not AF)."""
    disease = [k for k in outcome_kws if k.lower() not in GENERIC_ANCHORS]
    generic = [k for k in outcome_kws if k.lower() in GENERIC_ANCHORS]
    if not generic:
        return disease
    low = abstract.lower()
    for s in _sentences(abstract):
        sl = s.lower()
        if any(g in sl for g in generic) and any(dk.lower() in sl for dk in disease):
            return disease + generic  # the trial's primary outcome is ours
    return disease


def extract_trial(abstract, outcome_kws, interv_terms, comp_terms):
    """Best conservative extraction for one trial's outcome. Returns dict or a reason."""
    abstract = _norm(abstract)
    dm = _DENOM_EACH.search(abstract)
    cand = [int(x) for x in _NEQ.findall(abstract)]
    if dm:
        cand.append(int(dm.group(1)))
    denom_each = sorted(set(cand)) or None
    sents = _outcome_sentences(abstract, _effective_kws(abstract, outcome_kws))
    for s in sents:
        arms = extract_arm_counts(s, interv_terms, comp_terms, denom_each)
        if arms:
            return {"ai": arms[0], "n1i": arms[1], "ci": arms[2], "n2i": arms[3],
                    "source": "abstract arm-level counts (percentage-corroborated): " + s.strip()[:200]}
    for s in sents:
        eff = extract_effect(s)
        if eff:
            return {"effect": eff[1], "ci_low": eff[2], "ci_high": eff[3], "scale": eff[0],
                    "source": f"abstract effect+CI ({eff[0]}): " + s.strip()[:200]}
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
