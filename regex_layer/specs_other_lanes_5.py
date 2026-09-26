"""Plants for the last 71 regex sites (29 files the OTHER lane owns; keys as regex_layer.inventory names them). The regex
layer only READS these files, and a located defect's fix belongs to the owning lane.

Runtime-built patterns are planted with the value their spec names in "bind": verify.py formats the value it is
grounding into each pattern ({int(v)}, {word}, {re.escape(c)}), so a plant states the requirement for one bound value.
"""

_HEX40 = "0123456789abcdef0123456789abcdef01234567"
_HEX64 = _HEX40 + "0123456789abcdef01234567"

SITE_SPECS: dict = {
    # ---- aact.py -----------------------------------------------------------------------------------------------------
    "aact.py:_RECURRENT_TITLE": {
        "kind": "search", "what": "is_recurrent_event_title: the outcome title counts EVENTS (recurrent), not patients",
        "plants": {"accept": [("Number of Hospitalizations for Heart Failure", None), ("Total HF events", None),
                              ("Annualized rate of exacerbations", None), ("Heart failure hospitalizations", None)],
                   "refuse": ["Time to first hospitalization for heart failure", "Change in eGFR"]}},
    "aact.py:_PARTICIPANT_TITLE": {
        "kind": "search", "what": "is_recurrent_event_title: the title counts PARTICIPANTS (binomial-safe)",
        "plants": {"accept": [("Number of Participants With Hospitalization", None), ("Patients with an event", None)],
                   "refuse": ["Number of hospitalizations", "Total events"]}},
    # ---- armcontrast.py / screen_entry.py ----------------------------------------------------------------------------
    "armcontrast.py:_PLACEBO": {
        "kind": "search", "what": "_norm_intv: the arm is a placebo / sham / usual-care control (not an active intervention)",
        "plants": {"accept": [("Placebo for dapagliflozin", None), ("sham procedure", None), ("usual care", None)],
                   "refuse": ["dapagliflozin", "Intensive glucose control"]}},
    "screen_entry.py:_CONTROL": {
        "kind": "search", "what": "the intervention is a control arm (placebo / sham / usual or standard care / control)",
        "plants": {"accept": [("Placebo", None), ("Usual care", None), ("Matching placebo", None)],
                   "refuse": ["Dapagliflozin", "Intensive glucose control"]}},
    # ---- certificate.py ----------------------------------------------------------------------------------------------
    "certificate.py:REF": {
        "kind": "search", "what": "a certificate input reference to a held cache/ or outputs/ file",
        "plants": {"accept": [("cache/colchicine-postop-af/records.json", None), ("outputs/regex_layer/x.txt", None)],
                   "refuse": ["cache/x/records.csv", "docs/x.json"]}},
    # ---- claim.py ----------------------------------------------------------------------------------------------------
    "claim.py:_ASSERT_SIG": {
        "kind": "search", "what": "significance_contradictions: a surface ASSERTS the result is significant / excludes the null",
        "plants": {"accept": [("the reduction was statistically significant", None), ("significantly reduced mortality", None),
                              ("the interval excludes the null", None)],
                   "refuse": ["not statistically significant",
                              "we did not find any statistically significant benefit of omega-3"]}},
    "claim.py:_ASSERT_NULL": {
        "kind": "search", "what": "significance_contradictions: a surface ASSERTS the result is NOT significant / spans the null",
        "plants": {"accept": [("not statistically significant", None), ("the interval crosses the null", None),
                              ("compatible with no effect", None)],
                   "refuse": ["significantly reduced", "excludes the null"]}},
    # ---- comparator_panel.py / comparator_second_pass.py -------------------------------------------------------------
    "comparator_panel.py:FORBIDDEN": {
        "kind": "search", "what": "forbidden_claims: the page claims independent corroboration / replication",
        "plants": {"accept": [("independent corroboration", None), ("independently corroborated", None),
                              ("the result was replicated", None)],
                   "refuse": ["robustness to analytic membership", "the comparator corroborates"]}},
    "comparator_panel.py:sub:7b4eac99d8": {
        "kind": "search", "what": "visible_text: collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "comparator_panel.py:sub:ebbe919eb3": {
        "kind": "search", "what": "visible_text: strip tags", "plants": {"accept": [("<p>x</p>", None)], "refuse": ["a &lt; b", "x"]}},
    "comparator_second_pass.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_compact: collapse whitespace", "plants": {"accept": [("a\nb", None)], "refuse": ["ab", "a-b"]}},
    # ---- ctgov_results.py --------------------------------------------------------------------------------------------
    "ctgov_results.py:search:193897396a": {
        "kind": "search", "what": "a COUNT_OF_PARTICIPANTS row whose (lowercased) title counts EVENTS (unit conflict)",
        "plants": {"accept": [("number of hospitalizations for heart failure", None), ("count of episodes", None),
                              ("number of all-cause hospitalizations (first and recurrent)", None)],
                   "refuse": ["number of participants with hospitalization", "time to first hospitalization"]}},
    "ctgov_results.py:search:e1f2c9fd48": {
        "kind": "search", "what": "the (lowercased) title counts participants / patients",
        "plants": {"accept": [("number of participants with an event", None), ("percentage of patients", None)],
                   "refuse": ["number of events", "proportion of days"]}},
    # ---- design_variance.py ------------------------------------------------------------------------------------------
    "design_variance.py:search:d460b12256": {
        "kind": "search", "what": "_pid: the 7-9 digit PMID in a trial id",
        "plants": {"accept": [("27633186", ("27633186",))], "refuse": ["123456", "NCT01179048"]}},
    "design_variance.py:search:56325787a0": {
        "kind": "search", "what": "_pid: the NCT number in a trial id",
        "plants": {"accept": [("NCT01179048", None), ("nct01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    # ---- endpoint_canonical.py ---------------------------------------------------------------------------------------
    "endpoint_canonical.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_clean: collapse whitespace", "plants": {"accept": [("cv  death", None)], "refuse": ["cvdeath", "cv-death"]}},
    "endpoint_canonical.py:sub:1850cf21f4": {
        "kind": "search", "what": "_generic_component_token: non-alphanumerics become '_'",
        "plants": {"accept": [("CV death", None)], "refuse": ["CVDEATH", "MI"]}},
    # ---- estmeasure.py -----------------------------------------------------------------------------------------------
    "estmeasure.py:_COX": {
        "kind": "search", "what": "the text names a Cox / proportional-hazards model",
        "plants": {"accept": [("Cox proportional hazards model", None), ("proportional-hazards regression", None)],
                   "refuse": ["coxib therapy", "hazard ratio 0.8"]}},
    "estmeasure.py:_RATE_MODEL": {
        "kind": "search", "what": "the text names a rate model (rate ratio, per person-years, recurrent-event analysis)",
        "plants": {"accept": [("rate ratio", None), ("per 100 person-years", None), ("recurrent-event analysis", None),
                              ("Lin-Wei-Yang-Ying model", None)],
                   "refuse": ["response rate", "odds ratio"]}},
    # ---- fda.py ------------------------------------------------------------------------------------------------------
    "fda.py:_NCT_RE": {
        "kind": "search", "what": "an NCT number in an FDA label section",
        "plants": {"accept": [("NCT01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    "fda.py:_SECTION_RE": {
        "kind": "search", "what": "an FDA label section-14 heading and its body (number, body)",
        "plants": {"accept": [("14.1 Heart Failure The trial enrolled adults 14.2 Kidney",
                               ("14.1", "Heart Failure The trial enrolled adults"))],
                   "refuse": ["114 patients", "section 15 results", "14 patients were enrolled"]}},
    "fda.py:search:89dbcde840": {
        "kind": "search", "what": "_trial_name_and_indication: the trial acronym ending the text before its NCT number",
        "plants": {"accept": [("in heart failure DELIVER", ("DELIVER",)), ("patients in EMPEROR-REDUCED", ("EMPEROR-REDUCED",))],
                   "refuse": ["in patients with heart failure", "DELIVER trial"]}},
    # ---- fetch.py ----------------------------------------------------------------------------------------------------
    "fetch.py:_NCT_RE": {
        "kind": "search", "what": "an NCT number",
        "plants": {"accept": [("NCT01179048", None)], "refuse": ["NCT0117904", "NCT-01179048"]}},
    "fetch.py:search:3348df34b8": {
        "kind": "search", "what": "the PMC OA service's ftp:// .tar.gz package link",
        "plants": {"accept": [('href="ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/ab/cd/PMC123.tar.gz"',
                               ("ftp://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_package/ab/cd/PMC123.tar.gz",))],
                   "refuse": ['href="ftp://x/PMC123.pdf"', "ftp://x/a.tar.gz"]}},
    "fetch.py:search:9d3135bb10": {
        "kind": "search", "what": "the PMC OA service's https:// .tar.gz package link",
        "plants": {"accept": [('href="https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC123.tar.gz"',
                               ("https://ftp.ncbi.nlm.nih.gov/pub/pmc/PMC123.tar.gz",))],
                   "refuse": ['href="https://x/PMC123.pdf"', "https://x/a.tar.gz"]}},
    "fetch.py:findall:43a3a2d613": {
        "kind": "search", "what": "_uid_query_result: a PMID enumerated as N[uid]",
        "plants": {"accept": [("27633186[uid]", ("27633186",)), ("27633186 [UID]", ("27633186",))],
                   "refuse": ["27633186[pmid]", "[uid]"]}},
    # ---- fixstate.py -------------------------------------------------------------------------------------------------
    "fixstate.py:SHA1_RE": {
        "kind": "search", "what": "the whole value is a 40-hex commit SHA",
        "plants": {"accept": [(_HEX40, None)], "refuse": [_HEX40[:39], "g" * 40]}},
    "fixstate.py:SHA256_RE": {
        "kind": "search", "what": "the whole value is a 64-hex SHA-256",
        "plants": {"accept": [(_HEX64, None)], "refuse": [_HEX64[:63], "g" * 64]}},
    "fixstate.py:search:3954d27b9b": {
        "kind": "search", "what": "a stored fix-state value uses the refused word 'status'",
        "plants": {"accept": [("status: fixed", None), ("the status is open", None)], "refuse": ["statuses", "FIX_STATUS"]}},
    "fixstate.py:findall:4850140664": {
        "kind": "search", "what": "a harness / scripts / tests .py path named in an evidence command",
        "plants": {"accept": [("python -m pytest tests/test_regex_plants.py -q", None), ("harness/gate.py", None)],
                   "refuse": ["docs/x.py", "harness/gate.md"]}},
    # ---- fulltext.py -------------------------------------------------------------------------------------------------
    "fulltext.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_clean: collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    # ---- gate_scorecard.py -------------------------------------------------------------------------------------------
    "gate_scorecard.py:ISO_UTC_RE": {
        "kind": "search", "what": "the whole value is an ISO UTC timestamp (YYYY-MM-DDTHH:MM:SSZ)",
        "plants": {"accept": [("2026-09-14T00:00:00Z", None)], "refuse": ["2026-09-14", "2026-09-14T00:00:00+00:00"]}},
    "gate_scorecard.py:SHA_RE": {
        "kind": "search", "what": "a 7-40 hex commit SHA in text",
        "plants": {"accept": [("a1b2c3d", None), ("commit " + _HEX40, None)], "refuse": ["abc12", "xyz1234"]}},
    "gate_scorecard.py:fullmatch:09fc75115e": {
        "kind": "search", "what": "_commit_exists: the value is a 7-40 hex SHA",
        "plants": {"accept": [("a1b2c3d", None)], "refuse": ["a1b2c3", "not-a-sha"]}},
    "gate_scorecard.py:sub:282549ad30": {
        "kind": "search", "what": "_legacy_event_id: non-alphanumerics become '-'",
        "plants": {"accept": [("L1 gate", None)], "refuse": ["gate1", "L1"]}},
    # ---- harms.py ----------------------------------------------------------------------------------------------------
    "harms.py:_EFFECT_OR_COMPARISON": {
        "kind": "search", "what": "the harm sentence reports an effect estimate or a numeric between-arm comparison",
        "plants": {"accept": [("hazard ratio 0.80", None),
                              ("12.5% in the drug group vs 8.1% in the placebo group", None),
                              ("12/200 versus 8/200", None)],
                   "refuse": ["hypoglycaemia was rare", "(N = 588) or glipizide 5 mg/day (N = 584) for 52 weeks"]}},
    "harms.py:sub:bc55264a26": {
        "kind": "search", "what": "_terms: non-alphanumerics in a folded keyword become spaces",
        "plants": {"accept": [("hypo-glycemia", None)], "refuse": ["hypoglycemia", "a b"]}},
    "harms.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_terms: collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "harms.py:sub:7b4eac99d8#2": {
        "kind": "search", "what": "compact a harm sentence", "plants": {"accept": [("a\nb", None)], "refuse": ["ab", "a-b"]}},
    # ---- heldout.py --------------------------------------------------------------------------------------------------
    "heldout.py:IDENTIFIER_RE": {
        "kind": "search", "what": "an identifier-shaped token (lowercase words joined by '-')",
        "plants": {"accept": [("empagliflozin-hfpef", None)], "refuse": ["---", "!!"]}},
    # ---- integrity.py ------------------------------------------------------------------------------------------------
    "integrity.py:_PMID_BLOCK": {
        "kind": "search", "what": "one <PubmedArticle> block of a PubMed XML response",
        "plants": {"accept": [("<PubmedArticle><PMID>1</PMID></PubmedArticle>", None)],
                   "refuse": ["<PubmedBookArticle>x</PubmedBookArticle>", "<PubmedArticleSet></PubmedArticleSet>"]}},
    "integrity.py:_PMID": {
        "kind": "search", "what": "the article's PMID element",
        "plants": {"accept": [('<PMID Version="1">27633186</PMID>', ("27633186",))],
                   "refuse": ["<PMID>abc</PMID>", "PMID 27633186"]}},
    "integrity.py:_PUBTYPE": {
        "kind": "search", "what": "a PublicationType element",
        "plants": {"accept": [('<PublicationType UI="D016449">Randomized Controlled Trial</PublicationType>',
                               ("Randomized Controlled Trial",))],
                   "refuse": ["<PublicationTypeList>", "Publication Type: RCT"]}},
    "integrity.py:_REFTYPE": {
        "kind": "search", "what": "a CommentsCorrections RefType (e.g. RetractionIn)",
        "plants": {"accept": [('<CommentsCorrections RefType="RetractionIn">', ("RetractionIn",))],
                   "refuse": ["<CommentsCorrectionsList>", 'RefType="ErratumIn"']}},
    # ---- invalidation.py ---------------------------------------------------------------------------------------------
    "invalidation.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm_term: collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "invalidation.py:sub:e3839b281a": {
        "kind": "search", "what": "_fold_term: non-alphanumerics become spaces",
        "plants": {"accept": [("cv-death", None)], "refuse": ["cvdeath", "mi"]}},
    "invalidation.py:sub:e3839b281a#2": {
        "kind": "search", "what": "_slug_form: non-alphanumerics become '-'",
        "plants": {"accept": [("cv death", None)], "refuse": ["cvdeath", "mi"]}},
    "invalidation.py:sub:e3839b281a#3": {
        "kind": "search", "what": "_compact: drop non-alphanumerics",
        "plants": {"accept": [("cv death", None)], "refuse": ["cvdeath", "mi"]}},
    # ---- known_missing.py --------------------------------------------------------------------------------------------
    "known_missing.py:sub:7b4eac99d8": {
        "kind": "search", "what": "collapse whitespace in a span", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "known_missing.py:search:352ce1b856": {
        "kind": "search", "what": "colchicine-postop-af 36286314: the per-arm analysed n and POAF counts",
        "plants": {"accept": [("The final analysis included 240 study subjects: 118 in the colchicine group and 122 in "
                               "the placebo group. POAF was observed in 20 (16.9%) vs. 33 (27.0%)",
                               ("240", "118", "122", "20", "33"))],
                   "refuse": ["final analysis included 240 patients", "POAF was observed in 20 vs. 33"]}},
    # ---- lexicon.py --------------------------------------------------------------------------------------------------
    "lexicon.py:sub:7b4eac99d8": {
        "kind": "search", "what": "fold: collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "lexicon.py:_MORT_Y": {
        "kind": "search", "what": "the text uses the word mortality (or mortalities)",
        "plants": {"accept": [("all-cause mortality", None), ("mortalities", None)], "refuse": ["immortal time bias", "mortal"]}},
    "lexicon.py:_MORT_D": {
        "kind": "search", "what": "the text uses the word death or deaths",
        "plants": {"accept": [("12 deaths occurred", None), ("death", None)], "refuse": ["patients who died", "deathly"]}},
    "lexicon.py:_CAUSE_RE": {
        "kind": "search", "what": "the text after an outcome term opens a cause clause (due to / from / caused by ...)",
        "plants": {"accept": [(" due to cardiovascular causes", None), ("from any cause", None)],
                   "refuse": ["fatal", "and stroke"]}},
    # ---- limitations.py ----------------------------------------------------------------------------------------------
    "limitations.py:sub:1850cf21f4": {
        "kind": "search", "what": "_slug_piece: non-alphanumerics become '-'",
        "plants": {"accept": [("follow up window", None)], "refuse": ["followup", "x1"]}},
    # ---- parity_relation.py ------------------------------------------------------------------------------------------
    "parity_relation.py:_PATIENT_PCT": {
        "kind": "search", "what": "a (possibly approximate) percentage of patients",
        "plants": {"accept": [("about 45%", ("45",)), ("12.5 %", ("12.5",))], "refuse": ["45 patients", "0.45"]}},
    "parity_relation.py:_RATIO": {
        "kind": "search", "what": "an N/M count ratio",
        "plants": {"accept": [("3/4", ("3", "4"))], "refuse": ["3 of 4", "3-4"]}},
    # ---- propositions.py ---------------------------------------------------------------------------------------------
    "propositions.py:_PMID_RE": {
        "kind": "search", "what": "a PMID (optionally labelled)",
        "plants": {"accept": [("PMID: 27633186", ("27633186",))], "refuse": ["123456", "NCT01179048"]}},
    "propositions.py:_NCT_RE": {
        "kind": "search", "what": "an NCT number",
        "plants": {"accept": [("NCT01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    "propositions.py:search:3d174448cd": {
        "kind": "search", "what": "the parity reason's pooled count ('we pool N')",
        "plants": {"accept": [("we pool 4 trials", ("4",)), ("we pool four trials", None)],
                   "refuse": ["we pooled 4", "we pool the trials"]}},
    "propositions.py:search:3c5b448a8e": {
        "kind": "search", "what": "the caveat says a trial was never searched for / never found",
        "plants": {"accept": [("it was never searched for", None), ("was never found", None)],
                   "refuse": ["searched for and found", "never pooled"]}},
    # ---- prospective.py ----------------------------------------------------------------------------------------------
    "prospective.py:SAFE_NAME_RE": {
        "kind": "search", "what": "the whole name is filesystem-safe",
        "plants": {"accept": [("defect-01.json", None)], "refuse": ["../x", "a b"]}},
    "prospective.py:fullmatch:30c6674876": {
        "kind": "search", "what": "_require_digest: a 40- or 64-hex digest",
        "plants": {"accept": [(_HEX40, None), (_HEX64, None)], "refuse": ["xyz", "0123"]}},
    "prospective.py:match:7085b2958e": {
        "kind": "search", "what": "the A4 section's first numbered item line",
        "plants": {"accept": [("1. First item", None)], "refuse": ["11. item", " 1. item"]}},
    # ---- second_source.py / source_hierarchy.py ----------------------------------------------------------------------
    "second_source.py:sub:7b4eac99d8": {
        "kind": "search", "what": "collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "source_hierarchy.py:_EFFECT_CANDIDATE": {
        "kind": "search", "what": "a ratio effect estimate with its confidence interval (label, estimate, lower, upper)",
        "plants": {"accept": [("hazard ratio, 0.80; 95% CI, 0.70 to 0.90", ("hazard ratio", "0.80", "0.70", "0.90")),
                              ("RR 0.87 (95 percent confidence interval 0.77-0.97)", ("RR", "0.87", "0.77", "0.97")),
                              ("hazard ratio, 0.87; 97.5% CI, 0.73 to 1.04", None)],
                   "refuse": ["the hazard ratio was similar", "or 0.87 (95% CI 0.7-1.0)"]}},
    "source_hierarchy.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_snippet: collapse whitespace", "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    # ---- verify.py (patterns formatted per value; planted for one bound value each) ----------------------------------
    "verify.py:search:a74619243b": {
        "kind": "search", "what": "_digits_in: the value (here 12.4) appears in the source as its own number",
        "bind": {"v": 12.4},
        "plants": {"accept": [("mean 12.4 (SD 3.1)", None)], "refuse": ["112 patients", "mean 12.9 (SD 3.1)"]}},
    "verify.py:search:f57813b775": {
        "kind": "search", "what": "_digits_in: a small count spelled as a word (here 'seven')",
        "bind": {"word": "seven"},
        "plants": {"accept": [("seven of 100 patients", None), ("Seven deaths", None)],
                   "refuse": ["seventeen", "sevenfold"]}},
    "verify.py:search:3a8ce1b5db": {
        "kind": "search", "what": "_rate_pct_in: the implied rate (here 64) appears as a '64%' token",
        "bind": {"c": "64"},
        "plants": {"accept": [("64% of 111", None), ("64 %", None)], "refuse": ["0.64%", "64 patients"]}},
    "verify.py:search:39f6421668": {
        "kind": "search", "what": "_effect_in: the effect value (here 0.88) appears as its own number",
        "bind": {"c": "0.88"},
        "plants": {"accept": [("HR 0.88 (0.78", None)], "refuse": ["0.885", "10.88"]}},
}
