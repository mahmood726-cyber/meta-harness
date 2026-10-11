"""R2 labelling specs for compat_check.py's OUTCOME-BINDING regex sites (audit 26-A / 12-03 / 04-2, 11 Oct): what each
site detects in words, and a broad trigger (a superset of its accept plants) used to sample sentences it might miss.
Merged into regex_layer.site_detects.DETECTS."""

_ABSTRACT = "trial abstract / registry sentence (held record) or a served row's source span"
_BEFORE = "the 80 characters of a sentence BEFORE a time phrase (compat_check.time_phrase_kind)"

DETECTS: dict = {
    "compat_check.py:_STAGE": {
        "detects": "the sentence is about a stage of the trial other than the randomised comparison (extension, "
                   "re-randomisation, run-in, open-label / continuation / withdrawal phase)",
        "trigger": r"extension|randomi|run-?in|phase|period", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_WORDS": {
        "detects": None, "why_not_labellable": "tokenises an outcome name into lowercase words; matches letters, not meaning",
        "text_source": "an outcome name, lowercased and vowel-folded", "lowercased": True},
    "compat_check.py:search:5d5481f295": {
        "detects": "the outcome word (bound value) occurs as a whole word, not after 'non'",
        "trigger": r"vertebral", "text_source": _ABSTRACT + " (lowercased, vowel-folded)", "lowercased": True},
    "compat_check.py:search:a882a7a0c4": {
        "detects": "the outcome's acronym (bound value) occurs as a whole word",
        "trigger": r"\bAAD", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_SENT_SPLIT": {
        "detects": None, "why_not_labellable": "sentence segmentation; matches punctuation and capitals, not meaning",
        "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_PRIMARY_SENTENCE": {
        "detects": "the sentence states the trial's primary outcome, end point or measure",
        "trigger": r"primary", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_ABX30": {
        "detects": "an outcome window of 'during and up to 30 days after' the antibiotic course",
        "trigger": r"30\s*d|abx", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_PLUS2W": {
        "detects": "an outcome window of 'during or up to 2 weeks after' the antibiotic course",
        "trigger": r"2\s+weeks", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_FU_STATED": {
        "detects": "a stated median or mean follow-up duration (number and unit)",
        "trigger": r"follow", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_FOLLOWED_FOR": {
        "detects": "participants were followed for a stated duration (number and unit)",
        "trigger": r"followed", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_OVER_MEDIAN": {
        "detects": "a result reported over / during a median or mean duration (number and unit)",
        "trigger": r"median|mean", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_SUPPLEMENTATION": {
        "detects": "a stated median duration of supplementation in years",
        "trigger": r"supplementation", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_BY_DAY": {
        "detects": "a time point written as 'by / at / on day|week|month|year N'",
        "trigger": r"\b(?:day|week|month|year)\s+\d", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_WITHIN": {
        "detects": "a window written as 'within N days|weeks|months|years'",
        "trigger": r"within", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_N_OR_M": {
        "detects": "two alternative durations written as one phrase 'N or M units'",
        "trigger": r"\d\s+or\s+\d", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TP_NUM_UNIT": {
        "detects": "a duration written as a number and a time unit",
        "trigger": r"\d.{0,3}(?:day|week|month|year)", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_TRIAL_FOLLOW_UP": {
        "detects": "the phrase is an explicit statement of the trial's own follow-up",
        "trigger": r"follow|median|mean", "text_source": "a time phrase found in the held record", "lowercased": False},
    "compat_check.py:_AGE": {
        "detects": "the text before a time phrase introduces an age ('mean age', 'aged')",
        "trigger": r"\bage", "text_source": _BEFORE, "lowercased": False},
    "compat_check.py:_AFTER_AGE": {
        "detects": "the text after a time phrase says it is an age ('of age', 'old')",
        "trigger": r"\bage\b|\bold\b", "text_source": "the characters of a sentence AFTER a time phrase", "lowercased": False},
    "compat_check.py:_DISPERSION_END": {
        "detects": "the time phrase is a dispersion (it follows ±, +/-, SD or IQR)",
        "trigger": r"±|\+/-|\bSD\b|\bIQR\b", "text_source": _BEFORE, "lowercased": False},
    "compat_check.py:_LOS": {
        "detects": "the time phrase is a length of hospital / ICU stay",
        "trigger": r"stay|hospital", "text_source": "a time phrase with its surrounding 140 characters", "lowercased": False},
    "compat_check.py:_SCHEDULE": {
        "detects": "the time phrase is a dosing schedule (every N, once / twice daily, qN)",
        "trigger": r"every|daily|twice|once|\bq\d", "text_source": "a time phrase", "lowercased": False},
    "compat_check.py:_EVERY_END": {
        "detects": "the text before a time phrase ends with 'every' (a dosing schedule)",
        "trigger": r"every", "text_source": _BEFORE, "lowercased": False},
    "compat_check.py:_FU_LEAD": {
        "detects": "the text before a time phrase introduces a follow-up window",
        "trigger": r"follow|\bby\b|\bat\b|\bon\b|through|until", "text_source": _BEFORE, "lowercased": False},
    "compat_check.py:_FU_PHRASE_START": {
        "detects": "the time phrase itself begins with a follow-up preposition",
        "trigger": r"\bby\b|within|during|up to|\bat\b", "text_source": "a time phrase", "lowercased": False},
    "compat_check.py:_CLAUSE_SPLIT": {
        "detects": None, "why_not_labellable": "clause segmentation at , ; : -- punctuation, not meaning",
        "text_source": _BEFORE, "lowercased": False},
    "compat_check.py:_EXPOSURE": {
        "detects": "the clause before a time phrase describes treatment (so the phrase is a treatment duration)",
        "trigger": r"taper|treat|therap|administ|receiv|infusion|course|dos|supplement|daily|total|subcutane|oral|intraven|assigned",
        "text_source": _BEFORE, "lowercased": False},
    "compat_check.py:_FOLLOW": {
        "detects": "the text around a time phrase describes an outcome or follow-up (so the phrase is a follow-up window)",
        "trigger": r"follow|death|died|mortal|occur|incidence|event|end ?point|outcome|surviv|assess|measur|cumulative",
        "text_source": "a time phrase with its surrounding 140 characters", "lowercased": False},
    "compat_check.py:_PRIMARY_CLAUSE": {
        "detects": "the clause naming the trial's primary outcome / end point, with the outcome captured",
        "trigger": r"primary", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_HEAD_BREAK": {
        "detects": None, "why_not_labellable": "cuts a captured outcome at its first parenthesis or definition word; a "
                                               "segmentation step, not a meaning",
        "text_source": "the text captured after 'primary outcome was'", "lowercased": False},
    "compat_check.py:_ANALYSIS_WORD": {
        "detects": "the sentence is about an analysis, an analysis population or an analysis set",
        "trigger": r"analy|population|\bset\b", "text_source": _ABSTRACT, "lowercased": False},
    "compat_check.py:_ROW_REPORTS_PRIMARY": {
        "detects": "the served row's own span reports the trial's primary outcome",
        "trigger": r"primary", "text_source": "a served row's source span", "lowercased": False},
    "compat_check.py:_ROW_NOT_PRIMARY": {
        "detects": "the served row's span says the row is not (or is a secondary to) the trial's primary outcome",
        "trigger": r"secondary|not", "text_source": "a served row's source span", "lowercased": False},
    "compat_check.py:_OUTCOME_NOUN": {
        "detects": "the text before an analysis-set statement names an outcome (so the statement is that outcome's)",
        "trigger": r"mortal|death|hospital|admission|stroke|fracture|bleed|hemorrh|infarct|surviv|infect|diarrh|relaps"
                   r"|recurr|remission|pain|exacerb", "text_source": "an abstract sentence, vowel-folded and lowercased, "
                   "up to its analysis-set match", "lowercased": True},
    "compat_check.py:_TRIAL_DEFINED_WINDOW": {
        "detects": "the asserted follow-up window is defined by each trial (trial end / longest / trial-reported)",
        "trigger": r"trial|study|longest", "text_source": "an outcome's asserted follow_up_window (compat_key)",
        "lowercased": True},
    "compat_check.py:_DURATION": {
        "detects": "the value is exactly one duration (number and unit)",
        "trigger": r"\d", "text_source": "a canonical follow-up value", "lowercased": True},
    "compat_check.py:_WINDOW_PREFIX": {
        "detects": "the value opens with a window preposition (within / by / at / up to)",
        "trigger": r"within|\bby\b|\bat\b|through|until|up to", "text_source": "a canonical follow-up value",
        "lowercased": True},
    "compat_check.py:_WEEK_N": {
        "detects": "a time point written unit-first ('week 68')",
        "trigger": r"(?:day|week|month|year)\s+\d", "text_source": "a canonical follow-up value", "lowercased": True},
    "compat_check.py:_ASSERTED_RANGE": {
        "detects": "the asserted window is a range of durations ('52-104 weeks')",
        "trigger": r"\d\s*-\s*\d", "text_source": "an outcome's asserted follow_up_window (compat_key)",
        "lowercased": True},
}
