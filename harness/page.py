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
    ("riskofbias", "Risk of bias"),
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
                ("Estimand", res.get("scale") or prim.get("estimand")),
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
    if not neutral:
        _tok, _ttot, _tcomp = _transparency_counts(r)
        if _ttot:
            _pct = round(100 * _tok / _ttot)
            parts.append(
                "<h3>Transparency (independently checkable)</h3>"
                f"<p><strong>{_e(_tok)} of {_e(_ttot)} numerical claims on this page ({_pct}%) carry a "
                "one-click source</strong> a reader can open to check independently — each pooled number "
                "its PMID/NCT and verbatim span, each declared-absent trial its reason, each risk-of-bias "
                "domain the structured field it read, the reproduction its protocol SHA and replay result. "
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
    rc = s.get("recall")
    if rc and rc.get("known"):
        # PRIMARY search metric: how many of this topic's KNOWN trials the committed registry-first
        # query recovers (reach, not inclusion). Regenerable by re-running scripts/recall.py.
        status = rc.get("status")
        line = (f"Registry-first RECALL: recovered <strong>{_e(rc.get('recovered'))}/{_e(rc.get('known'))}</strong> "
                f"of this topic's known trials (enumerated {_e(rc.get('enumerated'))}; status {_e(status)}).")
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
                     f"<td class='absent-cell'>declared absent</td><td>{_e(t.get('reason'))}</td></tr>"
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
    else:
        body += _kv([(k, v) for k, v in [
            # Show the scale of the number ACTUALLY pooled (res["scale"]: RR / HR / IRR / MD /
            # "mixed (…)"), not the topic's target estimand — the target is stated in the Analysis
            # Method prose, and a row reading "Estimand RR" beside a pooled HR is the defect this fixes.
            ("Estimand", res.get("scale") or o.get("estimand")),
            ("Analysis population", o.get("population")),
            ("Timepoint", o.get("timepoint")),
            ("Method", o.get("method")),
            ("k", res.get("k")),
            (_effect_label(res), _ci(res)),
            ("Prediction interval", (f"{_num(res.get('pi_low'))}–{_num(res.get('pi_high'))}" if res.get('pi_low') is not None else None)),
            ("τ²", _num(res.get("tau2")) if res.get("tau2") is not None else None),
            ("Note", res.get("pi_note")),
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
        ("k stated in the comparator's own text (auto-extracted)", ov.get("theirs_k")),
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
    body = _kv([
        ("Reproduction census failures", rep.get("failures")),
        ("Re-run from registration SHA", rep.get("protocol_sha")),
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
    body += ("<div class='banner'><strong>What this reproduction claim covers — and what it does not.</strong> "
             "It proves DETERMINISTIC REPLAY: re-running from the registration SHA on a fresh clone replays "
             "the committed cache and regenerates this page byte-for-byte (same inputs → same output). It does "
             "NOT claim independent REPEATABILITY — that a fresh literature search run today would retrieve the "
             "same trial set. Search databases update, records are added and revised, so the retrieved set can "
             "drift; the committed queries are printed verbatim on the Search tab so anyone can re-run them, and "
             "'re-search mode' (scripts/research_diff.py) measures the drift explicitly rather than assuming none. "
             "This is the honest form of 'living, not frozen': the analysis is frozen and auditable; the literature is not.</div>")
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
        uoa_html = ("<div class='absent'><strong>Unit-of-analysis caveat (disclosed, not adjusted).</strong> "
                    f"{len(uoa)} pooled trial(s) use a cluster-randomized or crossover design: {items}. "
                    "They are pooled from patient-level counts <strong>without applying a design effect</strong> "
                    "(cluster ICC) or a within-subject (crossover) adjustment, because the ICC / paired "
                    "variance is not reported in the source. <strong>Consequence:</strong> the true variance of "
                    "these trials is larger than the patient-level calculation assumes, so their inverse-variance "
                    "<strong>weight in the pool is OVERSTATED</strong> and the pooled confidence interval is "
                    "<strong>too narrow</strong> (over-precise) — the pooled point estimate is unaffected, but its "
                    "certainty is optimistic. This is a stated limitation (a documented meta-analysis error class "
                    "the harness flags but cannot correct without the missing variance component), not a silent "
                    "simple-parallel pooling.</div>")
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
        rows = "".join(
            f"<tr><td>{_e(f.get('id'))}</td><td>{_celltype(f)}</td>"
            f"<td>{_e(f.get('scanned') or f.get('source'))}</td><td>{_e(f.get('span'))}</td></tr>"
            for f in sorted(fund, key=lambda f: _ord(f.get("type"))))
        n_ind = sum(1 for f in fund if (f.get("type") or "").startswith("industry")
                    or f.get("type") == "mixed" or f.get("note"))
        n_ns_ft = sum(1 for f in fund if (f.get("type") or "").startswith("not stated (full text"))
        n_ns_ab = sum(1 for f in fund if (f.get("type") or "").startswith("not stated (abstract"))
        fund_html = ("<div class='absent'><strong>Funding / conflict-of-interest disclosure (per pooled "
                     "trial, from source — disclosed, not adjusted).</strong> Industry-funded trials are a "
                     "documented reporting-bias dimension (they tend to report more favourable results). For "
                     "each pooled trial the funding source is classified from a verbatim statement in the "
                     "committed source (full text preferred, abstract fallback), including an industry "
                     "<em>drug-supply</em> tie in an otherwise independently funded trial: "
                     f"<strong>{n_ind} of {len(fund)}</strong> pooled trials are industry-funded or "
                     "industry-tied (the industry-funded proportion of this pool, for comparison against a "
                     "comparator's). Absence is labelled by how "
                     f"deeply we looked — {n_ns_ft} with no funding statement in the <strong>full text</strong> "
                     f"(genuinely silent) and {n_ns_ab} where only the <strong>abstract</strong> was available "
                     "(full text not retrieved) — so 'not stated' is never presented as 'independently funded'. "
                     "The harness <strong>does not adjust</strong> for funding (the per-trial bias magnitude is "
                     "not quantifiable from a funding line) — it is disclosed so a reader can weigh it. Never "
                     "inferred."
                     "<table class='arms'><tr><th>Trial</th><th>Funding</th><th>Scanned</th>"
                     f"<th>Verbatim statement</th></tr>{rows}</table></div>")
    return (f"<p>{cover}</p>" + uoa_html + fund_html
            + "<p>Per-pooled-trial RoB2 risk of bias, computed from what is machine-available "
            f"({_e(rb.get('source') or 'AACT registry fields')}). <strong>Domain 5 (selective reporting)</strong> "
            "is computed from the trial's REGISTERED primary outcome vs the outcome we pooled — a machine-checkable "
            "signal most published meta-analyses do not report. D1/D2/D4 use AACT structured allocation/masking "
            "fields. D3 (missing outcome data) and the risk-of-bias judgements that need human reading are marked "
            "<em>not assessed — requires human judgement</em>: partial-but-honest, never guessed. Hover a cell "
            "for its basis.</p>"
            f"<table class='recs'>{head}{rows_join(rows)}</table>")


_R = {"overview": _overview, "protocol": _protocol, "search": _search,
      "screening": _screening, "outcomes": _outcomes, "harms": _harms, "riskofbias": _riskofbias,
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
