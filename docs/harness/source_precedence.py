"""SOURCE PRECEDENCE: a protocol's source hierarchy is an ORDER, not a prohibition.

The GLP-1 protocol lists "1 the trial's own publication and supplement; 2 regulatory review; 3 registry results; 4 HTA
assessment; 5 older meta-analyses -- pointers only, never the number itself" in DESCENDING PRIORITY: a lower tier is
used when the higher tiers are silent. Two PIONEER 6 harm rows were refused with "registry-only values do not meet this
lane's GLP-1 level-1-abstract/level-2-FDA requirement" -- a restriction the protocol never states. The held registry
results (level 3) reported one of the two outcomes outright.

  parse(protocol_text)  -> the levels, each PERMITTED or POINTER_ONLY, from the protocol's own hierarchy sentence
  problems(review)      -> HIERARCHY_TREATED_AS_PROHIBITION (blocking) for any not-pooled row whose stated reason
                           treats a PERMITTED level as disallowed (a tier 'requirement', or '<tier>-only values do not
                           meet'); a reason excluding a POINTER_ONLY level is the protocol's own rule, never flagged.
"""
from __future__ import annotations

import re
from typing import Any

_LINE = re.compile(r"source hierarchy[^\n]*", re.I)
_ITEM = re.compile(r"(?:^|;|:)[\s*_`]*(\d)\s+([^;]+)")     # '...:** 1 the trial's own publication; 2 ...'
_POINTER = re.compile(r"pointers? only|never the number", re.I)
_TIER_WORDS = {"publication": 1, "abstract": 1, "supplement": 1, "full text": 1, "fda": 2, "ema": 2, "regulatory": 2,
               "registry": 3, "aact": 3, "clinicaltrials": 3, "hta": 4, "nice": 4, "meta": 5}
# a reason that makes a tier a CONDITION of admission, rather than naming what the tiers held
_PROHIBITION = re.compile(r"(?:level[- ]?\d[^.;]{0,80}\brequirement\b|\b(registry|regulatory|hta|fda)[- ]only\b[^.;]{0,60}"
                          r"(?:do(?:es)? not meet|not (?:admissible|allowed|accepted|permitted)))", re.I)


def parse(protocol_text: str | None) -> list[dict[str, Any]]:
    m = _LINE.search(protocol_text or "")
    if not m:
        return []
    out = []
    for n, body in _ITEM.findall(m.group(0)):
        out.append({"level": int(n), "text": body.strip(), "use": "POINTER_ONLY" if _POINTER.search(body) else "PERMITTED"})
    return out


def _tiers_named(reason: str) -> set[int]:
    r = reason.lower()
    named = {lvl for w, lvl in _TIER_WORDS.items() if w in r}
    named |= {int(x) for x in re.findall(r"level[- ]?(\d)", r)}
    return named


def problems(review: dict[str, Any]) -> list[dict[str, Any]]:
    levels = parse(((review.get("protocol") or {}).get("text")) or "")
    permitted = {l["level"] for l in levels if l["use"] == "PERMITTED"}
    if not permitted:
        return []
    out = []
    for o in review.get("outcomes") or []:
        for a in o.get("declared_absent_trials") or []:
            reason = str(a.get("reason") or "")
            if not _PROHIBITION.search(reason):
                continue
            excluded = _tiers_named(reason) & permitted
            if max(permitted) > 1 and excluded:
                out.append({"kind": "HIERARCHY_TREATED_AS_PROHIBITION",
                            "report_id": re.sub(r"\D", "", str(a.get("id")))[:8] or str(a.get("id")),
                            "detail": (f"{o.get('name')}: {a.get('id')} is refused by a source-tier restriction "
                                       f"({reason[:160]!r}); the protocol's hierarchy permits levels {sorted(permitted)} "
                                       "in descending priority -- a lower tier is used when the higher are silent")})
    return out
