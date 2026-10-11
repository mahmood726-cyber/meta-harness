"""ONE component vocabulary and parser for every route that reads an endpoint's components (DISPATCH_REVIEW29, P0).

Before this module the extraction route (harness/target_endpoint._components_from_text) and the risk-of-bias route
(harness/rob2._component_set) each had their own vocabulary, and each silently DROPPED what it did not know:
  - rob2 did not know CHD death (ODYSSEY: D5 matched the registered 'CHD death' secondary by text_identity);
  - target_endpoint did not know 'cardiac interventions' (Alpha Omega served as EXACT 3-point MACE) and expanded a bare
    'major cardiovascular events' to the default 3-point set;
  - rob2 dropped 'urgent HF visit' (DAPA-HF, r18) and read composites with extra parts as 3-point (COLCOT, CLEAR, r25).

Rules (each planted in tests/test_components.py):
  1. one vocabulary, recognised by both routes (CHD death, coronary death, fatal CHD, revascularisation, hospitalisation
     for (unstable) angina, TIA, cardiac interventions, cardiac arrest, urgent HF visit, ...);
  2. a part of a composite listing that names an event this vocabulary does not know is UNRECOGNISED -- reported, never
     dropped; a caller treats it as NOT_ESTABLISHED;
  3. a generic label (MACE / major (adverse) cardiovascular events / major vascular events) is never expanded from SOURCE
     text: it binds to the trial's own definition span or is not established. Only an explicit '3-point' / '4-point'
     MACE names a standard set. (The REVIEW's declared target may expand its own generic name: that is a protocol
     decision, recorded where it is made -- target_endpoint.canonical_components.)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

# --------------------------------------------------------------------------------------------------- normalisation
_FOLD = (
    ("hospitalisation", "hospitalization"), ("hospitalisations", "hospitalizations"), ("hospitalised", "hospitalized"),
    ("revascularisation", "revascularization"), ("ischaemic", "ischemic"), ("ischaemia", "ischemia"),
    ("cv ", "cardiovascular "), ("cv-", "cardiovascular-"), ("hhf", "heart failure hospitalization"),
    ("e-gfr", "egfr"),
)


def fold(text: str | None) -> str:
    """Lower-case, British spellings folded to American, abbreviations the vocabulary reads expanded."""
    s = str(text or "").lower()
    for old, new in _FOLD:
        s = s.replace(old, new)
    s = re.sub(r"\bteaes?\b", "treatment-emergent adverse events", s)
    s = re.sub(r"\bsaes?\b", "serious adverse events", s)
    s = re.sub(r"\baes?\b", "adverse events", s)
    return re.sub(r"\s+", " ", s)


# ------------------------------------------------------------------------------------------------------ vocabulary
# canonical name -> uppercase id (rob2's served ids are kept; new components get new ids)
IDS = {
    "coronary heart disease death": "CHD_DEATH",
    "cardiovascular death": "CV_DEATH",
    "all-cause death": "ALL_CAUSE_MORTALITY",
    "non-cardiovascular death": "NONCV_DEATH",
    "myocardial infarction": "NONFATAL_MI",
    "stroke": "NONFATAL_STROKE",
    "transient ischemic attack": "TIA",
    "unstable angina": "UNSTABLE_ANGINA",
    "angina hospitalization": "ANGINA_HOSPITALISATION",
    "coronary revascularization": "REVASCULARISATION",
    "cardiac intervention": "CARDIAC_INTERVENTION",
    "cardiac arrest": "CARDIAC_ARREST",
    "pulmonary embolism": "PULMONARY_EMBOLISM",
    "deep vein thrombosis": "DVT",
    "cardiac arrhythmia": "CARDIAC_ARRHYTHMIA",
    "major bleeding": "MAJOR_BLEEDING",
    "heart failure hospitalization": "HF_HOSPITALISATION",
    "urgent heart failure visit": "URGENT_HF_VISIT",
    "heart failure death": "HF_DEATH",
    "heart failure event": "HF_EVENT_UNSPECIFIED",
    "recurrent events": "RECURRENT_EVENTS",
    "kidney failure": "KIDNEY_FAILURE",
    "sustained egfr decline": "EGFR_DECLINE",
    "renal death": "RENAL_DEATH",
    "kidney progression composite": "KIDNEY_PROGRESSION_COMPOSITE",
    "madrs change": "MADRS_CHANGE",
    "recurrent vte": "RECURRENT_VTE",
}
NAMES = {v: k for k, v in IDS.items()}
STANDARD_3P = frozenset({"cardiovascular death", "myocardial infarction", "stroke"})
_CARDIO = frozenset({"coronary heart disease death", "cardiovascular death", "all-cause death", "myocardial infarction",
                     "stroke", "transient ischemic attack", "unstable angina", "angina hospitalization",
                     "coronary revascularization", "cardiac intervention", "cardiac arrest",
                     "heart failure hospitalization", "urgent heart failure visit", "heart failure death",
                     "heart failure event"})

GENERIC_LABEL_RX = re.compile(r"\bmace\b|\bmajor adverse cardiovascular events?\b|\bmajor (?:adverse )?cardiovascular "
                              r"events?\b|\bmajor (?:adverse )?vascular events?\b|\bmajor cardiac events?\b")


def _named(s: str) -> set[str]:
    """The components a FOLDED text names (the union vocabulary of both former parsers, plus the review-29 additions).
    The extraction route's original rules are kept verbatim where they existed (their comments name the trials)."""
    comps: set[str] = set()
    # coronary death: 'death from coronary heart disease', 'CHD death', 'coronary death', 'fatal CHD', 'death from
    # coronary causes' (ODYSSEY; review 29)
    if ("coronary heart disease death" in s or "death from coronary heart disease" in s
            or re.search(r"\bchd\b.{0,30}death|death.{0,30}\bchd\b|\bfatal (?:chd|coronary heart disease)\b"
                         r"|\bcoronary death\b|death from coronary (?:causes|artery disease)", s)):
        comps.add("coronary heart disease death")
    # 'non-cardiovascular death' / 'death from non-cardiovascular causes' is NOT cardiovascular death
    s_cv = re.sub(r"\bnon-?\s?cardiovascular\b", "noncv", s)
    if ("cardiovascular death" in s_cv or "death from cardiovascular" in s_cv or "cardiovascular causes" in s_cv
            or re.search(r"cardiovascular(?:(?!\b(?:or|and)\b|[,;]).){0,30}death|death(?:(?!\b(?:or|and)\b|[,;]).){0,30}"
                         r"cardiovascular", s_cv)
            or re.search(r"\bcardiovascular[- ]related\s+death|\bcardiovascular\s+mortality\b", s_cv)
            # 'death from vascular causes' / 'vascular death' is the PLATO / PHILO / ASCEND / ORIGIN phrasing
            or re.search(r"(?<!cerebro)(?<!cardio)(?<!non-)(?<!non)\bvascular death|(?<!non-)death from vascular causes",
                         s)):
        comps.add("cardiovascular death")
    if re.search(r"\ball[- ]cause (?:mortality|death)\b|\bdeath from any cause\b|\bdeath (?:of|from) all causes\b", s):
        comps.add("all-cause death")
    if re.search(r"\bnon-?\s?cardiovascular (?:death|mortality)\b|\bdeath from non-?\s?cardiovascular causes\b", s):
        comps.add("non-cardiovascular death")
    if "transient ischemic attack" in s or re.search(r"\btia\b", s):
        comps.add("transient ischemic attack")
    if (("heart failure" in s and "hospitalization" in s)
            or "hospitalizations due to heart failure" in s
            or (re.search(r"\bhf\b", s) and re.search(r"hospitali[sz]", s))
            or (re.search(r"\bhospitali[sz]ed\s+(?:for|because of|due to)\s+(?:acute\s+|worsening\s+)?(?:heart failure|hf)\b", s)
                and (re.search(r"\b(?:were|was|been|being|be)\s+(?:re)?hospitali[sz]ed\b", s)
                     or re.search(r"hazard ratio|odds ratio|risk ratio|\b(?:hr|rr|or)\b|%|\bvs\b|versus", s))
                and not re.search(r"\b(?:eligib|enrol|inclusion|recruit)", s))):
        comps.add("heart failure hospitalization")
    if re.search(r"(?<!non-)(?<!non)\bfatal\b.{0,25}\b(?:hf|heart failure)\b|death from heart failure|heart failure death",
                 s):
        comps.add("heart failure death")
    # an urgent visit FOR HEART FAILURE only ('urgent asthma visit' is not this component)
    if re.search(r"\burgent\b[^.;]{0,30}\bvisit\b[^.;]{0,50}\b(?:heart failure|hf)\b|\b(?:heart failure|hf)\b[^.;]{0,20}"
                 r"\burgent\b[^.;]{0,20}\bvisit\b|\burgent (?:heart failure|hf) visit\b", s):
        comps.add("urgent heart failure visit")
    if (re.search(r"\b(?:new|worsening)\b.{0,15}\bheart failure\b|\bheart failure events?\b", s)
            and not comps & {"heart failure hospitalization", "urgent heart failure visit"}):
        comps.add("heart failure event")
    if ("recurrent" in s and ("hospitalization" in s or "event" in s)
            and ("rate of recurrent" in s or "recurrent event rate" in s or "total recurrent" in s
                 or "first and recurrent" in s
                 or re.search(r"analy[sz]ed as (?:a )?recurrent event|recurrent[- ]event analysis", s))):
        comps.add("recurrent events")
    if "myocardial infarction" in s or re.search(r"\bmi\b", s):
        comps.add("myocardial infarction")
    if "stroke" in s:
        comps.add("stroke")
    if "unstable angina" in s:
        comps.add("unstable angina")
    elif re.search(r"\bhospitali[sz](?:ation|ed)\b[^.;]{0,30}\bangina\b|\bangina\b[^.;]{0,30}\bhospitali[sz]", s):
        comps.add("angina hospitalization")
    if re.search(r"\b(?:coronary\s+)?revasculari[sz]ation", s) and not re.search(r"\bperipheral\s+revasculari", s):
        comps.add("coronary revascularization")
    if re.search(r"\bcardiac (?:interventions?|procedures?)\b", s):
        comps.add("cardiac intervention")
    if re.search(r"\bcardiac arrests?\b", s):
        comps.add("cardiac arrest")
    # further events composites list (registered spironolactone / tranexamic / ticagrelor outcomes): known, so a listing
    # that names them is established -- and a composite carrying them is never read as 3-point MACE
    if re.search(r"\bpulmonary embol", s):
        comps.add("pulmonary embolism")
    if re.search(r"\bdeep[- ]vein thrombosis\b|\bdvt\b", s):
        comps.add("deep vein thrombosis")
    if re.search(r"\b(?:cardiac\s+)?arrhythmias?\b", s):
        comps.add("cardiac arrhythmia")
    if re.search(r"\bmajor bleed", s):
        comps.add("major bleeding")
    if "kidney failure" in s:
        comps.add("kidney failure")
    if "kidney composite" in s or "renal composite" in s or "composite kidney outcome" in s:
        comps.update({"kidney failure", "sustained egfr decline", "renal death"})
    if "egfr" in s and any(w in s for w in ("decline", "decrease", "reduction")):
        comps.add("sustained egfr decline")
    if "renal death" in s or "death from renal" in s:
        comps.add("renal death")
    return comps


