"""Conservative, source-span reader of allocation-level blinding.

No registry masking field is read here. Groups share an allocation sentence (and
background stratum); comparisons never cross strata. Unsupported mixed prose is
MIXED, not permission to borrow blinding from another comparison.
"""
from __future__ import annotations

import re

from . import arm_parse

BLINDED = "BLINDED"
OPEN_LABEL = "OPEN_LABEL"
NOT_STATED = "NOT_STATED"
MIXED = "MIXED"

_CUE = re.compile(r"\b(?:open[- ]label|unblinded|unmasked|not blinded|not masked|"
                  r"double[- ]blind(?:ed)?|blinded|masked)\b", re.I)
_OPEN = re.compile(r"open[- ]label|unblinded|unmasked|not blinded|not masked", re.I)
_OTHER_STUDIES = re.compile(r"\b(?:additional|other|further|separate)\b[^.;]{0,80}?\b(?:studies|trials)\b", re.I)
_RANDOM = re.compile(r"randomi[sz]ed|randomly (?:assigned|allocated)", re.I)
_FASHION = re.compile(r"\bin (?:a|an) (blinded|double[- ]blind|open[- ]label|unblinded) fashion", re.I)


def _state(cue):
    return OPEN_LABEL if _OPEN.search(cue) else BLINDED


def _sentences(text):
    # A period inside a decimal, abbreviation, or species name is not a boundary.
    return re.split(r"(?<=[.!?])\s+(?=[A-Z])", text)


def _labels(text):
    text = re.sub(r"^\s*(?:or|either|to receive|to|receive)\s+", "", text, flags=re.I)
    return [x.strip(" ,;.") for x in re.split(r",\s*|\s+or\s+|\s+versus\s+|\s+vs\.?\s+", text)
            if x.strip(" ,;.")]


def _arm_groups(sentence, index, background, specs):
    return [dict(arms=arms, blinding=state, background=background,
                 stratum=index, span=sentence) for arms, state in specs if arms]


