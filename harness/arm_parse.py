"""Arm-label parsing with MATCHED PLACEBOS, and the ordered contrast between two parsed arms (empagliflozin-HFpEF review,
2026-09-27).

SAK-HFpEF (NCT05138575) was excluded X-CONTRAST because "empagliflozin appears in every arm". Its arms are
  A  Empagliflozin + Potassium Chloride
  B  Empagliflozin + Potassium Nitrate
  C  Potassium Chloride + Placebo for Empagliflozin
"Placebo for X" is a placebo MATCHED to X: arm C is NOT exposed to empagliflozin. A vs C is the empagliflozin-vs-placebo
contrast with potassium chloride held constant. The substring test ("empagliflozin" in the label) read C as exposed.

The same shape, in other words: "placebo Circadin", "fish oil placebo", "empagliflozin-matching placebo", "matching placebo
for X", "placebo (X)", "placebo to match X". An arm component that names a placebo is never an active exposure to the agent
it names. "fish oil/fish oil placebo" is two LEVELS inside one listed arm (a collapsed factorial label): exposure varies
within the arm, so the arm is neither exposed nor unexposed.

The design travels with the contrast: a CROSSOVER's arms are periods within the same people -- within-person dependence,
periods, washout and carryover -- never independent parallel arms. Only what the held registry states is filled in; the rest
is NOT_IN_HELD_BYTES, never assumed.
"""
from __future__ import annotations

import re
from typing import Any

NOT_IN_HELD_BYTES = "NOT_IN_HELD_BYTES"

# A daily total is not an administration schedule: 60 mg/day does not say QD.
_FREQUENCIES = {
    "BID": r"\btwice[ -](?:daily|a day|per day)\b|\bb\.?i\.?d\.?\b|\bb\.?d\.?\b|\bevery\s*12\s*(?:h|hours?)\b|\bq\s*12\s*h\b",
    "TID": r"\b(?:three|3)[ -]times[ -](?:daily|a day|per day)\b|\bthrice[ -]daily\b|\bt\.?i\.?d\.?\b|\bevery\s*8\s*(?:h|hours?)\b|\bq\s*8\s*h\b",
    "QW": r"\bonce[ -](?:weekly|a[ -]week|per week)\b|\bweekly\b|\bq\.?w\.?\b|\bevery\s*7\s*days?\b",
    "QD": r"\bonce[ -](?:daily|a day|per day)\b|\bq\.?d\.?\b|\bo\.?d\.?\b|\bevery\s*24\s*(?:h|hours?)\b|\bq\s*24\s*h\b",
}
_MG = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?\s*-?\s*mg\b", re.I)
_PER_DAY = re.compile(r"\s*(?:/\s*(?:day|d)\b|per day\b)", re.I)
_PER_DAY_RATE = {"QD": 1, "BID": 2, "TID": 3, "QW": 1 / 7}
_UNSUPPORTED_FREQUENCY = re.compile(
    r"\b(?:twice|thrice|two times|three times)[ -]weekly\b|\b(?:biweekly|fortnightly|monthly)\b|\bevery\s+\d+\s+months?\b", re.I)


def regimen_frequencies(text: str) -> set[str]:
    text = _UNSUPPORTED_FREQUENCY.sub(" ", text or "")
    found = {code for code, pattern in _FREQUENCIES.items() if re.search(pattern, text or "", re.I)}
    if re.search(r"\bonce (?:or|and) twice[ -]daily\b", text or "", re.I):
        found.update(("QD", "BID"))
    # Bare 'daily' is QD only when it is not part of twice/three-times daily or mg/day.
    rest = str(text or "")
    for pattern in _FREQUENCIES.values():
        rest = re.sub(pattern, " ", rest, flags=re.I)
    if re.search(r"\bdaily\b", rest, re.I) and not re.search(r"\bdaily (?:total|dose)\b|\btotal daily\b", rest, re.I):
        found.add("QD")
    return found


