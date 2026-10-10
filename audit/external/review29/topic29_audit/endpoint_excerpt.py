"""Manually transcribed isolated functions, NOT a checkout of production code.
Source: harness/rob2.py at meta-harness commit 0730234d0b4f, lines 94-193.
Connector-reported original Git blob: 0b66b00267ac6c2b138174cc38644b3bf7a955d9.
Only the component matching functions and their small dependencies are reproduced.
This file does not execute the full D5 assessment, acquisition, gate, or renderer.
"""
import re
from typing import Any, Callable

STANDARD_3P_MACE = frozenset({"CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"})
SECONDARY_COMPONENT_SUBSET_ALLOWED = {frozenset({"HF_HOSPITALISATION"})}

def _norm_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()

def _registered_text(row: dict[str, Any]) -> str:
    return _norm_text(" ".join(str(row.get(k) or "") for k in ("measure", "title", "description")))

def _component_set(text: str) -> frozenset[str]:
    s = _norm_text(text).lower()
    if not s:
        return frozenset()
    comps: set[str] = set()
    if re.search(r"\bmadrs\b|\bmontgomery[- ]?a?sberg\b|\bmontgomery[- ]?asberg\b", s):
        is_response = re.search(r"\bresponse\b|\bremission\b|50\s*%|\b50 percent\b|\breduction\b", s)
        is_change = re.search(r"\bchange\b|\bfrom baseline\b|\btotal score\b", s)
        if is_change and not is_response:
            comps.add("MADRS_CHANGE")
    if re.search(r"\brecurrent\b", s) and re.search(r"\bvtes?\b|\bvenous thromboembolism\b|\bdvt\b|\bdeep vein thrombosis\b|\bpe\b|\bpulmonary embolism\b", s):
        if not re.search(r"\bnet clinical benefit\b", s):
            comps.add("RECURRENT_VTE")
    if re.search(r"\ball[- ]cause mortality\b|\ball cause mortality\b", s):
        comps.add("ALL_CAUSE_MORTALITY")
    if re.search(r"\b(?:kidney|renal|egfr|gfr|esrd|end[- ]stage|dialysis)\b", s) and re.search(
        r"\b(?:composite|progression|sustained|decline|decrease|failure|replacement therapy|dialysis|death)\b", s
    ):
        comps.add("KIDNEY_PROGRESSION_COMPOSITE")
    if re.search(r"(?<!non-)(?<!non)(?<!non )\b(?:cv\s+death|cardiovascular(?:\s*\([^)]*\))?\s+death"
                 r"|(?:cv|cardiovascular)[- ]related\s+death)\b|\bdeath from cardiovascular causes\b", s):
        comps.add("CV_DEATH")
    if re.search(r"\bnon[- ]?fatal\s+(myocardial infarction|mi)\b", s):
        comps.add("NONFATAL_MI")
    elif re.search(r"\b(myocardial infarction|mi)\b", s):
        comps.add("NONFATAL_MI")
    if re.search(r"\bnon[- ]?fatal\s+stroke\b", s):
        comps.add("NONFATAL_STROKE")
    elif re.search(r"\bstroke\b", s):
        comps.add("NONFATAL_STROKE")
    if re.search(r"\bhhf\b|\bhospitali[sz](?:ation|ed)\b.{0,35}\b(?:heart failure|hf)\b|"
                 r"\b(?:heart failure|hf)\b.{0,35}\bhospitali[sz](?:ation|ed)\b", s):
        comps.add("HF_HOSPITALISATION")
    if re.search(r"\bunstable angina\b", s):
        comps.add("UNSTABLE_ANGINA")
    if re.search(r"\brevasculari[sz]ation\b", s):
        comps.add("REVASCULARISATION")
    mace_term = re.search(r"\bmace\b|\bmajor adverse cardiovascular events?\b|\bmajor cardiovascular events?\b", s)
    three_point = re.search(r"\b(?:3|three)[- ]?point\b", s)
    if mace_term and (three_point or not comps):
        comps.update(STANDARD_3P_MACE)
    if "KIDNEY_PROGRESSION_COMPOSITE" in comps:
        comps.discard("CV_DEATH")
    return frozenset(comps)

def _simple_matches(a: str, b: str) -> bool:
    aa = re.sub(r"[^a-z0-9]+", " ", (a or "").lower()).strip()
    bb = re.sub(r"[^a-z0-9]+", " ", (b or "").lower()).strip()
    return bool(aa and bb and (aa == bb or aa in bb or bb in aa))

def _outcome_match_detail(pooled_outcome: str, registered: dict[str, str],
                          matches: Callable[[str, str], bool] | None,
                          *, allow_secondary_component_subset: bool = False) -> dict[str, Any]:
    reg_text = _registered_text(registered)
    pooled_component_set = _component_set(pooled_outcome)
    registered_component_set = _component_set(reg_text)
    pooled_components = sorted(pooled_component_set)
    registered_components = sorted(registered_component_set)
    if pooled_component_set and registered_component_set:
        subset_match = (allow_secondary_component_subset
                        and pooled_component_set in SECONDARY_COMPONENT_SUBSET_ALLOWED
                        and pooled_component_set < registered_component_set)
        return {"matched": pooled_component_set == registered_component_set or subset_match,
                "method": "registered_secondary_component" if subset_match else "component_set",
                "pooled_components": pooled_components, "registered_components": registered_components,
                "registered_text": reg_text}
    if _simple_matches(pooled_outcome, reg_text) or (matches and matches(pooled_outcome, reg_text)):
        return {"matched": True, "method": "text_identity", "pooled_components": pooled_components,
                "registered_components": registered_components, "registered_text": reg_text}
    return {"matched": False, "method": "no_match", "pooled_components": pooled_components,
            "registered_components": registered_components, "registered_text": reg_text}
