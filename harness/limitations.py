"""Structured limitation objects for the legacy absent/banner surface.

Auditor defect class recorded verbatim: DIAGNOSTIC–DECISION DECOUPLING — a
validity hazard is correctly detected and represented, but its state is not
causally connected to the analytic decision it should constrain. Plain alias:
disclosure-as-control. Class PROCESS, direction optimistic, severity
major-to-critical.

This module is intentionally additive: page.py still renders the served page.
The builder mirrors that legacy surface from the review object so tests can
prove every visible absent/banner block has a structured object before a later
lane switches rendering authority.
"""
from __future__ import annotations

import hashlib
import json
import re
from enum import Enum
from typing import Any

from . import claimgraph
from . import hazard_consumers as _hazard_consumers
from . import page as _page
from . import rob_sensitivity as _rob_sensitivity_mod
from . import funding as _funding_mod


class LimitationKind(str, Enum):
    DECLARED_ABSENT_SECTION = "DECLARED_ABSENT_SECTION"
    RETRIEVAL_SNAPSHOT = "RETRIEVAL_SNAPSHOT"
    SEARCH_ENUMERATION_ONLY = "SEARCH_ENUMERATION_ONLY"
    RETRIEVAL_CLASS = "RETRIEVAL_CLASS"
    DECLARED_STRANDS = "DECLARED_STRANDS"
    STALE_TOPIC = "STALE_TOPIC"
    AUDITABILITY_SCOPE = "AUDITABILITY_SCOPE"
    SUPPRESSED_POOL = "SUPPRESSED_POOL"
    RETRACTED_TRIAL_POOLED = "RETRACTED_TRIAL_POOLED"
    DEFINITION_AUDIT = "DEFINITION_AUDIT"
    CLAIM_CHECK_ZERO = "CLAIM_CHECK_ZERO"
    REPRODUCTION_RETRACTION = "REPRODUCTION_RETRACTION"
    IDENTIFIER_SCOPE = "IDENTIFIER_SCOPE"
    UNIT_OF_ANALYSIS = "UNIT_OF_ANALYSIS"
    FUNDING_COI = "FUNDING_COI"
    RANDOMISED_CONTRAST = "RANDOMISED_CONTRAST"
    ROB_SENSITIVITY = "ROB_SENSITIVITY"
    GRADE_CERTAINTY = "GRADE_CERTAINTY"
    HARMS_INCOMPLETE = "HARMS_INCOMPLETE"
    ROB_SPANCHECK = "ROB_SPANCHECK"
    SEARCH_PROVENANCE = "SEARCH_PROVENANCE"
    ELIGIBILITY_CHAIN = "ELIGIBILITY_CHAIN"


class Severity(str, Enum):
    BLOCKS_CLAIM = "BLOCKS_CLAIM"
    QUALIFIES_CLAIM = "QUALIFIES_CLAIM"
    NOTE = "NOTE"


class EvidenceState(str, Enum):
    DECLARED_ABSENT = "DECLARED_ABSENT"
    NOT_ASSESSED = "NOT_ASSESSED"
    SUPPRESSED = "SUPPRESSED"
    STALE = "STALE"
    UNRECORDED = "UNRECORDED"
    RETRACTED = "RETRACTED"
    RAN_ERROR = "RAN_ERROR"
    NOT_RUN = "NOT_RUN"
    SOURCE_NOT_RETRIEVED = "SOURCE_NOT_RETRIEVED"
    EXTRACTION_NOT_PERFORMED = "EXTRACTION_NOT_PERFORMED"
    REFUSED_ON_EVIDENCE = "REFUSED_ON_EVIDENCE"
    ENGINE_CANNOT_CONSUME = "ENGINE_CANNOT_CONSUME"
    PROVISIONAL = "PROVISIONAL"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    RECORDED = "RECORDED"


class LimitationClass(str, Enum):
    INFORMATIONAL = "INFORMATIONAL"
    VALIDITY_THREATENING = "VALIDITY_THREATENING"


SEVERITY_ORDER = (
    Severity.BLOCKS_CLAIM.value,
    Severity.QUALIFIES_CLAIM.value,
    Severity.NOTE.value,
)

EVIDENCE_STATE_ORDER = (
    EvidenceState.DECLARED_ABSENT.value,
    EvidenceState.NOT_ASSESSED.value,
    EvidenceState.SUPPRESSED.value,
    EvidenceState.STALE.value,
    EvidenceState.UNRECORDED.value,
    EvidenceState.RETRACTED.value,
    EvidenceState.RAN_ERROR.value,
    EvidenceState.NOT_RUN.value,
    EvidenceState.SOURCE_NOT_RETRIEVED.value,
    EvidenceState.EXTRACTION_NOT_PERFORMED.value,
    EvidenceState.REFUSED_ON_EVIDENCE.value,
    EvidenceState.ENGINE_CANNOT_CONSUME.value,
    EvidenceState.PROVISIONAL.value,
    EvidenceState.PARTIAL.value,
    EvidenceState.UNKNOWN.value,
    EvidenceState.RECORDED.value,
)

_SEVERITY_RANK = {value: idx for idx, value in enumerate(SEVERITY_ORDER)}
_EVIDENCE_RANK = {value: idx for idx, value in enumerate(EVIDENCE_STATE_ORDER)}
_SOURCE_ABSENCE_STATES = {
    "NO_OUTCOME_DATA_IN_SOURCE": EvidenceState.DECLARED_ABSENT.value,
    "EXTRACTION_NOT_PERFORMED": EvidenceState.EXTRACTION_NOT_PERFORMED.value,
    "SOURCE_NOT_RETRIEVED": EvidenceState.SOURCE_NOT_RETRIEVED.value,
    "REFUSED_ON_EVIDENCE": EvidenceState.REFUSED_ON_EVIDENCE.value,
    "ENGINE_CANNOT_CONSUME": EvidenceState.ENGINE_CANNOT_CONSUME.value,
}
_VALIDITY_THREATENING_KINDS = {
    LimitationKind.UNIT_OF_ANALYSIS.value,
    LimitationKind.SUPPRESSED_POOL.value,
    LimitationKind.RETRACTED_TRIAL_POOLED.value,
    LimitationKind.STALE_TOPIC.value,
    LimitationKind.HARMS_INCOMPLETE.value,
    LimitationKind.SEARCH_PROVENANCE.value,
    LimitationKind.RETRIEVAL_CLASS.value,
    LimitationKind.CLAIM_CHECK_ZERO.value,
}
_VALIDITY_THREATENING_STATES = {
    EvidenceState.STALE.value,
    EvidenceState.SUPPRESSED.value,
    EvidenceState.RETRACTED.value,
    EvidenceState.RAN_ERROR.value,
    EvidenceState.NOT_RUN.value,
    EvidenceState.REFUSED_ON_EVIDENCE.value,
    EvidenceState.ENGINE_CANNOT_CONSUME.value,
}


def _e(value: Any) -> str:
    return _page._e(value)


def _num(value: Any) -> str:
    return _page._num(value)


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _slug_piece(value: Any) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", str(value or "item").lower()).strip("-")
    return text[:48] or "item"


def _enum_value(value: str | Enum) -> str:
    return value.value if isinstance(value, Enum) else str(value)


def classify_limitation(kind: LimitationKind | str, evidence_state: EvidenceState | str) -> str:
    kind_value = _enum_value(kind)
    state_value = _enum_value(evidence_state)
    if kind_value in _VALIDITY_THREATENING_KINDS or state_value in _VALIDITY_THREATENING_STATES:
        return LimitationClass.VALIDITY_THREATENING.value
    return LimitationClass.INFORMATIONAL.value


