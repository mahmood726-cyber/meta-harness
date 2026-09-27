"""Input-bound descriptions and explicit, non-mutating result-selection reports.

No topic identifiers or research estimates belong in this module. Unbound facts
remain unknown; annotations and whole-record abstracts are never description sources.
"""
from __future__ import annotations
import re
from copy import deepcopy

STALE_NARRATIVE = "STALE_NARRATIVE"
RULES = ("EACH_TRIAL_PRIMARY_COMPOSITE", "CLOSEST_TO_COMMON_COMPONENT_SET")


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def role(text):
    text = clean(text).lower()
    for pattern, value in ((r"post[- ]hoc analysis", "post hoc"),
                           (r"co[- ]?primary|two primary", "co-primary"),
                           (r"key secondary", "key secondary"),
                           (r"secondary", "secondary"), (r"primary", "primary")):
        if re.search(pattern, text):
            return value
    return None


def component_set(values):
    # Normalize spelling/abbreviation, not clinically distinct death/stroke types.
    aliases = {"cv death": "cardiovascular death", "mi": "myocardial infarction",
               "chd death": "coronary heart disease death", "ua hosp": "unstable angina",
               "unstable angina hospitalization": "unstable angina"}
    return {aliases.get(clean(v).lower().replace("_", " "),
                        clean(v).lower().replace("_", " ")) for v in values or []}


def derive(trial):
    """Read only this input's own binding, components, and time fields."""
    definition = clean(trial.get("endpoint_definition_span") or trial.get("registry_title"))
    result = clean(trial.get("endpoint_result_span") or trial.get("source") or
                   ((trial.get("study_effect") or {}).get("source_provenance") or {}).get("span"))
    # A bound sentence may enumerate several binary outcomes. A unique literal
    # arm-count pair can isolate its own clause without consulting an annotation.
    if all(trial.get(k) is not None for k in ("ai", "n1i", "ci", "n2i")):
        pairs = [f"{trial['ai']}/{trial['n1i']}", f"{trial['ci']}/{trial['n2i']}"]
        clauses = re.split(r";", definition or result)
        hits = [c.strip() for c in clauses if all(p in c for p in pairs)]
        if len(hits) == 1:
            definition = hits[0]
    components = list(trial.get("target_endpoint_components") or trial.get("components") or [])
    # Registry type is authoritative; 'primary' in a testing prerequisite isn't its role.
    registry_role = clean(trial.get("registry_type")).lower()
    qualifier = registry_role or role(definition) or role(trial.get("endpoint_result_span", ""))
    if registry_role == "secondary" and "key secondary" in (definition + " " + result).lower():
        qualifier = "key secondary"
    timeframe = clean(trial.get("registry_timeframe") or trial.get("timeframe"))
    if not timeframe:
        m = re.search(r"(?:at|within|by|over)\s+(?:day\s+)?\d+(?:\.\d+)?\s*(?:days?|weeks?|months?|years?)\b", definition or result, re.I)
        if not m:
            m = re.search(r"(?:at|by|within)\s+(?:day|week|month|year)\s+\d+(?:\.\d+)?\b", definition or result, re.I)
        timeframe = m.group(0) if m else None
    parts = [definition or result or "Endpoint not derivable from input"]
    if components:
        parts.append("Components: " + "; ".join(components))
    parts.append("Role: " + (qualifier or "not stated in input"))
    parts.append("Timepoint: " + (timeframe or "not stated in input"))
    return {"value": " | ".join(parts), "source": "pooled input binding",
            "span": definition or result, "definition_span": definition,
            "result_span": result, "components": components, "role": qualifier,
            "timepoint": timeframe}


