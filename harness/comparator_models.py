"""Model-specific comparator tuples and the comparator's INTERNAL mismatches (V1.0.1).

A comparator meta-analysis reports its pooled result more than once: in prose, and in a forest plot that prints one
row per model. They can disagree. Ma 2022 (PMID 36176989), Figure 3A MACE, prints

    Total (fixed effect, 95% CI)    0.65 [0.56, 0.75]
    Total (random effects, 95% CI)  0.54 [0.38, 0.77]

while its prose says "RR: 0.65; 95% CI: 0.38-0.77" -- the fixed-effect point with the random-effects interval. That
is a defect of the COMPARATOR, recorded as COMPARATOR_INTERNAL_MISMATCH and kept on the page. It is never resolved
by choosing one side, and never "fixed" by moving our own result.

Input: cache/<slug>/comparator_figures.json -- a typed transcription of a figure (rows, pooled model rows, the
image's URL and sha256 at read time). It is VALIDATED arithmetically before use: arm totals must equal the row sums,
and the fixed-effect (Mantel-Haenszel) and random-effects (DerSimonian-Laird, which is what the figure reports) pools
recomputed from the transcribed rows must round to the printed values. A transcription that fails is refused.

Uses:
  - model_tuples: {model, point, ci_low, ci_high, figure, panel, figure_row}
  - internal_mismatches: a prose tuple whose point is one model's and interval another's
    (PROSE_MIXES_MODELS); a figure row whose trial year differs from the comparator's own included-trial table
    (FIGURE_ROW_YEAR_DIFFERS_FROM_TABLE)
  - outcome-level membership: the figure panel's rows bound to the comparator's included-trial table
    (surname + year; surname alone only when unique in the table, with the year difference recorded), which binds
    the panel's outcome to our primary outcome for the overlap relation
"""
from __future__ import annotations

import html as _h
import json
import math
import re
from pathlib import Path
from typing import Optional

MISMATCH = "COMPARATOR_INTERNAL_MISMATCH"
_TUPLE = re.compile(r"\bRR:?\s*(\d+\.\d+)\s*[;,]\s*95%\s*CI:?\s*(\d+\.\d+)\s*[–—-]\s*(\d+\.\d+)")


class FigureRefused(ValueError):
    pass


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "cache" / slug / "comparator_figures.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    for fig in doc.get("figures") or []:
        validate(fig)
    return doc


def _pools(rows):
    num = sum(r["events_int"] * r["n_ctl"] / (r["n_int"] + r["n_ctl"]) for r in rows)
    den = sum(r["events_ctl"] * r["n_int"] / (r["n_int"] + r["n_ctl"]) for r in rows)
    ys, ws = [], []
    for r in rows:
        a, n1, c, n0 = r["events_int"], r["n_int"], r["events_ctl"], r["n_ctl"]
        if 0 in (a, c):
            a, c, n1, n0 = a + .5, c + .5, n1 + 1, n0 + 1
        ys.append(math.log((a / n1) / (c / n0)))
        ws.append(1 / (1 / a - 1 / n1 + 1 / c - 1 / n0))
    fe = sum(w * y for w, y in zip(ws, ys)) / sum(ws)
    q = sum(w * (y - fe) ** 2 for w, y in zip(ws, ys))
    cc = sum(ws) - sum(w * w for w in ws) / sum(ws)
    tau2 = max(0.0, (q - (len(ys) - 1)) / cc) if cc > 0 else 0.0
    wr = [1 / (1 / w + tau2) for w in ws]
    re_ = sum(w * y for w, y in zip(wr, ys)) / sum(wr)
    se = math.sqrt(1 / sum(wr))
    return {"fixed": num / den, "random": math.exp(re_),
            "random_ci": (math.exp(re_ - 1.959964 * se), math.exp(re_ + 1.959964 * se)), "tau2": tau2}


