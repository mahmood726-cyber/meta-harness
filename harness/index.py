"""Generated front page + index. Never hand-maintained.

Scans docs/reviews/*/manifest.json and writes docs/index.html. Deterministic:
reviews are sorted by slug. The front page states what this surface is and is not.
"""
from __future__ import annotations
import glob
import html
import json
import os
import re

_E = lambda x: html.escape("" if x is None else str(x), quote=True)

_FRONT = """<div class="banner">
<h2>What this is</h2>
<p>A reproducible harness that builds meta-analyses from a committed protocol, and
publishes each as a tabbed, auditable page. Every page here passed a two-limb gate:
it reproduces from a fresh clone with zero census failures and its served analysis
method equals its declared method; and it names a published open-access comparator
with the trial-set overlap stated.</p>
<h2>What this is not</h2>
<p>It is <strong>not</strong> a claim of stronger evidence than the peer-reviewed
comparators. The offer is <strong>greater auditability</strong>: every number is
traceable to a committed source, every absence is declared rather than left blank,
and any hand-edit breaks the gate. A page whose estimate matches its comparator on
an identical trial set is arithmetic, not corroboration &mdash; so the overlap is
stated on every page.</p>
</div>"""

_CSS = """body{font:15px/1.55 system-ui,Segoe UI,Arial,sans-serif;margin:0;color:#12232e;background:#f7f8fa}
header{background:#12232e;color:#fff;padding:20px 22px}header h1{margin:0;font-size:21px}
main{max-width:900px;margin:0 auto;padding:22px}
.banner{background:#eaf4fb;border-left:4px solid #4ea1d3;padding:2px 16px 12px;margin:0 0 20px;border-radius:6px}
.banner h2{font-size:15px;margin:14px 0 4px;color:#1d3b4d}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #dbe3e8;padding:7px 9px;text-align:left;font-size:13.5px}
th{background:#eef2f5}a{color:#1f6f9c;text-decoration:none}a:hover{text-decoration:underline}
.empty{color:#7a4b00;background:#fff4e5;border:1px solid #f0c27b;padding:12px;border-radius:6px}
"""


def _parity_section(docs_dir: str) -> str:
    """Render the parity table from the committed docs/parity.json (a measurement snapshot: each
    comparator's pooled trial list enumerated from its own reference list/full text, matched to
    ours; the comparable comparator k excludes out-of-scope / double-counted-substudy /
    observational / non-prespecified trials). The finishing metric: our k vs the comparable
    same-scope comparator k, with a named reason for every difference — including where THEIR
    extra trials are the ones that should not count."""
    p = os.path.join(docs_dir, "parity.json")
    if not os.path.exists(p):
        return ""
    try:
        rows = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    at = sum(1 for r in rows if str(r.get("status", "")).startswith("PARITY"))
    color = {"PARITY": "#e6f4ea", "PARITY-effective": "#e6f4ea", "NEAR": "#fff8e1"}
    body = (f"<div class='banner'><h2>Parity with the published comparator (the finishing metric)</h2>"
            f"<p>For each same-scope topic: our pooled <em>k</em> vs the <strong>comparable</strong> "
            f"comparator <em>k</em> (the comparator's pooled list, enumerated from its own references/"
            f"full text, after removing trials that are out of scope, double-counted substudies, "
            f"observational, or non-prespecified for the outcome). <strong>{at} of {len(rows)}</strong> "
            f"same-scope topics are at parity within scope; every remaining shortfall has a named reason. "
            f"This is a measurement snapshot (the enumeration is model-assisted; scope calls are "
            f"assessments, and each pooled recovery was verified against source before it counted).</p>"
            "<table><tr><th>Topic</th><th>Our k</th><th>Comparable comparator k</th><th>Status</th>"
            "<th>Named reason for any difference</th></tr>")
    for r in rows:
        st = str(r.get("status", ""))
        bg = color.get(st, "#fdecec" if st in ("GAP", "COMPARATOR-INVALID", "NOT-ENUMERABLE") else "#fff")
        body += (f"<tr style='background:{bg}'><td>{_E(r.get('slug'))}</td>"
                 f"<td>{_E(r.get('our_k'))}</td><td>{_E(r.get('comparable_comparator_k'))}</td>"
                 f"<td>{_E(st)}</td><td>{_E(r.get('reason'))}</td></tr>")
    return body + "</table></div>"


