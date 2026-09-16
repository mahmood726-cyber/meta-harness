"""Check asserted compatibility keys against the pooled trial rows.

The older compatibility key was an outcome-level promise. This module derives
the same dimensions from each pooled trial row and its committed source text,
then refuses a uniform assertion when the underlying rows are heterogeneous.
"""
from __future__ import annotations

import collections
import json
import os
import re
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSERTED_NOT_UNDERLYING = "COMPAT_ASSERTED_NOT_UNDERLYING"
UNDERIVABLE = "COMPAT_DIMENSION_UNDERIVABLE"
HETEROGENEOUS = "COMPAT_DIMENSION_HETEROGENEOUS"
HARMS_INCOMPLETE = "HARMS_INCOMPLETE"

_DIM_TO_KEY = {
    "analysis_set": "analysis_set",
    "follow_up_window": "follow_up_window",
    "endpoint": "endpoint",
}
_DIM_TO_DERIVED = {
    "analysis_set": "analysis_set",
    "follow_up_window": "follow_up_window",
    "endpoint": "endpoint_definition",
}

_PROBIOTIC_CLASS = "probiotic preparations"
_OMEGA3_CLASS = "omega-3 fatty acid preparations"


def _pid(value: Any) -> str:
    s = str(value or "").strip()
    for prefix in ("PMID ", "PMID:", "NCT"):
        if s.upper().startswith(prefix):
            s = s[len(prefix):].strip()
    return s


