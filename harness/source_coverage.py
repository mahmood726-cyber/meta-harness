"""SOURCE COVERAGE from held bytes (external audit E1: r3 #1, r6 omarigliptin, r7 #4, r17-03, r27-03 Moll, r28 STRENGTH).

A file's presence is not coverage. A PMC "publisher does not allow downloading" response, an XML with no <body>, or a
repository portal page all sat in the cache as "full text", and the pages said "held full text: CHECKED" and declared
outcomes absent from them. Every held source object gets ONE coverage label computed from its own bytes:

  FULLTEXT       the article's body is held (XML <body> with text, or prose carrying the article's sections)
  FULL_ABSTRACT  a complete abstract: every unit of a retained PubMed acquisition is preserved (see abstract_label)
  EXCERPT        part of a document: a self-declared excerpt, a short / sectionless text, an abridged abstract
  SUMMARY        a generated compression or summarisation (never a representation of the source)
  METADATA       a portal / landing page: bibliographic metadata, at most an abstract
  STUB           no content was delivered: the PMC no-download response, an XML with front matter and no <body>

The labels are DEFINED as the bundle's coverage_status (scripts/build_bundle.py VOCABULARY), not a parallel list:
FULLTEXT = COMPLETE_SOURCE scope, FULL_ABSTRACT = COMPLETE_ABSTRACT, EXCERPT / SUMMARY = EXCERPT_ONLY, METADATA / STUB =
no representation of the content. Its asymmetric rule applies: an ABSENCE claim may rest only on a COMPLETE_* object for
the scope searched (absence_licensed).
"""
from __future__ import annotations

import hashlib
import re

LABELS = ("FULLTEXT", "FULL_ABSTRACT", "EXCERPT", "SUMMARY", "METADATA", "STUB")
BUNDLE_COVERAGE = {"FULLTEXT": "COMPLETE_SOURCE", "FULL_ABSTRACT": "COMPLETE_ABSTRACT", "EXCERPT": "EXCERPT_ONLY",
                   "SUMMARY": "EXCERPT_ONLY", "METADATA": None, "STUB": None}
SCOPE = {"FULLTEXT": "fulltext", "FULL_ABSTRACT": "abstract"}

PMC_NO_DOWNLOAD = "does not allow downloading of the full text"
# a self-declared coverage header written by an acquisition step ('SOURCE EXCERPT -- NOT A COMPLETE DOCUMENT
# (coverage: EXCERPT_ONLY)', cache/spironolactone-hfref-mortality/ft_28824029.txt): the file's own statement wins
_DECLARED = re.compile(r"\(coverage:\s*([A-Z_]+)\)")
_DECLARED_GENERIC = re.compile(r"NOT A COMPLETE DOCUMENT")   # only when no '(coverage: X)' names a label (agy r3 #1)
# the ROOT element of a JATS document (after any XML declaration / doctype): an XHTML page behind '<?xml' is not JATS
# (codex e1-cov-r3 g1#1, agy r3 #2)
_ROOT_ELEMENT = re.compile(r"<(?![?!])([\w.-]+:)?([\w.-]+)")
# repository / portal page markers (Pure 'Research output', Scopus counts, an RIS export block)
_PORTAL = re.compile(r"Research output\s*:\s*Contribution to journal|Citations\s*\(Scopus\)|Overview\s+Fingerprint"
                     r"|^\s*(?:UR|ER|DO|AN|SN|M3)\s+-\s", re.M)
# section words of an article body, matched as words anywhere (flattened JATS loses the line breaks)
_SECTIONS = (re.compile(r"\b(?:Introduction|INTRODUCTION|Background|BACKGROUND)\b"),
             re.compile(r"\b(?:Methods|METHODS|Materials and [Mm]ethods|MATERIALS AND METHODS|Study [Dd]esign)\b"),
             re.compile(r"\b(?:Results|RESULTS)\b"),
             re.compile(r"\b(?:Discussion|DISCUSSION)\b"))
