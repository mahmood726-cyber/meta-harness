"""Deterministic tabbed-page renderer.

render_page(review) is a PURE function of the review object: same input -> byte
-identical output (no timestamps, no randomness, stable ordering). This is what
makes the reproduction census meaningful.

Contract (owner): every tab renders what the object holds, and every ABSENCE is
DECLARED, never blank. A section is either present-with-content, or an explicit
{"present": False, "reason": "..."} that renders as a visible declared-absent block.
"""
from __future__ import annotations
import html
from typing import Any

TABS = [
    ("overview", "Overview"),
    ("protocol", "Protocol"),
    ("search", "Search"),
    ("screening", "Screening"),
    ("extraction", "Extraction"),
    ("synthesis", "Synthesis"),
    ("harms", "Harms"),
    ("comparator", "Comparator"),
    ("reproduction", "Reproduction"),
]


def _e(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def _absent(section: Any) -> str | None:
    """Return a declared-absent reason if the section is not present, else None."""
    if section is None:
        return "not declared in the review object"
    if isinstance(section, dict) and section.get("present") is False:
        return section.get("reason") or "declared absent (no reason given)"
    return None


def _absent_block(reason: str) -> str:
    return (
        f'<div class="absent"><strong>DECLARED ABSENT.</strong> '
        f'{_e(reason)}</div>'
    )


def _kv_table(rows: list[tuple[str, Any]]) -> str:
    trs = "".join(
        f"<tr><th>{_e(k)}</th><td>{_e(v)}</td></tr>" for k, v in rows
    )
    return f"<table class='kv'>{trs}</table>"


# ---- individual tab renderers -------------------------------------------------

def _overview(r: dict) -> str:
    comp = r.get("comparator") or {}
    ov = (comp.get("overlap") or {}) if isinstance(comp, dict) else {}
    syn = r.get("synthesis") or {}
    res = (syn.get("result") or {}) if isinstance(syn, dict) else {}
    parts = [f"<h2>{_e(r.get('title'))}</h2>",
             f"<p class='q'>{_e(r.get('question'))}</p>"]
    parts.append(
        "<div class='banner'>This page offers <strong>greater auditability, "
        "not stronger evidence</strong>. Every number is traceable to a committed "
        "source; every absence is declared. It does not claim to supersede the "
        "peer-reviewed comparator it is measured against.</div>"
    )
    if res:
        parts.append("<h3>Headline (declared method)</h3>")
        parts.append(_kv_table([
            ("Estimand", syn.get("estimand")),
            ("Method (declared = served)", syn.get("method")),
            ("k (our search)", res.get("k")),
            ("Estimate", f"{res.get('estimate')} ({res.get('scale')})"),
            ("95% CI", f"{res.get('ci_low')} to {res.get('ci_high')}"),
            ("Prediction interval", f"{res.get('pi_low')} to {res.get('pi_high')}"),
        ]))
    return "".join(parts)


def _protocol(r: dict) -> str:
    p = r.get("protocol")
    reason = _absent(p)
    if reason:
        return _absent_block(reason)
    rows = [
        ("Protocol SHA (the registration)", p.get("sha")),
        ("Committed (UTC)", p.get("committed_utc")),
        ("Declared method", p.get("method_declared")),
    ]
    body = _kv_table(rows)
    if p.get("text"):
        body += f"<pre class='proto'>{_e(p.get('text'))}</pre>"
    return body


def _search(r: dict) -> str:
    s = r.get("search")
    reason = _absent(s)
    if reason:
        return _absent_block(reason)
    rows = [("Records retrieved", s.get("n_records")),
            ("Cache reference (committed)", s.get("cache_ref")),
            ("Run (UTC)", s.get("run_utc"))]
    body = _kv_table(rows)
    for src in s.get("sources", []) or []:
        body += f"<h4>{_e(src.get('name'))}</h4>"
        for q in src.get("queries", []) or []:
            body += f"<pre class='query'>{_e(q)}</pre>"
    return body


def _screening(r: dict) -> str:
    s = r.get("screening")
    reason = _absent(s)
    if reason:
        return _absent_block(reason)
    recs = s.get("records", []) or []
    head = "<tr><th>Record</th><th>Decision</th><th>Rule id</th><th>Rule</th></tr>"
    body = "".join(
        f"<tr><td>{_e(x.get('id'))}</td><td>{_e(x.get('decision'))}</td>"
        f"<td>{_e(x.get('rule_id'))}</td><td>{_e(x.get('rule'))}</td></tr>"
        for x in recs
    )
    n_inc = sum(1 for x in recs if x.get("decision") == "include")
    return (f"<p>{len(recs)} records screened, {n_inc} included. "
            "Every record carries a rule id.</p>"
            f"<table class='recs'>{head}{body}</table>")


def _extraction(r: dict) -> str:
    e = r.get("extraction")
    reason = _absent(e)
    if reason:
        return _absent_block(reason)
    body = ""
    hier = e.get("field_source_hierarchy")
    if hier:
        body += "<p><strong>Source hierarchy:</strong> " + _e(" &gt; ".join(hier)) + "</p>"
    for t in e.get("trials", []) or []:
        body += f"<h4>{_e(t.get('name'))} ({_e(t.get('id'))})</h4>"
        arms = t.get("arms", []) or []
        head = "<tr><th>Arm</th><th>n</th><th>events</th><th>source</th></tr>"
        rows = "".join(
            f"<tr><td>{_e(a.get('label'))}</td><td>{_e(a.get('n'))}</td>"
            f"<td>{_e(a.get('events'))}</td><td>{_e(a.get('source'))}</td></tr>"
            for a in arms
        )
        body += f"<table class='arms'>{head}{rows}</table>"
    return body or _absent_block("extraction object present but empty")


def _synthesis(r: dict) -> str:
    s = r.get("synthesis")
    reason = _absent(s)
    if reason:
        return _absent_block(reason)
    res = s.get("result") or {}
    rows = [
        ("Estimand", s.get("estimand")),
        ("Analysis population", s.get("population")),
        ("Timepoint", s.get("timepoint")),
        ("Method (declared = served)", s.get("method")),
        ("k", res.get("k")),
        ("Estimate", f"{res.get('estimate')} ({res.get('scale')})"),
        ("95% CI", f"{res.get('ci_low')} to {res.get('ci_high')}"),
        ("tau^2", res.get("tau2")),
        ("Prediction interval", f"{res.get('pi_low')} to {res.get('pi_high')}"),
    ]
    return _kv_table(rows)


def _harms(r: dict) -> str:
    h = r.get("harms")
    reason = _absent(h)
    if reason:
        return _absent_block(reason)
    body = ""
    for item in h.get("outcomes", []) or []:
        body += f"<h4>{_e(item.get('name'))}</h4>"
        body += _kv_table([
            ("Estimate", f"{item.get('estimate')} ({item.get('scale')})"),
            ("95% CI", f"{item.get('ci_low')} to {item.get('ci_high')}"),
            ("k", item.get("k")),
        ])
    return body or _absent_block("harms object present but empty")


def _comparator(r: dict) -> str:
    c = r.get("comparator")
    reason = _absent(c)
    if reason:
        return _absent_block(reason)
    ident = c.get("pmid") and f"PMID {c.get('pmid')}" or (c.get("doi") and f"DOI {c.get('doi')}")
    rows = [
        ("Published comparator", f"{c.get('name')} ({c.get('year')}), {c.get('journal')}"),
        ("Identifier", ident),
        ("Open access", c.get("open_access")),
        ("URL", c.get("url")),
    ]
    body = _kv_table(rows)
    ov = c.get("overlap") or {}
    body += "<h4>Trial-set overlap (an identical estimate on an identical set is arithmetic, not corroboration)</h4>"
    body += _kv_table([
        ("k in our review (our own search)", ov.get("ours_k")),
        ("k in the comparator", ov.get("theirs_k")),
        ("Shared trials", ov.get("shared_k")),
        ("Only in ours", ", ".join(ov.get("only_ours", []) or []) or "none"),
        ("Only in theirs", ", ".join(ov.get("only_theirs", []) or []) or "none"),
        ("Overlap method", ov.get("method")),
    ])
    return body


def _reproduction(r: dict) -> str:
    rep = r.get("reproduction")
    reason = _absent(rep)
    if reason:
        return _absent_block(reason)
    rows = [
        ("Census failures", rep.get("failures")),
        ("Re-run from protocol SHA", rep.get("protocol_sha")),
        ("Review sha256", rep.get("review_sha256")),
        ("Served-page sha256", rep.get("html_sha256")),
        ("Replayed offline from committed cache", rep.get("from_cache")),
    ]
    return _kv_table(rows)


_RENDERERS = {
    "overview": _overview, "protocol": _protocol, "search": _search,
    "screening": _screening, "extraction": _extraction, "synthesis": _synthesis,
    "harms": _harms, "comparator": _comparator, "reproduction": _reproduction,
}

_CSS = """
*{box-sizing:border-box}body{font:15px/1.5 system-ui,Segoe UI,Arial,sans-serif;margin:0;color:#12232e;background:#f7f8fa}
header{background:#12232e;color:#fff;padding:18px 22px}
header h1{margin:0;font-size:19px}header .sub{color:#9fb3c8;font-size:13px;margin-top:4px}
nav{display:flex;flex-wrap:wrap;gap:2px;background:#1d3b4d;padding:0 12px}
nav button{background:transparent;border:0;color:#cfe3f3;padding:11px 14px;cursor:pointer;font-size:13px;border-bottom:3px solid transparent}
nav button.active{color:#fff;border-bottom-color:#4ea1d3;font-weight:600}
main{max-width:960px;margin:0 auto;padding:22px}
.tab{display:none}.tab.active{display:block}
table.kv,table.recs,table.arms{border-collapse:collapse;width:100%;margin:10px 0}
table.kv th{text-align:left;width:38%;vertical-align:top;padding:6px 8px;color:#3a5a6b;background:#eef2f5;border:1px solid #dbe3e8}
table.kv td{padding:6px 8px;border:1px solid #dbe3e8}
table.recs th,table.recs td,table.arms th,table.arms td{border:1px solid #dbe3e8;padding:5px 8px;font-size:13px;text-align:left}
.absent{background:#fff4e5;border:1px solid #f0c27b;padding:12px 14px;border-radius:6px;color:#7a4b00}
.banner{background:#eaf4fb;border-left:4px solid #4ea1d3;padding:10px 14px;margin:12px 0;font-size:13.5px}
.q{font-size:16px;color:#2a4b5c}pre{background:#0f1c24;color:#d6e6f2;padding:10px;overflow:auto;border-radius:6px;font-size:12.5px}
h2{margin-top:0}
"""

_JS = """
function show(id){document.querySelectorAll('.tab').forEach(function(t){t.classList.toggle('active',t.id==='tab-'+id)});
document.querySelectorAll('nav button').forEach(function(b){b.classList.toggle('active',b.dataset.t===id)});}
document.addEventListener('DOMContentLoaded',function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);});
"""


def render_page(review: dict) -> str:
    """Pure, deterministic. No timestamps, no randomness."""
    nav = "".join(
        f'<button data-t="{tid}" onclick="show(\'{tid}\')">{_e(label)}</button>'
        for tid, label in TABS
    )
    tabs = ""
    for tid, _label in TABS:
        content = _RENDERERS[tid](review)
        tabs += f'<section class="tab" id="tab-{tid}">{content}</section>'
    title = _e(review.get("title") or review.get("slug"))
    return (
        "<!doctype html><html lang=en><head><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>{title}</title><style>{_CSS}</style></head><body>"
        f"<header><h1>{title}</h1>"
        "<div class=sub>Reproducible meta-analysis harness &mdash; auditability, not authority</div></header>"
        f"<nav>{nav}</nav><main>{tabs}</main>"
        f"<script>{_JS}</script></body></html>"
    )