def _named_rob2_only(s: str) -> set[str]:
    """Components the risk-of-bias route has always recognised for non-cardiovascular topics (MADRS, VTE, the broad
    kidney composite). They are part of the ONE vocabulary; listed separately only so their (unchanged) rules read as
    the rob2 rules they were."""
    comps: set[str] = set()
    if re.search(r"\bmadrs\b|\bmontgomery[- ]?a?sberg\b", s):
        is_response = re.search(r"\bresponse\b|\bremission\b|50\s*%|\b50 percent\b|\breduction\b", s)
        if re.search(r"\bchange\b|\bfrom baseline\b|\btotal score\b", s) and not is_response:
            comps.add("madrs change")
    if re.search(r"\brecurrent\b", s) and re.search(r"\bvtes?\b|\bvenous thromboembolism\b|\bdvt\b|\bdeep vein "
                                                     r"thrombosis\b|\bpe\b|\bpulmonary embolism\b", s):
        if not re.search(r"\bnet clinical benefit\b", s):
            comps.add("recurrent vte")
    if re.search(r"\b(?:kidney|renal|egfr|gfr|esrd|end[- ]stage|dialysis)\b", s) and re.search(
            r"\b(?:composite|progression|sustained|decline|decrease|failure|replacement therapy|dialysis|death)\b", s):
        comps.add("kidney progression composite")
    return comps


