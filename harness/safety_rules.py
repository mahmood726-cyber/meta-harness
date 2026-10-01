"""Safety-analysis rules that apply identically to every review (esketamine fixtures).

* Protocol status: a harm outcome is PRESPECIFIED only if the protocol's outcome sections (PICO / Outcomes / Estimand, including an
  'O (harms)' line) name it by its own words; otherwise it is EXPLORATORY. A mention elsewhere (eligibility, exclusions) is not a
  registration.
* Safety denominators: a harm row's denominators come from the SAFETY analysis set (the safety table's arm N or the row's own n/N),
  never from the efficacy analysis set when the two differ (TRANSFORM-1: safety 231/113, efficacy 209/108).
* Symptom rows are never summed into any-AE: one patient can appear in several rows. Only a row labelled as the any-AE total
  (e.g. 'TEAEs', 'patients with >=1 AE') stands for it.
"""
from __future__ import annotations

import re
from typing import Any

from . import evidence_identity

_OUTCOME_SECTION = re.compile(r"^#{1,6}\s*(?:PICO|Outcomes?|Estimand)\b.*?(?=^#{1,6}\s|\Z)", re.I | re.M | re.S)
_HARMS_LINE = re.compile(r"^.*\b(?:O \(harms\)|harms?|safety outcomes?)\b.*$", re.I | re.M)


def protocol_outcome_text(protocol_md: str) -> str:
    """Only the sections where a protocol DECLARES outcomes; eligibility and exclusion text is not a registration."""
    return "\n".join(m.group(0) for m in _OUTCOME_SECTION.finditer(protocol_md or ""))


_PIC_LINE = re.compile(r"^\s*[-*]?\s*\**\s*(?:P|I|C|Population|Participants|Intervention|Comparator|Design)\b\s*\**\s*[:(\-—]", re.I)
_GENERIC_AE = re.compile(r"\badverse (?:events?|effects?|reactions?)\b|\bside effects?\b|\bteaes?\b", re.I)


def _declaring_lines(protocol_md: str) -> list[str]:
    """Lines of the outcome sections that DECLARE outcomes -- never a P / I / C / design line (a population line naming 'type 2
    diabetes' does not register 'diabetic ketoacidosis')."""
    decls = []                                        # a bullet and its wrapped continuation lines are ONE declaration
    for line in protocol_outcome_text(protocol_md).splitlines():
        if not line.strip():
            continue
        if re.match(r"\s*(?:[-*]|#|\d+[.)])\s", line) or not decls:
            decls.append(line)
        else:
            decls[-1] += " " + line.strip()
    return [d for d in decls if not _PIC_LINE.search(d)]


def protocol_status(outcome: dict[str, Any], protocol_md: str | None) -> dict[str, Any]:
    """PRESPECIFIED only when ONE outcome-declaring line names EVERY content word of the outcome (a registration is a declaration,
    not a word shared with another outcome: 'cardiovascular' in the MACE line does not register 'non-cardiovascular death')."""
    if protocol_md is None:
        return {"status": "PROTOCOL_NOT_HELD", "basis": "no committed protocol for this review"}
    if outcome.get("primary"):
        return {"status": "PRESPECIFIED_PRIMARY", "basis": "the primary outcome"}
    name = (outcome.get("name") or "").lower()
    words = [w for w in re.findall(r"[a-z]{5,}", name) if w not in ("adverse", "effects", "events", "outcome", "leading")]
    for line in _declaring_lines(protocol_md):
        low = line.lower()
        if (all(w[:6] in low for w in words) if words else bool(_GENERIC_AE.search(low))):
            if "non-" in name and not re.search(r"\bnon[- ]?" + re.escape(name.split("non-", 1)[1][:6]), low):
                continue                                  # 'non-cardiovascular death' needs the 'non-', not just its words
            return {"status": "PRESPECIFIED", "basis": f"declared in the protocol: {line.strip()[:160]}"}
    return {"status": "EXPLORATORY",
            "basis": "not declared in the protocol's outcome sections (PICO / Outcomes / Estimand); reported as exploratory"}


def annotate_protocol_status(review: dict[str, Any], protocol_md: str | None) -> list[dict[str, Any]]:
    """Producer step: every outcome carries its protocol status; returns the harm outcomes marked EXPLORATORY."""
    out = []
    for o in review.get("outcomes") or []:
        o["protocol_status"] = protocol_status(o, protocol_md)
        if o.get("kind") == "harm" and o["protocol_status"]["status"] == "EXPLORATORY":
            out.append({"outcome": o.get("name")})
    return out


def denominator_problem(harm_ns: tuple, efficacy_ns: tuple | None, safety_ns: tuple | None) -> str | None:
    """None when the harm row's denominators are the safety set's; otherwise the typed problem. Never infers a safety N."""
    if safety_ns is None:
        return None if efficacy_ns is None or harm_ns != efficacy_ns else "SAFETY_DENOMINATOR_UNVERIFIED_EQUALS_EFFICACY"
    if harm_ns == safety_ns:
        return None
    if efficacy_ns is not None and harm_ns == efficacy_ns:
        return "DENOMINATOR_REUSED_ACROSS_ANALYSIS_SETS"
    return "DENOMINATOR_NOT_FROM_SAFETY_SET"
