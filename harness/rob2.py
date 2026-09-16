"""Registry-machine-signal-restricted risk-of-bias signals.

These are not a formal human risk-of-bias assessment. They are the subset of
signals that can be re-derived from structured registry fields and the pooled
outcome:

  D1 randomisation       AACT allocation, corrected by trial text when explicit
  D2 deviations          masking of participants/personnel
  D3 missing outcome     not assessed here; no outcome-missingness source
  D4 outcome measurement masking of outcome assessment
  D5 selective reporting registered primary/secondary outcome vs pooled outcome

Each domain object carries the rule id, the exact inputs used by the rule, and a
derived_at_build marker so a stored review can be refused if its rating is not
re-derivable from its own stated rule.
"""
from __future__ import annotations

import re
from typing import Any, Callable

OUTPUT_FAMILY = "registry-machine-signal-restricted"

DOMAIN_LABELS = {
    "D1_randomisation": "allocation sequence/randomisation",
    "D2_deviations": "masking of participants/personnel",
    "D3_missing_outcome_data": "missing outcome data",
    "D4_outcome_measurement": "masking of outcome assessment",
    "D5_selective_reporting": "registered outcome versus pooled outcome",
}

MACHINE_DOMAINS = (
    "D1_randomisation",
    "D2_deviations",
    "D4_outcome_measurement",
    "D5_selective_reporting",
)

NOT_ASSESSED_LEVELS = {"not assessed", "not_assessable"}
STANDARD_3P_MACE = frozenset({"CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"})


def _b(v):
    """AACT boolean: 't'/'f' (or 'true'/'false'); anything else is unknown (None)."""
    s = str(v or "").strip().lower()
    if s in ("t", "true", "yes"):
        return True
    if s in ("f", "false", "no"):
        return False
    return None


def _norm_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _domain(level: str, basis: str, rule_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "level": level,
        "basis": basis,
        "rule_id": rule_id,
        "inputs": inputs,
        "derived_at_build": True,
    }


def _outcome_dict(value: Any) -> dict[str, str]:
    if isinstance(value, dict):
        return {
            "measure": _norm_text(value.get("measure") or value.get("title") or ""),
            "title": _norm_text(value.get("title") or ""),
            "description": _norm_text(value.get("description") or ""),
        }
    return {"measure": _norm_text(value), "title": "", "description": ""}


def _outcome_dicts(values: list[Any] | None) -> list[dict[str, str]]:
    out = []
    for item in values or []:
        row = _outcome_dict(item)
        text = _registered_text(row)
        if text and text.upper() not in {"UNKNOWN", "NONE", "<NONE>", "NOT AVAILABLE", "N/A"}:
            out.append(row)
    return out


def _registered_text(row: dict[str, Any]) -> str:
    return _norm_text(" ".join(str(row.get(k) or "") for k in ("measure", "title", "description")))


def _outcome_label(row: dict[str, Any]) -> str:
    return _norm_text(row.get("measure") or row.get("title") or row.get("description") or "<unknown>")


def _component_set(text: str) -> frozenset[str]:
    s = _norm_text(text).lower()
    if not s:
        return frozenset()
    comps: set[str] = set()
    if re.search(r"\bcv\s+death\b|\bcardiovascular(?:\s*\([^)]*\))?\s+death\b|\bdeath from cardiovascular causes\b", s):
        comps.add("CV_DEATH")
    if re.search(r"\bnon[- ]?fatal\s+(myocardial infarction|mi)\b", s):
        comps.add("NONFATAL_MI")
    elif re.search(r"\b(myocardial infarction|mi)\b", s):
        comps.add("NONFATAL_MI")
    if re.search(r"\bnon[- ]?fatal\s+stroke\b", s):
        comps.add("NONFATAL_STROKE")
    elif re.search(r"\bstroke\b", s):
        comps.add("NONFATAL_STROKE")

    # Extra components keep a broader composite from falsely matching 3-point MACE.
    if re.search(r"\bhospitali[sz]ation\b.{0,35}\bheart failure\b|\bheart failure\b.{0,35}\bhospitali[sz]ation\b", s):
        comps.add("HF_HOSPITALISATION")
    if re.search(r"\bunstable angina\b", s):
        comps.add("UNSTABLE_ANGINA")
    if re.search(r"\brevasculari[sz]ation\b", s):
        comps.add("REVASCULARISATION")

    mace_term = re.search(r"\bmace\b|\bmajor adverse cardiovascular events?\b|\bmajor cardiovascular events?\b", s)
    three_point = re.search(r"\b(?:3|three)[- ]?point\b", s)
    if mace_term and (three_point or not comps):
        comps.update(STANDARD_3P_MACE)
    return frozenset(comps)


