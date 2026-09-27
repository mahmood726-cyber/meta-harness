"""Outcome-level matching of shared trials (V1.0.1, DOAC-VTE review): identical membership is not identical inputs.

van Es 2014 pools the same six trials as our DOAC-VTE pool (6 shared by name), but its recurrence row for Hokusai-VTE
uses the ON-TREATMENT counts (66/4,118 vs 80/4,122), whereas our row is the overall-study 12-month result. A
trial-level overlap of 6 of 6 therefore says nothing about whether the two pools had the same INPUTS.

cache/<slug>/comparator_member_inputs.json records, per shared trial, both sides on four dimensions -- population,
outcome, window, analysis set -- each typed and, where held, quoted from held bytes (an abstract sentence in
records.json, or a registry results cell in evidence/held/registry/<NCT>.json located by outcome/group title). A side
that is not held is REPORTED_NOT_HELD with who reported it. This module refuses a HELD source that is not located,
cross-checks OUR side against the served pool row, and compares:
  SAME            both sides held (or declared on both sides) and equal
  DIFFERENT       the typed values differ (a REPORTED_NOT_HELD side can make a difference visible, never an equality)
  NOT_ESTABLISHED a side is missing
A trial is INPUT_IDENTICAL only when all four dimensions are SAME.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# 'outcome_definition', not 'outcome': elsewhere in a review an object's 'outcome' key is an outcome NAME
# (harness/claimgraph.py reads it as one)
DIMENSIONS = ("population", "outcome_definition", "window", "analysis_set")


class InputsRefused(ValueError):
    pass


def _abstract(root: Path, ref: str, rid: str) -> str:
    recs = json.loads((root / ref).read_text(encoding="utf-8"))
    return next((str(r.get("abstract") or "") for v in recs.values() if isinstance(v, list) for r in v
                 if isinstance(r, dict) and str(r.get("id")) == str(rid)), "")


def _registry_cell(root: Path, src: dict):
    doc = json.loads((root / src["document_ref"]).read_text(encoding="utf-8"))
    for om in ((doc.get("resultsSection") or {}).get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []:
        if om.get("title") != src["outcome_title"]:
            continue
        gid = {g["id"]: g.get("title") for g in om.get("groups") or []}
        if src["field"] == "denom":
            for dn in om.get("denoms") or []:
                for c in dn.get("counts") or []:
                    if gid.get(c["groupId"]) == src["group_title"]:
                        return str(c.get("value"))
        else:
            for cl in om.get("classes") or []:
                if src.get("class_title") and cl.get("title") != src["class_title"]:
                    continue
                for cat in cl.get("categories") or []:
                    for m in cat.get("measurements") or []:
                        if gid.get(m["groupId"]) == src["group_title"]:
                            return str(m.get("value"))
    return None


def check_source(root, src: dict) -> None:
    root = Path(root)
    # REV-R1 (codex review, verified): an empty quote is 'in' any text, including a record that is not held at all
    if src["kind"] in ("abstract", "registry_field", "held_text") and len(str(src.get("quote") or "").strip()) < 10:
        raise InputsRefused(f"{src['kind']} source with an empty or too-short quote")
    if src["kind"] == "abstract":
        if src["quote"] not in _abstract(root, src["document_ref"], src["record_id"]):
            raise InputsRefused(f"quote not located in {src['document_ref']} record {src['record_id']}: {src['quote'][:60]}")
    elif src["kind"] == "registry_cell":
        got = _registry_cell(root, src)
        if got != str(src["value"]):
            raise InputsRefused(f"registry cell {src['outcome_title'][:40]} / {src['group_title']} / {src['field']} "
                                f"is {got!r}, not {src['value']!r}")
    elif src["kind"] == "registry_field":
        # V1.0.1 (melatonin review): a text field of a registry outcome (its population description, its description)
        doc = json.loads((root / src["document_ref"]).read_text(encoding="utf-8"))
        om = next((o for o in ((doc.get("resultsSection") or {}).get("outcomeMeasuresModule") or {}).get("outcomeMeasures") or []
                   if o.get("title") == src["outcome_title"]), None)
        if om is None or src["quote"] not in str(om.get(src["field"]) or ""):
            raise InputsRefused(f"registry field {src['field']} of {src['outcome_title'][:40]} does not contain the quote")
    elif src["kind"] == "held_text":
        # a quote in a held document's text (tags stripped, whitespace normalised on both sides)
        import html as _h
        import re as _re
        norm = lambda s: _re.sub(r"\s+", " ", _h.unescape(_re.sub(r"<[^>]+>", " ", s))).strip()  # noqa: E731
        if norm(src["quote"]) not in norm((root / src["document_ref"]).read_text(encoding="utf-8")):
            raise InputsRefused(f"quote not located in {src['document_ref']}: {src['quote'][:60]}")
    else:
        raise InputsRefused(f"unknown source kind {src['kind']}")


def load(root, slug) -> Optional[dict]:
    p = Path(root) / "cache" / slug / "comparator_member_inputs.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    for t in doc["trials"]:
        for side in ("theirs", "ours"):
            s = t[side]
            for src in s.get("sources") or []:
                check_source(root, src)
            for src in (s.get("counts") or {}).get("sources") or []:
                check_source(root, src)
            for dim in ("window", "analysis_set", "population", "outcome_definition"):
                d = s.get(dim) or {}
                if d.get("source"):
                    check_source(root, d["source"])
                elif d.get("state") == "HELD" and not d.get("literal"):
                    # REV-R1 (codex review, verified): HELD is a claim about bytes -- it needs the source that holds them
                    raise InputsRefused(f"{t['name']}: {side} {dim} is marked HELD with no source")
            if s.get("state") == "REPORTED_NOT_HELD" and not s.get("reported_by"):
                raise InputsRefused(f"{t['name']}: a REPORTED_NOT_HELD side must say who reported it")
    if (doc.get("comparator_scope") or {}).get("statement"):
        check_source(root, doc["comparator_scope"]["statement"])
    return doc


def _side_value(t, side, dim):
    if dim in ("population", "outcome_definition") and (t[side].get(dim) or {}).get("value") is not None:
        # V1.0.1 (melatonin review): the two sides may use DIFFERENT reports of one trial (Wade 2010 vs Wade 2011), so
        # population and outcome can be typed per side
        d = t[side][dim]
        return d["value"], d.get("state") or ("HELD" if d.get("source") else None)
    if dim in ("population", "outcome_definition"):
        key = "outcome" if dim == "outcome_definition" else dim
        return (t.get(key) or {}).get("value"), "HELD"      # declared once for both sides (same trial report)
    d = (t[side].get(dim) or {})
    return d.get("value"), d.get("state") or ("HELD" if d.get("source") or d.get("literal") else None)


def compare(doc: dict, review: Optional[dict] = None) -> dict:
    ours_rows = {}
    if review:
        prim = next((o for o in review.get("outcomes") or [] if o.get("primary")), {})
        ours_rows = {str(r.get("label")): r for r in prim.get("trials") or []}
    trials = []
    for t in doc["trials"]:
        row = ours_rows.get(str(t["report_pmid"]))
        if review is not None:
            if row is None:
                raise InputsRefused(f"{t['name']}: not a row of our served primary pool")
            if "effect" in t["ours"]:
                # NaN-safe: 'not (|a-b| <= tol)' refuses a NaN, where '|a-b| > tol' would let it through
                if not (abs(float(row["effect"]) - float(t["ours"]["effect"])) <= 1e-9) or row.get("scale") != t["ours"]["scale"]:
                    raise InputsRefused(f"{t['name']}: our side {t['ours']['effect']} {t['ours']['scale']} is not the "
                                        f"served row {row.get('effect')} {row.get('scale')}")
            else:   # a continuous row: our side is the served arm summaries
                keys = ("mean1", "sd1", "nc1", "mean2", "sd2", "nc2")
                if any(row.get(k) != t["ours"].get(k) for k in keys) or row.get("scale") != t["ours"]["scale"]:
                    raise InputsRefused(f"{t['name']}: our side is not the served row's arm summaries")
        dims = {}
        for dim in DIMENSIONS:
            (a, sa), (b, sb) = _side_value(t, "ours", dim), _side_value(t, "theirs", dim)
            if a is None or b is None:
                dims[dim] = {"state": "NOT_ESTABLISHED", "ours": a, "theirs": b}
            elif a != b:
                dims[dim] = {"state": "DIFFERENT", "ours": a, "theirs": b, "theirs_evidence": sb}
            elif sa == "HELD" and sb == "HELD":
                dims[dim] = {"state": "SAME", "value": a,
                             "basis": ((t.get("outcome" if dim == "outcome_definition" else dim) or {}).get("note")
                                       if dim in ("population", "outcome_definition") else
                                       "each side typed from its own held source")}
            else:
                dims[dim] = {"state": "NOT_ESTABLISHED", "ours": a, "theirs": b, "why": "one side not held"}
        identical = all(d["state"] == "SAME" for d in dims.values())
        trials.append({"family_id": t["family_id"], "name": t["name"], "report_pmid": t["report_pmid"],
                       "dimensions": dims, "inputs": "INPUT_IDENTICAL" if identical else
                       ("INPUT_DIFFERENT" if any(d["state"] == "DIFFERENT" for d in dims.values()) else "NOT_ESTABLISHED"),
                       "theirs_counts": {k: t["theirs"].get(k) for k in ("events_int", "n_int", "events_ctl", "n_ctl")},
                       "theirs_counts_state": t["theirs"]["state"],
                       "theirs_input": _input_text(t["theirs"]),
                       "ours_effect": (f"{t['ours']['scale']} {t['ours']['effect']}" if "effect" in t["ours"] else
                                       f"{t['ours']['scale']} from {t['ours']['mean1']} (SD {t['ours']['sd1']}, n {t['ours']['nc1']}) vs "
                                       f"{t['ours']['mean2']} (SD {t['ours']['sd2']}, n {t['ours']['nc2']})")})
    n = len(trials)
    return {"comparator_pmid": doc["comparator_pmid"], "outcome": doc["outcome"], "shared_by_name": n,
            "input_identical": sum(x["inputs"] == "INPUT_IDENTICAL" for x in trials),
            "input_different": sum(x["inputs"] == "INPUT_DIFFERENT" for x in trials),
            "not_established": sum(x["inputs"] == "NOT_ESTABLISHED" for x in trials),
            "trials": trials, "binding": doc.get("binding"), "comparator_text": doc.get("comparator_text"),
            "comparator_scope": doc.get("comparator_scope"),
            "rule": "identical membership is not identical inputs: a shared trial is input-identical only when "
                    "population, outcome, window and analysis set are the same on both sides"}


def _input_text(side: dict) -> str:
    if side.get("events_int") is not None:
        return f"{side['events_int']}/{side['n_int']} vs {side['events_ctl']}/{side['n_ctl']}"
    return f"{side.get('scale', '')} {side.get('effect')} ({side.get('ci_low')} to {side.get('ci_high')})".strip()


def control_rows(doc: dict, use_ours_for=()) -> list:
    """The comparator's per-trial rows (for harness/positive_control.py). use_ours_for swaps in OUR held counts for the
    named trials (the counterfactual: the comparator's pool with our analysis set)."""
    rows = []
    for t in doc["trials"]:
        src = t["ours"]["counts"] if t["name"] in use_ours_for else t["theirs"]
        rows.append({"label": t["name"], "state": src["state"],
                     **{k: src[k] for k in ("events_int", "n_int", "events_ctl", "n_ctl")}})
    return rows


def render(m: Optional[dict]) -> str:
    import html
    if not m:
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    rows = []
    for t in m["trials"]:
        cells = []
        for dim in DIMENSIONS:
            d = t["dimensions"][dim]
            cells.append(f"<td><code>{e(d['state'])}</code>" + (
                f"<br>ours {e(d.get('ours'))}; theirs {e(d.get('theirs'))}" if d["state"] != "SAME" else "") + "</td>")
        rows.append(f"<tr><td>{e(t['name'])}</td><td>{e(t['ours_effect'])}</td><td>{e(t.get('theirs_input'))} "
                    f"({e(t['theirs_counts_state'])})</td>{''.join(cells)}"
                    f"<td><strong>{e(t['inputs'])}</strong></td></tr>")
    return ("<div class='outcome-match'><h5>Outcome-level matching of shared trials</h5>"
            f"<p>{e(m['shared_by_name'])} trials shared by name; {e(m['input_identical'])} input-identical, "
            f"{e(m['input_different'])} with different inputs, {e(m['not_established'])} not established. "
            f"{e(m['rule'])}.</p><table><thead><tr><th>Trial</th><th>Our input</th><th>Comparator input</th>"
            "<th>Population</th><th>Outcome</th><th>Window</th><th>Analysis set</th><th>Inputs</th></tr></thead><tbody>"
            + "".join(rows) + f"</tbody></table><p class='small'>{e(m['binding'])}</p>"
            + (f"<p class='small'>Comparator scope (the comparator's, not ours): &ldquo;{e(m['comparator_scope']['statement']['quote'])}&rdquo; "
               f"Reported exclusion: {e(m['comparator_scope'].get('reported_exclusion'))}. Applies to: {e(m['comparator_scope']['applies_to'])}.</p>"
               if m.get("comparator_scope") else "") + "</div>")
