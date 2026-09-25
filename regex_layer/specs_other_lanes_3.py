"""Plants for the regex sites of harness/comparator_truth.py, reason_audit.py, consumer_consistency.py, index.py,
membership.py, cites.py and search_v2.py (keys as regex_layer.inventory names them). All seven files belong to the
OTHER lane: the regex layer only READS them, and a located defect's fix belongs to the owning lane.

Texts are written as each site sees them:
  reason_audit's compiled patterns are re.I on held abstract / full-text sentences (extract._norm) or trial ids;
  consumer_consistency reads held abstracts (phase / cycle / event-count sites), a pooled row's source string (PMID,
    published-effect sites);
  comparator_truth reads a held comparator review's text; index and membership read rendered banner prose, parity
    reasons and trial ids; cites and search_v2 read DOIs / PMIDs / titles / queries.
membership's per-identity word match is an f-string over re.escape(str(identity)); it is planted with identity
'SELECT' ("bind").
"""

SITE_SPECS: dict = {
    # ---- harness/cites.py --------------------------------------------------------------------------------------------
    "cites.py:_PMID_RE": {
        "kind": "search", "what": "_normalise_pmid: the whole value is a PMID (digits only)",
        "plants": {"accept": [("27633186", None), ("1", None)], "refuse": ["PMID 27633186", "27633186a"]}},
    "cites.py:_DOI_RE": {
        "kind": "search", "what": "_reference_doi: a DOI inside an unstructured reference",
        "plants": {"accept": [("10.1056/NEJMoa1603827", None), ("doi:10.1016/S0140-6736(19)32345-0.", None)],
                   "refuse": ["10.5 mg", "10.1/x"]}},
    "cites.py:sub:dd5e50e9d6": {
        "kind": "search", "what": "_normalise_doi: a doi.org resolver prefix",
        "plants": {"accept": [("https://doi.org/10.1056/x", None), ("http://dx.doi.org/10.1/x", None)],
                   "refuse": ["doi.org/10.1/x", "https://pubmed.ncbi.nlm.nih.gov/1"]}},
    "cites.py:sub:4e68c4d713": {
        "kind": "search", "what": "_normalise_doi: a leading 'doi:' label",
        "plants": {"accept": [("doi: 10.1/x", None), ("DOI:10.1/x", None)], "refuse": ["10.1/x", "see doi:10.1/x"]}},
    "cites.py:sub:e3839b281a": {
        "kind": "search", "what": "_normalise_title: non-alphanumeric runs become spaces",
        "plants": {"accept": [("a, b", None), ("x-y", None)], "refuse": ["ab", "a1"]}},
    "cites.py:split:d0a94246b5": {
        "kind": "split", "what": "_title_query_variants: the title's first sentence (split at '. ')",
        "plants": {"accept": [("Colchicine in pericarditis. A trial", ["Colchicine in pericarditis", "A trial"])],
                   "refuse": ["N.Engl", "Colchicine in pericarditis."]}},
    # ---- harness/comparator_truth.py ---------------------------------------------------------------------------------
    "comparator_truth.py:_WS": {
        "kind": "search", "what": "_flat: collapse whitespace runs",
        "plants": {"accept": [("a  b", None), ("a\nb", None)], "refuse": ["ab", "a-b"]}},
    "comparator_truth.py:_N_LVEF40": {
        "kind": "search", "what": "the comparator's n for its LVEF <= 40% subgroup",
        "plants": {"accept": [("LVEF ≤40% (n = 1,234)", ("1,234",)), ("LVEF <= 40%, n = 812", ("812",))],
                   "refuse": ["LVEF ≤35% (n = 812)", "LVEF >40% n = 812"]}},
    "comparator_truth.py:_ONLY_TWO": {
        "kind": "search", "what": "the comparator states only two of its four citations reported the renal composite",
        "plants": {"accept": [("Only two of the four citations reported renal composite outcomes", None)],
                   "refuse": ["two of four citations reported", "Only three of the four citations reported renal composite"]}},
    "comparator_truth.py:search:3be5b26f67": {
        "kind": "search", "what": "_as_int: the first number in a value string",
        "plants": {"accept": [("n = 1,234", None)], "refuse": ["none", "n/a"]}},
    "comparator_truth.py:sub:0b2060d20b": {
        "kind": "search", "what": "_as_int: drop non-digits from the number",
        "plants": {"accept": [("1,234", None)], "refuse": ["1234", "7"]}},
    "comparator_truth.py:split:a4601f97a8": {
        "kind": "split", "what": "_sentences: split at a sentence end before a capital or '('",
        "plants": {"accept": [("MRAs reduce death. The trials", ["MRAs reduce death.", "The trials"])],
                   "refuse": ["i.e. in RALES", "Fig. 2 shows"]}},
    "comparator_truth.py:search:9378a79674": {
        "kind": "search", "what": "agent_scope_from_text: the comparator names MRAs (a class)",
        "plants": {"accept": [("MRAs reduced mortality", None), ("(MRAs)", None)], "refuse": ["MRA use", "EMRAs"]}},
    "comparator_truth.py:finditer:82a1fa9ce1": {
        "kind": "search", "what": "completeness_vs_known_eligible: the comparator mentions EPHESUS",
        "plants": {"accept": [("EPHESUS", None), ("the Ephesus trial", None)], "refuse": ["Ephesians", "RALES"]}},
    "comparator_truth.py:search:0c19981303": {
        "kind": "search", "what": "completeness_vs_known_eligible: the EPHESUS span places it after myocardial infarction",
        "plants": {"accept": [("post-MI heart failure", None), ("after myocardial infarction", None), ("postMI", None)],
                   "refuse": ["heart failure with reduced ejection fraction", "mild symptoms"]}},
    # ---- harness/consumer_consistency.py -----------------------------------------------------------------------------
    "consumer_consistency.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_clip: collapse whitespace runs",
        "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "consumer_consistency.py:search:6270a59386": {
        "kind": "search", "what": "the abstract describes a phase 2 trial (refused for a design reason)",
        "plants": {"accept": [("a phase 2 trial", None), ("Phase II study", None), ("phase 2b", None)],
                   "refuse": ["phase 3 trial", "phase III study"]}},
    "consumer_consistency.py:search:ce09041473": {
        "kind": "search", "what": "_cycle_level_candidate: ovulation reported per ovulatory cycle (cycle-level unit)",
        "plants": {"accept": [("ovulation rate was 62.3% of the 1216 ovulatory cycles in the letrozole group", None)],
                   "refuse": ["ovulation occurred in 62.3% of women", "62.3% of the 1216 ovulatory cycles in the group"]}},
    "consumer_consistency.py:search:6ecd1e4cdd": {
        "kind": "search", "what": "_event_count_candidate: per-arm assigned denominators ('N were assigned to X ... M were assigned to placebo')",
        "plants": {"accept": [("2366 were assigned to colchicine and 2379 were assigned to placebo",
                               ("2366", "colchicine", "2379", "placebo")),
                              ("2366 patients were assigned to colchicine and 2379 patients were assigned to placebo", None)],
                   "refuse": ["2366 were assigned to colchicine", "2366 were assigned to placebo and 2379 to colchicine"]}},
    "consumer_consistency.py:search:5994968a29": {
        "kind": "search", "what": "_event_count_candidate: per-arm assigned denominators ('N were assigned to the X ..., and M to the placebo')",
        "plants": {"accept": [("2366 were assigned to the colchicine group and 2379 to the placebo group",
                               ("2366", "colchicine", "2379", "placebo")),
                              ("2366 were assigned to colchicine and 2379 to placebo", None)],
                   "refuse": ["2366 were assigned to the colchicine group", "2366 to the placebo group"]}},
    "consumer_consistency.py:search:ce14d051b1": {
        "kind": "search", "what": "_event_count_candidate: per-arm event counts compared across arms",
        "plants": {"accept": [("12 events in the colchicine group compared with 25 events in the placebo group",
                               ("12", "colchicine", "25", "placebo"))],
                   "refuse": ["12 events in the colchicine group", "12 events with placebo versus 25 events with colchicine"]}},
    "consumer_consistency.py:search:ee18f71fc1": {
        "kind": "search", "what": "_effect_source_id: the PMID in a row's source string",
        "plants": {"accept": [("PMID 27633186 abstract", ("27633186",)), ("PMID27633186", ("27633186",))],
                   "refuse": ["NCT01179048", "PMID 123"]}},
    "consumer_consistency.py:_PUBLISHED_EFFECT_IN_SOURCE": {
        "kind": "search", "what": "annotate_reconstruction_with_published_effect: the source span reports a published effect estimate with its CI",
        "plants": {"accept": [("hazard ratio, 0.87; 95% CI, 0.78 to 0.97", None),
                              ("relative risk 0.8 (95 percent confidence interval 0.7 to 0.9)", None),
                              ("16 of 45 patients (35.6%) in the placebo group (OR 0.34, 95% CI 0.125 to 0.944)", None)],
                   "refuse": ["the hazard ratio was similar", "risk difference 2% (95% CI 1 to 3)"]}},
    # ---- harness/index.py --------------------------------------------------------------------------------------------
    "index.py:search:5c88386f0c": {
        "kind": "search", "what": "the decoupling capture's 'RESULT: N of M topics' line",
        "plants": {"accept": [("RESULT: 12 of 14 topics", ("12", "14"))],
                   "refuse": ["RESULT: 12/14 topics", "result: 12 of 14 topics"]}},
    "index.py:sub:caf616cd71": {
        "kind": "search", "what": "_validate_prose_numbers: strip tags from the banners",
        "plants": {"accept": [("<p>12 pages</p>", None)], "refuse": ["a &lt; b", "plain"]}},
    "index.py:sub:f2d4b3ad26": {
        "kind": "search", "what": "_validate_prose_numbers: drop ISO measurement dates",
        "plants": {"accept": [("measured 2026-09-15", None)], "refuse": ["2026-9-15", "12026-09-15"]}},
    "index.py:sub:0441b19e00": {
        "kind": "search", "what": "_validate_prose_numbers: drop publication years",
        "plants": {"accept": [("since 2019", None), ("(1998)", None)], "refuse": ["12.5", "205"]}},
    "index.py:findall:17a0a13bd9": {
        "kind": "search", "what": "_validate_prose_numbers: decimals",
        "plants": {"accept": [("HR 0.87", None)], "refuse": ["12", "version three"]}},
    "index.py:sub:17a0a13bd9": {
        "kind": "search", "what": "_validate_prose_numbers: blank decimals before the integer pass",
        "plants": {"accept": [("0.87", None)], "refuse": ["87", "zero"]}},
    "index.py:findall:51811c45be": {
        "kind": "search", "what": "_validate_prose_numbers: 'N of M' pairs",
        "plants": {"accept": [("12 of 14", ("12", "14"))], "refuse": ["12 out of 14", "one of 14"]}},
    "index.py:findall:b5d71114cf": {
        "kind": "search", "what": "_validate_prose_numbers: integers",
        "plants": {"accept": [("37 pages", None)], "refuse": ["no digits", "pages"]}},
    # ---- harness/membership.py ---------------------------------------------------------------------------------------
    "membership.py:_NCT_RE": {
        "kind": "search", "what": "canonical ids: an NCT number",
        "plants": {"accept": [("NCT01179048", None), ("nct01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    "membership.py:_PMID_RE": {
        "kind": "search", "what": "canonical ids: a labelled PMID",
        "plants": {"accept": [("PMID: 27633186", ("27633186",)), ("pmid 27633186", ("27633186",))],
                   "refuse": ["NCT01179048", "PMC6135590"]}},
    "membership.py:_NUMERIC_PMID_RE": {
        "kind": "search", "what": "canonical ids: the whole id is numeric (a bare PMID)",
        "plants": {"accept": [("27633186", None)], "refuse": ["PMID 27633186", " 27633186"]}},
    "membership.py:_NEGATIVE_PARITY_RE": {
        "kind": "search", "what": "parity_conflicts: the parity sentence says a trial is excluded / refused / not pooled",
        "plants": {"accept": [("OMEMI is declared-absent", None), ("excluded (open-label)", None), ("two gap trials", None)],
                   "refuse": ["pooled as randomised", "SELECT was not excluded"]}},
    "membership.py:findall:693f9b4595": {
        "kind": "search", "what": "_record_trial_key: the 7-9 digit PMID in a record id",
        "plants": {"accept": [("27633186", None), ("PMID 27633186", None)], "refuse": ["NCT01179048", "123456"]}},
    "membership.py:findall:ac0fc4ac8d": {
        "kind": "search", "what": "_trial_identities: a trial acronym before '(PMID' / '(NCT' in the source",
        "plants": {"accept": [("OMEMI (NCT01841944)", ("OMEMI",)), ("SU.FOL.OM3 (PMID 20929777)", ("SU.FOL.OM3",))],
                   "refuse": ["the trial (PMID 1)", "OMEMI [NCT1]"]}},
    "membership.py:split:373165b5f8": {
        "kind": "split", "what": "parity_conflicts: split the parity reason into sentences",
        "plants": {"accept": [("OMEMI excluded. VITAL pooled", ["OMEMI excluded.", "VITAL pooled"])],
                   "refuse": ["OMEMI excluded.VITAL", "no sentence end"]}},
    "membership.py:search:3d23717e76": {
        "kind": "search", "what": "parity_conflicts: the sentence names this trial identity as a word (compiled with identity='SELECT')",
        "bind": {"identity": "SELECT"},
        "plants": {"accept": [("SELECT was excluded", None), ("select", None)], "refuse": ["SELECTED", "PRESELECT"]}},
    # ---- harness/reason_audit.py -------------------------------------------------------------------------------------
    "reason_audit.py:_NCT_OR_PMID": {
        "kind": "search", "what": "canonical_trial_id: the trial's NCT number or PMID",
        "plants": {"accept": [("NCT01179048", ("NCT01179048",)), ("PMID 27633186", ("27633186",))],
                   "refuse": ["12345", "ChiCTR-IOR-17012345"]}},
    "reason_audit.py:_COUNT_WITH_PERCENT": {
        "kind": "search", "what": "_has_numeric_outcome: an arm count written with its percentage",
        "plants": {"accept": [("1,234 patients (12.5%)", None), ("12.5% (25/200)", None), ("37 (18.5%)", None)],
                   "refuse": ["18.5% of patients", "HR 0.80 (95% CI 0.70-0.90)"]}},
    "reason_audit.py:_EXPLICIT_FRACTION": {
        "kind": "search", "what": "_has_numeric_outcome / _normalised_value: an explicit events/total fraction",
        "plants": {"accept": [("25/400", None), ("25 of 400", None)],
                   "refuse": ["25 patients", "ambulatory BP ≥125/75 mmHg with placebo"]}},
    "reason_audit.py:_TWO_ARM_EVENT_COUNTS": {
        "kind": "search", "what": "_has_numeric_outcome: per-arm event counts compared across arms",
        "plants": {"accept": [("12 events with colchicine versus 25 events with placebo", None)],
                   "refuse": ["12 events with colchicine", "12 events versus placebo"]}},
    "reason_audit.py:_GROUP_WORD": {
        "kind": "search", "what": "_has_numeric_outcome: the sentence names a trial arm",
        "plants": {"accept": [("placebo", None), ("usual care", None)], "refuse": ["a controlled trial", "the patients"]}},
    "reason_audit.py:_ASSIGNED": {
        "kind": "search", "what": "_assignment_denominators: N (participants) assigned to an arm (count, arm label)",
        "plants": {"accept": [("2366 were randomly assigned to the colchicine group", ("2366", "colchicine ")),
                              ("4745 patients were randomly assigned to colchicine, 4750 to placebo", None)],
                   "refuse": ["2366 were enrolled", "assigned to colchicine"]}},
    "reason_audit.py:_EVENT_IN_GROUP": {
        "kind": "search", "what": "_event_counts: N events in an arm (count, arm label)",
        "plants": {"accept": [("12 events in the colchicine group", ("12", "colchicine "))],
                   "refuse": ["12 events occurred", "events in the colchicine group"]}},
    "reason_audit.py:sub:7b4eac99d8": {
        "kind": "search", "what": "norm_space: collapse whitespace runs",
        "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    # ---- harness/search_v2.py ----------------------------------------------------------------------------------------
    "search_v2.py:_NCT_RE": {
        "kind": "search", "what": "an NCT number in a record / abstract",
        "plants": {"accept": [("NCT01179048", None), ("nct01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    "search_v2.py:_ISRCTN_RE": {
        "kind": "search", "what": "_normalise_isrctn: the whole value is an ISRCTN number",
        "plants": {"accept": [("ISRCTN12345678", None), ("isrctn12345678", None)],
                   "refuse": ["ISRCTN1234567", "see ISRCTN12345678"]}},
    "search_v2.py:_PMID_RE": {
        "kind": "search", "what": "_normalise_pmid: the whole value is a PMID (digits only)",
        "plants": {"accept": [("27633186", None)], "refuse": ["PMID 27633186", "2763318a"]}},
    "search_v2.py:_DOI_RE": {
        "kind": "search", "what": "a DOI in a record",
        "plants": {"accept": [("10.1056/NEJMoa1603827", None)], "refuse": ["10.5 mg", "10.1/x"]}},
    "search_v2.py:_WORD_SPLIT_RE": {
        "kind": "search", "what": "vocabulary tokens: whitespace between words",
        "plants": {"accept": [("a b", None)], "refuse": ["ab", "a-b"]}},
    "search_v2.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_clean_xml_text: collapse whitespace runs",
        "plants": {"accept": [("a\n b", None)], "refuse": ["ab", "a-b"]}},
    "search_v2.py:search:b19728903c": {
        "kind": "search", "what": "_first_year: the first year in a record's date fields",
        "plants": {"accept": [("2019", ("20",)), ("Lancet 1998;352", ("19",))], "refuse": ["2105", "12019"]}},
}
