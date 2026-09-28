"""Plants for the regex sites of harness/eligibility_chain.py and harness/compat_check.py (keys as regex_layer.inventory
names them).

protocol_criteria() reads the design / comparator sites on _fold(md_text) (lowercase, whitespace collapsed), and the
**Population** / **Timepoint** sites on the raw protocol markdown (re.I). compat_check's adult site reads a lowercased
comparator text; _summarize_follow reads derived follow-up value strings ('56 days', 'during treatment plus 30 days').
"""

SITE_SPECS: dict = {
    'compat_check.py:_ASSESSED': {
        "kind": 'search', "what": '_speech_score: identify an assessment statement about an outcome',
        "plants": {"accept": [('was assessed at 14 days', None)],
                   "refuse": ['followed for 14 days']}},
    'compat_check.py:_EFFECT_WORD': {
        "kind": 'search', "what": '_analysis_statement / _reports_other_estimate: recognize effect labels, with case-sensitive abbreviations',
        "plants": {"accept": [('HR 0.80', None)],
                   "refuse": ['stroke or systemic embolism']}},
    'compat_check.py:_PRIMARY_DEF': {
        "kind": 'search', "what": '_row_is_primary: identify a primary endpoint reference',
        "plants": {"accept": [('primary efficacy outcome', None)],
                   "refuse": ['secondary efficacy outcome']}},
    'compat_check.py:_TRIAL_WIDE': {
        "kind": 'search', "what": '_speech_score: recognize trial-wide follow-up language',
        "plants": {"accept": [('patients were followed for 12 months', None)],
                   "refuse": ['clinical cure at 14 days']}},
    'compat_check.py:findall:1cdf5b6602': {
        "kind": 'search', "what": '_reports_other_estimate: collect complete decimal estimates',
        "plants": {"accept": [('HR 0.80', None)],
                   "refuse": ['version 1.2.3']}},
    'compat_check.py:findall:2c65a104df': {
        "kind": 'search', "what": '_row_terms: capture parenthesized outcome acronyms',
        "plants": {"accept": [('myocardial infarction (MI)', ('MI',))],
                   "refuse": ['myocardial infarction (M)']}},
    'compat_check.py:findall:68f9162183': {
        "kind": 'search', "what": '_defined_phrase: tokenize the lowercased definition head',
        "plants": {"accept": [('new vertebral fracture', None)],
                   "refuse": ['123']}},
    'compat_check.py:findall:68f9162183#2': {
        "kind": 'search', "what": '_defines_this_row: tokenize the lowercased row and outcome for whole-word comparison',
        "plants": {"accept": [('nonvertebral fracture', None)],
                   "refuse": ['123']}},
    'compat_check.py:findall:fa98b9de0a': {
        "kind": 'search', "what": '_row_terms: tokenize the folded outcome name for its head and modifiers',
        "plants": {"accept": [('antibiotic-associated diarrhea', None)],
                   "refuse": ['123']}},
    'compat_check.py:findall:fa98b9de0a#2': {
        "kind": 'search', "what": '_row_terms: tokenize the folded outcome name to derive acronym initials',
        "plants": {"accept": [('major adverse events', None)],
                   "refuse": ['123']}},
    'compat_check.py:findall:fa98b9de0a#3': {
        "kind": 'search', "what": '_speech_score: tokenize folded words preceding the full outcome name',
        "plants": {"accept": [('patients developed', None)],
                   "refuse": ['123']}},
    'compat_check.py:findall:fa98b9de0a#4': {
        "kind": 'search', "what": '_speech_score: tokenize the folded sentence for head and modifier matching',
        "plants": {"accept": [('minor bleeding', None)],
                   "refuse": ['123']}},
    'compat_check.py:finditer:86e524ad3a': {
        "kind": 'search', "what": '_speech_score: match a complete folded outcome name without a hyphenated prefix',
        "bind": {'full': 'major bleeding'},
        "plants": {"accept": [('major bleeding occurred', None)],
                   "refuse": ['non-major bleeding']}},
    'compat_check.py:fullmatch:6687b4a806': {
        "kind": 'search', "what": '_row_terms: recognize numeric or numeric-hyphen tokens to omit from content',
        "plants": {"accept": [('30-day', None)],
                   "refuse": ['day']}},
    'compat_check.py:match:159a89219d': {
        "kind": 'search', "what": '_speech_score: recognize a numeric preceding token at the full-name match',
        "plants": {"accept": [('30', None)],
                   "refuse": ['major']}},
    'compat_check.py:match:159a89219d#2': {
        "kind": 'search', "what": '_speech_score: recognize a numeric preceding token at a head-noun match',
        "plants": {"accept": [('14', None)],
                   "refuse": ['minor']}},
    'compat_check.py:match:633ec5d533': {
        "kind": 'search', "what": '_analysis_statement: identify a following sentence that continues the analysis',
        "plants": {"accept": [('In the primary analysis, HR was 0.8', None)],
                   "refuse": ['Results were similar.']}},
    'compat_check.py:search:85c1af4051': {
        "kind": 'search', "what": '_defined_phrase: capture the definition after its linking verb',
        "plants": {"accept": [('the outcome was new vertebral fracture', ('new vertebral fracture',))],
                   "refuse": ['the outcome occurred']}},
    'compat_check.py:search:85c1af4051#2': {
        "kind": 'search', "what": '_defines_this_row: capture the defined components after the linking verb',
        "plants": {"accept": [('the outcome included death or stroke', ('death or stroke',))],
                   "refuse": ['the outcome occurred']}},
    'compat_check.py:search:93d74681ed': {
        "kind": 'search', "what": '_analysis_statement: distinguish analysis statements from population statements',
        "plants": {"accept": [('primary analyses', None)],
                   "refuse": ['analysiswide population']}},
    'compat_check.py:search:bba6783b13': {
        "kind": 'search', "what": '_row_estimates: capture an effect from a serialized refused-effect dictionary',
        "plants": {"accept": [("{'effect': 0.80}", ('0.80',))],
                   "refuse": ["{'effect_estimate': 0.80}"]}},
    'compat_check.py:split:27175a5a8a': {
        "kind": 'split', "what": '_sentences: split after a period or semicolon before uppercase, parenthesis or digit',
        "plants": {"accept": [('Cure fell. Death rose; (Details)', ['Cure fell.', 'Death rose;', '(Details)'])],
                   "refuse": ['HR 0.80 was reported']}},
    'compat_check.py:split:7af4648997': {
        "kind": 'split', "what": '_defined_phrase: stop the definition head at a bracket or list delimiter',
        "plants": {"accept": [('death, stroke; bleeding: severe (MI)', ['death', ' stroke', ' bleeding', ' severe ', 'MI)'])],
                   "refuse": ['new vertebral fracture']}},
    'compat_check.py:sub:7b4eac99d8#2': {
        "kind": 'search', "what": '_speech_score: formatting helper collapsing whitespace in the folded full name',
        "plants": {"accept": [('major  bleeding', None)],
                   "refuse": ['bleeding']}},
    'compat_check.py:sub:c4b470f596': {
        "kind": 'search', "what": '_row_terms: formatting helper removing parenthetical aliases from the folded name',
        "plants": {"accept": [('infarction (mi)', None)],
                   "refuse": ['infarction']}},
    'compat_check.py:sub:c4b470f596#2': {
        "kind": 'search', "what": '_speech_score: formatting helper removing parenthetical aliases before full-name matching',
        "plants": {"accept": [('infarction (mi)', None)],
                   "refuse": ['infarction']}},
    # ---- harness/eligibility_chain.py ----------------------------------------------------------------------------
    "eligibility_chain.py:_PMID_RE": {
        "kind": "search",
        "what": "_pid: the PMID digits of a trial id / label ('PMID 29146535' or a bare 7-9 digit id)",
        "plants": {"accept": [("PMID 29146535", ("29146535",)), ("29146535", ("29146535",)),
                              ("SUSTAIN-6 (PMID 27633186)", ("27633186",))],
                   "refuse": ["NCT01720446", "n=123456"]}},
    "eligibility_chain.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm: collapse whitespace runs before protocol wording is matched",
        "plants": {"accept": [("double-blind\n  placebo-controlled", None), ("usual\tcare", None)],
                   "refuse": ["double-blind", "placebo-controlled"]}},
    "eligibility_chain.py:search:0278e60920": {
        "kind": "search",
        "what": "protocol_criteria: the protocol admits trials that are double-blind OR placebo-controlled",
        "plants": {"accept": [("include trials that are double-blind or placebo-controlled", None),
                              ("double blind or placebo controlled", None)],
                   "refuse": ["double-blind, placebo-controlled trials", "double-blind and placebo-controlled"]}},
    "eligibility_chain.py:search:e9857d1c69": {
        "kind": "search",
        "what": "protocol_criteria: the protocol requires double-blind AND placebo-controlled (comma / juxtaposed form)",
        "plants": {"accept": [("randomised, double-blind, placebo-controlled trials", None),
                              ("double-blind placebo-controlled", None)],
                   "refuse": ["double-blind or placebo-controlled", "open-label, placebo-controlled"]}},
    "eligibility_chain.py:search:4744a336ec": {
        "kind": "search",
        "what": "protocol_criteria: the protocol requires double-blind AND placebo-controlled ('and' form)",
        "plants": {"accept": [("trials must be double-blind and placebo-controlled", None),
                              ("double blind and placebo controlled", None)],
                   "refuse": ["double-blind or placebo-controlled", "double-blind and open-label"]}},
    "eligibility_chain.py:search:9a073711ca": {
        "kind": "search",
        "what": "protocol_criteria: the value of the protocol's **Population** line (read for the analysis set)",
        "plants": {"accept": [("- **Population** - intention-to-treat as randomised.", ("intention-to-treat as randomised",)),
                              ("**Population**: per-protocol set\n", ("per-protocol set",)),
                              ("- **Population:** adults, intention-to-treat.", None),
                              ("- **Population** — intention-to-treat as randomised.", None)],
                   "refuse": ["Population: adults with heart failure", "**Timepoint** - 28 days."]}},
    "eligibility_chain.py:search:2f21bc603b": {
        "kind": "search",
        "what": "protocol_criteria: the value of the protocol's **Timepoint** line (the follow-up window)",
        "plants": {"accept": [("- **Timepoint** - 28 days.", ("28 days",)),
                              ("**Timepoint**: 1 year for the primary outcome\n", ("1 year for the primary outcome",)),
                              ("- **Timepoint** — longest recurrence follow-up each trial reports.", None)],
                   "refuse": ["Timepoint: 28 days", "**Population** - adults."]}},
    "eligibility_chain.py:search:36706f6be6": {
        "kind": "search", "what": "protocol_criteria: the protocol states a comparator (placebo / usual care / control)",
        "plants": {"accept": [("colchicine versus placebo", None), ("compared with usual care", None),
                              ("colchicine vs no colchicine", None), ("the control arm", None)],
                   "refuse": ["randomised controlled trials of colchicine", "uncontrolled cohort studies"]}},
    # ---- harness/compat_check.py ---------------------------------------------------------------------------------
    "compat_check.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm_ws: collapse whitespace runs in a span",
        "plants": {"accept": [("hazard  ratio\n0.8", None), ("a\tb", None)],
                   "refuse": ["hazard-ratio", "0.8"]}},
    "compat_check.py:findall:6ce8847b51": {
        "kind": "search", "what": "_summarize_follow: the day counts in per-trial follow-up values (for a min-max d range)",
        "plants": {"accept": [("56 days", ("56",)), ("during treatment plus 30 days", ("30",)), ("1 day", ("1",))],
                   "refuse": ["within 8 weeks", "1.5 years"]}},
    "compat_check.py:search:f092a0af63": {
        "kind": "search", "what": "comparator scope: the comparator review is ADULT-ONLY (vs a pool with paediatric trials)",
        "plants": {"accept": [("probiotics for antibiotic-associated diarrhoea in adults", None),
                              ("an adult population", None), ("adult inpatients", None)],
                   "refuse": ["probiotics for antibiotic-associated diarrhoea in children", "into adulthood",
                              "corticosteroids for treating sepsis in children and adults"]}},
}
