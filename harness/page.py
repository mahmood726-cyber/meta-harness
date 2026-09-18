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
import collections
import html
import json
import re
from typing import Any

from . import manuscript as _manuscript_mod
from . import grade as _grade_mod
from . import rob_sensitivity as _rob_sensitivity_mod
from . import claimgraph as _claimgraph_mod
from . import identity as _identity_mod
from . import propositions as _proposition_mod
from . import funding as _funding_mod
from . import scope_identity as _scope_identity_mod

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
    snap = ret.get("snapshot") or {}
    sha8 = str(snap.get("records_sha256") or "")[:8]
    body = ("<h4>Retrieval snapshot</h4><div class='banner'>"
            f"<p><strong>Snapshot:</strong> records_sha256 <code>{_e(sha8)}</code>; "
            f"retrieved_utc {_e(snap.get('retrieved_utc'))}; mode {_retrieval_mode_label(snap.get('mode'))}.</p>"
            "<p>This page replays the committed retrieval snapshot; it is not a claim that the protocol "
            "SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event "
            "(see Re-search below if present).</p>"
            "</div>")
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
        body += ("<div class='absent'><strong>No search was run for this topic: every PubMed source "
                 "is a PMID enumeration.</strong></div>")
    rows = []
    for src in ret.get("sources") or []:
        funnel = src.get("funnel") or {}
        flow = (f"{_retrieval_value(funnel.get('hits'))} -&gt; "
                f"{_retrieval_value(funnel.get('fetched'))} -&gt; "
                f"{_retrieval_value(funnel.get('retained'))}")
        rows.append(
            f"<tr><td>{_retrieval_kind_label(src.get('kind'))}</td>"
            f"<td><code>{_e(src.get('query'))}</code></td>"
            f"<td>{_e(src.get('run_utc'))}</td>"
            f"<td>{_retrieval_state_text(src)}</td>"
            f"<td>{flow}</td>"
            f"<td>{_retrieval_cap_text(funnel.get('cap'))}</td>"
            f"<td>{'yes' if src.get('discovery_capable') else 'no'}</td></tr>")
    if rows:
        body += ("<h4>Retrieval sources</h4>"
                 "<table class='recs'><tr><th>Kind</th><th>Query</th><th>Run date</th><th>State</th>"
                 "<th>hits -&gt; fetched -&gt; retained</th><th>Cap</th><th>Discovery-capable</th></tr>"
                 f"{''.join(rows)}</table>")
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
    body = (f"<h4>Retrieval class</h4><div class='{block_class}'><p><strong>{_e(rc.get('label'))}</strong>")
    if rc.get("retraction"):
        body += " " + _e(rc.get("retraction"))
    if rc.get("distinction"):
        body += " " + _e(rc.get("distinction")) + "."
    body += "</p></div>"
    rows = []
    for row in rc.get("basis") or []:
        features = "; ".join(row.get("features") or [])
        rows.append(
            f"<tr><td><code>{_e(row.get('query'))}</code></td>"
            f"<td>{_e(row.get('kind'))}</td><td>{_e(features)}</td></tr>"
        )
    if rows:
        body += ("<table class='recs'><tr><th>Verbatim query</th><th>Kind</th><th>Features fired</th></tr>"
                 f"{''.join(rows)}</table>")
    return body


def _search_provenance_html(rc: dict) -> str:
    sp = (rc or {}).get("search_provenance") or {}
    if not sp:
        return ""
    return (
        "<div class='absent'>"
        f"<strong>{_e(sp.get('heading'))}</strong> "
        "The registry-first (AACT) adapter status for this topic is "
        f"<strong>{_e(sp.get('registry_first_status'))}</strong>; "
        f"{_e(sp.get('class_statement'))}, "
        f"{_e(sp.get('discovery_statement'))} "
        f"{_e(sp.get('retraction'))}</div>"
    )


def _ci(res) -> str:
    return f"{_num(res.get('estimate'))} ({res.get('scale')}), 95% CI {_num(res.get('ci_low'))}–{_num(res.get('ci_high'))}"


def _effect_label(res) -> str:
    # A single-trial result is not a pooled effect; label it honestly so the k=1 CI is not
    # read as a random-effects pooled interval.
    if res.get("effect_label"):
        return res.get("effect_label")
    return "Single-trial effect" if res.get("k") == 1 else "Pooled effect"


def _k2_pool_refusal_block(res: dict, stale_reason="") -> str:
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
            f"I^2={_e(cf.get('would_be_i2'))}%. {_e(stale_reason)}</em>"
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
    kms = o.get("known_missing_sensitivity") or {}
    if not kms:
        return ""
    rows = []
    for r in kms.get("rows") or []:
        if r.get("value_status") == "IN_COMMITTED_SOURCE":
            if r.get("ai") is not None:
                val = f"{_e(r.get('ai'))}/{_e(r.get('n1i'))} vs {_e(r.get('ci'))}/{_e(r.get('n2i'))}"
            elif r.get("effect") is not None:
                val = (f"{_num(r.get('effect'))} ({_e(r.get('scale'))}), 95% CI "
                       f"{_num(r.get('ci_low'))}-{_num(r.get('ci_high'))}")
            else:
                val = "source-backed value"
            val += (f"<div class='muted'>{_e(r.get('source_ref'))}: {_e(r.get('source_span'))}</div>"
                    f"<div class='muted'>{_e(r.get('verify_basis'))}</div>")
        elif r.get("value_status") == "IN_SOURCE_DIFFERENT_ESTIMAND":
            val = "different estimand in committed source; no target-estimand number used"
        else:
            val = "named, value not in committed source; no number computed"
        sens = r.get("sensitivity")
        if sens:
            sens_txt = (f"{_e(sens.get('label'))}: k={_e(sens.get('k'))}, "
                        f"{_num(sens.get('estimate'))} ({_e(sens.get('scale'))}), 95% CI "
                        f"{_num(sens.get('ci_low'))}-{_num(sens.get('ci_high'))}; "
                        f"tau2={_tau(sens.get('tau2'))}")
            conclusion = sens.get("conclusion_effect")
        else:
            sens_txt = "not computable"
            conclusion = r.get("conclusion_effect") or "NOT_COMPUTABLE"
        rows.append(
            "<tr>"
            f"<td>{_e(r.get('name') or r.get('trial_key'))}</td>"
            f"<td>{_e(r.get('value_status'))}</td>"
            f"<td>{_e(r.get('missing_class'))}</td>"
            f"<td>{_e(r.get('why_eligible'))}</td>"
            f"<td>{val}</td>"
            f"<td>{sens_txt}</td>"
            f"<td>{_e(conclusion)}</td>"
            "</tr>"
        )
    combined = kms.get("combined")
    combined_html = ""
    if combined:
        combined_html = (
            "<p><strong>Combined SENSITIVITY:</strong> "
            f"k={_e(combined.get('k'))}, {_num(combined.get('estimate'))} ({_e(combined.get('scale'))}), "
            f"95% CI {_num(combined.get('ci_low'))}-{_num(combined.get('ci_high'))}; "
            f"tau2={_tau(combined.get('tau2'))}; conclusion_effect={_e(combined.get('conclusion_effect'))}.</p>"
        )
        if combined.get("pi_low") is not None:
            combined_html += (f"<p class='note'>Prediction interval "
                              f"{_num(combined.get('pi_low'))}-{_num(combined.get('pi_high'))}.</p>")
    comp = f"<p class='note'>Endpoint components: <code>{_e(kms.get('components'))}</code></p>" if kms.get("components") else ""
    return (
        "<div class='kms-panel' id='known-missing-sensitivity'>"
        f"<h3>{_e(kms.get('heading') or 'Known eligible trials not in this pool, and what they would do')}</h3>"
        f"<p><strong>Panel conclusion effect: {_e(kms.get('headline_conclusion_effect') or 'NOT_COMPUTABLE')}.</strong> "
        "These rows are SENSITIVITY only; they do not replace the primary pool.</p>"
        + combined_html + comp +
        "<table class='arms'><tr><th>Trial</th><th>Value status</th><th>Debt class</th>"
        "<th>Why eligible</th><th>Committed value/span</th><th>Sensitivity</th><th>Conclusion effect</th></tr>"
        + rows_join(rows) + "</table></div>"
    )


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
        pool = s.get("pool")
        if pool:
            sig = "crosses null" if pool.get("crosses_null") else "significant"
            sens = pool.get("common_effect_sensitivity") or {}
            senstxt = (f" <span class='note'>[common-effect sensitivity {_e(sens.get('effect'))} "
                       f"({_e(sens.get('ci_low'))}–{_e(sens.get('ci_high'))}), NOT the registered result]</span>"
                       if sens else "")
            res = (f"pooled {_e(pool.get('effect'))} ({_e(pool.get('ci_low'))}–{_e(pool.get('ci_high'))}), "
                   f"k={_e(pool.get('k'))}, HKSJ/PM &tau;&sup2;={_e(pool.get('tau2'))}, <strong>{sig}</strong>{senstxt}")
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
        return ("<p class='muted'><strong>Identifier scope:</strong> "
                f"{_e(scope.get('detail'))}. Verdict: <code>{_e(verdict)}</code>.</p>")
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