def parse_regimen(text: str) -> dict[str, Any]:
    """Parse ONE agent/regimen label. Unknown or conflicting dimensions remain unknown.

    dose_mg is per administration; mg/day alone supplies neither it nor frequency.
    QW daily_mg is the arithmetic daily average, not a daily administration.
    """
    text = str(text or "").lower().strip().replace("\u00b7", ".")
    doses = list(_MG.finditer(text))
    freqs = regimen_frequencies(text)
    freq = next(iter(freqs)) if len(freqs) == 1 else "NOT_STATED"
    if _UNSUPPORTED_FREQUENCY.search(text):
        freq = "NOT_STATED"  # unsupported schedules must not become QW
    agent = text[:doses[0].start()] if doses else text
    for pattern in _FREQUENCIES.values():
        agent = re.sub(pattern, " ", agent, flags=re.I)
    agent = re.sub(r"\([^)]*\)|\b(?:oral|tablets?|capsules?|daily)\b", " ", agent)
    agent = " ".join(agent.split()).strip(" -:,") or None
    dose = None
    if len(doses) == 1:
        m = doses[0]
        amount = float(re.match(r"\d+(?:[.,]\d+)?", m.group()).group().replace(",", "."))
        total = bool(_PER_DAY.match(text[m.end():]) or re.search(r"\b(?:total daily|daily total|daily dose)\b", text))
        dose = amount / _PER_DAY_RATE[freq] if total and freq in _PER_DAY_RATE else (None if total else amount)
        if re.match(r"\s*/\s*(?:kg|ml|m2)\b", text[m.end():]):
            dose = None  # concentration or body-size dose is not an administration amount
    return {"agent": agent, "dose_mg": dose, "frequency": freq,
            "daily_mg": dose * _PER_DAY_RATE[freq] if dose is not None and freq in _PER_DAY_RATE else None}


def same_regimen(a, b) -> bool:
    a = parse_regimen(a) if isinstance(a, str) else a
    b = parse_regimen(b) if isinstance(b, str) else b
    return bool(a.get("agent") and a.get("dose_mg") is not None and a.get("frequency") in _PER_DAY_RATE
                and all(a.get(k) == b.get(k) for k in ("agent", "dose_mg", "frequency")))


def select_regimen(rule: str, record: dict[str, Any]) -> dict[str, Any]:
    """Validate a dose override against held agent-specific schedules, before using its effect.

    Legacy mg-only rules can inherit a SINGLE held frequency. Mixed or missing schedules
    are refused. Never resolve a mixed-frequency trial by matching daily totals.
    """
    selected = parse_regimen(rule)
    agent = selected["agent"]
    refusal = {"state": "AMBIGUOUS_REGIMEN", "regimen": selected,
               "reason": "AMBIGUOUS_REGIMEN: dose selection requires agent, dose per administration and an unambiguous held frequency"}
    if not agent:
        return refusal
    hit = re.compile(r"(?<![a-z0-9])" + re.escape(agent) + r"(?![a-z0-9])", re.I)
    labels = [s for s in (record.get("interventions") or []) if hit.search(s)
              and exposure(parse_arm(s), [agent]) == "ACTIVE"]
    # Sentence boundaries preserve dotted abbreviations and decimal doses.
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", record.get("abstract") or "")
    spans = labels + [s for s in sentences if hit.search(s)]
    if any(_UNSUPPORTED_FREQUENCY.search(s) for s in spans):
        return refusal
    frequencies = set().union(*(regimen_frequencies(s) for s in spans)) if spans else set()
    if selected["frequency"] == "NOT_STATED":
        if len(frequencies) != 1 or selected["dose_mg"] is None:
            return refusal
        selected = parse_regimen(rule + " " + next(iter(frequencies)))
    if selected["dose_mg"] is None or selected["frequency"] not in frequencies:
        return refusal
    candidates = [parse_regimen(s) for s in labels]
    # In prose, bind an explicit dose to its following schedule, never to a daily total.
    for span in spans:
        for m in _MG.finditer(span):
            tail = span[m.end():]
            stop = _MG.search(tail)
            tail = tail[:stop.start()] if stop else tail
            tail = re.split(r"[;,]|\b(?:versus|warfarin|placebo)\b", tail, maxsplit=1, flags=re.I)[0]
            candidates.append(parse_regimen(agent + " " + m.group() + tail))
    complete = [c for c in candidates if c["agent"] == agent and c["dose_mg"] is not None
                and c["frequency"] != "NOT_STATED"]
    if (len(frequencies) > 1 or complete) and not any(same_regimen(selected, c) for c in complete):
        return refusal
    return {"state": "SELECTED", "regimen": selected,
            "matched_arms": [s for s in labels if same_regimen(selected, parse_regimen(s))],
            "frequency_source": spans}