def _rec_map(records: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for rec in (records or {}).get("records", []) or []:
        if rec.get("id") is not None:
            out[str(rec.get("id"))] = rec
        if rec.get("nct"):
            out[str(rec.get("nct")).upper()] = rec
    return out


def _norm_ws(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _short_span(text: str, match: re.Match[str] | None, flank: int = 110) -> str:
    if not text:
        return ""
    if not match:
        return _norm_ws(text[:240])
    return _norm_ws(text[max(0, match.start() - flank):match.end() + flank])


def _search(pattern: str, text: str) -> re.Match[str] | None:
    return re.search(pattern, text or "", re.I | re.S)


def _load_json(*parts: str) -> dict[str, Any]:
    path = os.path.join(ROOT, *parts)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _topic_definition_audit(slug: str | None, review: dict[str, Any]) -> dict[str, dict[str, Any]]:
    own = review.get("definition_audit") or {}
    if own:
        return own
    if not slug:
        return {}
    all_rows = (_load_json("docs", "definition_audit.json").get("by_row") or {})
    prefix = slug + "::"
    return {k: v for k, v in all_rows.items() if str(k).startswith(prefix)}


def _audit_for_trial(audit: dict[str, dict[str, Any]], outcome: str, pid: str) -> dict[str, Any] | None:
    key = f"::{outcome}::{pid}"
    for rid, row in audit.items():
        if str(rid).endswith(key):
            return row
    return None


def _trial_text(trial: dict[str, Any], rec: dict[str, Any] | None, audit_row: dict[str, Any] | None) -> str:
    bits = [
        trial.get("source"),
        ((trial.get("study_effect") or {}).get("source_provenance") or {}).get("span"),
        (rec or {}).get("title"),
        (rec or {}).get("abstract"),
    ]
    if audit_row:
        bits += [audit_row.get("detail"), audit_row.get("resolution")]
    return _norm_ws(" ".join(str(b or "") for b in bits))


def _text_span(source: str, label: str) -> dict[str, str]:
    return {"source": source, "span": label}


def _derived(value: str | None, source: str, span: str | None) -> dict[str, Any]:
    return {"value": value, "source": source, "span": _norm_ws(span or "")}


def _derive_analysis_set(
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    audit_row: dict[str, Any] | None,
) -> dict[str, Any]:
    text = _trial_text(trial, rec, audit_row)
    rules = [
        (r"\bmodified[-\s]+intention[-\s]+to[-\s]+treat\b|\bmodified\s+ITT\b|\bmITT\b",
         "modified intention-to-treat"),
        (r"\b(completers?|completed the trial and were included|efficacy analysis|no efficacy data)\b",
         "completers efficacy set"),
        (r"\bper[-\s]+protocol\b", "per-protocol"),
        (r"\bintention[-\s]+to[-\s]+treat\b|\bITT population\b|\banalys(?:is|es) (?:was|were )?based on allocated treatment\b|\banalyzed according to the intention-to-treat principle\b|\bdata were analyzed according to the intention-to-treat principle\b",
         "intention-to-treat"),
    ]
    for pattern, value in rules:
        m = _search(pattern, text)
        if m:
            return _derived(value, "committed source text", _short_span(text, m))
    existing = ((trial.get("study_effect") or {}).get("analysis_population")
                or (trial.get("compat_dimensions") or {}).get("analysis_set"))
    if existing and existing != "UNKNOWN":
        return _derived(str(existing), "study_effect.analysis_population", str(existing))
    return _derived(None, "underivable", "")


def _derive_follow_up(
    outcome: dict[str, Any],
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    audit_row: dict[str, Any] | None,
) -> dict[str, Any]:
    text = _trial_text(trial, rec, audit_row)
    rules = [
        (r"\bwithin\s+8\s+weeks\b", "within 8 weeks"),
        (r"\bwithin\s+12\s+weeks\b", "within 12 weeks"),
        (r"\bduring\s+and\s+up\s+to\s+30\s+days\s+after\b|\bAbx\+30d\b", "during treatment plus 30 days"),
        (r"\bduring\s+or\s+up\s+to\s+2\s+weeks\s+after\b|\bup to\s+2\s+weeks\s+after\b", "during treatment plus 2 weeks"),
        (r"\bat\s+56\s+days\b|\b56\s+days\b|56-day", "56 days"),
        (r"\bat\s+14\s+days\b|\b14\s+days\b", "14 days"),
        (r"\bat\s+21\s+days\b|\b21\s+days\b", "21 days"),
        (r"\bmedian follow[-\s]?up of\s+([0-9.]+)\s+years\b", None),
        (r"\bmean follow[-\s]?up of\s+([0-9.]+)\s+years\b", None),
        (r"\bfollowed for a median of\s+([0-9.]+)\s+years\b", None),
        (r"\bfor\s+40\s+months\b", "40 months"),
        (r"\bmedian duration of supplementation was\s+([0-9.]+)\s+years\b", None),
    ]
    for pattern, value in rules:
        m = _search(pattern, text)
        if not m:
            continue
        if value is None and m.groups():
            value = m.group(1) + " years"
        return _derived(value, "committed source text", _short_span(text, m))
    if trial.get("timeframe"):
        return _derived(str(trial.get("timeframe")), "trial.timeframe", str(trial.get("timeframe")))
    if outcome.get("timepoint"):
        return _derived(str(outcome.get("timepoint")), "outcome.timepoint", str(outcome.get("timepoint")))
    return _derived(None, "underivable", "")


def _derive_endpoint(
    outcome: dict[str, Any],
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    audit_row: dict[str, Any] | None,
) -> dict[str, Any]:
    text = _trial_text(trial, rec, audit_row)
    if audit_row and (audit_row.get("detail") or audit_row.get("resolution")):
        label = _norm_ws("; ".join(str(audit_row.get(k) or "") for k in ("detail", "resolution")))
        return _derived(label, "docs/definition_audit.json", label)
    rules = [
        (r"AAD\s*=\s*[^:;.]{8,120}", None),
        (r"diarrh?oe?a\s*\([^)]{10,180}\)", None),
        (r"diarrh?oe?a caused by Clostridium difficile or otherwise unexplained diarrh?oe?a", None),
        (r"primary (?:efficacy )?(?:measure|outcome|end point|endpoint) was a composite of [^.]{20,240}", None),
        (r"primary (?:outcome|end point|endpoint) was [^.]{20,240}", None),
        (r"serious vascular event \([^)]{10,180}\)", None),
        (r"major cardiovascular events, defined as [^.]{20,220}", None),
        (r"major cardiovascular events,? comprised [^.]{20,220}", None),
    ]
    for pattern, _ in rules:
        m = _search(pattern, text)
        if m:
            return _derived(_short_span(text, m, flank=0), "committed source text", _short_span(text, m))
    name = outcome.get("name")
    if name:
        return _derived(str(name), "outcome.name", str(name))
    return _derived(None, "underivable", "")


def _derive_population_age(trial: dict[str, Any], rec: dict[str, Any] | None) -> dict[str, Any]:
    text = _trial_text(trial, rec, None)
    rules = [
        (r"\bchildren\b|\bchild\b|\baged\s+\d+\s+months?\s+to\s+\d+\s+years?\b|\bpa?ediatric\b",
         "paediatric"),
        (r"\badults?\b|\bpatients aged\s+65\s+years and older\b|\bmen\s+\d+\s+years of age or older\b|\bwomen\s+\d+\s+years of age or older\b|\b60 through 80 years\b",
         "adult"),
    ]
    for pattern, value in rules:
        m = _search(pattern, text)
        if m:
            return _derived(value, "committed source text", _short_span(text, m))
    return _derived("not_stated", "committed source text", "")


def _topic_class(review: dict[str, Any]) -> str | None:
    hay = " ".join([
        str(review.get("slug") or ""),
        str((review.get("protocol_config") or {}).get("intervention_i_line") or ""),
        str((review.get("protocol") or {}).get("text") or ""),
    ]).lower()
    if "probiotic" in hay:
        return _PROBIOTIC_CLASS
    if "omega-3" in hay or "omega 3" in hay or "n-3 fatty" in hay:
        return _OMEGA3_CLASS
    return None


def _derive_intervention(review: dict[str, Any], trial: dict[str, Any], rec: dict[str, Any] | None) -> dict[str, Any]:
    text = _trial_text(trial, rec, None).lower()
    klass = _topic_class(review)
    out: dict[str, Any] = {"intervention_class": klass}
    if klass == _PROBIOTIC_CLASS:
        if "saccharomyces" in text or "boulardii" in text:
            out["intervention_member"] = "Saccharomyces boulardii"
        elif "lactobacillus" in text or "lacticaseibacillus" in text or "limosilactobacillus" in text:
            out["intervention_member"] = "Lactobacillus/Lacticaseibacillus preparation"
        elif "bifidobacter" in text:
            out["intervention_member"] = "Bifidobacterium-containing preparation"
        elif "bacillus" in text:
            out["intervention_member"] = "Bacillus-containing preparation"
        else:
            out["intervention_member"] = "probiotic preparation"
        if "yogurt" in text or "yoghurt" in text or "milk drink" in text or "margarine" in text:
            out["formulation"] = "food/fermented-product preparation"
        elif "multistrain" in text or "multi-strain" in text or "mix" in text:
            out["formulation"] = "multistrain product"
        else:
            out["formulation"] = "capsule/supplement or not stated"
        dose = _search(r"(\d+(?:\.\d+)?\s*(?:x|×)?\s*10\(?\d+\)?\s*(?:CFU|organisms)|\d+\s*mg|\d+\s*billion)", text)
        out["dose"] = _norm_ws(dose.group(1)) if dose else "not_stated"
    elif klass == _OMEGA3_CLASS:
        if "icosapent ethyl" in text or ("eicosapentaenoic" in text and "docosahexaenoic" not in text):
            out["agent"] = "EPA-only"
        elif "epa" in text and "dha" in text:
            out["agent"] = "EPA+DHA"
        elif "ala" in text or "alpha-linolenic" in text:
            out["agent"] = "ALA/dietary fatty acid"
        else:
            out["agent"] = "omega-3 fatty acids"
        if "carboxylic acid" in text or "omega-3 ca" in text:
            out["formulation"] = "carboxylic acid"
        elif "ethyl ester" in text or "ethyl esters" in text or "icosapent ethyl" in text:
            out["formulation"] = "ethyl ester"
        elif "margarine" in text:
            out["formulation"] = "dietary margarine"
        else:
            out["formulation"] = "capsule/supplement or not stated"
        dose = _search(r"(\d+(?:\.\d+)?\s*g(?:/d| per day| daily)?|\d+\s*mg)", text)
        out["dose"] = _norm_ws(dose.group(1)) if dose else "not_stated"
        if "mineral oil" in text:
            out["comparator_oil"] = "mineral oil"
        elif "corn oil" in text:
            out["comparator_oil"] = "corn oil"
        elif "olive oil" in text:
            out["comparator_oil"] = "olive oil"
        elif "placebo margarine" in text:
            out["comparator_oil"] = "placebo margarine"
        else:
            out["comparator_oil"] = "placebo/control oil not stated"
        if "without evidence of atherosclerotic cardiovascular disease" in text or "primary prevention" in text:
            out["population_risk"] = "primary prevention"
        elif "established cardiovascular disease" in text or "previous myocardial infarction" in text or "history of myocardial infarction" in text or "secondary prevention" in text:
            out["population_risk"] = "secondary prevention"
        else:
            out["population_risk"] = "mixed/unclear cardiovascular risk"
        out["population_enrichment"] = "triglyceride-enriched" if "triglyceride" in text or "hypertriglyceridemia" in text else "not_stated"
    return out


def derive_trial_dimensions(
    review: dict[str, Any],
    outcome: dict[str, Any],
    trial: dict[str, Any],
    records: dict[str, Any] | None = None,
    definition_audit: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    recs = _rec_map(records)
    pid = _pid(trial.get("id") or trial.get("label"))
    rec = recs.get(pid) or {}
    audit_row = _audit_for_trial(definition_audit or {}, str(outcome.get("name") or ""), pid)
    dims = {
        "trial_id": pid,
        "trial_label": trial.get("label") or trial.get("id"),
        "analysis_set": _derive_analysis_set(trial, rec, audit_row),
        "follow_up_window": _derive_follow_up(outcome, trial, rec, audit_row),
        "endpoint_definition": _derive_endpoint(outcome, trial, rec, audit_row),
        "population_age": _derive_population_age(trial, rec),
        "intervention_ontology": _derive_intervention(review, trial, rec),
    }
    return dims


def _canon(value: Any) -> str:
    s = _norm_ws(value).lower()
    s = s.replace("modified intention-to-treat", "mitt")
    s = s.replace("modified-intention-to-treat", "mitt")
    s = s.replace("intention to treat", "intention-to-treat")
    return s


def _is_unasserted_value(dim: str, value: Any, ck: dict[str, Any]) -> bool:
    matches = ck.get("dimension_matches") or {}
    if matches.get(dim) is False:
        return True
    s = _canon(value)
    return "mixed" in s or "trial-defined" in s or "heterogeneous" in s


def _value_counts(values: list[str]) -> dict[str, int]:
    return dict(collections.Counter(values))


def _violation(outcome: dict[str, Any], dim: str, code: str, asserted: Any,
               per_trial: list[dict[str, Any]], detail: str = "") -> dict[str, Any]:
    return {
        "code": code,
        "outcome": outcome.get("name"),
        "dimension": dim,
        "asserted": asserted,
        "per_trial_values": per_trial,
        "detail": detail,
    }


def _is_mismatch(dim: str, asserted: Any, values: list[str]) -> bool:
    vals = [_canon(v) for v in values if v]
    if not vals:
        return False
    if len(set(vals)) > 1:
        return True
    av = _canon(asserted)
    if dim == "analysis_set":
        if av in {"intention-to-treat", "itt"}:
            return any(v not in {"intention-to-treat", "itt"} for v in vals)
        return any(v != av for v in vals)
    if dim == "follow_up_window":
        if "study end" in av or "trial end" in av:
            return len(set(vals)) > 1 or any(v not in {av, "study end", "trial end"} for v in vals)
        return any(v != av for v in vals)
    if dim == "endpoint":
        if av in {"single endpoint", "composite"}:
            return len(set(vals)) > 1 or any(v != av for v in vals)
        return any(v != av for v in vals)
    return any(v != av for v in vals)


def check(
    review: dict[str, Any],
    records: dict[str, Any] | None = None,
    definition_audit: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return compatibility-underlying violations for a review object."""
    slug = review.get("slug")
    definition_audit = definition_audit or _topic_definition_audit(str(slug) if slug else None, review)
    violations: list[dict[str, Any]] = []
    for outcome in review.get("outcomes", []) or []:
        ck = outcome.get("compat_key") or {}
        if not ck:
            continue
        derived_rows = [
            derive_trial_dimensions(review, outcome, trial, records, definition_audit)
            for trial in (outcome.get("trials") or [])
        ]
        for dim, key_name in _DIM_TO_KEY.items():
            asserted = ck.get(key_name)
            if asserted in (None, "") or _is_unasserted_value(dim, asserted, ck):
                continue
            derived_key = _DIM_TO_DERIVED[dim]
            per_trial = []
            underivable = []
            values = []
            for row in derived_rows:
                cell = row.get(derived_key) or {}
                value = cell.get("value")
                item = {
                    "trial_id": row.get("trial_id"),
                    "trial_label": row.get("trial_label"),
                    "value": value,
                    "source": cell.get("source"),
                    "span": cell.get("span"),
                }
                per_trial.append(item)
                if value in (None, ""):
                    underivable.append(item)
                else:
                    values.append(str(value))
            if underivable:
                violations.append(_violation(
                    outcome, dim, UNDERIVABLE, asserted, underivable,
                    "per-trial value could not be derived from the row or committed source",
                ))
                continue
            if _is_mismatch(dim, asserted, values):
                violations.append(_violation(
                    outcome, dim, ASSERTED_NOT_UNDERLYING, asserted, per_trial,
                    "outcome-level key asserts a uniform value but pooled trial rows differ",
                ))
    return violations


def _summarize_analysis(values: list[str]) -> str:
    counts = _value_counts(values)
    parts = []
    labels = [
        ("intention-to-treat", "ITT"),
        ("modified intention-to-treat", "mITT"),
        ("completers efficacy set", "completers"),
        ("per-protocol", "per-protocol"),
    ]
    for raw, lab in labels:
        if counts.get(raw):
            parts.append(f"{lab} x{counts[raw]}")
    for raw, n in counts.items():
        if raw not in {r for r, _ in labels}:
            parts.append(f"{raw} x{n}")
    return "mixed (" + ", ".join(parts) + ")" if parts else "mixed"


def _summarize_follow(values: list[str]) -> str:
    nums = []
    for v in values:
        for n in re.findall(r"\b(\d+)\s+days?\b", v):
            nums.append(int(n))
    if nums:
        return f"trial-defined ({min(nums)}-{max(nums)} d; per trial listed)"
    return "trial-defined (per trial listed)"


def _summarize_endpoint(outcome: dict[str, Any]) -> str:
    name = str(outcome.get("name") or "endpoint")
    if "antibiotic-associated" in name.lower():
        return "trial-defined antibiotic-associated diarrhoea (definitions listed per trial)"
    return f"trial-defined {name} (definitions listed per trial)"


def _fix_compat_key(outcome: dict[str, Any], violations: list[dict[str, Any]]) -> None:
    ck = outcome.get("compat_key")
    if not isinstance(ck, dict):
        return
    by_dim = {v["dimension"]: v for v in violations if v.get("code") == ASSERTED_NOT_UNDERLYING}
    if not by_dim:
        return
    dim_matches = dict(ck.get("dimension_matches") or {})
    per_trial_table: dict[str, list[dict[str, Any]]] = {}
    for dim, viol in by_dim.items():
        vals = [str(x.get("value")) for x in viol.get("per_trial_values") or [] if x.get("value")]
        if dim == "analysis_set":
            ck["analysis_set"] = _summarize_analysis(vals)
        elif dim == "follow_up_window":
            ck["follow_up_window"] = _summarize_follow(vals)
        elif dim == "endpoint":
            ck["endpoint"] = _summarize_endpoint(outcome)
        dim_matches[dim] = False
        per_trial_table[dim] = viol.get("per_trial_values") or []
    ck["dimension_matches"] = dim_matches
    ck["limitation_code"] = HETEROGENEOUS
    ck["underlying_checked"] = True
    outcome["compat_underlying"] = {
        "status": HETEROGENEOUS,
        "dimensions": sorted(by_dim),
        "per_trial": per_trial_table,
    }


def _attach_trial_dimensions(
    review: dict[str, Any],
    records: dict[str, Any] | None,
    definition_audit: dict[str, dict[str, Any]],
) -> None:
    for outcome in review.get("outcomes", []) or []:
        for trial in outcome.get("trials") or []:
            dims = derive_trial_dimensions(review, outcome, trial, records, definition_audit)
            trial["analysis_set"] = (dims["analysis_set"] or {}).get("value")
            trial["follow_up_window"] = (dims["follow_up_window"] or {}).get("value")
            trial["endpoint_definition"] = (dims["endpoint_definition"] or {}).get("value")
            trial["population_age"] = (dims["population_age"] or {}).get("value")
            trial["intervention_ontology"] = dims["intervention_ontology"]
            trial["compat_dimensions"] = dims


def _source_for_pid(slug: str, pid: str, rec: dict[str, Any]) -> str:
    bits = [rec.get("title"), rec.get("abstract")]
    ft_path = os.path.join(ROOT, "cache", slug, f"ft_{pid}.txt")
    try:
        with open(ft_path, encoding="utf-8") as f:
            bits.append(f.read())
    except OSError:
        pass
    return _norm_ws(" ".join(str(b or "") for b in bits))


def _harm_terms(name: str) -> list[str]:
    n = name.lower()
    if "atrial" in n:
        return ["atrial fibrillation", "atrial flutter"]
    if "bleed" in n or "hemorrhage" in n or "haemorrhage" in n:
        return ["serious bleeding", "major bleeding", "bleeding events", "bleeding event", "bleeding"]
    return [n]


def _apply_harms_incomplete(review: dict[str, Any], records: dict[str, Any] | None) -> None:
    slug = str(review.get("slug") or "")
    if not slug:
        return
    recs = _rec_map(records)
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    primary_ids = [_pid(t.get("id") or t.get("label")) for t in (primary or {}).get("trials", []) or []]
    for outcome in review.get("outcomes", []) or []:
        if outcome.get("kind") != "harm":
            continue
        terms = _harm_terms(str(outcome.get("name") or ""))
        pooled_ids = {_pid(t.get("id") or t.get("label")) for t in outcome.get("trials", []) or []}
        refused_ids = {_pid(t.get("id") or t.get("label")) for t in outcome.get("declared_absent_trials", []) or []
                       if t.get("state") == "REFUSED_ON_EVIDENCE"}
        known = []
        for pid in primary_ids:
            rec = recs.get(pid) or {}
            text = _source_for_pid(slug, pid, rec).lower()
            hits = [term for term in terms if term in text]
            if hits:
                m = _search("|".join(re.escape(t) for t in hits), text)
                known.append({
                    "trial_id": pid,
                    "trial_label": (rec.get("acronym") or pid),
                    "terms": hits,
                    "span": _short_span(text, m),
                })
        unresolved = [x for x in known if x["trial_id"] not in pooled_ids and x["trial_id"] not in refused_ids]
        if unresolved and len(pooled_ids) < len(known):
            outcome["harms_incomplete"] = {
                "state": HARMS_INCOMPLETE,
                "n_reporting_pool_trials": len(known),
                "n_pooled": len(pooled_ids),
                "unresolved": unresolved,
            }
            outcome["result"] = {
                "present": False,
                "state": HARMS_INCOMPLETE,
                "n_reporting_pool_trials": len(known),
                "n_pooled": len(pooled_ids),
                "known_eligible_outcome_reports_unresolved": unresolved,
                "reason": (f"{HARMS_INCOMPLETE}: {len(unresolved)} known eligible outcome report(s) "
                           f"from primary-pool trials are unresolved; an isolated k={len(pooled_ids)} "
                           "harm estimate is suppressed until those rows are extracted or typed-refused."),
            }
            outcome.pop("compat_key", None)


def _comparator_age_scope(review: dict[str, Any], records: dict[str, Any] | None) -> None:
    comp = review.get("comparator")
    if not isinstance(comp, dict):
        return
    scope = comp.setdefault("scope", {})
    klass = _topic_class(review)
    if klass:
        scope["topic_is_class"] = True
        scope["topic_intervention_level"] = "intervention_class"
        scope["topic_intervention_class"] = klass
    text = " ".join([str(comp.get("name") or ""), str(comp.get("journal") or "")]).lower()
    comp_pmid = str(comp.get("pmid") or "")
    rec = _rec_map(records).get(comp_pmid) or {}
    comp_text = (text + " " + str(rec.get("title") or "") + " " + str(rec.get("abstract") or "")).lower()
    if "probiotic" in comp_text or "omega-3" in comp_text or "omega 3" in comp_text or "fatty acid" in comp_text:
        scope["comparator_is_class"] = True
        scope["comparator_intervention_level"] = "intervention_class"
    primary = next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)
    ages = []
    for trial in (primary or {}).get("trials", []) or []:
        age = trial.get("population_age") or ((trial.get("compat_dimensions") or {}).get("population_age") or {}).get("value")
        if age:
            ages.append({"trial_id": _pid(trial.get("id") or trial.get("label")), "age": age})
    adult_only_comp = bool(re.search(r"\badults?\b|\badult population\b", comp_text))
    paed = [x for x in ages if x.get("age") == "paediatric"]
    if adult_only_comp and paed:
        scope["population_match"] = False
        scope["population_match_basis"] = {
            "comparator": "adult-only comparator",
            "pool_has_paediatric_trials": paed,
        }
        scope["scope_valid"] = False
        scope["note"] = ("adult-only comparator vs a pool containing paediatric trials; population scope "
                         "does not match even though the broad topic label is similar")
    if scope.get("topic_is_class") and scope.get("comparator_is_class"):
        scope["intervention_level_match"] = True


def enrich(
    review: dict[str, Any],
    records: dict[str, Any] | None = None,
    definition_audit: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Attach per-trial dimensions and soften heterogeneous key assertions."""
    slug = review.get("slug")
    definition_audit = definition_audit or _topic_definition_audit(str(slug) if slug else None, review)
    _attach_trial_dimensions(review, records, definition_audit)
    before = check(review, records, definition_audit)
    for outcome in review.get("outcomes", []) or []:
        ovs = [v for v in before if v.get("outcome") == outcome.get("name")]
        _fix_compat_key(outcome, ovs)
    _apply_harms_incomplete(review, records)
    _comparator_age_scope(review, records)
    after = check(review, records, definition_audit)
    review["compat_underlying"] = {
        "checked": True,
        "n_pre_fix_asserted_not_underlying": sum(1 for v in before if v.get("code") == ASSERTED_NOT_UNDERLYING),
        "n_post_fix_asserted_not_underlying": sum(1 for v in after if v.get("code") == ASSERTED_NOT_UNDERLYING),
        "pre_fix_violations": before,
        "post_fix_violations": after,
    }
    return review


def page_gate_violations(review: dict[str, Any], records: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    return [v for v in check(review, records) if v.get("code") == ASSERTED_NOT_UNDERLYING]