def read_blinding(text: str) -> dict:
    """Return verbatim arm groups, their stratum/background, and text-level state.

    The bounded grammar recognises suffix/prefix 'in a ... fashion' and
    allocation sentences with one mode. Ancillary open-label periods/background
    and blinded endpoint assessment do not describe treatment allocation.
    """
    groups, cues = [], []
    for index, sentence in enumerate(_sentences(text or "")):
        matches = list(_CUE.finditer(sentence))
        if not matches:
            continue
        allocations = list(_RANDOM.finditer(sentence))
        # A later re-randomization can mention the earlier allocation as its
        # entry condition. The current contrast starts at the last allocation.
        allocation = allocations[-1] if allocations else None
        ancillary = re.search(r"extension|run[- ]in|follow-up|followed by open|"
                              r"open[- ]label use|(?:added|add-on) to open[- ]label|"
                              r"open[- ]label background|started taking open", sentence, re.I)
        relevant = []
        for m in matches:
            after = sentence[m.end():m.end() + 55]
            before = sentence[max(0, m.start()-45):m.start()]
            if re.match(r"\s+(?:cumulative|probability|biostatistician)", after, re.I):
                continue
            if not _OPEN.search(m.group()) and (re.match(r"[- ,]*(?:end[- ]?point|adjudication|interim|data|probability)", after, re.I)
                    or re.search(r"adjudicat|committee|assessors|analysts", before, re.I)):
                continue
            if ancillary and not allocation:
                continue
            # A cue inside a phrase naming OTHER studies ("three additional single-blind and open-label studies") describes a
            # different study set, not this record's comparisons. Written after reading melatonin 22346363 (its agreement there
            # is in-sample); every firing is counted in evidence/comparison_blinding/README.md.
            if not allocation and any(o.start() <= m.start() < o.end() for o in _OTHER_STUDIES.finditer(sentence)):
                continue
            if _OPEN.search(m.group()) and ancillary and re.search(r"extension|followed by open", sentence[m.start():], re.I):
                continue
            relevant.append(m)
            cues.append({"state": _state(m.group()), "span": sentence})
        if not relevant:
            continue
        bg = re.search(r"\bon background (.+?) treatment", sentence, re.I)
        add_on = re.search(r",\s*in addition to ([^.]+)", sentence, re.I)
        background = bg.group(1) if bg else add_on.group(1).strip() if add_on else ""
        # Explicit prefix groups: "two blinded ... arms (A vs placebo)
        # and one open-label ... arm (B)". No borrowing of a study-level cue.
        prefix_arms = list(re.finditer(
            r"(blinded|double[- ]blind|open[- ]label|unblinded)\s+[^().;]*?arms?\s*\(([^)]+)\)", sentence, re.I))
        if len(prefix_arms) >= 2:
            groups.extend(_arm_groups(sentence, index, background,
                [(_labels(m.group(2)), _state(m.group(1))) for m in prefix_arms]))
            continue
        fashion = list(_FASHION.finditer(sentence))
        if fashion and allocation:
            start = re.search(r"\bto (?:receive|either)\s+", sentence[allocation.end():], re.I)
            if start:
                pos = allocation.end() + start.end()
                for fm in fashion:
                    if fm.start() < pos:
                        continue
                    labels = _labels(sentence[pos:fm.start()])
                    groups.append(dict(arms=labels, blinding=_state(fm.group()),
                                       background=background, stratum=index, span=sentence))
                    pos = fm.end()
                continue
            # RE-LY shape: receive, in a blinded fashion, X or, in an
            # unblinded fashion, Y. Preserve the dose-bearing arm phrase.
            for i, fm in enumerate(fashion):
                end = fashion[i+1].start() if i+1 < len(fashion) else len(sentence)
                label = re.sub(r"[, ]*or[, ]*$", "", sentence[fm.end():end]).strip(" ,.")
                if label:
                    groups.append(dict(arms=[label], blinding=_state(fm.group()),
                                       background=background, stratum=index, span=sentence))
            continue
        states = {_state(m.group()) for m in relevant}
        if allocation and len(states) == 1:
            start = re.search(r"\b(?:to receive|to|compared)\s+", sentence[allocation.end():], re.I)
            if start:
                arm_text = sentence[allocation.end() + start.end():add_on.start() if add_on else len(sentence)]
                # A comparison, not the time interval preceding it.
                arm_text = re.sub(r"^.*?\bweeks to\s+", "", arm_text, flags=re.I)
                labels = _labels(arm_text)
                if relevant[0].start() > allocation.end() + start.end():
                    # A cue embedded after allocation can describe just one arm.
                    # Only a terminal 'fashion' (above) or 'all arms' is global.
                    continue
                if len(labels) >= 2:
                    groups.append(dict(arms=labels, blinding=next(iter(states)),
                                       background=background, stratum=index, span=sentence))
    states = {x["state"] for x in cues}
    return {"groups": groups, "statements": cues,
            "state": MIXED if len(states) > 1 else next(iter(states), NOT_STATED)}


def comparison_blinding(text: str, experimental_arm: str, comparator_arm: str,
                        *, background: str | None = None) -> str:
    """Blinding of an ordered pair; any explicitly open arm makes it open.

    Ambiguous repeated labels across strata are MIXED unless a background is
    supplied. No match in mixed prose remains MIXED (fail closed).
    """
    reading = read_blinding(text)
    matches = []
    for a in reading["groups"]:
        if background is not None and a["background"].lower() != background.lower():
            continue
        if not any(_matches(experimental_arm, label) for label in a["arms"]):
            continue
        for b in reading["groups"]:
            if a["stratum"] != b["stratum"]:
                continue
            if any(_matches(comparator_arm, label) for label in b["arms"]):
                states = {a["blinding"], b["blinding"]}
                matches.append(OPEN_LABEL if OPEN_LABEL in states else
                               BLINDED if states == {BLINDED} else NOT_STATED)
    states = set(matches)
    if len(states) == 1:
        return states.pop()
    if states or reading["state"] == MIXED:
        return MIXED
    return NOT_STATED if reading["groups"] else reading["state"]