def _simple_matches(a: str, b: str) -> bool:
    aa = re.sub(r"[^a-z0-9]+", " ", (a or "").lower()).strip()
    bb = re.sub(r"[^a-z0-9]+", " ", (b or "").lower()).strip()
    return bool(aa and bb and (aa == bb or aa in bb or bb in aa))


def _outcome_match_detail(
    pooled_outcome: str,
    registered: dict[str, str],
    matches: Callable[[str, str], bool] | None,
) -> dict[str, Any]:
    reg_text = _registered_text(registered)
    pooled_components = sorted(_component_set(pooled_outcome))
    registered_components = sorted(_component_set(reg_text))
    if pooled_components and registered_components:
        return {
            "matched": pooled_components == registered_components,
            "method": "component_set",
            "pooled_components": pooled_components,
            "registered_components": registered_components,
            "registered_text": reg_text,
        }
    if _simple_matches(pooled_outcome, reg_text) or (matches and matches(pooled_outcome, reg_text)):
        return {
            "matched": True,
            "method": "text_identity",
            "pooled_components": pooled_components,
            "registered_components": registered_components,
            "registered_text": reg_text,
        }
    return {
        "matched": False,
        "method": "no_match",
        "pooled_components": pooled_components,
        "registered_components": registered_components,
        "registered_text": reg_text,
    }


def _d1(inputs: dict[str, Any]) -> dict[str, Any]:
    alloc = str(inputs.get("AACT.designs.allocation") or "").upper()
    randomized_by_text = bool(inputs.get("trial_text.randomized_by_text"))
    if alloc == "RANDOMIZED":
        d1, d1b = "low", f"AACT allocation = {alloc}"
    elif randomized_by_text:
        d1, d1b = "low", (f"AACT allocation = {alloc or 'unstated'} but the trial's own abstract states "
                          "random assignment (abstract-corrected registry data error; FLAGGED "
                          "registry-vs-trial disagreement)")
    elif alloc:
        d1, d1b = "some concerns", f"AACT allocation = {alloc}"
    else:
        d1, d1b = "not assessed", "AACT allocation = unstated"
    return _domain(d1, d1b, f"{OUTPUT_FAMILY}:D1:allocation_v1", inputs)


def _d2(inputs: dict[str, Any]) -> dict[str, Any]:
    masking = str(inputs.get("AACT.designs.masking") or "").upper()
    blinded_by_text = bool(inputs.get("trial_text.blinded_by_text"))
    masking_blinded = any(w in masking for w in ("DOUBLE", "TRIPLE", "QUADRUPLE"))
    trial_blinded = masking_blinded or blinded_by_text
    src = (f"trial masking = {masking.title()}" if masking_blinded
           else "the trial's own abstract/text (double-blind/placebo-controlled)")
    sm = _b(inputs.get("AACT.designs.subject_masked"))
    cm = _b(inputs.get("AACT.designs.caregiver_masked"))
    if trial_blinded:
        d2 = "low"
        d2b = (f"{src} (blinded); overrides per-role Booleans "
               f"subject_masked={sm}/caregiver_masked={cm} (FLAGGED registry-vs-trial disagreement)"
               if (sm is False or cm is False) else
               f"{src} (blinded): participants/personnel blinded")
    elif sm and cm:
        d2, d2b = "low", f"blinding: subject_masked={sm}, caregiver_masked={cm}"
    elif sm is False or cm is False:
        d2, d2b = "some concerns", f"blinding: subject_masked={sm}, caregiver_masked={cm}"
    else:
        d2, d2b = "not assessed", f"blinding: subject_masked={sm}, caregiver_masked={cm}"
    return _domain(d2, d2b, f"{OUTPUT_FAMILY}:D2:masking_v1", inputs)


def _d3(attr) -> dict[str, Any]:
    if not attr or attr.get("overall_pct") is None:
        return _domain(
            "not assessed",
            "no AACT participant-flow data; outcome missingness needs human judgement",
            f"{OUTPUT_FAMILY}:D3:not_assessed_v1",
            {"AACT.milestones.attrition": attr},
        )
    o, d = attr["overall_pct"], attr.get("differential_pct") or 0
    return _domain(
        "not assessed",
        (f"not assessed - AACT flow shows between-arm differential attrition {d}% (overall {o}%), "
         "but study discontinuation is NOT outcome missingness and outcome-dependence needs human "
         "reading; the attrition figures are context, not a risk-of-bias rating"),
        f"{OUTPUT_FAMILY}:D3:not_assessed_v1",
        {"AACT.milestones.attrition": attr},
    )