def contradictions(derived, annotation):
    """Detect explicit conflicting facts; unsupported prose is not certified as matching."""
    if isinstance(annotation, str):
        annotation = {"endpoint_definition": annotation}
    text = clean(annotation.get("endpoint_definition") or annotation.get("detail"))
    reasons = []
    claimed = role(text)
    actual = derived.get("role")
    if claimed and actual and claimed != actual and {claimed, actual} != {"secondary", "key secondary"}:
        reasons.append("endpoint role")
    comps = derived.get("components") or []
    m = re.search(r"(\d+)[- ]point", text, re.I)
    if m and comps and int(m.group(1)) != len(comps):
        reasons.append("component count")
    if annotation.get("components") and comps:
        claimed_set, actual_set = component_set(annotation["components"]), component_set(comps)
        bound_text = clean(derived.get("definition_span")).lower()
        # The bound literal may retain a subtype omitted by normalized input tokens.
        if len(claimed_set) != len(actual_set) or any(c not in actual_set and c not in bound_text for c in claimed_set):
            reasons.append("component set")
    # Detect a description of an entirely different endpoint. Long composite
    # definitions cannot be substituted for a short harm or component result.
    from .target_endpoint import _components_from_text
    bound = derived.get("definition_span") or derived.get("result_span") or ""
    claimed_comps = _components_from_text(text, expand_named_composites=False)
    actual_comps = _components_from_text(bound, expand_named_composites=False)
    if claimed_comps and actual_comps and claimed_comps - actual_comps:
        reasons.append("endpoint components in bound span")
    # Explicit endpoint subjects, with qualifiers retained (hip != vertebral,
    # efficacy composite != harm). These are lexical facts, not trial-specific rules.
    subjects = (r"non.?vertebral fracture", r"(?<!non)(?<!non-)vertebral fracture",
                r"hip fracture", r"(?:adverse events?|adverse reactions?)", r"hypoglyc[ae]mia",
                r"ketoacidosis", r"amputation", r"(?:major|any) bleeding",
                r"life support", r"treatment failure", r"clinical status", r"mechanical ventilation",
                r"noncardiovascular|non-cardiovascular", r"venous thromboembolism",
                r"mortality|died|death",
                r"diarrh(?:ea|oea)|\baad\b")
    a = {pattern for pattern in subjects if re.search(pattern, text, re.I)}
    b = {pattern for pattern in subjects if re.search(pattern, bound, re.I)}
    if a and b and a.isdisjoint(b):
        reasons.append("different endpoint subject")
    if claimed_comps and b and (not actual_comps or "noncardiovascular" in bound.lower()):
        reasons.append("efficacy components substituted for bound endpoint")
    if "treatment failure" in text.lower() and "mortality" in bound.lower() and "treatment failure" not in bound.lower():
        reasons.append("treatment-failure composite versus mortality")
    asserted_time = annotation.get("timepoint") or annotation.get("follow_up_window")
    if asserted_time and not derived.get("timepoint"):
        # Two retained descriptions can contradict one another even when the
        # input lacks enough time evidence to decide which one is correct.
        window = re.search(r"(?:first|within)\s+(\d+)\s+(days?|weeks?|months?|years?)", text, re.I)
        stated = re.fullmatch(r"(\d+)\s+(days?|weeks?|months?|years?)", clean(asserted_time), re.I)
        if window and stated and (window[1], window[2].rstrip("s")) != (stated[1], stated[2].rstrip("s")):
            reasons.append("conflicting narrative timepoints; input timepoint unbound")
    if asserted_time and derived.get("timepoint"):
        def durations(s):
            text = re.sub(r"(day|week|month|year)\s+(\d+(?:\.\d+)?)", r"\2 \1", clean(s).lower())
            return set(re.findall(r"(\d+(?:\.\d+)?)\s*[- ]?\s*(day|week|month|year)s?", text))
        a, b = durations(asserted_time), durations(derived["timepoint"])
        if a and b and a.isdisjoint(b) and not re.search(r"up to|median|mean|approximately", derived["timepoint"], re.I):
            reasons.append("timepoint")
    return sorted(set(reasons))


def audit_trial(trial, annotations=()):
    derived = derive(trial)
    audit = list(trial.get("narrative_audit") or [])
    candidates = [{"endpoint_definition": None if trial.get("derived_narrative") else trial.get("endpoint_definition"),
                   "follow_up_window": trial.get("follow_up_window")}, *annotations]
    for annotation in candidates:
        if not annotation:
            continue
        reasons = contradictions(derived, annotation)
        entry = {"code": STALE_NARRATIVE if reasons else "NARRATIVE_NOT_CONTRADICTED",
                 "original": deepcopy(annotation), "conflicts": reasons}
        if entry not in audit:
            audit.append(entry)
    derived["audit"] = audit
    return derived


