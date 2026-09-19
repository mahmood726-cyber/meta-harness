"""Object-backed proposition assertions for non-numeric page sentences.

The canonical claim graph handles stale result-bearing objects and significance
wording. This module covers assertion-only sentences that are still checkable:
publication-bias state, protocol/config equality, protocol-SHA byte replay,
membership/count wording, search-found wording, and state-label collapses.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from collections import Counter
from typing import Any

from . import claimgraph


SCOPE_KINDS = (
    "publication_bias_state",
    "declared_equals_enforced",
    "byte_reproducible",
    "pooled_count",
    "rated_count",
    "retracted_count",
    "search_found",
    "state_collapsed",
)

_PMID_RE = re.compile(r"\b(?:PMID[:\s]*)?(\d{7,9})\b", re.I)
_NCT_RE = re.compile(r"\bNCT\d{8}\b", re.I)
_COLLAPSED_WORDS = {"unknown", "absent", "none", "not stated", "no harms recorded"}
_SEARCH_ALIAS_PMIDS = {
    "original copps": "22090167",
    "copps trial": "22090167",
}


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _claim_id(kind: str, surface: str, source_path: str) -> str:
    raw = f"{kind}|{surface}|{source_path}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _violation(code: str, kind: str, obj: dict[str, Any], detail: str, **extra: Any) -> dict[str, Any]:
    return {
        "code": code,
        "kind": kind,
        "claim_id": obj.get("claim_id") or _claim_id(kind, obj.get("surface") or "", obj.get("source_path") or ""),
        "detail": detail,
        "surface": obj.get("surface"),
        **extra,
    }


def _norm_id(value: Any) -> str:
    text = str(value or "").strip()
    if "·" in text:
        text = text.split("·")[-1].strip()
    text = text.replace("PMID ", "").replace("PMID:", "").strip()
    if _NCT_RE.fullmatch(text):
        return text.upper()
    return text.split()[-1].strip() if text.split() else text


def _primary(review: dict[str, Any]) -> dict[str, Any] | None:
    outs = review.get("outcomes") or []
    return next((o for o in outs if o.get("primary")), (outs[0] if outs else None))


def _primary_effect_count(review: dict[str, Any]) -> int | None:
    primary = _primary(review)
    if not primary:
        return None
    res = primary.get("result") or {}
    if isinstance(res.get("k"), int):
        return res["k"]
    if primary.get("trials"):
        return len(primary.get("trials") or [])
    return None


def _screened_in_ids(review: dict[str, Any]) -> set[str]:
    out: set[str] = set()
    for rec in (review.get("screening") or {}).get("records") or []:
        if rec.get("decision") == "include":
            rid = _norm_id(rec.get("id"))
            if rid:
                out.add(rid)
    return out


def _funding_spans_by_id(review: dict[str, Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    for row in review.get("funding") or []:
        if not isinstance(row, dict):
            continue
        rid = _norm_id(row.get("id"))
        if rid:
            out[rid] = " ".join(str(row.get(k) or "") for k in ("span", "source"))
    return out


def _primary_randomisation_count(review: dict[str, Any]) -> int | None:
    primary = _primary(review)
    if not primary:
        return None
    funding = _funding_spans_by_id(review)
    prospective = (review.get("integrity") or {}).get("prospective") or {}
    total = 0
    seen_any = False
    for trial in primary.get("trials") or []:
        key = _norm_id(trial.get("id") or trial.get("label"))
        text = " ".join(str(trial.get(k) or "") for k in ("source", "verify_basis", "provenance"))
        text += " " + funding.get(key, "")
        if isinstance(prospective.get(key), dict):
            text += " " + str(prospective[key].get("nct") or "")
        ncts = set(_NCT_RE.findall(text))
        total += max(1, len(ncts))
        seen_any = True
    return total if seen_any else None


def _publication_bias_state(review: dict[str, Any]) -> dict[str, Any] | None:
    pub = ((review.get("grade") or {}).get("domains") or {}).get("publication_bias")
    if not isinstance(pub, dict):
        return None
    assessed = bool(pub.get("assessed"))
    return {
        "assessed": assessed,
        "state": "ASSESSED" if assessed else "NOT_ASSESSED",
        "basis": pub.get("basis"),
        "not_assessable": bool(pub.get("not_assessable")),
    }


def _derived_protocol_divergences(review: dict[str, Any]) -> list[dict[str, Any]]:
    protocol = review.get("protocol") or {}
    text = str(protocol.get("text") or "").lower()
    eligibility = str(protocol.get("eligibility") or "").lower()
    out: list[dict[str, Any]] = []

    if (
        ("double-blind, placebo-controlled" in text or "not double-blind and placebo-controlled" in text
         or "double-blind and placebo-controlled" in text)
        and "double-blind or placebo-controlled" in eligibility
    ):
        out.append({
            "code": "DESIGN_MASKING_ANDOR",
            "dimension": "design",
            "prose": "double-blind AND placebo-controlled",
            "config": "double-blind OR placebo-controlled",
        })
    if "broad cardiovascular outcome trial" in text and "broad cardiovascular outcome" not in eligibility:
        out.append({
            "code": "POPULATION_SCOPE_DIVERGENCE",
            "dimension": "population",
            "prose": "broad cardiovascular outcome trials",
            "config": protocol.get("eligibility"),
        })
    needs_ovulation_context = (
        "ovulation-induction/subfertility context" in text
        or "undergoing ovulation induction" in text
        or "subfertility context" in text
    )
    if needs_ovulation_context and not any(x in eligibility for x in ("ovulation", "subfertility")):
        out.append({
            "code": "POPULATION_CONTEXT_DIVERGENCE",
            "dimension": "population",
            "prose": "PCOS in an ovulation-induction/subfertility context",
            "config": protocol.get("eligibility"),
        })
    return out


def protocol_divergences(review: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in ((review.get("protocol_config") or {}).get("divergences") or []) + _derived_protocol_divergences(review):
        if not isinstance(row, dict):
            continue
        key = (str(row.get("code") or ""), str(row.get("dimension") or ""))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _byte_state(review: dict[str, Any]) -> dict[str, Any]:
    rep = review.get("reproduction") or {}
    return {
        "protocol_sha_byte_reproducible": bool(rep.get("byte_reproducible_from_protocol_sha")),
        "committed_cache_replay": bool(rep.get("from_cache")) if rep else None,
    }


def _facts(review: dict[str, Any]) -> dict[str, Any]:
    parity = (review.get("reproduction") or {}).get("parity") or {}
    integrity = review.get("integrity") or {}
    sens = review.get("rob_sensitivity") or {}
    primary_effect_count = _primary_effect_count(review)
    randomisation_count = _primary_randomisation_count(review)
    return {
        "publication_bias": _publication_bias_state(review),
        "protocol_divergences": protocol_divergences(review),
        "byte_reproducible": _byte_state(review),
        "primary_effect_objects": primary_effect_count,
        "primary_randomisations": randomisation_count if randomisation_count is not None else primary_effect_count,
        "parity_our_k": parity.get("our_k") if isinstance(parity.get("our_k"), int) else primary_effect_count,
        "rob_rated": sens.get("n_rob_rated"),
        "rob_total": sens.get("n_trials"),
        "integrity_pooled": integrity.get("n_pooled"),
        "integrity_retracted": len(integrity.get("retracted") or []),
        "screened_in": _screened_in_ids(review),
    }


def _prop(kind: str, surface: str, source_path: str, **fields: Any) -> dict[str, Any]:
    obj = {"kind": kind, "surface": surface, "source_path": source_path, **fields}
    obj["claim_id"] = _claim_id(kind, surface, source_path)
    return obj


def generated_objects(review: dict[str, Any]) -> list[dict[str, Any]]:
    facts = _facts(review)
    out: list[dict[str, Any]] = []
    pub = facts["publication_bias"]
    if pub is not None:
        out.append(_prop(
            "publication_bias_state",
            "grade/manuscript/reporting",
            "/grade/domains/publication_bias",
            assessed=pub["assessed"],
            state=pub["state"],
        ))

    if (review.get("protocol") or {}).get("eligibility") is not None:
        divergences = facts["protocol_divergences"]
        out.append(_prop(
            "declared_equals_enforced",
            "reporting/prisma_item_5",
            "/protocol_config/divergences",
            asserted_equal=(len(divergences) == 0),
            divergence_count=len(divergences),
            divergence_codes=[d.get("code") for d in divergences],
        ))

    if (review.get("protocol") or {}).get("sha") or ((review.get("search") or {}).get("retrieval") or {}).get("snapshot"):
        out.append(_prop(
            "byte_reproducible",
            "search/reporting/reproduction/manuscript",
            "/reproduction",
            asserts_protocol_sha_replay=False,
            asserts_committed_cache_replay=True,
        ))

    if facts["primary_effect_objects"] is not None:
        out.append(_prop(
            "pooled_count",
            "overview/results/manuscript",
            "/outcomes/*[primary]/result/k",
            subject="primary_effect_objects",
            count=facts["primary_effect_objects"],
        ))
    if (
        facts["primary_randomisations"] is not None
        and facts["primary_effect_objects"] is not None
        and facts["primary_randomisations"] != facts["primary_effect_objects"]
    ):
        out.append(_prop(
            "pooled_count",
            "overview/randomisation-disclosure",
            "/outcomes/*[primary]/trials",
            subject="primary_randomisations",
            count=facts["primary_randomisations"],
        ))

    if facts["rob_rated"] is not None or facts["rob_total"] is not None:
        out.append(_prop(
            "rated_count",
            "riskofbias/manuscript",
            "/rob_sensitivity",
            rated=facts["rob_rated"],
            total=facts["rob_total"],
        ))

    if review.get("integrity"):
        out.append(_prop(
            "retracted_count",
            "riskofbias/integrity",
            "/integrity",
            pooled=facts["integrity_pooled"],
            retracted=facts["integrity_retracted"],
        ))

    for obj in _search_found_sentence_objects(review):
        out.append(obj)
    return out


def protocol_compliance_state(r: dict[str, Any]) -> dict[str, Any]:
    """Declared-versus-enforced compliance, derived from the protocol_config object and nothing else.
    ESTABLISHED only when at least one dimension was actually compared and none diverged; DISCLOSED_DIVERGENCE when
    the comparison found divergences; NOT_ESTABLISHED when no dimension was checked -- an empty divergence list is
    not evidence of compliance (the served glp1 page said "agree on these checked dimensions: none" and then
    "declared == enforced is backed"; Mahmood's review of 98726cc1, item 1: absence producing assurance)."""
    pc = r.get("protocol_config") or {}
    divergences = [d for d in (pc.get("divergences") or []) if isinstance(d, dict)]
    agreed = [str(x) for x in (pc.get("agreed_dimensions") or []) if x]
    if divergences:
        state = "DISCLOSED_DIVERGENCE"
    elif agreed:
        state = "ESTABLISHED"
    else:
        state = "NOT_ESTABLISHED"
    return {"state": state, "agreed_dimensions": agreed, "divergences": divergences,
            "sentence": {
                "ESTABLISHED": "declared == enforced on the checked dimensions (" + ", ".join(agreed) + ")",
                "DISCLOSED_DIVERGENCE": f"{len(divergences)} protocol/config divergence(s) disclosed; declared == enforced is not asserted",
                "NOT_ESTABLISHED": "NOT ESTABLISHED: no protocol/config dimension was checked, so declared == enforced is not asserted",
            }[state]}


def attach(review: dict[str, Any]) -> dict[str, Any]:
    review = copy.deepcopy(review)
    pc = dict(review.get("protocol_config") or {})
    pc["compliance"] = protocol_compliance_state(review)
    review["protocol_config"] = pc
    if isinstance(review.get("rob2"), dict) and review["rob2"].get("trials"):
        from . import rob2 as _rob2
        review["rob2"] = dict(review["rob2"], canonical=_rob2.canonical(review["rob2"]))
    review["propositions"] = {
        "version": 1,
        "objects": generated_objects(review),
        "scope_counts": scope_counts(review),
        "not_in_scope": [
            "verbatim source quotations",
            "external comparator prose without a committed object row",
        ],
    }
    return review


def scope_counts(review: dict[str, Any]) -> dict[str, int]:
    objects = ((review.get("propositions") or {}).get("objects") or generated_objects(review))
    counts = Counter(str(o.get("kind")) for o in objects)
    return {kind: int(counts.get(kind, 0)) for kind in SCOPE_KINDS}


def scope_summary(scope: dict[str, Any] | None) -> str:
    scope = scope or {}
    counts = scope.get("scope_counts") or scope.get("counts") or {}
    checked = ", ".join(f"{kind}={int(counts.get(kind, 0))}" for kind in SCOPE_KINDS)
    not_scope = ", ".join(scope.get("not_in_scope") or []) or "none"
    return f"{checked}; not in scope: {not_scope}"


def _required_kinds(review: dict[str, Any]) -> set[str]:
    facts = _facts(review)
    required: set[str] = set()
    if facts["publication_bias"] is not None:
        required.add("publication_bias_state")
    if (review.get("protocol") or {}).get("eligibility") is not None:
        required.add("declared_equals_enforced")
    if (review.get("protocol") or {}).get("sha") or ((review.get("search") or {}).get("retrieval") or {}).get("snapshot"):
        required.add("byte_reproducible")
    if facts["primary_effect_objects"] is not None:
        required.add("pooled_count")
    if facts["rob_rated"] is not None or facts["rob_total"] is not None:
        required.add("rated_count")
    if review.get("integrity"):
        required.add("retracted_count")
    if _search_found_sentence_objects(review):
        required.add("search_found")
    return required


def _legacy_objects(review: dict[str, Any]) -> list[dict[str, Any]]:
    facts = _facts(review)
    out: list[dict[str, Any]] = []
    if facts["publication_bias"] is not None:
        for surface in ("riskofbias_grade_narrative", "manuscript_abstract", "reporting_item_15"):
            out.append(_prop(
                "publication_bias_state",
                surface,
                "/grade/domains/publication_bias",
                assessed=True,
            ))
    if (review.get("protocol") or {}).get("eligibility") is not None:
        out.append(_prop(
            "declared_equals_enforced",
            "reporting/prisma_item_5",
            "/protocol_config/divergences",
            asserted_equal=True,
        ))
    if (review.get("protocol") or {}).get("sha") or ((review.get("search") or {}).get("retrieval") or {}).get("snapshot"):
        for surface in ("search/retrieval_snapshot", "reporting/prisma_item_24", "manuscript_methods"):
            out.append(_prop(
                "byte_reproducible",
                surface,
                "/reproduction",
                asserts_protocol_sha_replay=True,
            ))
    if (
        facts["primary_effect_objects"] is not None
        and facts["primary_randomisations"] is not None
        and facts["primary_effect_objects"] != facts["primary_randomisations"]
    ):
        out.append(_prop(
            "pooled_count",
            "overview/results_k_trials",
            "/outcomes/*[primary]/result/k",
            subject="primary_randomisations",
            count=facts["primary_effect_objects"],
        ))

    parity = (review.get("reproduction") or {}).get("parity") or {}
    reason = str(parity.get("reason") or "")
    m = re.search(r"\bwe pool\s+(\d+)\b", reason, re.I)
    if m:
        out.append(_prop(
            "pooled_count",
            "reproduction/parity_reason",
            "/reproduction/parity/reason",
            subject="parity_our_k",
            count=int(m.group(1)),
        ))
    out.extend(_search_found_sentence_objects(review))
    out.extend(_state_sentence_objects(review))
    return out


def _search_found_sentence_objects(review: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    text = str(review.get("evidence_base_caveat") or "")
    if re.search(r"\bnever\s+(?:searched\s+for|found)\b", text, re.I):
        lower = text.lower()
        seen: set[str] = set()
        for alias, pmid in _SEARCH_ALIAS_PMIDS.items():
            if pmid in seen:
                continue
            if alias in lower:
                seen.add(pmid)
                out.append(_prop(
                    "search_found",
                    "overview/evidence_base_caveat",
                    "/evidence_base_caveat",
                    pmid=pmid,
                    found=False,
                    alias=alias,
                ))
    return out


def _state_sentence_objects(review: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for obj in ((review.get("propositions") or {}).get("objects") or []):
        if obj.get("kind") == "state_collapsed":
            out.append(obj)
    return out


def _check_object(obj: dict[str, Any], facts: dict[str, Any]) -> list[dict[str, Any]]:
    kind = obj.get("kind")
    out: list[dict[str, Any]] = []
    if kind == "publication_bias_state":
        pub = facts["publication_bias"]
        if pub is not None and bool(obj.get("assessed")) != bool(pub["assessed"]):
            out.append(_violation(
                "PUBLICATION_BIAS_STATE",
                kind,
                obj,
                f"sentence asserts publication_bias.assessed={bool(obj.get('assessed'))}, "
                f"but grade object records assessed={bool(pub['assessed'])} ({pub['state']})",
                asserted_assessed=bool(obj.get("assessed")),
                actual_assessed=bool(pub["assessed"]),
            ))
    elif kind == "declared_equals_enforced":
        divergences = facts["protocol_divergences"]
        if obj.get("asserted_equal") is True and divergences:
            out.append(_violation(
                "DECLARED_ENFORCED_FALSE",
                kind,
                obj,
                "sentence asserts declared == enforced while protocol/config divergences exist",
                divergence_codes=[d.get("code") for d in divergences],
            ))
    elif kind == "byte_reproducible":
        byte = facts["byte_reproducible"]
        if obj.get("asserts_protocol_sha_replay") is True and not byte["protocol_sha_byte_reproducible"]:
            out.append(_violation(
                "BYTE_REPRODUCIBLE_FALSE",
                kind,
                obj,
                "sentence asserts protocol-SHA byte replay, but the object does not support that claim",
            ))
    elif kind == "pooled_count":
        subject = obj.get("subject")
        actual = facts.get(str(subject))
        if isinstance(actual, int) and isinstance(obj.get("count"), int) and obj.get("count") != actual:
            out.append(_violation(
                "POOLED_COUNT_MISMATCH",
                kind,
                obj,
                f"sentence asserts {subject}={obj.get('count')}, but object-derived value is {actual}",
                subject=subject,
                asserted=obj.get("count"),
                actual=actual,
            ))
    elif kind == "rated_count":
        if obj.get("rated") != facts["rob_rated"] or obj.get("total") != facts["rob_total"]:
            out.append(_violation(
                "RATED_COUNT_MISMATCH",
                kind,
                obj,
                f"sentence asserts rated/total={obj.get('rated')}/{obj.get('total')}, "
                f"but rob_sensitivity records {facts['rob_rated']}/{facts['rob_total']}",
            ))
    elif kind == "retracted_count":
        if obj.get("pooled") != facts["integrity_pooled"] or obj.get("retracted") != facts["integrity_retracted"]:
            out.append(_violation(
                "RETRACTED_COUNT_MISMATCH",
                kind,
                obj,
                f"sentence asserts pooled/retracted={obj.get('pooled')}/{obj.get('retracted')}, "
                f"but integrity records {facts['integrity_pooled']}/{facts['integrity_retracted']}",
            ))
    elif kind == "search_found":
        pmid = str(obj.get("pmid") or "")
        actual = pmid in facts["screened_in"]
        if obj.get("found") is not None and bool(obj.get("found")) != actual:
            out.append(_violation(
                "SEARCH_FOUND_CONTRADICTION",
                kind,
                obj,
                f"sentence asserts PMID {pmid} found={bool(obj.get('found'))}, but screening records found={actual}",
                pmid=pmid,
                asserted_found=bool(obj.get("found")),
                actual_found=actual,
            ))
    elif kind == "state_collapsed":
        source_state = str(obj.get("source_state") or "")
        rendered_state = str(obj.get("rendered_state") or "").lower()
        if source_state == "SOURCE_NOT_RETRIEVED" and rendered_state in _COLLAPSED_WORDS:
            out.append(_violation(
                "STATE_COLLAPSED",
                kind,
                obj,
                f"sentence maps SOURCE_NOT_RETRIEVED to {obj.get('rendered_state')!r}",
                source_state=source_state,
                rendered_state=obj.get("rendered_state"),
            ))
    return out


def check_propositions(review: dict[str, Any], registries: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    facts = _facts(review)
    explicit = bool((review.get("propositions") or {}).get("objects"))
    objects = (review.get("propositions") or {}).get("objects") if explicit else _legacy_objects(review)
    violations: list[dict[str, Any]] = []

    if explicit:
        present = {str(o.get("kind")) for o in objects}
        for kind in sorted(_required_kinds(review) - present):
            obj = _prop(kind, "rendered_surface", "/propositions/objects")
            violations.append(_violation(
                "UNBACKED_ASSERTION",
                kind,
                obj,
                f"review renders a {kind} proposition family without a backing proposition object",
            ))

    for obj in objects or []:
        if isinstance(obj, dict):
            violations.extend(_check_object(obj, facts))

    cg_violations = [
        v for v in claimgraph.check(review, registries)
        if v.get("code") == "REFUSED_AND_POOLED"
    ]
    for v in cg_violations:
        obj = _prop("pooled_count", "refusal_registry", "/reproduction/refusals")
        violations.append(_violation(
            "REFUSED_AND_POOLED",
            "pooled_count",
            obj,
            v.get("detail") or "refusal registry names a pooled trial",
            trial_keys=v.get("trial_keys"),
        ))
    return violations


def check_document(review: dict[str, Any]) -> dict[str, Any]:
    violations = check_propositions(review)
    return {
        "checked": True,
        "scope_counts": scope_counts(review),
        "scope": {
            "scope_counts": scope_counts(review),
            "not_in_scope": (review.get("propositions") or {}).get("not_in_scope") or [],
        },
        "contradictions": violations,
    }
