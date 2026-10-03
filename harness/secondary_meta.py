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
    # ARM-LEVEL continuous data as printed (a RevMan-style table: 'mean (SD)' and N per arm). A meta that prints these
    # pooled FROM them, so the positive control uses them; its printed per-trial CI is checked against them.
    mean_t: Optional[str] = None
    sd_t: Optional[str] = None
    mean_c: Optional[str] = None
    sd_c: Optional[str] = None
    findings: list = field(default_factory=list)     # typed findings ABOUT the meta's row (never a refusal reason)

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


_SIGNS = str.maketrans({"−": "-", "‒": "-", "–": "-", "—": "-", "‐": "-", "‑": "-",
                        "·": "."})


def _cell_text(el):
    """A cell's text with typographic signs folded to ASCII: a table printing '−11.50 (−13.68, −9.32)' (U+2212
    MINUS SIGN; Medicine 2026, PMID 42536519) otherwise yields no row and no pooled row, and the table silently drops.
    A minus glued to the next digit after a space ('− 10.90') is rejoined."""
    t = re.sub(r"\s+", " ", "".join(el.itertext())).strip().translate(_SIGNS)
    return re.sub(r"(?<![\d)])-\s+(?=\d)", "-", t)


def _measure_of(text):
    hits = [m for m, rx in _MEASURE.items() if rx.search(text or "")]
    return hits[0] if len(hits) == 1 else None


_MEAN_SD_CELL = re.compile(r"^(-?\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*\)$")
_INT_CELL = re.compile(r"^\d+$")
_CONTROL_HEAD = re.compile(r"placebo|control|comparator|usual care|standard", re.I)


def _arm_level(row: SecondaryRow, cells: list, header: Optional[list]) -> None:
    """Fill mean/SD/N per arm from a RevMan-style row: exactly two 'mean (SD)' cells, each followed by an integer N
    cell. The arms are told apart by the HEADER (the second must name the control, the first must not); with no aligned
    header the arm-level data are not taken (the row keeps its printed MD + CI only)."""
    pairs = [(i, m) for i, c in enumerate(cells[1:-1], 1) for m in [_MEAN_SD_CELL.match(c)]
             if m and _INT_CELL.match(cells[i + 1])]
    if len(pairs) != 2 or not header:
        return
    (i1, a), (i2, b) = pairs
    if _CONTROL_HEAD.search(header[i1]) or not _CONTROL_HEAD.search(header[i2]):
        return
    row.mean_t, row.sd_t, row.n_t = a.group(1), a.group(2), int(cells[i1 + 1])
    row.mean_c, row.sd_c, row.n_c = b.group(1), b.group(2), int(cells[i2 + 1])
    d = arm_ci_discrepancy(row)
    if d:
        row.findings = row.findings + [d]


def _has_arms(row) -> bool:
    return None not in (row.mean_t, row.sd_t, row.n_t, row.mean_c, row.sd_c, row.n_c) and row.n_t > 0 and row.n_c > 0


def arm_ci_discrepancy(row: SecondaryRow, z=1.959963984540054) -> Optional[dict]:
    """A meta row whose PRINTED MD + CI does not follow from its OWN printed arms (mean, SD, N) is a typed finding about
    the meta (Medicine 2026, Rubino 2021: printed -12.40 (-14.75, -10.05); its arms give -12.40 (-13.75, -11.05)).
    Tolerance: half a printed unit plus 0.05 for the rounding of the printed means/SDs."""
    if not _has_arms(row) or None in (row.effect, row.lower, row.upper):
        return None
    md = _num(row.mean_t) - _num(row.mean_c)
    se = math.sqrt(_num(row.sd_t) ** 2 / row.n_t + _num(row.sd_c) ** 2 / row.n_c)
    derived = {"effect": md, "lower": md - z * se, "upper": md + z * se}
    off = {k: (getattr(row, k), round(v, 2)) for k, v in derived.items()
           if abs(_num(getattr(row, k)) - v) > _half(getattr(row, k)) + 0.05}
    return {"finding": "ROW_CI_NOT_FROM_ARMS", "printed_vs_arm_derived": off} if off else None


_GENERIC_TERMS = re.compile(r"^(?:(?:weighted |standardi[sz]ed )?mean differences?|percent(?:age)?|w?md|smd|"
                            r"hazard ratio|risk ratio|odds ratio|relative risk|primary (?:outcome|end ?point))$", re.I)


_CLAUSE_BREAK = re.compile(r"[,;]|\b(?:but|while|whereas|although)\b|\band (?:the|a|an)\b", re.I)


