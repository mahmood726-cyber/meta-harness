"""Plants for the regex sites added by lane NR V1.0.1's label fixes (statins-older-adults and ticagrelor reviews):
harness/subgroup_provenance.py, harness/composite_label.py, harness/k2.py (conflict-claim guard) and rob2._DEATH_TERM.
Texts are written as each function reads them (all these patterns are re.I unless stated)."""

SITE_SPECS: dict = {
    # ---- harness/subgroup_provenance.py -------------------------------------------------------------------------------
    "subgroup_provenance.py:_BARE_POST_HOC": {
        "kind": "search", "what": "a bare 'post hoc' that is not negated ('were not post hoc')",
        "plants": {"accept": [("This post hoc analysis examined participants aged 70 years or older.", None),
                              ("The subgroup comparison was post-hoc.", None)],
                   "refuse": ["The subgroup analyses were not post hoc.", "Posthumous data were excluded."]}},
    "subgroup_provenance.py:_SUBGROUP_CUE": {
        "kind": "search", "what": "the clause is about a subgroup (subgroup, cut-point, threshold, strata, age, this analysis)",
        "plants": {"accept": [("a post hoc subgroup comparison", None), ("the age cut-point", None),
                              ("This exploratory analysis", None)],
                   "refuse": ["a post hoc sensitivity analysis excluded non-adherent participants", "the dose was doubled"]}},
    "subgroup_provenance.py:_POST_HOC": {
        "kind": "search", "what": "a subgroup / cut-point defined AFTER trial completion, 'not prespecified', 'retrospectively defined'",
        "plants": {"accept": [("LIMITATION: Effect estimates from this exploratory analysis with age cut-point chosen after "
                               "trial completion should be viewed in the context of the overall trial results.", None),
                              ("Exploratory subgroup analyses were devised after trial completion.", None),
                              ("The subgroups were not prospectively prespecified.", None),
                              ("the threshold was retrospectively defined", None)],
                   "refuse": ["The subgroups were prespecified, with cut-points not selected after trial completion.",
                              "The subgroup cut-points were defined before unblinding."]}},
    "subgroup_provenance.py:_PRESPECIFIED": {
        "kind": "search", "what": "an explicit pre-specification of the subgroup",
        "plants": {"accept": [("The age subgroups were prespecified in the statistical analysis plan.", None),
                              ("We evaluated a priori subgroups defined in the protocol.", None),
                              ("The subgroups had been predefined in the protocol before recruitment.", None),
                              ("examined subgroups defined a priori in the protocol", None)],
                   "refuse": ["This secondary analysis of a randomized trial examined treatment effects in subgroups.",
                              "The primary end point was prespecified."]}},
    "subgroup_provenance.py:_SENT": {
        "kind": "search", "what": "a sentence boundary that is not after 'vs.', 'e.g.', 'i.e.' or 'et al.'",
        "plants": {"accept": [("The subgroup was post hoc. The trial was large.", None),
                              ("It was prespecified; Results followed.", None)],
                   "refuse": ["The comparison of Drug A vs. Drug B was post hoc.",
                              "The subgroup analyses, e.g. Asian participants, were post hoc.",
                              "the Smith et al. Risk Index was used"]}},
    "subgroup_provenance.py:sub:7b4eac99d8": {
        "kind": "search", "what": "_sentences: collapse whitespace runs before splitting",
        "plants": {"accept": [("post  hoc\nsubgroup", None), ("age\tcut-point", None)], "refuse": ["posthoc", "subgroup"]}},
    "subgroup_provenance.py:_PRESPEC_PROSE": {
        "kind": "search", "what": "an asserted 'pre-specified' qualifying a subgroup in served prose",
        "plants": {"accept": [("one pre-specified JUPITER >=70-years subgroup", None),
                              ("pre-specified age 65-80 ITT subgroup (of an 18-80 enrolment)", None)],
                   "refuse": ["the pre-specified primary end point", "one JUPITER >=70-years subgroup"]}},
    "subgroup_provenance.py:_PRESPEC_UNIT_LABEL": {
        "kind": "search", "what": "the page's generated unit label calls a subgroup pre-specified",
        "plants": {"accept": [("k = 2 (1 trial + 1 pre-specified subgroup of JUPITER)", None),
                              ("k = 1 (1 pre-specified subgroup of age 65-80 ITT subgroup)", None)],
                   "refuse": ["k = 2 (1 trial + 1 post-hoc subgroup of JUPITER)",
                              "report the outcome for a pre-specified subgroup (e.g. Wade et al.)"]}},
    # ---- harness/composite_label.py ----------------------------------------------------------------------------------
    "composite_label.py:THREE_POINT_CLAIM": {
        "kind": "search", "what": "a served name or label claims a 3-point composite",
        "plants": {"accept": [("3-point major adverse cardiovascular events", None), ("three-point MACE", None),
                              ("3 point MACE", None)],
                   "refuse": ["4-point MACE", "a 13-point scale", "Major adverse cardiovascular events"]}},
    "composite_label.py:MACE_CLAIM": {
        "kind": "search", "what": "a served name claims MACE / major (adverse) cardiovascular or vascular events",
        "plants": {"accept": [("Major vascular events", None), ("Major adverse cardiovascular events", None),
                              ("Major vascular events / MACE", None)],
                   "refuse": ["Major bleeding", "grimace score", "Major adverse events"]}},
    "composite_label.py:_COMPOSITE_NAME": {
        "kind": "search", "what": "the outcome name is a composite (MACE, major (adverse) (cardio)vascular, composite)",
        "plants": {"accept": [("Composite cardiovascular death or heart-failure hospitalization", None),
                              ("Major adverse cardiovascular events", None), ("Total cardiovascular events", None)],
                   "refuse": ["All-cause mortality", "Major bleeding"]}},
    "composite_label.py:_STROKE_SUBTYPE": {
        "kind": "search", "what": "a stroke component carries a subtype (ischaemic / haemorrhagic), kept visible",
        "plants": {"accept": [("ISCHEMIC STROKE", None), ("ischaemic stroke", None), ("haemorrhagic stroke", None),
                              ("hemorrhagic stroke", None)],
                   "refuse": ["stroke", "transient ischemic attack"]}},
    # ---- harness/k2.py (generated text about a k=2 direction conflict) ----------------------------------------------
    "k2.py:_POPULATION_FACTOR": {
        "kind": "search", "what": "the sentence names a population factor (region, ethnicity, East Asian, race, geography)",
        "plants": {"accept": [("PHILO enrolled East Asian patients", None), ("regional differences", None),
                              ("by ethnicity", None), ("Japanese, Korean and Taiwanese patients", None)],
                   "refuse": ["the two trials conflict in direction", "PLATO HR 0.84"]}},
    "k2.py:_EXPLAINS": {
        "kind": "search", "what": "the sentence explains or attributes (explain, account for, attributable, driven by, due to)",
        "plants": {"accept": [("the difference may be explained by ethnicity", None), ("driven by regional practice", None),
                              ("attributable to the East Asian population", None)],
                   "refuse": ["the two trials conflict in direction", "shown alone as the pre-named anchor trial"]}},
    "k2.py:_EQUIVALENCE": {
        "kind": "search", "what": "the sentence reads as equivalence / non-inferiority / no benefit / no difference",
        "plants": {"accept": [("ticagrelor is equivalent to clopidogrel", None), ("there was no benefit", None),
                              ("no significant difference between the drugs", None), ("similar efficacy", None)],
                   "refuse": ["the computed pooled effect is withheld by display policy",
                              "the two trials conflict in direction"]}},
    "k2.py:_SENT_SPLIT": {
        "kind": "search", "what": "a sentence boundary in generated text",
        "plants": {"accept": [("PLATO alone. PHILO alone.", None), ("withheld; shown alone", None)],
                   "refuse": ["HR 0.84 (95% CI 0.77-0.92)", "PLATO alone"]}},
    "k2.py:_WS": {
        "kind": "search", "what": "conflict_claim_violations: collapse whitespace runs",
        "plants": {"accept": [("no  benefit", None), ("East\nAsian", None)], "refuse": ["nobenefit", "PLATO"]}},
    "k2.py:_CONFLICT_SUBJECT": {
        "kind": "search", "what": "the sentence is about the conflict / difference between the trials",
        "plants": {"accept": [("The conflict reflects regional differences.", None), ("the discordance between PLATO and PHILO", None),
                              ("heterogeneity between the trials", None)],
                   "refuse": ["The regional recruitment table reflects the trial locations.", "PLATO alone"]}},
    "k2.py:_NEGATED": {
        "kind": "search", "what": "a withheld or negated proposition (not the claim itself)",
        "plants": {"accept": [("The conflict cannot be explained by ethnicity.", None),
                              ("No conclusion can be drawn about equivalence.", None),
                              ("The treatments are not equivalent.", None)],
                   "refuse": ["Ticagrelor was equivalent to clopidogrel.",
                              "The discordance may be explained by the East Asian population."]}},
    # ---- harness/population_qualifier.py (k=1: the trial's own population) --------------------------------------------
    "population_qualifier.py:_ELIGIBILITY_SENTENCE": {
        "kind": "search", "what": "an eligibility sentence (who could be randomised)",
        "plants": {"accept": [("Those trial participants with hypoxia and evidence of systemic inflammation were eligible "
                               "for random assignment in a 1:1 ratio.", None),
                              ("Inclusion criteria were age over 18 years and pneumonia.", None)],
                   "refuse": ["Overall, 621 (31%) of the 2022 patients allocated tocilizumab died within 28 days.",
                              "Eligibility was not reported."]}},
    "population_qualifier.py:_RESTRICTION": {
        "kind": "search", "what": "a restricting condition named in the eligibility sentence, with its own definition",
        "plants": {"accept": [("hypoxia (oxygen saturation <92% on air or requiring oxygen therapy)", None),
                              ("systemic inflammation (C-reactive protein ≥75 mg/L)", None),
                              ("receiving invasive mechanical ventilation", None)],
                   "refuse": ["adults admitted to hospital", "a 1:1 ratio"]}},
    "population_qualifier.py:_COTREATMENT": {
        "kind": "search", "what": "the share of participants on a named co-treatment",
        "plants": {"accept": [("including 3385 (82%) patients receiving systemic corticosteroids", None),
                              ("56.9% received dexamethasone", None)],
                   "refuse": ["621 (31%) of the 2022 patients allocated tocilizumab died", "82% were men"]}},
    "population_qualifier.py:_SENT": {
        "kind": "search", "what": "a sentence boundary",
        "plants": {"accept": [("were eligible. Overall, 621 died", None)], "refuse": ["C-reactive protein ≥75 mg/L", "82%"]}},
    "population_qualifier.py:_WS": {
        "kind": "search", "what": "_sentences: collapse whitespace runs",
        "plants": {"accept": [("hypoxia  and\ninflammation", None)], "refuse": ["hypoxia", "82%"]}},
    # ---- harness/rob2.py (the D5 identity check) ---------------------------------------------------------------------
    "rob2.py:_UNTYPED_CV_DEATH": {
        "kind": "search", "what": "a CV-like death the vocabulary does not type (identity with CV death undecided)",
        "plants": {"accept": [("Death From Vascular Causes, Myocardial Infarction (MI), and Stroke", None),
                              ("time to coronary heart disease death", None), ("cardiac death", None)],
                   "refuse": ["Death from cancer or myocardial infarction", "all-cause mortality", "Fatal and Nonfatal MI"]}},
}
