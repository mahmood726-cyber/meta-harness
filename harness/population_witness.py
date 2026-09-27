"""Entry-population decision for a trial family, read from SOURCE EVIDENCE (V1.0.1).

The structural screen used to decide the population from the registry's `conditions` list alone, and it tested the
positive match BEFORE the exclusions. `conditions` is the registrant's topic label, not an entry criterion: ELIXA
lists "Acute Coronary Syndrome", HARMONY "Diabetes Mellitus", SELECT "Overweight; Obesity". The entry population is
stated in the held registry eligibility CRITERIA (AACT eligibilities.criteria) and in the primary report's own
account of whom it enrolled. This module reads both, as separate witnesses, and combines them:

  EXCLUDED        the protocol's population is excluded at entry (an exclusion criterion names it with no
                  qualifier, an inclusion criterion or the enrolment sentence negates it, or it names a population
                  the protocol excludes)  -> the family is INELIGIBLE on population
  ESTABLISHED     an inclusion criterion or the primary report's enrolment sentence names it, un-negated
  MIXED           one entry statement admits both the protocol's population and one it excludes
  CONFLICT        one witness establishes it and another excludes it
  NOT_ESTABLISHED no witness states it

Exclusions are evaluated BEFORE the positive match, and establishing the population is one axis of eligibility,
never eligibility itself. Terms come only from the topic config (`include.population_any` / `population_none`,
plus any disclosed retrospective `population_vocabulary_clarifications`); the only equivalence added at match time
is hyphen/space/comma. The registry `conditions` list is a WEAK witness: it may establish the population only when
the criteria and the primary reports are silent, and it never outvotes an entry statement.
"""
from __future__ import annotations

import re
from typing import Optional

from . import lexicon

STATES = ("EXCLUDED", "CONFLICT", "MIXED", "ESTABLISHED", "NOT_ESTABLISHED")
ABSENCE_CODE = {"NOT_ESTABLISHED": "ENTRY_POPULATION_NOT_ESTABLISHED", "MIXED": "ENTRY_POPULATION_MIXED",
                "CONFLICT": "POPULATION_SOURCES_CONFLICT"}

_NEG = re.compile(r"(?<![a-z])(?:no|not|without|non|never|free of|absence of|excluding)(?![a-z])[^.;:~]{0,40}$")
_WITH_OR_WITHOUT = re.compile(r"with or without[^.;:~]{0,40}$")
# an exclusion that names the population only as a SUBSET (a severity, treatment or complication qualifier) does not
# exclude the population
_QUALIFIER = re.compile(r"\b(?:uncontrolled|poorly controlled|inadequately controlled|decompensated|insulin|treated with|"
                        r"treatment with|requiring|on (?:insulin|treatment)|hba1c|a1c|glucose|complications?|nephropathy|"
                        r"retinopathy|neuropathy|gastroparesis|ketoacidosis|hypoglyc|severe|advanced|brittle|unstable|"
                        r"newly diagnosed|recently diagnosed|duration|"
                        # V1.0.1 (population validation, IV iron): a RECENT or ACUTE event within a time window is a
                        # qualified subset, not the population -- 'acute heart failure ... in the preceding 15 days'
                        # does not exclude heart-failure patients from a heart-failure trial
                        r"within|preceding|previous|prior|past|last|recent|recently|acute|acutely|"
                        r"hospitali[sz]ed for|hospitali[sz]ation for|admitted for|admission for)\b")
# diabetes phrases that are NOT the type 2 population
_OTHER_DIABETES = re.compile(r"\b(?:type (?:1|i)\b(?! or)|type-1|gestational|insipidus|pre-?diabet\w*|latent autoimmune|"
                             r"lada|mody|secondary diabet\w*|(?:special|other|rare|specific) (?:types?|forms?) of diabet\w*|monogenic|steroid[- ]induced|diabetic (?:ketoacidosis|retinopathy|"
                             r"nephropathy|neuropathy|foot|macular|kidney))[^.;:~]{0,20}")
_ENROL = re.compile(r"\b(?:randomly assigned|randomi[sz]ed|enrolled|recruited|were assigned|assigned|were included|"
                    r"included|eligible (?:patients|participants))\b", re.I)
