"""NARRATIVE RULES for text the harness GENERATES (external review of doac-vte-recurrence, 2026-09-26).

1. Never infer noninferiority or equivalence from a pooled interval (crossing 1 or not): the trials used prespecified NI margins that
   a pooled ratio does not test. A sentence on the page that asserts noninferiority / equivalence / comparable efficacy is allowed
   ONLY as a verbatim quotation of held source text (a trial's own conclusion, quoted); anything else is a generated inference and
   the publication gate refuses the page (check_ni_inference).
2. Name treatment STRATEGIES, not bare drugs: "parenteral lead-in then dabigatran" (RE-COVER, Hokusai) vs "rivaroxaban alone"
   (EINSTEIN, AMPLIFY) -- read from the held abstract, never guessed (strategy_label).
3. State analysis populations literally, as the source states them (populations_stated) -- e.g. an efficacy analysis restricted to
   patients with documented status, or an on-treatment safety analysis -- never a declared "intention-to-treat" the source does not
   state (the derived label in outcome_tiers already refuses to assert it).
"""
from __future__ import annotations

import html as _html
import re
from typing import Any, Iterable

# CLAIM constructions only (a bare "equivalent" is ordinary prose: "not equivalent to adjudication-confirmed cases", "Embase-
# equivalent coverage", "equivalent doses"; "non-inferiority trial" is a design label). Negated forms are not claims.
_NI = re.compile(r"(?i)\b(?:is|are|was|were|be|been|proved|remains?)\s+(?:shown\s+to\s+be\s+|found\s+to\s+be\s+)?non-?inferior\b"
                 r"|\bnon-?inferior(?:ity)?\s+(?:to|of|versus|vs\.?|compared)\b"
                 r"|\b(?:is|are|was|were|be|been)\s+(?:clinically\s+|therapeutically\s+)?equivalent\s+(?:to|with)\b"
                 r"|\bequivalence\s+(?:was|were)\s+(?:shown|demonstrated|established)\b"
                 r"|\bcomparable\s+(?:efficacy|effectiveness)\b|\bas\s+effective\s+as\b|\bsimilar\s+efficacy\b|\bno\s+less\s+effective\b")
_NEGATED = re.compile(r"(?i)\bnot\s+(?:shown\s+to\s+be\s+)?$")


def _norm(s: str) -> str:
    s = _html.unescape(s or "").replace("·", ".")
    return " ".join(s.split()).lower()


def page_sentences(page_html: str) -> list[str]:
    text = _norm(re.sub(r"<[^>]+>", " ", page_html or ""))
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]


def check_ni_inference(page_html: str, held_texts: Iterable[str]) -> list[dict[str, Any]]:
    """Every NI / equivalence phrase on the page must sit inside a verbatim window of held source text (the 40 characters on each
    side of the phrase, trimmed to what the sentence has). Returns the offending phrases with their sentence."""
    corpus = "\n".join(_norm(t) for t in held_texts if t)
    bad = []
    for sent in page_sentences(page_html):
        if "publication types:" in sent:
            continue                    # PubMed metadata ("Equivalence Trial") rendered in a screening list: a label, not a claim
        for m in _NI.finditer(sent):
            if _NEGATED.search(sent[max(0, m.start() - 20):m.start()]) or re.search(r"(?i)\bnot\s+$", sent[:m.start()][-8:]):
                continue
            # a quotation of held text: the text on EITHER side of the phrase matches (a quote the page truncates keeps its left side)
            left = sent[max(0, m.start() - 40):m.end()].strip(" .;:,")
            right = sent[m.start():min(len(sent), m.end() + 40)].strip(" .;:,")
            if left not in corpus and right not in corpus:
                bad.append({"phrase": m.group(0), "sentence": sent[:300]})
    return bad


_LEAD_IN = re.compile(r"(?i)after\s+(?:initial\s+)?(?:treatment\s+with\s+)?(?:at\s+least\s+\d+\s+days?\s+of\s+)?(?:parenteral|heparin|"
                      r"low[- ]molecular[- ]weight\s+heparin|lmwh|enoxaparin)|parenteral\s+(?:anticoagulation|therapy|lead[- ]in)\s+"
                      r"(?:followed\s+by|then)|lead[- ]in|initial\s+(?:parenteral\s+)?(?:heparin|anticoagulation)\s+(?:for|followed)"
                      # RE-COVER: "initially given parenteral anticoagulation therapy for a median of 9 days"; RE-COVER II: "treated with
                      # low-molecular-weight or unfractionated heparin for 5 to 11 days"
                      r"|initially\s+(?:given|treated\s+with|received)\s+(?:parenteral|heparin|low[- ]molecular)"
                      r"|treated\s+with\s+(?:low[- ]molecular[- ]weight|unfractionated|parenteral)[^.;]{0,60}?(?:heparin|anticoagula\w*)\s+for\s+\d")
# "alone" counts only when tied to the DRUG ("apixaban alone"), never "major bleeding alone" (AMPLIFY's safety outcome)
_ALONE_ANY = r"\bsingle[- ]drug\b|without\s+(?:initial\s+)?(?:parenteral|heparin)"


def strategy_label(abstract: str | None, drug: str) -> dict[str, Any]:
    """The treatment STRATEGY the trial tested, read from its held abstract: 'parenteral lead-in then <drug>' or '<drug> alone (no
    parenteral lead-in)'; NOT_STATED when the abstract says neither (never guessed from the drug name)."""
    a = abstract or ""
    if _LEAD_IN.search(a):
        return {"strategy": f"parenteral lead-in then {drug}", "basis": _LEAD_IN.search(a).group(0)}
    alone = re.search(rf"(?i)\b{re.escape(drug)}\s+alone\b|{_ALONE_ANY}", a)
    if alone:
        return {"strategy": f"{drug} alone (no parenteral lead-in)", "basis": alone.group(0)}
    return {"strategy": "NOT_STATED_IN_HELD_TEXT", "basis": f"the held abstract states no lead-in or single-drug strategy for {drug}"}


_POP = re.compile(r"(?i)(?:efficacy|safety|primary)\s+(?:analysis|outcome)?\s*(?:was|were)?\s*(?:assessed|analy[sz]ed|evaluated)?\s*"
                  r"(?:in|among)\s+([^.;]{0,120}?(?:intention[- ]to[- ]treat|per[- ]protocol|on[- ]treatment|modified|documented|"
                  r"received\s+at\s+least\s+one\s+dose|all\s+randomi[sz]ed)[^.;]{0,60})")


def populations_stated(abstract: str | None) -> list[str]:
    """The analysis populations the held abstract states, VERBATIM -- for literal display; empty when it states none."""
    return [m.group(0).strip() for m in _POP.finditer(abstract or "")]
