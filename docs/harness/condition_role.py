"""CONDITION-AS-OUTCOME: a registry condition can be what a trial PREVENTS, not whom it enrols (V1.0.1, statins-older-
adults review).

PREVENTABLE (NCT04262206: atorvastatin vs placebo in adults aged >= 75 without cardiovascular disease, disability or
dementia) registers its conditions as "Cognitive Impairment, Mild", "Dementia" and "Cardiovascular Diseases" -- the
outcomes it aims to prevent. Screening excluded it under X2 ("title/conditions mention 'dementia'"), reading a listed
condition as a baseline diagnosis. Its own eligibility criteria say the opposite: "Exclusion Criteria: ... Dementia
(clinically evident or previously diagnosed)".

A population_none term is a PREVENTION TARGET of a registry record when all hold:
  1. the term occurs, un-negated, in a registered condition;
  2. the record's title does not name it (a title is the trial's own account of whom it studies);
  3. an EXCLUSION criterion of the held registry eligibility criteria (AACT eligibilities.criteria) names that
     registered condition itself (its words before any comma or bracket), un-negated and unqualified -- people with
     it are refused at entry ('Diabetes Mellitus, Type 2' is not refused by 'history of diabetes insipidus', nor
     'Acute Myocardial Infarction' by 'nonobstructive acute myocardial infarction');
  4. no INCLUSION criterion names it, un-negated.
Such a term never excludes the record on population: an X2 that rests only on prevention targets is withdrawn and the
record is screened again without them (every other rule still applies). A record with no held criteria is never
changed here -- silence is not evidence.
"""
from __future__ import annotations

import re
from typing import Optional

from . import lexicon
from . import population_witness as _pw

RULE = "CONDITION_AS_OUTCOME"
_X2_MENTION = re.compile(r"^wrong population: title/conditions mention '([^']+)'\.$")


_PREFIX = r"(?:(?:a |any )?(?:known|history of|prior|previous|previously diagnosed|diagnosed|diagnosis of|clinically evident|established|existing|current)\s+)*"


def _names_condition(item_f: str, core: str) -> bool:
    """The exclusion item is ABOUT the registered condition: at most a history/diagnosis prefix, the condition's own words,
    then nothing but a bracket, a list continuation ('or atrial flutter') or the end. 'Dementia (clinically evident or
    previously diagnosed)' and 'Known atrial fibrillation or atrial flutter' qualify; 'metastatic breast cancer',
    'single ventricle heart disease without Fontan palliation' and 'type 1 diabetes' (for 'Diabetes') do not."""
    body = r"[\s,-]+".join(re.escape(w) for w in re.split(r"[\s,-]+", core) if w)
    return bool(body) and bool(re.match(r"^[*\-\s]*" + _PREFIX + body + r"(?![a-z0-9])\s*(?:$|[(.;:]|or\b|and/or\b)",
                                        item_f.strip()))


def prevention_targets(criteria_raw: Optional[str], conditions, title: str, none_terms) -> list:
    """[{term, condition, exclusion}] for each population_none term the record's own criteria exclude at entry while its
    registered conditions list it."""
    if not criteria_raw or not conditions:
        return []
    inc, exc, _ = _pw.split_criteria(criteria_raw)
    if not exc:
        return []
    title_f = lexicon.fold(title or "")
    out = []
    for term in none_terms or []:
        if _pw._hits(title_f, [term]):
            continue
        if any(not h[3] for item in inc for h in _pw._hits(lexicon.fold(item), [term])):
            continue
        for c in conditions:
            core = re.split(r"[,(]", lexicon.fold(str(c)))[0].strip()
            if not core or not any(not h[3] for h in _pw._hits(core, [term])):
                continue
            ex = next((item for item in exc if _names_condition(lexicon.fold(item), core)
                       and _pw._exclusion_names_population(lexicon.fold(item), [term])), None)
            if ex:
                out.append({"term": term, "condition": c, "exclusion": ex})
                break
    return out


