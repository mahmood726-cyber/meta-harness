"""Is the published comparator asking OUR question? (V1.0.1, DPP-4 review)

Patoulias 2021 was labelled "same question" on drug class and population alone. It includes CAROLINA (linagliptin vs
GLIMEPIRIDE, an active control), pools individual outcomes rather than 3-point MACE, and reports risk ratios. A
comparator is SAME_QUESTION only when CONTROL, ENDPOINT, EFFECT MEASURE, POPULATION and INTERVENTION all agree with
ours. Any dimension checked and found to DIFFER makes it a RELATED_TRIAL_INVENTORY_MAP (its trial list is still a map
of the evidence; its result answers a different question) -- a broader or narrower population/intervention included.
With nothing found to differ but something unchecked, or with no checked record, the label is NOT_ESTABLISHED --
class and population alone never earn "same question". A dimension may be recorded NOT_ESTABLISHED without evidence;
YES and NO need located evidence.

cache/<slug>/comparator_question.json holds each dimension as {ours, theirs, agrees, evidence:[{document_ref, quote,
record_id?}]}; every quote is located in held bytes (tags ignored for XML/HTML) or the record is refused. The LABEL is
derived here from the dimensions, never read from the file.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

DIMS = ("control", "endpoint", "effect_measure", "population", "intervention")
SAME, RELATED, NOT_EST = "SAME_QUESTION", "RELATED_TRIAL_INVENTORY_MAP", "NOT_ESTABLISHED"
WORDS = {SAME: "same question", RELATED: "related: trial-inventory map", NOT_EST: "same question not established"}


class QuestionRefused(ValueError):
    pass


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def _held(root: Path, ev: dict) -> str:
    p = root / ev["document_ref"]
    if ev.get("record_id"):
        recs = json.loads(p.read_text(encoding="utf-8"))
        return next((str(r.get(ev.get("field") or "abstract") or "") for v in recs.values() if isinstance(v, list)
                     for r in v if isinstance(r, dict) and str(r.get("id")) == str(ev["record_id"])), "")
    if ev.get("field"):
        return str(json.loads(p.read_text(encoding="utf-8")).get(ev["field"]) or "")
    return p.read_text(encoding="utf-8")


def load(root, slug) -> Optional[dict]:
    root = Path(root)
    p = root / "cache" / slug / "comparator_question.json"
    if not p.exists():
        return None
    doc = json.loads(p.read_text(encoding="utf-8"))
    for dim in DIMS:
        d = (doc.get("dimensions") or {}).get(dim)
        if not d:
            raise QuestionRefused(f"{slug}: dimension {dim} missing")
        if d.get("agrees") not in ("YES", "NO", "NOT_ESTABLISHED"):
            raise QuestionRefused(f"{slug}: {dim}.agrees must be YES, NO or NOT_ESTABLISHED")
        if d["agrees"] != "NOT_ESTABLISHED" and not d.get("evidence"):
            raise QuestionRefused(f"{slug}: {dim} is {d['agrees']} without evidence")
        for ev in d.get("evidence") or []:
            held = _held(root, ev)
            if ev["quote"] not in held and _norm(ev["quote"]) not in _norm(held):
                raise QuestionRefused(f"{slug}: {dim} quote not located in {ev['document_ref']}: {ev['quote'][:60]}")
    return doc


_SCALE = {"RR": "RR", "RISK RATIO": "RR", "RELATIVE RISK": "RR", "OR": "OR", "ODDS RATIO": "OR", "HR": "HR",
          "HAZARD RATIO": "HR", "MD": "MD", "WMD": "MD", "MEAN DIFFERENCE": "MD", "SMD": "SMD", "RD": "RD"}


def effect_measure(ours_scale, reported: list, primary_name: str) -> dict:
    """The EFFECT MEASURE dimension, derived from served data, never from a record: our pooled primary scale vs the
    scale of the comparator's reported result for that outcome (its first reported row when none is named alike)."""
    row = next((r for r in reported or [] if str(r.get("outcome") or "").lower() == str(primary_name or "").lower()),
               (reported or [None])[0])
    a = _SCALE.get(str(ours_scale or "").upper())
    b = _SCALE.get(str((row or {}).get("scale") or "").upper())
    if not a or not b:
        return {"ours": ours_scale, "theirs": (row or {}).get("scale"), "agrees": "NOT_ESTABLISHED", "derived": True,
                "why": "our pooled scale or the comparator's reported scale is not a single known measure"}
    return {"ours": a, "theirs": b, "agrees": "YES" if a == b else "NO", "derived": True,
            "why": f"our served pooled {a} vs the comparator's reported {b} ({(row or {}).get('outcome')})"}