_JATS_START = ("<?xml", "<pmc-articleset", "<article", "<!doctype pmc-articleset", "<!doctype article")
_HTML_START = ("<!doctype html", "<html")
_HTTP_ERROR = re.compile(r"<(?:title|h1)>\s*(?:[45]\d\d\b[^<]*|(?:Gateway Time-?out|Bad Gateway|Service Unavailable|"
                         r"Not Found|Forbidden|Access Denied|Too Many Requests)[^<]*)</(?:title|h1)>", re.I)
# <body>, <jats:body>, <body/> -- and never <body-matter> ('-' is a word boundary for \b: agy r3 #3)
_TAG_BODY_OPEN = re.compile(r"<(?:[\w.-]+:)?body(?=[\s/>])[^>]*?(/?)>", re.I)
FULLTEXT_MIN_CHARS = 8000          # prose: a full article; an abstract with 'Methods: ... Results:' labels is shorter
REVISION_MIN_SIMILARITY = 0.97     # a revised PubMed record (spelling / one corrected word) v an abridgement (OMNeON: 0.69)
REVISION_MAX_LENGTH_DELTA = 0.03
REVISION_MIN_UNIT_COVERAGE = 0.6   # and EVERY acquired unit >= 60% present in runs of >= RUN_WORDS words (case- and
                                   # punctuation-normalised): a reworded unit passes (41831311 0.84, a changed URL 0.63),
                                   # a dropped unit scores ~0 -- and no number may be lost or changed (_numbers)
RUN_WORDS = 4


def _norm_words(x: str) -> str:
    # all punctuation is a word separator here ('www.clinicaltrials.gov' v 'clinicaltrials.gov'); numbers are compared
    # separately and exactly (_numbers), so nothing numeric is lost by this
    return re.sub(r"[^\w\s]", " ", (x or "").lower())


def _numbers(x: str) -> list:
    """Every number in a text, with multiplicity: a revision may reword, never lose or change a number."""
    return sorted(re.findall(r"\d+(?:[.·]\d+)?", x or ""))
_DECLARED_LABEL = {"EXCERPT_ONLY": "EXCERPT", "EXCERPT": "EXCERPT", "SUMMARY": "SUMMARY", "METADATA": "METADATA",
                   "STUB": "STUB", "UNKNOWN_COMPLETENESS": "EXCERPT"}


def _text(raw) -> str:
    t = raw.decode("utf-8", "replace") if isinstance(raw, (bytes, bytearray)) else str(raw or "")
    return t.lstrip("\ufeff")                     # a UTF-8 BOM is not content (codex e1-cov-r2 g1#3)


