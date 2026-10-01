"""Typed identity for every number the refusal auditor may cite (V1.0.1; external review of balanced-crystalloids, commit 6260e70c).

The auditor used to mark a refusal false when ANY sentence mentioned the outcome and held ANY number: crossover/exposure counts
disproved a mortality refusal, a composite disproved a component refusal, a raw count disproved a design refusal. A number is now
evidence against a refusal only through a typed identity that matches the refused claim on EVERY field:

  trial, comparison, outcome, part (COMPONENT | COMPOSITE), timepoint, population, effect measure, adjusted + model, role
  (OUTCOME_COUNT | EXPOSURE_COUNT | DENOMINATOR | BASELINE | EFFECT_ESTIMATE | UNDECIDED)

Deterministic regex / table extraction decides first. Where it cannot decide a number's ROLE (exposure vs outcome), a RECORDED,
replayable model proposal may decide -- read from registry/model_proposals/evidence_role.json, produced by reproducible_ai, never a
live call here -- and only if it passes the same deterministic cue check; the identity then says so (basis RECORDED_PROPOSAL,
record_id). Nothing in this module names a trial or a topic.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("OUTCOME_COUNT", "EXPOSURE_COUNT", "DENOMINATOR", "BASELINE", "EFFECT_ESTIMATE", "UNDECIDED")

# EXPOSURE is a real exposure/crossover cue. A bare "received" is NOT one: "patients who received the 5-mg dose" names the ARM.
_EXPOSURE = re.compile(r"\bunassigned\b|\bcross(?:ed)?[- ]?over\b|\bexposure\b|\bexposed\b|\bvolume of\b|\bnon-?study\b"
                       r"|\breceived any\b|\bopen-label\b(?=[^.;]{0,40}\b(?:use|treatment|therapy)\b)", re.I)
_OUTCOME = re.compile(r"\bdied\b|\bdeaths?\b|\bmortality\b|\bdeveloped\b|\boccurred\b|\bevents?\b|\bwas used in\b|\brequired\b"
                      r"|\bunderwent\b|\bnew renal[- ]replacement\b|\bhad (?:an? )?(?:[\w-]+ ){0,4}(?:event|injury|failure)\b"
                      r"|\b(?:was|were) (?:performed|observed|reported|diagnosed|recorded)\b|\bexperienced\b", re.I)
_DENOMINATOR = re.compile(r"\b(?:randomi[sz]ed|assigned|allocated|enrolled|included)\b", re.I)
_BASELINE = re.compile(r"\bat baseline\b|\bbaseline (?:characteristics|value|level)\b|\bat (?:enrollment|randomi[sz]ation)\b", re.I)
_COMPOSITE = re.compile(r"\bcomposite\b|\bmajor adverse (?:kidney|cardiovascular|cardiac|limb) events?\b|\bMAKE\d*\b|\bMACE\b", re.I)
_SUBGROUP = re.compile(r"\bamong (?:survivors|patients (?:who|with|without|not)[^.;,)]{0,60})|\bsubgroup\b|\bper[- ]protocol\b"
                       r"|\bas[- ]treated\b|\bin patients who\b", re.I)
_ADJUSTED = re.compile(r"\badjusted\b", re.I)
_MODEL = re.compile(r"[^.;]*(?:mixed[- ]effects?|random effects?|generali[sz]ed (?:linear|estimating)|\bGEE\b|cluster[- ]adjusted"
                    r"|proportional[- ]odds|Cox (?:proportional|regression|model)|logistic regression)[^.;]*", re.I)
_CLUSTER_MODEL = re.compile(r"random effects?|mixed[- ]effects?|generali[sz]ed estimating|\bGEE\b|cluster", re.I)
# spelled-out names match in any case ("Adjusted Odds Ratio" in a table header); abbreviations only in capitals, so the word "or"
# is never an odds ratio
_MEASURE = (("OR", re.compile(r"(?i:\bodds ratio\b)|\bOR\b")), ("HR", re.compile(r"(?i:\bhazard ratio\b)|\bHR\b")),
            ("RR", re.compile(r"(?i:\b(?:relative risk|risk ratio|rate ratio)\b)|\bRR\b")),
            ("RD", re.compile(r"(?i:\b(?:risk|absolute) difference\b)")))
_TIMEPOINT = re.compile(r"\b(?:within|before|at|by|through|after)\s+(\d+)\s+days?\b|\b(\d+)[- ]day\b|\bday\s+(\d+)\b"
                        r"|\b(in[- ]hospital|in the hospital|before (?:hospital|ICU) discharge|hospital discharge|ICU discharge)\b"
                        r"|\b(\d+)\s+months?\b", re.I)
_EFFECT_CELL = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*\(\s*(\d+(?:\.\d+)?)\s*(?:to|-|–|,)\s*(\d+(?:\.\d+)?)\s*\)\s*$")
_EFFECT_IN_TEXT = re.compile(r"\b(odds ratio|hazard ratio|relative risk|risk ratio|rate ratio|OR|HR|RR)\b[^0-9]{0,30}"
                             r"(\d+(?:\.\d+)?)\s*[\(\[;,]?\s*(?:95\s*%\s*(?:CI|confidence interval)\s*[,:=]?\s*)?[\(\[]?\s*"
                             r"(\d+(?:\.\d+)?)\s*(?:to|-|–|,)\s*(\d+(?:\.\d+)?)", re.I)
_TAG = re.compile(r"<[^>]+>")


def _text(fragment: str) -> str:
    return " ".join(html.unescape(_TAG.sub(" ", fragment)).split())


def measure_of(text: str) -> str | None:
    for name, rx in _MEASURE:
        if rx.search(text or ""):
            return name
    return None


def timepoint_of(text: str) -> str | None:
    """EVERY time qualifier the span states, in order ('in-hospital; 30 days' for 'In-hospital death before 30 days') -- the
    actual timepoint is kept whole, never cut to its first qualifier."""
    parts = []
    for m in _TIMEPOINT.finditer(text or ""):
        days = m.group(1) or m.group(2) or m.group(3)
        if days:
            tp = f"{days} days"
        elif m.group(4):
            tp = "in-hospital" if "hospital" in m.group(4).lower() and "icu" not in m.group(4).lower() else m.group(4).lower()
        else:
            tp = f"{m.group(5)} months"
        if tp not in parts:
            parts.append(tp)
    return "; ".join(parts) or None


def part_of(text: str) -> str:
    return "COMPOSITE" if _COMPOSITE.search(text or "") else "COMPONENT"


def population_of(text: str) -> str:
    m = _SUBGROUP.search(text or "")
    return m.group(0).strip() if m else "AS_REPORTED_UNQUALIFIED"


def lexical_role(text: str) -> str:
    """The deterministic role, from cues alone. UNDECIDED when the cues conflict or are absent."""
    if _EFFECT_IN_TEXT.search(text or ""):
        return "EFFECT_ESTIMATE"
    exposure, outcome = bool(_EXPOSURE.search(text or "")), bool(_OUTCOME.search(text or ""))
    if exposure and not outcome:
        return "EXPOSURE_COUNT"
    if outcome and not exposure:
        return "OUTCOME_COUNT"
    if exposure and outcome:
        return "UNDECIDED"
    if _BASELINE.search(text or ""):
        return "BASELINE"
    if _DENOMINATOR.search(text or ""):
        return "DENOMINATOR"
    return "UNDECIDED"


def role_supported(role: str, text: str) -> bool:
    """The deterministic check any role -- including a recorded model proposal -- must pass: the span carries that role's cue."""
    return {"OUTCOME_COUNT": bool(_OUTCOME.search(text or "")), "EXPOSURE_COUNT": bool(_EXPOSURE.search(text or "")),
            "DENOMINATOR": bool(_DENOMINATOR.search(text or "")), "BASELINE": bool(_BASELINE.search(text or "")),
            "EFFECT_ESTIMATE": bool(_EFFECT_IN_TEXT.search(text or ""))}.get(role, False)