def _d4(inputs: dict[str, Any]) -> dict[str, Any]:
    masking = str(inputs.get("AACT.designs.masking") or "").upper()
    blinded_by_text = bool(inputs.get("trial_text.blinded_by_text"))
    masking_blinded = any(w in masking for w in ("DOUBLE", "TRIPLE", "QUADRUPLE"))
    trial_blinded = masking_blinded or blinded_by_text
    src = (f"trial masking = {masking.title()}" if masking_blinded
           else "the trial's own abstract/text (double-blind/placebo-controlled)")
    oa = _b(inputs.get("AACT.designs.outcomes_assessor_masked"))
    if trial_blinded:
        d4 = "low"
        d4b = (f"{src} (blinded); overrides outcomes_assessor_masked={oa} "
               f"(FLAGGED registry-vs-trial disagreement)" if oa is False else
               f"{src} (blinded): outcome assessment blinded")
    else:
        d4 = "low" if oa else ("some concerns" if oa is False else "not assessed")
        d4b = f"outcome-assessor blinded = {oa}"
    return _domain(d4, d4b, f"{OUTPUT_FAMILY}:D4:outcome_assessor_masking_v1", inputs)


def derive_d5(
    registered_primaries: list[Any] | None,
    pooled_outcome: str,
    matches: Callable[[str, str], bool] | None = None,
    registered_secondaries: list[Any] | None = None,
) -> dict[str, Any]:
    primaries = _outcome_dicts(registered_primaries)
    secondaries = _outcome_dicts(registered_secondaries)
    inputs: dict[str, Any] = {
        "pooled_outcome": _norm_text(pooled_outcome),
        "registered_primary_outcomes": primaries,
        "registered_secondary_outcomes": secondaries,
    }
    if not primaries and not secondaries:
        inputs["comparison"] = {
            "matched": False,
            "method": "no_registered_outcome",
            "pooled_components": sorted(_component_set(pooled_outcome)),
            "registered_components": [],
        }
        return _domain(
            "not_assessable",
            "no registered primary or secondary outcomes available for this trial",
            f"{OUTPUT_FAMILY}:D5:registered_outcome_identity_v2",
            inputs,
        )

    for rp in primaries:
        detail = _outcome_match_detail(pooled_outcome, rp, matches)
        if detail["matched"]:
            inputs["comparison"] = {"registered_type": "primary", "registered_label": _outcome_label(rp), **detail}
            if detail["method"] == "component_set":
                basis = ("the pooled outcome matches the trial's pre-registered primary outcome by component set "
                         f"({', '.join(detail['pooled_components'])})")
            else:
                basis = "the pooled outcome IS the trial's pre-registered primary outcome"
            return _domain("low", basis, f"{OUTPUT_FAMILY}:D5:registered_outcome_identity_v2", inputs)

    for rs in secondaries:
        detail = _outcome_match_detail(pooled_outcome, rs, matches)
        if detail["matched"]:
            inputs["comparison"] = {"registered_type": "secondary", "registered_label": _outcome_label(rs), **detail}
            return _domain(
                "low",
                ("the pooled outcome is a PRE-REGISTERED SECONDARY outcome (prespecified in the "
                 "registry) -- prespecified reporting, not selective reporting"),
                f"{OUTPUT_FAMILY}:D5:registered_outcome_identity_v2",
                inputs,
            )

    first = primaries[0] if primaries else {}
    detail = _outcome_match_detail(pooled_outcome, first, matches) if first else {}
    inputs["comparison"] = {"registered_type": None, "registered_label": _outcome_label(first) if first else None, **detail}
    return _domain(
        "some concerns",
        ("the pooled outcome matches no registered primary or secondary outcome "
         f"(registered primary: {_outcome_label(first)[:80]!r}) -- possibly post-hoc/unregistered"),
        f"{OUTPUT_FAMILY}:D5:registered_outcome_identity_v2",
        inputs,
    )


