"""ONE component vocabulary for composite endpoints, shared by extraction (harness.target_endpoint) and RoB 2 D5 (harness.rob2).

P0 (external audit reviews 18, 25, 28, 29): the two routes kept DIFFERENT vocabularies, and both dropped what they did not know.
  * rob2 did not know 'CHD death', so ODYSSEY's 4-point primary read as 3 components and 'CHD death' alone read as {}.
  * Extraction did not know 'cardiac interventions', so Alpha Omega's 'fatal and nonfatal cardiovascular events and cardiac
    interventions' passed as 3-point MACE while ASCEND was refused for its TIA.
  * In both, a bare generic label ('MACE', 'major (adverse) cardiovascular events') expanded to the default 3-point set even when
    the same sentence enumerated something else.

The rules here:
  1. components(text) returns the canonical components the text NAMES, and the enumerated items it could NOT map (`unknown`).
     An unknown item is never dropped: a caller treats the composite as NOT ESTABLISHED.
  2. A generic label expands to the default 3-point set only when the text enumerates nothing at all (or says '3-point').
  3. Item recognition uses the UNION of both routes' vocabularies, so a composite either route already understood (kidney, VTE,
     all-cause, heart-failure death ...) never becomes 'unknown': P0 changes only what neither route knew.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

THREE_POINT = frozenset({"cardiovascular death", "myocardial infarction", "stroke"})

# canonical name -> rob2's established names (unchanged downstream contract)
ROB2_NAME = {
    "cardiovascular death": "CV_DEATH",
    "myocardial infarction": "NONFATAL_MI",
    "stroke": "NONFATAL_STROKE",
    "heart failure hospitalization": "HF_HOSPITALISATION",
    "unstable angina": "UNSTABLE_ANGINA",
    "coronary revascularization": "REVASCULARISATION",
    "coronary heart disease death": "CHD_DEATH",
    "transient ischemic attack": "TIA",
}

# an enumeration cue: what follows lists the composite's components
_ENUM_CUE = re.compile(r"\b(?:composite of|composite outcome of|composite end ?point of|comprised|comprising|consisting of|"
                       r"defined as|which included|include[sd]?|including)\b\s*:?\s*", re.I)
_ITEM_SPLIT = re.compile(r"\s*(?:,|;|\bor\b|\band\b|/)\s*", re.I)
_ITEM_NOISE = re.compile(r"^(?:the|a|an|any|first|occurrence of|time to(?: the)? first(?: occurrence of)?|either|fatal|"
                         r"non-?fatal|nonfatal|respectively|whichever (?:came|occurred) first)\b\s*", re.I)
# a fragment that only qualifies a component and names none of its own
_QUALIFIER_ONLY = re.compile(r"^(?:fatal|non-?fatal|nonfatal|urgent|emergent|elective|any|first|other|all|whichever .*|respectively|"
                             r"time to first occurrence|death|excluding .*|(?:the )?time from .*|.*any component of .*|"
                             # a scope phrase ('in the efficacy analysis', 'in the') names no component
                             r"in the\b.*)$", re.I)
_OTHER_KNOWN = re.compile(
    r"all[- ]cause (?:death|mortality)|death from any cause|^death$|^mortality$|"
    r"heart failure death|death from heart failure|urgent (?:heart failure |hf )?visit|"
    r"kidney failure|end[- ]stage (?:kidney|renal)|\besrd\b|\beskd\b|dialysis|kidney transplant|renal replacement|"
    r"egfr|\bgfr\b|serum creatinine|renal death|renal causes|"
    r"venous thromboembolism|\bvte\b|deep[- ]vein thrombosis|\bdvt\b|pulmonary embolism|\bpe\b|"
    r"madrs|montgomery|recurrent events?|heart failure|\bhf\b|cardiac arrest|vascular causes|cardiovascular causes|"
    # 'death from cardiovascular or undetermined causes' (AMPLITUDE-O): the split orphans 'undetermined causes', which the standard
    # CV-endpoint adjudication convention counts AS cardiovascular death -- part of the death component, not a new one
    r"undetermined causes?|unknown causes?")


_GENERIC_ITEM = re.compile(r"^(?:(?:the )?(?:major |serious )?(?:adverse )?(?:(?:cv|cardiovascular|vascular|cardiac) events?|mace)(?: components?)?\s*)+$")
# only a DEFINING cue unwraps a parenthetical: 'nonfatal (including silent) myocardial infarction' qualifies a component, it
# does not define a composite (LEADER: round-2 unwrapping made 'silent' an unknown component)
_DEFINING_CUE = re.compile(r"\b(?:defined as|comprised|comprising|consisting of|consisted of|composite of)\b", re.I)
# 'The endpoint comprised X.' defines the composite named in the sentence before (agy p0-r2 #3)
_SUBJECT_CUE = re.compile(r"\b(?:end ?points?|outcomes?)\s+(?:was |were |is |are )?(?:comprised|composed of|consisted of|"
                          r"included|includes|defined as)\b")
_COMPOSITE_CONTEXT = re.compile(r"\bcomposite\b|\bmace\b|\bmajor (?:adverse )?(?:cardio)?vascular events?\b|"
                                r"\b(?:cv|cardiovascular) events\b")


@dataclass
class Parsed:
    components: set[str] = field(default_factory=set)
    unknown: list[str] = field(default_factory=list)      # enumerated items no vocabulary maps
    enumerated: bool = False                              # the text lists components after a cue
    expanded_generic: bool = False                         # the default 3-point set came from a generic label


def _fold(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").lower().replace("‐", "-").replace("‑", "-")).strip()


def known(s: str) -> set[str]:
    """Canonical cardiovascular components named anywhere in the (folded) text."""
    comps: set[str] = set()
    if ("coronary heart disease death" in s or "death from coronary heart disease" in s or "coronary death" in s
            or "fatal coronary heart disease" in s or "fatal chd" in s
            or re.search(r"\bchd\b.{0,30}death|death.{0,30}\bchd\b", s)):
        comps.add("coronary heart disease death")
    # 'non-CV death' is not CV death: the hyphen is a word boundary, so '\bcv\b' matched inside it (agy p0-r1 #1 / p0-r5 #1)
    s_cv = re.sub(r"\bnon-?\s?(?:cardiovascular|cv)\b", "noncv", s)
    if ("cardiovascular death" in s_cv or "death from cardiovascular" in s_cv or "cardiovascular causes" in s_cv
            or re.search(r"cardiovascular(?:(?!\b(?:or|and)\b|[,;]).){0,30}death|death(?:(?!\b(?:or|and)\b|[,;]).){0,30}cardiovascular", s_cv)
            or re.search(r"\bcv\b.*death|death.*\bcv\b", s_cv)
            or re.search(r"(?:cv|cardiovascular)[- ]related death", s_cv)
            or re.search(r"(?<!cerebro)(?<!cardio)(?<!non-)(?<!non)\bvascular death|(?<!non-)death from vascular causes", s)):
        comps.add("cardiovascular death")
    if "transient ischemic attack" in s or "transient ischaemic attack" in s or re.search(r"\btia\b", s):
        comps.add("transient ischemic attack")
    if (re.search(r"\bhhf\b", s) or re.search(r"hospitali[sz](?:ation|ed)\b.{0,35}\b(?:heart failure|hf)\b", s)
            or re.search(r"\b(?:heart failure|hf)\b.{0,35}hospitali[sz](?:ation|ed)", s)):
        comps.add("heart failure hospitalization")
    if "myocardial infarction" in s or re.search(r"\bmi\b", s):
        comps.add("myocardial infarction")
    if "stroke" in s:
        comps.add("stroke")
    if "unstable angina" in s:
        comps.add("unstable angina")
    if re.search(r"revasculari[sz]ation", s):
        comps.add("coronary revascularization")
    return comps


def _item_known(item: str) -> bool:
    it = item.strip(" .()[]")
    # the item as written first: 'fatal coronary heart disease' is a named synonym, and stripping 'fatal' would lose it
    # (codex p0-r2 #3)
    if known(_fold(it)) or _OTHER_KNOWN.search(_fold(it)):
        return True
    while True:
        new = _ITEM_NOISE.sub("", it).strip()
        if new == it:
            break
        it = new
    if not it or _QUALIFIER_ONLY.match(it):
        return True
    f = _fold(it)
    return bool(known(f) or _OTHER_KNOWN.search(f))


def enumerated_items(s: str) -> list[str]:
    """The items listed after each enumeration cue, up to the clause end ('.', a bracket, a result word) or the next cue.
    Parenthetical groups are removed first ('cardiovascular (CV) death', 'myocardial infarction (fatal or nonfatal)'), so a
    qualifier never cuts the list and hides later items (codex p0-r1 #3); a registry title and description joined without a
    stop ('Composite of CV Events CV events include: ...') are two segments."""
    # a parenthetical that ENUMERATES ('MACE (defined as ...)') is unwrapped and read; any other is removed (codex/agy p0-r2 #1)
    s = re.sub(r"\s*\(([^()]*)\)", lambda m: (" " + m.group(1) + ". ") if _DEFINING_CUE.search(m.group(1)) else "",
               strip_exclusions(s))
    items: list[str] = []
    # only a sentence that names a COMPOSITE enumerates its components: a registry description's other 'defined as' clauses
    # (censoring: 'defined as the latest of the dates of assessments ...') are not component lists
    # sentences, including two glued without a space ('...respectively.at 12 months': PHILO)
    for sent in re.split(r"(?<=\.)\s+|(?<=[a-z]{2}\.)(?=[a-z])", s):
        if not (_COMPOSITE_CONTEXT.search(sent) or _SUBJECT_CUE.search(sent)):
            continue
        cues = list(_ENUM_CUE.finditer(sent))
        for i, m in enumerate(cues):
            tail = sent[m.end():cues[i + 1].start()] if i + 1 < len(cues) else sent[m.end():]
            # the list ends at the clause end, a result word, or a relative / temporal clause ('..., which was assessed in
            # the intention-to-treat population': REWIND)
            end = re.search(r"\.(?:\s|$)|[)\]]|\(|\bvs\b|\bversus\b|\boccurred\b|\bwas reported\b|\bwere\b|\bwas\b|"
                            r"\bwhich\b|\bthat\b|\bassessed\b|\badjudicated\b|\bamong\b|\bduring\b|\bwithin\b|\bbut\b|"
                            r"\bin (?:patients|participants|subjects)\b|\b(?:patients|participants) with\b", tail)
            seg = tail[:end.start()] if end else tail
            items += [x for x in _ITEM_SPLIT.split(seg) if x and x.strip(" .")]
    return items


_EXCLUSION = re.compile(
    r"\b(?:excluding|except(?: for)?|other than|not including)\b[^,.;)]*"
    # Passive exclusions name the component BEFORE the verb (M2 W4a/W4b).
    # Stop at list/clause boundaries so included components are not swallowed.
    # The tail stops at a following clause ('... was excluded BUT myocardial infarction was included': codex m2w4-cap-r1 #3).
    r"|\b(?:(?!\b(?:and|or)\b)[^,.;()])+?\s+(?:was|were|is|are)\s+excluded\b"
    r"(?:(?!\b(?:but|while|whereas|although|and)\b)[^,.;)])*")


# a passive exclusion whose SUBJECT is a population is an eligibility criterion, never an endpoint exclusion: 'Patients with
# prior stroke were excluded' removed stroke from MACE (captain review of the M2 W4 change, 12 Oct)
_POPULATION_SUBJECT = re.compile(r"\b(?:patients?|participants?|subjects?|individuals?|people|persons?|women|men|those|"
                                 r"anyone|history|prior|previous|pregnan\w*|children|adults?)\b", re.I)


def _endpoint_exclusions(text):
    """(start, end) of each ENDPOINT exclusion clause in text. A passive one ('stroke and MI were excluded') spans its whole
    conjoined subject back to the nearest comma / bracket / clause mark (agy m2w4-cap-r1 #2: only 'MI' was excluded)."""
    for m in _EXCLUSION.finditer(text):
        v = re.search(r"\s(?:was|were|is|are)\s+excluded\b", m.group(0))
        if not v:
            yield m.start(), m.end()
            continue
        verb = m.start() + v.start()
        # the population test reads the WHOLE subject -- from the clause start to the verb, across 'and' ('patients with
        # diabetes and stroke were excluded': codex m2w4-cap-r1 #1) -- and ONLY the subject, never words after the verb
        # ('stroke was excluded from the endpoint in patients with diabetes' is an endpoint exclusion: #2)
        clause = max(text.rfind(c, 0, m.start()) for c in ".;:") + 1
        if _POPULATION_SUBJECT.search(text[clause:verb]):
            continue
        # the verb's NUMBER decides the subject: 'stroke and MI WERE excluded' is one conjoined subject (agy m2w4-cap-r1 #2),
        # 'defined as CV death and MI and nonfatal stroke WAS excluded' is a list, then a new clause on its last item
        if re.match(r"\s(?:were|are)\b", v.group(0)):
            yield max(text.rfind(c, 0, m.start()) for c in ".;:,()") + 1, m.end()
        else:
            yield m.start(), m.end()


def excluded(text: str | None) -> set[str]:
    """Components an exclusion clause names: they stay out even after a generic label expands (codex/agy p0-r2 #2)."""
    if not text:
        return set()
    t = _fold(text)
    return set().union(*[known(t[a:b]) for a, b in _endpoint_exclusions(t)])


def strip_exclusions(s: str) -> str:
    """Remove exclusion clauses: an excluded component is not a named one (codex p0-r1 #5, M2 W4)."""
    s = s or ""
    for a, b in reversed(list(_endpoint_exclusions(s))):
        s = s[:a] + " " + s[b:]
    return s


def components(text: str | None, expand_generic: bool = True) -> Parsed:
    s = _fold(text)
    out = Parsed(components=known(strip_exclusions(s)))
    items = enumerated_items(s)
    if items:
        out.enumerated = True
        out.unknown = [i.strip() for i in items if not _item_known(i)]
        # a generic CATEGORY item ('CV events', 'cardiovascular events') is a label, not a component, when the same text
        # names real components (STRENGTH's registry: 'The Composite of CV Events ... CV events include: CV death, non-fatal
        # MI and non-fatal stroke'); with none named (Alpha Omega) it stays unknown
        if out.components:
            out.unknown = [u for u in out.unknown if not _GENERIC_ITEM.search(_fold(u))]
    generic = re.search(r"\bmace\b|\bmajor (?:adverse )?cardiovascular events?\b", s)   # not 'major vascular events' (CTT)
    three_point = re.search(r"\b(?:3|three)[- ]?point\b", s)
    if expand_generic and generic and (three_point or (not out.components and not out.enumerated)):
        out.components |= set(THREE_POINT)
        out.expanded_generic = True
    # '4-point' implies unstable angina only when nothing is enumerated (an enumerated fourth component wins: codex p0-r1 #1)
    if expand_generic and generic and not out.enumerated and re.search(r"\b(?:4|four)[- ]?point\b", s):
        out.components.add("unstable angina")
    out.components -= excluded(s)
    return out