def proposal_supported(role: str, quote: str, text: str) -> bool:
    """The deterministic check a RECORDED model proposal must pass (the regex already failed to decide this span, so the check is on
    the proposal's own verbatim quote, not on the cue list that failed): the quote is in the span, carries one of its numbers, and
    fits the role -- an outcome count quotes no exposure cue; an exposure count quotes an exposure word; a denominator quotes an
    allocation word; a baseline quotes 'baseline'; an effect estimate quotes a ratio with its interval."""
    q, span = " ".join((quote or "").split()), " ".join((text or "").split())
    if not q or q not in span or not re.search(r"\d", q):
        return False
    return {"OUTCOME_COUNT": not _EXPOSURE.search(q),
            "EXPOSURE_COUNT": bool(_EXPOSURE.search(q) or re.search(r"\b(?:received|given|administered|treated with)\b", q, re.I)),
            "DENOMINATOR": bool(_DENOMINATOR.search(q)), "BASELINE": bool(re.search(r"\bbaseline\b", q, re.I)),
            "EFFECT_ESTIMATE": bool(_EFFECT_IN_TEXT.search(q))}.get(role, False)


def span_key(text: str) -> str:
    return hashlib.sha256(" ".join((text or "").split()).encode("utf-8")).hexdigest()


def _recorded_proposals(root: Path = ROOT) -> dict[str, Any]:
    p = root / "registry" / "model_proposals" / "evidence_role.json"
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("proposals", {})
    except (OSError, ValueError):
        return {}


