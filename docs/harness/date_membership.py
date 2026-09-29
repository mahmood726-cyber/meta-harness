"""No membership by publication date (V1.0.1, tocilizumab-COVID review).

IMMCoVA's own paper is from 2023 (PMID 38157348, NCT04412291); WHO REACT's 2021 prospective meta-analysis already
analysed it (its Figure 1 prints an 'ImmCoVA' row). A trial is in or out of a comparator by registration, trial
identity and analysis membership -- never because its paper post-dates the comparator. Treating the 2023 paper as a new
trial would count IMMCoVA twice.

claims(text) finds sentences that decide comparator membership or a trial's uniqueness FROM A DATE: 'published after
the comparator', 'not in the comparator because it was published later', 'new since the review's search', 'unique
because more recent'. The gate refuses a page that serves one; a sentence that states the rule (publication year is
never used ...) is not a claim.
"""
from __future__ import annotations

import html as _html
import re

_SENT = re.compile(r"[^.!?]*[.!?]")
_DATE_REASON = re.compile(
    r"(?i)\b(?:published|reported|appeared|came out|was released)\s+(?:after|later than|since|following)\b"
    r"|\bpost-?dates?\b|\bnewer than\b|\bmore recent than\b|\bsince (?:the|its) (?:comparator|review|search|meta-analysis)\b"
    r"|\bbecause (?:it|its paper|the paper|the report) (?:was|is) (?:published|reported) (?:later|after)\b")
_MEMBERSHIP = re.compile(r"(?i)\b(?:not (?:in|included in|part of)|absent from|missing from|unique|new|additional|"
                         r"not yet in|not covered by|excluded from)\b")
_COMPARATOR = re.compile(r"(?i)\b(?:comparator|meta-analysis|review|REACT|search|pool)\b")
_RULE = re.compile(r"(?i)\b(?:never|not) (?:used|a reason|evidence)\b|\bpublication year is never\b|\bnever by dates?\b")


def claims(text: str) -> list:
    """Sentences that decide membership or uniqueness from a publication date."""
    plain = _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text or "")))
    out = []
    for s in _SENT.findall(plain):
        if _DATE_REASON.search(s) and _MEMBERSHIP.search(s) and _COMPARATOR.search(s) and not _RULE.search(s):
            out.append(s.strip())
    return out


def gate_reasons(page_html: str) -> list:
    return [f"DATE_DECIDES_MEMBERSHIP: {c[:200]}" for c in claims(page_html)]
