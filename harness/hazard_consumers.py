"""Executable consumer links for structured limitation hazards.

Each limitation object gets either a consumer edge to the gate that reads the
hazard state, or an explicit UNWIRED marker with a reviewed acknowledgement.
The mapping is pair-level: (kind, evidence_state) -> gate function + object path.
"""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path
from typing import Any

from . import compat, design_key, estmeasure, invalidation


ROOT = Path(__file__).resolve().parents[1]
ACK_PATH = ROOT / "docs" / "hazard_acknowledgements.json"

PHASE_BASE = "base"
PHASE_FINAL = "final"
PHASE_LANE_AD = "lane_ad"

VALIDITY_THREATENING = "VALIDITY_THREATENING"
BLOCKING_SEVERITY = "BLOCKS_CLAIM"


def _spec(gate_id: str, gate_function: str, gate_input_path: str, runner: str,
          phase: str = PHASE_BASE) -> dict[str, str]:
    return {
        "gate_id": gate_id,
        "gate_function": gate_function,
        "gate_input_path": gate_input_path,
        "runner": runner,
        "phase": phase,
    }


WIRED_CONSUMERS: dict[tuple[str, str], dict[str, str]] = {
    # RESULT WITHDRAWN (2026-09-20): the executable consumer is the L1 primary-result check, which reads /withdrawn
    # and refuses a withdrawn page that still pools a row, lacks any required statement, or serves no notice; the
    # pipeline's unpooling reads the same field. A validity-threatening limitation with no consumer is visible state
    # that controls nothing -- the gate refused the first version of this notice for exactly that.
    ("RESULT_WITHDRAWN", "REFUSED_ON_EVIDENCE"): _spec(
        "gate.check_primary_result",
        "harness.gate.check_primary_result",
        "/withdrawn",
        "withdrawn",
    ),
    ("STALE_TOPIC", "STALE"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/invalidation/stale",
        "invalidation",
    ),
    ("CLAIM_CHECK_ZERO", "NOT_RUN"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/outcomes/*/result/claim",
        "invalidation",
    ),
    ("IDENTIFIER_SCOPE", "REFUSED_ON_EVIDENCE"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/identifier_scope",
        "invalidation",
    ),
    ("RETRACTED_TRIAL_POOLED", "RETRACTED"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/integrity/retracted",
        "invalidation",
    ),
    ("SUPPRESSED_POOL", "SUPPRESSED"): _spec(
        "estmeasure.pool_compatibility",
        "harness.estmeasure.pool_compatibility",
        "/outcomes/*/result/estmeasure/status",
        "estmeasure",
    ),
    ("UNIT_OF_ANALYSIS", "NOT_ASSESSED"): _spec(
        "design_key.decision_for_trial",
        "harness.design_key.decision_for_trial",
        "/unit_of_analysis",
        "design",
    ),
    ("UNIT_OF_ANALYSIS", "REFUSED_ON_EVIDENCE"): _spec(
        "design_key.decision_for_trial",
        "harness.design_key.decision_for_trial",
        "/outcomes/*/result/design_refusal",
        "design",
    ),
    ("UNIT_OF_ANALYSIS", "ENGINE_CANNOT_CONSUME"): _spec(
        "design_key.decision_for_trial",
        "harness.design_key.decision_for_trial",
        "/outcomes/*/result/design_refusal",
        "design",
    ),
    ("RANDOMISED_CONTRAST", "PARTIAL"): _spec(
        "compat.outcome_key",
        "harness.compat.outcome_key",
        "/arm_contrast/trials",
        "compat",
    ),
    ("RANDOMISED_CONTRAST", "RECORDED"): _spec(
        "compat.outcome_key",
        "harness.compat.outcome_key",
        "/arm_contrast/trials",
        "compat",
    ),
    ("HARMS_INCOMPLETE", "PARTIAL"): _spec(
        "compat_check.harms_incomplete",
        "harness.compat_check.enrich",
        "/harms/*/result/state",
        "compat_underlying",
    ),
    ("RETRIEVAL_CLASS", "NOT_RUN"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/search/retrieval_class/retrieval_auditable",
        "invalidation",
        PHASE_LANE_AD,
    ),
    ("RETRIEVAL_CLASS", "UNRECORDED"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/search/retrieval_class/retrieval_auditable",
        "invalidation",
        PHASE_LANE_AD,
    ),
    ("SEARCH_ENUMERATION_ONLY", "NOT_RUN"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/search/retrieval/enumeration_only",
        "invalidation",
        PHASE_LANE_AD,
    ),
    ("SEARCH_PROVENANCE", "RETRACTED"): _spec(
        "invalidation.assess",
        "harness.invalidation.assess",
        "/search/retrieval_class/search_provenance",
        "invalidation",
        PHASE_LANE_AD,
    ),
    ("ELIGIBILITY_CHAIN", "REFUSED_ON_EVIDENCE"): _spec(
        "gate.check_eligibility_chain",
        "harness.gate.check_eligibility_chain",
        "/eligibility_chain/violations",
        "eligibility_chain",
    ),
}


