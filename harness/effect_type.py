"""Evidence-bearing effect types. No eligibility decisions or automatic coercions.

UNKNOWN is data, never an invitation to copy a protocol target into an effect.
Only declared binding axes constrain unification. Coercions are external,
permanent signed decision records, scoped to exact source and target values.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import TypedDict

from . import endpoint_canonical

AXES = ("population", "randomised_contrast", "analysis_set", "endpoint_components",
        "first_or_recurrent", "time_origin", "follow_up", "censoring",
        "effect_measure", "adjustment", "estimator", "report")
ACCEPTED = {"MATCH", "MATCH_WITH_DECLARED_COERCION"}
UNKNOWN = "UNKNOWN"
EMPTY = (None, "", "UNKNOWN", "unstated", "not_stated", "NOT_DERIVABLE")
ENUMS = {"analysis_set": {"ITT", "mITT", "PP", "on-treatment"},
         "censoring": {"on-study", "on-treatment", "end-of-study", "end-of-treatment"},
         "effect_measure": {"HR", "RR", "OR", "RD", "MD", "SMD"}}


class EffectType(TypedDict):
    effect_type_id: str
    trial: str
    axes: dict
    known_axes: int
    unknown_axes: list[str]


def _digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def field(value=UNKNOWN, *, span=None, source=None, rule_id=None, absence_code="NO_ROW_EVIDENCE"):
    if value in EMPTY or not (span or rule_id):
        return {"value": UNKNOWN, "basis": {"absence_code": absence_code}}
    basis = {"span": span, "source": source} if span else {"rule_id": rule_id}
    return {"value": value, "basis": basis}


def known(f):
    return (isinstance(f, dict) and f.get("value") not in EMPTY
            and bool((f.get("basis") or {}).get("span") or (f.get("basis") or {}).get("rule_id")))


def axis_known(axis, f):
    if not known(f):
        return False
    if axis in ENUMS:
        return isinstance(f["value"], str) and f["value"] in ENUMS[axis]
    return True


def components(text):
    """Literal component recognition; unlike legacy MACE parsing, no acronym default."""
    patterns = {
        "CV_DEATH": r"cardiovascular death|death from cardiovascular causes|CV death",
        "NONFATAL_MI": r"non[- ]?fatal (?:myocardial infarction|MI)",
        "NONFATAL_STROKE": r"non[- ]?fatal stroke",
        "UA_HOSP": r"(?:hospitali[sz]ation for )?unstable angina",
    }
    found = {k for k, p in patterns.items() if re.search(p, text, re.I)}
    if "NONFATAL_MI" not in found and re.search(r"myocardial infarction|\bMI\b", text, re.I):
        found.add("MI_FATALITY_UNSTATED")
    if "NONFATAL_STROKE" not in found and re.search(r"\bstroke\b", text, re.I):
        found.add("STROKE_FATALITY_UNSTATED")
    return sorted(found)


def build_effect(row, record=None) -> EffectType:
    record = record or {}
    axes = {a: field(absence_code="UNSTATED" if row.get(a) == "unstated" else "NO_ROW_EVIDENCE") for a in AXES}
    source = str(row.get("source") or "")
    abstract = str(record.get("abstract") or "")
    ref = "record:" + str(record.get("id") or row.get("id") or "unidentified")
    # Accept explicit provenance-bearing fields; never legacy protocol-inherited scalars.
    for axis, f in (row.get("effect_type_evidence") or {}).items():
        if axis in axes and isinstance(f, dict):
            axes[axis] = field(f.get("value"), **{k: v for k, v in (f.get("basis") or {}).items()
                                               if k in {"span", "source", "rule_id", "absence_code"}})

    # SC3 arm evidence: require two explicit arms, one drug occurrence, and
    # equal evidenced backgrounds. A 'verified' summary label is insufficient.
    arm = row.get("arm_object") or record.get("arm_object") or {}
    arms = arm.get("randomised_arm") or []
    if len(arms) == 2 and row.get("drug_of_interest"):
        drugs = [a.get("drug") or {} for a in arms]
        backgrounds = [a.get("background_therapy") or {} for a in arms]
        fs = drugs + backgrounds
        if all(f.get("value") not in EMPTY and f.get("span") not in EMPTY for f in fs):
            valid = (sum(str(d["value"]).casefold() == str(row["drug_of_interest"]).casefold() for d in drugs) == 1
                     and backgrounds[0]["value"] == backgrounds[1]["value"])
            axes["randomised_contrast"] = field(valid, span=json.dumps(fs), source="SC3:randomised_arm")
    pop = arm.get("population") or {}
    requested = row.get("population_fields") or []
    if requested and all(isinstance(pop.get(k), dict) and pop[k].get("value") not in EMPTY
                         and pop[k].get("span") not in EMPTY for k in requested):
        axes["population"] = field({k: pop[k]["value"] for k in requested},
                                   span=json.dumps({k: pop[k] for k in requested}), source="SC3:population")

    def derive(axis, patterns, text, suffix):
        if known(axes[axis]):
            return
        hits = [(value, m.group(0)) for pattern, value in patterns
                for m in re.finditer(pattern, text, re.I)]
        values = {v or s for v, s in hits}
        if len(values) == 1:
            value, span = hits[0]
            axes[axis] = field(value or span, span=span, source=ref + suffix)
        elif len(values) > 1:
            axes[axis] = field(absence_code="AMBIGUOUS_ROW_EVIDENCE")

    # Analysis sets / follow-up may be stated in the trial abstract. Censoring,
    # estimator and adjustment stay local to the selected effect's source span.
    text = source + "\n" + abstract
    analysis = [(r"modified[- ]intention[- ]to[- ]treat|\bmITT\b", "mITT"),
                (r"(?<!modified )(?<!modified-)intention[- ]to[- ]treat|\bITT\b", "ITT"),
                (r"per[- ]protocol", "PP")]
    derive("analysis_set", analysis, text, ".source/abstract")
    derive("censoring", [(r"end[- ]of[- ]study", "end-of-study"),
                         (r"end[- ]of[- ]treatment", "end-of-treatment"),
                         (r"on[- ]study", "on-study"), (r"on[- ]treatment", "on-treatment")], source, ".source")
    derive("first_or_recurrent", [(r"time to first|time-to-first|first occurrence", "first"),
                                  (r"first and recurrent|total recurrent", "recurrent")], source, ".source")
    derive("time_origin", [(r"from randomi[sz]ation", "randomisation")], source, ".source")
    derive("follow_up", [(r"median (?:duration of )?follow[- ]?up (?:of |was )?[0-9.]+ (?:years|months|weeks)", None),
                         (r"followed for a median of [0-9.]+ (?:years|months|weeks)", None)], text, ".source/abstract")
    derive("estimator", [(r"Cox (?:proportional hazards|PH|model)", "Cox PH"),
                         (r"log-binomial", "log-binomial")], source, ".source")
    derive("adjustment", [(r"(?:stratified by|adjusted for) [^.;\n]+", None)], source, ".source")
    # Effect-local endpoint wording takes priority; otherwise an explicitly
    # defined primary endpoint sentence, never the outcome name or trial name.
    endpoint_text = source if len(components(source)) >= 3 else ""
    if not endpoint_text:
        matches = re.findall(r"[^.\n]*(?:primary (?:composite )?(?:outcome|end point|endpoint))[^.\n]*", abstract, re.I)
        matches = [m for m in matches if len(components(m)) >= 3]
        if len(matches) == 1:
            endpoint_text = matches[0]
    if endpoint_text and not known(axes["endpoint_components"]):
        axes["endpoint_components"] = field(components(endpoint_text), span=endpoint_text, source=ref + ".endpoint")
    scale = str(row.get("scale") or "").upper()
    if scale in {"HR", "RR", "OR", "RD", "MD", "SMD"} and source:
        # Explicit selected scale and source, not the outcome's requested estimand.
        axes["effect_measure"] = field(scale, span=source, source=ref + ".source; row.scale")
    provenance = row.get("provenance")
    reports = {"abstract": ("publication", 1), "fulltext_verified": ("publication", 1),
               "pmc_fulltext_effect": ("publication", 1), "ctgov_results_effect": ("registry results", 3)}
    if provenance in reports and source:
        label, level = reports[provenance]
        value = {"kind": label, "source_level": level}
        if row.get("document_sha256"):
            value["document_sha256"] = row["document_sha256"]
        axes["report"] = field(value, rule_id="source_hierarchy:provenance:" + provenance)
    report = row.get("report_source") or {}
    kinds = {"publication": 1, "supplement": 1, "regulatory FDA/EMA": 2,
             "registry results": 3, "HTA": 4, "older meta pointer": 5}
    if report.get("kind") in kinds and report.get("source_level") == kinds[report["kind"]] and report.get("span"):
        value = {"kind": report["kind"], "source_level": report["source_level"]}
        if report.get("document_path"):
            root = Path(__file__).resolve().parents[1]
            path = (root / report["document_path"]).resolve()
            if not path.is_relative_to(root):
                raise ValueError("Held document must be within the repository")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if report.get("document_sha256") and report["document_sha256"] != digest:
                raise ValueError("Held document digest mismatch")
            value["document_sha256"] = digest
        axes["report"] = field(value, span=report["span"], source=report.get("document_path") or report.get("source"))
    for axis, f in axes.items():
        if known(f) and not axis_known(axis, f):
            axes[axis] = field(absence_code="INVALID_AXIS_VALUE")
    obj = {"trial": str(row.get("id") or row.get("label") or "unidentified"), "axes": axes}
    return dict(obj, effect_type_id="effect-type:" + _digest({"type": obj, "effect": {k: row.get(k) for k in ("effect", "ci_low", "ci_high", "ai", "ci", "n1i", "n2i")}}),
                known_axes=sum(known(f) for f in axes.values()),
                unknown_axes=[a for a, f in axes.items() if not known(f)])


def validate_coercion(c):
    required = ("coercion_id", "who", "why", "evidence_spans", "date", "consequence", "signed_by", "axis", "from", "to")
    if not isinstance(c, dict) or any(k not in c or c[k] in EMPTY or c[k] == [] for k in required):
        return False
    if any(not isinstance(c[k], str) or not c[k].strip()
           for k in ("coercion_id", "who", "why", "consequence", "signed_by", "axis")):
        return False
    try:
        date.fromisoformat(c["date"])
    except (ValueError, TypeError):
        return False
    return (c["axis"] in AXES and isinstance(c["evidence_spans"], list)
            and all(isinstance(s, dict) and isinstance(s.get("source"), str) and s["source"].strip()
                    and isinstance(s.get("span"), str) and s["span"].strip() for s in c["evidence_spans"]))


def _equal(axis, a, b):
    if axis == "endpoint_components" and isinstance(a, list) and isinstance(b, list):
        return sorted(set(a)) == sorted(set(b))
    return a == b


def unify(target, effect, coercions=()):
    binding = target.get("binding_axes")
    if not isinstance(binding, list) or any(a not in AXES for a in binding):
        return {"status": "REFUSE", "axis": None, "reason": "invalid or absent protocol binding_axes"}
    disclosures, used = [], []
    ids = [c.get("coercion_id") for c in coercions if isinstance(c, dict)]
    for n, axis in enumerate(AXES, 1):
        f = effect.get("axes", {}).get(axis)
        if not axis_known(axis, f):
            reason = (f or {}).get("basis", {}).get("absence_code", "NO_ROW_EVIDENCE")
            if axis in binding:
                return {"status": "UNKNOWN_FAILS_CLOSED", "axis": n, "axis_name": axis,
                        "reason": f"UNTYPED — axis {n} unknown: {reason}"}
            disclosures.append(f"axis {n} unstated")
            continue
        if axis not in binding:
            continue
        t = target.get("axes", {}).get(axis)
        if not axis_known(axis, t):
            return {"status": "UNKNOWN_FAILS_CLOSED", "axis": n, "axis_name": axis,
                    "reason": f"UNTYPED — axis {n} unknown: protocol target has no basis"}
        if _equal(axis, t["value"], f["value"]):
            continue
        c = next((c for c in coercions if validate_coercion(c) and ids.count(c["coercion_id"]) == 1
                  and c["axis"] == axis and _equal(axis, c["from"], f["value"])
                  and _equal(axis, c["to"], t["value"])
                  and (not c.get("effect_type_id") or c["effect_type_id"] == effect.get("effect_type_id"))), None)
        if c is None:
            return {"status": "REFUSE", "axis": n, "axis_name": axis,
                    "reason": f"axis {n}: {f['value']} differs from target {t['value']}; no valid declared coercion"}
        used.append(c["coercion_id"])
    return {"status": "MATCH_WITH_DECLARED_COERCION" if used else "MATCH",
            "coercion_ids": used, "disclosures": disclosures}


def protocol_target(spec, protocol_text=""):
    """Compile only explicit declarations. Integrator can supply all 12 axes.

    Legacy timepoint prose is not silently mapped to a censoring policy.
    """
    if "effect_type_target" in spec:
        return copy.deepcopy(spec["effect_type_target"])
    axes = {}
    analysis = endpoint_canonical._normal_analysis_literal(spec.get("population"))
    if analysis in {"ITT", "mITT", "PP", "on-treatment"}:
        axes["analysis_set"] = field(analysis, rule_id="protocol:outcome.population")
    if spec.get("estimand") in {"HR", "RR", "OR", "RD", "MD", "SMD"}:
        axes["effect_measure"] = field(spec["estimand"], rule_id="protocol:outcome.estimand")
    if spec.get("canonical_components"):
        axes["endpoint_components"] = field(spec["canonical_components"], rule_id="protocol:outcome.canonical_components")
    # Exact amendment declarations; never infer these from a topic/trial name.
    if spec.get("primary") and "**log-HRs only**" in protocol_text:
        axes["effect_measure"] = field("HR", span="**log-HRs only**", source="protocol:Effect measure")
    endpoint = "time to first** occurrence of cardiovascular death, nonfatal myocardial infarction or nonfatal stroke"
    if spec.get("primary") and endpoint in protocol_text:
        axes["endpoint_components"] = field(["CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE"], span=endpoint, source="protocol:Estimand")
        axes["first_or_recurrent"] = field("first", span=endpoint, source="protocol:Estimand")
    timepoint = "at the end of randomised, blinded follow-up"
    if spec.get("primary") and timepoint in protocol_text:
        axes["censoring"] = field("end-of-study", span=timepoint, source="protocol:Timepoint")
    return {"binding_axes": list(axes), "axes": axes,
            "disclosure": "Only explicit machine-readable declarations compiled; no additional binding policy inferred."}


def type_rows(rows, target, records=None, coercions=()):
    kept, refused, effects = [], [], []
    for original in rows:
        row = copy.deepcopy(original)
        key = str(row.get("id") or "").replace("PMID ", "")
        e = build_effect(row, (records or {}).get(key))
        verdict = unify(target, e, coercions)
        e["unification"] = verdict
        row.update(effect_type_id=e["effect_type_id"], unification=verdict)
        effects.append(e)
        if verdict["status"] in ACCEPTED:
            kept.append(row)
        else:
            row.update(absent_kind="refused_on_evidence", reason=verdict["reason"], state="EFFECT_TYPE_REFUSED")
            refused.append(row)
    return kept, refused, effects


def load_coercions(path):
    path = Path(path)
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or any(not validate_coercion(c) for c in data):
        raise ValueError("Invalid coercion register: " + str(path))
    if len({c["coercion_id"] for c in data}) != len(data):
        raise ValueError("Duplicate coercion_id in register")
    return data


def persist(path, outcomes):
    """Write derived type artefacts only; never author a coercion decision."""
    data = {"schema_version": 1, "outcomes": [
        {"name": o["name"], "target": o["effect_type_target"], "effects": o["effect_types"]}
        for o in outcomes]}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def check_review(review):
    errors = []
    for o in review.get("outcomes", []):
        result = o.get("result") or {}
        if result.get("present") is False or result.get("suppressed_incompatible") or not result.get("k"):
            continue
        if result["k"] != len(o.get("trials", [])):
            errors.append(f"EFFECT_TYPE_COUNT_MISMATCH {o.get('name')}: k differs from trial rows")
        effects = {e["effect_type_id"]: e for e in o.get("effect_types", [])}
        for row in o.get("trials", []):
            e = effects.get(row.get("effect_type_id"))
            v = unify(o.get("effect_type_target") or {}, e or {}, o.get("coercions", []))
            if not e or v["status"] not in ACCEPTED or row.get("unification") != v or e.get("unification") != v:
                errors.append(f"EFFECT_TYPE_REFUSED {o.get('name')} / {row.get('id')}: {v.get('reason', 'missing or stale type verdict')}")
    return errors