def apply(scr: dict, records: list, registry: dict, config: dict, rescreen) -> list:
    """Withdraw every X2 that rests only on prevention targets and screen the record again without them.
    rescreen(rec, config) -> decision dict. Returns the changed record ids."""
    inc = config.get("include") or {}
    none = list(inc.get("population_none") or [])
    by_id = {str(r.get("id")): r for r in records}
    changed = []
    for i, d in enumerate(scr.get("decisions") or []):
        m = _X2_MENTION.match(str(d.get("reason") or ""))
        rec = by_id.get(str(d.get("id")))
        if d.get("rule_id") != "X2" or not m or not rec or rec.get("id_type") != "nct":
            continue
        reg = registry.get(str(rec["id"])) or {}
        pop = reg.get("population") or {}
        crit = pop.get("criteria") or {}
        conds = (pop.get("conditions") or {}).get("value") or rec.get("conditions") or []
        targets = prevention_targets(crit.get("value"), conds, rec.get("title") or "", none)
        tset = {t["term"] for t in targets}
        if m.group(1) not in tset:
            continue
        cfg = dict(config, include=dict(inc, population_none=[t for t in none if t not in tset]))
        new = dict(rescreen(dict(rec), cfg))
        new["condition_role"] = {"rule": RULE, "withdrawn": {k: d.get(k) for k in ("decision", "rule_id", "reason", "span")},
                                 "prevention_targets": targets,
                                 "criteria_reference": crit.get("span"),
                                 "reading": ("a registered condition the trial's own exclusion criteria refuse at entry "
                                             "is what it aims to prevent, not a baseline diagnosis")}
        t0 = next(t for t in targets if t["term"] == m.group(1))
        new["reason"] = (str(new.get("reason") or "") + f" [{RULE}: the X2 on the registered condition '{t0['condition']}' "
                         f"is withdrawn -- the trial's own exclusion criteria refuse it at entry (\"{t0['exclusion']}\"), "
                         "so it is what the trial prevents, not whom it enrols]")
        scr["decisions"][i] = new
        changed.append(str(rec["id"]))
    return changed


# ---- V1.0.1 round 14: the same fact on the PubMed side of screening (scripts/plants_round14.py) ------------------------
# A topic whose QUESTION enrols people without the condition and asks whether the intervention prevents it (probiotics:
# "In patients receiving antibiotics, do probiotics reduce antibiotic-associated diarrhoea") screens population by that
# condition's words. A trial naming it only as what it prevents, in its abstract, is then "population not on-topic".
# Such records are surfaced as CANDIDATES -- never screened in here: screening them in moves the pool, a protocol
# decision owed a signature. A topic that enrols people WITH the condition ("In adults with acute symptomatic VTE")
# never proposes: there, 'prevention of VTE' is another population.
OUTCOME_RULE = "CONDITION_AS_OUTCOME_IN_QUESTION"
_Q_POPULATION = re.compile(r"^\s*in\s+(.*?),\s*(?:do|does|did|is|are|can|will)\b", re.I | re.S)
_PREVENTION_FRAME = re.compile(r"\b(?:prevent\w*|prophyla\w*|reduc\w* (?:the )?(?:risk|incidence|occurrence) of|"
                               r"incidence of|occurrence of|risk of developing)\b[^.;]{0,60}$", re.I)


def _stem(term: str) -> str:
    return term.rstrip("*").lower()


def question_outcome_conditions(question: str, inc: dict) -> list:
    """The topic's population terms that its QUESTION names only as the outcome: none of the population terms in the
    question's population clause ('In <clause>, do ...'), and these named after it. Empty otherwise."""
    terms = list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])
    m = _Q_POPULATION.match(question or "")
    if not m or not terms:
        return []
    clause, rest = m.group(1).lower(), (question or "")[m.end():].lower()
    if any(_stem(t) in clause for t in terms):
        return []
    return [t for t in terms if _stem(t) in rest]


def outcome_condition_candidates(scr: dict, records: list, config: dict) -> list:
    """Every X2 'population not on-topic' record whose abstract names the question's outcome condition in a prevention
    frame ('to prevent', 'for the prevention of', 'incidence of' ... within 60 characters before it). A candidate only:
    the decision is never changed here."""
    inc = config.get("include") or {}
    if not question_outcome_conditions(config.get("question") or "", inc):
        return []
    terms = list(inc.get("population_any") or []) + list(inc.get("population_any_extra") or [])
    by_id = {str(r.get("id")): r for r in records}
    out = []
    for d in scr.get("decisions") or []:
        if d.get("rule_id") != "X2" or not str(d.get("reason") or "").startswith("population not on-topic"):
            continue
        rec = by_id.get(str(d.get("id"))) or {}
        abstract = rec.get("abstract") or ""
        hit = None
        for t in terms:
            for mm in re.finditer(re.escape(_stem(t)), abstract, re.I):
                if _PREVENTION_FRAME.search(abstract[max(0, mm.start() - 90):mm.start()]):
                    hit = (t, abstract[max(0, mm.start() - 90):mm.end() + 40].strip())
                    break
            if hit:
                break
        if hit:
            out.append({"id": str(d["id"]), "rule": OUTCOME_RULE, "term": hit[0], "span": hit[1],
                        "status": "PROPOSED -- screening it in moves the pool: a protocol decision owed a signature"})
    return out