UNWIRED_REASONS: dict[tuple[str, str], str] = {
    ("AUDITABILITY_SCOPE", "RECORDED"): "auditability disclosure only; no analytic gate changes on this state",
    ("DECLARED_ABSENT_SECTION", "DECLARED_ABSENT"): "section/outcome absence is visible scoping evidence; no single analytic gate consumes all such sections",
    ("DECLARED_ABSENT_SECTION", "NOT_ASSESSED"): "absence caused by an empty assessment scope; no analytic gate consumes the section-level object",
    ("DECLARED_ABSENT_SECTION", "UNKNOWN"): "section/outcome absence is visible scoping evidence; no single analytic gate consumes all unknown absences",
    ("DECLARED_STRANDS", "REFUSED_ON_EVIDENCE"): "the suppressed-pool object carries the consuming estimand gate; strand disclosure is a decomposition label",
    ("DEFINITION_AUDIT", "PARTIAL"): "definition heterogeneity is disclosed as an audit table; no refusal gate consumes it yet",
    ("FUNDING_COI", "PARTIAL"): "funding and conflict-of-interest are disclosed but not adjusted by an analytic gate",
    ("FUNDING_COI", "RECORDED"): "funding and conflict-of-interest are disclosed but not adjusted by an analytic gate",
    ("GRADE_CERTAINTY", "NOT_ASSESSED"): "GRADE certainty is a downstream label; no publication gate consumes it",
    ("GRADE_CERTAINTY", "PROVISIONAL"): "GRADE certainty is a downstream label; no publication gate consumes it",
    ("REPRODUCTION_RETRACTION", "RETRACTED"): "the old byte-for-byte reproduction claim is withdrawn visibly; no current analytic gate consumes the withdrawn claim",
    ("RETRIEVAL_SNAPSHOT", "RECORDED"): "retrieval snapshot is replay provenance; it does not constrain an analytic claim by itself",
    ("RETRIEVAL_SNAPSHOT", "UNRECORDED"): "legacy retrieval snapshot is replay provenance; it does not constrain an analytic claim by itself",
    ("ROB_SENSITIVITY", "PARTIAL"): "risk-of-bias sensitivity is disclosed as an interpretation aid; no gate consumes the partial state",
    ("ROB_SPANCHECK", "RECORDED"): "span reliability is a disclosure metric; no analytic gate changes on this recorded state",
}


def pair_for(obj: dict[str, Any]) -> tuple[str, str]:
    return str(obj.get("kind") or ""), str(obj.get("evidence_state") or "")


def _spec_for(pair: tuple[str, str], phase: str = PHASE_FINAL) -> dict[str, str] | None:
    spec = WIRED_CONSUMERS.get(pair)
    if spec is None:
        return None
    if phase == PHASE_BASE and spec["phase"] == PHASE_LANE_AD:
        return None
    return spec


def wired_pairs(phase: str = PHASE_FINAL) -> dict[tuple[str, str], dict[str, str]]:
    return {pair: spec for pair, spec in WIRED_CONSUMERS.items() if _spec_for(pair, phase)}


