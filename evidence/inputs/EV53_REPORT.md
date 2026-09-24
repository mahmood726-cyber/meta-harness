# EV53 held evidence — INFERRED

Evidence gathering only. This report makes no eligibility decision, admits no row, and changes no build input. The proposed hand-eligibility route does not exist; adoption is Mahmood's decision. No commit or push was made.

## Evidence coverage

All classifications and interpretive judgments below are **INFERRED**. Counts describe the supplied primary rows in `the53.json`, not trials admitted to a pool.

| INFERRED completeness verdict | Supplied primary rows |
|---|---|
| ALL_BLOCKERS_HAVE_HELD_EVIDENCE | 36 of 53 |
| NONE | 1 of 53 |
| PARTIAL | 16 of 53 |

INFERRED evidence coverage only: every observed RLX blocker, plus explicitly named missing PICD/identity requirements for RLX-excluded rows. Additional excluded requirements are not fabricated RLX steps. chain_only_completeness separately restricts the calculation to the measured chain. Nonempty registry structures are NOT manufactured from report text; found substantive evidence is a possible future hand record only.

The main totals include the additional missing PICD requirements of excluded rows. Each row also carries a separate chain-only verdict, so a parent-only stopped chain is not confused with a complete PICD audit. A substantive report passage is not a claim that a term exists in `population.conditions`; the present screen still reads the unchanged registry fields.

| RLX depth group | ALL | PARTIAL | NONE | Denominator |
|---|---|---|---|---|
| 1 | 21 of 22 | 0 of 22 | 1 of 22 | supplied rows in RLX cleared-depth 1 |
| 2 | 8 of 8 | 0 of 8 | 0 of 8 | supplied rows in RLX cleared-depth 2 |
| 3 | 0 of 2 | 2 of 2 | 0 of 2 | supplied rows in RLX cleared-depth 3 |
| 4 | 1 of 1 | 0 of 1 | 0 of 1 | supplied rows in RLX cleared-depth 4 |
| EXCLUDED | 6 of 20 | 14 of 20 | 0 of 20 | supplied rows in RLX excluded group |

RLX exclusion is its own group, not a successful depth-zero result. Raw attempted depth, identity depth, terminal unrelaxed blocker and complete ordered chain are retained per row. No unobserved later relaxation step is invented.

The two depth-three rows are the corticosteroid and tocilizumab RECOVERY reports: COVID entry and randomized comparison are held, but the assigned control is usual care, not placebo. The depth-four EMPHASIS-HF row has primary-report evidence for all four blockers; its held registry design describes a later single-group phase and must not be silently overwritten. The depth-one probiotic row lacks support for the configured AAD entry criterion even though its prevention-trial methods are held.

## RLX-excluded rows: instrument limit versus missing evidence

20 of 20 RLX-excluded supplied rows have held population, intervention/comparator and design material, allowing expressly named secondary sources. This does not mean their configured entry criteria or identity requirements are all established. The distinctions below are INFERRED.

| INFERRED diagnosis | Rows among the RLX-excluded group | Row indices |
|---|---|---|
| INSTRUMENT_LIMIT_WITH_HELD_PICD_AND_IDENTITY | 5 of 20 | 3, 4, 10, 20, 29 |
| HELD_PICD_BUT_PARENT_IDENTIFIER_EVIDENCE_GAP | 3 of 20 | 19, 21, 48 |
| HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP | 9 of 20 | 32, 33, 35, 36, 37, 38, 39, 40, 41 |
| HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH | 1 of 20 | 34 |
| INSTRUMENT_FAMILY_CARDINALITY_LIMIT_WITH_HELD_PICD_AND_BOTH_PARENTS | 1 of 20 | 45 |
| HELD_PARENT_TRIAL_PICD_BUT_POSTHOC_ENTRY_MISMATCH_AND_IDENTITY_GAP | 1 of 20 | 50 |

The pure instrument cases are rows 3, 4, 10, 20 and 29: 5 of 20 RLX-excluded rows have held PICD and identity support for the assessed facts. Row 45 additionally has both named CANVAS parents, but the integrated report must be split into source-bound families before any future hand record could be considered. Thus its ALL evidence verdict is not single-family bindability.

In rows 32 and 41, the Goodman review table and its explicitly linked reference establish antibiotic exposure; these are other held documents, not the trial's own primary record. In row 39, randomization comes from PubMed indexing plus the linked RCT review, while the trial abstract supplies the blinded parallel comparison. These source-policy distinctions remain explicit. The supplied B53X audit already identified them; EV53 relocates and verifies their spans rather than treating the prior conclusion as evidence.

## Scope, search and positive controls

937 of 937 inventoried held files under `cache/` were searched and hashed. This includes all topic files, all held comparator files, cross-topic copies, `records.json`, held `ft_*.txt`/full-text objects and both compressed AACT files. The payload was searched for eligibility criteria; the compact row file was not treated as if it contained those criteria. The complete manifest, patterns, family locators and per-row hit paths are in `ev53.json`.

The extended search also covered 2478 of 2478 inventoried repository documents outside `cache/`, including raw acquisitions under `docs/` and `outputs/`, registry files and topic protocols. Source candidates were distinguished from generated audit prose and test fixtures. PDF pages were searched through read-only text extraction for discovery; no extracted PDF string is presented as a quote located in raw PDF bytes. The additional manifest and candidate-review disposition are in `ev53.json`.

Generated cache projections were searched as locators and never counted as independent trial evidence. An `ft_` filename does not guarantee a full-text body. Scope is the held corpus only, with no network acquisition. Primary abstract/title fields were read in full; relevant full-text methods, registry criteria and linked review passages were checked in context. Search matches in background, exclusion lists, endpoints or bibliography do not establish entry eligibility.

Negative classifications mean no source-bound supporting span was located in this disclosed search, not that no document anywhere could contain the fact. They retain near misses or explicit counterevidence, identify what would settle the question, and link a retrieval positive control. The controls demonstrate that the search fires; they do not turn keyword retrieval into proof of semantic exhaustiveness.

