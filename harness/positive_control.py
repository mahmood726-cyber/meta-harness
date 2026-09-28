"""Positive controls for the pooling ENGINE (V1.0.1): reproduce a published meta-analysis from its own forest-plot rows.

A published analysis that states its method (e.g. Paule-Mandel tau^2 with a Hartung-Knapp interval) and prints its
per-trial rows is an external known answer for harness/synth.pool. Each control in registry/positive_controls.json
carries the rows (with where they were read and the evidence state), the method, and the expected results; this module
pools the rows with OUR engine and compares:
  CE     inverse-variance common effect, z interval      (synth.pool estimate_fixed / ci_*_fixed)
  PM_HK  Paule-Mandel tau^2, Hartung-Knapp t_{k-1} interval (synth.pool estimate / ci_low / ci_high)
  I2     from the common-effect Q
A control whose rows are not held is PENDING_SOURCE and raises PendingSource -- it is never run on rows typed from
memory, and never reported as a pass.

V1.0.1 (DOAC-VTE review): a control may instead take its rows from a validated member-inputs object
(rows_from: {"slug": ..., "use_ours_for": [...]}, harness/outcome_match.py), where each row is HELD (quoted from the
trial's own held report) or REPORTED_NOT_HELD (with who reported it). Such a control runs, and its result names the
rows it is CONDITIONAL on; it is never reported as an unconditional pass.
"""
from __future__ import annotations

import json
from pathlib import Path

from .synth import Study, pool


class PendingSource(RuntimeError):
    pass


def load(root) -> list:
    p = Path(root) / "registry" / "positive_controls.json"
    return json.loads(p.read_text(encoding="utf-8")).get("controls", []) if p.exists() else []


def rows_of(control: dict, root=None) -> list:
    if control.get("state") == "ROWS_FROM_FIGURE":
        # V1.0.1 (melatonin review): the comparator's own forest-plot rows, read from its held figure image
        # (cache/<slug>/comparator_figure_rows.json; image sha256 and every quote verified by comparator_display.load)
        from . import comparator_display
        doc = comparator_display.load(root, control["rows_from"]["slug"])
        if doc is None:
            raise PendingSource(f"{control.get('id')}: comparator_figure_rows.json not held")
        return [{"label": r["label"], "effect": r["effect"], "ci_low": r["ci_low"], "ci_high": r["ci_high"],
                 "state": "HELD"} for r in doc["rows"]]
    if control.get("state") == "ROWS_FROM_ANALYSIS":
        # V1.0.1 (semaglutide-obesity review): the comparator's governing-analysis plot rows (counts), read from its
        # HELD figure image (cache/<slug>/comparator_analysis.json; image sha256, k and n verified by comparator_analysis)
        from . import comparator_analysis
        doc = comparator_analysis.load(root, control["rows_from"]["slug"])
        if doc is None or not doc.get("membership"):
            raise PendingSource(f"{control.get('id')}: comparator_analysis.json membership not held")
        return [{"label": r["label"], "events_int": r["counts"][0], "n_int": r["counts"][1], "events_ctl": r["counts"][2],
                 "n_ctl": r["counts"][3], "state": "HELD"} for r in doc["membership"]["rows"]]
    if control.get("state") == "ROWS_FROM_MEMBER_INPUTS":
        from . import outcome_match
        rf = control["rows_from"]
        doc = outcome_match.load(root, rf["slug"])
        if doc is None:
            raise PendingSource(f"{control.get('id')}: cache/{rf['slug']}/comparator_member_inputs.json not held")
        return outcome_match.control_rows(doc, rf.get("use_ours_for") or ())
    if control.get("state") != "HELD" or not control.get("rows"):
        raise PendingSource(f"{control.get('id')}: rows not held ({control.get('why_pending', 'no rows')})")
    return control["rows"]


