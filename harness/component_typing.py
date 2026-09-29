"""COMPONENT-SET TYPING, derived: the components of a trial's OWN primary composite, read from its held definition
sentence (harness/target_endpoint._definition_sentences) -- never declared by hand.

Statins in older adults (2026-09-28): the served 'major vascular events' pool mixes trial-defined composites (JUPITER:
MI, stroke, arterial revascularisation, unstable-angina hospitalisation, CV death; STAREE: CV death, nonfatal MI or
stroke, coronary revascularisation), and HOPE-3's >= 70 result would be a 3-POINT outcome. The endpoint policy
(harness/endpoint_policy.py) needs each input's component set typed; this derives it, and lists every item of the
definition that the component vocabulary does NOT type ('arterial revascularization') instead of silently dropping it.

  derive(abstract) -> {'components': [...], 'untyped': [...], 'definition_span': str} or None
"""
from __future__ import annotations

import re
from typing import Any

# the FIRST enumerated list: a parenthetical, or 'composite of ...' up to the next parenthesis / sentence end (a second
# composite in the same sentence -- STAREE's disability-free survival -- is never read as the first one's items)
_LIST = re.compile(r"\(([^()]{8,400})\)|(?:composite|consisting|defined as|comprising)\s+of\s+([^.;()]{8,400})", re.I)


def _items(span: str) -> list[str]:
    m = _LIST.search(span or "")
    body = (m.group(1) or m.group(2)) if m else ""
    parts = re.split(r",\s*|\s+or\s+|\s+and\s+", body)
    return [p.strip(" .()") for p in parts if len(p.strip(" .()")) > 2]


def derive(abstract: str | None) -> dict[str, Any] | None:
    from . import target_endpoint as te
    defs = [d for d in te._definition_sentences(abstract or "") if d.get("primary")]
    if not defs:
        return None
    d = defs[0]
    untyped = [it for it in _items(d["span"]) if not te._components_from_text(it, expand_named_composites=True)]
    return {"components": sorted(d["components"]), "untyped": untyped, "definition_span": d["span"],
            "basis": "harness.target_endpoint._definition_sentences on the trial's held abstract"}