_SUBJECT = re.compile(r"\b(?:patients|participants|adults|people|persons|subjects|men and women|individuals)\b", re.I)
_SECTION = re.compile(r"^\s*([A-Z][A-Z ,&/]{2,40}):\s*")
_NOT_ENTRY_SECTIONS = {"BACKGROUND", "CONCLUSION", "CONCLUSIONS", "INTERPRETATION", "CONTEXT", "IMPORTANCE",
                       "OBJECTIVE", "OBJECTIVES", "AIM", "AIMS", "PURPOSE", "INTRODUCTION", "RESULTS", "FINDINGS",
                       "FUNDING", "TRIAL REGISTRATION", "CLINICAL TRIAL REGISTRATION", "REGISTRATION"}


def _pattern(term: str) -> re.Pattern:
    f = lexicon.fold(str(term)).strip()
    prefix = f.endswith("*")
    words = re.split(r"[\s,-]+", f.rstrip("*"))
    body = r"[\s,-]+".join(re.escape(w) for w in words if w)
    return re.compile(r"(?<![a-z0-9])" + body + (r"" if prefix else r"(?![a-z0-9])"))


def _hits(text: str, terms, negation_exempt=False):
    """[(term, start, end, negated, mixed)] for every whole-token occurrence of a term in folded text."""
    out = []
    for t in terms or []:
        exempt = negation_exempt or bool(re.match(r"(?:no |without |.*\bwithout\b)", lexicon.fold(str(t))))
        for m in _pattern(t).finditer(text):
            before = text[max(0, m.start() - 60):m.start()]
            out.append((t, m.start(), m.end(), (not exempt) and bool(_NEG.search(before)),
                        bool(_WITH_OR_WITHOUT.search(before))))
    return out


_NEG_DIABETES = re.compile(
    r"(?<![a-z])(?:no|without|never had|free of|absence of|(?:does|do|did) not have|not have|except(?: for)?|excluding|but not)\s+"
    r"(?:(?:a|any|known|prior|previous|documented|history of|personal history of|diagnosis of|diagnosed|established|"
    r"evidence of|clinical|self-reported)\s+){0,3}(?:type (?:1 or |2 or )?(?:1|2|i|ii) )?diabetes\b"
    r"(?! (?:therapy|treatment|medication|drug|agent)s?\b)|"
    r"\bnon[- ]?diabetic (?:patients|participants|subjects|adults|people|persons|individuals|volunteers)\b")


def _negated_diabetes(text: str) -> Optional[str]:
    """The absence of diabetes AS A CONDITION ('no history of diabetes', 'without type 2 diabetes', 'non-diabetic
    patients', '(except type 1 or 2 diabetes)') -> the phrase. 'Other than diabetes, subjects must be in good
    health' AFFIRMS diabetes, so 'other than' is not a negation here. Adjectives and therapies ('anti-diabetic', 'not on oral anti-diabetic medication',
    'without metformin as only diabetes therapy', 'no treatment for diabetic retinopathy') are not it."""
    m = _NEG_DIABETES.search(text)
    if m and not re.search(r"with or without", text[max(0, m.start() - 10):m.end()]):
        return m.group(0)
    return None


def split_criteria(raw: str):
    """(inclusion items, exclusion items, unsectioned items) from AACT eligibilities.criteria, whose line separator
    is '~'. Items keep their verbatim text (for the span)."""
    inc, exc, uns, cur = [], [], [], None
    text = str(raw or "").strip().strip('"')
    # a section header written inline ('... - HbA1c 7.0% Exclusion Criteria: - Type 1 diabetes') starts a new line
    text = re.sub(r"(?i)(?<=\S)\s*((?:key |main |general )?(?:inclusion|exclusion) criteri\w*\s*:)", r"~\1~", text)
    # ' - ' before a capital letter is a bullet inside one registry line (never a numeric range: '6.0 - 7.9')
    text = re.sub(r"\s+-\s+(?=[A-Z])", "~", text)
    for line in re.split(r"~|\n", text):
        s = line.strip().strip('"').strip()
        if not s:
            continue
        head = re.match(r"^[*\-•\d.)\s]*(?:key\s+|main\s+|general\s+)?(inclusion|exclusion)\s+criteri\w*\s*:?\s*(.*)$", s, re.I)
        if head:
            cur = head.group(1).lower()
            s = head.group(2).strip()
            # criteria for a LATER phase (extension, re-treatment, follow-on, open-label continuation) are not entry
            # criteria of the randomised phase: their items are not read (NCT00896532 lists 'New malignancy' under
            # its follow-on phase)
            if re.search(r"\b(?:extension|re-?treatment|follow-?on|open[- ]label|continuation|maintenance) (?:phase|period|study)\b"
                         r"|\bphase \(month", s, re.I):
                cur = "later_phase"
                continue
            if not s:
                continue
        item = re.sub(r"^[*\-•]\s*|^\d{1,2}[.)]\s+", "", s).strip()
        if item:
            if cur == "later_phase":
                continue
            (inc if cur == "inclusion" else exc if cur == "exclusion" else uns).append(item)
    return inc, exc, uns