def _reason_codes(verdict: dict[str, Any]) -> list[str]:
    codes: list[str] = []
    for item in verdict.get("reasons") or []:
        if isinstance(item, dict) and item.get("code"):
            code = str(item["code"])
            if code not in codes:
                codes.append(code)
    return codes


def _format_invalidation_verdict(verdict: dict[str, Any]) -> str:
    if not verdict.get("stale"):
        return "CURRENT"
    return "STALE: " + ", ".join(_reason_codes(verdict) or ["unnamed_reason"])


def _invalidation_verdict(review: dict[str, Any], *, allow_fresh: bool = True) -> str:
    if not allow_fresh:
        stored = review.get("invalidation") if isinstance(review.get("invalidation"), dict) else {}
        return _format_invalidation_verdict(stored)
    fresh = invalidation.assess(review)
    stored = review.get("invalidation") if isinstance(review.get("invalidation"), dict) else {}
    stale = bool(fresh.get("stale") or stored.get("stale"))
    codes: list[str] = []
    for code in _reason_codes(stored):
        if code not in codes:
            codes.append(code)
    for code in _reason_codes(fresh):
        if code not in codes:
            codes.append(code)
    return "STALE: " + ", ".join(codes or ["unnamed_reason"]) if stale else "CURRENT"


def _estmeasure_verdict(review: dict[str, Any]) -> str:
    statuses: list[str] = []
    for outcome in review.get("outcomes") or []:
        result = outcome.get("result") if isinstance(outcome, dict) else {}
        if not isinstance(result, dict):
            continue
        em = result.get("estmeasure") if isinstance(result.get("estmeasure"), dict) else {}
        if result.get("suppressed_incompatible") or em.get("status") == "incompatible":
            statuses.append(f"{outcome.get('name')}: {em.get('status') or 'suppressed'}")
    if statuses:
        return "SUPPRESSED: " + "; ".join(statuses)
    return "POOLABLE"


def _canon_id(value: Any) -> str:
    text = str(value or "")
    for prefix in ("PMID ", "PMID:", "NCT"):
        if text.upper().startswith(prefix.upper()):
            return text[len(prefix):].strip()
    return text.split()[-1].strip() if text.split() else text.strip()


def _find_trial(review: dict[str, Any], raw_id: Any) -> dict[str, Any] | None:
    want = _canon_id(raw_id)
    for outcome in review.get("outcomes") or []:
        for trial in outcome.get("trials") or []:
            if _canon_id(trial.get("id") or trial.get("label")) == want:
                return trial
    return None


def _design_from_uoa(item: dict[str, Any]) -> dict[str, Any]:
    design = str(item.get("design") or "").lower()
    if design == "factorial":
        key = ("FACTORIAL", "INDIVIDUAL", "reported")
    elif "cluster" in design and "crossover" in design:
        key = ("CLUSTER_CROSSOVER", "CLUSTER", "reconstructed")
    elif "cluster" in design:
        key = ("CLUSTER", "CLUSTER", "reconstructed")
    elif "crossover" in design:
        key = ("CROSSOVER", "UNKNOWN", "reconstructed")
    elif "stepped" in design:
        key = ("STEPPED_WEDGE", "CLUSTER", "reconstructed")
    else:
        key = ("UNKNOWN", "UNKNOWN", "reconstructed")
    design_key_value, unit, derivation = key
    return {
        "id": item.get("id"),
        "derivation": derivation,
        "effect": 1.0 if derivation == "reported" else None,
        "ai": 1 if derivation == "reconstructed" else None,
        "design": {
            "design": design_key_value,
            "unit_of_randomisation": unit,
            "correlation_handling": {"method": "none", "evidence": []},
        },
    }


def _design_action_summary(action: dict[str, Any]) -> str:
    return f"{action.get('action')}: {action.get('gate_id')} - {action.get('decision_state')}"


