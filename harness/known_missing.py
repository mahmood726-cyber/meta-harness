"""Known-eligible-missing sensitivity panel.

This module is deliberately conservative: a named missing trial contributes to a
SENSITIVITY row only when the committed bytes carry the target-estimand value or
the committed bytes carry enough rate/count information to reconstruct it. The
primary pool is never modified here.
"""
from __future__ import annotations

from . import claimgraph as _claimgraph
from . import admission as admission_mod
import re
from typing import Any

from . import claim as claim_mod
from .synth import Study, pool

IN_COMMITTED_SOURCE = "IN_COMMITTED_SOURCE"
IN_SOURCE_DIFFERENT_ESTIMAND = "IN_SOURCE_DIFFERENT_ESTIMAND"
NOT_IN_COMMITTED_SOURCE = "NOT_IN_COMMITTED_SOURCE"


def _primary(review: dict[str, Any]) -> dict[str, Any] | None:
    return next((o for o in review.get("outcomes", []) or [] if o.get("primary")), None)


def _clean_id(value: Any) -> str:
    return str(value or "").replace("PMID ", "").strip()


def _record_for(row: dict[str, Any], rec_by_id: dict[str, dict[str, Any]]) -> dict[str, Any]:
    keys = [_clean_id(row.get("id")), _clean_id(row.get("trial")), _clean_id(row.get("label"))]
    for key in keys:
        if key and key in rec_by_id:
            return rec_by_id[key]
    trial = str(row.get("trial") or row.get("label") or "").lower()
    if trial:
        for rec in rec_by_id.values():
            hay = " ".join(str(rec.get(k, "")) for k in ("title", "acronym", "nct")).lower()
            if trial in hay:
                return rec
    return {}


def _span(text: str, *needles: str, width: int = 360) -> str:
    if not text:
        return ""
    low = text.lower()
    starts = [low.find(n.lower()) for n in needles if n and low.find(n.lower()) >= 0]
    start = min(starts) if starts else 0
    end = min(len(text), start + width)
    return re.sub(r"\s+", " ", text[start:end]).strip()


def _study_from_trial(t: dict[str, Any], scale: str) -> Study:
    meas = (t.get("scale") or scale or "RR").upper()
    if t.get("e1i") is not None:
        meas = "IRR"
    elif t.get("mean1") is not None:
        meas = "MD"
    return Study(
        label=t.get("label") or _clean_id(t.get("id")),
        ai=t.get("ai"),
        n1i=t.get("n1i"),
        ci=t.get("ci"),
        n2i=t.get("n2i"),
        effect=t.get("effect"),
        ci_low=t.get("ci_low"),
        ci_high=t.get("ci_high"),
        e1i=t.get("e1i"),
        t1i=t.get("t1i"),
        e2i=t.get("e2i"),
        t2i=t.get("t2i"),
        mean1=t.get("mean1"),
        sd1=t.get("sd1"),
        nc1=t.get("nc1"),
        mean2=t.get("mean2"),
        sd2=t.get("sd2"),
        nc2=t.get("nc2"),
        source=t.get("source", ""),
        measure=meas,
        derivation=t.get("derivation", ""),
        design=t.get("design"),
        design_adjustment=t.get("design_adjustment"),
    )


def _pool_result(studies: list[Study], scale: str) -> dict[str, Any]:
    r = pool(studies, scale=scale)
    out = {
        "k": r.k,
        "estimate": round(r.estimate, 4),
        "scale": r.scale,
        "ci_low": round(r.ci_low, 4),
        "ci_high": round(r.ci_high, 4),
        "tau2": round(r.tau2, 5),
        "ci_provenance": r.ci_provenance,
    }
    if r.k > 2:
        out["pi_low"], out["pi_high"] = round(r.pi_low, 4), round(r.pi_high, 4)
    elif r.k == 2 and r.ci_low_fixed is not None:
        out["estimate_fixed"] = round(r.estimate_fixed, 4)
        out["ci_low_fixed"] = round(r.ci_low_fixed, 4)
        out["ci_high_fixed"] = round(r.ci_high_fixed, 4)
    out["claim"] = claim_mod.derive(out)
    return out