def resolve_role(text: str, proposals: dict[str, Any] | None = None) -> tuple[str, str, str | None]:
    """(role, basis, record_id). A recorded proposal is used only for an UNDECIDED span, and only if it passes role_supported."""
    role = lexical_role(text)
    if role != "UNDECIDED":
        return role, "REGEX", None
    prop = (proposals if proposals is not None else _recorded_proposals()).get(span_key(text))
    if (isinstance(prop, dict) and prop.get("role") in ROLES and prop["role"] != "UNDECIDED"
            and proposal_supported(prop["role"], prop.get("quote") or "", text)):
        return prop["role"], "RECORDED_PROPOSAL", prop.get("record_id")
    return "UNDECIDED", ("RECORDED_PROPOSAL_REFUSED" if prop else "REGEX"), (prop or {}).get("record_id") if isinstance(prop, dict) else None


def from_sentence(sentence: str, trial: str, source_id: str, proposals: dict[str, Any] | None = None) -> dict[str, Any]:
    role, basis, record_id = resolve_role(sentence, proposals)
    eff = _EFFECT_IN_TEXT.search(sentence or "")
    model = _MODEL.search(sentence or "")
    return {"trial": trial, "source_id": source_id, "span": " ".join(sentence.split())[:320], "kind": "SENTENCE",
            "role": role, "role_basis": basis, "role_record_id": record_id,
            "part": part_of(sentence), "timepoint": timepoint_of(sentence), "population": population_of(sentence),
            "effect_measure": measure_of(eff.group(1)) if eff else ("COUNTS" if role == "OUTCOME_COUNT" else None),
            "estimate": float(eff.group(2)) if eff else None, "ci": [float(eff.group(3)), float(eff.group(4))] if eff else None,
            "adjusted": bool(_ADJUSTED.search(sentence or "")), "model": model.group(0).strip()[:240] if model else None,
            "comparison": "TWO_ARMS_NAMED" if (re.search(r"\b(?:vs\.?|versus|compared with|compared to|respectively)\b", sentence or "", re.I)
                                               or len(re.findall(r"\b(?:group|arm)s?\b", sentence or "", re.I)) >= 2)
            else "UNSTATED"}