def _linked_decision(kind: LimitationKind | str, evidence_state: EvidenceState | str) -> dict[str, str]:
    kind_value = _enum_value(kind)
    state_value = _enum_value(evidence_state)
    if kind_value == LimitationKind.RETRIEVAL_CLASS.value:
        return {
            "action": "ALLOW_WITH_LABEL",
            "gate_id": "limitation:retrieval-class",
            "decision_state": "page may publish only with the retrieval-class label; systematic-search claim refused",
        }
    if kind_value == LimitationKind.UNIT_OF_ANALYSIS.value:
        return {
            "action": "ALLOW_WITH_LABEL",
            "gate_id": "limitation:unit-of-analysis",
            "decision_state": "design state is labelled and delegated to the typed design action",
        }
    if kind_value == LimitationKind.SEARCH_PROVENANCE.value:
        return {
            "action": "REFUSE",
            "gate_id": "limitation:search-provenance",
            "decision_state": "unqualified registry-first/systematic-search claim refused",
        }
    if kind_value == LimitationKind.HARMS_INCOMPLETE.value:
        return {
            "action": "REFUSE",
            "gate_id": "compat-check:harms-incomplete",
            "decision_state": "isolated harms estimate is suppressed until known primary-pool reports are extracted or typed-refused",
        }
    if kind_value in {
        LimitationKind.STALE_TOPIC.value,
        LimitationKind.SUPPRESSED_POOL.value,
        LimitationKind.RETRACTED_TRIAL_POOLED.value,
        LimitationKind.CLAIM_CHECK_ZERO.value,
    }:
        return {
            "action": "REFUSE",
            "gate_id": f"limitation:{kind_value.lower()}",
            "decision_state": f"{kind_value} blocks the affected analytic claim",
        }
    if state_value in _VALIDITY_THREATENING_STATES:
        return {
            "action": "REFUSE",
            "gate_id": "limitation:evidence-state",
            "decision_state": f"{state_value} blocks the affected claim unless specifically resolved",
        }
    return {
        "action": "ALLOW_WITH_LABEL",
        "gate_id": "limitation:labelled-validity-threat",
        "decision_state": "validity threat is explicitly labelled on the affected claim",
    }


def _object(
    review: dict[str, Any],
    suffix: str,
    kind: LimitationKind,
    severity: Severity,
    claim_affected: str,
    evidence_state: EvidenceState | str,
    source_fields: list[str],
    rendered_html: str,
) -> dict[str, Any]:
    rendered = str(rendered_html)
    state_value = _enum_value(evidence_state)
    class_value = classify_limitation(kind, state_value)
    obj = {
        "limitation_id": f"topic:{review.get('slug', 'unknown')}:{suffix}",
        "kind": kind.value,
        "limitation_class": class_value,
        "severity": severity.value,
        "claim_affected": claim_affected,
        "evidence_state": state_value,
        "source_fields": list(source_fields),
        "rendered_text": rendered,
        "text_sha256": _sha256(rendered),
    }
    obj["linked_decision"] = _linked_decision(kind, state_value)
    return obj


def render_limitation(obj: dict[str, Any]) -> str:
    """Render one limitation object as the block HTML used for legacy comparison."""

    return str(obj.get("rendered_text") or "")


def _absent(section: Any) -> str | None:
    if section is None:
        return "not declared in the review object"
    if isinstance(section, dict) and section.get("present") is False:
        return section.get("reason") or "declared absent (no reason given)"
    return None


def _absent_block(reason: str) -> str:
    return f'<div class="absent"><strong>DECLARED ABSENT.</strong> {_e(reason)}</div>'


def _primary(review: dict[str, Any]) -> dict[str, Any] | None:
    for outcome in review.get("outcomes", []) or []:
        if outcome.get("primary"):
            return outcome
    outcomes = review.get("outcomes") or []
    return outcomes[0] if outcomes else None


def _declared_absent_state(section: Any) -> str:
    if isinstance(section, dict):
        state = section.get("state")
        if state == "HARMS_INCOMPLETE":
            return EvidenceState.PARTIAL.value
        if state in _SOURCE_ABSENCE_STATES:
            return _SOURCE_ABSENCE_STATES[state]
        if section.get("absent_kind") == "refused_on_evidence":
            return EvidenceState.REFUSED_ON_EVIDENCE.value
        if section.get("present") is False:
            return EvidenceState.DECLARED_ABSENT.value
    return EvidenceState.UNKNOWN.value


def _retrieval_snapshot_block(ret: dict[str, Any]) -> str:
    snap = ret.get("snapshot") or {}
    sha8 = str(snap.get("records_sha256") or "")[:8]
    return (
        "<div class='banner'>"
        f"<p><strong>Snapshot:</strong> records_sha256 <code>{_e(sha8)}</code>; "
        f"retrieved_utc {_e(snap.get('retrieved_utc'))}; mode {_page._retrieval_mode_label(snap.get('mode'))}.</p>"
        "<p>This page replays the committed retrieval snapshot; it is not a claim that the protocol "
        "SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event "
        "(see Re-search below if present).</p>"
        "</div>"
    )


def _retrieval_state(ret: dict[str, Any]) -> str:
    states = [str(src.get("state") or "") for src in (ret.get("sources") or [])]
    if any(state == "RAN_ERROR" for state in states):
        return EvidenceState.RAN_ERROR.value
    if any(state == "NOT_RUN" for state in states):
        return EvidenceState.NOT_RUN.value
    if any(state == "RAN_UNRECORDED" for state in states):
        return EvidenceState.UNRECORDED.value
    if states:
        return EvidenceState.RECORDED.value
    return EvidenceState.UNKNOWN.value


def _retrieval_class_block(rc: dict[str, Any]) -> str:
    block_class = "banner" if rc.get("retrieval_auditable") else "absent"
    body = f"<div class='{block_class}'><p><strong>{_e(rc.get('label'))}</strong>"
    if rc.get("retraction"):
        body += " " + _e(rc.get("retraction"))
    if rc.get("distinction"):
        body += " " + _e(rc.get("distinction")) + "."
    return body + "</p></div>"


def _retrieval_class_state(rc: dict[str, Any]) -> str:
    if rc.get("retrieval_auditable"):
        return EvidenceState.RECORDED.value
    kinds = {row.get("kind") for row in (rc.get("basis") or [])}
    if kinds == {"PMID_ENUMERATION"}:
        return EvidenceState.NOT_RUN.value
    return EvidenceState.UNRECORDED.value


def _suppressed_overview_block(res: dict[str, Any]) -> str:
    return (
        "<div class='absent'><strong>Pooled result SUPPRESSED (estimand-incompatible).</strong> "
        f"{_e(res.get('suppressed_reason'))} <em>Estimand classes: "
        f"{_e(' + '.join((res.get('estmeasure') or {}).get('canonicals', [])))}; the "
        f"{_e(res.get('k'))} eligible trials are shown individually in Results, not pooled.</em></div>"
    )


def _suppressed_outcome_block(res: dict[str, Any]) -> str:
    cf = res.get("counterfactual") or {}
    cf_line = ""
    if cf.get("would_be_estimate") is not None:
        cf_line = (
            f" <em>Refusal is reversible and auditable &mdash; reason code "
            f"<code>{_e(cf.get('reason_code'))}</code>; had these classes been pooled anyway "
            f"the (INVALID) result would have been {_num(cf.get('would_be_estimate'))} "
            f"({_num(cf.get('would_be_ci_low'))}&ndash;{_num(cf.get('would_be_ci_high'))}) &mdash; shown "
            f"only so the refusal is inspectable, never as a usable number.</em>"
        )
    return (
        "<div class='absent'><strong>Pooled result SUPPRESSED (estimand-incompatible).</strong> "
        f"{_e(res.get('suppressed_reason'))} <em>Estimand classes: "
        f"{_e(' + '.join((res.get('estmeasure') or {}).get('canonicals', [])))}; k = "
        f"{_e(res.get('k'))} trials, shown individually below, not pooled.</em>{cf_line}</div>"
    )