# ------------------------------------------------------------------------------------------- listings / unknown parts
_LIST_MARKER = re.compile(r"\b(?:composite(?:\s+(?:end\s*-?point|outcome))?\s+of|consisting\s+of|which\s+compris(?:ed|es)"
                          r"|which\s+includ(?:ed|es)"
                          r"|compris(?:ed|ing|es)\s+(?:of\s+)?|first\s+(?:occurrence|event)\s+of|defined\s+as(?:\s+the\s+"
                          r"composite\s+of)?|including|:)", re.I)
_EVENT_NOUN = re.compile(r"\b(?:death|deaths|mortality|infarction|stroke|hospitali[sz]|visit|arrest|angina|revasculari[sz]"
                         r"|failure|embol|thrombo|bleed|haemorrhage|hemorrhage|amputation|intervention|procedure|surgery"
                         # (not 'disease': 'patients at risk for atherosclerotic cardiovascular disease' is a population)
                         r"|transplant|dialysis|attack|syncope|arrhythmia|events?|hypertension|fibrillation)",
                         re.I)
_QUALIFIER = re.compile(r"\b(?:including|excluding|excluded|except|adjudicat\w*|prior\s+to|censoring|co-primary|"
                        # a POPULATION is not a component ('in patients with heart failure with preserved ejection fraction')
                        r"with\s+(?:preserved|reduced|mildly\s+reduced)|ejection\s+fraction|in\s+(?:patients|participants)|"
                        r"(?:patients|participants|subjects)\s+with|"
                        r"as\s+assessed|according\s+to|"
                        r"committee|whichever|within\s+\d|at\s+\d|over\s+\d|during)\b.*$", re.I)
