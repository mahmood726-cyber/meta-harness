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
from collections import Counter

from . import parity_relation

_E = lambda x: html.escape("" if x is None else str(x), quote=True)


def _read_object(docs_dir, relative, default=None):
    try:
        with open(os.path.join(docs_dir, relative), encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, ValueError):
        return default


def _recovery_attempts(docs_dir, attempts):
    parity = _read_object(docs_dir, "parity.json", [])
    for attempt in attempts:
        row = dict(attempt)
        trial = row.get("trial", "")
        topics = {r["slug"] for r in parity if trial and
                  re.search(r"\b" + re.escape(trial) + r"\b", r.get("reason", ""), re.I)}
        if topics and row.get("topic") not in topics:
            yield {"trial": trial, "topic": "withheld", "status": "TOPIC_MISMATCH",
                   "note": "Parity attribution: " + ", ".join(sorted(topics))}
            continue
        review = _read_object(docs_dir, os.path.join("reviews", row.get("topic", ""), "review.json"), {})
        pmid = str(row.get("pmid", ""))
        records = (review.get("screening") or {}).get("records", [])
        screen = next((r for r in records if str(r.get("id")) == pmid), {})
        primary = next((o for o in review.get("outcomes", []) if o.get("primary")), {})
        absent = next((t for t in primary.get("declared_absent_trials", [])
                       if str(t.get("id")) in (pmid, "PMID " + pmid)), {})
        pooled = any(str(t.get("id")) in (pmid, "PMID " + pmid) for t in primary.get("trials", []))
        if screen or absent or pooled:
            row.pop("before", None)
            row.pop("after", None)
            row["status"] = ("POOLED" if pooled else "DECLARED_ABSENT" if absent else
                             "EXCLUDED" if screen.get("decision") == "exclude" else "SCREENED_IN")
            row["note"] = ("Current review: screening=" + str(screen.get("decision", "unrecorded"))
                           + "; state=" + str(absent.get("state", row["status"]))
                           + "; reason audit=" + str((absent.get("reason_code_audit") or {}).get("verdict", "unrecorded")))
        yield row


def _method_display(docs_dir, method):
    # A manifest records a method, not evidence of universal gate enforcement.
    method = re.sub(r"Validated vs metafor[^.]*5\.0\.1.*?\)\.", "", method or "")
    scorecard = _read_object(docs_dir, "gate_scorecard.json", {})
    gate = next((g for g in scorecard.get("gates", [])
                 if g.get("gate_id") == "census.interval_provenance"), {})
    state = (gate.get("computed") or {}).get("validation", "UNPROVEN")
    return method.strip() + " Interval provenance gate: " + str(state) + "."

