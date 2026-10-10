"""Typed screening vocabulary (12-01 class fix + review 27-B). Pure tables and pure functions: the screen's decisions
stay a function of the committed cache + the topic config + these tables, so a fresh clone replays them.

  DEV_CODES          a drug's development codes ARE the drug (ARTS-DN Japan registers finerenone only as 'BAY94-8862').
                     Applied only to an INN the protocol's own intervention terms already name.
  POP_SYNONYMS       registry-label variants of a population concept ('Diabetes Mellitus, Type 2' = 'type 2 diabetes').
                     Applied only when the protocol's own population terms name the concept; the population_none
                     exclusions are untouched and still decide first.
  placebo_masks_intervention()
                     ROLE-AWARE comparator (r27-B): when the protocol's comparator is placebo, a record satisfies it when a
                     placebo arm MASKS THE INTERVENTION on an identical background ('placebo for X', 'X placebo', or
                     'B plus placebo' alongside 'B plus X' / 'combination of X and B': Legro PPCOS I). A placebo that
                     masks ANOTHER agent (the intervention is in both arms), or an unequal background, never satisfies it.
"""
from __future__ import annotations

import re

DEV_CODES = {
    "finerenone": ["BAY94-8862", "BAY 94-8862", "BAY-94-8862", "BAY948862"],
    "sacubitril": ["LCZ696", "LCZ 696", "LCZ-696"],
    "dapagliflozin": ["BMS-512148", "BMS512148"], "empagliflozin": ["BI 10773", "BI10773", "BI-10773"],
    "canagliflozin": ["JNJ-28431754", "TA-7284"], "ertugliflozin": ["MK-8835", "PF-04971729"],
    "sotagliflozin": ["LX4211", "SAR439954"], "edoxaban": ["DU-176b", "DU176b"],
    "dabigatran": ["BIBR 1048", "BIBR1048"], "rivaroxaban": ["BAY 59-7939", "BAY59-7939"],
    "apixaban": ["BMS-562247", "BMS562247"], "semaglutide": ["NN9535", "NN9536", "NN9924"],
    "liraglutide": ["NN2211", "NN8022"], "dulaglutide": ["LY2189265"], "albiglutide": ["GSK716155"],
    "exenatide": ["AC2993"], "lixisenatide": ["AVE0010"], "efpeglenatide": ["HM11260C"],
    "evolocumab": ["AMG 145", "AMG145"], "alirocumab": ["SAR236553", "REGN727"],
    "omarigliptin": ["MK-3102"], "sitagliptin": ["MK-0431"], "linagliptin": ["BI 1356"], "saxagliptin": ["BMS-477118"],
    "alogliptin": ["SYR-322", "SYR322"], "denosumab": ["AMG 162", "AMG162"], "esketamine": ["JNJ-54135419"],
    "ticagrelor": ["AZD6140"], "ferric carboxymaltose": ["VIT-45"],
}

POP_SYNONYMS = {
    "type 2 diabetes": ["diabetes mellitus, type 2", "diabetes mellitus type 2", "type ii diabetes", "type-2 diabetes",
                        "type 2 diabetic", "t2dm", "niddm", "non-insulin-dependent diabetes"],
    "chronic kidney disease": ["renal insufficiency, chronic", "chronic renal insufficiency", "kidney failure, chronic",
                               "diabetic kidney disease"],
    "atrial fibrillation": ["non-valvular atrial fibrillation", "nonvalvular atrial fibrillation", "nvaf"],
    "venous thromboembolism": ["deep vein thrombosis", "deep venous thrombosis", "pulmonary embolism"],
    "osteoporosis": ["osteoporosis, postmenopausal", "postmenopausal osteoporosis"],
    "insomnia": ["sleep initiation and maintenance disorders", "insomnia disorder"],
    "polycystic ovary syndrome": ["polycystic ovarian syndrome", "pcos"],
    "treatment-resistant depression": ["depressive disorder, treatment-resistant", "treatment resistant depression"],
    "covid-19": ["sars-cov-2", "coronavirus disease 2019", "covid 19"],
    "postpartum haemorrhage": ["postpartum hemorrhage", "post-partum haemorrhage", "post-partum hemorrhage"],
}