def decide(doc: Optional[dict], measure: Optional[dict] = None) -> dict:
    if doc and measure and measure["agrees"] in ("YES", "NO"):
        doc = dict(doc, dimensions=dict(doc["dimensions"], effect_measure=measure))
    elif measure and measure["agrees"] == "NO":
        # no checked record, but the served data alone show a different effect measure
        doc = {"dimensions": {**{k: {"agrees": "NOT_ESTABLISHED"} for k in DIMS}, "effect_measure": measure}}
    if not doc:
        return {"label": NOT_EST, "words": WORDS[NOT_EST],
                "why": "control, endpoint and effect measure have not been checked against the comparator; drug class "
                       "and population alone do not make it the same question"}
    a = {k: doc["dimensions"][k]["agrees"] for k in DIMS}
    if all(v == "YES" for v in a.values()):
        label = SAME
    elif "NO" in a.values():
        label = RELATED
    else:
        label = NOT_EST
    differs = [k for k in DIMS if a[k] == "NO"]
    unknown = [k for k in DIMS if a[k] == "NOT_ESTABLISHED"]
    return {"label": label, "words": WORDS[label], "agrees": a, "differs": differs, "not_established": unknown,
            "dimensions": doc["dimensions"],
            "why": (("differs on " + ", ".join(differs)) if differs else "") +
                   ((("; " if differs else "") + "not established: " + ", ".join(unknown)) if unknown else "")}


def apply_to_scope(scope: dict, decision: dict) -> dict:
    """The scope object keeps its intervention-level / population checks; 'scope_valid' (served as 'same question')
    additionally requires the same-question label."""
    out = dict(scope)
    out["same_question"] = decision
    if scope.get("scope_valid") and decision["label"] != SAME:
        out["scope_valid"] = False
        out["note"] = (f"{decision['words']} -- {decision['why']}. Class and population match; that alone is not the "
                       "same question")
    return out


def render(scope: dict) -> str:
    import html
    sq = (scope or {}).get("same_question")
    if not sq or not sq.get("dimensions"):
        return ""
    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    rows = "".join(
        f"<tr><td>{e(k)}</td><td>{e(d.get('ours'))}</td><td>{e(d.get('theirs'))}</td><td><code>{e(d['agrees'])}</code>"
        + (f"<br><span class='small'>derived: {e(d.get('why'))}</span>" if d.get("derived") else "")
        + "".join(f"<br><span class='small'>&ldquo;{e(ev['quote'])}&rdquo; ({e(ev['document_ref'])})</span>"
                  for ev in (d.get("evidence") or [])[:2]) + "</td></tr>"
        for k, d in ((k, sq["dimensions"][k]) for k in DIMS if k in sq["dimensions"]))   # fixed order: renders
        # must be byte-identical after a canonical (key-sorted) JSON round trip
    return (f"<div class='same-question'><p><strong>{e(sq['words'])}</strong> ({e(sq['label'])}): {e(sq['why'])}.</p>"
            "<table><thead><tr><th>Dimension</th><th>Ours</th><th>Comparator</th><th>Agrees</th></tr></thead><tbody>"
            + rows + "</tbody></table></div>")