def validate(fig: dict) -> None:
    d = fig.get("document") or {}
    if not re.fullmatch(r"[0-9a-f]{64}", str(d.get("sha256") or "")) or not d.get("url") or not d.get("read_utc"):
        raise FigureRefused("FIGURE: document url / sha256 / read time missing")
    rows = fig.get("rows") or []
    if not rows or not fig.get("pooled"):
        raise FigureRefused("FIGURE: no rows or no pooled model rows")
    for r in rows:
        if not (r["ci_low"] <= r["rr"] <= r["ci_high"]):
            raise FigureRefused(f"FIGURE: row {r['row_label']} point outside its interval")
    pooled = {p["model"].split()[0]: p for p in fig["pooled"]}
    fe = pooled.get("fixed")
    if fe and fe.get("n_int") is not None:
        if fe["n_int"] != sum(r["n_int"] for r in rows) or fe["n_ctl"] != sum(r["n_ctl"] for r in rows):
            raise FigureRefused("FIGURE: arm totals do not equal the row sums (transcription error)")
    if all(k in rows[0] for k in ("events_int", "n_int", "events_ctl", "n_ctl")) and "risk ratio" in str(fig.get("measure", "")).lower():
        got = _pools(rows)
        if fe and round(got["fixed"], 2) != fe["point"]:
            raise FigureRefused(f"FIGURE: Mantel-Haenszel pool of the transcribed rows is {got['fixed']:.4f}, printed {fe['point']}")
        rnd = pooled.get("random")
        if rnd and (round(got["random"], 2) != rnd["point"] or round(got["random_ci"][0], 2) != rnd["ci_low"]
                    or round(got["random_ci"][1], 2) != rnd["ci_high"]):
            raise FigureRefused("FIGURE: DerSimonian-Laird pool of the transcribed rows does not reproduce the printed "
                                f"random-effects row ({got['random']:.4f} {got['random_ci'][0]:.4f}-{got['random_ci'][1]:.4f})")
        fig["_recomputed"] = {"fixed_MH": round(got["fixed"], 4), "random_DL": round(got["random"], 4),
                              "random_DL_ci": [round(x, 4) for x in got["random_ci"]], "tau2_DL": round(got["tau2"], 4)}


def _sentence(text: str, at: int) -> str:
    lo = max(text.rfind(". ", 0, at) + 2, 0)
    hi = text.find(". ", at)
    return text[lo: hi + 1 if hi != -1 else len(text)].strip()


def prose_mismatches(text: str, fig: dict) -> list:
    models = fig["pooled"]
    out = []
    for m in _TUPLE.finditer(text or ""):
        p, lo, hi = float(m.group(1)), float(m.group(2)), float(m.group(3))
        if any(x["point"] == p and x["ci_low"] == lo and x["ci_high"] == hi for x in models):
            continue
        pt = [x for x in models if x["point"] == p]
        iv = [x for x in models if x["ci_low"] == lo and x["ci_high"] == hi]
        if pt and iv and pt[0]["model"] != iv[0]["model"]:
            out.append({"code": MISMATCH, "kind": "PROSE_MIXES_MODELS",
                        "prose": {"point": p, "ci_low": lo, "ci_high": hi, "quote": _sentence(text, m.start())},
                        "point_from": pt[0]["model"], "interval_from": iv[0]["model"],
                        "figure": f"{fig['figure']}{fig['panel']} ({fig['panel_title']})",
                        "figure_rows": [f"{x['figure_row']} {x['point']} [{x['ci_low']}, {x['ci_high']}]" for x in models]})
    return out


def _surname(member):
    return re.sub(r"[^a-z]", "", (member.get("name_in_source") or member["family_id"]).split()[0].lower().replace("’", ""))


def bind_rows(fig: dict, trial_set: list):
    """[(row, member or None, note)] -- surname+year; surname alone only when unique in the included-trial table."""
    out = []
    for row in fig["rows"]:
        label = row["row_label"]
        words = {re.sub(r"[^a-z]", "", w.lower()) for w in re.split(r"[\s,.\-]+", label) if w}
        year = (re.search(r"(\d{4})\s*$", label) or [None, None])[1]
        cands = [m for m in trial_set if _surname(m) in words]
        exact = [m for m in cands if year and re.search(r"\b" + year + r"\b", m["family_id"])]
        if len(exact) == 1:
            out.append((row, exact[0], None))
        elif len(cands) == 1:
            ty = (re.search(r"\b(19|20)\d{2}\b", cands[0]["family_id"]) or [None])[0]
            out.append((row, cands[0], {"code": MISMATCH, "kind": "FIGURE_ROW_YEAR_DIFFERS_FROM_TABLE",
                                        "figure_row": label, "figure_year": year, "table_row": cands[0]["family_id"],
                                        "table_year": ty}))
        else:
            out.append((row, None, {"code": "FIGURE_ROW_NOT_BOUND", "figure_row": label, "candidates": len(cands)}))
    return out