# 'type 1 or type 2 diabetes', 'type 1 and 2 diabetes': one entry statement admitting both types
_MIXED_TYPES = re.compile(r"\btype[\s-]*(?:1|i)\s+(?:or|and|and/or|&)\s+(?:type[\s-]*)?(?:2|ii)\b[^.;:~]{0,12}diabet|"
                          r"\btype[\s-]*(?:2|ii)\s+(?:or|and|and/or|&)\s+(?:type[\s-]*)?(?:1|i)\b[^.;:~]{0,12}diabet")
_EXCEPTION = re.compile(r"(?:other than|except(?: for)?|apart from|besides|aside from|excluding)\s+(?:\w+\s+){0,2}$")


def _exclusion_names_population(item_f: str, target_terms, diabetes: bool = False) -> Optional[str]:
    """An exclusion criterion that excludes the whole target population (not a qualified subset, and not an
    exception: 'any clinically significant disease other than type 2 diabetes' excludes everything BUT it)."""
    if _QUALIFIER.search(item_f):
        return None
    for t, s, e, neg, mixed in _hits(item_f, target_terms):
        if not neg and not mixed and not _EXCEPTION.search(item_f[max(0, s - 40):s]):
            return item_f[s:e]
    # generic diabetes ('Diabetes mellitus', 'History of diabetes') -- only for a declared diabetes population, and
    # only when the item names no specific other type: 'Type 1 diabetes, special types of diabetes, or gestational
    # diabetes' is a list of NON-target types
    if not diabetes or _OTHER_DIABETES.search(item_f):
        return None
    m = re.search(r"\bdiabet(?:es|ic)\b(?: mellitus)?", item_f)
    if m and len(item_f.split()) <= 14 and not _negated_diabetes(item_f) \
            and not _EXCEPTION.search(item_f[max(0, m.start() - 40):m.start()]):
        return m.group(0)
    return None


def criteria_witness(raw: str, span_ref: dict, target_terms, none_terms, diabetes: bool = False) -> dict:
    inc, exc, uns = split_criteria(raw)
    base = {"source": "registry eligibility criteria", "reference": span_ref}
    if not inc and not exc:
        return dict(base, verdict="NOT_ESTABLISHED", why="criteria text has no inclusion/exclusion sections",
                    unsectioned_items=len(uns))
    for item in inc:
        f = lexicon.fold(item)
        pos = [h for h in _hits(f, target_terms) if not h[3]]
        bad = [h for h in _hits(f, none_terms) if not h[3]]
        mixed = [h for h in pos if h[4]]
        if diabetes and _MIXED_TYPES.search(f) and not _negated_diabetes(f):
            mixed = mixed or [("type 1 or type 2", 0, 0, False, True)]
        if (pos and bad) or mixed:
            return dict(base, verdict="MIXED", section="inclusion", quote=item,
                        why="one inclusion criterion admits the protocol population together with another population")
        if bad:
            return dict(base, verdict="EXCLUDED", section="inclusion", quote=item,
                        why=f"inclusion criterion names a population the protocol excludes ({f[bad[0][1]:bad[0][2]]})")
        neg = _negated_diabetes(f) if diabetes else None
        if neg and not pos:
            return dict(base, verdict="EXCLUDED", section="inclusion", quote=item,
                        why=f"inclusion criterion requires the absence of diabetes ({neg})")
    for item in inc:
        f = lexicon.fold(item)
        pos = [h for h in _hits(f, target_terms) if not h[3] and not h[4]]
        if pos:
            return dict(base, verdict="ESTABLISHED", section="inclusion", quote=item,
                        why=f"inclusion criterion requires {f[pos[0][1]:pos[0][2]]}")
    for item in exc:
        named = _exclusion_names_population(lexicon.fold(item), target_terms, diabetes)
        if named:
            return dict(base, verdict="EXCLUDED", section="exclusion", quote=item,
                        why=f"exclusion criterion excludes {named}, and no inclusion criterion requires the protocol population")
    return dict(base, verdict="NOT_ESTABLISHED", why="no inclusion criterion names the protocol population")


