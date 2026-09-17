"""Target-endpoint selection for pooled trial rows.

The selector separates endpoint identity from numeric extraction: enumerate
held-source candidates, classify each against the registered target endpoint,
then choose the best candidate by endpoint match before source rank.  A disclosed
near-match is poolable only when no exact target exists in held source bytes.
"""
from __future__ import annotations

import re
from typing import Any

from . import extract
from .ctgov_results import _classify_arms, _num, _registry_measure_type

EXACT_TARGET = "EXACT_TARGET"
NEAR_MATCH = "NEAR_MATCH"
DIFFERENT_OUTCOME = "DIFFERENT_OUTCOME"
EXACT_TARGET_IN_SOURCE_NOT_HELD = "EXACT_TARGET_IN_SOURCE_NOT_HELD"

PUBLISHED_TARGET_EFFECT = "published_target_effect"
REGISTRY_PUBLISHED_EFFECT = "registry_published_effect"
RECONSTRUCTION = "reconstruction"

SOURCE_RANK = {
    PUBLISHED_TARGET_EFFECT: 300,
    REGISTRY_PUBLISHED_EFFECT: 200,
    RECONSTRUCTION: 100,
}


def protocol_rule_object() -> dict[str, Any]:
    return {
        "summary": (
            "Target endpoint selector: EXACT_TARGET beats NEAR_MATCH; a near-match may be pooled "
            "only when no exact target is held. Within the same endpoint class, source-reported "
            "target-estimand effects beat registry effect estimates, which beat crude reconstructions. "
            "For multiple registered primaries in the same outcome family, choose the prespecified "
            "primary whose component set is closest to the canonical review definition; ties use "
            "registration order and alternatives render as sensitivity rows. Rule applied after "
            "results were already known in this lane, so the timing is disclosed."
        ),
        "results_known_at_rule_time": True,
    }