_CACHE: dict = {}


def expand(inc: dict) -> dict:
    """A copy of the include object with the typed codes/synonyms added (never removed); the original is untouched."""
    key = id(inc)
    hit = _CACHE.get(key)
    if hit is not None and hit[0] is inc:
        return hit[1]
    out = dict(inc or {})
    ia = [str(t) for t in out.get("intervention_any") or []]
    low = " ".join(t.lower() for t in ia)
    add = [c for inn, codes in DEV_CODES.items() if inn in low for c in codes if c.lower() not in low]
    if add:
        out["intervention_any"] = ia + add
    pa = [str(t) for t in (out.get("population_any") or []) + (out.get("population_any_extra") or [])]
    plow = " ".join(t.lower() for t in pa)
    padd = [s for concept, syns in POP_SYNONYMS.items() if concept in plow for s in syns if s not in plow]
    if padd and out.get("population_any"):
        out["population_any_extra"] = list(out.get("population_any_extra") or []) + padd
    _CACHE[key] = (inc, out)
    return out


_JOIN = r"\s*(?:\+|plus|and|with|/)\s*"


def placebo_masks_intervention(rec: dict, inc: dict, text: str) -> dict | None:
    """{'term', 'span'} when the record shows a placebo arm that MASKS the intervention on an identical background,
    else None. Read only from the record's own interventions / arms / title / abstract."""
    if not any("placebo" in str(t).lower() for t in (inc.get("comparator_any") or []) + (inc.get("comparator_any_extra") or [])):
        return None
    ints = [str(t).lower() for t in inc.get("intervention_any") or [] if len(str(t)) >= 4]
    if not ints:
        return None
    parts = [str(x) for x in (rec.get("interventions") or []) + (rec.get("arms") or []) if x]
    hay = " ; ".join(parts + [str(rec.get("title") or ""), str(text or "")])
    low = hay.lower()
    iq = "|".join(re.escape(i) for i in ints)
    # (1) an explicit placebo OF the intervention
    m = re.search(rf"(?:matching\s+)?placebo\s+(?:for|to|of)\s+(?:{iq})|(?:{iq})[\s-]*(?:matching\s+)?placebo\b", low)
    if m:
        return {"term": "placebo (masks the intervention)", "span": hay[m.start():m.end()]}
    # (2) 'B plus placebo' paired with the SAME background combined with the intervention ('combination of X and B')
    for pm in re.finditer(rf"\b([a-z][a-z-]*(?:\s+[a-z][a-z-]*)?){_JOIN}placebo\b", low):
        # the background agent is the LAST one or two words before '+ placebo' ('clomiphene citrate plus placebo');
        # a lazy wider capture took 'syndrome to receive clomiphene citrate' and tested 'syndrome'
        words = [w for w in pm.group(1).split() if len(w) >= 4 and w not in _STOP]
        if not words or re.search(iq, pm.group(1)):    # a placebo masking ANOTHER agent: the intervention is in this
            continue                                    # arm, so it is not masked -- never a contrast
        for bg_core in words:
            b = re.escape(bg_core)
            # the COMBINATION arm must be its own phrase: intervention and background JOINED directly ('metformin and
            # clomiphene', 'clomiphene plus metformin', 'combination of X and B'). A loose proximity test matched across
            # the placebo arm itself ('clomiphene citrate plus placebo or metformin alone': an unequal background)
            combo = (rf"\b(?:{iq})(?:\s+[a-z-]+)?{_JOIN}(?:[a-z-]+\s+)?{b}\b|\b{b}(?:\s+[a-z-]+)?{_JOIN}(?:[a-z-]+\s+)?(?:{iq})\b"
                     rf"|combination of (?:{iq}) and {b}|combination of {b} and (?:{iq})")
            if re.search(combo, low):
                return {"term": f"placebo (masks the intervention; shared background {bg_core})",
                        "span": hay[pm.start():pm.end()]}
    return None


_STOP = {"receive", "received", "either", "with", "group", "groups", "patients", "subjects", "women", "arms", "alone",
         "dose", "doses", "daily", "oral", "tablet", "tablets", "therapy", "treatment", "matching"}