def _design_verdict(review: dict[str, Any], obj: dict[str, Any]) -> str:
    state = str(obj.get("evidence_state") or "")
    actions: list[str] = []
    if state in {"REFUSED_ON_EVIDENCE", "ENGINE_CANNOT_CONSUME"}:
        for outcome in review.get("outcomes") or []:
            result = outcome.get("result") if isinstance(outcome, dict) else {}
            if isinstance(result, dict) and result.get("design_refusal"):
                for item in result.get("refused") or outcome.get("design_refusals") or []:
                    if isinstance(item, dict):
                        actions.append("REFUSE: " + str(item.get("reason") or item.get("design") or "design_refusal"))
        return "; ".join(actions) if actions else "REFUSE: design_refusal"

    for item in review.get("unit_of_analysis") or []:
        if not isinstance(item, dict):
            continue
        trial = copy.deepcopy(_find_trial(review, item.get("id")) or _design_from_uoa(item))
        action = ((trial.get("design") or {}).get("design_action")
                  if isinstance(trial.get("design"), dict) else None)
        if not isinstance(action, dict):
            action = design_key.decision_for_trial(trial)
        actions.append(_design_action_summary(action))
    return "; ".join(actions) if actions else "NO_UNIT_OF_ANALYSIS_STATE"


def _compat_verdict(review: dict[str, Any]) -> str:
    bits: list[str] = []
    for outcome in review.get("outcomes") or []:
        if not isinstance(outcome, dict):
            continue
        key = compat.outcome_key(outcome, review)
        if not key:
            continue
        rc = key.get("randomised_contrast") or {}
        bits.append(f"{outcome.get('name')}: verified {rc.get('verified')}/{rc.get('total')}")
    return "; ".join(bits) if bits else "NO_POOLED_COMPAT_KEY"


def _compat_underlying_verdict(review: dict[str, Any]) -> str:
    names: list[str] = []
    outcomes = list(review.get("harms") or []) + list(review.get("outcomes") or [])
    for outcome in outcomes:
        result = outcome.get("result") if isinstance(outcome, dict) else {}
        if isinstance(result, dict) and result.get("state") == "HARMS_INCOMPLETE":
            names.append(str(outcome.get("name") or "unnamed harm"))
    return "HARMS_INCOMPLETE: " + "; ".join(names) if names else "NO_HARMS_INCOMPLETE"


def _eligibility_chain_verdict(review: dict[str, Any]) -> str:
    violations = ((review.get("eligibility_chain") or {}).get("violations")) or []
    hard = [v for v in violations if isinstance(v, dict)]
    return f"REFUSE: {len(hard)} eligibility-chain violation(s)" if hard else "PASS"


def _gate_verdict(review: dict[str, Any], obj: dict[str, Any], spec: dict[str, str],
                  phase: str = PHASE_FINAL) -> str:
    runner = spec["runner"]
    if runner == "invalidation":
        return _invalidation_verdict(review, allow_fresh=phase != PHASE_BASE)
    if runner == "estmeasure":
        return _estmeasure_verdict(review)
    if runner == "design":
        return _design_verdict(review, obj)
    if runner == "compat":
        return _compat_verdict(review)
    if runner == "compat_underlying":
        return _compat_underlying_verdict(review)
    if runner == "eligibility_chain":
        return _eligibility_chain_verdict(review)
    if runner == "withdrawn":
        return _withdrawn_verdict(review)
    return "UNKNOWN_RUNNER"


def _withdrawn_verdict(review: dict[str, Any]) -> str:
    """What the L1 primary-result check decides about a withdrawal, computed from the review object alone."""
    w = review.get("withdrawn")
    prim = next((o for o in review.get("outcomes", []) if o.get("primary")), None) or {}
    k = len(prim.get("trials") or []) or int((prim.get("result") or {}).get("k") or 0)
    if not w:
        return "PASS: no withdrawal declared"
    if k:
        return f"REFUSE: withdrawal contradicted -- primary still pools k={k}"
    missing = [key for key in ("date", "summary", "statements", "status") if not (isinstance(w, dict) and w.get(key))]
    if missing:
        return "REFUSE: withdrawal incomplete -- missing " + ", ".join(missing)
    return "REFUSE: primary pooled estimate withheld (result withdrawn; no number may be read as the result)"