def _overview(r, neutral):
    parts = [f"<h2>{_e(r.get('title'))}</h2>", f"<p class='q'>{_e(r.get('question'))}</p>"]
    if r.get("grade"):
        parts.append(f"<p data-grade-certainty='true'>{_e(_grade_mod.render_certainty(r['grade']))}</p>")
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
            parts.append(_k2_pool_refusal_block(res, _grade_mod.stale_heterogeneity(r)))
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
            if inc_counts["trials"] is not None and k is not None and isinstance(k, int):
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
                rows.append(("Prediction interval", f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))} {_e(_grade_mod.stale_heterogeneity(r))}"))
            if res.get("tau2") is not None:
                rows.append(("Between-study τ²", _tau(res.get("tau2")) + " " + _e(_grade_mod.stale_heterogeneity(r))))
            if _grade_mod.membership_incomplete(r):
                rows.append(("Heterogeneity state", _grade_mod.stale_heterogeneity(r)))
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
        parts.append(
            "<h3>Stated limitations</h3><ul class='limits'>"
            "<li><strong>Small k on many topics.</strong> A pool of one or two trials is a trial "
            "summary in meta-analysis apparatus (τ² undefined, wide intervals from lack of data); "
            "the k here is honest, not inflated — see the gap vs the comparator.</li>"
            "<li><strong>Open-access comparator only.</strong> The benchmark meta is restricted to an "
            "OA-retrievable publication, a narrower and sometimes weaker comparator set than the full "
            "literature.</li>"
            + ((f"<li><strong>Comparator scope mismatch.</strong> {_e((r.get('comparator') or {}).get('scope',{}).get('note'))}</li>")
               if (r.get('comparator') or {}).get('scope', {}).get('scope_valid') is False else "")
            + ((f"<li><strong>Evidence base incomplete.</strong> {_e(r.get('evidence_base_caveat'))}</li>")
               if r.get('evidence_base_caveat') else "")
            + "<li><strong>Favourable topic sample.</strong> Topics were chosen by us; clean binary "
            "outcomes with registered trials succeeded, while continuous, recurrent-event and older "
            "literature were declined — so the success rate reflects a selected sample, not the whole "
            "field.</li>"
            "<li><strong>Risk of bias is partial.</strong> Registry-machine-signal-restricted domains are computed from machine-"
            "available registry fields; domains needing human reading are marked not-assessed.</li>"
            "<li><strong>Registry snapshot is dated.</strong> AACT is a fixed local snapshot; trials "
            "registered, or results posted, after it are invisible to the registry-first recall, ghost "
            "and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the "
            "Reproducibility tab measures the resulting drift rather than assuming none.</li>"
            "<li><strong>Dual screening is not fully independent.</strong> The two rule screeners share "
            "an author and criteria, so their agreement overstates reliability; an independent model "
            "adjudicator is used on disagreements (see Reporting, PRISMA item 8).</li>"
            "<li><strong>The blind comparison is judged by an AI, and transparency is what we optimise "
            "for.</strong> A model scoring auditability will reward auditability — so that win is partly "
            "circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is "
            "the cross-check, and it is the axis we claim, not superior evidence.</li></ul>")
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
    rows = [("Registration (protocol commit SHA)", p.get("sha")),
            ("Committed (UTC)", p.get("committed_utc")),
            ("Declared analysis method", p.get("method_declared")),
            ("Target endpoint selection", (p.get("target_endpoint_selection") or {}).get("summary")),
            ("Eligibility (P/I/C/design)", p.get("eligibility"))]
    body = _kv([(k, v) for k, v in rows if v])
    # The raw protocol text names the comparator and the machinery; omit it in the
    # blinding-safe render so the judge cannot identify which page is the harness's.
    if p.get("text") and not neutral:
        body += f"<pre class='proto'>{_e(p.get('text'))}</pre>"
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
    body = _kv([(k, v) for k, v in [
        ("Records retrieved", s.get("n_records")),
        ("Databases / sources", ", ".join(s.get("databases", []) or []) or None),
        ("Committed cache", s.get("cache_ref")),
        ("Run (UTC)", s.get("run_utc")),
    ] if v is not None])
    if s.get("retrieval"):
        body += _retrieval_html(s["retrieval"])
    ss = s.get("source_status") or {}
    if ss:
        # Four-state per source: which adapters ran, returned nothing, errored, or were not attempted
        # for this topic — so process coverage is visible, not assumed.
        # sorted() so the render order is independent of dict key order (canonical_json sorts keys;
        # an insertion-order iteration would render differently pre/post-canonicalisation — the
        # deterministic-render census check catches exactly that, as it did for the partial machine block).
        cells = " · ".join(f"{_e(k)}: <strong>{_e(v)}</strong>" for k, v in sorted(ss.items()))
        body += ("<h4>Source status (which adapters ran)</h4><p class='muted'>" + cells +
                 " — RAN_OK = ran and returned records; RAN_ZERO = ran, none matched; RAN_ERROR = "
                 "attempted but failed; NOT_RUN = not attempted for this topic.</p>")
    if s.get("retrieval_class"):
        body += _retrieval_class_html(s["retrieval_class"])
        body += _search_provenance_html(s["retrieval_class"])
    rc = s.get("recall")
    if rc and rc.get("known"):
        # PRIMARY search metric: how many of this topic's KNOWN trials the committed registry-first
        # query recovers (reach, not inclusion). Regenerable by re-running scripts/recall.py.
        status = rc.get("status")
        line = (f"Positive-control recovery: the committed registry query re-found "
                f"<strong>{_e(rc.get('recovered'))}/{_e(rc.get('known'))}</strong> of this topic's "
                f"PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated "
                f"{_e(rc.get('enumerated'))}; status {_e(status)}).")
        # A bare recall reads every non-recovery as a search failure. Split the missed trials by CAUSE
        # so the number is honest: trials with no own-publication registry linkage are UNREACHABLE by a
        # registry-first search (the literature predates or omits trial registration), while trials that
        # ARE registered but were not enumerated are the improvable ceiling of the committed query.
        ceil, nolink = rc.get("reachable_ceiling"), rc.get("no_registry_link")
        reasons = rc.get("missed_reasons") or {}
        if rc.get("missed"):
            reg_ne = [m for m in rc.get("missed", []) if reasons.get(str(m)) == "registered_not_enumerated"]
            unreg = [m for m in rc.get("missed", []) if reasons.get(str(m)) == "no_registry_link"]
            if ceil is not None and ceil != rc.get("recovered"):
                line += (f" Reachable ceiling <strong>{_e(ceil)}/{_e(rc.get('known'))}</strong>: "
                         f"{_e(len(reg_ne))} trial(s) are registered but not enumerated by the committed "
                         f"query (registry vocabulary limit — improvable).")
            if nolink:
                line += (f" {_e(nolink)} missed trial(s) have <strong>no own-publication registry "
                         f"linkage</strong> — unregistered / pre-registration-era, so unreachable by any "
                         f"registry-first search (a property of the literature, not a search failure).")
            line += f" <span class='muted'>Missed: {_e(', '.join(str(m) for m in rc.get('missed', [])))}.</span>"
        if rc.get("measured_utc"):
            line += f" <span class='muted'>Measured {_e(rc.get('measured_utc'))}.</span>"
        body += ("<h4>Positive-control recovery (NOT systematic-review recall)</h4><p>" + line
                 + " <strong>This is not systematic-review recall.</strong> It measures whether the "
                 "committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that "
                 "was never in the known set is not in the denominator, so a high value does <strong>not</strong> "
                 "mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an "
                 "eplerenone trial, for the MRA topic published under the identifier "
                 "spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in "
                 "a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query "
                 "+ registry enumeration, not the seed list); that rebuild is in progress. Recovery is also "
                 "search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's "
                 "and extractor's job.</p>")
    g = s.get("ghost")
    if g and g.get("enumerated"):
        # Registry landscape from AACT (broad query = reach, not precision). The strong, actionable
        # signal is results_only (posted CT.gov results, no publication -> poolable unpublished data);
        # the completed-without-results remainder is a LOOSE upper bound on non-publication.
        body += ("<h4>Registry landscape &amp; unpublished evidence (AACT)</h4>"
                 f"<p>Of <strong>{_e(g.get('enumerated'))}</strong> registry records matching the query "
                 f"(broad — reach, not precision): {_e(g.get('published'))} have a linked publication; "
                 f"<strong>{_e(g.get('results_only'))}</strong> have posted CT.gov results but no "
                 f"publication (<em>poolable unpublished data no published meta in this topic has</em>); "
                 f"{_e(g.get('ghost_upper_bound'))} are completed &ge;12 months ago with neither results "
                 f"nor a linked publication — a <em>loose upper bound</em> on non-publication, inflated by "
                 f"the broad enumeration and by NCT&rarr;PMID linkage misses, not a publication-bias claim. "
                 f"<span class='muted'>{_e(g.get('source'))}.</span></p>")
    for src in s.get("sources", []) or []:
        body += f"<h4>{_e(src.get('name'))}</h4>"
        for q in src.get("queries", []) or []:
            body += f"<pre class='query'>{_e(q)}</pre>"
    return body


