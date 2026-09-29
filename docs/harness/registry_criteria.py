"""REGISTRY CRITERIA: a registration's own eligibility text, split into INCLUSION and EXCLUSION sections, read
deterministically (the held AACT eligibilities row; '~' is its line break).

Statins in older adults (2026-09-28): PREVENTABLE (NCT04262206) was screened out X2 because its registry CONDITION
labels list 'Dementia' -- which its own criteria EXCLUDE ('Dementia (clinically evident or previously diagnosed)') and
its primary outcome MEASURES. A condition label that appears ONLY in the exclusion section is not the trial's entry
condition, so it never vetoes; one that appears in the inclusion section (or nowhere in the criteria) still does.

  sections(criteria) -> (inclusion_text, exclusion_text)
  label_only_excluded(term, criteria) -> bool
  inclusion_matches(terms, criteria) -> the first term found in the INCLUSION section, or None
"""
from __future__ import annotations

import re
from typing import Iterable

_EXCL = re.compile(r"exclusion\s+criteria\s*:?", re.I)
_INCL = re.compile(r"inclusion\s+criteria\s*:?", re.I)


def _fold(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").replace("~", "\n").replace("\\", "")).lower()


def sections(criteria: str | None) -> tuple[str, str]:
    text = _fold(criteria)
    m = _EXCL.search(text)
    if not m:
        return text, ""
    inc = _INCL.sub(" ", text[:m.start()])
    return inc, text[m.end():]


def _has(text: str, term: str) -> bool:
    return bool(re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", text))


def label_only_excluded(term: str, criteria: str | None) -> bool:
    """True iff the criteria have an exclusion section naming `term` and the inclusion section does not."""
    inc, exc = sections(criteria)
    return bool(exc) and _has(exc, term) and not _has(inc, term)


def inclusion_matches(terms: Iterable[str], criteria: str | None) -> str | None:
    inc, _ = sections(criteria)
    return next((t for t in terms or [] if inc and _has(inc, t)), None)