def _k2_pool_refusal_block(res: dict[str, Any]) -> str:
    ref = res.get("pool_refused") or {}
    cf = res.get("counterfactual") or {}
    line = (
        "<div class='absent'><strong>Pooled result REFUSED (k=2 direction conflict).</strong> "
        f"{_e(ref.get('detail'))} {_e(ref.get('rule'))}"
    )
    if cf.get("would_be_estimate") is not None:
        line += (
            f" <em>The invalid pooled row is quarantined for audit only: "
            f"{_num(cf.get('would_be_estimate'))} ({_num(cf.get('would_be_ci_low'))}-"
            f"{_num(cf.get('would_be_ci_high'))}), tau^2={_e(cf.get('would_be_tau2'))}, "
            f"I^2={_e(cf.get('would_be_i2'))}%.</em>"
        )
    anchor = ref.get("honest_k1_anchor") or {}
    if anchor:
        line += (
            f"<p><strong>Honest k=1 anchor:</strong> {_e(anchor.get('name') or anchor.get('label'))} "
            f"{_e(anchor.get('scale') or res.get('scale'))} {_num(anchor.get('effect'))} "
            f"(95% CI {_num(anchor.get('ci_low'))}-{_num(anchor.get('ci_high'))}). "
            f"{_e(anchor.get('basis') or '')}</p>"
        )
        rem = ref.get("named_remainders") or []
        if rem:
            items = "".join(
                f"<li>{_e(x.get('label'))}: {_e(x.get('scale') or res.get('scale'))} {_num(x.get('effect'))} "
                f"(95% CI {_num(x.get('ci_low'))}-{_num(x.get('ci_high'))})</li>" for x in rem
            )
            line += f"<p><strong>Named remainder(s), not pooled:</strong></p><ul>{items}</ul>"
    return line + "</div>"


def _k2_ci_refusal_block(res: dict[str, Any]) -> str:
    ref = res.get("pooled_ci_refused") or {}
    return (
        "<div class='absent'><strong>Registered pooled CI REFUSED at k=2.</strong> "
        f"{_e(ref.get('detail'))} The point estimate may be displayed, but no pooled "
        "significance/null-crossing claim is emitted.</div>"
    )


def _harms_incomplete_block(res: dict[str, Any]) -> str:
    unresolved = res.get("known_eligible_outcome_reports_unresolved") or []
    names = ", ".join(str(x.get("trial_id")) for x in unresolved[:8])
    return (
        "<div class='absent'><strong>HARMS_INCOMPLETE.</strong> "
        f"{_e(res.get('reason'))} "
        f"<span class='muted'>Known unresolved primary-pool trial(s): {_e(names)}</span></div>"
    )


def _harms_result_incomplete_block(res: dict[str, Any]) -> str:
    unresolved = ", ".join(str(x.get("label") or x.get("id"))
                           for x in (res.get("known_reported_not_yet_extracted") or []))
    return (
        "<div class='absent'><strong>HARMS_INCOMPLETE.</strong> "
        f"{_e(res.get('reason'))} "
        f"<span class='muted'>Unresolved: {_e(unresolved)}</span></div>"
    )


def _harms_registry_incomplete_block(state: dict[str, Any]) -> str:
    names = ", ".join(str(x.get("label") or x.get("id"))
                      for x in (state.get("known_reported_not_yet_extracted") or [])[:8])
    return (
        "<div class='absent'><strong>HARMS_INCOMPLETE.</strong> "
        f"{_e(state.get('reason'))} "
        f"<span class='muted'>Known source-reported harms: {_e(names)}</span></div>"
    )


def _design_refusal_block(res: dict[str, Any]) -> str:
    dr = res.get("design_refusal") or {}
    refused = "; ".join(
        f"{_e(x.get('trial'))} ({_e(x.get('design'))})" for x in (dr.get("refused") or [])
    )
    missing = "; ".join(
        f"{_e(x.get('trial'))}: {_e(x.get('reason_code') or x.get('state'))} missing {_e(x.get('missing'))}"
        for x in (dr.get("refused") or [])
    )
    return (
        "<div class='absent'><strong>ENGINE_CANNOT_CONSUME design variance.</strong> "
        f"{_e(dr.get('statement'))} Refused trial(s): {refused}. {missing}. "
        "The evidence is not absent; this engine cannot consume the row without a held "
        "design-adjusted effect or ICC design-effect variance.</div>"
    )


def _integrity_block(integrity: dict[str, Any]) -> str:
    retracted = integrity.get("retracted", [])
    return (
        f"<div class='absent'><strong>RETRACTED TRIAL POOLED:</strong> {_e(', '.join(retracted))} "
        "&mdash; this page must not stand until resolved.</div>"
    )


def _uoa_block(review: dict[str, Any], uoa: list[dict[str, Any]]) -> str:
    variance_designs = {
        "cluster-randomized",
        "cluster-randomized crossover",
        "crossover",
        "stepped-wedge",
    }
    variance_uoa = [u for u in uoa if (u.get("design") or "").lower() in variance_designs]
    factorial_uoa = [u for u in uoa if (u.get("design") or "").lower() == "factorial"]
    other_uoa = [u for u in uoa if u not in variance_uoa and u not in factorial_uoa]
    sensitivity = _page._uoa_sensitivity(review, [u.get("id") for u in variance_uoa]) if variance_uoa else None
    sens_txt = ""
    if sensitivity and len(sensitivity["points"]) > 1:
        base = sensitivity["points"][0][1]
        rng = "; ".join(f"&times;{factor:g}&rarr;{estimate}" for factor, estimate in sensitivity["points"][1:])
        sens_txt = (
            f" <strong>The pooled point estimate is NOT invariant to this</strong>: inflating only "
            f"these trials' variances re-pools (illustrative DL) from {base} to "
            f"{sensitivity['points'][-1][1]} ({rng}) &mdash; because changing a study's variance changes its "
            "inverse-variance weight, so both the estimate and its interval move."
        )
    parts = []
    if variance_uoa:
        items = "; ".join(f"{_e(u.get('id'))} ({_e(u.get('design'))})" for u in variance_uoa)
        parts.append(
            f"{len(variance_uoa)} pooled trial(s) use a clustered, stepped-wedge, or crossover design: "
            f"{items}. If they are reconstructed from patient-level counts, they require an explicit "
            "<strong>design-correlation adjustment</strong> (ICC, cluster-period correlation, or paired "
            "analysis); otherwise their variance is not a simple parallel-arm variance."
            + sens_txt
        )
    if factorial_uoa:
        items = "; ".join(f"{_e(u.get('id'))} ({_e(u.get('design'))})" for u in factorial_uoa)
        parts.append(
            f"{len(factorial_uoa)} pooled trial(s) are individual-randomized factorial designs: {items}. "
            "These are disclosed as marginal factorial contrasts; when a source-reported adjusted "
            "marginal estimate with acceptable interaction evidence is available, the design key records "
            "that estimator and labels it rather than using a raw reconstruction silently."
        )
    if other_uoa:
        items = "; ".join(f"{_e(u.get('id'))} ({_e(u.get('design'))})" for u in other_uoa)
        parts.append(f"{len(other_uoa)} pooled trial(s) have non-simple design text: {items}.")
    return (
        "<div class='absent'><strong>Unit-of-analysis/design caveat (disclosed, not silently adjusted)."
        "</strong> "
        + " ".join(parts)
        + " This is a stated limitation and design-key disclosure, not silent simple-parallel pooling.</div>"
    )


def _funding_known(funding: dict[str, Any]) -> bool:
    return _funding_mod.funding_known(funding)