def _screening(r, neutral):
    s = r.get("screening")
    reason = _absent(s)
    if reason:
        return _absent_block(reason)
    recs = s.get("records", []) or []
    show_units = _has_publication_units(r) and any(x.get("trial_family_id") for x in recs)
    unit_heads = "<th>Trial family</th><th>Publication role</th>" if show_units else ""
    show_completeness = any(x.get("completeness_state") for x in recs)
    completeness_head = "<th>Completeness</th>" if show_completeness else ""
    def adjudicator_note(x):
        if not x.get("adjudicator_state"):
            return ""
        return (f"<br><code>{_e(x.get('adjudicator_state'))}</code>: recommends "
                f"{_e(x.get('adjudicator_recommended_decision'))}; "
                f"{_e(x.get('adjudicator_rationale'))}")
    if (r.get("search") or {}).get("retrieval"):
        head = ("<tr><th>Record</th><th>Type</th><th>Decision</th><th>Rule</th><th>Found by</th>"
                f"{unit_heads}{completeness_head}<th>Reason (true of the record)</th><th>Verbatim span (from the record)</th></tr>")
        rows = "".join(
            (f"<tr><td>{_e(x.get('id'))}</td><td>{_e(x.get('id_type'))}</td>"
             f"<td class='dec-{_e(x.get('decision'))}'>{_e(x.get('decision'))}</td>"
             f"<td>{_e(x.get('rule_id'))}</td><td>{_e(', '.join(x.get('found_by') or []))}</td>"
            + (f"<td>{_e(x.get('trial_family_id'))}</td><td>{_e(x.get('publication_role'))}</td>"
               if show_units else "")
            + (f"<td>{_e(x.get('completeness_state'))}</td>" if show_completeness else "")
             + f"<td>{_e(x.get('reason'))}{adjudicator_note(x)}</td>"
             + f"<td class='span'>{_e(x.get('span'))}</td></tr>")
            for x in recs)
    else:
        head = ("<tr><th>Record</th><th>Type</th><th>Decision</th><th>Rule</th>"
                f"{unit_heads}{completeness_head}<th>Reason (true of the record)</th><th>Verbatim span (from the record)</th></tr>")
        rows = "".join(
            (f"<tr><td>{_e(x.get('id'))}</td><td>{_e(x.get('id_type'))}</td>"
             f"<td class='dec-{_e(x.get('decision'))}'>{_e(x.get('decision'))}</td>"
             f"<td>{_e(x.get('rule_id'))}</td>"
            + (f"<td>{_e(x.get('trial_family_id'))}</td><td>{_e(x.get('publication_role'))}</td>"
               if show_units else "")
            + (f"<td>{_e(x.get('completeness_state'))}</td>" if show_completeness else "")
            + f"<td>{_e(x.get('reason'))}{adjudicator_note(x)}</td>"
             + f"<td class='span'>{_e(x.get('span'))}</td></tr>")
            for x in recs)
    n_inc = sum(1 for x in recs if x.get("decision") == "include")
    inc_counts = _included_unit_counts(r)
    integ = r.get("integrity")
    integ_html = ""
    if integ:
        retracted, concern = integ.get("retracted", []), integ.get("concern", [])
        if retracted:
            integ_html = (f"<div class='absent'><strong>RETRACTED TRIAL POOLED:</strong> {_e(', '.join(retracted))} "
                          "— this page must not stand until resolved.</div>")
        else:
            retro = integ.get("retrospectively_registered", [])
            msg = (f"<p class='note'><strong>Trial integrity:</strong> none of the {_e(integ.get('n_pooled'))} "
                   f"trials pooled across all outcomes on this page is retracted"
                   + (f"; {len(concern)} under an expression of concern ({_e(', '.join(concern))})" if concern else "")
                   + (f"; {len(retro)} registered retrospectively — after enrolment began, a reporting-bias "
                      f"signal, not disqualifying ({_e(', '.join(retro))})" if retro else "")
                   + f" (checked {_e(integ.get('checked_utc'))} via {_e(integ.get('source'))} + AACT dates).</p>")
            if integ.get("n_not_checkable") is not None:
                msg = (f"<p class='note'><strong>Trial integrity:</strong> {_e(integ.get('n_pooled'))} "
                       f"trials pooled; {_e(integ.get('n_pubmed_checked'))} checked via PubMed, "
                       f"{_e(integ.get('n_not_checkable'))} not checkable (registry-only rows). "
                       f"{_e(integ.get('n_not_assessed', 0))} NOT_ASSESSED (offline lane). "
                       "None of the checked pooled trials is retracted"
                       + (f"; {len(concern)} under an expression of concern ({_e(', '.join(concern))})" if concern else "")
                       + (f"; {len(retro)} registered retrospectively - after enrolment began, a reporting-bias "
                          f"signal, not disqualifying ({_e(', '.join(retro))})" if retro else "")
                       + f" (checked {_e(integ.get('checked_utc'))} via {_e(integ.get('source'))}).</p>")
            integ_html = msg
    # PRISMA 2020 flow (items 16a/16b): counts at every stage, exclusions broken down by rule.
    from collections import Counter as _C
    rule_counts = _C(x.get("rule_id") for x in recs if x.get("decision") == "exclude")
    prim = next((o for o in (r.get("outcomes") or []) if o.get("primary")), None)
    pooled_k = ((prim or {}).get("result") or {}).get("k") if prim else None
    if show_units:
        absent_counts = (_outcome_unit_counts(prim, has_units=True)["absent"]
                         if prim else {"trials": max(inc_counts["trials"] - (pooled_k or 0), 0),
                                       "publications": max(inc_counts["publications"] - (pooled_k or 0), 0)})
        eligible_display = _identity_mod.count_phrase(inc_counts, "trial family")
        absent_display = _identity_mod.count_phrase(absent_counts, "trial family")
    else:
        eligible_display = n_inc
        absent_display = n_inc - (pooled_k or 0)
    engine_refused = sum(
        1 for x in ((prim or {}).get("declared_absent_trials") or [])
        if x.get("state") == "ENGINE_CANNOT_CONSUME"
    )
    if show_units:
        retrieved_refused_display = _identity_mod.count_phrase(
            {"trials": engine_refused, "publications": engine_refused},
            "trial family",
        )
        not_extracted_display = absent_display
    else:
        retrieved_refused_display = engine_refused
        not_extracted_display = max((absent_display or 0) - engine_refused, 0)
    refused_row = (
        "<tr><td>Eligible with outcome retrieved but refused "
        "(engine cannot consume design variance)</td>"
        f"<td>{_e(retrieved_refused_display)}</td></tr>"
        if engine_refused else ""
    )
    n_identified = ((r.get("search") or {}).get("n_records")) or len(recs)
    excl_bits = " · ".join(f"{rid} {n}" for rid, n in sorted(rule_counts.items()))
    flow = ("<h4>Study selection flow (PRISMA 2020)</h4>"
            "<table class='recs'><tr><th>Stage</th><th>n</th></tr>"
            f"<tr><td>Records identified (committed search)</td><td>{_e(n_identified)}</td></tr>"
            f"<tr><td>Records screened (deduplicated)</td><td>{_e(len(recs))}</td></tr>"
            f"<tr><td>Excluded at screening — by rule</td><td>{_e(sum(rule_counts.values()))} ({_e(excl_bits)})</td></tr>"
            f"<tr><td>Met eligibility (P/I/C/design)</td><td>{_e(eligible_display)}</td></tr>"
            f"<tr><td><strong>Pooled in the primary outcome (k)</strong></td><td><strong>{_e(pooled_k)}</strong></td></tr>"
            + refused_row
            + f"<tr><td>Eligible but outcome not extracted from the abstract (full-text pass pending)</td><td>{_e(not_extracted_display)}</td></tr>"
            "</table>"
            "<p class='note'>Every excluded record's rule id, reason and verbatim span are listed below "
            "(PRISMA item 16b: exclusions with reasons).</p>")
    dual = s.get("dual")
    if dual:
        flow += ("<h4>Dual independent screening (PRISMA item 8)</h4>"
                 f"<p>Two independently-implemented rule screeners over {_e(dual.get('n'))} records: "
                 f"agreement <strong>{_e(dual.get('agree'))}/{_e(dual.get('n'))}</strong>, "
                 f"disagreement <strong>{_e(dual.get('disagreement_rate_pct'))}%</strong> "
                 f"({_e(dual.get('disagree'))} records"
                 + (f"; {_e(dual.get('unresolved'))} records UNRESOLVED — bare registry entries with no "
                    "retrievable text, eligibility UNKNOWN not excluded, held out of the rate" if dual.get('unresolved') else "")
                 + f"). {_e(dual.get('method'))} "
                 f"<em>{_e(dual.get('caveat'))}</em></p>")
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
    included_phrase = ((f"{_identity_mod.count_phrase(inc_counts, 'trial family')} included")
                       if show_units else f"{n_inc} included")
    body = (_identifier_scope_block(r) + flow + integ_html + f"<p>{len(recs)} records screened; <strong>{included_phrase}</strong>. "
            "Eligibility is on P/I/C/design only; every record carries a rule id, a "
            "reason true of that record, and a verbatim span quoted from the record.</p>"
            f"<table class='recs'>{head}{rows}</table>")
    pc = s.get("positive_control")
    nc = s.get("negative_control")
    if pc or nc:
        body += "<h4>Controls</h4><ul>"
        if pc:
            body += f"<li><strong>Positive:</strong> {_e(pc)}</li>"
        if nc:
            body += f"<li><strong>Negative:</strong> {_e(nc)}</li>"
        body += "</ul>"
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
        vst = t.get("verified")
        if vst == "verified":
            src = "<span class='vok' title='" + _e(t.get("verify_basis", "")) + "'>✓ verified against source</span><br>" + _e(t.get("source"))
        elif vst == "verified_handchecked":
            src = "<span class='vok' title='" + _e(t.get("verify_basis", "")) + "'>✓ verified (AACT-derived, cross-checked)</span><br>" + _e(t.get("source"))
        elif vst == "not-yet":
            src = "<span class='vno' title='" + _e(t.get("verify_basis", "")) + "'>⚠ NOT YET verified against source</span><br>" + _e(t.get("source"))
        else:
            src = _e(t.get("source"))
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
        # ENDPOINT BINDING (external review of glp1 edaf5f6b, defect 1): the number's own result span and
        # the definition span it was classified against, plus the admissibility verdict every route
        # passes. A hand-verified row with no span binding says so (unbound_legacy) rather than looking bound.
        if t.get("endpoint_binding") or t.get("endpoint_admissibility"):
            eb = [f"binding: {t.get('endpoint_binding') or 'unbound'}",
                  f"admissibility: {t.get('endpoint_admissibility') or 'not evaluated'}"]
            src += "<div class='ident'><em>endpoint binding:</em> " + _e("; ".join(eb))
            if t.get("endpoint_definition_span"):
                src += (f"<br><span class='muted'>definition span: "
                        f"{_e(' '.join(str(t.get('endpoint_definition_span')).split()))}</span>")
            if t.get("endpoint_result_span") and t.get("endpoint_result_span") != t.get("endpoint_definition_span"):
                src += (f"<br><span class='muted'>result span: "
                        f"{_e(' '.join(str(t.get('endpoint_result_span')).split()))}</span>")
            src += "</div>"
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
                    f"adjustment_status: {_e(dk.get('adjustment_status') or 'UNRESOLVED')} "
                    f"({_e((dk.get('adjustment_axis') or {}).get('span') or 'no located adjustment span')}); "
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
    for t in o.get("declared_absent_trials", []) or []:
        alt = t.get("published_alternative") or ((t.get("design") or {}).get("published_alternative"))
        alt_txt = ""
        if alt:
            alt_txt = (f"<br><em>Published alternative disclosed, not pooled:</em> "
                       f"{_num(alt.get('effect'))} ({_e(alt.get('scale'))}), 95% CI "
                       f"{_num(alt.get('ci_low'))}â€“{_num(alt.get('ci_high'))}"
                       + ("; adjusted" if alt.get("adjusted") else "; not labelled adjusted") + ".")
        code = t.get("reason_code") or t.get("state")
        span = t.get("source_span") or t.get("verbatim_span")
        # Raw evidence stays byte-verbatim in review.json; HTML displays normal
        # prose whitespace, including spans transcribed from held PDF text.
        if span:
            span = " ".join(span.split())
        reason_detail = _e(t.get("reason"))
        if code:
            reason_detail += f"<br><code>{_e(code)}</code>"
        audit = t.get("reason_code_audit") or {}
        if audit:
            reason_detail += (
                f"<br><span class='muted'>reason-code audit: "
                f"<code>{_e(audit.get('verdict'))}</code>"
                + (f" {_e(audit.get('source_id'))}: {_e(audit.get('source_span'))}"
                   if audit.get("source_span") else "")
                + "</span>"
            )
        if span:
            reason_detail += f"<br><span class='muted'>span: {_e(span)}</span>"
        if t.get("endpoint_admissibility"):
            rf = t.get("refused_effect") or {}
            if rf.get("effect") is not None:
                reason_detail += (f"<br><span class='muted'>refused number (not pooled): {_e(rf.get('scale'))} "
                                  f"{_num(rf.get('effect'))} (95% CI {_num(rf.get('ci_low'))}–{_num(rf.get('ci_high'))})</span>")
            elif rf.get("ai") is not None:
                reason_detail += (f"<br><span class='muted'>refused counts (not pooled): {_e(rf.get('ai'))}/{_e(rf.get('n1i'))} "
                                  f"vs {_e(rf.get('ci'))}/{_e(rf.get('n2i'))}</span>")
            if t.get("endpoint_definition_span"):
                reason_detail += (f"<br><span class='muted'>definition span: "
                                  f"{_e(' '.join(str(t.get('endpoint_definition_span')).split()))}</span>")
            if t.get("endpoint_result_span") and t.get("endpoint_result_span") != t.get("endpoint_definition_span"):
                reason_detail += (f"<br><span class='muted'>result span: "
                                  f"{_e(' '.join(str(t.get('endpoint_result_span')).split()))}</span>")
        if t.get("state_basis"):
            reason_detail += f"<br><span class='muted'>basis: {_e(t.get('state_basis'))}</span>"
        if t.get("completeness_state"):
            reason_detail += f"<br><span class='muted'>completeness: {_e(t.get('completeness_state'))}</span>"
        if t.get("completeness_basis"):
            reason_detail += f"<br><span class='muted'>completeness basis: {_e(t.get('completeness_basis'))}</span>"
        hm = t.get("harm_absence_state")
        if hm:
            reason_detail += f"<br><code>{_e(hm)}</code>"
            if t.get("harm_source_span"):
                reason_detail += f"<br><span class='muted'>harm span: {_e(t.get('harm_source_span'))}</span>"
        absent_label = _HARM_ABSENCE_STATE_LABEL.get(hm) or _absent_label(t.get('reason'), t.get('state'))
        if code == "SIGNAL_SPURIOUS":
            absent_label = "HM: spurious signal -- source span is not about this harm"
        absent_rows.append(f"<tr><td>{_e(t.get('label'))}</td><td>{_id_cell(t)}</td>"
                           f"<td class='absent-cell'>{_e(absent_label)}</td>"
                           f"<td>{reason_detail}{alt_txt}</td></tr>")
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


