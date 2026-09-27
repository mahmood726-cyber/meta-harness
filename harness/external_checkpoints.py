"""External checkpoints (V1.0.1, finerenone review): a published result that pools the SAME trials as ours, shown beside
our result as a checkpoint -- never an exact target, never an input.

FIDELITY (Agarwal 2022, PMID 35023547) is the prespecified individual-patient pooled analysis of FIDELIO-DKD and
FIGARO-DKD. For the composite of kidney failure, a sustained >=40% eGFR decrease or renal death it reports HR 0.85
(0.77-0.93). Our pool of the same two trials' published results is an aggregate re-analysis; a small difference is
expected (individual-patient vs published-HR pooling, follow-up, model). The checkpoint is therefore DESCRIBED (the
log-HR distance and whether the intervals overlap), never scored pass/fail, and it may never enter our pool as a third
trial: a checkpoint whose PMID is among our pooled rows or family reports refuses the build.

cache/<slug>/external_checkpoints.json holds each checkpoint with a verbatim quote located in held bytes.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Optional


class CheckpointRefused(ValueError):
    pass


def _norm(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", str(s or ""))).strip()


def load(root, slug) -> list:
    p = Path(root) / "cache" / slug / "external_checkpoints.json"
    if not p.exists():
        return []
    doc = json.loads(p.read_text(encoding="utf-8"))
    for c in doc.get("checkpoints") or []:
        if c.get("role") != "EXTERNAL_CHECKPOINT":
            raise CheckpointRefused(f"{slug}: {c.get('name')}: role must be EXTERNAL_CHECKPOINT")
        ev = c["evidence"]
        held = (Path(root) / ev["document_ref"]).read_text(encoding="utf-8")
        if _norm(ev["quote"]) not in _norm(held):
            raise CheckpointRefused(f"{slug}: {c['name']}: quote not located in {ev['document_ref']}")
    return doc.get("checkpoints") or []


def attach(review: dict, checkpoints: list) -> list:
    out = []
    prim = next((o for o in review.get("outcomes") or [] if o.get("primary")), {})
    pooled_ids = {str(t.get("label")) for t in prim.get("trials") or []} | {str(t.get("id")) for t in prim.get("trials") or []}
    family_reports = {str(r.get("report_id")) for f in review.get("trial_families") or [] for r in f.get("reports") or []}
    res = prim.get("result") or {}
    for c in checkpoints:
        if str(c["pmid"]) in pooled_ids or f"PMID {c['pmid']}" in pooled_ids or str(c["pmid"]) in family_reports:
            raise CheckpointRefused(f"{c['name']} (PMID {c['pmid']}) is an external checkpoint and may never be an input")
        row = dict(c)
        ours = (res.get("estimate"), res.get("ci_low"), res.get("ci_high"))
        if isinstance(ours[0], (int, float)) and ours[0] > 0 and res.get("scale") == c.get("scale"):
            has_ci = all(isinstance(v, (int, float)) and v > 0 for v in ours[1:])
            row["comparison"] = {"ours": {"estimate": ours[0], "ci_low": ours[1], "ci_high": ours[2]},
                                 "log_distance": round(math.log(ours[0]) - math.log(c["estimate"]), 4),
                                 "intervals_overlap": (not (ours[2] < c["ci_low"] or c["ci_high"] < ours[1])) if has_ci
                                 else "NOT_ASSESSABLE (our interval is not served)",
                                 "our_point_inside_checkpoint_ci": c["ci_low"] <= ours[0] <= c["ci_high"],
                                 "reading": "a checkpoint, not a target: no pass/fail is scored"}
        else:
            row["comparison"] = {"state": "NOT_COMPARABLE", "why": "our pooled result is absent or on another scale"}
        out.append(row)
    return out


def render(rows: Optional[list]) -> str:
    import html
    if not rows:
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    items = []
    for c in rows:
        cmp_ = c.get("comparison") or {}
        ours = cmp_.get("ours")
        items.append(
            f"<li><strong>{e(c['name'])}</strong> (PMID {e(c['pmid'])}; {e(c['what'])}): {e(c['scale'])} {e(c['estimate'])} "
            f"({e(c['ci_low'])} to {e(c['ci_high'])}) &mdash; &ldquo;{e(c['evidence']['quote'])}&rdquo;. "
            + (f"Ours: {e(c['scale'])} {e(ours['estimate'])}" + (f" ({e(ours['ci_low'])} to {e(ours['ci_high'])})" if ours.get('ci_low') else "")
               + f"; log distance {e(cmp_['log_distance'])}; intervals overlap: {e(cmp_['intervals_overlap'])}; our point inside "
               f"the checkpoint interval: {e(cmp_['our_point_inside_checkpoint_ci'])}. {e(cmp_['reading'])}." if ours else e(cmp_.get("why", "")))
            + "</li>")
    return ("<div class='external-checkpoints'><h5>External checkpoints (never a target, never an input)</h5><ul>"
            + "".join(items) + "</ul></div>")
