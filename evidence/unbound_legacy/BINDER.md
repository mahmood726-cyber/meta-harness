# Single-outcome binder evidence

Pinned source: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. Local patch only; no commit, release, registry binding, or served-data regeneration.

## Classification comparison

| Class | Before | After |
|---|---:|---:|
| EXACT_TARGET | 8 | 10 |
| ENDPOINT_UNBOUND | 43 | 41 |
| NOT_AN_ABSTRACT_ROW | 14 | 14 |

All 65 rows compared by topic, outcome and identifier. The only class changes are the two ENDPOINT_UNBOUND -> EXACT_TARGET rows below. All eight previously EXACT rows and all 14 non-abstract rows are unchanged. This preserves existing classifications; it does not independently certify their correctness.

## Patch and conservative coverage

The fallback runs only after the existing component binder abstains. It requires a full name, definition, or explicit synonym in the estimate's own adjacent outcome slot. Retrieval `keywords` are not treated as equivalent outcome names: a source-defined abbreviation is accepted only if it also occurs in the declared keywords. The held AAD expansion is resolved from each abstract, not from a topic-specific dictionary. Orthographic normalization handles whitespace, hyphens, diarrhoea/diarrhea, and reversible legacy encoding damage.

Only one source-reported ratio is supported. The point must match the explicit `effect` argument, or (for the existing three-argument API) an estimate actually present in the source quotation. The abstract-candidate caller now supplies its effect. The requested classifier script is unchanged and uses the three-argument API; a quotation truncated before its estimate therefore remains unbound in this report. Count-derived rows, transformed relative-risk reductions, long/non-adjacent outcome descriptions and multi-effect sentences remain abstentions. These are coverage limitations, not proof that their underlying results concern the wrong outcome.

Composite declarations (including unrecognized component vocabularies and trial annotation component lists), subgroup/secondary qualifiers, unresolved timepoints/populations, and ambiguous outcome clauses cannot use this fallback. Existing GLP-1/composite behavior remains on the original path. `_identity_missing` and admissibility are unchanged.

## Static versus dynamic disclosure

| Item | Static rule or dynamic evidence |
|---|---|
| Grammar, qualifier rejection, unique-estimate requirement | Static conservative parsing rules |
| Outcome identity terms | Dynamic topic spec; no per-topic synonym table |
| Abbreviation expansion | Dynamic held abstract plus declared keywords |
| Sentences, PMIDs, effects | Pinned git records and impact rows; newly bound points checked against held sentences |
| Counts and class changes below | Computed from baseline and rerun JSON |

## Every newly bound row

### probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 35727573

Row point: 0.81. single outcome: declared phrase 'aad' adjacent to the row's estimate.

> Compared with placebo (n = 155), the probiotic (n = 158) had no effect on risk of AAD (relative risk [RR], 0.81; 95% CI, 0.49-1.33).

### probiotics-aad-prevention / Antibiotic-associated diarrhoea / PMID 24772726

Row point: 0.7. single outcome: declared phrase 'aad' adjacent to the row's estimate.

> The relative risk for AAD was 0.7 with the 95% CI being 0.4 to 1.2.

## Every remaining unbound abstract row

