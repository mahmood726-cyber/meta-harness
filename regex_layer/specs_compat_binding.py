"""Plants for the OUTCOME-BINDING regex sites of harness/compat_check.py (external audit 26-A / 12-03 / 04-2, 11 Oct).

Each site's plants are the sentences that motivated it -- CAPE COD's taper, Torres's treatment-failure primary, the
melatonin extension phase, FREEDOM's vertebral primary on the hip row -- plus a refuse case for the near miss. Keys are
regex_layer.inventory site names. Wired into INLINE_SPECS by regex_layer/specs.py.
"""

SITE_SPECS: dict = {
    "compat_check.py:_STAGE": {
        "kind": "search", "what": "a sentence about another STAGE of the trial (extension / re-randomisation / run-in)",
        "plants": {"accept": [("placebo completers were re-randomized 1:1 to PRM or placebo", None),
                              ("an open-label extension of 26 weeks", None), ("after a 2-week run-in", None)],
                   "refuse": ["patients were randomized to PRM or placebo", "the primary analysis was intention to treat"]}},
    "compat_check.py:_WORDS": {
        "kind": "search", "what": "_outcome_tokens: a run of lowercase letters (an outcome-name word)",
        "plants": {"accept": [("all-cause mortality", None)], "refuse": ["123 / 456", "( - )"]}},
    "compat_check.py:search:5d5481f295": {
        "kind": "search", "bind": {"a": "vertebral"},
        "what": "_has_token: an outcome word, whole, plural allowed, never inside 'non-' / 'nonvertebral'",
        "plants": {"accept": [("the primary end point was new vertebral fracture", None), ("two vertebrals", None)],
                   "refuse": ["nonvertebral fracture", "non-vertebral fracture", "non vertebral fracture"]}},
    "compat_check.py:search:a882a7a0c4": {
        "kind": "search", "bind": {"acr": "AAD"},
        "what": "_about_outcome: the outcome's own acronym as a whole word",
        "plants": {"accept": [("The primary outcome was the incidence of AAD during 2 weeks", None)],
                   "refuse": ["AADT was used", "a quadrant"]}},
    "compat_check.py:_SENT_SPLIT": {
        "kind": "split", "what": "_sentences: split after . ; ! ? before a capital, parenthesis or bracket",
        "plants": {"accept": [("Death occurred in 25. The primary outcome was death.",
                               ["Death occurred in 25.", "The primary outcome was death."])],
                   "refuse": ["a ratio of 0.80 was seen", "e.g. patients"]}},
    "compat_check.py:_PRIMARY_SENTENCE": {
        "kind": "search", "what": "a sentence that states the trial's primary outcome / end point / measure",
        "plants": {"accept": [("The primary outcome was death at 28 days.", None), ("primary efficacy end point", None)],
                   "refuse": ["secondary outcomes included hospitalisation", "primary care physicians"]}},
    "compat_check.py:_TP_ABX30": {
        "kind": "search", "what": "the probiotic AAD window 'during and up to 30 days after' antibiotics",
        "plants": {"accept": [("diarrhoea during and up to 30 days after antibiotic use", None), ("Abx+30d", None)],
                   "refuse": ["during and up to 2 weeks after", "30 days after discharge"]}},
    "compat_check.py:_TP_PLUS2W": {
        "kind": "search", "what": "the probiotic AAD window 'during or up to 2 weeks after' antibiotic therapy",
        "plants": {"accept": [("occurring during or up to 2 weeks after the antibiotic therapy", None)],
                   "refuse": ["during the 2 weeks of therapy", "2 weeks after randomisation"]}},
    "compat_check.py:_TP_FU_STATED": {
        "kind": "search", "what": "a stated median / mean follow-up with its duration (number, unit)",
        "plants": {"accept": [("The median duration of follow-up was 28.6 months.", ("28.6", "month")),
                              ("During a median follow-up of 5·4 years", ("5·4", "year")),
                              ("The median follow-up was approximately 96 weeks.", ("96", "week"))],
                   "refuse": ["a median of 2.3 years", "follow-up visits at 4 weeks",
                              "a median follow-up of at least 1.5 years had accrued"]}},
    "compat_check.py:_TP_FOLLOWED_FOR": {
        "kind": "search", "what": "'followed (up) for [a median of] N units'",
        "plants": {"accept": [("Patients were followed for a median of 22.6 months.", ("22.6", "month")),
                              ("followed for a mean of 188.2 weeks", ("188.2", "week"))],
                   "refuse": ["followed by tapering for a total of 14 days", "were followed up"]}},
    "compat_check.py:_TP_OVER_MEDIAN": {
        "kind": "search", "what": "'over / during a median (follow-up) of N units'",
        "plants": {"accept": [("Over a median of 2.3 years, the primary outcome occurred", ("2.3", "year")),
                              ("During a median of 2.0 years of follow-up", ("2.0", "year"))],
                   "refuse": ["over 2 years", "a median of 2 years"]}},
    "compat_check.py:_TP_SUPPLEMENTATION": {
        "kind": "search", "what": "'median duration of supplementation was N years'",
        "plants": {"accept": [("The median duration of supplementation was 4.7 years.", ("4.7",))],
                   "refuse": ["supplementation for 4.7 years", "median follow-up was 4.7 years"]}},
    "compat_check.py:_TP_BY_DAY": {
        "kind": "search", "what": "'by / at / on / through / until / to DAY|WEEK|MONTH|YEAR N' (unit, number)",
        "plants": {"accept": [("By day 28, death had occurred", ("day", "28")), ("At week 68, the change", ("week", "68"))],
                   "refuse": ["28 days", "daily for 7 days"]}},
    "compat_check.py:_TP_WITHIN": {
        "kind": "search", "what": "'within N units' (number, unit)",
        "plants": {"accept": [("Death within 90 days after randomization", ("90", "day"))],
                   "refuse": ["within the trial", "90 days"]}},
    "compat_check.py:_TP_N_OR_M": {
        "kind": "search", "what": "'N or M units' as one phrase ('daily for either 4 or 7 days')",
        "plants": {"accept": [("tapering for a total of 8 or 14 days", ("8", "14", "day"))],
                   "refuse": ["8 to 14 days", "14 days"]}},
    "compat_check.py:_TP_NUM_UNIT": {
        "kind": "search", "what": "a bare 'N units' / 'N-unit' time phrase (number, unit); never the SD tail of '34.2±13.7'",
        "plants": {"accept": [("28-day mortality", ("28", "day")), ("for 36 months", ("36", "month")),
                              ("1·5 years", ("1·5", "year"))],
                   "refuse": ["±13.7 months", "day 28 visit", "36 patients"]}},
    "compat_check.py:_TRIAL_FOLLOW_UP": {
        "kind": "search", "what": "an explicit statement of the trial's own follow-up (median/mean follow-up, followed for)",
        "plants": {"accept": [("The median duration of follow-up was 1.8 years", None), ("followed for a mean of 3.5 years", None),
                              ("Over a median of 2.4 years", None)],
                   "refuse": ["3, 6, or 12 months of treatment", "follow-up visits were scheduled"]}},
    "compat_check.py:_AGE": {
        "kind": "search", "what": "the text BEFORE a time phrase ends in an age context ('mean age, ')",
        "plants": {"accept": [("participants (mean age, ", None), ("women aged ", None)],
                   "refuse": ["death had occurred by ", "patients were followed for "]}},
    "compat_check.py:_AFTER_AGE": {
        "kind": "search", "what": "the text AFTER a time phrase starts with 'of age' / 'old'",
        "plants": {"accept": [(" of age or older", None), (" old or older", None)],
                   "refuse": [", death occurred", " after randomization, and in those over 60 of age"]}},
    "compat_check.py:_DISPERSION_END": {
        "kind": "search", "what": "the text before a time phrase ends with ± / +/- / SD / IQR (the phrase is a dispersion)",
        "plants": {"accept": [("duration of exposure was 34.2±", None), ("[SD, 12 years]; IQR ", None)],
                   "refuse": ["duration of exposure was ", "the median was "]}},
    "compat_check.py:_LOS": {
        "kind": "search", "what": "a length-of-stay context",
        "plants": {"accept": [("the median length of hospital stay was 5 days", None), ("5 days in hospital", None)],
                   "refuse": ["hospital mortality at 30 days", "stayed on treatment"]}},
    "compat_check.py:_SCHEDULE": {
        "kind": "search", "what": "a dosing schedule ('every 6 months', 'twice daily', 'q6m')",
        "plants": {"accept": [("every 6 months", None), ("twice daily", None)],
                   "refuse": ["for 36 months", "daily for 7 days"]}},
    "compat_check.py:_EVERY_END": {
        "kind": "search", "what": "the text before a time phrase ends with 'every'",
        "plants": {"accept": [("subcutaneously every ", None)], "refuse": ["subcutaneously for ", "everyone "]}},
    "compat_check.py:_FU_LEAD": {
        "kind": "search", "what": "the text before a time phrase introduces a follow-up ('median follow-up', 'followed for', 'by ')",
        "plants": {"accept": [("the median follow-up of ", None), ("patients were followed for ", None), ("death by ", None)],
                   "refuse": ["tapering for a total of ", "treated for "]}},
    "compat_check.py:_FU_PHRASE_START": {
        "kind": "search", "what": "a time phrase that itself begins with a follow-up preposition (by / within / during / up to)",
        "plants": {"accept": [("within 90 days", None), ("during or up to 2 weeks after", None), ("By day 28", None)],
                   "refuse": ["28 days", "for 14 days"]}},
    "compat_check.py:_CLAUSE_SPLIT": {
        "kind": "split", "what": "split the text before a time phrase at , ; : (the phrase's own clause is the last part)",
        "plants": {"accept": [("hydrocortisone daily, followed by tapering", ["hydrocortisone daily", " followed by tapering"])],
                   "refuse": ["followed by tapering for a total of"]}},
    "compat_check.py:_EXPOSURE": {
        "kind": "search", "what": "a treatment-duration context in the phrase's clause (taper, treated, administered, daily, ...)",
        "plants": {"accept": [("followed by tapering for a total of ", None), ("received the study drug for ", None)],
                   "refuse": ["death had occurred by ", "the median follow-up of "]}},
    "compat_check.py:_FOLLOW": {
        "kind": "search", "what": "an outcome / follow-up context near a time phrase (death, occurred, incidence, end point, ...)",
        "plants": {"accept": [("death had occurred in 25 of 400", None), ("the cumulative incidence at 3 years", None)],
                   "refuse": ["hydrocortisone was given intravenously", "tablets were taken nightly"]}},
    "compat_check.py:_PRIMARY_CLAUSE": {
        "kind": "search", "what": "'primary outcome/end point was [a composite of] X' -- X captured",
        "plants": {"accept": [("The primary end point was new vertebral fracture.", ("new vertebral fracture",)),
                              ("The primary outcome was death at 28 days.", ("death at 28 days",))],
                   "refuse": ["secondary end points included hip fracture", "the primary outcome event rate"]}},
    "compat_check.py:_HEAD_BREAK": {
        "kind": "split", "what": "_primary_head: cut the primary-outcome text at its first parenthesis / definition break",
        "plants": {"accept": [("treatment failure (composite of shock", ["treatment failure ", "composite of shock"])],
                   "refuse": ["new vertebral fracture"]}},
    "compat_check.py:_ANALYSIS_WORD": {
        "kind": "search", "what": "a sentence about an analysis / population / set (a trial-level analysis statement)",
        "plants": {"accept": [("data were analyzed according to the intention-to-treat principle", None),
                              ("the per-protocol population", None)],
                   "refuse": ["both groups were followed up as per protocol visits", "patients were randomized"]}},
    "compat_check.py:_ROW_REPORTS_PRIMARY": {
        "kind": "search", "what": "the row's own span reports the trial's PRIMARY outcome",
        "plants": {"accept": [("a primary outcome event occurred in 197 of 2152", None), ("the primary end point occurred", None)],
                   "refuse": ["In-hospital mortality did not differ", "primary care"]}},
    # --- follow-up comparison (_follow_compatible): asserted window vs the bound per-trial value ---------------------
    "compat_check.py:_TRIAL_DEFINED_WINDOW": {
        "kind": "search", "what": "an asserted follow-up window that is TRIAL-DEFINED (trial end / longest / trial-reported)",
        "plants": {"accept": [("trial end", None), ("trial end / longest randomized follow-up", None),
                              ("trial-reported follow-up", None)],
                   "refuse": ["28 days", "in-hospital / index-admission", "trial ending early"]}},
    "compat_check.py:_DURATION": {
        "kind": "search", "what": "a canonical bare duration 'N unit(s)' and nothing else (number, unit)",
        "plants": {"accept": [("2.6 years", ("2.6", "year")), ("1 week", ("1", "week"))],
                   "refuse": ["within 28 days", "trial end", "2.6 years of follow-up"]}},
    "compat_check.py:_WINDOW_PREFIX": {
        "kind": "search", "what": "a leading window preposition to drop before comparing ('within 28 days' = '28 days')",
        "plants": {"accept": [("within 28 days", None), ("up to 90 days", None)],
                   "refuse": ["28 days within hospital", "withinness"]}},
    "compat_check.py:_WEEK_N": {
        "kind": "search", "what": "a 'unit N' time point to rewrite as 'N units' ('week 68' -> '68 weeks') (unit, number)",
        "plants": {"accept": [("week 68", ("week", "68")), ("at day 28", ("day", "28"))],
                   "refuse": ["68 weeks", "weekly"]}},
    "compat_check.py:_ASSERTED_RANGE": {
        "kind": "search", "what": "an asserted range of durations 'N-M unit(s)' (low, high, unit)",
        "plants": {"accept": [("52-104 weeks", ("52", "104", "week")), ("6 - 12 months", ("6", "12", "month"))],
                   "refuse": ["52 weeks", "6 or 12 months"]}},
}