def _funding_block(fund: list[dict[str, Any]]) -> str:
    def _class(item: dict[str, Any]) -> str:
        return item.get("sponsor_class") or item.get("type") or ""

    def _ord(item: dict[str, Any]) -> int:
        typ = _class(item)
        if typ.startswith("industry"):
            return 0
        if typ == "mixed":
            return 1
        if typ.startswith("public"):
            return 2
        if typ.startswith("in_source"):
            return 3
        return 4

    def _celltype(item: dict[str, Any]) -> str:
        bits = [f"<strong>{_e(_class(item))}</strong>", _e(item.get("status") or "")]
        if item.get("note"):
            bits.append(f"<em>{_e(item.get('note'))}</em>")
        if item.get("industry_authors_present"):
            bits.append("<em>industry authors present (not sponsor evidence)</em>")
        return "<br>".join(bit for bit in bits if bit)

    def _sponsor_cell(item: dict[str, Any]) -> str:
        sponsors = item.get("sponsors") or []
        roles = item.get("role") or []
        body = "; ".join(_e(value) for value in sponsors) or "&mdash;"
        if roles:
            body += "<br><em>roles: " + _e(", ".join(roles)) + "</em>"
        return body

    def _source_cell(item: dict[str, Any]) -> str:
        sources = item.get("sources") or [{
            "source_id": item.get("source_id") or item.get("source"),
            "basis_span": item.get("basis_span") or item.get("span"),
            "role": item.get("role") or [],
        }]
        rows = []
        for src in sources:
            label = src.get("source_id") or ""
            span = src.get("basis_span") or ""
            role = src.get("role") or []
            text = f"<strong>{_e(label)}</strong>: {_e(span)}"
            if role:
                text += f" <em>roles: {_e(', '.join(role))}</em>"
            rows.append(text)
        return "<br>".join(rows) or "&mdash;"

    rows = "".join(
        f"<tr><td>{_e(item.get('id'))}</td><td>{_celltype(item)}</td>"
        f"<td>{_sponsor_cell(item)}</td><td>{_e(item.get('scanned') or item.get('source'))}</td>"
        f"<td>{_source_cell(item)}</td></tr>"
        for item in sorted(fund, key=lambda item: _ord(item))
    )
    n_ind = sum(1 for item in fund if _funding_mod.industry_tied(item))
    n_ns_ft = sum(1 for item in fund if item.get("status") == "none_stated_in_held_text"
                  and (item.get("scanned") or "").startswith("full text"))
    n_ns_ab = sum(1 for item in fund if item.get("status") == "none_stated_in_held_text"
                  and not (item.get("scanned") or "").startswith("full text"))
    n_known = sum(1 for item in fund if _funding_known(item))
    n_unknown = len(fund) - n_known
    return (
        "<div class='absent'><strong>Funding / conflict-of-interest disclosure (per pooled "
        "trial, from source &mdash; disclosed, not adjusted).</strong> Industry-funded trials are a "
        "documented reporting-bias dimension (they tend to report more favourable results). For "
        "each pooled trial the funding source is classified from held text (full text preferred, "
        "abstract fallback) and the registry sponsor is shown as a second source when available; "
        "when held text and registry disagree, both source spans are rendered. Industry author "
        "affiliations are flagged only as affiliations, never sponsor evidence. Including an "
        "industry <em>drug-supply</em> tie in an otherwise independently funded trial: "
        f"<strong>{n_ind} of {n_known} known</strong> ({n_unknown} unknown) pooled trials are "
        "industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN "
        "funding &mdash; unknown-funding trials are reported separately below, not counted as "
        "independently funded &mdash; for comparison against a "
        "comparator's). Absence is labelled by how "
        f"deeply we looked &mdash; {n_ns_ft} with no funding statement in the <strong>full text</strong> "
        f"(genuinely silent) and {n_ns_ab} where only the <strong>abstract</strong> was available "
        "(full text not retrieved) &mdash; so 'not stated' is never presented as 'independently funded'. "
        "The harness <strong>does not adjust</strong> for funding (the per-trial bias magnitude is "
        "not quantifiable from a funding line) &mdash; it is disclosed so a reader can weigh it. Never "
        "inferred."
        "<table class='arms'><tr><th>Trial</th><th>Funding</th><th>Sponsors / roles</th>"
        f"<th>Scanned</th><th>Source evidence</th></tr>{rows}</table></div>"
    )


def _arm_contrast_block(ac: dict[str, dict[str, Any]]) -> str:
    labels = {
        "verified": "parser-confirmed contrast",
        "background_only": "BACKGROUND IN ALL ARMS &mdash; not a randomised contrast",
        "unverified_granularity": "contrast unverified (registry class label / dev code)",
        "unverified_no_contrast": "contrast unverified (no arm-level contrast coded)",
        "unverified_no_arm_data": "contrast unverified &mdash; no registry arm data",
    }
    order = {"background_only": 0, "unverified_no_arm_data": 1, "unverified_no_contrast": 2,
             "unverified_granularity": 3, "verified": 4}
    n_ver = sum(1 for entry in ac.values() if entry.get("status") == "verified")
    n_bg = sum(1 for entry in ac.values() if entry.get("status") == "background_only")
    rows = "".join(
        f"<tr><td>{_e(pid)}</td><td>{_e(labels.get(entry.get('status'), entry.get('status')))}</td>"
        f"<td title='{_e(entry.get('basis'))}'>{_e('; '.join(entry.get('differing') or []) or '&mdash;')}</td></tr>"
        for pid, entry in sorted(ac.items(), key=lambda kv: (order.get(kv[1].get("status"), 9), kv[0]))
    )
    return (
        "<div class='absent'><strong>Parser-confirmed contrast disclosure (per pooled trial, from the "
        "AACT arm-label parser - disclosed, not an adjustment).</strong> This measures the parser, not the trial. Eligibility should test "
        "what actually DIFFERS between the randomised arms, not the mere presence of the drug word: "
        "a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same "
        "agent, randomising a different drug) is not a randomised comparison of it. For each pooled "
        "trial the randomised contrast is reconstructed from AACT <code>design_groups</code> + "
        f"<code>interventions</code>: <strong>{n_ver} of {len(ac)}</strong> pooled trials have a "
        "parser-confirmed contrast (the intervention of interest matched a differing coded arm)"
        + (f"; <strong>{n_bg} is background in every arm (flagged)</strong>" if n_bg else "")
        + ". A trial with no registry arm data, or coded under a class label / development code we "
        "cannot machine-match, is shown as <em>contrast unverified</em> &mdash; a VISIBLE fail-open state, "
        "never silently treated as verified. "
        "<table class='arms'><tr><th>Trial</th><th>Contrast status</th><th>Randomised difference</th>"
        f"</tr>{rows}</table></div>"
    )


def _stale_contrast_block(stale: dict[str, Any]) -> str:
    return (
        "<div class='absent'><strong>UNRENDERABLE stale contrast block.</strong> "
        f"{_e(stale.get('reason'))}; current pooled trial ids: "
        f"{_e(', '.join(stale.get('current_pooled_trial_ids') or []))}; suppressed stale ids: "
        f"{_e(', '.join(stale.get('dropped_trial_ids') or []))}.</div>"
    )


def _protocol_control_block(ctrl: dict[str, Any]) -> str:
    return (
        "<div class='absent'><strong>UNRENDERABLE protocol control expectation.</strong> "
        f"{_e(ctrl.get('control'))}. {_e(ctrl.get('reason'))}</div>"
    )


_ROB_SENS_REFUSED_HTML = "<h4>Risk-of-bias sensitivity (re-pooled with the same estimator)</h4><div class='absent'><strong>Does the result survive dropping the trials that are not low risk of bias?</strong> Not computed: the primary pooled row is REFUSED ({code}), so there is no pooled estimate to re-pool by risk-of-bias stratum. The per-trial rows and their risk-of-bias ratings are shown above; a stratified re-pool of a refused pool would be a number about nothing.</div>"


def _rob_sensitivity_block(sens: dict[str, Any]) -> str:
    def _fmt(point: dict[str, Any] | None) -> str:
        if point and point.get("ci_refused"):
            return f"k={point['k']}, {point['scale']} {point['estimate']} (CI refused at k=2: {point['ci_refused']})"
        if not point:
            return "&mdash;"
        return f"k={point['k']}, {point['scale']} {point['estimate']} [{point['ci_low']}, {point['ci_high']}]"

    full, drop_high, low_only = sens.get("full"), sens.get("drop_high"), sens.get("low_only")
    lines = [f"<tr><td>Full pool (all pooled trials)</td><td>{_fmt(full)}</td></tr>"]
    if sens.get("any_high"):
        lines.append(f"<tr><td>Excluding high risk of bias</td><td>{_fmt(drop_high)}</td></tr>")
    if not low_only:
        low_cell = (
            "<strong>NOT ESTIMABLE</strong> &mdash; no pooled trial qualifies as low risk of "
            "bias, so this stratum has no trials to re-pool (an empty subgroup is not agreement "
            "with the full pool)"
        )
    else:
        low_cell = _fmt(low_only) + _rob_sensitivity_mod.low_only_relation_note_html(sens)
    lines.append(f"<tr><td>Low risk of bias only</td><td>{low_cell}</td></tr>")
    return (
        "<div class='absent'><strong>Does the result survive dropping the trials that are not "
        "low risk of bias?</strong> The primary outcome is re-pooled by risk-of-bias stratum "
        "with the identical estimator. "
        f"<strong>{sens.get('n_rob_rated')} of {sens.get('n_trials')}</strong> pooled trials have a risk-of-bias rating; "
        + ("no pooled trial is rated <em>high</em> risk (the registry-derived assessment does not "
           "reach 'high'), so the standard drop-high sensitivity is inert and the informative "
           "stratum is <em>low-only</em>. " if not sens.get("any_high") else "")
        + _rob_sensitivity_mod.low_only_relation_context_html(sens)
        + f"<table class='arms'><tr><th>Stratum</th><th>Re-pooled estimate</th></tr>"
        f"{''.join(lines)}</table></div>"
    )


