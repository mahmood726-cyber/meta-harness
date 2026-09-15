"""Structured limitation objects for the legacy absent/banner surface.

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

from . import page as _page


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
    ROB_SPANCHECK = "ROB_SPANCHECK"
    SEARCH_PROVENANCE = "SEARCH_PROVENANCE"


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
    PROVISIONAL = "PROVISIONAL"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    RECORDED = "RECORDED"


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
    return {
        "limitation_id": f"topic:{review.get('slug', 'unknown')}:{suffix}",
        "kind": kind.value,
        "severity": severity.value,
        "claim_affected": claim_affected,
        "evidence_state": _enum_value(evidence_state),
        "source_fields": list(source_fields),
        "rendered_text": rendered,
        "text_sha256": _sha256(rendered),
    }


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
        "<p>This page is a REPLAY of that snapshot: re-running from the protocol SHA regenerates "
        "it byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present).</p>"
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


def _integrity_block(integrity: dict[str, Any]) -> str:
    retracted = integrity.get("retracted", [])
    return (
        f"<div class='absent'><strong>RETRACTED TRIAL POOLED:</strong> {_e(', '.join(retracted))} "
        "&mdash; this page must not stand until resolved.</div>"
    )


def _uoa_block(review: dict[str, Any], uoa: list[dict[str, Any]]) -> str:
    items = "; ".join(f"{_e(u.get('id'))} ({_e(u.get('design'))})" for u in uoa)
    sensitivity = _page._uoa_sensitivity(review, [u.get("id") for u in uoa])
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
    return (
        "<div class='absent'><strong>Unit-of-analysis caveat (disclosed, not adjusted).</strong> "
        f"{len(uoa)} pooled trial(s) use a cluster-randomized or cluster-period (policy) crossover "
        f"design: {items}. They are pooled from patient-level counts <strong>without applying a "
        "design effect</strong> (cluster ICC / cluster-period correlation), because that variance "
        "component is not reported in the source &mdash; these are CLUSTER-PERIOD policy crossovers, not "
        "within-person crossovers. <strong>Consequence:</strong> the true variance of these trials is "
        "larger than the patient-level calculation assumes, so their inverse-variance <strong>weight "
        "in the pool is OVERSTATED</strong> and the pooled confidence interval is <strong>too narrow"
        "</strong> (over-precise)."
        + sens_txt
        + " This is a stated limitation (a documented "
        "meta-analysis error class the harness flags but cannot correct without the missing variance "
        "component), not a silent simple-parallel pooling.</div>"
    )


def _funding_known(funding: dict[str, Any]) -> bool:
    typ = funding.get("type") or ""
    return (
        typ.startswith("industry")
        or typ == "mixed"
        or typ.startswith("public")
        or typ.startswith("non-profit")
        or bool(funding.get("note"))
    )


def _funding_block(fund: list[dict[str, Any]]) -> str:
    def _ord(item: dict[str, Any]) -> int:
        typ = item.get("type") or ""
        if typ.startswith("industry"):
            return 0
        if typ == "mixed":
            return 1
        if typ.startswith("public"):
            return 2
        if typ.startswith("declared") or typ.startswith("stated"):
            return 3
        return 4

    def _celltype(item: dict[str, Any]) -> str:
        return _e(item.get("type")) + (f"<br><em>{_e(item.get('note'))}</em>" if item.get("note") else "")

    rows = "".join(
        f"<tr><td>{_e(item.get('id'))}</td><td>{_celltype(item)}</td>"
        f"<td>{_e(item.get('scanned') or item.get('source'))}</td><td>{_e(item.get('span'))}</td></tr>"
        for item in sorted(fund, key=lambda item: _ord(item))
    )
    n_ind = sum(
        1
        for item in fund
        if (item.get("type") or "").startswith("industry") or item.get("type") == "mixed" or item.get("note")
    )
    n_ns_ft = sum(1 for item in fund if (item.get("type") or "").startswith("not stated (full text"))
    n_ns_ab = sum(1 for item in fund if (item.get("type") or "").startswith("not stated (abstract"))
    n_known = sum(1 for item in fund if _funding_known(item))
    n_unknown = len(fund) - n_known
    return (
        "<div class='absent'><strong>Funding / conflict-of-interest disclosure (per pooled "
        "trial, from source &mdash; disclosed, not adjusted).</strong> Industry-funded trials are a "
        "documented reporting-bias dimension (they tend to report more favourable results). For "
        "each pooled trial the funding source is classified from a verbatim statement in the "
        "committed source (full text preferred, abstract fallback), including an industry "
        "<em>drug-supply</em> tie in an otherwise independently funded trial: "
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
        "<table class='arms'><tr><th>Trial</th><th>Funding</th><th>Scanned</th>"
        f"<th>Verbatim statement</th></tr>{rows}</table></div>"
    )


def _arm_contrast_block(ac: dict[str, dict[str, Any]]) -> str:
    labels = {
        "verified": "randomised contrast verified",
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
        "<div class='absent'><strong>Randomised-contrast disclosure (per pooled trial, from the "
        "registry arm structure &mdash; disclosed, not an adjustment).</strong> Eligibility should test "
        "what actually DIFFERS between the randomised arms, not the mere presence of the drug word: "
        "a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same "
        "agent, randomising a different drug) is not a randomised comparison of it. For each pooled "
        "trial the randomised contrast is reconstructed from AACT <code>design_groups</code> + "
        f"<code>interventions</code>: <strong>{n_ver} of {len(ac)}</strong> pooled trials have a "
        "registry-confirmed contrast (the intervention of interest differs across arms)"
        + (f"; <strong>{n_bg} is background in every arm (flagged)</strong>" if n_bg else "")
        + ". A trial with no registry arm data, or coded under a class label / development code we "
        "cannot machine-match, is shown as <em>contrast unverified</em> &mdash; a VISIBLE fail-open state, "
        "never silently treated as verified. "
        "<table class='arms'><tr><th>Trial</th><th>Contrast status</th><th>Randomised difference</th>"
        f"</tr>{rows}</table></div>"
    )


def _rob_sensitivity_block(sens: dict[str, Any]) -> str:
    def _fmt(point: dict[str, Any] | None) -> str:
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
        low_cell = _fmt(low_only) + (
            "" if sens.get("low_only_informative")
            else " <em>(fewer trials than the full pool &mdash; see coverage)</em>"
        )
    lines.append(f"<tr><td>Low risk of bias only</td><td>{low_cell}</td></tr>")
    return (
        "<div class='absent'><strong>Does the result survive dropping the trials that are not "
        "low risk of bias?</strong> The primary outcome is re-pooled by risk-of-bias stratum "
        "with the identical estimator. "
        f"<strong>{sens.get('n_rob_rated')} of {sens.get('n_trials')}</strong> pooled trials have a risk-of-bias rating; "
        + ("no pooled trial is rated <em>high</em> risk (the registry-derived assessment does not "
           "reach 'high'), so the standard drop-high sensitivity is inert and the informative "
           "stratum is <em>low-only</em>. " if not sens.get("any_high") else "")
        + "An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials "
        "than the full pool reflects both risk of bias and assessment coverage &mdash; read the "
        "widened interval with that caveat, not as instability of the effect."
        f"<table class='arms'><tr><th>Stratum</th><th>Re-pooled estimate</th></tr>"
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
        rows.append(f"<tr><td>{_e(label)}</td><td>{mark}</td><td>{_e(value.get('basis',''))}</td></tr>")
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
    return (
        "<div class='absent'><strong>Overall certainty (provisional): "
        f"{_e(grade.get('certainty','').replace('_',' '))}</strong> "
        f"(starting from <em>high</em> for randomized trials, {grade.get('downgrades',0)} "
        f"downgrade(s)).{cap}"
        "<strong>PROVISIONAL:</strong> this is a machine-derived certainty &mdash; risk of bias "
        "uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, "
        "so a formal human GRADE assessment may differ. "
        "Risk of bias, inconsistency, imprecision and publication bias are computed from "
        "committed fields; <strong>publication bias is assessed from the registry ghost census, "
        "not funnel-plot asymmetry</strong> (which is unreliable at our small k). "
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
    return count


def build_limitations(review: dict[str, Any]) -> list[dict[str, Any]]:
    """Build one structured object per legacy page-level absent/banner block."""

    out: list[dict[str, Any]] = []

    def add(
        suffix: str,
        kind: LimitationKind,
        severity: Severity,
        claim: str,
        state: EvidenceState | str,
        fields: list[str],
        html: str,
    ) -> None:
        out.append(_object(review, suffix, kind, severity, claim, state, fields, html))

    inv = review.get("invalidation") or {}
    if inv.get("stale"):
        reasons = "".join(f"<li>{_e(item.get('detail'))}</li>" for item in inv.get("reasons", []))
        add(
            "overview:stale-topic",
            LimitationKind.STALE_TOPIC,
            Severity.BLOCKS_CLAIM,
            "current/settled topic result",
            EvidenceState.STALE,
            ["/invalidation/stale", "/invalidation/reasons"],
            "<div class='absent'><strong>STALE &mdash; this topic's result is not current.</strong> "
            "One or more dependent outputs on this page are known to be incomplete, superseded, or "
            f"unproven, so the result must not be read as a settled current estimate:<ul>{reasons}</ul></div>",
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
        add(
            "harms:none",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            "harms outcomes",
            EvidenceState.UNKNOWN,
            ["/outcomes"],
            _absent_block("no harms recorded"),
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
        add(
            f"{prefix}:result-absent",
            LimitationKind.DECLARED_ABSENT_SECTION,
            Severity.BLOCKS_CLAIM,
            f"outcome result: {outcome.get('name')}",
            _declared_absent_state(result),
            ["/outcomes/*/result/present", "/outcomes/*/result/reason"],
            _absent_block(rr),
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

    out: dict[str, dict[str, int]] = {"kind": {}, "severity": {}, "evidence_state": {}}
    for obj in limitations:
        for field in out:
            key = str(obj.get(field))
            out[field][key] = out[field].get(key, 0) + 1
    return out