_SPLIT = re.compile(r"\s*(?:\+|;|,|\bplus\b|\bwith\b|\band\b)\s*", re.I)
_PLACEBO_WORD = re.compile(r"(?i)\b(?:placebos?|sham|dummy)\b")
# words that only say WHICH agent a placebo is matched to
_MATCH_WORDS = re.compile(r"(?i)\b(?:placebos?|sham|dummy|for|to|of|match(?:ing|ed)?|corresponding|identical)\b|[-()]")
_DOSE = re.compile(r"(?i)\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|µg|ug|g|ml|iu|units?)\b(?:\s*/\s*(?:day|d|kg))?|\b(?:oral|tablets?|capsules?|once|daily|od|bid)\b")


def _clean(s: str) -> str:
    return " ".join(_DOSE.sub(" ", s).split()).strip(" -").lower()


def _single(text: str) -> dict[str, Any]:
    if _PLACEBO_WORD.search(text):
        agent = _clean(_MATCH_WORDS.sub(" ", text))
        return {"text": text.strip(), "kind": "MATCHED_PLACEBO" if agent else "PLACEBO", "matched_to": agent or None}
    return {"text": text.strip(), "kind": "ACTIVE", "agent": _clean(text)}


def _component(text: str) -> dict[str, Any]:
    """A slash marks two LEVELS inside one listed arm only in the "X/X placebo" form: one side the active agent, the other a
    placebo matched to that SAME agent (VITAL-Echo "fish oil/fish oil placebo"). Every other slash belongs to one component --
    a fixed combination ("sacubitril/valsartan", "balcinrenone/dapagliflozin"), a dose ("15 mg/10 mg") or a unit ("mg/ml")
    (arm-parse corpus fixture: those four labels were read as levels)."""
    alts = [a.strip() for a in text.split("/") if a.strip()]
    if len(alts) == 2:
        a, b = _single(alts[0]), _single(alts[1])
        if {a["kind"], b["kind"]} == {"ACTIVE", "MATCHED_PLACEBO"}:
            act, pl = (a, b) if a["kind"] == "ACTIVE" else (b, a)
            x, y = act.get("agent") or "", pl.get("matched_to") or ""
            if x and y and (x in y or y in x):
                return {"text": text.strip(), "kind": "LEVELS_WITHIN_ARM", "levels": [a, b]}
    return _single(text)


def parse_arm(label: str) -> dict[str, Any]:
    comps = [_component(c) for c in _SPLIT.split(str(label or "")) if c.strip()]
    return {"label": str(label or ""), "components": comps}


def _hit(text: str | None, keywords) -> bool:
    t = (text or "").lower()
    return any(k and re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t) for k in keywords)


def _kws(keywords) -> list[str]:
    return [str(k).lower().strip() for k in (keywords or []) if str(k or "").strip()]