def assess(design: dict, registered_primaries: list, pooled_outcome: str, matches,
           registered_secondaries: list = None, blinded_by_text: bool = False,
           randomized_by_text: bool = False) -> dict:
    """Return domain signals with rule id, inputs, and derived_at_build metadata."""
    design = design or {}
    d1_inputs = {
        "AACT.designs.allocation": design.get("allocation") or "",
        "trial_text.randomized_by_text": bool(randomized_by_text),
    }
    d2_inputs = {
        "AACT.designs.masking": design.get("masking") or "",
        "AACT.designs.subject_masked": design.get("subject_masked"),
        "AACT.designs.caregiver_masked": design.get("caregiver_masked"),
        "trial_text.blinded_by_text": bool(blinded_by_text),
    }
    d4_inputs = {
        "AACT.designs.masking": design.get("masking") or "",
        "AACT.designs.outcomes_assessor_masked": design.get("outcomes_assessor_masked"),
        "trial_text.blinded_by_text": bool(blinded_by_text),
    }
    return {
        "D1_randomisation": _d1(d1_inputs),
        "D2_deviations": _d2(d2_inputs),
        "D3_missing_outcome_data": _d3(design.get("attrition")),
        "D4_outcome_measurement": _d4(d4_inputs),
        "D5_selective_reporting": derive_d5(registered_primaries, pooled_outcome, matches, registered_secondaries),
    }


def rob_basis(domains: dict[str, dict[str, Any]]) -> dict[str, Any]:
    assessed, unassessed = [], []
    for domain_id, label in DOMAIN_LABELS.items():
        level = ((domains or {}).get(domain_id) or {}).get("level")
        if level in NOT_ASSESSED_LEVELS:
            unassessed.append({"domain": domain_id, "label": label, "level": level})
        else:
            assessed.append({"domain": domain_id, "label": label, "level": level})
    return {
        "output_family": OUTPUT_FAMILY,
        "assessed_domains": assessed,
        "unassessed_domains": unassessed,
    }


def overall(domains: dict) -> str:
    """Conservative overall signal over assessed domains."""
    levels = [d["level"] for d in domains.values()]
    if "high" in levels:
        return "high"
    assessed = [x for x in levels if x not in NOT_ASSESSED_LEVELS]
    if any(x == "some concerns" for x in assessed):
        return "some concerns"
    if assessed and all(x == "low" for x in assessed):
        return "low (on assessed domains; some domains require human judgement)"
    return "some concerns (partial - key domains not assessed)"


def rederive_domain(domain: dict[str, Any], matches: Callable[[str, str], bool] | None = None) -> dict[str, Any]:
    rule_id = str((domain or {}).get("rule_id") or "")
    inputs = (domain or {}).get("inputs") or {}
    if not rule_id or not inputs or (domain or {}).get("derived_at_build") is not True:
        raise ValueError("domain lacks rule_id, inputs, or derived_at_build=true")
    if ":D1:" in rule_id:
        return _d1(inputs)
    if ":D2:" in rule_id:
        return _d2(inputs)
    if ":D3:" in rule_id:
        return _d3(inputs.get("AACT.milestones.attrition"))
    if ":D4:" in rule_id:
        return _d4(inputs)
    if ":D5:" in rule_id:
        return derive_d5(
            inputs.get("registered_primary_outcomes") or [],
            inputs.get("pooled_outcome") or "",
            matches,
            inputs.get("registered_secondary_outcomes") or [],
        )
    raise ValueError(f"unknown rule_id {rule_id!r}")


def rederivation_violations(review: dict[str, Any], matches: Callable[[str, str], bool] | None = None) -> list[dict[str, Any]]:
    """Return stored domains whose level is not re-derivable from their own rule inputs."""
    violations = []
    for trial_id, entry in (((review.get("rob2") or {}).get("trials") or {}).items()):
        for domain_id, stored in ((entry or {}).get("domains") or {}).items():
            if domain_id not in MACHINE_DOMAINS and domain_id != "D3_missing_outcome_data":
                continue
            try:
                expected = rederive_domain(stored, matches)
            except Exception as exc:  # noqa: BLE001 - gate reports malformed stored objects
                violations.append({
                    "trial": trial_id,
                    "domain": domain_id,
                    "stored_level": stored.get("level") if isinstance(stored, dict) else None,
                    "expected_level": None,
                    "reason": str(exc),
                    "inputs": stored.get("inputs") if isinstance(stored, dict) else None,
                })
                continue
            if expected.get("level") != stored.get("level"):
                violations.append({
                    "trial": trial_id,
                    "domain": domain_id,
                    "stored_level": stored.get("level"),
                    "expected_level": expected.get("level"),
                    "stored_basis": stored.get("basis"),
                    "expected_basis": expected.get("basis"),
                    "inputs": stored.get("inputs"),
                    "expected_inputs": expected.get("inputs"),
                })
    return violations
