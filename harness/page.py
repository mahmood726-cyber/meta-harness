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
    head = "<tr><th>Record</th><th>Type</th><th>Decision</th><th>Rule</th><th>Reason (true of the record)</th></tr>"
    rows = "".join(
        f"<tr><td>{_e(x.get('id'))}</td><td>{_e(x.get('id_type'))}</td>"
        f"<td class='dec-{_e(x.get('decision'))}'>{_e(x.get('decision'))}</td>"
        f"<td>{_e(x.get('rule_id'))}</td><td>{_e(x.get('reason'))}</td></tr>"
        for x in recs)
    n_inc = sum(1 for x in recs if x.get("decision") == "include")
    body = (f"<p>{len(recs)} records screened; <strong>{n_inc} included</strong>. "
            "Eligibility is on P/I/C/design only; every record carries a rule id and a "
            "reason true of that record.</p>"
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
        rows.append(f"<tr><td>{_e(t.get('label'))}</td><td>{_e(t.get('id'))}</td>"
                    f"<td>{inp}</td><td>{_e(t.get('source'))}</td></tr>")
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


_R = {"overview": _overview, "protocol": _protocol, "search": _search,
      "screening": _screening, "outcomes": _outcomes, "harms": _harms,
      "comparator": _comparator, "reproduction": _reproduction}

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