def consumer_for(review: dict[str, Any], obj: dict[str, Any],
                 phase: str = PHASE_FINAL) -> dict[str, str] | None:
    spec = _spec_for(pair_for(obj), phase)
    if spec is None:
        return None
    return {
        "gate_id": spec["gate_id"],
        "gate_input_path": spec["gate_input_path"],
        "gate_verdict_at_build": _gate_verdict(review, obj, spec, phase),
    }


def load_acknowledgements(path: Path | None = None) -> dict[str, Any]:
    path = path or ACK_PATH
    if not path.exists():
        return {"acknowledgements": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"acknowledgements": []}
    if isinstance(data, dict):
        return data
    if isinstance(data, list):
        return {"acknowledgements": data}
    return {"acknowledgements": []}


def _ack_entries(acknowledgements: Any) -> list[dict[str, Any]]:
    if isinstance(acknowledgements, dict):
        raw = acknowledgements.get("acknowledgements")
    else:
        raw = acknowledgements
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _valid_ack(entry: dict[str, Any]) -> bool:
    if not _signed_ack(entry):
        return False
    if entry.get("limitation_id"):
        return True
    return bool(entry.get("kind") and entry.get("evidence_state"))


def _signed_ack(entry: dict[str, Any]) -> bool:
    return all(isinstance(entry.get(key), str) and entry.get(key).strip()
               for key in ("signed_by", "date", "reason", "tranche"))


def acknowledgement_for(obj: dict[str, Any], acknowledgements: Any = None) -> dict[str, str] | None:
    entries = _ack_entries(load_acknowledgements() if acknowledgements is None else acknowledgements)
    obj_pair = pair_for(obj)
    obj_id = obj.get("limitation_id")
    for entry in entries:
        if not _valid_ack(entry):
            continue
        if entry.get("limitation_id") == obj_id or (
            str(entry.get("kind")) == obj_pair[0]
            and str(entry.get("evidence_state")) == obj_pair[1]
        ):
            out = {
                "signed_by": str(entry["signed_by"]),
                "date": str(entry["date"]),
                "reason": str(entry["reason"]),
                "tranche": str(entry["tranche"]),
            }
            if entry.get("ack_id"):
                out["ack_id"] = str(entry["ack_id"])
            return out
    return None


def _embedded_ack(obj: dict[str, Any]) -> dict[str, str] | None:
    ack = obj.get("unwired_acknowledged")
    if isinstance(ack, dict) and _signed_ack(ack):
        return {
            "signed_by": str(ack["signed_by"]),
            "date": str(ack["date"]),
            "reason": str(ack["reason"]),
            "tranche": str(ack["tranche"]),
        }
    return None


def annotate_object(review: dict[str, Any], obj: dict[str, Any],
                    acknowledgements: Any = None, phase: str = PHASE_FINAL) -> dict[str, Any]:
    out = dict(obj)
    consumer = consumer_for(review, out, phase=phase)
    if consumer is not None:
        out["consumer"] = consumer
        out.pop("unwired", None)
        out.pop("unwired_reason", None)
        out.pop("unwired_acknowledged", None)
        return out

    out["consumer"] = None
    out["unwired"] = True
    reason = UNWIRED_REASONS.get(pair_for(out), "no executable consumer mapping changes on this limitation state")
    out["unwired_reason"] = reason
    ack = acknowledgement_for(out, acknowledgements)
    if ack:
        out["unwired_acknowledged"] = ack
    else:
        out.pop("unwired_acknowledged", None)
    return out


def annotate_limitations(review: dict[str, Any], limitations: list[dict[str, Any]],
                         acknowledgements: Any = None, phase: str = PHASE_FINAL) -> list[dict[str, Any]]:
    return [annotate_object(review, obj, acknowledgements, phase) for obj in limitations]


def _needs_consumer(obj: dict[str, Any]) -> bool:
    return (
        obj.get("limitation_class") == VALIDITY_THREATENING
        or obj.get("severity") == BLOCKING_SEVERITY
    )


