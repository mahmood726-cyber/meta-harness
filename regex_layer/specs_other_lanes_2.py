"""Plants for the regex sites of harness/gate.py, protocol_compiler.py, absence.py, registry_multi.py and pipeline.py
(keys as regex_layer.inventory names them). All five files belong to the OTHER lane: the regex layer only READS them,
and a located defect's fix belongs to the owning lane.

Texts are written as each site sees them:
  absence's compiled patterns are re.I on held abstract / full-text sentences (after extract._norm; markup stripped);
  gate's manuscript-numeral sites read rendered manuscript HTML/text, its parity sites a stored parity reason, its
    dose-rule site the LOWERCASED protocol, its surface sites rendered page text;
  protocol_compiler reads raw protocol markdown (re.I where the harness says so; the masking sites read it lowercased,
    _canon_estimand reads an estimand line lowercased);
  registry_multi reads fetched EU-CTR / ICTRP HTML and a search-query string; its spelling-variant compile is built
    per replacement pair at runtime and is planted with the pair named in "bind" (old = 'haemorrhage');
  pipeline reads search-query strings and source-reference strings.
"""

SITE_SPECS: dict = {
    # ---- harness/absence.py ------------------------------------------------------------------------------------------
    "absence.py:_EFFECT": {
        "kind": "search", "what": "_outcome_number_present: the outcome's sentences carry a ratio effect estimate (RR/OR/HR/IRR + a decimal)",
        "plants": {"accept": [("hazard ratio, 0.80; 95% CI, 0.70 to 0.91", None), ("HR 0.74 (0.65 to 0.85)", None),
                              ("the odds ratio was 1.52", None)],
                   "refuse": ["the hazard ratio was similar across subgroups",
                              "hospitalized for atrial fibrillation or flutter (3.1% vs. 2.1%, P=0.004)"]}},
    "absence.py:_ARMS": {
        "kind": "search", "what": "_outcome_number_present: the outcome's sentences carry arm counts (events/total, N of M)",
        "plants": {"accept": [("12/200 in the colchicine group", None), ("25 of 400 patients", None),
                              ("three of 120 patients", None)],
                   "refuse": ["the 3 of us", "a PA ≥ 130/80 mm Hg at baseline"]}},
    "markup.py:MARKUP": {
        "kind": "search", "what": "strip_markup: a MARKUP token (tag, comment, CDATA, PI, DOCTYPE) -- never a literal '<' in scientific text",
        "plants": {"accept": [("<p>x</p>", None), ("<sup>2</sup>", None), ('<xref rid="r1" ref-type="bibr">', None),
                              ("<!-- note -->", None), ("<br/>", None)],
                   "refuse": ["(P<0.001), HR 0.82 (95% CI 0.70 to 0.96; P>0.2)", "age < 65", "p<.05", "<=10 mg", "p &lt; 0.05"]}},
    "absence.py:_COUNT_WITH_PERCENT": {
        "kind": "search", "what": "_count_candidates: an arm count written with its percentage (N/M (x%), x% (N/M), N patients (x%))",
        "plants": {"accept": [("12/200 (6.0%)", None), ("6.0% (12/200)", None), ("37 patients (18.5%)", None),
                              ("452 patients (35.2 percent)", None)],
                   "refuse": ["18.5% of patients", "HR 0.80 (95% CI 0.70-0.90)"]}},
    "absence.py:_BARE_OUTCOME_COUNTS": {
        "kind": "search", "what": "_count_candidates: bare per-arm totals of heart-failure hospitalisations ('a total of N and M ...')",
        "plants": {"accept": [("a total of 245 and 311 hospitalizations for heart failure", None),
                              ("total of 12 and 20 first and recurrent hospitalisations for heart failure", None)],
                   "refuse": ["a total of 245 patients", "245 and 311 deaths"]}},
    "absence.py:_PRIMARY_RESULT": {
        "kind": "search", "what": "_candidate_sentences: the sentence reports THE primary outcome / end point",
        "plants": {"accept": [("the primary outcome occurred in 12%", None), ("primary end points", None),
                              ("A primary composite outcome event occurred in 839 of 7356 patients", None)],
                   "refuse": ["primary care physicians", "a secondary outcome occurred"]}},
    "absence.py:_ESTIMAND_SUFFIX": {
        "kind": "search", "what": "_terms: an estimand word or abbreviation to strip from an outcome keyword ('death (HR)')",
        "plants": {"accept": [("all-cause death (HR)", None), ("hazard ratio for death", None)],
                   "refuse": ["death", "CV death or HHF"]}},
    "absence.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_strip_markup: collapse whitespace runs",
        "plants": {"accept": [("death  fell", None), ("a\nb", None)], "refuse": ["death-fell", "HR"]}},
    "absence.py:sub:7b4eac99d8#2": {
        "kind": "search", "what": "_norm_space: collapse whitespace runs",
        "plants": {"accept": [("cv\tdeath", None), ("a  b", None)], "refuse": ["cvdeath", "mace"]}},
    "absence.py:sub:bdbb968f46": {
        "kind": "search", "what": "_terms: non-alphanumerics in a keyword become spaces",
        "plants": {"accept": [("cv-death", None), ("death (hr)", None)], "refuse": ["cv death", "death"]}},
    "absence.py:split:ee27e721ca": {
        "kind": "split", "what": "_effect_candidates: split the clause before an effect at . ; or ) followed by whitespace",
        "plants": {"accept": [("death fell. stroke rose", ["death fell.", "stroke rose"]),
                              ("(HR 0.8) and death", ["(HR 0.8)", "and death"])],
                   "refuse": ["death fell.stroke rose", "HR 0.8, stroke"]}},
    # ---- harness/gate.py ---------------------------------------------------------------------------------------------
    "gate.py:sub:b2b1cda05a": {
        "kind": "search", "what": "check_paper_numerals: drop <svg> blocks (layout coordinates, not claims)",
        "plants": {"accept": [('<svg width="10"><g/></svg>', None), ("<svg>\n12\n</svg>", None)],
                   "refuse": ["<svgx>1</svgx>", "<g>1</g>"]}},
    "gate.py:sub:4755f742a5": {
        "kind": "search", "what": "check_paper_numerals: drop the <pre> one-command block",
        "plants": {"accept": [("<pre>make all</pre>", None), ('<pre class="c">\nx\n</pre>', None)],
                   "refuse": ["<p>x</p>", "<prefix>x</prefix>"]}},
    "gate.py:sub:caf616cd71": {
        "kind": "search", "what": "check_paper_numerals: strip tags from the rendered manuscript",
        "plants": {"accept": [("<td>1</td>", None), ('<span class="k">k</span>', None)],
                   "refuse": ["p &lt; 0.05", "plain prose"]}},
    "gate.py:sub:2d78918e2a": {
        "kind": "search", "what": "check_paper_numerals: drop a registration SHA fragment (7+ hex chars)",
        "plants": {"accept": [("commit a1b2c3d", None), ("sha 0123abcdef", None)],
                   "refuse": ["HR 0.87", "abc12", "a1b2c3"]}},
    "gate.py:sub:0441b19e00": {
        "kind": "search", "what": "check_paper_numerals: drop publication YEARS (a count is not a year)",
        "plants": {"accept": [("published in 2019", None), ("(1998)", None)],
                   "refuse": ["12.5", "2047 patients were randomized"]}},
    "gate.py:sub:02dd231974": {
        "kind": "search", "what": "check_paper_numerals: drop the 'k - 1' df formula",
        "plants": {"accept": [("k &minus; 1 df", None), ("k&minus;1", None)], "refuse": ["k - 1", "k &minus; 12"]}},
    "gate.py:findall:17a0a13bd9": {
        "kind": "search", "what": "check_paper_numerals: every decimal numeral in the manuscript prose",
        "plants": {"accept": [("HR 0.87", None), ("1.5", None)], "refuse": ["12", "version three"]}},
    "gate.py:sub:17a0a13bd9": {
        "kind": "search", "what": "check_paper_numerals: blank decimals before the integer pass",
        "plants": {"accept": [("0.87 (0.78)", None)], "refuse": ["87", "zero point eight"]}},
    "gate.py:findall:51811c45be": {
        "kind": "search", "what": "check_paper_numerals: 'N of M' integer pairs",
        "plants": {"accept": [("12 of 100", ("12", "100"))], "refuse": ["12 out of 100", "one of 100"]}},
    "gate.py:findall:b5d71114cf": {
        "kind": "search", "what": "check_paper_numerals: every integer in the prose",
        "plants": {"accept": [("k = 12", None), ("7", None)], "refuse": ["no digits", "k"]}},
    "gate.py:_PARITY_EXCL_CUE": {
        "kind": "search", "what": "check_parity_our_k: the parity reason names what follows as EXCLUDED / not pooled",
        "plants": {"accept": [("OMEMI was excluded (open-label)", None), ("design-excluded: OMEMI", None),
                              ("not pooled: VITAL", None)],
                   "refuse": ["pooled as randomised", "all trials included", "SELECT was not excluded"]}},
    "gate.py:_PARITY_ACRONYM": {
        "kind": "search", "what": "check_parity_our_k: a trial acronym named in the parity reason",
        "plants": {"accept": [("SU.FOL.OM3", ("SU.FOL.OM3",)), ("OMEGA-REMODEL", ("OMEGA-REMODEL",)),
                              ("VITAL", ("VITAL",))],
                   "refuse": ["the trial", "HR 0.8"]}},
    "gate.py:findall:8cbf399ebf": {
        "kind": "search", "what": "check_parity_our_k: a trial acronym in trial-name position (before '(PMID/PMC/NCT')",
        "plants": {"accept": [("SU.FOL.OM3 (PMID 20929777)", ("SU.FOL.OM3",)), ("OMEMI (NCT01841944)", ("OMEMI",))],
                   "refuse": ["the trial (PMID 1)", "OMEMI [PMID 1]"]}},
    "gate.py:findall:8caff6711a": {
        "kind": "search", "what": "check_parity_our_k: a PMID (7-8 digits) named in the parity reason",
        "plants": {"accept": [("PMID 20929777", None), ("2092977", None)],
                   "refuse": ["NCT01841944", "123456", "123456789"]}},
    "gate.py:search:f3bc3e60aa": {
        "kind": "search", "what": "check_dose_prespecified: the (lowercased) protocol documents a dose-selection rule or amendment",
        "plants": {"accept": [("the highest licensed dose arm is pooled", None), ("## amendment 2026-09-01", None)],
                   "refuse": ["colchicine versus placebo", "patients on low-dose aspirin were eligible"]}},
    "gate.py:search:8aebad504f": {
        "kind": "search", "what": "certainty_surfaces_agree: a PROVISIONAL certainty rendered as a GRADE category",
        "plants": {"accept": [("GRADE certainty was moderate", None), ("Overall certainty (provisional): low", None),
                              ("overall certainty: very low", None)],
                   "refuse": ["GRADE certainty: provisional", "certainty was moderate"]}},
    "gate.py:search:3f33b77a44": {
        "kind": "search", "what": "stale_heterogeneity_surfaces: the page interprets the pool as homogeneous",
        "plants": {"accept": [("results were homogeneous", None), ("prediction interval not markedly wider", None)],
                   "refuse": ["heterogeneous", "no heterogeneity was assessed"]}},
    "gate.py:search:9a92bea520": {
        "kind": "search", "what": "stale_heterogeneity_surfaces: a primary heterogeneity row (prediction interval / tau² / I²)",
        "plants": {"accept": [("Prediction interval 0.6 to 1.2", None), ("Between-study τ² 0.01", None),
                              ("τ² = 0.02", None), ("I² = 40%", None)],
                   "refuse": ["the I² statistic", "Confidence interval 0.7 to 0.9"]}},
    "gate.py:search:159a89219d": {
        "kind": "search", "what": "stale_heterogeneity_surfaces: the heterogeneity row carries a number",
        "plants": {"accept": [("0.02", None), ("I² 40%", None)], "refuse": ["not estimable", "—"]}},
    "gate.py:search:e1d3371bfb": {
        "kind": "search", "what": "check_harms_synthesis_gated: the rendered harms tab panel body",
        "plants": {"accept": [('<section class="tab" id="tab-harms"><h3 class="tabname">Harms</h3><p>x</p></section>',
                               ("<p>x</p>",))],
                   "refuse": ['<section class="tab" id="tab-overview"><h3 class="tabname">O</h3></section>',
                              '<section id="tab-harms"><p>x</p></section>']}},
    # ---- harness/protocol_compiler.py --------------------------------------------------------------------------------
    "protocol_compiler.py:search:9a8cc773b0": {
        "kind": "search", "what": "_canon_estimand: an explicit parenthesised estimand code in a (lowercased) estimand line",
        "plants": {"accept": [("risk ratio (rr)", ("rr",)), ("hazard ratio (hr), colchicine vs placebo", ("hr",))],
                   "refuse": ["risk ratio", "(95% ci)"]}},
    "protocol_compiler.py:search:6d4338abae": {
        "kind": "search", "what": "parse_prose: the value of the protocol's **Estimand** line",
        "plants": {"accept": [("- **Estimand** - risk ratio (RR), colchicine vs placebo.",
                               ("risk ratio (RR), colchicine vs placebo",)),
                              ("**Estimand**: hazard ratio\n", ("hazard ratio",)),
                              ("- **Estimand** — risk ratio (RR), colchicine vs placebo.", None)],
                   "refuse": ["Estimand: RR", "- **Population** - intention-to-treat."]}},
    "protocol_compiler.py:search:249cd61f88": {
        "kind": "search", "what": "parse_prose: the value of the protocol's **Population** line (read for the analysis set)",
        "plants": {"accept": [("- **Population** - intention-to-treat as randomised.", ("intention-to-treat as randomised",)),
                              ("- **Population** — intention-to-treat as randomised.", None),
                              ("- **Population:** adults, intention-to-treat.", None)],
                   "refuse": ["Population: adults", "- **Estimand** - RR."]}},
    "protocol_compiler.py:search:dcfda9493e": {
        "kind": "search", "what": "parse_prose: the (lowercased) protocol admits double-blind OR placebo-controlled trials",
        "plants": {"accept": [("double-blind or placebo-controlled trials", None)],
                   "refuse": ["double-blind, placebo-controlled", "double-blind and placebo-controlled"]}},
    "protocol_compiler.py:search:cbbabbb69a": {
        "kind": "search", "what": "parse_prose: the (lowercased) protocol requires double-blind AND placebo-controlled",
        "plants": {"accept": [("randomised, double-blind, placebo-controlled", None),
                              ("double-blind and placebo-controlled", None),
                              ("randomised, double blind, placebo-controlled trials", None)],
                   "refuse": ["double-blind or placebo-controlled", "open-label, placebo-controlled"]}},
    "protocol_compiler.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm_text: collapse whitespace runs",
        "plants": {"accept": [("colchicine  0.5 mg", None), ("a\tb", None)], "refuse": ["colchicine", "0.5mg"]}},
    "protocol_compiler.py:sub:e3839b281a": {
        "kind": "search", "what": "_fold_for_prose: non-alphanumeric runs become spaces",
        "plants": {"accept": [("hr/rr", None), ("risk ratio (rr)", None)], "refuse": ["rr", "riskratio"]}},
    "protocol_compiler.py:start_re": {
        "kind": "search", "what": "intervention_line: the protocol's PICO Intervention bullet and its value",
        "plants": {"accept": [("- **Intervention** - colchicine 0.5 mg", ("colchicine 0.5 mg",)),
                              ("- **I (intervention):** colchicine", ("colchicine",)),
                              ("  - **Intervention** — SGLT2 inhibitor", ("SGLT2 inhibitor",))],
                   "refuse": ["- **Inclusion** - adults", "Intervention: colchicine"]}},
    "protocol_compiler.py:bullet_re": {
        "kind": "search", "what": "intervention_line: the next bold PICO bullet ends the intervention value",
        "plants": {"accept": [("- **Comparator** - placebo", None), ("  - **C** placebo", None)],
                   "refuse": ["  continuation line", "-- not a bullet"]}},
    "protocol_compiler.py:finditer:bf8a0d70a0": {
        "kind": "search", "what": "scope_amendments: a dated '## Amendment YYYY-MM-DD' heading (date, rest of heading)",
        "plants": {"accept": [("## Amendment 2026-09-01 - identifier scope\n", ("2026-09-01", " - identifier scope"))],
                   "refuse": ["## Amendment 1\n", "### Amendment 2026-09-01\n"]}},
    "protocol_compiler.py:search:5851103837": {
        "kind": "search", "what": "scope_amendments: the amendment's original identifier scope",
        "plants": {"accept": [("**Original identifier scope.** colchicine only", ("colchicine only",))],
                   "refuse": ["Original identifier scope: colchicine", "**Original identifier scope.**"]}},
    "protocol_compiler.py:search:4715c0c46f": {
        "kind": "search", "what": "scope_amendments: the amendment's widened scope",
        "plants": {"accept": [("**Widened scope.** any SGLT2 inhibitor", ("any SGLT2 inhibitor",))],
                   "refuse": ["Widened scope: any", "**Widened scope.**"]}},
    "protocol_compiler.py:search:7b2c2a25c9": {
        "kind": "search", "what": "scope_amendments: the amendment's stated reason",
        "plants": {"accept": [("**Reason.** class effect", ("class effect",))],
                   "refuse": ["Reason: class effect", "**Reason.**"]}},
    "protocol_compiler.py:search:f3b63c4300": {
        "kind": "search", "what": "scope_amendments: the amendment's pre-specified agent list",
        "plants": {"accept": [("**Pre-specified list.** dapagliflozin, empagliflozin", ("dapagliflozin, empagliflozin",))],
                   "refuse": ["Pre-specified list: dapagliflozin", "**Pre-specified list.**"]}},
    "protocol_compiler.py:ELIGIBILITY_HEADING": {
        "kind": "search", "what": "eligibility_clause: the rule-A heading '## Eligibility - (on) P/I/C/DESIGN only'",
        "plants": {"accept": [("## Eligibility - on P/I/C/DESIGN only", None), ("## Eligibility: P/I/C/design only", None)],
                   "refuse": ["## Eligibility", "### Eligibility - P/I/C/DESIGN only"]}},
    "protocol_compiler.py:ELIGIBILITY_BULLET": {
        "kind": "search", "what": "eligibility_clause: a '- **Eligibility (label).** clause' bullet (label, clause)",
        "plants": {"accept": [("- **Eligibility (B-prime).** trials are eligible", ("B-prime", "trials are eligible")),
                              ("* **Eligibility.** P/I/C only", (None, "P/I/C only"))],
                   "refuse": ["Eligibility: trials", "- **Population** - adults"]}},
    "protocol_compiler.py:search:1e08a0ee7b": {
        "kind": "search", "what": "eligibility_clause: the next '## ' section heading ends the eligibility section",
        "plants": {"accept": [("text\n## Next", None), ("## Methods", None)], "refuse": ["### Sub", "text ## not a heading"]}},
    # ---- harness/registry_multi.py -----------------------------------------------------------------------------------
    "registry_multi.py:_EUDRACT_RE": {
        "kind": "search", "what": "_parse_euctr_html: a EudraCT number (YYYY-NNNNNN-NN)",
        "plants": {"accept": [("2011-002123-42", None), ("EudraCT 2011-002123-42", None)],
                   "refuse": ["2011-00212-42", "NCT01179048"]}},
    "registry_multi.py:_ICTRP_ROW_RE": {
        "kind": "search", "what": "_parse_ictrp_html: one ICTRP result row",
        "plants": {"accept": [('<tr valign="top"><td>x</td></tr>', None)],
                   "refuse": ["<tr><td>x</td></tr>", '<tr valign="middle"><td>x</td>']}},
    "registry_multi.py:pattern": {
        "kind": "search", "what": "_query_variants: the spelling being swapped (compiled with old='haemorrhage')",
        "bind": {"old": "haemorrhage"},
        "plants": {"accept": [("postpartum haemorrhage", None), ("HAEMORRHAGE", None)],
                   "refuse": ["postpartum hemorrhage", "haemorrhoids"]}},
    "registry_multi.py:findall:01ccab1c69": {
        "kind": "search", "what": "_euctr_link: every href in a result block",
        "plants": {"accept": [('<a href="/ctr-search/trial/2011-002123-42/results">', ("/ctr-search/trial/2011-002123-42/results",))],
                   "refuse": ["href=/x", "<a>x</a>"]}},
    "registry_multi.py:search:808134fb4a": {
        "kind": "search", "what": "_euctr_full_title: the protocol page's full trial title (between its label and A.3.1)",
        "plants": {"accept": [("A.3 Full title of the trial Colchicine in pericarditis A.3.1 Title",
                               ("Colchicine in pericarditis",))],
                   "refuse": ["Full title of the trial Colchicine", "Title of the trial x A.3.1"]}},
    "registry_multi.py:search:c2f5733989": {
        "kind": "search", "what": "_parse_euctr_html: the EudraCT number cell",
        "plants": {"accept": [("EudraCT Number:</span> 2011-002123-42</td>", ("2011-002123-42",))],
                   "refuse": ["EudraCT Number: 2011-002123-42", "EudraCT Number:</span></td>"]}},
    "registry_multi.py:search:59e7e1f76c": {
        "kind": "search", "what": "_parse_euctr_html: the Full Title cell",
        "plants": {"accept": [("Full Title:</span> Colchicine for\n pericarditis </td>", ("Colchicine for\n pericarditis",))],
                   "refuse": ["Full Title: x </td>", "Full Title:</span> x"]}},
    "registry_multi.py:findall:01ccab1c69#2": {
        "kind": "search", "what": "_parse_euctr_html: every href in a result block (protocol links)",
        "plants": {"accept": [('<a href="/ctr-search/trial/2011-002123-42/GB">', ("/ctr-search/trial/2011-002123-42/GB",))],
                   "refuse": ["href=/x", "<a>x</a>"]}},
    "registry_multi.py:search:0e30ce316a": {
        "kind": "search", "what": "_parse_ictrp_html: the trial-id span (id ...Label1)",
        "plants": {"accept": [('<span id="DataList3_ctl01_Label1">ISRCTN123</span>', ("ISRCTN123",))],
                   "refuse": ['<span id="Label2">x</span>', "<div>Label1</div>"]}},
    "registry_multi.py:search:d0b77052c3": {
        "kind": "search", "what": "_parse_ictrp_html: the Trial2.aspx link (trial id, title)",
        "plants": {"accept": [('<a href="Trial2.aspx?TrialID=ISRCTN123" target="_blank">Colchicine</a>',
                               ("ISRCTN123", "Colchicine"))],
                   "refuse": ['<a href="Trial.aspx?TrialID=1">x</a>', "Trial2.aspx?TrialID=1"]}},
    # ---- harness/pipeline.py -----------------------------------------------------------------------------------------
    "pipeline.py:_DOI_RE": {
        "kind": "search", "what": "_query_classification: a DOI literal in a search query",
        "plants": {"accept": [("10.1056/NEJMoa1603827", None), ("doi 10.1016/S0140-6736(19)32345-0", None)],
                   "refuse": ["10.5 mg", "10.1/ab"]}},
    "pipeline.py:_PMID_LITERAL_RE": {
        "kind": "search", "what": "_query_classification: a PMID literal in a search query (not a [uid] enumeration)",
        "plants": {"accept": [("27633186", None), ("27633186[pmid]", None)],
                   "refuse": ["27633186[uid]", "123456", "NCT:NCT00113685 OR NCT:NCT00135473"]}},
    "pipeline.py:_TITLE_FIELD_RE": {
        "kind": "search", "what": "_query_classification: a title-field tag ([ti] / [title])",
        "plants": {"accept": [("empagliflozin[ti]", None), ("EMPA-REG[Title]", None)],
                   "refuse": ["empagliflozin[tiab]", "heart failure[tw]"]}},
    "pipeline.py:_ACRONYM_TOKEN_RE": {
        "kind": "search", "what": "_trial_acronym_tokens: a capitalised (possibly hyphenated) token in a query",
        "plants": {"accept": [("EMPA-REG OUTCOME", ("EMPA-REG",)), ("the LEADER trial", ("LEADER",))],
                   "refuse": ["empagliflozin trial", "non-empa"]}},
    "pipeline.py:_YEAR_RE": {
        "kind": "search", "what": "_journal_year_features: a year in a query",
        "plants": {"accept": [("2019", None), ("NEJM 1998", None)], "refuse": ["12019", "2105"]}},
    "pipeline.py:_JOURNAL_RE": {
        "kind": "search", "what": "_journal_year_features: a journal name in a query",
        "plants": {"accept": [("N Engl J Med 2016", None), ("lancet", None)],
                   "refuse": ["journal of medicine", "BMJOpen"]}},
    "pipeline.py:findall:56325787a0": {
        "kind": "search", "what": "_query_classification: an NCT literal in a query",
        "plants": {"accept": [("NCT01179048", None), ("nct01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    "pipeline.py:_NAMED_HELD_PATH": {
        "kind": "search", "what": "a hand row's source naming a held cache file (path, optional PMID)",
        "plants": {"accept": [("cache/omega3-cardiovascular-events/ft_38199870.txt (PMID 38199870)",
                               ("cache/omega3-cardiovascular-events/ft_38199870.txt", "38199870")),
                              ("cache/x/records.json abstract", ("cache/x/records.json", None))],
                   "refuse": ["see cache/x/records.json", "cache/x/y/z.json"]}},
    "pipeline.py:findall:e902435e30": {
        "kind": "search", "what": "_norm_endpoint_tokens: lowercase alphanumeric tokens of an endpoint name",
        "plants": {"accept": [("cv death", None), ("3-point", None)], "refuse": ["---", "—"]}},
    "pipeline.py:search:c2741ecf04": {
        "kind": "search", "what": "_mace_like: the (lowercased) endpoint names MI",
        "plants": {"accept": [("death, mi or stroke", None), ("mi", None)], "refuse": ["mild", "admission"]}},
}