def _entry_sentences(abstract: str):
    section = None
    for sent in re.split(r"(?<=[.;])\s+(?=[A-Z(])", abstract or ""):
        m = _SECTION.match(sent)
        if m:
            section = m.group(1).strip().upper()
            sent = sent[m.end():]
        if section in _NOT_ENTRY_SECTIONS:
            continue
        if _ENROL.search(sent) and _SUBJECT.search(sent):
            yield section, sent


def report_witness(rec: dict, target_terms, none_terms, diabetes: bool = False) -> Optional[dict]:
    """The primary report's own enrolment sentence (outside BACKGROUND/RESULTS/CONCLUSIONS)."""
    for section, sent in _entry_sentences(str(rec.get("abstract") or "")):
        f = lexicon.fold(sent)
        pos = [h for h in _hits(f, target_terms) if not h[3]]
        bad = [h for h in _hits(f, none_terms) if not h[3]]
        neg = _negated_diabetes(f) if diabetes else None
        base = {"source": "primary report abstract (enrolment sentence)", "report_id": str(rec.get("id")),
                "section": section, "quote": sent}
        if (pos and (bad or neg)) or any(h[4] for h in pos) or (diabetes and _MIXED_TYPES.search(f) and not neg):
            return dict(base, verdict="MIXED", why="the enrolment sentence names the protocol population and another")
        if bad or neg:
            return dict(base, verdict="EXCLUDED",
                        why=f"the enrolment sentence excludes the protocol population ({neg or f[bad[0][1]:bad[0][2]]})")
        if pos:
            return dict(base, verdict="ESTABLISHED", why=f"the enrolment sentence names {f[pos[0][1]:pos[0][2]]}")
    return None


def title_witness(rec: dict, target_terms, none_terms, diabetes: bool = False) -> Optional[dict]:
    """The primary report's OWN title is the trial's statement of its population ('Denosumab for prevention of fractures
    in postmenopausal women with osteoporosis'). FREEDOM's registry criteria say only 'Women ... 60 to 90' and 'T-Score
    less than -2.5'; its title names the population."""
    f = lexicon.fold(str(rec.get("title") or ""))
    if not f:
        return None
    pos = [h for h in _hits(f, target_terms) if not h[3]]
    bad = [h for h in _hits(f, none_terms) if not h[3]]
    neg = _negated_diabetes(f) if diabetes else None
    base = {"source": "primary report title", "report_id": str(rec.get("id")), "quote": rec.get("title")}
    if pos and (bad or neg):
        return dict(base, verdict="MIXED", why="the title names the protocol population and another")
    if bad or neg:
        return dict(base, verdict="EXCLUDED", why=f"the title names a population the protocol excludes ({neg or f[bad[0][1]:bad[0][2]]})")
    if pos:
        return dict(base, verdict="ESTABLISHED", why=f"the title names {f[pos[0][1]:pos[0][2]]}")
    return None