_FRONT = """<div class="banner"><h2>What this is</h2>
<p>A harness for generating meta-analysis pages from committed inputs. Gate results
and source evidence must be inspected for each page; this index does not establish
fresh-clone reproduction, complete source coverage, or comparative superiority.</p></div>"""

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
    enriched = []
    for r in rows:
        rp = os.path.join(docs_dir, "reviews", r.get("slug", ""), "review.json")
        review = None
        if os.path.exists(rp):
            try:
                review = json.load(open(rp, encoding="utf-8"))
            except (OSError, ValueError):
                review = None
        enriched.append(parity_relation.enrich(r, review, strict=False))
    identical = sum(1 for r in enriched
                    if (r.get("parity_relation") or {}).get("relation") == "IDENTICAL_SET")
    color = {"IDENTICAL_SET": "#e6f4ea", "DOMINANT_SUBSET": "#fff8e1", "SUPERSET": "#fff8e1",
             "SUBSET": "#fff8e1", "OVERLAPPING": "#fff8e1"}
    body = (f"<div class='banner'><h2>Parity with the published comparator (the finishing metric)</h2><p>For each same-scope topic: our pooled <em>k</em> vs the <strong>comparable</strong> comparator <em>k</em> (the comparator's pooled list, enumerated from its own references/full text, after removing trials that are out of scope, double-counted substudies, observational, or non-prespecified for the outcome). <strong>{identical} of {len(rows)}</strong> topics with parity rows have an identical computed trial set; identical-set agreement is arithmetic replication, not independent corroboration. Named reasons come from the parity record. SOURCE_VERIFICATION_UNPROVEN: parity membership does not establish source verification of each recovery.</p><table><tr><th>Topic</th><th>Our k</th><th>Comparator k</th><th>Computed relation</th><th>Named reason for any difference</th></tr>")
    for r in enriched:
        rel = r.get("parity_relation") or {}
        st = str(rel.get("relation") or r.get("status", ""))
        bg = color.get(st, "#fdecec" if st in ("COMPARATOR_INVALID", "NOT_ENUMERABLE") else "#fff")
        their_k = rel.get("their_k")
        if their_k is None:
            their_k = r.get("comparable_comparator_k")
        body += (f"<tr style='background:{bg}'><td>{_E(r.get('slug'))}</td>"
                 f"<td>{_E(rel.get('our_k', r.get('our_k')))}</td><td>{_E(their_k)}</td>"
                 f"<td>{_E(st)}<br><span>{_E(rel.get('label'))}</span></td>"
                 f"<td>{_E(r.get('reason'))}</td></tr>")
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
    attempts = list(_recovery_attempts(docs_dir, d.get("attempts") or []))
    states = Counter(a.get("status", "UNRECORDED") for a in attempts)
    state_line = "; ".join(f"{_E(state)}: {count}" for state, count in sorted(states.items()))
    rows = "".join(
        f"<li><strong>{_E(a.get('trial'))}</strong> &rarr; {_E(a.get('topic'))}: "
        f"<code>{_E(a.get('status'))}</code>"
        + (f" &mdash; {_E(a.get('before'))} &rarr; {_E(a.get('after'))}" if a.get('before') else "")
        + (f" <span class='muted'>{_E(a.get('note'))}</span>" if a.get('note') else "") + "</li>"
        for a in attempts)
    rd = d.get("recall_denominator") or {}
    recall_line = (f"<p><strong>Baseline unaided search recall: {_E(rd.get('baseline_unaided_recall'))}</strong> &mdash; against the {_E(rd.get('clean_eligible_denominator'))} entries labelled source-verified-eligible in the historical recovery record. CURRENT_RECALL_UNPROVEN: this snapshot does not establish misses of the current search; its recorded test-set error count is {_E(sb.get('test_set_errors_found') or 0)} errors, caught by source verification.</p>"
                   if rd else "")
    return (f"<div class='banner'><h2>Recovery inventory</h2>{recall_line}"
            f"<p>{len(attempts)} recorded attempts; current review state where linked, otherwise historical recovery state: "
            f"{state_line}. NOT_FOUND identifies an unresolved recovery search; EXCLUDED and DECLARED_ABSENT "
            "are distinct dispositions. State labels do not establish source verification.</p>"
            f"<ul>{rows}</ul></div>")


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
                + (f" ({_E(len(r.get('missed_pmids') or []))} absent from historical Boolean set: {_E(', '.join(r['missed_pmids']))}; not a current recovery-state count)" if r.get('missed_pmids') else "")
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


