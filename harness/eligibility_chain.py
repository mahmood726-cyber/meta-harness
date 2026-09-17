"""Executable eligibility chain.

The protocol, screening config, rendered compatibility key, and per-trial values
are separate sources. This module compares them without changing pooling
arithmetic: it annotates the review object with the contract that would have to
be true for a pooled row to be admissible, and emits typed violations when the
sources disagree.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import re
from typing import Any

from . import screen


HARD_CODES = {
    "PROTOCOL_CONFIG_DIVERGENCE",
    "CONFIG_WITHOUT_PROTOCOL",
    "TRIAL_FAILS_CONTRACT",
    "ELIGIBILITY_STATE_INCONSISTENT",
    "PROSE_PREDICATE_FALSE",
}

_PMID_RE = re.compile(r"\b(?:PMID\s*)?(\d{7,9})\b")


@dataclass(frozen=True)
class Criterion:
    dimension: str
    value: Any
    sentence: str


def _norm(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def _fold(text: Any) -> str:
    return _norm(text).lower()


def _pid(value: Any) -> str:
    m = _PMID_RE.search(str(value or ""))
    return m.group(1) if m else str(value or "").replace("PMID ", "").strip()


def _sentence_containing(md_text: str, needle: str) -> str:
    text = _norm(md_text)
    folded = text.lower()
    n = needle.lower()
    idx = folded.find(n)
    if idx < 0:
        return ""
    left = max(text.rfind(".", 0, idx), text.rfind("\n", 0, idx))
    right_dot = text.find(".", idx)
    right_nl = text.find("\n", idx)
    candidates = [x for x in (right_dot, right_nl) if x >= 0]
    right = min(candidates) if candidates else len(text)
    return text[left + 1:right + 1].strip(" -")


def protocol_criteria(md_text: str) -> dict[str, Criterion]:
    """Extract the protocol's executable criteria.

    Conservative: only dimensions with recognizable wording are returned. A
    caller that needs a criterion to be executable compares this dict to the
    config rules and emits a refusal when a stated protocol dimension has no
    machine rule.
    """
    tl = _fold(md_text)
    out: dict[str, Criterion] = {}
    if re.search(r"double[-\s]blind\s+or\s+placebo[-\s]controlled", tl):
        out["design_masking"] = Criterion(
            "design_masking", "double_blind_or_placebo_controlled",
            _sentence_containing(md_text, "double-blind") or "double-blind OR placebo-controlled",
        )
    elif (re.search(r"double[-\s]blind[, ]+\s*placebo[-\s]controlled", tl)
          or re.search(r"double[-\s]blind\s+and\s+placebo[-\s]controlled", tl)):
        out["design_masking"] = Criterion(
            "design_masking", "double_blind_and_placebo_controlled",
            _sentence_containing(md_text, "double-blind") or "double-blind placebo-controlled",
        )
    if "broad cardiovascular outcome trial" in tl or "broad cardiovascular outcome trials" in tl:
        out["design_population_context"] = Criterion(
            "design_population_context", "broad_cv_outcome_trial",
            _sentence_containing(md_text, "broad cardiovascular outcome trial"),
        )
    if "ovulation-induction/subfertility context" in tl or "ovulation induction/subfertility context" in tl:
        out["population_context"] = Criterion(
            "population_context", "ovulation_induction_or_subfertility",
            _sentence_containing(md_text, "ovulation-induction/subfertility context"),
        )
    if m := re.search(r"\*\*Population\*\*\s*[-:]\s*([^\n.]+)", md_text, re.I):
        pop = _fold(m.group(1))
        if "intention" in pop or "itt" in pop:
            out["analysis_set"] = Criterion("analysis_set", "intention-to-treat", m.group(0))
        elif "as randomised" in pop or "as randomized" in pop:
            out["analysis_set"] = Criterion("analysis_set", "as_randomised", m.group(0))
        elif "per-protocol" in pop or "per protocol" in pop:
            out["analysis_set"] = Criterion("analysis_set", "per-protocol", m.group(0))
    elif "intention-to-treat" in tl or "intention to treat" in tl:
        out["analysis_set"] = Criterion(
            "analysis_set", "intention-to-treat",
            _sentence_containing(md_text, "intention-to-treat"),
        )
    if m := re.search(r"\*\*Timepoint\*\*\s*[-:]\s*([^\n.]+)", md_text, re.I):
        out["follow_up_window"] = Criterion("follow_up_window", _fold(m.group(1)), m.group(0))
    elif "in-hospital / index-admission" in tl:
        out["follow_up_window"] = Criterion(
            "follow_up_window", "in-hospital / index-admission",
            _sentence_containing(md_text, "in-hospital / index-admission"),
        )
    if re.search(r"\bplacebo\b|\busual care\b|\bno colchicine\b|\bcontrol\b", tl):
        out["comparator"] = Criterion(
            "comparator", "protocol_comparator",
            _sentence_containing(md_text, "placebo") or _sentence_containing(md_text, "control"),
        )
    return out


def _config_rules(config: dict[str, Any]) -> dict[str, Any]:
    inc = config.get("include") or {}
    primary = config.get("primary_outcome") or {}
    rules: dict[str, Any] = {}
    if inc.get("design_double_blind"):
        # screen._double_blind accepts a placebo-controlled record as satisfying
        # this rule, so its executable semantics are OR, not AND.
        rules["design_masking"] = "double_blind_or_placebo_controlled"
    if inc.get("comparator_any") or inc.get("comparator_any_extra"):
        rules["comparator"] = list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])
    if inc.get("population_any") or inc.get("population_any_extra"):
        rules["population"] = list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])
    if primary.get("population"):
        rules["analysis_set"] = primary.get("population")
    if primary.get("timepoint"):
        rules["follow_up_window"] = primary.get("timepoint")
    if inc.get("broad_cvot") or inc.get("design_broad_cvot") or inc.get("trial_context_any"):
        rules["design_population_context"] = "broad_cv_outcome_trial"
    if inc.get("population_context_any"):
        rules["population_context"] = list(inc.get("population_context_any") or [])
    return rules


def compile_contract(slug: str, config: dict[str, Any], md_text: str) -> dict[str, Any]:
    criteria = protocol_criteria(md_text)
    rules = _config_rules(config)
    divergences: list[dict[str, Any]] = []
    agreed: list[str] = []
    for dim, crit in sorted(criteria.items()):
        cfg = rules.get(dim)
        if cfg is None:
            divergences.append({
                "code": "PROTOCOL_CONFIG_DIVERGENCE",
                "dimension": dim,
                "protocol_value": crit.value,
                "config_value": None,
                "sentence": crit.sentence,
                "detail": f"protocol states {dim}, but the topic config has no executable rule for it",
            })
            continue
        if dim == "design_masking" and cfg != crit.value:
            divergences.append({
                "code": "PROTOCOL_CONFIG_DIVERGENCE",
                "dimension": dim,
                "protocol_value": crit.value,
                "config_value": cfg,
                "sentence": crit.sentence,
                "detail": f"protocol requires {crit.value}, config enforces {cfg}",
            })
        elif dim in {"design_population_context", "population_context"} and cfg != crit.value:
            divergences.append({
                "code": "PROTOCOL_CONFIG_DIVERGENCE",
                "dimension": dim,
                "protocol_value": crit.value,
                "config_value": cfg,
                "sentence": crit.sentence,
                "detail": f"protocol criterion {crit.value} is not represented by an equivalent config rule",
            })
        else:
            agreed.append(dim)
    for dim, cfg in sorted(rules.items()):
        if dim in {"population"}:
            continue
        if dim not in criteria:
            divergences.append({
                "code": "CONFIG_WITHOUT_PROTOCOL",
                "dimension": dim,
                "protocol_value": None,
                "config_value": cfg,
                "detail": f"config has executable rule {dim}, but no protocol sentence was parsed for it",
            })
    return {
        "slug": slug,
        "criteria": {k: {"dimension": v.dimension, "value": v.value, "sentence": v.sentence}
                     for k, v in criteria.items()},
        "config_rules": rules,
        "divergences": divergences,
        "agreed_dimensions": agreed,
    }


def _record_text(rec: dict[str, Any] | None, trial: dict[str, Any] | None = None) -> str:
    rec = rec or {}
    trial = trial or {}
    return " ".join(str(x or "") for x in (
        rec.get("title"), rec.get("abstract"), " ".join(rec.get("conditions") or []),
        " ".join(rec.get("interventions") or []), rec.get("masking"), trial.get("source"),
    ))


def _span(text: str, needle: str) -> str:
    i = _fold(text).find(_fold(needle))
    if i < 0:
        return ""
    a = max(0, i - 45)
    b = min(len(text), i + len(needle) + 90)
    return ("..." if a else "") + _norm(text[a:b]) + ("..." if b < len(text) else "")


def _design_value(text: str, rec: dict[str, Any] | None = None) -> tuple[str, str]:
    tl = _fold(text)
    masking = _fold((rec or {}).get("masking"))
    if "open-label" in tl or "open label" in tl:
        return "open_label", _span(text, "open-label") or _span(text, "open label")
    if "no-colchicine" in tl or "no colchicine" in tl:
        return "open_label_no_colchicine", _span(text, "no-colchicine") or _span(text, "no colchicine")
    has_blind = any(x in tl for x in ("double-blind", "double blind", "triple-blind", "triple blind",
                                      "quadruple", "masked")) or any(x in masking for x in ("double", "triple", "quadruple"))
    has_placebo = "placebo" in tl
    if has_blind and has_placebo:
        return "double_blind_placebo_controlled", _span(text, "double-blind") or _span(text, "placebo")
    if has_blind:
        return "double_blind", _span(text, "double-blind") or masking
    if has_placebo:
        return "placebo_controlled", _span(text, "placebo")
    return "not_stated", ""


def _passes_design(value: str, contract: str | None) -> bool | None:
    if not contract:
        return None
    blind = value in {"double_blind", "double_blind_placebo_controlled"}
    placebo = value in {"placebo_controlled", "double_blind_placebo_controlled"}
    if contract == "double_blind_or_placebo_controlled":
        return blind or placebo
    if contract == "double_blind_and_placebo_controlled":
        return blind and placebo
    return None


def _follow_up_value(pid: str, text: str) -> tuple[str, str]:
    known = {
        "25172965": ("3 months", "within 3 months / 1- and 3-month visits"),
        "27502857": ("in-hospital / until discharge", "continued until hospital discharge"),
        "32720823": ("in-hospital / until discharge", "until hospital discharge"),
        "42132185": ("14 days / postoperative admission", "maintenance dose ... for 14 days"),
        "22090167": ("1 month", "at 1 month"),
        "36286314": ("until discharge", "until the discharge from the hospital"),
    }
    if pid in known:
        return known[pid]
    tl = _fold(text)
    for pat, val in (("trial end", "trial end"), ("3 months", "3 months"), ("1 month", "1 month"), ("14 days", "14 days"),
                     ("hospital discharge", "in-hospital / until discharge"), ("in-hospital", "in-hospital")):
        if pat in tl:
            return val, _span(text, pat)
    return "not_stated", ""


def _analysis_set_value(pid: str, text: str) -> tuple[str, str]:
    tl = _fold(text)
    if pid == "42132185":
        return "AVAILABLE_CASE", "172 randomised; 163 analysed (81 + 82)"
    if pid == "36286314":
        return "MODIFIED_ITT", "267 randomised; 240 final analysis"
    if "intention-to-treat" in tl or "intention to treat" in tl:
        return "ITT", _span(text, "intention")
    if "analyzed patients" in tl or "analysed patients" in tl or "final analysis included" in tl:
        return "AVAILABLE_CASE", _span(text, "analyzed patients") or _span(text, "final analysis included")
    return "not_stated", ""


def _passes_analysis(value: str, contract: str | None) -> bool | None:
    if not contract:
        return None
    cl = _fold(contract)
    if "intention" in cl or "itt" in cl:
        return value in {"ITT"}
    if "as random" in cl:
        return value in {"ITT", "not_stated"}
    return None


def _endpoint_definition(pid: str, text: str) -> dict[str, str]:
    data = {
        "27502857": {"duration_threshold": ">5 minutes", "surveillance_window": "until hospital discharge"},
        "32720823": {"duration_threshold": ">=5 minutes", "surveillance_window": "until hospital discharge"},
        "25172965": {"duration_threshold": ">=30 seconds", "surveillance_window": "1- and 3-month visits"},
        "42132185": {"duration_threshold": "not_stated", "surveillance_window": "14-day regimen / analysed population"},
    }
    if pid in data:
        return data[pid]
    tl = _fold(text)
    if "5 minutes" in tl:
        return {"duration_threshold": ">=5 minutes", "surveillance_window": "not_stated"}
    return {"duration_threshold": "not_stated", "surveillance_window": "not_stated"}


def admission_record(
    trial: dict[str, Any],
    rec: dict[str, Any] | None,
    outcome: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    pid = _pid(trial.get("id") or trial.get("label"))
    text = _record_text(rec, trial)
    criteria = contract.get("criteria") or {}
    cfg = contract.get("config_rules") or {}
    out: dict[str, dict[str, Any]] = {}

    dval, dspan = _design_value(text, rec)
    dc = (criteria.get("design_masking") or {}).get("value")
    dv = _passes_design(dval, dc)
    out["design_masking"] = {
        "trial_value": dval,
        "span": dspan,
        "contract_value": dc,
        "verdict": "PASS" if dv is True else ("FAIL" if dv is False else "NOT_CHECKED"),
    }

    comp_terms = cfg.get("comparator") or []
    comp_hit = next((term for term in comp_terms if _fold(term) in _fold(text)), None)
    out["comparator"] = {
        "trial_value": comp_hit or "not_stated",
        "span": _span(text, comp_hit) if comp_hit else "",
        "contract_value": comp_terms,
        "verdict": "PASS" if (not comp_terms or comp_hit) else "FAIL",
    }

    fu, fspan = _follow_up_value(pid, text)
    fcontract = (criteria.get("follow_up_window") or {}).get("value")
    fp = None
    if fcontract:
        fl = _fold(fu)
        fc = _fold(fcontract)
        if "trial end" in fc:
            fp = fl == "trial end"
        elif "end of treatment" in fc:
            fp = fl in {"trial end", "end of treatment", "not_stated"}
        else:
            fp = any(x in fl for x in ("in-hospital", "index", "discharge"))
    out["follow_up_window"] = {
        "trial_value": fu,
        "span": fspan,
        "contract_value": fcontract or outcome.get("timepoint"),
        "verdict": "PASS" if fp is True else ("FAIL" if fp is False else "NOT_CHECKED"),
    }

    av, aspan = _analysis_set_value(pid, text)
    acontract = (criteria.get("analysis_set") or {}).get("value") or outcome.get("population")
    ap = _passes_analysis(av, acontract)
    out["analysis_set"] = {
        "trial_value": av,
        "span": aspan,
        "contract_value": acontract,
        "verdict": "PASS" if ap is True else ("FAIL" if ap is False else "NOT_CHECKED"),
    }

    ep = _endpoint_definition(pid, text)
    out["endpoint_definition"] = {
        "trial_value": ep,
        "span": "",
        "contract_value": "topic endpoint definition",
        "verdict": "DESCRIPTIVE",
    }
    return out


def _trial_failures(outcome: dict[str, Any]) -> list[dict[str, Any]]:
    out = []
    for trial in outcome.get("trials") or []:
        admission = trial.get("admission") or {}
        for dim, row in admission.items():
            if row.get("verdict") == "FAIL":
                out.append({
                    "code": "TRIAL_FAILS_CONTRACT",
                    "dimension": dim,
                    "outcome": outcome.get("name"),
                    "trial": trial.get("label") or trial.get("id"),
                    "trial_id": trial.get("id"),
                    "trial_value": row.get("trial_value"),
                    "contract_value": row.get("contract_value"),
                    "span": row.get("span"),
                    "detail": f"{trial.get('label') or trial.get('id')} fails {dim}",
                })
    return out


def _prose_predicates(review: dict[str, Any]) -> list[dict[str, Any]]:
    if review.get("slug") != "colchicine-postop-af":
        return []
    out = []
    records = (review.get("screening") or {}).get("records") or []
    ids = {str(r.get("id")).split("·")[-1].strip() for r in records}
    caveat = review.get("evidence_base_caveat") or ""
    if "original COPPS" in caveat and "22090167" in ids:
        out.append({
            "code": "PROSE_PREDICATE_FALSE",
            "dimension": "reach_vs_screening",
            "detail": "prose says original COPPS was never found, but PMID 22090167 is in the screening table",
        })
    parity = ((review.get("reproduction") or {}).get("parity") or {}).get("reason", "")
    primary = next((o for o in review.get("outcomes") or [] if o.get("primary")), {})
    absent = {str(a.get("id") or ""): a for a in primary.get("declared_absent_trials") or []}
    cocs = absent.get("PMID 36286314")
    if "not a search/extraction failure" in parity and cocs:
        out.append({
            "code": "PROSE_PREDICATE_FALSE",
            "dimension": "extraction_debt",
            "trial": "PMID 36286314",
            "detail": "parity says the k gap is not an extraction failure while COCS is marked not extracted",
        })
    return out


def _state_inconsistencies(review: dict[str, Any]) -> list[dict[str, Any]]:
    if review.get("slug") != "colchicine-postop-af":
        return []
    out = []
    z_screen = None
    for row in (review.get("screening") or {}).get("records") or []:
        if str(row.get("id")) == "27223641" and row.get("decision") == "exclude":
            z_screen = row
            break
    parity = ((review.get("reproduction") or {}).get("parity") or {}).get("reason", "")
    if z_screen and "Zarpelon" in parity:
        rationale2 = "multi-arm/dose-timing ambiguity"
        if "MULTI-ARM" in parity or "dose/timing" in parity:
            out.append({
                "code": "ELIGIBILITY_STATE_INCONSISTENT",
                "trial": "PMID 27223641",
                "dimension": "exclusion_rationale",
                "rationales": [z_screen.get("reason"), rationale2],
                "detail": "Zarpelon carries screening and parity rationales for one exclusion decision",
            })
    return out


def apply_admissions(
    review: dict[str, Any],
    config: dict[str, Any],
    records: dict[str, Any],
    protocol_text: str,
) -> dict[str, Any]:
    contract = compile_contract(review.get("slug") or config.get("slug") or "", config, protocol_text)
    rec_by_id = {str(r.get("id")): r for r in records.get("records") or []}
    violations = list(contract.get("divergences") or [])
    for outcome in review.get("outcomes") or []:
        for trial in outcome.get("trials") or []:
            rec = rec_by_id.get(_pid(trial.get("id")))
            trial["admission"] = admission_record(trial, rec, outcome, contract)
        for row in outcome.get("declared_absent_trials") or []:
            rec = rec_by_id.get(_pid(row.get("id") or row.get("label")))
            if not rec:
                continue
            admission = admission_record(row, rec, outcome, contract)
            row["admission"] = admission
            design = admission.get("design_masking") or {}
            if design.get("verdict") == "FAIL":
                row["eligibility_chain_rationale"] = "design_masking"
                row["eligibility_refusal_code"] = "TRIAL_FAILS_CONTRACT"
                row["absent_kind"] = "refused_on_evidence"
                row["reason_code"] = "REFUSED_ON_EVIDENCE"
                row["state"] = "REFUSED_ON_EVIDENCE"
                row["reason"] = (
                    "eligibility chain refusal: trial design/masking "
                    f"{design.get('trial_value')} does not satisfy protocol contract "
                    f"{design.get('contract_value')}"
                )
                row["state_basis"] = (
                    "REFUSED_ON_EVIDENCE: " + (design.get("span") or row["reason"])
                )
        violations.extend(_trial_failures(outcome))
        _derive_key_from_admissions(outcome)
    violations.extend(_state_inconsistencies(review))
    violations.extend(_prose_predicates(review))
    review["eligibility_chain"] = {
        "contract": contract,
        "violations": violations,
        "summary": dict(Counter(v["code"] for v in violations)),
    }
    pc = review.setdefault("protocol_config", {})
    pc["divergences"] = list(contract.get("divergences") or [])
    pc["agreed_dimensions"] = list(contract.get("agreed_dimensions") or [])
    return review


def _dimension_from_admissions(outcome: dict[str, Any], dim: str) -> dict[str, Any] | None:
    values = []
    per_trial = []
    for trial in outcome.get("trials") or []:
        row = (trial.get("admission") or {}).get(dim)
        if not row:
            continue
        value = row.get("trial_value")
        key = value if isinstance(value, str) else str(value)
        values.append(key)
        per_trial.append({"trial": trial.get("label") or trial.get("id"), "value": value,
                          "verdict": row.get("verdict")})
    if not per_trial:
        return None
    return {"values": sorted(set(values)), "matched": len(set(values)) <= 1, "per_trial": per_trial}


def _derive_key_from_admissions(outcome: dict[str, Any]) -> None:
    if not outcome.get("trials"):
        return
    ck = outcome.get("compat_key") or {}
    for dim in ("follow_up_window", "analysis_set", "endpoint_definition"):
        d = _dimension_from_admissions(outcome, dim)
        if d:
            ck[dim] = d
            if not d["matched"]:
                ck.setdefault("limitations", []).append({
                    "code": "COMPAT_DIMENSION_HETEROGENEOUS",
                    "dimension": dim,
                    "detail": f"pooled trials differ on {dim}: " + ", ".join(str(x) for x in d["values"]),
                    "hard": dim in {"follow_up_window", "analysis_set"},
                })
    if ck:
        ck["matched"] = ck.get("matched", True) and not any(
            x.get("hard") for x in ck.get("limitations") or []
            if x.get("code") == "COMPAT_DIMENSION_HETEROGENEOUS"
        )
        outcome["compat_key"] = ck


def check_review(review: dict[str, Any]) -> list[dict[str, Any]]:
    return list(((review.get("eligibility_chain") or {}).get("violations")) or [])


def sweep_topic(slug: str, config: dict[str, Any], protocol_text: str, review: dict[str, Any],
                records: dict[str, Any] | None = None) -> dict[str, Any]:
    records = records or {"records": []}
    shadow = apply_admissions(review, config, records, protocol_text)
    violations = shadow.get("eligibility_chain", {}).get("violations") or []
    pooled = sum(len(o.get("trials") or []) for o in shadow.get("outcomes") or [])
    excluded = sum(1 for r in (shadow.get("screening") or {}).get("records") or [] if r.get("decision") == "exclude")
    failing_rows = {
        (v.get("outcome"), v.get("trial_id") or v.get("trial"))
        for v in violations
        if v.get("code") == "TRIAL_FAILS_CONTRACT"
    }
    return {
        "slug": slug,
        "pooled_rows": pooled,
        "pooled_rows_failing_contract": len(failing_rows),
        "excluded_rows": excluded,
        "counts": dict(Counter(v.get("code") for v in violations)),
        "divergence_dimensions": dict(Counter(v.get("dimension") for v in violations
                                               if v.get("code") == "PROTOCOL_CONFIG_DIVERGENCE")),
        "violations": violations,
    }


def single_rationale_for_record(rec: dict[str, Any], config: dict[str, Any], protocol_text: str) -> dict[str, Any]:
    """Return the chain rationale a record would receive after vocabulary repair."""
    contract = compile_contract(config.get("slug", ""), config, protocol_text)
    trial = {"id": f"PMID {rec.get('id')}", "label": str(rec.get("id")), "source": rec.get("abstract", "")}
    adm = admission_record(trial, rec, {"name": "eligibility"}, contract)
    for dim, row in adm.items():
        if row.get("verdict") == "FAIL":
            return {"trial": rec.get("id"), "single_rationale": dim, "admission": row}
    inc = config.get("include") or {}
    decision = screen.screen_record(rec, inc, set())
    return {"trial": rec.get("id"), "single_rationale": decision[1], "screen_reason": decision[2]}
