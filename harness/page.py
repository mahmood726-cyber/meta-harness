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
from typing import Any

TABS = [
    ("overview", "Overview"),
    ("protocol", "Protocol"),
    ("search", "Search"),
    ("screening", "Screening"),
    ("outcomes", "Results"),
    ("harms", "Harms"),
    ("comparator", "Comparator"),
    ("reporting", "Reporting (PRISMA)"),
    ("reproduction", "Reproducibility"),
]
NEUTRAL_DROP = {"comparator"}


def _e(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def _num(x: Any) -> str:
    if isinstance(x, float):
        return f"{x:.3g}"
    return _e(x)


def _absent(section: Any):
    if section is None:
        return "not declared in the review object"
    if isinstance(section, dict) and section.get("present") is False:
        return section.get("reason") or "declared absent (no reason given)"
    return None


def _absent_block(reason: str) -> str:
    return f'<div class="absent"><strong>DECLARED ABSENT.</strong> {_e(reason)}</div>'


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

def _overview(r, neutral):
    parts = [f"<h2>{_e(r.get('title'))}</h2>", f"<p class='q'>{_e(r.get('question'))}</p>"]
    if not neutral:
        parts.append(
            "<div class='banner'>This page offers <strong>greater auditability, not "
            "stronger evidence</strong>: every number traces to a committed source, every "
            "absence is declared, and any hand-edit breaks the reproduction census.</div>")
    prim = _primary(r)
    if prim and _absent(prim) is None:
        res = prim.get("result") or {}
        if _absent(res) is None:
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
                ("Estimand", prim.get("estimand")),
                ("Trials pooled (k)", kdisp),
            ]
            if recon:
                rows.append(("Screened-in → pooled", recon))
            rows.append((_effect_label(res), _ci(res)))
            if res.get("pi_low") is not None:
                rows.append(("Prediction interval", f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}"))
            if res.get("tau2") is not None:
                rows.append(("Between-study τ²", _num(res.get("tau2"))))
            rows.append(("Method", prim.get("method") or r.get("method_declared")))
            parts.append(_kv(rows))
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
    rc = s.get("recall")
    if rc and rc.get("known"):
        # PRIMARY search metric: how many of this topic's KNOWN trials the committed registry-first
        # query recovers (reach, not inclusion). Regenerable by re-running scripts/recall.py.
        status = rc.get("status")
        line = (f"Registry-first RECALL: recovered <strong>{_e(rc.get('recovered'))}/{_e(rc.get('known'))}</strong> "
                f"of this topic's known trials (enumerated {_e(rc.get('enumerated'))}; status {_e(status)}).")
        if rc.get("missed"):
            line += f" Missed: {_e(', '.join(str(m) for m in rc.get('missed', [])))} — a reach gap, not an inclusion decision."
        if rc.get("measured_utc"):
            line += f" <span class='muted'>Measured {_e(rc.get('measured_utc'))}.</span>"
        body += ("<h4>Registry-first recall (reach)</h4><p>" + line
                 + " Recall is search REACH; whether a recovered trial is eligible/poolable is the "
                 "screen's and extractor's job — a candidate is not an include.</p>")
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
                   f"pooled trials is retracted"
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
            f"<tr><td>Eligible but outcome not extractable (declared-absent)</td><td>{_e(n_inc - (pooled_k or 0))}</td></tr>"
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
            inp = f"{_num(t.get('effect'))} ({o.get('estimand')}), 95% CI {_num(t.get('ci_low'))}–{_num(t.get('ci_high'))}"
        else:
            inp = "—"
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
                     f"<td class='absent-cell'>declared absent</td><td>{_e(t.get('reason'))}</td></tr>"
                     for t in o.get("declared_absent_trials", []) or [])
    return ("<table class='arms'><tr><th>Trial</th><th>Id</th><th>Input</th><th>Source</th></tr>"
            + rows_join(rows) + absent + "</table>")


