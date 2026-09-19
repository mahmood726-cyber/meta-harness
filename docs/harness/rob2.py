"""Registry-machine-signal-restricted partial machine assessment.

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
SECONDARY_COMPONENT_SUBSET_ALLOWED = {frozenset({"HF_HOSPITALISATION"})}


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
        r"\b(?:composite|progression|sustained|decline|decrease|failure|replacement therapy|dialysis|death)\b",
        s,
    ):
        comps.add("KIDNEY_PROGRESSION_COMPOSITE")
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
    if re.search(
        r"\bhhf\b|\bhospitali[sz](?:ation|ed)\b.{0,35}\b(?:heart failure|hf)\b|"
        r"\b(?:heart failure|hf)\b.{0,35}\bhospitali[sz](?:ation|ed)\b",
        s,
    ):
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


def _outcome_match_detail(
    pooled_outcome: str,
    registered: dict[str, str],
    matches: Callable[[str, str], bool] | None,
    *,
    allow_secondary_component_subset: bool = False,
) -> dict[str, Any]:
    reg_text = _registered_text(registered)
    pooled_component_set = _component_set(pooled_outcome)
    registered_component_set = _component_set(reg_text)
    pooled_components = sorted(pooled_component_set)
    registered_components = sorted(registered_component_set)
    if pooled_component_set and registered_component_set:
        subset_match = (
            allow_secondary_component_subset
            and pooled_component_set in SECONDARY_COMPONENT_SUBSET_ALLOWED
            and pooled_component_set < registered_component_set
        )
        return {
            "matched": pooled_component_set == registered_component_set or subset_match,
            "method": "registered_secondary_component" if subset_match else "component_set",
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
                         f"({', '.join(detail['pooled_components'])}); registered {_outcome_label(rp)!r}")
            else:
                basis = f"the pooled outcome IS the trial's pre-registered primary outcome; registered {_outcome_label(rp)!r}"
            return _domain("low", basis, f"{OUTPUT_FAMILY}:D5:registered_outcome_identity_v2", inputs)

    for rs in secondaries:
        detail = _outcome_match_detail(
            pooled_outcome,
            rs,
            matches,
            allow_secondary_component_subset=True,
        )
        if detail["matched"]:
            inputs["comparison"] = {"registered_type": "secondary", "registered_label": _outcome_label(rs), **detail}
            if detail["method"] == "registered_secondary_component":
                basis = ("the pooled outcome is a prespecified component of a registered secondary outcome; "
                         f"registered {_outcome_label(rs)!r}")
            else:
                basis = f"prespecified secondary outcome, registered {_outcome_label(rs)!r}"
            return _domain(
                "low",
                basis,
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


# ---------------------------------------------------------------------------------------------------------------
# CANONICAL RoB OBJECT (Mahmood's adjudication, 19 Sep 2026): the served page rendered "formal RoB 2 not assessed"
# x41 and "low (on assessed domains" x8 for the same trials -- one quantity from two sources. Both the signal and
# the verdict now render from THIS object: the machine signals stay (they are real registry-derived information),
# labelled as signals with their basis; the verdict is stated separately; the bare judgement word never stands in a
# verdict position because no verdict exists under the registry machine-signal family.
# ---------------------------------------------------------------------------------------------------------------

VERDICT_NOT_ASSESSED = "NOT_ASSESSED"


def _signal_overall(overall):
    o = str(overall or "").lower()
    if o.startswith("low"):
        return "consistent with low risk on the assessed domains"
    if o.startswith("some concerns"):
        return "some concerns on the assessed domains"
    if o.startswith("high"):
        return "high-risk signal on at least one assessed domain"
    return "no aggregate signal"


def canonical(rob2_obj):
    """One object per trial: {verdict, verdict_basis, signal_overall, domains: {k: {signal, signal_basis, verdict}}}.
    Under the registry machine-signal output family every verdict is NOT_ASSESSED; a formal RoB 2 assessment object
    (a different output family, adjudicated) would carry its judgements as verdicts."""
    rob2_obj = rob2_obj or {}
    formal = rob2_obj.get("output_family") not in (None, OUTPUT_FAMILY)
    out = {}
    for pid, a in (rob2_obj.get("trials") or {}).items():
        domains = {}
        for k, d in (a.get("domains") or {}).items():
            level = str((d or {}).get("level") or "")
            domains[k] = {
                "signal": level,
                "signal_basis": (d or {}).get("basis") or "",
                "signal_source": a.get("assessed_from") or rob2_obj.get("source") or "registry",
                "verdict": (level if formal else VERDICT_NOT_ASSESSED),
            }
        out[str(pid)] = {
            "verdict": (str(a.get("overall") or "") if formal else VERDICT_NOT_ASSESSED),
            "verdict_basis": ("formal RoB 2 assessment" if formal
                              else "formal RoB 2 not assessed: the registry machine-signal family carries no judgement (B-prime withdrew RoB 2 judgements)"),
            "signal_overall": _signal_overall(a.get("overall")),
            "signal_overall_raw": str(a.get("overall") or ""),
            "domains": domains,
        }
    return {"output_family": rob2_obj.get("output_family"), "formal": formal, "trials": out}


_JUDGEMENT_WORDS = {"low", "some concerns", "high", "moderate", "unclear"}


def verify_rendered_verdicts(html, rob2_obj):
    """The gate: every cell in a verdict position of the rendered RoB table must carry `data-rob-verdict` equal to the
    canonical verdict for its trial (and domain); a verdict-position cell whose visible text is a bare judgement word,
    or which starts with a judgement word followed by a qualifier ("low (on assessed domains"), is ROB_VERDICT_UNRESOLVED.
    Returns the list of violations (empty = resolved). Run against the served 8c8874b4 page it reports the eight
    Overall cells that quoted the machine aggregate -- the blindness this gate closes."""
    import re as _re
    import html as _html
    canon = canonical(rob2_obj)["trials"]
    i = html.find("<th>Overall</th>")
    if i < 0:
        return []
    table = html[i: html.find("</table>", i)]
    violations = []
    for row in _re.findall(r"<tr>(.*?)</tr>", table, _re.S):
        cells = _re.findall(r"<td([^>]*)>(.*?)</td>", row, _re.S)
        if not cells:
            continue
        pid = _re.sub(r"<[^>]+>", "", cells[0][1]).strip()
        trial = canon.get(pid)
        for idx, (attrs, inner) in enumerate(cells[1:], start=1):
            text = _html.unescape(_re.sub(r"<[^>]+>", " ", inner))
            text = _re.sub(r"\s+", " ", text).strip().lower()
            m = _re.search(r"data-rob-verdict=['\"]([^'\"]+)['\"]", attrs)
            expected = None
            if trial is not None:
                if idx == 1:
                    expected = trial["verdict"]
                else:
                    dkeys = list(trial["domains"].keys())
                    if idx - 2 < len(dkeys):
                        expected = trial["domains"][dkeys[idx - 2]]["verdict"]
            if trial is None:
                # a pooled trial with no canonical object: allowed only as an explicit not-assessed row
                if text not in ("not assessed", "") and not m:
                    violations.append({"code": "ROB_VERDICT_UNRESOLVED", "trial": pid, "cell": idx,
                                       "detail": f"no canonical object for {pid}; cell text {text[:60]!r}"})
                continue
            if not m:
                violations.append({"code": "ROB_VERDICT_UNRESOLVED", "trial": pid, "cell": idx,
                                   "detail": f"verdict-position cell carries no data-rob-verdict; text {text[:60]!r}"})
                continue
            if expected is not None and m.group(1) != expected:
                violations.append({"code": "ROB_VERDICT_MISMATCH", "trial": pid, "cell": idx,
                                   "detail": f"rendered {m.group(1)} but the canonical object says {expected}"})
            first = _re.split(r"[;:(\-–—]", text)[0].strip()
            if expected == VERDICT_NOT_ASSESSED and first in _JUDGEMENT_WORDS:
                violations.append({"code": "ROB_SIGNAL_IN_VERDICT_POSITION", "trial": pid, "cell": idx,
                                   "detail": f"a judgement word stands in a verdict position: {text[:60]!r}"})
    return violations