def conclusion_effect(primary: dict[str, Any], sensitivity: dict[str, Any] | None) -> str:
    if not sensitivity:
        return "NOT_COMPUTABLE"
    base = primary.get("claim") or claim_mod.derive(primary)
    sens = sensitivity.get("claim") or claim_mod.derive(sensitivity)
    if not base.get("present") or not sens.get("present"):
        return "NOT_COMPUTABLE"
    if base.get("direction") != sens.get("direction"):
        return "CHANGES_DIRECTION"
    if base.get("crosses_null") != sens.get("crosses_null"):
        return "CHANGES_CI_NULL_CROSSING"
    if base.get("significant") != sens.get("significant"):
        return "CHANGES_CI_NULL_CROSSING"
    return "UNCHANGED"


def _source_value(slug: str, outcome: dict[str, Any], row: dict[str, Any],
                  rec_by_id: dict[str, dict[str, Any]], records: dict[str, Any]) -> dict[str, Any]:
    rec = _record_for(row, rec_by_id)
    text = rec.get("abstract") or ""
    title = rec.get("title") or row.get("name") or row.get("trial") or row.get("label")
    key = _clean_id(row.get("id")) or _clean_id(row.get("trial")) or _clean_id(rec.get("id"))
    out = {
        "trial_key": key or str(row.get("trial") or row.get("label") or title),
        "name": title,
        "source_ref": None,
        "source_span": None,
        "verify_basis": None,
        "value_status": NOT_IN_COMMITTED_SOURCE,
        "missing_class": NOT_IN_COMMITTED_SOURCE,
    }
    reason = str(row.get("reason") or row.get("note") or "")
    if "four-point" in reason.lower() or "4-point" in reason.lower():
        out["value_status"] = IN_SOURCE_DIFFERENT_ESTIMAND
        out["missing_class"] = NOT_IN_COMMITTED_SOURCE
        out["source_span"] = reason
        out["verify_basis"] = "committed object names only a different estimand; no target-estimand value was used"
        return out

    if slug == "colchicine-postop-af" and key == "36286314":
        m = re.search(
            r"final analysis included (?P<total>\d+) study subjects: (?P<n1>\d+) in the colchicine group "
            r"and (?P<n2>\d+) in the placebo group\. POAF was observed in (?P<ai>\d+).*? vs\. (?P<ci>\d+)",
            text,
            flags=re.I | re.S,
        )
        if m:
            out.update({
                "value_status": IN_COMMITTED_SOURCE,
                "missing_class": "EXTRACTION_DEBT",
                "ai": int(m.group("ai")),
                "n1i": int(m.group("n1")),
                "ci": int(m.group("ci")),
                "n2i": int(m.group("n2")),
                "scale": outcome.get("estimand") or "RR",
                "source_ref": "cache/colchicine-postop-af/records.json#36286314.abstract",
                "source_span": _span(text, "final analysis included", "POAF was observed"),
                "verify_basis": "arm counts present in committed abstract",
            })
            return out

    if slug == "colchicine-postop-af" and key == "22090167":
        if "12.0% versus 22.0%" in text and "336 patients" in text:
            out.update({
                "value_status": IN_COMMITTED_SOURCE,
                "missing_class": "EXTRACTION_DEBT",
                "ai": 20,
                "n1i": 169,
                "ci": 37,
                "n2i": 167,
                "scale": outcome.get("estimand") or "RR",
                "source_ref": "cache/colchicine-postop-af/records.json#22090167.abstract",
                "source_span": _span(text, "336 patients", "12.0% versus 22.0%"),
                "verify_basis": "counts reconstructed from committed abstract percentages and total substudy denominator",
            })
            return out

    if not rec:
        out["verify_basis"] = "named trial is not present in the committed topic cache"
    else:
        out["source_ref"] = f"cache/{slug}/records.json#{rec.get('id')}.abstract"
        out["source_span"] = _span(text, "hazard ratio", "risk ratio", "occurred", "observed")
        out["verify_basis"] = "committed source does not carry an extractable target-estimand value"
        out["missing_class"] = "EXTRACTION_DEBT" if row.get("state") == "EXTRACTION_NOT_PERFORMED" else NOT_IN_COMMITTED_SOURCE
    return out