def rows_join(rows):
    return "".join(rows)


def _outcome_block(o, show_inputs=True):
    reason = _absent(o)
    if reason:
        return f"<h4>{_e(o.get('name'))}</h4>" + _absent_block(reason)
    body = f"<h4>{_e(o.get('name'))}{' (primary)' if o.get('primary') else ''}</h4>"
    res = o.get("result")
    rr = _absent(res)
    if rr:
        body += _absent_block(rr)
    else:
        body += _kv([(k, v) for k, v in [
            ("Estimand", o.get("estimand")),
            ("Analysis population", o.get("population")),
            ("Timepoint", o.get("timepoint")),
            ("Method", o.get("method")),
            ("k", res.get("k")),
            (_effect_label(res), _ci(res)),
            ("Prediction interval", (f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}" if res.get('pi_low') is not None else None)),
            ("τ²", _num(res.get("tau2")) if res.get("tau2") is not None else None),
            ("Note", res.get("pi_note")),
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
                     f"pooled; {n_abs} further screened-in trial(s) reported no poolable value "
                     f"for this outcome and are shown as <em>declared absent</em>.</p>")
        body += _trial_inputs(o)
    return body


def _outcomes(r, neutral):
    outs = [o for o in (r.get("outcomes") or []) if o.get("kind") != "harm"]
    if not outs:
        return _absent_block("no efficacy outcomes in the review object")
    return "".join(_outcome_block(o) for o in outs)


def _harms(r, neutral):
    harms = [o for o in (r.get("outcomes") or []) if o.get("kind") == "harm"]
    if not harms:
        return _absent_block("no harms recorded")
    return "".join(_outcome_block(o) for o in harms)


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
    ov = c.get("overlap") or {}
    body += "<h4>Trial-set overlap (an identical estimate on an identical set is arithmetic, not corroboration)</h4>"
    body += _kv([
        ("k in this review (our own search)", ov.get("ours_k")),
        ("k in the comparator", ov.get("theirs_k")),
        ("Shared trials", ov.get("shared_k")),
        ("Only in ours", ", ".join(ov.get("only_ours", []) or []) or None),
        ("Only in theirs", ", ".join(ov.get("only_theirs", []) or []) or None),
        ("Overlap method", ov.get("method")),
        ("Note", ov.get("note")),
    ])
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
    return _kv([
        ("Reproduction census failures", rep.get("failures")),
        ("Re-run from registration SHA", rep.get("protocol_sha")),
        ("Content hash (review core)", rep.get("review_sha256")),
        ("Replayed offline from committed cache", rep.get("from_cache")),
    ])


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
         "Results tab — the machine-computable certainty signals are shown: imprecision via the 95% CI"
         + (" and the prediction interval" if has_pi else "")
         + (", single-trial (k=1) flagged" if res.get("k") == 1 else "")
         + ", inconsistency via tau^2. A FORMAL GRADE rating (risk-of-bias, indirectness, publication bias) "
           "is NOT automated — it needs human judgement — so certainty is reported as signals, not a graded label.",
         ""),
        ("16a Flow with counts at every stage", bool(scr.get("records")),
         "Screening tab — PRISMA flow: identified -> screened -> excluded-by-rule (counts) -> eligible -> pooled k -> declared-absent.",
         "no screening flow"),
        ("16b Exclusions with reasons", bool(scr.get("records")),
         "Screening tab — every excluded record lists its rule id, a reason true of the record, and a verbatim span.",
         "no per-record exclusions"),
        ("24a-c Registration & protocol", bool(prot.get("sha")),
         f"Protocol + Reproducibility tabs — registered at commit SHA {str(prot.get('sha'))[:10]}, committed before synthesis, "
         "eligibility generated from the structured object.",
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


_R = {"overview": _overview, "protocol": _protocol, "search": _search,
      "screening": _screening, "outcomes": _outcomes, "harms": _harms,
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