_FILLER = re.compile(r"\b(?:subjects|participants|patients|number|included|in|the|of|a|an|first|occurrence|time|to|any|"
                     r"event|events|cumulative|percentage|proportion|plus|which|included|includes|include|"
                     r"composite|endpoint|end|point|outcome|primary|secondary|co|nonfatal|non|fatal|acute|recurrent|new|"
                     r"target|vessel|related|due|for|from|with|resulting|requiring|defined|as|by|on|at|least|one|or|and|"
                     r"is|was|were|which|that|definitive|adjudicated|confirmed|clinical|clinically|unplanned|driven|"
                     r"urgent|resuscitated|hospitalization|hospitalized|coronary|ischemic|ischemia|rate|rates|"
                     r"incidence|risk)\b|[^a-z]+", re.I)
_BARE_DEATH = re.compile(r"^\W*(?:all\s+)?(?:deaths?|mortality)\W*$", re.I)


# a part that opens with the endpoint's ROLE ('the primary outcome was', 'the initially specified primary end point was the
# cumulative rate of') carries the endpoint's name, not a component: the role phrase and rate wording are stripped before the
# part is judged (ASCEND 'The primary outcome was a first serious vascular event (...)'; ORIGIN '... was the cumulative
# rate of death, ...'; PROSPER '... was the occurrence of a first cardiovascular event (...)')
_ROLE_INTRO = re.compile(r"^.*?\b(?:primary|secondary|co-?primary|principal|main)\s+(?:[a-z-]+\s+){0,3}?"
                         r"(?:outcome|end\s*-?\s*point|endpoint)s?(?:\s+measures?)?\s*(?:was|were|is|are|:)?\s*", re.I)
_RATE_INTRO = re.compile(r"^\s*(?:the\s+)?(?:cumulative\s+)?(?:rate|incidence|occurrence|risk|time)\s+(?:of|to)\s+"
                         r"(?:the\s+)?(?:a\s+)?(?:first\s+)?(?:occurrence\s+of\s+)?", re.I)


def _parts(seg: str) -> list[str]:
    out = []
    for part in [x for x in re.split(r",|;|\bor\b|\band\b|/|\(|\)", seg) if x.strip()]:
        part = _QUALIFIER.sub("", part)
        part = _RATE_INTRO.sub("", _ROLE_INTRO.sub("", part))
        if part.strip():
            out.append(part)
    return out


def bare_death_listed(text: str | None) -> bool:
    """A listing part that is ONLY 'death' / 'mortality' ('composite of death, MI, or stroke'; ORIGIN '... the cumulative
    rate of death, ...') is ALL-CAUSE death -- a component, counted, never dropped (rule 2)."""
    seg = _listing_segment(fold(text))
    return bool(seg) and any(_BARE_DEATH.match(p) for p in _parts(seg))


