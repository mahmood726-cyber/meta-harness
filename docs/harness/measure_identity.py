"""Offline measure identity; diagnostics never rewrite the protocol or pool data.

Callers must supply outcome-bound held rows/spans, not entire papers. Selection
assumes candidates already passed endpoint, arm, and source admission checks.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
import math
import re


class Measure(str, Enum):
    HAZARD_RATIO = "HAZARD_RATIO"
    RATE_RATIO = "RATE_RATIO"
    RISK_RATIO = "RISK_RATIO"
    ODDS_RATIO = "ODDS_RATIO"
    RMST_DIFFERENCE = "RMST_DIFFERENCE"
    MEAN_DIFFERENCE = "MEAN_DIFFERENCE"
    UNKNOWN = "UNKNOWN"


_WORDS = {
    Measure.HAZARD_RATIO: r"\bhazard[- ]ratios?\b",
    Measure.RATE_RATIO: r"\b(?:incidence[- ]|event[- ])?rate[- ]ratios?\b",
    Measure.RISK_RATIO: r"\b(?:risk[- ]ratios?|relative[- ]risk(?!\s+reduction))\b",
    Measure.ODDS_RATIO: r"\bodds[- ]ratios?\b",
    Measure.RMST_DIFFERENCE: r"\b(?:RMST[- ]difference|difference\s+in\s+(?:RMST|restricted mean survival time)|restricted mean survival time[- ]difference)\b",
    Measure.MEAN_DIFFERENCE: r"(?<!standardized )(?<!standardised )\bmean[- ]difference\b",
}
_ALIASES = {"HR": Measure.HAZARD_RATIO, "IRR": Measure.RATE_RATIO,
            "RR": Measure.RISK_RATIO, "OR": Measure.ODDS_RATIO,
            "MD": Measure.MEAN_DIFFERENCE}
_COUNTS = ("ai", "n1i", "ci", "n2i")


def word_measures(text):
    return {m for m, pattern in _WORDS.items() if re.search(pattern, str(text or ""), re.I)}


def normalize(value):
    if isinstance(value, Measure):
        return value
    value = str(value or "").strip()
    if value.upper() in Measure._value2member_map_:
        return Measure(value.upper())
    if value.upper() in _ALIASES:
        return _ALIASES[value.upper()]
    found = word_measures(value)
    return next(iter(found)) if len(found) == 1 else Measure.UNKNOWN


def measure_from_table(header, footnote, row_label):
    """A measure-specific footnote overrides a composite table header.

    Ambiguous footnotes do not license falling back to a convenient header.
    Caller must bind the footnote to this row before calling.
    """
    for text in (footnote, row_label, header):
        found = word_measures(text)
        if found:
            return next(iter(found)) if len(found) == 1 else Measure.UNKNOWN
        value = normalize(text)
        if value != Measure.UNKNOWN:
            return value
    return Measure.UNKNOWN


def row_span(row):
    for key in ("source_span", "span", "source"):
        if isinstance(row.get(key), str) and row[key].strip():
            return row[key]
    return ""


def _count_row(row):
    return row.get("effect") is None and any(row.get(k) is not None for k in _COUNTS)


def _valid_counts(row):
    vals = [row.get(k) for k in _COUNTS]
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               and math.isfinite(v) and v == int(v) for v in vals):
        return False
    a, n, c, m = vals
    return n > 0 and m > 0 and 0 <= a <= n and 0 <= c <= m


def measure_of(row, source_text=""):
    """Return a strict measure, preferring local words over a scale label.

    Counts describe cumulative risk per the lane contract; they never acquire
    a published HR merely because that HR appears in surrounding source text.
    Multiple local word classes are unresolved. No whole-abstract fallback.
    """
    if str(row.get("derivation", "")).upper() == "RELAYED":
        return Measure.UNKNOWN
    if _count_row(row):
        if not _valid_counts(row):
            return Measure.UNKNOWN
        return (Measure.ODDS_RATIO if row.get('reconstruction_measure') == 'OR'
                else Measure.RISK_RATIO)
    if "table_header" in row:
        return measure_from_table(row["table_header"], row.get("footnote", ""), row.get("row_label", ""))
    text = source_text or row_span(row)
    # Bind a measure to this estimate's own numeric clause, not explanatory prose.
    local = set()
    if row.get('effect') is not None:
        for measure, pattern in _WORDS.items():
            for match in re.finditer(pattern + r"(?:\s+vs\.?\s+[A-Za-z][A-Za-z -]{0,45})?\s*(?:\(95%\s*CI\)|\[(?:HR|RR|OR)\])?\s*[,=:]?\s*(?:was\s+|of\s+)?(\d+(?:[.?]\d+)?)", text, re.I):
                if math.isclose(float(match.group(1).replace('?', '.')), float(row['effect']), rel_tol=1e-9):
                    local.add(measure)
        if local:
            return next(iter(local)) if len(local) == 1 else Measure.UNKNOWN
    found = word_measures(text)
    if found:
        return next(iter(found)) if len(found) == 1 else Measure.UNKNOWN
    label_words = word_measures(row.get("row_label", "")) | word_measures(row.get("label", ""))
    if label_words:
        return next(iter(label_words)) if len(label_words) == 1 else Measure.UNKNOWN
    for key in ("measure", "scale", "row_label", "label"):
        value = normalize(row.get(key))
        if value != Measure.UNKNOWN:
            return value
    return Measure.UNKNOWN


def identity(row, source_text=""):
    measure = measure_of(row, source_text)
    derivation = ("RELAYED" if str(row.get("derivation", "")).upper() == "RELAYED"
                  else "RECONSTRUCTED" if _count_row(row)
                  else "PUBLISHED" if row.get("effect") is not None
                  else "UNKNOWN")
    return {"measure": measure.value, "derivation": derivation,
            "admissible": measure != Measure.UNKNOWN and derivation != "RELAYED"}


def _problem(code, item, **details):
    return {"code": code, "item": str(item), "refused": True, **details}


def check_pool(rows, name="pool"):
    identified = [(str(r.get("id") or r.get("label") or i), measure_of(r))
                  for i, r in enumerate(rows)]
    classes = {m for _, m in identified if m != Measure.UNKNOWN}
    problems = []
    unknown = [rid for rid, m in identified if m == Measure.UNKNOWN]
    if unknown:
        problems.append(_problem("MEASURE_UNKNOWN", name, rows=unknown))
    if len(classes) > 1:
        problems.append(_problem("MEASURE_MIX_POOLED", name,
                                 measures=sorted(m.value for m in classes),
                                 rows=[{"id": rid, "measure": m.value} for rid, m in identified]))
    return problems


def protocol_specs(config):
    return [config.get("primary_outcome", {})] + list(config.get("secondary_outcomes", [])) + list(config.get("harm_outcomes", []))


@dataclass(frozen=True)
class MeasureMapping:
    """Integrator-validated conversion receipt, not a free-form exemption.

    No conversion implementation is supplied in this lane. A receipt must bind
    the source and target, method and held evidence; an arbitrary JSON dict is
    deliberately insufficient to waive the gate.
    """
    source: Measure
    target: Measure
    method: str
    evidence: str


def outcome_identity(outcome, spec):
    result = outcome.get("result") or {}
    rows = outcome.get("trials") or []
    measures = {measure_of(row) for row in rows}
    served = next(iter(measures)) if len(measures) == 1 else Measure.UNKNOWN
    if not rows:
        served = normalize(result.get("measure") or result.get("scale"))
    return {"target_measure": normalize(spec.get("estimand")).value,
            "served_measure": served.value}


def check_target(review, config):
    """Check each served outcome against the immutable topic specification."""
    specs = {s.get("name"): s for s in protocol_specs(config) if s.get("name")}
    problems = []
    for outcome in review.get("outcomes", []):
        result = outcome.get("result") or {}
        if result.get("present") is False or result.get("suppressed") or result.get("estimate") is None:
            continue
        name = outcome.get("name", "<unnamed>")
        spec = specs.get(name, {})
        fields = outcome_identity(outcome, spec)
        target, served = (normalize(fields[k]) for k in ("target_measure", "served_measure"))
        labelled = normalize(result.get("measure") or result.get("scale"))
        if Measure.UNKNOWN in (target, served, labelled):
            problems.append(_problem("MEASURE_UNKNOWN", name, **fields, labelled_measure=labelled.value))
        mapping = result.get("measure_mapping")
        mapped = (isinstance(mapping, MeasureMapping) and mapping.source == served
                  and mapping.target == target and labelled == target
                  and bool(mapping.method.strip()) and bool(mapping.evidence.strip())
                  and served != Measure.UNKNOWN and target != Measure.UNKNOWN)
        if not mapped and (target != labelled or target != served):
            problems.append(_problem("TARGET_MEASURE_REWRITTEN", name, **fields, labelled_measure=labelled.value))
        if labelled != served and not mapped:
            problems.append(_problem("SERVED_MEASURE_MISLABELLED", name, **fields, labelled_measure=labelled.value))
        if any(result.get(k) != v for k, v in fields.items()):
            problems.append(_problem("MEASURE_IDENTITY_FIELDS_MISSING_OR_WRONG", name, **fields))
    return problems


def select(candidates, peer_measures):
    """Return selected row plus explicit refusal diagnostics; never pool here.

    Input order breaks equal-candidate ties. Tied/unknown peer modes refuse
    admission instead of inventing a preferred class. A fallback count row is
    retained for inspection, with admissible=False when unresolved.
    """
    candidates = list(candidates)
    peers = [normalize(p) for p in peer_measures]
    counts = Counter(peers)
    modes = [m for m, n in counts.items() if n == max(counts.values())] if counts else []
    modal = modes[0] if len(modes) == 1 and Measure.UNKNOWN not in peers else Measure.UNKNOWN
    usable = [r for r in candidates if identity(r)["admissible"]]
    published = [r for r in usable if identity(r)["derivation"] == "PUBLISHED" and measure_of(r) == modal]
    reconstructed = [r for r in usable if identity(r)["derivation"] == "RECONSTRUCTED"]
    chosen = next(iter(published or reconstructed or usable), None)
    problems = []
    if chosen is None or modal == Measure.UNKNOWN or measure_of(chosen) != modal or len(set(peers)) != 1:
        problems.append(_problem("MEASURE_MISMATCH_UNRESOLVED", (chosen or {}).get("id", "selection"),
                                 peer_measures=[p.value for p in peers],
                                 selected_measure=measure_of(chosen or {}).value))
    return {"row": chosen, "identity": identity(chosen or {}),
            "admissible": not problems, "problems": problems}
