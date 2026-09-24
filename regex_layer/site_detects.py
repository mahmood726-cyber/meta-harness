"""R2 labelling specs: for each regex site of harness/target_endpoint.py, eligibility_chain.py and compat_check.py, what a
piece of text must STATE for the site to be right to match it -- written so a labeller can judge a sentence without
seeing the regex.  Keys are the regex_layer.inventory site keys (the same keys as the SITE_SPECS plant entries).

  detects      one sentence: the requirement, read from how the surrounding code uses the match (not the regex)
  trigger      a deliberately BROAD case-insensitive regex that any text the site SHOULD match contains; used to sample
               candidate misses, so it must be a superset (tests/test_site_detects.py checks it against every accept plant)
  text_source  what text the harness actually applies the site to
  lowercased   whether the harness lowercases that text before matching
Sites that match formatting rather than meaning (whitespace, punctuation, sentence boundaries) carry detects=None and a
why_not_labellable instead of a trigger.
"""

_COMPONENTS_SRC = ("text passed to _components_from_text: an abstract definition or result sentence, a registry "
                   "outcome-measure title, or the review's target-endpoint name / component list (after _fold)")
_FOLD_SRC = ("any text _fold() normalises: abstract sentences, endpoint names and keywords, registry paramType, "
             "arm-group labels")
_PROTOCOL_SRC = "the whole protocol markdown after _fold (whitespace collapsed, lowercased)"