def unrecognised_parts(text: str | None) -> tuple[str, ...]:
    """Parts of a component LISTING that name an event the vocabulary does not know -- never dropped (rule 2).

    A text is a listing when a list marker ('composite of', 'which comprised', 'defined as', ...) introduces the parts,
    or when it is itself a list of >= 2 recognised cardiovascular components ('death from coronary heart disease,
    non-fatal myocardial infarction, ischemic stroke, or unstable angina'). Any other text -> () (a single named
    outcome is not a listing)."""
    seg = _listing_segment(fold(text))
    if not seg:
        return ()
    unknown = []
    for part in _parts(seg):
        if _named(part) or _named_rob2_only(part) or _BARE_DEATH.match(part) or not _EVENT_NOUN.search(part):
            continue
        if GENERIC_LABEL_RX.search(part) and not _FILLER.sub("", GENERIC_LABEL_RX.sub("", part)).strip():
            continue                       # the composite's own generic NAME ('the rate of major adverse cardiovascular
                                           # events') is not an unknown component
        if _FILLER.sub("", part).strip():
            unknown.append(re.sub(r"\s+", " ", part).strip()[:60])
    return tuple(unknown)


def _segment_text(text: str) -> str:
    """A listing's text up to where it ends: a sentence break, a ';', a comparison, a result parenthesis, or a RESULT cue
    (a listing never runs on into what happened: 'a 3-point MACE event occurred in 336 patients', VESALIUS-CV)."""
    # (a double quote too: registry text quotes a population label -- empagliflozin's '... (HHF) "Failure with preserved
    # Ejection Fraction (HFpEF)', truncated at source)
    seg = re.split(r"\b(?:compared\s+(?:to|with)|versus|vs\.?)\b|\.\s|;|[\"“”]|\(\s*(?:hazard|hr|rr|95%)"
                   r"|\b(?:occurred|occurring|developed|was reported|were reported)\b|\d+(?:\.\d+)?\s*%"
                   # ... or a METHOD cue ('was evaluated using time-to-event analysis', GLP-1 registry text)
                   r"|\b(?:was|were)\s+(?:evaluated|analy[sz]ed|assessed|calculated|estimated)\b|\busing\b"
                   r"|\b\d+\s+(?:of|patients|participants|subjects)\b", text)[0]
    # '(CV)', '(MI)': an abbreviation, not a part -- removed, and the gap closed ('coronary heart disease (CHD) death'
    # must still read as 'coronary heart disease death')
    return re.sub(r"\s+", " ", re.sub(r"\(\s*[a-z0-9-]{1,8}\s*\)", " ", seg))


def _listing_segment(s: str) -> str:
    """The listing of a FOLDED text, or '' when it is not a cardiovascular listing."""
    s = re.split(r"\bsecondary\s+(?:\w+\s+){0,2}(?:end\s*-?points?|outcomes?)\b", s, maxsplit=1)[0]
    # only a CARDIOVASCULAR listing is judged (>= 2 cardiovascular components, or a generic cardiovascular label): this
    # vocabulary is cardiovascular, and a VTE or respiratory composite is not read by it (rob2-r1 of PR #67)
    if len(_named(s) & _CARDIO) < 2 and not GENERIC_LABEL_RX.search(s):
        return ""

    def _segment(start: int) -> str:
        return _segment_text(s[start:])

    # of several markers ('Time to First Occurrence of MACE ... comprised of CHD death, ...'), the LISTING is the
    # segment that names the most recognised components (ties: the later marker)
    # 'the primary outcome was a first serious vascular event (i.e., nonfatal MI or stroke, TIA, or vascular death)': a
    # composite NAME followed by its parenthesised listing -- the parenthesis IS the listing (ASCEND 30146932, PROSPER
    # 20404379); a name with no parenthesised listing is judged as written (Alpha Omega stays not established)
    for inner in re.findall(r"\(([^()]{10,400})\)", s):
        if len(_named(inner) & _CARDIO) >= 2:
            return _segment_text(re.sub(r"^\s*(?:i\.\s*e\.|e\.\s*g\.|ie|eg)\s*,?\s*", "", inner))
    marks = list(_LIST_MARKER.finditer(s))
    if marks:
        segs = [_segment(m.end()) for m in marks]
        counts = [len(_named(x) | _named_rob2_only(x)) for x in segs]
        return segs[len(segs) - 1 - counts[::-1].index(max(counts))]
    if re.search(r",|\bor\b", s):
        return _segment(0)
    return ""


