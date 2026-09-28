"""WRITTEN vs EXECUTABLE eligibility (V1.0.1, semaglutide-weight review).

The weight topic's screen excluded any record mentioning 'knee osteoarthritis' or 'heart failure', but the protocol's
eligibility prose never says so: STEP 9 (68-week once-weekly semaglutide 2.4 mg vs placebo in obesity with knee
osteoarthritis, body weight among its principal outcomes) would have been excluded by a keyword no written rule
contains. Every executable exclusion term (topic include: population_none, intervention_none, design_none,
comparator_none) must therefore trace to the registered protocol text:

  TRACED_LITERAL     the protocol prints the term itself
  TRACED_BY_CLAUSE   registry/rule_trace/<slug>.json names the protocol clause the term implements, quoted and located
                     in the protocol ('liraglutide' -> "a different GLP-1 agonist")
  UNTRACED           neither

A topic with a trace file ENFORCES it: an UNTRACED term is flagged and NOT applied -- it can no longer exclude, and a
record that would have been included but mentions it is NEEDS_ADJUDICATION (neither included nor excluded by a keyword
no written rule contains). A topic without a trace file is reported (its untraced terms listed on the page) and still
applies its terms: enforcing there would move screening decisions nobody has adjudicated.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path
from typing import Optional

KEYS = ("population_none", "intervention_none", "design_none", "comparator_none")
ADJUDICATE = "adjudicate"
RULE = "X-UNTRACED"


class TraceRefused(ValueError):
    pass


def _norm(s) -> str:
    return re.sub(r"\s+", " ", str(s or "").replace("’", "'")).strip().lower()


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "registry" / "rule_trace" / f"{slug}.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    prot = _norm((Path(root) / "protocols" / f"{slug}.md").read_text(encoding="utf-8"))
    for term, t in (doc.get("terms") or {}).items():
        q = _norm(t.get("protocol_quote"))
        if len(q) < 8 or q not in prot:
            raise TraceRefused(f"{slug}: trace for {term!r} quotes text not in protocols/{slug}.md: {t.get('protocol_quote')!r}")
        if not t.get("why"):
            raise TraceRefused(f"{slug}: trace for {term!r} says nothing about how the clause covers the term")
    return doc


def trace(root, slug, include: dict) -> dict:
    p = Path(root) / "protocols" / f"{slug}.md"
    prot = _norm(p.read_text(encoding="utf-8")) if p.exists() else ""
    doc = load(root, slug)
    by = (doc or {}).get("terms") or {}
    rows = []
    for key in KEYS:
        for term in (include or {}).get(key) or []:
            if _norm(term) and _norm(term) in prot:
                rows.append({"key": key, "term": term, "state": "TRACED_LITERAL"})
            elif term in by:
                rows.append({"key": key, "term": term, "state": "TRACED_BY_CLAUSE", "protocol_quote": by[term]["protocol_quote"],
                             "why": by[term]["why"]})
            else:
                rows.append({"key": key, "term": term, "state": "UNTRACED"})
    return {"enforced": doc is not None, "rows": rows,
            "untraced": [r["term"] for r in rows if r["state"] == "UNTRACED"]}


def enforce(root, config: dict) -> tuple:
    """(config with UNTRACED terms removed from every exclusion list, [untraced terms]) for an enforced topic; the
    config unchanged and [] otherwise."""
    slug = config.get("slug")
    inc = dict(config.get("include") or {})
    t = trace(root, slug, inc)
    if not t["enforced"] or not t["untraced"]:
        return config, []
    for key in KEYS:
        if inc.get(key):
            inc[key] = [x for x in inc[key] if x not in t["untraced"]]
    return dict(config, include=inc), list(t["untraced"])


def render(t: Optional[dict], adjudicate_rows: list = ()) -> str:
    if not t or not t.get("rows"):
        return ""
    e = lambda s: _html.escape(str(s), quote=True)  # noqa: E731
    n = {s: sum(r["state"] == s for r in t["rows"]) for s in ("TRACED_LITERAL", "TRACED_BY_CLAUSE", "UNTRACED")}
    head = (f"<p><strong>Written vs executable exclusions.</strong> {len(t['rows'])} executable exclusion terms: "
            f"{n['TRACED_LITERAL']} printed in the protocol, {n['TRACED_BY_CLAUSE']} traced to a protocol clause, "
            f"<strong>{n['UNTRACED']} not traced to any protocol text</strong>. ")
    if t["enforced"]:
        head += ("Untraced terms are flagged and NOT applied: they exclude nothing, and a record that would otherwise "
                 "be included but mentions one is <code>NEEDS_ADJUDICATION</code>.</p>")
    else:
        head += ("This topic has no trace record yet, so its terms are still applied; the untraced ones below are "
                 "exclusions no written rule states.</p>")
    un = "".join(f"<li><code>{e(r['key'])}</code> &lsquo;{e(r['term'])}&rsquo;</li>" for r in t["rows"] if r["state"] == "UNTRACED")
    cl = "".join(f"<li>&lsquo;{e(r['term'])}&rsquo; &larr; &ldquo;{e(r['protocol_quote'])}&rdquo; ({e(r['why'])})</li>"
                 for r in t["rows"] if r["state"] == "TRACED_BY_CLAUSE")
    adj = "".join(f"<li>{e(d['id'])}: {e(d['reason'])}</li>" for d in adjudicate_rows)
    return ("<div class='rule-trace'>" + head + (f"<p>Untraced:</p><ul>{un}</ul>" if un else "")
            + (f"<details><summary>Traced by clause</summary><ul>{cl}</ul></details>" if cl else "")
            + (f"<p>Needs adjudication:</p><ul>{adj}</ul>" if adj else "") + "</div>")