def _dl(rows: list, measure: str) -> tuple:
    """DerSimonian-Laird random effects on log RR / log OR from counts (0.5 added to every cell of a zero-cell row).
    V1.0.1 (SGLT2 HHF-in-CVOTs review): used ONLY to reproduce a published analysis that states DL; our own pooling
    never uses DL (harness/synth.py). Returns (estimate, low, high, tau2, Q, I2)."""
    import math
    y, v = [], []
    for r in rows:
        a, n1, c, n2 = r["events_int"], r["n_int"], r["events_ctl"], r["n_ctl"]
        b, d = n1 - a, n2 - c
        if min(a, b, c, d) == 0:
            a, b, c, d, n1, n2 = a + .5, b + .5, c + .5, d + .5, n1 + 1, n2 + 1
        if measure == "OR":
            y.append(math.log(a * d / (b * c)))
            v.append(1 / a + 1 / b + 1 / c + 1 / d)
        else:
            y.append(math.log((a / n1) / (c / n2)))
            v.append(1 / a - 1 / n1 + 1 / c - 1 / n2)
    w = [1 / x for x in v]
    fe = sum(wi * yi for wi, yi in zip(w, y)) / sum(w)
    q = sum(wi * (yi - fe) ** 2 for wi, yi in zip(w, y))
    k = len(y)
    t2 = max(0.0, (q - (k - 1)) / (sum(w) - sum(x * x for x in w) / sum(w)))
    ws = [1 / (x + t2) for x in v]
    mu = sum(wi * yi for wi, yi in zip(ws, y)) / sum(ws)
    se = (1 / sum(ws)) ** 0.5
    z = 1.959963984540054
    return (math.exp(mu), math.exp(mu - z * se), math.exp(mu + z * se), t2, q, max(0.0, (q - (k - 1)) / q) * 100 if q > 0 else 0.0)


def reproduce(control: dict, root=None) -> dict:
    rows = rows_of(control, root)
    sub = control.get("substitute") or {}
    if sub:
        # one row replaced by the counts its trial's OWN held report prints (the basis is recorded with the control)
        rows = [dict(r, events_int=sub["counts"][0], n_int=sub["counts"][1], events_ctl=sub["counts"][2],
                     n_ctl=sub["counts"][3], substituted=True) if r["label"] == sub["row"] else r for r in rows]
        if not any(r.get("substituted") for r in rows):
            raise PendingSource(f"{control.get('id')}: substitute row {sub['row']!r} is not a row of the analysis")
        from .comparator_analysis import _norm
        from pathlib import Path
        b = sub.get("basis") or {}
        held = _norm((Path(root or ".") / b["document_ref"]).read_text(encoding="utf-8")) if b.get("document_ref") else ""
        if not b.get("quote") or _norm(b["quote"]) not in held or not all(str(x) in b["quote"] for x in sub["counts"]):
            raise PendingSource(f"{control.get('id')}: the substitution's basis is not located in its held report")
    m = control["measure"]
    studies = [Study(label=r["label"], effect=r["effect"], ci_low=r["ci_low"], ci_high=r["ci_high"], measure=m)
               if "effect" in r else
               Study(label=r["label"], ai=r["events_int"], n1i=r["n_int"], ci=r["events_ctl"], n2i=r["n_ctl"], measure=m)
               for r in rows]
    res = pool(studies, scale=m)
    k = len(studies)
    i2 = max(0.0, (res.Q - (k - 1)) / res.Q) * 100 if res.Q > 0 else 0.0
    out_dl = {}
    if "DL" in (control.get("expected") or {}):
        e_, l_, h_, t2_, q_, i2_ = _dl(rows, m)
        out_dl = {"DL": (e_, l_, h_), "DL_tau2": t2_, "DL_Q": q_, "DL_I2": i2_}
    return {**out_dl, "CE": (res.estimate_fixed, res.ci_low_fixed, res.ci_high_fixed),
            "PM_HK": (res.estimate, res.ci_low, res.ci_high), "I2": i2, "tau2": res.tau2, "Q": res.Q, "k": k,
            "conditional_on": [r["label"] for r in rows if r.get("state") == "REPORTED_NOT_HELD"]}


def compare(control: dict, got: dict) -> list:
    """[(quantity, expected, got)] for every expected value outside the control's tolerance."""
    tol = float(control.get("tolerance", 5e-5))
    exp = control["expected"]
    bad = []
    for q in ("CE", "PM_HK", "DL"):
        if q in exp:
            for e, g in zip(exp[q], got[q]):
                if abs(e - g) > tol:
                    bad.append((q, exp[q], tuple(round(x, 5) for x in got[q])))
                    break
    if "I2" in exp and abs(exp["I2"] - got["I2"]) > float(control.get("i2_tolerance", 0.005)):
        bad.append(("I2", exp["I2"], round(got["I2"], 3)))
    if "DL_I2" in exp and abs(exp["DL_I2"] - got["DL_I2"]) > float(control.get("i2_tolerance", 0.05)):
        bad.append(("DL_I2", exp["DL_I2"], round(got["DL_I2"], 2)))
    for q in ("Q", "tau2"):
        if q in exp and abs(exp[q] - got[q]) > tol:
            bad.append((q, exp[q], round(got[q], 6)))
    return bad