def _harms_ledger_block(o):
    from . import harms
    rows = []
    for item in harms.reporting_ledger(o):
        ladder = "; ".join(f"{r.get('rung')}: {r.get('state')} {r.get('obligation', '')}"
                           for r in item.get("source_ladder") or []) or "Source ladder unresolved — checks not recorded"
        rows.append(f"<tr><td>{_e(item.get('label') or item.get('id'))}</td>"
                    f"<td>{_e(item.get('state'))} / {_e(item.get('reason_code', ''))}: {_e(item.get('reason', ''))}</td>"
                    f"<td>{_e(' '.join(str(item.get('span') or 'Span unresolved').split()))}</td><td>{_e(ladder)}</td></tr>")
    heading = ("<div class='absent harms-synthesis-gated'><strong>" + harms.INCOMPLETE_MESSAGE
               + "</strong></div>" if harms.synthesis_incomplete(o) else "<h5>Harms extraction ledger</h5>")
    return (heading + "<table class='arms harms-debt-ledger'><tr><th>Reporting trial</th>"
            "<th>Extraction state / refusal reason</th><th>Located span</th>"
            "<th>Source-ladder obligations</th></tr>" + "".join(rows) + "</table>")


def _outcome_block(o, show_inputs=True, review=None):
    r = (review or {"outcomes": [o]}) if o.get("primary") else {}
    from . import harms
    if harms.synthesis_incomplete(o):
        return (f"<h4>{_e(o.get('name'))}</h4>" + _harms_ledger_block(o)
                + (_trial_inputs(o) if show_inputs else ""))
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
        body += _k2_pool_refusal_block(res, _grade_mod.stale_heterogeneity(r))
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
            ("Prediction interval", (f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))} {_e(_grade_mod.stale_heterogeneity(r))}" if res.get('pi_low') is not None else None)),
            ("τ²", _tau(res.get("tau2")) + " " + _e(_grade_mod.stale_heterogeneity(r)) if res.get("tau2") is not None else None),
            ("I²", str(res.get("i2")) + "% " + _grade_mod.stale_heterogeneity(r) if res.get("i2") is not None else None),
            ("Note", _grade_mod.stale_heterogeneity(r) or res.get("pi_note")),
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
    if o.get("kind") == "harm":
        body += _harms_ledger_block(o)
    return ("<div data-primary-result='true'>" + body + "</div>") if o.get("primary") else body


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
    ra = r.get("reason_code_audit") or {}
    if not ra:
        return ""
    rc = ra.get("counts") or {}
    ua = r.get("unextracted_outcome_audit") or {}
    uc = ua.get("counts") or {}
    rows = []
    for row in (ra.get("rows") or []):
        if row.get("verdict") not in ("REASON_FALSE_VALUE_HELD", "REASON_WRONG_KIND", "NOT_VERIFIABLE"):
            continue
        rows.append(
            f"<tr><td>{_e(row.get('trial_key'))}</td><td>{_e(row.get('outcome'))}</td>"
            f"<td><code>{_e(row.get('stated_reason_code'))}</code></td>"
            f"<td><strong>{_e(row.get('verdict'))}</strong></td>"
            f"<td>{_e(row.get('source_id') or row.get('detail'))}"
            + (f"<br><span class='muted'>{_e(row.get('source_span'))}</span>" if row.get("source_span") else "")
            + "</td></tr>"
        )
    detail = ""
    if rows:
        detail = ("<table class='arms'><tr><th>Trial</th><th>Outcome</th><th>Code</th>"
                  "<th>Audit verdict</th><th>Held source</th></tr>"
                  # every audited row is rendered: a display cap hid the last row whenever a new
                  # refusal was added at the top (the honest-state marker count fell while the audit
                  # grew) -- a count must never be quieter than its own table
                  + "".join(rows) + "</table>")
    return (
        "<div class='audit-block'><h3>Reason-code audit</h3>"
        f"<p><strong>{_e(rc.get('REASON_FALSE_VALUE_HELD', 0))} of {_e(ra.get('N', 0))}</strong> "
        "declared-absent/refusal reason code(s) have a numeric value in a held source; "
        f"{_e(rc.get('REASON_WRONG_KIND', 0))} wrong-kind code(s); "
        f"{_e(rc.get('NOT_VERIFIABLE', 0))} not verifiable from held sources. "
        f"Registered-outcome sweep: {_e(uc.get('HELD_NOT_EXTRACTED', 0))} of {_e(ua.get('N', 0))} "
        "included-trial/outcome pair(s) are held-but-not-extracted.</p>"
        f"{detail}</div>"
    )