| Control | Exact matched text | Source span | Result |
|---|---|---|---|
| PARENT | `IRCT20200328046886N6` at document character 11415 | [B53-03-E02](#b53-03-e02) | PASS |
| RANDOMIZED | `randomized` at document character 1408 | [B53-01-E01](#b53-01-e01) | PASS |
| PLACEBO | `placebo` at document character 1556 | [B53-18-E01](#b53-18-e01) | PASS |
| ENTRY | `critically ill` at document character 1450 | [B53-01-E01](#b53-01-e01) | PASS |
| MASKING | `double-blind` at document character 171103 | [B53-04-E01](#b53-04-e01) | PASS |
| PARALLEL | `parallel` at document character 953268 | [B53-39-E01](#b53-39-e01) | PASS |
| ADULT | `adults` at document character 10115 | [B53-03-E01](#b53-03-e01) | PASS |

## Static versus dynamic disclosure

| Item | Kind | Basis |
|---|---|---|
| Source rows, RLX chains, document bytes, offsets, hashes and counts | dynamic | Read from held inputs and computed locally |
| Fact interpretation, source rank, phase/family binding and completeness | static human-style audit judgments | INFERRED; linked verbatim source spans; no runtime decision |
| Search patterns and evidence record proposal | static design | Disclosed search aids and design only, not fake study outputs |

## Per-row evidence

Each row is counted once per completeness cross-tab. A fact has one canonical fact_id per row; repeated spans, alternate sources and reuse across blockers never create additional found facts. Original evidence IDs are citation identifiers, not independent confirmations.

### Row 1: PMID 35041780 — NCT02721654

Topic: `balanced-crystalloids-vs-saline-mortality`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-01-E01](#b53-01-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-01-E01](#b53-01-e01) |

The patients assigned to BMES or saline are explicitly critically ill and in ICU; Hypovolemia alone does not establish ICU entry.

Own held context: [EV01-OWN-TITLE](#ev01-own-title), [EV01-OWN-ABSTRACT](#ev01-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 2: PMID 34375394 — NCT02875873

Topic: `balanced-crystalloids-vs-saline-mortality`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-02-E01](#b53-02-e01) |

The fluid-type factor is explicitly randomized. Infusion rate is a separate factor, not the comparator to balanced fluid. No parallel-only requirement applies.

Own held context: [EV02-OWN-TITLE](#ev02-own-title), [EV02-OWN-ABSTRACT](#ev02-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 3: PMID 42132185 — SYN-f9c2d88aa0de

Topic: `colchicine-postop-af`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED → INSUFFICIENT_PICD_EVIDENCE`. RLX excluded; attempted depth: 1; identity depth 1; screen depth 0.

RLX stopping reason: Missing registry_design, population.conditions.value, arms. Supplying a complete report/parent-derived PICD bundle would clear other predicates too; truthy dummy structures would invent evidence. Excluded at this structural gate.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INSUFFICIENT_PICD_EVIDENCE` → `design`, `entry_population`, `arms`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E02](#b53-03-e02) |
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E01](#b53-03-e01) |
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E01](#b53-03-e01) |
| `arms`: The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E01](#b53-03-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E01](#b53-03-e01) |
| `masking` (additional excluded requirement): At least double masking for the relevant randomized phase. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E01](#b53-03-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-03-E01](#b53-03-e01) |

The primary methods establish randomized double-blind colchicine/placebo in on-pump CABG. The abstract names an IRCT parent; current regex nonrecognition is separate from held identity evidence.

INFERRED excluded-row diagnosis: **INSTRUMENT_LIMIT_WITH_HELD_PICD_AND_IDENTITY**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-03-E01](#b53-03-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-03-E01](#b53-03-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-03-E01](#b53-03-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV03-OWN-TITLE](#ev03-own-title), [EV03-OWN-ABSTRACT](#ev03-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 4: PMID 32865380 — ACTRN12614000093684

Topic: `colchicine-secondary-cv-prevention`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INSUFFICIENT_PICD_EVIDENCE`. RLX sequence: `INSUFFICIENT_PICD_EVIDENCE`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: Missing registry_design, population.conditions.value, arms. Supplying a complete report/parent-derived PICD bundle would clear other predicates too; truthy dummy structures would invent evidence. Excluded at this structural gate.

Ordered blockers and fact IDs:

1. `INSUFFICIENT_PICD_EVIDENCE` → `design`, `entry_population`, `arms`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-04-E01](#b53-04-e01) |
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-04-E01](#b53-04-e01) |
| `arms`: The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-04-E01](#b53-04-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-04-E01](#b53-04-e01) |
| `masking` (additional excluded requirement): At least double masking for the relevant randomized phase. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-04-E01](#b53-04-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-04-E01](#b53-04-e01) |

Chronic coronary disease is the entry population. Ischemic stroke is an outcome, not an entry population; the primary LoDoCo2 report supplies the comparison without relying on its later exploratory reports.

INFERRED excluded-row diagnosis: **INSTRUMENT_LIMIT_WITH_HELD_PICD_AND_IDENTITY**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-04-E01](#b53-04-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-04-E01](#b53-04-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-04-E01](#b53-04-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV04-OWN-TITLE](#ev04-own-title), [EV04-OWN-ABSTRACT](#ev04-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 5: PMID 32678530 — NCT04381936

Topic: `corticosteroids-covid19-mortality`. **INFERRED PARTIAL**. Chain-only: **INFERRED PARTIAL**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 3; identity depth 0; screen depth 3.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
3. `PLACEBO_CONTROL_NOT_PROVEN` → `placebo_control`; INFERRED NONE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-05-E01](#b53-05-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-05-E01](#b53-05-e01) |
| `placebo_control`: A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-05-E01](#b53-05-e01) |

The COVID-era dexamethasone comparison is randomized against usual care alone, contradicting the current screen placebo requirement. The current registry is a later pneumonia/influenza epoch. The held full text also removes the age floor during recruitment; no elderly/adult-only restriction is inferred.

Additional scope/phase context (not additional found facts): [X05-EPOCH](#x05-epoch), [X05-AGE-EPOCH](#x05-age-epoch), [X05-PERIOD](#x05-period).

Missing `placebo_control`: Usual care alone is the randomized comparator, not placebo. The config allows usual care as an alternative but the current screen also demands literal placebo. To settle: A protocol or primary full report showing a placebo randomized control in this same phase. The held usual-care comparison is contrary evidence; accepting it would require a comparator-policy change. Positive controls: PLACEBO (PASS above).

Missing observed blockers: `PLACEBO_CONTROL_NOT_PROVEN`.

All missing assessed fact IDs: `placebo_control`.

Own held context: [EV05-OWN-TITLE](#ev05-own-title), [EV05-OWN-ABSTRACT](#ev05-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 6: PMID 19671655 — NCT00089791

Topic: `denosumab-vertebral-fracture`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-06-E01](#b53-06-e01), [B53-06-E06](#b53-06-e06) |

The primary title explicitly says postmenopausal women with osteoporosis; the methods add entry age and bone-density criteria. Age alone would not establish postmenopausal status. Cancer is an adverse-event statement, not the entry indication.

Own held context: [EV06-OWN-TITLE](#ev06-own-title), [EV06-OWN-ABSTRACT](#ev06-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 7: PMID 24344086 — NCT00680186

Topic: `doac-vte-recurrence`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-07-E01](#b53-07-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-07-E01](#b53-07-e01) |

The methods concern the new RE-COVER II acute-VTE cohort; the separate pooled-analysis paragraph does not turn it into an extended-treatment cohort. Heparin is initial therapy, not the randomized comparator.

Own held context: [EV07-OWN-TITLE](#ev07-own-title), [EV07-OWN-ABSTRACT](#ev07-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 8: PMID 19966341 — NCT00291330

Topic: `doac-vte-recurrence`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-08-E01](#b53-08-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-08-E01](#b53-08-e01) |

Acute VTE is the randomized entry population; dabigatran is compared with dose-adjusted warfarin after initial parenteral therapy.

Own held context: [EV08-OWN-TITLE](#ev08-own-title), [EV08-OWN-ABSTRACT](#ev08-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 9: PMID 22449293 — NCT00439777

Topic: `doac-vte-recurrence`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-09-E01](#b53-09-e01) |

The trial randomized acute symptomatic PE patients to rivaroxaban versus an enoxaparin/VKA regimen. The background DVT trial is not the deciding evidence.

Own held context: [EV09-OWN-TITLE](#ev09-own-title), [EV09-OWN-ABSTRACT](#ev09-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 10: PMID 21128814 — SYN-968e8c7d0a82

Topic: `doac-vte-recurrence`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED → INSUFFICIENT_PICD_EVIDENCE`. RLX excluded; attempted depth: 1; identity depth 1; screen depth 0.

RLX stopping reason: Missing registry_design, population.conditions.value, arms. Supplying a complete report/parent-derived PICD bundle would clear other predicates too; truthy dummy structures would invent evidence. Excluded at this structural gate.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INSUFFICIENT_PICD_EVIDENCE` → `design`, `entry_population`, `arms`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-10-E02](#b53-10-e02), [B53-10-E06](#b53-10-e06); context/counterevidence: [B53-10-E07](#b53-10-e07) |
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-10-E01](#b53-10-e01), [B53-10-E06](#b53-10-e06) |
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-10-E01](#b53-10-e01), [B53-10-E06](#b53-10-e06) |
| `arms`: The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-10-E01](#b53-10-e01), [B53-10-E06](#b53-10-e06) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-10-E01](#b53-10-e01), [B53-10-E06](#b53-10-e06) |

Only the acute-DVT study is eligible. The publication also describes a distinct continued-treatment placebo trial, which cannot be used for this contrast. Held parent criteria disambiguate the two NCTs.

INFERRED excluded-row diagnosis: **INSTRUMENT_LIMIT_WITH_HELD_PICD_AND_IDENTITY**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-10-E01](#b53-10-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-10-E01](#b53-10-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-10-E01](#b53-10-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV10-OWN-TITLE](#ev10-own-title), [EV10-OWN-ABSTRACT](#ev10-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 11: PMID 23991658 — NCT00986154

Topic: `doac-vte-recurrence`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-11-E01](#b53-11-e01) |

The randomized contrast is edoxaban versus warfarin after initial heparin. The later right-ventricular-dysfunction subgroup does not supply entry eligibility.

Own held context: [EV11-OWN-TITLE](#ev11-own-title), [EV11-OWN-ABSTRACT](#ev11-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 12: PMID 23808982 — NCT00643201

Topic: `doac-vte-recurrence`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-12-E01](#b53-12-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-12-E01](#b53-12-e01) |

The acute-VTE methods compare apixaban with enoxaparin followed by warfarin; this is not a same-drug dose comparison.

Own held context: [EV12-OWN-TITLE](#ev12-own-title), [EV12-OWN-ABSTRACT](#ev12-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 13: PMID 30418475 — NCT01897532

Topic: `dpp4-mace-t2d`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-13-E01](#b53-13-e01) |

The methods explicitly enroll adults with type 2 diabetes; usual care is shared background. Required masking is established by the linked registry DOUBLE field, not by the abstract.

Additional scope/phase context (not additional found facts): [B53-13-E02](#b53-13-e02), [B53-13-E03](#b53-13-e03), [B53-13-E04](#b53-13-e04).

Own held context: [EV13-OWN-TITLE](#ev13-own-title), [EV13-OWN-ABSTRACT](#ev13-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 14: PMID 28893244 — NCT01703208

Topic: `dpp4-mace-t2d`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-14-E01](#b53-14-e01), [B53-14-E06](#b53-14-e06) |

The same primary abstract identifies omarigliptin as a DPP-4 inhibitor and randomizes it against matching placebo. The class definition alone would merely mention the intervention; the assignment sentence completes the proof.

Own held context: [EV14-OWN-TITLE](#ev14-own-title), [EV14-OWN-ABSTRACT](#ev14-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 15: PMID 37025256 — NCT03434041

Topic: `esketamine-trd-madrs`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-15-E01](#b53-15-e01) |

The primary report explicitly establishes TRD entry in the randomized trial and esketamine versus matching placebo, each with a newly initiated oral antidepressant. Shared antidepressant therapy does not define the randomized difference.

Own held context: [EV15-OWN-TITLE](#ev15-own-title), [EV15-OWN-ABSTRACT](#ev15-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 16: NCT02422186 — NCT02422186

Topic: `esketamine-trd-madrs`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-16-E05](#b53-16-e05), [X16-CRITERIA](#x16-criteria) |

The held registry title expressly names elderly participants with treatment-resistant depression. Its inclusion criteria document the current depressive episode, prior antidepressant nonresponse and prospective qualification; exclusion criteria are not treated as positive entry diagnoses.

Additional scope/phase context (not additional found facts): [B53-16-E01](#b53-16-e01), [B53-16-E02](#b53-16-e02), [B53-16-E03](#b53-16-e03).

Own held context: [EV16-OWN-TITLE](#ev16-own-title). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 17: PMID 30291013 — NCT02465515

Topic: `glp1-ra-mace-t2d`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-17-E01](#b53-17-e01) |

The primary methods require type 2 diabetes and age at least 40. The held PARALLEL model supplies the additional B-prime design requirement; two groups alone would not prove that model.

Additional scope/phase context (not additional found facts): [B53-17-E02](#b53-17-e02), [B53-17-E03](#b53-17-e03), [B53-17-E04](#b53-17-e04), [B53-17-E06](#b53-17-e06).

Own held context: [EV17-OWN-TITLE](#ev17-own-title), [EV17-OWN-ABSTRACT](#ev17-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 18: PMID 40159390 — NCT03036462

Topic: `iv-iron-hfref-hosp`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `PLACEBO_CONTROL_NOT_PROVEN` → `placebo_control`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-18-E01](#b53-18-e01) |
| `placebo_control`: A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-18-E01](#b53-18-e01) |

The primary intervention is ferric carboxymaltose versus explicitly named saline placebo. The registry generic iron/saline projection is not the only evidence.

Own held context: [EV18-OWN-TITLE](#ev18-own-title), [EV18-OWN-ABSTRACT](#ev18-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 19: PMID 19522426 — SYN-a65b65385197

Topic: `metformin-pcos-ovulation`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X19-FULL-ABSTRACT](#x19-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-19-E01](#b53-19-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-19-E01](#b53-19-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-19-E01](#b53-19-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-19-E01](#b53-19-e01) |

PCOS patients were randomized to metformin or placebo on shared clomifene. No registry parent is named in the held abstract; primary PICD sufficiency cannot invent an identifier.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`.

INFERRED excluded-row diagnosis: **HELD_PICD_BUT_PARENT_IDENTIFIER_EVIDENCE_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-19-E01](#b53-19-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-19-E01](#b53-19-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-19-E01](#b53-19-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV19-OWN-TITLE](#ev19-own-title), [EV19-OWN-ABSTRACT](#ev19-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 20: PMID 16769748 — ISRCTN55906981

Topic: `metformin-pcos-ovulation`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INSUFFICIENT_PICD_EVIDENCE`. RLX sequence: `INSUFFICIENT_PICD_EVIDENCE`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: Missing registry_design, population.conditions.value, arms. Supplying a complete report/parent-derived PICD bundle would clear other predicates too; truthy dummy structures would invent evidence. Excluded at this structural gate.

Ordered blockers and fact IDs:

1. `INSUFFICIENT_PICD_EVIDENCE` → `design`, `entry_population`, `arms`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-20-E01](#b53-20-e01) |
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-20-E01](#b53-20-e01) |
| `arms`: The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-20-E01](#b53-20-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-20-E01](#b53-20-e01) |

The trial methods explicitly describe PCOS, random allocation and metformin versus placebo, both with clomifene. The quality-of-life companion is not needed.

INFERRED excluded-row diagnosis: **INSTRUMENT_LIMIT_WITH_HELD_PICD_AND_IDENTITY**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-20-E01](#b53-20-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-20-E01](#b53-20-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-20-E01](#b53-20-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV20-OWN-TITLE](#ev20-own-title), [EV20-OWN-ABSTRACT](#ev20-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 21: PMID 11172832 — SYN-90e1fc6ced9d

Topic: `metformin-pcos-ovulation`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X21-FULL-ABSTRACT](#x21-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02) |

The randomized placebo/metformin phase is followed by clomiphene in both arms; it remains the assigned comparison. No held registry parent is named.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`.

INFERRED excluded-row diagnosis: **HELD_PICD_BUT_PARENT_IDENTIFIER_EVIDENCE_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-21-E01](#b53-21-e01), [B53-21-E02](#b53-21-e02). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV21-OWN-TITLE](#ev21-own-title), [EV21-OWN-ABSTRACT](#ev21-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 22: PMID 21830957 — NCT00403767

Topic: `noac-vs-warfarin-af-stroke`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-22-E01](#b53-22-e01) |

ROCKET AF directly randomizes rivaroxaban versus warfarin. Registry arm links are complete; the active-comparator residual is a rule defect.

Own held context: [EV22-OWN-TITLE](#ev22-own-title), [EV22-OWN-ABSTRACT](#ev22-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 23: PMID 19717844 — NCT00262600

Topic: `noac-vs-warfarin-af-stroke`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-23-E01](#b53-23-e01) |

RE-LY explicitly randomizes two dabigatran doses versus unblinded warfarin. Double blinding is not required for this topic; absence of masking in the registry is not an exclusion.

Own held context: [EV23-OWN-TITLE](#ev23-own-title), [EV23-OWN-ABSTRACT](#ev23-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 24: PMID 24251359 — NCT00781391

Topic: `noac-vs-warfarin-af-stroke`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-24-E01](#b53-24-e01) |

ENGAGE explicitly compares each edoxaban regimen with warfarin. Double-dummy placebos do not make this an edoxaban-versus-placebo efficacy comparison.

Own held context: [EV24-OWN-TITLE](#ev24-own-title), [EV24-OWN-ABSTRACT](#ev24-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 25: PMID 21870978 — NCT00412984

Topic: `noac-vs-warfarin-af-stroke`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-25-E01](#b53-25-e01) |

ARISTOTLE explicitly compares apixaban with warfarin. Aspirin in the background describes another study and is not this comparator.

Own held context: [EV25-OWN-TITLE](#ev25-own-title), [EV25-OWN-ABSTRACT](#ev25-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 26: PMID 33190147 — NCT02104817

Topic: `omega3-cardiovascular-events`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `PLACEBO_CONTROL_NOT_PROVEN` → `placebo_control`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-26-E01](#b53-26-e01) |
| `placebo_control`: A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-26-E01](#b53-26-e01) |

Corn oil is expressly intended as an inert comparator in the blinded randomized trial. That establishes functional placebo control in a hand representation; it does not establish biological inertness, nor make the untouched literal drug-field check pass.

Own held context: [EV26-OWN-TITLE](#ev26-own-title), [EV26-OWN-ABSTRACT](#ev26-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 27: PMID 30415628 — NCT01492361

Topic: `omega3-cardiovascular-events`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-27-E01](#b53-27-e01) |

The primary methods directly randomize icosapent ethyl versus placebo, with statins as background therapy.

Own held context: [EV27-OWN-TITLE](#ev27-own-title), [EV27-OWN-ABSTRACT](#ev27-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 28: PMID 20929341 — NCT00127452

Topic: `omega3-cardiovascular-events`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `PLACEBO_CONTROL_NOT_PROVEN` → `placebo_control`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-28-E01](#b53-28-e01), [X28-ALIAS](#x28-alias) |
| `placebo_control`: A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-28-E01](#b53-28-e01), [X28-ALIAS](#x28-alias) |

Four randomized margarines include EPA-DHA alone and placebo, with and without ALA. Bind the EPA-DHA factor or matched cells, never EPA-DHA versus its ALA factorial partner. The abstract defines EPA/DHA as marine n-3 fatty acids.

Own held context: [EV28-OWN-TITLE](#ev28-own-title), [EV28-OWN-ABSTRACT](#ev28-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 29: PMID 21115589 — ISRCTN41926726

Topic: `omega3-cardiovascular-events`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INSUFFICIENT_PICD_EVIDENCE`. RLX sequence: `INSUFFICIENT_PICD_EVIDENCE`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: Missing registry_design, population.conditions.value, arms. Supplying a complete report/parent-derived PICD bundle would clear other predicates too; truthy dummy structures would invent evidence. Excluded at this structural gate.

Ordered blockers and fact IDs:

1. `INSUFFICIENT_PICD_EVIDENCE` → `design`, `entry_population`, `arms`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-29-E01](#b53-29-e01), [X29-FACTOR](#x29-factor) |
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-29-E01](#b53-29-e01), [X29-FACTOR](#x29-factor) |
| `arms`: The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-29-E01](#b53-29-e01), [X29-FACTOR](#x29-factor) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-29-E01](#b53-29-e01), [X29-FACTOR](#x29-factor) |
| `masking` (additional excluded requirement): At least double masking for the relevant randomized phase. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-29-E01](#b53-29-e01), [X29-FACTOR](#x29-factor) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-29-E01](#b53-29-e01), [X29-FACTOR](#x29-factor) |

The factorial methods and full text explicitly randomize omega 3 versus its placebo independently of B vitamins. B vitamins are a separate factor, not the omega-3 comparator.

INFERRED excluded-row diagnosis: **INSTRUMENT_LIMIT_WITH_HELD_PICD_AND_IDENTITY**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-29-E01](#b53-29-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-29-E01](#b53-29-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-29-E01](#b53-29-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV29-OWN-TITLE](#ev29-own-title), [EV29-OWN-ABSTRACT](#ev29-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 30: PMID 28304224 — NCT01764633

Topic: `pcsk9-mace`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-30-E01](#b53-30-e01) |

Atherosclerotic cardiovascular disease is explicit in the randomized entry cohort. The low-LDL subgroup is not the entry evidence; Dyslipidemia alone would be insufficient.

Own held context: [EV30-OWN-TITLE](#ev30-own-title), [EV30-OWN-ABSTRACT](#ev30-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 31: PMID 35727573 — NCT03334604

Topic: `probiotics-aad-prevention`. **INFERRED NONE**. Chain-only: **INFERRED NONE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED NONE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-31-E01](#b53-31-e01), [X31-OUTCOME](#x31-outcome) |

The primary report establishes antibiotic initiation at entry, including children. AAD is an outcome, not the entry condition. Neither antibiotic recipients nor expanded diarrhoea spellings are in the literal population_any list.

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The primary report establishes antibiotic initiation at entry, including children. AAD is an outcome, not the entry condition. Neither antibiotic recipients nor expanded diarrhoea spellings are in the literal population_any list. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `ENTRY_POPULATION_NOT_ESTABLISHED`.

All missing assessed fact IDs: `entry_population`.

Own held context: [EV31-OWN-TITLE](#ev31-own-title), [EV31-OWN-ABSTRACT](#ev31-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 32: PMID 32035998 — SYN-0419eae8aeb8

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X32-FULL-ABSTRACT](#x32-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-32-E01](#b53-32-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-32-E01](#b53-32-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-32-E01](#b53-32-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-32-E01](#b53-32-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-32-E01](#b53-32-e01) |

The abstract states randomized probiotic/placebo and age, but AAD appears as an outcome. Antibiotic exposure at entry is only established by the linked secondary review table plus its eligibility criteria. No registry parent is named.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The abstract states randomized probiotic/placebo and age, but AAD appears as an outcome. Antibiotic exposure at entry is only established by the linked secondary review table plus its eligibility criteria. No registry parent is named. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_OTHER_HELD_DOCUMENT: [B53-32-S01](#b53-32-s01), [X32-REFERENCE](#x32-reference), [X-SECONDARY-ENTRY](#x-secondary-entry). Not the trial's own primary report. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-32-E01](#b53-32-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-32-E01](#b53-32-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV32-OWN-TITLE](#ev32-own-title), [EV32-OWN-ABSTRACT](#ev32-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 33: PMID 24772726 — SYN-94f93929fa67

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X33-FULL-ABSTRACT](#x33-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-33-E01](#b53-33-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-33-E01](#b53-33-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-33-E01](#b53-33-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-33-E01](#b53-33-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-33-E01](#b53-33-e01) |

The primary methods establish a seven-day antibiotic course at entry. AAD is the outcome; this does not satisfy the configured entry-population terms. The trial is not the later AAD subgroup mentioned in results.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The primary methods establish a seven-day antibiotic course at entry. AAD is the outcome; this does not satisfy the configured entry-population terms. The trial is not the later AAD subgroup mentioned in results. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-33-E01](#b53-33-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-33-E01](#b53-33-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-33-E01](#b53-33-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV33-OWN-TITLE](#ev33-own-title), [EV33-OWN-ABSTRACT](#ev33-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 34: PMID 23932219 — ISRCTN70017204

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED PARTIAL**.

Recorded absence: `INSUFFICIENT_PICD_EVIDENCE`. RLX sequence: `INSUFFICIENT_PICD_EVIDENCE`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: Missing registry_design, population.conditions.value, arms. Supplying a complete report/parent-derived PICD bundle would clear other predicates too; truthy dummy structures would invent evidence. Excluded at this structural gate.

Ordered blockers and fact IDs:

1. `INSUFFICIENT_PICD_EVIDENCE` → `design`, `entry_population`, `arms`; INFERRED PARTIAL. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-34-E01](#b53-34-e01) |
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-34-E01](#b53-34-e01), [X34-OUTCOME](#x34-outcome) |
| `arms`: The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-34-E01](#b53-34-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-34-E01](#b53-34-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-34-E01](#b53-34-e01) |

Primary methods and the held protocol establish older antibiotic recipients, not an entry cohort with AAD. The protocol excludes diarrhea at entry; broad antibiotic exposure still requires a corrected population rule.

Additional scope/phase context (not additional found facts): [EV34-PROTOCOL-ENTRY](#ev34-protocol-entry).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. Primary methods and the held protocol establish older antibiotic recipients, not an entry cohort with AAD. The protocol excludes diarrhea at entry; broad antibiotic exposure still requires a corrected population rule. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `INSUFFICIENT_PICD_EVIDENCE`.

All missing assessed fact IDs: `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-34-E01](#b53-34-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-34-E01](#b53-34-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-34-E01](#b53-34-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV34-OWN-TITLE](#ev34-own-title), [EV34-OWN-ABSTRACT](#ev34-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 35: PMID 18701826 — SYN-3bb36b8c9d29

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X35-FULL-ABSTRACT](#x35-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-35-E01](#b53-35-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-35-E01](#b53-35-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-35-E01](#b53-35-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-35-E01](#b53-35-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-35-E01](#b53-35-e01) |

The methods enroll antibiotic-treated children with infections and randomize the probiotic mixture against placebo. Children are permitted by this config. AAD is a prevention target, not the entry condition.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The methods enroll antibiotic-treated children with infections and randomize the probiotic mixture against placebo. Children are permitted by this config. AAD is a prevention target, not the entry condition. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-35-E01](#b53-35-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-35-E01](#b53-35-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-35-E01](#b53-35-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV35-OWN-TITLE](#ev35-own-title), [EV35-OWN-ABSTRACT](#ev35-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 36: PMID 18410562 — SYN-a2a3bd246f45

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X36-FULL-ABSTRACT](#x36-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-36-E01](#b53-36-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-36-E01](#b53-36-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-36-E01](#b53-36-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-36-E01](#b53-36-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-36-E01](#b53-36-e01) |

Children with common infections receive antibiotics and randomized probiotic/placebo. AAD develops after entry; no configured AAD entry population is established.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. Children with common infections receive antibiotics and randomized probiotic/placebo. AAD develops after entry; no configured AAD entry population is established. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-36-E01](#b53-36-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-36-E01](#b53-36-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-36-E01](#b53-36-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV36-OWN-TITLE](#ev36-own-title), [EV36-OWN-ABSTRACT](#ev36-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 37: PMID 15740542 — SYN-962dc41d54af

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X37-FULL-ABSTRACT](#x37-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-37-E01](#b53-37-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-37-E01](#b53-37-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-37-E01](#b53-37-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-37-E01](#b53-37-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-37-E01](#b53-37-e01) |

The methods concern children receiving antibiotics, whereas the background adults sentence describes prior evidence. AAD is the prevention outcome, not the entry population.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The methods concern children receiving antibiotics, whereas the background adults sentence describes prior evidence. AAD is the prevention outcome, not the entry population. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-37-E01](#b53-37-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-37-E01](#b53-37-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-37-E01](#b53-37-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV37-OWN-TITLE](#ev37-own-title), [EV37-OWN-ABSTRACT](#ev37-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 38: PMID 11560298 — SYN-0b772df8adc9

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X38-FULL-ABSTRACT](#x38-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-38-E01](#b53-38-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-38-E01](#b53-38-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-38-E01](#b53-38-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-38-E01](#b53-38-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-38-E01](#b53-38-e01) |

Hospitalized antibiotic recipients are randomized to LGG or placebo. The beta-lactam subgroup is not the entry cohort. AAD occurs after enrollment.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. Hospitalized antibiotic recipients are randomized to LGG or placebo. The beta-lactam subgroup is not the entry cohort. AAD occurs after enrollment. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-38-E01](#b53-38-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-38-E01](#b53-38-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-38-E01](#b53-38-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV38-OWN-TITLE](#ev38-own-title), [EV38-OWN-ABSTRACT](#ev38-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 39: PMID 7872284 — SYN-e445a1f4ca49

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X39-FULL-ABSTRACT](#x39-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_OTHER_HELD_DOCUMENT | [B53-39-S02](#b53-39-s02), [B53-39-S01](#b53-39-s01), [X39-REFERENCE](#x39-reference), [X-SECONDARY-ENTRY](#x-secondary-entry), [B53-39-E01](#b53-39-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-39-E01](#b53-39-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-39-E01](#b53-39-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_OTHER_HELD_DOCUMENT | [B53-39-S02](#b53-39-s02), [B53-39-S01](#b53-39-s01), [X39-REFERENCE](#x39-reference), [X-SECONDARY-ENTRY](#x-secondary-entry), [B53-39-E01](#b53-39-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-39-E01](#b53-39-e01) |

The abstract establishes a blinded parallel placebo comparison and new beta-lactam prescriptions, with no acute diarrhea at entry. It never states random allocation. PubMed RCT indexing is separate non-primary evidence; AAD remains an outcome.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

`design`: Randomization is established here by PubMed indexing and the Goodman review; neither is the trial's own primary report. The primary abstract supplies only the comparison and parallel design. The primary abstract states a blinded parallel placebo comparison but not random allocation. PubMed Randomized Controlled Trial indexing plus the linked review trial row and RCT-only eligibility provide secondary evidence. Do not present randomization as verbatim primary-report methods.

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The abstract establishes a blinded parallel placebo comparison and new beta-lactam prescriptions, with no acute diarrhea at entry. It never states random allocation. PubMed RCT indexing is separate non-primary evidence; AAD remains an outcome. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

`randomized_contrast`: Randomization is established here by PubMed indexing and the Goodman review; neither is the trial's own primary report. The primary abstract supplies only the comparison and parallel design. The primary abstract states a blinded parallel placebo comparison but not random allocation. PubMed Randomized Controlled Trial indexing plus the linked review trial row and RCT-only eligibility provide secondary evidence. Do not present randomization as verbatim primary-report methods.

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-39-E01](#b53-39-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-39-E01](#b53-39-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_OTHER_HELD_DOCUMENT: [B53-39-S02](#b53-39-s02), [B53-39-S01](#b53-39-s01), [X39-REFERENCE](#x39-reference), [X-SECONDARY-ENTRY](#x-secondary-entry), [B53-39-E01](#b53-39-e01). Not the trial's own primary report. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV39-OWN-TITLE](#ev39-own-title), [EV39-OWN-ABSTRACT](#ev39-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 40: PMID 21165295 — SYN-2163745e2514

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X40-FULL-ABSTRACT](#x40-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-40-E01](#b53-40-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-40-E01](#b53-40-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-40-E01](#b53-40-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-40-E01](#b53-40-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-40-E01](#b53-40-e01) |

The primary full-text methods confirm antibiotic-treated respiratory-infection patients and exclude baseline diarrheal disease. The background treatment-of-AAD sentence is not this trial. AAD is an incident endpoint.

Additional scope/phase context (not additional found facts): [EV40-BASELINE-EXCLUSION](#ev40-baseline-exclusion).

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The primary full-text methods confirm antibiotic-treated respiratory-infection patients and exclude baseline diarrheal disease. The background treatment-of-AAD sentence is not this trial. AAD is an incident endpoint. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-40-E01](#b53-40-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-40-E01](#b53-40-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-40-E01](#b53-40-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV40-OWN-TITLE](#ev40-own-title), [EV40-OWN-ABSTRACT](#ev40-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 41: PMID 18026577 — SYN-750512ad72a7

Topic: `probiotics-aad-prevention`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X41-FULL-ABSTRACT](#x41-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-41-E01](#b53-41-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-41-E01](#b53-41-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-41-E01](#b53-41-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-41-E01](#b53-41-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-41-E01](#b53-41-e01) |

The primary abstract describes hospitalized patients and randomized fermented milk/placebo; it does not explicitly require antibiotics at entry. The held ft object has no body. Linked secondary review evidence fills antibiotic exposure only under a broader source policy.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The configured population terms concern AAD, which appears as a prevention endpoint/background rather than an entry diagnosis. screen_family uses literal substrings (including literal *); antibiotic exposure is not a listed entry term. The primary abstract describes hospitalized patients and randomized fermented milk/placebo; it does not explicitly require antibiotics at entry. The held ft object has no body. Linked secondary review evidence fills antibiotic exposure only under a broader source policy. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PREVENTION_PICD_BUT_CONFIGURED_ENTRY_RULE_MISMATCH_AND_PARENT_IDENTIFIER_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_OTHER_HELD_DOCUMENT: [B53-41-S01](#b53-41-s01), [X41-REFERENCE](#x41-reference), [X-SECONDARY-ENTRY](#x-secondary-entry). Not the trial's own primary report. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-41-E01](#b53-41-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-41-E01](#b53-41-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV41-OWN-TITLE](#ev41-own-title), [EV41-OWN-ABSTRACT](#ev41-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 42: PMID 25176015 — NCT01035255

Topic: `sacubitril-valsartan-hfref`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-42-E01](#b53-42-e01) |

The primary PARADIGM methods randomize LCZ696 against enalapril with recommended therapy. The PARAGON discussion in a companion is background and is not the eligible population.

Own held context: [EV42-OWN-TITLE](#ev42-own-title), [EV42-OWN-ABSTRACT](#ev42-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 43: NCT02468232 — NCT02468232

Topic: `sacubitril-valsartan-hfref`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-43-E01](#b53-43-e01), [B53-43-E05](#b53-43-e05), [B53-43-E06](#b53-43-e06), [B53-43-E07](#b53-43-e07), [B53-43-E08](#b53-43-e08), [B53-43-E09](#b53-43-e09), [B53-43-E10](#b53-43-e10), [EV43-ARM-144](#ev43-arm-144), [EV43-ARM-146](#ev43-arm-146) |

The registry contains a randomized parallel QUADRUPLE design and two completely linked arms: LCZ696 plus dummy enalapril versus enalapril plus dummy LCZ696. This is an active comparison; no placebo efficacy control is required.

Own held context: [EV43-OWN-TITLE](#ev43-own-title). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 44: PMID 37952131 — NCT03574597

Topic: `semaglutide-obesity-mace`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-44-E01](#b53-44-e01), [X44-ENTRY](#x44-entry) |

Methods establish cardiovascular disease, BMI at least 27 and no diabetes. The same primary report conclusion supplies the exact configured phrase cardiovascular disease and overweight or obesity; the B53 method cut alone lacks that phrase.

Own held context: [EV44-OWN-TITLE](#ev44-own-title), [EV44-OWN-ABSTRACT](#ev44-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 45: PMID 28605608 — SYN-c880f84165d0

Topic: `sglt2-primary-prevention-hf`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: Multiple named trial parents NCT01032629, NCT01989754; the integrated publication cannot become one family without splitting/aliasing.

The two parent names are FOUND as identifier evidence. A future object per family requires a report/analysis split; no unique merged family or effect is established.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E02](#b53-45-e02) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E01](#b53-45-e01), [B53-45-E03](#b53-45-e03), [B53-45-E05](#b53-45-e05), [B53-45-E06](#b53-45-e06), [B53-45-E08](#b53-45-e08) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E01](#b53-45-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E01](#b53-45-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E01](#b53-45-e01) |
| `masking` (additional excluded requirement): At least double masking for the relevant randomized phase. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E05](#b53-45-e05), [B53-45-E08](#b53-45-e08) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-45-E01](#b53-45-e01) |

The primary integrated report establishes assignment separately in CANVAS and CANVAS-R, and names both parents. Both held registry rows establish QUADRUPLE masking. It is not one randomized family and must not merge parent identities.

INFERRED excluded-row diagnosis: **INSTRUMENT_FAMILY_CARDINALITY_LIMIT_WITH_HELD_PICD_AND_BOTH_PARENTS**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-45-E01](#b53-45-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-45-E01](#b53-45-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-45-E01](#b53-45-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV45-OWN-TITLE](#ev45-own-title), [EV45-OWN-ABSTRACT](#ev45-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 46: PMID 26378978 — NCT01131676

Topic: `sglt2-primary-prevention-hf`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 2; identity depth 0; screen depth 2.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [X46-ENTRY](#x46-entry), [B53-46-E01](#b53-46-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-46-E01](#b53-46-e01) |

The B53 primary cut places type 2 diabetes in background. The full primary conclusion identifies the treated trial patients, and the renal companion corroborates them; secondary evidence is therefore not the only entry proof. Registry DOUBLE supplies masking.

Additional scope/phase context (not additional found facts): [B53-46-E02](#b53-46-e02), [B53-46-E03](#b53-46-e03), [B53-46-E04](#b53-46-e04).

Own held context: [EV46-OWN-TITLE](#ev46-own-title), [EV46-OWN-ABSTRACT](#ev46-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 47: PMID 30415602 — NCT01730534

Topic: `sglt2-primary-prevention-hf`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-47-E01](#b53-47-e01) |

The primary methods explicitly randomize type-2-diabetes patients at cardiovascular risk to dapagliflozin/placebo. The elderly companion is not needed for entry; registry QUADRUPLE supplies masking.

Additional scope/phase context (not additional found facts): [B53-47-E02](#b53-47-e02), [B53-47-E03](#b53-47-e03), [B53-47-E04](#b53-47-e04).

Own held context: [EV47-OWN-TITLE](#ev47-own-title), [EV47-OWN-ABSTRACT](#ev47-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 48: PMID 10471456 — SYN-983d4c339111

Topic: `spironolactone-hfref-mortality`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X48-FULL-ABSTRACT](#x48-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-48-E01](#b53-48-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-48-E01](#b53-48-e01) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-48-E01](#b53-48-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-48-E01](#b53-48-e01) |
| `masking` (additional excluded requirement): At least double masking for the relevant randomized phase. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-48-E01](#b53-48-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-48-E01](#b53-48-e01) |

RALES methods explicitly establish severe HFrEF, random assignment, double blinding and spironolactone/placebo. No registry parent is named in the held abstract.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`.

INFERRED excluded-row diagnosis: **HELD_PICD_BUT_PARENT_IDENTIFIER_EVIDENCE_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-48-E01](#b53-48-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-48-E01](#b53-48-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-48-E01](#b53-48-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV48-OWN-TITLE](#ev48-own-title), [EV48-OWN-ABSTRACT](#ev48-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

INFERRED rejected identity match: [EV48-REJECT-SYMPTOM](#ev48-reject-symptom). The lower-case rales term is an entry symptom in another trial, not the RALES acronym or its parent identifier.

### Row 49: PMID 21073363 — NCT00232180

Topic: `spironolactone-hfref-mortality`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `None`. RLX sequence: `ALLOCATION_NOT_RANDOMIZED → INTERVENTION_CONTRAST_NOT_PROVEN → BLINDING_NOT_PROVEN → PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 4; identity depth 0; screen depth 4.

The supplied recorded absence is INTERVENTION_CONTRAST_NOT_PROVEN; RLX's re-read begins with ALLOCATION_NOT_RANDOMIZED. Both inputs are retained. The chain concerns the report's randomized phase; held current registry fields describe a later single-group phase.

Ordered blockers and fact IDs:

1. `ALLOCATION_NOT_RANDOMIZED` → `design`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
3. `BLINDING_NOT_PROVEN` → `masking`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
4. `PLACEBO_CONTROL_NOT_PROVEN` → `placebo_control`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `design`: Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-49-E01](#b53-49-e01), [X49-NCT](#x49-nct); context/counterevidence: [X49-CRITERIA](#x49-criteria), [B53-49-E02](#b53-49-e02), [B53-49-E03](#b53-49-e03), [B53-49-E04](#b53-49-e04) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-49-E01](#b53-49-e01) |
| `masking`: At least double masking for the relevant randomized phase. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-49-E01](#b53-49-e01) |
| `placebo_control`: A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-49-E01](#b53-49-e01) |

The primary report establishes the randomized double-blind eplerenone/placebo phase and names the same NCT. Registry entry requires prior participation in that phase and has one active arm. It cannot be used as the original phase design, but does not contradict the published randomized phase.

Own held context: [EV49-OWN-TITLE](#ev49-own-title), [EV49-OWN-ABSTRACT](#ev49-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 50: PMID 20404379 — SYN-f393bbca005f

Topic: `statins-primary-prevention-elderly`. **INFERRED PARTIAL**. Chain-only: **INFERRED NONE**.

Recorded absence: `REGISTRY_PARENT_UNRESOLVED`. RLX sequence: `REGISTRY_PARENT_UNRESOLVED`. RLX excluded; attempted depth: 0; identity depth 0; screen depth 0.

RLX stopping reason: No explicit registry parent in held family source title/abstract; publication-only PICD is not a parent identifier.

Ordered blockers and fact IDs:

1. `REGISTRY_PARENT_UNRESOLVED` → `registry_parent`; INFERRED NONE. Terminal unrelaxed blocker.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `registry_parent`: A source-named registry parent identifier, with report-to-parent and phase scope explicit. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [X50-FULL-ABSTRACT](#x50-full-abstract) |
| `design` (additional excluded requirement): Random allocation in the relevant reported trial phase; a registry design structure is absent or unsuitable. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-50-E01](#b53-50-e01) |
| `entry_population` (additional excluded requirement): A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-50-E01](#b53-50-e01), [X50-SUBGROUP](#x50-subgroup) |
| `arms` (additional excluded requirement): The intervention and permitted comparator arms, with shared background treatment distinguished. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-50-E01](#b53-50-e01) |
| `randomized_contrast` (additional excluded requirement): Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-50-E01](#b53-50-e01) |
| `placebo_control` (additional excluded requirement): A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-50-E01](#b53-50-e01) |

The named older population is a post-completion age subgroup of JUPITER, not the family entry population. A subset retaining randomized assignments is not a newly randomized elderly-only trial. The report explicitly contradicts treating its age cut-point as entry eligibility.

Missing `registry_parent`: No registry parent is identified in the full held report abstract or supplied family-linked documents. A publication-only identity policy could waive this gate; it cannot make a registry-parent claim true. To settle: A registry record or trial protocol/full report explicitly linking this report to its named parent; otherwise a separately authorized publication-only identity policy would be a waiver, not evidence. Positive controls: PARENT (PASS above).

Missing `entry_population`: The named older population is a post-completion age subgroup of JUPITER, not the family entry population. A subset retaining randomized assignments is not a newly randomized elderly-only trial. The report explicitly contradicts treating its age cut-point as entry eligibility. To settle: An original eligibility/protocol or registry-criteria field establishing the configured entry condition. Where held methods instead show prevention or a post-hoc subgroup, only an explicit population-policy decision can resolve the mismatch; do not invent an entry fact. Positive controls: ENTRY (PASS above).

Missing observed blockers: `REGISTRY_PARENT_UNRESOLVED`.

All missing assessed fact IDs: `registry_parent`, `entry_population`.

INFERRED excluded-row diagnosis: **HELD_PARENT_TRIAL_PICD_BUT_POSTHOC_ENTRY_MISMATCH_AND_IDENTITY_GAP**. Missing machine structures: `registry_design`, `population.conditions`, `arms`.

- `population_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-50-E01](#b53-50-e01). Trial report or its registry material. Actual entry population is described; this material does not establish a configured AAD entry diagnosis or convert an age subgroup into original trial entry.
- `intervention_and_comparator_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-50-E01](#b53-50-e01). Trial report or its registry material. Intervention, comparator and shared background are in the report.
- `design_material` — INFERRED FOUND_IN_TRIAL_OWN_DOCUMENT: [B53-50-E01](#b53-50-e01). Trial report or its registry material. Randomized-design material; for JUPITER this is the parent trial, not newly randomized age-subgroup entry.

The absent machine structures are an instrument/input-representation limit. The additional source-identity, configured-entry or family-cardinality issues named in this classification remain separate; publication PICD cannot fill them by assertion.

Own held context: [EV50-OWN-TITLE](#ev50-own-title), [EV50-OWN-ABSTRACT](#ev50-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

INFERRED rejected identity match: [EV50-REJECT-CITY](#ev50-reject-city). Jupiter is a Florida recruitment city in a different trial, not the JUPITER trial identifier.

INFERRED rejected identity match: [EV50-REJECT-BACKGROUND](#ev50-reject-background). JUPITER is background literature in another registry record. That record's own NCT cannot be assigned to the elderly JUPITER subgroup report.

### Row 51: PMID 19717846 — NCT00391872

Topic: `ticagrelor-vs-clopidogrel-acs`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-51-E01](#b53-51-e01) |

PLATO methods directly randomize ticagrelor versus clopidogrel in acute coronary syndrome; the diabetes substudy is not needed.

Own held context: [EV51-OWN-TITLE](#ev51-own-title), [EV51-OWN-ABSTRACT](#ev51-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 52: PMID 26376600 — NCT01294462

Topic: `ticagrelor-vs-clopidogrel-acs`. **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**. Chain-only: **INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE**.

Recorded absence: `INTERVENTION_CONTRAST_NOT_PROVEN`. RLX sequence: `INTERVENTION_CONTRAST_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 1; identity depth 0; screen depth 1.

Ordered blockers and fact IDs:

1. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-52-E01](#b53-52-e01) |

PHILO methods directly randomize ticagrelor versus clopidogrel in ACS. Planned PCI is an entry attribute and is not excluded by this topic.

Own held context: [EV52-OWN-TITLE](#ev52-own-title), [EV52-OWN-ABSTRACT](#ev52-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

### Row 53: PMID 33933206 — NCT04381936

Topic: `tocilizumab-covid19-mortality`. **INFERRED PARTIAL**. Chain-only: **INFERRED PARTIAL**.

Recorded absence: `ENTRY_POPULATION_NOT_ESTABLISHED`. RLX sequence: `ENTRY_POPULATION_NOT_ESTABLISHED → INTERVENTION_CONTRAST_NOT_PROVEN → PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`. RLX cleared depth: 3; identity depth 0; screen depth 3.

Ordered blockers and fact IDs:

1. `ENTRY_POPULATION_NOT_ESTABLISHED` → `entry_population`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
2. `INTERVENTION_CONTRAST_NOT_PROVEN` → `randomized_contrast`; INFERRED ALL_BLOCKERS_HAVE_HELD_EVIDENCE.
3. `PLACEBO_CONTROL_NOT_PROVEN` → `placebo_control`; INFERRED NONE.

| Needed fact | INFERRED classification | Verbatim support / counterevidence |
|---|---|---|
| `entry_population`: A configured population_any term must describe entry, not background, an outcome, an exclusion or a post-hoc subgroup. The literal screen reads registry conditions only. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-53-E01](#b53-53-e01) |
| `randomized_contrast`: Random assignment between the configured intervention and a permitted comparator, with active comparator and factorial scope explicit. | FOUND_IN_TRIAL_OWN_DOCUMENT | [B53-53-E01](#b53-53-e01) |
| `placebo_control`: A placebo control in the intervention contrast, not usual care or a double-dummy placebo in an active comparison. | NOT_IN_ANY_HELD_DOCUMENT | No supporting span; context/counterevidence: [B53-53-E01](#b53-53-e01) |

The COVID-era comparison directly randomizes usual care alone versus usual care plus tocilizumab in hypoxic/inflamed adults. Corticosteroids are background treatment, not the comparator. Placebo is contradicted; the current registry describes a later pneumonia epoch.

Additional scope/phase context (not additional found facts): [X53-EPOCH](#x53-epoch), [X53-PERIOD](#x53-period).

Missing `placebo_control`: Usual care alone is the randomized comparator, not placebo. The config allows usual care as an alternative but the current screen also demands literal placebo. To settle: A protocol or primary full report showing a placebo randomized control in this same phase. The held usual-care comparison is contrary evidence; accepting it would require a comparator-policy change. Positive controls: PLACEBO (PASS above).

Missing observed blockers: `PLACEBO_CONTROL_NOT_PROVEN`.

All missing assessed fact IDs: `placebo_control`.

Own held context: [EV53-OWN-TITLE](#ev53-own-title), [EV53-OWN-ABSTRACT](#ev53-own-abstract). Other topic documents, all comparator documents and matching cross-topic files are listed in this row's JSON search audit.

## Proposed record — design only

One object per source-bound family and phase, with an explicit report identifier. The blocker map would contain:

```text
{blocker: {fact, document_ref, span, offset, document_sha256, rank}}
```

Use supporting span lists when one quote cannot establish the whole fact, and retain a canonical fact ID when multiple blockers reuse it. Rank distinguishes the trial's own primary report, a registry row, and another named held document. Preserve typed parent identifiers and the original machine absence. Multi-parent publications need separate objects and an explicit report/analysis map.

1. Require an explicitly adopted schema and policy; this lane creates no such route.
2. Re-read held bytes, check physical SHA-256, decompress gzip deterministically, decode UTF-8 without newline normalization, and require text.find(span)>=0 AND text[offset:offset+len(span)]==span. Check decoded hash and byte offset as additional guards, like verified_effects.
3. Check the JSON field pointer and bind the record identifier, registry row/link, parent, phase, intervention and comparator. Generic RANDOMIZED or Placebo tokens from another record must fail closed.
4. Reject unsupported population semantics, unapproved source ranks, wrong-phase substitutions, combined-parent family merging and stale configuration; do not mutate registry conditions.
5. One canonical fact per family/phase may support several blockers without being counted twice. Report subsets and integrated analyses require an explicit family/analysis map.
6. Evidence verification alone cannot authorize eligibility, P8 endpoint binding, effect extraction, variance choice or pool admission.

Show: Hand-established eligibility fact (INFERRED), named reviewer/adoption policy, source rank, exact quote, source link/hash, family/phase scope and remaining uncertainty. Preserve the original machine absence code and distinguish primary evidence, registry evidence and another held document. Never label it parser-confirmed.

No schema, loader, config, eligibility code or page was changed. The proposed format and verification sequence are design only.

## Validation

PASS: 237 of 237 distinct cited spans located at their recorded character offsets, with physical-document SHA-256, decompressed-content SHA-256 and byte-offset checks. 220 of 220 used JSON-pointer citations lie within their named fields. 23 of 23 used compact-registry-row citations match their named registry identifier.

PASS: 53 of 53 supplied row identities and RLX sequences preserved; all completeness and depth tables recomputed. 7 of 7 disclosed positive controls fire. 937 of 937 inventoried held source files and all supplied lane inputs retain their original hashes.

PASS: 2478 of 2478 additional held files outside `cache/` retain their original hashes. No tracked repository change was made, no process was stopped or signaled, and no commit or push was performed.

The second pass checked identifiers, family/phase scope, dates as quoted source text, and aggregate denominators. No treatment-effect statistic was recalculated. Reproduce the audit checks with `python .tmp/ev53_verify_report.py`. These are artifact-integrity checks; no application/UI test is relevant because application files are unchanged.

## Verbatim source-span appendix

Every quote below is exactly located in held bytes. For gzip sources, character offsets refer to decompressed UTF-8 text without newline normalization; document SHA-256 always hashes the physical file. JSON escaping in a raw span is intentional and is not silently replaced with a decoded paraphrase. Citations reused for several facts appear once here.

<a id="b53-01-e01"></a>
### B53-01-E01

Source: `cache/balanced-crystalloids-vs-saline-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `35041780`. INFERRED attribution; exact location verified.

Character offset: 1389; byte offset: 1389. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`. Decoded SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`.

```text
In a double-blind, randomized, controlled trial, we assigned critically ill patients to receive BMES (Plasma-Lyte 148) or saline as fluid therapy in the intensive care unit (ICU) for 90 days.
```

<a id="b53-02-e01"></a>
### B53-02-E01

Source: `cache/balanced-crystalloids-vs-saline-mortality/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `34375394`. INFERRED attribution; exact location verified.

Character offset: 4203; byte offset: 4215. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`. Decoded SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`.

```text
Double-blind, factorial, randomized clinical trial conducted at 75 ICUs in Brazil. Patients who were admitted to the ICU with at least 1 risk factor for worse outcomes, who required at least 1 fluid expansion, and who were expected to remain in the ICU for more than 24 hours were randomized between May 29, 2017, and March 2, 2020; follow-up concluded on October 29, 2020. Patients were randomized to 2 different fluid types (a balanced solution vs saline solution reported in this article) and 2 different infusion rates (reported separately). INTERVENTIONS: Patients were randomly assigned 1:1 to receive either a balanced solution (n = 5522) or 0.9% saline solution (n = 5530) for all intravenous fluids.
```

<a id="b53-03-e01"></a>
### B53-03-E01

Source: `cache/colchicine-postop-af/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `42132185`. INFERRED attribution; exact location verified.

Character offset: 10051; byte offset: 10129. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`. Decoded SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`.

```text
In this randomized, double-blind, placebo-controlled trial, 172 adults scheduled for on-pump CABG received colchicine or placebo.
```

<a id="b53-03-e02"></a>
### B53-03-E02

Source: `cache/colchicine-postop-af/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `42132185`. INFERRED attribution; exact location verified.

Character offset: 11358; byte offset: 11449. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`. Decoded SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`.

```text
TRIAL REGISTRATION: Iranian Registry of Clinical Trials, IRCT20200328046886N6.
```

<a id="b53-04-e01"></a>
### B53-04-E01

Source: `cache/colchicine-secondary-cv-prevention/records.json#/records/71/abstract`. Rank: `PRIMARY_REPORT`. Record: `32865380`. INFERRED attribution; exact location verified.

Character offset: 171074; byte offset: 171771. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`. Decoded SHA-256: `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`.

```text
In a randomized, controlled, double-blind trial, we assigned patients with chronic coronary disease to receive 0.5 mg of colchicine once daily or matching placebo.
```

<a id="b53-05-e01"></a>
### B53-05-E01

Source: `cache/corticosteroids-covid19-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `32678530`. INFERRED attribution; exact location verified.

Character offset: 828; byte offset: 828. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `4653eaca3791dc225f769924e30956b4eb834d354b9afb1629bd0c1807877470`. Decoded SHA-256: `4653eaca3791dc225f769924e30956b4eb834d354b9afb1629bd0c1807877470`.

```text
In this controlled, open-label trial comparing a range of possible treatments in patients who were hospitalized with Covid-19, we randomly assigned patients to receive oral or intravenous dexamethasone (at a dose of 6 mg once daily) for up to 10 days or to receive usual care alone.
```

<a id="b53-06-e01"></a>
### B53-06-E01

Source: `cache/denosumab-vertebral-fracture/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `19671655`. INFERRED attribution; exact location verified.

Character offset: 901; byte offset: 901. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`. Decoded SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`.

```text
We enrolled 7868 women between the ages of 60 and 90 years who had a bone mineral density T score of less than -2.5 but not less than -4.0 at the lumbar spine or total hip. Subjects were randomly assigned to receive either 60 mg of denosumab or placebo subcutaneously every 6 months for 36 months.
```

<a id="b53-06-e06"></a>
### B53-06-E06

Source: `cache/denosumab-vertebral-fracture/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `19671655`. INFERRED attribution; exact location verified.

Character offset: 435; byte offset: 435. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`. Decoded SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`.

```text
Denosumab for prevention of fractures in postmenopausal women with osteoporosis.
```

<a id="b53-07-e01"></a>
### B53-07-E01

Source: `cache/doac-vte-recurrence/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `24344086`. INFERRED attribution; exact location verified.

Character offset: 709; byte offset: 709. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
In a randomized, double-blind, double-dummy trial of 2589 patients with acute VTE treated with low-molecular-weight or unfractionated heparin for 5 to 11 days, we compared dabigatran 150 mg twice daily with warfarin.
```

<a id="b53-08-e01"></a>
### B53-08-E01

Source: `cache/doac-vte-recurrence/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `19966341`. INFERRED attribution; exact location verified.

Character offset: 2889; byte offset: 2889. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
In a randomized, double-blind, noninferiority trial involving patients with acute venous thromboembolism who were initially given parenteral anticoagulation therapy for a median of 9 days (interquartile range, 8 to 11), we compared oral dabigatran, administered at a dose of 150 mg twice daily, with warfarin that was dose-adjusted to achieve an international normalized ratio of 2.0 to 3.0.
```

<a id="b53-09-e01"></a>
### B53-09-E01

Source: `cache/doac-vte-recurrence/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `22449293`. INFERRED attribution; exact location verified.

Character offset: 5692; byte offset: 5692. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
In a randomized, open-label, event-driven, noninferiority trial involving 4832 patients who had acute symptomatic pulmonary embolism with or without deep-vein thrombosis, we compared rivaroxaban (15 mg twice daily for 3 weeks, followed by 20 mg once daily) with standard therapy with enoxaparin followed by an adjusted-dose vitamin K antagonist for 3, 6, or 12 months.
```

<a id="b53-10-e01"></a>
### B53-10-E01

Source: `cache/doac-vte-recurrence/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `21128814`. INFERRED attribution; exact location verified.

Character offset: 7959; byte offset: 7959. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
We conducted an open-label, randomized, event-driven, noninferiority study that compared oral rivaroxaban alone (15 mg twice daily for 3 weeks, followed by 20 mg once daily) with subcutaneous enoxaparin followed by a vitamin K antagonist (either warfarin or acenocoumarol) for 3, 6, or 12 months in patients with acute, symptomatic DVT.
```

<a id="b53-10-e02"></a>
### B53-10-E02

Source: `cache/doac-vte-recurrence/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `21128814`. INFERRED attribution; exact location verified.

Character offset: 9884; byte offset: 9884. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
ClinicalTrials.gov numbers, NCT00440193 and NCT00439725.).
```

<a id="b53-10-e06"></a>
### B53-10-E06

Source: `cache/doac-vte-recurrence/family_registry.payload.json.gz#/objects/200`. Rank: `REGISTRY`. Record: `NCT00440193`. INFERRED attribution; exact location verified.

Character offset: 82146; byte offset: 82150. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `3012bfbf2c5fc6e18eb4942698ac518f343b89ba2ab636cd08d49174842e35b6`. Decoded SHA-256: `b2ca13f1fb0bb5381c03823211176dcf7fc95eaf74da4d3f061ca5a3c246552f`.

```text
Confirmed acute symptomatic proximal DVT without symptomatic PE
```

<a id="b53-10-e07"></a>
### B53-10-E07

Source: `cache/doac-vte-recurrence/family_registry.payload.json.gz#/objects/167`. Rank: `REGISTRY`. Record: `NCT00439725`. INFERRED attribution; exact location verified.

Character offset: 68880; byte offset: 68884. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `3012bfbf2c5fc6e18eb4942698ac518f343b89ba2ab636cd08d49174842e35b6`. Decoded SHA-256: `b2ca13f1fb0bb5381c03823211176dcf7fc95eaf74da4d3f061ca5a3c246552f`.

```text
Patients with confirmed symptomatic PE or DVT who have been treated for 6 or 12 months
```

<a id="b53-11-e01"></a>
### B53-11-E01

Source: `cache/doac-vte-recurrence/records.json#/records/4/abstract`. Rank: `PRIMARY_REPORT`. Record: `23991658`. INFERRED attribution; exact location verified.

Character offset: 10595; byte offset: 10595. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
In a randomized, double-blind, noninferiority study, we randomly assigned patients with acute venous thromboembolism, who had initially received heparin, to receive edoxaban at a dose of 60 mg once daily, or 30 mg once daily (e.g., in the case of patients with creatinine clearance of 30 to 50 ml per minute or a body weight below 60 kg), or to receive warfarin.
```

<a id="b53-12-e01"></a>
### B53-12-E01

Source: `cache/doac-vte-recurrence/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `23808982`. INFERRED attribution; exact location verified.

Character offset: 13211; byte offset: 13211. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
In this randomized, double-blind study, we compared apixaban (at a dose of 10 mg twice daily for 7 days, followed by 5 mg twice daily for 6 months) with conventional therapy (subcutaneous enoxaparin, followed by warfarin) in 5395 patients with acute venous thromboembolism.
```

<a id="b53-13-e01"></a>
### B53-13-E01

Source: `cache/dpp4-mace-t2d/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `30418475`. INFERRED attribution; exact location verified.

Character offset: 6076; byte offset: 6076. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
Randomized, placebo-controlled, multicenter noninferiority trial conducted from August 2013 to August 2016 at 605 clinic sites in 27 countries among adults with type 2 diabetes, hemoglobin A1c of 6.5% to 10.0%, high CV risk (history of vascular disease and urine-albumin creatinine ratio [UACR] >200 mg/g), and high renal risk (reduced eGFR and micro- or macroalbuminuria). Participants with end-stage renal disease (ESRD) were excluded. Final follow-up occurred on January 18, 2018. INTERVENTIONS: Patients were randomized to receive linagliptin, 5 mg once daily (n = 3494), or placebo once daily (n = 3485) added to usual care. Other glucose-lowering medications or insulin could be added based on clinical need and local clinical guidelines.
```

<a id="b53-13-e02"></a>
### B53-13-E02

Source: `cache/dpp4-mace-t2d/family_registry.rows.json.gz#/689/inline/allocation`. Rank: `REGISTRY`. Record: `NCT01897532`. INFERRED attribution; exact location verified.

Character offset: 197238; byte offset: 197268. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `71fdd5736bf703c283398171feeffe16691f00265766aacdea20101c40b15131`. Decoded SHA-256: `53b5ac248c2bfc96848e4b196d7f03e9f83228136cfd6b71bf1768120bf420e3`.

```text
RANDOMIZED
```

<a id="b53-13-e03"></a>
### B53-13-E03

Source: `cache/dpp4-mace-t2d/family_registry.rows.json.gz#/689/inline/intervention_model`. Rank: `REGISTRY`. Record: `NCT01897532`. INFERRED attribution; exact location verified.

Character offset: 197272; byte offset: 197302. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `71fdd5736bf703c283398171feeffe16691f00265766aacdea20101c40b15131`. Decoded SHA-256: `53b5ac248c2bfc96848e4b196d7f03e9f83228136cfd6b71bf1768120bf420e3`.

```text
PARALLEL
```

<a id="b53-13-e04"></a>
### B53-13-E04

Source: `cache/dpp4-mace-t2d/family_registry.rows.json.gz#/689/inline/masking`. Rank: `REGISTRY`. Record: `NCT01897532`. INFERRED attribution; exact location verified.

Character offset: 197293; byte offset: 197323. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `71fdd5736bf703c283398171feeffe16691f00265766aacdea20101c40b15131`. Decoded SHA-256: `53b5ac248c2bfc96848e4b196d7f03e9f83228136cfd6b71bf1768120bf420e3`.

```text
DOUBLE
```

<a id="b53-14-e01"></a>
### B53-14-E01

Source: `cache/dpp4-mace-t2d/records.json#/records/7/abstract`. Rank: `PRIMARY_REPORT`. Record: `28893244`. INFERRED attribution; exact location verified.

Character offset: 21875; byte offset: 21910. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
In this randomized, double-blind study, 4202 patients with T2DM and established CV disease were assigned to either omarigliptin 25 mg q.w. or matching placebo in addition to their existing diabetes therapy.
```

<a id="b53-14-e06"></a>
### B53-14-E06

Source: `cache/dpp4-mace-t2d/records.json#/records/7/abstract`. Rank: `PRIMARY_REPORT`. Record: `28893244`. INFERRED attribution; exact location verified.

Character offset: 21587; byte offset: 21622. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
Omarigliptin is a once-weekly (q.w.) oral DPP-4 inhibitor that is approved for the treatment of patients with type 2 diabetes mellitus (T2DM) in Japan.
```

<a id="b53-15-e01"></a>
### B53-15-E01

Source: `cache/esketamine-trd-madrs/records.json#/records/4/abstract`. Rank: `PRIMARY_REPORT`. Record: `37025256`. INFERRED attribution; exact location verified.

Character offset: 10347; byte offset: 10414. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`. Decoded SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`.

```text
This Phase 3, multicenter study (NCT03434041) was conducted in primarily Chinese patients with treatment-resistant depression (TRD) to support the registration of esketamine nasal spray in China. PATIENTS AND METHODS: This randomized, double-blind, active-controlled study was conducted in China and the United States (US) in patients with TRD (single or recurrent episode). Eligible patients were randomized 1:1 to receive intranasal esketamine or matching placebo, each in conjunction with a newly initiated oral antidepressant (AD; duloxetine, escitalopram, sertraline, and venlafaxine extended release) (ie, esketamine plus AD or AD plus placebo).
```

<a id="b53-16-e01"></a>
### B53-16-E01

Source: `cache/esketamine-trd-madrs/family_registry.rows.json.gz#/713/inline/allocation`. Rank: `REGISTRY`. Record: `NCT02422186`. INFERRED attribution; exact location verified.

Character offset: 218724; byte offset: 218737. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `25549111d911ef7a3d36d1a3a035d2f1c521bbe11c69831de8e57a42a43c0a83`. Decoded SHA-256: `ab426b439628a262d2a925cffc6b1b3274449a4a9074fe9b46a4db69f459851e`.

```text
RANDOMIZED
```

<a id="b53-16-e02"></a>
### B53-16-E02

Source: `cache/esketamine-trd-madrs/family_registry.rows.json.gz#/713/inline/intervention_model`. Rank: `REGISTRY`. Record: `NCT02422186`. INFERRED attribution; exact location verified.

Character offset: 218758; byte offset: 218771. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `25549111d911ef7a3d36d1a3a035d2f1c521bbe11c69831de8e57a42a43c0a83`. Decoded SHA-256: `ab426b439628a262d2a925cffc6b1b3274449a4a9074fe9b46a4db69f459851e`.

```text
PARALLEL
```

<a id="b53-16-e03"></a>
### B53-16-E03

Source: `cache/esketamine-trd-madrs/family_registry.rows.json.gz#/713/inline/masking`. Rank: `REGISTRY`. Record: `NCT02422186`. INFERRED attribution; exact location verified.

Character offset: 218779; byte offset: 218792. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `25549111d911ef7a3d36d1a3a035d2f1c521bbe11c69831de8e57a42a43c0a83`. Decoded SHA-256: `ab426b439628a262d2a925cffc6b1b3274449a4a9074fe9b46a4db69f459851e`.

```text
DOUBLE
```

<a id="b53-16-e05"></a>
### B53-16-E05

Source: `cache/esketamine-trd-madrs/records.json#/ctgov/2/title`. Rank: `REGISTRY`. Record: `NCT02422186`. INFERRED attribution; exact location verified.

Character offset: 279196; byte offset: 280506. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`. Decoded SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`.

```text
A Study to Evaluate the Efficacy, Safety, and Tolerability of Intranasal Esketamine Plus an Oral Antidepressant in Elderly Participants With Treatment-resistant Depression
```

<a id="b53-17-e01"></a>
### B53-17-E01

Source: `cache/glp1-ra-mace-t2d/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `30291013`. INFERRED attribution; exact location verified.

Character offset: 15695; byte offset: 15730. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`. Decoded SHA-256: `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`.

```text
We did a double-blind, randomised, placebo-controlled trial in 610 sites across 28 countries. We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease (at a 1:1 ratio) to groups that either received a subcutaneous injection of albiglutide (30-50 mg, based on glycaemic response and tolerability) or of a matched volume of placebo once a week, in addition to their standard care. Investigators used an interactive voice or web response system to obtain treatment assignment, and patients and all study investigators were masked to their treatment allocation.
```

<a id="b53-17-e02"></a>
### B53-17-E02

Source: `cache/glp1-ra-mace-t2d/family_registry.rows.json.gz#/5853/inline/allocation`. Rank: `REGISTRY`. Record: `NCT02465515`. INFERRED attribution; exact location verified.

Character offset: 1709550; byte offset: 1709795. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `23878acfb9fc36de4e25e131638e0604e7f0c7ffb62dd47c5dba1f2891443b59`. Decoded SHA-256: `64fff681b23c0048d6ae4cd17c58db8a9e3320312b0ac49ff1f9bfbaa66df946`.

```text
RANDOMIZED
```

<a id="b53-17-e03"></a>
### B53-17-E03

Source: `cache/glp1-ra-mace-t2d/family_registry.rows.json.gz#/5853/inline/intervention_model`. Rank: `REGISTRY`. Record: `NCT02465515`. INFERRED attribution; exact location verified.

Character offset: 1709584; byte offset: 1709829. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `23878acfb9fc36de4e25e131638e0604e7f0c7ffb62dd47c5dba1f2891443b59`. Decoded SHA-256: `64fff681b23c0048d6ae4cd17c58db8a9e3320312b0ac49ff1f9bfbaa66df946`.

```text
PARALLEL
```

<a id="b53-17-e04"></a>
### B53-17-E04

Source: `cache/glp1-ra-mace-t2d/family_registry.rows.json.gz#/5853/inline/masking`. Rank: `REGISTRY`. Record: `NCT02465515`. INFERRED attribution; exact location verified.

Character offset: 1709605; byte offset: 1709850. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `23878acfb9fc36de4e25e131638e0604e7f0c7ffb62dd47c5dba1f2891443b59`. Decoded SHA-256: `64fff681b23c0048d6ae4cd17c58db8a9e3320312b0ac49ff1f9bfbaa66df946`.

```text
QUADRUPLE
```

<a id="b53-17-e06"></a>
### B53-17-E06

Source: `cache/glp1-ra-mace-t2d/family_registry.payload.json.gz#/objects/1999/age_min/value`. Rank: `REGISTRY`. Record: `NCT02465515`. INFERRED attribution; exact location verified.

Character offset: 889511; byte offset: 889877. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `9b3150dad60773628dbfdf474d00c949b8485c9c89a5cd0aa063fa6ea619a207`. Decoded SHA-256: `0c0ee6011785ec0c4873c007259acd5a15c8fe78c7e62b4b9251d1fc53b8eec0`.

```text
40 Years
```

<a id="b53-18-e01"></a>
### B53-18-E01

Source: `cache/iv-iron-hfref-hosp/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `40159390`. INFERRED attribution; exact location verified.

Character offset: 907; byte offset: 907. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6ec77b3291b771f5f49adc5f9215f87c7fb6a134c36fb9f26687c626429c75ee`. Decoded SHA-256: `6ec77b3291b771f5f49adc5f9215f87c7fb6a134c36fb9f26687c626429c75ee`.

```text
This multicenter, randomized clinical trial enrolled 1105 patients with heart failure (defined as having a left ventricular ejection fraction of ≤45%) and iron deficiency (serum ferritin level <100 ng/mL; or if transferrin saturation was <20%, a serum ferritin level between 100 ng/mL and 299 ng/mL) at 70 clinic sites in 6 European countries from March 2017 to November 2023. The median follow-up was 16.6 months (IQR, 7.9-29.9 months). INTERVENTION: Administration of ferric carboxymaltose (n = 558) initially given at an intravenous dose of up to 2000 mg that was followed by 500 mg every 4 months (unless stopping criteria were met) vs a saline placebo (n = 547).
```

<a id="b53-19-e01"></a>
### B53-19-E01

Source: `cache/metformin-pcos-ovulation/records.json#/records/28/abstract`. Rank: `PRIMARY_REPORT`. Record: `19522426`. INFERRED attribution; exact location verified.

Character offset: 85596; byte offset: 85715. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
Our prospective study aim is to compare the effectiveness of clomifene citrate plus metformin and clomifene citrate plus placebo in women with newly diagnosed polycystic ovary syndrome. METHODS: From February 24 to September 29 (2007), PCOS was explored on women attending the Department of Obstetrics & Gynaecology sterility consultation unit (CHU Hedi Chaker-Sfax) according to the Rotterdam 2003 diagnostic criteria. PCOS patients were randomized to receive, in addition to clomifene citrate treatment, placebo or metformin 850 mg two times a day all ovulatory cycle for three trials maximum.
```

<a id="b53-20-e01"></a>
### B53-20-E01

Source: `cache/metformin-pcos-ovulation/records.json#/records/39/abstract`. Rank: `PRIMARY_REPORT`. Record: `16769748`. INFERRED attribution; exact location verified.

Character offset: 110349; byte offset: 110468. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
OBJECTIVE: To compare the effectiveness of clomifene citrate plus metformin and clomifene citrate plus placebo in women with newly diagnosed polycystic ovary syndrome. DESIGN: Randomised clinical trial. SETTING: Multicentre trial in 20 Dutch hospitals. PARTICIPANTS: 228 women with polycystic ovary syndrome. INTERVENTIONS: Clomifene citrate plus metformin or clomifene citrate plus placebo.
```

<a id="b53-21-e01"></a>
### B53-21-E01

Source: `cache/metformin-pcos-ovulation/records.json#/records/101/abstract`. Rank: `PRIMARY_REPORT`. Record: `11172832`. INFERRED attribution; exact location verified.

Character offset: 296642; byte offset: 297021. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
DESIGN: Randomized, double-blind, placebo-controlled trial. SETTING: Multicenter environment. PATIENT(S): Anovulatory women with the polycystic ovary syndrome (PCOS) who were resistant to CC. INTERVENTION(S): Participants received placebo or metformin, 500 mg three times daily, for 7 weeks.
```

<a id="b53-21-e02"></a>
### B53-21-E02

Source: `cache/metformin-pcos-ovulation/records.json#/records/101/abstract`. Rank: `PRIMARY_REPORT`. Record: `11172832`. INFERRED attribution; exact location verified.

Character offset: 297068; byte offset: 297447. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
Metformin or placebo was continued and CC treatment was begun at 50 mg daily for 5 days. Serum P level > or =4 ng/mL was considered to indicate ovulation.
```

<a id="b53-22-e01"></a>
### B53-22-E01

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `21830957`. INFERRED attribution; exact location verified.

Character offset: 722; byte offset: 722. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
In a double-blind trial, we randomly assigned 14,264 patients with nonvalvular atrial fibrillation who were at increased risk for stroke to receive either rivaroxaban (at a daily dose of 20 mg) or dose-adjusted warfarin.
```

<a id="b53-23-e01"></a>
### B53-23-E01

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `19717844`. INFERRED attribution; exact location verified.

Character offset: 3154; byte offset: 3154. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
In this noninferiority trial, we randomly assigned 18,113 patients who had atrial fibrillation and a risk of stroke to receive, in a blinded fashion, fixed doses of dabigatran--110 mg or 150 mg twice daily--or, in an unblinded fashion, adjusted-dose warfarin.
```

<a id="b53-24-e01"></a>
### B53-24-E01

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `24251359`. INFERRED attribution; exact location verified.

Character offset: 5709; byte offset: 5709. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
We conducted a randomized, double-blind, double-dummy trial comparing two once-daily regimens of edoxaban with warfarin in 21,105 patients with moderate-to-high-risk atrial fibrillation (median follow-up, 2.8 years).
```

<a id="b53-25-e01"></a>
### B53-25-E01

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `21870978`. INFERRED attribution; exact location verified.

Character offset: 8652; byte offset: 8652. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
In this randomized, double-blind trial, we compared apixaban (at a dose of 5 mg twice daily) with warfarin (target international normalized ratio, 2.0 to 3.0) in 18,201 patients with atrial fibrillation and at least one additional risk factor for stroke.
```

<a id="b53-26-e01"></a>
### B53-26-E01

Source: `cache/omega3-cardiovascular-events/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `33190147`. INFERRED attribution; exact location verified.

Character offset: 3856; byte offset: 3861. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
A double-blind, randomized, multicenter trial (enrollment October 30, 2014, to June 14, 2017; study termination January 8, 2020; last patient visit May 14, 2020) comparing omega-3 CA with corn oil in statin-treated participants with high cardiovascular risk, hypertriglyceridemia, and low levels of high-density lipoprotein cholesterol (HDL-C). A total of 13 078 patients were randomized at 675 academic and community hospitals in 22 countries in North America, Europe, South America, Asia, Australia, New Zealand, and South Africa. INTERVENTIONS: Participants were randomized to receive 4 g/d of omega-3 CA (n = 6539) or corn oil, which was intended to serve as an inert comparator (n = 6539), in addition to usual background therapies, including statins.
```

<a id="b53-27-e01"></a>
### B53-27-E01

Source: `cache/omega3-cardiovascular-events/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `30415628`. INFERRED attribution; exact location verified.

Character offset: 10011; byte offset: 10034. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
We performed a multicenter, randomized, double-blind, placebo-controlled trial involving patients with established cardiovascular disease or with diabetes and other risk factors, who had been receiving statin therapy and who had a fasting triglyceride level of 135 to 499 mg per deciliter (1.52 to 5.63 mmol per liter) and a low-density lipoprotein cholesterol level of 41 to 100 mg per deciliter (1.06 to 2.59 mmol per liter). The patients were randomly assigned to receive 2 g of icosapent ethyl twice daily (total daily dose, 4 g) or placebo.
```

<a id="b53-28-e01"></a>
### B53-28-E01

Source: `cache/omega3-cardiovascular-events/records.json#/records/25/abstract`. Rank: `PRIMARY_REPORT`. Record: `20929341`. INFERRED attribution; exact location verified.

Character offset: 72073; byte offset: 72117. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
In a multicenter, double-blind, placebo-controlled trial, we randomly assigned 4837 patients, 60 through 80 years of age (78% men), who had had a myocardial infarction and were receiving state-of-the-art antihypertensive, antithrombotic, and lipid-modifying therapy to receive for 40 months one of four trial margarines: a margarine supplemented with a combination of EPA and DHA (with a targeted additional daily intake of 400 mg of EPA-DHA), a margarine supplemented with ALA (with a targeted additional daily intake of 2 g of ALA), a margarine supplemented with EPA-DHA and ALA, or a placebo margarine.
```

<a id="b53-29-e01"></a>
### B53-29-E01

Source: `cache/omega3-cardiovascular-events/records.json#/records/76/abstract`. Rank: `PRIMARY_REPORT`. Record: `21115589`. INFERRED attribution; exact location verified.

Character offset: 165601; byte offset: 165762. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
OBJECTIVE: To investigate whether dietary supplementation with B vitamins or omega 3 fatty acids, or both, could prevent major cardiovascular events in patients with a history of ischaemic heart disease or stroke. DESIGN: Double blind, randomised, placebo controlled trial; factorial design. SETTING: Recruitment throughout France via a network of 417 cardiologists, neurologists, and other physicians. PARTICIPANTS: 2501 patients with a history of myocardial infarction, unstable angina, or ischaemic stroke. INTERVENTION: Daily dietary supplement containing 5-methyltetrahydrofolate (560 μg), vitamin B-6 (3 mg), and vitamin B-12 (20 μg) or placebo; and containing omega 3 fatty acids (600 mg of eicosapentanoic acid and docosahexaenoic acid at a ratio of 2:1) or placebo. Median duration of supplementation was 4.7 years.
```

<a id="b53-30-e01"></a>
### B53-30-E01

Source: `cache/pcsk9-mace/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `28304224`. INFERRED attribution; exact location verified.

Character offset: 1559; byte offset: 1559. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `d6897186b50257e98df053070532702dfba5bb4ea37fc8f8644e1ae17312ef8f`. Decoded SHA-256: `d6897186b50257e98df053070532702dfba5bb4ea37fc8f8644e1ae17312ef8f`.

```text
We conducted a randomized, double-blind, placebo-controlled trial involving 27,564 patients with atherosclerotic cardiovascular disease and LDL cholesterol levels of 70 mg per deciliter (1.8 mmol per liter) or higher who were receiving statin therapy. Patients were randomly assigned to receive evolocumab (either 140 mg every 2 weeks or 420 mg monthly) or matching placebo as subcutaneous injections.
```

<a id="b53-31-e01"></a>
### B53-31-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/104/abstract`. Rank: `PRIMARY_REPORT`. Record: `35727573`. INFERRED attribution; exact location verified.

Character offset: 254683; byte offset: 255397. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
This randomized, quadruple-blind, placebo-controlled trial was conducted from February 2018 to May 2021 in a multicenter, mixed setting (inpatients and outpatients). Patients were followed up throughout the intervention period. Eligibility criteria included age 3 months to 18 years, recruitment within 24 hours following initiation of broad-spectrum systemic antibiotics, and signed informed consent. In total, 646 eligible patients were approached and 350 patients took part in the trial. INTERVENTIONS: A multispecies probiotic consisting of Bifidobacterium bifidum W23, Bifidobacterium lactis W51, Lactobacillus acidophilus W37, L acidophilus W55, Lacticaseibacillus paracasei W20, Lactiplantibacillus plantarum W62, Lacticaseibacillus rhamnosus W71, and Ligilactobacillus salivarius W24, for a total dose of 10 billion colony-forming units daily, for the duration of antibiotic treatment and for 7 days after.
```

<a id="b53-32-e01"></a>
### B53-32-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/156/abstract`. Rank: `PRIMARY_REPORT`. Record: `32035998`. INFERRED attribution; exact location verified.

Character offset: 369767; byte offset: 370699. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
A multicentre, double-blind, placebo-controlled, randomized trial was conducted to evaluate the role of Lactobacillus casei DN114001 (combined as a drink with two regular yoghurt bacterial strains) in reducing AAD and Clostridioides difficile infection in patients aged over 55 years.
```

<a id="b53-32-s01"></a>
### B53-32-S01

Source: `cache/probiotics-aad-prevention/comparator_fulltext.txt`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 14286; byte offset: 14444. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`. Decoded SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`.

```text
Rajkumar et al 64 1126 (549:577) Inpatient ≥55 L. casei DN114001 , L. delbrueckii subspecies bulgaricus, S. thermophilus 20.4×10 9 Duration of antibiotic+7 days Placebo ≥2 loose stools (5–7 Bristol Stool Scale) in 24 hours
```

<a id="b53-33-e01"></a>
### B53-33-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/328/abstract`. Rank: `PRIMARY_REPORT`. Record: `24772726`. INFERRED attribution; exact location verified.

Character offset: 789902; byte offset: 791991. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIMS: To evaluate the effectiveness, safety and tolerability of a probiotic formulation containing Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12 in the prevention of antibiotic associated diarrhoea (AAD). METHODS AND MATERIAL: A double-blind randomised placebo controlled multicentric trial was conducted in adults who were prescribed a seven-day course of oral antibiotic (either cefadroxil or amoxycillin) for a documented indication. The effectiveness of a 14-day therapy (concomitant with antibiotic course and seven days thereafter) of the probiotic formulation in preventing AAD was evaluated.
```

<a id="b53-34-e01"></a>
### B53-34-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/333/abstract`. Rank: `PRIMARY_REPORT`. Record: `23932219`. INFERRED attribution; exact location verified.

Character offset: 803609; byte offset: 805728. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
We did a multicentre, randomised, double-blind, placebo-controlled, pragmatic, efficacy trial of inpatients aged 65 years and older and exposed to one or more oral or parenteral antibiotics. A computer-generated randomisation scheme was used to allocate participants (in a 1:1 ratio) to receive either a multistrain preparation of lactobacilli and bifidobacteria, with a total of 6 × 10(10) organisms, one per day for 21 days, or an identical placebo. Patients, study staff, and specimen and data analysts were masked to assignment.
```

<a id="b53-35-e01"></a>
### B53-35-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/357/abstract`. Rank: `PRIMARY_REPORT`. Record: `18701826`. INFERRED attribution; exact location verified.

Character offset: 859146; byte offset: 861328. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIM: To determine the efficacy of a combination of Bifidobacterium longum PL03, Lactobacillus rhamnosus KL53A and Lactobacillus plantarum PL02 for the prevention of antibiotic-associated diarrhea in children. METHODS: Seventy-eight children (age: 5 months to 16 years) with otitis media, and/or respiratory tract infections, and/or urinary tract infections were enrolled in a double-blind randomized control trial in which they received standard antibiotic treatment plus a food supplement containing 10(8) colony-forming units of B. longum, L. rhamnosus and L. plantarum (n = 40) or a placebo (n = 38) orally twice daily for the duration of antibiotic treatment.
```

<a id="b53-36-e01"></a>
### B53-36-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/359/abstract`. Rank: `PRIMARY_REPORT`. Record: `18410562`. INFERRED attribution; exact location verified.

Character offset: 863686; byte offset: 865868. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIM: To determine the efficacy of administration of Lactobacillus rhamnosus (strains E/N, Oxy and Pen) for the prevention of antibiotic-associated diarrhoea in children. METHODS: Children (aged 3 months to 14 years) with common infections were enrolled in a double-blind, randomized, placebo-controlled trial in which they received standard antibiotic treatment plus 2 x 10(10) colony forming units of a probiotic (n = 120) or a placebo (n = 120), administered orally twice daily throughout antibiotic treatment.
```

<a id="b53-37-e01"></a>
### B53-37-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/375/abstract`. Rank: `PRIMARY_REPORT`. Record: `15740542`. INFERRED attribution; exact location verified.

Character offset: 897259; byte offset: 899441. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIM: To determine whether S. boulardii prevents antibiotic-associated diarrhoea in children. METHODS: A total of 269 children (aged 6 months to 14 years) with otitis media and/or respiratory tract infections were enrolled in a double-blind, randomized placebo-controlled trial in which they received standard antibiotic treatment plus 250 mg of S. boulardii (experimental group, n = 132) or a placebo (control group, n = 137) orally twice daily for the duration of antibiotic treatment.
```

<a id="b53-38-e01"></a>
### B53-38-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/384/abstract`. Rank: `PRIMARY_REPORT`. Record: `11560298`. INFERRED attribution; exact location verified.

Character offset: 917673; byte offset: 919855. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
OBJECTIVES: To assess the efficacy of Lactobacillus GG in preventing antibiotic-associated diarrhea (AAD) in adults and, secondarily, to assess the effect of coadministered Lactobacillus GG on the number of tests performed to determine the cause of diarrhea. PATIENTS AND METHODS: In this prospective, randomized, double-blind, placebo-controlled trial conducted from July 1998 to October 1999, 302 hospitalized patients receiving antibiotics were randomized to receive Lactobacillus GG, 20 x 10(9) CFU/d, or placebo for 14 days.
```

<a id="b53-39-e01"></a>
### B53-39-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/400/abstract`. Rank: `PRIMARY_REPORT`. Record: `7872284`. INFERRED attribution; exact location verified.

Character offset: 953046; byte offset: 955228. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
OBJECTIVES: To determine the safety and efficacy of a new preventive agent for antibiotic-associated diarrhea (AAD) in patients receiving at least one beta-lactam antibiotic. METHODS: A double-blinded, placebo-controlled, parallel group study was performed in a high-risk group of hospitalized patients receiving a new prescription for a beta-lactam antibiotic and having no acute diarrhea on enrollment. Lyophilized Saccharomyces boulardii or placebo (1 g/day) was given within 72 h of the start of the antibiotic(s) and continued until 3 days after the antibiotic was discontinued, after which the patients were followed for 7 wk.
```

<a id="b53-39-s01"></a>
### B53-39-S01

Source: `cache/probiotics-aad-prevention/comparator_fulltext.txt`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 13259; byte offset: 13387. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`. Decoded SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`.

```text
McFarland et al 59 193 (97:96) Inpatient >18 S. boulardii Not noted Duration of antibiotic+3 days Placebo ≥3 loose stools (5–7 Bristol Stool Scale) for ≥2 days
```

<a id="b53-39-s02"></a>
### B53-39-S02

Source: `cache/probiotics-aad-prevention/records.json#/records/400/pubtypes/4`. Rank: `INDEXING`. Record: `7872284`. INFERRED attribution; exact location verified.

Character offset: 954440; byte offset: 956622. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Randomized Controlled Trial
```

<a id="b53-40-e01"></a>
### B53-40-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/420/abstract`. Rank: `PRIMARY_REPORT`. Record: `21165295`. INFERRED attribution; exact location verified.

Character offset: 996128; byte offset: 998356. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
The aim of this multicenter, randomized, placebo-controlled, double-blind trial was to assess the efficacy of probiotic Lactobacillus (Lacidofil® cap) for the prevention of AAD in adults. From September 2008 to November 2009, a total of 214 patients with respiratory tract infection who had begun receiving antibiotics were randomized to receive Lactobacillus (Lacidofil® cap) or placebo for 14 days.
```

<a id="b53-41-e01"></a>
### B53-41-E01

Source: `cache/probiotics-aad-prevention/records.json#/records/430/abstract`. Rank: `PRIMARY_REPORT`. Record: `18026577`. INFERRED attribution; exact location verified.

Character offset: 1011241; byte offset: 1013472. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
The main objective of the present study was to assess the efficacy and safety of a fermented milk combining Lactobacillus acidophilus and Lactobacillus casei that is widely available in Canada, in the prevention of antibiotic-associated diarrhea. METHODS: In this double-blind, randomized study, hospitalized patients were randomly assigned to receive either a lactobacilli-fermented milk or a placebo on a daily basis.
```

<a id="b53-41-s01"></a>
### B53-41-S01

Source: `cache/probiotics-aad-prevention/comparator_fulltext.txt`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 9317; byte offset: 9338. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`. Decoded SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`.

```text
Beausoleil et al 42 89 (44:45) Inpatient 54–85 L. acidophilus , L. casei (Bio-K+CL1285, Bio-K+International, Canada) 50×10 9 Duration of antibiotic Placebo ≥3 loose stools (5–7 Bristol Stool Scale) in 24 hours
```

<a id="b53-42-e01"></a>
### B53-42-E01

Source: `cache/sacubitril-valsartan-hfref/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `25176015`. INFERRED attribution; exact location verified.

Character offset: 779; byte offset: 779. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`. Decoded SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`.

```text
In this double-blind trial, we randomly assigned 8442 patients with class II, III, or IV heart failure and an ejection fraction of 40% or less to receive either LCZ696 (at a dose of 200 mg twice daily) or enalapril (at a dose of 10 mg twice daily), in addition to recommended therapy.
```

<a id="b53-43-e01"></a>
### B53-43-E01

Source: `cache/sacubitril-valsartan-hfref/family_registry.rows.json.gz#/1135/inline/allocation`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 344772; byte offset: 344793. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `1bc4c3f80dac5937d2f4ffbb37808ce9328e73ac0fba24187ff812712fcb4124`. Decoded SHA-256: `16aff38ccb438e69fb47597780380e46aa221b7504df2b204d65cbf444c13651`.

```text
RANDOMIZED
```

<a id="b53-43-e05"></a>
### B53-43-E05

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/144/label/value`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 84546; byte offset: 84564. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
LCZ696
```

<a id="b53-43-e06"></a>
### B53-43-E06

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/144/drug/value/0`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 84437; byte offset: 84455. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
LCZ696
```

<a id="b53-43-e07"></a>
### B53-43-E07

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/144/drug/value/1`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 84446; byte offset: 84464. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
Placebo to Enalapril
```

<a id="b53-43-e08"></a>
### B53-43-E08

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/146/label/value`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 85320; byte offset: 85338. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
Enalapril
```

<a id="b53-43-e09"></a>
### B53-43-E09

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/146/drug/value/0`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 85211; byte offset: 85229. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
Enalapril
```

<a id="b53-43-e10"></a>
### B53-43-E10

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/146/drug/value/1`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 85223; byte offset: 85241. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
Placebo to LCZ696
```

<a id="b53-44-e01"></a>
### B53-44-E01

Source: `cache/semaglutide-obesity-mace/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `37952131`. INFERRED attribution; exact location verified.

Character offset: 906; byte offset: 906. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`. Decoded SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`.

```text
In a multicenter, double-blind, randomized, placebo-controlled, event-driven superiority trial, we enrolled patients 45 years of age or older who had preexisting cardiovascular disease and a body-mass index (the weight in kilograms divided by the square of the height in meters) of 27 or greater but no history of diabetes. Patients were randomly assigned in a 1:1 ratio to receive once-weekly subcutaneous semaglutide at a dose of 2.4 mg or placebo.
```

<a id="b53-45-e01"></a>
### B53-45-E01

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `28605608`. INFERRED attribution; exact location verified.

Character offset: 749; byte offset: 749. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
Methods The CANVAS Program integrated data from two trials involving a total of 10,142 participants with type 2 diabetes and high cardiovascular risk. Participants in each trial were randomly assigned to receive canagliflozin or placebo and were followed for a mean of 188.2 weeks.
```

<a id="b53-45-e02"></a>
### B53-45-E02

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `28605608`. INFERRED attribution; exact location verified.

Character offset: 2732; byte offset: 2732. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754 , respectively.).
```

<a id="b53-45-e03"></a>
### B53-45-E03

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5378/inline/allocation`. Rank: `REGISTRY`. Record: `NCT01032629`. INFERRED attribution; exact location verified.

Character offset: 1552669; byte offset: 1552863. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
RANDOMIZED
```

<a id="b53-45-e05"></a>
### B53-45-E05

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5378/inline/masking`. Rank: `REGISTRY`. Record: `NCT01032629`. INFERRED attribution; exact location verified.

Character offset: 1552724; byte offset: 1552918. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
QUADRUPLE
```

<a id="b53-45-e06"></a>
### B53-45-E06

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5384/inline/allocation`. Rank: `REGISTRY`. Record: `NCT01989754`. INFERRED attribution; exact location verified.

Character offset: 1554406; byte offset: 1554600. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
RANDOMIZED
```

<a id="b53-45-e08"></a>
### B53-45-E08

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5384/inline/masking`. Rank: `REGISTRY`. Record: `NCT01989754`. INFERRED attribution; exact location verified.

Character offset: 1554461; byte offset: 1554655. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
QUADRUPLE
```

<a id="b53-46-e01"></a>
### B53-46-E01

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `26378978`. INFERRED attribution; exact location verified.

Character offset: 3288; byte offset: 3288. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
BACKGROUND: The effects of empagliflozin, an inhibitor of sodium-glucose cotransporter 2, in addition to standard care, on cardiovascular morbidity and mortality in patients with type 2 diabetes at high cardiovascular risk are not known. METHODS: We randomly assigned patients to receive 10 mg or 25 mg of empagliflozin or placebo once daily.
```

<a id="b53-46-e02"></a>
### B53-46-E02

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5231/inline/allocation`. Rank: `REGISTRY`. Record: `NCT01131676`. INFERRED attribution; exact location verified.

Character offset: 1510566; byte offset: 1510760. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
RANDOMIZED
```

<a id="b53-46-e03"></a>
### B53-46-E03

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5231/inline/intervention_model`. Rank: `REGISTRY`. Record: `NCT01131676`. INFERRED attribution; exact location verified.

Character offset: 1510600; byte offset: 1510794. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
PARALLEL
```

<a id="b53-46-e04"></a>
### B53-46-E04

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5231/inline/masking`. Rank: `REGISTRY`. Record: `NCT01131676`. INFERRED attribution; exact location verified.

Character offset: 1510621; byte offset: 1510815. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
DOUBLE
```

<a id="b53-47-e01"></a>
### B53-47-E01

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `30415602`. INFERRED attribution; exact location verified.

Character offset: 8906; byte offset: 8910. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
We randomly assigned patients with type 2 diabetes who had or were at risk for atherosclerotic cardiovascular disease to receive either dapagliflozin or placebo.
```

<a id="b53-47-e02"></a>
### B53-47-E02

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5412/inline/allocation`. Rank: `REGISTRY`. Record: `NCT01730534`. INFERRED attribution; exact location verified.

Character offset: 1562509; byte offset: 1562703. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
RANDOMIZED
```

<a id="b53-47-e03"></a>
### B53-47-E03

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5412/inline/intervention_model`. Rank: `REGISTRY`. Record: `NCT01730534`. INFERRED attribution; exact location verified.

Character offset: 1562543; byte offset: 1562737. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
PARALLEL
```

<a id="b53-47-e04"></a>
### B53-47-E04

Source: `cache/sglt2-primary-prevention-hf/family_registry.rows.json.gz#/5412/inline/masking`. Rank: `REGISTRY`. Record: `NCT01730534`. INFERRED attribution; exact location verified.

Character offset: 1562564; byte offset: 1562758. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `a47dad85e82f6d4289d0478583c52e3d1db2bde5f86ff71bdc2ab7562b00638a`. Decoded SHA-256: `96afcc4e0fe250f88cdf904d2f43f1286d881b59b3e57a3f62213911d55ce613`.

```text
QUADRUPLE
```

<a id="b53-48-e01"></a>
### B53-48-E01

Source: `cache/spironolactone-hfref-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `10471456`. INFERRED attribution; exact location verified.

Character offset: 577; byte offset: 577. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
In a doubleblind study, we enrolled 1663 patients who had severe heart failure and a left ventricular ejection fraction of no more than 35 percent and who were being treated with an angiotensin-converting-enzyme inhibitor, a loop diuretic, and in most cases digoxin. A total of 822 patients were randomly assigned to receive 25 mg of spironolactone daily, and 841 to receive placebo.
```

<a id="b53-49-e01"></a>
### B53-49-E01

Source: `cache/spironolactone-hfref-mortality/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `21073363`. INFERRED attribution; exact location verified.

Character offset: 3151; byte offset: 3151. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
In this randomized, double-blind trial, we randomly assigned 2737 patients with New York Heart Association class II heart failure and an ejection fraction of no more than 35% to receive eplerenone (up to 50 mg daily) or placebo, in addition to recommended therapy.
```

<a id="b53-49-e02"></a>
### B53-49-E02

Source: `cache/spironolactone-hfref-mortality/family_registry.rows.json.gz#/535/inline/allocation`. Rank: `REGISTRY`. Record: `NCT00232180`. INFERRED attribution; exact location verified.

Character offset: 162949; byte offset: 162975. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `602c59fc19c96a5704753fe7ef3bb07a2bb8edd6b1a65c87fe2d25744cdf63e1`. Decoded SHA-256: `539f965645f50ce13783edc21c8f5a7a85bae1ef20c812d022748b880532b25f`.

```text
NON_RANDOMIZED
```

<a id="b53-49-e03"></a>
### B53-49-E03

Source: `cache/spironolactone-hfref-mortality/family_registry.rows.json.gz#/535/inline/intervention_model`. Rank: `REGISTRY`. Record: `NCT00232180`. INFERRED attribution; exact location verified.

Character offset: 162987; byte offset: 163013. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `602c59fc19c96a5704753fe7ef3bb07a2bb8edd6b1a65c87fe2d25744cdf63e1`. Decoded SHA-256: `539f965645f50ce13783edc21c8f5a7a85bae1ef20c812d022748b880532b25f`.

```text
SINGLE_GROUP
```

<a id="b53-49-e04"></a>
### B53-49-E04

Source: `cache/spironolactone-hfref-mortality/family_registry.rows.json.gz#/535/inline/masking`. Rank: `REGISTRY`. Record: `NCT00232180`. INFERRED attribution; exact location verified.

Character offset: 163012; byte offset: 163038. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `602c59fc19c96a5704753fe7ef3bb07a2bb8edd6b1a65c87fe2d25744cdf63e1`. Decoded SHA-256: `539f965645f50ce13783edc21c8f5a7a85bae1ef20c812d022748b880532b25f`.

```text
NONE
```

<a id="b53-50-e01"></a>
### B53-50-E01

Source: `cache/statins-primary-prevention-elderly/records.json#/records/0/abstract`. Rank: `SECONDARY_TRIAL_REPORT`. Record: `20404379`. INFERRED attribution; exact location verified.

Character offset: 1108; byte offset: 1108. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`. Decoded SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`.

```text
OBJECTIVE: To assess the efficacy and safety of rosuvastatin in persons 70 years or older. DESIGN: Secondary analysis of JUPITER (Justification for the Use of statins in Prevention: an Intervention Trial Evaluating Rosuvastatin), a randomized, double-blind, placebo-controlled trial. SETTING: 1315 sites in 26 countries randomly assigned participants in JUPITER. PARTICIPANTS: Among the 17 802 participants randomly assigned with low-density lipoprotein (LDL) cholesterol levels less than 3.37 mmol/L (<130 mg/dL) and high-sensitivity C-reactive protein levels of 2.0 mg/L or more without cardiovascular disease, 5695 were 70 years or older. INTERVENTION: Participants were randomly assigned in a 1:1 ratio to receive 20 mg of rosuvastatin daily or placebo.
```

<a id="b53-51-e01"></a>
### B53-51-E01

Source: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `19717846`. INFERRED attribution; exact location verified.

Character offset: 588; byte offset: 588. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`. Decoded SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`.

```text
In this multicenter, double-blind, randomized trial, we compared ticagrelor (180-mg loading dose, 90 mg twice daily thereafter) and clopidogrel (300-to-600-mg loading dose, 75 mg daily thereafter) for the prevention of cardiovascular events in 18,624 patients admitted to the hospital with an acute coronary syndrome, with or without ST-segment elevation.
```

<a id="b53-52-e01"></a>
### B53-52-E01

Source: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/records/29/abstract`. Rank: `PRIMARY_REPORT`. Record: `26376600`. INFERRED attribution; exact location verified.

Character offset: 61865; byte offset: 61949. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`. Decoded SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`.

```text
The multicenter, double-blind, randomized PHILO trial compared the safety and efficacy of ticagrelor vs. clopidogrel in 801 patients with ACS (Japanese, n=721; Taiwanese, n=35; South Korean, n=44; unknown ethnicity, n=1). All were planned to undergo percutaneous coronary intervention and randomized within 24 h of symptom onset.
```

<a id="b53-53-e01"></a>
### B53-53-E01

Source: `cache/tocilizumab-covid19-mortality/records.json#/records/8/abstract`. Rank: `PRIMARY_REPORT`. Record: `33933206`. INFERRED attribution; exact location verified.

Character offset: 16156; byte offset: 16207. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`. Decoded SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`.

```text
BACKGROUND: In this study, we aimed to evaluate the effects of tocilizumab in adult patients admitted to hospital with COVID-19 with both hypoxia and systemic inflammation. METHODS: This randomised, controlled, open-label, platform trial (Randomised Evaluation of COVID-19 Therapy [RECOVERY]), is assessing several possible treatments in patients hospitalised with COVID-19 in the UK. Those trial participants with hypoxia (oxygen saturation <92% on air or requiring oxygen therapy) and evidence of systemic inflammation (C-reactive protein ≥75 mg/L) were eligible for random assignment in a 1:1 ratio to usual standard of care alone versus usual standard of care plus tocilizumab at a dose of 400 mg-800 mg (depending on weight) given intravenously.
```

<a id="ev01-own-abstract"></a>
### EV01-OWN-ABSTRACT

Source: `cache/balanced-crystalloids-vs-saline-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `35041780`. INFERRED attribution; exact location verified.

Character offset: 1161; byte offset: 1161. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`. Decoded SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`.

```text
BACKGROUND: Whether the use of balanced multielectrolyte solution (BMES) in preference to 0.9% sodium chloride solution (saline) in critically ill patients reduces the risk of acute kidney injury or death is uncertain. METHODS: In a double-blind, randomized, controlled trial, we assigned critically ill patients to receive BMES (Plasma-Lyte 148) or saline as fluid therapy in the intensive care unit (ICU) for 90 days. The primary outcome was death from any cause within 90 days after randomization. Secondary outcomes were receipt of new renal-replacement therapy and the maximum increase in the creatinine level during ICU stay. RESULTS: A total of 5037 patients were recruited from 53 ICUs in Australia and New Zealand - 2515 patients were assigned to the BMES group and 2522 to the saline group. Death within 90 days after randomization occurred in 530 of 2433 patients (21.8%) in the BMES group and in 530 of 2413 patients (22.0%) in the saline group, for a difference of -0.15 percentage points (95% confidence interval [CI], -3.60 to 3.30; P = 0.90). New renal-replacement therapy was initiated in 306 of 2403 patients (12.7%) in the BMES group and in 310 of 2394 patients (12.9%) in the saline group, for a difference of -0.20 percentage points (95% CI, -2.96 to 2.56). The mean (±SD) maximum increase in serum creatinine level was 0.41±1.06 mg per deciliter (36.6±94.0 μmol per liter) in the BMES group and 0.41±1.02 mg per deciliter (36.1±90.0 μmol per liter) in the saline group, for a difference of 0.01 mg per deciliter (95% CI, -0.05 to 0.06) (0.5 μmol per liter [95% CI, -4.7 to 5.7]). The number of adverse and serious adverse events did not differ meaningfully between the groups. CONCLUSIONS: We found no evidence that the risk of death or acute kidney injury among critically ill adults in the ICU was lower with the use of BMES than with saline. (Funded by the National Health and Medical Research Council of Australia and the Health Research Council of New Zealand; PLUS ClinicalTrials.gov number, NCT02721654.).
```

<a id="ev01-own-title"></a>
### EV01-OWN-TITLE

Source: `cache/balanced-crystalloids-vs-saline-mortality/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `35041780`. INFERRED attribution; exact location verified.

Character offset: 1065; byte offset: 1065. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`. Decoded SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`.

```text
Balanced Multielectrolyte Solution versus Saline in Critically Ill Adults.
```

<a id="ev02-own-abstract"></a>
### EV02-OWN-ABSTRACT

Source: `cache/balanced-crystalloids-vs-saline-mortality/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `34375394`. INFERRED attribution; exact location verified.

Character offset: 3779; byte offset: 3791. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`. Decoded SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`.

```text
IMPORTANCE: Intravenous fluids are used for almost all intensive care unit (ICU) patients. Clinical and laboratory studies have questioned whether specific fluid types result in improved outcomes, including mortality and acute kidney injury. OBJECTIVE: To determine the effect of a balanced solution vs saline solution (0.9% sodium chloride) on 90-day survival in critically ill patients. DESIGN, SETTING, AND PARTICIPANTS: Double-blind, factorial, randomized clinical trial conducted at 75 ICUs in Brazil. Patients who were admitted to the ICU with at least 1 risk factor for worse outcomes, who required at least 1 fluid expansion, and who were expected to remain in the ICU for more than 24 hours were randomized between May 29, 2017, and March 2, 2020; follow-up concluded on October 29, 2020. Patients were randomized to 2 different fluid types (a balanced solution vs saline solution reported in this article) and 2 different infusion rates (reported separately). INTERVENTIONS: Patients were randomly assigned 1:1 to receive either a balanced solution (n = 5522) or 0.9% saline solution (n = 5530) for all intravenous fluids. MAIN OUTCOMES AND MEASURES: The primary outcome was 90-day survival. RESULTS: Among 11 052 patients who were randomized, 10 520 (95.2%) were available for the analysis (mean age, 61.1 [SD, 17] years; 44.2% were women). There was no significant interaction between the 2 interventions (fluid type and infusion speed; P = .98). Planned surgical admissions represented 48.4% of all patients. Of all the patients, 60.6% had hypotension or vasopressor use and 44.3% required mechanical ventilation at enrollment. Patients in both groups received a median of 1.5 L of fluid during the first day after enrollment. By day 90, 1381 of 5230 patients (26.4%) assigned to a balanced solution died vs 1439 of 5290 patients (27.2%) assigned to saline solution (adjusted hazard ratio, 0.97 [95% CI, 0.90-1.05]; P = .47). There were no unexpected treatment-related severe adverse events in either group. CONCLUSION AND RELEVANCE: Among critically ill patients requiring fluid challenges, use of a balanced solution compared with 0.9% saline solution did not significantly reduce 90-day mortality. The findings do not support the use of this balanced solution. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT02875873.
```

<a id="ev02-own-title"></a>
### EV02-OWN-TITLE

Source: `cache/balanced-crystalloids-vs-saline-mortality/records.json#/records/1/title`. Rank: `PRIMARY_REPORT`. Record: `34375394`. INFERRED attribution; exact location verified.

Character offset: 3592; byte offset: 3604. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`. Decoded SHA-256: `79cfa5f4702bbc615f1c5038a3c1c2ac4e598a97847f167f4428a7205a8eb335`.

```text
Effect of Intravenous Fluid Treatment With a Balanced Solution vs 0.9% Saline Solution on Mortality in Critically Ill Patients: The BaSICS Randomized Clinical Trial.
```

<a id="ev03-own-abstract"></a>
### EV03-OWN-ABSTRACT

Source: `cache/colchicine-postop-af/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `42132185`. INFERRED attribution; exact location verified.

Character offset: 9604; byte offset: 9682. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`. Decoded SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`.

```text
BACKGROUND: Postoperative arrhythmias are common after coronary artery bypass graft (CABG) surgery and are linked to adverse outcomes. Colchicine, an anti-inflammatory agent, has shown inconsistent results in prior studies, possibly due to dosing and timing variations. OBJECTIVES: To evaluate the efficacy and safety of short-term, weight-adjusted colchicine initiated preoperatively for preventing postoperative arrhythmias after CABG. METHODS: In this randomized, double-blind, placebo-controlled trial, 172 adults scheduled for on-pump CABG received colchicine or placebo. The regimen included a preoperative loading dose (1 mg twice daily) followed by a weight-based maintenance dose (0.5 mg daily if <70 kg; 1 mg daily if ≥70 kg) for 14 days. The primary outcome was incidence of postoperative atrial fibrillation (POAF). Secondary outcomes included early (≤48 h) and late (>48 h) POAF, other arrhythmias, inflammatory markers (CRP, ESR), length of stay, and adverse events. RESULTS: Of 163 analyzed patients (81 colchicine, 82 placebo), POAF incidence was significantly lower in the colchicine group (17.3% vs. 46.3%; RR 0.37, 95% CI 0.21-0.66; p < 0.001), with an absolute risk reduction of 29.0% and number needed to treat (NNT) of 4. Colchicine reduced both early and late POAF (p < 0.001 and p = 0.002). No significant reduction was seen in other arrhythmias. Gastrointestinal events, primarily diarrhea, were more common with colchicine (25.9% vs. 8.5%, p = 0.003), but were manageable and without serious adverse events. CONCLUSION: Short-term perioperative weight-adjusted colchicine is effective and safe for preventing POAF after CABG, with a low NNT and manageable side effects, though it did not significantly affect other arrhythmias. TRIAL REGISTRATION: Iranian Registry of Clinical Trials, IRCT20200328046886N6.
```

<a id="ev03-own-title"></a>
### EV03-OWN-TITLE

Source: `cache/colchicine-postop-af/records.json#/records/5/title`. Rank: `PRIMARY_REPORT`. Record: `42132185`. INFERRED attribution; exact location verified.

Character offset: 9464; byte offset: 9542. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`. Decoded SHA-256: `7d4566ef2b14f4053b82d88a46bc5cfa1df02deb6757e121ed3385e58a7096af`.

```text
Short-Term, Weight-Adjusted Colchicine to Prevent Post-CABG Arrhythmias: A Randomized, Double-Blind, Controlled Trial.
```

<a id="ev04-own-abstract"></a>
### EV04-OWN-ABSTRACT

Source: `cache/colchicine-secondary-cv-prevention/records.json#/records/71/abstract`. Rank: `PRIMARY_REPORT`. Record: `32865380`. INFERRED attribution; exact location verified.

Character offset: 170786; byte offset: 171483. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`. Decoded SHA-256: `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`.

```text
BACKGROUND: Evidence from a recent trial has shown that the antiinflammatory effects of colchicine reduce the risk of cardiovascular events in patients with recent myocardial infarction, but evidence of such a risk reduction in patients with chronic coronary disease is limited. METHODS: In a randomized, controlled, double-blind trial, we assigned patients with chronic coronary disease to receive 0.5 mg of colchicine once daily or matching placebo. The primary end point was a composite of cardiovascular death, spontaneous (nonprocedural) myocardial infarction, ischemic stroke, or ischemia-driven coronary revascularization. The key secondary end point was a composite of cardiovascular death, spontaneous myocardial infarction, or ischemic stroke. RESULTS: A total of 5522 patients underwent randomization; 2762 were assigned to the colchicine group and 2760 to the placebo group. The median duration of follow-up was 28.6 months. A primary end-point event occurred in 187 patients (6.8%) in the colchicine group and in 264 patients (9.6%) in the placebo group (incidence, 2.5 vs. 3.6 events per 100 person-years; hazard ratio, 0.69; 95% confidence interval [CI], 0.57 to 0.83; P<0.001). A key secondary end-point event occurred in 115 patients (4.2%) in the colchicine group and in 157 patients (5.7%) in the placebo group (incidence, 1.5 vs. 2.1 events per 100 person-years; hazard ratio, 0.72; 95% CI, 0.57 to 0.92; P = 0.007). The incidence rates of spontaneous myocardial infarction or ischemia-driven coronary revascularization (composite end point), cardiovascular death or spontaneous myocardial infarction (composite end point), ischemia-driven coronary revascularization, and spontaneous myocardial infarction were also significantly lower with colchicine than with placebo. The incidence of death from noncardiovascular causes was higher in the colchicine group than in the placebo group (incidence, 0.7 vs. 0.5 events per 100 person-years; hazard ratio, 1.51; 95% CI, 0.99 to 2.31). CONCLUSIONS: In a randomized trial involving patients with chronic coronary disease, the risk of cardiovascular events was significantly lower among those who received 0.5 mg of colchicine once daily than among those who received placebo. (Funded by the National Health Medical Research Council of Australia and others; LoDoCo2 Australian New Zealand Clinical Trials Registry number, ACTRN12614000093684.).
```

<a id="ev04-own-title"></a>
### EV04-OWN-TITLE

Source: `cache/colchicine-secondary-cv-prevention/records.json#/records/71/title`. Rank: `PRIMARY_REPORT`. Record: `32865380`. INFERRED attribution; exact location verified.

Character offset: 170714; byte offset: 171411. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`. Decoded SHA-256: `3dc22aef2eaed207527667ad52bbe447077f73909714143b965d01758a62471d`.

```text
Colchicine in Patients with Chronic Coronary Disease.
```

<a id="ev05-own-abstract"></a>
### EV05-OWN-ABSTRACT

Source: `cache/corticosteroids-covid19-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `32678530`. INFERRED attribution; exact location verified.

Character offset: 603; byte offset: 603. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `4653eaca3791dc225f769924e30956b4eb834d354b9afb1629bd0c1807877470`. Decoded SHA-256: `4653eaca3791dc225f769924e30956b4eb834d354b9afb1629bd0c1807877470`.

```text
BACKGROUND: Coronavirus disease 2019 (Covid-19) is associated with diffuse lung damage. Glucocorticoids may modulate inflammation-mediated lung injury and thereby reduce progression to respiratory failure and death. METHODS: In this controlled, open-label trial comparing a range of possible treatments in patients who were hospitalized with Covid-19, we randomly assigned patients to receive oral or intravenous dexamethasone (at a dose of 6 mg once daily) for up to 10 days or to receive usual care alone. The primary outcome was 28-day mortality. Here, we report the final results of this assessment. RESULTS: A total of 2104 patients were assigned to receive dexamethasone and 4321 to receive usual care. Overall, 482 patients (22.9%) in the dexamethasone group and 1110 patients (25.7%) in the usual care group died within 28 days after randomization (age-adjusted rate ratio, 0.83; 95% confidence interval [CI], 0.75 to 0.93; P<0.001). The proportional and absolute between-group differences in mortality varied considerably according to the level of respiratory support that the patients were receiving at the time of randomization. In the dexamethasone group, the incidence of death was lower than that in the usual care group among patients receiving invasive mechanical ventilation (29.3% vs. 41.4%; rate ratio, 0.64; 95% CI, 0.51 to 0.81) and among those receiving oxygen without invasive mechanical ventilation (23.3% vs. 26.2%; rate ratio, 0.82; 95% CI, 0.72 to 0.94) but not among those who were receiving no respiratory support at randomization (17.8% vs. 14.0%; rate ratio, 1.19; 95% CI, 0.92 to 1.55). CONCLUSIONS: In patients hospitalized with Covid-19, the use of dexamethasone resulted in lower 28-day mortality among those who were receiving either invasive mechanical ventilation or oxygen alone at randomization but not among those receiving no respiratory support. (Funded by the Medical Research Council and National Institute for Health Research and others; RECOVERY ClinicalTrials.gov number, NCT04381936; ISRCTN number, 50189673.).
```

<a id="ev05-own-title"></a>
### EV05-OWN-TITLE

Source: `cache/corticosteroids-covid19-mortality/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `32678530`. INFERRED attribution; exact location verified.

Character offset: 528; byte offset: 528. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `4653eaca3791dc225f769924e30956b4eb834d354b9afb1629bd0c1807877470`. Decoded SHA-256: `4653eaca3791dc225f769924e30956b4eb834d354b9afb1629bd0c1807877470`.

```text
Dexamethasone in Hospitalized Patients with Covid-19.
```

<a id="ev06-own-abstract"></a>
### EV06-OWN-ABSTRACT

Source: `cache/denosumab-vertebral-fracture/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `19671655`. INFERRED attribution; exact location verified.

Character offset: 537; byte offset: 537. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`. Decoded SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`.

```text
BACKGROUND: Denosumab is a fully human monoclonal antibody to the receptor activator of nuclear factor-kappaB ligand (RANKL) that blocks its binding to RANK, inhibiting the development and activity of osteoclasts, decreasing bone resorption, and increasing bone density. Given its unique actions, denosumab may be useful in the treatment of osteoporosis. METHODS: We enrolled 7868 women between the ages of 60 and 90 years who had a bone mineral density T score of less than -2.5 but not less than -4.0 at the lumbar spine or total hip. Subjects were randomly assigned to receive either 60 mg of denosumab or placebo subcutaneously every 6 months for 36 months. The primary end point was new vertebral fracture. Secondary end points included nonvertebral and hip fractures. RESULTS: As compared with placebo, denosumab reduced the risk of new radiographic vertebral fracture, with a cumulative incidence of 2.3% in the denosumab group, versus 7.2% in the placebo group (risk ratio, 0.32; 95% confidence interval [CI], 0.26 to 0.41; P<0.001)--a relative decrease of 68%. Denosumab reduced the risk of hip fracture, with a cumulative incidence of 0.7% in the denosumab group, versus 1.2% in the placebo group (hazard ratio, 0.60; 95% CI, 0.37 to 0.97; P=0.04)--a relative decrease of 40%. Denosumab also reduced the risk of nonvertebral fracture, with a cumulative incidence of 6.5% in the denosumab group, versus 8.0% in the placebo group (hazard ratio, 0.80; 95% CI, 0.67 to 0.95; P=0.01)--a relative decrease of 20%. There was no increase in the risk of cancer, infection, cardiovascular disease, delayed fracture healing, or hypocalcemia, and there were no cases of osteonecrosis of the jaw and no adverse reactions to the injection of denosumab. CONCLUSIONS: Denosumab given subcutaneously twice yearly for 36 months was associated with a reduction in the risk of vertebral, nonvertebral, and hip fractures in women with osteoporosis. (ClinicalTrials.gov number, NCT00089791.)
```

<a id="ev06-own-title"></a>
### EV06-OWN-TITLE

Source: `cache/denosumab-vertebral-fracture/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `19671655`. INFERRED attribution; exact location verified.

Character offset: 435; byte offset: 435. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`. Decoded SHA-256: `585357e1a0d1f4e4422cbe4cbe6d643e22cfb433e217b4756214f0f76829f619`.

```text
Denosumab for prevention of fractures in postmenopausal women with osteoporosis.
```

<a id="ev07-own-abstract"></a>
### EV07-OWN-ABSTRACT

Source: `cache/doac-vte-recurrence/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `24344086`. INFERRED attribution; exact location verified.

Character offset: 506; byte offset: 506. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
BACKGROUND: Dabigatran and warfarin have been compared for the treatment of acute venous thromboembolism (VTE) in a previous trial. We undertook this study to extend those findings. METHODS AND RESULTS: In a randomized, double-blind, double-dummy trial of 2589 patients with acute VTE treated with low-molecular-weight or unfractionated heparin for 5 to 11 days, we compared dabigatran 150 mg twice daily with warfarin. The primary outcome, recurrent symptomatic, objectively confirmed VTE and related deaths during 6 months of treatment occurred in 30 of the 1279 dabigatran patients (2.3%) compared with 28 of the 1289 warfarin patients (2.2%; hazard ratio, 1.08; 95% confidence interval [CI], 0.64-1.80; absolute risk difference, 0.2%; 95% CI, -1.0 to 1.3; P<0.001 for the prespecified noninferiority margin for both criteria). The safety end point, major bleeding, occurred in 15 patients receiving dabigatran (1.2%) and in 22 receiving warfarin (1.7%; hazard ratio, 0.69; 95% CI, 0.36-1.32). Any bleeding occurred in 200 dabigatran (15.6%) and 285 warfarin (22.1%; hazard ratio, 0.67; 95% CI, 0.56-0.81) patients. Deaths, adverse events, and acute coronary syndromes were similar in both groups. Pooled analysis of this study RE-COVER II and the RE-COVER trial gave hazard ratios for recurrent VTE of 1.09 (95% CI, 0.76-1.57), for major bleeding of 0.73 (95% CI, 0.48-1.11), and for any bleeding of 0.70 (95% CI, 0.61-0.79). CONCLUSION: Dabigatran has similar effects on VTE recurrence and a lower risk of bleeding compared with warfarin for the treatment of acute VTE. CLINICAL TRIAL REGISTRATION URL: www.clinicaltrials.gov. Unique identifiers: NCT00680186 and NCT00291330.
```

<a id="ev07-own-title"></a>
### EV07-OWN-TITLE

Source: `cache/doac-vte-recurrence/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `24344086`. INFERRED attribution; exact location verified.

Character offset: 394; byte offset: 394. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
Treatment of acute venous thromboembolism with dabigatran or warfarin and pooled analysis.
```

<a id="ev08-own-abstract"></a>
### EV08-OWN-ABSTRACT

Source: `cache/doac-vte-recurrence/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `19966341`. INFERRED attribution; exact location verified.

Character offset: 2685; byte offset: 2685. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
BACKGROUND: The direct oral thrombin inhibitor dabigatran has a predictable anticoagulant effect and may be an alternative therapy to warfarin for patients who have acute venous thromboembolism. METHODS: In a randomized, double-blind, noninferiority trial involving patients with acute venous thromboembolism who were initially given parenteral anticoagulation therapy for a median of 9 days (interquartile range, 8 to 11), we compared oral dabigatran, administered at a dose of 150 mg twice daily, with warfarin that was dose-adjusted to achieve an international normalized ratio of 2.0 to 3.0. The primary outcome was the 6-month incidence of recurrent symptomatic, objectively confirmed venous thromboembolism and related deaths. Safety end points included bleeding events, acute coronary syndromes, other adverse events, and results of liver-function tests. RESULTS: A total of 30 of the 1274 patients randomly assigned to receive dabigatran (2.4%), as compared with 27 of the 1265 patients randomly assigned to warfarin (2.1%), had recurrent venous thromboembolism; the difference in risk was 0.4 percentage points (95% confidence interval [CI], -0.8 to 1.5; P<0.001 for the prespecified noninferiority margin). The hazard ratio with dabigatran was 1.10 (95% CI, 0.65 to 1.84). Major bleeding episodes occurred in 20 patients assigned to dabigatran (1.6%) and in 24 patients assigned to warfarin (1.9%) (hazard ratio with dabigatran, 0.82; 95% CI, 0.45 to 1.48), and episodes of any bleeding were observed in 205 patients assigned to dabigatran (16.1%) and 277 patients assigned to warfarin (21.9%; hazard ratio with dabigatran, 0.71; 95% CI, 0.59 to 0.85). The numbers of deaths, acute coronary syndromes, and abnormal liver-function tests were similar in the two groups. Adverse events leading to discontinuation of the study drug occurred in 9.0% of patients assigned to dabigatran and in 6.8% of patients assigned to warfarin (P=0.05). CONCLUSIONS: For the treatment of acute venous thromboembolism, a fixed dose of dabigatran is as effective as warfarin, has a safety profile that is similar to that of warfarin, and does not require laboratory monitoring. (ClinicalTrials.gov number, NCT00291330.)
```

<a id="ev08-own-title"></a>
### EV08-OWN-TITLE

Source: `cache/doac-vte-recurrence/records.json#/records/1/title`. Rank: `PRIMARY_REPORT`. Record: `19966341`. INFERRED attribution; exact location verified.

Character offset: 2587; byte offset: 2587. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
Dabigatran versus warfarin in the treatment of acute venous thromboembolism.
```

<a id="ev09-own-abstract"></a>
### EV09-OWN-ABSTRACT

Source: `cache/doac-vte-recurrence/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `22449293`. INFERRED attribution; exact location verified.

Character offset: 5381; byte offset: 5381. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
BACKGROUND: A fixed-dose regimen of rivaroxaban, an oral factor Xa inhibitor, has been shown to be as effective as standard anticoagulant therapy for the treatment of deep-vein thrombosis, without the need for laboratory monitoring. This approach may also simplify the treatment of pulmonary embolism. METHODS: In a randomized, open-label, event-driven, noninferiority trial involving 4832 patients who had acute symptomatic pulmonary embolism with or without deep-vein thrombosis, we compared rivaroxaban (15 mg twice daily for 3 weeks, followed by 20 mg once daily) with standard therapy with enoxaparin followed by an adjusted-dose vitamin K antagonist for 3, 6, or 12 months. The primary efficacy outcome was symptomatic recurrent venous thromboembolism. The principal safety outcome was major or clinically relevant nonmajor bleeding. RESULTS: Rivaroxaban was noninferior to standard therapy (noninferiority margin, 2.0; P=0.003) for the primary efficacy outcome, with 50 events in the rivaroxaban group (2.1%) versus 44 events in the standard-therapy group (1.8%) (hazard ratio, 1.12; 95% confidence interval [CI], 0.75 to 1.68). The principal safety outcome occurred in 10.3% of patients in the rivaroxaban group and 11.4% of those in the standard-therapy group (hazard ratio, 0.90; 95% CI, 0.76 to 1.07; P=0.23). Major bleeding was observed in 26 patients (1.1%) in the rivaroxaban group and 52 patients (2.2%) in the standard-therapy group (hazard ratio, 0.49; 95% CI, 0.31 to 0.79; P=0.003). Rates of other adverse events were similar in the two groups. CONCLUSIONS: A fixed-dose regimen of rivaroxaban alone was noninferior to standard therapy for the initial and long-term treatment of pulmonary embolism and had a potentially improved benefit-risk profile. (Funded by Bayer HealthCare and Janssen Pharmaceuticals; EINSTEIN-PE ClinicalTrials.gov number, NCT00439777.).
```

<a id="ev09-own-title"></a>
### EV09-OWN-TITLE

Source: `cache/doac-vte-recurrence/records.json#/records/2/title`. Rank: `PRIMARY_REPORT`. Record: `22449293`. INFERRED attribution; exact location verified.

Character offset: 5290; byte offset: 5290. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
Oral rivaroxaban for the treatment of symptomatic pulmonary embolism.
```

<a id="ev10-own-abstract"></a>
### EV10-OWN-ABSTRACT

Source: `cache/doac-vte-recurrence/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `21128814`. INFERRED attribution; exact location verified.

Character offset: 7736; byte offset: 7736. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
BACKGROUND: Rivaroxaban, an oral factor Xa inhibitor, may provide a simple, fixed-dose regimen for treating acute deep-vein thrombosis (DVT) and for continued treatment, without the need for laboratory monitoring. METHODS: We conducted an open-label, randomized, event-driven, noninferiority study that compared oral rivaroxaban alone (15 mg twice daily for 3 weeks, followed by 20 mg once daily) with subcutaneous enoxaparin followed by a vitamin K antagonist (either warfarin or acenocoumarol) for 3, 6, or 12 months in patients with acute, symptomatic DVT. In parallel, we carried out a double-blind, randomized, event-driven superiority study that compared rivaroxaban alone (20 mg once daily) with placebo for an additional 6 or 12 months in patients who had completed 6 to 12 months of treatment for venous thromboembolism. The primary efficacy outcome for both studies was recurrent venous thromboembolism. The principal safety outcome was major bleeding or clinically relevant nonmajor bleeding in the initial-treatment study and major bleeding in the continued-treatment study. RESULTS: The study of rivaroxaban for acute DVT included 3449 patients: 1731 given rivaroxaban and 1718 given enoxaparin plus a vitamin K antagonist. Rivaroxaban had noninferior efficacy with respect to the primary outcome (36 events [2.1%], vs. 51 events with enoxaparin-vitamin K antagonist [3.0%]; hazard ratio, 0.68; 95% confidence interval [CI], 0.44 to 1.04; P<0.001). The principal safety outcome occurred in 8.1% of the patients in each group. In the continued-treatment study, which included 602 patients in the rivaroxaban group and 594 in the placebo group, rivaroxaban had superior efficacy (8 events [1.3%], vs. 42 with placebo [7.1%]; hazard ratio, 0.18; 95% CI, 0.09 to 0.39; P<0.001). Four patients in the rivaroxaban group had nonfatal major bleeding (0.7%), versus none in the placebo group (P=0.11). CONCLUSIONS: Rivaroxaban offers a simple, single-drug approach to the short-term and continued treatment of venous thrombosis that may improve the benefit-to-risk profile of anticoagulation. (Funded by Bayer Schering Pharma and Ortho-McNeil; ClinicalTrials.gov numbers, NCT00440193 and NCT00439725.).
```

<a id="ev10-own-title"></a>
### EV10-OWN-TITLE

Source: `cache/doac-vte-recurrence/records.json#/records/3/title`. Rank: `PRIMARY_REPORT`. Record: `21128814`. INFERRED attribution; exact location verified.

Character offset: 7658; byte offset: 7658. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
Oral rivaroxaban for symptomatic venous thromboembolism.
```

<a id="ev11-own-abstract"></a>
### EV11-OWN-ABSTRACT

Source: `cache/doac-vte-recurrence/records.json#/records/4/abstract`. Rank: `PRIMARY_REPORT`. Record: `23991658`. INFERRED attribution; exact location verified.

Character offset: 10442; byte offset: 10442. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
BACKGROUND: Whether the oral factor Xa inhibitor edoxaban can be an alternative to warfarin in patients with venous thromboembolism is unclear. METHODS: In a randomized, double-blind, noninferiority study, we randomly assigned patients with acute venous thromboembolism, who had initially received heparin, to receive edoxaban at a dose of 60 mg once daily, or 30 mg once daily (e.g., in the case of patients with creatinine clearance of 30 to 50 ml per minute or a body weight below 60 kg), or to receive warfarin. Patients received the study drug for 3 to 12 months. The primary efficacy outcome was recurrent symptomatic venous thromboembolism. The principal safety outcome was major or clinically relevant nonmajor bleeding. RESULTS: A total of 4921 patients presented with deep-vein thrombosis, and 3319 with a pulmonary embolism. Among patients receiving warfarin, the time in the therapeutic range was 63.5%. Edoxaban was noninferior to warfarin with respect to the primary efficacy outcome, which occurred in 130 patients in the edoxaban group (3.2%) and 146 patients in the warfarin group (3.5%) (hazard ratio, 0.89; 95% confidence interval [CI], 0.70 to 1.13; P<0.001 for noninferiority). The safety outcome occurred in 349 patients (8.5%) in the edoxaban group and 423 patients (10.3%) in the warfarin group (hazard ratio, 0.81; 95% CI, 0.71 to 0.94; P=0.004 for superiority). The rates of other adverse events were similar in the two groups. A total of 938 patients with pulmonary embolism had right ventricular dysfunction, as assessed by measurement of N-terminal pro-brain natriuretic peptide levels; the rate of recurrent venous thromboembolism in this subgroup was 3.3% in the edoxaban group and 6.2% in the warfarin group (hazard ratio, 0.52; 95% CI, 0.28 to 0.98). CONCLUSIONS: Edoxaban administered once daily after initial treatment with heparin was noninferior to high-quality standard therapy and caused significantly less bleeding in a broad spectrum of patients with venous thromboembolism, including those with severe pulmonary embolism. (Funded by Daiichi-Sankyo; Hokusai-VTE ClinicalTrials.gov number, NCT00986154.).
```

<a id="ev11-own-title"></a>
### EV11-OWN-TITLE

Source: `cache/doac-vte-recurrence/records.json#/records/4/title`. Rank: `PRIMARY_REPORT`. Record: `23991658`. INFERRED attribution; exact location verified.

Character offset: 10339; byte offset: 10339. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
Edoxaban versus warfarin for the treatment of symptomatic venous thromboembolism.
```

<a id="ev12-own-abstract"></a>
### EV12-OWN-ABSTRACT

Source: `cache/doac-vte-recurrence/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `23808982`. INFERRED attribution; exact location verified.

Character offset: 13069; byte offset: 13069. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
BACKGROUND: Apixaban, an oral factor Xa inhibitor administered in fixed doses, may simplify the treatment of venous thromboembolism. METHODS: In this randomized, double-blind study, we compared apixaban (at a dose of 10 mg twice daily for 7 days, followed by 5 mg twice daily for 6 months) with conventional therapy (subcutaneous enoxaparin, followed by warfarin) in 5395 patients with acute venous thromboembolism. The primary efficacy outcome was recurrent symptomatic venous thromboembolism or death related to venous thromboembolism. The principal safety outcomes were major bleeding alone and major bleeding plus clinically relevant nonmajor bleeding. RESULTS: The primary efficacy outcome occurred in 59 of 2609 patients (2.3%) in the apixaban group, as compared with 71 of 2635 (2.7%) in the conventional-therapy group (relative risk, 0.84; 95% confidence interval [CI], 0.60 to 1.18; difference in risk [apixaban minus conventional therapy], -0.4 percentage points; 95% CI, -1.3 to 0.4). Apixaban was noninferior to conventional therapy (P<0.001) for predefined upper limits of the 95% confidence intervals for both relative risk (<1.80) and difference in risk (<3.5 percentage points). Major bleeding occurred in 0.6% of patients who received apixaban and in 1.8% of those who received conventional therapy (relative risk, 0.31; 95% CI, 0.17 to 0.55; P<0.001 for superiority). The composite outcome of major bleeding and clinically relevant nonmajor bleeding occurred in 4.3% of the patients in the apixaban group, as compared with 9.7% of those in the conventional-therapy group (relative risk, 0.44; 95% CI, 0.36 to 0.55; P<0.001). Rates of other adverse events were similar in the two groups. CONCLUSIONS: A fixed-dose regimen of apixaban alone was noninferior to conventional therapy for the treatment of acute venous thromboembolism and was associated with significantly less bleeding (Funded by Pfizer and Bristol-Myers Squibb; ClinicalTrials.gov number, NCT00643201).
```

<a id="ev12-own-title"></a>
### EV12-OWN-TITLE

Source: `cache/doac-vte-recurrence/records.json#/records/5/title`. Rank: `PRIMARY_REPORT`. Record: `23808982`. INFERRED attribution; exact location verified.

Character offset: 12983; byte offset: 12983. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`. Decoded SHA-256: `5a8887072f40d8841e56e7eb4edfe328c06e7b4a2a6ded5c4eeb16b32afb8b52`.

```text
Oral apixaban for the treatment of acute venous thromboembolism.
```

<a id="ev13-own-abstract"></a>
### EV13-OWN-ABSTRACT

Source: `cache/dpp4-mace-t2d/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `30418475`. INFERRED attribution; exact location verified.

Character offset: 5593; byte offset: 5593. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
IMPORTANCE: Type 2 diabetes is associated with increased cardiovascular (CV) risk. Prior trials have demonstrated CV safety of 3 dipeptidyl peptidase 4 (DPP-4) inhibitors but have included limited numbers of patients with high CV risk and chronic kidney disease. OBJECTIVE: To evaluate the effect of linagliptin, a selective DPP-4 inhibitor, on CV outcomes and kidney outcomes in patients with type 2 diabetes at high risk of CV and kidney events. DESIGN, SETTING, AND PARTICIPANTS: Randomized, placebo-controlled, multicenter noninferiority trial conducted from August 2013 to August 2016 at 605 clinic sites in 27 countries among adults with type 2 diabetes, hemoglobin A1c of 6.5% to 10.0%, high CV risk (history of vascular disease and urine-albumin creatinine ratio [UACR] >200 mg/g), and high renal risk (reduced eGFR and micro- or macroalbuminuria). Participants with end-stage renal disease (ESRD) were excluded. Final follow-up occurred on January 18, 2018. INTERVENTIONS: Patients were randomized to receive linagliptin, 5 mg once daily (n = 3494), or placebo once daily (n = 3485) added to usual care. Other glucose-lowering medications or insulin could be added based on clinical need and local clinical guidelines. MAIN OUTCOMES AND MEASURES: Primary outcome was time to first occurrence of the composite of CV death, nonfatal myocardial infarction, or nonfatal stroke. Criteria for noninferiority of linagliptin vs placebo was defined by the upper limit of the 2-sided 95% CI for the hazard ratio (HR) of linagliptin relative to placebo being less than 1.3. Secondary outcome was time to first occurrence of adjudicated death due to renal failure, ESRD, or sustained 40% or higher decrease in eGFR from baseline. RESULTS: Of 6991 enrollees, 6979 (mean age, 65.9 years; eGFR, 54.6 mL/min/1.73 m2; 80.1% with UACR >30 mg/g) received at least 1 dose of study medication and 98.7% completed the study. During a median follow-up of 2.2 years, the primary outcome occurred in 434 of 3494 (12.4%) and 420 of 3485 (12.1%) in the linagliptin and placebo groups, respectively, (absolute incidence rate difference, 0.13 [95% CI, -0.63 to 0.90] per 100 person-years) (HR, 1.02; 95% CI, 0.89-1.17; P < .001 for noninferiority). The kidney outcome occurred in 327 of 3494 (9.4%) and 306 of 3485 (8.8%), respectively (absolute incidence rate difference, 0.22 [95% CI, -0.52 to 0.97] per 100 person-years) (HR, 1.04; 95% CI, 0.89-1.22; P = .62). Adverse events occurred in 2697 (77.2%) and 2723 (78.1%) patients in the linagliptin and placebo groups; 1036 (29.7%) and 1024 (29.4%) had 1 or more episodes of hypoglycemia; and there were 9 (0.3%) vs 5 (0.1%) events of adjudication-confirmed acute pancreatitis. CONCLUSIONS AND RELEVANCE: Among adults with type 2 diabetes and high CV and renal risk, linagliptin added to usual care compared with placebo added to usual care resulted in a noninferior risk of a composite CV outcome over a median 2.2 years. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT01897532.
```

<a id="ev13-own-title"></a>
### EV13-OWN-TITLE

Source: `cache/dpp4-mace-t2d/records.json#/records/2/title`. Rank: `PRIMARY_REPORT`. Record: `30418475`. INFERRED attribution; exact location verified.

Character offset: 5399; byte offset: 5399. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
Effect of Linagliptin vs Placebo on Major Cardiovascular Events in Adults With Type 2 Diabetes and High Cardiovascular and Renal Risk: The CARMELINA Randomized Clinical Trial.
```

<a id="ev14-own-abstract"></a>
### EV14-OWN-ABSTRACT

Source: `cache/dpp4-mace-t2d/records.json#/records/7/abstract`. Rank: `PRIMARY_REPORT`. Record: `28893244`. INFERRED attribution; exact location verified.

Character offset: 21587; byte offset: 21622. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
Omarigliptin is a once-weekly (q.w.) oral DPP-4 inhibitor that is approved for the treatment of patients with type 2 diabetes mellitus (T2DM) in Japan. To support approval of omarigliptin in the United States, the clinical development program included a cardiovascular (CV) safety study. In this randomized, double-blind study, 4202 patients with T2DM and established CV disease were assigned to either omarigliptin 25 mg q.w. or matching placebo in addition to their existing diabetes therapy. A Cox proportional hazards model was used to summarize the primary endpoint of time to first major adverse CV event (MACE, the composite of CV death, nonfatal myocardial infarction, and nonfatal stroke). The median follow-up was approximately 96 weeks. The primary MACE outcome occurred in 114/2092 patients in the omarigliptin group (5.45%) and 114/2100 patients in the placebo group (5.43%), with a hazard ratio (HR) of 1.00 (95% confidence interval [CI] 0.77, 1.29). In this CV safety study of patients with T2DM and established CV disease, omarigliptin did not increase the risk of MACE. Trial registration ClinicalTrials.gov: NCT01703208.
```

<a id="ev14-own-title"></a>
### EV14-OWN-TITLE

Source: `cache/dpp4-mace-t2d/records.json#/records/7/title`. Rank: `PRIMARY_REPORT`. Record: `28893244`. INFERRED attribution; exact location verified.

Character offset: 21410; byte offset: 21445. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`. Decoded SHA-256: `0aa7fcfaafc8b7b22eff8d8727ab53a8027dda217628d723306adf161b9723ab`.

```text
A randomized, placebo-controlled study of the cardiovascular safety of the once-weekly DPP-4 inhibitor omarigliptin in patients with type 2 diabetes mellitus.
```

<a id="ev15-own-abstract"></a>
### EV15-OWN-ABSTRACT

Source: `cache/esketamine-trd-madrs/records.json#/records/4/abstract`. Rank: `PRIMARY_REPORT`. Record: `37025256`. INFERRED attribution; exact location verified.

Character offset: 10338; byte offset: 10405. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`. Decoded SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`.

```text
PURPOSE: This Phase 3, multicenter study (NCT03434041) was conducted in primarily Chinese patients with treatment-resistant depression (TRD) to support the registration of esketamine nasal spray in China. PATIENTS AND METHODS: This randomized, double-blind, active-controlled study was conducted in China and the United States (US) in patients with TRD (single or recurrent episode). Eligible patients were randomized 1:1 to receive intranasal esketamine or matching placebo, each in conjunction with a newly initiated oral antidepressant (AD; duloxetine, escitalopram, sertraline, and venlafaxine extended release) (ie, esketamine plus AD or AD plus placebo). The primary endpoint, change from baseline in Montgomery-Åsberg Depression Rating Scale (MADRS) total score at Day 28, was analyzed using a mixed-effects model for repeated measures. Secondary endpoints including safety were also evaluated. RESULTS: Of 252 randomized patients (China, 224; US, 28), 214 completed the double-blind treatment phase. The difference between treatment groups at Day 28 was not statistically significant (difference in least-square means [95% CI]: -2.0 [-4.64, 0.55]; 2-sided p = 0.123). However, esketamine plus AD demonstrated a clinically meaningful treatment difference compared with AD plus placebo in MADRS total score at 24 hours after first dose for the study overall population and China sub-population (difference in least-square mean [95% CI]: -3.3 [-5.33, -1.33] and -2.6 [-4.64, -0.60], respectively). No new safety signals were observed. CONCLUSION: Esketamine plus AD was not statistically superior to AD plus placebo in improving depressive symptoms in TRD patients at Day 28. Rapid reduction in depressive symptoms within 24 hours was observed for TRD patients treated with esketamine plus AD in the overall population and China sub-population. Safety was consistent with the established safety profile of esketamine.
```

<a id="ev15-own-title"></a>
### EV15-OWN-TITLE

Source: `cache/esketamine-trd-madrs/records.json#/records/4/title`. Rank: `PRIMARY_REPORT`. Record: `37025256`. INFERRED attribution; exact location verified.

Character offset: 10065; byte offset: 10132. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`. Decoded SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`.

```text
Efficacy and Safety of Flexibly Dosed Esketamine Nasal Spray Plus a Newly Initiated Oral Antidepressant in Adult Patients with Treatment-Resistant Depression: A Randomized, Double-Blind, Multicenter, Active-Controlled Study Conducted in China and USA.
```

<a id="ev16-own-title"></a>
### EV16-OWN-TITLE

Source: `cache/esketamine-trd-madrs/records.json#/ctgov/2/title`. Rank: `REGISTRY`. Record: `NCT02422186`. INFERRED attribution; exact location verified.

Character offset: 279196; byte offset: 280506. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`. Decoded SHA-256: `fcee0007db60a5ed4de902437861ebe8b7340481d274eb703aef4eb8c9f806a4`.

```text
A Study to Evaluate the Efficacy, Safety, and Tolerability of Intranasal Esketamine Plus an Oral Antidepressant in Elderly Participants With Treatment-resistant Depression
```

<a id="ev17-own-abstract"></a>
### EV17-OWN-ABSTRACT

Source: `cache/glp1-ra-mace-t2d/records.json#/records/5/abstract`. Rank: `PRIMARY_REPORT`. Record: `30291013`. INFERRED attribution; exact location verified.

Character offset: 15322; byte offset: 15357. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`. Decoded SHA-256: `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`.

```text
BACKGROUND: Glucagon-like peptide 1 receptor agonists differ in chemical structure, duration of action, and in their effects on clinical outcomes. The cardiovascular effects of once-weekly albiglutide in type 2 diabetes are unknown. We aimed to determine the safety and efficacy of albiglutide in preventing cardiovascular death, myocardial infarction, or stroke. METHODS: We did a double-blind, randomised, placebo-controlled trial in 610 sites across 28 countries. We randomly assigned patients aged 40 years and older with type 2 diabetes and cardiovascular disease (at a 1:1 ratio) to groups that either received a subcutaneous injection of albiglutide (30-50 mg, based on glycaemic response and tolerability) or of a matched volume of placebo once a week, in addition to their standard care. Investigators used an interactive voice or web response system to obtain treatment assignment, and patients and all study investigators were masked to their treatment allocation. We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population. If non-inferiority was confirmed by an upper limit of the 95% CI for a hazard ratio of less than 1·30, closed testing for superiority was prespecified. This study is registered with ClinicalTrials.gov, number NCT02465515. FINDINGS: Patients were screened between July 1, 2015, and Nov 24, 2016. 10 793 patients were screened and 9463 participants were enrolled and randomly assigned to groups: 4731 patients were assigned to receive albiglutide and 4732 patients to receive placebo. On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome. The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4·6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5·9 events per 100 person-years in the placebo group (hazard ratio 0·78, 95% CI 0·68-0·90), which indicated that albiglutide was superior to placebo (p<0·0001 for non-inferiority; p=0·0006 for superiority). The incidence of acute pancreatitis (ten patients in the albiglutide group and seven patients in the placebo group), pancreatic cancer (six patients in the albiglutide group and five patients in the placebo group), medullary thyroid carcinoma (zero patients in both groups), and other serious adverse events did not differ between the two groups. There were three (<1%) deaths in the placebo group that were assessed by investigators, who were masked to study drug assignment, to be treatment-related and two (<1%) deaths in the albiglutide group. INTERPRETATION: In patients with type 2 diabetes and cardiovascular disease, albiglutide was superior to placebo with respect to major adverse cardiovascular events. Evidence-based glucagon-like peptide 1 receptor agonists should therefore be considered as part of a comprehensive strategy to reduce the risk of cardiovascular events in patients with type 2 diabetes. FUNDING: GlaxoSmithKline.
```

<a id="ev17-own-title"></a>
### EV17-OWN-TITLE

Source: `cache/glp1-ra-mace-t2d/records.json#/records/5/title`. Rank: `PRIMARY_REPORT`. Record: `30291013`. INFERRED attribution; exact location verified.

Character offset: 15131; byte offset: 15166. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`. Decoded SHA-256: `1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750`.

```text
Albiglutide and cardiovascular outcomes in patients with type 2 diabetes and cardiovascular disease (Harmony Outcomes): a double-blind, randomised placebo-controlled trial.
```

<a id="ev18-own-abstract"></a>
### EV18-OWN-ABSTRACT

Source: `cache/iv-iron-hfref-hosp/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `40159390`. INFERRED attribution; exact location verified.

Character offset: 627; byte offset: 627. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6ec77b3291b771f5f49adc5f9215f87c7fb6a134c36fb9f26687c626429c75ee`. Decoded SHA-256: `6ec77b3291b771f5f49adc5f9215f87c7fb6a134c36fb9f26687c626429c75ee`.

```text
IMPORTANCE: Uncertainty remains about the efficacy of intravenous iron in patients with heart failure and iron deficiency. OBJECTIVE: To assess the efficacy and safety of ferric carboxymaltose in patients with heart failure and iron deficiency. DESIGN, SETTING, AND PARTICIPANTS: This multicenter, randomized clinical trial enrolled 1105 patients with heart failure (defined as having a left ventricular ejection fraction of ≤45%) and iron deficiency (serum ferritin level <100 ng/mL; or if transferrin saturation was <20%, a serum ferritin level between 100 ng/mL and 299 ng/mL) at 70 clinic sites in 6 European countries from March 2017 to November 2023. The median follow-up was 16.6 months (IQR, 7.9-29.9 months). INTERVENTION: Administration of ferric carboxymaltose (n = 558) initially given at an intravenous dose of up to 2000 mg that was followed by 500 mg every 4 months (unless stopping criteria were met) vs a saline placebo (n = 547). MAIN OUTCOMES AND MEASURES: The primary end point events were (1) time to cardiovascular death or first heart failure hospitalization, (2) total heart failure hospitalizations, and (3) time to cardiovascular death or first heart failure hospitalization in patients with a transferrin saturation less than 20%. All end point events were measured through follow-up. The end points would be considered statistically significant if they fulfilled at least 1 of the following conditions: (1) P ≤ .05 for all 3 of the end point comparisons, (2) P ≤ .025 for 2 of the end point comparisons, or (3) P ≤ .0167 for any of the 3 end point comparisons (Hochberg procedure). RESULTS: Of the 1105 participants (mean age, 70 years [SD, 12 years]; 33% were women), cardiovascular death or first heart failure hospitalization (first primary outcome) occurred in 141 in the ferric carboxymaltose group vs 166 in the placebo group (hazard ratio, 0.79 [95% CI, 0.63-0.99]; P = .04). The second primary outcome (total heart failure hospitalizations) occurred 264 times in the ferric carboxymaltose group vs 320 times in the placebo group (rate ratio, 0.80 [95% CI, 0.60-1.06]; P = .12). The third primary outcome (cardiovascular death or first heart failure hospitalization in patients with a transferrin saturation <20%) occurred in 103 patients in the ferric carboxymaltose group vs 128 patients in the placebo group (hazard ratio, 0.79 [95% CI, 0.61-1.02], P = .07). A similar amount of patients had at least 1 serious adverse event in the ferric carboxymaltose group (269; 48.2%) vs in the placebo group (273; 49.9%) (P = .61). CONCLUSIONS AND RELEVANCE: In patients with heart failure and iron deficiency, ferric carboxymaltose did not significantly reduce the time to first heart failure hospitalization or cardiovascular death in the overall cohort or in patients with a transferrin saturation less than 20%, or reduce the total number of heart failure hospitalizations vs placebo. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT03036462.
```

<a id="ev18-own-title"></a>
### EV18-OWN-TITLE

Source: `cache/iv-iron-hfref-hosp/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `40159390`. INFERRED attribution; exact location verified.

Character offset: 486; byte offset: 486. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6ec77b3291b771f5f49adc5f9215f87c7fb6a134c36fb9f26687c626429c75ee`. Decoded SHA-256: `6ec77b3291b771f5f49adc5f9215f87c7fb6a134c36fb9f26687c626429c75ee`.

```text
Intravenous Ferric Carboxymaltose in Heart Failure With Iron Deficiency: The FAIR-HF2 DZHK05 Randomized Clinical Trial.
```

<a id="ev19-own-abstract"></a>
### EV19-OWN-ABSTRACT

Source: `cache/metformin-pcos-ovulation/records.json#/records/28/abstract`. Rank: `PRIMARY_REPORT`. Record: `19522426`. INFERRED attribution; exact location verified.

Character offset: 85083; byte offset: 85202. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
BACKGROUND: Polycystic ovary syndrome (PCOS) is a common, complex endocrine disorder for women on reproductive age. A high incidence of ovulation failure is observed in PCO women and perhaps linked to insulin resistance related to metabolic features In the last few years some studies assessed hyperinsulinimea and insulin resistance attenuation effects, by insulin sensitizing agents such as metformin, in PCOS women suggesting potential scope for these drugs in CC ovulation induction quality improvement. AIM: Our prospective study aim is to compare the effectiveness of clomifene citrate plus metformin and clomifene citrate plus placebo in women with newly diagnosed polycystic ovary syndrome. METHODS: From February 24 to September 29 (2007), PCOS was explored on women attending the Department of Obstetrics & Gynaecology sterility consultation unit (CHU Hedi Chaker-Sfax) according to the Rotterdam 2003 diagnostic criteria. PCOS patients were randomized to receive, in addition to clomifene citrate treatment, placebo or metformin 850 mg two times a day all ovulatory cycle for three trials maximum. Ovulation detection was done by the E2 serum measurements and ovarian transvaginal ultrasonography' evolution controlling on 7th, 11th and 13th day of the cycle. RESULTS: Within 7 months, 32 PCOS women were recruited in the study and equally allocated to the two groups. Baseline characteristics were similar in metformin group and placebo one. Ovulation was characterized by the presence of at least one mature follicle (> 16 mm), a circulating estradiol concentration in the edge of 150-250 pg and accessory an endometrial depth > 8 mm. The ovulation rate in the metformin group was 62.5% compared with 37.5% in the placebo group, a non-statistically significant (small study population) but important difference (1.66 times). Analyses show a higher mature follicle number and estradiol concentration in metformin group than in the placebo one. Metformin effect was, in our study, his only insulinosensitizer property consequence far away a 'making thinner' or Hyperandrogenism reducing ones. CONCLUSION: The ovulatory response to clomifene can be increased in polycystic ovary syndrome women by decreasing insulin secretion with metformin.
```

<a id="ev19-own-title"></a>
### EV19-OWN-TITLE

Source: `cache/metformin-pcos-ovulation/records.json#/records/28/title`. Rank: `PRIMARY_REPORT`. Record: `19522426`. INFERRED attribution; exact location verified.

Character offset: 84979; byte offset: 85098. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
Metformin effects on clomifene-induced ovulation in the polycystic ovary syndrome.
```

<a id="ev20-own-abstract"></a>
### EV20-OWN-ABSTRACT

Source: `cache/metformin-pcos-ovulation/records.json#/records/39/abstract`. Rank: `PRIMARY_REPORT`. Record: `16769748`. INFERRED attribution; exact location verified.

Character offset: 110349; byte offset: 110468. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
OBJECTIVE: To compare the effectiveness of clomifene citrate plus metformin and clomifene citrate plus placebo in women with newly diagnosed polycystic ovary syndrome. DESIGN: Randomised clinical trial. SETTING: Multicentre trial in 20 Dutch hospitals. PARTICIPANTS: 228 women with polycystic ovary syndrome. INTERVENTIONS: Clomifene citrate plus metformin or clomifene citrate plus placebo. MAIN OUTCOME MEASURE: The primary outcome measure was ovulation. Secondary outcome measures were ongoing pregnancy, spontaneous abortion, and clomifene resistance. RESULTS: 111 women were allocated to clomifene citrate plus metformin (metformin group) and 114 women were allocated to clomifene citrate plus placebo (placebo group). The ovulation rate in the metformin group was 64% compared with 72% in the placebo group, a non-significant difference (risk difference - 8%, 95% confidence interval - 20% to 4%). There were no significant differences in either rate of ongoing pregnancy (40% v 46%; - 6%, - 20% to 7%) or rate of spontaneous abortion (12% v 11%; 1%, - 7% to 10%). A significantly larger proportion of women in the metformin group discontinued treatment because of side effects (16% v 5%; 11%, 5% to 16%). CONCLUSION: Metformin is not an effective addition to clomifene citrate as the primary method of inducing ovulation in women with polycystic ovary syndrome. TRIAL REGISTRATION: Current Controlled Trials ISRCTN55906981 [controlled-trials.com].
```

<a id="ev20-own-title"></a>
### EV20-OWN-TITLE

Source: `cache/metformin-pcos-ovulation/records.json#/records/39/title`. Rank: `PRIMARY_REPORT`. Record: `16769748`. INFERRED attribution; exact location verified.

Character offset: 110127; byte offset: 110246. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
Effect of clomifene citrate plus metformin and clomifene citrate plus placebo on induction of ovulation in women with newly diagnosed polycystic ovary syndrome: randomised double blind clinical trial.
```

<a id="ev21-own-abstract"></a>
### EV21-OWN-ABSTRACT

Source: `cache/metformin-pcos-ovulation/records.json#/records/101/abstract`. Rank: `PRIMARY_REPORT`. Record: `11172832`. INFERRED attribution; exact location verified.

Character offset: 296467; byte offset: 296846. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
OBJECTIVE: To determine whether metformin treatment increases the ovulation and pregnancy rates in response to clomiphene citrate (CC) in women who are resistant to CC alone. DESIGN: Randomized, double-blind, placebo-controlled trial. SETTING: Multicenter environment. PATIENT(S): Anovulatory women with the polycystic ovary syndrome (PCOS) who were resistant to CC. INTERVENTION(S): Participants received placebo or metformin, 500 mg three times daily, for 7 weeks. Information on reproductive steroids, gonadotropins, and oral glucose tolerance testing was obtained at baseline and after treatment. Metformin or placebo was continued and CC treatment was begun at 50 mg daily for 5 days. Serum P level > or =4 ng/mL was considered to indicate ovulation. With ovulation, the daily CC dose was not changed, but with anovulation it was increased by 50 mg for the next cycle. Patients completed the study when they had had six ovulatory cycles, became pregnant, or experienced anovulation while receiving 150 mg of CC. MAIN OUTCOME MEASURE(S): Ovulation and pregnancy rates. RESULT(S): In the metformin and placebo groups, 9 of 12 participants (75%) and 4 of 15 participants (27%) ovulated, and 6 of 11 participants (55%) and 1 of 14 participants (7%) conceived, respectively. Comparisons between the groups were significant. CONCLUSION(S): In anovulatory women with PCOS who are resistant to CC, metformin use significantly increased the ovulation rate and pregnancy rate from CC treatment.
```

<a id="ev21-own-title"></a>
### EV21-OWN-TITLE

Source: `cache/metformin-pcos-ovulation/records.json#/records/101/title`. Rank: `PRIMARY_REPORT`. Record: `11172832`. INFERRED attribution; exact location verified.

Character offset: 296274; byte offset: 296653. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
Metformin increases the ovulatory rate and pregnancy rate from clomiphene citrate in patients with polycystic ovary syndrome who are resistant to clomiphene citrate alone.
```

<a id="ev22-own-abstract"></a>
### EV22-OWN-ABSTRACT

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `21830957`. INFERRED attribution; exact location verified.

Character offset: 437; byte offset: 437. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
BACKGROUND: The use of warfarin reduces the rate of ischemic stroke in patients with atrial fibrillation but requires frequent monitoring and dose adjustment. Rivaroxaban, an oral factor Xa inhibitor, may provide more consistent and predictable anticoagulation than warfarin. METHODS: In a double-blind trial, we randomly assigned 14,264 patients with nonvalvular atrial fibrillation who were at increased risk for stroke to receive either rivaroxaban (at a daily dose of 20 mg) or dose-adjusted warfarin. The per-protocol, as-treated primary analysis was designed to determine whether rivaroxaban was noninferior to warfarin for the primary end point of stroke or systemic embolism. RESULTS: In the primary analysis, the primary end point occurred in 188 patients in the rivaroxaban group (1.7% per year) and in 241 in the warfarin group (2.2% per year) (hazard ratio in the rivaroxaban group, 0.79; 95% confidence interval [CI], 0.66 to 0.96; P<0.001 for noninferiority). In the intention-to-treat analysis, the primary end point occurred in 269 patients in the rivaroxaban group (2.1% per year) and in 306 patients in the warfarin group (2.4% per year) (hazard ratio, 0.88; 95% CI, 0.74 to 1.03; P<0.001 for noninferiority; P=0.12 for superiority). Major and nonmajor clinically relevant bleeding occurred in 1475 patients in the rivaroxaban group (14.9% per year) and in 1449 in the warfarin group (14.5% per year) (hazard ratio, 1.03; 95% CI, 0.96 to 1.11; P=0.44), with significant reductions in intracranial hemorrhage (0.5% vs. 0.7%, P=0.02) and fatal bleeding (0.2% vs. 0.5%, P=0.003) in the rivaroxaban group. CONCLUSIONS: In patients with atrial fibrillation, rivaroxaban was noninferior to warfarin for the prevention of stroke or systemic embolism. There was no significant between-group difference in the risk of major bleeding, although intracranial and fatal bleeding occurred less frequently in the rivaroxaban group. (Funded by Johnson & Johnson and Bayer; ROCKET AF ClinicalTrials.gov number, NCT00403767.).
```

<a id="ev22-own-title"></a>
### EV22-OWN-TITLE

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `21830957`. INFERRED attribution; exact location verified.

Character offset: 352; byte offset: 352. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
Rivaroxaban versus warfarin in nonvalvular atrial fibrillation.
```

<a id="ev23-own-abstract"></a>
### EV23-OWN-ABSTRACT

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `19717844`. INFERRED attribution; exact location verified.

Character offset: 2946; byte offset: 2946. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
BACKGROUND: Warfarin reduces the risk of stroke in patients with atrial fibrillation but increases the risk of hemorrhage and is difficult to use. Dabigatran is a new oral direct thrombin inhibitor. METHODS: In this noninferiority trial, we randomly assigned 18,113 patients who had atrial fibrillation and a risk of stroke to receive, in a blinded fashion, fixed doses of dabigatran--110 mg or 150 mg twice daily--or, in an unblinded fashion, adjusted-dose warfarin. The median duration of the follow-up period was 2.0 years. The primary outcome was stroke or systemic embolism. RESULTS: Rates of the primary outcome were 1.69% per year in the warfarin group, as compared with 1.53% per year in the group that received 110 mg of dabigatran (relative risk with dabigatran, 0.91; 95% confidence interval [CI], 0.74 to 1.11; P<0.001 for noninferiority) and 1.11% per year in the group that received 150 mg of dabigatran (relative risk, 0.66; 95% CI, 0.53 to 0.82; P<0.001 for superiority). The rate of major bleeding was 3.36% per year in the warfarin group, as compared with 2.71% per year in the group receiving 110 mg of dabigatran (P=0.003) and 3.11% per year in the group receiving 150 mg of dabigatran (P=0.31). The rate of hemorrhagic stroke was 0.38% per year in the warfarin group, as compared with 0.12% per year with 110 mg of dabigatran (P<0.001) and 0.10% per year with 150 mg of dabigatran (P<0.001). The mortality rate was 4.13% per year in the warfarin group, as compared with 3.75% per year with 110 mg of dabigatran (P=0.13) and 3.64% per year with 150 mg of dabigatran (P=0.051). CONCLUSIONS: In patients with atrial fibrillation, dabigatran given at a dose of 110 mg was associated with rates of stroke and systemic embolism that were similar to those associated with warfarin, as well as lower rates of major hemorrhage. Dabigatran administered at a dose of 150 mg, as compared with warfarin, was associated with lower rates of stroke and systemic embolism but similar rates of major hemorrhage. (ClinicalTrials.gov number, NCT00262600.)
```

<a id="ev23-own-title"></a>
### EV23-OWN-TITLE

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/1/title`. Rank: `PRIMARY_REPORT`. Record: `19717844`. INFERRED attribution; exact location verified.

Character offset: 2860; byte offset: 2860. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
Dabigatran versus warfarin in patients with atrial fibrillation.
```

<a id="ev24-own-abstract"></a>
### EV24-OWN-ABSTRACT

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `24251359`. INFERRED attribution; exact location verified.

Character offset: 5483; byte offset: 5483. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
BACKGROUND: Edoxaban is a direct oral factor Xa inhibitor with proven antithrombotic effects. The long-term efficacy and safety of edoxaban as compared with warfarin in patients with atrial fibrillation is not known. METHODS: We conducted a randomized, double-blind, double-dummy trial comparing two once-daily regimens of edoxaban with warfarin in 21,105 patients with moderate-to-high-risk atrial fibrillation (median follow-up, 2.8 years). The primary efficacy end point was stroke or systemic embolism. Each edoxaban regimen was tested for noninferiority to warfarin during the treatment period. The principal safety end point was major bleeding. RESULTS: The annualized rate of the primary end point during treatment was 1.50% with warfarin (median time in the therapeutic range, 68.4%), as compared with 1.18% with high-dose edoxaban (hazard ratio, 0.79; 97.5% confidence interval [CI], 0.63 to 0.99; P<0.001 for noninferiority) and 1.61% with low-dose edoxaban (hazard ratio, 1.07; 97.5% CI, 0.87 to 1.31; P=0.005 for noninferiority). In the intention-to-treat analysis, there was a trend favoring high-dose edoxaban versus warfarin (hazard ratio, 0.87; 97.5% CI, 0.73 to 1.04; P=0.08) and an unfavorable trend with low-dose edoxaban versus warfarin (hazard ratio, 1.13; 97.5% CI, 0.96 to 1.34; P=0.10). The annualized rate of major bleeding was 3.43% with warfarin versus 2.75% with high-dose edoxaban (hazard ratio, 0.80; 95% CI, 0.71 to 0.91; P<0.001) and 1.61% with low-dose edoxaban (hazard ratio, 0.47; 95% CI, 0.41 to 0.55; P<0.001). The corresponding annualized rates of death from cardiovascular causes were 3.17% versus 2.74% (hazard ratio, 0.86; 95% CI, 0.77 to 0.97; P=0.01), and 2.71% (hazard ratio, 0.85; 95% CI, 0.76 to 0.96; P=0.008), and the corresponding rates of the key secondary end point (a composite of stroke, systemic embolism, or death from cardiovascular causes) were 4.43% versus 3.85% (hazard ratio, 0.87; 95% CI, 0.78 to 0.96; P=0.005), and 4.23% (hazard ratio, 0.95; 95% CI, 0.86 to 1.05; P=0.32). CONCLUSIONS: Both once-daily regimens of edoxaban were noninferior to warfarin with respect to the prevention of stroke or systemic embolism and were associated with significantly lower rates of bleeding and death from cardiovascular causes. (Funded by Daiichi Sankyo Pharma Development; ENGAGE AF-TIMI 48 ClinicalTrials.gov number, NCT00781391.).
```

<a id="ev24-own-title"></a>
### EV24-OWN-TITLE

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/2/title`. Rank: `PRIMARY_REPORT`. Record: `24251359`. INFERRED attribution; exact location verified.

Character offset: 5399; byte offset: 5399. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
Edoxaban versus warfarin in patients with atrial fibrillation.
```

<a id="ev25-own-abstract"></a>
### EV25-OWN-ABSTRACT

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `21870978`. INFERRED attribution; exact location verified.

Character offset: 8347; byte offset: 8347. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
BACKGROUND: Vitamin K antagonists are highly effective in preventing stroke in patients with atrial fibrillation but have several limitations. Apixaban is a novel oral direct factor Xa inhibitor that has been shown to reduce the risk of stroke in a similar population in comparison with aspirin. METHODS: In this randomized, double-blind trial, we compared apixaban (at a dose of 5 mg twice daily) with warfarin (target international normalized ratio, 2.0 to 3.0) in 18,201 patients with atrial fibrillation and at least one additional risk factor for stroke. The primary outcome was ischemic or hemorrhagic stroke or systemic embolism. The trial was designed to test for noninferiority, with key secondary objectives of testing for superiority with respect to the primary outcome and to the rates of major bleeding and death from any cause. RESULTS: The median duration of follow-up was 1.8 years. The rate of the primary outcome was 1.27% per year in the apixaban group, as compared with 1.60% per year in the warfarin group (hazard ratio with apixaban, 0.79; 95% confidence interval [CI], 0.66 to 0.95; P<0.001 for noninferiority; P=0.01 for superiority). The rate of major bleeding was 2.13% per year in the apixaban group, as compared with 3.09% per year in the warfarin group (hazard ratio, 0.69; 95% CI, 0.60 to 0.80; P<0.001), and the rates of death from any cause were 3.52% and 3.94%, respectively (hazard ratio, 0.89; 95% CI, 0.80 to 0.99; P=0.047). The rate of hemorrhagic stroke was 0.24% per year in the apixaban group, as compared with 0.47% per year in the warfarin group (hazard ratio, 0.51; 95% CI, 0.35 to 0.75; P<0.001), and the rate of ischemic or uncertain type of stroke was 0.97% per year in the apixaban group and 1.05% per year in the warfarin group (hazard ratio, 0.92; 95% CI, 0.74 to 1.13; P=0.42). CONCLUSIONS: In patients with atrial fibrillation, apixaban was superior to warfarin in preventing stroke or systemic embolism, caused less bleeding, and resulted in lower mortality. (Funded by Bristol-Myers Squibb and Pfizer; ARISTOTLE ClinicalTrials.gov number, NCT00412984.).
```

<a id="ev25-own-title"></a>
### EV25-OWN-TITLE

Source: `cache/noac-vs-warfarin-af-stroke/records.json#/records/3/title`. Rank: `PRIMARY_REPORT`. Record: `21870978`. INFERRED attribution; exact location verified.

Character offset: 8263; byte offset: 8263. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`. Decoded SHA-256: `6e35e6e5379076d27ee29755b122b72892404ecce68b22cd0e60f0cd33ce0242`.

```text
Apixaban versus warfarin in patients with atrial fibrillation.
```

<a id="ev26-own-abstract"></a>
### EV26-OWN-ABSTRACT

Source: `cache/omega3-cardiovascular-events/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `33190147`. INFERRED attribution; exact location verified.

Character offset: 3405; byte offset: 3410. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
IMPORTANCE: It remains uncertain whether the omega-3 fatty acids eicosapentaenoic acid (EPA) and docosahexaenoic acid (DHA) reduce cardiovascular risk. OBJECTIVE: To determine the effects on cardiovascular outcomes of a carboxylic acid formulation of EPA and DHA (omega-3 CA) with documented favorable effects on lipid and inflammatory markers in patients with atherogenic dyslipidemia and high cardiovascular risk. DESIGN, SETTING, AND PARTICIPANTS: A double-blind, randomized, multicenter trial (enrollment October 30, 2014, to June 14, 2017; study termination January 8, 2020; last patient visit May 14, 2020) comparing omega-3 CA with corn oil in statin-treated participants with high cardiovascular risk, hypertriglyceridemia, and low levels of high-density lipoprotein cholesterol (HDL-C). A total of 13 078 patients were randomized at 675 academic and community hospitals in 22 countries in North America, Europe, South America, Asia, Australia, New Zealand, and South Africa. INTERVENTIONS: Participants were randomized to receive 4 g/d of omega-3 CA (n = 6539) or corn oil, which was intended to serve as an inert comparator (n = 6539), in addition to usual background therapies, including statins. MAIN OUTCOMES AND MEASURES: The primary efficacy measure was a composite of cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, coronary revascularization, or unstable angina requiring hospitalization. RESULTS: When 1384 patients had experienced a primary end point event (of a planned 1600 events), the trial was prematurely halted based on an interim analysis that indicated a low probability of clinical benefit of omega-3 CA vs the corn oil comparator. Among the 13 078 treated patients (mean [SD] age, 62.5 [9.0] years; 35% women; 70% with diabetes; median low-density lipoprotein [LDL] cholesterol level, 75.0 mg/dL; median triglycerides level, 240 mg/dL; median HDL-C level, 36 mg/dL; and median high-sensitivity C-reactive protein level, 2.1 mg/L), 12 633 (96.6%) completed the trial with ascertainment of primary end point status. The primary end point occurred in 785 patients (12.0%) treated with omega-3 CA vs 795 (12.2%) treated with corn oil (hazard ratio, 0.99 [95% CI, 0.90-1.09]; P = .84). A greater rate of gastrointestinal adverse events was observed in the omega-3 CA group (24.7%) compared with corn oil-treated patients (14.7%). CONCLUSIONS AND RELEVANCE: Among statin-treated patients at high cardiovascular risk, the addition of omega-3 CA, compared with corn oil, to usual background therapies resulted in no significant difference in a composite outcome of major adverse cardiovascular events. These findings do not support use of this omega-3 fatty acid formulation to reduce major adverse cardiovascular events in high-risk patients. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT02104817.
```

<a id="ev26-own-title"></a>
### EV26-OWN-TITLE

Source: `cache/omega3-cardiovascular-events/records.json#/records/1/title`. Rank: `PRIMARY_REPORT`. Record: `33190147`. INFERRED attribution; exact location verified.

Character offset: 3212; byte offset: 3217. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
Effect of High-Dose Omega-3 Fatty Acids vs Corn Oil on Major Adverse Cardiovascular Events in Patients at High Cardiovascular Risk: The STRENGTH Randomized Clinical Trial.
```

<a id="ev27-own-abstract"></a>
### EV27-OWN-ABSTRACT

Source: `cache/omega3-cardiovascular-events/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `30415628`. INFERRED attribution; exact location verified.

Character offset: 9741; byte offset: 9764. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
BACKGROUND: Patients with elevated triglyceride levels are at increased risk for ischemic events. Icosapent ethyl, a highly purified eicosapentaenoic acid ethyl ester, lowers triglyceride levels, but data are needed to determine its effects on ischemic events. METHODS: We performed a multicenter, randomized, double-blind, placebo-controlled trial involving patients with established cardiovascular disease or with diabetes and other risk factors, who had been receiving statin therapy and who had a fasting triglyceride level of 135 to 499 mg per deciliter (1.52 to 5.63 mmol per liter) and a low-density lipoprotein cholesterol level of 41 to 100 mg per deciliter (1.06 to 2.59 mmol per liter). The patients were randomly assigned to receive 2 g of icosapent ethyl twice daily (total daily dose, 4 g) or placebo. The primary end point was a composite of cardiovascular death, nonfatal myocardial infarction, nonfatal stroke, coronary revascularization, or unstable angina. The key secondary end point was a composite of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. RESULTS: A total of 8179 patients were enrolled (70.7% for secondary prevention of cardiovascular events) and were followed for a median of 4.9 years. A primary end-point event occurred in 17.2% of the patients in the icosapent ethyl group, as compared with 22.0% of the patients in the placebo group (hazard ratio, 0.75; 95% confidence interval [CI], 0.68 to 0.83; P<0.001); the corresponding rates of the key secondary end point were 11.2% and 14.8% (hazard ratio, 0.74; 95% CI, 0.65 to 0.83; P<0.001). The rates of additional ischemic end points, as assessed according to a prespecified hierarchical schema, were significantly lower in the icosapent ethyl group than in the placebo group, including the rate of cardiovascular death (4.3% vs. 5.2%; hazard ratio, 0.80; 95% CI, 0.66 to 0.98; P=0.03). A larger percentage of patients in the icosapent ethyl group than in the placebo group were hospitalized for atrial fibrillation or flutter (3.1% vs. 2.1%, P=0.004). Serious bleeding events occurred in 2.7% of the patients in the icosapent ethyl group and in 2.1% in the placebo group (P=0.06). CONCLUSIONS: Among patients with elevated triglyceride levels despite the use of statins, the risk of ischemic events, including cardiovascular death, was significantly lower among those who received 2 g of icosapent ethyl twice daily than among those who received placebo. (Funded by Amarin Pharma; REDUCE-IT ClinicalTrials.gov number, NCT01492361 .).
```

<a id="ev27-own-title"></a>
### EV27-OWN-TITLE

Source: `cache/omega3-cardiovascular-events/records.json#/records/3/title`. Rank: `PRIMARY_REPORT`. Record: `30415628`. INFERRED attribution; exact location verified.

Character offset: 9643; byte offset: 9666. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
Cardiovascular Risk Reduction with Icosapent Ethyl for Hypertriglyceridemia.
```

<a id="ev28-own-abstract"></a>
### EV28-OWN-ABSTRACT

Source: `cache/omega3-cardiovascular-events/records.json#/records/25/abstract`. Rank: `PRIMARY_REPORT`. Record: `20929341`. INFERRED attribution; exact location verified.

Character offset: 71626; byte offset: 71670. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
BACKGROUND: Results from prospective cohort studies and randomized, controlled trials have provided evidence of a protective effect of n-3 fatty acids against cardiovascular diseases. We examined the effect of the marine n-3 fatty acids eicosapentaenoic acid (EPA) and docosahexaenoic acid (DHA) and of the plant-derived alpha-linolenic acid (ALA) on the rate of cardiovascular events among patients who have had a myocardial infarction. METHODS: In a multicenter, double-blind, placebo-controlled trial, we randomly assigned 4837 patients, 60 through 80 years of age (78% men), who had had a myocardial infarction and were receiving state-of-the-art antihypertensive, antithrombotic, and lipid-modifying therapy to receive for 40 months one of four trial margarines: a margarine supplemented with a combination of EPA and DHA (with a targeted additional daily intake of 400 mg of EPA-DHA), a margarine supplemented with ALA (with a targeted additional daily intake of 2 g of ALA), a margarine supplemented with EPA-DHA and ALA, or a placebo margarine. The primary end point was the rate of major cardiovascular events, which comprised fatal and nonfatal cardiovascular events and cardiac interventions. Data were analyzed according to the intention-to-treat principle, with the use of Cox proportional-hazards models. RESULTS: The patients consumed, on average, 18.8 g of margarine per day, which resulted in additional intakes of 226 mg of EPA combined with 150 mg of DHA, 1.9 g of ALA, or both, in the active-treatment groups. During the follow-up period, a major cardiovascular event occurred in 671 patients (13.9%). Neither EPA-DHA nor ALA reduced this primary end point (hazard ratio with EPA-DHA, 1.01; 95% confidence interval [CI], 0.87 to 1.17; P=0.93; hazard ratio with ALA, 0.91; 95% CI, 0.78 to 1.05; P=0.20). In the prespecified subgroup of women, ALA, as compared with placebo and EPA-DHA alone, was associated with a reduction in the rate of major cardiovascular events that approached significance (hazard ratio, 0.73; 95% CI, 0.51 to 1.03; P=0.07). The rate of adverse events did not differ significantly among the study groups. CONCLUSIONS: Low-dose supplementation with EPA-DHA or ALA did not significantly reduce the rate of major cardiovascular events among patients who had had a myocardial infarction and who were receiving state-of-the-art antihypertensive, antithrombotic, and lipid-modifying therapy. (Funded by the Netherlands Heart Foundation and others; ClinicalTrials.gov number, NCT00127452.).
```

<a id="ev28-own-title"></a>
### EV28-OWN-TITLE

Source: `cache/omega3-cardiovascular-events/records.json#/records/25/title`. Rank: `PRIMARY_REPORT`. Record: `20929341`. INFERRED attribution; exact location verified.

Character offset: 71534; byte offset: 71578. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
n-3 fatty acids and cardiovascular events after myocardial infarction.
```

<a id="ev29-own-abstract"></a>
### EV29-OWN-ABSTRACT

Source: `cache/omega3-cardiovascular-events/records.json#/records/76/abstract`. Rank: `PRIMARY_REPORT`. Record: `21115589`. INFERRED attribution; exact location verified.

Character offset: 165601; byte offset: 165762. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
OBJECTIVE: To investigate whether dietary supplementation with B vitamins or omega 3 fatty acids, or both, could prevent major cardiovascular events in patients with a history of ischaemic heart disease or stroke. DESIGN: Double blind, randomised, placebo controlled trial; factorial design. SETTING: Recruitment throughout France via a network of 417 cardiologists, neurologists, and other physicians. PARTICIPANTS: 2501 patients with a history of myocardial infarction, unstable angina, or ischaemic stroke. INTERVENTION: Daily dietary supplement containing 5-methyltetrahydrofolate (560 μg), vitamin B-6 (3 mg), and vitamin B-12 (20 μg) or placebo; and containing omega 3 fatty acids (600 mg of eicosapentanoic acid and docosahexaenoic acid at a ratio of 2:1) or placebo. Median duration of supplementation was 4.7 years. MAIN OUTCOME MEASURES: Major cardiovascular events, defined as a composite of non-fatal myocardial infarction, stroke, or death from cardiovascular disease. RESULTS: Allocation to B vitamins lowered plasma homocysteine concentrations by 19% compared with placebo, but had no significant effects on major vascular events (75 v 82 patients, hazard ratio, 0.90 (95% confidence interval 0.66 to 1.23, P=0.50)). Allocation to omega 3 fatty acids increased plasma concentrations of omega 3 fatty acids by 37% compared with placebo, but also had no significant effect on major vascular events (81 v 76 patients, hazard ratio 1.08 (0.79 to 1.47, P=0.64)). CONCLUSION: This study does not support the routine use of dietary supplements containing B vitamins or omega 3 fatty acids for prevention of cardiovascular disease in people with a history of ischaemic heart disease or ischaemic stroke, at least when supplementation is introduced after the acute phase of the initial event. TRIAL REGISTRATION: Current Controlled Trials ISRCTN41926726.
```

<a id="ev29-own-title"></a>
### EV29-OWN-TITLE

Source: `cache/omega3-cardiovascular-events/records.json#/records/76/title`. Rank: `PRIMARY_REPORT`. Record: `21115589`. INFERRED attribution; exact location verified.

Character offset: 165467; byte offset: 165628. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
Effects of B vitamins and omega 3 fatty acids on cardiovascular diseases: a randomised placebo controlled trial.
```

<a id="ev30-own-abstract"></a>
### EV30-OWN-ABSTRACT

Source: `cache/pcsk9-mace/records.json#/records/2/abstract`. Rank: `PRIMARY_REPORT`. Record: `28304224`. INFERRED attribution; exact location verified.

Character offset: 1296; byte offset: 1296. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `d6897186b50257e98df053070532702dfba5bb4ea37fc8f8644e1ae17312ef8f`. Decoded SHA-256: `d6897186b50257e98df053070532702dfba5bb4ea37fc8f8644e1ae17312ef8f`.

```text
BACKGROUND: Evolocumab is a monoclonal antibody that inhibits proprotein convertase subtilisin-kexin type 9 (PCSK9) and lowers low-density lipoprotein (LDL) cholesterol levels by approximately 60%. Whether it prevents cardiovascular events is uncertain. METHODS: We conducted a randomized, double-blind, placebo-controlled trial involving 27,564 patients with atherosclerotic cardiovascular disease and LDL cholesterol levels of 70 mg per deciliter (1.8 mmol per liter) or higher who were receiving statin therapy. Patients were randomly assigned to receive evolocumab (either 140 mg every 2 weeks or 420 mg monthly) or matching placebo as subcutaneous injections. The primary efficacy end point was the composite of cardiovascular death, myocardial infarction, stroke, hospitalization for unstable angina, or coronary revascularization. The key secondary efficacy end point was the composite of cardiovascular death, myocardial infarction, or stroke. The median duration of follow-up was 2.2 years. RESULTS: At 48 weeks, the least-squares mean percentage reduction in LDL cholesterol levels with evolocumab, as compared with placebo, was 59%, from a median baseline value of 92 mg per deciliter (2.4 mmol per liter) to 30 mg per deciliter (0.78 mmol per liter) (P<0.001). Relative to placebo, evolocumab treatment significantly reduced the risk of the primary end point (1344 patients [9.8%] vs. 1563 patients [11.3%]; hazard ratio, 0.85; 95% confidence interval [CI], 0.79 to 0.92; P<0.001) and the key secondary end point (816 [5.9%] vs. 1013 [7.4%]; hazard ratio, 0.80; 95% CI, 0.73 to 0.88; P<0.001). The results were consistent across key subgroups, including the subgroup of patients in the lowest quartile for baseline LDL cholesterol levels (median, 74 mg per deciliter [1.9 mmol per liter]). There was no significant difference between the study groups with regard to adverse events (including new-onset diabetes and neurocognitive events), with the exception of injection-site reactions, which were more common with evolocumab (2.1% vs. 1.6%). CONCLUSIONS: In our trial, inhibition of PCSK9 with evolocumab on a background of statin therapy lowered LDL cholesterol levels to a median of 30 mg per deciliter (0.78 mmol per liter) and reduced the risk of cardiovascular events. These findings show that patients with atherosclerotic cardiovascular disease benefit from lowering of LDL cholesterol levels below current targets. (Funded by Amgen; FOURIER ClinicalTrials.gov number, NCT01764633 .).
```

<a id="ev30-own-title"></a>
### EV30-OWN-TITLE

Source: `cache/pcsk9-mace/records.json#/records/2/title`. Rank: `PRIMARY_REPORT`. Record: `28304224`. INFERRED attribution; exact location verified.

Character offset: 1201; byte offset: 1201. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `d6897186b50257e98df053070532702dfba5bb4ea37fc8f8644e1ae17312ef8f`. Decoded SHA-256: `d6897186b50257e98df053070532702dfba5bb4ea37fc8f8644e1ae17312ef8f`.

```text
Evolocumab and Clinical Outcomes in Patients with Cardiovascular Disease.
```

<a id="ev31-own-abstract"></a>
### EV31-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/104/abstract`. Rank: `PRIMARY_REPORT`. Record: `35727573`. INFERRED attribution; exact location verified.

Character offset: 254417; byte offset: 255131. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
IMPORTANCE: The efficacy of multispecies probiotic formulations in the prevention of antibiotic-associated diarrhea (AAD) remains unclear. OBJECTIVE: To assess the effect of a multispecies probiotic on the risk of AAD in children. DESIGN, SETTING, AND PARTICIPANTS: This randomized, quadruple-blind, placebo-controlled trial was conducted from February 2018 to May 2021 in a multicenter, mixed setting (inpatients and outpatients). Patients were followed up throughout the intervention period. Eligibility criteria included age 3 months to 18 years, recruitment within 24 hours following initiation of broad-spectrum systemic antibiotics, and signed informed consent. In total, 646 eligible patients were approached and 350 patients took part in the trial. INTERVENTIONS: A multispecies probiotic consisting of Bifidobacterium bifidum W23, Bifidobacterium lactis W51, Lactobacillus acidophilus W37, L acidophilus W55, Lacticaseibacillus paracasei W20, Lactiplantibacillus plantarum W62, Lacticaseibacillus rhamnosus W71, and Ligilactobacillus salivarius W24, for a total dose of 10 billion colony-forming units daily, for the duration of antibiotic treatment and for 7 days after. MAIN OUTCOMES AND MEASURES: The primary outcome was AAD, defined as 3 or more loose or watery stools per day in a 24-hour period, caused either by Clostridioides difficile or of otherwise unexplained etiology, after testing for common diarrheal pathogens. The secondary outcomes included diarrhea regardless of the etiology, diarrhea duration, and predefined diarrhea complications. RESULTS: A total of 350 children (192 boys and 158 girls; mean [range] age, 50 [3-212] months) were randomized and 313 were included in the intention-to-treat analysis. Compared with placebo (n = 155), the probiotic (n = 158) had no effect on risk of AAD (relative risk [RR], 0.81; 95% CI, 0.49-1.33). However, children in the probiotic group had a lower risk of diarrhea regardless of the etiology (RR, 0.65; 95% CI, 0.44-0.94). No differences were observed between the groups for most of the secondary outcomes, including adverse events. CONCLUSIONS AND RELEVANCE: A multispecies probiotic did not reduce the risk of AAD in children when analyzed according to the most stringent definition. However, it reduced the overall risk of diarrhea during and for 7 days after antibiotic treatment. Our study also shows that the AAD definition has a significant effect on clinical trial results and their interpretation. TRIAL REGISTRATION: ClinicalTrials.gov Identifier: NCT03334604.
```

<a id="ev31-own-title"></a>
### EV31-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/104/title`. Rank: `PRIMARY_REPORT`. Record: `35727573`. INFERRED attribution; exact location verified.

Character offset: 254278; byte offset: 254992. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Multispecies Probiotic for the Prevention of Antibiotic-Associated Diarrhea in Children: A Randomized Clinical Trial.
```

<a id="ev32-own-abstract"></a>
### EV32-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/156/abstract`. Rank: `PRIMARY_REPORT`. Record: `32035998`. INFERRED attribution; exact location verified.

Character offset: 369619; byte offset: 370551. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Antibiotic-associated diarrhoea (AAD) is a side-effect of antibiotic consumption and probiotics have been shown to reduce AAD. METHODS: A multicentre, double-blind, placebo-controlled, randomized trial was conducted to evaluate the role of Lactobacillus casei DN114001 (combined as a drink with two regular yoghurt bacterial strains) in reducing AAD and Clostridioides difficile infection in patients aged over 55 years. The primary outcome was the incidence of AAD during 2 weeks of follow-up. RESULTS: A total of 1127 patients (mean age ± standard deviation: 73.6 ± 10.5) were randomized to the active group (N = 549) or placebo group (N = 577). Both groups were followed up as per protocol. The proportion of patients experiencing AAD during follow-up was 19.3% (106/549) in the probiotic group vs 17.9% (103/577) in the placebo group (unadjusted odds ratio 1.10, 95% confidence interval 0.82-1.49, P = 0.53). CONCLUSIONS: No significant evidence was found of a beneficial effect of the specific probiotic formulation in preventing AAD in this elderly population drawn from a number of different UK hospitals. However, in the UK and in many other healthcare systems there have, in recent years, been many changes in antibiotic stewardship policies, an overall decrease in incidence in C. difficile infection, as well as an increased awareness of infection prevention, and modifications in nursing practice. In light of these factors, it is impossible to conclude definitively from the current trial that the study-specific probiotic formulation has no role in preventing AAD, and it is our view that further trials may be indicated, controlling for these variables.
```

<a id="ev32-own-title"></a>
### EV32-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/156/title`. Rank: `PRIMARY_REPORT`. Record: `32035998`. INFERRED attribution; exact location verified.

Character offset: 369481; byte offset: 370413. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Do probiotics prevent antibiotic-associated diarrhoea? Results of a multicentre randomized placebo-controlled trial.
```

<a id="ev33-own-abstract"></a>
### EV33-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/328/abstract`. Rank: `PRIMARY_REPORT`. Record: `24772726`. INFERRED attribution; exact location verified.

Character offset: 789902; byte offset: 791991. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIMS: To evaluate the effectiveness, safety and tolerability of a probiotic formulation containing Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12 in the prevention of antibiotic associated diarrhoea (AAD). METHODS AND MATERIAL: A double-blind randomised placebo controlled multicentric trial was conducted in adults who were prescribed a seven-day course of oral antibiotic (either cefadroxil or amoxycillin) for a documented indication. The effectiveness of a 14-day therapy (concomitant with antibiotic course and seven days thereafter) of the probiotic formulation in preventing AAD was evaluated. Safety profile was assessed by monitoring of all treatment emergent adverse events and tolerability on a global well being scale. RESULTS: The incidence of AAD in the probiotic group was 10.8% compared to 15.6% in the placebo group, the difference being statistically non-significant (p = 0.19). The relative risk for AAD was 0.7 with the 95% CI being 0.4 to 1.2. The diarrhoea duration in the probiotic group was two days with an interquartile range of 1- 3 days and was significantly less (p = 0.01) than the placebo group which was four days with an interquartile range of 3 - 5.5 days. Subgroup analysis of subjects with AAD showed that the incidence of severe diarrhoea (watery stools) was 96% in the placebo group (25 out of 26) compared to 31.6% (6 out of 19) in the probiotic group and this difference was significant statistically (p < 0.001). Four mild, non-serious, adverse events were detected (2.0%) in the probiotic group but there were none in the placebo group. CONCLUSION: This randomised controlled trial shows that prophylactic administration of the probiotic formulation containing Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12, did not effectively lower the incidence of AAD in adults. However, compared to placebo the duration of diarrhoea in the probiotic group was significantly reduced. Its tolerability and safety profile were good.
```

<a id="ev33-own-title"></a>
### EV33-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/328/title`. Rank: `PRIMARY_REPORT`. Record: `24772726`. INFERRED attribution; exact location verified.

Character offset: 789685; byte offset: 791774. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Randomised placebo-controlled double blind multicentric trial on efficacy and safety of Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12 for prevention of antibiotic-associated diarrhoea.
```

<a id="ev34-own-abstract"></a>
### EV34-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/333/abstract`. Rank: `PRIMARY_REPORT`. Record: `23932219`. INFERRED attribution; exact location verified.

Character offset: 802836; byte offset: 804953. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Antibiotic-associated diarrhoea (AAD) occurs most frequently in older (≥65 years) inpatients exposed to broad-spectrum antibiotics. When caused by Clostridium difficile, AAD can result in life-threatening illness. Although underlying disease mechanisms are not well understood, microbial preparations have been assessed in the prevention of AAD. However, studies have been mostly small single-centre trials with varying quality, providing insufficient data to reliably assess effectiveness. We aimed to do a pragmatic efficacy trial in older inpatients who would be representative of those admitted to National Health Service (NHS) and similar secondary care institutions and to recruit a sufficient number of patients to generate a definitive result. METHODS: We did a multicentre, randomised, double-blind, placebo-controlled, pragmatic, efficacy trial of inpatients aged 65 years and older and exposed to one or more oral or parenteral antibiotics. A computer-generated randomisation scheme was used to allocate participants (in a 1:1 ratio) to receive either a multistrain preparation of lactobacilli and bifidobacteria, with a total of 6 × 10(10) organisms, one per day for 21 days, or an identical placebo. Patients, study staff, and specimen and data analysts were masked to assignment. The primary outcomes were occurrence of AAD within 8 weeks and C difficile diarrhoea (CDD) within 12 weeks of recruitment. Analysis was by modified intention-to-treat. This trial is registered, number ISRCTN70017204. FINDINGS: Of 17,420 patients screened, 1493 were randomly assigned to the microbial preparation group and 1488 to the placebo group. 1470 and 1471, respectively, were included in the analyses of the primary endpoints. AAD (including CDD) occurred in 159 (10·8%) participants in the microbial preparation group and 153 (10·4%) participants in the placebo group (relative risk [RR] 1·04; 95% CI 0·84-1·28; p=0·71). CDD was an uncommon cause of AAD and occurred in 12 (0·8%) participants in the microbial preparation group and 17 (1·2%) participants in the placebo group (RR 0·71; 95% CI 0·34-1·47; p=0·35). 578 (19·7%) participants had one or more serious adverse event; the frequency of serious adverse events was much the same in the two study groups and none was attributed to participation in the trial. INTERPRETATION: We identified no evidence that a multistrain preparation of lactobacilli and bifidobacteria was effective in prevention of AAD or CDD. An improved understanding of the pathophysiology of AAD is needed to guide future studies. FUNDING: Health Technology Assessment programme; National Institute for Health Research, UK.
```

<a id="ev34-own-title"></a>
### EV34-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/333/title`. Rank: `PRIMARY_REPORT`. Record: `23932219`. INFERRED attribution; exact location verified.

Character offset: 802596; byte offset: 804713. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Lactobacilli and bifidobacteria in the prevention of antibiotic-associated diarrhoea and Clostridium difficile diarrhoea in older inpatients (PLACIDE): a randomised, double-blind, placebo-controlled, multicentre trial.
```

<a id="ev34-protocol-entry"></a>
### EV34-PROTOCOL-ENTRY

Source: `cache/probiotics-aad-prevention/ft_22559011.txt`. Rank: `TRIAL_PROTOCOL`. Record: `22559011`. INFERRED attribution; exact location verified.

Character offset: 0; byte offset: 0. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8e97dd35b444b8e55c38925bda0f1070e094c2e849796da83039ab4e9f409f90`. Decoded SHA-256: `8e97dd35b444b8e55c38925bda0f1070e094c2e849796da83039ab4e9f409f90`.

```text

```

<a id="ev35-own-abstract"></a>
### EV35-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/357/abstract`. Rank: `PRIMARY_REPORT`. Record: `18701826`. INFERRED attribution; exact location verified.

Character offset: 859146; byte offset: 861328. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIM: To determine the efficacy of a combination of Bifidobacterium longum PL03, Lactobacillus rhamnosus KL53A and Lactobacillus plantarum PL02 for the prevention of antibiotic-associated diarrhea in children. METHODS: Seventy-eight children (age: 5 months to 16 years) with otitis media, and/or respiratory tract infections, and/or urinary tract infections were enrolled in a double-blind randomized control trial in which they received standard antibiotic treatment plus a food supplement containing 10(8) colony-forming units of B. longum, L. rhamnosus and L. plantarum (n = 40) or a placebo (n = 38) orally twice daily for the duration of antibiotic treatment. RESULTS: Patients receiving probiotics had a similar rate of diarrhea (> or =3 loose or watery stools/day for > or =48 h occurring during or up to 2 weeks after the antibiotic therapy) as those receiving placebo (relative risk 0.5, 95% CI 0.06-3.5). The mean number of stools per day was significantly lower in the experimental group (mean difference -0.3 stool/day, 95% CI -0.5 to -0.07). No adverse events were reported. CONCLUSION: The administration of the 3 probiotics did not significantly alter the rate of diarrhea, although it reduced the frequency of stools per day. As the overall frequency of diarrhea was surprisingly low, these results should be interpreted with caution.
```

<a id="ev35-own-title"></a>
### EV35-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/357/title`. Rank: `PRIMARY_REPORT`. Record: `18701826`. INFERRED attribution; exact location verified.

Character offset: 858930; byte offset: 861112. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Bifidobacterium longum PL03, Lactobacillus rhamnosus KL53A, and Lactobacillus plantarum PL02 in the prevention of antibiotic-associated diarrhea in children: a randomized controlled pilot trial.
```

<a id="ev36-own-abstract"></a>
### EV36-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/359/abstract`. Rank: `PRIMARY_REPORT`. Record: `18410562`. INFERRED attribution; exact location verified.

Character offset: 863531; byte offset: 865713. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Convincing evidence that probiotic administration can lower the risk of antibiotic-associated diarrhoea is limited to certain micro-organisms. AIM: To determine the efficacy of administration of Lactobacillus rhamnosus (strains E/N, Oxy and Pen) for the prevention of antibiotic-associated diarrhoea in children. METHODS: Children (aged 3 months to 14 years) with common infections were enrolled in a double-blind, randomized, placebo-controlled trial in which they received standard antibiotic treatment plus 2 x 10(10) colony forming units of a probiotic (n = 120) or a placebo (n = 120), administered orally twice daily throughout antibiotic treatment. Analyses were by intention to treat. RESULTS: Any diarrhoea (>or=3 loose or watery stools/day for >or=48 h occurring during or up to 2 weeks after the antibiotic therapy) occurred in nine (7.5%) patients in the probiotic group and in 20 (17%) patients in the placebo group (relative risk, RR 0.45, 95% confidence interval, CI 0.2-0.9). Three (2.5%) children in the probiotic group developed AAD (diarrhoea caused by Clostridium difficile or otherwise unexplained diarrhoea) compared to nine (7.5%) in the placebo group (RR 0.33, 95% CI 0.1-1.06). No adverse events were observed. CONCLUSION: Administration of L. rhamnosus (strains E/N, Oxy and Pen) to children receiving antibiotics reduced the risk of any diarrhoea, as defined in this study.
```

<a id="ev36-own-title"></a>
### EV36-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/359/title`. Rank: `PRIMARY_REPORT`. Record: `18410562`. INFERRED attribution; exact location verified.

Character offset: 863360; byte offset: 865542. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Clinical trial: effectiveness of Lactobacillus rhamnosus (strains E/N, Oxy and Pen) in the prevention of antibiotic-associated diarrhoea in children.
```

<a id="ev37-own-abstract"></a>
### EV37-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/375/abstract`. Rank: `PRIMARY_REPORT`. Record: `15740542`. INFERRED attribution; exact location verified.

Character offset: 897096; byte offset: 899278. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Co-treatment with Saccharomyces boulardii appears to lower the risk of antibiotic-associated diarrhoea in adults receiving broad-spectrum antibiotics. AIM: To determine whether S. boulardii prevents antibiotic-associated diarrhoea in children. METHODS: A total of 269 children (aged 6 months to 14 years) with otitis media and/or respiratory tract infections were enrolled in a double-blind, randomized placebo-controlled trial in which they received standard antibiotic treatment plus 250 mg of S. boulardii (experimental group, n = 132) or a placebo (control group, n = 137) orally twice daily for the duration of antibiotic treatment. Analyses were based on allocated treatment and included data from 246 children. RESULTS: Patients receiving S. boulardii had a lower prevalence of diarrhoea (> or =3 loose or watery stools/day for > or =48 h occurring during or up to 2 weeks after the antibiotic therapy) than those receiving placebo [nine of 119 (8%) vs. 29 of 127 (23%), relative risk: 0.3, 95% confidence interval: 0.2-0.7]. S. boulardii also reduced the risk of antibiotic-associated diarrhoea (diarrhoea caused by Clostridium difficile or otherwise unexplained diarrhoea) compared with placebo [four of 119 (3.4%) vs. 22 of 127 (17.3%), relative risk: 0.2; 95% confidence interval: 0.07-0.5]. No adverse events were observed. CONCLUSION: This is the first randomized-controlled trial evidence that S. boulardii effectively reduces the risk of antibiotic-associated diarrhoea in children.
```

<a id="ev37-own-title"></a>
### EV37-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/375/title`. Rank: `PRIMARY_REPORT`. Record: `15740542`. INFERRED attribution; exact location verified.

Character offset: 896933; byte offset: 899115. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Saccharomyces boulardii in the prevention of antibiotic-associated diarrhoea in children: a randomized double-blind placebo-controlled trial.
```

<a id="ev38-own-abstract"></a>
### EV38-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/384/abstract`. Rank: `PRIMARY_REPORT`. Record: `11560298`. INFERRED attribution; exact location verified.

Character offset: 917673; byte offset: 919855. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
OBJECTIVES: To assess the efficacy of Lactobacillus GG in preventing antibiotic-associated diarrhea (AAD) in adults and, secondarily, to assess the effect of coadministered Lactobacillus GG on the number of tests performed to determine the cause of diarrhea. PATIENTS AND METHODS: In this prospective, randomized, double-blind, placebo-controlled trial conducted from July 1998 to October 1999, 302 hospitalized patients receiving antibiotics were randomized to receive Lactobacillus GG, 20 x 10(9) CFU/d, or placebo for 14 days. Subjects recorded the number of stools and their consistency daily for 21 days. The primary outcome was the proportion of patients who developed diarrhea in the first 21 days after enrollment. Weekly telephone follow-up was also performed. Results were analyzed in an intention-to-treat fashion. RESULTS: Diarrhea developed in 39 (29.3%) of 133 patients randomized to receive Lactobacillus GG and in 40 (29.9%) of 134 patients randomized to receive placebo (P=.93). No additional difference in the rate of occurrence of diarrhea was found between treatment and placebo patients in a subgroup analysis of those treated with beta-lactam vs non-beta-lactam antibiotics. Too few patients had stool cultures, additional laboratory tests for diarrhea, or a positive diagnosis of Clostridium difficile infection to assess between-group differences. CONCLUSION: Lactobacillus GG in a dose of 20 x 10(9) CFU/d did not reduce the rate of occurrence of diarrhea in this sample of 267 adult patients taking antibiotics initially administered in the hospital setting.
```

<a id="ev38-own-title"></a>
### EV38-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/384/title`. Rank: `PRIMARY_REPORT`. Record: `11560298`. INFERRED attribution; exact location verified.

Character offset: 917542; byte offset: 919724. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Lack of effect of Lactobacillus GG on antibiotic-associated diarrhea: a randomized, placebo-controlled trial.
```

<a id="ev39-own-abstract"></a>
### EV39-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/400/abstract`. Rank: `PRIMARY_REPORT`. Record: `7872284`. INFERRED attribution; exact location verified.

Character offset: 953046; byte offset: 955228. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
OBJECTIVES: To determine the safety and efficacy of a new preventive agent for antibiotic-associated diarrhea (AAD) in patients receiving at least one beta-lactam antibiotic. METHODS: A double-blinded, placebo-controlled, parallel group study was performed in a high-risk group of hospitalized patients receiving a new prescription for a beta-lactam antibiotic and having no acute diarrhea on enrollment. Lyophilized Saccharomyces boulardii or placebo (1 g/day) was given within 72 h of the start of the antibiotic(s) and continued until 3 days after the antibiotic was discontinued, after which the patients were followed for 7 wk. RESULTS: Of the 193 eligible patients, significantly fewer, 7/97 (7.2%), patients receiving S. boulardii developed AAD compared with 14/96 (14.6%) on placebo (p = 0.02). The efficacy of S. boulardii for the prevention of AAD was 51%. Using a multivariate model to adjust for two independent risk factors for AAD (age and days of cephalosporin use), the adjusted relative risk was significantly protective for S. boulardii (RR = 0.29, 95% CI = 0.08, 0.98). CONCLUSION: The prophylactic use of S. boulardii given with a beta-lactam antibiotic resulted in a significant reduction of AAD with no serious adverse reactions.
```

<a id="ev39-own-title"></a>
### EV39-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/400/title`. Rank: `PRIMARY_REPORT`. Record: `7872284`. INFERRED attribution; exact location verified.

Character offset: 952929; byte offset: 955111. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Prevention of beta-lactam-associated diarrhea by Saccharomyces boulardii compared with placebo.
```

<a id="ev40-baseline-exclusion"></a>
### EV40-BASELINE-EXCLUSION

Source: `cache/probiotics-aad-prevention/ft_21165295.txt`. Rank: `PRIMARY_REPORT`. Record: `21165295`. INFERRED attribution; exact location verified.

Character offset: 16327; byte offset: 16334. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `4a83ee3dbf9df85006b748186ed92bfa96df59208919b48379e15cc74ea631eb`. Decoded SHA-256: `4a83ee3dbf9df85006b748186ed92bfa96df59208919b48379e15cc74ea631eb`.

```text
The following patients were excluded from the study: 1) those who were diagnosed with <italic toggle="yes">C. difficile</italic> colitis within the previous 3 months, 2) those who were given tube feeding or who underwent an ileostomy or colostomy, 3) those with basal diarrheal disease (acute enteritis, inflammatory bowel disease, radiation enteritis, ischemic colitis and diarrhea caused by carcinoid)
```

<a id="ev40-own-abstract"></a>
### EV40-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/420/abstract`. Rank: `PRIMARY_REPORT`. Record: `21165295`. INFERRED attribution; exact location verified.

Character offset: 995898; byte offset: 998126. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Antibiotic-associated diarrhea (AAD) is a common complication of antibiotic use. There is growing interest in probiotics for the treatment of AAD and Clostridium difficile infection because of the wide availability of probiotics. The aim of this multicenter, randomized, placebo-controlled, double-blind trial was to assess the efficacy of probiotic Lactobacillus (Lacidofil® cap) for the prevention of AAD in adults. From September 2008 to November 2009, a total of 214 patients with respiratory tract infection who had begun receiving antibiotics were randomized to receive Lactobacillus (Lacidofil® cap) or placebo for 14 days. Patients recorded bowel frequency and stool consistency daily for 14 days. The primary outcome was the proportion of patients who developed AAD within 14 days of enrollment. AAD developed in 4 (3.9%) of 103 patients in the Lactobacillus group and in 8 (7.2%) of 111 patients in the placebo group (P=0.44). However, the Lactobacillus group showed lower change in bowel frequency and consistency (50/103, 48.5%) than the placebo group (35/111, 31.5%) (P=0.01). Although the Lacidofil® cap does not reduce the rate of occurrence of AAD in adult patients with respiratory tract infection who have taken antibiotics, the Lactobacillus group maintains their bowel habits to a greater extent than the placebo group.
```

<a id="ev40-own-title"></a>
### EV40-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/420/title`. Rank: `PRIMARY_REPORT`. Record: `21165295`. INFERRED attribution; exact location verified.

Character offset: 995712; byte offset: 997939. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Effect of probiotic Lactobacillus (Lacidofil® cap) for the prevention of antibiotic-associated diarrhea: a prospective, randomized, double-blind, multicenter study.
```

<a id="ev41-own-abstract"></a>
### EV41-OWN-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/430/abstract`. Rank: `PRIMARY_REPORT`. Record: `18026577`. INFERRED attribution; exact location verified.

Character offset: 1011025; byte offset: 1013256. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Antibiotic-associated diarrhea is an important problem in hospitalized patients. The use of probiotics is gaining interest in the scientific community as a potential measure to prevent this complication. The main objective of the present study was to assess the efficacy and safety of a fermented milk combining Lactobacillus acidophilus and Lactobacillus casei that is widely available in Canada, in the prevention of antibiotic-associated diarrhea. METHODS: In this double-blind, randomized study, hospitalized patients were randomly assigned to receive either a lactobacilli-fermented milk or a placebo on a daily basis. RESULTS: Among 89 randomized patients, antibiotic-associated diarrhea occurred in seven of 44 patients (15.9%) in the lactobacilli group and in 16 of 45 patients (35.6%) in the placebo group (OR 0.34, 95% CI 0.125 to 0.944; P=0.05). The median hospitalization duration was eight days in the lactobacilli group, compared with 10 days in the placebo group (P=0.09). Overall, the lactobacilli-fermented milk was well tolerated. CONCLUSION: The daily administration of a lactobacilli-fermented milk was safe and effective in the prevention of antibiotic-associated diarrhea in hospitalized patients.
```

<a id="ev41-own-title"></a>
### EV41-OWN-TITLE

Source: `cache/probiotics-aad-prevention/records.json#/records/430/title`. Rank: `PRIMARY_REPORT`. Record: `18026577`. INFERRED attribution; exact location verified.

Character offset: 1010803; byte offset: 1013034. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Effect of a fermented milk combining Lactobacillus acidophilus Cl1285 and Lactobacillus casei in the prevention of antibiotic-associated diarrhea: a randomized, double-blind, placebo-controlled trial.
```

<a id="ev42-own-abstract"></a>
### EV42-OWN-ABSTRACT

Source: `cache/sacubitril-valsartan-hfref/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `25176015`. INFERRED attribution; exact location verified.

Character offset: 543; byte offset: 543. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`. Decoded SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`.

```text
BACKGROUND: We compared the angiotensin receptor-neprilysin inhibitor LCZ696 with enalapril in patients who had heart failure with a reduced ejection fraction. In previous studies, enalapril improved survival in such patients. METHODS: In this double-blind trial, we randomly assigned 8442 patients with class II, III, or IV heart failure and an ejection fraction of 40% or less to receive either LCZ696 (at a dose of 200 mg twice daily) or enalapril (at a dose of 10 mg twice daily), in addition to recommended therapy. The primary outcome was a composite of death from cardiovascular causes or hospitalization for heart failure, but the trial was designed to detect a difference in the rates of death from cardiovascular causes. RESULTS: The trial was stopped early, according to prespecified rules, after a median follow-up of 27 months, because the boundary for an overwhelming benefit with LCZ696 had been crossed. At the time of study closure, the primary outcome had occurred in 914 patients (21.8%) in the LCZ696 group and 1117 patients (26.5%) in the enalapril group (hazard ratio in the LCZ696 group, 0.80; 95% confidence interval [CI], 0.73 to 0.87; P<0.001). A total of 711 patients (17.0%) receiving LCZ696 and 835 patients (19.8%) receiving enalapril died (hazard ratio for death from any cause, 0.84; 95% CI, 0.76 to 0.93; P<0.001); of these patients, 558 (13.3%) and 693 (16.5%), respectively, died from cardiovascular causes (hazard ratio, 0.80; 95% CI, 0.71 to 0.89; P<0.001). As compared with enalapril, LCZ696 also reduced the risk of hospitalization for heart failure by 21% (P<0.001) and decreased the symptoms and physical limitations of heart failure (P=0.001). The LCZ696 group had higher proportions of patients with hypotension and nonserious angioedema but lower proportions with renal impairment, hyperkalemia, and cough than the enalapril group. CONCLUSIONS: LCZ696 was superior to enalapril in reducing the risks of death and of hospitalization for heart failure. (Funded by Novartis; PARADIGM-HF ClinicalTrials.gov number, NCT01035255.).
```

<a id="ev42-own-title"></a>
### EV42-OWN-TITLE

Source: `cache/sacubitril-valsartan-hfref/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `25176015`. INFERRED attribution; exact location verified.

Character offset: 453; byte offset: 453. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`. Decoded SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`.

```text
Angiotensin-neprilysin inhibition versus enalapril in heart failure.
```

<a id="ev43-arm-144"></a>
### EV43-ARM-144

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/144`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 84191; byte offset: 84209. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
{"active_interventions":["lcz696"],"arm_id":"NCT02468232:434353320","background_therapy":[],"dose":{"absence_code":"NOT_SEPARATELY_CODED","value":null},"drug":{"span":{"rows":[{"$row":1401},{"$row":1339}],"source":"AACT.interventions"},"value":["LCZ696","Placebo to Enalapril"]},"label":{"span":{"row":{"$row":285},"source":"AACT.design_groups"},"value":"LCZ696"},"linkage_complete":true,"n_randomised":{"absence_code":"NO_DESIGN_GROUP_TO_RESULT_GROUP_LINK","value":null},"route":{"absence_code":"NOT_SEPARATELY_CODED","value":null},"schedule":{"absence_code":"NOT_SEPARATELY_CODED","value":null},"span":{"$object":143}}
```

<a id="ev43-arm-146"></a>
### EV43-ARM-146

Source: `cache/sacubitril-valsartan-hfref/family_registry.payload.json.gz#/objects/146`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 84962; byte offset: 84980. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `63aec39f596be635e4bf45c985f358f2dce206c450c44c2a384c245b2287843b`. Decoded SHA-256: `e62b535061b47a793daa2c27b86130d21d263b2eca70055e1b3303b1a9c0a111`.

```text
{"active_interventions":["enalapril"],"arm_id":"NCT02468232:434353321","background_therapy":[],"dose":{"absence_code":"NOT_SEPARATELY_CODED","value":null},"drug":{"span":{"rows":[{"$row":1402},{"$row":1351}],"source":"AACT.interventions"},"value":["Enalapril","Placebo to LCZ696"]},"label":{"span":{"row":{"$row":286},"source":"AACT.design_groups"},"value":"Enalapril"},"linkage_complete":true,"n_randomised":{"absence_code":"NO_DESIGN_GROUP_TO_RESULT_GROUP_LINK","value":null},"route":{"absence_code":"NOT_SEPARATELY_CODED","value":null},"schedule":{"absence_code":"NOT_SEPARATELY_CODED","value":null},"span":{"$object":145}}
```

<a id="ev43-own-title"></a>
### EV43-OWN-TITLE

Source: `cache/sacubitril-valsartan-hfref/records.json#/ctgov/16/title`. Rank: `REGISTRY`. Record: `NCT02468232`. INFERRED attribution; exact location verified.

Character offset: 143642; byte offset: 143895. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`. Decoded SHA-256: `29bc165858bc01df37c424e8334a4cc5052bedd12f88c77271871ce1c7fcb31d`.

```text
Study of Efficacy and Safety of LCZ696 in Japanese Patients With Chronic Heart Failure and Reduced Ejection Fraction
```

<a id="ev44-own-abstract"></a>
### EV44-OWN-ABSTRACT

Source: `cache/semaglutide-obesity-mace/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `37952131`. INFERRED attribution; exact location verified.

Character offset: 605; byte offset: 605. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`. Decoded SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`.

```text
BACKGROUND: Semaglutide, a glucagon-like peptide-1 receptor agonist, has been shown to reduce the risk of adverse cardiovascular events in patients with diabetes. Whether semaglutide can reduce cardiovascular risk associated with overweight and obesity in the absence of diabetes is unknown. METHODS: In a multicenter, double-blind, randomized, placebo-controlled, event-driven superiority trial, we enrolled patients 45 years of age or older who had preexisting cardiovascular disease and a body-mass index (the weight in kilograms divided by the square of the height in meters) of 27 or greater but no history of diabetes. Patients were randomly assigned in a 1:1 ratio to receive once-weekly subcutaneous semaglutide at a dose of 2.4 mg or placebo. The primary cardiovascular end point was a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke in a time-to-first-event analysis. Safety was also assessed. RESULTS: A total of 17,604 patients were enrolled; 8803 were assigned to receive semaglutide and 8801 to receive placebo. The mean (±SD) duration of exposure to semaglutide or placebo was 34.2±13.7 months, and the mean duration of follow-up was 39.8±9.4 months. A primary cardiovascular end-point event occurred in 569 of the 8803 patients (6.5%) in the semaglutide group and in 701 of the 8801 patients (8.0%) in the placebo group (hazard ratio, 0.80; 95% confidence interval, 0.72 to 0.90; P<0.001). Adverse events leading to permanent discontinuation of the trial product occurred in 1461 patients (16.6%) in the semaglutide group and 718 patients (8.2%) in the placebo group (P<0.001). CONCLUSIONS: In patients with preexisting cardiovascular disease and overweight or obesity but without diabetes, weekly subcutaneous semaglutide at a dose of 2.4 mg was superior to placebo in reducing the incidence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke at a mean follow-up of 39.8 months. (Funded by Novo Nordisk; SELECT ClinicalTrials.gov number, NCT03574597.).
```

<a id="ev44-own-title"></a>
### EV44-OWN-TITLE

Source: `cache/semaglutide-obesity-mace/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `37952131`. INFERRED attribution; exact location verified.

Character offset: 515; byte offset: 515. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`. Decoded SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`.

```text
Semaglutide and Cardiovascular Outcomes in Obesity without Diabetes.
```

<a id="ev45-own-abstract"></a>
### EV45-OWN-ABSTRACT

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `28605608`. INFERRED attribution; exact location verified.

Character offset: 474; byte offset: 474. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
Background Canagliflozin is a sodium-glucose cotransporter 2 inhibitor that reduces glycemia as well as blood pressure, body weight, and albuminuria in people with diabetes. We report the effects of treatment with canagliflozin on cardiovascular, renal, and safety outcomes. Methods The CANVAS Program integrated data from two trials involving a total of 10,142 participants with type 2 diabetes and high cardiovascular risk. Participants in each trial were randomly assigned to receive canagliflozin or placebo and were followed for a mean of 188.2 weeks. The primary outcome was a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke. Results The mean age of the participants was 63.3 years, 35.8% were women, the mean duration of diabetes was 13.5 years, and 65.6% had a history of cardiovascular disease. The rate of the primary outcome was lower with canagliflozin than with placebo (occurring in 26.9 vs. 31.5 participants per 1000 patient-years; hazard ratio, 0.86; 95% confidence interval [CI], 0.75 to 0.97; P<0.001 for noninferiority; P=0.02 for superiority). Although on the basis of the prespecified hypothesis testing sequence the renal outcomes are not viewed as statistically significant, the results showed a possible benefit of canagliflozin with respect to the progression of albuminuria (hazard ratio, 0.73; 95% CI, 0.67 to 0.79) and the composite outcome of a sustained 40% reduction in the estimated glomerular filtration rate, the need for renal-replacement therapy, or death from renal causes (hazard ratio, 0.60; 95% CI, 0.47 to 0.77). Adverse reactions were consistent with the previously reported risks associated with canagliflozin except for an increased risk of amputation (6.3 vs. 3.4 participants per 1000 patient-years; hazard ratio, 1.97; 95% CI, 1.41 to 2.75); amputations were primarily at the level of the toe or metatarsal. Conclusions In two trials involving patients with type 2 diabetes and an elevated risk of cardiovascular disease, patients treated with canagliflozin had a lower risk of cardiovascular events than those who received placebo but a greater risk of amputation, primarily at the level of the toe or metatarsal. (Funded by Janssen Research and Development; CANVAS and CANVAS-R ClinicalTrials.gov numbers, NCT01032629 and NCT01989754 , respectively.).
```

<a id="ev45-own-title"></a>
### EV45-OWN-TITLE

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `28605608`. INFERRED attribution; exact location verified.

Character offset: 383; byte offset: 383. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
Canagliflozin and Cardiovascular and Renal Events in Type 2 Diabetes.
```

<a id="ev46-own-abstract"></a>
### EV46-OWN-ABSTRACT

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `26378978`. INFERRED attribution; exact location verified.

Character offset: 3288; byte offset: 3288. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
BACKGROUND: The effects of empagliflozin, an inhibitor of sodium-glucose cotransporter 2, in addition to standard care, on cardiovascular morbidity and mortality in patients with type 2 diabetes at high cardiovascular risk are not known. METHODS: We randomly assigned patients to receive 10 mg or 25 mg of empagliflozin or placebo once daily. The primary composite outcome was death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke, as analyzed in the pooled empagliflozin group versus the placebo group. The key secondary composite outcome was the primary outcome plus hospitalization for unstable angina. RESULTS: A total of 7020 patients were treated (median observation time, 3.1 years). The primary outcome occurred in 490 of 4687 patients (10.5%) in the pooled empagliflozin group and in 282 of 2333 patients (12.1%) in the placebo group (hazard ratio in the empagliflozin group, 0.86; 95.02% confidence interval, 0.74 to 0.99; P=0.04 for superiority). There were no significant between-group differences in the rates of myocardial infarction or stroke, but in the empagliflozin group there were significantly lower rates of death from cardiovascular causes (3.7%, vs. 5.9% in the placebo group; 38% relative risk reduction), hospitalization for heart failure (2.7% and 4.1%, respectively; 35% relative risk reduction), and death from any cause (5.7% and 8.3%, respectively; 32% relative risk reduction). There was no significant between-group difference in the key secondary outcome (P=0.08 for superiority). Among patients receiving empagliflozin, there was an increased rate of genital infection but no increase in other adverse events. CONCLUSIONS: Patients with type 2 diabetes at high risk for cardiovascular events who received empagliflozin, as compared with placebo, had a lower rate of the primary composite cardiovascular outcome and of death from any cause when the study drug was added to standard care. (Funded by Boehringer Ingelheim and Eli Lilly; EMPA-REG OUTCOME ClinicalTrials.gov number, NCT01131676.).
```

<a id="ev46-own-title"></a>
### EV46-OWN-TITLE

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/1/title`. Rank: `PRIMARY_REPORT`. Record: `26378978`. INFERRED attribution; exact location verified.

Character offset: 3193; byte offset: 3193. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
Empagliflozin, Cardiovascular Outcomes, and Mortality in Type 2 Diabetes.
```

<a id="ev47-own-abstract"></a>
### EV47-OWN-ABSTRACT

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/3/abstract`. Rank: `PRIMARY_REPORT`. Record: `30415602`. INFERRED attribution; exact location verified.

Character offset: 8704; byte offset: 8708. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
BACKGROUND: The cardiovascular safety profile of dapagliflozin, a selective inhibitor of sodium-glucose cotransporter 2 that promotes glucosuria in patients with type 2 diabetes, is undefined. METHODS: We randomly assigned patients with type 2 diabetes who had or were at risk for atherosclerotic cardiovascular disease to receive either dapagliflozin or placebo. The primary safety outcome was a composite of major adverse cardiovascular events (MACE), defined as cardiovascular death, myocardial infarction, or ischemic stroke. The primary efficacy outcomes were MACE and a composite of cardiovascular death or hospitalization for heart failure. Secondary efficacy outcomes were a renal composite (≥40% decrease in estimated glomerular filtration rate to <60 ml per minute per 1.73 m2 of body-surface area, new end-stage renal disease, or death from renal or cardiovascular causes) and death from any cause. RESULTS: We evaluated 17,160 patients, including 10,186 without atherosclerotic cardiovascular disease, who were followed for a median of 4.2 years. In the primary safety outcome analysis, dapagliflozin met the prespecified criterion for noninferiority to placebo with respect to MACE (upper boundary of the 95% confidence interval [CI], <1.3; P<0.001 for noninferiority). In the two primary efficacy analyses, dapagliflozin did not result in a lower rate of MACE (8.8% in the dapagliflozin group and 9.4% in the placebo group; hazard ratio, 0.93; 95% CI, 0.84 to 1.03; P=0.17) but did result in a lower rate of cardiovascular death or hospitalization for heart failure (4.9% vs. 5.8%; hazard ratio, 0.83; 95% CI, 0.73 to 0.95; P=0.005), which reflected a lower rate of hospitalization for heart failure (hazard ratio, 0.73; 95% CI, 0.61 to 0.88); there was no between-group difference in cardiovascular death (hazard ratio, 0.98; 95% CI, 0.82 to 1.17). A renal event occurred in 4.3% in the dapagliflozin group and in 5.6% in the placebo group (hazard ratio, 0.76; 95% CI, 0.67 to 0.87), and death from any cause occurred in 6.2% and 6.6%, respectively (hazard ratio, 0.93; 95% CI, 0.82 to 1.04). Diabetic ketoacidosis was more common with dapagliflozin than with placebo (0.3% vs. 0.1%, P=0.02), as was the rate of genital infections that led to discontinuation of the regimen or that were considered to be serious adverse events (0.9% vs. 0.1%, P<0.001). CONCLUSIONS: In patients with type 2 diabetes who had or were at risk for atherosclerotic cardiovascular disease, treatment with dapagliflozin did not result in a higher or lower rate of MACE than placebo but did result in a lower rate of cardiovascular death or hospitalization for heart failure, a finding that reflects a lower rate of hospitalization for heart failure. (Funded by AstraZeneca; DECLARE-TIMI 58 ClinicalTrials.gov number, NCT01730534 .).
```

<a id="ev47-own-title"></a>
### EV47-OWN-TITLE

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/3/title`. Rank: `PRIMARY_REPORT`. Record: `30415602`. INFERRED attribution; exact location verified.

Character offset: 8621; byte offset: 8625. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
Dapagliflozin and Cardiovascular Outcomes in Type 2 Diabetes.
```

<a id="ev48-own-abstract"></a>
### EV48-OWN-ABSTRACT

Source: `cache/spironolactone-hfref-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `10471456`. INFERRED attribution; exact location verified.

Character offset: 487; byte offset: 487. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
BACKGROUND AND METHODS: Aldosterone is important in the pathophysiology of heart failure. In a doubleblind study, we enrolled 1663 patients who had severe heart failure and a left ventricular ejection fraction of no more than 35 percent and who were being treated with an angiotensin-converting-enzyme inhibitor, a loop diuretic, and in most cases digoxin. A total of 822 patients were randomly assigned to receive 25 mg of spironolactone daily, and 841 to receive placebo. The primary end point was death from all causes. RESULTS: The trial was discontinued early, after a mean follow-up period of 24 months, because an interim analysis determined that spironolactone was efficacious. There were 386 deaths in the placebo group (46 percent) and 284 in the spironolactone group (35 percent; relative risk of death, 0.70; 95 percent confidence interval, 0.60 to 0.82; P<0.001). This 30 percent reduction in the risk of death among patients in the spironolactone group was attributed to a lower risk of both death from progressive heart failure and sudden death from cardiac causes. The frequency of hospitalization for worsening heart failure was 35 percent lower in the spironolactone group than in the placebo group (relative risk of hospitalization, 0.65; 95 percent confidence interval, 0.54 to 0.77; P<0.001). In addition, patients who received spironolactone had a significant improvement in the symptoms of heart failure, as assessed on the basis of the New York Heart Association functional class (P<0.001). Gynecomastia or breast pain was reported in 10 percent of men who were treated with spironolactone, as compared with 1 percent of men in the placebo group (P<0.001). The incidence of serious hyperkalemia was minimal in both groups of patients. CONCLUSIONS: Blockade of aldosterone receptors by spironolactone, in addition to standard therapy, substantially reduces the risk of both morbidity and death among patients with severe heart failure.
```

<a id="ev48-own-title"></a>
### EV48-OWN-TITLE

Source: `cache/spironolactone-hfref-mortality/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `10471456`. INFERRED attribution; exact location verified.

Character offset: 321; byte offset: 321. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
The effect of spironolactone on morbidity and mortality in patients with severe heart failure. Randomized Aldactone Evaluation Study Investigators.
```

<a id="ev48-reject-symptom"></a>
### EV48-REJECT-SYMPTOM

Source: `outputs/search_v2/verification/sglt2-hfref-hosp-cvdeath-remainder/sglt2-hfref-hosp-cvdeath-raw/NCT03200860.json`. Rank: `OTHER_TRIAL_REGISTRY`. Record: `NCT03200860`. INFERRED attribution; exact location verified.

Character offset: 7445; byte offset: 7447. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `308c0e45315a127da813cb2ee2d281bfa87c4bf7bea86300c4bb6fa120086359`. Decoded SHA-256: `308c0e45315a127da813cb2ee2d281bfa87c4bf7bea86300c4bb6fa120086359`.

```text
Signs of congestion, such as edema, rales, and/or congestion on chest radiograph
```

<a id="ev49-own-abstract"></a>
### EV49-OWN-ABSTRACT

Source: `cache/spironolactone-hfref-mortality/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `21073363`. INFERRED attribution; exact location verified.

Character offset: 2871; byte offset: 2871. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
BACKGROUND: Mineralocorticoid antagonists improve survival among patients with chronic, severe systolic heart failure and heart failure after myocardial infarction. We evaluated the effects of eplerenone in patients with chronic systolic heart failure and mild symptoms. METHODS: In this randomized, double-blind trial, we randomly assigned 2737 patients with New York Heart Association class II heart failure and an ejection fraction of no more than 35% to receive eplerenone (up to 50 mg daily) or placebo, in addition to recommended therapy. The primary outcome was a composite of death from cardiovascular causes or hospitalization for heart failure. RESULTS: The trial was stopped prematurely, according to prespecified rules, after a median follow-up period of 21 months. The primary outcome occurred in 18.3% of patients in the eplerenone group as compared with 25.9% in the placebo group (hazard ratio, 0.63; 95% confidence interval [CI], 0.54 to 0.74; P<0.001). A total of 12.5% of patients receiving eplerenone and 15.5% of those receiving placebo died (hazard ratio, 0.76; 95% CI, 0.62 to 0.93; P=0.008); 10.8% and 13.5%, respectively, died of cardiovascular causes (hazard ratio, 0.76; 95% CI, 0.61 to 0.94; P=0.01). Hospitalizations for heart failure and for any cause were also reduced with eplerenone. A serum potassium level exceeding 5.5 mmol per liter occurred in 11.8% of patients in the eplerenone group and 7.2% of those in the placebo group (P<0.001). CONCLUSIONS: Eplerenone, as compared with placebo, reduced both the risk of death and the risk of hospitalization among patients with systolic heart failure and mild symptoms. (Funded by Pfizer; ClinicalTrials.gov number, NCT00232180.).
```

<a id="ev49-own-title"></a>
### EV49-OWN-TITLE

Source: `cache/spironolactone-hfref-mortality/records.json#/records/1/title`. Rank: `PRIMARY_REPORT`. Record: `21073363`. INFERRED attribution; exact location verified.

Character offset: 2783; byte offset: 2783. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
Eplerenone in patients with systolic heart failure and mild symptoms.
```

<a id="ev50-own-abstract"></a>
### EV50-OWN-ABSTRACT

Source: `cache/statins-primary-prevention-elderly/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `20404379`. INFERRED attribution; exact location verified.

Character offset: 892; byte offset: 892. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`. Decoded SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`.

```text
BACKGROUND: Randomized data on statins for primary prevention in older persons are limited, and the relative hazard of cardiovascular disease associated with an elevated cholesterol level weakens with advancing age. OBJECTIVE: To assess the efficacy and safety of rosuvastatin in persons 70 years or older. DESIGN: Secondary analysis of JUPITER (Justification for the Use of statins in Prevention: an Intervention Trial Evaluating Rosuvastatin), a randomized, double-blind, placebo-controlled trial. SETTING: 1315 sites in 26 countries randomly assigned participants in JUPITER. PARTICIPANTS: Among the 17 802 participants randomly assigned with low-density lipoprotein (LDL) cholesterol levels less than 3.37 mmol/L (<130 mg/dL) and high-sensitivity C-reactive protein levels of 2.0 mg/L or more without cardiovascular disease, 5695 were 70 years or older. INTERVENTION: Participants were randomly assigned in a 1:1 ratio to receive 20 mg of rosuvastatin daily or placebo. MEASUREMENTS: The primary end point was the occurrence of a first cardiovascular event (myocardial infarction, stroke, arterial revascularization, hospitalization for unstable angina, or death from cardiovascular causes). RESULTS: The 32% of trial participants 70 years or older accrued 49% (n = 194) of the 393 confirmed primary end points. The rates of the primary end point in this age group were 1.22 and 1.99 per 100 person-years of follow-up in the rosuvastatin and placebo groups, respectively (hazard ratio, 0.61 [95% CI, 0.46 to 0.82]; P < 0.001). Corresponding rates of all-cause mortality in this age group were 1.63 and 2.04 (hazard ratio, 0.80 [CI, 0.62 to 1.04]; P = 0.090). Although no significant heterogeneity was found in treatment effects by age, absolute reductions in event rates associated with rosuvastatin were greater in older persons. The relative rate of any serious adverse event among older persons in the rosuvastatin versus placebo group was 1.05 (CI, 0.93 to 1.17). LIMITATION: Effect estimates from this exploratory analysis with age cut-point chosen after trial completion should be viewed in the context of the overall trial results. CONCLUSION: In apparently healthy older persons without hyperlipidemia but with elevated high-sensitivity C-reactive protein levels, rosuvastatin reduces the incidence of major cardiovascular events. PRIMARY FUNDING SOURCE: AstraZeneca.
```

<a id="ev50-own-title"></a>
### EV50-OWN-TITLE

Source: `cache/statins-primary-prevention-elderly/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `20404379`. INFERRED attribution; exact location verified.

Character offset: 678; byte offset: 678. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`. Decoded SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`.

```text
Rosuvastatin for primary prevention in older persons with elevated C-reactive protein and low to average low-density lipoprotein cholesterol levels: exploratory analysis of a randomized trial.
```

<a id="ev50-reject-background"></a>
### EV50-REJECT-BACKGROUND

Source: `outputs/search_v2/verification/omega3-cardiovascular-events-remainder/omega3-cardiovascular-events-raw/ctgov_NCT03192579.json`. Rank: `OTHER_TRIAL_REGISTRY`. Record: `NCT03192579`. INFERRED attribution; exact location verified.

Character offset: 2573; byte offset: 2573. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `1063ba651e3e9c2475e88bafa1a9b644033994ebc3f8691807988367ef3500fb`. Decoded SHA-256: `1063ba651e3e9c2475e88bafa1a9b644033994ebc3f8691807988367ef3500fb`.

```text
The JUPITER (Justification for the Use of Statins in Prevention: an Intervention Trial Evaluating Rosuvastatin ) trial demonstrated
```

<a id="ev50-reject-city"></a>
### EV50-REJECT-CITY

Source: `outputs/search_v2/verification/ticagrelor-vs-clopidogrel-acs/ticagrelor-vs-clopidogrel-acs-raw/NCT00391872.ctgov.json`. Rank: `OTHER_TRIAL_REGISTRY`. Record: `NCT00391872`. INFERRED attribution; exact location verified.

Character offset: 14475; byte offset: 14476. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e2175b2287f3823c2735d323c49f431c6f99531f960749d6b0dc9c9a41e97257`. Decoded SHA-256: `e2175b2287f3823c2735d323c49f431c6f99531f960749d6b0dc9c9a41e97257`.

```text
"city":"Jupiter","state":"Florida"
```

<a id="ev51-own-abstract"></a>
### EV51-OWN-ABSTRACT

Source: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `19717846`. INFERRED attribution; exact location verified.

Character offset: 378; byte offset: 378. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`. Decoded SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`.

```text
BACKGROUND: Ticagrelor is an oral, reversible, direct-acting inhibitor of the adenosine diphosphate receptor P2Y12 that has a more rapid onset and more pronounced platelet inhibition than clopidogrel. METHODS: In this multicenter, double-blind, randomized trial, we compared ticagrelor (180-mg loading dose, 90 mg twice daily thereafter) and clopidogrel (300-to-600-mg loading dose, 75 mg daily thereafter) for the prevention of cardiovascular events in 18,624 patients admitted to the hospital with an acute coronary syndrome, with or without ST-segment elevation. RESULTS: At 12 months, the primary end point--a composite of death from vascular causes, myocardial infarction, or stroke--had occurred in 9.8% of patients receiving ticagrelor as compared with 11.7% of those receiving clopidogrel (hazard ratio, 0.84; 95% confidence interval [CI], 0.77 to 0.92; P<0.001). Predefined hierarchical testing of secondary end points showed significant differences in the rates of other composite end points, as well as myocardial infarction alone (5.8% in the ticagrelor group vs. 6.9% in the clopidogrel group, P=0.005) and death from vascular causes (4.0% vs. 5.1%, P=0.001) but not stroke alone (1.5% vs. 1.3%, P=0.22). The rate of death from any cause was also reduced with ticagrelor (4.5%, vs. 5.9% with clopidogrel; P<0.001). No significant difference in the rates of major bleeding was found between the ticagrelor and clopidogrel groups (11.6% and 11.2%, respectively; P=0.43), but ticagrelor was associated with a higher rate of major bleeding not related to coronary-artery bypass grafting (4.5% vs. 3.8%, P=0.03), including more instances of fatal intracranial bleeding and fewer of fatal bleeding of other types. CONCLUSIONS: In patients who have an acute coronary syndrome with or without ST-segment elevation, treatment with ticagrelor as compared with clopidogrel significantly reduced the rate of death from vascular causes, myocardial infarction, or stroke without an increase in the rate of overall major bleeding but with an increase in the rate of non-procedure-related bleeding. (ClinicalTrials.gov number, NCT00391872.)
```

<a id="ev51-own-title"></a>
### EV51-OWN-TITLE

Source: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/records/0/title`. Rank: `PRIMARY_REPORT`. Record: `19717846`. INFERRED attribution; exact location verified.

Character offset: 287; byte offset: 287. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`. Decoded SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`.

```text
Ticagrelor versus clopidogrel in patients with acute coronary syndromes.
```

<a id="ev52-own-abstract"></a>
### EV52-OWN-ABSTRACT

Source: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/records/29/abstract`. Rank: `PRIMARY_REPORT`. Record: `26376600`. INFERRED attribution; exact location verified.

Character offset: 61639; byte offset: 61723. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`. Decoded SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`.

```text
BACKGROUND: Few data on the relative efficacy and safety of new P2Y12inhibitors such as prasugrel and ticagrelor in Japanese, Taiwanese and South Korean patients with acute coronary syndromes (ACS) exist. METHODS AND RESULTS: The multicenter, double-blind, randomized PHILO trial compared the safety and efficacy of ticagrelor vs. clopidogrel in 801 patients with ACS (Japanese, n=721; Taiwanese, n=35; South Korean, n=44; unknown ethnicity, n=1). All were planned to undergo percutaneous coronary intervention and randomized within 24 h of symptom onset. Primary safety and efficacy endpoints were time to first occurrence of any major bleeding event and to any event from the composite of myocardial infarction, stroke or death from vascular causes, respectively.At 12 months, overall major bleeding occurred in 10.3% of ticagrelor-treated patients and in 6.8% of clopidogrel-treated patients (hazard ratio (HR), 1.54; 95% confidence interval (CI): 0.94-2.53); the composite primary efficacy endpoint occurred in 9.0% and in 6.3% of ticagrelor- and clopidogrel-treated patients, respectively (HR, 1.47; 95% CI: 0.88-2.44). For both analyses, the difference between groups was not statistically significant. CONCLUSIONS: In ACS patients from Japan, Taiwan and South Korea, event rates of primary safety and efficacy endpoints were higher, albeit not significantly, in ticagrelor-treated patients compared with clopidogrel-treated patients. This observation could be explained by the small sample size, imbalance in clinical characteristics and low number of events in the PHILO population.
```

<a id="ev52-own-title"></a>
### EV52-OWN-TITLE

Source: `cache/ticagrelor-vs-clopidogrel-acs/records.json#/records/29/title`. Rank: `PRIMARY_REPORT`. Record: `26376600`. INFERRED attribution; exact location verified.

Character offset: 61470; byte offset: 61554. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`. Decoded SHA-256: `03ec3e516051963fd7103ea8db6f82875398ee70d2c927135c8922b3a06d3ab0`.

```text
Ticagrelor vs. clopidogrel in Japanese, Korean and Taiwanese patients with acute coronary syndrome -- randomized, double-blind, phase III PHILO study.
```

<a id="ev53-own-abstract"></a>
### EV53-OWN-ABSTRACT

Source: `cache/tocilizumab-covid19-mortality/records.json#/records/8/abstract`. Rank: `PRIMARY_REPORT`. Record: `33933206`. INFERRED attribution; exact location verified.

Character offset: 16156; byte offset: 16207. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`. Decoded SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`.

```text
BACKGROUND: In this study, we aimed to evaluate the effects of tocilizumab in adult patients admitted to hospital with COVID-19 with both hypoxia and systemic inflammation. METHODS: This randomised, controlled, open-label, platform trial (Randomised Evaluation of COVID-19 Therapy [RECOVERY]), is assessing several possible treatments in patients hospitalised with COVID-19 in the UK. Those trial participants with hypoxia (oxygen saturation <92% on air or requiring oxygen therapy) and evidence of systemic inflammation (C-reactive protein ≥75 mg/L) were eligible for random assignment in a 1:1 ratio to usual standard of care alone versus usual standard of care plus tocilizumab at a dose of 400 mg-800 mg (depending on weight) given intravenously. A second dose could be given 12-24 h later if the patient's condition had not improved. The primary outcome was 28-day mortality, assessed in the intention-to-treat population. The trial is registered with ISRCTN (50189673) and ClinicalTrials.gov (NCT04381936). FINDINGS: Between April 23, 2020, and Jan 24, 2021, 4116 adults of 21 550 patients enrolled into the RECOVERY trial were included in the assessment of tocilizumab, including 3385 (82%) patients receiving systemic corticosteroids. Overall, 621 (31%) of the 2022 patients allocated tocilizumab and 729 (35%) of the 2094 patients allocated to usual care died within 28 days (rate ratio 0·85; 95% CI 0·76-0·94; p=0·0028). Consistent results were seen in all prespecified subgroups of patients, including those receiving systemic corticosteroids. Patients allocated to tocilizumab were more likely to be discharged from hospital within 28 days (57% vs 50%; rate ratio 1·22; 1·12-1·33; p<0·0001). Among those not receiving invasive mechanical ventilation at baseline, patients allocated tocilizumab were less likely to reach the composite endpoint of invasive mechanical ventilation or death (35% vs 42%; risk ratio 0·84; 95% CI 0·77-0·92; p<0·0001). INTERPRETATION: In hospitalised COVID-19 patients with hypoxia and systemic inflammation, tocilizumab improved survival and other clinical outcomes. These benefits were seen regardless of the amount of respiratory support and were additional to the benefits of systemic corticosteroids. FUNDING: UK Research and Innovation (Medical Research Council) and National Institute of Health Research.
```

<a id="ev53-own-title"></a>
### EV53-OWN-TITLE

Source: `cache/tocilizumab-covid19-mortality/records.json#/records/8/title`. Rank: `PRIMARY_REPORT`. Record: `33933206`. INFERRED attribution; exact location verified.

Character offset: 16010; byte offset: 16061. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`. Decoded SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`.

```text
Tocilizumab in patients admitted to hospital with COVID-19 (RECOVERY): a randomised, controlled, open-label, platform trial.
```

<a id="x-secondary-entry"></a>
### X-SECONDARY-ENTRY

Source: `cache/probiotics-aad-prevention/comparator_fulltext.txt`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 4292; byte offset: 4302. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`. Decoded SHA-256: `58ffaef583553f34f0e6aa525b65418d22deb031395287d642ab9cd82805d957`.

```text
Randomised controlled trials (RCTs) comparing probiotic use (any strain, dose or formulation) to placebo, alternative dose, alternative probiotic strain or no treatment, for the prevention of diarrhoea in adults receiving antibiotic therapy, were eligible for inclusion in this review.
```

<a id="x05-age-epoch"></a>
### X05-AGE-EPOCH

Source: `cache/corticosteroids-covid19-mortality/ft_32678530.txt`. Rank: `PRIMARY_REPORT`. Record: `32678530`. INFERRED attribution; exact location verified.

Character offset: 19297; byte offset: 19306. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `9b432353a5e8d57fce6dfec263d0dfa134412754a1153f9988037528b8bc3db1`. Decoded SHA-256: `9b432353a5e8d57fce6dfec263d0dfa134412754a1153f9988037528b8bc3db1`.

```text
Initially, recruitment was limited to patients who were at least 18 years of age, but the age limit was removed starting on May 9, 2020.
```

<a id="x05-epoch"></a>
### X05-EPOCH

Source: `cache/corticosteroids-covid19-mortality/family_registry.payload.json.gz`. Rank: `REGISTRY`. Record: `NCT04381936`. INFERRED attribution; exact location verified.

Character offset: 98063; byte offset: 98079. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `caa401b955f8ff0b8f1ffbec372501791147742f16882fa0828c6b38e702ac4e`. Decoded SHA-256: `5e274499e507b7c19eae86325665f7d3a709605918f5c4fdb69628dd236e00a1`.

```text
Note: the eligibility criteria has changed from COVID-19 to pneumonia (Influenza
```

<a id="x05-period"></a>
### X05-PERIOD

Source: `cache/corticosteroids-covid19-mortality/ft_32678530.txt`. Rank: `PRIMARY_REPORT`. Record: `32678530`. INFERRED attribution; exact location verified.

Character offset: 27260; byte offset: 27275. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `9b432353a5e8d57fce6dfec263d0dfa134412754a1153f9988037528b8bc3db1`. Decoded SHA-256: `9b432353a5e8d57fce6dfec263d0dfa134412754a1153f9988037528b8bc3db1`.

```text
Of the 11,303 patients who underwent randomization from March 19 to June 8, 2020
```

<a id="x16-criteria"></a>
### X16-CRITERIA

Source: `cache/esketamine-trd-madrs/family_registry.payload.json.gz#/objects/105`. Rank: `REGISTRY`. Record: `NCT02422186`. INFERRED attribution; exact location verified.

Character offset: 51811; byte offset: 51817. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `17b4a13a7f3da42b067354ef79512c9f918fed06cc292f23a825acc955414b3b`. Decoded SHA-256: `ebf0e11ad1297b3c349ebf96c84eb1da92677be77b6664b54c96d0f6e843db09`.

```text
\"Inclusion Criteria:~* At the time of signing the informed consent form (ICF), participant must be a man or woman 65 years of age or older~* At the start of the Screening/prospective observational Phase, participant must meet the Diagnostic and Statistical Manual of Mental Disorders (DSM-5) diagnostic criteria for single-episode major depressive disorder (MDD) \\[if single-episode MDD, the duration must be greater than or equal to (\\>=) 2 years\\] or recurrent MDD, without psychotic features, based upon clinical assessment and confirmed by the Mini-International Neuropsychiatric Interview (MINI)~* At the start of the Screening/Prospective observational Phase, participant must have an Inventory of Depressive Symptomatology-Clinician rated (IDS-C30) total score of greater than or equal to (\\>=) 31~* At the start of the Screening/Prospective observational Phase, participants must have had nonresponse (less than or equal to 25% improvement) to \\>=1 but less than or equal to (\\<=) 8 oral antidepressant treatments taken at adequate dosage and for adequate duration, as assessed using the Massachusetts General Hospital - Antidepressant Treatment Response Questionnaire (MGH-ATRQ) and documented records by medical and pharmacy/prescription records, or a letter from the treating physician, for the current episode of depression~* Participant must be taking one of the oral antidepressant treatment with nonresponse that is documented on the MGH-ATRQ at the start of the screening/prospective observational phase~* The participant's current major depressive episode, depression symptom severity (Week 1 MADRS total score greater than or equal to 24 required) and treatment response to antidepressant treatments used in the current depressive episode (retrospectively assessed) must be confirmed for participation in a clinical study based on a Site-Independent Qualification Assessment~* Participant must be medically stable on the basis of clinical laboratory tests performed in the screening/prospective observational phase~Exclusion Criteria:~* The participant's depressive symptoms have previously demonstrated nonresponse to: Esketamine or ketamine in the current major depressive episode per clinical judgment, or all of the 4 oral antidepressant treatment options available for the double-blind induction Phase (Duloxetine, Escitalopram, Sertraline, and Venlafaxine extended release \\[XR\\]) in the current major depressive episode (based on MGH-ATRQ), or an adequate course of treatment with electroconvulsive therapy (ECT) in the current major depressive episode, defined as at least 7 treatments with unilateral ECT~* Participants who has received vagal nerve stimulation (VNS) or who has received deep brain stimulation (DBS) in the current episode of depression~* Participant has a current or prior DSM-5 diagnosis of a psychotic disorder or MDD with psychosis, bipolar or related disorders (confirmed by the MINI), obsessive compulsive disorder (current episode only), intellectual disability ( intellectual disability \\[DSM-5 diagnostic codes 317, 318.0, 318.1, 318.2, 315.8, and 319\\]), borderline personality disorder, antisocial personality disorder, histrionic personality disorder, or narcissistic personality disorder~* Participant has homicidal ideation/intent, per the Investigator's clinical judgment, or has suicidal ideation with some intent to act within 6 months prior to the start of the Screening/prospective observational Phase, per the Investigator's clinical judgment or based on the Columbia Suicide Severity Rating Scale (C-SSRS) and also includes history of suicidal behavior within the past year prior to start of the screening/prospective observational phase~* Participant has a history (lifetime) of ketamine, phencyclidine (PCP), lysergic acid diethylamide (LSD), or 3, 4-methylenedioxy-methamphetamine (MDMA) hallucinogen-related use disorder\\\\~* Participant has a Mini Mental State Examination (MMSE) \\< 25 or \\<22 for those participants with less than an equivalent of high school education~* Participant has neurodegenerative disorder (eg, Alzheimer's Disease, Vascular dementia, Parkinson's disease with clinical evidence of cognitive impairment) or evidence of mild cognitive impairment (MCI)~* Participant has a history of uncontrolled hypertension; current or past history of significant pulmonary insufficiency/condition;clinically significant ECG abnormalities; current or past history of seizures; clinically significant cardiovascular disorders including cerebral and cardiac vascular disease\"
```

<a id="x19-full-abstract"></a>
### X19-FULL-ABSTRACT

Source: `cache/metformin-pcos-ovulation/records.json#/records/28/abstract`. Rank: `PRIMARY_REPORT`. Record: `19522426`. INFERRED attribution; exact location verified.

Character offset: 85083; byte offset: 85202. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
BACKGROUND: Polycystic ovary syndrome (PCOS) is a common, complex endocrine disorder for women on reproductive age. A high incidence of ovulation failure is observed in PCO women and perhaps linked to insulin resistance related to metabolic features In the last few years some studies assessed hyperinsulinimea and insulin resistance attenuation effects, by insulin sensitizing agents such as metformin, in PCOS women suggesting potential scope for these drugs in CC ovulation induction quality improvement. AIM: Our prospective study aim is to compare the effectiveness of clomifene citrate plus metformin and clomifene citrate plus placebo in women with newly diagnosed polycystic ovary syndrome. METHODS: From February 24 to September 29 (2007), PCOS was explored on women attending the Department of Obstetrics & Gynaecology sterility consultation unit (CHU Hedi Chaker-Sfax) according to the Rotterdam 2003 diagnostic criteria. PCOS patients were randomized to receive, in addition to clomifene citrate treatment, placebo or metformin 850 mg two times a day all ovulatory cycle for three trials maximum. Ovulation detection was done by the E2 serum measurements and ovarian transvaginal ultrasonography' evolution controlling on 7th, 11th and 13th day of the cycle. RESULTS: Within 7 months, 32 PCOS women were recruited in the study and equally allocated to the two groups. Baseline characteristics were similar in metformin group and placebo one. Ovulation was characterized by the presence of at least one mature follicle (> 16 mm), a circulating estradiol concentration in the edge of 150-250 pg and accessory an endometrial depth > 8 mm. The ovulation rate in the metformin group was 62.5% compared with 37.5% in the placebo group, a non-statistically significant (small study population) but important difference (1.66 times). Analyses show a higher mature follicle number and estradiol concentration in metformin group than in the placebo one. Metformin effect was, in our study, his only insulinosensitizer property consequence far away a 'making thinner' or Hyperandrogenism reducing ones. CONCLUSION: The ovulatory response to clomifene can be increased in polycystic ovary syndrome women by decreasing insulin secretion with metformin.
```

<a id="x21-full-abstract"></a>
### X21-FULL-ABSTRACT

Source: `cache/metformin-pcos-ovulation/records.json#/records/101/abstract`. Rank: `PRIMARY_REPORT`. Record: `11172832`. INFERRED attribution; exact location verified.

Character offset: 296467; byte offset: 296846. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`. Decoded SHA-256: `a1ef426822f17f7e0032dc6e33223e6255cc8dd53ff503dc83bcc902f2b8409b`.

```text
OBJECTIVE: To determine whether metformin treatment increases the ovulation and pregnancy rates in response to clomiphene citrate (CC) in women who are resistant to CC alone. DESIGN: Randomized, double-blind, placebo-controlled trial. SETTING: Multicenter environment. PATIENT(S): Anovulatory women with the polycystic ovary syndrome (PCOS) who were resistant to CC. INTERVENTION(S): Participants received placebo or metformin, 500 mg three times daily, for 7 weeks. Information on reproductive steroids, gonadotropins, and oral glucose tolerance testing was obtained at baseline and after treatment. Metformin or placebo was continued and CC treatment was begun at 50 mg daily for 5 days. Serum P level > or =4 ng/mL was considered to indicate ovulation. With ovulation, the daily CC dose was not changed, but with anovulation it was increased by 50 mg for the next cycle. Patients completed the study when they had had six ovulatory cycles, became pregnant, or experienced anovulation while receiving 150 mg of CC. MAIN OUTCOME MEASURE(S): Ovulation and pregnancy rates. RESULT(S): In the metformin and placebo groups, 9 of 12 participants (75%) and 4 of 15 participants (27%) ovulated, and 6 of 11 participants (55%) and 1 of 14 participants (7%) conceived, respectively. Comparisons between the groups were significant. CONCLUSION(S): In anovulatory women with PCOS who are resistant to CC, metformin use significantly increased the ovulation rate and pregnancy rate from CC treatment.
```

<a id="x28-alias"></a>
### X28-ALIAS

Source: `cache/omega3-cardiovascular-events/records.json#/records/25/abstract`. Rank: `PRIMARY_REPORT`. Record: `20929341`. INFERRED attribution; exact location verified.

Character offset: 71836; byte offset: 71880. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`. Decoded SHA-256: `73468a1334f3712ac6cf3c68f887e38054907310ca416b1a8f29e62f41e63ecd`.

```text
the marine n-3 fatty acids eicosapentaenoic acid (EPA) and docosahexaenoic acid (DHA)
```

<a id="x29-factor"></a>
### X29-FACTOR

Source: `cache/omega3-cardiovascular-events/ft_21115589.txt`. Rank: `PRIMARY_REPORT`. Record: `21115589`. INFERRED attribution; exact location verified.

Character offset: 18439; byte offset: 18481. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `b72d4d186492cce21374a97751e627c01bb8a6f7bc253663f1f22519208a0512`. Decoded SHA-256: `b72d4d186492cce21374a97751e627c01bb8a6f7bc253663f1f22519208a0512`.

```text
Included participants were randomly assigned to receive B vitamins alone, omega 3 fatty acids alone, both active treatments, or placebo for both treatments.
```

<a id="x31-outcome"></a>
### X31-OUTCOME

Source: `cache/probiotics-aad-prevention/records.json#/records/104/abstract`. Rank: `PRIMARY_REPORT`. Record: `35727573`. INFERRED attribution; exact location verified.

Character offset: 255598; byte offset: 256312. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
MAIN OUTCOMES AND MEASURES: The primary outcome was AAD, defined as 3 or more loose or watery stools per day
```

<a id="x32-full-abstract"></a>
### X32-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/156/abstract`. Rank: `PRIMARY_REPORT`. Record: `32035998`. INFERRED attribution; exact location verified.

Character offset: 369619; byte offset: 370551. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Antibiotic-associated diarrhoea (AAD) is a side-effect of antibiotic consumption and probiotics have been shown to reduce AAD. METHODS: A multicentre, double-blind, placebo-controlled, randomized trial was conducted to evaluate the role of Lactobacillus casei DN114001 (combined as a drink with two regular yoghurt bacterial strains) in reducing AAD and Clostridioides difficile infection in patients aged over 55 years. The primary outcome was the incidence of AAD during 2 weeks of follow-up. RESULTS: A total of 1127 patients (mean age ± standard deviation: 73.6 ± 10.5) were randomized to the active group (N = 549) or placebo group (N = 577). Both groups were followed up as per protocol. The proportion of patients experiencing AAD during follow-up was 19.3% (106/549) in the probiotic group vs 17.9% (103/577) in the placebo group (unadjusted odds ratio 1.10, 95% confidence interval 0.82-1.49, P = 0.53). CONCLUSIONS: No significant evidence was found of a beneficial effect of the specific probiotic formulation in preventing AAD in this elderly population drawn from a number of different UK hospitals. However, in the UK and in many other healthcare systems there have, in recent years, been many changes in antibiotic stewardship policies, an overall decrease in incidence in C. difficile infection, as well as an increased awareness of infection prevention, and modifications in nursing practice. In light of these factors, it is impossible to conclude definitively from the current trial that the study-specific probiotic formulation has no role in preventing AAD, and it is our view that further trials may be indicated, controlling for these variables.
```

<a id="x32-reference"></a>
### X32-REFERENCE

Source: `cache/probiotics-aad-prevention/diagnostic-2026-09-15/raw/2026-09-15-pmc-goodman-2021-fulltext-xml-2b85e82c055f3dc1.xml`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 140594; byte offset: 140994. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `2b85e82c055f3dc1e39534f7f237f8cebaee0751e791383aaf7dbbfcf3cc33dd`. Decoded SHA-256: `2b85e82c055f3dc1e39534f7f237f8cebaee0751e791383aaf7dbbfcf3cc33dd`.

```text
<ref id="R64"><label>64</label><mixed-citation publication-type="journal"><person-group person-group-type="author"><string-name name-style="western"><surname>Rajkumar</surname><given-names>C</given-names></string-name>, <string-name name-style="western"><surname>Wilks</surname><given-names>M</given-names></string-name>, <string-name name-style="western"><surname>Islam</surname><given-names>J</given-names></string-name>, <etal>et al</etal></person-group>. <article-title>Do probiotics prevent antibiotic-associated diarrhoea? results of a multicentre randomized placebo-controlled trial</article-title>. <source>J Hosp Infect</source><year>2020</year>;<volume>105</volume>:<fpage>280</fpage>–<lpage>8</lpage>. <pub-id pub-id-type="doi">10.1016/j.jhin.2020.01.018</pub-id><pub-id pub-id-type="pmid">32035998</pub-id></mixed-citation></ref>
```

<a id="x33-full-abstract"></a>
### X33-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/328/abstract`. Rank: `PRIMARY_REPORT`. Record: `24772726`. INFERRED attribution; exact location verified.

Character offset: 789902; byte offset: 791991. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIMS: To evaluate the effectiveness, safety and tolerability of a probiotic formulation containing Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12 in the prevention of antibiotic associated diarrhoea (AAD). METHODS AND MATERIAL: A double-blind randomised placebo controlled multicentric trial was conducted in adults who were prescribed a seven-day course of oral antibiotic (either cefadroxil or amoxycillin) for a documented indication. The effectiveness of a 14-day therapy (concomitant with antibiotic course and seven days thereafter) of the probiotic formulation in preventing AAD was evaluated. Safety profile was assessed by monitoring of all treatment emergent adverse events and tolerability on a global well being scale. RESULTS: The incidence of AAD in the probiotic group was 10.8% compared to 15.6% in the placebo group, the difference being statistically non-significant (p = 0.19). The relative risk for AAD was 0.7 with the 95% CI being 0.4 to 1.2. The diarrhoea duration in the probiotic group was two days with an interquartile range of 1- 3 days and was significantly less (p = 0.01) than the placebo group which was four days with an interquartile range of 3 - 5.5 days. Subgroup analysis of subjects with AAD showed that the incidence of severe diarrhoea (watery stools) was 96% in the placebo group (25 out of 26) compared to 31.6% (6 out of 19) in the probiotic group and this difference was significant statistically (p < 0.001). Four mild, non-serious, adverse events were detected (2.0%) in the probiotic group but there were none in the placebo group. CONCLUSION: This randomised controlled trial shows that prophylactic administration of the probiotic formulation containing Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12, did not effectively lower the incidence of AAD in adults. However, compared to placebo the duration of diarrhoea in the probiotic group was significantly reduced. Its tolerability and safety profile were good.
```

<a id="x34-outcome"></a>
### X34-OUTCOME

Source: `cache/probiotics-aad-prevention/records.json#/records/333/abstract`. Rank: `PRIMARY_REPORT`. Record: `23932219`. INFERRED attribution; exact location verified.

Character offset: 804142; byte offset: 806262. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
The primary outcomes were occurrence of AAD within 8 weeks and C difficile diarrhoea (CDD) within 12 weeks of recruitment.
```

<a id="x35-full-abstract"></a>
### X35-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/357/abstract`. Rank: `PRIMARY_REPORT`. Record: `18701826`. INFERRED attribution; exact location verified.

Character offset: 859146; byte offset: 861328. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
AIM: To determine the efficacy of a combination of Bifidobacterium longum PL03, Lactobacillus rhamnosus KL53A and Lactobacillus plantarum PL02 for the prevention of antibiotic-associated diarrhea in children. METHODS: Seventy-eight children (age: 5 months to 16 years) with otitis media, and/or respiratory tract infections, and/or urinary tract infections were enrolled in a double-blind randomized control trial in which they received standard antibiotic treatment plus a food supplement containing 10(8) colony-forming units of B. longum, L. rhamnosus and L. plantarum (n = 40) or a placebo (n = 38) orally twice daily for the duration of antibiotic treatment. RESULTS: Patients receiving probiotics had a similar rate of diarrhea (> or =3 loose or watery stools/day for > or =48 h occurring during or up to 2 weeks after the antibiotic therapy) as those receiving placebo (relative risk 0.5, 95% CI 0.06-3.5). The mean number of stools per day was significantly lower in the experimental group (mean difference -0.3 stool/day, 95% CI -0.5 to -0.07). No adverse events were reported. CONCLUSION: The administration of the 3 probiotics did not significantly alter the rate of diarrhea, although it reduced the frequency of stools per day. As the overall frequency of diarrhea was surprisingly low, these results should be interpreted with caution.
```

<a id="x36-full-abstract"></a>
### X36-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/359/abstract`. Rank: `PRIMARY_REPORT`. Record: `18410562`. INFERRED attribution; exact location verified.

Character offset: 863531; byte offset: 865713. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Convincing evidence that probiotic administration can lower the risk of antibiotic-associated diarrhoea is limited to certain micro-organisms. AIM: To determine the efficacy of administration of Lactobacillus rhamnosus (strains E/N, Oxy and Pen) for the prevention of antibiotic-associated diarrhoea in children. METHODS: Children (aged 3 months to 14 years) with common infections were enrolled in a double-blind, randomized, placebo-controlled trial in which they received standard antibiotic treatment plus 2 x 10(10) colony forming units of a probiotic (n = 120) or a placebo (n = 120), administered orally twice daily throughout antibiotic treatment. Analyses were by intention to treat. RESULTS: Any diarrhoea (>or=3 loose or watery stools/day for >or=48 h occurring during or up to 2 weeks after the antibiotic therapy) occurred in nine (7.5%) patients in the probiotic group and in 20 (17%) patients in the placebo group (relative risk, RR 0.45, 95% confidence interval, CI 0.2-0.9). Three (2.5%) children in the probiotic group developed AAD (diarrhoea caused by Clostridium difficile or otherwise unexplained diarrhoea) compared to nine (7.5%) in the placebo group (RR 0.33, 95% CI 0.1-1.06). No adverse events were observed. CONCLUSION: Administration of L. rhamnosus (strains E/N, Oxy and Pen) to children receiving antibiotics reduced the risk of any diarrhoea, as defined in this study.
```

<a id="x37-full-abstract"></a>
### X37-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/375/abstract`. Rank: `PRIMARY_REPORT`. Record: `15740542`. INFERRED attribution; exact location verified.

Character offset: 897096; byte offset: 899278. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Co-treatment with Saccharomyces boulardii appears to lower the risk of antibiotic-associated diarrhoea in adults receiving broad-spectrum antibiotics. AIM: To determine whether S. boulardii prevents antibiotic-associated diarrhoea in children. METHODS: A total of 269 children (aged 6 months to 14 years) with otitis media and/or respiratory tract infections were enrolled in a double-blind, randomized placebo-controlled trial in which they received standard antibiotic treatment plus 250 mg of S. boulardii (experimental group, n = 132) or a placebo (control group, n = 137) orally twice daily for the duration of antibiotic treatment. Analyses were based on allocated treatment and included data from 246 children. RESULTS: Patients receiving S. boulardii had a lower prevalence of diarrhoea (> or =3 loose or watery stools/day for > or =48 h occurring during or up to 2 weeks after the antibiotic therapy) than those receiving placebo [nine of 119 (8%) vs. 29 of 127 (23%), relative risk: 0.3, 95% confidence interval: 0.2-0.7]. S. boulardii also reduced the risk of antibiotic-associated diarrhoea (diarrhoea caused by Clostridium difficile or otherwise unexplained diarrhoea) compared with placebo [four of 119 (3.4%) vs. 22 of 127 (17.3%), relative risk: 0.2; 95% confidence interval: 0.07-0.5]. No adverse events were observed. CONCLUSION: This is the first randomized-controlled trial evidence that S. boulardii effectively reduces the risk of antibiotic-associated diarrhoea in children.
```

<a id="x38-full-abstract"></a>
### X38-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/384/abstract`. Rank: `PRIMARY_REPORT`. Record: `11560298`. INFERRED attribution; exact location verified.

Character offset: 917673; byte offset: 919855. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
OBJECTIVES: To assess the efficacy of Lactobacillus GG in preventing antibiotic-associated diarrhea (AAD) in adults and, secondarily, to assess the effect of coadministered Lactobacillus GG on the number of tests performed to determine the cause of diarrhea. PATIENTS AND METHODS: In this prospective, randomized, double-blind, placebo-controlled trial conducted from July 1998 to October 1999, 302 hospitalized patients receiving antibiotics were randomized to receive Lactobacillus GG, 20 x 10(9) CFU/d, or placebo for 14 days. Subjects recorded the number of stools and their consistency daily for 21 days. The primary outcome was the proportion of patients who developed diarrhea in the first 21 days after enrollment. Weekly telephone follow-up was also performed. Results were analyzed in an intention-to-treat fashion. RESULTS: Diarrhea developed in 39 (29.3%) of 133 patients randomized to receive Lactobacillus GG and in 40 (29.9%) of 134 patients randomized to receive placebo (P=.93). No additional difference in the rate of occurrence of diarrhea was found between treatment and placebo patients in a subgroup analysis of those treated with beta-lactam vs non-beta-lactam antibiotics. Too few patients had stool cultures, additional laboratory tests for diarrhea, or a positive diagnosis of Clostridium difficile infection to assess between-group differences. CONCLUSION: Lactobacillus GG in a dose of 20 x 10(9) CFU/d did not reduce the rate of occurrence of diarrhea in this sample of 267 adult patients taking antibiotics initially administered in the hospital setting.
```

<a id="x39-full-abstract"></a>
### X39-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/400/abstract`. Rank: `PRIMARY_REPORT`. Record: `7872284`. INFERRED attribution; exact location verified.

Character offset: 953046; byte offset: 955228. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
OBJECTIVES: To determine the safety and efficacy of a new preventive agent for antibiotic-associated diarrhea (AAD) in patients receiving at least one beta-lactam antibiotic. METHODS: A double-blinded, placebo-controlled, parallel group study was performed in a high-risk group of hospitalized patients receiving a new prescription for a beta-lactam antibiotic and having no acute diarrhea on enrollment. Lyophilized Saccharomyces boulardii or placebo (1 g/day) was given within 72 h of the start of the antibiotic(s) and continued until 3 days after the antibiotic was discontinued, after which the patients were followed for 7 wk. RESULTS: Of the 193 eligible patients, significantly fewer, 7/97 (7.2%), patients receiving S. boulardii developed AAD compared with 14/96 (14.6%) on placebo (p = 0.02). The efficacy of S. boulardii for the prevention of AAD was 51%. Using a multivariate model to adjust for two independent risk factors for AAD (age and days of cephalosporin use), the adjusted relative risk was significantly protective for S. boulardii (RR = 0.29, 95% CI = 0.08, 0.98). CONCLUSION: The prophylactic use of S. boulardii given with a beta-lactam antibiotic resulted in a significant reduction of AAD with no serious adverse reactions.
```

<a id="x39-reference"></a>
### X39-REFERENCE

Source: `cache/probiotics-aad-prevention/diagnostic-2026-09-15/raw/2026-09-15-pmc-goodman-2021-fulltext-xml-2b85e82c055f3dc1.xml`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 136393; byte offset: 136783. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `2b85e82c055f3dc1e39534f7f237f8cebaee0751e791383aaf7dbbfcf3cc33dd`. Decoded SHA-256: `2b85e82c055f3dc1e39534f7f237f8cebaee0751e791383aaf7dbbfcf3cc33dd`.

```text
<ref id="R59"><label>59</label><mixed-citation publication-type="journal"><person-group person-group-type="author"><string-name name-style="western"><surname>McFarland</surname><given-names>LV</given-names></string-name>, <string-name name-style="western"><surname>Surawicz</surname><given-names>CM</given-names></string-name>, <string-name name-style="western"><surname>Greenberg</surname><given-names>RN</given-names></string-name>, <etal>et al</etal></person-group>. <article-title>Prevention of beta-lactam-associated diarrhea by Saccharomyces boulardii compared with placebo</article-title>. <source>Am J Gastroenterol</source><year>1995</year>;<volume>90</volume>:<fpage>439</fpage>–<lpage>48</lpage>.<pub-id pub-id-type="pmid">7872284</pub-id></mixed-citation></ref>
```

<a id="x40-full-abstract"></a>
### X40-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/420/abstract`. Rank: `PRIMARY_REPORT`. Record: `21165295`. INFERRED attribution; exact location verified.

Character offset: 995898; byte offset: 998126. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
Antibiotic-associated diarrhea (AAD) is a common complication of antibiotic use. There is growing interest in probiotics for the treatment of AAD and Clostridium difficile infection because of the wide availability of probiotics. The aim of this multicenter, randomized, placebo-controlled, double-blind trial was to assess the efficacy of probiotic Lactobacillus (Lacidofil® cap) for the prevention of AAD in adults. From September 2008 to November 2009, a total of 214 patients with respiratory tract infection who had begun receiving antibiotics were randomized to receive Lactobacillus (Lacidofil® cap) or placebo for 14 days. Patients recorded bowel frequency and stool consistency daily for 14 days. The primary outcome was the proportion of patients who developed AAD within 14 days of enrollment. AAD developed in 4 (3.9%) of 103 patients in the Lactobacillus group and in 8 (7.2%) of 111 patients in the placebo group (P=0.44). However, the Lactobacillus group showed lower change in bowel frequency and consistency (50/103, 48.5%) than the placebo group (35/111, 31.5%) (P=0.01). Although the Lacidofil® cap does not reduce the rate of occurrence of AAD in adult patients with respiratory tract infection who have taken antibiotics, the Lactobacillus group maintains their bowel habits to a greater extent than the placebo group.
```

<a id="x41-full-abstract"></a>
### X41-FULL-ABSTRACT

Source: `cache/probiotics-aad-prevention/records.json#/records/430/abstract`. Rank: `PRIMARY_REPORT`. Record: `18026577`. INFERRED attribution; exact location verified.

Character offset: 1011025; byte offset: 1013256. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`. Decoded SHA-256: `ed2f696e6c9a100fb82d745f7af816e8f3cb05a9318caa1dd4cf2f60c75204ac`.

```text
BACKGROUND: Antibiotic-associated diarrhea is an important problem in hospitalized patients. The use of probiotics is gaining interest in the scientific community as a potential measure to prevent this complication. The main objective of the present study was to assess the efficacy and safety of a fermented milk combining Lactobacillus acidophilus and Lactobacillus casei that is widely available in Canada, in the prevention of antibiotic-associated diarrhea. METHODS: In this double-blind, randomized study, hospitalized patients were randomly assigned to receive either a lactobacilli-fermented milk or a placebo on a daily basis. RESULTS: Among 89 randomized patients, antibiotic-associated diarrhea occurred in seven of 44 patients (15.9%) in the lactobacilli group and in 16 of 45 patients (35.6%) in the placebo group (OR 0.34, 95% CI 0.125 to 0.944; P=0.05). The median hospitalization duration was eight days in the lactobacilli group, compared with 10 days in the placebo group (P=0.09). Overall, the lactobacilli-fermented milk was well tolerated. CONCLUSION: The daily administration of a lactobacilli-fermented milk was safe and effective in the prevention of antibiotic-associated diarrhea in hospitalized patients.
```

<a id="x41-reference"></a>
### X41-REFERENCE

Source: `cache/probiotics-aad-prevention/diagnostic-2026-09-15/raw/2026-09-15-pmc-goodman-2021-fulltext-xml-2b85e82c055f3dc1.xml`. Rank: `SECONDARY_REVIEW`. Record: `None`. INFERRED attribution; exact location verified.

Character offset: 121876; byte offset: 122225. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `2b85e82c055f3dc1e39534f7f237f8cebaee0751e791383aaf7dbbfcf3cc33dd`. Decoded SHA-256: `2b85e82c055f3dc1e39534f7f237f8cebaee0751e791383aaf7dbbfcf3cc33dd`.

```text
<ref id="R42"><label>42</label><mixed-citation publication-type="journal"><person-group person-group-type="author"><string-name name-style="western"><surname>Beausoleil</surname><given-names>M</given-names></string-name>, <string-name name-style="western"><surname>Fortier</surname><given-names>N</given-names></string-name>, <string-name name-style="western"><surname>Guénette</surname><given-names>S</given-names></string-name>, <etal>et al</etal></person-group>. <article-title>Effect of a fermented milk combining Lactobacillus acidophilus Cl1285 and Lactobacillus casei in the prevention of antibiotic-associated diarrhea: a randomized, double-blind, placebo-controlled trial</article-title>. <source>Can J Gastroenterol</source><year>2007</year>;<volume>21</volume>:<fpage>732</fpage>–<lpage>6</lpage>. <pub-id pub-id-type="doi">10.1155/2007/720205</pub-id><pub-id pub-id-type="pmid">18026577</pub-id><pub-id pub-id-type="pmcid">PMC2658588</pub-id></mixed-citation></ref>
```

<a id="x44-entry"></a>
### X44-ENTRY

Source: `cache/semaglutide-obesity-mace/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `37952131`. INFERRED attribution; exact location verified.

Character offset: 2262; byte offset: 2265. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`. Decoded SHA-256: `5ada8141d3d2d9d5e5a22fcd7e4bfbd07b08f435385464fa7fe82812cc249d4c`.

```text
In patients with preexisting cardiovascular disease and overweight or obesity but without diabetes
```

<a id="x46-entry"></a>
### X46-ENTRY

Source: `cache/sglt2-primary-prevention-hf/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `26378978`. INFERRED attribution; exact location verified.

Character offset: 4977; byte offset: 4977. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`. Decoded SHA-256: `8aa92759095be6b9178838fc90b95cbb810a32e952d40147920dcda9eab26c22`.

```text
Patients with type 2 diabetes at high risk for cardiovascular events who received empagliflozin, as compared with placebo
```

<a id="x48-full-abstract"></a>
### X48-FULL-ABSTRACT

Source: `cache/spironolactone-hfref-mortality/records.json#/records/0/abstract`. Rank: `PRIMARY_REPORT`. Record: `10471456`. INFERRED attribution; exact location verified.

Character offset: 487; byte offset: 487. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
BACKGROUND AND METHODS: Aldosterone is important in the pathophysiology of heart failure. In a doubleblind study, we enrolled 1663 patients who had severe heart failure and a left ventricular ejection fraction of no more than 35 percent and who were being treated with an angiotensin-converting-enzyme inhibitor, a loop diuretic, and in most cases digoxin. A total of 822 patients were randomly assigned to receive 25 mg of spironolactone daily, and 841 to receive placebo. The primary end point was death from all causes. RESULTS: The trial was discontinued early, after a mean follow-up period of 24 months, because an interim analysis determined that spironolactone was efficacious. There were 386 deaths in the placebo group (46 percent) and 284 in the spironolactone group (35 percent; relative risk of death, 0.70; 95 percent confidence interval, 0.60 to 0.82; P<0.001). This 30 percent reduction in the risk of death among patients in the spironolactone group was attributed to a lower risk of both death from progressive heart failure and sudden death from cardiac causes. The frequency of hospitalization for worsening heart failure was 35 percent lower in the spironolactone group than in the placebo group (relative risk of hospitalization, 0.65; 95 percent confidence interval, 0.54 to 0.77; P<0.001). In addition, patients who received spironolactone had a significant improvement in the symptoms of heart failure, as assessed on the basis of the New York Heart Association functional class (P<0.001). Gynecomastia or breast pain was reported in 10 percent of men who were treated with spironolactone, as compared with 1 percent of men in the placebo group (P<0.001). The incidence of serious hyperkalemia was minimal in both groups of patients. CONCLUSIONS: Blockade of aldosterone receptors by spironolactone, in addition to standard therapy, substantially reduces the risk of both morbidity and death among patients with severe heart failure.
```

<a id="x49-criteria"></a>
### X49-CRITERIA

Source: `cache/spironolactone-hfref-mortality/family_registry.payload.json.gz#/objects/2`. Rank: `REGISTRY`. Record: `NCT00232180`. INFERRED attribution; exact location verified.

Character offset: 834; byte offset: 834. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `f2ccfd9c06f9c703e3b6a1a9b3294bd4ff95dbc2635ac0b3c45f745f95e8559b`. Decoded SHA-256: `28abd05e0ab36eef8cd9934c203bd95fa2865b9680303edc12b9614b11fecc62`.

```text
\"Inclusion Criteria:~* History (Hx) of chronic systolic heart failure of ischemic or non-ischemic etiology of at least 4 weeks duration; Currently, New York Heart Association (NYHA) functional Class II and on optimal dose, or maximally tolerated dose of standard heart failure medicines (advisable to include ACE-I/ARBs; beta-blockers) and diuretics if indicated for fluid overload. Should have participated in the double-blind phase of the EMPHASIS-HF trial~Exclusion Criteria:~* Severe chronic systolic heart failure symptomatic at rest despite optimal medical therapy; estimated glomerular filtration rate (eGFR) \\<30 ml/min/1.73m2.\"
```

<a id="x49-nct"></a>
### X49-NCT

Source: `cache/spironolactone-hfref-mortality/records.json#/records/1/abstract`. Rank: `PRIMARY_REPORT`. Record: `21073363`. INFERRED attribution; exact location verified.

Character offset: 4540; byte offset: 4540. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`. Decoded SHA-256: `e901036c243cd53f5c1b4644dc0e5d003caf8e540c1d13514856f1096a0cf461`.

```text
ClinicalTrials.gov number, NCT00232180.
```

<a id="x50-full-abstract"></a>
### X50-FULL-ABSTRACT

Source: `cache/statins-primary-prevention-elderly/records.json#/records/0/abstract`. Rank: `SECONDARY_TRIAL_REPORT`. Record: `20404379`. INFERRED attribution; exact location verified.

Character offset: 892; byte offset: 892. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`. Decoded SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`.

```text
BACKGROUND: Randomized data on statins for primary prevention in older persons are limited, and the relative hazard of cardiovascular disease associated with an elevated cholesterol level weakens with advancing age. OBJECTIVE: To assess the efficacy and safety of rosuvastatin in persons 70 years or older. DESIGN: Secondary analysis of JUPITER (Justification for the Use of statins in Prevention: an Intervention Trial Evaluating Rosuvastatin), a randomized, double-blind, placebo-controlled trial. SETTING: 1315 sites in 26 countries randomly assigned participants in JUPITER. PARTICIPANTS: Among the 17 802 participants randomly assigned with low-density lipoprotein (LDL) cholesterol levels less than 3.37 mmol/L (<130 mg/dL) and high-sensitivity C-reactive protein levels of 2.0 mg/L or more without cardiovascular disease, 5695 were 70 years or older. INTERVENTION: Participants were randomly assigned in a 1:1 ratio to receive 20 mg of rosuvastatin daily or placebo. MEASUREMENTS: The primary end point was the occurrence of a first cardiovascular event (myocardial infarction, stroke, arterial revascularization, hospitalization for unstable angina, or death from cardiovascular causes). RESULTS: The 32% of trial participants 70 years or older accrued 49% (n = 194) of the 393 confirmed primary end points. The rates of the primary end point in this age group were 1.22 and 1.99 per 100 person-years of follow-up in the rosuvastatin and placebo groups, respectively (hazard ratio, 0.61 [95% CI, 0.46 to 0.82]; P < 0.001). Corresponding rates of all-cause mortality in this age group were 1.63 and 2.04 (hazard ratio, 0.80 [CI, 0.62 to 1.04]; P = 0.090). Although no significant heterogeneity was found in treatment effects by age, absolute reductions in event rates associated with rosuvastatin were greater in older persons. The relative rate of any serious adverse event among older persons in the rosuvastatin versus placebo group was 1.05 (CI, 0.93 to 1.17). LIMITATION: Effect estimates from this exploratory analysis with age cut-point chosen after trial completion should be viewed in the context of the overall trial results. CONCLUSION: In apparently healthy older persons without hyperlipidemia but with elevated high-sensitivity C-reactive protein levels, rosuvastatin reduces the incidence of major cardiovascular events. PRIMARY FUNDING SOURCE: AstraZeneca.
```

<a id="x50-subgroup"></a>
### X50-SUBGROUP

Source: `cache/statins-primary-prevention-elderly/records.json#/records/0/abstract`. Rank: `SECONDARY_TRIAL_REPORT`. Record: `20404379`. INFERRED attribution; exact location verified.

Character offset: 2876; byte offset: 2876. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`. Decoded SHA-256: `fb0836f35450fce1cc87ba1a1bc3b38c7aea89f7d16403166e04e1c1e0244552`.

```text
Effect estimates from this exploratory analysis with age cut-point chosen after trial completion should be viewed in the context of the overall trial results.
```

<a id="x53-epoch"></a>
### X53-EPOCH

Source: `cache/tocilizumab-covid19-mortality/family_registry.payload.json.gz`. Rank: `REGISTRY`. Record: `NCT04381936`. INFERRED attribution; exact location verified.

Character offset: 123920; byte offset: 123964. zero-based Unicode characters in gzip-decompressed UTF-8 file; no newline normalization.

Document SHA-256: `3b060626ddf17022a199c37759c35855266499eae64b2cc1077f63b3a5141a19`. Decoded SHA-256: `258afc3544209a5a5b32bcbe6e61d2a178d43d642bc5dfcfcd85dfb1dfef7d34`.

```text
Note: the eligibility criteria has changed from COVID-19 to pneumonia (Influenza
```

<a id="x53-period"></a>
### X53-PERIOD

Source: `cache/tocilizumab-covid19-mortality/records.json#/records/8/abstract`. Rank: `PRIMARY_REPORT`. Record: `33933206`. INFERRED attribution; exact location verified.

Character offset: 17179; byte offset: 17232. zero-based Unicode characters in UTF-8 file; no newline normalization.

Document SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`. Decoded SHA-256: `678bac27447a937c128fed9ebb6b2bbd7ebe3f119365dc9af4456947433e5da2`.

```text
Between April 23, 2020, and Jan 24, 2021
```