| Topic | Outcome | PMID | Reason |
|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | Mortality | PMID 35041780 | single outcome: timepoint identity is missing or different |
| balanced-crystalloids-vs-saline-mortality | Mortality | PMID 34375394 | single outcome: source quotation does not uniquely prefix a held sentence |
| balanced-crystalloids-vs-saline-mortality | New renal-replacement therapy | PMID 35041780 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| colchicine-postop-af | Postoperative atrial fibrillation | PMID 42132185 | single outcome: row point estimate is unavailable or differs from the sentence |
| colchicine-postop-af | Postoperative atrial fibrillation | PMID 32720823 | single outcome: row point estimate is unavailable or differs from the sentence |
| colchicine-postop-af | Postoperative atrial fibrillation | PMID 25172965 | single outcome: subgroup or secondary identity is unresolved |
| colchicine-recurrent-pericarditis | Recurrent pericarditis | PMID 24694983 | single outcome: source quotation does not uniquely prefix a held sentence |
| colchicine-recurrent-pericarditis | Recurrent pericarditis | PMID 21873705 | single outcome: timepoint identity is missing or different |
| colchicine-recurrent-pericarditis | Symptom persistence at 72 hours | PMID 21873705 | single outcome: timepoint identity is missing or different |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | PMID 34876021 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| colchicine-secondary-cv-prevention | Non-cardiovascular death | PMID 32865380 | single outcome: row point estimate is unavailable or differs from the sentence |
| corticosteroids-cap-mortality | All-cause mortality | PMID 36942789 | single outcome: timepoint identity is missing or different |
| corticosteroids-cap-mortality | All-cause mortality | PMID 25688779 | single outcome: timepoint identity is missing or different |
| corticosteroids-cap-mortality | Hyperglycaemia | PMID 25688779 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| corticosteroids-cap-mortality | Hyperglycaemia | PMID 25608756 | single outcome: row point estimate is unavailable or differs from the sentence |
| corticosteroids-covid19-mortality | 28-day all-cause mortality | PMID 32678530 | single outcome: row point estimate is unavailable or differs from the sentence |
| denosumab-vertebral-fracture | New vertebral fracture | PMID 19671655 | single outcome: timepoint identity is missing or different |
| denosumab-vertebral-fracture | Nonvertebral fracture | PMID 19671655 | single outcome: row point estimate is unavailable or differs from the sentence |
| denosumab-vertebral-fracture | Hip fracture | PMID 19671655 | single outcome: row point estimate is unavailable or differs from the sentence |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 24344086 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 19966341 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 22449293 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 21128814 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 23991658 | single outcome: composite identity is outside this fallback |
| doac-vte-recurrence | Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death) | PMID 23808982 | single outcome: composite identity is outside this fallback |
| metformin-pcos-ovulation | Ovulation with metformin added to clomifene | PMID 11172832 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| noac-vs-warfarin-af-stroke | Major bleeding | PMID 24251359 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| noac-vs-warfarin-af-stroke | Major bleeding | PMID 21870978 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 32035998 | single outcome: row point estimate is unavailable or differs from the sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 23932219 | single outcome: row point estimate is unavailable or differs from the sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 18701826 | single outcome: timepoint identity is missing or different |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 18410562 | single outcome: source quotation does not uniquely prefix a held sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 11560298 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 7872284 | single outcome: row point estimate is unavailable or differs from the sentence |
| probiotics-aad-prevention | Antibiotic-associated diarrhoea | PMID 21165295 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| spironolactone-hfref-mortality | All-cause mortality | PMID 10471456 | single outcome: row point estimate is unavailable or differs from the sentence |
| statins-primary-prevention-elderly | Major vascular events | PMID 42670961 | single outcome: row point estimate is unavailable or differs from the sentence |
| tocilizumab-covid19-mortality | 28-day all-cause mortality | PMID 33933206 | single outcome: source quotation does not uniquely prefix a held sentence |
| tocilizumab-covid19-mortality | Serious adverse events | PMID 33631066 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| tocilizumab-covid19-mortality | Serious adverse events | PMID 33332779 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |
| tranexamic-acid-pph | Death due to bleeding | PMID 28456509 | single outcome: requires one source-reported ratio, not counts or multiple/transformed effects |

## Negative plants and the clauses that stop them

| Plant (synthetic) | Defect if accepted | Patch clause |
|---|---|---|
| Mortality or adverse events under AAD; primary-outcome label with an AAD definition elsewhere | Another outcome inherits target identity | Full declared phrase must occupy the ratio's own outcome slot |
| Diarrhoea under diarrhoea-or-vomiting composite | Component substituted for composite | Composite declaration guard, even with no recognized canonical components |
| Subgroup, men-only, secondary, or day-7 result | Restricted population/timepoint substituted for target | Qualifier/population/ordinal guards and timepoint equality |
| Mortality with/and AAD, non-AAD, recurrent AAD, or a trailing men-only qualifier | Incidental, combined, or negated mention treated as target | Qualified/ambiguous prefix guard |
| Correct outcome but row point 0.70 versus sentence 0.81 | Endpoint identity attached to another estimate | Exact point equality |
| Truncated quote with no point | Recovered sentence presumed to be the row's numeric result | Explicit row effect or quoted estimate required |
| Two effects in one sentence | First number silently attached to another outcome | Exactly one ratio required |
| Unexpanded AAD | Acronym guessed from retrieval keyword | Held name-to-abbreviation expansion required |

