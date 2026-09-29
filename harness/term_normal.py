"""Comparator wording normalised before the comparator rule matches (V1.0.1, tocilizumab-COVID review).

Talaschian 2024 (PMID 38485912) randomised tocilizumab plus "standard-of-care (SOC)" against "SOC" and was excluded on
X3 ("no eligible comparator") because the rule looks for the words "standard of care" and the record prints them
hyphenated, then as an abbreviation. Two normalisations, and only these:
  1. hyphens and slashes between words are spaces ('standard-of-care' -> 'standard of care');
  2. an abbreviation is expanded ONLY where the text itself defines it AND its expansion is a comparator term:
     'standard-of-care (SOC)' makes every later whole-token 'SOC' read 'standard of care'. A bare 'SOC', 'UC' or 'BSC'
     that the text never defines is left alone ('UC' is ulcerative colitis as often as usual care), and so is a defined
     abbreviation that is not a comparator term ('AAD').
The normalised text is used for the comparator match only; spans are still quoted from the record's own words.
"""
from __future__ import annotations

import re

_HYPHEN = re.compile(r"(?<=[A-Za-z])\s*[-‐‑–/]\s*(?=[A-Za-z])")
# '<words> (ABBR)': the abbreviation's letters are the initials of the words just before it, in order
_DEFINED = re.compile(r"((?:[A-Za-z]+[\s-]+){1,6}?[A-Za-z]+)\s*\(\s*([A-Z]{2,6})\s*\)")


def _initials(words: str) -> str:
    return "".join(w[0] for w in re.split(r"[\s-]+", words) if w).upper()


def defined_abbreviations(text: str) -> dict:
    """{ABBR: expansion} for every '<expansion> (ABBR)' whose ABBR is the initials of the last len(ABBR) words
    (small words like 'of' count: 'standard of care (SOC)')."""
    out = {}
    for m in _DEFINED.finditer(text or ""):
        words = re.split(r"[\s-]+", m.group(1).strip())
        abbr = m.group(2)
        tail = words[-len(abbr):]
        if len(tail) == len(abbr) and _initials(" ".join(tail)) == abbr:
            out.setdefault(abbr, " ".join(tail))
    return out


def comparator_text(text: str, terms=None) -> str:
    """Hyphens as spaces, and ONLY the abbreviations whose expansion IS a comparator term ('SOC' -> 'standard of care'
    when 'standard of care' is a term). Expanding any other abbreviation would move words away from a negation:
    'patients without AAD as the control group' became '... without antibiotic associated diarrhea as the control group',
    out of the negation window, and a non-randomised comparison read as a control arm."""
    t = _HYPHEN.sub(" ", text or "")
    wanted = {re.sub(r"\s+", " ", _HYPHEN.sub(" ", str(x))).strip().lower() for x in terms or []}
    for abbr, expansion in defined_abbreviations(text or "").items():
        exp = _HYPHEN.sub(" ", expansion)
        if exp.lower() not in wanted:
            continue
        t = re.sub(r"(?<![A-Za-z0-9])" + re.escape(abbr) + r"(?![A-Za-z0-9])", exp, t)
    return t