# ------------------------------------------------------------------------------------------------------------- parse
@dataclass(frozen=True)
class Parse:
    components: frozenset[str]                      # canonical names
    unrecognised: tuple[str, ...] = ()              # listing parts naming an unknown event (rule 2)
    generic_only: bool = False                      # a generic label and no components (rule 3)
    standard_set: frozenset[str] = field(default_factory=frozenset)   # what an explicit 3-/4-point label names

    @property
    def established(self) -> bool:
        return bool(self.components) and not self.unrecognised

    def ids(self) -> frozenset[str]:
        return frozenset(IDS[c] for c in self.components)


def parse(text: str | None, expand_standard: bool = True) -> Parse:
    """The components a SOURCE text names. A bare generic label is generic_only (no expansion); an explicit '3-point' /
    '4-point' MACE with no listing names its standard set."""
    s = fold(text)
    if not s.strip():
        return Parse(frozenset())
    comps = _named(s) | _named_rob2_only(s)
    if bare_death_listed(text):
        comps.add("all-cause death")                  # 'composite of death, MI, or stroke': counted, never dropped
    if "recurrent vte" in comps:
        # recurrent VTE IS its parts (DVT, PE): beside its own umbrella they are not extra components (doac-vte)
        comps -= {"pulmonary embolism", "deep vein thrombosis"}
    if "kidney progression composite" in comps:
        comps.discard("cardiovascular death")         # rob2's rule: a kidney composite's death is not a CV component
        if comps & {"kidney failure", "sustained egfr decline", "renal death"}:
            # the umbrella stands only for a kidney composite named WITHOUT its parts; beside its parts it is not an extra
            # component (finerenone FIDELIO / FIGARO were read as kidney composite + 3 parts)
            comps.discard("kidney progression composite")
    standard: frozenset[str] = frozenset()
    if GENERIC_LABEL_RX.search(s):
        if re.search(r"\b(?:3|three)[- ]?point\b", s):
            standard = STANDARD_3P
        elif re.search(r"\b(?:4|four)[- ]?point\b", s):
            standard = STANDARD_3P | {"unstable angina"}
    # an explicit 3-/4-point label names its standard set in a DEFINITION; a RESULT span ('a 3-point MACE event occurred
    # in 336 patients') is read without it, so it binds to the trial's own definition (VESALIUS-CV: CHD death, MI,
    # ischemic stroke) -- expand_standard=False, as the extraction route has always read result spans
    if expand_standard and standard and not (comps & _CARDIO):
        comps |= standard
    generic_only = bool(GENERIC_LABEL_RX.search(s)) and not comps
    return Parse(frozenset(comps), unrecognised_parts(text), generic_only, standard)


def names(text: str | None, expand_standard: bool = True) -> set[str]:
    """Just the canonical component names (the extraction route's former return type)."""
    return set(parse(text, expand_standard).components)


def target_set(name: str | None, declared: Iterable[str] | None = None) -> set[str]:
    """The REVIEW's declared target components: explicit declared components, else the outcome name parsed -- where a
    generic name ('Major vascular events / MACE') IS expanded to the standard 3-point set. That expansion is the review's
    own protocol decision about ITS target, never a reading of a trial's source text (rule 3)."""
    if declared:
        got = names(" ; ".join(map(str, declared))) & TARGET_VOCABULARY
        return got or {str(x) for x in declared}
    p = parse(name)
    got = set(p.components) & TARGET_VOCABULARY
    if got:
        return got
    # exactly the generic names the extraction route expanded before P0 ('mace', 'major adverse cardiovascular', 'major
    # cardiovascular'): a target named 'Major vascular events' keeps its keyword-family matching (statins topic)
    s = fold(name)
    return set(STANDARD_3P) if ("mace" in s or "major adverse cardiovascular" in s or "major cardiovascular" in s) else set()


# the components a review's TARGET can be declared in: the extraction route's composite vocabulary. A single-concept
# outcome ('All-cause mortality', 'Symptomatic recurrent VTE', 'New renal-replacement therapy') keeps no component target
# and is matched by its keyword family exactly as before -- the source side still READS 'death from any cause' as a
# component, so a composite that includes it is never taken for 3-point MACE.
TARGET_VOCABULARY = frozenset(_CARDIO - {"all-cause death", "heart failure event"}) | {"recurrent events", "kidney failure",
                                                                 "sustained egfr decline", "renal death"}