def _outcomes(r, neutral):
    outs = [o for o in (r.get("outcomes") or []) if o.get("kind") != "harm"]
    if not outs:
        return _absent_block("no efficacy outcomes in the review object")
    return _definition_audit_block(r) + _reason_code_audit_block(r) + "".join(_outcome_block(o, review=r) for o in outs)


def _harms(r, neutral):
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
    return "".join(_outcome_block(o) for o in harms)


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
    ident = (c.get("pmid") and f"PMID {c.get('pmid')}") or (c.get("doi") and f"DOI {c.get('doi')}")
    body = _kv([
        ("Published comparator", f"{c.get('name')} ({c.get('year')}), {c.get('journal')}"),
        ("Identifier", ident),
        ("Open access", c.get("open_access")),
        ("URL", c.get("url")),
    ])
    for rep in ([] if r.get("comparator_panel") else c.get("reported", []) or []):
        body += f"<p>{_e(rep.get('outcome'))}: {_num(rep.get('estimate'))} ({rep.get('scale')}), 95% CI {_num(rep.get('ci_low'))}–{_num(rep.get('ci_high'))}</p>"
    sc = c.get("scope") or {}
    if sc:
        note_l = str(sc.get("note") or "").lower()
        if sc.get("scope_valid"):
            v = "✓ same question"
        elif "comparator invalid" in note_l:
            v = "COMPARATOR INVALID"
        else:
            v = "⚠ SCOPE MISMATCH"
        topic_level = sc.get("topic_intervention_level") or ("class-level" if sc.get("topic_is_class") else "a single agent")
        comp_level = sc.get("comparator_intervention_level") or ("class-level" if sc.get("comparator_is_class") else "a single agent")
        body += ("<h4>Scope match (is this the same question?)</h4>"
                 f"<p><strong>{v}.</strong> Intervention level: topic is {_e(topic_level)}, "
                 f"comparator is {_e(comp_level)} "
                 f"(match: {_e(sc.get('intervention_level_match'))}); population match: {_e(sc.get('population_match'))}. "
                 f"{_e(sc.get('note'))} <span class='muted'>Decided by one uniform rule applied to every topic "
                 "before the k was seen.</span></p>")
        if sc.get("population_match_basis"):
            pm = sc.get("population_match_basis") or {}
            paed = ", ".join(x.get("trial_id", "") for x in pm.get("pool_has_paediatric_trials", []) or [])
            body += (f"<p><strong>Population-scope basis.</strong> {_e(pm.get('comparator'))}; "
                     f"paediatric pooled trial(s): {_e(paed)}.</p>")
        # When the uniform rule flags a mismatch, resolving a VALID (same-scope) comparator is required.
        # This per-topic note records the resolution: either a single-agent benchmark exists and is
        # used, or none exists (k=1 is the complete single-drug evidence base — itself a finding), or
        # the mismatch coincides with a genuine single-drug reach gap that must be ground down, not
        # excused as scope. Sourced from the topic config; shown verbatim beside the uniform verdict.
        if r.get("comparator_scope_note"):
            body += f"<p><strong>Comparator resolution.</strong> {_e(r.get('comparator_scope_note'))}</p>"
    if r.get("comparator_panel"):
        from .comparator_panel import render
        # Preserve explicit absence disclosures required by the standing page gate.
        # Numeric legacy overlap snapshots remain suppressed; the panel owns the counts.
        for key in ("theirs_k", "shared_k"):
            missing = (c.get("overlap") or {}).get(key)
            if isinstance(missing, str) and missing.startswith(("not stated", "not exactly verifiable")):
                body += f"<p>Legacy comparator extraction, {_e(key)}: {_e(missing)}.</p>"
        return body + render(r)
    body += _comparator_truth_block(c)
    ov = c.get("overlap") or {}
    body += "<h4>Trial-set overlap (an identical estimate on an identical set is arithmetic, not corroboration)</h4>"
    body += _kv([
        ("k in this review (our own search)", ov.get("ours_k")),
        (("k in the comparator (verified against its source text)" if ov.get("theirs_k_source")
          else "k stated in the comparator's own text (auto-extracted)"), ov.get("theirs_k")),
        *([("Comparator k — source", ov.get("theirs_k_source"))] if ov.get("theirs_k_source") else []),
        ("Shared trials", ov.get("shared_k")),
        ("Only in ours", ", ".join(ov.get("only_ours", []) or []) or None),
        ("Only in theirs", ", ".join(ov.get("only_theirs", []) or []) or None),
        ("Overlap method", ov.get("method")),
        ("Note", ov.get("note")),
    ])
    cp2_rows = []
    if ts := c.get("comparator_trial_set"):
        cp2_rows.extend([
            ("Comparator trial-set status", ts.get("status")),
            ("Comparator trial-set source", ts.get("source_kind") or ts.get("note")),
        ])
        if ts.get("trials"):
            cp2_rows.append(("Comparator trial-set list", ", ".join(ts.get("trials") or [])))
    for label, key in [
        ("Quantity match", "quantity_match"),
        ("Comparator recency", "comparator_recency"),
        ("Treatment strategy match", "treatment_strategy_match"),
        ("Outcome match", "outcome_match"),
    ]:
        obj = c.get(key) or {}
        if obj:
            cp2_rows.append((label, obj.get("status")))
            if obj.get("note"):
                cp2_rows.append((label + " note", obj.get("note")))
    if cp2_rows:
        body += "<h4>Comparator second-pass audit</h4>"
        body += _kv(cp2_rows)
    # The auto-extracted comparator k above is a keyword hit in the comparator's abstract/full text and
    # can pick up a sub-analysis count rather than the same-scope pooled total (e.g. omega3: it reads 8,
    # while the comparator's MACE pool is 22 and its same-scope comparable subset is 15). The enumerated,
    # scope-classified comparator k — the finishing metric — is the parity table's figure, not this one.
    body += ("<p class='note'>The comparator <em>k</em> above is auto-extracted from the comparator's own "
             "text and may reference a sub-analysis rather than its same-scope pooled total; the "
             "<strong>enumerated same-scope comparator <em>k</em></strong> (scope-classified, the "
             "finishing metric) is the figure in the parity table, which governs where these differ.</p>")
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
    # PREREGISTRATION vs BUILD (audit 20): distinguish a prospective, protocol-ONLY registration commit
    # from the BUILD commit. The old single "registration SHA" was usually a build commit (protocol +
    # cache + synthesis + page together), which cannot show the protocol preceded synthesis. State which.
    pre = rep.get("preregistration") or {}
    # RETRACTION #2 (round-2 doac-vte P0): a protocol that already CONTAINS the known trial identifiers
    # (PMIDs/NCTs) or effect results is a timestamped internal record of what we knew, NOT a prospective
    # registration — and it fails PRISMA 24a regardless of a protocol-only SHA. Retract the prospective claim
    # wherever the committed protocol text carries results/identifiers.
    _proto_txt = (r.get("protocol") or {}).get("text", "") or ""
    _proto_has_results = bool(re.search(r"\bNCT\d{8}\b|\bPMID[:\s]|\b\d{7,8}\b|hazard ratio|\bHR\b|95%\s*CI|"
                                        r"\bRR\b|odds ratio|rate ratio", _proto_txt))
    if pre.get("prospective") and not _proto_has_results:
        prereg_row = (f"prospectively registered at <code>{_e(pre.get('sha'))}</code> "
                      f"({_e(pre.get('kind'))}) — a protocol-only commit, so the protocol demonstrably "
                      f"preceded the build")
    elif pre.get("prospective") and _proto_has_results:
        prereg_row = ("<strong>NOT prospectively registered</strong> — although a protocol-only commit exists, "
                      "the committed protocol text ALREADY CONTAINS trial identifiers (PMIDs/NCTs) and/or "
                      "results, so it is a timestamped internal record of what we already knew, not a "
                      "prospective registration (and it does not satisfy PRISMA 24a). Retracted.")
    elif pre:
        prereg_row = ("<strong>NOT demonstrated for this topic</strong> — no protocol-only commit exists; "
                      "the protocol first entered the repository inside a build commit "
                      f"(<code>{_e(pre.get('build_sha'))}</code>), so this repository's history does not show "
                      "the protocol preceding synthesis. The PICO is still fixed and replay from the "
                      "committed cache is deterministic; only prospective PRECEDENCE is unproven here.")
    else:
        prereg_row = None
    body = _kv([
        ("Reproduction census failures", rep.get("failures")),
        ("Prospective registration (protocol before synthesis)", prereg_row),
        ("Build / replay SHA", (pre.get("build_sha") or rep.get("protocol_sha"))),
        ("Content hash (review core)", rep.get("review_sha256")),
        ("Replayed offline from committed cache", rep.get("from_cache")),
    ])
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
    if (pa := rep.get("parity")) and not r.get("comparator_panel"):
        body += "<h4>Parity with the published comparator</h4>"
        if pa.get("unrenderable"):
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
        ck = du.get("agree", 0) + du.get("reconcile", 0) + du.get("conflict", 0)
        body += (f"<h4>Independent second extraction (blind)</h4><p>Of this page's pooled numbers, a "
                 f"blind second extractor agreed or reconciled on <strong>{du.get('agree',0)+du.get('reconcile',0)} "
                 f"of {ck}</strong> that are checkable from the abstract "
                 f"({du.get('agree',0)} identical, {du.get('reconcile',0)} same-result-different-statistic, "
                 f"{du.get('conflict',0)} conflict; {du.get('not_checkable',0)} not stated in the abstract). "
                 "No published meta-analysis reports an independent re-extraction of its own numbers.</p>")
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
        body += ("<h4>Canonical claim object (one object, every surface)</h4>"
                 "<p>Each stated result on this page &mdash; whether it is statistically significant, "
                 "whether its interval spans no effect &mdash; is derived from a single claim object, "
                 "not recomputed per surface. At build the rendered page and manuscript are scanned for "
                 "any wording that asserts the opposite of that object; the build is refused on a "
                 f"contradiction. <strong>Claims checked: {_e(n_chk)}; "
                 f"contradictions caught: {n_con}; scope: "
                 f"{_e(_claimgraph_mod.scope_summary(cc.get('scope') or {}))}.</strong>"
                 + ("" if n_con == 0 else " " + _e(json.dumps(cc.get("contradictions"))))
                 + "</p>" + _zero)
        # SEVENTH GATE (categorical/membership + methodological): the two contradiction families a
        # significance check cannot see. Rendered so the reader sees it ran (build refuses on any).
        if (pc := rep.get("proposition_check")) is not None:
            _pcon = pc.get("contradictions") or []
            _pscope = _proposition_mod.scope_summary(pc.get("scope") or pc)
            body += ("<p>Beyond significance, the build also refuses object-backed proposition "
                     "contradictions: publication-bias state, declared-vs-enforced eligibility, "
                     "protocol-SHA byte replay, pooled/rated/retracted counts, search-found membership, "
                     "and state-label collapses. "
                     f"<strong>Proposition contradictions caught: {len(_pcon)}; scope: {_e(_pscope)}.</strong>"
                     + ("" if not _pcon else " " + _e(json.dumps(_pcon))) + "</p>")
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
            body += ("<h4>Protocol ↔ config (two independent sources)</h4>"
                     "<p>The prose protocol and executable config agree on these checked dimensions: "
                     f"<strong>{_e(', '.join(pc.get('agreed_dimensions') or []) or 'none')}</strong>. "
                     "Compared as separate sources.</p>")
    body += ("<div class='absent'><strong>RETRACTED (round-2): reproducibility claim not currently supported.</strong> "
             "We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page "
             "byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical "
             "output files, and running it AT the registered SHA produced an essentially empty review because the "
             "build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that "
             "is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with "
             "hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from "
             "the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent "
             "REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.</div>")
    return body