def from_tables(raw: str, trial: str, source_id: str) -> list[dict[str, Any]]:
    """One identity per table row that carries an effect estimate (and one per row of arm counts), with the table's model footnote,
    the row's own timepoint and part, and the section it sits under."""
    out = []
    for wrap in re.findall(r"<table-wrap.*?</table-wrap>", raw or "", re.S) or re.findall(r"<table.*?</table>", raw or "", re.S):
        feet = " ".join(_text(f) for f in re.findall(r"<table-wrap-foot>(.*?)</table-wrap-foot>", wrap, re.S)) or \
            " ".join(_text(f) for f in re.findall(r"<fn[^>]*>(.*?)</fn>", wrap, re.S))
        model = _MODEL.search(feet)
        composite_defined = {m.group(1).strip().lower() for m in re.finditer(r"(?:^|\W)(?:A|An|The)\s+([^.]{3,80}?)\s+is the composite of", feet)}
        header, section = [], ""
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", wrap, re.S):
            cells = [_text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            if not cells:
                continue
            if "<th" in tr and not header:
                header = cells
                continue
            if len(cells) == 1 or all(not c for c in cells[1:]):
                section = cells[0]
                continue
            label = cells[0]
            full_label = f"{section} :: {label}" if section else label
            is_component = bool(re.search(r"\bcomponents? of\b", section, re.I))
            part = "COMPONENT" if is_component else (
                "COMPOSITE" if (_COMPOSITE.search(label) or any(d and d in label.lower() for d in composite_defined)) else "COMPONENT")
            for i, cell in enumerate(cells[1:], start=1):
                m = _EFFECT_CELL.match(cell)
                col = header[i] if i < len(header) else ""
                if not m or not measure_of(col):
                    continue
                out.append({"trial": trial, "source_id": source_id, "span": f"{full_label} | {cell} [{col}]", "kind": "TABLE_ROW",
                            "role": "EFFECT_ESTIMATE", "role_basis": "TABLE", "role_record_id": None, "part": part,
                            "timepoint": timepoint_of(label) or timepoint_of(section), "population": population_of(label),
                            "effect_measure": measure_of(col), "estimate": float(m.group(1)),
                            "ci": [float(m.group(2)), float(m.group(3))], "adjusted": bool(_ADJUSTED.search(col)),
                            "model": model.group(0).strip()[:240] if model else None,
                            "comparison": "TWO_ARMS_NAMED" if len(header) >= 3 else "UNSTATED", "label": label, "section": section})
    return out


# a COUNT cell says it is one: 'n/N', 'n/N (x%)' or 'n (x%)' -- a bare number may be a percentage or a p-value
_COUNT_CELL = re.compile(r"^\s*(\d[\d,]*)\s*(?:/\s*(\d[\d,]*)\s*(?:\(\s*\d+(?:\.\d+)?\s*%?\s*\))?|\(\s*\d+(?:\.\d+)?\s*%?\s*\))\s*$")
_ANY_EVENT = re.compile(r"^\s*(?:any|all|overall|total)\b.*\b(?:adverse|event|effect)", re.I)
_NOT_AN_ARM = re.compile(r"\bp\b|p[- ]?value|\btotal\b|\ball patients\b|difference|ratio|\bCI\b|\bRR\b|\bOR\b|\bHR\b", re.I)
_PERCENT_ROW = re.compile(r"%\s*$|,\s*%|\(%\)\s*$|percent", re.I)
_RESTRICTING = re.compile(r"\bserious\b|\bsevere\b|\bgrade\s*(?:≥|>=|3|4)|\b(?:drug|treatment|study[- ]drug)[- ]related\b|\bfatal\b", re.I)


def count_rows(raw: str, trial: str, source_id: str) -> list[dict[str, Any]]:
    """Every table row that gives a COUNT of affected individuals per arm ('26/180 (14.4)' or '26 (14.4)'), one identity per labelled
    row. Rows are never combined here: a count belongs to the one label it is printed under."""
    out = []
    for wrap in re.findall(r"<table-wrap.*?</table-wrap>", raw or "", re.S) or re.findall(r"<table.*?</table>", raw or "", re.S):
        header, section = [], ""
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", wrap, re.S):
            cells = [_text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            if not cells:
                continue
            if "<th" in tr and not header:
                header = cells
                continue
            if len(cells) == 1 or all(not c for c in cells[1:]):
                section = cells[0]
                continue
            if _PERCENT_ROW.search(cells[0]):
                continue                                      # a row of percentages is not a row of counts
            arms = [(header[i] if i < len(header) else f"col{i}", _COUNT_CELL.match(c)) for i, c in enumerate(cells[1:], start=1)]
            counts = [(h, int(m.group(1).replace(",", "")), int(m.group(2).replace(",", "")) if m.group(2) else None)
                      for h, m in arms if m and not _NOT_AN_ARM.search(h)      # never pair an arm with a p-value/total column,
                      and not h.startswith("col")]                             # nor with a column whose header is missing
            if len(counts) < 2:
                continue
            out.append({"trial": trial, "source_id": source_id, "kind": "TABLE_COUNT_ROW", "label": cells[0], "section": section,
                        "span": f"{cells[0]} | " + " | ".join(f"{h}: {e}" + (f"/{n}" if n else "") for h, e, n in counts[:2]),
                        "role": "OUTCOME_COUNT", "role_basis": "TABLE", "role_record_id": None,
                        "any_event_row": bool(_ANY_EVENT.search(cells[0])),
                        "arms": [{"arm": h, "events": e, "n": n} for h, e, n in counts[:2]],
                        "part": part_of(cells[0]), "timepoint": timepoint_of(cells[0]) or timepoint_of(section),
                        "population": population_of(cells[0]), "effect_measure": "COUNTS", "estimate": None, "ci": None,
                        "adjusted": False, "model": None, "comparison": "TWO_ARMS_NAMED" if len(header) >= 3 else "UNSTATED"})
    return out


def names_the_outcome(label: str, outcome_name: str) -> bool:
    """A table row stands for an outcome only if it is named by the outcome's OWN name (not merely by a symptom keyword), and adds
    no restricting qualifier the outcome lacks ('serious ...' is a subset of 'adverse events ...')."""
    head = [w for w in re.findall(r"[a-z]{5,}", (outcome_name or "").lower()) if w not in ("adverse", "effects", "events", "outcome", "leading")]
    if not head or not any(w[:6] in (label or "").lower() for w in head):
        return False
    return not (_RESTRICTING.search(label or "") and not _RESTRICTING.search(outcome_name or ""))


def bind_labelled_count_row(raw: str, trial: str, source_id: str, outcome_terms: list[str], matches_term,
                            outcome_name: str = "") -> dict[str, Any]:
    """Bind a (specific) outcome to exactly ONE labelled count row of the same source's tables -- the recovery step after a number
    is rejected as the wrong endpoint. Refuses rather than guesses:
      - an 'any adverse event' row never stands for a specific endpoint;
      - two or more rows matching the outcome -> AMBIGUOUS (no pick);
      - symptom rows are NEVER summed into the outcome: without the table stating that the affected patients are distinct,
        a sum can count one patient twice. So no matching row -> NOT_FOUND, even when component symptoms are present."""
    rows = count_rows(raw, trial, source_id)
    hits = [r for r in rows if not r["any_event_row"] and matches_term(r["label"], outcome_terms)]
    # a row named by the outcome's OWN name ('gastrointestinal ...') outranks rows matched only through a symptom keyword
    # ('diarrh'): a symptom is a component of the outcome, not the outcome
    head = [w for w in re.findall(r"[a-z]{5,}", (outcome_name or "").lower()) if w not in ("adverse", "effects", "events", "outcome")]
    named = [r for r in hits if head and any(w[:6] in r["label"].lower() for w in head)]
    if len(named) == 1:
        return {"state": "BOUND", "row": named[0]}
    if len(hits) == 1:
        return {"state": "BOUND", "row": hits[0]}
    if len(hits) > 1:
        return {"state": "AMBIGUOUS", "rows": [h["label"] for h in hits]}
    return {"state": "NOT_FOUND", "why": "no row labelled with this outcome; symptom rows are not summed (patients not shown distinct)",
            "rows_seen": [r["label"] for r in rows]}


def claim_of(outcome: dict[str, Any], row: dict[str, Any], terms_text: str) -> dict[str, Any]:
    """The refused claim, typed on the same fields."""
    design = row.get("design") if isinstance(row.get("design"), dict) else {}
    reason = str(row.get("reason") or "")
    return {"trial": str(row.get("id") or row.get("label")), "outcome": outcome.get("name"),
            # the outcome's timepoint field, else the one its own NAME states ('Secondary infections by 28 days')
            "part": part_of(f"{outcome.get('name')} {terms_text}"),
            "timepoint": outcome.get("timepoint") or timepoint_of(outcome.get("name") or ""),
            "population": outcome.get("population"), "effect_measure": outcome.get("estimand"),
            "design_refusal": bool(design and design.get("adjustment_status") not in (None, "ADJUSTED", "RESOLVED")
                                   or "design_adjusted_effect" in reason or "design=" in reason),
            "design": design.get("design")}


def _timepoint_in(claim_tp: str | None, got: str | None) -> bool:
    if not claim_tp:
        return True                                                   # the claim does not constrain the timepoint
    if not got:
        return False                                                  # constrained, but the evidence's timepoint is unknown
    tp = claim_tp.lower()
    rng = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*day", tp)
    one = re.search(r"(\d+)\s*[- ]?day", tp)
    for q in got.split("; "):                                         # every qualifier the evidence states must fit the claim
        if q == "in-hospital":
            ok = "hospital" in tp
        else:
            m = re.match(r"(\d+) (days|months)", q)
            if not m:
                return False
            days = int(m.group(1)) * (30 if m.group(2) == "months" else 1)
            ok = (rng and int(rng.group(1)) <= days <= int(rng.group(2))) or (not rng and one and int(one.group(1)) == days)
        if not ok:
            return False
    return True


def mismatches(identity: dict[str, Any], claim: dict[str, Any], outcome_named: bool) -> list[str]:
    """Every field on which this evidence fails to be evidence ABOUT the refused claim. Empty only on a full match."""
    bad = []
    if identity["role"] not in ("OUTCOME_COUNT", "EFFECT_ESTIMATE"):
        bad.append(f"role:{identity['role']}")
    if not outcome_named:
        bad.append("outcome")
    if identity["part"] != claim["part"]:
        bad.append(f"part:{identity['part']}!={claim['part']}")
    if not _timepoint_in(claim.get("timepoint"), identity.get("timepoint")):
        bad.append(f"timepoint:{identity.get('timepoint')}")
    pop = str(claim.get("population") or "").lower()
    if identity["population"] != "AS_REPORTED_UNQUALIFIED" and (not pop or pop not in identity["population"].lower()):
        bad.append(f"population:{identity['population']}")
    want = claim.get("effect_measure")
    got = identity.get("effect_measure")
    if want and got not in (want, "COUNTS" if want in ("RR", "OR", "RD") else None):
        bad.append(f"effect_measure:{got}!={want}")
    if identity.get("comparison") != "TWO_ARMS_NAMED":
        bad.append("comparison")
    if claim.get("design_refusal"):
        if identity["role"] != "EFFECT_ESTIMATE" or not identity.get("adjusted") or not _CLUSTER_MODEL.search(identity.get("model") or ""):
            bad.append("design_variance: no design-adjusted estimate with a model that accounts for the design")
    return bad