Tests include positive controls for the exact-point and truncation plants, and validate every previously classified held abstract row. Wrong-outcome plants keep the same ratio and place the correct target definition elsewhere in the abstract, so a whole-abstract keyword fallback would wrongly admit them.

## Reproduction

```text
python evidence/unbound_legacy/classify_legacy_rows.py 3876a62dca66764dff1b4f84d6b43356a1a9e3bb evidence/unbound_legacy/impact_3876a62d.json evidence/unbound_legacy/legacy_rows_classified_binder.json
python -m pytest -q -p no:cacheprovider tests/test_single_outcome_binding.py tests/test_unbound_legacy_failclosed.py
```

Final verification: **33 passed in 67.94s**, using only the two test files above (including held GLP-1/composite controls). `git diff --check` passed. All four output files are UTF-8 without BOM. The final classifier rerun retained the table above; no already-classified row changed class.

## REGISTRY

Pinned source: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. This section extends the committed single-outcome patch `96be01c8`. Local changes only; no commit or served-data regeneration.

### Overall classification comparison

| Class | Single-outcome binder | Registry binder |
|---|---:|---:|
| EXACT_TARGET | 10 | 12 |
| ENDPOINT_UNBOUND | 41 | 47 |
| ENDPOINT_IDENTITY_MISSING | 0 | 6 |
| NOT_AN_ABSTRACT_ROW | 14 | 0 |

All 65 identifiers/outcomes were compared. The 51 abstract rows retain their previous classes. Of the 14 previously labelled NOT_AN_ABSTRACT_ROW, two become EXACT_TARGET, six become ENDPOINT_UNBOUND (measure located, declared identity unresolved), and six become ENDPOINT_IDENTITY_MISSING (no registry result measure or bound arithmetic parents). No row is classified from a matching number alone.

### Binding contract and coverage

The locator replays the existing CT.gov extractor against each measure in the row's own NCT record, requiring the complete emitted source quotation and the complete count or mean/SD/n tuple to match exactly one measure. The impact JSON is intentionally lossy (160-character sources, no continuous tuples), so the report reads each full row from `docs/reviews/<slug>/review.json` at the pinned ref. PMID-to-NCT associations come from that topic's held `records` entry; a registry-only row uses its explicit NCT identifier. The quotes below come from the same pinned `cache/<slug>/records.json` object. Measure indexes are zero-based.

Classification uses the located measure's own title/description, time frame and population. Full declared names, definitions or explicit synonyms are accepted; retrieval keywords do not become synonyms. No new topic synonym lists or inferred expansions are added. Numeric timepoints must match exactly, with baseline zero excluded; ambiguous durations and unresolved nonnumeric labels abstain. Explicit population wording must be present in the measure's population. Composites require the same explicitly enumerated supported components, with named-composite expansion disabled.

The existing target-endpoint registry candidate route and the pipeline registry fallback now use this classifier. Arithmetic identity can be inherited only from explicit parent rows, all independently rebound to held measures and all exact targets with compatible time frames/populations; copied class labels, missing parents and unsupported nested lineage abstain. This is an identity contract, not an arithmetic certification. The six non-CT.gov legacy rows have no supported registry parent lineage. Their prose/labels cannot manufacture it.

Coverage limits: MADRS's declared observed-case/raw-change-score identity is not the complete registry title; sleep-onset latency is not an explicit synonym declaration for subjective sleep latency; Percent change in body weight is not the literal title Change in Body Weight (%). Those six located rows remain unbound under the requested phrase-only rules. This does not assert that the clinical outcomes differ.