def apply_outcome(outcome, annotations=None):
    """Replace display descriptions, retain original text in a separate audit ledger."""
    per_trial = []
    for trial in outcome.get("trials") or []:
        pid = str(trial.get("id") or trial.get("label") or "").removeprefix("PMID ")
        extra = list((annotations or {}).get(pid, []))
        ck = outcome.get("compat_key") or {}
        old_dim = ck.get("endpoint_definition") or {}
        if isinstance(old_dim, dict):
            extra.extend(x.get("value") for x in old_dim.get("per_trial", [])
                         if str(x.get("trial")) in (pid, str(trial.get("id")), str(trial.get("label"))))
        old_rows = ((outcome.get("compat_underlying") or {}).get("per_trial") or {}).get("endpoint", [])
        extra.extend(x.get("value") for x in old_rows if str(x.get("trial_id")) == pid)

        d = audit_trial(trial, extra)
        trial["narrative_audit"] = d.pop("audit")
        trial["derived_narrative"] = d
        trial["endpoint_definition"] = d["value"]
        trial["follow_up_window"] = d["timepoint"] or "not stated in input"
        trial.setdefault("compat_dimensions", {})["endpoint_definition"] = d
        trial["compat_dimensions"]["follow_up_window"] = {
            "value": trial["follow_up_window"], "source": "pooled input binding", "span": d["span"]}
        per_trial.append({"trial": trial.get("label") or trial.get("id"), "value": d["value"]})
    # The existing underlying table is another display surface, not a source.
    underlying = (outcome.get("compat_underlying") or {}).get("per_trial")
    if underlying is not None:
        for dimension, field in (("endpoint", "endpoint_definition"), ("follow_up_window", "follow_up_window")):
            if dimension in underlying:
                underlying[dimension] = [{"trial_id": str(t.get("id", "")).removeprefix("PMID "),
                    "trial_label": t.get("label"), "value": t.get(field), "source": "pooled input binding",
                    "span": t["derived_narrative"]["span"]} for t in outcome.get("trials") or []]
    ck = outcome.get("compat_key")
    if ck is not None:
        if ck.get("endpoint_definition") and not outcome.get("original_compat_narrative"):
            outcome["original_compat_narrative"] = deepcopy(ck["endpoint_definition"])
        # Recompute component displays from the same inputs, without a cached
        # topic-specific component mapper dropping death/angina subtypes.
        component_rows = [{"trial": t.get("label") or t.get("id"),
                           "value": " | ".join(t["derived_narrative"]["components"]) or "not stated in input"}
                          for t in outcome.get("trials") or []]
        component_values = sorted({x["value"] for x in component_rows})
        if "endpoint_components" in ck:
            ck["endpoint_components"] = {"values": component_values, "matched": len(component_values) <= 1,
                                         "per_trial": component_rows}
        for canonical in (ck.get("endpoint_canonical"), outcome.get("endpoint_canonical")):
            if isinstance(canonical, dict):
                groups = {}
                for t in outcome.get("trials") or []:
                    components = tuple(t["derived_narrative"]["components"])
                    if components:
                        groups.setdefault(components, []).append(t.get("label") or t.get("id"))
                canonical["components"] = sorted({c for group in groups for c in group})
                canonical["component_sets"] = [{"components": list(c), "trials": ts} for c, ts in sorted(groups.items())]
        vals = sorted({x["value"] for x in per_trial})
        ck["endpoint_definition"] = {"values": vals, "matched": len(vals) <= 1, "per_trial": per_trial}
        times = sorted({t["follow_up_window"] for t in outcome.get("trials") or []})
        ck["follow_up_window"] = "; ".join(times)
        for dim in (outcome.get("compat_direction") or {}).get("dimensions", []):
            if dim.get("dimension") == "endpoint_definition":
                dim["underlying"] = deepcopy(ck["endpoint_definition"])

    return outcome


