"""Which of the comparator's analyses is OURS, and who is in it (V1.0.1, metformin-PCOS review).

Sharpe 2019 (Cochrane CD013505) reports OR 2.64 (1.85-3.75) for ovulation -- Comparison 1, metformin vs placebo or
no treatment. Our question is metformin ADDED to clomifene. The closer analysis is 2.4 (metformin plus clomiphene
versus clomiphene alone): OR 1.65 (1.35-2.03), 21 studies, 1,568 women, whose 'clomiphene alone' control is broader
than our placebo requirement (harness/same_question.py records that as a CONTROL difference). The protocol's 2.64 was
therefore the wrong benchmark: it is kept, labelled WRONG_COMPARISON, and replaced by the governing analysis.

The governing analysis' membership is read from its forest plot: 21 rows, whose group totals must equal the stated
women (789 + 779 = 1,568) and whose count must equal the stated studies. The plot image is Cochrane's and is not held
(no open licence); its URL, sha256 and reader are recorded, and only the transcribed numbers are served. A row bound to
one of our pooled trials must carry the SAME counts as our served row, or the file is refused. A row whose counts the
trial's own report contradicts is COMPARATOR_ROW_UNRECONCILED and is never copied into anything (Legro 2007: 108/209
vs 106/209 in the plot; 'subjects who ovulated' 174 vs 157 in the paper).

cache/<slug>/comparator_analysis.json; every quote is located in the held comparator text.
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path
from typing import Optional


class AnalysisRefused(ValueError):
    pass


def _norm(s):
    # REV-R2 (codex review, reproduced): '<[^>]+>' also removed clinical text between a less-than and a greater-than
    # sign ('aged <18 years were excluded; those >65'), so a materially different quote could be "located"
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"</?[A-Za-z!?][^<>]*>", " ", str(s or "")))).strip()


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "cache" / slug / "comparator_analysis.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    held = {}

    def locate(q):
        ref = q["document_ref"]
        held.setdefault(ref, _norm((Path(root) / ref).read_text(encoding="utf-8")))
        if len(_norm(q["quote"])) < 10 or _norm(q["quote"]) not in held[ref]:
            raise AnalysisRefused(f"{slug}: quote not located in {ref}: {q['quote'][:60]}")

    for part in ("governing", "protocol_benchmark"):
        if doc.get(part):
            locate(doc[part])
    # V1.0.1 (NOAC-AF review): a comparator on the SAME trials with another model (COMBINE AF: IPD, stratified Cox with
    # random effects, 32-month censoring) -- its narrower interval is the model's, never our error
    # V1.0.1 (PCSK9 review): the comparator's SCOPE in its own words, so a larger set is never read as our omissions
    for part in ("method_difference", "scope"):
        for q in (doc.get(part) or {}).get("quotes") or []:
            locate(q)
    mem = doc.get("membership")
    if mem:
        locate(mem["figure"]["caption"])
        rows = mem["rows"]
        g = doc["governing"]
        if len(rows) != g["k"]:
            raise AnalysisRefused(f"{slug}: {len(rows)} figure rows, the governing analysis states {g['k']} studies")
        n = sum(r["counts"][1] + r["counts"][3] for r in rows)
        if n != g["n"]:
            raise AnalysisRefused(f"{slug}: figure rows total {n} participants, the governing analysis states {g['n']}")
        for r in rows:
            a, n1, c, n2 = r["counts"]
            if not (0 <= a <= n1 and 0 <= c <= n2):
                raise AnalysisRefused(f"{slug}: row {r['label']} has impossible counts {r['counts']}")
        fig = mem["figure"]
        if fig.get("document_ref"):
            # V1.0.1 (semaglutide-obesity review): a HELD figure image is pinned by its bytes
            import hashlib
            if hashlib.sha256((Path(root) / fig["document_ref"]).read_bytes()).hexdigest() != fig["sha256"]:
                raise AnalysisRefused(f"{slug}: figure bytes do not match the recorded sha256")
        bound = [r.get("panel_row") for r in rows]
        if any(bound):
            # each plot row names the comparator panel row (its located table row) it is; all or none, never twice
            pp = Path(root) / "cache" / slug / "comparators.json"
            panel = json.loads(pp.read_text(encoding="utf-8")) if pp.exists() else []
            ids = {m["family_id"] for c in panel for m in c.get("trial_set") or []}
            if not all(bound) or len(set(bound)) != len(bound) or not set(bound) <= ids:
                raise AnalysisRefused(f"{slug}: every plot row must name a distinct row of the comparator panel's trial set")
    return doc


def weight_concentration(rows: list, scale: str) -> Optional[dict]:
    """V1.0.1 (semaglutide-obesity review): how much of the comparator's inverse-variance weight one trial carries.
    Log OR / log RR from each row's counts; 0.5 is added to every cell of a row with a zero cell (a row with no events in
    either arm carries no information and is left out, named). SELECT carrying 97.44% of Stefanou 2024's MACE weight
    means agreement with that pool is agreement with SELECT, not 7-trial corroboration."""
    if scale not in ("OR", "RR") or not rows:
        return None
    import math
    w, eff, dropped = {}, {}, []
    for r in rows:
        a, n1, c, n2 = r["counts"]
        if a == 0 and c == 0:
            dropped.append(r["label"])
            continue
        b, d = n1 - a, n2 - c
        if min(a, b, c, d) == 0:
            a, b, c, d = a + .5, b + .5, c + .5, d + .5
            n1, n2 = n1 + 1, n2 + 1
        if scale == "OR":
            y, v = math.log(a * d / (b * c)), 1 / a + 1 / b + 1 / c + 1 / d
        else:
            y, v = math.log((a / n1) / (c / n2)), 1 / a - 1 / n1 + 1 / c - 1 / n2
        w[r["label"]], eff[r["label"]] = 1 / v, y
    if not w:
        return None
    tot = sum(w.values())
    top = max(w, key=w.get)
    ra = next(r for r in rows if r["label"] == top)["counts"]
    crude = ((ra[0] / (ra[1] - ra[0])) / (ra[2] / (ra[3] - ra[2])) if scale == "OR" else (ra[0] / ra[1]) / (ra[2] / ra[3]))         if min(ra[0], ra[2], ra[1] - ra[0], ra[3] - ra[2]) > 0 else None
    return {"scale": scale, "top": top, "top_share": round(100 * w[top] / tot, 2), "top_crude": round(crude, 4) if crude else None,
            "shares": {k: round(100 * v / tot, 2) for k, v in w.items()}, "no_events_left_out": dropped, "k": len(rows)}


def assess(doc: Optional[dict], review: dict) -> Optional[dict]:
    if not doc:
        return None
    prim = next((o for o in review.get("outcomes") or [] if o.get("primary")), {})
    ours = {str(t.get("label")): t for t in prim.get("trials") or []}
    out = {"outcome": doc["outcome"], "governing": doc.get("governing"), "protocol_benchmark": doc.get("protocol_benchmark"),
           **({"method_difference": doc["method_difference"]} if doc.get("method_difference") else {}),
           **({"scope": doc["scope"]} if doc.get("scope") else {})}
    mem = doc.get("membership")
    if mem:
        members = []
        for r in mem["rows"]:
            m = {"label": r["label"], "counts": r["counts"]}
            flag = next((f for f in doc.get("row_flags") or [] if f["row"] == r["label"]), None)
            if r.get("report_pmid") and flag and flag.get("state") == "COMPARATOR_ROW_UNRECONCILED":
                # REV-R2: an unreconciled row is never copied into anything, so it never counts as shared inputs
                raise AnalysisRefused(f"row {r['label']}: COMPARATOR_ROW_UNRECONCILED rows are never bound to our pool")
            if r.get("report_pmid"):
                t = ours.get(str(r["report_pmid"]))
                if t is None:
                    raise AnalysisRefused(f"row {r['label']}: PMID {r['report_pmid']} is not a row of our served pool")
                mine = [t.get("ai"), t.get("n1i"), t.get("ci"), t.get("n2i")]
                if mine != r["counts"]:
                    raise AnalysisRefused(f"row {r['label']}: comparator counts {r['counts']} differ from our served {mine}")
                m.update(report_pmid=str(r["report_pmid"]), inputs="SAME_COUNTS")
            if flag:
                m["flag"] = flag
            members.append(m)
        for m, r in zip(members, mem["rows"]):
            if r.get("panel_row"):
                m["panel_row"] = r["panel_row"]
        out["membership"] = {"figure": mem["figure"], "members": members, "endpoint": doc["outcome"],
                             "endpoint_label": mem.get("endpoint_label") or (doc.get("governing") or {}).get("analysis"),
                             "shared_same_counts": [m["label"] for m in members if m.get("inputs") == "SAME_COUNTS"],
                             "weight_concentration": weight_concentration(mem["rows"], (doc.get("governing") or {}).get("scale"))}
    out["row_flags"] = doc.get("row_flags") or []
    return out


def apply_to_reported(reported: list, a: Optional[dict]) -> list:
    """Our outcome's comparator row becomes the GOVERNING analysis; the protocol's benchmark is kept beside it."""
    if not a or not a.get("governing") or not a.get("protocol_benchmark"):
        return reported
    g, b = a["governing"], a["protocol_benchmark"]
    row = {"outcome": a["outcome"], "estimate": g["estimate"], "scale": g["scale"], "ci_low": g["ci_low"],
           "ci_high": g["ci_high"], "analysis": g["analysis"], "source": g["quote"],
           "replaces_protocol_benchmark": {k: b[k] for k in ("analysis", "label", "estimate", "ci_low", "ci_high", "state", "why")}}
    return [row] + [r for r in reported or [] if str(r.get("outcome")) != a["outcome"]]


def render(a: Optional[dict]) -> str:
    if not a:
        return ""
    e = lambda s: _html.escape(str(s), quote=True)  # noqa: E731
    g, b = a.get("governing"), a.get("protocol_benchmark")
    parts = []
    sc = a.get("scope")
    if sc:
        parts.append("<p><strong>Scope, in the comparator's words:</strong> "
                     + " ".join(f"&ldquo;{e(q['quote'])}&rdquo;" for q in sc["quotes"]) + f" {e(sc['reading'])}</p>")
    md = a.get("method_difference")
    if md:
        parts.append(f"<p><strong>{e(md.get('heading') or 'Same trials, different model')}:</strong> "
                     + " ".join(f"&ldquo;{e(q['quote'])}&rdquo;" for q in md["quotes"]) + f" {e(md['reading'])}</p>")
    if g and b:
        parts.append(f"<p><strong>Governing comparator analysis:</strong> {e(g['analysis'])} &mdash; {e(g['label'])}: {e(g['scale'])} "
                     f"{e(g['estimate'])} ({e(g['ci_low'])} to {e(g['ci_high'])}), {e(g['k'])} studies, {e(g['n'])} participants. "
                     f"<code>{e(b['state'])}</code>: the protocol benchmarked {e(b['analysis'])} ({e(b['label'])}, {e(b['estimate'])}, "
                     f"{e(b['ci_low'])} to {e(b['ci_high'])}) &mdash; {e(b['why'])}.</p>")
    elif g:
        parts.append(f"<p><strong>Comparator analysis for our outcome:</strong> {e(g['analysis'])} &mdash; {e(g['label'])}: "
                     f"{e(g['scale'])} {e(g['estimate'])} ({e(g['ci_low'])} to {e(g['ci_high'])}), {e(g['k'])} studies, "
                     f"{e(g['n'])} participants.</p>")
    m = a.get("membership")
    if m:
        f = m["figure"]
        held = (f"held as {e(f['document_ref'])} ({e(f.get('licence'))})" if f.get("document_ref")
                else f"not held: {e(f['why_not_held'])}")
        parts.append(f"<p>Membership of {e((g or {}).get('analysis'))}: {e(len(m['members']))} rows read from its forest plot "
                     f"({e(f['caption']['quote'])}; {e(f['url'])}, sha256 {e(f['sha256'][:16])}&hellip;, {held}; read by "
                     f"{e(f['read_by'])}). Shared with our pool, with the same counts: "
                     f"{e(', '.join(m['shared_same_counts']) or 'none')}.</p>")
        wc = m.get("weight_concentration")
        if wc:
            parts.append(f"<p><strong>Weight concentration:</strong> {e(wc['top'])} carries {e(wc['top_share'])}% of the "
                         f"comparator's inverse-variance weight (log {e(wc['scale'])} from the plotted counts; 0.5 added to "
                         f"rows with a zero cell)"
                         + (f"; its own crude {e(wc['scale'])} is {e(wc['top_crude'])}" if wc.get("top_crude") else "")
                         + ". " + (f"The pooled result is close to {e(wc['top'])} alone, so agreement with it is agreement "
                                   f"with one trial, not {e(wc['k'])}-trial corroboration." if wc["top_share"] >= 50 else
                                   "No single trial carries most of the weight.")
                         + (f" Rows with no events in either arm carry no weight: {e(', '.join(wc['no_events_left_out']))}."
                            if wc["no_events_left_out"] else "") + "</p>")
    for fl in a.get("row_flags") or []:
        parts.append(f"<p><code>{e(fl['state'])}</code> {e(fl['row'])}: the plot prints {e(fl['printed'])}; "
                     f"{e(fl['source_says'])} ({e(fl['source_state'])}, {e(fl.get('reported_by'))}). {e(fl['rule'])}.</p>")
    return "<div class='comparator-analysis'><h5>Which comparator analysis answers our question</h5>" + "".join(parts) + "</div>"