Numeric-origin caveat: the existing continuous extractor uses the first class's means/SDs with overall measure denominators. The two semaglutide rows therefore reproduce overall n=407/204 and n=1306/655, while their in-trial classes separately report n=373/189 and n=1212/577. The report preserves both held structures in `registry_numeric_quote`; locating their origin does not validate that denominator choice. Both rows remain unbound. No extraction arithmetic is changed here.

### Static versus dynamic disclosure

| Item | Static rule or dynamic evidence |
|---|---|
| Locator, exact source/tuple equality, ambiguity refusal | Static deterministic contract |
| Identity terms and qualifiers | Dynamic declared spec and located measure; no topic aliases |
| Parent identity | Dynamic explicit parent rows, each rechecked against held measures |
| Measures, arm tuples, PMID/NCT associations and route quotations | Pinned held JSON/git bytes; quoted below |
| AACT/design availability | Inspected held schemas; hashes/design flags do not supply outcome results |
| Counts and class changes | Computed comparison of the two classification JSON files |

### Every former NOT_AN_ABSTRACT_ROW

For all eight topics, `aact_inputs.json` holds `study_dates`, `sponsors`, and `arm_index` values, not raw outcome-result tables. `registry_designs.json` holds design/allocation/masking fields, not outcome measures. These files were inspected and their schema inventories are recorded per row in the rerun JSON. The result-measure quotes below are from `records.json.ctgov_results`. Where none can be located, there is deliberately no fabricated outcome title, description, time frame or population.

#### esketamine-trd-madrs / PMID 37025256 / Observed-case Day-28 raw change-score MADRS MD

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_UNBOUND**. Route: `ctgov_results`. registry measure: no full declared outcome phrase in this measure's title/description.

Held location: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT03434041/0` at the pinned ref.

Title:

> Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score to the End of Double-blind Treatment Phase (Day 28)

Description:

> The MADRS is a clinician-rated scale designed to measure depression severity and detects changes due to antidepressant treatment. The scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel (interest level), pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0 to 60. Higher scores represent a more severe condition. Negative change in score indicates improvement.

Time frame:

> Baseline up to end of the double-blind treatment phase (Day 28)

Population:

> Full analysis set included all randomized participants who received a least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind treatment phase. Here 'N' (number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.

Matched arm tuple (replayed from the quoted measure):

```json
{"mean1": -10.1, "sd1": 10.8, "nc1": 109, "mean2": -8.1, "sd2": 10.26, "nc2": 106}
```

#### esketamine-trd-madrs / PMID 31109201 / Observed-case Day-28 raw change-score MADRS MD

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_UNBOUND**. Route: `ctgov_results`. registry measure: no full declared outcome phrase in this measure's title/description.

Held location: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02418585/0` at the pinned ref.

Title:

> Change From Baseline in Montgomery-Asberg Depression Rating Scale (MADRS) Total Score up to Day 28 in the Double-blind Induction Phase- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis

Description:

> MADRS is clinician-rated scale designed to measure depression severity, and to detect changes due to antidepressant treatment. Scale consists of 10 items (apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, interest level, pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item is not present or is normal) to 6 (severe or continuous presence of symptoms), summed for a total possible score of 0 to 60. Higher scores represent more severe condition.

Time frame:

> Baseline up to Day 28 of Double-blind Induction Phase

Population:

> Full analysis set (FAS) defined as all randomized participants who received at least 1 dose of intranasal study medication, 1 dose of oral antidepressant (AD) medication during double-blind induction phase (D-BIP). Here 'N' (overall number of participants analyzed) signifies number of participants who were evaluable for this outcome measure.

Matched arm tuple (replayed from the quoted measure):

```json
{"mean1": -21.4, "sd1": 12.32, "nc1": 101, "mean2": -17.0, "sd2": 13.88, "nc2": 100}
```

#### esketamine-trd-madrs / NCT02422186 / Observed-case Day-28 raw change-score MADRS MD

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_UNBOUND**. Route: `ctgov_results`. registry measure: no full declared outcome phrase in this measure's title/description.

Held location: `cache/esketamine-trd-madrs/records.json#/ctgov_results/NCT02422186/0` at the pinned ref.