def _grade_block(grade: dict[str, Any]) -> str:
    domains = grade.get("domains", {})
    order = [
        ("risk_of_bias", "Risk of bias"),
        ("inconsistency", "Inconsistency"),
        ("imprecision", "Imprecision"),
        ("indirectness", "Indirectness"),
        ("publication_bias", "Publication bias (registry-based)"),
    ]
    rows = []
    for key, label in order:
        value = domains.get(key, {})
        downgrade = value.get("downgrade", 0)
        if not value.get("assessed", True):
            mark = "human judgement" if value.get("not_auto_rated") else "<strong>NOT ASSESSED</strong>"
        else:
            mark = "&minus;1" if downgrade == 1 else f"&minus;{downgrade}" if downgrade else "not downgraded"
        rows.append(f"<tr><th scope='row'>{_e(label)}</th><td colspan='2'>"
                    + claimgraph.grade_render(grade, 'grade-domain-' + key) + "</td></tr>")
    cap = (
        " The rating is capped below <em>high</em> because risk of bias is not assessed for every "
        "pooled trial." if grade.get("certainty_capped_by_rob_coverage") else ""
    )
    if grade.get("certainty_capped_unassessed_domain"):
        unassessed = ", ".join(item.replace("_", " ") for item in (grade.get("unassessed_domains") or []))
        cap += (
            f" The rating is capped below <em>high</em> because a required GRADE domain was NOT "
            f"ASSESSED ({unassessed}); an unassessed domain is not evidence of no concern, so the top "
            f"certainty cannot be certified until it is rated (unassessed never counts as favourable)."
        )
    if grade.get("certainty_capped_d3_unassessed"):
        cap += (
            " The rating is capped below <em>high</em> because D3 (missing outcome data), a required "
            "risk-of-bias domain, is NOT ASSESSED for any pooled trial (no outcome-missingness "
            "source) &mdash; high certainty cannot be certified on a structurally-incomplete bias assessment."
        )
    if grade.get("rob_basis"):
        cap += f" <strong>RoB basis:</strong> {_e(grade.get('rob_basis'))}."
    rob_phrase = (
        "uses registry-machine-signal-restricted domains"
        if grade.get("rob_basis")
        else "uses machine-derived signals"
    )
    if grade.get("certainty") == "not_rateable":
        return (
            "<div class='absent'><strong>Overall certainty: not rateable.</strong> "
            f"{_e(grade.get('not_rateable_reason',''))}. The individual domain signals are shown "
            "below, but no overall certainty category is emitted &mdash; a partial or incoherent "
            "evidence object cannot produce one, and &lsquo;provisional&rsquo; would soften the "
            "language without repairing the logic."
            "<table class='arms'><tr><th>Domain</th><th>Signal</th><th>Basis</th></tr>"
            f"{''.join(rows)}</table></div>"
        )
    pub = (grade.get("domains") or {}).get("publication_bias") or {}
    pub_sentence = (
        "Risk of bias, inconsistency and imprecision are computed from committed fields; "
        "<strong>publication bias is NOT ASSESSED automatically</strong> because the available "
        "registry ghost census is descriptive until its denominator is PICO-scoped. "
        if pub.get("assessed") is False else
        "Risk of bias, inconsistency, imprecision and publication bias are computed from "
        "committed fields; <strong>publication bias is assessed from the registry ghost census, "
        "not funnel-plot asymmetry</strong> (which is unreliable at our small k). "
    )
    return (
        "<div class='absent'><strong>Overall certainty (provisional): "
        f"{claimgraph.certainty_render({'grade': grade})}</strong> "
        f"{claimgraph.grade_render(grade, 'grade-downgrades')} {cap}"
        "<strong>PROVISIONAL:</strong> this is a machine-derived certainty &mdash; risk of bias "
        f"{rob_phrase} (registry-machine-signal-restricted signals, not a human risk-of-bias assessment) "
        "and indirectness is not auto-rated, "
        "so a formal human GRADE assessment may differ. "
        + pub_sentence +
        "<strong>Indirectness is left to human judgement</strong> (the PICO scope note states "
        "the directness) &mdash; this is a partial GRADE, honestly labelled."
        "<table class='arms'><tr><th>Domain</th><th>Effect on certainty</th><th>Basis</th></tr>"
        f"{''.join(rows)}</table></div>"
    )


def _rob_spancheck_block(rsc: dict[str, Any]) -> str:
    return (
        "<div class='banner'><strong>RoB spans span-checked (cross-family): "
        f"{round(rsc['agreement_rate'] * 100)}% agreement</strong> ({rsc.get('supported')} of "
        f"{rsc.get('supported', 0) + rsc.get('not_supported', 0)} scoreable), from a seeded sample of "
        f"{rsc.get('n_sampled')} model/registry-derived domain ratings independently checked by a "
        f"different model family (Fable) against each trial abstract; {rsc.get('unclear')} were "
        "unscoreable (no claim, or a conservative not-stated rating). This check itself found and "
        "fixed a real error &mdash; one trial (EMPHASIS-HF) was mislabelled NON_RANDOMIZED by the "
        "registry, contradicted by its abstract; the RoB block was also visibly broken until a "
        "human review caught it. The number is here because a RoB block a reader cannot trust is "
        "worthless (<code>docs/rob_spancheck.json</code>).</div>"
    )


def _manuscript_banner_block() -> str:
    return (
        "<div class='banner'>This manuscript is <strong>generated from the review object</strong> &mdash; "
        "every number is interpolated from a committed field, and a gate limb refuses any manuscript "
        "numeral that is not object-derived. It is a machine artefact, not a hand-written paper.</div>"
    )


def _claim_check_count(review: dict[str, Any]) -> int:
    rep = review.get("reproduction") or {}
    cc = rep.get("claim_check") if isinstance(rep, dict) else None
    if isinstance(cc, dict) and cc.get("claims_checked") is not None:
        return int(cc.get("claims_checked") or 0)
    count = 0
    for outcome in review.get("outcomes", []) or []:
        result = outcome.get("result")
        if not isinstance(result, dict):
            continue
        claim = result.get("claim") or {}
        if claim.get("present"):
            count += 1
    scope_counts = claimgraph.scope_counts(review, count)
    return count + int(scope_counts.get("strand_pool") or 0)


