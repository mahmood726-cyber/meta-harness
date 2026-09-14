"""Absence-state ontology (external audit): 'declared absent' conflated four epistemically different
things, letting a page say 'no harms recorded' while the abstract reports a harm. Split them, and
reserve the strong claim for the first only:

  NO_OUTCOME_DATA_IN_SOURCE  — the retrieved source genuinely does not report this outcome. The ONLY
                               state that licenses 'declared absent' (a claim about the trial).
  EXTRACTION_NOT_PERFORMED   — the outcome's effect/counts ARE in the retrieved source but were not
                               machine-extracted (a claim about US, not the trial). The false-absence class.
  SOURCE_NOT_RETRIEVED       — only the abstract was retrieved and it does not report this (usually a
                               secondary/harm); the full text was not fetched, so absence in the TRIAL
                               is not established — we cannot distinguish 'not in trial' from 'not in abstract'.
  OUTCOME_NOT_REQUESTED      — the outcome is not on this topic's prespecified list (handled upstream;
                               a declared-absent trial is always about a REQUESTED outcome, so the
                               per-trial classifier returns one of the three above).

`UNASSESSED NEVER COUNTS AS FAVOURABLE`: none of these is evidence of no effect.
"""
import re
from . import extract

_EFFECT = re.compile(r"\b(?:RR|OR|HR|IRR|rate ratio|risk ratio|hazard ratio|odds ratio|relative risk)\b"
                     r"[^.]{0,40}?\d+\.\d+", re.I)
_ARMS = re.compile(r"\b\d+\s*/\s*\d{2,}\b|\b\d+\s+of\s+\d{2,}\b|"
                   r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+of\s+\d{2,}\b", re.I)
_TAG = re.compile(r"<[^>]+>")


def _strip_markup(text):
    """Full texts are committed as raw JATS/HTML; the sentence splitter needs prose, not tags. Strip
    tags ONLY (and collapse whitespace) -- deliberately NOT dropping any region. The safety asymmetry:
    a spurious 'number present' only downgrades the strong DECLARED_ABSENT claim to a self-deprecating
    'extraction gap' (safe), whereas dropping a region that might hold the result (e.g. a JATS <back>
    appendix carrying a supplementary outcome table) could mask a real number and manufacture a false
    absence (dangerous). So we keep everything and only remove markup, which alone kills the tag-attribute
    numbers (id="FN3", DOIs) that caused a footnote to match. The abstract path is plain text (no-op)."""
    if not text or "<" not in text:
        return text
    return re.sub(r"\s+", " ", _TAG.sub(" ", text))


def _outcome_number_present(text, keywords):
    """True iff the OUTCOME's own sentences (selected by its keywords) contain an effect+CI or arm
    counts -- scoped, so a different outcome's number elsewhere in the text does not count."""
    if not text or not keywords:
        return False
    sents = " ".join(extract._outcome_sentences(_strip_markup(text), keywords))
    return bool(_EFFECT.search(sents) or _ARMS.search(sents))


def classify(keywords, abstract, fulltext=None):
    """Return (state, basis). `fulltext` is the committed full text if we hold it (else None)."""
    if _outcome_number_present(abstract, keywords) or (fulltext and _outcome_number_present(fulltext, keywords)):
        return ("EXTRACTION_NOT_PERFORMED",
                "the outcome's effect/counts ARE present in the retrieved source but were not "
                "machine-extracted; this is a limitation of extraction, NOT evidence the trial lacks the outcome")
    if fulltext:
        return ("NO_OUTCOME_DATA_IN_SOURCE",
                "neither the abstract nor the retrieved full text reports this outcome")
    return ("SOURCE_NOT_RETRIEVED",
            "only the abstract was retrieved and it does not report this outcome; the full text was not "
            "fetched, so absence of the outcome in the TRIAL is not established")