Title:

> Change From Baseline in Montgomery Asberg Depression Rating Scale (MADRS) Total Score up to Endpoint (Double-blind Induction Phase [Day 28])- Mixed-Effects Model Using Repeated Measures (MMRM) Analysis

Description:

> The MADRS is a clinician-rated scale designed to measure depression severity and to detect changes due to antidepressant treatment. The scale consists of 10 items (to evaluates apparent sadness, reported sadness, inner tension, sleep, appetite, concentration, lassitude, inability to feel \[interest level\], pessimistic thoughts, and suicidal thoughts), each of which is scored from 0 (item not present or normal) to 6 (severe or continuous presence of the symptoms), summed for a total possible score range of 0-60. Higher scores represent a more severe condition. Negative change in score indicates improvement.

Time frame:

> Baseline up to Endpoint (Double-blind Induction Phase[Day 28])

Population:

> The full analysis set (FAS) was defined as all randomized participants who received at least 1 dose of intranasal study medication and 1 dose of oral antidepressant medication during the double-blind induction phase. Here, N (Overall number of participants analyzed) signifies number of participants who were evaluable for this endpoint.

Matched arm tuple (replayed from the quoted measure):

```json
{"mean1": -10.0, "sd1": 12.74, "nc1": 63, "mean2": -6.3, "sd2": 8.86, "nc2": 60}
```

#### melatonin-primary-insomnia-sol / PMID 20712869 / Sleep-onset latency

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_UNBOUND**. Route: `ctgov_results`. registry measure: no full declared outcome phrase in this measure's title/description.

Held location: `cache/melatonin-primary-insomnia-sol/records.json#/ctgov_results/NCT00397189/0` at the pinned ref.

Title:

> The Change From Baseline in Subjective Sleep Latency.

Description:

> Sleep latency (SL) after 3 weeks of treatment was assessed by Patient Daily Sleep Diary (National sleep foundation sleep diary). The patients reported subjectively of their SL. The Sleep Diary question 3 (SL) was summarised at baseline (end of the two-week run-in period) and after three weeks double-blind treatment (actual and change from baseline) for each treatment group using descriptive statistics. At each visit, the mean of the seven days prior to the visit were used. For each treatment group, the mean score at visit 3 was compared, adjusting for the visit 2 score. An ANCOVA model was used. Lower score indicates reduction in sleep latency and thus considered improvement

Time frame:

> Baseline and 3 weeks

Population:

> Pre-planned analysis on ITT population age 65-80

Matched arm tuple (replayed from the quoted measure):

```json
{"mean1": -19.1, "sd1": 47.3, "nc1": 137, "mean2": -1.7, "sd2": 47.8, "nc2": 144}
```

#### metformin-pcos-ovulation / PMID 19522426 / Ovulation with metformin added to clomifene

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_IDENTITY_MISSING**. Route: `published_rate`. no registry extraction or explicit bound parent rows; provenance labels are not evidence.

No registry outcome-measure quote is available. Held NCT link: `absent`; that record has 0 held result measures. Title, description, time frame and population remain unbound.

Actual held route quote: `cache/metformin-pcos-ovulation/verified_arms.json` entry `19522426` (also carried on the full review row):

> Ben Ayed 2009, abstract: '32 PCOS women were recruited in the study and equally allocated to the two groups. The ovulation rate in the metformin group was 62.5% compared with 37.5% in the placebo group.' Equal allocation of 32 -> 16 per arm; counts are exact: 62.5% of 16 = 10, 37.5% of 16 = 6 (an S2 add-on-to-clomifene contrast, metformin+CC vs CC+placebo).

The parent proportions/denominators are abstract prose, with no explicit registry parent rows. The route rounds reported proportions into counts; this binder cannot inherit registry identity.

#### metformin-pcos-ovulation / PMID 16769748 / Ovulation with metformin added to clomifene

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_IDENTITY_MISSING**. Route: `published_rate`. no registry extraction or explicit bound parent rows; provenance labels are not evidence.

No registry outcome-measure quote is available. Held NCT link: `absent`; that record has 0 held result measures. Title, description, time frame and population remain unbound.