def pooled_sentence(text: str, pooled: dict, outcome_terms: list) -> Optional[str]:
    """TABLE OUTCOME IDENTITY BY THE META'S OWN WORDS: the sentence of the meta's text that prints the table's pooled
    row (the same effect + CI, typed, rounding-aware) AND names a registered outcome term. Generic measure words
    ('mean difference', 'percent', 'primary outcome') never identify an outcome. None when no such sentence exists.
    Medicine 2026 captions its weight table 'mean weight difference'; its abstract says 'greater weight loss than
    placebo (mean difference: -11.85%; 95% CI: -12.81 to -10.90)' -- the identity is the meta's, not ours."""
    terms = [t.lower() for t in outcome_terms if t and not _GENERIC_TERMS.match(t.strip())]
    t = _fold_text(text or "")
    t = re.sub(r"(?<![\d)])-\s+(?=\d)", "-", t)
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z])", t):
        if not any(k in s.lower() for k in terms):
            continue
        for m in _TEXT_TRIPLE.finditer(s):
            if not all(_eq_printed(a, pooled.get(k)) for a, k in ((m.group(1), "effect"), (m.group(2), "lower"),
                                                                  (m.group(3), "upper"))):
                continue
            # the term must GOVERN the numbers: it ends within 60 characters before them with no clause break between
            # ('Weight loss was assessed, but systolic blood pressure decreased (MD -5.00 ...)' names another endpoint)
            before = s[:m.start()].lower()
            for k in terms:
                j = before.rfind(k)
                gap = before[j + len(k):] if j >= 0 else None
                if gap is not None and len(gap) <= 60 and not _CLAUSE_BREAK.search(gap):
                    return s.strip()[:400]
    return None


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
        head_rows = [[_cell_text(c) for c in r if c.tag in ("th", "td")] for th in tw.iter("thead") for r in th.iter("tr")]

        def header_for(n, _rows=head_rows):
            """The header row aligned with an n-cell body row (the last thead row of that width), or None."""
            return next((h for h in reversed(_rows) if len(h) == n), None)
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
                r = SecondaryRow(meta_pmid=meta_pmid, meta_doi=meta_doi, location=loc, source_digest=digest,
                                 provenance="TYPED_TABLE", trial_label=cells[0], measure=measure,
                                 outcome_definition=caption[:300], effect=m.group(1).replace("·", "."),
                                 lower=m.group(2).replace("·", "."), upper=m.group(3).replace("·", "."))
                if measure == "MD":
                    _arm_level(r, cells, header_for(len(cells)))
                rows.append(r)
            elif len(counts) == 2 and not triples and measure in ("RR", "OR"):
                (ia, a), (ib, b) = counts
                # ARM ORDER from the header, not the column order: a 'Placebo | Drug' table read in column order
                # inverts every ratio. Control named first -> swap; no aligned header -> column order, recorded.
                hdr = header_for(len(cells))
                note = []
                if hdr and _CONTROL_HEAD.search(hdr[ia]) and not _CONTROL_HEAD.search(hdr[ib]):
                    a, b = b, a
                elif not (hdr and _CONTROL_HEAD.search(hdr[ib]) and not _CONTROL_HEAD.search(hdr[ia])):
                    note = [{"finding": "ARM_ORDER_FROM_COLUMN_ORDER"}]
                rows.append(SecondaryRow(meta_pmid=meta_pmid, meta_doi=meta_doi, location=loc, source_digest=digest,
                                         provenance="TYPED_TABLE", trial_label=cells[0], measure=measure,
                                         outcome_definition=caption[:300], events_t=int(a.group(1)), n_t=int(a.group(2)),
                                         events_c=int(b.group(1)), n_c=int(b.group(2)), findings=note))
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
    """(yi, vi) on the analysis scale: log for ratios, raw for differences; from counts (log RR/OR) or the CI. An MD row
    carrying its arms (mean, SD, N) is taken FROM THE ARMS, which is what a RevMan-style meta pooled."""
    ratio = row.measure.upper() in RATIO
    if row.measure.upper() == "MD" and _has_arms(row):
        return (_num(row.mean_t) - _num(row.mean_c),
                _num(row.sd_t) ** 2 / row.n_t + _num(row.sd_c) ** 2 / row.n_c)
    if row.effect is not None:
        e, lo, hi = _num(row.effect), _num(row.lower), _num(row.upper)
        if None in (e, lo, hi) or (ratio and min(e, lo, hi) <= 0) or not (lo < hi and lo <= e <= hi):
            return None        # reversed / zero-width / point-outside-CI: not a usable row (zero variance would divide)
        f = math.log if ratio else (lambda x: x)
        return f(e), ((f(hi) - f(lo)) / (2 * z)) ** 2
    a, n1, c, n2 = row.events_t, row.n_t, row.events_c, row.n_c
    if None in (a, n1, c, n2) or min(n1, n2) <= 0:
        return None            # neither an effect with its CI nor a full 2x2: not poolable (was a TypeError)
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
    # a topic whose estimand admits either ratio ('RR/HR': spironolactone, all-cause mortality) admits each named one
    if m == e or (m and m in {x.strip() for x in e.split("/")}):
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
    # a fractional length ('0.5 years') is read whole: '\d+' alone read '0.5 years' as 5 years
    m = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)\s*[- ]?\s*(day|week|month|year)s?\b", t)
    if m:
        n, unit = float(m.group(1)), m.group(2)
    else:
        m = re.search(r"\b(day|week|month|year)\s*(\d+(?:\.\d+)?)", t)
        if not m:
            return None
        n, unit = float(m.group(2)), m.group(1)
    d = n * {"day": 1, "week": 7, "month": 30, "year": 365}[unit]
    return int(d) if d == int(d) else d


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