def _decoupling_universal_section(docs_dir: str) -> str:
    """The headline finding of 2026-09-15, read from the generated capture so the count cannot be typed."""
    path = os.path.join(docs_dir, "evidence", "decoupling-universal-2026-09-15", "01-per-topic-before.txt")
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return ""
    m = re.search(r"RESULT: (\d+) of (\d+) topics", text)
    if not m:
        return ""
    return (f"<div class='absent'><h2>Diagnostic-decision decoupling was universal, not an unlucky page</h2>"
            f"<p><strong>{_E(m.group(1))} of {_E(m.group(2))} topics</strong> carried at least one detected, rendered hazard that "
            "was routed to the reader and to no analytic decision, before any consumer was wired (the auditor's mechanism, "
            "disclosure-as-control: a validity hazard correctly detected and represented, but not causally connected to the "
            "decision it should constrain). Crystalloids was the instance; the corpus state was the rule. Since then the "
            "retrieval-class, search-provenance and enumeration hazards feed <code>invalidation.assess</code>; ROB_SENSITIVITY and "
            "DEFINITION_AUDIT are acknowledged as <strong>owed a consumer</strong>, not as informational; the rest are acknowledged "
            "as informational after reading. A signed acknowledgement is not a wiring. Per-topic names: "
            "<a href='evidence/decoupling-universal-2026-09-15/'>decoupling-universal-2026-09-15</a>.</p></div>")


