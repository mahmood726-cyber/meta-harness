"""The RapidMeta-style transparent tabs that were missing from the review page (2026-10-08, pva lane): Included studies,
Data extraction, Analysis, Changes & signatures, plus the additions to Protocol, Search, Risk of bias & GRADE, Results,
Comparison and Reproduce. PRESENTATION ONLY: every value shown is read from the review object or from a committed
registry file named beside it; nothing here computes a pooled number, and no number is written by hand.

A required element with nothing to show renders a stated reason, never an empty panel:
    <p class="tab-reason" data-element="NAME">...why, with the file it was looked for in...</p>
tests/test_review_tabs.py plants an empty tab and requires the reason; scripts/review_tab_inventory.py measures every
served page against the same contract.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPO_URL = "https://github.com/mahmood726-cyber/meta-harness"
TAB_CONTRACT = "rapidmeta-v1"


def _e(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def _reason(element: str, text: str) -> str:
    return f'<p class="tab-reason" data-element="{_e(element)}"><strong>Not shown -- </strong>{text}</p>'


def _fmt(x: Any) -> str:
    if isinstance(x, bool) or x is None:
        return _e(x)
    if isinstance(x, float):
        return f"{x:.4g}"
    return _e(x)


@lru_cache(maxsize=None)
def _registry(name: str) -> dict:
    p = ROOT / "registry" / name
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _src(path: str) -> str:
    """A committed file, linked on the public repository (the page cannot know its own release commit, so the link is to
    the default branch and the text names the file; docs/audit/ pins every link to the release commit)."""
    return f"<a href='{REPO_URL}/blob/main/{_e(path)}'><code>{_e(path)}</code></a>"


# ------------------------------------------------------------------------------------------- status (active/abandoned)
def topic_status(slug: str) -> dict:
    """ACTIVE, or ABANDONED_BY_DECISION as recorded in registry/g1_abandoned.json (rule, decision, rank and reason)."""
    try:
        reg = _registry("g1_abandoned.json")
    except (OSError, ValueError):
        return {"state": "UNKNOWN", "why": "registry/g1_abandoned.json could not be read"}
    for t in reg.get("topics") or []:
        if t.get("slug") == slug:
            d = t.get("decision") or reg.get("decision") or {}
            return {"state": t.get("state"), "rank": t.get("rank"), "reason": t.get("reason"), "rule_id": reg.get("rule_id"),
                    "rule_commit": reg.get("rule_commit"), "by": d.get("by"), "words": d.get("words"), "date": d.get("date"),
                    "status_text": reg.get("status_of_abandoned")}
    return {"state": "ACTIVE", "rule_id": reg.get("rule_id")}


def status_banner(slug: str) -> str:
    st = topic_status(slug)
    if st["state"] == "ABANDONED_BY_DECISION":
        return ("<div class='topic-status abandoned' data-topic-status='ABANDONED_BY_DECISION'><strong>ABANDONED BY DECISION"
                f"</strong> ({_e(st['rule_id'])}, rank {_e(st['rank'])}): {_e(st['reason'])}. Decided by {_e(st['by'])} on "
                f"{_e(st['date'])} (&ldquo;{_e(st['words'])}&rdquo;). {_e(st['status_text'])}. "
                f"Source: {_src('registry/g1_abandoned.json')}; list: <a href='../../g1/index.html#abandoned'>/g1/#abandoned</a>.</div>")
    if st["state"] == "ACTIVE":
        return ("<div class='topic-status active' data-topic-status='ACTIVE'><strong>ACTIVE topic</strong> "
                f"(not on the {_e(st.get('rule_id'))} abandonment list, {_src('registry/g1_abandoned.json')}).</div>")
    return f"<div class='topic-status' data-topic-status='UNKNOWN'>{_e(st['why'])}</div>"


# ------------------------------------------------------------------------------------------------------------ Protocol
_AMEND = re.compile(r"^#{1,4}\s*(Amendment[^\n]*?(20\d\d-\d\d-\d\d)[^\n]*)$", re.M)


def protocol_additions(r: dict) -> str:
    p = r.get("protocol") or {}
    text = p.get("text") or ""
    out = ["<h4 id='protocol-amendments'>Amendments (dated sections of the committed protocol text)</h4>"]
    am = _AMEND.findall(text)
    if am:
        out.append("<table class='recs'><tr><th>Date</th><th>Amendment heading (verbatim)</th></tr>"
                   + "".join(f"<tr><td>{_e(d)}</td><td>{_e(h)}</td></tr>" for h, d in am) + "</table>")
    else:
        out.append(_reason("amendments with dates",
                           f"the committed protocol text (sha <code>{_e(p.get('sha'))}</code>, committed {_e(p.get('committed_utc'))}) "
                           "contains no dated <em>Amendment</em> section, so no amendment has been registered for this topic. "
                           "Corrections after registration appear as signed notices in the Changes &amp; signatures tab."))
    out.append(decisions_table())
    return "".join(out)


def decisions_table() -> str:
    try:
        reg = _registry("g1_decisions.json")
    except (OSError, ValueError):
        return _reason("decisions D1-D12", "registry/g1_decisions.json could not be read at build time.")
    rows = []
    for d in reg.get("decisions") or []:
        rat = d.get("ratified") or {}
        rows.append(f"<tr><td><code>{_e(d.get('id'))}</code></td><td>{_e(d.get('decided'))}</td><td>{_e(d.get('by'))}</td>"
                    f"<td>{_e(d.get('rule'))}</td><td>{_e(d.get('applied_in'))}</td>"
                    f"<td>{_e(rat.get('state') or (('ratified ' + str(rat.get('date'))) if rat.get('date') else '--'))}</td></tr>")
    return ("<h4 id='decisions'>Review decisions in force at this build (the typed G1 decisions)</h4>"
            f"<p>{_e(reg.get('rule'))} Rendered from {_src('registry/g1_decisions.json')}; the current list is on "
            "<a href='../../g1/index.html#decisions'>/g1/#decisions</a>.</p>"
            "<table class='recs'><tr><th>Decision</th><th>Decided</th><th>By</th><th>Rule</th><th>Applied in</th>"
            f"<th>Ratification</th></tr>{''.join(rows)}</table>")


# -------------------------------------------------------------------------------------------------------------- Search
def search_additions(r: dict) -> str:
    s = r.get("search") or {}
    if not any(src.get("queries") for src in s.get("sources") or [] if isinstance(src, dict)):
        rc = s.get("retrieval_class")
        cls = rc.get("class") if isinstance(rc, dict) else rc
        return _reason("queries", f"no query string is recorded in this review's search object (retrieval class "
                                  f"<code>{_e(cls)}</code>); the retrieval sources above are what ran. See the label "
                                  "above for what this retrieval class does and does not claim.")
    return ""


# ---------------------------------------------------------------------------------------------------- Included studies
def _ids(t: dict) -> tuple[str | None, str | None]:
    s = json.dumps({k: t.get(k) for k in ("id", "label", "pmid", "nct", "trial_family_id", "effect_source_id")})
    pm = re.search(r"PMID[ :]*(\d{6,9})", s) or re.search(r'"pmid": "?(\d{6,9})', s)
    nct = re.search(r"NCT\d{8}", s)
    return (pm.group(1) if pm else None), (nct.group(0) if nct else None)


def _pmid_link(pm: str | None) -> str:
    return f"<a href='https://pubmed.ncbi.nlm.nih.gov/{_e(pm)}/'>PMID {_e(pm)}</a>" if pm else "--"


def _nct_link(n: str | None) -> str:
    return f"<a href='https://clinicaltrials.gov/study/{_e(n)}'>{_e(n)}</a>" if n else "--"


def included_tab(r: dict) -> str:
    by: dict[str, dict] = {}
    for o in r.get("outcomes") or []:
        for t in o.get("trials") or []:
            key = str(t.get("id") or t.get("label"))
            e = by.setdefault(key, {"t": t, "outcomes": []})
            e["outcomes"].append(o.get("name"))
    absent: dict[str, list] = {}
    for o in r.get("outcomes") or []:
        for t in o.get("declared_absent_trials") or []:
            absent.setdefault(str(t.get("id") or t.get("label")), []).append((o.get("name"), t.get("state") or t.get("reason_code") or t.get("code")))
    if not by and not absent:
        return _reason("included trials", "no outcome of this review has a pooled trial or a declared-absent eligible trial.")
    rows = []
    for key, e in sorted(by.items(), key=lambda kv: str(kv[1]["t"].get("label"))):
        pm, nct = _ids(e["t"])
        rows.append(f"<tr><td>{_e(e['t'].get('label'))}</td><td>{_pmid_link(pm)}</td><td>{_nct_link(nct)}</td>"
                    f"<td>{_e('; '.join(dict.fromkeys(str(x) for x in e['outcomes'])))}</td></tr>")
    out = ("<p>Every trial row that enters a pooled outcome of this review, with its identifiers as recorded on the row "
           "(PMID from the row id or label; NCT from the row or its trial family). Identifiers link to PubMed and "
           "ClinicalTrials.gov.</p><table class='recs' id='included-trials'><tr><th>Trial</th><th>PMID</th><th>Registry</th>"
           f"<th>Pooled in</th></tr>{''.join(rows)}</table>")
    if absent:
        arows = "".join(f"<tr><td>{_e(k)}</td><td>{_e('; '.join(f'{n}: {s}' for n, s in v))}</td></tr>"
                        for k, v in sorted(absent.items()))
        out += ("<h4>Eligible but not pooled (declared absent), by outcome</h4><table class='recs'><tr><th>Trial</th>"
                f"<th>Outcome: state</th></tr>{arows}</table><p class='note'>The family-level ledger, with every eligible "
                "trial family and what is missing, is in the Screening tab.</p>")
    return out


# ----------------------------------------------------------------------------------------------------- Data extraction
def _gated(o: dict) -> str | None:
    """Why an outcome may not get a new numerical surface (the gate's rules), or None."""
    from . import harms
    res = o.get("result") or {}
    if harms.synthesis_incomplete(o):
        return "its harm-extraction ledger is incomplete, so its numbers are served only as the gated ledger in the Harms tab"
    if res.get("suppressed_incompatible"):
        return "its pool is suppressed as incompatible (see the Results tab)"
    return None


def _value(t: dict) -> str:
    if t.get("effect") is not None:
        ci = f" ({_fmt(t.get('ci_low'))} to {_fmt(t.get('ci_high'))})" if t.get("ci_low") is not None else ""
        return f"{_e(t.get('scale') or '')} {_fmt(t.get('effect'))}{ci}".strip()
    if t.get("ai") is not None:
        return f"{_fmt(t.get('ai'))}/{_fmt(t.get('n1i'))} vs {_fmt(t.get('ci'))}/{_fmt(t.get('n2i'))}"
    if t.get("mean1") is not None:
        return (f"{_fmt(t.get('mean1'))} (SD {_fmt(t.get('sd1'))}, n {_fmt(t.get('n1'))}) vs "
                f"{_fmt(t.get('mean2'))} (SD {_fmt(t.get('sd2'))}, n {_fmt(t.get('n2'))})")
    return "--"


def passage(t: dict) -> str:
    """The text a pooled number was read from: the bound result span, else the row's own source text."""
    return str(t.get("endpoint_result_span") or t.get("source") or "")


def passage_sha256(t: dict) -> str | None:
    p = passage(t)
    return hashlib.sha256(p.encode("utf-8")).hexdigest() if p else None


def extraction_rows(r: dict) -> list[dict]:
    """One row per pooled number (outcome x trial) that may be shown; the audit pack samples these rows."""
    from .provenance_class import recorded_reads, served_class
    reads = recorded_reads(str(ROOT))
    slug = r.get("slug") or ""
    rows = []
    for oi, o in enumerate(r.get("outcomes") or []):
        if _gated(o):
            continue
        for ti, t in enumerate(o.get("trials") or []):
            cls, why, recs = served_class(t, slug, o.get("name"), str(ROOT), reads)
            rows.append({"anchor": f"x{oi}-{ti}", "outcome": o.get("name"), "trial": t.get("label"), "id": t.get("id"),
                         "value": _value(t), "provenance": t.get("provenance"), "class": cls, "class_why": why,
                         "verified": t.get("verified"), "passage": passage(t), "passage_sha256": passage_sha256(t),
                         "records": recs})
    return rows


def _rec_link(rid: str) -> str:
    for base in ("registry/model_calls", "evidence/model_calls"):
        hits = list((ROOT / base).glob(f"**/{rid}.json"))
        if hits:
            return _src(hits[0].relative_to(ROOT).as_posix())
    return f"<code>{_e(rid)}</code> (not found in the tree)"


def extraction_tab(r: dict) -> str:
    rows = extraction_rows(r)
    gated = [(o.get("name"), _gated(o)) for o in r.get("outcomes") or [] if _gated(o)]
    out = ["<p>Every pooled number on this page, with the passage it was read from, the sha256 of that passage "
           "(UTF-8; recompute it from the text shown), its provenance type as recorded on the row, and its provenance "
           "class as the provenance-census gate computes it (<code>harness/provenance_class.py</code>): "
           "<strong>EXTRACTOR</strong> = a deterministic regex/typed extractor over a held source; "
           "<strong>RECORDED_MODEL_CALL</strong> = a recorded model call that replays offline (record ids linked); "
           "<strong>HAND_ENTERED</strong> = entered outside the harness, bound to a held span, on the burn-down list "
           f"{_src('registry/provenance_hand_entered.json')}; <strong>UNTRACED</strong> = refused by the gate.</p>"]
    if rows:
        body = []
        for x in rows:
            recs = "<br>".join(_rec_link(i) for i in x["records"]) or "--"
            ptxt = (f"<blockquote class='span'>{_e(x['passage'])}</blockquote>" if x["passage"] else
                    "<span class='tab-reason' data-element='source span'>no passage on this row</span>")
            body.append(f"<tr id='{_e(x['anchor'])}'><td>{_e(x['outcome'])}</td><td>{_e(x['trial'])}</td><td>{x['value']}</td>"
                        f"<td><code>{_e(x['provenance'])}</code><br><strong>{_e(x['class'])}</strong><br>"
                        f"<span class='muted'>{_e(x['class_why'])}</span></td><td>{_e(x['verified'])}</td>"
                        f"<td>{ptxt}<code class='digest'>sha256 {_e(x['passage_sha256'])}</code></td><td>{recs}</td></tr>")
        out.append("<table class='recs' id='extraction-rows'><tr><th>Outcome</th><th>Trial</th><th>Value</th>"
                   "<th>Provenance (type / class)</th><th>Verified</th><th>Source passage + digest</th>"
                   f"<th>Recorded call(s)</th></tr>{''.join(body)}</table>")
    else:
        why = "no outcome of this review has a pooled row that may be shown (each outcome is withheld for the reason below)"
        for el in ("source span per pooled number", "digest", "extractor or recorded call"):
            out.append(_reason(el, why + "."))
    for name, why in gated:
        out.append(_reason("gated outcome", f"{_e(name)}: {_e(why)}."))
    return "".join(out)


# --------------------------------------------------------------------------------------------------------- RoB & GRADE
def d11_status() -> str:
    try:
        d = next(x for x in _registry("g1_decisions.json").get("decisions") or [] if str(x.get("id")).startswith("D11"))
    except (OSError, ValueError, StopIteration):
        return _reason("D11 reproducible-AI sign-off", "no D11 decision is recorded in registry/g1_decisions.json.")
    return ("<h4 id='d11-signoff'>D11: reproducible-AI sign-off of RoB 2 and GRADE</h4>"
            f"<p>Decision <code>{_e(d.get('id'))}</code> ({_e(d.get('decided'))}, {_e(d.get('by'))}): {_e(d.get('rule'))}</p>"
            + _reason("D11 reproducible-AI sign-off",
                      f"status recorded with the decision: <em>{_e(d.get('applied_in'))}</em>. No recorded dual-model "
                      "sign-off exists for this topic at this build, so the judgements above are the rule-based ratings "
                      f"only. Source: {_src('registry/g1_decisions.json')}."))


# ------------------------------------------------------------------------------------------------------------ Analysis
def _forest(o: dict) -> str:
    from . import manuscript
    return manuscript.forest_for(o, label=f"Forest plot: {o.get('name')}")


def analysis_tab(r: dict) -> str:
    out = ["<p>For each outcome: the declared model (verbatim from the outcome's <code>method</code>), the forest plot "
           "drawn from the pooled rows, heterogeneity and prediction interval as computed, and the leave-one-out "
           "sensitivity. Other sensitivity analyses (risk of bias, known missing trials) are in the Risk of bias and "
           "Results tabs.</p>"]
    any_out = False
    for o in r.get("outcomes") or []:
        res = o.get("result") or {}
        out.append(f"<h4>{_e(o.get('name'))}{' (primary)' if o.get('primary') else ''}</h4>")
        g = _gated(o)
        if g:
            out.append(_reason("forest plot", f"{_e(g)}."))
            continue
        if not res.get("k"):
            out.append(_reason("forest plot", "no pooled estimate for this outcome (k = 0 or not stated); see Results."))
            continue
        any_out = True
        out.append(f"<p class='method'><strong>Model:</strong> {_e(o.get('method'))}</p>")
        fp = _forest(o)
        out.append(fp or _reason("forest plot", "no row of this outcome has a displayable effect."))
        out.append("<table class='kv'>"
                   + "".join(f"<tr><th>{_e(k)}</th><td>{_fmt(v)}</td></tr>" for k, v in (
                       ("k", res.get("k")), ("Pooled estimate", res.get("estimate")), ("95% CI", f"{_fmt(res.get('ci_low'))} to {_fmt(res.get('ci_high'))}"),
                       ("tau-squared", res.get("tau2")), ("I-squared", res.get("i2")), ("Q", res.get("Q")),
                       ("95% prediction interval", f"{_fmt(res.get('pi_low'))} to {_fmt(res.get('pi_high'))}"),
                       ("Prediction-interval note", res.get("pi_note"))) if v is not None)
                   + "</table>")
        loo = res.get("leave_one_out") or {}
        if loo.get("per_trial"):
            out.append("<p>Leave-one-out: " + _e(loo.get("note")) + "</p><table class='recs'><tr><th>Trial dropped</th>"
                       "<th>Re-pooled estimate</th></tr>"
                       + "".join(f"<tr><td>{_e(x.get('dropped'))}</td><td>{_fmt(x.get('estimate'))}</td></tr>" for x in loo["per_trial"])
                       + f"</table><p class='muted'>Range {_fmt(loo.get('min'))} to {_fmt(loo.get('max'))}; most influential: "
                       f"{_e(loo.get('most_influential'))}.</p>")
        else:
            out.append(_reason("sensitivity", "leave-one-out: " + _e(loo.get("note") or "not recorded for this outcome") + "."))
    if not any_out:
        why = ("no outcome of this review has a pooled estimate that may be shown (each is withheld for the reason given "
               "under its heading)")
        for el in ("model", "heterogeneity", "sensitivity", "HKSJ rule"):
            out.append(_reason(el, why + "."))
    return "".join(out)


# ------------------------------------------------------------------------------------------------ Results/conclusions
_CLAIM_FIELDS = (("present", "A pooled claim is made"), ("significant", "95% CI excludes the null"),
                 ("crosses_null", "95% CI crosses the null"), ("touches_null", "95% CI touches the null"),
                 ("null", "Null value on this scale"), ("direction", "Direction of the point estimate"),
                 ("state", "Claim state"), ("refusal_code", "Refusal code"), ("basis", "Basis"))


def conclusions(r: dict) -> str:
    """The conclusion as the canonical claim object states it (harness/claim.py derives it; every surface is checked
    against it by the gate). Rendered field by field: no sentence is composed here."""
    prim = next((o for o in r.get("outcomes") or [] if o.get("primary")), None)
    claim = ((prim or {}).get("result") or {}).get("claim")
    if not isinstance(claim, dict):
        return _reason("conclusions", "the primary outcome carries no canonical claim object at this build.")
    rows = "".join(f"<tr><th>{_e(lab)}</th><td>{_e(claim.get(k))}</td></tr>" for k, lab in _CLAIM_FIELDS if k in claim)
    return ("<h4 id='conclusions'>Conclusion: the canonical claim object for the primary outcome</h4>"
            "<p>The page's conclusion is this object, derived from the pooled result by <code>harness/claim.py</code>; "
            "every other sentence on the page is checked against it. Certainty is stated in the Risk of bias &amp; GRADE "
            f"tab.</p><table class='kv' id='claim-object'>{rows}</table>")


# ---------------------------------------------------------------------------------------------------------- Comparator
def comparator_additions(r: dict) -> str:
    slug = r.get("slug") or ""
    return ("<h4 id='g1-panel'>G1 panel (trial-for-trial match against the published meta-analysis)</h4>"
            f"<p>This topic's G1 row -- matched trials, open gaps and named differences -- is on the scoreboard at "
            f"<a href='../../g1/index.html#{_e(slug)}'>/g1/#{_e(slug)}</a>, built from "
            f"<code>outputs/k_gap/g1/{_e(slug)}.json</code>. It is linked, not copied, so it can update without "
            "reissuing this page's certificate.</p>")


# -------------------------------------------------------------------------------------------------- Changes/signatures
def changes_tab(r: dict) -> str:
    from . import page as P
    slug = r.get("slug") or ""
    notices = (r.get("reproduction") or {}).get("result_changes") or []
    out = []
    if notices:
        rows = []
        for n in notices:
            sig = n.get("reviewer_countersignature") or {}
            st = P.result_changes_status(n)
            rows.append(f"<tr><td>{_e(str(n.get('when_utc'))[:10])}</td><td>{_e(n.get('outcome'))}</td>"
                        f"<td>{_e('NOT APPLIED: ' + st['state'] if st else 'applied')}</td><td>{_e(sig.get('state'))}</td>"
                        f"<td>{_e(sig.get('by'))}</td><td>{_e(str(sig.get('when_utc'))[:16])}</td>"
                        f"<td><code>{_e(str(sig.get('rendered_sha256'))[:16])}</code></td></tr>")
        out.append("<p>Every result-change notice for this topic in <code>docs/result_changes.json</code>, with its "
                   "countersignature. A signature is on the bytes of the rendered notice below (its "
                   "<code>rendered_sha256</code>), not on this table.</p><table class='recs' id='notice-ledger'><tr>"
                   "<th>Notice date</th><th>Outcome</th><th>Applied?</th><th>Signature</th><th>By</th><th>When (UTC)</th>"
                   f"<th>Signed block sha256</th></tr>{''.join(rows)}</table>")
        for n in notices:
            st = P.result_changes_status(n)
            if st:
                out.append("<p class='absent' data-result-change-status='" + _e(st["state"]) + "'><strong>NOT APPLIED -- "
                           + _e(st["text"]) + "</strong> The notice below is kept as signed, for the record; the served "
                           "result does not include it.</p>")
            out.append(P.result_change_block(n))
    else:
        out.append(_reason("every committed notice", "no result-change notice for this topic in docs/result_changes.json "
                                                     "at this build: the served result has not changed since first publication."))
    try:
        rein = [x for x in _registry("result_change_reinstatements.json").get("reinstatements") or [] if x.get("slug") == slug]
    except (OSError, ValueError):
        rein = []
    if rein:
        out.append("<h4>Reinstatements</h4><table class='recs'><tr><th>Outcome</th><th>Trial</th><th>Notice</th>"
                   "<th>Reverses</th><th>Declared by</th></tr>"
                   + "".join(f"<tr><td>{_e(x.get('outcome'))}</td><td>{_e(x.get('trial'))}</td><td>{_e(x.get('notice_when_utc'))}</td>"
                             f"<td>{_e(x.get('reverses_when_utc'))}</td><td>{_e(x.get('declared_by'))}</td></tr>" for x in rein)
                   + f"</table><p class='note'>Source: {_src('registry/result_change_reinstatements.json')}.</p>")
    try:
        sw = (_registry("comparator_switch_signatures.json").get("switches") or {}).get(slug)
    except (OSError, ValueError):
        sw = None
    if sw:
        out.append("<h4>Comparator switch (signed)</h4>"
                   f"<p>{_e(sw.get('item'))}: comparator PMID {_e(sw.get('from'))} &rarr; {_e(sw.get('to'))}, "
                   f"{_e(sw.get('state'))} by {_e(sw.get('by'))} at {_e(sw.get('when_utc'))} (packet sha256 "
                   f"<code>{_e(str(sw.get('packet_sha256'))[:16])}</code>). Source: {_src('registry/comparator_switch_signatures.json')}.</p>")
    wd = [n for n in notices if (P.result_changes_status(n) or {}).get("state") == "WITHDRAWN_BY_SIGNER"]
    if not wd and not rein:
        out.append(_reason("withdrawals/reinstatements stated",
                           "no withdrawal by a signer and no reinstatement is recorded for this topic "
                           f"(docs/result_changes.json; {_src('registry/result_change_reinstatements.json')})."))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------ Reproduce
def reproduce_additions(r: dict) -> str:
    slug = r.get("slug") or ""
    out = ["<h4 id='one-command'>One-command replay</h4>"
           f"<pre>git clone {REPO_URL}.git &amp;&amp; cd meta-harness\n"
           "python -m pip install --require-hashes -r docs/offline/requirements.lock\n"
           f"python scripts/reproduce_review.py {_e(slug)}</pre>"
           "<p>The replay rebuilds this review from the committed protocol and cache, offline, and compares every "
           "digest in <a href='CERTIFICATE.json'>CERTIFICATE.json</a> and the served page bytes. The certificate's "
           "digests are listed in the Verify this page tab.</p>"]
    if (ROOT / "docs" / "reviews" / slug / "BUNDLE.json").is_file():
        out.append("<h4 id='bundle'>Evidence bundle</h4><p><a href='BUNDLE.json'>BUNDLE.json</a> (verification API: "
                   "per pooled row the source, span, endpoint, effect, decision and admission objects; check it with "
                   "<code>python docs/scripts/verify_bundle.py</code>).</p>")
    else:
        out.append("<h4 id='bundle'>Evidence bundle</h4>" + _reason(
            "bundle download",
            f"no evidence bundle has been built for this topic: <code>docs/acquisitions/{_e(slug)}/</code> holds no "
            "PubMed acquisition objects, and scripts/build_bundle.py refuses to build without them. Everything the "
            f"replay reads is in the public repository: <a href='{REPO_URL}/archive/refs/heads/main.zip'>download the "
            "repository</a> (or clone it) and run the command above."))
    return "".join(out)


# ------------------------------------------------------------------------------------------------------------ contract
# the page tab ids that carry the required RapidMeta tabs (results and reproduce kept their legacy ids)
REQUIRED_PAGE_TABS = ("protocol", "search", "screening", "included", "extraction", "riskofbias", "analysis", "outcomes",
                      "comparator", "changes", "reproduction")
_SECTION = re.compile(r'<section class="tab" id="tab-([a-z]+)"><h3 class="tabname">[^<]*</h3>(.*?)</section>(?=<section class="tab"|</main>)', re.S)


def tab_contract_problems(page_html: str, neutral: bool = False) -> list[str]:
    """The rapidmeta-v1 contract on one rendered page: every required tab present and non-empty, and a tab whose only
    content is stated reasons is still non-empty (a reason is content; silence is not)."""
    out = []
    if f"<meta name='tab-contract' content='{TAB_CONTRACT}'>" not in page_html:
        out.append("the page does not declare the tab contract")
    tabs = {m.group(1): m.group(2) for m in _SECTION.finditer(page_html)}
    need = [t for t in REQUIRED_PAGE_TABS if not (neutral and t in {"comparator", "included", "extraction", "analysis", "changes"})]
    for t in need:
        if t not in tabs:
            out.append(f"tab {t} is missing")
            continue
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", tabs[t]))).strip()
        if not text:
            out.append(f"tab {t} is empty and states no reason")
    if not neutral:
        for t in ("included", "extraction", "analysis", "changes"):
            if t in tabs and 'class="tab-reason"' not in tabs[t] and "<table" not in tabs[t] and "<svg" not in tabs[t]:
                out.append(f"tab {t} shows neither a table nor a stated reason")
    if "id='sections-heading'" not in page_html or "role','tablist'" not in page_html:
        out.append("the tab bar is not exposed as an accessible tablist under a section heading")
    return out
