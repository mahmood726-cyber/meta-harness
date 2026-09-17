"""Deterministic tabbed-page renderer (RapidMeta-style).

render_page(review, neutral=False) is a PURE function of the review object: same
input -> byte-identical output. This makes the reproduction census meaningful.

Contract: every tab renders what the object holds; every ABSENCE is DECLARED, never
blank. A section/outcome is either present-with-content or {"present": False,
"reason": "..."} that renders a visible declared-absent block.

neutral=True renders a blinding-safe page for the blind judge: neutral chrome, and
the cross-reference "Comparator" tab is omitted (naming the comparator would reveal
which page is the harness's). Both the harness page and the comparator benchmark are
rendered by this same function so a judge cannot tell them apart by structure.
"""
from __future__ import annotations
from . import integration_prose as _integrated

from .topic_registry import topic_id
import collections
import html
import json
import re
from typing import Any

from . import manuscript as _manuscript_mod
from . import rob_sensitivity as _rob_sensitivity_mod
from . import claimgraph as _claimgraph_mod
from . import identity as _identity_mod
from . import propositions as _proposition_mod
from . import funding as _funding_mod
from . import scope_identity as _scope_identity_mod
from . import section_claims as _section_claims
from . import remainder_prose as _remainder

TABS = [
    ("overview", "Overview"),
    ("protocol", "Protocol"),
    ("search", "Search"),
    ("screening", "Screening"),
    ("outcomes", "Results"),
    ("harms", "Harms"),
    ("comparator", "Comparator"),
    ("riskofbias", "Risk of bias"),
    ("manuscript", "Manuscript"),
    ("reporting", "Reporting (PRISMA)"),
    ("reproduction", "Reproducibility"),
]
NEUTRAL_DROP = {"comparator"}
KNOWN_ITEM_RETRIEVAL_LABEL = "KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH"
TITLE_SEEDED_RETRIEVAL_LABEL = "TITLE-SEEDED RETRIEVAL — DISCOVERY-BIASED, NOT A SYSTEMATIC SEARCH"
HAND_WRITTEN_KEYWORD_SEARCH_LABEL = "HAND-WRITTEN KEYWORD SEARCH — NOT A REGISTERED CONCEPT SEARCH; NOT A SYSTEMATIC SEARCH"
RETRIEVAL_UNAUDITABLE_DISTINCTION = "an auditable screening ledger attached to an unauditable retrieval process"
RETRIEVAL_RETRACTION = "We retract any claim of a registry-first or systematic search for this topic."