def apply_to_panel(entry: dict, doc: dict, primary_outcome: Optional[str], root) -> dict:
    """Annotate the registered comparator's panel entry in place (after comparator_panel.validate)."""
    text = ""
    if entry.get("document_ref"):
        p = Path(root) / entry["document_ref"]
        text = p.read_text(encoding="utf-8") if p.exists() else ""
    tuples, mism, bindings = [], [], []
    for fig in doc.get("figures") or []:
        for x in fig["pooled"]:
            tuples.append({"model": x["model"], "point": x["point"], "ci_low": x["ci_low"], "ci_high": x["ci_high"],
                           "figure": fig["figure"], "panel": fig["panel"], "panel_title": fig["panel_title"],
                           "figure_row": x["figure_row"], "document_sha256": fig["document"]["sha256"],
                           "document_url": fig["document"]["url"], "read_by": fig["document"].get("read_by")})
        mism += prose_mismatches(text, fig)
        ts = entry.get("trial_set") or []
        if ts:
            bound = bind_rows(fig, ts)
            for row, m, note in bound:
                bindings.append({"figure_row": row["row_label"], "table_row": m["family_id"] if m else None,
                                 **({"note": note} if note else {})})
                if note and note["code"] == MISMATCH:
                    mism.append(note)
            if primary_outcome and all(m for _, m, _ in bound):
                label = fig["outcome_label"]
                hit = {m["family_id"] for _, m, _ in bound}
                for m in ts:
                    m["endpoint"] = label if m["family_id"] in hit else f"not in {label}"
                entry["outcome_endpoints"] = dict(entry.get("outcome_endpoints") or {}, **{primary_outcome: label})
                entry["outcome_membership_source"] = (f"{fig['figure']}{fig['panel']} rows bound to the included-trial "
                                                      f"table ({len(hit)} of {len(ts)} table trials in this panel)")
    entry["figure_model_tuples"] = tuples
    entry["internal_mismatches"] = mism
    entry["figure_row_bindings"] = bindings
    return entry


def load_reported(root, slug) -> Optional[dict]:
    """cache/<slug>/comparator_reported_mismatches.json: internal inconsistencies REPORTED by a review, each side typed
    HELD (quote located verbatim in the held record) or REPORTED_NOT_HELD. A HELD side whose quote is not in the held
    bytes is refused."""
    p = Path(root) / "cache" / slug / "comparator_reported_mismatches.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    for m in doc.get("mismatches") or []:
        if m.get("code") != MISMATCH:
            raise FigureRefused("REPORTED: unknown code")
        for side in m.get("sides") or []:
            if side.get("state") == "HELD":
                recs = json.loads((Path(root) / side["document_ref"]).read_text(encoding="utf-8"))
                text = next((str(r.get("abstract") or "") for v in recs.values() if isinstance(v, list) for r in v
                             if isinstance(r, dict) and str(r.get("id")) == str(side["record_id"])), "")
                if side["quote"] not in text:
                    raise FigureRefused(f"REPORTED: HELD side quote not located in {side['document_ref']}")
            elif side.get("state") != "REPORTED_NOT_HELD" or not side.get("reported_by"):
                raise FigureRefused("REPORTED: a side must be HELD or REPORTED_NOT_HELD with who reported it")
    return doc


def attach_review(review: dict, entry: Optional[dict], reported: Optional[dict] = None) -> dict:
    """Copy the model tuples and mismatches onto review['comparator'] and flag -- never change -- a reported row
    that repeats a mixed prose pair."""
    comp = dict(review.get("comparator") or {})
    if reported:
        comp["internal_mismatches"] = list(comp.get("internal_mismatches") or []) + [
            dict(m, evidence_state="BOTH_SIDES_HELD" if all(s["state"] == "HELD" for s in m["sides"]) else "ONE_SIDE_HELD"
                 if any(s["state"] == "HELD" for s in m["sides"]) else "NOT_HELD") for m in reported.get("mismatches") or []]
        if reported.get("reported_trial_membership"):
            comp["reported_trial_membership"] = reported["reported_trial_membership"]
    if not entry or not entry.get("figure_model_tuples"):
        return comp
    comp["model_tuples"] = entry["figure_model_tuples"]
    comp["internal_mismatches"] = (entry.get("internal_mismatches") or []) + [
        m for m in comp.get("internal_mismatches") or [] if m.get("sides")]
    mixed = [x for x in comp["internal_mismatches"] if x.get("kind") == "PROSE_MIXES_MODELS"]
    for row in comp.get("reported") or []:
        for x in mixed:
            if (row.get("estimate"), row.get("ci_low"), row.get("ci_high")) == (x["prose"]["point"], x["prose"]["ci_low"],
                                                                                x["prose"]["ci_high"]):
                row["internal_mismatch"] = {"code": MISMATCH, "kind": x["kind"], "point_from": x["point_from"],
                                            "interval_from": x["interval_from"], "figure_rows": x["figure_rows"],
                                            "note": "kept as printed; the comparator's own figure reports these as two "
                                                    "different models -- compare against a model-specific row, never "
                                                    "this pair"}
    return comp