def build_limitations(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Build one structured object per legacy page-level absent/banner block."""

    out: list[dict[str, Any]] = []
    acknowledgements = _hazard_consumers.load_acknowledgements()

    def add(
        suffix: str,
        kind: LimitationKind,
        severity: Severity,
        claim: str,
        state: EvidenceState | str,
        fields: list[str],
        html: str,
    ) -> None:
        obj = _object(review, suffix, kind, severity, claim, state, fields, html)
        out.append(_hazard_consumers.annotate_object(review, obj, acknowledgements))

    inv = review.get("invalidation") or {}
    if inv.get("stale"):
        add(
            "overview:stale-topic",
            LimitationKind.STALE_TOPIC,
            Severity.BLOCKS_CLAIM,
            "current/settled topic result",
            EvidenceState.STALE,
            ["/invalidation/stale", "/invalidation/reasons"],
            _page._stale_topic_overview(review),
        )

    identifier_html = _page._identifier_scope_block(review)
    identifier_scope = review.get("identifier_scope") or {}
    if identifier_scope.get("verdict") not in (None, "MATCH", "NOT_APPLICABLE") and identifier_html:
        for suffix in ("overview:identifier-scope", "screening:identifier-scope"):
            add(
                suffix,
                LimitationKind.IDENTIFIER_SCOPE,
                Severity.BLOCKS_CLAIM,
                "claim about the identifier-named intervention alone",
                EvidenceState.REFUSED_ON_EVIDENCE,
                ["/identifier_scope"],
                identifier_html,
            )

    if (review.get("eligibility_chain") or {}).get("violations"):
        add(
            "protocol:eligibility-chain",
            LimitationKind.ELIGIBILITY_CHAIN,
            Severity.BLOCKS_CLAIM,
            "admissible pooled claim",
            EvidenceState.REFUSED_ON_EVIDENCE,
            ["/eligibility_chain/violations", "/eligibility_chain/contract"],
            _page._eligibility_chain_block(review),
        )

    rc = (review.get("search") or {}).get("retrieval_class") or {}
    if rc.get("class") in ("KNOWN_ITEM_RETRIEVAL", "TITLE_SEEDED_RETRIEVAL", "HAND_WRITTEN_KEYWORD_SEARCH"):
        add(
            "overview:retrieval-class",
            LimitationKind.RETRIEVAL_CLASS,
            Severity.QUALIFIES_CLAIM,
            "search completeness / systematic-search claim",
            _retrieval_class_state(rc),
            ["/search/retrieval_class/class", "/search/retrieval_class/basis"],
            _page._retrieval_class_overview(rc),
        )

    add(
        "overview:auditability-scope",
        LimitationKind.AUDITABILITY_SCOPE,
        Severity.NOTE,
        "auditability versus evidence strength",
        EvidenceState.RECORDED,
        ["/slug"],
        "<div class='banner'>This page offers <strong>greater auditability, not "
        "stronger evidence</strong>: every number traces to a committed source, every "
        "absence is declared, and any hand-edit breaks the reproduction census.</div>",
    )

    primary = _primary(review)
    if primary and _absent(primary) is None:
        pres = primary.get("result") or {}
        if pres.get("pool_refused"):
            add(
                "overview:k2-direction-conflict:primary",
                LimitationKind.SUPPRESSED_POOL,
                Severity.BLOCKS_CLAIM,
                "primary pooled estimate",
                EvidenceState.SUPPRESSED,
                ["/outcomes/*/result/pool_refused", "/outcomes/*/result/k2_trial_diagnostics"],
                _k2_pool_refusal_block(pres),
            )
        if pres.get("suppressed_incompatible"):
            add(
                "overview:suppressed-pool:primary",
                LimitationKind.SUPPRESSED_POOL,
                Severity.BLOCKS_CLAIM,
                "primary pooled estimate",
                EvidenceState.SUPPRESSED,
                ["/outcomes/*/result/suppressed_incompatible", "/outcomes/*/result/suppressed_reason"],
                _suppressed_overview_block(pres),
            )
            if review.get("strands"):
                add(
                    "overview:declared-strands",
                    LimitationKind.DECLARED_STRANDS,
                    Severity.QUALIFIES_CLAIM,
                    "endpoint-clean decomposition after refused cross-endpoint pool",
                    EvidenceState.REFUSED_ON_EVIDENCE,
                    ["/strands/why_topic_is_suppressed", "/strands/strands", "/strands/refused_cross_endpoint_pool"],
                    _page.render_strands_section(review["strands"]),
                )

    for idx, ctrl in enumerate(((review.get("protocol") or {}).get("control_expectations") or [])):
        if ctrl.get("state") == "UNRENDERABLE":
            add(
                f"protocol:control-expectation:{idx}",
                LimitationKind.AUDITABILITY_SCOPE,
                Severity.NOTE,
                "protocol control expectation",
                EvidenceState.RECORDED,
                ["/protocol/control_expectations"],
                _protocol_control_block(ctrl),
            )

    for section_name in ("protocol", "search", "screening"):
        reason = _absent(review.get(section_name))
        if reason:
            add(
                f"{section_name}:declared-absent",
                LimitationKind.DECLARED_ABSENT_SECTION,
                Severity.BLOCKS_CLAIM,
                f"{section_name} tab content",
                _declared_absent_state(review.get(section_name)),
                [f"/{section_name}/present", f"/{section_name}/reason"],
                _absent_block(reason),
            )

    search = review.get("search") or {}
    if not _absent(search):
        ret = search.get("retrieval")
        if ret:
            add(
                "search:retrieval-snapshot",
                LimitationKind.RETRIEVAL_SNAPSHOT,
                Severity.NOTE,
                "retrieval replay boundary",
                _retrieval_state(ret),
                ["/search/retrieval/snapshot", "/search/retrieval/sources"],
                _retrieval_snapshot_block(ret),
            )
            if ret.get("enumeration_only"):
                add(
                    "search:enumeration-only",
                    LimitationKind.SEARCH_ENUMERATION_ONLY,
                    Severity.BLOCKS_CLAIM,
                    "search completeness / systematic-search claim",
                    EvidenceState.NOT_RUN,
                    ["/search/retrieval/enumeration_only"],
                    "<div class='absent'><strong>No search was run for this topic: every PubMed source "
                    "is a PMID enumeration.</strong></div>",
                )
        if search.get("retrieval_class"):
            rclass = search["retrieval_class"]
            add(
                "search:retrieval-class",
                LimitationKind.RETRIEVAL_CLASS,
                Severity.QUALIFIES_CLAIM if not rclass.get("retrieval_auditable") else Severity.NOTE,
                "search completeness / systematic-search claim",
                _retrieval_class_state(rclass),
                ["/search/retrieval_class/label", "/search/retrieval_class/retrieval_auditable"],
                _retrieval_class_block(rclass),
            )
            # The restored "Search provenance" block: a retraction of the systematic-search claim,
            # rendered by page._search_provenance_html from retrieval_class.search_provenance only.
            if rclass.get("search_provenance"):
                add(
                    "search:search-provenance",
                    LimitationKind.SEARCH_PROVENANCE,
                    Severity.BLOCKS_CLAIM,
                    "registry-first / systematic-search claim (retracted)",
                    EvidenceState.RETRACTED,
                    ["/search/retrieval_class/search_provenance"],
                    _page._search_provenance_html(rclass),
                )

    integrity = review.get("integrity") or {}
    if integrity.get("retracted"):
        add(
            "screening:retracted-trial-pooled",
            LimitationKind.RETRACTED_TRIAL_POOLED,
            Severity.BLOCKS_CLAIM,
            "valid pooled page",
            EvidenceState.RETRACTED,
            ["/integrity/retracted"],
            _integrity_block(integrity),
        )

    definition_audit = review.get("definition_audit") or {}
    if definition_audit:
        add(
            "outcomes:definition-audit",
            LimitationKind.DEFINITION_AUDIT,
            Severity.QUALIFIES_CLAIM,
            "outcome definition identity",
            EvidenceState.PARTIAL,
            ["/definition_audit"],
            _page._definition_audit_block(review),
        )

    non_harm = [outcome for outcome in (review.get("outcomes") or []) if outcome.get("kind") != "harm"]
    if not non_harm:
        add(
            "outcomes:none",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            "efficacy outcomes",
            EvidenceState.UNKNOWN,
            ["/outcomes"],
            _absent_block("no efficacy outcomes in the review object"),
        )
    for idx, outcome in enumerate(non_harm):
        _add_outcome_limitations(add, outcome, f"outcomes:{idx}:{_slug_piece(outcome.get('name'))}")

    harms = [outcome for outcome in (review.get("outcomes") or []) if outcome.get("kind") == "harm"]
    if not harms:
        hstate = review.get("harms_registry_state") or {}
        add(
            "harms:none",
            LimitationKind.HARMS_INCOMPLETE if hstate else LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            "harms outcomes",
            EvidenceState.PARTIAL if hstate else EvidenceState.UNKNOWN,
            (
                ["/harms_registry_state/known_reported_not_yet_extracted", "/harms_registry_state/reason"]
                if hstate
                else ["/outcomes"]
            ),
            _harms_registry_incomplete_block(hstate) if hstate else _absent_block("no harms recorded"),
        )
    for idx, outcome in enumerate(harms):
        _add_outcome_limitations(add, outcome, f"harms:{idx}:{_slug_piece(outcome.get('name'))}")

    reason = _absent(review.get("comparator"))
    if reason:
        add(
            "comparator:declared-absent",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            "published comparator tab content",
            _declared_absent_state(review.get("comparator")),
            ["/comparator/present", "/comparator/reason"],
            _absent_block(reason),
        )

    _add_risk_of_bias_limitations(add, review)

    add(
        "manuscript:generated-object-banner",
        LimitationKind.AUDITABILITY_SCOPE,
        Severity.NOTE,
        "manuscript generation provenance",
        EvidenceState.RECORDED,
        ["/outcomes", "/comparator", "/reproduction"],
        _manuscript_banner_block(),
    )

    rep = review.get("reproduction")
    if isinstance(rep, dict) and rep.get("present") is False:
        reason = _absent(rep)
        add(
            "reproduction:declared-absent",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            "reproduction tab content",
            _declared_absent_state(rep),
            ["/reproduction/present", "/reproduction/reason"],
            _absent_block(reason or "declared absent (no reason given)"),
        )
    else:
        if _claim_check_count(review) == 0:
            add(
                "reproduction:claim-check-zero",
                LimitationKind.CLAIM_CHECK_ZERO,
                Severity.BLOCKS_CLAIM,
                "canonical claim contradiction gate coverage",
                EvidenceState.NOT_RUN,
                ["/reproduction/claim_check/claims_checked", "/outcomes/*/result/claim"],
                "<div class='absent'><strong>No checkable pooled claim (Claims checked: 0).</strong> "
                "Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing "
                "to check here &mdash; this is a limitation, not a clean result.</div>",
            )
        add(
            "reproduction:round-2-retraction",
            LimitationKind.REPRODUCTION_RETRACTION,
            Severity.BLOCKS_CLAIM,
            "byte-for-byte reproduction from protocol SHA",
            EvidenceState.RETRACTED,
            ["/reproduction/protocol_sha", "/reproduction/review_sha256"],
            "<div class='absent'><strong>RETRACTED (round-2): reproducibility claim not currently supported.</strong> "
            "We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page "
            "byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical "
            "output files, and running it AT the registered SHA produced an essentially empty review because the "
            "build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that "
            "is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with "
            "hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from "
            "the protocol SHA &mdash; only that the analysis is deterministic given the committed cache as-is. Independent "
            "REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.</div>",
        )
    return out


def _add_outcome_limitations(add: Any, outcome: dict[str, Any], prefix: str) -> None:
    reason = _absent(outcome)
    if reason:
        add(
            f"{prefix}:declared-absent",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            f"outcome result: {outcome.get('name')}",
            _declared_absent_state(outcome),
            ["/outcomes/*/present", "/outcomes/*/reason"],
            _absent_block(reason),
        )
        return
    result = outcome.get("result") or {}
    rr = _absent(result)
    if rr:
        is_harms_incomplete = result.get("state") == "HARMS_INCOMPLETE"
        block = _harms_incomplete_block(result) if is_harms_incomplete else _absent_block(rr)
        add(
            f"{prefix}:result-absent",
            LimitationKind.HARMS_INCOMPLETE if is_harms_incomplete else LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            f"outcome result: {outcome.get('name')}",
            EvidenceState.PARTIAL if is_harms_incomplete else _declared_absent_state(result),
            (
                ["/harms/*/result/state", "/harms/*/result/known_eligible_outcome_reports_unresolved"]
                if is_harms_incomplete
                else ["/outcomes/*/result/present", "/outcomes/*/result/reason"]
            ),
            block,
        )
    elif result.get("suppressed_incompatible"):
        add(
            f"{prefix}:suppressed-pool",
            LimitationKind.SUPPRESSED_POOL,
            Severity.BLOCKS_CLAIM,
            f"pooled estimate: {outcome.get('name')}",
            EvidenceState.SUPPRESSED,
            ["/outcomes/*/result/suppressed_incompatible", "/outcomes/*/result/suppressed_reason"],
            _suppressed_outcome_block(result),
        )
    elif result.get("pool_refused"):
        add(
            f"{prefix}:k2-direction-conflict",
            LimitationKind.SUPPRESSED_POOL,
            Severity.BLOCKS_CLAIM,
            f"pooled estimate: {outcome.get('name')}",
            EvidenceState.SUPPRESSED,
            ["/outcomes/*/result/pool_refused", "/outcomes/*/result/k2_trial_diagnostics"],
            _k2_pool_refusal_block(result),
        )
    elif result.get("pooled_ci_refused"):
        add(
            f"{prefix}:k2-ci-refused",
            LimitationKind.GRADE_CERTAINTY,
            Severity.QUALIFIES_CLAIM,
            f"pooled confidence interval: {outcome.get('name')}",
            EvidenceState.NOT_ASSESSED,
            ["/outcomes/*/result/pooled_ci_refused", "/outcomes/*/result/ci_hksj_unserved"],
            _k2_ci_refusal_block(result),
        )
    if (not rr and not result.get("suppressed_incompatible") and not result.get("pool_refused")
            and result.get("design_refusal")):
        add(
            f"{prefix}:design-refusal",
            LimitationKind.UNIT_OF_ANALYSIS,
            Severity.QUALIFIES_CLAIM,
            f"pooled estimate: {outcome.get('name')}",
            EvidenceState.ENGINE_CANNOT_CONSUME,
            ["/outcomes/*/result/design_refusal", "/outcomes/*/design_refusals"],
            _design_refusal_block(result),
        )
    if (not rr and not result.get("unrenderable") and not result.get("suppressed_incompatible")
            and not result.get("pool_refused") and result.get("harms_incomplete")):
        add(
            f"{prefix}:harms-incomplete",
            LimitationKind.HARMS_INCOMPLETE,
            Severity.BLOCKS_CLAIM,
            f"outcome result: {outcome.get('name')}",
            EvidenceState.PARTIAL,
            ["/outcomes/*/result/harms_incomplete", "/outcomes/*/result/known_reported_not_yet_extracted"],
            _harms_result_incomplete_block(result),
        )


def _add_risk_of_bias_limitations(add: Any, review: dict[str, Any]) -> None:
    rb = review.get("rob2") or {}
    assessed = rb.get("trials") or {}
    primary = _primary(review)
    pooled = {}
    for trial in (primary or {}).get("trials", []) or []:
        pid = str(trial.get("id", "")).replace("PMID ", "").strip()
        if pid:
            pooled.setdefault(pid, trial.get("label") or "")
    if not pooled and not assessed:
        add(
            "riskofbias:declared-absent",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            "risk-of-bias assessment",
            EvidenceState.NOT_ASSESSED,
            ["/rob2/trials", "/outcomes/*/trials"],
            _absent_block("no trials pooled in the primary outcome, so there is nothing to assess for risk of bias"),
        )

    rsc = review.get("rob_spancheck") or {}
    if rsc.get("agreement_rate") is not None:
        add(
            "riskofbias:rob-spancheck",
            LimitationKind.ROB_SPANCHECK,
            Severity.NOTE,
            "risk-of-bias span reliability",
            EvidenceState.RECORDED,
            ["/rob_spancheck/agreement_rate", "/rob_spancheck/supported", "/rob_spancheck/not_supported"],
            _rob_spancheck_block(rsc),
        )

    uoa = review.get("unit_of_analysis") or []
    if uoa:
        add(
            "riskofbias:unit-of-analysis",
            LimitationKind.UNIT_OF_ANALYSIS,
            Severity.QUALIFIES_CLAIM,
            "primary pooled variance and precision",
            EvidenceState.NOT_ASSESSED,
            ["/unit_of_analysis"],
            _uoa_block(review, uoa),
        )

    ac = (review.get("arm_contrast") or {}).get("trials") or {}
    if ac:
        stale = (review.get("arm_contrast") or {}).get("stale_block_unrenderable") or {}
        if stale:
            add(
                "riskofbias:stale-randomised-contrast",
                LimitationKind.RANDOMISED_CONTRAST,
                Severity.QUALIFIES_CLAIM,
                "randomised-contrast membership for current pooled trials",
                EvidenceState.PARTIAL,
                ["/arm_contrast/stale_block_unrenderable", "/arm_contrast/trials"],
                _stale_contrast_block(stale),
            )
        statuses = {entry.get("status") for entry in ac.values()}
        state = EvidenceState.RECORDED if statuses == {"verified"} else EvidenceState.PARTIAL
        add(
            "riskofbias:randomised-contrast",
            LimitationKind.RANDOMISED_CONTRAST,
            Severity.QUALIFIES_CLAIM,
            "randomised intervention contrast",
            state,
            ["/arm_contrast/trials"],
            _arm_contrast_block(ac),
        )

    fund = review.get("funding") or []
    if fund:
        state = EvidenceState.RECORDED if all(_funding_known(item) for item in fund) else EvidenceState.PARTIAL
        add(
            "riskofbias:funding-coi",
            LimitationKind.FUNDING_COI,
            Severity.QUALIFIES_CLAIM,
            "funding and conflict-of-interest adjustment",
            state,
            ["/funding"],
            _funding_block(fund),
        )

    sens = review.get("rob_sensitivity") or {}
    _prim_refused = next(((o.get("result") or {}).get("pool_refused") for o in (review.get("outcomes") or [])
                          if o.get("primary")), None)
    if not sens.get("full") and _prim_refused:
        add(
            "riskofbias:rob-sensitivity",
            LimitationKind.ROB_SENSITIVITY,
            Severity.QUALIFIES_CLAIM,
            "risk-of-bias sensitivity interpretation",
            EvidenceState.PARTIAL,
            ["/outcomes/*/result/pool_refused"],
            _ROB_SENS_REFUSED_HTML.format(code=str(_prim_refused.get("code"))),
        )
    if sens.get("full"):
        add(
            "riskofbias:rob-sensitivity",
            LimitationKind.ROB_SENSITIVITY,
            Severity.QUALIFIES_CLAIM,
            "risk-of-bias sensitivity interpretation",
            EvidenceState.PARTIAL,
            ["/rob_sensitivity/full", "/rob_sensitivity/drop_high", "/rob_sensitivity/low_only"],
            _rob_sensitivity_block(sens),
        )

    grade = review.get("grade") or {}
    if grade.get("certainty"):
        state = EvidenceState.NOT_ASSESSED if grade.get("certainty") == "not_rateable" else EvidenceState.PROVISIONAL
        add(
            "riskofbias:grade-certainty",
            LimitationKind.GRADE_CERTAINTY,
            Severity.QUALIFIES_CLAIM,
            "overall GRADE certainty",
            state,
            ["/grade/certainty", "/grade/domains"],
            _grade_block(grade),
        )


def _ack_entries(acknowledgements: Any) -> list[dict[str, Any]]:
    if isinstance(acknowledgements, dict):
        raw = acknowledgements.get("acknowledgements", [])
    else:
        raw = acknowledgements
    return [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []


def _has_review_fields(entry: dict[str, Any]) -> bool:
    actor = entry.get("reviewer") or entry.get("by")
    return bool(actor) and bool(entry.get("reason"))


def _ack_removed(entry: dict[str, Any], old_id: str, after_ids: set[str]) -> bool:
    repl = entry.get("replacement_limitation_ids") or entry.get("replacement_ids") or []
    if isinstance(repl, str):
        repl = [repl]
    return (
        entry.get("lost_limitation_id") == old_id
        and bool(repl)
        and all(item in after_ids for item in repl)
        and _has_review_fields(entry)
    )


def _ack_transition(entry: dict[str, Any], old_obj: dict[str, Any], new_obj: dict[str, Any]) -> bool:
    return (
        entry.get("limitation_id") == old_obj.get("limitation_id")
        and entry.get("old_severity", old_obj.get("severity")) == old_obj.get("severity")
        and entry.get("new_severity", new_obj.get("severity")) == new_obj.get("severity")
        and entry.get("old_evidence_state", old_obj.get("evidence_state")) == old_obj.get("evidence_state")
        and entry.get("new_evidence_state", new_obj.get("evidence_state")) == new_obj.get("evidence_state")
        and _has_review_fields(entry)
    )


def _ack_renderer_update(entry: dict[str, Any], old_obj: dict[str, Any], new_obj: dict[str, Any]) -> bool:
    return (
        entry.get("limitation_id") == old_obj.get("limitation_id")
        and entry.get("old_text_sha256") == old_obj.get("text_sha256")
        and entry.get("new_text_sha256") == new_obj.get("text_sha256")
        and bool(entry.get("renderer_update_acknowledged") or entry.get("renderer_update"))
        and _has_review_fields(entry)
    )


def compare_limitation_sets(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    acknowledgements: Any,
) -> tuple[bool, list[str]]:
    """Refuse silent movement toward a less-limited limitation state."""

    old = {obj["limitation_id"]: obj for obj in before}
    new = {obj["limitation_id"]: obj for obj in after}
    after_ids = set(new)
    entries = _ack_entries(acknowledgements)
    reasons: list[str] = []

    for old_id, old_obj in old.items():
        new_obj = new.get(old_id)
        if new_obj is None:
            if not any(_ack_removed(entry, old_id, after_ids) for entry in entries):
                reasons.append(f"removed limitation_id {old_id}")
            continue

        old_sev = _SEVERITY_RANK.get(str(old_obj.get("severity")))
        new_sev = _SEVERITY_RANK.get(str(new_obj.get("severity")))
        if old_sev is not None and new_sev is not None and new_sev > old_sev:
            if not any(_ack_transition(entry, old_obj, new_obj) for entry in entries):
                reasons.append(
                    f"{old_id}: severity moved toward less limitation "
                    f"{old_obj.get('severity')} -> {new_obj.get('severity')}"
                )

        old_state = _EVIDENCE_RANK.get(str(old_obj.get("evidence_state")))
        new_state = _EVIDENCE_RANK.get(str(new_obj.get("evidence_state")))
        if old_state is not None and new_state is not None and new_state > old_state:
            if not any(_ack_transition(entry, old_obj, new_obj) for entry in entries):
                reasons.append(
                    f"{old_id}: evidence_state moved toward less limitation "
                    f"{old_obj.get('evidence_state')} -> {new_obj.get('evidence_state')}"
                )

        state_same = (
            old_obj.get("severity") == new_obj.get("severity")
            and old_obj.get("evidence_state") == new_obj.get("evidence_state")
        )
        if state_same and old_obj.get("text_sha256") != new_obj.get("text_sha256"):
            if not any(_ack_renderer_update(entry, old_obj, new_obj) for entry in entries):
                reasons.append(f"{old_id}: rendered_text changed without state change or renderer acknowledgement")

    return not reasons, reasons


def pretty_counts(limitations: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Small helper for evidence/report generation."""

    out: dict[str, dict[str, int]] = {"kind": {}, "severity": {}, "evidence_state": {}, "limitation_class": {}}
    for obj in limitations:
        for field in out:
            key = str(obj.get(field))
            out[field][key] = out[field].get(key, 0) + 1
    return out


def publication_gate_refusals(limitations: list[dict[str, Any]]) -> list[str]:
    """Return page-gate refusal reasons for malformed validity-threatening limitations."""

    reasons: list[str] = []
    for obj in limitations or []:
        if obj.get("limitation_class") != LimitationClass.VALIDITY_THREATENING.value:
            continue
        linked = obj.get("linked_decision")
        if not isinstance(linked, dict):
            reasons.append(f"{obj.get('limitation_id')}: VALIDITY_THREATENING limitation has no linked_decision")
            continue
        missing = [key for key in ("action", "gate_id", "decision_state") if not linked.get(key)]
        if missing:
            reasons.append(
                f"{obj.get('limitation_id')}: linked_decision missing {', '.join(missing)}"
            )
    reasons.extend(_hazard_consumers.check_consumers({"limitations": limitations or []}))
    return reasons


def check_consumers(review: dict[str, Any], acknowledgements: Any = None) -> list[str]:
    """Return publication-gate refusal reasons for declared hazards with no consumer."""

    return _hazard_consumers.check_consumers(review, acknowledgements)