def _matches(needle, label):
    return bool(re.search(r"(?<![a-z0-9])" + re.escape(needle.strip()) + r"(?![a-z0-9])", label, re.I))


def eligible_comparisons(text: str, interest, comparators) -> list[dict]:
    """Only active-interest vs comparator pairs within the same allocation.

    A placebo on the stated comparator background is a comparator arm. A
    stratum on the interest is background-only, never an interest contrast.
    """
    groups = read_blinding(text)["groups"]
    out = []
    for a in groups:
        if any(_matches(k, a["background"]) for k in interest):
            continue
        for al in a["arms"]:
            if arm_parse.exposure(arm_parse.parse_arm(al), interest) != "ACTIVE":
                continue
            for b in groups:
                if a["stratum"] != b["stratum"]:
                    continue
                for bl in b["arms"]:
                    if arm_parse.exposure(arm_parse.parse_arm(bl), interest) not in ("ABSENT", "MATCHED_PLACEBO"):
                        continue
                    direct = any(_matches(k, bl) for k in comparators)
                    bg = any(_matches(k, b["background"]) for k in comparators)
                    if not direct and not (bg and re.search(r"\bplacebo\b", bl, re.I)):
                        continue
                    out.append(dict(experimental_arm=al, comparator_arm=bl,
                                    background=b["background"], span=a["span"],
                                    blinding=OPEN_LABEL if OPEN_LABEL in (a["blinding"], b["blinding"]) else
                                    BLINDED if a["blinding"] == b["blinding"] == BLINDED else NOT_STATED))
    return out


def screening_refusal(rec: dict, inc: dict) -> tuple[str, str, str] | None:
    text = " ".join(str(rec.get(k) or "") for k in ("title", "abstract"))
    reading = read_blinding(text)
    groups = reading["groups"]
    interest = inc.get("intervention_any") or []
    if (groups and reading["state"] != MIXED
            and all(any(_matches(k, g["background"]) for k in interest) for g in groups)):
        return ("X-CONTRAST", "CONTRAST_ABSENT: the intervention of interest is background in both arms; "
                "the randomized comparison is another treatment vs its comparator.", groups[0]["span"])
    if not inc.get("design_double_blind") or reading["state"] == NOT_STATED:
        return None
    pairs = eligible_comparisons(text, inc.get("intervention_any") or [],
                                 list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or []))
    if any(p["blinding"] == BLINDED for p in pairs):
        return None
    if pairs and all(p["blinding"] == OPEN_LABEL for p in pairs):
        p = pairs[0]
        label = f"{p['experimental_arm']} vs {p['comparator_arm']}"
        if p["background"]:
            label += f" (background {p['background']})"
        return "X-DESIGN", f"OPEN_LABEL eligible comparison: {label}; double-blind comparison required.", p["span"]
    if reading["state"] == MIXED:
        return ("X-DESIGN", "MIXED blinding: blinding of the eligible comparison "
                f"({' / '.join(inc.get('intervention_any') or [])} vs {' / '.join(inc.get('comparator_any') or [])}) "
                "cannot be established from held text; record-level masking cannot resolve it.",
                reading["statements"][0]["span"])
    if reading["state"] == OPEN_LABEL:
        return ("X-DESIGN", "OPEN_LABEL eligible comparison: "
                f"{' / '.join(interest)} vs {' / '.join(inc.get('comparator_any') or [])}; "
                "double-blind comparison required.", reading["statements"][0]["span"])
    return None


def established_blinded(rec, inc):
    """Positive text evidence, including a blinded pair in a mixed record."""
    text = " ".join(str(rec.get(k) or "") for k in ("title", "abstract"))
    reading = read_blinding(text)
    return reading["state"] == BLINDED or any(
        p["blinding"] == BLINDED for p in eligible_comparisons(
            text, inc.get("intervention_any") or [],
            list(inc.get("comparator_any") or []) + list(inc.get("comparator_any_extra") or [])))
