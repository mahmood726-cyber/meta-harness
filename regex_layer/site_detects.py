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

# ---- other-lane files (harness/rob2.py, funding.py, hand_binding.py): read only; a site whose text is the whole held
# title+abstract / prose names 'abstract' in text_source (site_measure samples abstract sentences for it); a site that
# reads a derived string (a registry outcome row, a funding basis span, a table cell, XML) names no held population.
_ROB2_SRC = ("a registered AACT outcome (measure + title + description) or the review's pooled outcome name, as rob2 "
             "D5 reads them (after _norm_text, lowercased)")
_FUND_DOC = "held title + abstract, or held full text, as funding.detect / scan_pooled read it"
_FUND_SPAN = "the funding basis span funding.detect cut from held text (a sentence window around the funding anchor)"
_XML = "raw PMC JATS XML of a held full text"
_PROSE = "one sentence of held prose (abstract or full-text body) as hand_binding reads it"


def _fmt(why: str, src: str, low: bool = False) -> dict:
    return {"detects": None, "why_not_labellable": why, "text_source": src, "lowercased": low}


DETECTS.update({
    # ---- harness/rob2.py ---------------------------------------------------------------------------------------------
    "rob2.py:sub:7b4eac99d8": _fmt("whitespace normalisation in _norm_text; matches formatting, not meaning", _ROB2_SRC),
    "rob2.py:search:b4e124d7bc": {
        "detects": "the outcome is measured on the MADRS (Montgomery-Asberg Depression Rating Scale), by name or abbreviation",
        "trigger": r"madrs|montgomery|sberg|depression rating", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:6a51f42d5e": {
        "detects": "the (MADRS) outcome is a response or remission outcome (e.g. >=50% reduction), not a change score",
        "trigger": r"respon|remission|50|reduc", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:c958964040": {
        "detects": "the (MADRS) outcome is a change-from-baseline or total-score outcome",
        "trigger": r"change|baseline|score", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:74ee9684cf": {
        "detects": "the thromboembolic outcome counts a RECURRENCE (recurrent VTE), not a first event",
        "trigger": r"recurr", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:2ee9bddbd6": {
        "detects": "the outcome names a venous thromboembolic event (VTE, deep vein thrombosis, pulmonary embolism)",
        "trigger": r"vte|venous|thrombo|embol|dvt|\bpe\b", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:217d388541": {
        "detects": "the outcome is a net-clinical-benefit composite",
        "trigger": r"net|benefit", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:2302517c9d": {
        "detects": "the outcome is all-cause mortality (death from any cause), not a cause-specific death",
        "trigger": r"all[- ]?cause|any cause|mortality|death", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:95e6c448a9": {
        "detects": "the outcome concerns the kidney (kidney / renal / eGFR / ESRD / end-stage / dialysis)",
        "trigger": r"kidney|renal|gfr|esrd|end[- ]stage|dialysis|nephr", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:39f51c3310": {
        "detects": "the (kidney) outcome is a progression, sustained decline, failure, replacement therapy or composite",
        "trigger": r"composite|progress|sustain|declin|decreas|failure|replacement|dialysis|death",
        "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:052d9d5ea5": {
        "detects": "the outcome names cardiovascular death (not non-cardiovascular death, not all-cause death)",
        "trigger": r"cardiovascular|\bcv\b|cardiac", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:6cd81436fb": {
        "detects": "the outcome names NON-fatal myocardial infarction",
        "trigger": r"fatal", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:ac07acacc3": {
        "detects": "the outcome names myocardial infarction (MI)",
        "trigger": r"myocard|infarct|\bmi\b", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:4ae0272c1d": {
        "detects": "the outcome names NON-fatal stroke",
        "trigger": r"fatal", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:75347cb965": {
        "detects": "the outcome names stroke",
        "trigger": r"stroke|cerebrovascular", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:4494298990": {
        "detects": "the outcome names hospitalisation for heart failure (HHF)",
        "trigger": r"hhf|hospi|admi", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:145e8c3798": {
        "detects": "the outcome names unstable angina",
        "trigger": r"angina", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:07c0729508": {
        "detects": "the outcome names (coronary) revascularisation",
        "trigger": r"revascul|pci|cabg", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:a26bd545ce": {
        "detects": "the outcome is a MACE-type composite (MACE, major adverse cardiovascular/cardiac events), not 'major "
                   "adverse events' in general",
        "trigger": r"mace|major", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:search:e1fe9ad18e": {
        "detects": "the MACE is declared 3-point",
        "trigger": r"3|three", "text_source": _ROB2_SRC, "lowercased": True},
    "rob2.py:sub:e3839b281a": _fmt("punctuation-to-space normalisation in _simple_matches; matches formatting, not meaning",
                                   "the pooled outcome name (lowercased)", True),
    "rob2.py:sub:e3839b281a#2": _fmt("punctuation-to-space normalisation in _simple_matches; matches formatting, not meaning",
                                     "a registered outcome text (lowercased)", True),
    # ---- harness/funding.py ------------------------------------------------------------------------------------------
    "funding.py:_STRONG_ANCHOR": {
        "detects": "the text makes an explicit funding statement (funded by, funding:, grants from, sponsored by, role of "
                   "the funding source, this study was funded/supported/sponsored)",
        "trigger": r"fund|grant|sponsor|financ|support", "text_source": _FUND_DOC, "lowercased": False},
    "funding.py:_WEAK_ANCHOR": {
        "detects": "the text says something was 'supported by' someone (a possible funding statement)",
        "trigger": r"support", "text_source": _FUND_DOC, "lowercased": False},
    "funding.py:_INDUSTRY": {
        "detects": "the funding text names an industry sponsor (a company, manufacturer or pharmaceutical firm)",
        "trigger": r"pharm|inc\b|ltd|llc|gmbh|\bag\b|corp|compan|manufactur|biotech|therapeutics|laborator|nordisk|pfizer|"
                   r"janssen|johnson|astra|boehringer|novartis|bayer|merck|msd|sanofi|gsk|glaxo|lilly|abbvie|amgen|"
                   r"bristol|takeda|roche|genentech|gilead|servier|daiichi|otsuka|lundbeck|vifor|medical",
        "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:_PUBLIC": {
        "detects": "the funding text names a public or non-profit funder (government, research council, university, "
                   "foundation, charity) or states the work received no funding",
        "trigger": r"national|institut|health|council|wellcome|gates|foundation|universit|college|government|ministry|"
                   r"department|european|horizon|charit|academic|nhmrc|nihr?\b|mrc\b|no (?:specific |external )?(?:grant|fund)|"
                   r"not (?:externally )?funded",
        "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:_DRUG_SUPPLY": {
        "detects": "the text states who supplied the study drug or placebo (provided / supplied / donated by a party)",
        "trigger": r"provid|suppl|donat|manufactur|furnish|gift",
        "text_source": _FUND_DOC, "lowercased": False},
    "funding.py:_FUNDING_POINTER": {
        "detects": "the text defers its funding details to a supplement, appendix or online material",
        "trigger": r"fund", "text_source": _FUND_DOC, "lowercased": False},
    "funding.py:_INDUSTRY_AUTHORS": {
        "detects": "the text says an author is employed by (or holds equity in) an industry company",
        "trigger": r"employ|stock|equity|shareholder",
        "text_source": _FUND_DOC, "lowercased": False},
    "funding.py:L81": {"detects": "the span gives the funder a role (or no role) in study design",
                       "trigger": r"design", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:L82": {"detects": "the span gives the funder a role (or no role) in study conduct",
                       "trigger": r"conduct|perform|run", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:L83": {"detects": "the span gives the funder a role (or no role) in data collection",
                       "trigger": r"collect|gather", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:L84": {"detects": "the span gives the funder a role (or no role) in data analysis",
                       "trigger": r"analy", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:L85": {"detects": "the span gives the funder a role (or no role) in writing the report / manuscript",
                       "trigger": r"wr[io]t|manuscript|draft|report", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:_NCT_RE": {
        "detects": "the text carries a ClinicalTrials.gov registration number (NCT + 8 digits)",
        "trigger": r"nct|clinicaltrials",
        "text_source": "a pooled trial's source / label / abstract value (funding.scan_pooled)", "lowercased": False},
    "funding.py:sub:7b4eac99d8": _fmt("whitespace normalisation in _clean; matches formatting, not meaning", _FUND_DOC),
    "funding.py:search:a4601f97a8": _fmt("sentence-boundary finder for the funding window; matches formatting, not meaning",
                                         _FUND_DOC),
    "funding.py:sub:7282f3a795": {
        "detects": "the span opens its sponsor list with a funding lead-in (funded by / funding: / grants from / supported by)",
        "trigger": r"fund|grant|support", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:sub:70a43250a0": {
        "detects": "the span begins 'this study / trial / work / research was funded by'",
        "trigger": r"funded", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:split:88ba5636a3": _fmt("finds where the sponsor list ends (;, sentence end, registration statement); "
                                        "a boundary, not a statement", _FUND_SPAN),
    "funding.py:sub:a8c5be7f86": {
        "detects": "the sponsor list ends with an unnamed remainder ('and others')",
        "trigger": r"others", "text_source": _FUND_SPAN, "lowercased": False},
    "funding.py:split:d3389b2de7": _fmt("list-separator splitter (, and &) between sponsor names; matches formatting, "
                                        "not meaning", _FUND_SPAN),
    "funding.py:sub:5150d3bfe8": _fmt("leading-article stripper on a sponsor name; matches formatting, not meaning",
                                      _FUND_SPAN),
    # ---- harness/hand_binding.py -------------------------------------------------------------------------------------
    "hand_binding.py:_REF_JUNK": {
        "detects": "the sentence is reference-list or front-matter debris (carries a DOI, a PMC id, a pdf link or a "
                   "copyright notice), not trial prose",
        "trigger": r"10\.\d|doi|pmc|pdf|rights reserved|copyright",
        "text_source": _PROSE, "lowercased": False},
    "hand_binding.py:sub:7b4eac99d8": _fmt("whitespace normalisation in _plain; matches formatting, not meaning", _XML),
    "hand_binding.py:sub:caf616cd71": _fmt("XML tag stripper in _plain; matches markup, not meaning", _XML),
    "hand_binding.py:split:59b745f04e": _fmt("sentence splitter after ').' before a digit; matches formatting, not meaning",
                                             _PROSE),
    "hand_binding.py:findall:1af9a0dc3c": _fmt("JATS table-cell extractor; matches markup, not meaning", _XML),
    "hand_binding.py:finditer:2fa8c78f40": _fmt("JATS <table-wrap> block finder; matches markup, not meaning", _XML),
    "hand_binding.py:findall:d83cacfc5a": _fmt("JATS caption extractor; matches markup, not meaning", _XML),
    "hand_binding.py:findall:3ab362c751": _fmt("JATS <thead> block finder; matches markup, not meaning", _XML),
    "hand_binding.py:search:b44342a693": _fmt("JATS <tbody> block finder; matches markup, not meaning", _XML),
    "hand_binding.py:findall:ea304f7fe8": _fmt("JATS table-row finder; matches markup, not meaning", _XML),
    "hand_binding.py:search:159a89219d": _fmt("any-digit test telling a data row from a heading cell; matches a character "
                                              "class, not meaning", "one table cell of a held full text"),
    "hand_binding.py:findall:e1bb2e6e84": _fmt("JATS table-footnote extractor; matches markup, not meaning", _XML),
    "hand_binding.py:_TEXT_TABLES_MARK": _fmt("serialisation marker opening the flattened tables section; matches file "
                                              "format, not meaning", "a held pmc_<pid>_fulltext.txt file"),
    "hand_binding.py:search:b4ef0d080a": _fmt("number-shape test telling a header row from a data row; matches number "
                                              "formatting, not meaning", "the cells of one flattened table line"),
    "hand_binding.py:search:159a89219d#2": _fmt("any-digit test telling a data row from a heading cell; matches a character "
                                                "class, not meaning", "one flattened table cell"),
    "hand_binding.py:sub:2fa8c78f40": _fmt("JATS <table-wrap> remover; matches markup, not meaning", _XML),
    "hand_binding.py:sub:ddb5c10500": _fmt("JATS <ref-list> remover; matches markup, not meaning", _XML),
    "hand_binding.py:sub:2abf06a9a2": _fmt("JATS front/back-matter element remover; matches markup, not meaning", _XML),
    "hand_binding.py:sub:e6e9990818": _fmt("JATS <article-id> remover; matches markup, not meaning", _XML),
    "hand_binding.py:sub:8782f4efdb": _fmt("JATS <xref> citation-marker remover; matches markup, not meaning", _XML),
    "hand_binding.py:sub:caf616cd71#2": _fmt("XML tag stripper in prose_of; matches markup, not meaning", _XML),
    "hand_binding.py:sub:575187a28f": _fmt("word-final 's' stripper for plural tolerance; matches spelling, not meaning",
                                           "folded result text (target_endpoint._fold)", True),
    "hand_binding.py:sub:575187a28f#2": _fmt("word-final 's' stripper for plural tolerance; matches spelling, not meaning",
                                             "a folded endpoint keyword", True),
    "hand_binding.py:sub:07d45602cf": _fmt("non-letter stripper on a table label; matches formatting, not meaning",
                                           "a table row label (lowercased)", True),
    "hand_binding.py:_RESULT_PAREN": {
        "detects": "the sentence carries a parenthesised result with its confidence interval",
        "trigger": r"\bci\b|confidence|95",
        "text_source": _PROSE, "lowercased": False},
    "hand_binding.py:_LEADING_JOIN": _fmt("strips a leading conjunction (as was / and / whereas / while / but) from an "
                                          "attached clause; matches clause syntax, not a statement",
                                          "one attached clause of a held result sentence"),
    "hand_binding.py:match:43cb536653": {
        "detects": "the declared comparator direction names two arms as 'A vs B' / 'A versus B'",
        "trigger": r"\bvs\b|versus|\bv\b|compared",
        "text_source": "a hand row's declared comparator-direction string", "lowercased": False},
})

# ---- other-lane files, batch 2 (harness/absence.py, gate.py, protocol_compiler.py, registry_multi.py, pipeline.py) --
_ABS_SENT = "one held abstract / full-text sentence as absence reads it (markup stripped, extract._norm)"
_KEYWORD = "an outcome keyword from a topic's keyword list (absence._terms)"
_MANUSCRIPT = "the rendered manuscript text of a review (gate.check_paper_numerals)"
_PARITY = "a review's stored parity reason, or a pooled trial's source string (gate.check_parity_our_k)"
_PAGE = "the rendered review page text (gate surface checks)"
_PROTO = "raw protocol markdown as protocol_compiler reads it"
_REG_HTML = "fetched EU-CTR / ICTRP registry HTML (not held in this repo)"
_QUERY = "a literature search query string (pipeline._query_classification)"

DETECTS.update({
    # ---- harness/absence.py ------------------------------------------------------------------------------------------
    "absence.py:_EFFECT": {
        "detects": "the sentence reports a ratio effect estimate (RR / OR / HR / IRR / relative risk with its value), "
                   "not merely the conjunction 'or' before a number",
        "trigger": r"ratio|\brr\b|\bor\b|\bhr\b|\birr\b|relative risk", "text_source": _ABS_SENT, "lowercased": False},
    "absence.py:_ARMS": {
        "detects": "the sentence reports arm counts (events out of patients, e.g. 12/200, 25 of 400), not a ratio like a "
                   "blood-pressure reading",
        "trigger": r"\d\s*/\s*\d|\bof\s+\d", "text_source": _ABS_SENT, "lowercased": False},
    "absence.py:_TAG": _fmt("XML/HTML tag stripper; matches markup, not meaning", "a held full text (raw JATS/HTML)"),
    "absence.py:_COUNT_WITH_PERCENT": {
        "detects": "the sentence reports an arm count together with its percentage",
        "trigger": r"%|percent", "text_source": _ABS_SENT, "lowercased": False},
    "absence.py:_BARE_OUTCOME_COUNTS": {
        "detects": "the sentence reports per-arm totals of heart-failure hospitalisations ('a total of N and M ...')",
        "trigger": r"total\s+of", "text_source": _ABS_SENT, "lowercased": False},
    "absence.py:_PRIMARY_RESULT": {
        "detects": "the sentence is about THE primary outcome / end point (incl. primary composite / efficacy outcome)",
        "trigger": r"primary", "text_source": _ABS_SENT, "lowercased": False},
    "absence.py:_ESTIMAND_SUFFIX": {
        "detects": "the outcome keyword carries an estimand word or abbreviation (HR, RR, OR, MD, hazard ratio ...) -- "
                   "not the conjunction 'or'",
        "trigger": r"\b(?:rr|or|hr|irr|md|smd)\b|ratio|difference", "text_source": _KEYWORD, "lowercased": False},
    "absence.py:sub:7b4eac99d8": _fmt("whitespace normalisation in _strip_markup; matches formatting, not meaning",
                                      "a held full text"),
    "absence.py:sub:7b4eac99d8#2": _fmt("whitespace normalisation in _norm_space; matches formatting, not meaning",
                                        "a keyword or span"),
    "absence.py:sub:bdbb968f46": _fmt("non-alphanumeric stripper on a keyword; matches formatting, not meaning", _KEYWORD),
    "absence.py:split:ee27e721ca": _fmt("clause splitter after . ; ) ; matches formatting, not meaning",
                                        "the clause before an effect match"),
    # ---- harness/gate.py ---------------------------------------------------------------------------------------------
    "gate.py:sub:b2b1cda05a": _fmt("<svg> block remover; matches markup, not meaning", "rendered manuscript HTML"),
    "gate.py:sub:4755f742a5": _fmt("<pre> block remover; matches markup, not meaning", "rendered manuscript HTML"),
    "gate.py:sub:caf616cd71": _fmt("tag stripper; matches markup, not meaning", "rendered manuscript HTML"),
    "gate.py:sub:2d78918e2a": {
        "detects": "the text carries a commit / registration hash fragment (7+ hex characters)",
        "trigger": r"[0-9a-f]{5,}|sha|commit", "text_source": _MANUSCRIPT, "lowercased": False},
    "gate.py:sub:0441b19e00": {
        "detects": "the numeral is a publication year (not a count or other value)",
        "trigger": r"(?:19|20)\d\d", "text_source": _MANUSCRIPT, "lowercased": False},
    "gate.py:sub:02dd231974": _fmt("the 'k - 1' degrees-of-freedom formula token; matches notation, not a statement",
                                   _MANUSCRIPT),
    "gate.py:findall:17a0a13bd9": _fmt("decimal-number shape; matches number formatting, not meaning", _MANUSCRIPT),
    "gate.py:sub:17a0a13bd9": _fmt("decimal-number shape; matches number formatting, not meaning", _MANUSCRIPT),
    "gate.py:findall:51811c45be": _fmt("'N of M' number shape; matches number formatting, not meaning", _MANUSCRIPT),
    "gate.py:findall:b5d71114cf": _fmt("integer shape; matches number formatting, not meaning", _MANUSCRIPT),
    "gate.py:_PARITY_EXCL_CUE": {
        "detects": "the parity reason says what follows was excluded / declined / not pooled (not a negated exclusion)",
        "trigger": r"exclu|open-label|declin|not pooled|trap|caught", "text_source": _PARITY, "lowercased": False},
    "gate.py:_PARITY_ACRONYM": {
        "detects": "the text names a trial by its acronym",
        "trigger": r"[a-z]{3,}", "text_source": _PARITY, "lowercased": False},
    "gate.py:findall:8cbf399ebf": {
        "detects": "the source names a trial acronym immediately before its identifier (PMID / PMC / NCT)",
        "trigger": r"pmid|pmc|nct", "text_source": _PARITY, "lowercased": False},
    "gate.py:findall:8caff6711a": {
        "detects": "the parity reason names a trial by PMID",
        "trigger": r"\d{7}|pmid", "text_source": _PARITY, "lowercased": False},
    "gate.py:search:f3bc3e60aa": {
        "detects": "the protocol documents a dose-selection rule or a dated amendment (not merely a mention of a dose)",
        "trigger": r"dose|amend|approv|pre-?specif", "text_source": "the whole protocol markdown, lowercased (gate dose-rule check)",
        "lowercased": True},
    "gate.py:search:8aebad504f": {
        "detects": "the page renders a GRADE certainty CATEGORY (high / moderate / low / very low) as the overall certainty",
        "trigger": r"certainty", "text_source": _PAGE, "lowercased": False},
    "gate.py:search:3f33b77a44": {
        "detects": "the page interprets the pool as homogeneous (no between-study heterogeneity)",
        "trigger": r"homogene|heterogene|prediction interval", "text_source": _PAGE, "lowercased": False},
    "gate.py:search:9a92bea520": {
        "detects": "the page row is a primary heterogeneity statistic (prediction interval, between-study tau², I²)",
        "trigger": r"prediction|τ|tau|i²|i2|heterogene", "text_source": _PAGE, "lowercased": False},
    "gate.py:search:159a89219d": _fmt("any-digit test; matches a character class, not meaning", _PAGE),
    "gate.py:search:e1d3371bfb": _fmt("harms-tab panel extractor; matches markup, not meaning", "rendered review page HTML"),
    # ---- harness/protocol_compiler.py --------------------------------------------------------------------------------
    "protocol_compiler.py:search:9a8cc773b0": {
        "detects": "the estimand line names its estimand by a parenthesised code (HR, RR, OR, MD, SMD, IRR)",
        "trigger": r"\((?:hr|rr|or|md|smd|irr)\)|ratio|difference",
        "text_source": "an estimand line of protocol markdown, lowercased", "lowercased": True},
    "protocol_compiler.py:search:6d4338abae": {
        "detects": "the line is the protocol's labelled Estimand field and gives its value",
        "trigger": r"estimand", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:249cd61f88": {
        "detects": "the line is the protocol's labelled Population field and gives its value",
        "trigger": r"population", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:dcfda9493e": {
        "detects": "the protocol admits trials that are double-blind OR placebo-controlled (either suffices)",
        "trigger": r"blind|mask|placebo", "text_source": _PROTO + " (lowercased)", "lowercased": True},
    "protocol_compiler.py:search:cbbabbb69a": {
        "detects": "the protocol requires trials that are both double-blind AND placebo-controlled",
        "trigger": r"blind|mask|placebo", "text_source": _PROTO + " (lowercased)", "lowercased": True},
    "protocol_compiler.py:sub:7b4eac99d8": _fmt("whitespace normalisation in _norm_text; matches formatting, not meaning",
                                                _PROTO),
    "protocol_compiler.py:sub:e3839b281a": _fmt("punctuation-to-space fold in _fold_for_prose; matches formatting, not "
                                                "meaning", _PROTO),
    "protocol_compiler.py:start_re": {
        "detects": "the line is the protocol's PICO Intervention bullet and gives the intervention",
        "trigger": r"\*\*\s*i\b|intervention", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:bullet_re": _fmt("next-bold-bullet boundary; matches markdown structure, not meaning", _PROTO),
    "protocol_compiler.py:finditer:bf8a0d70a0": {
        "detects": "the line is a dated protocol amendment heading",
        "trigger": r"amendment", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:5851103837": {
        "detects": "the amendment states its original identifier scope",
        "trigger": r"identifier scope|original", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:4715c0c46f": {
        "detects": "the amendment states its widened scope",
        "trigger": r"widen", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:7b2c2a25c9": {
        "detects": "the amendment states its reason",
        "trigger": r"reason", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:f3b63c4300": {
        "detects": "the amendment states its pre-specified agent list",
        "trigger": r"pre-?specified", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:ELIGIBILITY_HEADING": {
        "detects": "the heading declares rule-A eligibility on P/I/C/design only",
        "trigger": r"eligib", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:ELIGIBILITY_BULLET": {
        "detects": "the line is a labelled Eligibility clause of the protocol and gives it",
        "trigger": r"eligib", "text_source": _PROTO, "lowercased": False},
    "protocol_compiler.py:search:1e08a0ee7b": _fmt("next-section heading boundary; matches markdown structure, not meaning",
                                                   _PROTO),
    # ---- harness/registry_multi.py -----------------------------------------------------------------------------------
    "registry_multi.py:_EUDRACT_RE": {
        "detects": "the text is (or carries) a EudraCT trial number",
        "trigger": r"\d{4}-\d{5,6}-\d{2}|eudract", "text_source": _REG_HTML, "lowercased": False},
    "registry_multi.py:_ICTRP_ROW_RE": _fmt("ICTRP result-row extractor; matches markup, not meaning", _REG_HTML),
    "registry_multi.py:sub:caf616cd71": _fmt("tag stripper in _clean_text; matches markup, not meaning", _REG_HTML),
    "registry_multi.py:pattern": {
        "detects": "the query uses the spelling variant being swapped (here British 'haemorrhage')",
        "trigger": r"ha?emorrhag", "text_source": "a registry search query string", "lowercased": False},
    "registry_multi.py:findall:01ccab1c69": _fmt("href extractor; matches markup, not meaning", _REG_HTML),
    "registry_multi.py:search:808134fb4a": _fmt("EU-CTR protocol-page field extractor (title between its label and "
                                                "A.3.1); matches page layout, not meaning", _REG_HTML),
    "registry_multi.py:search:c2f5733989": _fmt("EU-CTR EudraCT-number cell extractor; matches markup, not meaning",
                                                _REG_HTML),
    "registry_multi.py:search:59e7e1f76c": _fmt("EU-CTR Full Title cell extractor; matches markup, not meaning", _REG_HTML),
    "registry_multi.py:findall:01ccab1c69#2": _fmt("href extractor; matches markup, not meaning", _REG_HTML),
    "registry_multi.py:search:0e30ce316a": _fmt("ICTRP trial-id span extractor; matches markup, not meaning", _REG_HTML),
    "registry_multi.py:search:d0b77052c3": _fmt("ICTRP Trial2.aspx link extractor; matches markup, not meaning", _REG_HTML),
    # ---- harness/pipeline.py -----------------------------------------------------------------------------------------
    "pipeline.py:_DOI_RE": {
        "detects": "the query carries a DOI",
        "trigger": r"10\.\d|doi", "text_source": _QUERY, "lowercased": False},
    "pipeline.py:_PMID_LITERAL_RE": {
        "detects": "the query carries a PMID literal (not an NCT number's digits, not a [uid] enumeration)",
        "trigger": r"\d{7}|pmid", "text_source": _QUERY, "lowercased": False},
    "pipeline.py:_TITLE_FIELD_RE": {
        "detects": "the query restricts a term to the title field ([ti] / [title])",
        "trigger": r"\[(?:ti|title)", "text_source": _QUERY, "lowercased": False},
    "pipeline.py:_ACRONYM_TOKEN_RE": _fmt("capitalised-token shape; the trial / non-trial decision is made downstream by "
                                          "_trial_acronym_tokens", _QUERY),
    "pipeline.py:_YEAR_RE": {
        "detects": "the query carries a year",
        "trigger": r"(?:19|20)\d\d", "text_source": _QUERY, "lowercased": False},
    "pipeline.py:_JOURNAL_RE": {
        "detects": "the query names a journal",
        "trigger": r"jama|lancet|engl|nejm|bmj|circulation|heart fail|coll cardiol|intern med",
        "text_source": _QUERY, "lowercased": False},
    "pipeline.py:findall:56325787a0": {
        "detects": "the query carries an NCT registry number",
        "trigger": r"nct", "text_source": _QUERY, "lowercased": False},
    "pipeline.py:_NAMED_HELD_PATH": {
        "detects": "the source string names a held cache file (and optionally its PMID)",
        "trigger": r"cache/", "text_source": "a hand row's source string", "lowercased": False},
    "pipeline.py:findall:e902435e30": _fmt("alphanumeric tokeniser; matches formatting, not meaning",
                                           "an endpoint name (lowercased)", True),
    "pipeline.py:search:c2741ecf04": {
        "detects": "the endpoint names myocardial infarction by the abbreviation MI",
        "trigger": r"\bmi\b|myocard|infarct", "text_source": "an endpoint name (lowercased)", "lowercased": True},
})