def exposure(arm: dict[str, Any], keywords) -> str:
    """ACTIVE | MATCHED_PLACEBO | VARIES_WITHIN_ARM | ABSENT -- for the agent named by `keywords`."""
    kws = _kws(keywords)
    states = set()
    for c in arm["components"]:
        if c["kind"] == "ACTIVE" and _hit(c["agent"], kws):
            states.add("ACTIVE")
        elif c["kind"] == "MATCHED_PLACEBO" and _hit(c["matched_to"], kws):
            states.add("MATCHED_PLACEBO")
        elif c["kind"] == "LEVELS_WITHIN_ARM":
            lv = {exposure({"components": [x]}, kws) for x in c["levels"]}
            if "ACTIVE" in lv and lv - {"ACTIVE"}:
                states.add("VARIES_WITHIN_ARM")
            elif "ACTIVE" in lv:
                states.add("ACTIVE")
            elif "MATCHED_PLACEBO" in lv:
                states.add("MATCHED_PLACEBO")
    # an arm that GIVES the agent and also carries a matching placebo (a double-dummy, MIRO-CKD's "balcinrenone/dapagliflozin
    # ... and matching placebo for dapagliflozin") is exposed: the dummy only preserves blinding
    if "VARIES_WITHIN_ARM" in states:
        return "VARIES_WITHIN_ARM"
    if "ACTIVE" in states:
        return "ACTIVE"
    if "MATCHED_PLACEBO" in states:
        return "MATCHED_PLACEBO"
    return "ABSENT"


def _other_actives(arm: dict[str, Any], kws) -> tuple[str, ...]:
    out = []
    for c in arm["components"]:
        if c["kind"] == "ACTIVE" and not _hit(c["agent"], kws):
            out.append(c["agent"])
        elif c["kind"] == "LEVELS_WITHIN_ARM":
            out.append("levels:" + c["text"].lower())
    return tuple(sorted(out))


def ordered_contrasts(labels, keywords, design: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Every ordered pair (exposed arm, unexposed arm) for the agent. CLEAN when every other active agent is the same on both
    sides (held constant); otherwise CONFOUNDED with the differing agents named. The design object rides on each contrast."""
    kws = _kws(keywords)
    arms = [parse_arm(x) for x in labels or []]
    out = []
    for a in arms:
        if exposure(a, kws) != "ACTIVE":
            continue
        for b in arms:
            eb = exposure(b, kws)
            if b is a or eb not in ("MATCHED_PLACEBO", "ABSENT"):
                continue
            oa, ob = _other_actives(a, kws), _other_actives(b, kws)
            rec = {"experimental_arm": a["label"], "comparator_arm": b["label"],
                   "comparator": "matched placebo" if eb == "MATCHED_PLACEBO" else "no exposure to the agent",
                   "state": "CLEAN" if oa == ob else "CONFOUNDED",
                   "held_constant": list(oa) if oa == ob else sorted(set(oa) & set(ob)),
                   "differs_also": [] if oa == ob else sorted(set(oa) ^ set(ob)),
                   "design": design or design_object(None)}
            out.append(rec)
    return out


def interest_in_every_arm(labels, keywords) -> bool:
    """True only when EVERY listed arm is ACTIVELY exposed. A matched-placebo arm, a plain placebo arm, an arm without the
    agent, or an arm whose exposure varies inside it all make this False -- the check can only remove a provable background."""
    arms = [parse_arm(x) for x in labels or []]
    return len(arms) >= 2 and all(exposure(a, keywords) == "ACTIVE" for a in arms)


def design_object(registry_row: dict[str, Any] | None) -> dict[str, Any]:
    """The trial design as the held registry states it. A crossover carries within-person dependence; its periods,
    period length, washout and carryover handling are filled only from held bytes (NOT_IN_HELD_BYTES otherwise)."""
    row = registry_row or {}
    model = str(row.get("intervention_model") or "").upper()
    if not model:
        return {"design": NOT_IN_HELD_BYTES, "source": None}
    obj = {"design": model, "source": "registry intervention_model",
           "model_description": row.get("intervention_model_description") or None}
    if model == "CROSSOVER":
        obj.update({"within_person": True,
                    "periods": NOT_IN_HELD_BYTES, "period_length": NOT_IN_HELD_BYTES, "washout": NOT_IN_HELD_BYTES,
                    "carryover": NOT_IN_HELD_BYTES,
                    "analysis_requirement": ("within-person (paired) contrast; periods are the same people, never independent "
                                             "parallel arms -- a parallel-arm variance double-counts them")})
    else:
        obj["within_person"] = False
    return obj