Actual held route quote: `cache/metformin-pcos-ovulation/verified_arms.json` entry `16769748` (also carried on the full review row):

> Moll 2006 (BMJ, NCT-registered multicentre RCT), abstract: '111 women were allocated to clomifene citrate plus metformin (metformin group) and 114 women were allocated to clomifene citrate plus placebo (placebo group). The ovulation rate in the metformin group was 64% compared with 72% in the placebo group.' Counts recovered as the unique integers consistent with the reported rate and denominator: round(0.64*111)=71 (71/111=63.96% -> '64%'; 70->63%, 72->65%), round(0.72*114)=82 (82/114=71.9% -> '72%'; 81->71%, 83->73%). Metformin ARM WORSE than placebo (an S2 add-on-to-clomifene contrast; treatment-naive PCOS).

The parent proportions/denominators are abstract prose, with no explicit registry parent rows. The route rounds reported proportions into counts; this binder cannot inherit registry identity.

#### noac-vs-warfarin-af-stroke / PMID 19717844 / Stroke or systemic embolism

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_IDENTITY_MISSING**. Route: `pre_specified_dose`. no registry extraction or explicit bound parent rows; provenance labels are not evidence.

No registry outcome-measure quote is available. Held NCT link: `NCT00262600`; that record has 0 held result measures. Title, description, time frame and population remain unbound.

Actual held route quote: `cache/noac-vs-warfarin-af-stroke/dose_selection.json` entry `19717844` (also carried on the full review row):

> RE-LY, verbatim: '... in the group that received 150 mg of dabigatran (relative risk, 0.66; 95% CI, 0.53 to 0.82; P<0.001 for superiority)'. Approved-dose rule (protocol amendment 2026-09-12, post-hoc; the marketed dose, matching the standard-dose comparator): the 150 mg regimen is the marketed dose; the abstract's first-mentioned 110 mg arm (RR 0.91) is the lower dose and is not the review's pooled comparison.

The dose-selection entry cites an abstract effect, not a registry measure. The held registry-design record establishes trial design only. No registry identity is inferred from the trial identifier.

#### noac-vs-warfarin-af-stroke / PMID 24251359 / Stroke or systemic embolism

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_IDENTITY_MISSING**. Route: `pre_specified_dose`. no registry extraction or explicit bound parent rows; provenance labels are not evidence.

No registry outcome-measure quote is available. Held NCT link: `NCT00781391`; that record has 0 held result measures. Title, description, time frame and population remain unbound.

Actual held route quote: `cache/noac-vs-warfarin-af-stroke/dose_selection.json` entry `24251359` (also carried on the full review row):

> ENGAGE AF-TIMI 48, verbatim (intention-to-treat, matching the ITT basis of ROCKET-AF and ARISTOTLE in this pool): '... there was a trend favoring high-dose edoxaban versus warfarin (hazard ratio, 0.87; 97.5% CI, 0.73 to 1.04; P=0.08)'. Approved-dose rule (protocol amendment 2026-09-12, post-hoc; the marketed dose, matching the standard-dose comparator): the 60 mg higher-dose regimen is the marketed dose; the 30 mg low-dose arm is not pooled. [CI CONVERTED: source reports HR 0.87 with a 97.5% CI 0.73-1.04 (multiplicity-adjusted for the two edoxaban doses); converted to a 95% CI 0.745-1.016 (SE=0.079 from the 97.5% bounds, z=2.2414) so it pools on the same 95% basis as the other trials. Cycle 75 audit.]

The dose-selection entry cites an abstract effect, not a registry measure. The held registry-design record establishes trial design only. The CI conversion also has no explicit bound registry parent row.

#### omega3-cardiovascular-events / PMID 30146932 / Atrial fibrillation

**NOT_AN_ABSTRACT_ROW -> EXACT_TARGET**. Route: `ctgov_results`. registry measure: full declared outcome phrase and declared qualifiers match.

Held location: `cache/omega3-cardiovascular-events/records.json#/ctgov_results/NCT00135226/22` at the pinned ref.