def _consumer_ok(obj: dict[str, Any]) -> bool:
    consumer = obj.get("consumer")
    return isinstance(consumer, dict) and all(
        isinstance(consumer.get(key), str) and consumer.get(key).strip()
        for key in ("gate_id", "gate_input_path", "gate_verdict_at_build")
    )


def check_consumers(review: dict[str, Any], acknowledgements: Any = None) -> list[str]:
    ack_source = load_acknowledgements() if acknowledgements is None else acknowledgements
    reasons: list[str] = []
    for obj in review.get("limitations") or []:
        if not isinstance(obj, dict) or not _needs_consumer(obj):
            continue
        if _consumer_ok(obj):
            continue
        if acknowledgement_for(obj, ack_source) or _embedded_ack(obj):
            continue
        reasons.append(f"declared hazard with no consumer: {obj.get('limitation_id')}")
    return reasons


def _clean_core() -> dict[str, Any]:
    return {
        "outcomes": [
            {
                "name": "Primary",
                "primary": True,
                "result": {"k": 1, "estimate": 0.8, "ci_low": 0.6, "ci_high": 0.95, "scale": "RR"},
                "trials": [{"id": "PMID 111", "label": "111"}],
            }
        ],
        "screening": {"records": [{"id": "PMID 111", "decision": "include"}]},
        "search": {"source_status": {"PubMed": "RAN_OK"}},
    }


def _plant_core(pair: tuple[str, str]) -> dict[str, Any]:
    core = _clean_core()
    kind, _state = pair
    if kind == "CLAIM_CHECK_ZERO":
        core["outcomes"][0]["result"] = {"present": False, "reason": "plant"}
    elif kind == "IDENTIFIER_SCOPE":
        core["identifier_scope"] = {
            "verdict": "SINGLE_AGENT_OVER_CLASS_POOL",
            "reason": {"code": "identifier_single_agent_class_pool", "detail": "plant"},
        }
    elif kind in {"STALE_TOPIC", "RETRACTED_TRIAL_POOLED"}:
        core["integrity"] = {"retracted": ["111"], "concern": []}
    elif kind == "RESULT_WITHDRAWN":
        # the planted hazard: a declared withdrawal beside a still-pooled row -- the consumer must refuse it
        core["withdrawn"] = {"date": "plant", "summary": "plant", "statements": ["what was published", "what the held evidence holds", "why", "not yet published"], "status": "plant"}
    elif kind == "RETRIEVAL_CLASS":
        core["search"]["retrieval_class"] = {
            "class": "KNOWN_ITEM_RETRIEVAL",
            "label": "known item",
            "retrieval_auditable": False,
            "distinction": "known-item retrieval cannot discover unknown eligible trials",
        }
    elif kind == "SEARCH_ENUMERATION_ONLY":
        core["search"]["retrieval"] = {"enumeration_only": True}
    elif kind == "SEARCH_PROVENANCE":
        core["search"]["retrieval_class"] = {
            "class": "TITLE_SEEDED_RETRIEVAL",
            "label": "title seeded",
            "retrieval_auditable": False,
            "search_provenance": {"retraction": "not a completed systematic search"},
        }
    elif kind == "HARMS_INCOMPLETE":
        core["harms"] = [{
            "name": "Plant harm",
            "result": {
                "present": False,
                "state": "HARMS_INCOMPLETE",
                "reason": "plant",
                "known_eligible_outcome_reports_unresolved": [{"trial_id": "111"}],
            },
        }]
    return core


def _plant_estmeasure(pair: tuple[str, str], planted: bool) -> str:
    effects = (
        [
            {"reported_label": "HR", "canonical_estimand": "HAZARD_RATIO_FIRST_EVENT"},
            {"reported_label": "IRR", "canonical_estimand": "INCIDENCE_RATE_RATIO"},
        ]
        if planted
        else [
            {"reported_label": "HR", "canonical_estimand": "HAZARD_RATIO_FIRST_EVENT"},
            {"reported_label": "RR", "canonical_estimand": "RISK_RATIO"},
        ]
    )
    return str(estmeasure.pool_compatibility(effects).get("status"))


