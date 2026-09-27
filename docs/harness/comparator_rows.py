"""Comparator ROW plausibility and outcome-level membership (V1.0.1, esketamine review).

A comparator row is checked against the trial it cites, before anything on our page is validated against the
comparator's numbers:
  n          the row's randomised n (both arms) <= the cited trial's randomised N
  design     the row's printed design class equals the cited trial's (randomised withdrawal vs parallel vs open-label)
  direction  the row's effect is roughly consistent with the cited trial's own result for that outcome: implausible
             when the points have opposite signs AND the row's point lies outside the cited trial's interval
Xie 2026 fails all three: its 'Trial A' row (cites TRANSFORM-2) prints 172/174 against TRANSFORM-2's 227 randomised;
its older-adult MD +0.50 (-3.57 to 4.57) against TRANSFORM-3's -3.6 (-7.20 to 0.07); its 'Trial E' row prints
double-blind randomised withdrawal for a reference whose own title says SUSTAIN-2 is an open-label study.

cache/<slug>/comparator_row_checks.json holds, per row, the printed and the cited facts, each with a verbatim quote
located in held bytes (tags ignored) or typed REPORTED_NOT_HELD with who reported it. The VERDICTS are computed here.
Any COMPARATOR_ROW_IMPLAUSIBLE row withholds numerical validation against the comparator. The same object may carry
the comparator's OUTCOME-LEVEL membership (which rows its result for our outcome pools), checked by arithmetic.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

IMPLAUSIBLE = "COMPARATOR_ROW_IMPLAUSIBLE"


class RowsRefused(ValueError):
    pass


def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s or ""))).strip()


def _held(root: Path, ev: dict) -> str:
    raw = (root / ev["document_ref"]).read_text(encoding="utf-8")
    if ev.get("record_id"):
        recs = json.loads(raw)
        return next((str(r.get(ev.get("field") or "abstract") or "") for v in recs.values() if isinstance(v, list) for r in v
                     if isinstance(r, dict) and str(r.get("id")) == str(ev["record_id"])), "")
    return raw


def _check_ev(root: Path, ev: dict, where: str):
    if ev.get("state") == "REPORTED_NOT_HELD":
        if not ev.get("reported_by"):
            raise RowsRefused(f"{where}: REPORTED_NOT_HELD needs reported_by")
        return
    held = _held(root, ev)
    if ev["quote"] not in held and _norm(ev["quote"]) not in _norm(held):
        raise RowsRefused(f"{where}: quote not located in {ev['document_ref']}: {ev['quote'][:60]}")


def load(root, slug) -> Optional[dict]:
    root = Path(root)
    p = root / "cache" / slug / "comparator_row_checks.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    for r in doc.get("rows") or []:
        for side in ("printed", "cited"):
            for k, v in (r.get(side) or {}).items():
                if isinstance(v, dict) and "evidence" in v:
                    for ev in v["evidence"]:
                        _check_ev(root, ev, f"{r['row']}.{side}.{k}")
    om = doc.get("outcome_membership")
    if om:
        for ev in om.get("evidence") or []:
            _check_ev(root, ev, "outcome_membership")
    for dc in doc.get("definition_checks") or []:
        for r in dc.get("rows") or []:
            for ev in (r.get("printed_evidence") or []) + (r.get("definition_evidence") or []):
                _check_ev(root, ev, f"definition_checks.{dc.get('outcome')}.{r.get('row')}")
    return doc


def _checks(r: dict) -> list:
    pr, ci = r.get("printed") or {}, r.get("cited") or {}
    out = []
    n, N = (pr.get("n") or {}), (ci.get("randomised_n") or {})
    if n.get("value") is not None and N.get("value") is not None:
        ok = n["value"] <= N["value"]
        out.append({"check": "n", "state": "PASS" if ok else "FAIL",
                    "detail": f"row n {n['value']} vs cited trial randomised {N['value']}"})
    d, D = (pr.get("design") or {}), (ci.get("design") or {})
    if d.get("value") and D.get("value"):
        ok = d["value"] == D["value"]
        out.append({"check": "design", "state": "PASS" if ok else "FAIL",
                    "detail": f"row prints {d['value']}; cited trial is {D['value']}"})
    e, E = (pr.get("effect") or {}), (ci.get("effect") or {})
    if e.get("point") is not None and E.get("point") is not None:
        opposite = (e["point"] > 0) != (E["point"] > 0) and e["point"] != 0 and E["point"] != 0
        outside = E.get("ci_low") is not None and not (E["ci_low"] <= e["point"] <= E["ci_high"])
        ok = not (opposite and outside)
        held = "REPORTED_NOT_HELD" not in {ev.get("state") for ev in (e.get("evidence") or []) + (E.get("evidence") or [])}
        out.append({"check": "direction", "state": "PASS" if ok else "FAIL",
                    "detail": f"row {e['point']} vs cited trial {E['point']} ({E.get('ci_low')} to {E.get('ci_high')})"
                              + ("" if held else "; one side REPORTED_NOT_HELD")})
    return out


def assess(doc: Optional[dict]) -> Optional[dict]:
    if not doc:
        return None
    rows = []
    for r in doc.get("rows") or []:
        cs = _checks(r)
        rows.append({"row": r["row"], "cites": r.get("cites"), "checks": cs,
                     "state": IMPLAUSIBLE if any(c["state"] == "FAIL" for c in cs) else
                              ("PLAUSIBLE" if cs else "NOT_CHECKED")})
    bad = [r for r in rows if r["state"] == IMPLAUSIBLE]
    out = {"rows": rows,
           "numerical_validation": ({"state": "WITHHELD", "why": f"{len(bad)} comparator row(s) {IMPLAUSIBLE} against "
                                     "the trials they cite: " + ", ".join(r["row"] for r in bad)}
                                    if bad else {"state": "ALLOWED"})}
    # V1.0.1 (finerenone review): one pooled comparator result must use ONE definition across its rows. Ghosal &
    # Sinha's Fig 3B pools FIDELIO's TREATMENT-RELATED hyperkalaemia (333/135) with FIGARO's INVESTIGATOR-REPORTED
    # hyperkalaemia (396/193) -> COMPARATOR_DEFINITION_MIX; nothing of ours is validated against that outcome
    mixes = []
    for dc in doc.get("definition_checks") or []:
        defs = {r["row"]: r.get("matched_definition") for r in dc.get("rows") or []}
        known = {v for v in defs.values() if v}
        if len(known) > 1:
            states = {ev.get("state", "HELD") for r in dc["rows"] for ev in
                      (r.get("printed_evidence") or []) + (r.get("definition_evidence") or [])}
            mixes.append({"code": "COMPARATOR_DEFINITION_MIX", "outcome": dc["outcome"], "where": dc.get("where"),
                          "definitions": defs, "counts": {r["row"]: r.get("printed_counts") for r in dc["rows"]},
                          "evidence_states": sorted(states), "note": dc.get("note")})
    if mixes:
        out["definition_mixes"] = mixes
        out["numerical_validation_by_outcome"] = {m["outcome"]: {"state": "WITHHELD", "why": "COMPARATOR_DEFINITION_MIX: "
                                                  + ", ".join(f"{k} {v}" for k, v in m["definitions"].items())}
                                                  for m in mixes}
    om = doc.get("outcome_membership")
    if om:
        tot = sum(om.get("row_n", {}).values())
        stated = om.get("stated_participants")
        out["outcome_membership"] = dict(om, arithmetic=("MATCH" if stated is None or tot == stated else "MISMATCH"),
                                         row_n_total=tot)
    return out


def apply_to_panel(panel_entry: dict, assessed: Optional[dict], outcome_name: str) -> None:
    """Outcome-level membership: the comparator's result for OUR outcome pools only the listed rows. Applied only
    when the rows' printed n add up to the participants the comparator states for that result."""
    om = (assessed or {}).get("outcome_membership")
    if not om or om.get("arithmetic") != "MATCH":
        return
    label = om["endpoint_label"]
    panel_entry.setdefault("outcome_endpoints", {})[outcome_name] = label
    members = set(om["members"])
    for m in panel_entry.get("trial_set") or []:
        m["endpoint"] = label if m["family_id"] in members else om.get("other_label", "another analysis of the comparator")
        m["endpoint_basis"] = "comparator_row_checks.json outcome_membership (row n sum = stated participants)"