def decide(family: dict, config: dict, report_role=None) -> dict:
    """{'state', 'witnesses', 'basis'} for one family. report_role(rec) -> (role, evidence)."""
    inc = config.get("include") or {}
    target = list(inc.get("population_any") or [])
    none = list(inc.get("population_none") or [])
    topic = config.get("population_witness") or {}
    if topic.get("none_population_terms") is not None:
        # validated per topic: only the exclusion terms that describe a POPULATION ('prostate cancer', 'pediatric');
        # a topic's population_none may also list drugs or designs ('romosozumab', 'vertebroplasty') that must never
        # read as a population exclusion (registry/population_witness_topics.json)
        none = list(topic["none_population_terms"])
    clar = [c for c in config.get("population_vocabulary_clarifications") or [] if c.get("terms")]
    if not target:
        return {"state": "NOT_APPLICABLE", "witnesses": [], "basis": "the topic declares no population_any"}
    declared = str(((config.get("family_requirements") or {}).get("population")) or "")
    # the diabetes-specific rules (a negated diabetes condition; a generic 'diabetes' exclusion) apply only where the
    # protocol DECLARES a diabetes population; any other population is read by its config terms alone
    diabetes = "diabet" in declared.lower()
    pop = family.get("population") or {}
    crit = pop.get("criteria") or {}
    witnesses = []
    if crit.get("value"):
        witnesses.append(criteria_witness(crit["value"], crit.get("span"), target, none, diabetes))
    roles = {str(r.get("report_id")): r.get("role") for r in family.get("reports") or []}
    for rec in family.get("source_records") or []:
        role = roles.get(str(rec.get("id")))
        if role is None and report_role:
            role = report_role(rec)[0]
        if role in ("PRIMARY", "PRIMARY_WITH_POOLED_ANALYSIS"):
            w = report_witness(rec, target, none, diabetes) if rec.get("abstract") else None
            if w:
                witnesses.append(w)
            tw = title_witness(rec, target, none, diabetes)
            if tw:
                witnesses.append(tw)
    conds = (pop.get("conditions") or {}).get("value") or []
    strong = {w["verdict"] for w in witnesses}
    if conds:
        text = lexicon.fold(" | ".join(str(c) for c in conds))
        bad = [h for h in _hits(text, none) if not h[3]]
        from .trial_family import population_matches
        if bad and population_matches(target, conds):
            witnesses.append({"source": "registry conditions", "verdict": "MIXED", "strength": "WEAK", "quote": conds,
                              "why": "the registered conditions name the protocol population and one it excludes"})
        elif bad:
            witnesses.append({"source": "registry conditions", "verdict": "EXCLUDED", "strength": "WEAK", "quote": conds,
                              "why": f"a registered condition names a population the protocol excludes ({text[bad[0][1]:bad[0][2]]})"})
        elif population_matches(target, conds):
            witnesses.append({"source": "registry conditions", "verdict": "ESTABLISHED", "strength": "WEAK", "quote": conds,
                              "why": "a registered condition names the protocol population (the registrant's label, "
                                     "not an entry criterion: used only when criteria and reports are silent)"})
    weak = {w["verdict"] for w in witnesses if w.get("strength") == "WEAK"}
    # strong witnesses (criteria, primary report) decide; exclusions first. The registry conditions label only fills
    # silence, and never outvotes an entry statement.
    if "EXCLUDED" in strong and "ESTABLISHED" in strong:
        state = "CONFLICT"
    elif "EXCLUDED" in strong:
        state = "EXCLUDED"
    elif "MIXED" in strong:
        state = "MIXED"
    elif "ESTABLISHED" in strong:
        state = "CONFLICT" if "EXCLUDED" in weak else "ESTABLISHED"
    elif "EXCLUDED" in weak:
        state = "EXCLUDED"
    elif "MIXED" in weak:
        state = "MIXED"
    elif "ESTABLISHED" in weak:
        state = "ESTABLISHED"
    else:
        state = "NOT_ESTABLISHED"
    out = {"state": state, "witnesses": witnesses,
           "basis": "registry eligibility criteria + primary report enrolment sentence and title; exclusions before "
                    "the positive match; the registry conditions label only fills silence"}
    if state == "NOT_ESTABLISHED" and clar:
        # a disclosed RETROSPECTIVE vocabulary clarification may establish it; it is recorded as such
        from .trial_family import population_clarification
        texts = [w.get("quote") for w in witnesses if isinstance(w.get("quote"), str)]
        inc_items = split_criteria(crit.get("value") or "")[0]
        c = population_clarification(config, inc_items + texts + list(conds))
        if c:
            out.update(state="ESTABLISHED", population_basis="RETROSPECTIVE_VOCABULARY_CLARIFICATION",
                       population_clarification=c)
    return out


# ---------------------------------------------------------------------------------------------------------------
# V1.0.1 extension (dapagliflozin HFmrEF/HFpEF review)
#
# (1) COMORBIDITY IS NOT EXCLUSION. A protocol that excludes "diabetes-ONLY" or "CKD-only" populations excludes a
#     record that mentions diabetes only when positive evidence of the qualifying condition is ABSENT. CARDIA-STIFF
#     (NCT04739215) requires T2D + LVEF >= 50% + clinically diagnosed HFpEF; its conditions list both, and it was
#     excluded under X2 because the config listed 'diabetes' as a plain veto. The "-only" wording is read from the
#     protocol's own exclusion line, so the rule follows the registered text, not a hand-edited config.
# (2) EF MEASURED OR NOT. "HF without known reduced EF" (DECLARE-TIMI 58, n = 1316) is not proof of measured preserved
#     EF, although the comparator's table prints that subgroup as "HF and EF >= 45%". The trial's own report says EF
#     "was collected when available". The row is typed EF_UNMEASURED_OR_UNKNOWN from the trial's report.

_ONLY_ABBREV = {"ckd": "kidney", "t2d": "diabet", "t2dm": "diabet", "mi": "myocardial infarction", "af": "atrial fibrillation"}


