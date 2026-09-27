"""ARM PAIRS: a multi-arm (double-dummy) trial's comparisons are judged per PAIR of arms, on what the pair's arms
actually differ in -- never on whether a drug's NAME appears in an arm label.

CONFIDENCE (NCT05254002), 3-arm double-dummy:
  A 'Finerenone and Empagliflozin'          -> active {finerenone, empagliflozin}
  B 'Finerenone and Empagliflozin placebo'  -> active {finerenone}, placebo for {empagliflozin}
  C 'Empagliflozin and Finerenone placebo'  -> active {empagliflozin}, placebo for {finerenone}
  A vs C: finerenone vs placebo on an empagliflozin background  -> the eligible finerenone-vs-placebo contrast
  B vs C: finerenone vs empagliflozin                            -> an ACTIVE comparator, not placebo
  A vs B: empagliflozin vs placebo on a finerenone background    -> not a finerenone contrast at all
'Placebo for X' / 'X placebo' / 'matching placebo for X' is a placebo component, never the active drug X.
"""
from __future__ import annotations

import re
from typing import Any

_SPLIT = re.compile(r"\s*(?:\+|\band\b|\bwith\b|\bplus\b|,|;)\s*", re.I)
_PLACEBO_FOR = re.compile(r"^(?:matching\s+)?placebo\s+(?:for|to|of|matching)\s+(.+)$|^(.+?)\s+(?:matching\s+)?placebo$", re.I)
_DOSE = re.compile(r"\(.*?\)|\b\d+(?:\.\d+)?\s*(?:mg|mcg|µg|g)\b|\bdrug:\s*", re.I)


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", _DOSE.sub(" ", s)).strip().lower()


def parse_arm(label: str) -> dict[str, Any]:
    active, placebo_for, plain_placebo = set(), set(), False
    for part in _SPLIT.split(label or ""):
        p = _clean(part)
        if not p:
            continue
        m = _PLACEBO_FOR.match(p)
        if m:
            placebo_for.add((m.group(1) or m.group(2)).strip())
        elif p == "placebo" or p.startswith("matching placebo"):
            plain_placebo = True
        else:
            active.add(p)
    return {"label": label, "active": sorted(active), "placebo_for": sorted(placebo_for), "placebo": plain_placebo}


def contrast(experimental: str, comparator: str) -> dict[str, Any]:
    a, b = parse_arm(experimental), parse_arm(comparator)
    A, B = set(a["active"]), set(b["active"])
    return {"experimental_only": sorted(A - B), "comparator_only": sorted(B - A), "background": sorted(A & B),
            "comparator_placebo_for": b["placebo_for"], "comparator_placebo": b["placebo"] or bool(b["placebo_for"])}


def judge(experimental: str, comparator: str, agents: list[str]) -> dict[str, Any]:
    """Is this arm pair an intervention-vs-placebo contrast for one of `agents`? Returns fails (X3) or passes."""
    c = contrast(experimental, comparator)
    ag = [x.lower() for x in agents]
    names = lambda xs: [x for x in xs if any(g in x for g in ag)]
    fails = []
    if c["comparator_only"]:
        fails.append({"rule": "X3", "why": (f"the comparator arm gives {c['comparator_only']} that the experimental arm does "
                                            f"not: an active comparator, not placebo")})
    if not names(c["experimental_only"]):
        fails.append({"rule": "X3", "why": (f"the randomised difference is {c['experimental_only'] or 'nothing'}; "
                                            f"{', '.join(agents)} is {'background in both arms' if names(c['background']) else 'not randomised'}")})
    if not fails and not c["comparator_placebo"]:
        fails.append({"rule": "X3", "why": "the comparator arm has no placebo for the intervention"})
    return {"contrast": c, "fails": fails, "eligible_contrast": not fails}