def verify_against_primary(row: SecondaryRow, primary: Optional[dict], queue_reason: Optional[str] = None) -> SecondaryRow:
    """primary: {'measure','effect','lower','upper' | 'events_t','n_t','events_c','n_c', 'span', 'source'} from the
    trial's OWN report/registry. None -> the row stays queued. A mismatch names the field, both values and locations,
    and which side the evidence points to: the primary value is taken as right only when its numbers are IN its span."""
    if row.state not in (UNVERIFIED,):
        return row
    if not primary:
        # QUEUED: no primary value of the trial's own report yet. The reason is a typed field, never an absence: every
        # row left SECONDARY_UNVERIFIED must say why (queue_complete)
        row.verification = {"result": "QUEUED", "queue_reason": queue_reason or "NO_PRIMARY_VALUE"}
        return row
    p = SecondaryRow(meta_pmid="primary", meta_doi="", location={"kind": "primary", "id": primary.get("source", "")},
                     source_digest="0" * 64, provenance="PRIMARY", trial_label=row.trial_label,
                     measure=primary.get("measure") or row.measure, outcome_definition=row.outcome_definition,
                     events_t=primary.get("events_t"), n_t=primary.get("n_t"), events_c=primary.get("events_c"),
                     n_c=primary.get("n_c"), effect=primary.get("effect"), lower=primary.get("lower"),
                     upper=primary.get("upper"))
    # our primary values are floats ('0.80' arrives as 0.8, one decimal): restore each number's PRINTED form from its own
    # span, so the comparison runs at the precision the trial printed (VITAL 0.81 vs 0.80 is a difference, not a match)
    # a primary value that is not a plain number ('0:31', a sleep latency in h:mm) cannot be compared: the row stays queued
    bad = [k for k in ("effect", "lower", "upper") if getattr(p, k) is not None and _num(getattr(p, k)) is None]
    if bad:
        row.verification = {"result": "PRIMARY_NOT_NUMERIC", "queue_reason": "PRIMARY_NOT_NUMERIC", "fields": bad,
                            "primary_source": primary.get("source")}
        return row
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
        row.verification = {"result": "MEASURE_DIFFERS", "queue_reason": "MEASURE_DIFFERS",
                            "secondary_measure": row.measure, "primary_measure": p.measure,
                            "primary_source": primary.get("source")}
        return row
    if same_value(row, p):
        row.state = VERIFIED
        row.verification = {"result": "MATCH" + ("_FROM_PRIMARY_COUNTS" if derived else ""),
                            "route": "PRIMARY_EXTRACTION",
                            "primary_source": primary.get("source"), "primary_span": primary.get("span")}
        return row
    span = primary.get("span") or ""
    nums = [x for x in (primary.get("effect"), primary.get("lower"), primary.get("upper"), primary.get("events_t"),
                        primary.get("n_t"), primary.get("events_c"), primary.get("n_c")) if x is not None]
    # anchored NUMERICALLY: '0.8' is the span's '0.80' (a float drops the trailing zero; the span keeps it)
    # ...against the primary's span AND its full report text: a stored span is often clipped (PIONEER 6's ends before
    # "0.57 to 1.11"), which made a primary-right mismatch look UNDETERMINED
    anchor_text = span + " " + (primary.get("report_text") or "")
    in_span = {float(m) for m in re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d])", anchor_text.replace("·", "."))}
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


_NUM = re.compile(r"-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?")