def _e(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def _num(x: Any) -> str:
    if isinstance(x, float):
        return f"{round(x, 2):g}"  # consistent 2-dp display for effects/CIs (was .3g -> mixed decimals like 0.79 vs 0.914)
    return _e(x)


def _tau(x: Any) -> str:
    # RETRACTION #7 (round-2 sglt2-ckd): a rounded display must not imply a different value from the one used
    # downstream. tau2=0.00134 was shown as "0" by the 2-dp _num, and GRADE reads tau2==0 to decline an
    # inconsistency downgrade — so the display drove a judgement off a value it misrepresented. Show tau2 with
    # 3 significant figures, and mark a genuine non-zero that would round to 0.
    if not isinstance(x, (int, float)):
        return _e(x)
    if x == 0:
        return "0"
    return f"{x:.3g}" + (" (non-zero; not 0)" if 0 < x < 0.005 else "")


def _absent(section: Any):
    if section is None:
        return "not declared in the review object"
    if isinstance(section, dict) and section.get("present") is False:
        return section.get("reason") or "declared absent (no reason given)"
    return None


def _absent_block(reason: str) -> str:
    return f'<div class="absent"><strong>DECLARED ABSENT.</strong> {_e(reason)}</div>'


def _unrenderable_block(obj: dict[str, Any]) -> str:
    return (
        "<div class='absent'><strong>UNRENDERABLE claimgraph object.</strong> "
        f"Violation <code>{_e(obj.get('violation_code'))}</code>; "
        f"claim_id <code>{_e(obj.get('claim_id'))}</code>. "
        "The stale object's numbers and prose are suppressed.</div>"
    )


# ABSENCE-STATE ONTOLOGY (external audit, STATE root system): the per-trial `state` set in the pipeline
# is the authority for how a declared-absent trial is labelled — a machine-checkable field, not a guess
# off the reason string. Only NO_OUTCOME_DATA_IN_SOURCE licenses the strong "declared absent" claim (a
# statement about the TRIAL). The other states are statements about US (extraction/retrieval) or a
# deliberate refusal of a number that WAS found — none is evidence the outcome does not exist.
_ABSENCE_STATE_LABEL = {
    "OUTCOME_NOT_IN_SOURCE": "not in cached source -- no outcome sentence/effect found",
    "NO_OUTCOME_DATA_IN_SOURCE": "declared absent — no outcome data in the retrieved source",
    "EFFECT_PRESENT_ESTIMAND_CLASS_MISMATCH": "excluded on evidence -- effect present but wrong estimand class",
    "COUNTS_PRESENT_NOT_CORROBORATED": "not extracted -- arm counts present but percentage corroboration failed",
    "MULTI_ARM_UNRESOLVED": "excluded on evidence -- multi-arm contrast unresolved",
    "TIMEPOINT_MISMATCH": "excluded on evidence -- timepoint mismatch",
    "POPULATION_MISMATCH": "excluded on evidence -- population or analysis-set mismatch",
    "EXTRACTION_NOT_PERFORMED": "not extracted — the outcome's number IS in the source (extraction gap, not trial absence)",
    "SOURCE_NOT_RETRIEVED": "source not retrieved -- cached abstract text is missing",
    "EXTRACTION_DEBT": "extraction debt -- source-visible value shown below, not pooled",
    "KNOWN_REPORTED_NOT_YET_EXTRACTED": "extraction debt -- source-visible value shown below, not pooled",
    "RETRIEVED_INCOMPATIBLE_STRUCTURE": "retrieved but incompatible with the registered structure",
    "RETRIEVED_REFUSED_WITH_REASON": "retrieved and refused with a source-backed reason",
    "UNIT_MISMATCH_CYCLE_LEVEL": "retrieved but refused -- cycle-level/repeated-within-woman unit mismatch",
    "REFUSED_ON_EVIDENCE": "excluded on evidence — a number was found and deliberately not pooled (see reason)",
    "outcome_post_hoc_not_pooled": "excluded on evidence -- outcome was post hoc and not prespecified",
    "outcome_not_reported": "declared absent -- outcome not reported in the committed source",
    "ENGINE_CANNOT_CONSUME": "engine cannot consume this design -- variance model unavailable",
}

_HARM_ABSENCE_STATE_LABEL = {
    "NOT_RETRIEVED": "HM: source not retrieved",
    "RETRIEVED_OUTCOME_NOT_REPORTED": "HM: retrieved source does not report this harm",
    "RETRIEVED_INCOMPATIBLE_STRUCTURE": "HM: retrieved source reports harm in an incompatible structure",
    "RETRIEVED_REFUSED_WITH_REASON": "HM: retrieved source reports harm but row is refused with reason",
    "KNOWN_REPORTED_NOT_YET_EXTRACTED": "HM: harm is reported in the cached source but not yet extracted",
}


def _absent_label(reason, state=None) -> str:
    """Label a declared-absent trial. Prefer the explicit ontology `state` (machine-set in the pipeline);
    fall back to the legacy reason heuristic only for objects that predate the state field. External
    audit (C-EXTRACT-1): do NOT say "absent" when only the abstract was checked — the outcome may exist
    in the full text; and NEVER read a machine extraction-gap as evidence the trial lacks the outcome."""
    if state and state in _ABSENCE_STATE_LABEL:
        return _ABSENCE_STATE_LABEL[state]
    rl = (reason or "").lower()
    if any(w in rl for w in ("exclud", "wrong ", "estimand", "non-cardiac", "population", "per-protocol",
                             "per protocol", "completers", "different composite", "first-attack")):
        return "excluded (see reason)"
    if "abstract" in rl:
        return "not extracted — abstract only, full text not retrieved"
    return "not extracted (see reason)"


def _id_cell(t: dict[str, Any]) -> str:
    ident = t.get("id")
    effect_source = t.get("effect_source_id")
    if effect_source and effect_source != ident:
        return f"{_e(ident)}<br><span class='muted'>(effect from {_e(effect_source)})</span>"
    return _e(ident)


def _kv(rows) -> str:
    trs = "".join(f"<tr><th>{_e(k)}</th><td>{v if isinstance(v,str) and v.startswith('<') else _e(v)}</td></tr>" for k, v in rows)
    return f"<table class='kv'>{trs}</table>"


def _retrieval_value(x: Any) -> str:
    return "unknown" if x is None else _e(x)


def _retrieval_first(d: dict, keys: tuple[str, ...]) -> Any:
    for k in keys:
        if k in d and d.get(k) is not None:
            return d.get(k)
    return None


def _retrieval_cap_text(cap: dict | None) -> str:
    if not cap:
        return "none"
    return (f"{_e(cap.get('kind') or 'unknown')} "
            f"(n={_retrieval_value(cap.get('n'))}; remainder={_retrieval_value(cap.get('remainder'))})")


def _retrieval_state_text(src: dict) -> str:
    state = src.get("state")
    if state == "RAN_ERROR":
        return ("<strong>RAN_ERROR</strong>: attempted and FAILED — its zero is not observed, not absent. "
                f"Error: {_retrieval_value(src.get('error'))}")
    if state == "RAN_ZERO":
        return "<strong>RAN_ZERO</strong>: ran; nothing matched"
    if state == "NOT_RUN":
        return "<strong>NOT_RUN</strong>: not attempted"
    if state == "RAN_OK":
        return "<strong>RAN_OK</strong>: ran and returned records"
    if state == "RAN_UNRECORDED":
        return ("<strong>RAN_UNRECORDED</strong>: attempted by a pre-ledger fetch; its yield was never recorded, so "
                "neither a count nor a zero can be shown (legacy only — a live run may not carry this state)")
    return f"<strong>{_e(state)}</strong>"


def _retrieval_kind_label(kind: Any) -> str:
    if kind == "PUBMED_PMID_ENUMERATION":
        return "PMID enumeration — not a search; can retrieve only what it was told"
    return _e(kind)


def _retrieval_mode_label(mode: Any) -> str:
    if mode == "REFRESH":
        return "REFRESH: live search run on that date"
    if mode == "LEGACY_UNRECORDED":
        return ("LEGACY_UNRECORDED: a pre-ledger fetch; which query retrieved which record was not "
                "recorded; every record's found_by names this single source")
    return _e(mode)


def _retrieval_html(ret: dict) -> str:
    body = ("<h4>Retrieval snapshot</h4><div class='banner'><p>"
            + _remainder.receipt("snapshot", ret.get("snapshot") or {})
            + "</p><p>" + _remainder.replay_boundary() + "</p></div>")
    rc = ret.get("record_cap")
    if rc:
        retrieved = _retrieval_first(rc, ("retrieved", "n_retrieved", "records_retrieved", "before"))
        retained = _retrieval_first(rc, ("retained", "n_retained", "records_retained", "after"))
        n = _retrieval_first(rc, ("n", "cap", "record_cap"))
        remainder = _retrieval_first(rc, ("remainder", "not_screened", "n_not_screened"))
        body += ("<p class='note'>"
                 f"{_retrieval_value(retrieved)} records retrieved, {_retrieval_value(retained)} retained "
                 f"after the record cap (n={_retrieval_value(n)}); {_retrieval_value(remainder)} not screened"
                 "</p>")
    if ret.get("enumeration_only"):
        body += '<div class="absent">' + _integrated.limit('enumeration') + '</div>'
    rows = _section_claims.retrieval_rows(ret)
    if rows:
        body += ("<h4>Retrieval sources</h4>"
                 "<table class='recs'><tr><th>Kind</th><th>Query</th><th>Run date</th><th>State</th>"
                 "<th>hits -&gt; fetched -&gt; retained</th><th>Cap</th><th>Discovery-capable</th></tr>"
                 f"{rows}</table>")
    return body


def _retrieval_class_counts(rc: dict) -> dict[str, int]:
    basis = rc.get("basis") or []
    pmid = sum(1 for row in basis if row.get("kind") == "PMID_ENUMERATION")
    seeded = sum(1 for row in basis if row.get("kind") in (
        "TITLE_OR_NAME_SEEDED",
        "TITLE_ANCHORED",
        "NAME_SEEDED",
        "IDENTIFIER_SEEDED",
    ))
    free = sum(1 for row in basis if row.get("kind") == "FREE_TEXT_KEYWORD")
    return {"pmid": pmid, "seeded": seeded, "free": free}


def _retrieval_class_overview(rc: dict) -> str:
    counts = _retrieval_class_counts(rc)
    parts = ["<div class='absent'><strong>" + _e(rc.get("label")) + "</strong>"]
    if rc.get("retraction"):
        parts.append(" " + _e(rc.get("retraction")))
    if rc.get("distinction"):
        parts.append(" " + _e(rc.get("distinction")) + ".")
    parts.append(
        f" {_e(counts['pmid'])} PMID-enumeration queries; "
        f"{_e(counts['seeded'])} title/name-seeded queries; "
        f"{_e(counts['free'])} free-text keyword queries.</div>"
    )
    return "".join(parts)


def _retrieval_class_html(rc: dict) -> str:
    if not rc or not rc.get("label"):
        return ""
    block_class = "banner" if rc.get("retrieval_auditable") else "absent"
    body = (f"<h4>Retrieval class</h4><div class='{block_class}'><p>"
            + _remainder.receipt("retrieval_class", rc) + "</p></div>")
    rows = _section_claims.retrieval_basis_rows(rc)
    if rows:
        body += ("<table class='recs'><tr><th>Verbatim query</th><th>Kind</th><th>Features fired</th></tr>"
                 f"{rows}</table>")
    return body


def _search_provenance_html(rc: dict) -> str:
    sp = (rc or {}).get("search_provenance") or {}
    if not sp:
        return ""
    return "<div class='absent'>" + _remainder.receipt("search_provenance", sp) + "</div>"


def _ci(res) -> str:
    return f"{_num(res.get('estimate'))} ({res.get('scale')}), 95% CI {_num(res.get('ci_low'))}–{_num(res.get('ci_high'))}"


def _effect_label(res) -> str:
    # A single-trial result is not a pooled effect; label it honestly so the k=1 CI is not
    # read as a random-effects pooled interval.
    if res.get("effect_label"):
        return res.get("effect_label")
    return "Single-trial effect" if res.get("k") == 1 else "Pooled effect"


def _k2_pool_refusal_block(res: dict) -> str:
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


def _registered_ci_refusal_text(res: dict) -> str:
    ref = res.get("pooled_ci_refused") or {}
    return f"REFUSED ({_e(ref.get('code'))}): {_e(ref.get('detail'))}"


def _k2_ci_refusal_block(res: dict) -> str:
    ref = res.get("pooled_ci_refused") or {}
    return (
        "<div class='absent'><strong>Registered pooled CI REFUSED at k=2.</strong> "
        f"{_e(ref.get('detail'))} The point estimate may be displayed, but no pooled "
        "significance/null-crossing claim is emitted.</div>"
    )


def _effect_rows(res: dict) -> list[tuple[str, str]]:
    if res.get("pooled_ci_refused"):
        return [
            ("Pooled point estimate (registered CI refused)",
             f"{_num(res.get('estimate'))} ({_e(res.get('scale'))}); no pooled significance/null-crossing claim"),
            ("Registered PM/HKSJ CI", _registered_ci_refusal_text(res)),
        ]
    return [(_effect_label(res), _ci(res))]


def _common_effect_row(res: dict) -> tuple[str, str] | None:
    if res.get("ci_low_fixed") is None:
        return None
    txt = (f"{_num(res.get('estimate_fixed'))} ({res.get('scale')}), 95% CI "
           f"{_num(res.get('ci_low_fixed'))}-{_num(res.get('ci_high_fixed'))}")
    if res.get("fixed_heterogeneity_caveat"):
        txt += f" [{_e(res.get('fixed_heterogeneity_caveat'))}]"
    return ("Common-effect sensitivity (z-based; not the registered interval)", txt)


_ROB_SENS_REFUSED_HTML = "<h4>Risk-of-bias sensitivity (re-pooled with the same estimator)</h4><div class='absent'><strong>Does the result survive dropping the trials that are not low risk of bias?</strong> Not computed: the primary pooled row is REFUSED ({code}), so there is no pooled estimate to re-pool by risk-of-bias stratum. The per-trial rows and their risk-of-bias ratings are shown above; a stratified re-pool of a refused pool would be a number about nothing.</div>"



def _known_missing_sensitivity_panel(o: dict) -> str:
    from .page_claims import known_missing
    return known_missing(o)


# ---- tabs --------------------------------------------------------------------

def _transparency_counts(r):
    """Count claims on this page that carry a one-click resolvable source pointer (the countable
    transparency test). Mirrors scripts/transparency_score.py; kept compact for a one-line render."""
    total = ok = 0
    for o in r.get("outcomes", []) or []:
        for t in o.get("trials", []) or []:
            total += 1
            ok += 1 if (t.get("id") and t.get("source") and t.get("provenance")) else 0
        for a in o.get("declared_absent_trials", []) or []:
            total += 1
            ok += 1 if (a.get("id") and a.get("reason")) else 0
        if (o.get("result") or {}).get("k"):
            total += 1
            ok += 1 if all(t.get("id") and t.get("source") for t in (o.get("trials") or [])) else 0
    for tid, e in ((r.get("rob2") or {}).get("trials") or {}).items():
        total += 1
        doms = (e or {}).get("domains") or {}
        ok += 1 if (doms and all(isinstance(v, dict) and v.get("basis") for v in doms.values())) else 0
    rep = r.get("reproduction") or {}
    total += 1
    ok += 1 if ((rep.get("protocol_sha") or rep.get("sha")) and rep.get("failures") is not None) else 0
    comp = len((r.get("comparator") or {}).get("reported", []) or [])
    return ok, total, comp


def render_strands_section(d: dict) -> str:
    """Render a topic's declared strands (docs/<*>_strands.json content). Shared by the topic page
    (where the single pool is suppressed) and the index, so both surfaces show the SAME strands from
    the ONE artefact -- no categorical/state contradiction between two surfaces."""
    strands = (d or {}).get("strands") or []
    if not strands:
        return ""
    rows = []
    for s in strands:
        typed = _claimgraph_mod.strand_render(s)
        if typed is not None:
            rows.append("<li>" + typed + "</li>")
            continue
        pool = s.get("pool")
        if pool:
            sig = "crosses null" if pool.get("crosses_null") else "significant"
            sens = pool.get("common_effect_sensitivity") or {}
            senstxt = (f" <span class='note'>[common-effect sensitivity {_e(sens.get('effect'))} "
                       f"({_e(sens.get('ci_low'))}–{_e(sens.get('ci_high'))}), NOT the registered result]</span>"
                       if sens else "")
            res = (f"pooled {_e(pool.get('effect'))} ({_e(pool.get('ci_low'))}–{_e(pool.get('ci_high'))}), "
                   f"k={_e(pool.get('k'))}, HKSJ/PM &tau;&sup2;={_e(pool.get('tau2'))}, <strong>{sig}</strong>{senstxt}")
            if d.get('primary_strand'):
                res += f"; prediction interval {_e(pool.get('pi_low'))}–{_e(pool.get('pi_high'))}"
        elif not (s.get("members") or []):
            res = f"<code>{_e(s.get('status') or 'EMPTY')}</code>: {_e(s.get('reason') or 'no source-backed members declared')}"
        else:
            m = (s.get("members") or [{}])[0]
            res = f"{_e(m.get('trial'))} {_e(m.get('effect', m.get('crude_rr')))} ({_e(m.get('scale'))}), k=1 (single trial)"
        rows.append(f"<li><strong>Strand {_e(s.get('strand'))}</strong> — {_e(s.get('name'))} "
                    f"[<code>{_e(s.get('event_process'))}</code>]: {res}</li>")
    ref = d.get("refused_cross_endpoint_pool") or {}
    refline = (f"<p><strong>Refused cross-endpoint pool:</strong> {_e(ref.get('description'))} "
               f"If forced it would be {_e(ref.get('if_forced_it_would_be'))} — "
               f"<code>{_e(ref.get('verdict'))}</code>.</p>" if ref else "")
    if d.get('primary_strand'):
        return ("<div class='banner'><h3>Declared strands: primary and any delivery</h3>"
                f"<ul>{''.join(rows)}</ul></div>")
    return (f"<div class='banner'><h3>Declared strands (the single pool is suppressed; these are the "
            f"endpoint-clean decompositions)</h3><p>{_e(d.get('why_topic_is_suppressed'))}</p>"
            f"<ul>{''.join(rows)}</ul>{refline}"
            f"<p class='note'>Every effect source-verified; intervals from the canonical engine. The "
            f"compatibility key keeps strands apart; a cross-strand pool is refused, not computed.</p></div>")


def _identifier_scope_block(r):
    scope = r.get("identifier_scope") or {}
    verdict = scope.get("verdict")
    if not verdict:
        return ""
    if verdict in ("MATCH", "NOT_APPLICABLE"):
        return "<p>" + _remainder.receipt("identifier_scope", scope) + "</p>"
    if verdict == "DISCLOSED_SCOPE_AMENDMENT":
        amend = scope.get("amendment") or {}
        return ("<div class='banner'><strong>Identifier scope amendment.</strong> "
                f"Dated {_e(amend.get('date'))}: {_e(scope.get('detail'))} "
                f"<span class='muted'>Verdict: <code>{_e(verdict)}</code>.</span></div>")
    if verdict == "UNRESOLVED":
        unresolved = "; ".join(
            f"{x.get('trial')}={x.get('matched_intervention')}" for x in scope.get("unresolved", []) or []
        )
        detail = (f"{scope.get('detail')}: {unresolved}. This page must not be read as resolved until "
                  "the intervention declaration maps every included record.")
    else:
        detail = scope.get("detail")
    return ("<div class='absent'><strong>Identifier scope failure.</strong> "
            f"{_e(detail)} <span class='muted'>Verdict: <code>{_e(verdict)}</code>.</span></div>")


def _scope_identity_block(r):
    scope = r.get("scope_identity")
    block = _scope_identity_mod.rendered_block(scope)
    if _scope_identity_mod.requires_qualification(scope):
        block += "<p>" + _e(_scope_identity_mod.qualification_text(
            scope, _included_unit_counts(r)["trials"])) + ".</p>"
    return block


def _hazard_acknowledgements_block(r):
    rows = []
    seen = set()
    for obj in r.get("limitations") or []:
        if not isinstance(obj, dict):
            continue
        ack = obj.get("unwired_acknowledged")
        if not isinstance(ack, dict):
            continue
        key = (
            obj.get("limitation_id"),
            ack.get("signed_by"),
            ack.get("date"),
            ack.get("reason"),
            ack.get("tranche"),
        )
        if key in seen:
            continue
        seen.add(key)
        rows.append(
            "<tr>"
            f"<td><code>{_e(obj.get('limitation_id'))}</code></td>"
            f"<td>{_e(obj.get('kind'))}<br><code>{_e(obj.get('evidence_state'))}</code></td>"
            f"<td>{_e(obj.get('severity'))}</td>"
            f"<td>{_e(ack.get('reason'))}</td>"
            f"<td>{_e(ack.get('signed_by'))}<br>{_e(ack.get('date'))}<br><code>{_e(ack.get('tranche'))}</code></td>"
            "</tr>"
        )
    if not rows:
        return ""
    return (
        "<div class='hazard-acks'><h3>Hazard acknowledgements</h3>"
        "<p class='note'>These limitation objects are deliberately UNWIRED: no executable gate changes on "
        "the named state, so publication is allowed only because the reviewed acknowledgement is carried "
        "on the object.</p>"
        "<table class='arms'><tr><th>limitation</th><th>kind/state</th><th>severity</th>"
        "<th>acknowledgement</th><th>signed</th></tr>"
        + "".join(rows)
        + "</table></div>"
    )


def _stale_topic_overview(r):
    inv = r.get("invalidation") or {}
    if not inv.get("stale"):
        return ""
    reasons = "".join(f"<li>{_e(x.get('detail'))}</li>" for x in inv.get("reasons", []))
    prim_for_inv = _primary(r)
    kms = (prim_for_inv or {}).get("known_missing_sensitivity") or {}
    if not kms:
        return (
            "<div class='absent'><strong>STALE — this topic's result is not current.</strong> "
            "One or more dependent outputs on this page are known to be incomplete, superseded, or "
            f"unproven, so the result must not be read as a settled current estimate:<ul>{reasons}</ul></div>"
        )
    link = " See the <a href='#known-missing-sensitivity'>known-missing sensitivity panel</a>."
    change = (
        " Named, in-source missing evidence changes the CI null-crossing conclusion; the served "
        "conclusion is invalidated by that evidence."
        if kms.get("headline_conclusion_effect") in ("CHANGES_CI_NULL_CROSSING", "CHANGES_DIRECTION")
        else ""
    )
    return (
        "<div class='absent'><strong>STALE — this topic's result is not current.</strong> "
        "One or more dependent outputs on this page are known to be incomplete, superseded, or "
        f"unproven, so the result must not be read as a settled current estimate. {change}{link}<ul>{reasons}</ul></div>"
    )


def _stated_limitations(r):
    return (
        "<h3>Stated limitations</h3><ul class='limits'>"
        + '<li>' + _section_claims.boundary(r, 'small-k') + '</li>'
        + '<li>' + _section_claims.boundary(r, 'oa') + '</li>'
        + ((f"<li><strong>Comparator scope mismatch.</strong> {_e((r.get('comparator') or {}).get('scope',{}).get('note'))}</li>")
           if (r.get('comparator') or {}).get('scope', {}).get('scope_valid') is False else "")
        + ((f"<li><strong>Evidence base incomplete.</strong> {_e(r.get('evidence_base_caveat'))}</li>")
           if r.get('evidence_base_caveat') else "")
        + ''.join('<li>' + _integrated.limit(name) + '</li>' for name in ('sample', 'bias', 'snapshot'))
        + '<li>' + _section_claims.boundary(r, 'screening') + '</li></ul>')


def _overview(r, neutral):
    from .page_claims import overview
    migrated = overview(r, neutral)
    if migrated is not None:
        return migrated + (_stated_limitations(r) if not neutral else "")
    parts = [f"<h2>{_e(r.get('title'))}</h2>", f"<p class='q'>{_e(r.get('question'))}</p>"]
    # INVALIDATION PROPAGATION: a single STALE verdict poisons the headline. If any dependent output
    # is known incomplete/superseded/unproven, say so at the top rather than let the result read as
    # current. Each reason is named; the corpus index publishes the count as it falls.
    stale = _stale_topic_overview(r)
    if stale:
        parts.append(stale)
    parts.append(_identifier_scope_block(r))
    rc = (r.get("search") or {}).get("retrieval_class") or {}
    if rc.get("class") in ("KNOWN_ITEM_RETRIEVAL", "TITLE_SEEDED_RETRIEVAL", "HAND_WRITTEN_KEYWORD_SEARCH"):
        parts.append(_retrieval_class_overview(rc))
    parts.append(_scope_identity_block(r))
    if not neutral:
        parts.append(
            "<div class='banner'>This page offers <strong>greater auditability, not "
            "stronger evidence</strong>: every number traces to a committed source, every "
            "absence is declared, and any hand-edit breaks the reproduction census.</div>")
        parts.append(_hazard_acknowledgements_block(r))
    prim = _primary(r)
    if prim and _absent(prim) is None:
        res = prim.get("result") or {}
        if res.get("pool_refused"):
            parts.append("<h3>Primary outcome</h3>")
            parts.append(_k2_pool_refusal_block(res))
        elif res.get("suppressed_incompatible"):
            # FAIL CLOSED (audit 23): the overview summary must not present a suppressed-incompatible primary
            # as pooled — no "Trials pooled (k)", no "Pooled effect" row (even with the number popped, the
            # framing implies a pool). Show the suppression, defer per-trial estimates to Results.
            parts.append("<h3>Primary outcome</h3>")
            parts.append(
                "<div class='absent'><strong>Pooled result SUPPRESSED (estimand-incompatible).</strong> "
                f"{_e(res.get('suppressed_reason'))} <em>Estimand classes: "
                f"{_e(' + '.join((res.get('estmeasure') or {}).get('canonicals', [])))}; the "
                f"{_e(res.get('k'))} eligible trials are shown individually in Results, not pooled.</em></div>")
            # DECLARED STRANDS: show the same endpoint-clean decomposition the index shows, so the topic
            # page does not render a bare refusal while the index renders four strands for the same review.
            if r.get("strands"):
                parts.append(render_strands_section(r["strands"]))
        elif _absent(res) is None:
            parts.append("<h3>Primary outcome</h3>")
            pooled = _pooled_ids(prim)
            k = res.get("k")
            kdisp = f"{k} — {'; '.join(pooled)}" if pooled else k
            has_units = _has_publication_units(r)
            inc_counts = _included_unit_counts(r)
            count_noun = "trial family" if has_units else "trial"
            recon = None
            if r.get('family_count_chain'):
                from .trial_family import count_sentence
                recon = count_sentence(r['family_count_chain'])
            elif inc_counts["trials"] is not None and k is not None and isinstance(k, int):
                scope_identity = r.get("scope_identity") or {}
                scoped = _scope_identity_mod.requires_qualification(scope_identity)
                if inc_counts["trials"] != k:
                    absent_counts = _outcome_unit_counts(prim, has_units=has_units)["absent"]
                    if scoped:
                        prefix = _scope_identity_mod.qualification_text(scope_identity, inc_counts["trials"])
                    else:
                        prefix = f"{_identity_mod.count_phrase(inc_counts, count_noun)} met P/I/C/design (screening)"
                    recon = (f"{prefix}; {k} reported this "
                             f"outcome with an extractable number and were pooled; the remaining "
                             f"{_identity_mod.count_phrase(absent_counts, count_noun)} are listed as declared-absent in Results (they were "
                             f"included but reported no poolable value for this outcome).")
                else:
                    if scoped:
                        recon = _scope_identity_mod.qualification_text(scope_identity, inc_counts["trials"])
                    elif has_units:
                        recon = (f"all {_identity_mod.count_phrase(inc_counts, count_noun)} reported this outcome and were "
                                 f"pooled (screening count = k).")
                    else:
                        label = "trial" if inc_counts["trials"] == 1 else "trials"
                        recon = (f"all {inc_counts['trials']} screened-in {label} reported this outcome and were "
                                 f"pooled (screening count = k).")
            dc = prim.get("design_consumption") or res.get("design_consumption") or {}
            rows = [
                ("Outcome", prim.get("name")),
                ("Estimand", res.get("scale") or prim.get("estimand")),
                ("Estimand decision", _estimand_decision_text(prim)),
            ]
            if dc.get("design_refused"):
                rows.append(("Design-consumption state", dc.get("headline")))
            rows.append(("Trials pooled (k)", kdisp))
            if recon:
                rows.append(("Screened-in → pooled", recon))
            rows.extend(_effect_rows(res))
            if res.get("ci_low_fixed") is not None:
                rows.append(_common_effect_row(res))
            if res.get("pi_low") is not None:
                rows.append(("Prediction interval", f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}"))
            if res.get("tau2") is not None:
                rows.append(("Between-study τ²", _tau(res.get("tau2"))))
            rows.append(("Method", prim.get("method") or r.get("method_declared")))
            parts.append(_kv(rows))
            parts.append(_known_missing_sensitivity_panel(prim))
    if not neutral:
        _tok, _ttot, _tcomp = _transparency_counts(r)
        if _ttot:
            _pct = round(100 * _tok / _ttot)
            parts.append(
                "<h3>Transparency (independently checkable)</h3>"
                f"<p><strong>{_e(_tok)} of {_e(_ttot)} numerical claims on this page ({_pct}%) carry a source "
                "IDENTIFIER</strong> (a PMID/NCT/span/field). <strong>RETRACTED claim (round-2):</strong> we "
                "previously called these 'one-click sources' a reader can open — that is not verified: the "
                "identifiers are NOT rendered as resolving hyperlinks, and at least one PMCID was found to "
                "point to an unrelated article. Until every identifier is fetched and confirmed to resolve to "
                "the cited work, this is a count of identifiers present, not of sources that resolve. Each "
                "pooled number carries its PMID/NCT and verbatim span; each declared-absent trial its reason; "
                "each risk-of-bias domain the field it read; the reproduction its protocol SHA and replay. "
                f"The published comparator exposes {_e(_tcomp)} such claim(s) — its reported estimate(s) with "
                "one citation; its per-trial inputs are not machine-exposed. "
                "<span class='muted'>Score: scripts/transparency_score.py (committed docs/transparency.json).</span></p>")
        parts.append(_stated_limitations(r))
    return "".join(parts)


def _primary(r):
    for o in r.get("outcomes", []) or []:
        if o.get("primary"):
            return o
    outs = r.get("outcomes") or []
    return outs[0] if outs else None


def _pooled_ids(o):
    """Human labels+ids of the trials actually pooled for this outcome, so a k is never
    shown container-only (a k with no trials named is the container-vs-contents defect)."""
    ids = []
    for t in o.get("trials", []) or []:
        lbl, idv = t.get("label"), t.get("id")
        ids.append(f"{lbl} ({idv})" if lbl and str(lbl) != str(idv) else str(idv))
    return ids


def _has_publication_units(r):
    return bool(r.get("publication_units"))


def _included_unit_counts(r):
    if _has_publication_units(r):
        return _identity_mod.included_counts(r)
    n = _n_included(r) or 0
    return {"trials": n, "publications": n}


def _outcome_unit_counts(o, *, has_units=False):
    if has_units:
        return _identity_mod.outcome_counts(o)
    n_pool = len(o.get("trials") or [])
    n_abs = len(o.get("declared_absent_trials") or [])
    return {
        "pooled": {"trials": n_pool, "publications": n_pool},
        "absent": {"trials": n_abs, "publications": n_abs},
    }


def _n_included(r):
    recs = ((r.get("screening") or {}).get("records")) or []
    return sum(1 for x in recs if x.get("decision") == "include") if recs else None


def _protocol(r, neutral):
    p = r.get("protocol")
    reason = _absent(p)
    if reason:
        return _absent_block(reason)
    from .remainder_prose import protocol_metadata
    body = protocol_metadata(r, neutral)
    body += _eligibility_chain_block(r)
    controls = p.get("control_expectations") or []
    for ctrl in controls:
        if ctrl.get("state") == "UNRENDERABLE":
            body += (
                "<div class='absent'><strong>UNRENDERABLE protocol control expectation.</strong> "
                f"{_e(ctrl.get('control'))}. {_e(ctrl.get('reason'))}</div>"
            )
    return body


def _search(r, neutral):
    s = r.get("search")
    reason = _absent(s)
    if reason:
        return _absent_block(reason)
    from . import section_claims
    body = section_claims.search_metadata(r)
    if s.get("retrieval"):
        body += _retrieval_html(s["retrieval"])
    ss = s.get("source_status") or {}
    if ss:
        body += "<h4>Source status (which adapters ran)</h4><p>" + _remainder.receipt("source_status", ss) + "</p>"
    if s.get("retrieval_class"):
        body += _retrieval_class_html(s["retrieval_class"])
        body += _search_provenance_html(s["retrieval_class"])
    rc = s.get("recall")
    if rc and rc.get("known"):
        body += '<h4>Positive-control recovery (NOT systematic-review recall)</h4><p>' + _integrated.recorded('recall', rc) + '</p><p>' + _integrated.limit('recall') + '</p>'
    g = s.get("ghost")
    if g and g.get("enumerated"):
        body += '<h4>Registry landscape</h4><p>' + _integrated.recorded('ghost', g) + '</p><p>' + _integrated.limit('ghost') + '</p>'
    for src in s.get("sources", []) or []:
        body += f"<h4>{_e(src.get('name'))}</h4>"
        for index, q in enumerate(src.get("queries", []) or []):
            body += f"<pre class='query'>{_section_claims.query_render(src, index)}</pre>"
    return body


def _trial_families(r):
    from .trial_family import count_sentence
    nodes = r.get('trial_families')
    if nodes is None:
        return ''
    rows = []
    for f in nodes:
        reports = '; '.join(x['report_id']+': '+x['role'] for x in f['reports'])
        arms = '; '.join(str(a.get('label',{}).get('value') or a['arm_id']) for a in f['arms']) or f['arm_absence_code']
        contrasts = '; '.join(c['drug']+' ('+' / '.join(c['arm_ids'])+')' for c in f['randomised_contrasts']) or 'NOT_PROVEN'
        life = '; '.join(k+': '+str(v.get('value') or v.get('absence_code')) for k,v in sorted(f['lifecycle'].items()))
        statuses = '; '.join(s['outcome']+': '+', '.join(k+'='+s[k]['state'] for k in
                            ('prospectively_specified','measured','reported','extractable','in_primary_pool')) for s in f['outcome_status'])
        rows.append('<tr>'+''.join('<td>'+_e(v)+'</td>' for v in
                    (f['family_id'], ', '.join(f['aliases']['acronym']), reports, arms, contrasts,
                     f['eligibility']['state'], life, statuses))+'</tr>')
    return ('<section id="trial-families"><h4>Trial families</h4><p class="family-count-chain">'
            +_e(count_sentence(r['family_count_chain']))+'</p><div style="overflow-x:auto"><table class="recs"><thead><tr>'
            +''.join('<th>'+v+'</th>' for v in ('Family ID','Acronym','Reports by role','Arms','Contrasts','Eligibility','Lifecycle','Per-outcome status'))
            +'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></section>')


def _screening(r, neutral):
    s = r.get("screening")
    reason = _absent(s)
    if reason:
        return _absent_block(reason)
    recs = s.get("records", []) or []
    from . import section_claims
    # Typed table authority: ledger projections are explicitly labelled as such.
    head = '<tr>' + ''.join('<th>' + _e(field.replace('_', ' ').capitalize()) + '</th>'
                           for field in section_claims.screening_fields(r)) + '</tr>'
    rows = section_claims.screening_rows(r)
    integ = r.get("integrity")
    integ_html = ""
    if integ:
        integ_html = '<p>' + _integrated.recorded('integrity', integ) + '</p><p>' + _integrated.limit('integrity') + '</p>'
    # Do not conflate refusal, missing extraction and demonstrated source absence.
    flow = '<h4>Study selection flow (PRISMA 2020)</h4>' + section_claims.selection_flow(r)
    if r.get('family_count_chain'):
        flow += '<p>' + _integrated.recorded('family_count_chain', r['family_count_chain']) + '</p>' + _trial_families(r)
    dual = s.get("dual")
    if dual:
        flow += '<h4>Rule screening agreement</h4><p>' + _integrated.recorded('dual', dual) + '</p><p>' + _integrated.limit('dual') + '</p>'
        ma = dual.get("model_adjudication")
        if ma:
            fl = ma.get("flags", [])
            flag_txt = ("; ".join(f"{f['id']} (served {f['served']}, model {f['model']}: {f['rationale']})" for f in fl)
                        if fl else "none — the model agrees with the served rule screener on all of them")
            flow += ("<h5>Independent model adjudication of the disagreements</h5>"
                     f"<p>A capable model (different information + method than the two correlated rule sets) "
                     f"adjudicated {_e(ma.get('n'))} content-bearing disagreements; it agrees with the served "
                     f"rule screener on <strong>{_e(ma.get('agree_with_served'))}/{_e(ma.get('n'))}</strong>. "
                     f"{_e(ma.get('note'))} Flags: {_e(flag_txt)}</p>")
    body = (_identifier_scope_block(r) + flow + integ_html +
            f"<table class='recs'>{head}{rows}</table>")
    pc = s.get("positive_control")
    nc = s.get("negative_control")
    if pc or nc:
        body += "<h4>Controls</h4><p>" + _remainder.receipt("controls",
            {"positive_control": pc, "negative_control": nc}) + "</p>"
    return body


def _unit_label(unit):
    if unit == "prespecified_subgroup":
        return "pre-specified subgroup"
    if unit == "post_hoc_subgroup":
        return "post-hoc subgroup"
    return "trial"


def _evidence_unit_summary(o):
    trials = o.get("trials") or []
    if not trials or all((t.get("evidence_unit") or "trial") == "trial" for t in trials):
        return None
    counts = collections.Counter((t.get("evidence_unit") or "trial") for t in trials)
    bits = []
    if counts.get("trial"):
        bits.append(f"{counts['trial']} trial" + ("" if counts["trial"] == 1 else "s"))
    for unit in ("prespecified_subgroup", "post_hoc_subgroup"):
        group = [t for t in trials if t.get("evidence_unit") == unit]
        if not group:
            continue
        details = sorted({t.get("evidence_unit_detail") for t in group if t.get("evidence_unit_detail")})
        if len(group) == 1 and details:
            bits.append(f"1 {_unit_label(unit)} of {details[0]}")
        else:
            bits.append(f"{len(group)} {_unit_label(unit)}" + ("" if len(group) == 1 else "s"))
    return " + ".join(bits)


def _k_display(o):
    k = (o.get("result") or {}).get("k")
    eu = _evidence_unit_summary(o)
    return f"{k} ({eu})" if eu and k is not None else k


def _common_effect_label(o):
    if _evidence_unit_summary(o):
        return f"Common-effect CI (k={_k_display(o)} sensitivity)"
    return "Common-effect CI (k=2 sensitivity)"


def _estimand_decision_text(o):
    d = o.get("estimand_decision") or {}
    if not d:
        return None
    text = (f"{d.get('decision')}: {d.get('rule')} Target scale {d.get('target_scale')}; "
            f"declared {d.get('declared_estimand')}.")
    if d.get("served_scale_changed"):
        text += f" Served scale changed because {d.get('reason')}."
    return text


def _compat_dimension_text(dim):
    if not dim:
        return None
    vals = dim.get("values") or []
    if vals == ["not_stated"]:
        return None
    per = dim.get("per_trial") or []
    by_val = collections.defaultdict(list)
    for item in per:
        by_val[str(item.get("value"))].append(str(item.get("trial")))
    bits = []
    for val in vals:
        labs = ", ".join(x for x in by_val.get(str(val), []) if x)
        bits.append(f"{val}" + (f" ({labs})" if labs else ""))
    prefix = "matched" if dim.get("matched") else "heterogeneous"
    return f"{prefix}: " + "; ".join(bits)

def _alternative_label(alt):
    if alt.get("effect") is not None:
        txt = (f"{_num(alt.get('effect'))} ({_e(alt.get('scale'))}), 95% CI "
               f"{_num(alt.get('ci_low'))}-{_num(alt.get('ci_high'))}")
    elif alt.get("ai") is not None:
        txt = (f"{_e(alt.get('ai'))}/{_e(alt.get('n1i'))} vs "
               f"{_e(alt.get('ci'))}/{_e(alt.get('n2i'))}"
               + (f"; implied RR {_num(alt.get('implied_rr'))}" if alt.get("implied_rr") is not None else ""))
    elif alt.get("mean1") is not None:
        txt = (f"{_num(alt.get('mean1'))}+/-{_num(alt.get('sd1'))} (n={_e(alt.get('nc1'))}) vs "
               f"{_num(alt.get('mean2'))}+/-{_num(alt.get('sd2'))} (n={_e(alt.get('nc2'))})")
    elif alt.get("e1i") is not None:
        txt = f"{_e(alt.get('e1i'))}/{_num(alt.get('t1i'))} vs {_e(alt.get('e2i'))}/{_num(alt.get('t2i'))}"
    else:
        txt = "unclassified candidate"
    reason = f"; {_e(alt.get('not_selected_reason'))}" if alt.get("not_selected_reason") else ""
    span = f" <span class='muted'>{_e(alt.get('source_span'))}</span>" if alt.get("source_span") else ""
    return f"{_e(alt.get('derivation'))}: {txt}{reason}.{span}"


def _eligibility_chain_block(r):
    ec = r.get("eligibility_chain") or {}
    if not ec:
        return ""
    violations = ec.get("violations") or []
    contract = ec.get("contract") or {}
    agreed = ", ".join(contract.get("agreed_dimensions") or []) or "none"
    state_class = "absent" if violations else "note"
    body = ("<h4>Executable eligibility chain</h4>"
            f"<div class='{state_class}'><strong>Eligibility is checked as one chain:</strong> "
            "protocol criteria, executable screening config, compatibility key, and each pooled "
            "trial's own values. A failure here means the page is not renderable as an admissible "
            "pooled claim until the protocol/config/trial-set decision is resolved. "
            f"Agreed dimensions: {_e(agreed)}.</div>")
    if violations:
        rows = []
        for v in violations:
            rows.append(
                f"<tr><td><code>{_e(v.get('code'))}</code></td>"
                f"<td>{_e(v.get('dimension'))}</td><td>{_e(v.get('trial') or v.get('trial_id') or '')}</td>"
                f"<td>{_e(v.get('detail') or v.get('sentence') or '')}</td></tr>"
            )
        body += ("<table class='recs'><tr><th>Code</th><th>Dimension</th><th>Trial</th><th>Detail</th></tr>"
                 + "".join(rows) + "</table>")
    return body


def _compat_direction_block(o):
    audit = o.get("compat_direction") or {}
    dims = audit.get("dimensions") or []
    if not dims:
        return ""
    rows = []
    for dim in dims:
        underlying = dim.get("underlying") or {}
        vals = ", ".join(str(x) for x in (underlying.get("values") or []))
        if not vals and underlying.get("missing_trials"):
            vals = "not derivable: " + ", ".join(str(x) for x in underlying.get("missing_trials") or [])
        rows.append(
            "<tr><td>{}</td><td><code>{}</code></td><td>{}</td></tr>".format(
                _e(dim.get("label") or dim.get("dimension")),
                _e(dim.get("key_direction")),
                _e(vals),
            )
        )
    return (
        "<h5>Compatibility direction audit</h5><table class='arms'>"
        "<tr><th>Dimension</th><th>Direction</th><th>Underlying values</th></tr>"
        + "".join(rows)
        + "</table>"
    )


def _trial_inputs(o):
    rows = []
    for t in o.get("trials", []) or []:
        from .page_claims import provenance_trial
        migrated = provenance_trial(t, o)
        if migrated is not None:
            rows.append(migrated)
            continue
        if t.get("ai") is not None:
            inp = f"{_e(t.get('ai'))}/{_e(t.get('n1i'))} vs {_e(t.get('ci'))}/{_e(t.get('n2i'))} (events/n)"
        elif t.get("e1i") is not None:
            inp = (f"{_e(t.get('e1i'))}/{_num(t.get('t1i'))} vs {_e(t.get('e2i'))}/{_num(t.get('t2i'))} "
                   "(events/person-time)")
        elif t.get("mean1") is not None:
            inp = (f"{_num(t.get('mean1'))}±{_num(t.get('sd1'))} (n={_e(t.get('nc1'))}) vs "
                   f"{_num(t.get('mean2'))}±{_num(t.get('sd2'))} (n={_e(t.get('nc2'))}) (mean±SD)")
        elif t.get("effect") is not None:
            # Label each trial with ITS OWN reported scale (the extractor tags HR/RR/IRR from the
            # source), NOT the topic's target estimand — otherwise an HR 0.80 prints as "0.80 (RR)".
            inp = f"{_num(t.get('effect'))} ({_e(t.get('scale') or o.get('estimand'))}), 95% CI {_num(t.get('ci_low'))}–{_num(t.get('ci_high'))}"
        else:
            inp = "—"
        ec = t.get("endpoint_counts") or {}
        if ec and t.get("effect") is not None:
            inp += (f"; endpoint counts {_e(ec.get('ai'))}/{_e(ec.get('n1i'))} vs "
                    f"{_e(ec.get('ci'))}/{_e(ec.get('n2i'))}")
        # VERIFIED badge (rendered, not assumed): does this pooled number's digits appear in the
        # committed source? verified / verified (hand-checked, AACT-derived) / NOT YET.
        # A legacy verification label is not a located, digest-backed FACT.
        # Keep the number visible, but let the graph determine its class mark.
        fact_status = _claimgraph_mod.verify_fact(t)
        vst = t.get("verified") if fact_status["verified"] else None
        if vst == "verified":
            src = "<span class='vok' title='" + _e(t.get("verify_basis", "")) + "'>✓ verified against source</span><br>" + _e(t.get("source"))
        elif vst == "verified_handchecked":
            src = "<span class='vok' title='" + _e(t.get("verify_basis", "")) + "'>✓ verified (AACT-derived, cross-checked)</span><br>" + _e(t.get("source"))
        elif vst == "not-yet":
            src = "<span class='vno' title='" + _e(t.get("verify_basis", "")) + "'>⚠ NOT YET verified against source</span><br>" + _e(t.get("source"))
        else:
            src = _e(t.get("source"))
        inp = _claimgraph_mod.fact_render(dict(t, scale=t.get("scale") or o.get("estimand"))) + "<br>" + inp
        cs = t.get("cross_source")
        if cs:
            bits = []
            if cs.get("pooled_effect_for_endpoint_match") is not None and cs.get("ctgov_rr") is not None:
                bits.append(
                    f"pooled {cs.get('pooled_scale_for_endpoint_match') or 'effect'} "
                    f"{cs.get('pooled_effect_for_endpoint_match')} vs "
                    f"{cs.get('registry_effect_label') or 'CT.gov registry value'} {cs.get('ctgov_rr')}"
                )
            elif cs.get("abstract_rr") is not None and cs.get("ctgov_rr") is not None:
                bits.append(f"abstract RR {cs['abstract_rr']} vs CT.gov RR {cs['ctgov_rr']}")
            elif cs.get("ctgov_rr") is not None:
                bits.append(f"CT.gov RR {cs['ctgov_rr']}")
            meta = []
            if cs.get("registry_measure_type"):
                meta.append(f"type {cs.get('registry_measure_type')}")
            if cs.get("registry_selected_timepoint") or cs.get("registry_timeframe"):
                meta.append("timepoint " + str(cs.get("registry_selected_timepoint") or cs.get("registry_timeframe")))
            if cs.get("registry_population"):
                meta.append("population " + str(cs.get("registry_population")))
            if cs.get("corroborates_endpoint"):
                # IDENTICAL_ENDPOINT only: CT.gov structured result may corroborate the pooled row.
                src += (f"<div class='xsrc'><em>second source (✓ corroborated):</em> "
                        + (_e("; ".join(bits) + ". ") if bits else "")
                        + (_e("; ".join(meta) + ". ") if meta else "")
                        + _e(cs.get("note", "")) + "</div>")
            elif cs.get("agree") is False:
                src += (f"<div class='xsrc'><em>second source (⚠ DISCREPANCY):</em> "
                        + (_e("; ".join(bits) + ". ") if bits else "")
                        + (_e("; ".join(meta) + ". ") if meta else "")
                        + _e(cs.get("note", "")) + "</div>")
            else:
                verdict = cs.get("endpoint_match") or cs.get("second_source_verdict") or "SECOND_SOURCE_NOT_CHECKABLE"
                src += (f"<div class='xsrc'><em>second source ({_e(verdict)}):</em> "
                        + (_e("; ".join(bits) + ". ") if bits else "")
                        + (_e("; ".join(meta) + ". ") if meta else "")
                        + _e(cs.get("endpoint_match_reason") or cs.get("note", "")) + "</div>")
        j = t.get("identity_judgment")
        if j:
            # Model-derived outcome-identity judgment (checkable, 5 fields). It admitted this
            # CT.gov measure as THE review's outcome; it supplies no number.
            src += ("<div class='ident'><em>outcome-identity check (model-derived):</em> "
                    f"population <b>{_e(j.get('candidate_population'))}</b>; "
                    f"timepoint <b>{_e(j.get('candidate_timepoint'))}</b>; "
                    f"definition <b>{_e(j.get('candidate_definition'))}</b>; "
                    f"is-match <b>{_e(j.get('is_match'))}</b> — {_e(j.get('rationale'))}</div>")
        te = t.get("target_endpoint_class")
        if te:
            bits = [str(te)]
            if t.get("target_endpoint_source_rank"):
                bits.append("source rank: " + str(t.get("target_endpoint_source_rank")))
            if t.get("near_match_reason"):
                bits.append("near-match reason: " + str(t.get("near_match_reason")))
            comps = t.get("target_endpoint_components") or []
            if comps:
                bits.append("components: " + "; ".join(str(x) for x in comps))
            if t.get("results_known_at_rule_time"):
                bits.append("rule timing: applied after results were known")
            src += "<div class='ident'><em>target endpoint selector:</em> " + _e("; ".join(bits)) + "</div>"
            alts = t.get("target_endpoint_alternatives") or []
            if alts:
                items = []
                for a in alts[:4]:
                    label = a.get("registry_title") or a.get("source_type") or a.get("candidate_id")
                    detail = str(a.get("target_endpoint_class") or "")
                    if a.get("extra_components"):
                        detail += " extra: " + ", ".join(a.get("extra_components") or [])
                    if a.get("missing_components"):
                        detail += " missing: " + ", ".join(a.get("missing_components") or [])
                    items.append(f"<li>{_e(label)} [{_e(detail)}]</li>")
                src += ("<div class='ident'><em>endpoint sensitivity alternatives, not pooled:</em>"
                        f"<ul>{''.join(items)}</ul></div>")
            rp = t.get("registered_primary_selection_rule")
            if rp:
                src += ("<div class='ident'><em>multiple registered primaries:</em> "
                        f"{_e(rp.get('n_registered_primaries_in_family'))} in outcome family; "
                        f"{_e(rp.get('rule'))}; rule timing: applied after results were known.</div>")
        # DERIVATION provenance: is this the trial's OWN reported effect, or a harness reconstruction
        # from arm-level data? Both legitimate; labelling prevents 'the trial's own effect' on a number
        # the harness computed (the melatonin -17.4 defect).
        _der = t.get("derivation")
        if _der == "reconstructed":
            inp += " <span class='muted' title='effect computed by the harness from arm-level data, not the trial-reported effect'>· harness-reconstructed</span>"
        elif _der == "reported":
            inp += " <span class='muted' title='the effect+CI reported by the source'>· source-reported</span>"
        cc_state = t.get("consumer_consistency_state")
        if cc_state:
            src += ("<div class='xsrc'><em>consumer-consistency:</em> "
                    f"{_e(cc_state)}"
                    + (f" - {_e(t.get('source_warning'))}" if t.get("source_warning") else "")
                    + "</div>")
        if t.get("selection_rule"):
            inp += f" <span class='muted' title='source hierarchy selector rule'>&middot; {_e(t.get('selection_rule'))}</span>"
        if t.get("alternatives"):
            src += ("<div class='ident'><em>source-hierarchy alternatives not selected:</em><ul>"
                    + "".join(f"<li>{_alternative_label(a)}</li>" for a in t.get("alternatives") or [])
                    + "</ul></div>")
        if t.get("source_hierarchy_limitations"):
            src += ("<div class='ident'><em>source-hierarchy limitation:</em><ul>"
                    + "".join(
                        f"<li><code>{_e(l.get('code'))}</code>: {_e(l.get('reason'))} "
                        f"<span class='muted'>{_e(l.get('citation'))}</span></li>"
                        for l in t.get("source_hierarchy_limitations") or []
                    )
                    + "</ul></div>")
        dk = t.get("design") or {}
        if dk:
            basis = "; ".join(b.get("span", "") for b in (dk.get("basis") or []) if b.get("span"))
            corr = dk.get("correlation_handling") or {}
            decision = dk.get("design_action") or {}
            design_label = "UNPROVEN" if decision.get("action") == "DESIGN_UNPROVEN" else dk.get("design")
            src += ("<div class='ident'><em>design key:</em> "
                    f"{_e(design_label)} / unit {_e(dk.get('unit_of_randomisation'))}; "
                    f"estimator {_e(dk.get('estimator_source'))}; "
                    f"correlation handling {_e(corr.get('method'))}; "
                    f"action {_e(decision.get('action'))}"
                    + (f" <span class='muted'>{_e(basis)}</span>" if basis else "")
                    + "</div>")
        details = []
        if t.get("evidence_unit"):
            ev = _unit_label(t.get("evidence_unit"))
            if t.get("evidence_unit_detail"):
                ev += f" of {t.get('evidence_unit_detail')}"
            details.append(f"evidence unit: {ev}")
        if t.get("prior_disease_stage"):
            details.append(f"prior disease stage: {t.get('prior_disease_stage')}")
        if t.get("background_therapy"):
            details.append(f"background therapy: {t.get('background_therapy')}")
        if t.get("endpoint_definition"):
            details.append(f"endpoint definition: {t.get('endpoint_definition')}")
        if t.get("follow_up_window"):
            details.append(f"follow-up window: {t.get('follow_up_window')}")
        if t.get("analysis_set"):
            details.append(f"analysis set: {t.get('analysis_set')}")
        if t.get("effect_model_class"):
            details.append(f"effect-model class: {t.get('effect_model_class')}")
        if t.get("source_label"):
            details.append(f"source label: {t.get('source_label')}")
        if t.get("background_lifestyle_intensity"):
            details.append(f"background lifestyle intensity: {t.get('background_lifestyle_intensity')}")
        if t.get("treatment_strategy"):
            details.append(f"treatment strategy: {t.get('treatment_strategy')}")
        if t.get("clomifene_status"):
            details.append(f"clomifene status: {t.get('clomifene_status')}")
        if t.get("dose_regimen"):
            details.append(f"dose regimen: {t.get('dose_regimen')}")
        if t.get("run_in_enrichment"):
            details.append(f"run-in enrichment: {t.get('run_in_enrichment')}")
        if t.get("analysis_set_literal"):
            details.append(f"analysis set literal: {t.get('analysis_set_literal')}")
        if t.get("endpoint_event_time"):
            details.append(f"endpoint event time: {t.get('endpoint_event_time')}")
        if t.get("components"):
            details.append("components: " + "; ".join(str(x) for x in (t.get("components") or [])))
        if t.get("continuity_correction"):
            details.append(t.get("continuity_correction"))
        if details:
            src += "<div class='ident'><em>compatibility row fields:</em> " + _e("; ".join(details)) + "</div>"
        rows.append(f"<tr><td>{_e(t.get('label'))}</td><td>{_id_cell(t)}</td>"
                    f"<td>{inp}</td><td>{src}</td></tr>")
    absent_rows = []
    from .remainder_prose import absent_trial
    for t in o.get("declared_absent_trials", []) or []:
        absent_rows.append(absent_trial(t))
    absent = "".join(absent_rows)
    return ("<table class='arms'><tr><th>Trial</th><th>Id</th><th>Input</th><th>Source</th></tr>"
            + rows_join(rows) + absent + "</table>")


def rows_join(rows):
    return "".join(rows)


def _loo_text(loo):
    """Compact leave-one-out render: influence range + most-influential trial, or the not-assessable note."""
    if not loo:
        return None
    if loo.get("min") is not None:
        return (f"estimate ranges {_num(loo.get('min'))}–{_num(loo.get('max'))} across single-trial drops; "
                f"most influential: {_e(loo.get('most_influential'))}. "
                + _e(loo.get("note", "")))
    return _e(loo.get("note"))


def typed_effects_html(o):
    from .remainder_prose import typed_effects
    return typed_effects(o)


def _outcome_block(o, show_inputs=True):
    from .page_claims import outcome_summary, outcome_details, harm_summary
    migrated = outcome_summary(o)
    if migrated is not None:
        body = migrated + _known_missing_sensitivity_panel(o) + outcome_details(o)
        if show_inputs:
            body += _trial_inputs(o)
        return body + (typed_effects_html(o) if show_inputs else '')
    migrated = harm_summary(o)
    if migrated is not None:
        return migrated + (_trial_inputs(o) + typed_effects_html(o) if show_inputs else '')
    reason = _absent(o)
    if reason:
        return f"<h4>{_e(o.get('name'))}</h4>" + _absent_block(reason)
    body = f"<h4>{_e(o.get('name'))}{' (primary)' if o.get('primary') else ''}</h4>"
    res = o.get("result")
    rr = _absent(res)
    if rr and isinstance(res, dict) and res.get("state") == "HARMS_INCOMPLETE":
        unresolved = res.get("known_eligible_outcome_reports_unresolved") or []
        names = ", ".join(str(x.get("trial_id")) for x in unresolved[:8])
        body += ("<div class='absent'><strong>HARMS_INCOMPLETE.</strong> "
                 f"{_e(res.get('reason'))} "
                 f"<span class='muted'>Known unresolved primary-pool trial(s): {_e(names)}</span></div>")
    elif rr:
        body += _absent_block(rr)
    elif res.get("unrenderable"):
        body += _unrenderable_block(res)
    elif res.get("pool_refused"):
        body += _k2_pool_refusal_block(res)
    elif res.get("suppressed_incompatible"):
        # FAIL CLOSED (audit 23): detected-invalid means NOTHING pooled is rendered — no effect, CI, tau^2,
        # prediction interval, common-effect sensitivity, forest or leave-one-out. Only the reason + the
        # per-trial estimates (below) survive. Detecting the failure and printing the number is a caption.
        _cf = res.get("counterfactual") or {}
        _cf_line = ""
        if _cf.get("would_be_estimate") is not None:
            _cf_line = (f" <em>Refusal is reversible and auditable — reason code "
                        f"<code>{_e(_cf.get('reason_code'))}</code>; had these classes been pooled anyway "
                        f"the (INVALID) result would have been {_num(_cf.get('would_be_estimate'))} "
                        f"({_num(_cf.get('would_be_ci_low'))}–{_num(_cf.get('would_be_ci_high'))}) — shown "
                        f"only so the refusal is inspectable, never as a usable number.</em>")
        body += ("<div class='absent'><strong>Pooled result SUPPRESSED (estimand-incompatible).</strong> "
                 f"{_e(res.get('suppressed_reason'))} <em>Estimand classes: "
                 f"{_e(' + '.join((res.get('estmeasure') or {}).get('canonicals', [])))}; k = "
                 f"{_e(res.get('k'))} trials, shown individually below, not pooled.</em>" + _cf_line + "</div>")
    else:
        _dr = res.get("design_refusal") or {}
        if _dr:
            refused = "; ".join(
                f"{_e(x.get('trial'))} ({_e(x.get('design'))})" for x in (_dr.get("refused") or [])
            )
            missing = "; ".join(
                f"{_e(x.get('trial'))}: {_e(x.get('reason_code') or x.get('state'))} "
                f"missing {_e(x.get('missing'))}"
                for x in (_dr.get("refused") or [])
            )
            body += ("<div class='absent'><strong>ENGINE_CANNOT_CONSUME design variance.</strong> "
                     f"{_e(_dr.get('statement'))} Refused trial(s): {refused}. {missing}. "
                     "The evidence is not absent; this engine cannot consume the row without a held "
                     "design-adjusted effect or ICC design-effect variance.</div>")
        if res.get("pooled_ci_refused"):
            body += _k2_ci_refusal_block(res)
        if res.get("harms_incomplete"):
            unresolved = ", ".join(str(x.get("label") or x.get("id"))
                                   for x in (res.get("known_reported_not_yet_extracted") or []))
            body += ("<div class='absent'><strong>HARMS_INCOMPLETE.</strong> "
                     f"{_e(res.get('reason'))} "
                     f"<span class='muted'>Unresolved: {_e(unresolved)}</span></div>")
        rows = [
            # Show the scale of the number ACTUALLY pooled (res["scale"]: RR / HR / IRR / MD /
            # "mixed (…)"), not the topic's target estimand — the target is stated in the Analysis
            # Method prose, and a row reading "Estimand RR" beside a pooled HR is the defect this fixes.
            ("Estimand", res.get("scale") or o.get("estimand")),
            ("Estimand decision", _estimand_decision_text(o)),
            # The authoritative compatibility contract is the Compatibility key block below (compat.py,
            # the shipped gate). The only estmeasure verdict surfaced here is the INCOMPATIBLE warning;
            # the old "reported labels differ … SAME compatibility class (RR/OR/HR)" sentence was a
            # SECOND, looser compatibility judgement that contradicted the gate (OR/RR/HR are distinct
            # estimands, not one poolable class) and is removed — the compat key now judges the label mix.
            ("Estimand compatibility", (
                ("⚠ INCOMPATIBLE — the pooled trials report DIFFERENT estimand classes ("
                 + " + ".join((res.get("estmeasure") or {}).get("canonicals", []))
                 + "): these measures are not directly poolable without an explicit, source-backed "
                 "conversion — read any forced pooled number as an invalid diagnostic only, not a valid "
                 "summary (a stated limitation, surfaced not smoothed)")
                if (res.get("estmeasure") or {}).get("status") == "incompatible" else None)),
            ("Design consumption", (o.get("design_consumption") or {}).get("headline")
             if (o.get("design_consumption") or {}).get("design_refused") else None),
            ("Analysis population", o.get("population")),
            ("Timepoint", o.get("timepoint")),
            ("Method", o.get("method")),
            ("k", _k_display(o)),
        ]
        rows.extend(_effect_rows(res))
        cerow = _common_effect_row(res)
        if cerow:
            _eu = _evidence_unit_summary(o)
            rows.append((cerow[0] + (f" [k={_k_display(o)}]" if _eu else ""), cerow[1]))
        for sens in res.get("co_primary_sensitivities") or []:
            pool = sens.get("pool") or {}
            if pool.get("estimate") is None:
                continue
            rows.append((
                "Alternative co-primary sensitivity",
                f"{_e(sens.get('trial'))}: {_e(sens.get('alternative'))} -> "
                f"k={_e(pool.get('k'))}, {_e(pool.get('scale'))} {_num(pool.get('estimate'))} "
                f"(95% CI {_num(pool.get('ci_low'))}-{_num(pool.get('ci_high'))}); "
                f"tau^2={_tau(pool.get('tau2'))}. {_e(sens.get('rule'))}",
            ))
        rows.extend([
            ("Prediction interval", (f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}" if res.get('pi_low') is not None else None)),
            ("τ²", _tau(res.get("tau2")) if res.get("tau2") is not None else None),
            ("Note", res.get("pi_note")),
            ("Small-k note", res.get("fixed_note")),
            ("Composite heterogeneity", res.get("composite_heterogeneity")),
            ("Leave-one-out (influence)", _loo_text(res.get("leave_one_out"))),
        ])
        body += _kv([(k, v) for k, v in rows if v is not None])
        if o.get("primary"):
            body += _known_missing_sensitivity_panel(o)
        # COMPATIBILITY KEY: the explicit contract that lets these trials be pooled -- the six
        # dimensions they must share. Rendered so a reader can see the pool is not a mix of
        # different quantities; the randomised-contrast fraction discloses how many are parser-
        # confirmed contrasts of the intervention of interest.
        ck = o.get("compat_key")
        if ck:
            rc = ck.get("randomised_contrast") or {}
            _labels = ck.get("effect_measure") or []
            _dm = ck.get("dimension_matches") or {}
            _het = [d for d, ok in sorted(_dm.items()) if ok is False]
            _ec = ck.get("endpoint_canonical") or {}
            body += "<h5>Compatibility key (pooling contract)</h5>" + _kv([
                ("Effect-measure class", ", ".join(ck.get("event_process") or []) or None),
                ("Effect label", ck.get("effect_label")),
                # Factual: the distinct reported labels actually pooled (HR, RR, …). Not a reassurance
                # that they are identical -- the recovery-recheck limitation below states the caveat.
                ("Effect-measure labels pooled", ", ".join(_labels) if len(set(_labels)) > 1 else None),
                ("Endpoint", ck.get("endpoint")),
                *([("Endpoint components", _compat_dimension_text(ck.get("endpoint_components")))]
                  if "endpoint_components" in ck else []),
                ("Endpoint canonical status", ck.get("endpoint_canonical_status")),
                ("Endpoint canonical components", "; ".join(_ec.get("components") or []) if _ec else None),
                ("Follow-up window", _compat_dimension_text(ck.get("follow_up_window"))
                 if isinstance(ck.get("follow_up_window"), dict) else ck.get("follow_up_window")),
                ("Analysis set", _compat_dimension_text(ck.get("analysis_set"))
                 if isinstance(ck.get("analysis_set"), dict) else ck.get("analysis_set")),
                *([("Endpoint definition", _compat_dimension_text(ck.get("endpoint_definition")))]
                  if "endpoint_definition" in ck else []),
                ("Declared analysis set", ck.get("analysis_set_declared")
                 if ck.get("analysis_set_declared") != ck.get("analysis_set") else None),
                *([("Prior disease stage", _compat_dimension_text(ck.get("prior_disease_stage")))]
                  if "prior_disease_stage" in ck else []),
                *([("Background therapy", _compat_dimension_text(ck.get("background_therapy")))]
                  if "background_therapy" in ck else []),
                *([("Treatment strategy", _compat_dimension_text(ck.get("treatment_strategy")))]
                  if "treatment_strategy" in ck else []),
                *([("Clomifene status", _compat_dimension_text(ck.get("clomifene_status")))]
                  if "clomifene_status" in ck else []),
                *([("Dose regimen", _compat_dimension_text(ck.get("dose_regimen")))]
                  if "dose_regimen" in ck else []),
                *([("Run-in enrichment", _compat_dimension_text(ck.get("run_in_enrichment")))]
                  if "run_in_enrichment" in ck else []),
                ("Heterogeneous key dimensions",
                 (", ".join(_het) + f" [{_e(ck.get('limitation_code'))}]") if _het else None),
                ("Parser-confirmed contrast",
                 (f"{rc.get('verified')} of {rc.get('total')} pooled trials"
                  if rc.get("total") else None)),
            ])
            _lims = [x for x in (ck.get("limitations") or [])
                     if x.get("code") == "COMPAT_DIMENSION_HETEROGENEOUS"]
            if _lims:
                body += ("<p class='note'>Compatibility limitation: "
                         + _e("; ".join(x.get("detail", "") for x in _lims)) + ".</p>")
            cu = o.get("compat_underlying") or {}
            ptr = cu.get("per_trial") or {}
            if ptr:
                rows = []
                for dim, vals in sorted(ptr.items()):
                    for item in vals:
                        rows.append(
                            f"<tr><td>{_e(dim)}</td><td>{_e(item.get('trial_id'))}</td>"
                            f"<td>{_e(item.get('value'))}</td><td>{_e(item.get('span'))}</td></tr>"
                        )
                body += ("<table class='arms'><tr><th>Dimension</th><th>Trial</th>"
                         "<th>Derived value</th><th>Source span</th></tr>"
                         f"{''.join(rows)}</table>")
        body += _compat_direction_block(o)
        if _evidence_unit_summary(o):
            body += f"<p class='note'>k = {_e(_k_display(o))}.</p>"
        # RECOVERY-INDUCED-INCOMPATIBILITY disclosure: a pool that mixes effect-measure labels at small
        # k (e.g. a recovery adding a reconstructed RR to a published RR + HR pool) is surfaced as an
        # approximation to weigh, never smoothed over. Object-derived from the recovery-recheck verdict.
        _rdisc = o.get("recovery_disclosure")
        if _rdisc:
            body += f"<p class='note'>⚠ {_e(_rdisc)}</p>"
        # A k stated without the contributing trials named is the container-vs-contents
        # defect. When trials are enumerable, name them (below). When they are not (a
        # transcribed comparator), say so plainly so the bare k is not mistaken for auditable.
        if (res.get("k") is not None and not o.get("trials")
                and not o.get("declared_absent_trials")):
            body += ("<p class='note'>k is as reported by the source; the individual trials "
                     "behind it were not machine-extracted from the transcription, so this "
                     "count cannot be audited on this page.</p>")
    findings = o.get("contract_compatibility") or []
    if findings:
        body += ("<h5>Protocol compatibility findings (not eligibility exclusions)</h5>"
                 "<table class='arms'><tr><th>Trial</th><th>Axis</th><th>Observed</th><th>Contract</th><th>Finding</th></tr>"
                 + "".join(f"<tr><td>{_e(x.get('trial_id'))}</td><td>{_e(x.get('dimension'))}</td>"
                           f"<td>{_e(x.get('trial_value'))}</td><td>{_e(x.get('contract_value'))}</td>"
                           f"<td>{_e(x.get('verdict'))}: {_e(x.get('finding_code'))}</td></tr>" for x in findings)
                 + "</table>")
    strict = o.get("strict_contract_sensitivity")
    if strict:
        body += ("<h5>Retrospective protocol reading sensitivity — 17 Sep 2026</h5>"
                 "<table class='arms'><tr><th>Reading</th><th>Trials</th><th>Result</th></tr>"
                 f"<tr><td>Strict contract sensitivity</td><td>k={strict['k']}</td>"
                 f"<td>{'No pooled result (fewer than two trials)' if strict['k'] < 2 else 'See per-trial contract findings'}</td></tr>"
                 f"<tr><td>Compatibility-axis reading</td><td>k={strict['compat_axis_k']}</td>"
                 "<td>Outcome result above; compatibility findings retained</td></tr></table>"
                 f"<p>{_e(strict['reason'])} Both readings were known when the amendment was written.</p>"
                 f"<p>{_e(strict.get('amendment', ''))}</p>")
    admission_sets = o.get("admission_analysis_sets") or {}
    if admission_sets:
        body += (f"<p class='note'>Candidate analysis sets: {_e(admission_sets.get('label'))}. "
                 f"{_e(admission_sets.get('scope'))}.</p><table class='arms'>"
                 "<tr><th>Trial</th><th>Analysis set</th><th>Contract verdict</th></tr>"
                 + "".join(f"<tr><td>{_e(t.get('trial_id'))}</td><td>{_e(t.get('value'))}</td>"
                           f"<td>{_e(t.get('verdict'))}</td></tr>" for t in admission_sets.get("per_trial") or [])
                 + "</table>")
    n_pool = len(o.get("trials") or [])
    n_abs = len(o.get("declared_absent_trials") or [])
    if show_inputs and (n_pool or n_abs):
        if n_abs and n_pool:
            _states = collections.Counter((t.get("state") or "") for t in (o.get("declared_absent_trials") or []))
            _nd = _states.get("NO_OUTCOME_DATA_IN_SOURCE", 0)
            unitized = any((t.get("trial_family_id") for t in (o.get("trials") or []))) or any(
                (t.get("trial_family_id") for t in (o.get("declared_absent_trials") or [])))
            absent_display = (
                "a further " + _identity_mod.count_phrase(_outcome_unit_counts(o, has_units=True)["absent"],
                                                           "trial family")
                if unitized else f"{n_abs} further screened-in trial(s)"
            )
            body += (f"<p class='note'>k = {_k_display(o)}: the {n_pool} trial(s) named below were "
                     f"pooled; {absent_display} had no poolable value for this "
                     f"outcome and are listed below with an explicit <em>absence/refusal state</em>. These "
                     f"typed states distinguish source silence from effect-present estimand mismatches, "
                     f"uncorroborated counts, multi-arm/timepoint/population mismatches, missing cached "
                     f"abstracts, and other evidence refusals; only <em>no outcome data in source</em> "
                     f"({_nd} here) is a claim about the trial itself. An unassessed outcome never counts as "
                     f"favourable to the intervention.</p>")
        body += _trial_inputs(o)
    # Typed axes include verbatim individual-source evidence, just like _trial_inputs.
    # Keep them on the served page but outside the pooled-significance surface.
    return body + (typed_effects_html(o) if show_inputs else '')


def _definition_audit_block(r):
    """Render the cross-family definition-audit findings for this topic (composite component set / timepoint /
    population / analysis set), each with its adjudication + resolution, so a recorded mismatch is VISIBLE."""
    da = r.get("definition_audit") or {}
    if not da:
        return ""
    rows = []
    for rid, v in sorted(da.items()):
        parts = rid.split("::")
        outcome, pmid = (parts[1] if len(parts) > 1 else ""), (parts[-1] if parts else "")
        both = " ·both families" if v.get("both_families") else ""
        rows.append(f"<tr><td>{_e(pmid)}</td><td>{_e(outcome)}</td><td>{_e(v.get('detail',''))}{_e(both)}</td>"
                    f"<td><strong>{_e(v.get('resolution',''))}</strong></td></tr>")
    return ("<div class='absent'><strong>Cross-family definition audit.</strong> Two independent model "
            "families (Gemini via AGY, and Fable) re-read every pooled row and checked whether the extracted "
            "result matches the outcome LABEL's definition &mdash; composite component set, timepoint, "
            "population, analysis set &mdash; not just the number. Rows flagged for this topic, with how each "
            "was resolved (refuse the trial / disclose the heterogeneity / relabel the timepoint / already "
            "disclosed). This is the endpoint-<strong>IDENTITY</strong> check &mdash; distinct from the "
            "per-number <strong>MAGNITUDE</strong> check (every pooled number located in its committed source "
            "span, gate-enforced). A number can pass magnitude and fail identity, which is exactly the class "
            "this audit catches; &lsquo;verified&rsquo; on this harness now means both:"
            "<table class='arms'><tr><th>Trial</th><th>Outcome</th><th>Finding</th><th>Resolution</th></tr>"
            + "".join(rows) + "</table></div>")


def _reason_code_audit_block(r):
    from .remainder_prose import reason_audit
    return reason_audit(r)


def _outcomes(r, neutral):
    outs = [o for o in (r.get("outcomes") or []) if o.get("kind") != "harm"]
    if not outs:
        return _absent_block("no efficacy outcomes in the review object")
    return _definition_audit_block(r) + _reason_code_audit_block(r) + "".join(_outcome_block(o) for o in outs)


def _harms(r, neutral):
    from . import section_claims
    harms = [o for o in (r.get("outcomes") or []) if o.get("kind") == "harm"]
    if not harms:
        hstate = r.get("harms_registry_state") or {}
        if hstate:
            names = ", ".join(str(x.get("label") or x.get("id"))
                              for x in (hstate.get("known_reported_not_yet_extracted") or [])[:8])
            return ("<div class='absent'><strong>HARMS_INCOMPLETE.</strong> "
                    f"{_e(hstate.get('reason'))} "
                    f"<span class='muted'>Known source-reported harms: {_e(names)}</span></div>")
        return _absent_block("no harms recorded")
    return "".join(section_claims.harms_unpooled(o)
                   if not o.get('trials') and o.get('declared_absent_trials')
                   else _outcome_block(o) for o in harms)


# Public render wrappers for the canonical-claim contradiction scan (census._claim_check): they
# expose the SAME per-outcome / overview / manuscript bytes a reader sees, so the scan reads the
# exact surface it is judging. Named (not private) so the gate can call and tests can patch them.
def render_outcome_block(o):
    # show_inputs=False: exclude the per-trial VERBATIM SOURCE SPANS (e.g. a trial abstract's own
    # "evolocumab significantly reduced ...") from the significance scan. Those are the source's
    # words about a single trial, not the harness's assertion about the pooled result, and must not
    # be read as a claim the pooled object could contradict.
    return _outcome_block(o, show_inputs=False)


def render_overview(r, neutral=False):
    return _overview(r, neutral)


def render_manuscript(r, neutral=False):
    return _manuscript(r, neutral)


def _comparator_truth_block(c):
    truth = (c or {}).get("truth") or {}
    if not truth:
        return ""
    rows = []
    agent = truth.get("agent_scope") or {}
    if agent.get("comparator_agent_scope") and agent.get("comparator_agent_scope") != "not-classified":
        rows.append(("Comparator agent scope", agent.get("comparator_agent_scope")))
        rows.append(("Agent-scope source sentence", agent.get("sentence")))
    nrec = truth.get("participant_reconciliation") or {}
    if nrec.get("code") and nrec.get("code") != "NOT_ASSESSED":
        rows.append(("Participant-count reconciliation", nrec.get("detail") or nrec.get("code")))
        if nrec.get("theirs_n_span"):
            rows.append(("Comparator n source span", (nrec.get("theirs_n_span") or {}).get("span")))
    comp = truth.get("completeness") or {}
    if comp.get("code") and comp.get("code") != "NOT_ASSESSED":
        rows.append(("Completeness vs named eligible trials", comp.get("detail") or comp.get("code")))
        if comp.get("relation"):
            rows.append(("Text-derived trial-set relation", comp.get("relation")))
        if comp.get("contradictions"):
            rows.append(("Comparator-side contradiction", "; ".join(
                f"{x.get('code')} {x.get('trial')}: {x.get('reason')}" for x in comp.get("contradictions") or []
            )))
    rec = truth.get("recency") or {}
    if rec.get("predates"):
        rows.append(("Recency vs named eligible trials", "; ".join(x.get("code") for x in rec.get("predates") or [])))
    spans = truth.get("rendered_comparator_value_spans") or []
    if spans:
        missing = sum(1 for x in spans if x.get("status") != "FOUND")
        rows.append(("Rendered comparator values located in held text", f"{len(spans) - missing} of {len(spans)}"))
    return "<h4>Comparator truth checks (from cached comparator text)</h4>" + _kv(rows)


def _comparator(r, neutral):
    c = r.get("comparator")
    reason = _absent(c)
    if reason:
        return _absent_block(reason)
    from .remainder_prose import comparator_metadata, comparator_assessments
    body = comparator_metadata(r)
    for rep in c.get("reported", []) or []:
        body += '<p>' + _integrated.recorded('comparator_estimate', rep) + '</p>'
    body += comparator_assessments(r)
    body += _estimand_exclusions_block(r)
    return body


def _estimand_exclusions_block(r):
    """Render trials the comparator pools that THIS review deliberately excludes because they
    report a different estimand — so a reader sees a smaller k as a rigour decision, not a search
    miss. Each row names the trial, the outcome IT reports, and why that is not our estimand."""
    ex = r.get("estimand_exclusions") or []
    if not ex:
        return ""
    head = ("<tr><th>Trial</th><th>Id</th><th>What the trial reports</th>"
            "<th>Why excluded (estimand)</th></tr>")
    rows = "".join(
        f"<tr><td>{_e(t.get('trial'))}</td><td>{_e(t.get('id'))}</td>"
        f"<td>{_e(t.get('their_outcome'))}{(' — ' + _e(t.get('their_effect'))) if t.get('their_effect') else ''}</td>"
        f"<td>{_e(t.get('reason'))}</td></tr>" for t in ex)
    return ("<h4>Trials the comparator pools that this review EXCLUDES on estimand grounds</h4>"
            "<p class='note'>A larger k bought by pooling a different outcome is not a larger "
            "evidence base — it is a different question. These trials were found; they are excluded "
            "deliberately because the outcome they report is not this review's estimand, not because "
            "the search missed them.</p>"
            f"<table class='arms'>{head}{rows}</table>")


def _reproduction(r, neutral):
    rep = r.get("reproduction")
    reason = _absent(rep)
    if reason:
        return _absent_block(reason)
    from .remainder_prose import reproduction_metadata
    body = reproduction_metadata(r)
    # ITEM 1: replay is not independent repeatability — state plainly what the claim covers and does
    # not, so a reader is not misled into thinking a fresh search today would return the same set.
    if rs := rep.get("research_diff"):
        body += ("<h4>Re-search (living vs frozen)</h4><p>Re-running the committed queries live and "
                 f"diffing against the cache: {_e(rs.get('summary'))} "
                 f"<span class='muted'>Measured {_e(rs.get('measured_utc'))}; source scope {_e(rs.get('scope'))}.</span></p>")
    # PARITY vs the published comparator (measurement snapshot, outside the core hash): our pooled k
    # vs the COMPARABLE same-scope comparator k, with a named reason for any difference — including
    # where the comparator's extra trials are out-of-scope, double-counted substudies, observational,
    # or non-prespecified for the outcome.
    if pa := rep.get("parity"):
        body += "<h4>Parity with the published comparator</h4>"
        if (r.get('comparator') or {}).get('overlap', {}).get('shared_trials') is not None:
            body += '<p>' + _section_claims.parity_check(r) + '</p>'
        elif pa.get("unrenderable"):
            # A parity row whose prose names a trial set that is no longer the pool renders as the
            # claim-graph refusal block, never as its stale sentence (CG).
            body += _unrenderable_block(pa)
        elif pa.get("membership_status") == "STALE_VS_MEMBERSHIP":
            # The membership object (EM) found the parity prose naming a pooled trial as refused.
            conflicts = pa.get("membership_conflicts") or []
            named = ", ".join(
                f"{c.get('label') or c.get('trial_key')} ({c.get('trial_key')})" for c in conflicts
            )
            body += ("<div class='note'><strong>STALE_VS_MEMBERSHIP.</strong> "
                     "The stored comparator-parity row is not rendered because it contradicts the "
                     "current outcome membership object: "
                     f"{_e(named)} is pooled in this review but the stored parity text describes it as "
                     "a gap/refused/not-pooled trial. The stale prose is suppressed until the hand "
                     "parity object is rewritten from the current membership.</div>")
        else:
            # The status word comes from the computed trial-set relation; hand text is commentary (CP).
            rel = pa.get("parity_relation") or {}
            status = rel.get("relation") or pa.get("status")
            label = rel.get("label") or status
            their_k = rel.get("their_k")
            if their_k is None:
                their_k = pa.get("comparable_comparator_k")
            body += (f"<p>Our pooled <em>k</em> = "
                     f"<strong>{_e(rel.get('our_k', pa.get('our_k')))}</strong> vs the comparator "
                     f"<em>k</em> = <strong>{_e(their_k)}</strong> &mdash; "
                     f"<strong>{_e(status)}</strong>: {_e(label)}. Commentary: {_e(pa.get('reason'))}</p>")
    # INDEPENDENT SECOND EXTRACTION (blind): a second extractor located each pooled number's digits
    # from the abstract, blind to ours. agree = same 2x2; reconcile = same result via a different
    # statistic; conflict = genuine numeric disagreement; not-checkable = not stated in the abstract.
    # Two independent extractions agreeing is a claim no published meta makes about its own numbers.
    if du := rep.get("dual"):
        body += '<h4>Recorded second extraction</h4><p>' + _integrated.recorded('extract', du) + '</p><p>' + _integrated.limit('extract') + '</p>'
    # VERIFIED-BUT-NOT-POOLED: a trial we located and whose numbers we verified, yet did not pool,
    # with the reason. "We found it, verified it, and still refused it, because ..." is a stronger
    # honesty statement than a larger k. Outside the core hash (committed docs/refusals.json).
    if rf := rep.get("refusals"):
        rows = "".join(
            f"<tr><td>{_e(x.get('trial'))}</td><td>{_e(x.get('verified'))}</td>"
            f"<td>{_e(x.get('not_pooled_because'))}{(' <strong>DISPUTED &mdash; this trial IS pooled despite the refusal above; both policies are declared; decision owed to ' + _e(x['disputed'].get('decision_owed_to')) + ' (signed ' + _e(x['disputed'].get('signed_by')) + ', ' + _e(x['disputed'].get('date')) + '): ' + _e(x['disputed'].get('reason')) + '</strong>') if isinstance(x.get('disputed'), dict) else ''}</td></tr>" for x in rf)
        body += ("<h4>Verified but not pooled (refusals, with reasons)</h4>"
                 "<p class='muted'>Trials we located and whose numbers we verified against source, "
                 "yet deliberately did not pool. Honest k over inflated k: a named refusal is a result.</p>"
                 "<table class='arms'><tr><th>Trial</th><th>What was verified</th>"
                 f"<th>Why it was not pooled</th></tr>{rows}</table>")
    # CANONICAL CLAIM OBJECT: every surface derives its significance wording from one object; the build
    # scans the rendered page + manuscript and fails closed on any surface that asserts the opposite.
    if cc := rep.get("claim_check"):
        n_con = len(cc.get("contradictions") or [])
        n_chk = cc.get("claims_checked") or 0
        # Claims checked: 0 is a FAILING state, not neutral: a page with no pooled claim gives the
        # canonical-claim gate nothing to fire on, so the WORST evidence page would show the cleanest
        # gate output. Render it as a limitation (and the invalidation gate treats it as STALE).
        _zero = ("<div class='absent'><strong>No checkable pooled claim (Claims checked: 0).</strong> "
                 "Nothing was pooled on this page, so the canonical-claim contradiction gate has nothing "
                 "to check here — this is a limitation, not a clean result.</div>" if n_chk == 0 else "")
        body += "<h4>Canonical claim check ledger</h4><p>" + _remainder.receipt("check_ledger", cc) + "</p>" + _zero
        # SEVENTH GATE (categorical/membership + methodological): the two contradiction families a
        # significance check cannot see. Rendered so the reader sees it ran (build refuses on any).
        if (pc := rep.get("proposition_check")) is not None:
            _pcon = pc.get("contradictions") or []
            _pscope = _proposition_mod.scope_summary(pc.get("scope") or pc)
            body += "<p>" + _remainder.receipt("check_ledger", pc) + "</p>"
    # NEVER_CONSIDERED (fifth trial state): in-scope trials absent from every identifier space — never
    # retrieved, so invisible to screening/PRISMA/declared-absent unless shown here. The true search gap.
    nc = r.get("never_considered")
    if nc:
        _nrows = "".join(
            f"<li><strong>{_e(x.get('trial'))}</strong>"
            + (f" (NCT {_e(x.get('nct'))})" if x.get('nct') else "")
            + (f" (PMID {_e(x.get('pmid'))})" if x.get('pmid') else "")
            + (f" — {_e(x.get('note'))}" if x.get('note') else "") + "</li>" for x in nc)
        body += ("<h4>Never considered (a fifth state — the true search gap)</h4>"
                 "<p>These trials are verified in-scope under the registered PICO yet were absent from "
                 "EVERY identifier space in this review — not screened, not excluded, not declared absent, "
                 "simply never retrieved. They are invisible to the STALE count, PRISMA and the "
                 f"declared-absent census unless named here:<ul>{_nrows}</ul></p>")
    # PROTOCOL COMPILER (two independent sources): show where the PROSE protocol and the executable
    # config disagree. A check that reads only the config it certifies cannot fail; this reads both.
    pc = r.get("protocol_config") or {}
    pcd = pc.get("divergences")
    if pcd is not None:
        if pcd:
            _rows = "".join(f"<li><code>{_e(x.get('code'))}</code> ({_e(x.get('dimension'))}): prose says "
                            f"<strong>{_e(x.get('prose', x.get('protocol_value')))}</strong>, config enforces "
                            f"<strong>{_e(x.get('config', x.get('config_value')))}</strong></li>" for x in pcd)
            body += ("<h4>Protocol ↔ config divergences (two independent sources)</h4>"
                     "<p>The prose protocol and the executable config are compared as SEPARATE sources "
                     "(a conformance check derived from the config it certifies cannot fail). "
                     f"<strong>{len(pcd)} divergence(s)</strong> — each is a defect to resolve or a dated "
                     f"amendment to declare, never a silent widening:<ul>{_rows}</ul></p>")
        else:
            body += "<h4>Protocol comparison</h4><p>" + _remainder.receipt("protocol_dimensions", pc) + "</p>"
    body += '<div class="absent">' + _integrated.limit('retracted') + '</div>'
    return body


def _reporting(r, neutral):
    from .remainder_prose import reporting
    return reporting(r)


def _uoa_sensitivity(r, uoa_ids):
    """DERIVED (not authored) sensitivity for the unit-of-analysis caveat: re-pool the primary outcome with
    the cluster/crossover trials' variances INFLATED by a range of design-effect factors, and return the
    resulting pooled-estimate range. This replaces the (false) claim that omitting the correction 'leaves the
    point estimate unchanged' — in inverse-variance pooling, changing a study's variance changes its weight
    and therefore the pooled estimate. Transparent DL random-effects re-pool from the committed per-study
    (yi, vi); labelled illustrative, not the primary PM+HKSJ estimate."""
    import math as _m
    from .rob_sensitivity import _studies_and_scale as _ss
    from .synth import pool as _pool
    prim = next((o for o in r.get("outcomes", []) if o.get("primary")), None)
    if not prim or not prim.get("trials"):
        return None
    studies, scale = _ss(prim["trials"], prim.get("estimand", "RR"))
    try:
        pr = _pool(studies, scale=scale)
    except ValueError:
        return None
    if pr.k < 2:
        return None
    ratio = (scale or "").upper() not in ("MD", "SMD")
    ids = {str(x).replace("PMID ", "").strip() for x in uoa_ids}

    def _is_uoa(label):
        return str(label).replace("PMID ", "").strip() in ids

    def _re_estimate(vfactor):
        yv = [(y, (v * vfactor if _is_uoa(lbl) else v)) for lbl, y, v in pr.per_study]
        w0 = [1.0 / v for _, v in yv]
        ybar0 = sum(w * y for w, (y, _) in zip(w0, yv)) / sum(w0)
        Q = sum(w * (y - ybar0) ** 2 for w, (y, _) in zip(w0, yv))
        C = sum(w0) - sum(w * w for w in w0) / sum(w0)
        tau2 = max(0.0, (Q - (len(yv) - 1)) / C) if C > 0 else 0.0
        w = [1.0 / (v + tau2) for _, v in yv]
        ybar = sum(wi * y for wi, (y, _) in zip(w, yv)) / sum(w)
        return _m.exp(ybar) if ratio else ybar

    factors = [1.0, 1.25, 2.0, 4.0, 10.0]
    return {"scale": scale, "points": [(f, round(_re_estimate(f), 4)) for f in factors]}


def _riskofbias(r, neutral):
    from . import risk_prose
    return risk_prose.render(r) + '<p>' + _integrated.recorded('grade_arithmetic', dict(next(record for name, record in _integrated.records(r) if name == 'grade_arithmetic'))) + '</p>'


def _manuscript(r, neutral):
    return _manuscript_mod.render(r, neutral)


_R = {"overview": _overview, "protocol": _protocol, "search": _search,
      "screening": _screening, "outcomes": _outcomes, "harms": _harms, "riskofbias": _riskofbias,
      "manuscript": _manuscript,
      "comparator": _comparator, "reproduction": _reproduction, "reporting": _reporting}

_CSS = """
*{box-sizing:border-box}body{font:15px/1.55 system-ui,Segoe UI,Arial,sans-serif;margin:0;color:#12232e;background:#f7f8fa}
header{background:#12232e;color:#fff;padding:18px 22px}header h1{margin:0;font-size:19px}header .sub{color:#9fb3c8;font-size:13px;margin-top:4px}
nav{display:flex;flex-wrap:wrap;gap:2px;background:#1d3b4d;padding:0 12px}
nav button{background:transparent;border:0;color:#cfe3f3;padding:11px 14px;cursor:pointer;font-size:13px;border-bottom:3px solid transparent}
nav button.active{color:#fff;border-bottom-color:#4ea1d3;font-weight:600}
main{max-width:960px;margin:0 auto;padding:22px}
.tab{display:block;margin-top:8px;padding-top:8px;border-top:1px solid #e6ebef}
.tab h3.tabname{color:#1d3b4d;font-size:14px;margin:0 0 6px}
html.js .tab{display:none;border-top:0}html.js .tab.active{display:block}
html.js .tab h3.tabname{display:none}
table.kv,table.recs,table.arms{border-collapse:collapse;width:100%;margin:10px 0}
table.kv th{text-align:left;width:36%;vertical-align:top;padding:6px 8px;color:#3a5a6b;background:#eef2f5;border:1px solid #dbe3e8}
table.kv td{padding:6px 8px;border:1px solid #dbe3e8}
table.recs th,table.recs td,table.arms th,table.arms td{border:1px solid #dbe3e8;padding:5px 8px;font-size:12.5px;text-align:left;vertical-align:top}
.dec-include{color:#136f3b;font-weight:600}.dec-exclude{color:#8a4b00}
.vok{color:#137333;font-weight:600}.vno{color:#b31412;font-weight:600}
.absent{background:#fff4e5;border:1px solid #f0c27b;padding:10px 14px;border-radius:6px;color:#7a4b00}
.absent-cell{color:#7a4b00}
.kms-panel{background:#fff4e5;border:1px solid #f0c27b;padding:10px 14px;border-radius:6px;color:#7a4b00;margin:12px 0}
.banner{background:#eaf4fb;border-left:4px solid #4ea1d3;padding:10px 14px;margin:12px 0;font-size:13.5px}
.audit-block{background:#eaf4fb;border-left:4px solid #4ea1d3;padding:10px 14px;margin:12px 0;font-size:13.5px}
.hazard-acks{border-left:4px solid #7c6f64;background:#f5f4f2;padding:10px 14px;margin:12px 0;font-size:13px}
.note{color:#4a5b66;font-size:12.5px;margin:6px 0;font-style:italic}
.q{font-size:16px;color:#2a4b5c}pre{background:#0f1c24;color:#d6e6f2;padding:10px;overflow:auto;border-radius:6px;font-size:12px;white-space:pre-wrap}
h2{margin-top:0}h4{margin:16px 0 4px}
"""
_JS = """document.documentElement.className='js';
function show(id){document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('active',t.id==='tab-'+id)});
document.querySelectorAll('nav button').forEach(function(b){b.classList.toggle('active',b.dataset.t===id)});}
(function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();"""


@_claimgraph_mod._provenance_batch()
def render_page(review: dict, neutral: bool = False) -> str:
    from . import grade as grade_mod
    if review.get('grade'):
        grade_mod.validate_arithmetic(review['grade'])
    tabs_spec = [(tid, lbl) for tid, lbl in TABS if not (neutral and tid in NEUTRAL_DROP)]
    nav = "".join(f'<button data-t="{tid}" onclick="show(\'{tid}\')">{_e(lbl)}</button>' for tid, lbl in tabs_spec)
    body = ("<div class='absent'><strong>AACT_NOT_MEASURED</strong>: registry inputs have not "
            "been measured into a valid per-topic cache; registry dates, sponsors and arm "
            "contrasts are unavailable.</div>" if review.get("aact_status") == "AACT_NOT_MEASURED" else "")
    if (review.get('strands') or {}).get('generated_from_declarations'):
        from .remainder_prose import strand_rows
        body += render_strands_section(review["strands"]) + strand_rows(review)
    for tid, lbl in tabs_spec:
        body += (f'<section class="tab" id="tab-{tid}">'
                 f'<h3 class="tabname">{_e(lbl)}</h3>{_R[tid](review, neutral)}</section>')
    from . import statistical_layers
    objects = review.get('statistical_layers') or statistical_layers.build(review)
    body += statistical_layers.render(objects)
    title = _e(review.get("title") or review.get("slug"))
    from .remainder_prose import header
    identity_header = header(review, neutral)
    rendered_html = ("<!doctype html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{_CSS}</style></head><body>"
            f"<header><h1>{title}</h1>{identity_header}</header>"
            f"<nav>{nav}</nav><main>{body}</main><script>{_JS}</script></body></html>")
    # FDA verbatim source objects retain CRLF. HTML display uses LF so readers
    # that apply universal-newline decoding reproduce exactly the served bytes.
    if (review.get('strands') or {}).get('generated_from_declarations'):
        return re.sub(r'[ \t]+\n', '\n', rendered_html.replace('\r\n', '\n'))
    return rendered_html
