"""COMPOSITE LABEL of a served pooled result, DERIVED from the typed component sets of its inputs (lane NR V1.0.1;
statins-older-adults review addendum).

A pooled composite may be called '3-point MACE' only when every input's typed component set IS the canonical 3-point set
(cardiovascular death, myocardial infarction, stroke). The statins pool mixes JUPITER's 5-component primary (MI, stroke,
arterial revascularisation, hospitalisation for unstable angina, CV death) with STAREE's 4-component one (CV death,
nonfatal MI, stroke, coronary revascularisation): its label is 'trial-defined composites that differ', never an
unqualified 3-point label, whatever the topic's outcome name says.

Each input's set comes from, in order:
  1. the row's own typed components bound to its definition span (the endpoint module's binding);
  2. otherwise the SOLE definition-bearing sentence in the held abstract (target_endpoint._definition_sentences --
     background text never defines), recorded as such because the result row itself is not bound to it;
  3. otherwise UNTYPED -- which is stated, never guessed.
The component vocabulary does not distinguish arterial from coronary revascularisation, so the label says
'revascularisation' and each input keeps its definition span for the reader.
"""
from __future__ import annotations

import re
from typing import Any

CANONICAL_3P = frozenset({"cardiovascular death", "myocardial infarction", "stroke"})
IDENTICAL_3P, IDENTICAL, DIFFER, UNTYPED = "IDENTICAL_3P", "IDENTICAL", "DIFFER", "UNTYPED"
RULE_ID = "composite_label:typed_input_sets_v1"

# a served name or label that CLAIMS a 3-point composite ('3-point MACE', 'three-point major adverse cardiovascular events')
THREE_POINT_CLAIM = re.compile(r"\b(?:3|three)[\s-]*point\s+(?:mace|major\s+adverse\s+cardiovascular\s+events?)\b", re.I)
MACE_CLAIM = re.compile(r"\bmace\b|\bmajor\s+(?:adverse\s+)?(?:cardio)?vascular\s+events?\b", re.I)
_COMPOSITE_NAME = re.compile(r"\bmace\b|\bmajor\s+(?:adverse\s+)?(?:cardio)?vascular\b|\bcomposite\b|\bcardiovascular\s+events\b",
                             re.I)
_STROKE_SUBTYPE = re.compile(r"\b(isch(?:a)?emic|ha?emorrhagic)\s+stroke\b", re.I)
_DISPLAY = {"cardiovascular death": "CV death", "myocardial infarction": "MI", "coronary revascularization": "revascularisation",
            "coronary heart disease death": "CHD death", "ischemic stroke": "ischaemic stroke",
            "hemorrhagic stroke": "haemorrhagic stroke",
            "unstable angina": "unstable angina"}


def _norm_token(tok: str) -> set[str]:
    """One stored component token ('CHD_DEATH', 'cardiovascular death', 'MI') as parser vocabulary."""
    from . import target_endpoint as te
    text = str(tok or "").replace("_", " ").strip()
    if text.lower() == "mi":
        text = "myocardial infarction"
    if text.lower() == "chd death":
        text = "death from coronary heart disease"
    got = set(te._components_from_text(text, expand_named_composites=False))
    # the vocabulary folds a stroke SUBTYPE into 'stroke'; ischaemic vs all stroke is a real difference that must stay
    # visible (VESALIUS-CV, PCSK9 review), so a subtype-qualified stroke keeps its subtype
    sub = _STROKE_SUBTYPE.search(text)
    if sub and "stroke" in got:
        got = (got - {"stroke"}) | {sub.group(1).lower().replace("ischaemic", "ischemic").replace("haemorrhagic", "hemorrhagic")
                                     + " stroke"}
    return got if got else ({text.lower()} if text else set())


def _row_set(t: dict[str, Any], record: dict[str, Any] | None) -> dict[str, Any]:
    comps = [c for c in (t.get("components") or []) if str(c).strip()]
    span = t.get("endpoint_definition_span")
    if comps and span:
        s: set[str] = set()
        for c in comps:
            s |= _norm_token(c)
        return {"components": sorted(s), "basis": "row bound to its definition span", "span": span}
    from . import target_endpoint as te
    defs = te._definition_sentences((record or {}).get("abstract") or "")
    sets = {frozenset(d["components"]) for d in defs if d.get("components") and len(d["components"]) >= 2}
    if len(sets) == 1:
        d = next(d for d in defs if frozenset(d["components"]) in sets)
        return {"components": sorted(next(iter(sets))), "span": d["span"],
                "basis": "the sole definition-bearing sentence in the held abstract (the result row is not bound to it)"}
    return {"components": None, "span": None,
            "basis": ("no definition-bearing sentence in the held abstract" if not sets else
                      f"{len(sets)} different definitions in the held abstract and the row is not bound to one")}


def _name(t: dict[str, Any]) -> str:
    return str(t.get("id") or t.get("label") or "")


def _all_inputs(k: int) -> str:
    return "its single input" if k == 1 else f"all {k} inputs"


def _show(components: list[str]) -> str:
    return ", ".join(_DISPLAY.get(c, c) for c in components)


