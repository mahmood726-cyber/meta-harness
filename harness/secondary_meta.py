"""SECONDARY-SOURCE TIER: per-trial data taken from previously published meta-analyses (approved 2026-09-30).

A secondary row is never a primary fact. It enters as SECONDARY_UNVERIFIED, is shown as provisional with its source
named, and is queued for verification against the trial's own primary source (paper / registry / regulator):

    SECONDARY_UNVERIFIED --match--> PRIMARY_VERIFIED
                         --mismatch--> MISMATCH (a typed finding: which field, both values, both locations, which side)
    two independent metas disagree on the same trial -> BLOCKED_CROSSCHECK until resolved (never averaged, never first)

Admission uses the SAME questions the primary gate asks (measure identity, outcome components, timepoint, population,
family/report consolidation, nested-subgroup), plus an EXTRACTION POSITIVE CONTROL: the meta's own printed pooled
result must be reproduced from the rows extracted from it, or none of that meta's rows is used.

G1 ANTI-CIRCULARITY: a row sourced from meta X never counts toward G1 agreement with meta X, and G1 'k matched'
counts only PRIMARY_VERIFIED rows (g1_countable).

Numbers are typed from the meta's own text/tables (regex) where it prints them; a forest-plot row read by a model is a
recorded, replayable PROPOSAL admitted only through the same gate and the positive control. Nothing here writes to a
served page: a served-number change goes through a derived notice for signature.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, asdict
from typing import Any, Optional

UNVERIFIED, VERIFIED, MISMATCH, BLOCKED = "SECONDARY_UNVERIFIED", "PRIMARY_VERIFIED", "MISMATCH", "BLOCKED_CROSSCHECK"
REFUSED = "REFUSED"
RATIO = {"HR", "RR", "OR", "IRR"}
_SUBGROUP_LABEL = re.compile(r"subgroup|planned invasive|invasive(?:ly)? managed|\bPCI\b|\bCABG\b|substudy|sub-study|"
                             r"post[- ]hoc|per[- ]protocol|on[- ]treatment|stratum|cohort of|patients with prior|"
                             r"without prior|diabet(?:ic|es) subgroup", re.I)


@dataclass
class SecondaryRow:
    """One trial's data as printed by one meta-analysis. Every field that the gate or a reader needs is explicit."""
    meta_pmid: str
    meta_doi: str
    location: dict                     # {"kind": "table"|"figure", "id": ..., "panel": ..., "row_label": ...}
    source_digest: str                 # sha256 of the bytes the row was read from (JATS table XML or figure image)
    provenance: str                    # "TYPED_TABLE" | "TYPED_TEXT" | "MODEL_PROPOSAL:<record_id>"
    trial_label: str
    measure: str                       # HR / RR / OR / MD ...
    outcome_definition: str            # as the meta states it (caption / column header / methods)
    timepoint: Optional[str] = None
    population: Optional[str] = None
    arm_dose: Optional[str] = None
    events_t: Optional[int] = None
    n_t: Optional[int] = None
    events_c: Optional[int] = None
    n_c: Optional[int] = None
    effect: Optional[str] = None       # PRINTED strings: precision is part of the fact ('1.10' is not '1.1')
    lower: Optional[str] = None
    upper: Optional[str] = None
    family_id: Optional[str] = None
    state: str = UNVERIFIED
    reasons: list = field(default_factory=list)
    verification: Optional[dict] = None

    def to_dict(self):
        return asdict(self)


def validate(row: SecondaryRow) -> list:
    """A row that cannot say where it came from, or carries neither counts nor an effect with its CI, is not a row."""
    probs = []
    if not (row.meta_pmid or row.meta_doi):
        probs.append("NO_META_IDENTITY")
    if not (row.location or {}).get("kind") or not (row.location or {}).get("id"):
        probs.append("NO_EXACT_LOCATION")
    if not re.fullmatch(r"[0-9a-f]{64}", row.source_digest or ""):
        probs.append("NO_SOURCE_DIGEST")
    counts = None not in (row.events_t, row.n_t, row.events_c, row.n_c)
    eff = None not in (row.effect, row.lower, row.upper)
    if not counts and not eff:
        probs.append("NEITHER_COUNTS_NOR_EFFECT_CI")
    if not row.measure:
        probs.append("NO_MEASURE")
    if not row.outcome_definition:
        probs.append("NO_OUTCOME_DEFINITION")
    return probs