def _fold(text: str | None) -> str:
    s = str(text or "").lower()
    replacements = {
        "hospitalisation": "hospitalization",
        "hospitalisations": "hospitalizations",
        "cardiovascular": "cardiovascular",
        "cv ": "cardiovascular ",
        "hhf": "heart failure hospitalization",
        "e-gfr": "egfr",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return re.sub(r"\s+", " ", s)


def _components_from_text(text: str | None) -> set[str]:
    s = _fold(text)
    comps: set[str] = set()
    if ("coronary heart disease death" in s or "death from coronary heart disease" in s
            or re.search(r"\bchd\b.{0,30}death|death.{0,30}\bchd\b", s)):
        comps.add("coronary heart disease death")
    if ("cardiovascular death" in s or "death from cardiovascular" in s
            or "cardiovascular causes" in s
            or re.search(r"cardiovascular.{0,30}death|death.{0,30}cardiovascular", s)
            or re.search(r"\bcv\b.*death|death.*\bcv\b", s)):
        comps.add("cardiovascular death")
    if (("heart failure" in s and "hospitalization" in s)
            or "hospitalizations due to heart failure" in s):
        comps.add("heart failure hospitalization")
    if "urgent visit" in s and ("heart failure" in s or re.search(r"\bhf\b", s)):
        comps.add("urgent heart failure visit")
    if (
        "recurrent" in s
        and ("hospitalization" in s or "event" in s)
        and (
            "rate of recurrent" in s
            or "recurrent event rate" in s
            or "total recurrent" in s
            or "first and recurrent" in s
        )
    ):
        comps.add("recurrent events")
    if "myocardial infarction" in s or re.search(r"\bmi\b", s):
        comps.add("myocardial infarction")
    if "stroke" in s:
        comps.add("stroke")
    if "unstable angina" in s:
        comps.add("unstable angina")
    if "coronary revascularization" in s or "revascularisation" in s:
        comps.add("coronary revascularization")
    if "kidney failure" in s:
        comps.add("kidney failure")
    if "kidney composite" in s or "renal composite" in s or "composite kidney outcome" in s:
        comps.update({"kidney failure", "sustained egfr decline", "renal death"})
    if "egfr" in s and any(w in s for w in ("decline", "decrease", "reduction")):
        comps.add("sustained egfr decline")
    if "renal death" in s or "death from renal" in s:
        comps.add("renal death")
    if ("mace" in s or "major adverse cardiovascular" in s or "major cardiovascular" in s):
        if not comps or "3-point" in s or "three-point" in s:
            comps.update({"cardiovascular death", "myocardial infarction", "stroke"})
        if "4-point" in s or "four-point" in s:
            comps.add("unstable angina")
    return comps


def canonical_components(spec: dict[str, Any]) -> list[str]:
    explicit = spec.get("components") or spec.get("canonical_components")
    if explicit:
        return sorted(_components_from_text(" ; ".join(map(str, explicit))) or {str(x) for x in explicit})
    return sorted(_components_from_text(spec.get("name")))


def _keyword_family_match(spec: dict[str, Any], text: str | None) -> bool:
    s = _fold(text)
    for kw in spec.get("keywords") or []:
        k = _fold(kw)
        if len(k) > 3 and k in s:
            return True
    canon = set(canonical_components(spec))
    return bool(canon and (canon & _components_from_text(text)))


def _classify(spec: dict[str, Any], text: str | None, components: set[str] | None = None) -> dict[str, Any]:
    canon = set(canonical_components(spec))
    cand = set(components or _components_from_text(text))
    if not canon:
        cls = EXACT_TARGET if _keyword_family_match(spec, text) else DIFFERENT_OUTCOME
        return {
            "target_endpoint_class": cls,
            "target_components": sorted(cand),
            "extra_components": [],
            "missing_components": [],
            "component_distance": 0 if cls == EXACT_TARGET else 999,
        }
    cand_for_match = set(cand)
    if "cardiovascular death" in canon and "coronary heart disease death" in cand:
        cand_for_match.add("cardiovascular death")
    extra = sorted(
        c for c in (cand - canon)
        if not (c == "coronary heart disease death" and "cardiovascular death" in canon)
    )
    missing = sorted(canon - cand_for_match)
    if not extra and not missing:
        cls = EXACT_TARGET
    elif cand and (not missing or not extra):
        cls = NEAR_MATCH
    else:
        cls = DIFFERENT_OUTCOME
    return {
        "target_endpoint_class": cls,
        "target_components": sorted(cand),
        "extra_components": extra,
        "missing_components": missing,
        "component_distance": len(extra) + len(missing),
    }


def _effect_analysis(om: dict[str, Any]) -> dict[str, Any] | None:
    for a in om.get("analyses") or []:
        ptype = _fold(a.get("paramType"))
        scale = None
        if "hazard ratio" in ptype or re.search(r"\bhr\b", ptype):
            scale = "HR"
        elif "risk ratio" in ptype or re.search(r"\brr\b", ptype):
            scale = "RR"
        elif "odds ratio" in ptype or re.search(r"\bor\b", ptype):
            scale = "OR"
        if not scale:
            continue
        effect = _num(a.get("paramValue"))
        lo = _num(a.get("ciLowerLimit"))
        hi = _num(a.get("ciUpperLimit"))
        if effect is not None and lo is not None and hi is not None:
            return {
                "effect": effect,
                "ci_low": lo,
                "ci_high": hi,
                "scale": scale,
                "analysis_method": a.get("statisticalMethod"),
                "analysis_param_type": a.get("paramType"),
            }
    return None


_EFFECT_RE = re.compile(
    r"\b(hazard ratio|risk ratio|relative risk|odds ratio|hr|rr|or)\b"
    r"(?:\s+for\b[^,;()]*)?\s*[:,]?\s*"
    r"(\d+(?:\.\d+)?)\s*[,;]?\s*"
    r"95%\s*(?:confidence interval\s*)?(?:\[[A-Za-z]+\]\s*)?[:,]?\s*"
    r"(\d+(?:\.\d+)?)\s*(?:to|-|–)\s*(\d+(?:\.\d+)?)",
    re.I,
)


def _published_effect_from_abstract(
    spec: dict[str, Any],
    abstract: str,
    interv: list[str],
    comp: list[str],
) -> dict[str, Any] | None:
    """Parse source-reported effect+CI phrases the legacy extractor misses."""
    try:
        sents = extract._outcome_sentences(abstract, extract._effective_kws(abstract, spec.get("keywords") or []))
    except AttributeError:
        sents = re.split(r"(?<=[.?!])\s+", abstract or "")
    for s in sents:
        if not _keyword_family_match(spec, s):
            continue
        m = _EFFECT_RE.search(s)
        if not m:
            continue
        lab = m.group(1).lower()
        if lab in ("hazard ratio", "hr"):
            scale = "HR"
        elif lab in ("odds ratio", "or"):
            scale = "OR"
        else:
            scale = "RR"
        return {
            "effect": float(m.group(2)),
            "ci_low": float(m.group(3)),
            "ci_high": float(m.group(4)),
            "scale": scale,
            "source": "abstract source-reported effect (target endpoint): " + s.strip()[:220],
        }
    return None


def _counts_from_om(om: dict[str, Any], interv: list[str], comp: list[str]) -> dict[str, Any] | None:
    groups = om.get("groups") or []
    if len(groups) < 2:
        return None
    interv_gid, comp_gid = _classify_arms(groups, [_fold(x) for x in interv], [_fold(x) for x in comp])
    if not (interv_gid and comp_gid):
        return None
    classes = om.get("classes") or []
    if not (classes and classes[0].get("categories")):
        return None
    measurements = classes[0]["categories"][0].get("measurements") or []
    values = {m.get("groupId"): _num(m.get("value")) for m in measurements}
    denoms = {}
    for d in om.get("denoms") or []:
        for c in d.get("counts") or []:
            denoms[c.get("groupId")] = _num(c.get("value"))
    ai, n1i = values.get(interv_gid), denoms.get(interv_gid)
    ci, n2i = values.get(comp_gid), denoms.get(comp_gid)
    if None in (ai, n1i, ci, n2i):
        return None
    if not (0 <= ai <= n1i and 0 <= ci <= n2i and n1i > 0 and n2i > 0):
        return None
    gi = next((g.get("title") for g in groups if g.get("id") == interv_gid), "")
    gc = next((g.get("title") for g in groups if g.get("id") == comp_gid), "")
    return {
        "ai": int(ai),
        "n1i": int(n1i),
        "ci": int(ci),
        "n2i": int(n2i),
        "intervention_arm": gi,
        "comparator_arm": gc,
    }


def _candidate_from_abstract(
    ex: dict[str, Any],
    *,
    spec: dict[str, Any],
    abstract: str,
    source_kind: str,
    source_rank_kind: str,
    source_order: int,
) -> dict[str, Any] | None:
    if not ex or ex.get("absent"):
        return None
    if not (ex.get("effect") is not None or ex.get("ai") is not None):
        return None
    c = {
        "candidate_id": f"abstract:{source_kind}:{source_order}",
        "source_type": "abstract",
        "source_kind": source_kind,
        "source_rank_kind": source_rank_kind,
        "source_rank": SOURCE_RANK[source_rank_kind],
        "source_order": source_order,
        "source": ex.get("source"),
        "classification_text": abstract,
        "provenance": "abstract",
    }
    for k in ("effect", "ci_low", "ci_high", "scale", "ai", "n1i", "ci", "n2i"):
        if ex.get(k) is not None:
            c[k] = ex[k]
    c.update(_classify(spec, abstract))
    return c


def _ctgov_candidates(
    outcome_measures: list[dict[str, Any]] | None,
    spec: dict[str, Any],
    interv: list[str],
    comp: list[str],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for order, om in enumerate(outcome_measures or []):
        title = om.get("title") or ""
        desc = om.get("description") or ""
        text = " ".join(str(x or "") for x in (title, desc))
        if not _keyword_family_match(spec, text):
            continue
        counts = _counts_from_om(om, interv, comp)
        analysis = _effect_analysis(om)
        if not counts and not analysis:
            continue
        denom_units = "; ".join(d.get("units", "") for d in om.get("denoms", []) if d.get("units"))
        measure_type = _registry_measure_type(
            om,
            ((om.get("classes") or [{}])[0] or {}).get("title"),
            ((((om.get("classes") or [{}])[0] or {}).get("categories") or [{}])[0] or {}).get("measurements") or [],
            denom_units,
        )
        base = {
            "candidate_id": f"ctgov:{order}",
            "source_type": "ctgov_results",
            "registry_title": title,
            "registry_type": om.get("type"),
            "registry_param_type": om.get("paramType"),
            "registry_measure_type": measure_type,
            "registry_timeframe": om.get("timeFrame") or om.get("time_frame"),
            "source_order": order,
            "classification_text": text,
            "provenance": "ctgov_results",
        }
        base.update(_classify(spec, text))
        if analysis:
            c = dict(base)
            c.update(analysis)
            c["source_kind"] = REGISTRY_PUBLISHED_EFFECT
            c["source_rank_kind"] = REGISTRY_PUBLISHED_EFFECT
            c["source_rank"] = SOURCE_RANK[REGISTRY_PUBLISHED_EFFECT]
            if counts and measure_type == "COUNT_OF_PARTICIPANTS":
                c["endpoint_counts"] = {k: counts[k] for k in ("ai", "n1i", "ci", "n2i")}
                count_txt = (
                    f"; endpoint counts {counts['ai']}/{counts['n1i']} ({counts['intervention_arm']}) "
                    f"vs {counts['ci']}/{counts['n2i']} ({counts['comparator_arm']})"
                )
            else:
                count_txt = ""
            c["source"] = (
                f"ClinicalTrials.gov results (structured target endpoint): outcome '{title[:100]}' "
                f"{c['scale']} {c['effect']:g} (95% CI {c['ci_low']:g} to {c['ci_high']:g})"
                f"{count_txt}"
            )
            out.append(c)
        if counts and measure_type == "COUNT_OF_PARTICIPANTS":
            c = dict(base)
            c.update({k: counts[k] for k in ("ai", "n1i", "ci", "n2i")})
            c["source_kind"] = RECONSTRUCTION
            c["source_rank_kind"] = RECONSTRUCTION
            c["source_rank"] = SOURCE_RANK[RECONSTRUCTION]
            c["source"] = (
                f"ClinicalTrials.gov results (structured target endpoint): outcome '{title[:100]}' "
                f"COUNT_OF_PARTICIPANTS {counts['ai']}/{counts['n1i']} ({counts['intervention_arm']}) "
                f"vs {counts['ci']}/{counts['n2i']} ({counts['comparator_arm']})"
            )
            out.append(c)
    return out


def enumerate_candidates(
    spec: dict[str, Any],
    abstract: str | None,
    outcome_measures: list[dict[str, Any]] | None,
    interv: list[str],
    comp: list[str],
) -> list[dict[str, Any]]:
    abstract = abstract or ""
    dc = extract.declared_is_composite(spec.get("name", ""))
    candidates: list[dict[str, Any]] = []
    hr_ex = extract.extract_trial(abstract, spec.get("keywords") or [], interv, comp,
                                  declared_composite=dc, estimand="HR")
    parsed_effect = _published_effect_from_abstract(spec, abstract, interv, comp)
    if parsed_effect and (not hr_ex or hr_ex.get("effect") is None):
        hr_ex = parsed_effect
    c = _candidate_from_abstract(
        hr_ex,
        spec=spec,
        abstract=abstract,
        source_kind=PUBLISHED_TARGET_EFFECT,
        source_rank_kind=PUBLISHED_TARGET_EFFECT,
        source_order=0,
    )
    if c and c.get("effect") is not None:
        candidates.append(c)
    default_ex = extract.extract_trial(abstract, spec.get("keywords") or [], interv, comp,
                                       declared_composite=dc, estimand=spec.get("estimand"))
    rank = PUBLISHED_TARGET_EFFECT if default_ex.get("effect") is not None else RECONSTRUCTION
    c = _candidate_from_abstract(
        default_ex,
        spec=spec,
        abstract=abstract,
        source_kind=rank,
        source_rank_kind=rank,
        source_order=1,
    )
    if c:
        candidates.append(c)
    candidates.extend(_ctgov_candidates(outcome_measures, spec, interv, comp))

    deduped: list[dict[str, Any]] = []
    seen = set()
    for c in candidates:
        key = (
            c.get("source_type"), c.get("source_kind"), c.get("effect"), c.get("ci_low"),
            c.get("ci_high"), c.get("ai"), c.get("n1i"), c.get("ci"), c.get("n2i"),
            c.get("registry_title"),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


def _selection_key(c: dict[str, Any]) -> tuple[int, int, int, int]:
    cls_score = 2 if c.get("target_endpoint_class") == EXACT_TARGET else 1
    return (
        cls_score,
        int(c.get("source_rank") or 0),
        -int(c.get("component_distance") or 0),
        -int(c.get("source_order") or 0),
    )


def _near_reason(c: dict[str, Any]) -> str:
    bits = []
    if c.get("extra_components"):
        bits.append("extra components: " + ", ".join(c["extra_components"]))
    if c.get("missing_components"):
        bits.append("missing components: " + ", ".join(c["missing_components"]))
    return "; ".join(bits) or "component set differs from the registered target"


def _public_candidate(c: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "candidate_id", "source_type", "source_kind", "registry_title", "registry_type",
        "target_endpoint_class", "extra_components", "missing_components", "source_rank_kind",
    )
    return {k: c.get(k) for k in keys if c.get(k) not in (None, [], "")}


def row_from_candidate(c: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "source": c.get("source"),
        "provenance": c.get("provenance"),
        "target_endpoint_class": c.get("target_endpoint_class"),
        "target_endpoint_source_rank": c.get("source_rank_kind"),
        "target_endpoint_components": c.get("target_components") or [],
        "components": c.get("target_components") or [],
        "target_endpoint_extra_components": c.get("extra_components") or [],
        "target_endpoint_missing_components": c.get("missing_components") or [],
        "results_known_at_rule_time": True,
    }
    if c.get("target_endpoint_class") == NEAR_MATCH:
        row["near_match_reason"] = _near_reason(c)
    if c.get("effect") is not None:
        row.update({"effect": c.get("effect"), "ci_low": c.get("ci_low"),
                    "ci_high": c.get("ci_high"), "scale": c.get("scale")})
    else:
        row.update({"ai": c.get("ai"), "n1i": c.get("n1i"), "ci": c.get("ci"), "n2i": c.get("n2i")})
    if c.get("endpoint_counts"):
        row["endpoint_counts"] = dict(c["endpoint_counts"])
    for k in ("registry_title", "registry_type", "registry_measure_type", "registry_timeframe"):
        if c.get(k) is not None:
            row[k] = c[k]
    return row


def select_target_endpoint(
    spec: dict[str, Any],
    abstract: str | None,
    outcome_measures: list[dict[str, Any]] | None,
    interv: list[str],
    comp: list[str],
) -> dict[str, Any]:
    if not canonical_components(spec):
        return {"selected": None, "candidates": [], "exact_target_in_held_source": False}
    candidates = enumerate_candidates(spec, abstract, outcome_measures, interv, comp)
    exact = [c for c in candidates if c.get("target_endpoint_class") == EXACT_TARGET]
    near = [c for c in candidates if c.get("target_endpoint_class") == NEAR_MATCH]
    eligible = exact or near
    if not eligible:
        return {"selected": None, "candidates": [_public_candidate(c) for c in candidates],
                "exact_target_in_held_source": False}
    selected = sorted(eligible, key=_selection_key, reverse=True)[0]
    row = row_from_candidate(selected)
    alternatives = [
        _public_candidate(c) for c in (exact + near)
        if c.get("candidate_id") != selected.get("candidate_id")
    ]
    if alternatives:
        row["target_endpoint_alternatives"] = alternatives[:6]
    primary_family = [
        c for c in eligible
        if c.get("source_type") == "ctgov_results" and str(c.get("registry_type") or "").upper() == "PRIMARY"
    ]
    if len(primary_family) > 1:
        row["registered_primary_selection_rule"] = {
            "n_registered_primaries_in_family": len(primary_family),
            "rule": "closest component set to canonical target; ties use registration order",
            "alternatives": [_public_candidate(c) for c in primary_family],
            "results_known_at_rule_time": True,
        }
    return {
        "selected": row,
        "candidates": [_public_candidate(c) for c in candidates],
        "exact_target_in_held_source": bool(exact),
        "selected_candidate": _public_candidate(selected),
        "near_match_while_exact_exists": bool(exact and selected.get("target_endpoint_class") == NEAR_MATCH),
    }
