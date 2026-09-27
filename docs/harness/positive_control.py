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


def reproduce(control: dict, root=None) -> dict:
    rows = rows_of(control, root)
    m = control["measure"]
    studies = [Study(label=r["label"], ai=r["events_int"], n1i=r["n_int"], ci=r["events_ctl"], n2i=r["n_ctl"], measure=m)
               for r in rows]
    res = pool(studies, scale=m)
    k = len(studies)
    i2 = max(0.0, (res.Q - (k - 1)) / res.Q) * 100 if res.Q > 0 else 0.0
    return {"CE": (res.estimate_fixed, res.ci_low_fixed, res.ci_high_fixed),
            "PM_HK": (res.estimate, res.ci_low, res.ci_high), "I2": i2, "tau2": res.tau2, "Q": res.Q, "k": k,
            "conditional_on": [r["label"] for r in rows if r.get("state") == "REPORTED_NOT_HELD"]}


def compare(control: dict, got: dict) -> list:
    """[(quantity, expected, got)] for every expected value outside the control's tolerance."""
    tol = float(control.get("tolerance", 5e-5))
    exp = control["expected"]
    bad = []
    for q in ("CE", "PM_HK"):
        if q in exp:
            for e, g in zip(exp[q], got[q]):
                if abs(e - g) > tol:
                    bad.append((q, exp[q], tuple(round(x, 5) for x in got[q])))
                    break
    if "I2" in exp and abs(exp["I2"] - got["I2"]) > float(control.get("i2_tolerance", 0.005)):
        bad.append(("I2", exp["I2"], round(got["I2"], 3)))
    for q in ("Q", "tau2"):
        if q in exp and abs(exp[q] - got[q]) > tol:
            bad.append((q, exp[q], round(got[q], 6)))
    return bad