# ------------------------------------------------------------------ TYPED extraction from a meta's JATS tables (regex)

_TRIPLE = re.compile(r"(-?\d+(?:[.·]\d+)?)\s*[(\[]\s*(-?\d+(?:[.·]\d+)?)\s*(?:[-‐-―−,;]|to)\s*"
                     r"(-?\d+(?:[.·]\d+)?)\s*[)\]]")
# events/N, optionally followed by its percentage as tables print it: "24/120" or "24/120 (20.0%)"
_COUNTS = re.compile(r"^\s*(\d+)\s*/\s*(\d+)(?:\s*\(\s*\d+(?:\.\d+)?\s*%?\s*\))?\s*$")
_POOLED = re.compile(r"^\s*(?:overall|total|pooled|summary|random[- ]effects?|fixed[- ]effects?|combined)\b", re.I)
_MEASURE = {"HR": re.compile(r"\bHR\b|hazard ratio", re.I), "RR": re.compile(r"\bRR\b|risk ratio|relative risk", re.I),
            "OR": re.compile(r"\bOR\b|odds ratio"), "MD": re.compile(r"\bW?MD\b|mean difference", re.I)}


def _cell_text(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _measure_of(text):
    hits = [m for m, rx in _MEASURE.items() if rx.search(text or "")]
    return hits[0] if len(hits) == 1 else None


def typed_rows_from_jats(jats: bytes, meta_pmid: str, meta_doi: str = "") -> list:
    """Every JATS <table-wrap> of a meta as candidate per-trial rows, read by regex, never by a model. Returns
    [{"table_id", "caption", "digest", "measure", "rows": [SecondaryRow...], "pooled": {effect,lower,upper} | None}].
    A row is a body row whose first cell names a trial and that carries ONE effect-with-CI cell, or events/N in two
    cells (intervention, control) under a header naming them. The pooled row ('Overall', 'Total', ...) is the
    positive-control target; its absence leaves the table unusable (no control, no rows)."""
    import hashlib
    import xml.etree.ElementTree as ET
    root = ET.fromstring(jats)
    out = []
    for tw in root.iter("table-wrap"):
        tid = tw.get("id") or ""
        caption = _cell_text(tw.find("caption")) if tw.find("caption") is not None else ""
        digest = hashlib.sha256(ET.tostring(tw)).hexdigest()
        head = [_cell_text(c) for tr in tw.iter("thead") for r in tr.iter("tr") for c in r if c.tag in ("th", "td")]
        body = [[_cell_text(c) for c in tr if c.tag in ("td", "th")] for tb in tw.iter("tbody") for tr in tb.iter("tr")]
        measure = _measure_of(" ".join(head)) or _measure_of(caption)
        rows, pooled = [], None
        for cells in body:
            if len(cells) < 2 or not cells[0]:
                continue
            triples = [(i, m) for i, c in enumerate(cells[1:], 1) for m in [_TRIPLE.search(c)] if m]
            counts = [(i, m) for i, c in enumerate(cells[1:], 1) for m in [_COUNTS.match(c)] if m]
            if _POOLED.match(cells[0]):
                if len(triples) == 1:
                    m = triples[0][1]
                    pooled = {"effect": m.group(1).replace("·", "."), "lower": m.group(2).replace("·", "."),
                              "upper": m.group(3).replace("·", "."), "row_label": cells[0]}
                continue
            loc = {"kind": "table", "id": tid, "row_label": cells[0]}
            if len(triples) == 1 and measure:
                m = triples[0][1]
                rows.append(SecondaryRow(meta_pmid=meta_pmid, meta_doi=meta_doi, location=loc, source_digest=digest,
                                         provenance="TYPED_TABLE", trial_label=cells[0], measure=measure,
                                         outcome_definition=caption[:300], effect=m.group(1).replace("·", "."),
                                         lower=m.group(2).replace("·", "."), upper=m.group(3).replace("·", ".")))
            elif len(counts) == 2 and not triples and measure in ("RR", "OR"):
                (_, a), (_, b) = counts
                rows.append(SecondaryRow(meta_pmid=meta_pmid, meta_doi=meta_doi, location=loc, source_digest=digest,
                                         provenance="TYPED_TABLE", trial_label=cells[0], measure=measure,
                                         outcome_definition=caption[:300], events_t=int(a.group(1)), n_t=int(a.group(2)),
                                         events_c=int(b.group(1)), n_c=int(b.group(2))))
        if rows:
            out.append({"table_id": tid, "caption": caption, "digest": digest, "measure": measure, "rows": rows,
                        "pooled": pooled})
    return out


# ------------------------------------------------------------------ extraction positive control

def _num(s):
    try:
        return float(str(s).replace("−", "-").replace("·", "."))
    except (TypeError, ValueError):
        return None


def _decimals(s):
    m = re.search(r"\.(\d+)", str(s))
    return len(m.group(1)) if m else 0


def _half(s):
    return 0.5 * 10 ** (-_decimals(s))


def row_yi_vi(row: SecondaryRow, z=1.959963984540054):
    """(yi, vi) on the analysis scale: log for ratios, raw for differences; from counts (log RR/OR) or the CI."""
    ratio = row.measure.upper() in RATIO
    if row.effect is not None:
        e, lo, hi = _num(row.effect), _num(row.lower), _num(row.upper)
        if None in (e, lo, hi) or (ratio and min(e, lo, hi) <= 0):
            return None
        f = math.log if ratio else (lambda x: x)
        return f(e), ((f(hi) - f(lo)) / (2 * z)) ** 2
    a, n1, c, n2 = row.events_t, row.n_t, row.events_c, row.n_c
    if 0 in (a, c) or a >= n1 or c >= n2:
        a, n1, c, n2 = a + 0.5, n1 + 1, c + 0.5, n2 + 1          # 0.5 only when a cell is zero (Cochrane convention)
    if row.measure.upper() == "OR":
        return math.log((a / (n1 - a)) / (c / (n2 - c))), 1 / a + 1 / (n1 - a) + 1 / c + 1 / (n2 - c)
    return math.log((a / n1) / (c / n2)), 1 / a - 1 / n1 + 1 / c - 1 / n2


def pool(yi, vi, method="FE", hk=False, z=1.959963984540054):
    from scipy import stats
    k = len(yi)
    w = [1 / v for v in vi]
    fe = sum(a * b for a, b in zip(w, yi)) / sum(w)
    t2 = 0.0
    if method == "DL":
        q = sum(a * (b - fe) ** 2 for a, b in zip(w, yi))
        c = sum(w) - sum(a * a for a in w) / sum(w)
        t2 = max(0.0, (q - (k - 1)) / c) if c > 0 else 0.0
    elif method == "PM":
        from .synth import _paule_mandel_tau2
        t2 = float(_paule_mandel_tau2(yi, vi))
    ww = [1 / (v + t2) for v in vi]
    mu = sum(a * b for a, b in zip(ww, yi)) / sum(ww)
    if hk and k >= 2:
        se = math.sqrt(sum(a * (b - mu) ** 2 for a, b in zip(ww, yi)) / (k - 1) / sum(ww))
        q = stats.t.ppf(0.975, k - 1)
    else:
        se, q = math.sqrt(1 / sum(ww)), z
    return mu, mu - q * se, mu + q * se


def positive_control(rows: list, printed: dict, measure: str) -> dict:
    """Does the meta's own printed pooled result follow from the rows extracted from it? FE/DL/PM, each +/- HK; the
    tolerance is the printed rounding plus one printed unit for row-rounding propagation. A meta that fails is unused."""
    ratio = measure.upper() in RATIO
    g = math.exp if ratio else (lambda x: x)
    pairs = [row_yi_vi(r) for r in rows]
    if len(rows) < 2 or any(p is None for p in pairs):
        return {"reproduced": False, "why": "FEWER_THAN_2_USABLE_ROWS", "methods": []}
    yi, vi = [p[0] for p in pairs], [p[1] for p in pairs]
    tol = lambda s: _half(s) * 3 + 1e-9                      # noqa: E731 - printed half-unit + one unit of propagation
    ok = []
    for m in ("FE", "DL", "PM"):
        for hk in (False, True):
            try:
                mu, lo, hi = (g(x) for x in pool(yi, vi, m, hk))
            except Exception:  # noqa: BLE001 - an estimator that fails to converge reproduces nothing
                continue
            if all(abs(v - _num(printed[k])) <= tol(printed[k]) for v, k in ((mu, "effect"), (lo, "lower"), (hi, "upper"))):
                ok.append(m + ("+HK" if hk else ""))
    return {"reproduced": bool(ok), "methods": ok, "why": None if ok else "PRINTED_POOL_NOT_REPRODUCED"}


# ------------------------------------------------------------------ admission gate (the primary gate's questions)

def nested_subgroup(row: SecondaryRow, randomised_n: Optional[int]) -> Optional[str]:
    """A row that is a SUBSET of the trial is not the trial: PLATO's planned-invasive stratum (n=13,408 of 18,624)
    carried as 'PLATO'. Caught by a subgroup word in the label/population, or by a total N well below enrolment."""
    txt = " ".join(x for x in (row.trial_label, row.population or "", (row.location or {}).get("row_label") or "") if x)
    if _SUBGROUP_LABEL.search(txt):
        return f"NESTED_SUBGROUP_LABEL:{_SUBGROUP_LABEL.search(txt).group(0)}"
    if randomised_n and row.n_t and row.n_c and (row.n_t + row.n_c) < 0.9 * randomised_n:
        return f"NESTED_SUBGROUP_N:{row.n_t + row.n_c}_of_{randomised_n}"
    return None


def measure_identity(row: SecondaryRow, estimand: str) -> Optional[str]:
    """The row's measure must BE the topic's estimand, or be derivable without assumption (counts -> RR/OR)."""
    m, e = (row.measure or "").upper(), (estimand or "").upper()
    if m == e:
        return None
    counts = None not in (row.events_t, row.n_t, row.events_c, row.n_c)
    if e in ("RR", "OR") and counts:
        return None
    return f"MEASURE_{m}_IS_NOT_ESTIMAND_{e}"


def outcome_identity(row: SecondaryRow, outcome_keywords: list, component_words: tuple = (),
                     core_words: tuple = ()) -> Optional[str]:
    """The meta's outcome definition must name the topic's outcome -- one of its keyword phrases, or its CORE word
    ('mortality' for '28-day all-cause mortality'; the timepoint is then a separate check, timepoint_identity).
    Naming only a COMPONENT of a composite (nonfatal MI for MACE) is a different outcome."""
    from . import lexicon
    d = lexicon.fold(row.outcome_definition or "")
    if not any(lexicon.fold(k) in d for k in outcome_keywords if k) and \
            not any(re.search(r"\b" + re.escape(lexicon.fold(c)) + r"\b", d) for c in core_words if c):
        return "OUTCOME_NOT_THE_TOPICS"
    if component_words and any(lexicon.fold(c) in d for c in component_words) and \
            not any(lexicon.fold(k) in d for k in outcome_keywords[:3]):
        return "OUTCOME_IS_A_COMPONENT"
    return None


def _days(t):
    """A stated follow-up as days ('28 days', '28-day', 'day 28', '6 months'); None when no length is stated."""
    t = (t or "").lower()
    m = re.search(r"(\d+)\s*[- ]?\s*(day|week|month|year)s?\b", t)
    if m:
        n, unit = int(m.group(1)), m.group(2)
    else:
        m = re.search(r"\b(day|week|month|year)\s*(\d+)", t)
        if not m:
            return None
        n, unit = int(m.group(2)), m.group(1)
    return n * {"day": 1, "week": 7, "month": 30, "year": 365}[unit]


def timepoint_identity(row: SecondaryRow, timepoint: Optional[str]) -> Optional[str]:
    """A topic that registers a timepoint (28-day mortality) cannot take a row whose meta does not state one: metas
    pool mortality across mixed follow-up. Stated timepoints must be the same length of time."""
    if not timepoint or _days(timepoint) is None:
        return None                      # 'trial end' / 'end of follow-up' registers no LENGTH: nothing to compare
    if not row.timepoint:
        return "TIMEPOINT_NOT_STATED_BY_META"
    a, b = _days(row.timepoint), _days(timepoint)
    return None if (a is not None and a == b) else f"TIMEPOINT_{row.timepoint}_NE_{timepoint}"


def admit(row: SecondaryRow, spec: dict, family_of, randomised_n: Optional[int] = None) -> SecondaryRow:
    """spec: {estimand, keywords, components, timepoint}. family_of(row) -> family id or None (ambiguous/unknown)."""
    reasons = validate(row)
    for check in (measure_identity(row, spec.get("estimand")),
                  outcome_identity(row, spec.get("keywords") or [], tuple(spec.get("components") or ()),
                                   tuple(spec.get("core") or ())),
                  timepoint_identity(row, spec.get("timepoint")),
                  nested_subgroup(row, randomised_n)):
        if check:
            reasons.append(check)
    fam = family_of(row)
    if not fam:
        reasons.append("FAMILY_NOT_RESOLVED")
    row.family_id = fam
    row.reasons = reasons
    row.state = REFUSED if reasons else UNVERIFIED
    return row


def consolidate(rows: list) -> list:
    """One trial family per meta: two rows of the same meta mapping to one family (a trial and its extension, two
    doses) are refused together rather than one being picked."""
    by = {}
    for r in rows:
        if r.state == UNVERIFIED:
            by.setdefault((r.meta_pmid, r.family_id), []).append(r)
    for (meta, fam), group in by.items():
        if len(group) > 1:
            for r in group:
                r.state, r.reasons = REFUSED, r.reasons + [f"FAMILY_{fam}_HAS_{len(group)}_ROWS_IN_META_{meta}"]
    return rows


# ------------------------------------------------------------------ cross-check and primary verification

def same_value(a: SecondaryRow, b: SecondaryRow) -> bool:
    """Rounding-aware equality at the coarser printed precision (counts must be identical)."""
    if None not in (a.events_t, b.events_t):
        return (a.events_t, a.n_t, a.events_c, a.n_c) == (b.events_t, b.n_t, b.events_c, b.n_c)
    if None in (a.effect, b.effect) or a.measure.upper() != b.measure.upper():
        return False
    for x, y in ((a.effect, b.effect), (a.lower, b.lower), (a.upper, b.upper)):
        d = min(_decimals(x), _decimals(y))
        if abs(_num(x) - _num(y)) > 0.5 * 10 ** (-max(d, 1)) + 1e-9:
            return False
    return True


def cross_check(rows: list) -> list:
    """Two independent metas on the same trial: agreement is a cross-check; disagreement BLOCKS both until resolved."""
    by = {}
    for r in rows:
        if r.state in (UNVERIFIED, VERIFIED):
            by.setdefault(r.family_id, []).append(r)
    for fam, group in by.items():
        metas = {r.meta_pmid for r in group}
        if len(metas) < 2:
            continue
        base = group[0]
        if not all(same_value(base, r) for r in group[1:]):
            for r in group:
                r.state = BLOCKED
                r.reasons = r.reasons + [f"CROSSCHECK_DISAGREES:{sorted(metas)}"]
    return rows


def verify_against_primary(row: SecondaryRow, primary: Optional[dict]) -> SecondaryRow:
    """primary: {'measure','effect','lower','upper' | 'events_t','n_t','events_c','n_c', 'span', 'source'} from the
    trial's OWN report/registry. None -> the row stays queued. A mismatch names the field, both values and locations,
    and which side the evidence points to: the primary value is taken as right only when its numbers are IN its span."""
    if row.state not in (UNVERIFIED,) or not primary:
        return row
    p = SecondaryRow(meta_pmid="primary", meta_doi="", location={"kind": "primary", "id": primary.get("source", "")},
                     source_digest="0" * 64, provenance="PRIMARY", trial_label=row.trial_label,
                     measure=primary.get("measure") or row.measure, outcome_definition=row.outcome_definition,
                     events_t=primary.get("events_t"), n_t=primary.get("n_t"), events_c=primary.get("events_c"),
                     n_c=primary.get("n_c"), effect=primary.get("effect"), lower=primary.get("lower"),
                     upper=primary.get("upper"))
    # our primary values are floats ('0.80' arrives as 0.8, one decimal): restore each number's PRINTED form from its own
    # span, so the comparison runs at the precision the trial printed (VITAL 0.81 vs 0.80 is a difference, not a match)
    span_tokens = re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d])", (primary.get("span") or "").replace("·", "."))
    for k in ("effect", "lower", "upper"):
        v = getattr(p, k)
        if v is not None:
            same = [t for t in span_tokens if abs(float(t) - float(v)) < 1e-12]
            if same:
                setattr(p, k, max(same, key=_decimals))
    # the primary gave COUNTS and the meta printed a ratio: derive the ratio + CI from the counts (no assumption), and
    # compare at the meta's printed precision (13/81 vs 13/71 IS RR 0.88 [0.44, 1.76])
    derived = False
    if row.effect is not None and p.effect is None and None not in (p.events_t, p.n_t, p.events_c, p.n_c) and \
            row.measure.upper() in ("RR", "OR"):
        p.measure = row.measure.upper()
        yi, vi = row_yi_vi(p)
        z = 1.959963984540054
        d = max(_decimals(row.effect), 1)
        p.effect, p.lower, p.upper = (f"{math.exp(x):.{d}f}" for x in (yi, yi - z * math.sqrt(vi), yi + z * math.sqrt(vi)))
        derived = True
    # different MEASURES (a meta's RR against the trial's HR) are not a numeric disagreement: nothing to compare, the
    # row stays queued for a same-measure primary
    if row.effect is not None and p.effect is not None and row.measure.upper() != (p.measure or "").upper():
        row.verification = {"result": "MEASURE_DIFFERS", "secondary_measure": row.measure, "primary_measure": p.measure,
                            "primary_source": primary.get("source")}
        return row
    if same_value(row, p):
        row.state = VERIFIED
        row.verification = {"result": "MATCH" + ("_FROM_PRIMARY_COUNTS" if derived else ""),
                            "primary_source": primary.get("source"), "primary_span": primary.get("span")}
        return row
    span = primary.get("span") or ""
    nums = [x for x in (primary.get("effect"), primary.get("lower"), primary.get("upper"), primary.get("events_t"),
                        primary.get("n_t"), primary.get("events_c"), primary.get("n_c")) if x is not None]
    # anchored NUMERICALLY: '0.8' is the span's '0.80' (a float drops the trailing zero; the span keeps it)
    in_span = {float(m) for m in re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d])", span.replace("·", "."))}
    anchored = bool(nums) and all(float(n) in in_span for n in nums)
    row.state = MISMATCH
    row.verification = {"result": "MISMATCH",
                        "secondary": {k: getattr(row, k) for k in ("measure", "effect", "lower", "upper", "events_t",
                                                                    "n_t", "events_c", "n_c")},
                        "secondary_location": {"meta_pmid": row.meta_pmid, **row.location},
                        "primary": {k: primary.get(k) for k in ("measure", "effect", "lower", "upper", "events_t",
                                                                "n_t", "events_c", "n_c")},
                        "primary_source": primary.get("source"), "primary_span": span,
                        "which_side": "SECONDARY_WRONG (primary numbers are in the primary's own span)" if anchored
                        else "UNDETERMINED (primary value not anchored in a primary span)"}
    return row


def g1_countable(rows: list, comparator_meta_ids: set) -> list:
    """G1 'k matched' against a comparator: only PRIMARY_VERIFIED rows, and never a row sourced FROM that comparator
    (it would be the comparator agreeing with itself)."""
    ids = {str(x) for x in comparator_meta_ids}
    return [r for r in rows if r.state == VERIFIED and str(r.meta_pmid) not in ids and str(r.meta_doi) not in ids]
