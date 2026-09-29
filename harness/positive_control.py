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

import html
import json
import re
from pathlib import Path

from .synth import Study, pool


class PendingSource(RuntimeError):
    pass


def load(root) -> list:
    p = Path(root) / "registry" / "positive_controls.json"
    return json.loads(p.read_text(encoding="utf-8")).get("controls", []) if p.exists() else []


# ------------------------------------------------------------------------------------------------------------------
# V1.0.1 (statins-older-adults review). A PENDING_SOURCE control's "not held" must be a RECORDED result: every route
# (PMC ID converter, Europe PMC, the publisher's DOI) was requested and none returned an open full text
# (scripts/positive_control_acquire.py -> registry/positive_control_acquisition.json). A control whose source a route
# reports as open is not pending -- it is un-acquired, and refused as such. A typed why_pending with no recorded
# request is refused too.
ACQUISITION = "registry/positive_control_acquisition.json"
ROUTES = ("PMC_IDCONV", "EUROPE_PMC", "PUBLISHER_DOI")
NOT_HELD_STATES = {"NOT_IN_PMC", "IN_PMC_NOT_OPEN", "NOT_OPEN_ACCESS", "BOT_CHECK_NOT_BYPASSED", "LANDING_PAGE_READ",
                   "IN_PMC"}


def acquisition(root) -> dict:
    p = Path(root) / ACQUISITION
    return json.loads(p.read_text(encoding="utf-8")).get("controls", {}) if p.exists() else {}


def pending_problems(control: dict, acq: dict) -> list:
    if control.get("state") != "PENDING_SOURCE" or not control.get("pmid"):
        return []
    rec = acq.get(control["id"]) or {}
    got = {a.get("route"): a for a in rec.get("attempts") or []}
    need = [r for r in ROUTES if r != "PUBLISHER_DOI" or control.get("doi")]
    out = [f"{control['id']}: PENDING_SOURCE with no recorded {r} request" for r in need if r not in got]
    out += [f"{control['id']}: {r} records {got[r].get('state')} -- an open source is un-acquired, not pending"
            for r in need if r in got and got[r].get("state") == "OPEN_FULL_TEXT"]
    out += [f"{control['id']}: {r} request failed ({got[r].get('state')}) -- a failed request is not evidence of 'not held'"
            for r in need if r in got and got[r].get("state") not in NOT_HELD_STATES | {"OPEN_FULL_TEXT"}]
    return out


def checkpoints(root, slug: str) -> list:
    """RCT checkpoints registered for THIS topic (role RCT_CHECKPOINT, topic == slug): a randomised-evidence analysis
    of the topic's question, shown beside a registered comparator that is not one. Held rows run through our engine
    and are compared; a pending one states the recorded acquisition result. Never an input, never a target."""
    acq, out = acquisition(root), []
    for c in load(root):
        if c.get("role") != "RCT_CHECKPOINT" or c.get("topic") != slug:
            continue
        probs = pending_problems(c, acq)
        if probs:
            raise PendingSource("; ".join(probs))
        row = {"id": c["id"], "source": c["source"], "measure": c["measure"], "expected": c["expected"],
               "expected_reported_by": c.get("expected_reported_by"), "note": c.get("note"), "state": c["state"]}
        if c["state"] == "PENDING_SOURCE":
            row["acquisition"] = [{k: a.get(k) for k in ("route", "state", "utc", "status")}
                                  for a in (acq.get(c["id"]) or {}).get("attempts") or []]
        else:
            got = reproduce(c, root)
            row["result"] = {"CE": got["CE"], "problems": [list(map(str, p)) for p in compare(c, got)]}
        out.append(row)
    return out


_OBS = re.compile(r"(?i)\b(?:observational|cohort|case[- ]control|registry-based|real[- ]world)\s+"
                                r"(?:stud(?:y|ies)|data|analys[ie]s|evidence)")
_RCT = re.compile(r"(?i)\b(?:randomi[sz]ed(?:[- ]controlled)?\s+(?:clinical\s+)?trials?|RCTs)\b")


def comparator_design(abstract: str) -> dict:
    """NON_RANDOMISED when the comparator's own held abstract says it pooled observational (cohort, case-control,
    registry, real-world) evidence and nowhere says it included randomised trials; else RANDOMISED_OR_NOT_STATED."""
    o, r = _OBS.search(abstract or ""), _RCT.search(abstract or "")
    return ({"state": "NON_RANDOMISED", "quote": o.group(0)} if o and not r else
            {"state": "RANDOMISED_OR_NOT_STATED", "quote": r.group(0) if r else None})


def render_checkpoints(rows, design: dict | None = None) -> str:
    if design and design.get("state") == "NON_RANDOMISED" and not rows:
        return ("<div class='rct-checkpoints'><p><strong>Comparator is non-randomised</strong> (its abstract: "
                f"&ldquo;{html.escape(str(design.get('quote')))}&rdquo;) and no RCT checkpoint is registered for "
                "this topic.</p></div>")
    if not rows:
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    parts = []
    for r in rows:
        exp = r["expected"].get("CE") or r["expected"].get("PM_HK") or r["expected"].get("DL")
        head = (f"<p><strong>RCT checkpoint</strong> ({e(r['state'])}): {e(r['source'])}. Expected {e(r['measure'])} "
                f"{e(exp[0])} ({e(exp[1])}&ndash;{e(exp[2])}), reported by {e(r.get('expected_reported_by'))}. ")
        if r["state"] == "PENDING_SOURCE":
            head += ("Not run: its rows are not held. Recorded acquisition: "
                     + "; ".join(f"{e(a['route'])} {e(a['state'])} ({e(a['utc'])})" for a in r["acquisition"])
                     + ". A pending checkpoint is never reported as a pass.")
        else:
            head += ("Our engine on its rows: " + e(tuple(round(x, 6) for x in r["result"]["CE"]))
                     + (" &mdash; agrees." if not r["result"]["problems"] else f" &mdash; DISAGREES: {e(r['result']['problems'])}."))
        parts.append(head + (f" {e(r['note'])}" if r.get("note") else "") + "</p>")
    return "<div class='rct-checkpoints'><h5>RCT checkpoint for a non-randomised comparator</h5>" + "".join(parts) + "</div>"


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
        rows = doc["membership"]["rows"]
        if rows and all("log_se" in r for r in rows):
            # V1.0.1 (MRA-HFrEF review): a generic inverse-variance plot's printed log[HR] and SE, passed to the engine
            # as the z interval they define (synth recovers exactly that SE)
            return [dict(zip(("effect", "ci_low", "ci_high"), comparator_analysis.log_row_effect(r)), label=r["label"],
                         state="HELD") for r in rows]
        out = [{"label": r["label"], "events_int": r["counts"][0], "n_int": r["counts"][1], "events_ctl": r["counts"][2],
                "n_ctl": r["counts"][3], "state": "HELD"} for r in rows]
        if control.get("drop_double_zero"):
            # V1.0.1 (tocilizumab review): the published analysis leaves out rows with no events in either arm (REACT
            # prints them 'NA'); a single-zero row keeps its 0.5 correction
            out = [r for r in out if r["events_int"] or r["events_ctl"]]
        return out
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