Title:

> Number of Participants With Event: Atrial Fibrillation (Omega-3 Comparison Only)

Description:

> Includes fatal and non-fatal events.

Time frame:

> Randomized treatment phase during a mean of 7.4 years

Population:

> [field absent in held measure; no population inferred]

Matched arm tuple (replayed from the quoted measure):

```json
{"ai": 166, "n1i": 7740, "ci": 135, "n2i": 7740}
```

#### probiotics-aad-prevention / PMID 15740542 / Antibiotic-associated diarrhoea

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_IDENTITY_MISSING**. Route: `aact_verified`. no registry extraction or explicit bound parent rows; provenance labels are not evidence.

No registry outcome-measure quote is available. Held NCT link: `absent`; that record has 0 held result measures. Title, description, time frame and population remain unbound.

Actual held route quote: `cache/probiotics-aad-prevention/verified_arms.json` entry `15740542` (also carried on the full review row):

> Can 2006 (PMID 15740542) abstract: 'S. boulardii also reduced the risk of antibiotic-associated diarrhoea ... [four of 119 (3.4%) vs. 22 of 127 (17.3%), relative risk: 0.2; 95% confidence interval: 0.07-0.5]'. ENDPOINT CORRECTION (override): the abstract extractor took the trial's ANY-diarrhoea figure (9/119 vs 29/127, RR 0.3) but our outcome is ANTIBIOTIC-ASSOCIATED diarrhoea, which the same abstract reports separately as 4/119 vs 22/127 (RR 0.2).

Despite the aact_verified label, this entry explicitly cites abstract counts and an endpoint/scale correction. No registry result measure supplies these numbers in the inspected held schemas.

#### probiotics-aad-prevention / PMID 18026577 / Antibiotic-associated diarrhoea

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_IDENTITY_MISSING**. Route: `aact_verified`. no registry extraction or explicit bound parent rows; provenance labels are not evidence.

No registry outcome-measure quote is available. Held NCT link: `absent`; that record has 0 held result measures. Title, description, time frame and population remain unbound.

Actual held route quote: `cache/probiotics-aad-prevention/verified_arms.json` entry `18026577` (also carried on the full review row):

> Beausoleil 2007 (PMID 18026577) abstract: 'antibiotic-associated diarrhea occurred in seven of 44 patients (15.9%) in the lactobacilli group and in 16 of 45 patients (35.6%) in the placebo group (OR 0.34, 95% CI 0.125 to 0.944)'. SCALE CORRECTION (override): the abstract extractor pooled the source ODDS RATIO 0.34 into this RR-family pool; the per-arm counts give the count-based RR directly, consistent with the other count-based trials.

Despite the aact_verified label, this entry explicitly cites abstract counts and an endpoint/scale correction. No registry result measure supplies these numbers in the inspected held schemas.

#### semaglutide-obesity-weight / PMID 33625476 / Percent change in body weight

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_UNBOUND**. Route: `ctgov_results`. registry measure: no full declared outcome phrase in this measure's title/description.

Held location: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03611582/0` at the pinned ref.

Title:

> Change in Body Weight (%)

Description:

> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment periods. In-trial observation period: the uninterrupted time interval from the start of randomisation (week 0) to last trial-related subject-site contact (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period).

Time frame:

> Baseline (week 0) to week 68

Population:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

Matched arm tuple (replayed from the quoted measure):

```json
{"mean1": -16.5, "sd1": 10.1, "nc1": 407, "mean2": -5.8, "sd2": 7.7, "nc2": 204}
```

#### semaglutide-obesity-weight / PMID 33567185 / Percent change in body weight

**NOT_AN_ABSTRACT_ROW -> ENDPOINT_UNBOUND**. Route: `ctgov_results`. registry measure: no full declared outcome phrase in this measure's title/description.

Held location: `cache/semaglutide-obesity-weight/records.json#/ctgov_results/NCT03548935/0` at the pinned ref.

Title:

> Change in Body Weight (%)

Description:

