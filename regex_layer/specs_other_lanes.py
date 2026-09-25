"""Plants for the regex sites of harness/rob2.py, harness/funding.py and harness/hand_binding.py (keys as
regex_layer.inventory names them). These three files belong to the OTHER lane: the regex layer only READS them --
plants and measurement live here and in tests/, and a located defect's fix belongs to the owning lane.

Texts are written as the code sees them:
  rob2._component_set lowercases (after _norm_text), so its sites get lowercase text;
  funding's compiled patterns are re.I and read raw held title+abstract / full text (the role patterns and the
    sponsor-splitting sites read the funding basis span funding.detect cut from it);
  hand_binding's XML sites read raw PMC JATS, its prose sites read sentences of held abstract / full-text prose.
An f-string site (hand_binding's per-tag front-matter strip) is compiled with the value named in "bind".
"""

SITE_SPECS: dict = {
    # ---- harness/rob2.py (_component_set on a registered AACT outcome / the pooled outcome name, lowercased) -------
    "rob2.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_norm_text: collapse whitespace runs in a registered outcome field",
        "plants": {"accept": [("cardiovascular  death\nor stroke", None), ("mace\t(3-point)", None)],
                   "refuse": ["cardiovascular-death", "mace"]}},
    "rob2.py:search:b4e124d7bc": {
        "kind": "search", "what": "_component_set: the outcome is measured on the MADRS (by abbreviation or full name)",
        "plants": {"accept": [("change from baseline in madrs total score", None),
                              ("montgomery-asberg depression rating scale", None),
                              ("montgomery asberg depression rating scale", None),
                              ("change from baseline in montgomery–åsberg depression rating scale total score", None)],
                   "refuse": ["hamilton depression rating scale", "phq-9 total score"]}},
    "rob2.py:search:6a51f42d5e": {
        "kind": "search", "what": "_component_set: the MADRS outcome is a response / remission (dichotomised) outcome",
        "plants": {"accept": [("madrs response (>=50% reduction from baseline)", None),
                              ("remission (madrs total score <=12)", None)],
                   "refuse": ["change from baseline in madrs total score", "mean madrs total score at day 28"]}},
    "rob2.py:search:c958964040": {
        "kind": "search", "what": "_component_set: the MADRS outcome is a change / total-score outcome",
        "plants": {"accept": [("change from baseline in madrs total score", None), ("madrs total score at day 28", None)],
                   "refuse": ["madrs response rate", "percentage of participants in remission"]}},
    "rob2.py:search:74ee9684cf": {
        "kind": "search", "what": "_component_set: the thromboembolic outcome is a RECURRENCE (with the VTE site)",
        "plants": {"accept": [("recurrent venous thromboembolism", None), ("symptomatic recurrent vte", None),
                              ("symptomatic vte recurrence", None)],
                   "refuse": ["first venous thromboembolism", "incident vte after surgery"]}},
    "rob2.py:search:2ee9bddbd6": {
        "kind": "search", "what": "_component_set: the outcome names a venous thromboembolic event (VTE, DVT, PE)",
        "plants": {"accept": [("recurrent vte", None), ("recurrent pulmonary embolism", None),
                              ("deep vein thrombosis", None), ("recurrent deep venous thrombosis", None)],
                   "refuse": ["arterial thrombosis", "pericardial effusion"]}},
    "rob2.py:search:217d388541": {
        "kind": "search", "what": "_component_set: the outcome is a net-clinical-benefit composite (excluded from recurrent VTE)",
        "plants": {"accept": [("net clinical benefit (recurrent vte or major bleeding)", None)],
                   "refuse": ["clinical benefit", "net reclassification improvement"]}},
    "rob2.py:search:2302517c9d": {
        "kind": "search", "what": "_component_set: the outcome is all-cause mortality (death from any cause)",
        "plants": {"accept": [("all-cause mortality", None), ("all cause mortality", None),
                              ("number of participants with an event of all-cause death", None),
                              ("death from any cause", None)],
                   "refuse": ["cardiovascular mortality", "cause-specific mortality"]}},
    "rob2.py:search:95e6c448a9": {
        "kind": "search", "what": "_component_set: the outcome concerns the kidney (with the progression-word site)",
        "plants": {"accept": [("sustained egfr decline >=40%", None), ("end-stage kidney disease", None),
                              ("renal death", None)],
                   "refuse": ["heart failure hospitalization", "hepatic failure"]}},
    "rob2.py:search:39f51c3310": {
        "kind": "search", "what": "_component_set: the kidney outcome is a progression / decline / failure / composite",
        "plants": {"accept": [("composite kidney outcome", None), ("progression of ckd", None),
                              ("renal replacement therapy", None)],
                   "refuse": ["urine albumin-to-creatinine ratio at week 12", "kidney function at baseline"]}},
    "rob2.py:search:052d9d5ea5": {
        "kind": "search", "what": "_component_set: the outcome names cardiovascular death",
        "plants": {"accept": [("cv death", None), ("cardiovascular death", None), ("cardiovascular (cv) death", None),
                              ("death from cardiovascular causes", None),
                              ("number of participants with an event of cv-related death", None),
                              ("death due to cardiovascular causes", None)],
                   "refuse": ["death from any cause", "cardiovascular hospitalization", "non-cardiovascular death"]}},
    "rob2.py:search:6cd81436fb": {
        "kind": "search", "what": "_component_set: the outcome names NON-fatal myocardial infarction",
        "plants": {"accept": [("non-fatal myocardial infarction", None), ("nonfatal mi", None)],
                   "refuse": ["fatal myocardial infarction", "myocardial infarction"]}},
    "rob2.py:search:ac07acacc3": {
        "kind": "search", "what": "_component_set: the outcome names myocardial infarction (MI)",
        "plants": {"accept": [("myocardial infarction", None), ("fatal or non-fatal mi", None)],
                   "refuse": ["mild adverse events", "mitral regurgitation"]}},
    "rob2.py:search:4ae0272c1d": {
        "kind": "search", "what": "_component_set: the outcome names NON-fatal stroke",
        "plants": {"accept": [("non-fatal stroke", None), ("nonfatal stroke", None)],
                   "refuse": ["fatal stroke", "stroke"]}},
    "rob2.py:search:75347cb965": {
        "kind": "search", "what": "_component_set: the outcome names stroke",
        "plants": {"accept": [("stroke", None), ("ischemic stroke", None)],
                   "refuse": ["transient ischemic attack", "myocardial infarction"]}},
    "rob2.py:search:4494298990": {
        "kind": "search", "what": "_component_set: the outcome names hospitalisation for heart failure",
        "plants": {"accept": [("hhf", None), ("hospitalization for heart failure", None),
                              ("heart failure hospitalisation", None), ("hospitalized for hf", None),
                              ("rate of total (first and recurrent) events of hospitalisations for heart failure (hf)", None)],
                   "refuse": ["all-cause hospitalization", "heart failure death"]}},
    "rob2.py:search:145e8c3798": {
        "kind": "search", "what": "_component_set: the outcome names unstable angina",
        "plants": {"accept": [("unstable angina", None), ("hospitalization for unstable angina", None)],
                   "refuse": ["stable angina", "angina pectoris"]}},
    "rob2.py:search:07c0729508": {
        "kind": "search", "what": "_component_set: the outcome names (coronary) revascularisation",
        "plants": {"accept": [("coronary revascularization", None), ("urgent revascularisation", None)],
                   "refuse": ["target lesion failure", "vascular access complications"]}},
    "rob2.py:search:a26bd545ce": {
        "kind": "search", "what": "_component_set: the outcome is a MACE-type composite (MACE / major adverse cardiovascular events)",
        "plants": {"accept": [("mace", None), ("major adverse cardiovascular events", None),
                              ("major cardiovascular events", None), ("major adverse cardiac events", None)],
                   "refuse": ["major adverse events", "grimace score", "major bleeding"]}},
    "rob2.py:search:e1fe9ad18e": {
        "kind": "search", "what": "_component_set: the MACE is declared 3-point",
        "plants": {"accept": [("3-point mace", None), ("three-point mace", None), ("3 point mace", None)],
                   "refuse": ["4-point mace", "a 13-point scale"]}},
    "rob2.py:sub:e3839b281a": {
        "kind": "search", "what": "_simple_matches: non-alphanumeric runs become spaces (pooled outcome side)",
        "plants": {"accept": [("cv death", None), ("3-point mace", None)], "refuse": ["cvdeath", "mace3"]}},
    "rob2.py:sub:e3839b281a#2": {
        "kind": "search", "what": "_simple_matches: non-alphanumeric runs become spaces (registered outcome side)",
        "plants": {"accept": [("heart-failure hospitalization", None), ("(mace)", None)],
                   "refuse": ["hhf", "stroke"]}},
    # ---- harness/funding.py (compiled patterns are re.I) -------------------------------------------------------------
    "funding.py:_STRONG_ANCHOR": {
        "kind": "search", "what": "detect: the text carries an explicit funding statement (funded by / funding: / grants from / sponsor)",
        "plants": {"accept": [("(Funded by Novo Nordisk; LEADER ClinicalTrials.gov number, NCT01179048.)", None),
                              ("Funding: None.", None), ("Role of the funding source: the sponsor had no role", None),
                              ("This trial was supported by the NIHR.", None)],
                   "refuse": ["Patients were supported by nurses.", "Hospital funding of care increased."]}},
    "funding.py:_WEAK_ANCHOR": {
        "kind": "search", "what": "detect: a funding statement introduced by 'supported by' (weak: read only with a sponsor marker)",
        "plants": {"accept": [("Supported by the Swiss National Science Foundation.", None),
                              ("This work was supported by Pfizer.", None)],
                   "refuse": ["Funded by Pfizer.", "supportive care was given"]}},
    "funding.py:_INDUSTRY": {
        "kind": "search", "what": "_class_from_markers / detect: the funding window names an industry sponsor",
        "plants": {"accept": [("Funded by Novo Nordisk.", None), ("Janssen Research & Development, LLC", None),
                              ("supported by Boehringer Ingelheim", None),
                              ("FUNDING: Corvia Medical Inc.", None)],
                   "refuse": ["Funded by the National Institutes of Health.", "University of Oxford",
                              "Funded by the Medical Research Council."]}},
    "funding.py:_PUBLIC": {
        "kind": "search", "what": "_class_from_markers: the funding window names a public / non-profit funder, or states no funding",
        "plants": {"accept": [("Funded by the National Institutes of Health.", None), ("the Wellcome Trust", None),
                              ("The authors received no external funding.", None),
                              ("Funded by the National Heart, Lung, and Blood Institute.", None)],
                   "refuse": ["Funded by AstraZeneca.", "Sanofi provided support."]}},
    "funding.py:_DRUG_SUPPLY": {
        "kind": "search", "what": "detect: the text states the study drug / placebo was supplied by someone",
        "plants": {"accept": [("Study drug was provided by Novartis.", None),
                              ("Placebo and study drug were supplied by Merck.", None),
                              ("Tablets were kindly donated by Cipla.", None),
                              ("Novo Nordisk provided the study drug.", None)],
                   "refuse": ["The study drug was administered by nurses.", "Funded by Pfizer."]}},
    "funding.py:_FUNDING_POINTER": {
        "kind": "search", "what": "detect: the funding statement is deferred to a supplement / appendix not held",
        "plants": {"accept": [("Funding details are available in the Supplementary Appendix.", None),
                              ("funding information is available online", None)],
                   "refuse": ["Funded by Novo Nordisk.", "See the Supplementary Appendix for methods."]}},
    "funding.py:_INDUSTRY_AUTHORS": {
        "kind": "search", "what": "detect / scan_pooled: an author is employed by (or holds equity in) an industry company",
        "plants": {"accept": [("J.S. is an employee of Pfizer.", None), ("Two authors are Novo Nordisk employees.", None),
                              ("V.L. and B.R. are employees of Vifor Pharma Ltd.", None)],
                   "refuse": ["J.S. has received consulting fees from Pfizer.",
                              "J.S. is an employee of the University of Oxford. The trial was funded by Pfizer."]}},
    "funding.py:L81": {
        "kind": "search", "what": "_roles: the span assigns the funder a role in study DESIGN",
        "plants": {"accept": [("the funder had no role in study design", None), ("the sponsor designed the trial", None)],
                   "refuse": ["a designated centre", "designer drugs"]}},
    "funding.py:L82": {
        "kind": "search", "what": "_roles: the span assigns the funder a role in study CONDUCT",
        "plants": {"accept": [("no role in the conduct of the study", None), ("the sponsor performed the monitoring", None)],
                   "refuse": ["skin conductance", "exercise performance"]}},
    "funding.py:L83": {
        "kind": "search", "what": "_roles: the span assigns the funder a role in DATA COLLECTION",
        "plants": {"accept": [("no role in data collection", None), ("the sponsor collected the data", None)],
                   "refuse": ["a collective effort", "recollection bias"]}},
    "funding.py:L84": {
        "kind": "search", "what": "_roles: the span assigns the funder a role in data ANALYSIS",
        "plants": {"accept": [("no role in data analysis", None), ("the sponsor analyzed the data", None),
                              ("the funder had no role in analysing the data", None)],
                   "refuse": ["an analyst was hired", "psychoanalytic theory"]}},
    "funding.py:L85": {
        "kind": "search", "what": "_roles: the span assigns the funder a role in WRITING the manuscript",
        "plants": {"accept": [("the sponsor wrote the first draft", None), ("no role in writing of the report", None)],
                   "refuse": ["written informed consent", "handwriting samples"]}},
    "funding.py:_NCT_RE": {
        "kind": "search", "what": "the NCT registry number in a trial's source / label / abstract",
        "plants": {"accept": [("NCT01179048", None), ("ClinicalTrials.gov number, nct01179048.", None)],
                   "refuse": ["NCT0117904", "NCT011790480"]}},
    "funding.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_clean: collapse whitespace runs",
        "plants": {"accept": [("Funded by\n Pfizer", None), ("a\tb", None)], "refuse": ["Funded-by-Pfizer", "NIH"]}},
    "funding.py:search:a4601f97a8": {
        "kind": "search", "what": "_sentence_window: end the window at the next sentence boundary",
        "plants": {"accept": [("Funded by Pfizer. The trial was", None), ("was it funded? (No)", None)],
                   "refuse": ["Pfizer Inc. and Merck", "a dose of 10.5 mg"]}},
    "funding.py:sub:7282f3a795": {
        "kind": "search", "what": "_split_sponsors: strip everything up to the funding lead-in (funded by / funding: / grants from / supported by)",
        "plants": {"accept": [("Funded by Novo Nordisk", None), ("This work was supported by the NIHR", None),
                              ("Funding: Wellcome", None)],
                   "refuse": ["Novo Nordisk", "The sponsor had no role"]}},
    "funding.py:sub:70a43250a0": {
        "kind": "search", "what": "_split_sponsors: strip a leading 'this study/trial/work/research was funded by'",
        "plants": {"accept": [("This study was funded by Pfizer", None), ("this trial was funded by the MRC", None)],
                   "refuse": ["Pfizer funded this study", "The study was funded by Pfizer"]}},
    "funding.py:split:88ba5636a3": {
        "kind": "split", "what": "_split_sponsors: the sponsor list ends at ; a sentence end or a trial-registration statement",
        "plants": {"accept": [("Novo Nordisk; LEADER", ["Novo Nordisk", " LEADER"]),
                              ("the NIHR. The trial", ["the NIHR", "The trial"])],
                   "refuse": ["Novo Nordisk and Pfizer", "Janssen Research & Development, LLC"]}},
    "funding.py:sub:a8c5be7f86": {
        "kind": "search", "what": "_split_sponsors: drop an unnamed remainder 'and others'",
        "plants": {"accept": [("Pfizer and others", None), ("the NIH, and others", None)],
                   "refuse": ["another sponsor", "and other funders"]}},
    "funding.py:split:d3389b2de7": {
        "kind": "split", "what": "_split_sponsors: split a sponsor list into sponsor names (never inside one name)",
        "plants": {"accept": [("Novo Nordisk and Pfizer", ["Novo Nordisk ", " Pfizer"]),
                              ("NIH, Wellcome", ["NIH", " Wellcome"])],
                   "refuse": ["Novo Nordisk", "Rand Corporation", "Johnson & Johnson",
                              "Bill & Melinda Gates Foundation", "National Heart, Lung, and Blood Institute"]}},
    "funding.py:sub:5150d3bfe8": {
        "kind": "search", "what": "_split_sponsors: strip a leading article from a sponsor name",
        "plants": {"accept": [("the Wellcome Trust", ("the",)), ("An anonymous donor", ("An",))],
                   "refuse": ["Theravance", "Amgen"]}},
    # ---- harness/hand_binding.py -------------------------------------------------------------------------------------
    "hand_binding.py:_REF_JUNK": {
        "kind": "search", "what": "_definition_binding / _label_definition: a prose sentence is reference-list / front-matter debris (DOI, PMC id, pdf, copyright)",
        "plants": {"accept": [("N Engl J Med 2016;375:311-22. doi:10.1056/NEJMoa1603827", None), ("PMCID: PMC6135590", None),
                              ("pmc-release date", None), ("Download the .pdf file", None), ("All rights reserved.", None),
                              ("the Seventh Framework Program 10.13039/501100000780 European Commission", None)],
                   "refuse": ["HR 0.87 (95% CI 0.78-0.97)", "10.5% of patients died"]}},
    "hand_binding.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_plain: collapse whitespace runs",
        "plants": {"accept": [("0.87  (0.78-0.97)", None), ("Death\nfrom", None)], "refuse": ["0.87", "Death"]}},
    "hand_binding.py:sub:caf616cd71": {
        "kind": "search", "what": "_plain: strip XML tags from a cell / caption",
        "plants": {"accept": [("<td>0.87</td>", None), ("<italic>n</italic> (%)", None)],
                   "refuse": ["p &lt; 0.05", "n (%)"]}},
    "hand_binding.py:split:59b745f04e": {
        "kind": "split", "what": "_sentences: split after ').' when a digit starts the next sentence",
        "plants": {"accept": [("p=0.067). 2347 (47.4%) participants", ["p=0.067).", "2347 (47.4%) participants"])],
                   "refuse": ["p=0.067). The rate", "(p=0.067) 2347 participants"]}},
    "hand_binding.py:findall:1af9a0dc3c": {
        "kind": "search", "what": "_cells: the content of each <td>/<th> cell",
        "plants": {"accept": [('<td align="left">0.87</td>', ("0.87",)), ("<th>HR</th>", ("HR",))],
                   "refuse": ["<tr></tr>", "<thead>x</thead>"]}},
    "hand_binding.py:finditer:2fa8c78f40": {
        "kind": "search", "what": "table_rows: each <table-wrap> block",
        "plants": {"accept": [('<table-wrap id="t1"><table></table></table-wrap>', None), ("<table-wrap>\nx\n</table-wrap>", None)],
                   "refuse": ["<table-wrap-foot>note</table-wrap-foot>", "<table>x</table>"]}},
    "hand_binding.py:findall:d83cacfc5a": {
        "kind": "search", "what": "table_rows: the table caption",
        "plants": {"accept": [("<caption><p>Table 2</p></caption>", ("<p>Table 2</p>",))],
                   "refuse": ["<title>Table 2</title>", "caption: Table 2"]}},
    "hand_binding.py:findall:3ab362c751": {
        "kind": "search", "what": "table_rows: the column-header block",
        "plants": {"accept": [("<thead><tr><th>A</th></tr></thead>", None)], "refuse": ["<tbody></tbody>", "<th>A</th>"]}},
    "hand_binding.py:search:b44342a693": {
        "kind": "search", "what": "table_rows: the table body",
        "plants": {"accept": [("<tbody><tr><td>1</td></tr></tbody>", ("<tr><td>1</td></tr>",))],
                   "refuse": ["<thead></thead>", "<tbody/>"]}},
    "hand_binding.py:findall:ea304f7fe8": {
        "kind": "search", "what": "table_rows: each table row (<tr> ... </tr>, with or without attributes)",
        "plants": {"accept": [("<tr><td>1</td></tr>", None),
                              ('<tr style="border-bottom: solid 1px"><td>Death</td><td>12 (3.1)</td></tr>', None)],
                   "refuse": ["<td>1</td>", "<thead></thead>"]}},
    "hand_binding.py:search:159a89219d": {
        "kind": "search", "what": "table_rows: a single-cell row carrying a digit is data, not a section heading",
        "plants": {"accept": [("Table 2", None), ("12 months", None)], "refuse": ["Primary outcome", "Heart failure"]}},
    "hand_binding.py:findall:e1bb2e6e84": {
        "kind": "search", "what": "table_rows: the table footnotes",
        "plants": {"accept": [("<table-wrap-foot><p>HR, hazard ratio</p></table-wrap-foot>", ("<p>HR, hazard ratio</p>",))],
                   "refuse": ["<fn>HR, hazard ratio</fn>", "<table-wrap></table-wrap>"]}},
    "hand_binding.py:_TEXT_TABLES_MARK": {
        "kind": "search", "what": "text_table_rows / prose_of: the '=== TABLES' line opening the flattened tables section",
        "plants": {"accept": [("Body text\n=== TABLES (3) ===\nTABLE 1", None), ("=== TABLES ===", None)],
                   "refuse": ["== TABLES ==", "see === TABLES below"]}},
    "hand_binding.py:search:b4ef0d080a": {
        "kind": "search", "what": "text_table_rows: a flattened row's cells carry a numeric result (count (pct), decimal, bare integer)",
        "plants": {"accept": [("120 (12.5)", None), ("0.87", None), ("120", None)],
                   "refuse": ["Placebo", "HR (95% CI)"]}},
    "hand_binding.py:search:159a89219d#2": {
        "kind": "search", "what": "text_table_rows: a single-cell row carrying a digit is data, not a section heading",
        "plants": {"accept": [("Week 52", None), ("3", None)], "refuse": ["Secondary outcomes", "Safety"]}},
    "hand_binding.py:sub:2fa8c78f40": {
        "kind": "search", "what": "prose_of: drop <table-wrap> blocks from the prose",
        "plants": {"accept": [("<table-wrap><table/></table-wrap>", None)],
                   "refuse": ["<table-wrap-foot>x</table-wrap-foot>", "<p>text</p>"]}},
    "hand_binding.py:sub:ddb5c10500": {
        "kind": "search", "what": "prose_of: drop the reference list from the prose",
        "plants": {"accept": [("<ref-list><ref>x</ref></ref-list>", None), ('<ref-list id="r1">\nx\n</ref-list>', None)],
                   "refuse": ["<ref>x</ref>", "<p>references</p>"]}},
    "hand_binding.py:sub:2abf06a9a2": {
        "kind": "search", "what": "prose_of: drop a front-matter / back-matter element (compiled with tag='back')",
        "bind": {"tag": "back"},
        "plants": {"accept": [("<back><ack>Supported by X</ack></back>", None), ('<back id="b1">\nx\n</back>', None)],
                   "refuse": ["<background>x</background>", "<body>x</body>"]}},
    "hand_binding.py:sub:e6e9990818": {
        "kind": "search", "what": "prose_of: drop <article-id> elements",
        "plants": {"accept": [('<article-id pub-id-type="pmid">27295427</article-id>', None)],
                   "refuse": ["<article-title>x</article-title>", "article id 27295427"]}},
    "hand_binding.py:sub:8782f4efdb": {
        "kind": "search", "what": "prose_of: drop citation markers (<xref> ... </xref>)",
        "plants": {"accept": [('<xref ref-type="bibr" rid="R10">10</xref>', None)],
                   "refuse": ["<ext-link>x</ext-link>", "xref 10"]}},
    "hand_binding.py:sub:caf616cd71#2": {
        "kind": "search", "what": "prose_of: strip the remaining XML tags",
        "plants": {"accept": [("<p>Death occurred</p>", None), ("<sec id='s1'>", None)],
                   "refuse": ["p &lt; 0.05", "Death occurred"]}},
    "hand_binding.py:sub:575187a28f": {
        "kind": "search", "what": "_family_match_tolerant: strip a word-final s (plural tolerance, folded text side)",
        "plants": {"accept": [("gastrointestinal adverse events", None)], "refuse": ["an adverse event", "death"]}},
    "hand_binding.py:sub:575187a28f#2": {
        "kind": "search", "what": "_family_match_tolerant: strip a word-final s (plural tolerance, keyword side)",
        "plants": {"accept": [("serious adverse events", None)], "refuse": ["hypoglycemia", "event"]}},
    "hand_binding.py:sub:07d45602cf": {
        "kind": "search", "what": "_label_definition: non-letters in a table label become spaces",
        "plants": {"accept": [("3-point mace", None), ("primary (composite)", None)],
                   "refuse": ["primary composite outcome", "mace"]}},
    "hand_binding.py:_RESULT_PAREN": {
        "kind": "search", "what": "_owning_clause: a parenthesised result carrying its confidence interval",
        "plants": {"accept": [("fatal or hospitalized HF (HR, 0.70; 95% CI, 0.51-0.96)", None),
                              ("[hazard ratio 0.87, CI 0.78-0.97]", None),
                              ("(risk reduction, 26 percent; 95 percent confidence interval, 18 to 34 percent)", None)],
                   "refuse": ["(n=4,687)", "(95% of patients)", "(HR, 0.78)"]}},
    "hand_binding.py:_LEADING_JOIN": {
        "kind": "search", "what": "_owning_clause: strip a leading conjunction from an attached clause",
        "plants": {"accept": [(", as was fatal or hospitalized HF", None), ("and hospitalized HF alone", None),
                              ("whereas placebo", None)],
                   "refuse": ["andexanet alfa", "hospitalized HF"]}},
    "hand_binding.py:match:43cb536653": {
        "kind": "search", "what": "_direction_ok: a declared comparator direction 'A vs B' / 'A versus B' (groups A, B)",
        "plants": {"accept": [("Empagliflozin vs placebo", ("Empagliflozin", "placebo")),
                              ("colchicine versus placebo", ("colchicine", "placebo")),
                              ("A vs. B", ("A", "B"))],
                   "refuse": ["empagliflozin compared with placebo", "versus placebo"]}},
}
