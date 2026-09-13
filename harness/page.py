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
import html
import json
import re
from typing import Any

from . import manuscript as _manuscript_mod

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


def _absent_label(reason) -> str:
    """External audit (C-EXTRACT-1): do NOT say "absent" when only the abstract was checked — the
    outcome may exist in the full text. Classify the per-trial reason: a genuine exclusion (wrong
    population/composite/estimand) stays "excluded"; an abstract-only miss is labelled "not extracted
    (abstract only; full text not retrieved)" so it is not read as evidence the outcome does not exist."""
    rl = (reason or "").lower()
    if any(w in rl for w in ("exclud", "wrong ", "estimand", "non-cardiac", "population", "per-protocol",
                             "per protocol", "completers", "different composite", "first-attack")):
        return "excluded (see reason)"
    if "abstract" in rl:
        return "not extracted — abstract only, full text not retrieved"
    return "not extracted (see reason)"


def _kv(rows) -> str:
    trs = "".join(f"<tr><th>{_e(k)}</th><td>{v if isinstance(v,str) and v.startswith('<') else _e(v)}</td></tr>" for k, v in rows)
    return f"<table class='kv'>{trs}</table>"


def _ci(res) -> str:
    return f"{_num(res.get('estimate'))} ({res.get('scale')}), 95% CI {_num(res.get('ci_low'))}–{_num(res.get('ci_high'))}"


def _effect_label(res) -> str:
    # A single-trial result is not a pooled effect; label it honestly so the k=1 CI is not
    # read as a random-effects pooled interval.
    return "Single-trial effect" if res.get("k") == 1 else "Pooled effect"


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