def render(assessed: Optional[dict]) -> str:
    import html
    if not assessed:
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    items = "".join(
        f"<li><strong>{e(r['row'])}</strong> (cites {e(r.get('cites'))}): <code>{e(r['state'])}</code>"
        + "".join(f"; {e(c['check'])} {e(c['state'])} ({e(c['detail'])})" for c in r["checks"]) + "</li>"
        for r in assessed["rows"])
    nv = assessed["numerical_validation"]
    head = ("<p><strong>Numerical validation against this comparator is WITHHELD</strong>: " + e(nv["why"]) + ".</p>"
            if nv["state"] == "WITHHELD" else "")
    for m in assessed.get("definition_mixes") or []:
        head += (f"<p><code>COMPARATOR_DEFINITION_MIX</code> ({e(m['outcome'])}, {e(m.get('where'))}): the pooled rows use "
                 "different definitions -- " + e("; ".join(f"{k}: {m['counts'].get(k)} ({v})" for k, v in m["definitions"].items()))
                 + f" [evidence: {e(', '.join(m['evidence_states']))}]. <strong>Numerical validation against this comparator "
                 f"is WITHHELD for {e(m['outcome'])}</strong>.</p>")
    om = assessed.get("outcome_membership")
    omh = (f"<p class='small'>Outcome-level membership: the comparator's result for this outcome pools "
           f"{e(', '.join(om['members']))} ({e(om['arithmetic'])}: row n total {e(om['row_n_total'])} vs stated "
           f"{e(om.get('stated_participants'))}).</p>") if om else ""
    return ("<div class='comparator-rows'><h5>Comparator rows checked against the trials they cite</h5>" + head
            + f"<ul>{items}</ul>" + omh + "</div>")