DETECTS: dict = {
    # ---- harness/target_endpoint.py ------------------------------------------------------------------------------
    "target_endpoint.py:_NAMED_COMPOSITE_RX": {
        "detects": "the sentence refers to a named trial endpoint -- the primary/secondary outcome (end point, measure, "
                   "variable), MACE / major adverse cardiovascular or vascular events, or a composite outcome -- rather "
                   "than just a single event type",
        "trigger": r"primary|secondary|outcome|end ?-?point|measure|variable|mace|composite|major|serious",
        "text_source": "one abstract sentence (a definition-candidate sentence, or a result sentence being bound)",
        "lowercased": True},
    "target_endpoint.py:_QUALIFIER_RX": {
        "detects": "the sentence says whether the endpoint it names is a primary (incl. co-primary / first or second "
                   "primary) or a secondary (incl. key secondary) outcome",
        "trigger": r"primary|secondary",
        "text_source": "one abstract sentence (definition span or result span)",
        "lowercased": True},
    "target_endpoint.py:_MACE_RX": {
        "detects": "the sentence names a MACE-type composite (MACE, major adverse cardiovascular events, major "
                   "cardiovascular events, major/serious vascular events) -- not 'major adverse events' in general",
        "trigger": r"mace|major|serious|vascular",
        "text_source": "one abstract sentence (definition span or result span)",
        "lowercased": True},
    "target_endpoint.py:_ORDINAL_RX": {
        "detects": "the sentence names WHICH numbered endpoint it is about (e.g. the second primary outcome, the first "
                   "key secondary end point)",
        "trigger": r"first|second|third|fourth|1st|2nd|3rd|4th",
        "text_source": "one abstract sentence (definition span or result span)",
        "lowercased": True},
    "target_endpoint.py:_TIMEPOINT_RX": {
        "detects": "the sentence states the timepoint or follow-up window at which the endpoint is measured (e.g. "
                   "within 30 days, 90-day, at week 52) -- not a patient age or a count",
        "trigger": r"day|week|month|year",
        "text_source": "one abstract sentence (definition span or result span)",
        "lowercased": True},
    "target_endpoint.py:_POPULATION_RX": {
        "detects": "the sentence states the analysis population the endpoint result applies to (e.g. in all randomized "
                   "patients, among patients with diabetes)",
        "trigger": r"patients|participants|randomi[sz]ed|those|population|subgroup",
        "text_source": "one abstract sentence (definition span or result span)",
        "lowercased": True},
    "target_endpoint.py:_EFFECT_RE": {
        "detects": "the sentence reports a ratio effect estimate (hazard, risk/relative risk or odds ratio) together "
                   "with its 95% confidence interval",
        "trigger": r"ratio|relative risk|\bhr\b|\brr\b|\bor\b|confidence|\bci\b",
        "text_source": "one raw abstract outcome sentence (published-effect parsing; also used to reject result "
                       "sentences as definitions)",
        "lowercased": False},
    "target_endpoint.py:sub:7b4eac99d8": {
        "detects": None,
        "why_not_labellable": "whitespace normalisation of a captured population string; matches formatting, not meaning",
        "text_source": "the population group captured by _POPULATION_RX", "lowercased": True},
    "target_endpoint.py:sub:a7bc694bbb": {
        "detects": None,
        "why_not_labellable": "punctuation/non-word stripping to build a dedupe key; matches formatting, not meaning",
        "text_source": "a definition span (lowercased) used as a dedupe key", "lowercased": True},
    "target_endpoint.py:sub:ff4ae8621b": {
        "detects": "the text uses the abbreviation TEAE(s) to mean treatment-emergent adverse event(s)",
        "trigger": r"teae|treatment[- ]emergent",
        "text_source": _FOLD_SRC, "lowercased": True},
    "target_endpoint.py:sub:fce6fbe7f9": {
        "detects": "the text uses the abbreviation SAE(s) to mean serious adverse event(s)",
        "trigger": r"\bsaes?\b|serious adverse",
        "text_source": _FOLD_SRC, "lowercased": True},
    "target_endpoint.py:sub:0b02262c07": {
        "detects": "the text uses the abbreviation AE(s) to mean adverse event(s)",
        "trigger": r"\baes?\b|adverse",
        "text_source": _FOLD_SRC, "lowercased": True},
    "target_endpoint.py:sub:7b4eac99d8#2": {
        "detects": None,
        "why_not_labellable": "whitespace normalisation inside _fold; matches formatting, not meaning",
        "text_source": _FOLD_SRC, "lowercased": True},
    "target_endpoint.py:search:b01e38dc40": {
        "detects": "the text names coronary heart disease (CHD) death as an outcome or component",
        "trigger": r"chd|coronary",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:sub:cb26b534c7": {
        "detects": "the text names NON-cardiovascular death (or another non-cardiovascular outcome), which must not be "
                   "read as cardiovascular death",
        "trigger": r"non[- ]?\s?(?:cardio|cv)",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:714a13cd06": {
        "detects": "the text names cardiovascular death as an outcome component (not non-cardiovascular death, not "
                   "all-cause death, not a cardiovascular non-fatal event)",
        "trigger": r"cardiovascular|\bcv\b|cardiac",
        "text_source": _COMPONENTS_SRC + "; non-cardiovascular masked", "lowercased": True},
    "target_endpoint.py:search:3cac5c21b4": {
        "detects": "the text names cardiovascular death using the abbreviation CV (e.g. CV-death, death (CV))",
        "trigger": r"\bcv|cardiovascular",
        "text_source": _COMPONENTS_SRC + "; non-cardiovascular masked", "lowercased": True},
    "target_endpoint.py:search:aa4a355e65": {
        "detects": "the text names vascular death / death from vascular causes as cardiovascular death (not "
                   "cerebrovascular death, not non-vascular death)",
        "trigger": r"vascular",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:c511b01726": {
        "detects": "the text names transient ischaemic attack (TIA) as an outcome or component",
        "trigger": r"tia|transient|isch",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:bb8366c955": {
        "detects": "the text refers to heart failure by the abbreviation HF (here, as part of an HF hospitalization "
                   "outcome)",
        "trigger": r"\bhf|heart failure|cardiac failure",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:8c575f0c81": {
        "detects": "the text refers to hospitalization / being hospitalized (here, for heart failure)",
        "trigger": r"hospi|admi",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:4a4f5b989a": {
        "detects": "the text names death from heart failure (fatal HF / heart-failure death) as a component -- not a "
                   "non-fatal HF event",
        "trigger": r"fatal|death|died|mortality",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:bb8366c955#2": {
        "detects": "the text refers to heart failure by the abbreviation HF (here, as part of an urgent HF visit "
                   "outcome)",
        "trigger": r"\bhf|heart failure|cardiac failure",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:3994cff820": {
        "detects": "the text says the outcome is analysed as recurrent (total, first-and-repeat) events rather than "
                   "time to first event",
        "trigger": r"recurr|repeat|total",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:c2741ecf04": {
        "detects": "the text names myocardial infarction (MI) as an outcome or component",
        "trigger": r"mi\b|myocard|infarct|heart attack",
        "text_source": _COMPONENTS_SRC, "lowercased": True},
    "target_endpoint.py:search:722dd482f3": {
        "detects": "the sentence reports arm-level counts (events out of patients, e.g. '458 of 3686'), i.e. it is a "
                   "result sentence, not an endpoint definition",
        "trigger": r"\d[^.]{0,40}(?:of|/|among|out of)[^.]{0,20}\d|\d+/\d+",
        "text_source": "one abstract definition-candidate sentence", "lowercased": True},
    "target_endpoint.py:search:a8e12cadeb": {
        "detects": "the sentence defines the PRIMARY endpoint using the words measure or variable (e.g. 'the primary "
                   "efficacy measure was')",
        "trigger": r"primary|main|principal",
        "text_source": "one abstract definition-candidate sentence", "lowercased": True},
    "target_endpoint.py:search:bd7f86d57b": {
        "detects": "the registry analysis's parameter type is a hazard ratio",
        "trigger": r"hazard|\bhr\b",
        "text_source": "a CT.gov results analysis paramType string", "lowercased": True},
    "target_endpoint.py:search:8cbbf29039": {
        "detects": "the registry analysis's parameter type is a risk ratio / relative risk",
        "trigger": r"risk|relative|\brr\b",
        "text_source": "a CT.gov results analysis paramType string", "lowercased": True},
    "target_endpoint.py:search:dafd757c05": {
        "detects": "the registry analysis's parameter type is an odds ratio",
        "trigger": r"odds|\bor\b",
        "text_source": "a CT.gov results analysis paramType string", "lowercased": True},
    "target_endpoint.py:split:4634658391": {
        "detects": None,
        "why_not_labellable": "sentence-boundary splitter (whitespace after . ? !); matches formatting, not meaning",
        "text_source": "raw abstract (fallback sentence split)", "lowercased": False},
    # ---- harness/eligibility_chain.py ----------------------------------------------------------------------------
    "eligibility_chain.py:_PMID_RE": {
        "detects": "the trial id / label carries a PubMed identifier (PMID) -- not an NCT number or another count",
        "trigger": r"pmid|pubmed|\d{7}",
        "text_source": "a pooled trial's id or label", "lowercased": False},
    "eligibility_chain.py:sub:7b4eac99d8": {
        "detects": None,
        "why_not_labellable": "whitespace normalisation in _norm; matches formatting, not meaning",
        "text_source": "protocol markdown and trial text passed to _norm", "lowercased": False},
    "eligibility_chain.py:search:0278e60920": {
        "detects": "the protocol admits trials that are double-blind OR placebo-controlled (either suffices)",
        "trigger": r"blind|mask|placebo",
        "text_source": _PROTOCOL_SRC, "lowercased": True},
    "eligibility_chain.py:search:e9857d1c69": {
        "detects": "the protocol requires trials that are both double-blind AND placebo-controlled (stated as "
                   "'double-blind, placebo-controlled')",
        "trigger": r"blind|mask|placebo",
        "text_source": _PROTOCOL_SRC, "lowercased": True},
    "eligibility_chain.py:search:4744a336ec": {
        "detects": "the protocol requires trials that are both double-blind AND placebo-controlled (stated with 'and')",
        "trigger": r"blind|mask|placebo",
        "text_source": _PROTOCOL_SRC, "lowercased": True},
    "eligibility_chain.py:search:3a8e5df5f4": {
        "detects": "the line is the protocol's labelled Population field and gives its value (read for the analysis "
                   "set: ITT, as randomised, per-protocol)",
        "trigger": r"population",
        "text_source": "raw protocol markdown (a '**Population**' field line)", "lowercased": False},
    "eligibility_chain.py:search:47eac977e0": {
        "detects": "the line is the protocol's labelled Timepoint field and gives its value (the follow-up window)",
        "trigger": r"time ?point|follow",
        "text_source": "raw protocol markdown (a '**Timepoint**' field line)", "lowercased": False},
    "eligibility_chain.py:search:36706f6be6": {
        "detects": "the protocol states a comparator arm (placebo, usual care, no treatment, or a control group) -- not "
                   "merely the phrase 'controlled trial'",
        "trigger": r"placebo|usual|standard|control|comparator|sham|\bno\b|versus|\bvs\b",
        "text_source": _PROTOCOL_SRC, "lowercased": True},
    # ---- harness/compat_check.py ---------------------------------------------------------------------------------
    "compat_check.py:sub:7b4eac99d8": {
        "detects": None,
        "why_not_labellable": "whitespace normalisation in _norm_ws; matches formatting, not meaning",
        "text_source": "source spans shown in compatibility records", "lowercased": False},
    "compat_check.py:findall:6ce8847b51": {
        "detects": "the follow-up value states a duration in days (the number of days is what is summarised)",
        "trigger": r"day|\bd\b",
        "text_source": "a derived per-trial follow-up window value string (e.g. '56 days', 'within 8 weeks')",
        "lowercased": False},
    "compat_check.py:search:854c55479d": {
        "detects": "the comparator review is restricted to ADULTS only (not children, not children and adults together)",
        "trigger": r"adult|aged|years|age\b|older",
        "text_source": "comparator review name + journal + record title + abstract", "lowercased": True},
}