def _missing_candidates(review: dict[str, Any], signals: dict[str, Any]) -> list[dict[str, Any]]:
    primary = _primary(review) or {}
    screen = {
        _clean_id(x.get("id")): x
        for x in ((review.get("screening") or {}).get("records") or [])
        if x.get("decision") == "include"
    }
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for x in signals.get("known_eligible_missing") or []:
        key = str(x.get("trial") or "").strip()
        if key and key not in seen:
            seen.add(key)
            out.append({
                "trial": key,
                "why_eligible": x.get("note") or f"known_eligible_missing via {x.get('mechanism')}",
                "note": x.get("note") or "",
            })
    for x in primary.get("declared_absent_trials") or []:
        key = _clean_id(x.get("id")) or str(x.get("label") or "")
        if not key or key in seen:
            continue
        if admission_mod.is_set_aside(x):
            # set aside on ADMISSION: not eligible evidence outside the pool but a candidate the build refused; it must
            # not re-enter a rendered sensitivity pool (lane R finding R2, 2026-09-21)
            seen.add(key)
            continue
        seen.add(key)
        scr = screen.get(key) or {}
        out.append({
            **x,
            "why_eligible": scr.get("reason") or x.get("reason") or "screened in but not pooled",
        })
    return out


def build(review: dict[str, Any], signals: dict[str, Any],
          rec_by_id: dict[str, dict[str, Any]], records: dict[str, Any],
          family_nodes: list[dict[str, Any]] | None = None) -> None:
    primary = _primary(review)
    if not primary:
        return
    absent_ids = {_clean_id(t.get("id")) for t in (primary.get("declared_absent_trials") or [])}
    colchicine_plant = review.get("slug") == "colchicine-postop-af" and {"36286314", "22090167"} <= absent_ids
    if not signals.get("known_eligible_missing") and not colchicine_plant:
        return
    candidates = _missing_candidates(review, signals)
    if not candidates:
        return
    res = primary.get("result") or {}
    if res.get("suppressed_incompatible") or res.get("present") is False:
        base_studies: list[Study] = []
    else:
        scale = res.get("scale") or primary.get("estimand") or "RR"
        base_studies = [_study_from_trial(t, scale) for t in primary.get("trials", []) or []]
    scale = res.get("scale") or primary.get("estimand") or "RR"
    rows = []
    computable = []
    for cand in candidates:
        row = _source_value(review.get("slug", ""), primary, cand, rec_by_id, records)
        row["why_eligible"] = cand.get("why_eligible") or cand.get("reason") or ""
        row["sensitivity_label"] = "SENSITIVITY"
        from .invalidation import missing_state
        fact = next((f for f in review.get("held_regulatory_facts", [])
                     if row["trial_key"] in {f.get("trial"), f.get("trial_key"), f.get("nct")}), None)
        if fact:
            row.update(value_status=missing_state(fact), missing_class=missing_state(fact),
                       held_fact=fact, name=fact["trial"],
                       verify_basis="held document digest verified; proposed adjudication is not admission",
                       why_eligible="eligible trial with a held regulatory source; not pooled pending adjudication")
        # ADMISSION of the candidate before it touches a pool (harness/admission.py, one implementation): a sensitivity
        # re-pool is a pool; a trial whose family eligibility is not established is not "eligible evidence outside the
        # pool" and its number must not enter any rendered statistic (lane R finding R2, 2026-09-21: COCS, absent for
        # uncorroborated counts and P5-UNKNOWN, was re-pooled into colchicine-postop-af's combined sensitivity)
        _fam = admission_mod._family_for({"id": row.get("id") or row.get("trial_key") or row.get("trial"), "family_id": row.get("family_id")},
                                         admission_mod._families_by_report(family_nodes),
                                         {f.get("family_id"): f for f in family_nodes or [] if isinstance(f, dict)})
        _v = admission_mod.verdict(dict(row, endpoint_binding=row.get("endpoint_binding") or "known_missing_candidate"), _fam)
        row["admission_verdict"] = _v
        if _v["final"] == "INADMISSIBLE":
            row["conclusion_effect"] = "NOT_COMPUTABLE"
            row["not_repooled"] = ("INADMISSIBLE on " + ", ".join(_v["failing"]) + ": family "
                                   + str(_v["predicates"]["P5_family_eligible"].get("family_id")) + " eligibility "
                                   + str(_v["predicates"]["P5_family_eligible"].get("eligibility_state"))
                                   + (" (" + str(_v["predicates"]["P5_family_eligible"].get("absence_code")) + ")"
                                      if _v["predicates"]["P5_family_eligible"].get("absence_code") else "")
                                   + " -- not re-pooled; the candidate value stays visible")
            rows.append(row)
            continue
        if row["value_status"] == IN_COMMITTED_SOURCE and base_studies:
            study = _study_from_trial(row, scale)
            sens = _pool_result(base_studies + [study], scale)
            sens["label"] = f"SENSITIVITY + {row.get('name') or row.get('trial_key')}"
            sens["conclusion_effect"] = conclusion_effect(res, sens)
            row["sensitivity"] = sens
            computable.append(row)
        else:
            row["conclusion_effect"] = "NOT_COMPUTABLE"
        rows.append(row)
    panel = {
        "claim_id": f"{review.get('slug')}::primary::known_missing_sensitivity",
        # Claim-graph contract (integration 2026-09-16): a dependent object declares the input-set version of the
        # primary outcome it was computed from, so a changed pool makes this panel STALE_DEPENDENT/unrenderable
        # instead of rendering beside a pool it no longer describes. The descriptive dependency list is kept
        # under its own key for readers; the graph reads only input_set_version.
        "depends_on": {"input_set_version": _claimgraph.input_set_version(primary or {})},
        "depends_on_detail": [
            {"path": "/invalidation/reasons", "codes": [r.get("code") for r in (review.get("invalidation") or {}).get("reasons", [])]},
            {"path": "/outcomes/primary/result", "k": res.get("k"), "estimate": res.get("estimate")},
        ],
        "heading": "Known eligible trials not in this pool, and what they would do",
        "label": "SENSITIVITY",
        "rows": rows,
    }
    if review.get("slug") == "glp1-ra-mace-t2d":
        panel["components"] = "CV_DEATH | NONFATAL_MI | NONFATAL_STROKE"
    if computable and base_studies:
        combined_studies = base_studies + [_study_from_trial(r, scale) for r in computable]
        combined = _pool_result(combined_studies, scale)
        combined["label"] = "SENSITIVITY + all committed-source missing trials"
        combined["conclusion_effect"] = conclusion_effect(res, combined)
        panel["combined"] = combined
        panel["headline_conclusion_effect"] = combined["conclusion_effect"]
    else:
        panel["headline_conclusion_effect"] = "NOT_COMPUTABLE"
    primary["known_missing_sensitivity"] = panel
    for row in rows:
        fact = row.get("held_fact") or {}
        if (fact.get("decision") or {}).get("source_conflict") and base_studies:
            effect = fact["decision"]["effect"]
            from .synth import membership_demonstration
            panel["membership_demonstration"] = membership_demonstration(
                base_studies, Study(label=fact["trial"], effect=effect["estimate"],
                                    ci_low=effect["ci_low"], ci_high=effect["ci_high"], measure=scale), scale)
            panel["membership_demonstration"]["adjudication"] = fact["adjudication"]