def _plant_design(pair: tuple[str, str], planted: bool) -> str:
    if not planted:
        trial = {
            "id": "PMID 111",
            "derivation": "reconstructed",
            "ai": 1,
            "design": {
                "design": "PARALLEL",
                "unit_of_randomisation": "INDIVIDUAL",
                "correlation_handling": {"method": "none", "evidence": []},
            },
        }
    elif pair[1] in {"REFUSED_ON_EVIDENCE", "ENGINE_CANNOT_CONSUME"}:
        trial = {
            "id": "PMID 111",
            "derivation": "reconstructed",
            "ai": 1,
            "design": {
                "design": "CLUSTER_CROSSOVER",
                "unit_of_randomisation": "CLUSTER",
                "correlation_handling": {"method": "none", "evidence": []},
            },
        }
    else:
        trial = {
            "id": "PMID 111",
            "derivation": "reported",
            "effect": 0.9,
            "design": {
                "design": "FACTORIAL",
                "unit_of_randomisation": "INDIVIDUAL",
                "correlation_handling": {"method": "published_model", "evidence": [{"span": "adjusted"}]},
            },
        }
    return _design_action_summary(design_key.decision_for_trial(trial))


def _plant_compat(pair: tuple[str, str], planted: bool) -> str:
    core = _clean_core()
    core["outcomes"][0]["trials"] = [{"id": "PMID 111", "label": "111"}]
    if planted and pair[1] == "RECORDED":
        core["arm_contrast"] = {"trials": {"111": {"status": "verified"}}}
    elif planted:
        core["arm_contrast"] = {"trials": {"111": {"status": "unverified_no_arm_data"}}}
    else:
        core["arm_contrast"] = {"trials": {"111": {"status": "verified"}} if pair[1] == "PARTIAL" else {}}
    key = compat.outcome_key(core["outcomes"][0], core) or {}
    rc = key.get("randomised_contrast") or {}
    return f"verified {rc.get('verified')}/{rc.get('total')}"


def _plant_eligibility_chain(pair: tuple[str, str], planted: bool) -> str:
    core = _clean_core()
    if planted:
        core["eligibility_chain"] = {
            "violations": [{"code": "TRIAL_FAILS_CONTRACT", "dimension": "design_masking"}]
        }
    return _eligibility_chain_verdict(core)


def _plant_verdict(pair: tuple[str, str], spec: dict[str, str], planted: bool) -> str:
    runner = spec["runner"]
    if runner == "invalidation":
        core = _plant_core(pair) if planted else _clean_core()
        return _invalidation_verdict(core)
    if runner == "estmeasure":
        return _plant_estmeasure(pair, planted)
    if runner == "design":
        return _plant_design(pair, planted)
    if runner == "compat":
        return _plant_compat(pair, planted)
    if runner == "compat_underlying":
        return _compat_underlying_verdict(_plant_core(pair) if planted else _clean_core())
    if runner == "eligibility_chain":
        return _plant_eligibility_chain(pair, planted)
    if runner == "withdrawn":
        return _withdrawn_verdict(_plant_core(pair) if planted else _clean_core())
    return "UNKNOWN_RUNNER"


def plant_results(phase: str = PHASE_FINAL) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for pair, spec in sorted(wired_pairs(phase).items()):
        baseline = _plant_verdict(pair, spec, False)
        planted = _plant_verdict(pair, spec, True)
        rows.append({
            "kind": pair[0],
            "evidence_state": pair[1],
            "gate_id": spec["gate_id"],
            "gate_function": spec["gate_function"],
            "gate_input_path": spec["gate_input_path"],
            "baseline_verdict": baseline,
            "planted_verdict": planted,
            "changed": baseline != planted,
        })
    return rows


def review_paths_at_ref(ref: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "--", "docs/reviews"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return []
    return sorted(line.strip() for line in proc.stdout.splitlines() if line.strip().endswith("/review.json"))


def load_review_at_ref(ref: str, rel: str) -> dict[str, Any] | None:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{rel}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