def _overview(r, neutral):
    parts = [f"<h2>{_e(r.get('title'))}</h2>", f"<p class='q'>{_e(r.get('question'))}</p>"]
    # INVALIDATION PROPAGATION: a single STALE verdict poisons the headline. If any dependent output
    # is known incomplete/superseded/unproven, say so at the top rather than let the result read as
    # current. Each reason is named; the corpus index publishes the count as it falls.
    inv = r.get("invalidation") or {}
    if inv.get("stale"):
        _rz = "".join(f"<li>{_e(x.get('detail'))}</li>" for x in inv.get("reasons", []))
        parts.append(
            "<div class='absent'><strong>STALE — this topic's result is not current.</strong> "
            "One or more dependent outputs on this page are known to be incomplete, superseded, or "
            f"unproven, so the result must not be read as a settled current estimate:<ul>{_rz}</ul></div>")
    if not neutral:
        parts.append(
            "<div class='banner'>This page offers <strong>greater auditability, not "
            "stronger evidence</strong>: every number traces to a committed source, every "
            "absence is declared, and any hand-edit breaks the reproduction census.</div>")
    prim = _primary(r)
    if prim and _absent(prim) is None:
        res = prim.get("result") or {}
        if res.get("suppressed_incompatible"):
            # FAIL CLOSED (audit 23): the overview summary must not present a suppressed-incompatible primary
            # as pooled — no "Trials pooled (k)", no "Pooled effect" row (even with the number popped, the
            # framing implies a pool). Show the suppression, defer per-trial estimates to Results.
            parts.append("<h3>Primary outcome</h3>")
            parts.append(
                "<div class='absent'><strong>Pooled result SUPPRESSED (estimand-incompatible).</strong> "
                f"{_e(res.get('suppressed_reason'))} <em>Estimand classes: "
                f"{_e(' + '.join((res.get('estmeasure') or {}).get('canonicals', [])))}; the "
                f"{_e(res.get('k'))} eligible trials are shown individually in Results, not pooled.</em></div>")
        elif _absent(res) is None:
            parts.append("<h3>Primary outcome</h3>")
            pooled = _pooled_ids(prim)
            k = res.get("k")
            kdisp = f"{k} — {'; '.join(pooled)}" if pooled else k
            n_inc = _n_included(r)
            n_absent = len(prim.get("declared_absent_trials") or [])
            recon = None
            if n_inc is not None and k is not None and isinstance(k, int):
                if n_inc != k:
                    recon = (f"{n_inc} trials met P/I/C/design (screening); {k} reported this "
                             f"outcome with an extractable number and were pooled; the remaining "
                             f"{n_inc - k} are listed as declared-absent in Results (they were "
                             f"included but reported no poolable value for this outcome).")
                else:
                    recon = (f"all {n_inc} screened-in trials reported this outcome and were "
                             f"pooled (screening count = k).")
            rows = [
                ("Outcome", prim.get("name")),
                ("Estimand", res.get("scale") or prim.get("estimand")),
                ("Trials pooled (k)", kdisp),
            ]
            if recon:
                rows.append(("Screened-in → pooled", recon))
            rows.append((_effect_label(res), _ci(res)))
            if res.get("ci_low_fixed") is not None:
                rows.append(("Common-effect CI (k=2 sensitivity)",
                             f"{_num(res.get('estimate_fixed'))} ({res.get('scale')}), 95% CI "
                             f"{_num(res.get('ci_low_fixed'))}–{_num(res.get('ci_high_fixed'))}"))
            if res.get("pi_low") is not None:
                rows.append(("Prediction interval", f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}"))
            if res.get("tau2") is not None:
                rows.append(("Between-study τ²", _tau(res.get("tau2"))))
            rows.append(("Method", prim.get("method") or r.get("method_declared")))
            parts.append(_kv(rows))
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
            "<li><strong>Risk of bias is partial.</strong> RoB2 domains are computed from machine-"
            "available registry fields; domains needing human reading are marked not-assessed.</li>"
            "<li><strong>Registry snapshot is dated.</strong> AACT is a fixed local snapshot; trials "
            "registered, or results posted, after it are invisible to the registry-first recall, ghost "
            "and RoB2 signals (the snapshot date is shown on those blocks). The re-search mode on the "
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
            ("Eligibility (P/I/C/design)", p.get("eligibility"))]
    body = _kv([(k, v) for k, v in rows if v])
    # The raw protocol text names the comparator and the machinery; omit it in the
    # blinding-safe render so the judge cannot identify which page is the harness's.
    if p.get("text") and not neutral:
        body += f"<pre class='proto'>{_e(p.get('text'))}</pre>"
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
    ss = s.get("source_status") or {}
    if ss:
        # Four-state per source: which adapters ran, returned nothing, errored, or were not attempted
        # for this topic — so process coverage is visible, not assumed.
        # sorted() so the render order is independent of dict key order (canonical_json sorts keys;
        # an insertion-order iteration would render differently pre/post-canonicalisation — the
        # deterministic-render census check catches exactly that, as it did for RoB2).
        cells = " · ".join(f"{_e(k)}: <strong>{_e(v)}</strong>" for k, v in sorted(ss.items()))
        body += ("<h4>Source status (which adapters ran)</h4><p class='muted'>" + cells +
                 " — RAN_OK = ran and returned records; RAN_ZERO = ran, none matched; RAN_ERROR = "
                 "attempted but failed; NOT_RUN = not attempted for this topic.</p>")
        # RETRACTION (round-2 P0): the search narrative must be DERIVED from source_status + the committed
        # provenance classification, never authored. A fetch of named identifiers is not a search; a
        # RAN_ERROR/NOT_RUN registry adapter did not run. We do NOT claim a registry-first/systematic search
        # where the evidence is proven-or-unclassified provenance.
        _aact = ss.get("Registry-first (AACT)")
        _slug = r.get("slug") or r.get("topic") or ""
        _prov = None
        try:
            import json as _j
            import os as _o
            _pj = _o.path.join(_o.path.dirname(_o.path.dirname(_o.path.abspath(__file__))), "docs", "search_provenance.json")
            _pd = _j.load(open(_pj, encoding="utf-8"))
            for _cls, _v in (_pd.get("classes") or {}).items():
                if _slug in (_v.get("topics") or []):
                    _prov = _cls
        except Exception:
            _prov = None
        if _aact in ("RAN_ERROR", "NOT_RUN") or _prov in ("RAN_ERROR_rendered_as_run", "PMID_ENUMERATION_explicit"):
            body += ("<div class='absent'><strong>Search provenance — not a completed systematic search.</strong> "
                     f"The registry-first (AACT) adapter status for this topic is <strong>{_e(_aact)}</strong>"
                     + ("; its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications "
                        "(UID/PMID-anchored queries for pre-identified trials), which cannot discover an "
                        "unknown eligible trial. A fetch of named identifiers is not a systematic search."
                        if _prov == "PMID_ENUMERATION_explicit" or _aact in ("RAN_ERROR", "NOT_RUN") else ".")
                     + " We retract any claim of a registry-first or systematic search for this topic.</div>")
        elif _prov is None or _prov == "needs_verbatim_query_check":
            body += ("<p class='muted'><em>Search provenance: UNCLASSIFIED — the verbatim query set for this "
                     "topic has not been verified as a concept search vs known-item retrieval; no systematic-"
                     "search claim is made pending that check.</em></p>")
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
                 "mean the search is complete — external audits found eligible trials (J-EMPHASIS-HF for "
                 "spironolactone, PHILO for ticagrelor) entirely absent precisely because they were never in "
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
    head = ("<tr><th>Record</th><th>Type</th><th>Decision</th><th>Rule</th>"
            "<th>Reason (true of the record)</th><th>Verbatim span (from the record)</th></tr>")
    rows = "".join(
        f"<tr><td>{_e(x.get('id'))}</td><td>{_e(x.get('id_type'))}</td>"
        f"<td class='dec-{_e(x.get('decision'))}'>{_e(x.get('decision'))}</td>"
        f"<td>{_e(x.get('rule_id'))}</td><td>{_e(x.get('reason'))}</td>"
        f"<td class='span'>{_e(x.get('span'))}</td></tr>"
        for x in recs)
    n_inc = sum(1 for x in recs if x.get("decision") == "include")
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
            integ_html = msg
    # PRISMA 2020 flow (items 16a/16b): counts at every stage, exclusions broken down by rule.
    from collections import Counter as _C
    rule_counts = _C(x.get("rule_id") for x in recs if x.get("decision") == "exclude")
    prim = next((o for o in (r.get("outcomes") or []) if o.get("primary")), None)
    pooled_k = ((prim or {}).get("result") or {}).get("k") if prim else None
    n_identified = ((r.get("search") or {}).get("n_records")) or len(recs)
    excl_bits = " · ".join(f"{rid} {n}" for rid, n in sorted(rule_counts.items()))
    flow = ("<h4>Study selection flow (PRISMA 2020)</h4>"
            "<table class='recs'><tr><th>Stage</th><th>n</th></tr>"
            f"<tr><td>Records identified (committed search)</td><td>{_e(n_identified)}</td></tr>"
            f"<tr><td>Records screened (deduplicated)</td><td>{_e(len(recs))}</td></tr>"
            f"<tr><td>Excluded at screening — by rule</td><td>{_e(sum(rule_counts.values()))} ({_e(excl_bits)})</td></tr>"
            f"<tr><td>Met eligibility (P/I/C/design)</td><td>{_e(n_inc)}</td></tr>"
            f"<tr><td><strong>Pooled in the primary outcome (k)</strong></td><td><strong>{_e(pooled_k)}</strong></td></tr>"
            f"<tr><td>Eligible but outcome not extracted from the abstract (full-text pass pending)</td><td>{_e(n_inc - (pooled_k or 0))}</td></tr>"
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
    body = (flow + integ_html + f"<p>{len(recs)} records screened; <strong>{n_inc} included</strong>. "
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
            # Second independent extractor (CT.gov structured) corroborating the abstract number.
            verd = ("✓ corroborated" if cs.get("agree") else
                    ("⚠ DISCREPANCY" if cs.get("agree") is False else "· corroboration"))
            bits = []
            if cs.get("abstract_rr") is not None and cs.get("ctgov_rr") is not None:
                bits.append(f"abstract RR {cs['abstract_rr']} vs CT.gov RR {cs['ctgov_rr']}")
            elif cs.get("ctgov_rr") is not None:
                bits.append(f"CT.gov RR {cs['ctgov_rr']}")
            src += (f"<div class='xsrc'><em>second source ({verd}):</em> "
                    + (_e("; ".join(bits) + ". ") if bits else "") + _e(cs.get("note", "")) + "</div>")
        j = t.get("identity_judgment")
        if j:
            # Model-derived outcome-identity judgment (checkable, 5 fields). It admitted this
            # CT.gov measure as THE review's outcome; it supplies no number.
            src += ("<div class='ident'><em>outcome-identity check (model-derived):</em> "
                    f"population <b>{_e(j.get('candidate_population'))}</b>; "
                    f"timepoint <b>{_e(j.get('candidate_timepoint'))}</b>; "
                    f"definition <b>{_e(j.get('candidate_definition'))}</b>; "
                    f"is-match <b>{_e(j.get('is_match'))}</b> — {_e(j.get('rationale'))}</div>")
        rows.append(f"<tr><td>{_e(t.get('label'))}</td><td>{_e(t.get('id'))}</td>"
                    f"<td>{inp}</td><td>{src}</td></tr>")
    absent = "".join(f"<tr><td>{_e(t.get('label'))}</td><td>{_e(t.get('id'))}</td>"
                     f"<td class='absent-cell'>{_e(_absent_label(t.get('reason')))}</td><td>{_e(t.get('reason'))}</td></tr>"
                     for t in o.get("declared_absent_trials", []) or [])
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


def _outcome_block(o, show_inputs=True):
    reason = _absent(o)
    if reason:
        return f"<h4>{_e(o.get('name'))}</h4>" + _absent_block(reason)
    body = f"<h4>{_e(o.get('name'))}{' (primary)' if o.get('primary') else ''}</h4>"
    res = o.get("result")
    rr = _absent(res)
    if rr:
        body += _absent_block(rr)
    elif res.get("suppressed_incompatible"):
        # FAIL CLOSED (audit 23): detected-invalid means NOTHING pooled is rendered — no effect, CI, tau^2,
        # prediction interval, common-effect sensitivity, forest or leave-one-out. Only the reason + the
        # per-trial estimates (below) survive. Detecting the failure and printing the number is a caption.
        body += ("<div class='absent'><strong>Pooled result SUPPRESSED (estimand-incompatible).</strong> "
                 f"{_e(res.get('suppressed_reason'))} <em>Estimand classes: "
                 f"{_e(' + '.join((res.get('estmeasure') or {}).get('canonicals', [])))}; k = "
                 f"{_e(res.get('k'))} trials, shown individually below, not pooled.</em></div>")
    else:
        body += _kv([(k, v) for k, v in [
            # Show the scale of the number ACTUALLY pooled (res["scale"]: RR / HR / IRR / MD /
            # "mixed (…)"), not the topic's target estimand — the target is stated in the Analysis
            # Method prose, and a row reading "Estimand RR" beside a pooled HR is the defect this fixes.
            ("Estimand", res.get("scale") or o.get("estimand")),
            ("Estimand compatibility", (
                ("⚠ INCOMPATIBLE — the pooled trials report DIFFERENT estimand classes ("
                 + " + ".join((res.get("estmeasure") or {}).get("canonicals", []))
                 + "): a recurrent-event/rate ratio and a first-event ratio count different things, so "
                 "the pooled number mixes measures that are not directly poolable — read it as a rough "
                 "signal, not a valid summary (a stated limitation, surfaced not smoothed)")
                if (res.get("estmeasure") or {}).get("status") == "incompatible" else
                ("reported labels differ (" + ", ".join((res.get("estmeasure") or {}).get("labels", []))
                 + ") but are the SAME compatibility class (first-event relative ratios: RR/OR/HR) — "
                 "pooled as compatible, not an estimand conflict"
                 if (res.get("estmeasure") or {}).get("status") == "compatible_labels" else None))),
            ("Analysis population", o.get("population")),
            ("Timepoint", o.get("timepoint")),
            ("Method", o.get("method")),
            ("k", res.get("k")),
            (_effect_label(res), _ci(res)),
            ("Common-effect CI (k=2 sensitivity)",
             (f"{_num(res.get('estimate_fixed'))} ({res.get('scale')}), 95% CI "
              f"{_num(res.get('ci_low_fixed'))}–{_num(res.get('ci_high_fixed'))}"
              if res.get("ci_low_fixed") is not None else None)),
            ("Prediction interval", (f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}" if res.get('pi_low') is not None else None)),
            ("τ²", _tau(res.get("tau2")) if res.get("tau2") is not None else None),
            ("Note", res.get("pi_note")),
            ("Small-k note", res.get("fixed_note")),
            ("Composite heterogeneity", res.get("composite_heterogeneity")),
            ("Leave-one-out (influence)", _loo_text(res.get("leave_one_out"))),
        ] if v is not None])
        # A k stated without the contributing trials named is the container-vs-contents
        # defect. When trials are enumerable, name them (below). When they are not (a
        # transcribed comparator), say so plainly so the bare k is not mistaken for auditable.
        if (res.get("k") is not None and not o.get("trials")
                and not o.get("declared_absent_trials")):
            body += ("<p class='note'>k is as reported by the source; the individual trials "
                     "behind it were not machine-extracted from the transcription, so this "
                     "count cannot be audited on this page.</p>")
    n_pool = len(o.get("trials") or [])
    n_abs = len(o.get("declared_absent_trials") or [])
    if show_inputs and (n_pool or n_abs):
        if n_abs and n_pool:
            body += (f"<p class='note'>k = {n_pool}: the {n_pool} trial(s) named below were "
                     f"pooled; {n_abs} further screened-in trial(s) had no poolable value for this "
                     f"outcome <em>in the abstract</em> and are listed below. Most are marked "
                     f"<em>not extracted — abstract only, full text not retrieved</em>: that is an "
                     f"extraction limit, NOT evidence the outcome is absent from the trial. A full-text "
                     f"retrieval pass is the fix (in progress); genuine exclusions are labelled "
                     f"<em>excluded</em> with their reason.</p>")
        body += _trial_inputs(o)
    return body


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


def _outcomes(r, neutral):
    outs = [o for o in (r.get("outcomes") or []) if o.get("kind") != "harm"]
    if not outs:
        return _absent_block("no efficacy outcomes in the review object")
    return _definition_audit_block(r) + "".join(_outcome_block(o) for o in outs)


def _harms(r, neutral):
    harms = [o for o in (r.get("outcomes") or []) if o.get("kind") == "harm"]
    if not harms:
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
    for rep in c.get("reported", []) or []:
        body += f"<p>{_e(rep.get('outcome'))}: {_num(rep.get('estimate'))} ({rep.get('scale')}), 95% CI {_num(rep.get('ci_low'))}–{_num(rep.get('ci_high'))}</p>"
    sc = c.get("scope") or {}
    if sc:
        v = "✓ same question" if sc.get("scope_valid") else "⚠ SCOPE MISMATCH"
        body += ("<h4>Scope match (is this the same question?)</h4>"
                 f"<p><strong>{v}.</strong> Intervention level: topic is {'class-level' if sc.get('topic_is_class') else 'a single agent'}, "
                 f"comparator is {'class-level' if sc.get('comparator_is_class') else 'a single agent'} "
                 f"(match: {_e(sc.get('intervention_level_match'))}); population match: {_e(sc.get('population_match'))}. "
                 f"{_e(sc.get('note'))} <span class='muted'>Decided by one uniform rule applied to every topic "
                 "before the k was seen.</span></p>")
        # When the uniform rule flags a mismatch, resolving a VALID (same-scope) comparator is required.
        # This per-topic note records the resolution: either a single-agent benchmark exists and is
        # used, or none exists (k=1 is the complete single-drug evidence base — itself a finding), or
        # the mismatch coincides with a genuine single-drug reach gap that must be ground down, not
        # excused as scope. Sourced from the topic config; shown verbatim beside the uniform verdict.
        if r.get("comparator_scope_note"):
            body += f"<p><strong>Comparator resolution.</strong> {_e(r.get('comparator_scope_note'))}</p>"
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
                      "the protocol preceding synthesis. The PICO is still fixed and the build is "
                      "byte-reproducible; only prospective PRECEDENCE is unproven here.")
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
    if pa := rep.get("parity"):
        body += (f"<h4>Parity with the published comparator</h4><p>Our pooled <em>k</em> = "
                 f"<strong>{_e(pa.get('our_k'))}</strong> vs the comparable same-scope comparator "
                 f"<em>k</em> = <strong>{_e(pa.get('comparable_comparator_k'))}</strong> &mdash; "
                 f"<strong>{_e(pa.get('status'))}</strong>. {_e(pa.get('reason'))}</p>")
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
            f"<td>{_e(x.get('not_pooled_because'))}</td></tr>" for x in rf)
        body += ("<h4>Verified but not pooled (refusals, with reasons)</h4>"
                 "<p class='muted'>Trials we located and whose numbers we verified against source, "
                 "yet deliberately did not pool. Honest k over inflated k: a named refusal is a result.</p>"
                 "<table class='arms'><tr><th>Trial</th><th>What was verified</th>"
                 f"<th>Why it was not pooled</th></tr>{rows}</table>")
    # CANONICAL CLAIM OBJECT: every surface derives its significance wording from one object; the build
    # scans the rendered page + manuscript and fails closed on any surface that asserts the opposite.
    if cc := rep.get("claim_check"):
        n_con = len(cc.get("contradictions") or [])
        body += ("<h4>Canonical claim object (one object, every surface)</h4>"
                 "<p>Each stated result on this page &mdash; whether it is statistically significant, "
                 "whether its interval spans no effect &mdash; is derived from a single claim object, "
                 "not recomputed per surface. At build the rendered page and manuscript are scanned for "
                 "any wording that asserts the opposite of that object; the build is refused on a "
                 f"contradiction. <strong>Claims checked: {_e(cc.get('claims_checked'))}; "
                 f"contradictions caught: {n_con}.</strong>"
                 + ("" if n_con == 0 else " " + _e(json.dumps(cc.get("contradictions"))))
                 + "</p>")
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
    items = [
        ("5 Eligibility criteria", bool(prot.get("eligibility")),
         "Protocol tab — generated from the structured include object (P/I/C/design), so declared == enforced.",
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
         ("Risk-of-bias tab — overall GRADE certainty is NOT RATEABLE: the primary pool mixes incompatible "
          "estimand classes, so no overall certainty, 95% CI or tau^2 summary is asserted (the domain signals "
          "are shown, the overall is suppressed until the estimand is made coherent)."
          if res.get("suppressed_incompatible") else
          "Results tab — the machine-computable certainty signals are shown: imprecision via the 95% CI"
          + (" and the prediction interval" if has_pi else "")
          + (", single-trial (k=1) flagged" if res.get("k") == 1 else "")
          + ", inconsistency via tau^2. A PARTIAL, object-derived GRADE is now rendered on the Risk-of-bias tab "
            "(risk-of-bias, inconsistency, imprecision, and registry-based publication bias computed from "
            "committed fields; indirectness left to human judgement) — a graded certainty label with each "
            "domain's basis, not a full hand-graded GRADE."),
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
          f"(SHA {_build_sha}), so the build is byte-reproducible but prospective precedence is NOT demonstrated "
          "here; eligibility is generated from the structured object."),
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
    """RoB2-style risk of bias, per pooled trial, built from AACT structured design fields + the
    registry-vs-pooled outcome (Domain 5). Partial-but-honest: domains needing human judgement are
    marked 'not assessed', never guessed. No published-meta comparator in our set renders this."""
    rb = r.get("rob2") or {}
    assessed = rb.get("trials") or {}
    # RoB2 here is assessed for the PRIMARY outcome's pooled trials (that is the scope the builder
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
    if not pooled and not assessed:
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
    # coverage is visible. RoB2 D1/D2/D4 here are auto-derived from AACT registry fields keyed on NCT;
    # a trial with no NCT/AACT match cannot be machine-assessed and is not guessed.
    unassessed = sorted(pid for pid in pooled if pid not in assessed)
    _na = "not assessed"
    _basis = "no NCT/AACT registry match for this pooled trial — the auto-derived RoB2 domains are not machine-assessable here and are not guessed"
    for pid in unassessed:
        cells = "".join(f"<td class='absent-cell' title='{_e(_basis)}'>{_e(_na)}</td>" for _ in dom_labels)
        rows.append(f"<tr><td>{_e(pid)}</td><td class='absent-cell'>{_e(_na)}</td>{cells}</tr>")
    n_ass, n_pool = len(pooled) - len(unassessed), len(pooled)
    cover = (f"<strong>Coverage: {n_ass} of {n_pool} primary-outcome pooled trials have a registry (AACT) "
             f"match and are assessed below</strong>"
             + (f"; the other {len(unassessed)} are pooled but have no registry match "
                f"({_e(', '.join(unassessed))}) and are shown as <em>not assessed</em> with the reason — "
                "never guessed." if unassessed else " (all primary-outcome pooled trials assessed).")
             + (f" RoB2 is scoped to the primary outcome; {len(secondary_only)} trial(s) pooled only in "
                f"secondary outcomes ({_e(', '.join(sorted(secondary_only)))}) are outside this assessment."
                if secondary_only else "")) if n_pool else ""
    uoa = r.get("unit_of_analysis") or []
    uoa_html = ""
    if uoa:
        items = "; ".join(f"{_e(u.get('id'))} ({_e(u.get('design'))})" for u in uoa)
        _sens = _uoa_sensitivity(r, [u.get("id") for u in uoa])
        _sens_txt = ""
        if _sens and len(_sens["points"]) > 1:
            base = _sens["points"][0][1]
            rng = "; ".join(f"&times;{f:g}&rarr;{est}" for f, est in _sens["points"][1:])
            _sens_txt = (f" <strong>The pooled point estimate is NOT invariant to this</strong>: inflating only "
                         f"these trials' variances re-pools (illustrative DL) from {base} to "
                         f"{_sens['points'][-1][1]} ({rng}) — because changing a study's variance changes its "
                         "inverse-variance weight, so both the estimate and its interval move.")
        uoa_html = ("<div class='absent'><strong>Unit-of-analysis caveat (disclosed, not adjusted).</strong> "
                    f"{len(uoa)} pooled trial(s) use a cluster-randomized or cluster-period (policy) crossover "
                    f"design: {items}. They are pooled from patient-level counts <strong>without applying a "
                    "design effect</strong> (cluster ICC / cluster-period correlation), because that variance "
                    "component is not reported in the source — these are CLUSTER-PERIOD policy crossovers, not "
                    "within-person crossovers. <strong>Consequence:</strong> the true variance of these trials is "
                    "larger than the patient-level calculation assumes, so their inverse-variance <strong>weight "
                    "in the pool is OVERSTATED</strong> and the pooled confidence interval is <strong>too narrow"
                    "</strong> (over-precise)." + _sens_txt + " This is a stated limitation (a documented "
                    "meta-analysis error class the harness flags but cannot correct without the missing variance "
                    "component), not a silent simple-parallel pooling.</div>")
    fund = r.get("funding") or []
    fund_html = ""
    if fund:
        def _ord(t):
            t = t or ""
            if t.startswith("industry"):
                return 0
            if t == "mixed":
                return 1
            if t.startswith("public"):
                return 2
            if t.startswith("declared") or t.startswith("stated"):
                return 3
            return 4  # not stated (either depth)
        def _celltype(f):
            return _e(f.get("type")) + (f"<br><em>{_e(f.get('note'))}</em>" if f.get("note") else "")
        fund_rows = "".join(
            f"<tr><td>{_e(f.get('id'))}</td><td>{_celltype(f)}</td>"
            f"<td>{_e(f.get('scanned') or f.get('source'))}</td><td>{_e(f.get('span'))}</td></tr>"
            for f in sorted(fund, key=lambda f: _ord(f.get("type"))))
        n_ind = sum(1 for f in fund if (f.get("type") or "").startswith("industry")
                    or f.get("type") == "mixed" or f.get("note"))
        n_ns_ft = sum(1 for f in fund if (f.get("type") or "").startswith("not stated (full text"))
        n_ns_ab = sum(1 for f in fund if (f.get("type") or "").startswith("not stated (abstract"))
        # UNKNOWN must not be folded into the negative denominator (audit 23): the industry-funded fraction
        # is over trials whose funding is KNOWN (industry / mixed / public / non-profit, or an industry
        # drug-supply tie), NOT over the whole pool. "not stated" and "declared (source unclassified)" are
        # unknown for the industry property and are reported separately, never as "not industry-funded".
        def _fund_known(f):
            t = (f.get("type") or "")
            return (t.startswith("industry") or t == "mixed" or t.startswith("public")
                    or t.startswith("non-profit") or bool(f.get("note")))
        n_known = sum(1 for f in fund if _fund_known(f))
        n_unknown = len(fund) - n_known
        fund_html = ("<div class='absent'><strong>Funding / conflict-of-interest disclosure (per pooled "
                     "trial, from source — disclosed, not adjusted).</strong> Industry-funded trials are a "
                     "documented reporting-bias dimension (they tend to report more favourable results). For "
                     "each pooled trial the funding source is classified from a verbatim statement in the "
                     "committed source (full text preferred, abstract fallback), including an industry "
                     "<em>drug-supply</em> tie in an otherwise independently funded trial: "
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
                     "<table class='arms'><tr><th>Trial</th><th>Funding</th><th>Scanned</th>"
                     f"<th>Verbatim statement</th></tr>{fund_rows}</table></div>")
    # Arm-contrast disclosure (TIER-1 structural fix): whether each pooled trial's intervention of interest
    # is a registry-CONFIRMED randomised contrast (differs across arms) or a fail-open/background inclusion.
    # The fail-open state is VISIBLE (a trial with no registry arm data reads 'contrast unverified'), never a
    # silent verified-looking inclusion. Never an adjustment; a disclosure computed from AACT arm structure.
    ac = (r.get("arm_contrast") or {}).get("trials") or {}
    ac_html = ""
    if ac:
        _AC_LABEL = {"verified": "randomised contrast verified",
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
        ac_html = ("<div class='absent'><strong>Randomised-contrast disclosure (per pooled trial, from the "
                   "registry arm structure — disclosed, not an adjustment).</strong> Eligibility should test "
                   "what actually DIFFERS between the randomised arms, not the mere presence of the drug word: "
                   "a trial giving the drug of interest as BACKGROUND in every arm (e.g. all arms on the same "
                   "agent, randomising a different drug) is not a randomised comparison of it. For each pooled "
                   "trial the randomised contrast is reconstructed from AACT <code>design_groups</code> + "
                   f"<code>interventions</code>: <strong>{n_ver} of {len(ac)}</strong> pooled trials have a "
                   "registry-confirmed contrast (the intervention of interest differs across arms)"
                   + (f"; <strong>{n_bg} is background in every arm (flagged)</strong>" if n_bg else "")
                   + ". A trial with no registry arm data, or coded under a class label / development code we "
                   "cannot machine-match, is shown as <em>contrast unverified</em> — a VISIBLE fail-open state, "
                   "never silently treated as verified. "
                   "<table class='arms'><tr><th>Trial</th><th>Contrast status</th><th>Randomised difference</th>"
                   f"</tr>{ac_rows}</table></div>")
    # RoB-stratified sensitivity re-pool (object-derived from r['rob_sensitivity']; regenerates on rebuild)
    sens = r.get("rob_sensitivity") or {}
    sens_html = ""
    if sens.get("full"):
        def _fmt(p):
            if not p:
                return "&mdash;"
            return f"k={p['k']}, {p['scale']} {p['estimate']} [{p['ci_low']}, {p['ci_high']}]"
        f, dh, lo = sens.get("full"), sens.get("drop_high"), sens.get("low_only")
        n_rated, n_tr = sens.get("n_rob_rated"), sens.get("n_trials")
        lines = [f"<tr><td>Full pool (all pooled trials)</td><td>{_fmt(f)}</td></tr>"]
        if sens.get("any_high"):
            lines.append(f"<tr><td>Excluding high risk of bias</td><td>{_fmt(dh)}</td></tr>")
        # An EMPTY low-risk-only subgroup is NOT ESTIMABLE, never 'no difference' / agreement: with no
        # pooled trial qualifying as low risk, the re-pool cannot be computed at all. Render it as such.
        if not lo:
            low_cell = ("<strong>NOT ESTIMABLE</strong> &mdash; no pooled trial qualifies as low risk of "
                        "bias, so this stratum has no trials to re-pool (an empty subgroup is not agreement "
                        "with the full pool)")
        else:
            low_cell = _fmt(lo) + ("" if sens.get("low_only_informative")
                                   else " <em>(fewer trials than the full pool &mdash; see coverage)</em>")
        lines.append(f"<tr><td>Low risk of bias only</td><td>{low_cell}</td></tr>")
        sens_html = ("<h4>Risk-of-bias sensitivity (re-pooled with the same estimator)</h4>"
                     "<div class='absent'><strong>Does the result survive dropping the trials that are not "
                     "low risk of bias?</strong> The primary outcome is re-pooled by risk-of-bias stratum "
                     "with the identical estimator. "
                     f"<strong>{n_rated} of {n_tr}</strong> pooled trials have a risk-of-bias rating; "
                     + ("no pooled trial is rated <em>high</em> risk (the registry-derived assessment does not "
                        "reach 'high'), so the standard drop-high sensitivity is inert and the informative "
                        "stratum is <em>low-only</em>. " if not sens.get("any_high") else "")
                     + "An unrated trial cannot be placed in a stratum, so a low-only pool with fewer trials "
                     "than the full pool reflects both risk of bias and assessment coverage &mdash; read the "
                     "widened interval with that caveat, not as instability of the effect."
                     f"<table class='arms'><tr><th>Stratum</th><th>Re-pooled estimate</th></tr>"
                     f"{''.join(lines)}</table></div>")
    # Partial, object-derived GRADE certainty (from r['grade'])
    g = r.get("grade") or {}
    grade_html = ""
    if g.get("certainty"):
        doms = g.get("domains", {})
        order = [("risk_of_bias", "Risk of bias"), ("inconsistency", "Inconsistency"),
                 ("imprecision", "Imprecision"), ("indirectness", "Indirectness"),
                 ("publication_bias", "Publication bias (registry-based)")]
        drows = []
        for k, lab in order:
            dv = doms.get(k, {})
            dn = dv.get("downgrade", 0)
            mark = ("&minus;1" if dn == 1 else f"&minus;{dn}" if dn else "not downgraded")
            if dv.get("not_auto_rated"):
                mark = "human judgement"
            drows.append(f"<tr><td>{_e(lab)}</td><td>{mark}</td><td>{_e(dv.get('basis',''))}</td></tr>")
        cap = (" The rating is capped below <em>high</em> because risk of bias is not assessed for every "
               "pooled trial." if g.get("certainty_capped_by_rob_coverage") else "")
        if g.get("certainty_capped_d3_unassessed"):
            cap += (" The rating is capped below <em>high</em> because D3 (missing outcome data), a required "
                    "risk-of-bias domain, is NOT ASSESSED for any pooled trial (no outcome-missingness "
                    "source) — high certainty cannot be certified on a structurally-incomplete bias assessment.")
        if g.get("certainty") == "not_rateable":
            grade_html = ("<h4>GRADE certainty — NOT RATEABLE</h4>"
                          "<div class='absent'><strong>Overall certainty: not rateable.</strong> "
                          f"{_e(g.get('not_rateable_reason',''))}. The individual domain signals are shown "
                          "below, but no overall certainty category is emitted — a partial or incoherent "
                          "evidence object cannot produce one, and &lsquo;provisional&rsquo; would soften the "
                          "language without repairing the logic."
                          "<table class='arms'><tr><th>Domain</th><th>Signal</th><th>Basis</th></tr>"
                          f"{''.join(drows)}</table></div>")
        else:
          grade_html = ("<h4>GRADE certainty (PROVISIONAL — partial, object-derived)</h4>"
                      "<div class='absent'><strong>Overall certainty (provisional): "
                      f"{_e(g.get('certainty','').replace('_',' '))}</strong> "
                      f"(starting from <em>high</em> for randomized trials, {g.get('downgrades',0)} "
                      "downgrade(s)).{}"
                      "<strong>PROVISIONAL:</strong> this is a machine-derived certainty — risk of bias "
                      "uses machine-derived signals (not a human RoB2) and indirectness is not auto-rated, "
                      "so a formal human GRADE assessment may differ. "
                      "Risk of bias, inconsistency, imprecision and publication bias are computed from "
                      "committed fields; <strong>publication bias is assessed from the registry ghost census, "
                      "not funnel-plot asymmetry</strong> (which is unreliable at our small k). "
                      "<strong>Indirectness is left to human judgement</strong> (the PICO scope note states "
                      "the directness) &mdash; this is a partial GRADE, honestly labelled."
                      "<table class='arms'><tr><th>Domain</th><th>Effect on certainty</th><th>Basis</th></tr>"
                      f"{''.join(drows)}</table></div>").format(cap)
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
            + "<p><strong>Machine-derived risk-of-bias signals</strong> (per pooled trial) &mdash; NOT a "
            "formal Cochrane RoB2 assessment, which requires human judgements the registry cannot supply. "
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
.banner{background:#eaf4fb;border-left:4px solid #4ea1d3;padding:10px 14px;margin:12px 0;font-size:13.5px}
.note{color:#4a5b66;font-size:12.5px;margin:6px 0;font-style:italic}
.q{font-size:16px;color:#2a4b5c}pre{background:#0f1c24;color:#d6e6f2;padding:10px;overflow:auto;border-radius:6px;font-size:12px;white-space:pre-wrap}
h2{margin-top:0}h4{margin:16px 0 4px}
"""
_JS = """document.documentElement.className='js';
function show(id){document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('active',t.id==='tab-'+id)});
document.querySelectorAll('nav button').forEach(function(b){b.classList.toggle('active',b.dataset.t===id)});}
(function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();"""


def render_page(review: dict, neutral: bool = False) -> str:
    tabs_spec = [(tid, lbl) for tid, lbl in TABS if not (neutral and tid in NEUTRAL_DROP)]
    nav = "".join(f'<button data-t="{tid}" onclick="show(\'{tid}\')">{_e(lbl)}</button>' for tid, lbl in tabs_spec)
    body = ""
    for tid, lbl in tabs_spec:
        body += (f'<section class="tab" id="tab-{tid}">'
                 f'<h3 class="tabname">{_e(lbl)}</h3>{_R[tid](review, neutral)}</section>')
    title = _e(review.get("title") or review.get("slug"))
    sub = ("Meta-analysis" if neutral else
           "Reproducible meta-analysis harness — auditability, not authority")
    return ("<!doctype html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>{title}</title><style>{_CSS}</style></head><body>"
            f"<header><h1>{title}</h1><div class=sub>{sub}</div></header>"
            f"<nav>{nav}</nav><main>{body}</main><script>{_JS}</script></body></html>")