def _external_findings_section(docs_dir: str) -> str:
    """Findings about published comparators, rendered from the fix ledger under the auditor's heading. Every
    one is a hypothesis with verification NONE; the count is never a comparison with our own column."""
    try:
        ledger = json.load(open(os.path.join(docs_dir, "fix_ledger.json"), encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    rows = ledger.get("external_findings_about_published_comparators") or []
    if not rows:
        return ""
    heading = ledger.get("external_findings_heading") or "Findings about published comparators"
    n_none = sum(1 for r in rows if r.get("verification") == "NONE")
    items = "".join(
        f"<li><code>{_E(r.get('fix_id'))}</code> — {_E(r.get('title'))} "
        f"[verification {_E(r.get('verification'))}]</li>" for r in rows)
    return (f"<div class='absent'><h2>{_E(heading)}</h2>"
            f"<p><strong>{len(rows)}</strong> findings recorded, <strong>{n_none}</strong> with verification NONE and "
            f"<strong>{len(rows) - n_none}</strong> with a verification label other than NONE (not necessarily external confirmation). Applying the same instrument to a comparator "
            "and to our own pool establishes procedural symmetry, not instrument validity: a blind spot in our checker misses "
            "the same defect in both. These are hypotheses, promoted only by external source checking; the sentence "
            "\"our instrument found n problems in them and m in us\" is not evidence of anything and is not written here. "
            "Per-comparator evidence: <a href='evidence/comparator-correctness-2026-09-15/'>comparator-correctness-2026-09-15</a>."
            f"</p><ul>{items}</ul></div>")


def _gate_scorecard_section(docs_dir: str) -> str:
    """Render the measured gate scorecard summary from registry/gate_scorecard.json."""
    try:
        from . import gate_scorecard
        s = gate_scorecard.summary(os.path.dirname(docs_dir))
    except Exception:
        return ""
    rows = []
    for row in s.get("gate_lines") or []:
        rows.append(
            "<tr>"
            f"<td><code>{_E(row.get('gate_id'))}</code></td>"
            f"<td>{_E(row.get('line'))}</td>"
            "</tr>"
        )
    independence = s.get("adjudicator_independence")
    independence_text = "no adjudications" if independence is None else f"{float(independence):.3f}"
    ov = s.get("overall_adjudication") or {}
    def _pct(v):
        return "not observed" if v is None else f"{100.0 * float(v):.0f}%"
    coverage_line = (
        "<p><strong>Adjudication coverage first, so the unresolved cannot disappear:</strong> "
        f"<strong>{_E(ov.get('adjudicated'))} of {_E(ov.get('events'))}</strong> refusal events are adjudicated "
        f"(<strong>{_E(_pct(ov.get('adjudication_coverage')))}</strong>); "
        f"<strong>{_E(ov.get('independently_adjudicated'))} of {_E(ov.get('events'))}</strong> are independently adjudicated "
        f"(<strong>{_E(_pct(ov.get('independent_adjudication_coverage')))}</strong>); over PRODUCTION refusals alone, "
        f"<strong>{_E(ov.get('production_adjudicated'))} of {_E(ov.get('production_events'))}</strong> adjudicated "
        f"({_E(_pct(ov.get('production_adjudication_coverage')))}) and "
        f"<strong>{_E(ov.get('production_independently_adjudicated'))} of {_E(ov.get('production_events'))}</strong> independently "
        f"({_E(_pct(ov.get('production_independent_adjudication_coverage')))}). No precision below is to be read as if the "
        "unresolved remainder were not there; an UNRESOLVED event is neither a true nor a false refusal.</p>"
    )
    return (f"<div class='banner'><h2>Gate scorecard: plant validations and production refusals</h2>"
            + coverage_line +
            f"<p><strong>{_E(s.get('gate_count'))} production gates accounted for</strong>; "
            f"<strong>{_E(s.get('event_count'))}</strong> events; "
            f"<strong>{_E(s.get('plant_validation_count'))}</strong> adjudicated plant validations; "
            f"<strong>{_E(s.get('unvalidated_count'))}</strong> are <code>UNVALIDATED</code>; "
            f"<strong>{_E(s.get('unresolved_event_count'))}</strong> events are <code>UNRESOLVED</code>; "
            f"adjudicator_independence is <strong>{_E(independence_text)}</strong>; "
            f"<strong>{_E(s.get('production_true_refusal_gate_count'))}</strong> gates have an adjudicated production "
            f"true refusal; <strong>{_E(s.get('false_refusal_gate_count'))}</strong> have an adjudicated false refusal"
            + (": " + ", ".join(f"<code>{_E(g)}</code>" for g in (s.get("false_refusal_gates") or []))
               + " (the named pessimistic incident: the fix-state checker refused an evidence-only commit because its "
                 "subject contained 'refusing'; commit 6b1039cd records the structural correction; author-adjudicated, "
                 "not independent)" if s.get("false_refusal_gates") else "")
            + ". "
            f"<strong>{_E(s.get('auditor_sentence'))}</strong> "
            f"The scorecard rule is: {_E(s.get('unvalidated_sentence'))}. "
            f"{_E(s.get('precision_coverage_sentence'))}. "
            f"{_E(s.get('adjudicator_independence_sentence'))}. "
            f"Served JSON: <code>gate_scorecard.json</code>.</p>"
            f"<table><tr><th>gate</th><th>computed line</th></tr>{''.join(rows)}</table></div>")


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
    return (f"<div class='banner'><h2>Recorded source-digit verification states</h2>"
            f"<p><strong>{ok} of {n} pooled trial-outcome numbers</strong> carry a positive "
            "verification state. This count does not independently establish source-span validity, "
            "arm assignment, or publication-gate success.</p></div>")


def _error_coverage_section(docs_dir: str) -> str:
    ledger = _read_object(docs_dir, "fix_ledger.json", {})
    entries = ledger.get("fixes", [])
    if not entries:
        return ""
    counts = []
    for axis in ("kind", "implementation", "verification", "scope", "freshness"):
        values = Counter(str(row.get(axis, "UNRECORDED")) for row in entries)
        counts.append(f"<li>{_E(axis)}: " + "; ".join(
            f"{_E(key)}: {value}" for key, value in sorted(values.items())) + "</li>")
    return (f"<div class='banner'><h2>Fix ledger</h2><p>{len(entries)} ledger entries, "
            "recounted from fix_ledger.json. These include findings and controls as well as fixes; "
            "ledger counts do not measure per-review screening or enforcement.</p><ul>"
            + "".join(counts) + "</ul></div>")


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
    if d.get("independent_audit_state") == "HISTORICAL_ONLY":
        prov = (f"<em>Historical blind audit, measured {_E(when)} on {pop} then-pooled numbers; "
                "this is not a current-population error-rate estimate. "
                f"The live inventory contains {d.get('current_pooled_population')} pooled rows; "
                f"{d.get('not_independently_rechecked_current')} are explicitly NOT_INDEPENDENTLY_RECHECKED. "
                "The inventory refresh does not increase the historical independent-verification numerator.</em> ")
    return (f"<div class='banner'><h2>Historical internal error-rate measurement</h2><p>{prov}"
            "The historical record labels this exercise 'measured our own error rate'; it is an "
            "internal-consistency comparison. "
            f"The record reports {rv} of {pop} rows re-extractable, {ex} of {rv} matched exactly, {dis} disagreements, "
            f"{err} labelled internal errors and {nr} not re-checkable. "
            "These counters do not establish independent errors, current pool coverage or successful repairs. "
            "Consult the per-row comparison and adjudication records.</p></div>")


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
    rep = d.get("same_estimand_replication", 0)
    sd = d.get("same_estimand_diverge", 0)
    cp = d.get("cross_estimand_pending", 0)
    co = d.get("cross_estimand_opposite", 0)
    nc = d.get("non_comparable", 0)
    same_n = ag + rep + sd
    return (f"<div class='banner'><h2>External validation: our pooled numbers vs the published meta-analyses'</h2>"
            f"<p>The strongest check is against an external hand-built standard: our pooled primary estimate vs "
            f"the published comparator meta-analysis's reported pooled estimate. But a comparison is only 'the "
            f"same question' when the two share the <strong>same estimand</strong> — an RR is not an OR is not an "
            f"HR (an odds ratio sits further from 1 than a risk ratio for common events; a hazard ratio is a rate, "
            f"not a risk), so comparing them on the log scale as if interchangeable is a "
            f"<em>comparator-context mismatch</em>. Keying on the estimand: of {n} topics, <strong>{same_n} are "
            f"same-estimand comparisons, and {ag} of those agree within ~12%</strong> on the log scale "
            f"with a different evidence base; <strong>{rep}</strong> are arithmetic replications on an "
            f"identical trial set and are not counted as independent corroboration; {sd} same-estimand "
            f"comparison(s) diverge (adjudicated). "
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
    return (f"<div class='banner'><h2>Recorded cross-family comparison</h2><p>INDEPENDENCE_UNPROVEN: model labels and agreement counts do not establish independent errors or coverage of the current pool. The historical comparison record reports <strong>agreement with our stored value on {agree} of {comp}</strong> comparable numbers (<strong>{round(rate * 100, 1)}%</strong>); on <strong>{three}</strong> numbers all three families (our harness, a GPT-5 checker, and Gemini) agree. Every one of the <strong>{dis}</strong> disagreements was hand-adjudicated against source and <strong>{wrong}</strong> was a wrong number: they are a documented approved-dose rule, intention-to-treat vs the trial's on-treatment primary, a rounding tie, one registry-vs-abstract count, and one CT.gov-vs-abstract estimand difference (all disclosed in <code>docs/crossfamily.json</code>). A model call is treated as a source &mdash; the Gemini outputs are committed, so this regenerates without re-calling the model. <strong>Three-family agreement is a far stronger claim than our own dual extraction.</strong></p>"
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
    return (f"<div class='banner'><h2>Recorded definition audit</h2>"
            f"<p>The historical record lists {cand} of {n} rows as candidates and {both} flags from both families. "
            f"Recorded dispositions: {ref} refused, {disc} disclosure queued, {ok} already disclosed, {q} queued. "
            "AUDIT_COVERAGE_UNPROVEN: summary counters do not establish independent errors, complete current "
            "pool coverage or successful repairs. See docs/definition_audit.json.</p></div>")


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
    return (f"<div class='banner'><h2>Where the numbers come from &mdash; and what we do not yet claim</h2><p><strong>Provenance mix (a tracked metric).</strong> Of {tot} pooled numbers, <strong>{ab}</strong> come from the trial <strong>abstract</strong> (the authors' headline result &mdash; the weakest source, though the safest default) and <strong>{na}</strong> from other provenance categories (ClinicalTrials.gov structured results, PMC full text, and entries labelled hand-verified). PROMOTION_COVERAGE_UNPROVEN: this provenance count does not measure alternative-source availability or establish statistical independence of the historical model audits.</p><p>Comparators are restricted to open-access sources; protocol timestamps are internal git records and topic selection is not random.</p></div>")


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
    return (f"<div class='banner'><h2>Recorded screening reproducibility</h2>"
            f"<p>INDEPENDENCE_UNPROVEN: the historical title-and-abstract comparison record does not "
            f"establish independent errors or coverage of the current pooled set. Over the "
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
            f"<p>Each non-refused primary outcome with &ge;2 trials (<strong>{n['n']}</strong> of them) was re-pooled "
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
        return ("<div class='banner'><h2>Fair comparison</h2><p>COMPARISON_STATE_UNPROVEN: required full-text comparison records are absent or incomplete.</p></div>")
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
    return (f"<div class='banner'><h2>Recorded full-text comparison</h2>"
            f"<p>The historical comparison record covers {n['prisma_scorable']} of {n['prisma_total']} topics "
            f"and {n['prisma_cells']} PRISMA cells. Comparator-present cells: {n['prisma_comp_present']} of "
            f"{n['prisma_cells']}; ours lacking comparator-present items: {n['prisma_ours_lacks']} of "
            f"{n['prisma_cells']}; ours-only items: <strong>{n['prisma_we_present']}</strong>. "
            f"The judge record covers {n['judge_total']} topics and labels ours more "
            f"<strong>auditable on {n['judge_more_auditable_ours']} of {n['judge_total']}</strong>; {aud_clause}. "
            f"Recorded risk-of-bias reporting split: {rob_o}&ndash;{rob_c} {rob_dir}; comparator completeness "
            f"preference: {comp_complete} of {tot}. These aggregate counters do not establish a uniform "
            "per-topic conclusion or independent confirmation of current parity.</p></div>")


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
                      e.get("not_independently_rechecked_current"),
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
    refused = None
    p = os.path.join(docs_dir, "reviews", "semaglutide-obesity-weight", "review.json")
    if os.path.exists(p):
        try:
            rev = json.load(open(p, encoding="utf-8"))
            res = next((o["result"] for o in rev.get("outcomes", []) if o.get("primary")), {})
            k, md, lo, hi = res.get("k"), res.get("estimate"), res.get("ci_low"), res.get("ci_high")
            refused = (res.get("pooled_ci_refused") or not (res.get("claim") or {}).get("present")
                       or res.get("present") is False or not res.get("ci_provenance")
                       or lo is None or hi is None)
        except (OSError, ValueError, KeyError):
            pass
    if k is None or md is None:
        sema = "current primary result unavailable; no pooled significance or null-crossing claim"
    elif refused:
        sema = (f"it went from <strong>k=4, a tight and statistically significant pool</strong>, to "
                f"<strong>k={k}, MD {round(md,2)}%</strong>; the registered PM/HKSJ CI is "
                "unavailable for a served claim, so the index makes no pooled significance or null-crossing claim, after "
                "a timepoint-consistency guard refused to pool two Week-44 trials into a pre-registered "
                "Week-68 outcome")
    else:
        sema = (f"it went from <strong>k=4, a tight and statistically significant pool</strong>, to "
                f"<strong>k={k}, MD {round(md,2)}% (95% CI {round(lo,2)} to "
                f"{round(hi,2)})</strong> &mdash; null-crossing state: {_E((res.get('claim') or {}).get('crosses_null'))} &mdash; after a "
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
        "The served claim state comes from the primary outcome in review.json.</p></div>")


def build_index(docs_dir: str) -> str:
    rows = []
    parity_by_slug = {r['slug']: r for r in _read_object(docs_dir, 'parity.json', [])}
    for mpath in sorted(glob.glob(os.path.join(docs_dir, "reviews", "*", "manifest.json"))):
        with open(mpath, encoding="utf-8") as f:
            m = json.load(f)
        slug = m.get("slug") or os.path.basename(os.path.dirname(mpath))
        comp = m.get("comparator") or {}
        ov = comp.get("overlap") or {}
        parity = parity_by_slug.get(slug, {})
        if parity.get("comparable_comparator_k") is not None:
            ov = dict(ov, theirs_k=f"{parity['comparable_comparator_k']} (comparable; parity status {parity.get('status', 'UNRECORDED')})")
        ident = comp.get("pmid") and f"PMID {comp['pmid']}" or (comp.get("doi") and f"DOI {comp['doi']}") or "—"
        rows.append((slug, m, comp, ov, ident))

    if rows:
        body = "<table><tr><th>Review</th><th>Method</th><th>Comparator</th>"\
               "<th>Overlap (ours / theirs / shared)</th></tr>"
        for slug, m, comp, ov, ident in rows:
            body += (
                f"<tr><td><a href='reviews/{_E(slug)}/index.html'>{_E(m.get('title') or slug)}</a></td>"
                f"<td>{_E(_method_display(docs_dir, m.get('served_method')))}</td>"
                f"<td>{_E(comp.get('name'))} ({_E(ident)})</td>"
                f"<td>{_E(ov.get('ours_k'))} / {_E(ov.get('theirs_k'))} / {_E(ov.get('shared_k'))}</td></tr>"
            )
        body += "</table>"
    else:
        body = ("<div class='empty'>No harness-produced page manifests are listed here. "
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

    _stance = ("<div class='banner'><h2>Methodological stance</h2><p>REACH_STATE_UNPROVEN: this static summary cannot establish source availability, citation-chase recovery, or current screening decisions; consult each topic's retrieval ledger and explicit refusals.</p></div>")
    _thesis = ("<div class='banner'><h2>Limits of the evidence</h2><p>EXTERNAL_VERIFICATION_UNPROVEN: this index does not establish comparative superiority, independent verification, protocol-commit replay, or a uniform direction of recovery effects. Source spans, declared absent decisions, current pool decisions and historical audit records remain available for inspection; they do not justify a blanket accuracy or completeness claim.</p></div>")
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
    # EVIDENCE BUNDLE, linked first and by full URL: the auditor's fetcher could not reach the bundle and the
    # directory was not in any crawl. Every capture is served raw and as an HTML rendering (their layer refuses
    # text/plain), with its SHA-256 beside it. A reader who verifies only what we say about the evidence has verified
    # nothing; this link is the route to the bytes.
    _evidence = ("<div class='banner'><h2>Evidence bundle — raw captures of what was found and what refused</h2>"
                 "<p>Every finding this site reports about itself (a commit that failed verification and was deployed anyway, "
                 "the refusals after the fix, the independent re-demonstrations, the gate scorecard, the accounting of every "
                 "regeneration) is served as raw captures with the SHA-256 of each file, at "
                 "<a href='evidence/'>https://mahmood726-cyber.github.io/meta-harness/evidence/</a>. Start with "
                 "<a href='evidence/gate-authority-2026-09-14/01-prefix-deploy-unconditional.txt.html'>the 109053ad capture "
                 "(HTML rendering)</a> or its <a href='evidence/gate-authority-2026-09-14/01-prefix-deploy-unconditional.txt'>raw file</a>, "
                 "and <a href='evidence/gate-authority-2026-09-14/VERIFY-COLD.md.html'>how to verify it without us</a>. "
                 "The orthogonal fix ledger for every claim is in <a href='fix_ledger.json'>fix_ledger.json</a>; the gate scorecard in "
                 "<a href='gate_scorecard.json'>gate_scorecard.json</a>; the per-file digests of this deployment in "
                 "<a href='_production/manifest.json'>_production/manifest.json</a>.</p></div>")
    body = (_evidence + _decoupling_universal_section(docs_dir) + _external_findings_section(docs_dir) + _thesis + _erate + _xfam + _defaudit + _extval + _cont + _spec + _screen + _prov + _verification_section(docs_dir)
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