def _currency_section(docs_dir: str) -> str:
    """Corpus currency, published as it falls: how many topics carry an invalidation flag (STALE)
    and why. Self-counting from each review's committed invalidation verdict, so the number cannot
    drift — if 28 of 32 are current, it says 28 of 32."""
    rows = []
    total = 0
    for rp in sorted(glob.glob(os.path.join(docs_dir, "reviews", "*", "review.json"))):
        try:
            rev = json.load(open(rp, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        total += 1
        inv = rev.get("invalidation") or {}
        if inv.get("stale"):
            slug = os.path.basename(os.path.dirname(rp))
            codes = ", ".join(sorted({r.get("code") for r in inv.get("reasons", []) if r.get("code")}))
            rows.append((slug, codes))
    if not total:
        return ""
    stale = len(rows)
    current = total - stale
    lis = "".join(f"<li><code>{_E(s)}</code> — {_E(c)}</li>" for s, c in rows)
    # protocol<->config divergences across the corpus (two independent sources), self-counted.
    ndiv = ndiv_topics = 0
    for rp in glob.glob(os.path.join(docs_dir, "reviews", "*", "review.json")):
        try:
            rv = json.load(open(rp, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        dd = ((rv.get("protocol_config") or {}).get("divergences")) or []
        if dd:
            ndiv_topics += 1
            ndiv += len(dd)
    div_line = (f" Protocol↔config: <strong>{ndiv} divergence(s) across {ndiv_topics} of {total} topics</strong> "
                f"(prose protocol vs executable config, compared as two independent sources; each a defect "
                f"to resolve or a dated amendment to declare)." if total else "")
    return (f"<div class='banner'><h2>Corpus currency (invalidation propagation)</h2>"
            f"<p><strong>{current} of {total} topics current; {stale} of {total} STALE.</strong> A topic "
            f"is STALE when a committed signal invalidates a dependent output — a pooled trial is "
            f"retracted, the primary outcome is reported by a trial that could not be pooled, a trial "
            f"flagged ELIGIBLE is not pooled, or a search source errored (retrieval completeness unproven). "
            f"The flag poisons every surface: each STALE topic renders the reason at the top of its page "
            f"and cannot read as a settled current estimate. Published as it falls."
            + (f"<ul>{lis}</ul>" if rows else "") + div_line + "</p></div>")


def _recovery_section(docs_dir: str) -> str:
    """Recovery-pipeline scoreboard from docs/recovery_log.json: the harness's corrections are not
    systematically self-flattering, and we measure it one source-verified trial at a time."""
    p = os.path.join(docs_dir, "recovery_log.json")
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    sb = d.get("scoreboard") or {}
    rows = "".join(
        f"<li><strong>{_E(a.get('trial'))}</strong> &rarr; {_E(a.get('topic'))}: "
        f"<code>{_E(a.get('status'))}</code>"
        + (f" &mdash; {_E(a.get('before'))} &rarr; {_E(a.get('after'))}" if a.get('before') else "")
        + (f" <span class='muted'>{_E(a.get('note'))}</span>" if a.get('note') else "") + "</li>"
        for a in (d.get("attempts") or []))
    rd = d.get("recall_denominator") or {}
    recall_line = (f"<p><strong>Baseline unaided search recall: {_E(rd.get('baseline_unaided_recall'))}</strong> "
                   f"&mdash; against the {_E(rd.get('clean_eligible_denominator'))} source-verified-eligible "
                   f"missing trials. Every one is a confirmed miss of the current search; this is the honest "
                   f"zero from which search improvement is measured. Recall is computed ONLY against "
                   f"source-verified-eligible entries &mdash; the test set itself contained "
                   f"{_E((sb.get('test_set_errors_found') or 0))} errors, caught by source verification.</p>"
                   if rd else "")
    return (f"<div class='banner'><h2>Recovery scoreboard &mdash; corrections are not systematically "
            f"flattering</h2>{recall_line}<p><strong>{sb.get('recovered')} recovered of {sb.get('attempted')} "
            f"attempted</strong>: {sb.get('tightened')} tightened, {sb.get('cost_significance')} lost "
            f"significance, {sb.get('toward_null_stayed_nonsig')} moved toward the null; "
            f"{sb.get('refused_on_source')} refused on source, {sb.get('scope_pending')} held on scope. "
            f"Every recovery is source-verified (audit-relayed numbers are not sources); the vocabulary "
            f"blind spot is measured by where a recovery BREAKS, not by a forward scan that over-counts."
            f"<ul>{rows}</ul></p></div>")


def _participant_flow_section(docs_dir: str) -> str:
    """Render docs/participant_flow.json: per-arm participant-flow acquisition for the attrition (D3)
    risk-of-bias domain. DATA ONLY -- no D3 judgement is assigned yet. The honest number is the
    coverage cascade: not every pooled trial can even have registry flow, so the denominator is
    enumerated by kind (no NCT / NCT but no posted results / usable flow), never assumed."""
    p = os.path.join(docs_dir, "participant_flow.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    c = d.get("coverage_cascade") or {}
    tp = d.get("topic_d3_potential") or {}
    pooled = c.get("pooled_trials_across_32_topics")
    nonct = c.get("no_nct__registry_cannot_supply_flow")
    nores = c.get("has_nct_but_no_ctgov_results_posted")
    usable = c.get("has_nct_with_usable_participant_flow")
    if not pooled:
        return ""
    return (f"<div class='banner'><h2>Participant-flow acquisition for the attrition domain (D3) "
            f"&mdash; data landed, judgement pending</h2>"
            f"<p><strong>Of {pooled} pooled trials across 32 topics: {usable} have usable per-arm "
            f"participant flow</strong> on ClinicalTrials.gov (started / completed / not-completed with "
            f"verbatim non-completion reasons). The rest are not a failure to fetch but a boundary of the "
            f"source: <strong>{nonct} have no NCT at all</strong> (older or non-US trials the registry "
            f"cannot describe) and <strong>{nores} have an NCT but posted no structured results</strong> "
            f"to CT.gov. The non-completion REASON is carried verbatim; attrition is never derived from "
            f"started-minus-completed (the AMPLITUDE-O rule).</p>"
            f"<p><strong>{tp.get('topics_with_at_least_one_usable_flow_trial')} of "
            f"{tp.get('topics_total')} topics could have a real D3 judgement</strong> once judgement runs "
            f"(&ge;1 pooled trial with usable flow); "
            f"<strong>{tp.get('topics_where_all_pooled_trials_have_usable_flow')}</strong> have usable flow "
            f"for every pooled trial. No D3 judgement is assigned in this pass &mdash; the field is "
            f"populated and rendered; the judgement is a separate, fresh pass.</p></div>")


def _iv_iron_strands_section(docs_dir: str) -> str:
    """Render the iv-iron declared strands via the SHARED renderer (harness.page.render_strands_section),
    the SAME function the topic page uses, so the index and the topic page cannot disagree about what the
    review concluded. Numbers are object-derived from the one artefact (docs/iv_iron_strands.json)."""
    p = os.path.join(docs_dir, "iv_iron_strands.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    from .page import render_strands_section
    inner = render_strands_section(d)
    if not inner:
        return ""
    return (f"<div class='banner'><h2>iv-iron HF-hospitalisation: declared strands (topic-page and index "
            f"render the same artefact)</h2>{inner}</div>")


def _search_recall_section(docs_dir: str) -> str:
    """Render search recall HONESTLY. The headline is now the named regression corpus, not
    prospective validation: all current topics have been exposed, so future held-out validation
    must use an external register revealed only when the prospective run begins."""
    ph = os.path.join(docs_dir, "search_recall_regression_corpus.json")
    pd = os.path.join(docs_dir, "search_recall.json")
    out = ""
    if os.path.exists(ph):
        try:
            h = json.load(open(ph, encoding="utf-8"))
        except (OSError, ValueError):
            h = None
        if h:
            sm = h.get("summary") or {}
            rows = "".join(
                f"<tr><td>{_E(r.get('slug'))}</td><td><code>{_E(r.get('state'))}</code></td>"
                f"<td>{_E(r.get('hits_in_boolean_set') if r.get('hits_in_boolean_set') is not None else 'unknown')}</td>"
                f"<td>{_E(r.get('recalled'))} of {_E(r.get('denominator'))}"
                + (f" ({_E(len(r.get('missed_pmids') or []))} missed)" if r.get('missed_pmids') else "")
                + (f" &mdash; <span class='muted'>{_E(r.get('error'))}</span>" if r.get('error') else "") + "</td></tr>"
                for r in (h.get("per_topic") or []))
            hist = "".join(f"<li>{_E(e.get('measured_utc'))}: {_E(e.get('recall_text'))} (engine <code>{_E(str(e.get('engine_sha'))[:12])}</code>)</li>"
                           for e in (h.get("history") or []))
            out += (f"<div class='banner'><h2>Search recall, regression corpus (not prospective validation): "
                    f"<strong>{_E(sm.get('recall_text'))}</strong> "
                    f"known-eligible trials recalled unaided</h2>"
                    f"<p>Measured {_E(sm.get('measured_utc'))} on the {_E(sm.get('topics'))} named regression-corpus "
                    f"topics in <code>registry/regression_recall_topics.json</code>. All 32 current corpus topics are "
                    f"disqualified as held-out because they have been exposed through audits, URLs, commit history, or "
                    f"regression work; prospective validation will use topics held outside the repository and revealed "
                    f"only when that run begins. Denominator per topic = pooled primary trials + "
                    f"eligible-declared-absent trials with a PMID. Engine pinned at "
                    f"<code>{_E(str(h.get('engine_sha'))[:12])}</code>; any change to the engine must publish a new "
                    f"regression-corpus row here before it can land.</p>"
                    f"<table><tr><th>topic</th><th>source state</th><th>boolean hits</th><th>recalled</th></tr>{rows}</table>"
                    + (f"<p class='muted'>Not scored (search state not OK/ZERO): {_E(', '.join(sm.get('topics_not_scored') or []))}.</p>"
                       if sm.get("topics_not_scored") else "")
                    + f"<p class='muted'>History (every published measurement, oldest first):</p><ul>{hist}</ul></div>")
    if os.path.exists(pd):
        try:
            d = json.load(open(pd, encoding="utf-8"))
        except (OSError, ValueError):
            d = None
        if d:
            out += (f"<div class='absent'><strong>Development-set recall (not validation): "
                    f"{_E(d.get('concept_query_unaided_recall'))}.</strong> This earlier figure was measured on the six "
                    f"trials hard-coded into the engine&rsquo;s target list, all already source-verified and pooled before "
                    f"the engine was written; it is a fit statistic, not recall, and the engine&rsquo;s own next measurement "
                    f"on held records found 0/64, 2/80, 6/80 and 6/71. It is retained here so the correction is visible, "
                    f"and it is not the number this site reports for search recall.</div>")
    return out


def _gate_scorecard_section(docs_dir: str) -> str:
    """Render the measured gate scorecard summary from registry/gate_scorecard.json."""
    try:
        from . import gate_scorecard
        s = gate_scorecard.summary(os.path.dirname(docs_dir))
    except Exception:
        return ""
    false_gates = ", ".join(s.get("false_refusal_gates") or [])
    return (f"<div class='banner'><h2>Gate scorecard: plant validations and production refusals</h2>"
            f"<p><strong>{_E(s.get('gate_count'))} production gates accounted for</strong>; "
            f"<strong>{_E(s.get('plant_only_count'))}</strong> are <code>PLANT_ONLY</code>; "
            f"<strong>{_E(s.get('unvalidated_count'))}</strong> are <code>UNVALIDATED</code>; "
            f"<strong>{_E(s.get('production_true_refusal_gate_count'))}</strong> have production true refusals; "
            f"<strong>{_E(s.get('false_refusal_gate_count'))}</strong> have adjudicated false refusals"
            f"{': ' + _E(false_gates) if false_gates else ''}. The named pessimistic incident is "
            f"{_E(s.get('named_pessimistic_incident'))}. "
            f"<strong>{_E(s.get('auditor_sentence'))}</strong> "
            f"Served JSON: <code>gate_scorecard.json</code>.</p></div>")


def _verification_section(docs_dir: str) -> str:
    """The strongest single integrity claim, gate-enforced: every pooled number on every page is
    verified against its committed source span, and a gate limb refuses any page that pools a number
    whose digits are not located in its source. Self-counting so the number cannot drift stale."""
    n = ok = 0
    for rp in glob.glob(os.path.join(docs_dir, "reviews", "*", "review.json")):
        try:
            rev = json.load(open(rp, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for o in rev.get("outcomes", []) or []:
            for t in o.get("trials", []) or []:
                n += 1
                if t.get("verified") in ("verified", "verified_handchecked"):
                    ok += 1
    if not n:
        return ""
    return (f"<div class='banner'><h2>Every pooled number is verified against its source "
            f"(gate-enforced)</h2><p><strong>All {ok} of {n} pooled trial-outcome numbers</strong> across "
            f"these pages have their digits located in the committed source span they cite (arm counts, "
            f"effect+CI, or per-arm mean/SD). A publication-gate limb "
            f"(<code>check_pooled_verified</code>) <strong>refuses any page that pools a number not found "
            f"in its source</strong>, so this cannot silently stop being true. No published meta-analysis "
            f"makes — or can be forced to keep — this claim about every one of its numbers.</p></div>")


def _error_coverage_section(docs_dir: str) -> str:
    """Render the meta-analysis error-library coverage from docs/error_coverage.json: how many
    documented meta-analysis mistakes every live review is screened against, and which remain
    unchecked (the work queue). A claim no published meta-analysis makes, and exactly measurable."""
    p = os.path.join(docs_dir, "error_coverage.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    per = d.get("per_review") or []
    if not per:
        return ""
    checkable = per[0].get("checkable_total")
    lo, hi = d.get("min_screened"), d.get("max_screened")
    rng = f"{lo}" if lo == hi else f"{lo}–{hi}"
    kinds = d.get("by_kind", {})
    nc = d.get("not_checked", [])
    body = (f"<div class='banner'><h2>Screened against a meta-analysis error library "
            f"(measured, not asserted)</h2>"
            f"<p>Every documented meta-analysis mistake is converted into one of: a <strong>gate limb</strong> "
            f"that refuses a finished review, a <strong>regression test</strong> with a plant that fires "
            f"pre-fix, or a <strong>rendered disclosure</strong> when it is a judgement the harness cannot "
            f"make. Of <strong>{d.get('library_size')}</strong> documented errors catalogued "
            f"({kinds.get('GATE_LIMB',0)} gate limbs, {kinds.get('REGRESSION_TEST',0)} regression tests, "
            f"{kinds.get('RENDERED',0)} rendered disclosures), <strong>{checkable}</strong> have an enforced "
            f"mechanism, and <strong>every live review is screened against {rng} of {checkable}</strong> of "
            f"them. This is a claim no published meta-analysis makes about itself, and it is directly "
            f"checkable (each entry names its mechanism in <code>harness/error_library.py</code>; the count "
            f"regenerates via <code>scripts/error_coverage.py</code>).</p>")
    if nc:
        items = "; ".join(f"{e.get('id')} {e.get('label')}" for e in nc)
        body += (f"<p><strong>Not yet checked (the work queue, stated not hidden):</strong> {_E(items)}. "
                 f"These are the next checks to build, in severity order &mdash; chiefly unit-of-analysis "
                 f"errors (shared-control double-counting, cluster design effect, crossover).</p>")
    return body + "</div>"


def _error_rate_section(docs_dir: str) -> str:
    """Render the blind accuracy census from docs/error_rate.json: our OWN measured extraction-error
    rate. Every pooled number was independently re-extracted from committed source by an offline checker
    blind to the stored value; disagreements were hand-adjudicated. Object-derived numbers only."""
    p = os.path.join(docs_dir, "error_rate.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    pop = d.get("census_population") or d.get("population")
    rv = d.get("independently_reverified")
    ex = d.get("exact_match")
    dis = d.get("disagreements_pre_adjudication")
    err = d.get("confirmed_our_errors_after_adjudication")
    nr = d.get("not_recheckable_from_abstract")
    when = d.get("measured_utc")
    lo, hi = (d.get("disagreement_wilson95") or [None, None])[:2]
    if pop is None:
        return ""
    prov = (f"<em>Measured on {_E(when)} against the {pop} pooled numbers committed at that time "
            f"(the sample is committed in <code>docs/error_rate_sample.json</code>); a freshness invariant "
            f"refuses a stale figure if the pooled population changes.</em> " if when else "")
    return (f"<div class='banner'><h2>We measured our own error rate (no meta-analysis reports this about "
            f"itself)</h2>"
            f"<p>{prov}Every claim the harness makes rests on the assumption that its numbers are right. So we "
            f"measured it: all <strong>{pop}</strong> pooled numbers were independently re-extracted from the "
            f"committed source by an offline checker <strong>blind to the stored value</strong>, then compared "
            f"deterministically. <strong>{rv} of {pop}</strong> were re-extractable from the same source the "
            f"checker was given; <strong>{ex} of {rv} matched exactly</strong> (&lsquo;exactly&rsquo; = the "
            f"effect and both confidence limits agree to the rounding of the source's printed precision, and "
            f"counts agree as integers). The "
            f"<strong>{dis}</strong> disagreements were hand-adjudicated against source: on adjudication "
            f"<strong>{err}</strong> was a genuine error on our side "
            f"(a gastrointestinal-adverse-event outcome that had pooled the trial's OVERALL adverse-event "
            f"count &mdash; a wrong endpoint that had passed every gate; found here and fixed), and the "
            f"remainder were checker-side (an incidence-rate ratio the checker called a plain rate ratio "
            f"with identical numbers; an on-treatment vs intention-to-treat estimand choice where our ITT "
            f"value is the standard one). The other <strong>{nr}</strong> numbers source from "
            f"ClinicalTrials.gov results or full text, so they were not re-checkable from the abstract and "
            f"are not counted as verified here. <strong>The pre-adjudication disagreement rate was {dis} of "
            f"{rv}</strong>"
            + (f" (Wilson 95% CI {round(lo*100,1)}&ndash;{round(hi*100,1)}%)" if lo is not None else "")
            + ". <strong>The honest caveat that makes this credible:</strong> the blind checker and the "
            "extractor share a model architecture, so this is an <strong>internal-consistency</strong> "
            "measure, not an independent accuracy estimate &mdash; a genuinely independent, cross-family "
            "(non-Claude) re-extraction is the stronger check, and is being built. It is nonetheless the "
            "single most important number the project lacked, and it is measured, adjudicated, and "
            "reproducible from <code>scripts/error_rate_compare.py</code>.</p></div>")


def _external_agreement_section(docs_dir: str) -> str:
    """Pooled-level external validation from docs/external_agreement.json: our pooled primary vs the published
    comparator meta's reported pooled estimate. Object-derived numerals."""
    p = os.path.join(docs_dir, "external_agreement.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    n = d.get("n_topics")
    if not n:
        return ""
    ag = d.get("same_estimand_agree", d.get("agree_within_12pct", 0))
    sd = d.get("same_estimand_diverge", 0)
    cp = d.get("cross_estimand_pending", 0)
    co = d.get("cross_estimand_opposite", 0)
    nc = d.get("non_comparable", 0)
    same_n = ag + sd
    return (f"<div class='banner'><h2>External validation: our pooled numbers vs the published meta-analyses'</h2>"
            f"<p>The strongest check is against an external hand-built standard: our pooled primary estimate vs "
            f"the published comparator meta-analysis's reported pooled estimate. But a comparison is only 'the "
            f"same question' when the two share the <strong>same estimand</strong> — an RR is not an OR is not an "
            f"HR (an odds ratio sits further from 1 than a risk ratio for common events; a hazard ratio is a rate, "
            f"not a risk), so comparing them on the log scale as if interchangeable is a "
            f"<em>comparator-context mismatch</em>. Keying on the estimand: of {n} topics, <strong>{same_n} are "
            f"same-estimand comparisons, and {ag} of those agree within ~12%</strong> on the log scale "
            f"(the genuine same-question agreements); {sd} same-estimand comparison(s) diverge (adjudicated). "
            f"<strong>{cp} are cross-estimand</strong> (e.g. our HR vs their OR): direction-consistent but the "
            f"same-question agreement claim is <strong>SUPPRESSED</strong> until a scale-matched, "
            f"event-rate-justified conversion is verified — a previous version counted these as agreements, "
            f"which compared different quantities. {co} cross-estimand comparison(s) disagree on direction, and "
            f"{nc} outcome(s) are not comparable at all (a mean difference vs a rate). Every case is enumerated "
            f"in <code>docs/external_agreement.json</code>. This is pooled-level agreement. "
            f"<strong>The per-trial head-to-head was attempted against the gold standard</strong> "
            f"(the Cochrane review CD013505 of metformin for PCOS ovulation): its pooled OR 2.64 (k=13) sits "
            f"far from our single-trial OR 8.25 (k=1) &mdash; a stark, honest illustration of the small-k "
            f"weakness the expansion tier targets &mdash; but a true number-by-number check is <strong>blocked "
            f"even for Cochrane</strong>: its per-woman arm counts live in forest-plot images, not the "
            f"open-access text (only per-cycle data is tabulated). Per-trial ground truth needs vision/OCR or "
            f"IPD (<code>docs/cochrane_headtohead.json</code>).</p>"
            + _evidence_base_line(docs_dir)
            + "</div>")


def _evidence_base_line(docs_dir: str) -> str:
    """One line answering 'is small k our limit or the question's?' from docs/evidence_base.json."""
    p = os.path.join(docs_dir, "evidence_base.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    c, gs, gl = d.get("n_complete"), d.get("n_gap_small"), d.get("n_gap_large")
    if c is None:
        return ""
    return (f"<p><strong>Is our small k our limit or the question's?</strong> Of the topics with a same-scope "
            f"comparator, <strong>{c}</strong> are at or above the <em>complete same-scope evidence</em> "
            f"(our k equals the comparable comparator's &mdash; the smallness is the literature's, not ours); "
            f"{gs} are 1&ndash;2 trials short (bar-limited, decomposed on the page); and {gl} face a genuinely "
            f"larger literature where the gap is named per topic (open-label excluded, different outcome "
            f"definition, prophylaxis-vs-treatment, or reach). So small k is labelled, not hidden &mdash; and "
            f"where it is the question's limit we say so.</p>")


def _crossfamily_section(docs_dir: str) -> str:
    """Cross-family independence from docs/crossfamily.json: a non-Claude family (Gemini) re-extracts the same
    source, so agreement is genuinely independent of our extractor/checker. Object-derived numerals."""
    p = os.path.join(docs_dir, "crossfamily.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    gv = d.get("gemini_vs_ours") or {}
    agree, dis = gv.get("agree"), gv.get("disagree")
    rate = d.get("gemini_agreement_rate_over_comparable")
    three = d.get("three_family_agree_ours_codex_gemini")
    wrong = d.get("confirmed_wrong_after_adjudication")
    if agree is None or rate is None:
        return ""
    comp = agree + (dis or 0)
    return (f"<div class='banner'><h2>Independent cross-family check &mdash; the fix for &lsquo;everything is "
            f"self-assessed&rsquo;</h2>"
            f"<p>Our checker and our error-rate sampler share a model architecture with our extractor, so the "
            f"internal error rate is a consistency measure, not independent accuracy. So a <strong>different "
            f"model family</strong> &mdash; Gemini 3.1 Pro, via AGY, sharing no architecture with our pipeline "
            f"&mdash; independently re-extracted every pooled number from the same committed source. It "
            f"<strong>agreed with our stored value on {agree} of {comp}</strong> comparable numbers "
            f"(<strong>{round(rate*100,1)}%</strong>); on <strong>{three}</strong> numbers all three families "
            f"(our harness, a GPT-5 checker, and Gemini) agree. Every one of the <strong>{dis}</strong> "
            f"disagreements was hand-adjudicated against source and <strong>{wrong}</strong> was a wrong number: "
            f"they are a documented approved-dose rule, intention-to-treat vs the trial's on-treatment primary, "
            f"a rounding tie, one registry-vs-abstract count, and one CT.gov-vs-abstract estimand difference "
            f"(all disclosed in <code>docs/crossfamily.json</code>). A model call is treated as a source &mdash; "
            f"the Gemini outputs are committed, so this regenerates without re-calling the model. "
            f"<strong>Three-family agreement is a far stronger claim than our own dual extraction.</strong></p>"
            + _crossfamily_judge_line(docs_dir)
            + "</div>")


def _definition_audit_section(docs_dir: str) -> str:
    """Full-corpus cross-family DEFINITION audit from docs/definition_audit.json: does each pooled result
    match its outcome LABEL (composite components, timepoint, population, analysis set), not just the number."""
    p = os.path.join(docs_dir, "definition_audit.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    n, cand, both = d.get("n_rows_audited"), d.get("n_candidates"), d.get("n_flagged_both_families")
    a = d.get("adjudication_counts") or {}
    if not n:
        return ""
    ref, disc, ok, q = a.get("refused_defect_fixed"), a.get("composite_heterogeneity_disclose_queued"), \
        a.get("already_disclosed_accept"), a.get("queued_adjudication")
    return (f"<div class='banner'><h2>Cross-family definition audit: is the number under the RIGHT label?</h2>"
            f"<p>A single cross-family QA pass over four rows had caught a defect (TECOS's 4-point composite "
            f"pooled under a 3-point label) that every internal gate passed &mdash; so we ran it over the "
            f"<strong>whole corpus</strong>. Two independent families (Gemini via AGY and Fable) re-read every "
            f"one of the <strong>{n}</strong> pooled rows and asked not just &lsquo;does the number match&rsquo; "
            f"but <strong>does the outcome DEFINITION match the label</strong> &mdash; composite component set, "
            f"timepoint, population, analysis set. <strong>{cand} of {n}</strong> rows were flagged for a "
            f"possible definition mismatch (<strong>{both}</strong> by both families). Adjudicated against "
            f"source: <strong>{ref}</strong> were genuine wrong-endpoint/population defects and were refused at "
            f"source this cycle (two omega-3 trials whose composite was not MACE; two probiotics trials pooling "
            f"a per-protocol/completers set, not ITT); {disc} are the well-known heterogeneity of pooling each "
            f"trial's own primary MACE (3&ndash;5 component composites) under one generic label, now being "
            f"disclosed; {ok} were already disclosed on the page (a stated subgroup or estimand); and {q} remain "
            f"queued for per-row adjudication. This class &mdash; a right number under a slightly wrong label "
            f"&mdash; is invisible to a value check and was only found by a different model family reading the "
            f"source fresh. The audit is now a standing check (<code>docs/definition_audit.json</code>) and its "
            f"guard refuses component/population mismatches at build time.</p></div>")


def _crossfamily_judge_line(docs_dir: str) -> str:
    """The cross-family BLIND JUDGING result (a non-Claude judge re-rating auditability)."""
    p = os.path.join(docs_dir, "crossfamily_judge.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    nt, nj = d.get("n_topics"), d.get("n_dimension_judgments")
    ow, ag = d.get("gemini_rates_ours_more_auditable"), d.get("gemini_agrees_with_claude")
    if not nj:
        return ""
    return (f"<p><strong>And the judge was re-run cross-family.</strong> The page-vs-comparator auditability "
            f"verdict previously rested on a Claude-family judge. A non-Claude judge (Gemini) re-judged the "
            f"same blinded pairs on {nj} dimension-comparisons across {nt} topics and rated <strong>our page "
            f"more auditable on {ow} of {nj}</strong> (agreeing with the Claude judge on {ag} of {nj}, and "
            f"more favourable to us on the rest). The auditability result is <strong>not an artefact of an AI "
            f"liking a page in its own style</strong> &mdash; a different family reaches the same verdict "
            f"(<code>docs/crossfamily_judge.json</code>).</p>")


def _provenance_section(docs_dir: str) -> str:
    """Provenance mix (tracked metric) from docs/provenance.json + the three standing limitations the
    reviewer asked to be stated plainly. Object-derived numerals only."""
    p = os.path.join(docs_dir, "provenance.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    tot, ab, na = d.get("total"), d.get("abstract"), d.get("non_abstract")
    if not tot:
        return ""
    return (f"<div class='banner'><h2>Where the numbers come from &mdash; and what we do not yet claim</h2>"
            f"<p><strong>Provenance mix (a tracked metric).</strong> Of {tot} pooled numbers, "
            f"<strong>{ab}</strong> come from the trial <strong>abstract</strong> (the authors' headline "
            f"result &mdash; the weakest source, though the safest default) and <strong>{na}</strong> from "
            f"higher tiers (ClinicalTrials.gov structured results, PMC full text, hand-verified arm counts). "
            f"Nearly every wrong number the audit found came from an abstract. <strong>We tested how far the "
            f"abstract share can be driven down and the answer is a bar, not effort:</strong> only a handful of "
            f"the abstract-sourced rows have a ClinicalTrials.gov structured result available to promote to, and "
            f"CT.gov results carry their own estimand/definition risk &mdash; exactly the class the definition "
            f"audit just proved (a structured number can be the wrong composite/timepoint). Full-text promotion "
            f"is available but per-row expensive (as done for the SGLT2 heart-failure hospitalizations). So "
            f"abstract-dominance is <strong>bar-limited, not effort-limited</strong>; the honest fix is not "
            f"bulk-promotion but the definition guards that make an abstract number safe to pool "
            f"(<code>scripts/provenance.py</code>).</p>"
            f"<p><strong>Stated limitations (plainly).</strong> (1) The comparators are <strong>open-access "
            f"only</strong> &mdash; we benchmark against free reviews, not necessarily the best ones. "
            f"(2) Protocol registration is <strong>self-hosted</strong> (a git commit SHA), with no external "
            f"timestamp authority &mdash; it proves order relative to our own history, not against a third "
            f"party. (3) <strong>Topic selection is ours</strong>, which can flatter the success rate; the "
            f"expansion tier is preregistered in one batch with declared-hard cases to counter this. "
            f"(4) The headline accuracy figure began as an <strong>internal-consistency</strong> measure; an "
            f"independent non-Claude model family has since re-extracted every pooled row against the same "
            f"committed source (reported in the cross-family section above), so it now carries a genuinely "
            f"independent check &mdash; though the census and blind-judging arms still share our architecture, "
            f"which leaves that cross-family re-extraction as the sole fully-decorrelated signal.</p></div>")


def _screen_section(docs_dir: str) -> str:
    """Screening reproducibility from docs/screen_reproducibility.json: an independent blind (model)
    screener vs the rule-screener, Cohen's kappa over abstract-bearing records. Object-derived."""
    p = os.path.join(docs_dir, "screen_reproducibility.json")
    if not os.path.exists(p):
        return ""
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    nd = d.get("n_decided")
    k = d.get("cohens_kappa")
    agree = d.get("raw_agreement")
    sens = d.get("sensitivity_blind_vs_ours")
    na = d.get("n_not_assessable_no_abstract_text")
    if nd is None or k is None:
        return ""
    return (f"<div class='banner'><h2>Screening reproducibility, measured against an independent blind "
            f"screener</h2>"
            f"<p>An independent screener &mdash; blind to our decision, working from title and abstract "
            f"against the same eligibility criteria &mdash; re-screened the pooled records. Over the "
            f"<strong>{nd}</strong> records that carry an abstract, agreement with our rule-screener was "
            f"<strong>{round(agree*100,1)}%</strong> (Cohen's &kappa; = <strong>{k}</strong>), and it "
            f"recovered <strong>{round(sens*100,1)}%</strong> of the records we included. This second "
            f"screener is model-assisted, so this is a measure of screening <em>reproducibility</em>, not "
            f"accuracy against a human gold standard; "
            + (f"{na} records with no abstract text in the cache (registry / citation-chase entries) could "
               f"not be shown to it and are reported as not-assessable rather than dropped from the base. "
               if na else "")
            + "Regenerable via <code>scripts/screen_reproducibility.py</code>.</p></div>")


def _spec_curve_numbers(docs_dir: str) -> dict:
    """Derive the specification-curve summary from docs/spec_curve.json."""
    p = os.path.join(docs_dir, "spec_curve.json")
    if not os.path.exists(p):
        return {}
    try:
        d = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    topics = [v for k, v in d.items() if not k.startswith("_") and isinstance(v, dict) and not v.get("not_applicable")]
    if not topics:
        return {}
    n = len(topics)
    dir_stable = sum(1 for v in topics if v.get("direction_stable"))
    sig_stable = sum(1 for v in topics if v.get("significance_stable"))
    # flips where OUR default (RE_HKSJ) is non-significant but a less conservative spec is significant
    conservative = 0
    for v in topics:
        sb = v.get("significance_by_spec", {})
        if sb.get("RE_HKSJ") is False and (sb.get("RE_z") or sb.get("FE")):
            conservative += 1
    return {"n": n, "dir_stable": dir_stable, "sig_stable": sig_stable, "conservative": conservative}


def _spec_curve_section(docs_dir: str) -> str:
    n = _spec_curve_numbers(docs_dir)
    if not n:
        return ""
    return (f"<div class='banner'><h2>Specification curve: the headline is the most conservative standard "
            f"choice</h2>"
            f"<p>Each primary outcome with &ge;2 trials (<strong>{n['n']}</strong> of them) was re-pooled "
            f"under three defensible specifications on the model/interval axis: random-effects with the "
            f"Hartung-Knapp interval (the harness default), random-effects with a Wald/z interval, and a "
            f"fixed-effect model. <strong>The direction of effect was stable across all three in "
            f"{n['dir_stable']} of {n['n']}</strong> — the sign never depends on the choice. Statistical "
            f"significance was identical across all three in only <strong>{n['sig_stable']} of {n['n']}</strong>, "
            f"and in <strong>{n['conservative']} of {n['n']}</strong> the divergence runs one way: our default "
            f"interval is <strong>not</strong> significant while the less conservative fixed-effect or z "
            f"specification would be. In other words the harness reports the widest of the standard intervals "
            f"at small k, so where we do claim significance it survives the stricter choice &mdash; the "
            f"curve is regenerable via <code>scripts/spec_curve.py</code>.</p></div>")


def _fair_numbers(docs_dir: str) -> dict:
    """Derive the fair-comparison numbers from the committed JSON records (prisma_fair.json,
    fair_judge.json) so the banner prose cannot drift stale as topics are added. Returns a dict of
    exactly the integers the banner interpolates; if a record is missing, returns {} and the banner
    falls back to a numberless statement."""
    n = {}
    pf_path = os.path.join(docs_dir, "prisma_fair.json")
    if os.path.exists(pf_path):
        try:
            pf = json.load(open(pf_path, encoding="utf-8"))
        except (OSError, ValueError):
            pf = {}
        rows = {k: v for k, v in pf.items() if not k.startswith("_")}
        inc = {k: v for k, v in rows.items() if v.get("comparator_fulltext_source") != "NONE"}
        items = list(next(iter(inc.values()))["ours"].keys()) if inc else []
        n["prisma_total"] = len(rows)
        n["prisma_scorable"] = len(inc)
        n["prisma_cells"] = len(inc) * len(items)
        n["prisma_comp_present"] = sum(1 for s in inc for i in items if inc[s]["comparator"][i].get("present"))
        n["prisma_ours_lacks"] = sum(1 for s in inc for i in items
                                     if inc[s]["comparator"][i].get("present") and not inc[s]["ours"][i])
        n["prisma_we_present"] = sum(1 for s in inc for i in items
                                     if inc[s]["ours"][i] and not inc[s]["comparator"][i].get("present"))
    fj_path = os.path.join(docs_dir, "fair_judge.json")
    if os.path.exists(fj_path):
        try:
            fj = json.load(open(fj_path, encoding="utf-8"))
        except (OSError, ValueError):
            fj = {}
        slugs = [k for k in fj if not k.startswith("_")]
        _res = lambda s: (fj[s].get("resolved") or {})
        _pd = lambda s: (_res(s).get("per_dimension") or {})
        n["judge_total"] = len(slugs)
        n["judge_more_auditable_ours"] = sum(1 for s in slugs if _res(s).get("more_auditable") == "ours")
        for dmn in ("search_reproducibility", "per_number_source_traceability", "completeness_of_evidence",
                    "risk_of_bias_reporting", "declared_absence_exclusion_transparency", "overall_auditability"):
            n[f"judge_{dmn}_ours"] = sum(1 for s in slugs if _pd(s).get(dmn) == "ours")
            n[f"judge_{dmn}_comp"] = sum(1 for s in slugs if _pd(s).get(dmn) == "comparator")
    return n


def _fair_section(docs_dir: str) -> str:
    """The fair-comparison banner, with every count DERIVED from prisma_fair.json / fair_judge.json at
    render time (never typed into prose — the '95 of 95' drift class). The four auditability dimensions
    are stated as a single margin only when they genuinely agree (all-ours), else spelled out."""
    n = _fair_numbers(docs_dir)
    if not n.get("prisma_cells") or not n.get("judge_total"):
        return ("<div class='banner'><h2>Fair comparison (measured against comparator FULL TEXT)</h2>"
                "<p>The fair full-text comparison record is being regenerated.</p></div>")
    rob_o, rob_c = n["judge_risk_of_bias_reporting_ours"], n["judge_risk_of_bias_reporting_comp"]
    comp_complete = n["judge_completeness_of_evidence_comp"]
    tot = n["judge_total"]
    # State each auditability dimension's ACTUAL margin (ours-comparator), so a dimension we do not sweep
    # is shown as it is, never rounded up to a clean "N-0". Order: strongest first.
    _labels = [("per_number_source_traceability", "per-number traceability"),
               ("declared_absence_exclusion_transparency", "declared-absence"),
               ("overall_auditability", "overall auditability"),
               ("search_reproducibility", "search reproducibility")]
    _parts = [f"{lbl} {n[f'judge_{key}_ours']}&ndash;{n[f'judge_{key}_comp']}" for key, lbl in _labels]
    aud_clause = "winning <strong>" + "; ".join(_parts) + "</strong>"
    # RoB direction-aware: it is not necessarily "to us".
    rob_dir = ("to us" if rob_o > rob_c else "to the comparator" if rob_c > rob_o else "even")
    return (
        "<div class='banner'><h2>Fair comparison (measured against comparator FULL TEXT)</h2>"
        "<p>An earlier countable PRISMA comparison read the comparators' <em>abstracts</em> against our "
        "full pages &mdash; a confound in our favour, which we flagged and then fixed by reading each "
        f"comparator's OA <strong>full text</strong> ({n['prisma_scorable']} of {n['prisma_total']} topics "
        "scorable; the remainder have no obtainable comparator full text). Scored fairly, full-text vs "
        f"full-page across the {n['prisma_scorable']} scorable topics ({n['prisma_cells']} cells, including "
        f"the continuous-outcome pages): the comparators satisfy <strong>{n['prisma_comp_present']} of "
        f"{n['prisma_cells']}</strong> checkable PRISMA-item cells, yet there is <strong>no reporting item a "
        f"comparator's full text presents that our page lacks ({n['prisma_ours_lacks']} of "
        f"{n['prisma_cells']})</strong>, while we present <strong>{n['prisma_we_present']}</strong> that even "
        "their full text does not (chiefly per-record exclusion reasons and a machine-checkable registration "
        "SHA). The margin narrowed under fair measurement, as it should; the direction held.</p>"
        f"<p><strong>Fair blind re-judge (full-text vs full-page, {n['judge_total']} topics, order-blinded).</strong> "
        "Restating the record on the fair basis, whatever it shows: our pages are judged more "
        f"<strong>auditable on {n['judge_more_auditable_ours']} of {n['judge_total']}</strong>, {aud_clause}; "
        f"the comparator is more <strong>complete on {comp_complete} of {tot}</strong> (larger "
        f"<em>k</em>); risk-of-bias reporting splits <strong>{rob_o}&ndash;{rob_c}</strong> {rob_dir}. "
        "The split holds across the whole judged set, binary and continuous alike &mdash; each page is more "
        "auditable and less complete than its comparator &mdash; but it is not a clean sweep on every "
        "sub-dimension: the comparator wins search reproducibility on one topic and edges risk-of-bias "
        "reporting, and those losses are shown here rather than hidden. So the earlier abstract-based "
        "&lsquo;15 clean wins&rsquo; is superseded by a stable domain split: <strong>we win transparency and "
        "auditability; we lose completeness/<em>k</em></strong> &mdash; the same conclusion the parity table "
        "reaches, confirmed by a blind reader on full text. The judge also flagged real defects in our pages "
        "(a risk-of-bias table covering only a subset of pooled trials; a retraction line whose count did not "
        "equal k); those are recorded, not hidden.</p></div>")


# Static numerals allowed in the thesis/continuous prose banners: facts that do NOT change as the corpus
# grows. Each carries a reason. Anything RISKY (a decimal effect size, an "N of M" aggregate, or an integer
# >= 10) that is neither here nor object-derived makes build_index RAISE — the permanent version of the
# "95 of 95 drifted stale" lesson, enforced fail-closed because the pre-commit hook regenerates the index.
_STATIC_PROSE_NUMERALS = {
    "9": "citation-chase reach: trials recovered of those reachable (fixed historical measurement)",
    "626": "declared-absent cells the independent V2 extractor scanned (fixed completed analysis)",
    "44": "Week 44 — the excluded regional trials' end-of-treatment timepoint (fixed trial design)",
    "68": "Week 68 — semaglutide's pre-registered primary timepoint (fixed protocol)",
    "95": "the 95% confidence-interval label (fixed)",
    "3.1": "Gemini 3.1 Pro — the cross-family checker's model version (a name, not a claim)",
    "12": "the ~12% log-scale agreement threshold for external validation (fixed methodological choice)",
    "013505": "Cochrane review identifier CD013505 (a catalogue code, not a claim)",
    "25": "the raw first-pass flip count (25) shown alongside its correction to 12 genuine recoveries",
    "19": "topics whose provisional GRADE certainty rose when spurious downgrades were removed (fixed historical measurement, vs the pre-fix commit)",
}


def _prose_derived_numerals(docs_dir: str) -> set:
    """Live numerals the banners legitimately cite, derived from the objects (semaglutide's k/MD/CI and the
    three continuous parity k's), so they are accounted rather than whitelisted."""
    out = set()
    p = os.path.join(docs_dir, "reviews", "semaglutide-obesity-weight", "review.json")
    if os.path.exists(p):
        try:
            res = next((o["result"] for o in json.load(open(p, encoding="utf-8")).get("outcomes", [])
                        if o.get("primary")), {})
            for v in (res.get("k"), res.get("estimate"), res.get("ci_low"), res.get("ci_high")):
                if isinstance(v, (int, float)):
                    out.add(str(abs(round(v, 2)) if isinstance(v, float) else v))
        except (OSError, ValueError, KeyError):
            pass
    pj = os.path.join(docs_dir, "parity.json")
    if os.path.exists(pj):
        try:
            for r in json.load(open(pj, encoding="utf-8")):
                if r.get("slug", "").startswith(("esketamine", "melatonin", "semaglutide")):
                    out.add(str(r.get("our_k")))
                    out.add(str(r.get("comparable_comparator_k")))
        except (OSError, ValueError):
            pass
    # error-rate banner numerals (derived from docs/error_rate.json)
    ep = os.path.join(docs_dir, "error_rate.json")
    if os.path.exists(ep):
        try:
            e = json.load(open(ep, encoding="utf-8"))
            for v in (e.get("population"), e.get("census_population"), e.get("current_pooled_population"),
                      e.get("independently_reverified"), e.get("exact_match"),
                      e.get("disagreements_pre_adjudication"), e.get("confirmed_our_errors_after_adjudication"),
                      e.get("not_recheckable_from_abstract")):
                if isinstance(v, int):
                    out.add(str(v))
            for v in (e.get("disagreement_wilson95") or []):
                if isinstance(v, (int, float)):
                    out.add(str(round(v * 100, 1)))
        except (OSError, ValueError):
            pass
    # spec-curve summary numerals
    sc = _spec_curve_numbers(docs_dir)
    for v in sc.values():
        if isinstance(v, int):
            out.add(str(v))
    # cross-family numerals (derived from docs/crossfamily.json)
    cp = os.path.join(docs_dir, "crossfamily.json")
    if os.path.exists(cp):
        try:
            cf = json.load(open(cp, encoding="utf-8"))
            gv = cf.get("gemini_vs_ours") or {}
            for v in (gv.get("agree"), gv.get("disagree"),
                      (gv.get("agree") or 0) + (gv.get("disagree") or 0),
                      cf.get("three_family_agree_ours_codex_gemini"),
                      cf.get("confirmed_wrong_after_adjudication")):
                if isinstance(v, int):
                    out.add(str(v))
            if isinstance(cf.get("gemini_agreement_rate_over_comparable"), (int, float)):
                out.add(str(round(cf["gemini_agreement_rate_over_comparable"] * 100, 1)))
        except (OSError, ValueError):
            pass
    # external-agreement numerals (derived from docs/external_agreement.json)
    ea = os.path.join(docs_dir, "external_agreement.json")
    if os.path.exists(ea):
        try:
            e = json.load(open(ea, encoding="utf-8"))
            ag = e.get("same_estimand_agree", e.get("agree_within_12pct"))
            sd = e.get("same_estimand_diverge", 0)
            for v in (e.get("n_topics"), ag, sd, e.get("cross_estimand_pending"),
                      e.get("cross_estimand_opposite"), e.get("non_comparable"),
                      (ag + sd) if isinstance(ag, int) and isinstance(sd, int) else None):
                if isinstance(v, int):
                    out.add(str(v))
            for row in e.get("rows", []):
                for v in (row.get("our_estimate"), row.get("their_estimate")):
                    if isinstance(v, (int, float)):
                        out.add(f"{round(v, 2):g}")
                        out.add(str(round(v, 2)))
        except (OSError, ValueError):
            pass
    # definition-audit numerals
    da = os.path.join(docs_dir, "definition_audit.json")
    if os.path.exists(da):
        try:
            v = json.load(open(da, encoding="utf-8"))
            for x in (v.get("n_rows_audited"), v.get("n_candidates"), v.get("n_flagged_both_families")):
                if isinstance(x, int):
                    out.add(str(x))
            for x in (v.get("adjudication_counts") or {}).values():
                if isinstance(x, int):
                    out.add(str(x))
        except (OSError, ValueError):
            pass
    # cross-family JUDGE numerals
    cj = os.path.join(docs_dir, "crossfamily_judge.json")
    if os.path.exists(cj):
        try:
            j = json.load(open(cj, encoding="utf-8"))
            for v in (j.get("n_topics"), j.get("n_dimension_judgments"),
                      j.get("gemini_rates_ours_more_auditable"), j.get("gemini_agrees_with_claude")):
                if isinstance(v, int):
                    out.add(str(v))
        except (OSError, ValueError):
            pass
    # evidence-base classification numerals
    eb = os.path.join(docs_dir, "evidence_base.json")
    if os.path.exists(eb):
        try:
            b = json.load(open(eb, encoding="utf-8"))
            for v in (b.get("n_complete"), b.get("n_gap_small"), b.get("n_gap_large")):
                if isinstance(v, int):
                    out.add(str(v))
        except (OSError, ValueError):
            pass
    # cochrane head-to-head numerals (pooled k, effects)
    ch = os.path.join(docs_dir, "cochrane_headtohead.json")
    if os.path.exists(ch):
        try:
            c = json.load(open(ch, encoding="utf-8"))
            cp = c.get("cochrane_pooled") or {}
            for v in (cp.get("k"), cp.get("effect"), (c.get("ours") or {}).get("estimate"),
                      (c.get("ours") or {}).get("k"), c.get("cochrane_trials_listed")):
                if isinstance(v, int):
                    out.add(str(v))
                elif isinstance(v, float):
                    out.add(f"{round(v, 2):g}")
        except (OSError, ValueError):
            pass
    # provenance-mix numerals (derived from docs/provenance.json)
    pp = os.path.join(docs_dir, "provenance.json")
    if os.path.exists(pp):
        try:
            pv = json.load(open(pp, encoding="utf-8"))
            for v in (pv.get("total"), pv.get("abstract"), pv.get("non_abstract")):
                if isinstance(v, int):
                    out.add(str(v))
        except (OSError, ValueError):
            pass
    # screening-reproducibility numerals (derived from docs/screen_reproducibility.json)
    sp = os.path.join(docs_dir, "screen_reproducibility.json")
    if os.path.exists(sp):
        try:
            s = json.load(open(sp, encoding="utf-8"))
            for v in (s.get("n_decided"), s.get("n_not_assessable_no_abstract_text")):
                if isinstance(v, int):
                    out.add(str(v))
            if isinstance(s.get("cohens_kappa"), (int, float)):
                out.add(str(s["cohens_kappa"]))
            for key in ("raw_agreement", "sensitivity_blind_vs_ours"):
                v = s.get(key)
                if isinstance(v, (int, float)):
                    out.add(str(round(v * 100, 1)))
        except (OSError, ValueError):
            pass
    return out


def _validate_prose_numbers(docs_dir: str, banners_html: str) -> None:
    """Raise if a RISKY numeral in the static prose banners is neither object-derived nor whitelisted static.
    Risky = a decimal (effect size), an 'N of M' aggregate, or an integer >= 10. Bare integers < 10 are
    inherent to prose ('three pages', 'two-arm') and low drift-risk, so they are allowed."""
    text = re.sub(r"<[^>]+>", " ", banners_html)
    text = re.sub(r"\b(?:19|20)\d\d-\d\d-\d\d\b", " ", text)          # ISO measurement DATES are static provenance
    text = re.sub(r"\b(?:19|20)\d\d\b", " ", text)                   # publication YEARS are inherently static
    allowed = set(_STATIC_PROSE_NUMERALS) | _prose_derived_numerals(docs_dir)
    risky = set(re.findall(r"\d+\.\d+", text))                       # decimals (effect sizes)
    ints_text = re.sub(r"\d+\.\d+", " ", text)                       # strip decimals so their integer parts don't double-count
    risky |= {n for pair in re.findall(r"(\d+)\s+of\s+(\d+)", ints_text) for n in pair}  # N of M
    risky |= {n for n in re.findall(r"\d+", ints_text) if int(n) >= 10}   # integers >= 10
    unaccounted = sorted(n for n in risky if n not in allowed)
    if unaccounted:
        raise ValueError(
            "index prose contains numerals that are neither object-derived nor whitelisted static: "
            f"{unaccounted}. Either derive them from the object, or add them to _STATIC_PROSE_NUMERALS "
            "with a reason. (Anti-drift guard — the '95 of 95' lesson.)")


def _continuous_section(docs_dir: str) -> str:
    """The continuous-tier banner. Semaglutide's LIVE result (k, MD, CI) is DERIVED from its committed
    review.json so it cannot drift if the pool is rebuilt; the pre-guard 'k=4' is a fixed narrative of
    what the timepoint guard removed (static), and Week-44/Week-68 describe fixed trial designs."""
    k = md = lo = hi = None
    p = os.path.join(docs_dir, "reviews", "semaglutide-obesity-weight", "review.json")
    if os.path.exists(p):
        try:
            rev = json.load(open(p, encoding="utf-8"))
            res = next((o["result"] for o in rev.get("outcomes", []) if o.get("primary")), {})
            k, md, lo, hi = res.get("k"), res.get("estimate"), res.get("ci_low"), res.get("ci_high")
        except (OSError, ValueError, KeyError):
            pass
    if k is None or md is None:
        sema = "a single Week-68 pool after a timepoint-consistency guard removed off-timepoint trials"
    else:
        sema = (f"it went from <strong>k=4, a tight and statistically significant pool</strong>, to "
                f"<strong>k={k}, MD &minus;{abs(round(md,2))}% (95% CI &minus;{abs(round(lo,2))} to "
                f"{round(hi,2)})</strong> &mdash; an interval that now crosses zero &mdash; because a "
                "timepoint-consistency guard refused to pool two Week-44 trials into a pre-registered "
                "Week-68 outcome")
    return (
        "<div class='banner'><h2>The same result from a second angle: the continuous tier is three pages, "
        "and here is why it is three</h2>"
        "<p>The continuous-primary tier (mean-difference outcomes: melatonin sleep-onset latency, esketamine "
        "MADRS, semaglutide weight) is <strong>bar-limited, not effort-limited</strong>. Growing it was "
        "attempted and <strong>five candidate topics were probed against their own posted ClinicalTrials.gov "
        "results and five were declined, each with a named reason</strong>: regulatory efficacy endpoints "
        "(FEV1, blood pressure, HbA1c) are posted as <strong>least-squares means with standard errors</strong> "
        "(ANCOVA), which we refuse rather than silently convert (roflumilast, tiotropium, renal-denervation); "
        "and symptom scales vary in <strong>instrument, timepoint and design</strong> across trials, so no "
        "same-scope pool of &ge;2 forms (pregabalin pain; liraglutide obesity is multi-arm / different "
        "timepoints). A topic builds cleanly here only when one registered outcome with raw per-arm mean&plusmn;SD "
        "is reported at one common timepoint across same-scope two-arm trials &mdash; a rare alignment. "
        f"<strong>Semaglutide is the clearest single illustration of the standard:</strong> {sema}. "
        "<strong>We gave up significance to keep the timepoints consistent.</strong> No comparator reports "
        "having made that trade. Together with the paragraph above this makes one claim: <strong>where we pool "
        "less, it is because of a stated bar &mdash; and the bar is shown, not asserted.</strong></p></div>")


def build_index(docs_dir: str) -> str:
    rows = []
    for mpath in sorted(glob.glob(os.path.join(docs_dir, "reviews", "*", "manifest.json"))):
        with open(mpath, encoding="utf-8") as f:
            m = json.load(f)
        slug = m.get("slug") or os.path.basename(os.path.dirname(mpath))
        comp = m.get("comparator") or {}
        ov = comp.get("overlap") or {}
        ident = comp.get("pmid") and f"PMID {comp['pmid']}" or (comp.get("doi") and f"DOI {comp['doi']}") or "—"
        rows.append((slug, m, comp, ov, ident))

    if rows:
        body = "<table><tr><th>Review</th><th>Method</th><th>Comparator</th>"\
               "<th>Overlap (ours / theirs / shared)</th></tr>"
        for slug, m, comp, ov, ident in rows:
            body += (
                f"<tr><td><a href='reviews/{_E(slug)}/index.html'>{_E(m.get('title') or slug)}</a></td>"
                f"<td>{_E(m.get('served_method'))}</td>"
                f"<td>{_E(comp.get('name'))} ({_E(ident)})</td>"
                f"<td>{_E(ov.get('ours_k'))} / {_E(ov.get('theirs_k'))} / {_E(ov.get('shared_k'))}</td></tr>"
            )
        body += "</table>"
    else:
        body = ("<div class='empty'>No harness-produced pages have passed the gate yet. "
                "This index is generated, never hand-maintained.</div>")

    # SELECTION EFFECT (item 9): the preregistered topic set vs what actually built. Stated on the
    # index so a reader is not misled by a build success rate that flatters us — the topics that
    # declined were disproportionately the hard cases.
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    n_prereg = len(glob.glob(os.path.join(_root, "topics", "*.json")))
    n_built = len(rows)
    if n_prereg:
        body = (f"<div class='banner'><h2>Selection effect (stated, not hidden)</h2>"
                f"<p>Of <strong>{n_built} of {n_prereg}</strong> preregistered topics, the built pages are "
                "shown below. The unbuilt topics were disproportionately the HARD cases — continuous or "
                "recurrent-event outcomes, composite-only endpoints, percentage-only or paywalled reports, "
                "and older or unregistered literature — which the harness correctly declined rather than "
                "extract unverifiably. So the build success rate <strong>flatters the harness</strong>: it "
                "reflects a sample selected toward clean binary-outcome registered trials, not the whole "
                "field. The topic set is preregistered and the declines are recorded (JUDGELOG), so the "
                "selection is visible rather than silent.</p></div>") + body

    _stance = ("<div class='banner'><h2>Methodological stance (measured, not asserted)</h2>"
               "<p><strong>We decline where the comparator imputed.</strong> On continuous outcomes "
               "(e.g. zinc for cold duration) the published comparator reconstructed per-arm variances "
               "from Kaplan&ndash;Meier curves and figures, or used paywalled values; of its 7 pooled "
               "trials, 0 report a verifiable per-arm SD in accessible primary text. We pool only what "
               "we can verify against source, so we decline those cells rather than impute &mdash; a "
               "genuine methodological difference, not a shortfall.</p>"
               "<p><strong>The reach picture is complete &mdash; all three routes measured.</strong> "
               "FDA/EMA and multi-registry (ISRCTN/EU-CTR/ICTRP) adapters reach newer approval-label and "
               "registered trials but cannot reach old pre-registry RCTs (DART 1989, GISSI-Prevenzione 1999, "
               "JELIS 2007, CORE/COPE 2005). <strong>Bibliographic citation chasing (Crossref) DOES reach "
               "them &mdash; 9 of 9 recovered</strong> from the comparators' own reference lists. But our "
               "preregistered screening then declines most for a stated, defensible reason: they are "
               "<strong>open-label</strong> where we require double-blind (CORE, COPE, JELIS, GISSI-P), or "
               "the population/outcome does not match. So <em>these particular</em> gaps (omega-3's "
               "pre-registry open-label trials) are screening-strictness decisions rather than search "
               "failures &mdash; the comparators' larger pools include open-label and off-outcome trials our "
               "criteria exclude. Each affected page names which recovered trials were declined and why. "
               "<strong>But this is not true of every topic: the external audits proved genuine search and "
               "extraction misses on others &mdash; see the honest split below.</strong></p></div>")
    _thesis = ("<div class='banner'><h2>The result, in two honest parts (after ten external audits)</h2>"
               "<p><strong>On reporting and reproducibility we are clearly better, and it is externally "
               "verified.</strong> Every pooled number carries a verbatim source span and the whole review "
               "regenerates from a committed protocol commit; ten independent audits found roughly two dozen "
               "defect classes in a week <em>because</em> every number is checkable &mdash; the errors were "
               "findable, which is the entire point. We correctly refused what several comparators pooled: "
               "ELIXA's four-point composite dropped into a three-point analysis, open-label trials under a "
               "double-blind protocol, per-arm variances reconstructed from figures. Every refusal is "
               "published with its reason.</p>"
               "<p><strong>On the evidence synthesis itself &mdash; finding the right trials and the right "
               "patients &mdash; the published comparators have been better on the topics audited.</strong> "
               "Our point estimates were arithmetically correct for the trials we did pool &mdash; but our "
               "own recovery work has since shown those pools were systematically too thin <em>and skewed "
               "toward larger effects</em>: every eligible trial we have recovered and source-verified moved "
               "the estimate <em>toward the null</em>, and toward the comparator (the probiotics pool moved "
               "measurably closer to the Goodman meta as we added the trials it had pooled and we had not). "
               "Being arithmetically right on a narrow, favourably-skewed evidence base is not a defensible "
               "position, and these pages no longer imply otherwise. The gap versus a comparator splits into "
               "two kinds, and we name which is which:</p>"
               "<ul><li><strong>Stated design bars (defensible).</strong> We pool fewer because we require "
               "double-blinding (omega-3 excludes open-label CORE/COPE/JELIS/GISSI-P), harmonise a single "
               "estimand, or decline figure-imputed variances (zinc); the comparator's larger pool includes "
               "trials our criteria exclude. Named on each page.</li>"
               "<li><strong>Search and extraction failures the audits proved (a real weakness, being "
               "fixed).</strong> Our enumerated (PMID-seeded) searches could not discover trials the authors "
               "did not already list &mdash; PCSK9 missed VESALIUS-CV, GLP-1 missed FLOW and SOUL, DPP-4 "
               "missed OMNeON, and the probiotics comparator (Goodman) pooled far more trials than we did; "
               "and &lsquo;declared absent&rsquo; masked outcomes that exist in full text we never retrieved "
               "(TECOS's and EXAMINE's three-point MACE). Colchicine-postop pooled non-cardiac (thoracic) "
               "trials and read a weaker effect than the cardiac-surgery metas. These are being fixed "
               "(searches rebuilt as concept queries; full-text retrieval required before any &lsquo;absent&rsquo;); "
               "the per-class fix status is tracked in the repository's AUDIT_RESPONSE.md. "
               "<strong>And the weakness is not confined to the audited topics:</strong> once a full-text "
               "fetch defect was fixed, our own recovery lane found the same under-population where no "
               "external auditor had looked &mdash; tocilizumab-COVID mortality was pooled from a single "
               "trial while the field holds roughly two dozen. Five further eligible trials are now "
               "source-verified but deliberately <em>not</em> pooled: adding that subset (small early-era "
               "trials, with the large benefit trials still missing from our corpus) would flip a real "
               "benefit to a spurious null. <strong>A recovery that changes a conclusion is not shipped until "
               "the recovered set is shown to be representative, not merely verified</strong> &mdash; the "
               "verified trials are held pending a full search rebuild, and the incompleteness is stated on "
               "that page.</li></ul>"
               "<p><strong>The adjudication design itself was losing eligible trials, and we measured it.</strong> "
               "Cold reads (a reviewer given a page with no brief, asked only &lsquo;is this a sound systematic "
               "review?&rsquo;) found that our screener treated a missing PubMed &lsquo;Randomized Controlled "
               "Trial&rsquo; publication type as <em>not an RCT</em>, when a missing tag is merely <em>unknown</em> "
               "&mdash; the abstract body should overrule incomplete metadata. Fixing it (the same four-state "
               "principle we apply to sources) recovered <strong>12 genuine pubtype-lag randomised trials across "
               "six topics</strong>. That number is a correction: a first pass flagged 25, but thirteen were "
               "reviews, comments, meta-analyses or protocols that our own guards then held back &mdash; and one of those "
               "guards, in turn, briefly excluded a real trial (RE-COVER II) until a positive control caught it. "
               "We report the corrected 12, not the raw 25, because a number with its correction visible is worth "
               "more than a bigger one. On <strong>esketamine</strong> this recovery (the Chen 2023 trial the "
               "metadata had hidden) plus a genuine continuous extractor that combines a trial&rsquo;s dose arms "
               "against its shared placebo moved the primary result from an interval wide enough to read as "
               "&lsquo;compatible with no effect&rsquo; to a modest but real benefit that matches the independent "
               "individual-patient-data meta-analysis &mdash; a conclusion change, built entirely from "
               "source-verified numbers.</p>"
               "<p><strong>Why 19 provisional GRADE ratings rose and none fell &mdash; and why that is not "
               "inflation.</strong> When the appraisal fixes landed &mdash; a per-trial risk-of-bias source "
               "hierarchy (a trial&rsquo;s own double-blind text overrules a registry Boolean that read it as "
               "unblinded), a publication-bias denominator scoped to the screened-eligible set rather than a "
               "broad drug universe, a rule that stops counting a REGISTERED SECONDARY endpoint as selective "
               "reporting, and a rounded-CI fix &mdash; 19 topics&rsquo; provisional certainty rose one level "
               "and none fell. The direction is one-way <em>by construction</em>: each of those fixes DELETES "
               "a spurious downgrade, and deleting a wrong penalty can only raise or leave a rating, never "
               "lower it &mdash; so an all-up direction is the expected signature of removing bad downgrades, "
               "not of inflating good ones. Every raised rating was checked individually against its evidence "
               "before shipping, and every GENUINE downgrade was retained: spironolactone keeps its imprecision "
               "downgrade (a wide interval), and omega-3 keeps its risk-of-bias downgrade (a trial with real "
               "between-arm differential attrition). A fix that raises our own confidence is held to a higher "
               "bar than one that lowers it, precisely so &lsquo;we fixed a bug&rsquo; can never quietly become "
               "&lsquo;our evidence is better than we said&rsquo;.</p>"
               "<p>So the honest offer is <strong>the most auditable synthesis, not the most complete one</strong> "
               "&mdash; and where our evidence base was narrower or wrong, the audits caught it precisely "
               "because every number is checkable.</p>"
               "<p><strong>The sharpest form of the argument.</strong> We attempted a per-trial, "
               "number-by-number check against the gold standard &mdash; the Cochrane review of metformin for "
               "PCOS ovulation (CD013505) &mdash; and found that <strong>0 of its 18 trials expose their "
               "per-trial counts in machine-readable form</strong>: the numbers live in forest-plot images, "
               "not the text. <strong>A reader cannot check a Cochrane review number-by-number. They can check "
               "ours</strong> &mdash; every pooled number here carries a verbatim source span, and the whole "
               "review regenerates from a committed protocol commit. (Extracting per-trial ground truth from "
               "forest-plot images is a named research-agenda item &mdash; vision/OCR or individual patient "
               "data &mdash; not yet attempted.)</p></div>")
    _cont = _continuous_section(docs_dir)
    _erate = _error_rate_section(docs_dir)
    _spec = _spec_curve_section(docs_dir)
    _screen = _screen_section(docs_dir)
    _prov = _provenance_section(docs_dir)
    _xfam = _crossfamily_section(docs_dir)
    _extval = _external_agreement_section(docs_dir)
    _defaudit = _definition_audit_section(docs_dir)
    # anti-drift: fail closed on an un-accounted numeral in ANY narrative banner
    _validate_prose_numbers(docs_dir, _thesis + _cont + _erate + _xfam + _defaudit + _extval + _spec + _screen + _prov + _stance)
    body = (_thesis + _erate + _xfam + _defaudit + _extval + _cont + _spec + _screen + _prov + _verification_section(docs_dir)
            + _currency_section(docs_dir) + _recovery_section(docs_dir)
            + _participant_flow_section(docs_dir) + _iv_iron_strands_section(docs_dir)
            + _search_recall_section(docs_dir)
            + _gate_scorecard_section(docs_dir)
            + _parity_section(docs_dir) + _error_coverage_section(docs_dir) + _stance
            + _fair_section(docs_dir) + body)

    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>Reproducible meta-analysis harness</title><style>{_CSS}</style></head><body>"
        "<header><h1>Reproducible meta-analysis harness</h1></header>"
        f"<main>{_FRONT}{body}</main></body></html>"
    )


def write_index(docs_dir: str) -> str:
    html_text = build_index(docs_dir)
    out = os.path.join(docs_dir, "index.html")
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(html_text)
    return out


if __name__ == "__main__":
    import sys
    d = sys.argv[1] if len(sys.argv) > 1 else "docs"
    print("wrote", write_index(d))
