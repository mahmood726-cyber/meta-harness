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


# formulation / salt / connective words that do not change WHICH agent an arm gives: "clomiphene citrate" and "a combination of ...
# clomiphene" hold the same agent constant (Legro 2007)
_CANON_DROP = re.compile(r"(?i)\b(?:a|an|the|combination|of|extended[- ]release|immediate[- ]release|sustained[- ]release|"
                         r"xr|er|sr|citrate|hydrochloride|hcl)\b")


def _canon(agent: str) -> str:
    return " ".join(_CANON_DROP.sub(" ", agent or "").split()).lower()


def _other_actives(arm: dict[str, Any], kws) -> tuple[str, ...]:
    out = []
    for c in arm["components"]:
        if c["kind"] == "ACTIVE" and not _hit(c["agent"], kws):
            out.append(_canon(c["agent"]))
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


# --------------------------------------------------------------------------- arm-based comparator recognition (metformin review)
# Legro 2007 (PMID 17287476) was excluded X3 "no eligible comparator" because the screen matched phrases ("placebo group",
# "placebo-controlled") and the abstract names its arms instead: "clomiphene citrate plus placebo, extended-release metformin plus
# placebo, or a combination of metformin and clomiphene". "X plus placebo" establishes a placebo arm; the eligible contrast is the
# CLEAN one (metformin + clomiphene vs placebo + clomiphene, clomiphene held constant) -- metformin vs clomiphene is not.
_ASSIGNED = re.compile(r"(?i)\b(?:randomly\s+assigned|randomi[sz]ed|allocated)\b[^.;]{0,120}?\bto\s+(?:receive\s+|take\s+|either\s+)*"
                       r"(?P<arms>[^.;]{8,320}?)(?=\s+for\s+(?:up\s+to\s+)?\d|\s+(?:daily|nightly|twice|once)\b|[.;]|$)")
_ARM_SPLIT = re.compile(r"\s*,\s*(?:or\s+)?|\s+or\s+|\s+versus\s+|\s+vs\.?\s+", re.I)


def abstract_arms(text: str | None) -> list[str]:
    """The randomised arm labels a held abstract lists ("randomly assigned ... to receive A, B, or C"); [] when it lists none."""
    m = _ASSIGNED.search(text or "")
    if not m:
        return []
    arms = [a.strip(" ,") for a in _ARM_SPLIT.split(m.group("arms")) if a.strip(" ,")]
    return arms if len(arms) >= 2 else []


def arm_based_comparator(labels, keywords, labels_are_arms: bool = True) -> dict[str, Any] | None:
    """A placebo comparator for the agent, read from the arms -- or None.

    ARM labels (a held abstract's "randomly assigned ... to receive A, B, or C"): a CLEAN ordered contrast whose comparator arm
    carries a placebo; a confounded contrast (metformin + placebo vs clomiphene + placebo) never counts.
    A registry INTERVENTION list is not a list of arms (NCT02792400 lists LY2403021, its placebo, a liquid meal, linagliptin, its
    placebo, empagliflozin, its placebo): pairing its entries as arms invents contrasts. From such a list only a placebo MATCHED to
    the agent, or a two-entry list of the agent and a plain placebo, is a comparator. Either way a matched placebo is preferred."""
    kws = _kws(keywords)
    parsed = {a: parse_arm(a) for a in labels or []}

    def _matched_to_agent(arm):
        return any(x["kind"] == "MATCHED_PLACEBO" and _hit(x.get("matched_to"), kws) for x in arm["components"])

    if not labels_are_arms:
        for lab, arm in parsed.items():
            if _matched_to_agent(arm) and exposure(arm, kws) == "MATCHED_PLACEBO":
                return {"comparator_arm": lab, "experimental_arm": None, "held_constant": [],
                        "basis": "registry intervention list: a placebo matched to the agent"}
        if len(parsed) == 2:
            (la, a), (lb, b) = parsed.items()
            for act, (lp, pl) in ((a, (lb, b)), (b, (la, a))):
                if exposure(act, kws) == "ACTIVE" and all(x["kind"] == "PLACEBO" for x in pl["components"]):
                    return {"comparator_arm": lp, "experimental_arm": act["label"], "held_constant": [],
                            "basis": "registry intervention list of two: the agent and a plain placebo"}
        return None
    clean = [c for c in ordered_contrasts(labels, keywords) if c["state"] == "CLEAN"
             and any(x["kind"] in ("PLACEBO", "MATCHED_PLACEBO") for x in parsed[c["comparator_arm"]]["components"])]
    clean.sort(key=lambda c: 0 if _matched_to_agent(parsed[c["comparator_arm"]]) else 1)
    if not clean:
        return None
    c = clean[0]
    return {"experimental_arm": c["experimental_arm"], "comparator_arm": c["comparator_arm"],
            "held_constant": c["held_constant"], "basis": "arm parsing: a CLEAN contrast against a placebo arm"}