> Change in body weight from baseline (week 0) to week 68 is presented. The endpoint was evaluated based on the data from both in-trial and on-treatment observation periods. In-trial observation period: the uninterrupted time interval from date of randomization (week 0) to date of last contact with trial site (week 75). On-treatment observation period: includes all time intervals in which participants are considered to be on treatment from the first (week 0) to last trial product administration (week 68), including 2 weeks of follow-up. It excludes any period of temporary treatment interruption. Temporary treatment interruption is defined as more than 2 consecutive missed doses (off-treatment period).

Time frame:

> Baseline (week 0) to week 68

Population:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

Matched arm tuple (replayed from the quoted measure):

```json
{"mean1": -15.6, "sd1": 10.1, "nc1": 1306, "mean2": -2.8, "sd2": 6.5, "nc2": 655}
```

#### ticagrelor-vs-clopidogrel-acs / PMID 19717846 / Major bleeding

**NOT_AN_ABSTRACT_ROW -> EXACT_TARGET**. Route: `ctgov_results`. registry measure: full declared outcome phrase and declared qualifiers match.

Held location: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/ctgov_results/NCT00391872/1` at the pinned ref.

Title:

> Participants With Any Major Bleeding Event

Description:

> Participants with major (fatal/life-threatening or other) bleed by a study protocol scale based on need for treatment, number of transfusions, hemoglobin decrease, and other factors. Events were adjudicated by an endpoint committee.

Time frame:

> First dosing up to 12 months

Population:

> The population was the safety analysis set, which included all randomized patients who took at least one dose of study drug

Matched arm tuple (replayed from the quoted measure):

```json
{"ai": 961, "n1i": 9235, "ci": 929, "n2i": 9186}
```

### Verification

Only `tests/test_registry_outcome_binding.py`, `tests/test_single_outcome_binding.py`, and `tests/test_unbound_legacy_failclosed.py` are run. Final focused run: **60 passed in 68.74 seconds**. `git diff --check` passed. No whole-suite run, commit, or served-data regeneration was performed. The second-pass review checked all 14 identifiers, full tuple locations and quoted time frames/populations against the pinned source objects; all 24 local cache files (three files across eight topics) matched those pinned JSON objects. The report was regenerated with:

```text
python evidence/unbound_legacy/classify_legacy_rows.py 3876a62dca66764dff1b4f84d6b43356a1a9e3bb evidence/unbound_legacy/impact_3876a62d.json evidence/unbound_legacy/legacy_rows_classified_registry.json
```

## Verifier's note: the EXISTING registry-candidate route was NOT changed -- and it has its own identity defect (a finding, not a fix)

Codex's patch also replaced the classifier inside `_ctgov_candidates`, which is the route that ALREADY classifies registry
outcome measures, with the stricter `classify_registry_measure`. That was out of scope (the brief: existing classifications must
not change) and it has been reverted. Measured before reverting (`registry_route_compare.py`: every held registry outcome
measure x every declared outcome, all topics, old code at 6311abb9 vs the patch):

- **688 of 730** candidate classifications changed: EXACT_TARGET -> ENDPOINT_UNBOUND **361**, NEAR_MATCH -> UNBOUND **268**,
  DIFFERENT_OUTCOME -> UNBOUND **59**. After the revert: **0 of 730** change.

The comparison shows the stricter reading is too strict to land as-is (e.g. "60-day Mortality: the primary outcome is all-cause
mortality" becomes UNBOUND under "All-cause mortality", on the timepoint rule). It ALSO shows the existing classifier is too
permissive, which is a defect of the same family as UNBOUND_LEGACY:

- balanced-crystalloids: "Major Adverse Kidney Event Within 30 Days" (NCT02444988, NCT02547779) and "Number of Patients With
  MAKE30" (NCT02345486) are classified **EXACT_TARGET for "Mortality"** and for "New renal-replacement therapy";
- a planted major-bleeding measure is EXACT_TARGET under "Cardiovascular death" when the spec's keywords name major bleeding
  (the keyword match stands in for identity).

How many SERVED rows came through such a candidate is not measured here. It is the next item: a candidate being EXACT_TARGET
does not mean it was the row pooled. Nothing about this route is changed on this branch.