def selection_report(topic, outcome, held_results, common_components=(), protocol=""):
    """Report both policies unless an explicit topic/outcome-wide enum is declared.

    held_results maps EVERY trial ID (including refused/no-result trials) to bound
    candidate objects. Caller supplies source-backed candidates, never estimates
    inferred from labels. Ties remain explicit unless a tie-break was declared.
    Selection is diagnostic only and never overrides an eligibility/refusal decision.
    """
    spec = topic.get("primary_outcome") or {}
    declared = spec.get("result_selection_rule", topic.get("result_selection_rule"))
    if declared not in RULES:
        # Only an explicit, scoped declaration line counts; explanatory mentions
        # of policy names elsewhere in a protocol do not declare a policy.
        m = re.search(r"(?im)^\s*(?:\*\*)?result[-_ ]selection[-_ ]rule(?:\*\*)?\s*:\s*`?(" + "|".join(RULES) + r")\b", protocol)
        declared = m.group(1) if m else None
    served = {str(t.get("id") or t.get("label")).removeprefix("PMID "): t
              for t in outcome.get("trials") or []}
    absent = {str(t.get("id") or t.get("label")).removeprefix("PMID "): t
              for t in outcome.get("declared_absent_trials") or []}
    rows = []
    for pid in sorted(set(held_results) | set(served) | set(absent)):
        candidates = held_results.get(pid, [])
        choices = {}
        for rule in RULES:
            eligible = [c for c in candidates if len(c.get("components") or []) >= 2 and
                        (c.get("endpoint_definition_span") or c.get("registry_title"))]
            if rule == RULES[0]:
                eligible = [c for c in eligible if derive(c)["role"] in ("primary", "co-primary")]
            elif common_components and eligible:
                distance = lambda c: len(component_set(c["components"]) ^ component_set(common_components))
                best = min(map(distance, eligible))
                eligible = [c for c in eligible if distance(c) == best]
            else:
                eligible = []
            # The scoped amendment is a tie-break between multiple primary composites only.
            annotation = (spec.get("trial_annotations") or {}).get(pid, {})
            scoped = annotation.get("co_primary_selection_rule", "")
            if rule == RULES[0] and len(eligible) > 1 and "closest to canonical 3-point MACE" in scoped and common_components:
                distance = lambda c: len(component_set(c["components"]) ^ component_set(common_components))
                best = min(map(distance, eligible))
                eligible = [c for c in eligible if distance(c) == best]
            def matches(c):
                t = served.get(pid)
                return bool(t and component_set(t.get("components")) == component_set(c.get("components"))
                            and all(t.get(k) == c.get(k) for k in ("effect", "ci_low", "ci_high", "scale")))
            choices[rule] = {"selected": [c["candidate_id"] for c in eligible],
                             "status": "SELECTED" if len(eligible) == 1 else "AMBIGUOUS" if eligible else "NO_HELD_RESULT",
                             "served_matches": matches(eligible[0]) if len(eligible) == 1 else None}
        annotation = (spec.get("trial_annotations") or {}).get(pid, {})
        conflicts = audit_trial(served[pid], [annotation])["audit"] if pid in served else []
        inconsistencies = [a for a in conflicts if a["code"] == STALE_NARRATIVE]
        if declared and choices[declared]["status"] == "SELECTED" and not choices[declared]["served_matches"]:
            inconsistencies.append({"code": "RESULT_SELECTION_MISMATCH" if pid in served else "SELECTED_RESULT_REFUSED",
                                    "selected": choices[declared]["selected"],
                                    "refusal": absent.get(pid, {}).get("reason_code")})
        rows.append({"trial_id": pid, "served": pid in served, "inconsistencies": inconsistencies,
                     "refusal": absent.get(pid, {}).get("reason_code"), "selections": choices,
                     "declared_selection": choices.get(declared),
                     "scoped_co_primary_rule": (spec.get("trial_annotations") or {}).get(pid, {}).get("co_primary_selection_rule")})
    return {"declared_rule": declared,
            "status": "DECLARED" if declared else "RESULT_SELECTION_RULE_NOT_DECLARED",
            "protocol_evidence": protocol, "per_trial": rows}