def label_document(raw) -> dict:
    """{label, reason, bundle_coverage, chars}: the coverage of ONE held file, from its bytes alone."""
    t = _text(raw)
    head = t.lstrip()[:300].lower()
    out = lambda lab, why: {"label": lab, "reason": why, "bundle_coverage": BUNDLE_COVERAGE[lab], "chars": len(t)}  # noqa: E731
    # evidence that nothing was delivered comes first: no header can outrank it (codex e1-cov-r1 g1#2)
    if PMC_NO_DOWNLOAD in t:
        return out("STUB", "PMC_NO_DOWNLOAD")
    if not t.strip():
        return out("STUB", "EMPTY")
    if _HTTP_ERROR.search(t[:2000]) and len(t) < 5000:
        # a saved server error response ('504 Gateway Time-out', comparators 24963045 / 38128217) delivered nothing
        return out("STUB", "HTTP_ERROR_PAGE")
    m = _DECLARED.search(t[:600])
    declared = m.group(1) if m else ("EXCERPT_ONLY" if _DECLARED_GENERIC.search(t[:600]) else None)
    if declared and declared not in ("COMPLETE_SOURCE", "COMPLETE_ABSTRACT"):
        # a header may LOWER coverage (an acquisition step saying 'this is an excerpt'); it never RAISES it: a
        # declared COMPLETE_* is ignored and the bytes decide (codex e1-cov-r1 g1#2); a declared METADATA / STUB keeps
        # its own label (agy e1-cov-r1-agy #2), even beside the generic phrase (agy r3 #1)
        return out(_DECLARED_LABEL.get(declared, "EXCERPT"), f"SELF_DECLARED:{declared}")
    # portal / landing-page markers before any structure: an HTML page is never JATS (codex e1-cov-r2 g1#1)
    if _PORTAL.search(t):
        return out("METADATA", "PORTAL_PAGE")
    if head.startswith(_HTML_START):
        return out("METADATA", "HTML_PAGE")
    root = _ROOT_ELEMENT.search(t)
    if head.startswith(_JATS_START) and root and root.group(2).lower() == "html":
        return out("METADATA", "HTML_PAGE")          # XHTML behind an XML declaration (codex r3 #1, agy r3 #2)
    if head.startswith(_JATS_START):
        mo = _TAG_BODY_OPEN.search(t)
        if not mo:
            return out("STUB", "XML_NO_BODY")
        if mo.group(1) == "/":                       # <body/>: delivered nothing (agy e1-cov-r1-agy #3)
            return out("STUB", "XML_EMPTY_BODY")
        # a JATS <body> IS the article's complete body however short (a research letter's body is a few hundred
        # words: comparators 27757047): length is never coverage. Only an empty body delivered nothing -- and a body
        # with no closing tag is a TRUNCATED download, never complete (codex e1-cov-r1 g1#1). Namespace prefixes
        # (<jats:body>) are bodies too (agy e1-cov-r1-agy #1).
        close = re.search(r"</(?:[\w.-]+:)?body\s*>", t[mo.end():], re.I)
        if not close:
            return out("EXCERPT", "XML_TRUNCATED")
        body = re.sub(r"<[^>]+>", " ", t[mo.end():mo.end() + close.start()])
        if re.sub(r"\s+", " ", body).strip():
            return out("FULLTEXT", "XML_BODY")
        return out("STUB", "XML_EMPTY_BODY")
    groups = sum(1 for rx in _SECTIONS if rx.search(t))
    if len(t) >= FULLTEXT_MIN_CHARS and groups >= 3:
        return out("FULLTEXT", f"PROSE_SECTIONS:{groups}")
    return out("EXCERPT", f"PROSE_NOT_A_BODY:chars={len(t)},sections={groups}")


