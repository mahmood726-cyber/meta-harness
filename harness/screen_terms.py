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

# A synonym / code stands ALONE only for a term that IS the concept, up to words naming the same concept ('type 2 diabetes
# mellitus', 'postmenopausal osteoporosis', 'primary insomnia', 'chronic kidney diseases', 'finerenone tablets'). Any other
# word is a REQUIREMENT the alternative must keep, so the synonym replaces the concept in place: 'type 2 diabetes with
# chronic kidney disease' -> 't2dm with chronic kidney disease' (codex pr65-cap-r1 #3), 'type 2 diabetes requiring
# insulin' -> 't2dm requiring insulin' (r2 #1), 'finerenone plus spironolactone' -> 'BAY94-8862 plus spironolactone' (r2 #2).
_SAME_CONCEPT = {"mellitus", "primary", "postmenopausal", "nonvalvular", "non-valvular", "s", "tablet", "tablets",
                 "capsule", "capsules", "oral", "injection"}


def _stands_alone(term, concept):
    rest = re.sub(re.escape(concept), " ", term, count=1, flags=re.I)
    return all(w in _SAME_CONCEPT or w in _SALTS for w in re.findall(r"[a-z0-9-]+", rest.lower()))


def _alternatives(terms, concept, subs):
    """The alternatives to add for one concept over the include terms that name it."""
    named = [t for t in terms if concept in t.lower()]
    if not named:
        return []
    if any(_stands_alone(t, concept) for t in named):
        return list(subs)
    return [re.sub(re.escape(concept), s, t, flags=re.I) for t in named for s in subs]


def expand(inc: dict) -> dict:
    """A copy of the include object with the typed codes/synonyms added (never removed); the original is untouched.
    Recomputed from the CONTENT every call: a cache keyed by object identity returned stale terms after the dict was
    mutated (codex pr65-cap-r1 #4)."""
    out = dict(inc or {})
    ia = [str(t) for t in out.get("intervention_any") or []]
    low = {t.lower() for t in ia}
    add = []
    for inn, codes in DEV_CODES.items():
        add += [c for c in _alternatives(ia, inn, codes) if c.lower() not in low and c not in add]
    if add:
        out["intervention_any"] = ia + add
    pa = [str(t) for t in (out.get("population_any") or []) + (out.get("population_any_extra") or [])]
    plow = " ".join(t.lower() for t in pa)
    padd = []
    for concept, syns in POP_SYNONYMS.items():
        padd += [s for s in _alternatives(pa, concept, syns) if s.lower() not in plow and s not in padd]
    if padd and out.get("population_any"):
        out["population_any_extra"] = list(out.get("population_any_extra") or []) + padd
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
    explicit = rf"(?:matching\s+)?placebo\s+(?:for|to|of)\s+(?:{iq})|(?:{iq})[\s-]*(?:matching\s+)?placebo\b"
    m = re.search(explicit, low)
    if m:
        # ... on the SAME background: when the record's own arms show it, the placebo arm's background agents must
        # equal an intervention arm's ('clomiphene plus metformin' v 'letrozole plus placebo for metformin' is a
        # different background: codex pr65-cap-r1 #1). Arms not listed -> as before (the explicit wording stands).
        arms = [p.lower() for p in parts]
        p_arms = [a for a in arms if re.search(explicit, a)]
        # an intervention arm is any arm carrying the intervention UNMASKED -- a double-dummy arm ('clomiphene plus
        # metformin plus placebo for letrozole') is one (codex pr65-cap-r2 #4: excluding every arm with 'placebo' emptied
        # the list and skipped the check)
        i_arms = [a for a in arms if re.search(iq, a) and not re.search(explicit, a)]
        if p_arms and i_arms and not any(_background(a, iq) == _background(p, iq) for p in p_arms for a in i_arms):
            return None
        return {"term": "placebo (masks the intervention)", "span": hay[m.start():m.end()]}
    # (2) 'B plus placebo' paired with the SAME background combined with the intervention ('combination of X and B')
    for pm in re.finditer(rf"\b([a-z][a-z-]*(?:\s+[a-z][a-z-]*)?){_JOIN}placebo\b", low):
        # the background agent is the LAST one or two words before '+ placebo' ('clomiphene citrate plus placebo');
        # a lazy wider capture took 'syndrome to receive clomiphene citrate' and tested 'syndrome'
        # a salt or form ('citrate', 'sodium') is not an agent: 'clomiphene citrate' and 'tamoxifen citrate' share a word,
        # never a background (codex pr65-cap-r1 #2)
        words = [w for w in pm.group(1).split() if len(w) >= 4 and w not in _STOP and w not in _SALTS]
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
                # ... and when the record lists its arms, the WHOLE background must be equal, not one shared agent
                # ('clomiphene plus placebo' v 'clomiphene plus metformin plus letrozole': codex pr65-cap-r2 #3)
                arms = [p.lower() for p in parts]
                p_arms = [a for a in arms if re.search(rf"\b{b}\b", a) and re.search(r"\bplacebo\b", a)
                          and not re.search(iq, a)]
                i_arms = [a for a in arms if re.search(iq, a) and not re.search(explicit, a)]
                if p_arms and i_arms and not any(_background(a, iq) == _background(p, iq) for p in p_arms for a in i_arms):
                    continue
                return {"term": f"placebo (masks the intervention; shared background {bg_core})",
                        "span": hay[pm.start():pm.end()]}
    return None


_STOP = {"receive", "received", "either", "with", "group", "groups", "patients", "subjects", "women", "arms", "alone",
         "dose", "doses", "daily", "oral", "tablet", "tablets", "therapy", "treatment", "matching"}
_SALTS = {"citrate", "sodium", "potassium", "calcium", "magnesium", "hydrochloride", "hydrobromide", "sulfate", "sulphate",
          "phosphate", "acetate", "maleate", "fumarate", "succinate", "tartrate", "mesylate", "besylate", "tosylate",
          "bromide", "chloride", "propionate", "dipropionate", "furoate", "valerate", "extended-release", "immediate-release",
          "release", "extended", "sustained", "modified", "hcl"}


def _background(arm, iq):
    """The background AGENTS of one arm: its joined components ('A plus B', 'A + B', 'A with B') other than the
    intervention and the placebo, each keyed by its first drug word -- salts / forms / dose words are not agents."""
    out = set()
    for comp in re.split(_JOIN, arm):
        if re.search(iq, comp) or "placebo" in comp:
            continue
        w = next((w for w in re.findall(r"[a-z][a-z-]+", comp) if len(w) >= 4 and w not in _STOP and w not in _SALTS),
                 None)
        if w:
            out.add(w)
    return out