def _reporting(r, neutral):
    """PRISMA 2020 item-by-item compliance: render each relevant item or declare it absent WITH a
    reason (never blank). Status is derived from the review object, so it cannot drift from what the
    page actually shows."""
    s = r.get("search") or {}
    scr = r.get("screening") or {}
    prot = r.get("protocol") or {}
    prim = next((o for o in (r.get("outcomes") or []) if o.get("primary")), None)
    res = (prim or {}).get("result") or {}
    dual = scr.get("dual")
    has_pi = res.get("pi_low") is not None
    # PRISMA item 24 must be driven by the SINGLE preregistration state (reproduction.preregistration),
    # the same field the Reproducibility row and the manuscript use — never a hardcoded "committed before
    # synthesis" (audit 24/26: that claim drifted from the honest prospective=False sites).
    _pre = (r.get("reproduction") or {}).get("preregistration") or {}
    # RETRACTION #2: protocol containing PMIDs/NCTs/results is not a prospective registration.
    _prosp = bool(_pre.get("prospective")) and not re.search(
        r"\bNCT\d{8}\b|\bPMID[:\s]|\b\d{7,8}\b|hazard ratio|95%\s*CI|odds ratio|rate ratio",
        (prot.get("text", "") or ""))
    _pre_sha = str(_pre.get("sha") or "")[:10]
    _build_sha = str(_pre.get("build_sha") or prot.get("sha") or "")[:10]
    _divs = _proposition_mod.protocol_divergences(r)
    _eligibility_sentence = (
        "Protocol tab - eligibility is rendered from the structured include object, but protocol/config "
        "divergences are disclosed in Reproducibility, so declared == enforced is not asserted."
        if _divs else
        "Protocol tab - eligibility is rendered from the structured include object; the proposition object "
        "records no protocol/config divergence on checked dimensions, so declared == enforced is backed."
    )
    _pub = ((r.get("grade") or {}).get("domains") or {}).get("publication_bias") or {}
    _pub_reporting = (
        "publication bias is NOT ASSESSED automatically; any registry ghost census is descriptive until "
        "a PICO-scoped denominator is available"
        if _pub.get("assessed") is False else
        "registry-based publication bias computed from committed fields"
    )
    items = [
        ("5 Eligibility criteria", bool(prot.get("eligibility")),
         _eligibility_sentence,
         "eligibility not declared"),
        ("6 Information sources + dates", bool(s.get("databases")),
         f"Search tab — {', '.join(s.get('databases', []))}; run {s.get('run_utc')}; AACT snapshot dated on the ghost/recall blocks.",
         "sources not declared"),
        ("7 Full search strategy, verbatim, every source", bool(s.get("sources")),
         "Search tab — the exact PubMed and ClinicalTrials.gov queries are printed verbatim and are re-runnable.",
         "verbatim queries not present"),
        ("8 Selection process (screeners, disagreement)", True,
         (("Two independently-implemented rule screeners; disagreement rate "
           f"{dual.get('disagreement_rate_pct')}% ({dual.get('disagree')}/{dual.get('n')}); rule-based adjudicates. "
           "CAVEAT: both rule sets share an author and the same criteria, so they are NOT statistically "
           "independent and this agreement overstates reliability — a genuinely independent model screener is the next step.")
          if dual else
          "Single deterministic rule-based screen; every decision carries a rule id, a reason true of the record, "
          "and a verbatim span. Dual independent screening is NOT yet implemented (declared, not hidden).")
         + (f" An independent capable-model reader adjudicated the disagreements and agrees with the served "
            f"screener on {dual['model_adjudication'].get('agree_with_served')}/{dual['model_adjudication'].get('n')} "
            "(genuinely independent — different information + method)."
            if dual and dual.get("model_adjudication") else ""),
         ""),
        ("9 Data collection process", True,
         "Results tab + per-trial Source column — source hierarchy (abstract > CT.gov structured > full text > "
         "hand-verified AACT arms), round-trip validation on every extraction, outcome-identity gating; refuse on ambiguity.",
         ""),
        ("15 Certainty assessment", bool(res.get("k")),
         _grade_mod.render_certainty(r.get("grade") or {}) + "; see the domain table for assessed and unassessed domains. " + _grade_mod.stale_heterogeneity(r),
         ""),
        ("16a Flow with counts at every stage", bool(scr.get("records")),
         "Screening tab — PRISMA flow: identified -> screened -> excluded-by-rule (counts) -> eligible -> pooled k -> declared-absent.",
         "no screening flow"),
        ("16b Exclusions with reasons", bool(scr.get("records")),
         "Screening tab — every excluded record lists its rule id, a reason true of the record, and a verbatim span.",
         "no per-record exclusions"),
        ("24a-c Registration & protocol", bool(prot.get("sha")),
         (f"Protocol + Reproducibility tabs — prospectively registered at protocol-only commit SHA "
          f"{_pre_sha}, committed before synthesis; eligibility generated from the structured object."
          if _prosp else
          f"Protocol + Reproducibility tabs — the protocol first entered the repository inside a BUILD commit "
          f"(SHA {_build_sha}), so prospective precedence is NOT demonstrated here and protocol-SHA "
          "byte-for-byte reproduction is not claimed; eligibility is generated from the structured object."),
         "no registration SHA"),
    ]
    rows = []
    for label, ok, present_txt, absent_txt in items:
        status = "✓ present" if ok else "✗ absent"
        txt = present_txt if ok else absent_txt
        cls = "dec-include" if ok else "dec-exclude"
        rows.append(f"<tr><td>{_e(label)}</td><td class='{cls}'>{status}</td><td>{_e(txt)}</td></tr>")
    return ("<p>Compliance with the PRISMA 2020 reporting items, derived from the review object so it "
            "cannot drift from the page. Every item is rendered or declared absent with a reason.</p>"
            "<table class='recs'><tr><th>PRISMA 2020 item</th><th>Status</th><th>Where / why</th></tr>"
            + "".join(rows) + "</table>")


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
    """Registry-machine-signal-restricted partial machine assessment, per pooled trial, built from AACT structured design fields + the
    registry-vs-pooled outcome (Domain 5). Partial-but-honest: domains needing human judgement are
    marked 'not assessed', never guessed. No published-meta comparator in our set renders this."""
    rb = r.get("rob2") or {}
    assessed = rb.get("trials") or {}
    # These signals are assessed for the PRIMARY outcome's pooled trials (that is the scope the builder
    # scans), so the coverage denominator is that set — and any primary-pooled trial with no registry
    # match is shown as an explicit "not assessed" row rather than silently omitted (the defect the
    # fair judge flagged). Trials pooled only in secondary outcomes are outside this scope and are
    # counted separately, not hidden.
    prim = next((o for o in (r.get("outcomes") or []) if o.get("primary")), None)
    pooled = {}
    for t in (prim or {}).get("trials", []) or []:
        pid = str(t.get("id", "")).replace("PMID ", "").strip()
        if pid:
            pooled.setdefault(pid, t.get("label") or "")
    secondary_only = set()
    for o in r.get("outcomes", []) or []:
        if o.get("primary"):
            continue
        for t in o.get("trials", []) or []:
            pid = str(t.get("id", "")).replace("PMID ", "").strip()
            if pid and pid not in pooled:
                secondary_only.add(pid)
    if not pooled and not assessed and not (r.get("funding") or []):
        return _absent_block("no trials pooled in the primary outcome, so there is nothing to assess for risk of bias")
    dom_labels = [("D1_randomisation", "D1 randomisation"), ("D2_deviations", "D2 deviations/blinding"),
                  ("D3_missing_outcome_data", "D3 missing data"), ("D4_outcome_measurement", "D4 measurement"),
                  ("D5_selective_reporting", "D5 selective reporting")]
    head = "<tr><th>Trial</th><th>Overall</th>" + "".join(f"<th>{_e(l)}</th>" for _, l in dom_labels) + "</tr>"
    rows = []
    for pid, a in sorted(assessed.items()):  # stable order (canonical_json sorts keys; render must too)
        cells = "".join(f"<td title='{_e(a['domains'][k]['basis'])}'>{_e(a['domains'][k]['level'])}</td>" for k, _ in dom_labels)
        rows.append(f"<tr><td>{_e(pid)}</td><td><strong>{_e(a.get('overall'))}</strong></td>{cells}</tr>")
    # Pooled trials with NO registry match: render as explicit not-assessed rows, with the reason, so
    # coverage is visible. D1/D2/D4 here are auto-derived from AACT registry fields keyed on NCT;
    # a trial with no NCT/AACT match cannot be machine-assessed and is not guessed.
    unassessed = sorted(pid for pid in pooled if pid not in assessed)
    _na = "not assessed"
    _basis = "no NCT/AACT registry match for this pooled trial - the auto-derived risk-of-bias domains are not machine-assessable here and are not guessed"
    for pid in unassessed:
        cells = "".join(f"<td class='absent-cell' title='{_e(_basis)}'>{_e(_na)}</td>" for _ in dom_labels)
        rows.append(f"<tr><td>{_e(pid)}</td><td class='absent-cell'>{_e(_na)}</td>{cells}</tr>")
    n_ass, n_pool = len(pooled) - len(unassessed), len(pooled)
    # Every pooled trial is assessed: those whose NCT is in the AACT snapshot use registry design +
    # the trial's own text; those AACT does not carry (no NCT, or a non-CT.gov/absent registration such
    # as J-EMPHASIS NCT01115855 or SOUL NCT03914326) are assessed from the ABSTRACT (blinding /
    # randomisation from the trial's own words) rather than left unassessed. The canonical trial
    # identity is shared with the Results table; RoB no longer drops a trial it cannot find in AACT.
    n_reg = sum(1 for pid, a in assessed.items() if pid in pooled and a.get("registry_in_aact"))
    n_abs = n_ass - n_reg
    cover = (f"<strong>Coverage: {n_ass} of {n_pool} primary-outcome pooled trials assessed</strong> "
             f"({n_reg} from registry (AACT) + trial text"
             + (f", {n_abs} from the abstract where AACT does not carry the trial" if n_abs else "")
             + ")"
             + (f"; {len(unassessed)} pooled trial(s) had no assessable source and are shown as "
                f"<em>not assessed</em> ({_e(', '.join(unassessed))}) — never guessed." if unassessed else "")
             + (f" Risk-of-bias signals are scoped to the primary outcome; {len(secondary_only)} trial(s) pooled only in "
                f"secondary outcomes ({_e(', '.join(sorted(secondary_only)))}) are outside this assessment."
                if secondary_only else "")) if n_pool else ""
    uoa = r.get("unit_of_analysis") or []
    uoa_html = ""
    if uoa:
        variance_designs = {
            "cluster-randomized",
            "cluster-randomized crossover",
            "crossover",
            "stepped-wedge",
        }
        variance_uoa = [u for u in uoa if (u.get("design") or "").lower() in variance_designs]
        factorial_uoa = [u for u in uoa if (u.get("design") or "").lower() == "factorial"]
        other_uoa = [u for u in uoa if u not in variance_uoa and u not in factorial_uoa]
        _sens = _uoa_sensitivity(r, [u.get("id") for u in variance_uoa]) if variance_uoa else None
        _sens_txt = ""
        if _sens and len(_sens["points"]) > 1:
            base = _sens["points"][0][1]
            rng = "; ".join(f"&times;{f:g}&rarr;{est}" for f, est in _sens["points"][1:])
            _sens_txt = (f" <strong>The pooled point estimate is NOT invariant to this</strong>: inflating only "
                         f"these trials' variances re-pools (illustrative DL) from {base} to "
                         f"{_sens['points'][-1][1]} ({rng}) — because changing a study's variance changes its "
                         "inverse-variance weight, so both the estimate and its interval move.")
        parts = []
        if variance_uoa:
            items = "; ".join(f"{_e(u.get('id'))} ({_e(u.get('design'))})" for u in variance_uoa)
            parts.append(
                f"{len(variance_uoa)} pooled trial(s) use a clustered, stepped-wedge, or crossover design: "
                f"{items}. If they are reconstructed from patient-level counts, they require an explicit "
                "<strong>design-correlation adjustment</strong> (ICC, cluster-period correlation, or paired "
                "analysis); otherwise their variance is not a simple parallel-arm variance."
                + _sens_txt
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
        uoa_html = (
            "<div class='absent'><strong>Unit-of-analysis/design caveat (disclosed, not silently adjusted)."
            "</strong> "
            + " ".join(parts)
            + " This is a stated limitation and design-key disclosure, not silent simple-parallel pooling.</div>"
        )
    fund = r.get("funding") or []
    fund_html = ""
    if fund:
        def _class(f):
            return f.get("sponsor_class") or f.get("type") or ""
        def _ord(f):
            t = _class(f)
            if t.startswith("industry"):
                return 0
            if t == "mixed":
                return 1
            if t.startswith("public"):
                return 2
            if t.startswith("in_source"):
                return 3
            return 4
        def _celltype(f):
            bits = [f"<strong>{_e(_class(f))}</strong>", _e(f.get("status") or "")]
            if f.get("note"):
                bits.append(f"<em>{_e(f.get('note'))}</em>")
            if f.get("industry_authors_present"):
                bits.append("<em>industry authors present (not sponsor evidence)</em>")
            return "<br>".join(x for x in bits if x)
        def _sponsor_cell(f):
            sponsors = f.get("sponsors") or []
            roles = f.get("role") or []
            body = "; ".join(_e(x) for x in sponsors) or "&mdash;"
            if roles:
                body += "<br><em>roles: " + _e(", ".join(roles)) + "</em>"
            return body
        def _source_cell(f):
            sources = f.get("sources") or [{
                "source_id": f.get("source_id") or f.get("source"),
                "basis_span": f.get("basis_span") or f.get("span"),
                "role": f.get("role") or [],
            }]
            rows = []
            for src in sources:
                label = src.get("source_id") or ""
                span = src.get("basis_span") or ""
                role = src.get("role") or []
                txt = f"<strong>{_e(label)}</strong>: {_e(span)}"
                if role:
                    txt += f" <em>roles: {_e(', '.join(role))}</em>"
                rows.append(txt)
            return "<br>".join(rows) or "&mdash;"
        fund_rows = "".join(
            f"<tr><td>{_e(f.get('id'))}</td><td>{_celltype(f)}</td>"
            f"<td>{_sponsor_cell(f)}</td><td>{_e(f.get('scanned') or f.get('source'))}</td>"
            f"<td>{_source_cell(f)}</td></tr>"
            for f in sorted(fund, key=_ord))
        n_ind = sum(1 for f in fund if _funding_mod.industry_tied(f))
        n_ns_ft = sum(1 for f in fund if f.get("status") == "none_stated_in_held_text"
                      and (f.get("scanned") or "").startswith("full text"))
        n_ns_ab = sum(1 for f in fund if f.get("status") == "none_stated_in_held_text"
                      and not (f.get("scanned") or "").startswith("full text"))
        n_in_source_not_held = sum(1 for f in fund if f.get("sponsor_class") == "in_source_not_held")
        # UNKNOWN must not be folded into the negative denominator (audit 23): the industry-funded fraction
        # is over trials whose funding is KNOWN (industry / mixed / public / non-profit, or an industry
        # drug-supply tie), NOT over the whole pool. "not stated" and "declared (source unclassified)" are
        # unknown for the industry property and are reported separately, never as "not industry-funded".
        n_known = sum(1 for f in fund if _funding_mod.funding_known(f))
        n_unknown = len(fund) - n_known
        extra_not_held = (f"; {n_in_source_not_held} point to a funding statement outside held text"
                          if n_in_source_not_held else "")
        fund_html = ("<div class='absent'><strong>Funding / conflict-of-interest disclosure (per pooled "
                     "trial, from source — disclosed, not adjusted).</strong> Industry-funded trials are a "
                     "documented reporting-bias dimension (they tend to report more favourable results). For "
                     "each pooled trial the funding source is classified from held text (full text preferred, "
                     "abstract fallback) and the registry sponsor is shown as a second source when available; "
                     "when held text and registry disagree, both source spans are rendered. Industry author "
                     "affiliations are flagged only as affiliations, never sponsor evidence. Including an "
                     "industry <em>drug-supply</em> tie in an otherwise independently funded trial: "
                     f"<strong>{n_ind} of {n_known} known</strong> ({n_unknown} unknown) pooled trials are "
                     "industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN "
                     "funding — unknown-funding trials are reported separately below, not counted as "
                     "independently funded — for comparison against a "
                     "comparator's). Absence is labelled by how "
                     f"deeply we looked — {n_ns_ft} with no funding statement in the <strong>full text</strong> "
                     f"(genuinely silent) and {n_ns_ab} where only the <strong>abstract</strong> was available "
                     "(full text not retrieved) — so 'not stated' is never presented as 'independently funded'. "
                     "The harness <strong>does not adjust</strong> for funding (the per-trial bias magnitude is "
                     "not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never "
                     "inferred."
                     "<table class='arms'><tr><th>Trial</th><th>Funding</th><th>Sponsors / roles</th>"
                     f"<th>Scanned</th><th>Source evidence</th></tr>{fund_rows}</table></div>")
    # Arm-contrast disclosure (TIER-1 structural fix): whether each pooled trial's intervention of interest
    # is parser-confirmed as a randomised contrast (differs across arms) or a fail-open/background inclusion.
    # The fail-open state is VISIBLE (a trial with no registry arm data reads 'contrast unverified'), never a
    # silent verified-looking inclusion. Never an adjustment; a disclosure computed from AACT arm structure.
    ac = (r.get("arm_contrast") or {}).get("trials") or {}
    ac_html = ""
    if ac:
        stale = (r.get("arm_contrast") or {}).get("stale_block_unrenderable") or {}
        _AC_LABEL = {"verified": "parser-confirmed contrast",
                     "background_only": "BACKGROUND IN ALL ARMS — not a randomised contrast",
                     "unverified_granularity": "contrast unverified (registry class label / dev code)",
                     "unverified_no_contrast": "contrast unverified (no arm-level contrast coded)",
                     "unverified_no_arm_data": "contrast unverified — no registry arm data"}
        _AC_ORD = {"background_only": 0, "unverified_no_arm_data": 1, "unverified_no_contrast": 2,
                   "unverified_granularity": 3, "verified": 4}
        n_ver = sum(1 for e in ac.values() if e.get("status") == "verified")
        n_bg = sum(1 for e in ac.values() if e.get("status") == "background_only")
        ac_rows = "".join(
            f"<tr><td>{_e(pid)}</td><td>{_e(_AC_LABEL.get(e.get('status'), e.get('status')))}</td>"
            f"<td title='{_e(e.get('basis'))}'>{_e('; '.join(e.get('differing') or []) or '&mdash;')}</td></tr>"
            for pid, e in sorted(ac.items(), key=lambda kv: (_AC_ORD.get(kv[1].get("status"), 9), kv[0])))
        if stale:
            ac_html += (
                "<div class='absent'><strong>UNRENDERABLE stale contrast block.</strong> "
                f"{_e(stale.get('reason'))}; current pooled trial ids: "
                f"{_e(', '.join(stale.get('current_pooled_trial_ids') or []))}; suppressed stale ids: "
                f"{_e(', '.join(stale.get('dropped_trial_ids') or []))}.</div>"
            )
        ac_html += ("<div class='absent'><strong>Parser-confirmed contrast disclosure (per pooled trial, from the "
                   "AACT arm-label parser - disclosed, not an adjustment).</strong> This measures the parser, not the trial. Eligibility should test "
                   "what actually DIFFERS between the randomised arms, not the mere presence of the drug word: "
                   "a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same "
                   "agent, randomising a different drug) is not a randomised comparison of it. For each pooled "
                   "trial the randomised contrast is reconstructed from AACT <code>design_groups</code> + "
                   f"<code>interventions</code>: <strong>{n_ver} of {len(ac)}</strong> pooled trials have a "
                   "parser-confirmed contrast (the intervention of interest matched a differing coded arm)"
                   + (f"; <strong>{n_bg} is background in every arm (flagged)</strong>" if n_bg else "")
                   + ". A trial with no registry arm data, or coded under a class label / development code we "
                   "cannot machine-match, is shown as <em>contrast unverified</em> — a VISIBLE fail-open state, "
                   "never silently treated as verified. "
                   "<table class='arms'><tr><th>Trial</th><th>Contrast status</th><th>Randomised difference</th>"
                   f"</tr>{ac_rows}</table></div>")
    from .limitations import _rob_sensitivity_block, _grade_block
    sens = r.get("rob_sensitivity") or {}
    sens_html = ""
    _prim_refused = next(((o.get("result") or {}).get("pool_refused") for o in (r.get("outcomes") or []) if o.get("primary")), None)
    if not sens.get("full") and _prim_refused:
        sens_html = _ROB_SENS_REFUSED_HTML.format(code=_e(_prim_refused.get("code")))
    if sens.get("full"):
        sens_html = "<h4>Risk-of-bias sensitivity</h4>" + _rob_sensitivity_block(dict(sens, formally_assessed=_grade_mod._rob_domain(r).get("assessed")))
    g = r.get("grade") or {}
    grade_html = (f"<h4 data-grade-certainty='true'>{_e(_grade_mod.render_certainty(g))}</h4>" + _grade_block(g)) if g else ""
    rsc = r.get("rob_spancheck") or {}
    rsc_html = ""
    if rsc.get("agreement_rate") is not None:
        rsc_html = ("<div class='banner'><strong>RoB spans span-checked (cross-family): "
                    f"{round(rsc['agreement_rate']*100)}% agreement</strong> ({rsc.get('supported')} of "
                    f"{rsc.get('supported',0)+rsc.get('not_supported',0)} scoreable), from a seeded sample of "
                    f"{rsc.get('n_sampled')} model/registry-derived domain ratings independently checked by a "
                    f"different model family (Fable) against each trial abstract; {rsc.get('unclear')} were "
                    "unscoreable (no claim, or a conservative not-stated rating). This check itself found and "
                    "fixed a real error &mdash; one trial (EMPHASIS-HF) was mislabelled NON_RANDOMIZED by the "
                    "registry, contradicted by its abstract; the RoB block was also visibly broken until a "
                    "human review caught it. The number is here because a RoB block a reader cannot trust is "
                    "worthless (<code>docs/rob_spancheck.json</code>).</div>")
    return (f"<p>{cover}</p>" + rsc_html + uoa_html + ac_html + fund_html
            + "<p><strong>Registry-machine-signal-restricted partial machine assessment</strong> (per pooled trial) &mdash; NOT a "
            "formal human risk-of-bias assessment, which requires human judgements the registry cannot supply. "
            "These are computed from what is machine-available "
            f"({_e(rb.get('source') or 'AACT registry fields')}). <strong>Domain 5 (selective reporting)</strong> "
            "is computed from the trial's REGISTERED primary outcome vs the outcome we pooled — a machine-checkable "
            "signal most published meta-analyses do not report. D1/D2/D4 use AACT structured allocation/masking "
            "fields. <strong>D3 (missing outcome data) is NOT ASSESSED for any trial — a stated limitation, not "
            "a per-trial judgement</strong>: the harness has no outcome-missingness evidence source (study "
            "discontinuation is not outcome missingness), so D3 is structurally unassessable here and is never "
            "rated; the attrition figures are shown as context only. This caps overall GRADE certainty below "
            "<em>high</em> corpus-wide (a required bias domain is unassessed), and it would be fixed by a "
            "committed outcome-missingness source (AACT <code>milestones</code> / the publication's flow "
            "diagram: analysed-vs-randomised at the outcome). Other risk-of-bias judgements that need human "
            "reading are likewise marked <em>not assessed</em>: partial-but-honest, never guessed. Hover a cell "
            "for its basis.</p>"
            f"<table class='recs'>{head}{rows_join(rows)}</table>"
            + sens_html + grade_html)


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


def render_page(review: dict, neutral: bool = False) -> str:
    from .certificate import render as render_certificate
    tabs_spec = [(tid, lbl) for tid, lbl in TABS if not (neutral and tid in NEUTRAL_DROP)]
    nav = "".join(f'<button data-t="{tid}" onclick="show(\'{tid}\')">{_e(lbl)}</button>' for tid, lbl in tabs_spec)
    body = ("<div class='absent'><strong>AACT_NOT_MEASURED</strong>: registry inputs have not "
            "been measured into a valid per-topic cache; registry dates, sponsors and arm "
            "contrasts are unavailable.</div>" if review.get("aact_status") == "AACT_NOT_MEASURED" else "")
    for tid, lbl in tabs_spec:
        body += (f'<section class="tab" id="tab-{tid}">'
                 f'<h3 class="tabname">{_e(lbl)}</h3>{_R[tid](review, neutral)}</section>')
    if not neutral:
        body = render_certificate((review.get("reproduction") or {}).get("certificate")) + body
    title = _e(review.get("title") or review.get("slug"))
    sub = ("Meta-analysis" if neutral else
           "Reproducible meta-analysis harness — auditability, not authority")
    # PINNED AUDIT IDENTITY (P0): the content hash uniquely pins the bytes an auditor read, so two
    # audits of "the same URL" that saw different states can be told apart (the noac-warfarin problem).
    # GitHub Pages serves only HEAD, so a /@<sha>/ route is not available; the hash IS the pin -- an
    # auditor cites it, and a different hash is provably a different version. Shown conspicuously in the
    # header, not buried in the Reproducibility tab.
    _rep = review.get("reproduction") or {}
    _csha = str(_rep.get("review_sha256") or "")
    _pin = ""
    if _csha:
        _pin = (f"<div style='font-size:12px;opacity:0.85;margin-top:4px'><strong>Pinned audit identity</strong>"
                f" — content hash of the canonical review object (review_sha256) <code>{_e(_csha[:16])}</code>; "
                "exact served bytes are attested separately (html_sha256 in manifest.json and the production "
                "record on the production-records branch). Cite this hash when auditing; a different hash is "
                "a different version of this page.</div>")
    return ("<!doctype html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{_CSS}</style></head><body>"
            f"<header><h1>{title}</h1><div class=sub>{sub}</div>{_pin}</header>"
            f"<nav>{nav}</nav><main>{body}</main><script>{_JS}</script></body></html>")