def _fold_text(t):
    """What a typographer varies without changing a number: dashes/minus -> '-', mid-dot -> '.', NBSP/thin spaces -> ' '."""
    t = re.sub("[‐-―−]", "-", t or "")
    t = t.replace("·", ".").replace("‧", ".")
    t = re.sub("[    ]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _as_number(v):
    """A copied value as a plain number string ('12,933' -> '12933', '0·87' -> '0.87', U+2212 minus -> '-'); None if it
    is not a number ('0:31' h:mm, 'NR')."""
    s = _fold_text(str(v))
    if not _NUM.fullmatch(s):
        return None
    return s.replace(",", "")


def gate_locator_claim(claim: dict, shown_text: str, prefer: Optional[str] = None) -> tuple:
    """The deterministic gate on a recorded locator answer ('quote where the trial reports its result and copy the numbers').
    Returns (value dict or None, typed reason). The model only LOCATES: every accepted number is a string the trial's own
    text prints, inside a quote that is verbatim in the text that was shown. Reasons are distinct, never one bucket:
      NOT_REPORTED          the model said the text does not report it
      QUOTE_NOT_IN_TEXT     the quote is not in the shown text (after typographic folding)
      NO_NUMBERS_COPIED     reported with a quote but no number copied (was mislabelled NUMBER_NOT_IN_QUOTE: 13 of 58)
      NON_NUMERIC           a copied value is not a number ('0:31')
      NUMBER_NOT_IN_QUOTE   a copied number does not occur in the quote in any printed form
      INCOMPLETE            numbers clean, but neither a full effect+CI nor full arm counts
      ACCEPTED              effect (point, lower, upper) and/or arm counts, as plain numbers"""
    if not isinstance(claim, dict) or claim.get("state") != "REPORTED" or not claim.get("quote"):
        return None, "NOT_REPORTED"
    q = _fold_text(claim["quote"])
    if q not in _fold_text(shown_text):
        return None, "QUOTE_NOT_IN_TEXT"
    raw = {k: claim.get(k) for k in ("point", "lower", "upper", "events_t", "n_t", "events_c", "n_c")
           if claim.get(k) not in (None, "")}
    if not raw:
        return None, "NO_NUMBERS_COPIED"
    nums = {k: _as_number(v) for k, v in raw.items()}
    if any(v is None for v in nums.values()):
        return None, "NON_NUMERIC"
    qn = q.replace(",", "")
    if not all(re.search(r"(?<![\d.])" + re.escape(v.lstrip("-")) + r"(?![\d])", qn) for v in nums.values()):
        return None, "NUMBER_NOT_IN_QUOTE"
    # a SIGNED copy must be printed with its sign: '-2.5' is not in 'mean difference 2.5 (1.2 to 3.8)'
    if not all(re.search(r"-\s?" + re.escape(v.lstrip("-")) + r"(?![\d])", qn) for v in nums.values()
               if v.startswith("-")):
        return None, "SIGN_NOT_IN_QUOTE"
    meas = (claim.get("measure") or "").upper()
    meas = ("HR" if "HAZARD" in meas or meas == "HR" else "RR" if ("RISK" in meas or meas == "RR") else
            "OR" if ("ODDS" in meas or meas == "OR") else "MD" if ("MEAN" in meas or meas in ("MD", "WMD")) else meas)
    counts_ok = all(k in nums for k in ("events_t", "n_t", "events_c", "n_c"))
    # a request FOR COUNTS (to verify a meta's RR against a trial that reports an HR) takes the counts when both are
    # copied: returning the HR first left VITAL's 386/12,933 vs 419/12,938 unused and the row MEASURE_DIFFERS
    if all(k in nums for k in ("point", "lower", "upper")) and not (prefer == "counts" and counts_ok):
        return {"measure": meas, "effect": nums["point"], "lower": nums["lower"], "upper": nums["upper"],
                "span": claim["quote"]}, "ACCEPTED"
    if counts_ok and not all(float(nums[k]) == int(float(nums[k])) for k in ("events_t", "n_t", "events_c", "n_c")):
        return None, "NON_INTEGER_COUNT"
    if counts_ok:
        return {"measure": "RR", "events_t": int(float(nums["events_t"])), "n_t": int(float(nums["n_t"])),
                "events_c": int(float(nums["events_c"])), "n_c": int(float(nums["n_c"])), "span": claim["quote"]}, "ACCEPTED"
    return None, "INCOMPLETE"


def queue_complete(rows: list) -> list:
    """INVARIANT: every row left SECONDARY_UNVERIFIED is IN the verification queue with a typed reason. Returns the rows
    that break it (an unverified row with no queue entry is a row nobody will ever verify -- it silently stays
    provisional). The build refuses to write its output while this list is non-empty."""
    return [r for r in rows if r.state == UNVERIFIED and not ((r.verification or {}).get("queue_reason"))]


# ------------------------------------------------------------------ DETERMINISTIC verification (no model)

_MEASURE_WORDS = {"HR": r"\bHR\b|hazard ratio", "RR": r"\bRR\b|risk ratio|relative risk|rate ratio",
                  "OR": r"\bOR\b|odds ratio", "MD": r"\bW?MD\b|mean difference|difference"}
# point, then (anything but digits, or a "95%"), then lower SEP upper: "0.79; 95% confidence interval [CI], 0.57 to 1.11",
# "0.79 (0.57-1.11)", "0.79 [95% CI 0.57, 1.11]"
_TEXT_TRIPLE = re.compile(r"(-?\d+(?:\.\d+)?)(?:[^\d]|95\s?%){0,45}?(-?\d+(?:\.\d+)?)\s*(?:-|to|,)\s*(-?\d+(?:\.\d+)?)")


def _eq_printed(a, b):
    """Two printed numbers are the same at the coarser of their printed precisions."""
    if _num(a) is None or _num(b) is None:
        return False
    d = max(min(_decimals(a), _decimals(b)), 0)
    return abs(_num(a) - _num(b)) <= 0.5 * 10 ** (-d) + 1e-9


def _outcome_near(text, i, j, outcome_terms, window=400):
    w = text[max(0, i - window): j + window].lower()
    return any(t.lower() in w for t in outcome_terms if t)


def typed_match_text(row: SecondaryRow, text: str, outcome_terms: list, source_ref: str) -> Optional[dict]:
    """The meta's printed numbers FOUND in a primary text, by regex: an effect+CI triple equal to the row's (rounding-
    aware) with a word naming the SAME measure just before it, or both arms' events/N, each within an outcome-term
    window. Returns {"result": "TYPED_MATCH", source, span} or None. A miss is not a mismatch (the text may report
    it elsewhere or differently): the row stays queued."""
    t = _fold_text(text or "")
    if row.effect is not None and row.measure.upper() in _MEASURE_WORDS:
        mw = re.compile(_MEASURE_WORDS[row.measure.upper()], re.I)
        for m in _TEXT_TRIPLE.finditer(t):
            if not (_eq_printed(m.group(1), row.effect) and _eq_printed(m.group(2), row.lower)
                    and _eq_printed(m.group(3), row.upper)):
                continue
            if mw.search(t[max(0, m.start() - 80): m.start()]) and _outcome_near(t, m.start(), m.end(), outcome_terms):
                return {"result": "TYPED_MATCH", "source": source_ref, "span": t[max(0, m.start() - 160): m.end() + 40]}
    if None not in (row.events_t, row.n_t, row.events_c, row.n_c):
        def pair(e, n):
            return re.compile(rf"(?<![\d.]){e}\s*(?:/|of|out of)\s*{n:,}(?![\d])|(?<![\d.]){e}\s*(?:/|of|out of)\s*{n}(?![\d])")
        for m in pair(row.events_t, row.n_t).finditer(t):
            near = t[max(0, m.start() - 400): m.end() + 400]
            if pair(row.events_c, row.n_c).search(near) and _outcome_near(t, m.start(), m.end(), outcome_terms):
                return {"result": "TYPED_MATCH", "source": source_ref, "span": near[:400]}
    return None


def typed_match_registry(row: SecondaryRow, registry: dict, outcome_terms: list, source_ref: str) -> Optional[dict]:
    """The meta's numbers FOUND in posted CT.gov results (AACT): registry = {"outcomes": {oid: {title, time_frame}},
    "analyses": [{outcome_id, param_type, param_value, ci_lower, ci_upper}], "groups": {oid: [{group, count, n}]}}.
    The outcome title must name the topic outcome; an analysis must be the same measure with the same estimate + CI,
    or two result groups of one outcome must carry the row's (events, N) pairs."""
    want_param = {"HR": "hazard ratio", "RR": "risk ratio", "OR": "odds ratio", "MD": "mean difference"}.get(row.measure.upper())
    named = {oid for oid, o in (registry.get("outcomes") or {}).items()
             if any(t.lower() in (o.get("title") or "").lower() for t in outcome_terms if t)}
    if row.effect is not None and want_param:
        for a in registry.get("analyses") or []:
            if a.get("outcome_id") in named and want_param in (a.get("param_type") or "").lower() and \
                    _eq_printed(a.get("param_value"), row.effect) and _eq_printed(a.get("ci_lower"), row.lower) and \
                    _eq_printed(a.get("ci_upper"), row.upper):
                o = registry["outcomes"][a["outcome_id"]]
                return {"result": "TYPED_MATCH", "source": source_ref, "route": "PRIMARY_REGISTRY",
                        "span": f"{o.get('title')} [{o.get('time_frame')}]: {a.get('param_type')} {a.get('param_value')} "
                                f"({a.get('ci_lower')}, {a.get('ci_upper')})",
                        "registry_fields": registry_fields(registry, a["outcome_id"], analysis=a),
                        "registry_vs_publication": registry_vs_publication(row, o)}
    if None not in (row.events_t, row.n_t, row.events_c, row.n_c):
        for oid in named:
            g = registry.get("groups", {}).get(oid) or []
            # two DISTINCT result groups must carry the two arms: one group of 10/100 cannot be both arms of 10/100
            gl = [(x.get("count"), x.get("n")) for x in g if x.get("count") is not None and x.get("n") is not None]
            pairs = set(gl)
            ti = [i for i, p_ in enumerate(gl) if p_ == (row.events_t, row.n_t)]
            ci = [i for i, p_ in enumerate(gl) if p_ == (row.events_c, row.n_c)]
            if ti and ci and any(x != y for x in ti for y in ci):
                o = registry["outcomes"][oid]
                return {"result": "TYPED_MATCH", "source": source_ref, "route": "PRIMARY_REGISTRY",
                        "span": f"{o.get('title')}: groups {sorted(pairs)}",
                        "registry_fields": registry_fields(registry, oid),
                        "registry_vs_publication": registry_vs_publication(row, o)}
    return None


# ------------------------------------------------------------------ CT.gov / AACT as a PRIMARY source (2 Oct decision)

_POP_CLASS = (("SAFETY", re.compile(r"safety (?:analysis |population|set)|as[- ]treated|received (?:at least one|any) dose", re.I)),
              ("PER_PROTOCOL", re.compile(r"per[- ]protocol", re.I)),
              ("MITT", re.compile(r"modified intent|\bm-?ITT\b|full analysis set", re.I)),
              ("ITT", re.compile(r"intent(?:ion)?[- ]to[- ]treat|\bITT\b|all randomi[sz]ed|randomi[sz]ed participants", re.I)))


def population_class(text: Optional[str]) -> str:
    """The analysis population a registry/publication STATES, typed: SAFETY / PER_PROTOCOL / MITT / ITT / NOT_STATED.
    Order matters: 'modified intention-to-treat' is MITT, not ITT."""
    for name, rx in _POP_CLASS:
        if rx.search(text or ""):
            return name
    return "NOT_STATED"


def registry_fields(registry: dict, outcome_id: str, analysis: Optional[dict] = None) -> dict:
    """The typed fields a registry verification rests on, recorded beside the verdict: snapshot id + digest, outcome
    measure title, time frame, stated analysis population, arm counts per result group, and the analysis if one."""
    o = (registry.get("outcomes") or {}).get(outcome_id) or {}
    titles = registry.get("group_titles") or {}
    return {"snapshot": registry.get("_snapshot"), "outcome_id": outcome_id, "measure_title": o.get("title"),
            "time_frame": o.get("time_frame"), "population": o.get("population"),
            "population_class": population_class(o.get("population")), "units_analyzed": o.get("units_analyzed"),
            "arm_counts": [dict(x, title=titles.get(str(x.get("group")))) for x in
                           (registry.get("groups") or {}).get(outcome_id) or []],
            "analysis": analysis}


def registry_vs_publication(row: SecondaryRow, outcome: dict) -> list:
    """Registry-vs-publication DIFFERENCES, recorded and never reconciled: a stated follow-up of a different length, or
    a stated analysis population of a different class. Unstated on either side is not a difference (nothing to
    compare) -- the registry's own values are kept in registry_fields regardless."""
    out = []
    a, b = _days(outcome.get("time_frame")), _days(row.timepoint)
    if a is not None and b is not None and a != b:
        out.append({"field": "timepoint", "registry": outcome.get("time_frame"), "publication": row.timepoint})
    pr, pp = population_class(outcome.get("population")), population_class(row.population)
    if "NOT_STATED" not in (pr, pp) and pr != pp:
        out.append({"field": "analysis_population", "registry": pr, "publication": pp,
                    "registry_text": (outcome.get("population") or "")[:200]})
    return out


# ------------------------------------------------------------------ TWO-SOURCE RULE (2 Oct decision)

TWO_SOURCE = "TWO_SOURCE_VERIFIED"
_REF_LIST = re.compile(rb"<ref-list\b.*?</ref-list>", re.S)
# either quote style: pub-id-type='pmid' is valid XML and was silently missed (an empty set reads as "cites nothing")
_PUB_ID = re.compile(rb"<pub-id[^>]*pub-id-type=[\"'](pmid|doi)[\"'][^>]*>\s*([^<\s]+)\s*</pub-id>", re.I)


def cited_ids_from_jats(jats: bytes) -> Optional[set]:
    """Every PMID and DOI (lower-cased) in a meta's reference list, by regex over its JATS. None when the JATS carries
    no reference list at all -- an unknown citation set, which the independence check treats as NOT independent."""
    lists = _REF_LIST.findall(jats or b"")
    if not lists:
        return None
    return {v.decode("utf-8", "replace").strip().lower() for blk in lists for _, v in _PUB_ID.findall(blk)}


def meta_ids(row: SecondaryRow) -> set:
    """Every identifier of the meta a row came from (PMID and DOI, lower-cased): one meta, however it is named."""
    return {str(row.meta_pmid or "").strip().lower(), str(row.meta_doi or "").strip().lower()} - {""}


def _alias_groups(known_metas) -> list:
    """known_metas as alias groups: each item a string (one id) or an iterable of the SAME meta's ids (PMID + DOI), so a
    meta cited by PMID in one reference list and by DOI in another is still recognised as one meta."""
    out = []
    for k in known_metas or ():
        g = {str(k).strip().lower()} if isinstance(k, (str, int)) else {str(x).strip().lower() for x in k if x}
        if g - {""}:
            out.append(g - {""})
    return out


def independence(a: SecondaryRow, b: SecondaryRow, refs_of, known_metas: set) -> Optional[str]:
    """None when two metas' extractions are INDEPENDENT; otherwise the typed reason they may not be. Fail-closed:
      SAME_META / SAME_BYTES             -- one extraction, not two (same PMID or same DOI)
      CITATIONS_UNKNOWN:<meta>           -- no reference list to check
      CITES_OTHER:<a>-><b>               -- one meta cites the other (may have copied its extraction)
      COMMON_CITED_META:<ids>            -- both cite a third meta of this topic, under any of its ids (may both have
                                            copied it)"""
    ia, ib = meta_ids(a), meta_ids(b)
    if ia & ib:
        return "SAME_META"
    if a.source_digest and a.source_digest == b.source_digest:
        return "SAME_BYTES"
    ra, rb = refs_of(a.meta_pmid), refs_of(b.meta_pmid)
    for m, r in ((a.meta_pmid, ra), (b.meta_pmid, rb)):
        if r is None:
            return f"CITATIONS_UNKNOWN:{m}"
    if ib & ra:
        return f"CITES_OTHER:{a.meta_pmid}->{b.meta_pmid}"
    if ia & rb:
        return f"CITES_OTHER:{b.meta_pmid}->{a.meta_pmid}"
    common = [g for g in _alias_groups(known_metas) if not (g & (ia | ib)) and (g & ra) and (g & rb)]
    if common:
        return f"COMMON_CITED_META:{','.join(sorted(min(g) for g in common))}"
    return None


def same_tuple(a: SecondaryRow, b: SecondaryRow) -> Optional[str]:
    """Two rows print the same TYPED TUPLE: the same value (same_value) AND no stated difference in timepoint length,
    analysis-population class or arm dose. Returns None when the same, else the differing field. Unstated on either
    side is not a difference (admit() already held both rows to the topic's registered outcome/timepoint)."""
    if not same_value(a, b):
        return "VALUE"
    da, db = _days(a.timepoint), _days(b.timepoint)
    if da is not None and db is not None and da != db:
        return "TIMEPOINT"
    pa, pb = population_class(a.population), population_class(b.population)
    if "NOT_STATED" not in (pa, pb) and pa != pb:
        return "POPULATION"
    if a.arm_dose and b.arm_dose and _fold_text(a.arm_dose).lower() != _fold_text(b.arm_dose).lower():
        return "ARM_DOSE"
    return None


def two_source(rows: list, refs_of, known_metas: set) -> list:
    """A row with no primary match is TWO_SOURCE_VERIFIED when two INDEPENDENT metas print the same typed tuple for the
    same trial family (same_tuple: value, and no stated difference in timepoint / population / dose). Only still-queued
    rows are considered (a disagreement was already BLOCKED by cross_check). A row whose agreeing partners are all
    dependent stays queued, with the dependence reason appended to its queue reason. Each independent pair is recorded
    by PMID (independent_pairs) and by every id of both metas (independent_pair_ids), so the G1 comparator can be
    removed whichever id it is named by."""
    by = {}
    for r in rows:
        if r.state == UNVERIFIED:
            by.setdefault(r.family_id, []).append(r)
    for fam, group in by.items():
        pairs, pair_ids, dep = [], [], {}
        for i, x in enumerate(group):
            for y in group[i + 1:]:
                if (meta_ids(x) & meta_ids(y)) or same_tuple(x, y):
                    continue
                why = independence(x, y, refs_of, known_metas)
                if why is None:
                    pairs.append(sorted([x.meta_pmid, y.meta_pmid]))
                    pair_ids.append(sorted(meta_ids(x) | meta_ids(y)))
                else:
                    dep.setdefault(id(x), []).append(why)
                    dep.setdefault(id(y), []).append(why)
        sup = {m for p in pairs for m in p}
        for r in group:
            prior = (r.verification or {}).get("queue_reason")
            if r.meta_pmid in sup:
                r.state = TWO_SOURCE
                r.verification = {"result": "TWO_SOURCE_MATCH", "route": "TWO_SOURCE", "supports": sorted(sup),
                                  "independent_pairs": pairs, "independent_pair_ids": pair_ids,
                                  "prior_queue_reason": prior}
            elif id(r) in dep:
                r.verification = dict(r.verification or {}, queue_reason=(prior or "NO_PRIMARY") +
                                      " | TWO_SOURCE_NOT_INDEPENDENT:" + ";".join(sorted(set(dep[id(r)]))))
    return rows


def route_of(row: SecondaryRow) -> str:
    """The verification ROUTE a row reached, for per-topic reporting: PRIMARY (text, registry or our extraction),
    TWO_SOURCE, or UNVERIFIED (queued / mismatch / blocked)."""
    if row.state == VERIFIED:
        return "PRIMARY"
    if row.state == TWO_SOURCE:
        return "TWO_SOURCE"
    if row.state == SECONDARY_SINGLE:
        return "SECONDARY_SINGLE"
    return "UNVERIFIED"


# ------------------------------------------------------------------ SECONDARY_SINGLE (Mahmood decision, 3 Oct)
# Per-trial rows from ONE published meta that is NOT the comparator count toward G1 when NO primary source is open,
# provided that meta SELF-REPRODUCES its pooled result (its own rows, pooled, give its printed pool: the positive
# control of a typed table / the gate of a figure read / the dual-model reader's stated-model reconstruction).
SECONDARY_SINGLE = "SECONDARY_SINGLE"


def secondary_single(rows: list, comparator_meta_ids: set, primary_open, reproduces) -> list:
    """Rows still SECONDARY_UNVERIFIED after primary verification and the two-source rule become SECONDARY_SINGLE when
      * the meta is not the comparator (under any of its ids),
      * reproduces(row) -- the meta self-reproduced its printed pooled result from its rows, and
      * not primary_open(row) -- no open primary source exists for the trial (an open one must be extracted instead;
        the row then stays queued with reason SECONDARY_SINGLE_REFUSED:PRIMARY_SOURCE_OPEN).
    A BLOCKED row (two metas disagree), a MISMATCH and a REFUSED row are never eligible. Returns the rows changed."""
    ids = {str(x).strip().lower() for x in comparator_meta_ids} - {""}
    out = []
    for r in rows:
        if r.state != UNVERIFIED or (meta_ids(r) & ids) or not reproduces(r):
            continue
        prior = (r.verification or {}).get("queue_reason")
        opened = primary_open(r)
        if opened:
            r.verification = dict(r.verification or {}, queue_reason=(prior or "NO_PRIMARY") +
                                  f" | SECONDARY_SINGLE_REFUSED:PRIMARY_SOURCE_OPEN:{opened}")
            continue
        r.state = SECONDARY_SINGLE
        r.verification = {"result": "SECONDARY_SINGLE", "route": "SECONDARY_SINGLE", "meta": r.meta_pmid,
                          "prior_queue_reason": prior,
                          "basis": "one non-comparator meta that self-reproduces its pooled result; no open primary "
                                   "source for the trial (decision 3 Oct)"}
        out.append(r)
    return out


def verify_typed(row: SecondaryRow, sources: list, outcome_terms: list) -> SecondaryRow:
    """DETERMINISTIC VERIFICATION FIRST: try every held primary source (texts and the posted registry) for the meta's
    exact printed numbers; a typed match -> PRIMARY_VERIFIED (no model). sources: [(kind, ref, payload)] with kind
    'text' or 'registry'."""
    if row.state != UNVERIFIED:
        return row
    for kind, ref, payload in sources:
        hit = (typed_match_text(row, payload, outcome_terms, ref) if kind == "text"
               else typed_match_registry(row, payload, outcome_terms, ref))
        if hit:
            hit.setdefault("route", "PRIMARY_TEXT")
            row.state, row.verification = VERIFIED, hit
            return row
    return row


def g1_countable(rows: list, comparator_meta_ids: set) -> list:
    """G1 'k matched' against a comparator: PRIMARY_VERIFIED rows, and TWO_SOURCE_VERIFIED rows whose support survives
    removing the comparator (an independent pair with neither meta being the comparator, under any of its ids). Never a
    row sourced FROM the comparator: it would be the comparator agreeing with itself. Ids compare case-insensitively
    (DOIs are case-insensitive)."""
    ids = {str(x).strip().lower() for x in comparator_meta_ids} - {""}

    def ok(r):
        if meta_ids(r) & ids:
            return False
        if r.state in (VERIFIED, SECONDARY_SINGLE):      # SECONDARY_SINGLE: decision 3 Oct (comparator excluded above)
            return True
        v = r.verification or {}
        groups = v.get("independent_pair_ids") or v.get("independent_pairs") or []
        return r.state == TWO_SOURCE and any(not ({str(m).lower() for m in p} & ids) for p in groups)
    return [r for r in rows if ok(r)]


# ------------------------------------------------------------------ TABLE LOCATION gate (recorded proposals -> pool)

def gate_table_location(claim: dict, text: str, outcome_keywords: list, spec_name: str,
                        prefer: Optional[str] = None, interv: Optional[list] = None, comp: Optional[list] = None) -> tuple:
    """A recorded table-location proposal is admitted only when (1) gate_locator_claim accepts it (the quote is verbatim
    in the held text and every number it copies is printed in that quote), (2) the quote NAMES the topic's outcome by a
    non-generic keyword, and (3) for a declared SINGLE outcome the quote is not a composite: SMART's primary
    'major adverse kidney event (the composite of death, new renal-replacement therapy, or persistent renal
    dysfunction)' would otherwise bind as mortality. Returns (value | None, reason)."""
    from harness import extract
    val, why = gate_locator_claim(claim, text, prefer=prefer)
    if not val:
        return None, why
    q = claim.get("quote") or ""
    ql = q.lower()
    named = [k for k in outcome_keywords if k and k.lower() not in extract.GENERIC_ANCHORS
             and extract._kw_in_sentence(k, ql)]
    if not named:
        return None, "OUTCOME_NOT_NAMED_IN_QUOTE"
    # the keyword must GOVERN the numbers: it precedes the first copied number with no sentence/clause break between
    # ('Mortality was similar. Stroke HR 0.80 (0.60 to 0.95)' names mortality, but the numbers are stroke's)
    qf = _fold_text(q)
    firsts = [m.start() for v in (claim.get(k) for k in ("point", "events_t", "lower", "n_t", "events_c", "n_c"))
              if v not in (None, "") for m in [re.search(r"(?<![\d.])" + re.escape(str(v).lstrip("-")) + r"(?![\d])",
                                                          qf.replace(",", ""))] if m]
    first = min(firsts) if firsts else len(qf)
    before = qf.replace(",", "")[:first].lower()
    governs = False
    for k in named:
        j = before.rfind(_fold_text(k).lower())
        if j >= 0 and not re.search(r"[.;]\s|\b(?:but|while|whereas|although)\b", before[j:]):
            governs = True
    if not governs:
        return None, "OUTCOME_DOES_NOT_GOVERN_THE_NUMBERS"
    # the harness never takes a subgroup / post-hoc / per-protocol result as the trial's (abstract rule, same detector),
    # in the quote OR in the text just before it (a heading 'Subgroup analysis: women only.' the quote leaves out)
    tf = _fold_text(text)
    at = tf.find(qf)
    if extract._is_subgroup_sentence(q) or (at > 0 and extract._is_subgroup_sentence(tf[max(0, at - 200):at])):
        return None, "SUBGROUP_OR_POST_HOC_QUOTED"
    # ARMS BY THEIR LABELS: when the quote names both arms, each copied count must follow ITS OWN arm's label, and a
    # 'control versus drug' comparison is refused (it is the inverse of the topic's contrast)
    ql2 = qf.lower()
    it = [ql2.find(t.lower()) for t in (interv or []) if t and ql2.find(t.lower()) >= 0]
    ct = [ql2.find(t.lower()) for t in (comp or []) if t and ql2.find(t.lower()) >= 0]
    if it and ct:
        pi, pc = min(it), min(ct)
        if pc < pi and re.search(r"\b(?:versus|vs\.?|compared with)\b", ql2[pc:pi]):
            return None, "INVERSE_COMPARISON_QUOTED"
        if claim.get("events_t") and claim.get("events_c"):
            def owner(v):
                m = re.search(r"(?<![\d.])" + re.escape(str(v)) + r"(?![\d])", ql2)
                if not m:
                    return None
                prev = [(p, "t") for p in it if p < m.start()] + [(p, "c") for p in ct if p < m.start()]
                nxt = [(p, "t") for p in it if p > m.start()] + [(p, "c") for p in ct if p > m.start()]
                if prev:
                    return max(prev)[1]
                return min(nxt)[1] if nxt else None
            ot, oc = owner(claim["events_t"]), owner(claim["events_c"])
            if ot and oc and (ot, oc) != ("t", "c"):
                return None, "ARM_COUNTS_SWAPPED"
    # a ratio and the arm events copied from ONE quote must point the same way: 'Total MACE | 8 (6.7) | 28 (21.7) |
    # 3.52 (1.60-7.74)' carries the INVERSE comparison (control vs colchicine)
    e = _num(claim.get("point"))
    et, ec, nt, nc = (_num(claim.get(k)) for k in ("events_t", "events_c", "n_t", "n_c"))
    if e and e > 0 and et is not None and ec is not None and et != ec:
        rt, rc = (et / nt, ec / nc) if (nt and nc) else (et, ec)
        if rt > 0 and rc > 0 and (e - 1) * (rt - rc) < 0 and abs(math.log(e)) > 0.05 and                 abs(math.log(rt / rc)) > (0.05 if (nt and nc) else 0.25):
            return None, "RATIO_DIRECTION_CONTRADICTS_ARM_EVENTS"
    if not extract.declared_is_composite(spec_name):
        if extract._names_composite(q) or re.search(r"\bcomposite\b|\bmajor adverse\b", q, re.I):
            return None, "COMPOSITE_QUOTED_FOR_SINGLE_OUTCOME"
    elif extract.composite_component_mismatch(spec_name, "composite outcome definition: " + q):
        return None, "COMPOSITE_COMPONENTS_DIFFER"
    return dict(val, named_by=named), "ACCEPTED"
