"""ONE component-by-component compatibility rule, applied identically to admitted and refused rows, decided before any effect is
looked at (external review of colchicine-secondary-cv-prevention, 2026-09-26).

COPS was refused by a hand-written entry (docs/refusals.json) as "a broader composite (mortality+ACS+revascularisation+stroke)
than a 3-point MACE", while the ADMITTED trials are not 3-point either: COLCOT adds resuscitated cardiac arrest and urgent
hospitalisation for angina leading to revascularisation; LoDoCo2 and CLEAR add ischaemia-driven coronary revascularisation. The
admitted rows never met a component rule at all (UNBOUND_LEGACY), so the two sides were judged by two different rules.

Here each row's own definition span is read into TYPED components; the row is compared with the outcome's declared CORE, and every
difference is typed: ADDED:<c>, MISSING:<c>, or SUBSTITUTED:<broader>_FOR_<core> (all-cause death for CV death; ACS for MI). A
PREDECLARED per-outcome `composite_component_policy` names which difference types stay in the PRIMARY analysis:
    {"core": [...], "allowed_in_primary": ["ADDED:CORONARY_REVASC", ...], "predeclared": true, "decided_by", "decided_on", "rationale"}
Every other difference sends the row to a SEPARATE analysis. With NO policy the default core is the outcome's declared
components when it has them, else 3-point (CV_DEATH, MI, STROKE), and NOTHING is allowed: every difference is separate. The
default is strict so that a rule refusing one "broader" composite necessarily flags every broader composite. The decision reads
only definitions, never an effect, a p-value or the pool."""
from __future__ import annotations

import re
from typing import Any

# order matters: the more specific phrase is tried first and its span is consumed, so "urgent hospitalization for angina leading
# to coronary revascularization" is ONE component (UA_HOSP_REVASC), never also a bare CORONARY_REVASC
_VOCAB = (
    ("CARDIAC_ARREST", r"resuscitated\s+(?:cardiac\s+arrest|sudden\s+death)|cardiac\s+arrest"),
    ("UA_HOSP_REVASC", r"(?:urgent\s+)?hospitali[sz]ations?\s+for\s+(?:unstable\s+)?angina\s+(?:leading\s+to|requiring|with)\s+(?:coronary\s+)?revasculari[sz]ation"),
    ("UA_HOSP", r"(?:urgent\s+)?hospitali[sz]ations?\s+for\s+unstable\s+angina|unstable\s+angina"),
    ("CORONARY_REVASC", r"(?:(?:ischa?emia[- ]driven|unplanned|urgent|clinically\s+driven)\s*(?:\([^)]{0,20}\)\s*)?)*(?:coronary\s+)?revasculari[sz]ation"),
    ("ACS", r"acute\s+coronary\s+syndromes?|(?-i:\bACS\b)"),
    ("ALL_CAUSE_DEATH", r"all[- ]cause\s+(?:mortality|death)|death\s+from\s+any\s+cause|total\s+mortality"),
    # CV death, in the wordings the served definitions actually use. Two EQUIVALENCES are stated, not guessed:
    #  - coronary heart disease death counts as CV death -- the existing classifier's rule (target_endpoint._classify), so the
    #    uniform rule cannot disagree with the gate the GLP-1/pcsk9 rows already passed;
    #  - "death from vascular causes" is the CV-death component of ACS trials (PLATO's wording; ticagrelor).
    ("CV_DEATH", r"death\s+(?:from|due\s+to)\s+(?:cardiovascular|CV|vascular)\s+(?:causes?|disease)|(?:cardiovascular|\bCV)\s+(?:\(CV\)\s+)?(?:death|mortality)"
                 r"|cardiac\s+death|vascular\s+death|coronary\s+heart\s+disease\s+death|death\s+from\s+coronary\s+heart\s+disease|\bCHD\s+death"),
    ("MI", r"myocardial\s+infarctions?"),
    ("STROKE", r"strokes?"),
    ("HF_HOSP", r"hospitali[sz]ations?\s+for\s+heart\s+failure|heart[- ]failure\s+hospitali[sz]ations?"),
)
_SUBSTITUTIONS = {("ALL_CAUSE_DEATH", "CV_DEATH"), ("ACS", "MI")}      # broader component standing in for a core one
DEFAULT_CORE = ["CV_DEATH", "MI", "STROKE"]


def components(text: str | None) -> list[str]:
    s = text or ""
    found, taken = [], []
    for name, rx in _VOCAB:
        for m in re.finditer(rx, s, re.I):
            if any(a < m.end() and m.start() < b for a, b in taken):
                continue
            taken.append((m.start(), m.end()))
            if name not in found:
                found.append(name)
    return sorted(found)


def policy(spec: dict[str, Any] | None) -> dict[str, Any] | None:
    p = (spec or {}).get("composite_component_policy")
    if not isinstance(p, dict) and ((spec or {}).get("allow_near_match") or (spec or {}).get("component_compat_key")):
        # the EXISTING predeclared near-match permission (target_endpoint.near_match_declared): a superset composite may be pooled
        # and disclosed; a missing or substituted component may not -- the same permission, in this rule's terms
        core = components(", ".join(map(str, (spec or {}).get("canonical_components") or []))) or list(DEFAULT_CORE)
        return {"core": sorted(core), "allowed_in_primary": ["ADDED:*"], "predeclared": True,
                "source": "outcome allow_near_match / component_compat_key (predeclared near-match permission)"}
    if not isinstance(p, dict) or p.get("predeclared") is not True or not p.get("core") \
            or not all(p.get(k) for k in ("decided_by", "decided_on", "rationale")):
        return None
    return {**p, "core": sorted({str(c).upper() for c in p["core"]}), "allowed_in_primary": sorted({str(x).upper() for x in p.get("allowed_in_primary") or []})}


def differences(comps: list[str], core: list[str]) -> list[str]:
    have, want = set(comps), set(core)
    out = []
    for broad, narrow in sorted(_SUBSTITUTIONS):
        if narrow in want and narrow not in have and broad in have:
            out.append(f"SUBSTITUTED:{broad}_FOR_{narrow}")
            have.discard(broad)
            want.discard(narrow)
    out += [f"MISSING:{c}" for c in sorted(want - have)]
    out += [f"ADDED:{c}" for c in sorted(have - want)]
    return out


def verdict(definition_text: str | None, spec: dict[str, Any] | None, declared_core: list[str] | None = None) -> dict[str, Any]:
    """The same function for every row, admitted or refused. PRIMARY only if every difference is allowed by a predeclared
    policy; SEPARATE_ANALYSIS otherwise; NO_DEFINITION when the row carries no definition span to read (never guessed)."""
    pol = policy(spec)
    core = pol["core"] if pol else sorted(declared_core or DEFAULT_CORE)
    comps = components(definition_text)
    if not comps:
        return {"state": "NO_DEFINITION", "core": core, "policy_declared": bool(pol), "components": [], "differences": []}
    diffs = differences(comps, core)
    allowed = set((pol or {}).get("allowed_in_primary") or [])
    blocking = [d for d in diffs if d not in allowed and not (d.startswith("ADDED:") and "ADDED:*" in allowed)]
    return {"state": "PRIMARY" if not blocking else "SEPARATE_ANALYSIS", "core": core, "policy_declared": bool(pol),
            "components": comps, "differences": diffs, "blocking": blocking}