def entry_only_terms_from_protocol(protocol_text: str, none_terms) -> list:
    """population_none terms the protocol's EXCLUSION wording qualifies with '-only' ('diabetes-only, CKD-only'):
    such a term excludes only a population that has nothing else -- i.e. only when the qualifying condition is absent."""
    out = []
    # only the X2 / wrong-population bullet and its indented continuation lines -- never another section's '-only'
    lines, on = [], False
    for ln in (protocol_text or "").splitlines():
        if re.search(r"\*\*X2\*\*|^\s*-?\s*X2\b|wrong population", ln, re.I):
            on = True
            lines.append(ln)
        elif on and ln.startswith((" ", "\t")) and ln.strip():
            lines.append(ln)
        else:
            on = False
    text = " ".join(lines)
    for m in re.finditer(r"([A-Za-z][A-Za-z0-9 /'-]{1,40}?)-only\b", text):
        phrase = m.group(1).strip().split(",")[-1].strip().split(" ")[-1].lower()
        # the qualified word begins a word of the term (adjective endings allowed: diabetes -> diabetic, thrombophilia ->
        # thrombophilic); a term joining two populations ('women and men') is never an '-only' population
        stem = _ONLY_ABBREV.get(phrase) or phrase[:max(4, len(phrase) - 2)]
        for t in none_terms or []:
            ft = lexicon.fold(str(t))
            if stem and re.search(r"(?<![a-z])" + re.escape(stem), ft) and " and " not in ft and t not in out:
                out.append(t)
    return out


_EF_UNKNOWN = re.compile(r"\bwithout known reduced (?:ejection fraction|EF)\b|\bEF was collected when available\b|"
                         r"\bejection fraction (?:was )?(?:not|un)(?:measured|known|available)\b", re.I)
_EF_MEASURED_PRESERVED = re.compile(r"\b(?:LVEF|ejection fraction|EF)\s*(?:of\s*)?(?:>=|≥|>|greater than|at least)\s*4\d\s*%", re.I)


def ef_state(report_text: str, n_as_printed=None):
    """(state, quote) for the EF of a subgroup, read from the trial's OWN report. When the comparator prints a subgroup
    size (N = 1316), the sentence of the report that carries that number decides; a report that says EF was collected
    'when available' / 'HF without known reduced EF' is EF_UNMEASURED_OR_UNKNOWN, never HFpEF."""
    text = re.sub(r"\s+", " ", report_text or "")
    sents = re.split(r"(?<=[.;])\s+(?=[A-Z(])", text)
    if n_as_printed:
        n = str(n_as_printed).replace(",", "")
        sents = [s for s in sents if re.search(r"(?<![\d,])" + re.escape(n) + r"(?![\d,])", s.replace(",", ""))] or []
    for s in sents:
        if _EF_UNKNOWN.search(s):
            return "EF_UNMEASURED_OR_UNKNOWN", s
    whole = [s for s in re.split(r"(?<=[.;])\s+(?=[A-Z(])", text) if _EF_UNKNOWN.search(s)]
    if whole:
        return "EF_UNMEASURED_OR_UNKNOWN", whole[0]
    for s in sents:
        if _EF_MEASURED_PRESERVED.search(s):
            return "EF_MEASURED_PRESERVED", s
    return "EF_STATE_NOT_ESTABLISHED", None


def member_populations(printed_text: str, reports: list) -> list:
    """For each held report of a comparator member: the comparator's printed population cell (located in its own text
    by the subgroup size the report states) beside the EF state read from the report."""
    out = []
    t = printed_text or ""
    for rep in reports or []:
        ab = rep.get("abstract") or ""
        rows = []
        for m in re.finditer(r"\b(?:HF|heart failure)[^()]{0,40}?\(N\s*=\s*([\d,]+)\)", t):
            n = m.group(1).replace(",", "")
            if re.search(r"(?<![\d,])" + n + r"(?![\d])", ab.replace(",", "")):
                rows.append((m.group(0), n))
        if not rows:
            continue
        cell, n = rows[0]
        state, quote = ef_state(ab, n)
        out.append({"member": rep["member"], "report_pmid": rep["pmid"], "comparator_prints": cell,
                    "n": int(n), "ef_state": state, "report_quote": quote,
                    "note": ("the comparator's label is kept as printed; the EF state is read from the trial's own "
                             "report" + ("" if state != "EF_UNMEASURED_OR_UNKNOWN" else
                                         " -- not proof of measured preserved EF, so not counted as HFpEF"))})
    return out