def abstract_label(held_abstract: str, acquired_units: list | None) -> dict:
    """An abstract's coverage against a RETAINED PubMed acquisition (scripts/build_bundle.preservation_record units):
    FULL_ABSTRACT only when every unit is preserved verbatim and nothing else is held; EXCERPT when units are missing;
    no acquisition -> label None (UNKNOWN_COMPLETENESS), never assumed full."""
    held = re.sub(r"\s+", " ", held_abstract or "").strip()
    if acquired_units is None:
        return {"label": None, "reason": "NO_RETAINED_ACQUISITION", "bundle_coverage": "UNKNOWN_COMPLETENESS"}
    if not held:
        return {"label": "METADATA", "reason": "NO_ABSTRACT_HELD", "bundle_coverage": None}
    # whitespace inside a section label is whitespace (PubMed prints 'METHODS AND RESULTS'; the cache 'METHODS AND
    # RESULTS'): the bundle's own documented normalisation, applied to the label as it is to the text
    units = [dict(u, label=re.sub(r"\s+", " ", u["label"]).strip()) if u.get("label") else u for u in acquired_units]
    pres = preservation_record(held, units)
    if pres["verdict"] == "PRESERVED":
        return {"label": "FULL_ABSTRACT", "reason": f"ALL_{pres['preserved']}_UNITS_PRESERVED",
                "bundle_coverage": "COMPLETE_ABSTRACT", "version_differs": False, "preservation": pres}
    # PubMed REVISES records (spelling, a corrected word): a held text as long as the current record and nearly
    # identical to it is a complete abstract of an EARLIER revision, not an abridgement. Recorded as version_differs
    # (a discrepancy to show, never hidden); an abridgement loses length and content and stays EXCERPT.
    import difflib
    acq = " ".join(((u["label"] + ": ") if u.get("label") else "") + u["text"] for u in units)
    ratio = difflib.SequenceMatcher(None, held, acq, autojunk=False).ratio()

    def unit_covered(u):
        # the share of THIS unit's WORDS found in the held text in runs of >= RUN_WORDS consecutive words: whole-text
        # similarity can hide a wholly missing unit (codex e1-cov-r1 g1#3), and scattered single characters can fake
        # coverage (codex e1-cov-r2 g1#2). A unit shorter than RUN_WORDS must be present verbatim (normalised).
        words = re.findall(r"\S+", _norm_words(u["text"]))
        if not words:
            return True
        if len(words) < RUN_WORDS:
            # a short unit must be a whole SENTENCE of the held text, not a substring: 'No deaths.' is not preserved by
            # 'No deaths were excluded from the analysis.' (codex e1-cov-r2 g1#2)
            core = re.escape(u["text"].strip().rstrip(".;:").strip())
            return bool(re.search(r"(?:^|[.;:]\s+)" + core + r"\s*(?:[.;:]|$)", held))
        hw = re.findall(r"\S+", _norm_words(held))
        blocks = difflib.SequenceMatcher(None, words, hw, autojunk=False).get_matching_blocks()
        return sum(b.size for b in blocks if b.size >= RUN_WORDS) >= REVISION_MIN_UNIT_COVERAGE * len(words)
    if ratio >= REVISION_MIN_SIMILARITY and abs(len(held) - len(acq)) <= REVISION_MAX_LENGTH_DELTA * max(len(acq), 1) \
            and all(unit_covered(u) for u in units) and _numbers(held) == _numbers(acq):
        return {"label": "FULL_ABSTRACT", "reason": f"REVISED_RECORD:similarity={ratio:.3f},chars={len(held)}v{len(acq)}",
                "bundle_coverage": "COMPLETE_ABSTRACT", "version_differs": True, "preservation": pres}
    return {"label": "EXCERPT", "version_differs": None, "reason": f"UNITS_MISSING:{pres['missing']}/{len(pres['units'])}"
            + (f";EXTRA_CHARS:{pres['extra_chars_in_cached_not_in_acquired']}" if pres["extra_chars_in_cached_not_in_acquired"] else ""),
            "bundle_coverage": "EXCERPT_ONLY", "preservation": pres}


def preservation_record(cached_abstract: str, units: list) -> dict:
    """The bundle's own preservation record (scripts/build_bundle.preservation_record), imported, never re-implemented."""
    import os
    import sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.join(root, "scripts") not in sys.path:
        sys.path.insert(0, os.path.join(root, "scripts"))
    import build_bundle
    return build_bundle.preservation_record(cached_abstract, units)


def absence_licensed(searched: list, scope: str = "abstract") -> bool:
    """The bundle's asymmetric rule, for the evidential SCOPE of the claim (agy e1-cov-r1-agy #4): 'not in the abstract'
    needs a complete ABSTRACT (a held article body says nothing about whether the abstract was acquired: codex
    e1-cov-r3 g1#2); 'not reported by the trial report' needs a FULLTEXT. An unknown scope fails closed (ValueError:
    codex e1-cov-r3 g1#3). searched = [label, ...] of the objects actually read."""
    need = {"abstract": "COMPLETE_ABSTRACT", "fulltext": "COMPLETE_SOURCE"}.get(scope)
    if need is None:
        raise ValueError(f"absence scope must be 'abstract' or 'fulltext', not {scope!r}")
    return any(BUNDLE_COVERAGE.get(lab) == need for lab in searched or [])


def sha256(raw) -> str:
    return hashlib.sha256(raw if isinstance(raw, (bytes, bytearray)) else _text(raw).encode("utf-8")).hexdigest()
