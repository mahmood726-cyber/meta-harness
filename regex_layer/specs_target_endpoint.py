"""Plants for the regex sites of harness/target_endpoint.py (keys as regex_layer.inventory names them).

Texts are written as the code sees them: sites reached through _fold() / .lower() get lowercase, folded input
(e.g. 'cv ' already rewritten to 'cardiovascular ', 'non-cardiovascular' already rewritten to 'noncv' where the site
reads s_cv); _EFFECT_RE and the sentence split read raw abstract text.
"""

SITE_SPECS: dict = {
    'target_endpoint.py:_WORSENING_HF': {
        "kind": 'search', "what": 'title_components: expand worsening heart failure in a composite title',
        "plants": {"accept": [('worsening heart failure', None)],
                   "refuse": ['stable heart failure']}},
    'target_endpoint.py:_ANCHOR_RX': {
        "kind": 'search', "what": '_anchors: identify the event from which a follow-up clock starts',
        "plants": {"accept": [('after hospital discharge', ('discharge', None))],
                   "refuse": ['before discharge']}},
    'target_endpoint.py:_BACKGROUND': {
        "kind": 'search', "what": '_definition_sentences: distinguish background uncertainty from an endpoint definition',
        "plants": {"accept": [('the effect is unknown', None)],
                   "refuse": ['the outcome was death']}},
    'target_endpoint.py:_COMPARISON_PREFIX': {
        "kind": 'search', "what": 'registry_outcome_match: detect comparison words in a registry label',
        "plants": {"accept": [('randomization comparison', None)],
                   "refuse": ['influenza mortality']}},
    'target_endpoint.py:_COX': {
        "kind": 'search', "what": 'event_process: recognize Cox or proportional-hazards analysis',
        "plants": {"accept": [('cox model', None)],
                   "refuse": ['negative binomial model']}},
    'target_endpoint.py:_DEATH_OR': {
        "kind": 'split', "what": '_death_composite: split candidate event alternatives',
        "plants": {"accept": [('death or ventilation', ['death', 'ventilation'])],
                   "refuse": ['mortality']}},
    'target_endpoint.py:_DEFINING': {
        "kind": 'search', "what": '_definition_sentences: recognize endpoint-defining language',
        "plants": {"accept": [('a composite of death or stroke', None)],
                   "refuse": ['the effect is unknown']}},
    'target_endpoint.py:_FIRST_EVENT': {
        "kind": 'search', "what": 'event_process: identify a first-event or patients-with-event statement',
        "plants": {"accept": [('time to first admission', None)],
                   "refuse": ['recurrent admissions']}},
    'target_endpoint.py:_GENERIC_PREFIX': {
        "kind": 'search', "what": 'registry_outcome_match: strip generic endpoint-label words before population checks',
        "plants": {"accept": [('primary outcome', None)],
                   "refuse": ['influenza']}},
    'target_endpoint.py:_IN_HOSPITAL': {
        "kind": 'search', "what": '_windows: identify a hospital-stay time window',
        "plants": {"accept": [('until hospital discharge', None)],
                   "refuse": ['during outpatient follow-up']}},
    'target_endpoint.py:_LABELLED_COMPOSITE': {
        "kind": 'search', "what": '_labelled_definitions: capture a composite body and its parenthesized label',
        "plants": {"accept": [('composite of death or stroke (two-point)', ('death or stroke', 'two-point'))],
                   "refuse": ['composite of death or stroke']}},
    'target_endpoint.py:_MORTALITY': {
        "kind": 'search', "what": 'registry_outcome_match / _death_composite: detect mortality or survival language',
        "plants": {"accept": [('all-cause mortality', None)],
                   "refuse": ['hospitalization']}},
    'target_endpoint.py:_MORT_QUALIFIER': {
        "kind": 'search', "what": '_death_composite: remove settings and mortality qualifiers before testing residual events',
        "plants": {"accept": [('intensive care', None)],
                   "refuse": ['ventilation']}},
    'target_endpoint.py:_NEGATED_BEFORE': {
        "kind": 'search', "what": '_names_excluded_population: identify negation preceding a population mention',
        "plants": {"accept": [('patients without ', None)],
                   "refuse": ['patients with ']}},
    'target_endpoint.py:_NOT_DEATH': {
        "kind": 'search', "what": 'registry_outcome_match: detect alive/discharge outcomes incompatible with death',
        "plants": {"accept": [('days alive', None)],
                   "refuse": ['days until death']}},
    'target_endpoint.py:_OPEN_ENDED': {
        "kind": 'search', "what": '_timepoint_agreement: recognize an unconstrained end-of-study window',
        "plants": {"accept": [('trial end', None)],
                   "refuse": ['30 days']}},
    'target_endpoint.py:_PATIENT_COUNTS': {
        "kind": 'search', "what": 'event_process: identify explicit counts of patients with events rather than denominators',
        "plants": {"accept": [('occurred in 12 patients', None)],
                   "refuse": ['assessed in 120 patients']}},
    'target_endpoint.py:_POP_PHRASE': {
        "kind": 'search', "what": 'registry_outcome_match: capture a disease population stated in an outcome body',
        "plants": {"accept": [('in patients with influenza', ('influenza',))],
                   "refuse": ['patients without influenza']}},
    'target_endpoint.py:_RECURRENT_METHOD': {
        "kind": 'search', "what": 'event_process: identify explicit recurrent-event analysis methods',
        "plants": {"accept": [('negative binomial model', None), ('lwyy proportional rates model', None),
                              ('semiparametric proportional-rates model', None)],
                   "refuse": ['cox model', 'proportional hazards model']}},
    'target_endpoint.py:_TIME_OR_STOP': {
        "kind": 'search', "what": '_death_composite: remove time and generic count words before testing event content',
        "plants": {"accept": [('within 30 days', None)],
                   "refuse": ['ventilation']}},
    'target_endpoint.py:_TOTAL_EVENTS': {
        "kind": 'search', "what": 'event_process: identify total or recurrent-event counting',
        "plants": {"accept": [('total heart failure hospitalizations', None),
                              ('events included in the composite endpoint of cv death', None),
                              ('rate ratio (lwyy proportional rates model)', None)],
                   "refuse": ['recurrent vte', 'subjects included in the composite endpoint of cv death']}},
    'target_endpoint.py:_TOTAL_NEGATED_AFTER': {
        "kind": 'search', "what": 'event_process: detect exclusion following a total-event phrase',
        "plants": {"accept": [(' were not counted', None)],
                   "refuse": [' were counted']}},
    'target_endpoint.py:_TOTAL_NEGATED_BEFORE': {
        "kind": 'search', "what": 'event_process: detect exclusion immediately preceding a total-event phrase',
        "plants": {"accept": [('excluding ', None)],
                   "refuse": ['including ']}},
    'target_endpoint.py:_WINDOW': {
        "kind": 'search', "what": '_windows: capture normalized numeric follow-up windows',
        "plants": {"accept": [('28-90 days', ('28', '90', 'day', None, None, None, None))],
                   "refuse": ['during hospitalization']}},
    'target_endpoint.py:findall:4016d0ec8a': {
        "kind": 'search', "what": '_title_parts: capture parenthetical candidate component enumerations',
        "plants": {"accept": [('vte (dvt / pe)', ('dvt / pe',))],
                   "refuse": ['vte']}},
    'target_endpoint.py:findall:55411db8ac': {
        "kind": 'search', "what": '_row_names_part: collect uppercase abbreviations from raw row text',
        "plants": {"accept": [('Stroke/SEE', None)],
                   "refuse": ['stroke/see']}},
    'target_endpoint.py:findall:96f7c78bb6': {
        "kind": 'search', "what": '_part_words: tokenize folded title or row words of at least three characters',
        "plants": {"accept": [('systemic embolism', None)],
                   "refuse": ['mi 12']}},
    'target_endpoint.py:findall:96f7c78bb6#2': {
        "kind": 'search', "what": '_row_names_part: tokenize sorted folded part words to derive initials',
        "plants": {"accept": [('embolism systemic', None)],
                   "refuse": ['mi 12']}},
    'target_endpoint.py:finditer:2d7cf5318e': {
        "kind": 'search', "what": '_names_excluded_population: locate a whole excluded population term before negation checks',
        "bind": {'p': 'influenza'},
        "plants": {"accept": [('with influenza', None)],
                   "refuse": ['with parainfluenza']}},
    'target_endpoint.py:finditer:82f706181f': {
        "kind": 'search', "what": 'composite_declaration_problem: capture an explicitly unassessed component',
        "plants": {"accept": [('stroke was not assessed', ('stroke',))],
                   "refuse": ['stroke was assessed']}},
    'target_endpoint.py:search:307f8c03f6': {
        "kind": 'search', "what": '_title_parts.readable: recognize an event term in a candidate title part',
        "plants": {"accept": [('nonfatal PE', None)],
                   "refuse": ['peptide']}},
    'target_endpoint.py:search:7480a6002c': {
        "kind": 'search', "what": '_classify: detect remaining general stroke wording after ischemic-stroke removal',
        "plants": {"accept": [('any stroke', None)],
                   "refuse": ['stroke (ischemic)']}},
    'target_endpoint.py:search:84dadd9c38': {
        "kind": 'search', "what": '_death_composite: detect residual event words after removing time and mortality qualifiers',
        "plants": {"accept": [('ventilation', None)],
                   "refuse": ['   ']}},
    'target_endpoint.py:search:92e4e814d8': {
        "kind": 'search', "what": '_classify: identify a narrower ischemic-stroke description',
        "plants": {"accept": [('ischaemic stroke', None)],
                   "refuse": ['hemorrhagic stroke']}},
    'target_endpoint.py:search:9303f4dadd': {
        "kind": 'search', "what": '_components_from_text: identify hospitalization for heart failure in folded text',
        "plants": {"accept": [('hospitalized for heart failure', None)],
                   "refuse": ['hospitalized for pneumonia']}},
    'target_endpoint.py:split:ec12adc24a': {
        "kind": 'split', "what": '_names_excluded_population: reset negation scope at punctuation or contrast',
        "plants": {"accept": [('without diabetes, but influenza', ['without diabetes', ' ', ' influenza'])],
                   "refuse": ['patients without influenza']}},
    'target_endpoint.py:sub:2130bc52f0': {
        "kind": 'search', "what": '_death_composite: formatting helper removing parenthetical details before splitting events',
        "plants": {"accept": [('death (all causes)', None)],
                   "refuse": ['death']}},
    'target_endpoint.py:sub:39dc6f1454': {
        "kind": 'search', "what": '_unhyphen: formatting helper replacing only letter-to-letter hyphens',
        "plants": {"accept": [('all-cause', None)],
                   "refuse": ['30-day']}},
    'target_endpoint.py:sub:4182931ebf': {
        "kind": 'search', "what": '_windows: reorder unit-first timepoints to numeric-first form',
        "plants": {"accept": [('week 12', ('week', '12'))],
                   "refuse": ['12 weeks']}},
    'target_endpoint.py:sub:69b6307f8e': {
        "kind": 'search', "what": '_title_parts: remove the leading composite label before enumerating components',
        "plants": {"accept": [('the composite outcome of death or stroke', None)],
                   "refuse": ['death or stroke']}},
    'target_endpoint.py:sub:72f1aed8e4': {
        "kind": 'search', "what": '_death_composite: normalize an event conjunction to the alternative separator',
        "plants": {"accept": [('death and ventilation', None)],
                   "refuse": ['death/ventilation']}},
    'target_endpoint.py:sub:7b4eac99d8#3': {
        "kind": 'search', "what": '_ws_lower: formatting helper collapsing whitespace before lowercasing',
        "plants": {"accept": [('Heart  Failure', None)],
                   "refuse": ['Heart-Failure']}},
    'target_endpoint.py:sub:7b4eac99d8#4': {
        "kind": 'search', "what": '_labelled_definitions: formatting helper collapsing whitespace in a captured label',
        "plants": {"accept": [('3-point  MACE', None)],
                   "refuse": ['MACE']}},
    'target_endpoint.py:sub:92e4e814d8': {
        "kind": 'search', "what": '_classify: remove ischemic-stroke wording before seeking general stroke',
        "plants": {"accept": [('nonhemorrhagic stroke', None)],
                   "refuse": ['hemorrhagic stroke']}},
    'target_endpoint.py:sub:c4b470f596': {
        "kind": 'search', "what": '_title_parts: formatting helper removing parentheses to check the outer umbrella label',
        "plants": {"accept": [('vte (dvt / pe)', None)],
                   "refuse": ['vte']}},
    'target_endpoint.py:sub:c4b470f596#2': {
        "kind": 'search', "what": '_title_parts: formatting helper removing parentheses before top-level slash splitting',
        "plants": {"accept": [('mortality (all causes)', None)],
                   "refuse": ['mortality']}},
    # ---- named compiled patterns -------------------------------------------------------------------------------
    "target_endpoint.py:_NAMED_COMPOSITE_RX": {
        "kind": "search",
        "what": "_definition_sentences / bind_result_span: the sentence NAMES an endpoint (primary/secondary outcome, MACE, composite)",
        "plants": {"accept": [("the primary outcome was a composite of cardiovascular death, mi, or stroke", None),
                              ("a primary-outcome event occurred", None),
                              ("the primary efficacy measure was the first occurrence of", None),
                              ("3-point mace was reduced", None)],
                   "refuse": ["death from any cause occurred in 10% of patients",
                              "patients were primarily older men",
                              "major adverse events were similar"]}},
    "target_endpoint.py:_QUALIFIER_RX": {
        "kind": "search",
        "what": "_reference_of / _definition_sentences: is the named endpoint primary or secondary (groups sec, pri)",
        "plants": {"accept": [("the key secondary outcome was", ("key secondary", None)),
                              ("the primary end point was", (None, "primary")),
                              ("the second primary outcome was", (None, "second primary"))],
                   "refuse": ["secondary prevention of stroke", "patients were primarily treated"]}},
    "target_endpoint.py:_MACE_RX": {
        "kind": "search",
        "what": "_definition_sentences / bind_result_span: the endpoint is a MACE-type composite",
        "plants": {"accept": [("3-point mace", None), ("major adverse cardiovascular events", None),
                              ("serious vascular events", None)],
                   "refuse": ["major adverse events were similar", "a grimace score", "major bleeding"]}},
    "target_endpoint.py:_ORDINAL_RX": {
        "kind": "search",
        "what": "_reference_of: which numbered primary/secondary endpoint a sentence names (group: the ordinal word)",
        "plants": {"accept": [("the second primary outcome was", ("second",)),
                              ("the first key secondary end point", ("first",))],
                   "refuse": ["the first patient was randomized", "the primary outcome in the first year"]}},
    "target_endpoint.py:_TIMEPOINT_RX": {
        "kind": "search",
        "what": "_reference_of: the timepoint an endpoint is measured at (n unit | n-unit | at unit n)",
        "plants": {"accept": [("death within 30 days", ("30", "days", None, None, None, None)),
                              ("the 90-day mortality", (None, None, "90", "day", None, None)),
                              ("change in hba1c at week 52", (None, None, None, None, "week", "52"))],
                   "refuse": ["patients aged 65 years or older", "in 30 patients with diabetes"]}},
    "target_endpoint.py:_POPULATION_RX": {
        "kind": "search",
        "what": "_reference_of: the analysis population an endpoint sentence names (group: the population)",
        "plants": {"accept": [("in all randomized patients, the rate was", ("all randomized patients",)),
                              ("among patients with diabetes, the hazard ratio was", ("patients with diabetes",))],
                   "refuse": ["in 30 patients with diabetes, death", "in patients, the rate was"]}},
    "target_endpoint.py:_EFFECT_RE": {
        "kind": "search",
        "what": "_published_effect_from_abstract / _definition_sentences: an effect label + estimate + 95% CI (label, est, lo, hi)",
        "plants": {"accept": [("hazard ratio, 0.74; 95% confidence interval [CI], 0.65 to 0.85",
                               ("hazard ratio", "0.74", "0.65", "0.85")),
                              ("odds ratio 1.52, 95% confidence interval 1.10–1.98",
                               ("odds ratio", "1.52", "1.10", "1.98"))],
                   "refuse": ["the hazard ratio, 0.87, was not significant",
                              "odds ratio, 1.5; 90% confidence interval, 1.1 to 2.0",
                              "the hazard ratio was similar across subgroups"]}},
    # ---- inline sites --------------------------------------------------------------------------------------------
    "target_endpoint.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_reference_of: collapse whitespace runs inside a captured population",
        "plants": {"accept": [("patients  with\tdiabetes", None), ("randomized\npatients", None)],
                   "refuse": ["diabetes", "randomized-patients"]}},
    "target_endpoint.py:sub:a7bc694bbb": {
        "kind": "search", "what": "_resolve_reference: punctuation-insensitive key so a repeated definition dedupes",
        "plants": {"accept": [("death, mi, or stroke.", None), ("3-point mace", None)],
                   "refuse": ["stroke", "mace"]}},
    "target_endpoint.py:sub:ff4ae8621b": {
        "kind": "search", "what": "_fold: expand the abbreviation TEAE(s) as safety tables label it",
        "plants": {"accept": [("teaes | 120 (95.2)", None), ("any teae", None)],
                   "refuse": ["tea consumption", "a teaser trial"]}},
    "target_endpoint.py:sub:fce6fbe7f9": {
        "kind": "search", "what": "_fold: expand the abbreviation SAE(s)",
        "plants": {"accept": [("saes were reported in 12%", None), ("any sae", None)],
                   "refuse": ["safety population", "saem score"]}},
    "target_endpoint.py:sub:0b02262c07": {
        "kind": "search", "what": "_fold: expand the abbreviation AE(s)",
        "plants": {"accept": [("aes occurred in 40%", None), ("any ae | 50 (40.0)", None)],
                   "refuse": ["haemoglobin fell", "aerobic exercise"]}},
    "target_endpoint.py:sub:7b4eac99d8#2": {
        "kind": "search", "what": "_fold: collapse whitespace runs in the folded text",
        "plants": {"accept": [("heart  failure\nhospitalization", None), ("mi\tor stroke", None)],
                   "refuse": ["heartfailure", "mi,stroke"]}},
    "target_endpoint.py:search:b01e38dc40": {
        "kind": "search", "what": "_components_from_text: coronary heart disease death named via the CHD abbreviation",
        "plants": {"accept": [("chd death", None), ("death from chd", None)],
                   "refuse": ["chd events were fewer", "death from stroke"]}},
    "target_endpoint.py:sub:cb26b534c7": {
        "kind": "search", "what": "_components_from_text: mask 'non-cardiovascular' so it is not read as cardiovascular death",
        "plants": {"accept": [("non-cardiovascular death", None), ("noncardiovascular death", None),
                              ("non cardiovascular death", None)],
                   "refuse": ["cardiovascular death", "nonfatal cardiovascular events"]}},
    "target_endpoint.py:search:05aff607b5": {
        "kind": "search", "what": "_components_from_text: cardiovascular death named with words between (reads s_cv)",
        "plants": {"accept": [("death due to cardiovascular disease", None), ("cardiovascular-related death", None)],
                   "refuse": ["noncv death", "cardiovascular hospitalization",
                              "death from any cause or cardiovascular hospitalization"]}},
    "target_endpoint.py:search:3cac5c21b4": {
        "kind": "search", "what": "_components_from_text: CV death via a 'cv' that _fold did not expand (cv-death, (cv))",
        "plants": {"accept": [("cv-death", None), ("death (cv)", None)],
                   "refuse": ["noncv death", "death from any cause"]}},
    "target_endpoint.py:search:e0e9b4f7fb": {
        "kind": "search", "what": "_components_from_text: 'vascular death' / 'death from vascular causes' as CV death, not cerebrovascular",
        "plants": {"accept": [("vascular death", None), ("death from vascular causes", None)],
                   "refuse": ["cerebrovascular death", "nonvascular death", "non-vascular death",
                              "peripheral vascular disease"]}},
    "target_endpoint.py:search:c511b01726": {
        "kind": "search", "what": "_components_from_text: transient ischemic attack via the TIA abbreviation",
        "plants": {"accept": [("stroke or tia", None), ("tia (n=4)", None)],
                   "refuse": ["dementia", "initial stroke"]}},
    "target_endpoint.py:search:bb8366c955": {
        "kind": "search", "what": "_components_from_text: HF abbreviation, paired with hospitali[sz] for HF hospitalization",
        "plants": {"accept": [("hospitalized hf alone", None), ("hf hospitalization", None)],
                   "refuse": ["half of patients", "heart rate"]}},
    "target_endpoint.py:search:8c575f0c81": {
        "kind": "search", "what": "_components_from_text: hospitalisation/hospitalization/hospitalized, paired with HF",
        "plants": {"accept": [("hospitalized hf", None), ("hf hospitalisation", None)],
                   "refuse": ["in-hospital death", "hospital discharge"]}},
    "target_endpoint.py:search:2535b7ece1": {
        "kind": "search", "what": "_components_from_text: a heart-failure DEATH component (fatal HF / death from HF)",
        "plants": {"accept": [("fatal or hospitalized hf", None), ("death from heart failure", None),
                              ("heart failure death", None)],
                   "refuse": ["nonfatal hf", "hospitalization for heart failure",
                              "non-fatal stroke or hf hospitalization"]}},
    "target_endpoint.py:search:bb8366c955#2": {
        "kind": "search", "what": "_components_from_text: HF abbreviation, paired with 'urgent visit' for urgent HF visit",
        "plants": {"accept": [("urgent visit for hf", None), ("hf urgent visit", None)],
                   "refuse": ["urgent visit for chest pain", "half"]}},
    "target_endpoint.py:search:3994cff820": {
        "kind": "search", "what": "_components_from_text: a registry measure declared as a recurrent-event analysis",
        "plants": {"accept": [("hf hospitalizations analysed as recurrent event", None),
                              ("analyzed as a recurrent event", None), ("recurrent-event analysis", None)],
                   "refuse": ["time to first event analysis", "recurrent stroke"]}},
    "target_endpoint.py:search:c2741ecf04": {
        "kind": "search", "what": "_components_from_text: myocardial infarction via the MI abbreviation",
        "plants": {"accept": [("non-fatal mi", None), ("mi, stroke", None)],
                   "refuse": ["mixed model", "admission", "mild"]}},
    "target_endpoint.py:search:722dd482f3": {
        "kind": "search", "what": "_definition_sentences: arm counts ('458 of 3686') mark a RESULT sentence, never a definition",
        "plants": {"accept": [("occurred in 458 of 3686 patients", None), ("12 of 100", None)],
                   "refuse": ["2 of the 3 components", "of 3686 patients"]}},
    "target_endpoint.py:search:a8e12cadeb": {
        "kind": "search", "what": "_definition_sentences: a 'primary ... measure/variable' definition marks the span primary",
        "plants": {"accept": [("the primary efficacy measure was", None), ("primary outcome variables", None)],
                   "refuse": ["the primary outcome was", "measured primarily"]}},
    "target_endpoint.py:search:bd7f86d57b": {
        "kind": "search", "what": "_effect_analysis: registry paramType abbreviated HR -> hazard-ratio scale",
        "plants": {"accept": [("hazard ratio (hr)", None), ("hr", None)],
                   "refuse": ["change in hrqol", "risk ratio (rr)"]}},
    "target_endpoint.py:search:8cbbf29039": {
        "kind": "search", "what": "_effect_analysis: registry paramType abbreviated RR -> risk-ratio scale",
        "plants": {"accept": [("relative risk (rr)", None), ("rr", None)],
                   "refuse": ["arr", "risk difference (rd)"]}},
    "target_endpoint.py:search:dafd757c05": {
        "kind": "search", "what": "_effect_analysis: registry paramType abbreviated OR -> odds-ratio scale",
        "plants": {"accept": [("odds ratio (or)", None), ("or", None)],
                   "refuse": ["other", "mean difference (final values)"]}},
    "target_endpoint.py:split:4634658391": {
        "kind": "split", "what": "_published_effect_from_abstract: fallback sentence split after . ? or !",
        "plants": {"accept": [("Death fell. Stroke rose.", ["Death fell.", "Stroke rose."]),
                              ("Was it lower? Yes!  No.", ["Was it lower?", "Yes!", "No."])],
                   "refuse": ["HR 0.80 (95% CI 0.70-0.90)", "rate 0.87 per 100"]}},
}