def render_reported(comp: dict) -> str:
    """The review-reported mismatches (each side with its evidence state) and any reported trial membership."""
    rep_ = [m for m in comp.get("internal_mismatches") or [] if m.get("sides")]
    tm = comp.get("reported_trial_membership")
    if not rep_ and not tm:
        return ""
    e = lambda s: _h.escape(str(s), quote=True)  # noqa: E731
    items = "".join(
        f"<li><code>{e(m['code'])}</code> {e(m['kind'])} ({e(m['evidence_state'])}): " + "; ".join(
            f"{e(sd['where'])} says {e(sd.get('as_reported') or sd['value'])} [{e(sd['state'])}"
            + (f": &ldquo;{e(sd['quote'])}&rdquo;" if sd.get("quote") else f", reported by {e(sd['reported_by'])}; "
               f"{e(sd['why_not_held'])}") + "]" for sd in m["sides"]) + ". Neither number is used as truth.</li>"
        for m in rep_)
    tmh = (f"<p class='small'>Trial membership reported but not held ({e(tm['state'])}): {e(tm['claim'])}. Not used for "
           f"the computed overlap: {e(tm['why'])}.</p>" if tm else "")
    return ("<div class='comparator-models'><h5>Comparator internal inconsistencies (reported)</h5>"
            + (f"<ul>{items}</ul>" if items else "") + tmh + "</div>")


def render_block(entry: dict) -> str:
    if not entry.get("figure_model_tuples"):
        return ""
    e = lambda s: _h.escape(str(s), quote=True)  # noqa: E731
    rows = "".join(f"<tr><td>{e(t['figure'])}{e(t['panel'])} {e(t['panel_title'])}</td><td>{e(t['model'])}</td>"
                   f"<td>{e(t['figure_row'])}</td><td>{e(t['point'])} [{e(t['ci_low'])}, {e(t['ci_high'])}]</td></tr>"
                   for t in entry["figure_model_tuples"])
    mm = [x for x in entry.get("internal_mismatches") or [] if not x.get("sides")]
    items = "".join(
        "<li><code>" + e(x["code"]) + "</code> " + e(x["kind"]) + ": "
        + (e(f"the prose tuple {x['prose']['point']} ({x['prose']['ci_low']}-{x['prose']['ci_high']}) takes its point from "
             f"the {x['point_from']} row and its interval from the {x['interval_from']} row of {x['figure']}. Prose: “")
           + e(x["prose"]["quote"]) + "”" if x["kind"] == "PROSE_MIXES_MODELS" else
           e(f"figure row '{x['figure_row']}' ({x['figure_year']}) is table row '{x['table_row']}' ({x['table_year']})"))
        + "</li>" for x in mm)
    t0 = entry["figure_model_tuples"][0]
    return ("<div class='comparator-models'><h5>Comparator results by model (from its own figure)</h5>"
            "<table><tr><th>Figure</th><th>Model</th><th>Row as printed</th><th>RR [95% CI]</th></tr>" + rows + "</table>"
            + (f"<p><strong>{len(mm)} internal mismatch(es) in the comparator</strong> -- kept as found; our result is not "
               "changed to agree with either side:</p><ul>" + items + "</ul>" if mm else "")
            + f"<p class='small'>Figure read by {e(t0.get('read_by'))}; image sha256 {e(t0['document_sha256'])} at "
              f"{e(t0['document_url'])} (bytes not held). The transcription is checked by recomputing both pooled rows "
              "from its per-trial rows.</p>"
            + (f"<p class='small'>Outcome-level membership: {e(entry['outcome_membership_source'])}.</p>"
               if entry.get("outcome_membership_source") else "") + "</div>")