def is_composite(outcome_name: str | None, inputs: list[dict[str, Any]]) -> bool:
    return bool(_COMPOSITE_NAME.search(outcome_name or "")) or any(
        len(i.get("components") or []) >= 2 for i in inputs)


def derive(outcome_name: str | None, trials: list[dict[str, Any]], rec_by_id: dict[str, Any] | None) -> dict[str, Any] | None:
    """{'kind', 'label', 'inputs', 'rule_id'} for a pooled composite, else None."""
    if not trials:
        return None
    inputs = []
    for t in trials:
        pid = str(t.get("id", "")).replace("PMID ", "").strip()
        rec = (rec_by_id or {}).get(pid) or (rec_by_id or {}).get(str(t.get("label") or ""))
        inputs.append({"trial": _name(t), **_row_set(t, rec)})
    if not is_composite(outcome_name, inputs):
        return None
    k = len(inputs)
    untyped = [i["trial"] for i in inputs if not i["components"]]
    distinct = {frozenset(i["components"]) for i in inputs if i["components"]}
    if untyped:
        kind = UNTYPED
        label = "trial-defined composites; component set not typed for " + ", ".join(untyped)
    elif len(distinct) == 1 and next(iter(distinct)) == CANONICAL_3P:
        kind = IDENTICAL_3P
        label = f"3-point MACE ({_show(sorted(CANONICAL_3P))}), the same typed component set in {_all_inputs(k)}"
    elif len(distinct) == 1:
        kind = IDENTICAL
        label = f"composite of {_show(sorted(next(iter(distinct))))}, the same typed component set in {_all_inputs(k)}"
    else:
        kind = DIFFER
        label = "trial-defined composites that differ (" + "; ".join(
            f"{i['trial']}: {_show(i['components'])}" for i in inputs) + ")"
    return {"kind": kind, "label": label, "inputs": inputs, "rule_id": RULE_ID}


def mace_claim(name: str | None) -> str | None:
    """'3P' when the name claims a 3-point composite, 'MACE' when it names MACE / major (adverse) cardiovascular or
    vascular events without a count, else None."""
    if THREE_POINT_CLAIM.search(name or ""):
        return "3P"
    return "MACE" if MACE_CLAIM.search(name or "") else None


def needs_qualification(name: str | None, kind: str | None) -> bool:
    """A 3-point name needs its qualification unless every input is the canonical 3-point set; a MACE name needs it when
    the inputs' sets differ or are not typed."""
    claim = mace_claim(name)
    if claim == "3P":
        return kind != IDENTICAL_3P
    return claim == "MACE" and kind in (DIFFER, UNTYPED)


def served_name(outcome: dict[str, Any]) -> str:
    """The outcome name as served: qualified by the derived label whenever the name claims more than its inputs earn."""
    name = str(outcome.get("name") or "")
    cl = outcome.get("composite_label") or {}
    if cl and needs_qualification(name, cl.get("kind")):
        head = "not a common 3-point set" if mace_claim(name) == "3P" else "as served"
        return f"{name} [{head}: {cl.get('label')}]"
    return name


def _in_page(text: str, page: str) -> bool:
    import html as _h
    return text in page or _h.escape(text, quote=False) in page or _h.escape(text) in page


def violations(review: dict[str, Any], html: str | None = None) -> list[str]:
    """Gate: no served pooled composite carries an unqualified MACE / 3-point label its inputs do not earn."""
    bad = []
    for o in review.get("outcomes") or []:
        cl = o.get("composite_label")
        if not cl:
            continue
        if cl.get("kind") != IDENTICAL_3P and THREE_POINT_CLAIM.search(str(cl.get("label") or "")):
            bad.append(f"{o.get('name')}: derived label claims 3-point but kind is {cl.get('kind')}")
        if needs_qualification(o.get("name"), cl.get("kind")) and html is not None and not _in_page(served_name(o), html):
            bad.append(f"{o.get('name')}: served without its qualification ({cl.get('kind')})")
    return bad


def audit(review: dict[str, Any], records: dict[str, Any] | None, html: str | None = None) -> dict[str, Any]:
    """Detector for pre-fix and post-fix outputs alike: every POOLED composite result, its derived kind (recomputed here
    from the rows and held records, not read from the review), and whether it is served with an unqualified MACE label."""
    rows = []
    for o in review.get("outcomes") or []:
        res = o.get("result") or {}
        if not res.get("k") or res.get("present") is False or res.get("suppressed_incompatible"):
            continue
        d = derive(o.get("name"), o.get("trials") or [], records)
        if not d:
            continue
        name = str(o.get("name") or "")
        need = needs_qualification(name, d["kind"])
        qualified = bool(o.get("composite_label")) and (html is None or _in_page(served_name(o), html))
        rows.append({"outcome": name, "primary": bool(o.get("primary")), "claim": mace_claim(name), "kind": d["kind"],
                     "needs_qualification": need, "unqualified": bool(need and not qualified), "label": d["label"]})
    return {"pooled_composites": rows, "unqualified": [r for r in rows if r["unqualified"]]}


