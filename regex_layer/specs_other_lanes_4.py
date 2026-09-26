"""Plants for the regex sites of harness/architecture_identity.py, claimgraph.py, design_key.py, scope_identity.py,
trial_family.py, compat_direction.py, honest_ratchet.py, page.py, registry_first.py, unit_of_analysis.py and
arm_object.py (keys as regex_layer.inventory names them). All belong to the OTHER lane: the regex layer only READS them,
and a located defect's fix belongs to the owning lane.

Texts are written as each site sees them: arm_object reads a record's title + abstract; design_key a pooled row's
source span; unit_of_analysis / trial_family record titles and abstracts; compat_direction review fields; page the
rendered page / protocol text; architecture_identity GitHub workflow YAML lines; registry_first / scope_identity ids,
ISRCTN XML and held records. honest_ratchet's retraction pattern is built per marker phrase at runtime and is planted
with phrase = 'we retract' ("bind").
"""

SITE_SPECS: dict = {
    # ---- harness/architecture_identity.py ----------------------------------------------------------------------------
    "architecture_identity.py:SHA40_RE": {
        "kind": "search", "what": "a full 40-hex-character git commit SHA (a pinned action ref)",
        "plants": {"accept": [("0123456789abcdef0123456789abcdef01234567", None),
                              ("0123456789ABCDEF0123456789ABCDEF01234567", None)],
                   "refuse": ["0123456789abcdef0123456789abcdef0123456", "v4"]}},
    "architecture_identity.py:match:704b8dda9d": {
        "kind": "search", "what": "a workflow line's 'uses:' action reference",
        "plants": {"accept": [("      - uses: actions/checkout@v4", ("actions/checkout@v4",)),
                              ("  uses: 'actions/setup-python@0a5c6158' # v5", ("actions/setup-python@0a5c6158",))],
                   "refuse": ["# uses: actions/checkout@v4", "  run: echo uses"]}},
    "architecture_identity.py:match:6b3929cc6f": {
        "kind": "search", "what": "the workflow's top-level 'jobs:' line",
        "plants": {"accept": [("jobs:", None), ("jobs:  ", None)], "refuse": ["  jobs:", "jobs: build"]}},
    "architecture_identity.py:match:a48edd0621": {
        "kind": "search", "what": "a job name line (two-space indent) under jobs:",
        "plants": {"accept": [("  build:", ("build",)), ("  verify-gate:", ("verify-gate",))],
                   "refuse": ["    steps:", "  build: x"]}},
    "architecture_identity.py:match:6cffb73cad": {
        "kind": "search", "what": "a job's 'needs:' value",
        "plants": {"accept": [("    needs: build", ("build",)), ("    needs: [build, test]", ("[build, test]",))],
                   "refuse": ["      needs: build", "  needs: build"]}},
    "architecture_identity.py:match:983fd0398b": {
        "kind": "search", "what": "a job's 'if:' condition",
        "plants": {"accept": [("    if: github.event_name == 'push'", ("github.event_name == 'push'",))],
                   "refuse": ["      if: x", "    iff: x"]}},
    # ---- harness/arm_object.py ---------------------------------------------------------------------------------------
    "arm_object.py:_DOSE": {
        "kind": "search", "what": "_dose_of: a dose with its unit (mg, g, mcg, ug, ml, %)",
        "plants": {"accept": [("10 mg", None), ("dapagliflozin 2,5 mg", None), ("100/1000 mg", None),
                              ("0.9% sodium chloride", None)],
                   "refuse": ["10 patients", "week 52"]}},
    "arm_object.py:_WEEK": {
        "kind": "search", "what": "_timepoint: the week of the outcome ('week 52', '68-week', 'at 52 weeks')",
        "plants": {"accept": [("at week 52", ("52", None)), ("the 68-week trial", (None, "68")),
                              ("cough-specific health status at 12 weeks", None)],
                   "refuse": ["weekly injections", "every week"]}},
    "arm_object.py:_AGE_RANGE": {
        "kind": "search", "what": "_population: an entry age range ('aged 12 to 17 years')",
        "plants": {"accept": [("aged 12 to 17 years", ("12", "17")), ("aged 18-75 years", ("18", "75"))],
                   "refuse": ["aged 65 years or older", "18 to 75 years"]}},
    "arm_object.py:search:1543b331b8": {
        "kind": "search", "what": "_generic_contrasts: the semaglutide dose of the contrast",
        "plants": {"accept": [("semaglutide 2.4 mg once weekly", ("2.4",)),
                              ("once-weekly semaglutide (0.5 mg", None)],
                   "refuse": ["semaglutide versus placebo", "liraglutide 3.0 mg"]}},
    # ---- harness/claimgraph.py ---------------------------------------------------------------------------------------
    "claimgraph.py:_PMID_RE": {
        "kind": "search", "what": "a PMID (optionally labelled)",
        "plants": {"accept": [("PMID: 27633186", ("27633186",)), ("27633186", ("27633186",))],
                   "refuse": ["123456", "NCT01179048"]}},
    "claimgraph.py:_NCT_RE": {
        "kind": "search", "what": "an NCT number",
        "plants": {"accept": [("NCT01179048", None)], "refuse": ["NCT0117904", "NCT011790480"]}},
    "claimgraph.py:findall:7efba48385": {
        "kind": "search", "what": "a PDF page marker in a handover text ('### PAGE n' / '===== page n =====')",
        "plants": {"accept": [("### PAGE 3", ("3",)), ("===== page 12 =====", ("12",))],
                   "refuse": ["PAGE 3", "## PAGE 3"]}},
    "claimgraph.py:search:0a97f189e1": {
        "kind": "search", "what": "_parity_named_count: the parity reason's 'N valid RCT(s) ... = ours'",
        "plants": {"accept": [("4 valid RCT (A+B+C+D) = ours", ("4",)), ("4 valid RCTs = ours", None)],
                   "refuse": ["4 RCTs in the comparator", "4 valid RCT"]}},
    "claimgraph.py:search:b1f76ed2f3": {
        "kind": "search", "what": "_parity_named_count: the parity reason's 'A + B = our pool'",
        "plants": {"accept": [("OMEMI + OMEGA-REMODEL = our pool", ("OMEMI + OMEGA-REMODEL",))],
                   "refuse": ["OMEMI = our pool", "OMEMI + OMEGA-REMODEL were excluded"]}},
    "claimgraph.py:split:74aca78d9f": {
        "kind": "split", "what": "_parity_named_count: split 'A + B' into trial names",
        "plants": {"accept": [("OMEMI + VITAL", ["OMEMI", "VITAL"])], "refuse": ["OMEMI", "OMEMI-VITAL"]}},
    # ---- harness/compat_direction.py ---------------------------------------------------------------------------------
    "compat_direction.py:_HETERO_RE": {
        "kind": "search", "what": "_warning_state / _text_state: the text asserts the dimension differs across trials",
        "plants": {"accept": [("follow-up windows differ", None), ("heterogeneous populations", None),
                              ("timepoints vary across trials", None)],
                   "refuse": ["the same 12-month window", "follow-up did not differ between trials"]}},
    "compat_direction.py:_ENDPOINT_HETERO_RE": {
        "kind": "search", "what": "_warning_state: the text asserts endpoint definitions differ",
        "plants": {"accept": [("component sets differ", None),
                              ("VTE-related death counts in EINSTEIN whereas Hokusai counts it", None)],
                   "refuse": ["components are identical", "endpoint definitions agree"]}},
    "compat_direction.py:sub:9bca43bba5": {
        "kind": "search", "what": "component codes: non-alphanumeric runs become '_' (upper-cased component)",
        "plants": {"accept": [("CV DEATH", None), ("EGFR-DECLINE", None)], "refuse": ["CVDEATH", "EGFR40"]}},
    "compat_direction.py:sub:9bca43bba5#2": {
        "kind": "search", "what": "kidney component codes: non-alphanumeric runs become '_'",
        "plants": {"accept": [("KIDNEY FAILURE", None)], "refuse": ["KIDNEYFAILURE", "ESKD"]}},
    "compat_direction.py:search:0c34b57e0a": {
        "kind": "search", "what": "_trial_id: the numeric trial id (PMID) in an id / label",
        "plants": {"accept": [("27633186", ("27633186",))], "refuse": ["12345", "NCT01179048"]}},
    # ---- harness/design_key.py ---------------------------------------------------------------------------------------
    "design_key.py:_ALT_RE": {
        "kind": "search", "what": "_published_alternative: a published ratio estimate with its CI in the row's source",
        "plants": {"accept": [("adjusted hazard ratio 0.80 (95% CI 0.70-0.90)",
                               ("adjusted ", "hazard ratio", "0.80", "0.70", "0.90")),
                              ("HR 0.80, 95% CI 0.70-0.90", (None, "HR", "0.80", "0.70", "0.90")),
                              ("hip fracture (hazard ratio, 0.60; 95% CI, 0.37 to 0.97)", None)],
                   "refuse": ["the hazard ratio was similar", "HR 0.80"]}},
    "design_key.py:_NO_INTERACTION_RE": {
        "kind": "search", "what": "_interaction_evidence: a stated no-significant-interaction with its P value",
        "plants": {"accept": [("no significant interaction between the two interventions (P=0.52)", None),
                              ("No significant interaction was seen (p = .31)", None)],
                   "refuse": ["a significant interaction (P=0.02)", "no significant interaction was observed"]}},
    "design_key.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_source_span: collapse whitespace runs",
        "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "design_key.py:split:9bca43bba5": {
        "kind": "split", "what": "_declared_estimand_class: split a declared estimand into tokens",
        "plants": {"accept": [("HR/RR", ["HR", "RR"])], "refuse": ["HR", "RR2"]}},
    "design_key.py:sub:7b4eac99d8#2": {
        "kind": "search", "what": "_published_alternative: collapse whitespace in the span",
        "plants": {"accept": [("HR\n0.80", None)], "refuse": ["HR", "0.80"]}},
    "design_key.py:sub:7b4eac99d8#3": {
        "kind": "search", "what": "_interaction_evidence: collapse whitespace in the span",
        "plants": {"accept": [("no  significant", None)], "refuse": ["no-significant", "p"]}},
    # ---- harness/honest_ratchet.py -----------------------------------------------------------------------------------
    "honest_ratchet.py:L53": {
        "kind": "search", "what": "RETRACTION_RE: the rendered page carries a retraction marker phrase (compiled with phrase='we retract')",
        "bind": {"phrase": "we retract"},
        "plants": {"accept": [("We retract this estimate", None), ("we  retract", None)],
                   "refuse": ["we retracted it", "were tracted"]}},
    "honest_ratchet.py:sub:627bb26cb4": {
        "kind": "search", "what": "_rendered_text: drop <script>/<style> blocks",
        "plants": {"accept": [("<script>var x = 1;</script>", None), ('<style type="text/css">p{}</style>', None)],
                   "refuse": ["<p>x</p>", "<scripts>x</scripts>"]}},
    "honest_ratchet.py:sub:caf616cd71": {
        "kind": "search", "what": "_rendered_text: strip tags",
        "plants": {"accept": [("<p>x</p>", None)], "refuse": ["a &lt; b", "plain"]}},
    "honest_ratchet.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_rendered_text: collapse whitespace runs",
        "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "honest_ratchet.py:sub:7b4eac99d8#2": {
        "kind": "search", "what": "block collector: collapse whitespace in a block's text",
        "plants": {"accept": [("a\nb", None)], "refuse": ["ab", "a-b"]}},
    # ---- harness/page.py ---------------------------------------------------------------------------------------------
    "page.py:sub:af38ae76fc": {
        "kind": "search", "what": "the legacy PRISMA 2020 selection-flow table",
        "plants": {"accept": [("<h4>Study selection flow (PRISMA 2020)</h4><table><tr><td>1</td></tr></table>", None)],
                   "refuse": ["<h4>Study selection flow</h4><table></table>",
                              "<h4>Study selection flow (PRISMA 2020)</h4><p>none</p>"]}},
    "page.py:sub:062e5ca288": {
        "kind": "search", "what": "the legacy 'Screened-in' reconciliation row (head, value, tail)",
        "plants": {"accept": [("<tr><td>Screened-in reports</td><td>12</td></tr>",
                               ("<tr><td>Screened-in reports</td><td>", "12", "</td></tr>"))],
                   "refuse": ["<tr><td>Screened-out</td><td>12</td></tr>", "Screened-in 12"]}},
    "page.py:sub:4f38856489": {
        "kind": "search", "what": "the legacy 'N records screened; <strong>...</strong>.' sentence",
        "plants": {"accept": [("<p>120 records screened; <strong>12 included</strong>.", None)],
                   "refuse": ["<p>records screened; <strong>12</strong>.", "120 records screened"]}},
    "page.py:search:2a82269e03": {
        "kind": "search", "what": "Reproducibility row: the protocol text carries results or identifiers (not prospective)",
        "plants": {"accept": [("NCT01179048", None), ("PMID: 27633186", None), ("HR 0.80 (95% CI 0.70-0.90)", None)],
                   "refuse": ["colchicine versus placebo", "- **Estimand** - risk ratio (RR), colchicine vs placebo."]}},
    "page.py:search:e9a52114b2": {
        "kind": "search", "what": "Methods/preregistration surface: the protocol text carries results or identifiers",
        "plants": {"accept": [("NCT01179048", None), ("hazard ratio 0.8", None), ("LEADER reported HR 0.87 for MACE", None)],
                   "refuse": ["colchicine versus placebo", "a 12-month window"]}},
    # ---- harness/registry_first.py -----------------------------------------------------------------------------------
    "registry_first.py:_NCT_RE": {
        "kind": "search", "what": "the whole id is an NCT number",
        "plants": {"accept": [("NCT01179048", None)], "refuse": ["NCT0117904", "see NCT01179048"]}},
    "registry_first.py:_PMID_RE": {
        "kind": "search", "what": "the whole id is a bare PMID",
        "plants": {"accept": [("27633186", None)], "refuse": ["PMID 1", "27a"]}},
    "registry_first.py:_ISRCTN_RE": {
        "kind": "search", "what": "the whole id is an ISRCTN number",
        "plants": {"accept": [("ISRCTN12345678", None)], "refuse": ["ISRCTN1234567", "ISRCTN123456789"]}},
    "registry_first.py:_ISRCTN_CANONICAL_RE": {
        "kind": "search", "what": "_parse_isrctn_ids: an ISRCTN XML record's canonical public identifier",
        "plants": {"accept": [('<trial publicIdentifierCanonical="ISRCTN12345678">', ("ISRCTN12345678",))],
                   "refuse": ['publicIdentifier="ISRCTN12345678"', 'publicIdentifierCanonical="NCT01179048"']}},
    "registry_first.py:search:00dd9077fe": {
        "kind": "search", "what": "the ISRCTN API response's totalCount",
        "plants": {"accept": [('<allTrials totalCount="12">', ("12",))], "refuse": ["totalCount=12", 'count="12"']}},
    # ---- harness/scope_identity.py -----------------------------------------------------------------------------------
    "scope_identity.py:_AMENDMENT_RE": {
        "kind": "search", "what": "a '## Amendment YYYY-MM-DD (label)' section (date, label, body)",
        "plants": {"accept": [("## Amendment 2026-09-01 (dose rule)\nbody\n## Next", ("2026-09-01", "dose rule", "\nbody\n"))],
                   "refuse": ["### Amendment 2026-09-01", "## Amendment 1"]}},
    "scope_identity.py:search:2cdeb7a7ad": {
        "kind": "search", "what": "_date_prefix: an ISO date",
        "plants": {"accept": [("2026-09-01T12:00Z", None)], "refuse": ["2026-9-1", "20260901"]}},
    "scope_identity.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_short_changed: collapse whitespace",
        "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
    "scope_identity.py:search:46590dd2ae": {
        "kind": "search", "what": "RE-LY: the dabigatran 110 mg arm's relative risk 0.91 (0.74-1.11)",
        "plants": {"accept": [("110 mg of dabigatran ... relative risk, 0.91; 95% CI, 0.74 to 1.11", None)],
                   "refuse": ["150 mg relative risk 0.66", "110 mg relative risk 0.91"]}},
    "scope_identity.py:search:bb9c1a634d": {
        "kind": "search", "what": "ENGAGE AF: the low-dose edoxaban arm's hazard ratio 1.13 (0.96-1.34)",
        "plants": {"accept": [("low-dose edoxaban ... hazard ratio, 1.13; 97.5% CI, 0.96 to 1.34", None)],
                   "refuse": ["high-dose edoxaban hazard ratio, 0.87", "low-dose edoxaban hazard ratio 1.13"]}},
    "scope_identity.py:search:153b0980f5": {
        "kind": "search", "what": "ENGAGE AF: the record labels a 30 mg edoxaban dose",
        "plants": {"accept": [("30 mg", None), ("30mg once daily", None)], "refuse": ["130 mg", "30 mcg"]}},
    # ---- harness/trial_family.py -------------------------------------------------------------------------------------
    "trial_family.py:REGISTRY": {
        "kind": "search", "what": "registry_ids: a trial registry number in a record id / abstract",
        "plants": {"accept": [("NCT01179048", None), ("2011-002123-42", None), ("ISRCTN12345678", None),
                              ("jRCT2031190012", None), ("ACTRN12615000123456", None),
                              ("ChiCTR2100045056", None), ("IRCT20200328046886N6", None)],
                   "refuse": ["NCT0117904", "trial 2011"]}},
    "trial_family.py:search:51bc07b8ef": {
        "kind": "search", "what": "report_role: the abstract's objective is 'in relation to' a baseline factor (a subgroup report)",
        "plants": {"accept": [("OBJECTIVE: To assess outcomes in relation to baseline eGFR.", None)],
                   "refuse": ["OBJECTIVE: To assess outcomes.", "in relation to baseline eGFR"]}},
    "trial_family.py:search:e13d2a5bf6": {
        "kind": "search", "what": "report_role: the abstract assesses an interaction with the treatment effect",
        "plants": {"accept": [("the interaction between baseline eGFR and treatment effect was assessed", None)],
                   "refuse": ["interaction between baseline eGFR and treatment", "treatment effect was assessed"]}},
    "trial_family.py:fullmatch:32005ef657": {
        "kind": "search", "what": "registry_ids ordering: the id is a EudraCT number",
        "plants": {"accept": [("2011-002123-42", None)], "refuse": ["2011-00212-42", "2011-002123-4"]}},
    "trial_family.py:search:76b3356c9e": {
        "kind": "search", "what": "an extension report loses the randomised contrast (open-label / crossed over / all received)",
        "plants": {"accept": [("open-label extension", None), ("patients crossed over to", None),
                              ("all participants subsequently received empagliflozin", None)],
                   "refuse": ["double-blind extension", "patients received placebo"]}},
    "trial_family.py:fullmatch:e45e5b124d": {
        "kind": "search", "what": "the registry minimum entry age in years",
        "plants": {"accept": [("18 Years", ("18",)), ("12.5 years", ("12.5",))], "refuse": ["18 Months", "N/A"]}},
    # ---- harness/unit_of_analysis.py ---------------------------------------------------------------------------------
    "unit_of_analysis.py:_CLUSTER": {
        "kind": "search", "what": "the trial is cluster-randomised",
        "plants": {"accept": [("a cluster-randomized trial", None), ("randomised by hospital", None)],
                   "refuse": ["a clustered analysis", "randomized by computer"]}},
    "unit_of_analysis.py:_CROSSOVER": {
        "kind": "search", "what": "the trial has a crossover design",
        "plants": {"accept": [("a crossover trial", None), ("double-crossover", None), ("two-period crossover", None)],
                   "refuse": ["patients crossed over to open-label", "crossover to placebo"]}},
    "unit_of_analysis.py:_FACTORIAL": {
        "kind": "search", "what": "the trial has a factorial design",
        "plants": {"accept": [("a 2 x 2 factorial design", None), ("factorial, randomized", None),
                              ("randomized in a 2 x 2 factorial", None)],
                   "refuse": ["factorial analysis", "risk factors"]}},
    "unit_of_analysis.py:_STEPPED_WEDGE": {
        "kind": "search", "what": "the trial has a stepped-wedge design",
        "plants": {"accept": [("stepped-wedge cluster randomised", None), ("stepped wedge", None)],
                   "refuse": ["wedge resection", "stepped care"]}},
    "unit_of_analysis.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_span: collapse whitespace",
        "plants": {"accept": [("a  b", None)], "refuse": ["ab", "a-b"]}},
}
