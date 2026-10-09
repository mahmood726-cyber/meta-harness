# V14 question -- the eligibility axis of each active topic (k-gap, 2026-10-10)

Writer: scripts/g1_v14_axis_question.py. Every quotation below is VERBATIM from protocols/<slug>.md.

## 1. GLP-1 (glp1-ra-mace-t2d): the B-prime sentence and its disclosure

protocols/glp1-ra-mace-t2d.md line 78:

> - **Eligibility (B-prime).** Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes **in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained** -- preferably with blinded or independent adjudication. Eligibility does **not** depend on the direction, statistical significance or published availability of the MACE result. **If MACE was measured but the result is unavailable, the trial is retained and the result is pursued** through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held.

protocols/glp1-ra-mace-t2d.md line 79:

> - **Alternatives disclosed.** Under **A** (the literal registered rule: outcome not an eligibility axis) the universe would additionally include SUSTAIN-1, PIONEER-1, AWARD-8, LEAD-2, Harmony 1, AMPLITUDE-M, GetGoal-P, GetGoal-L, GetGoal-Mono, FREEDOM-1 and others, entering screening and exiting on outcome availability. Under **B** ("large cardiovascular outcome trials") the universe would be the eight seeded CVOTs, with "large" and "CVOT" undefined. B-prime yields the intended small universe by a stated, executable criterion (prospective systematic ascertainment of the outcome), not by a label or by which results are convenient. FLOW (semaglutide, T2D with CKD; MACE prospectively adjudicated) is eligible under B-prime; FREEDOM-CVO (ITCA 650) is eligible under B-prime on the intervention-class strand that admits continuous delivery (see the class-boundary decision: `CONVENTIONAL_GLP1RA` primary strand, `GLP1RA_ANY_DELIVERY` rendered alongside); ELIXA (lixisenatide; 4-point primary, 3-point components prospectively ascertained) is eligible, its 3-point result pursued from the primary supplement or regulatory record, never from a secondary meta-analysis.

**The question.** The FDA 2008 guidance made sponsors of glycaemic phase 3 programmes prospectively adjudicate MACE as a safety endpoint, so many glycaemic RCTs (SUSTAIN-1, PIONEER-1, AWARD-8, ...) literally satisfy '3-point MACE ... prospectively specified and systematically ascertained'. The disclosure line names exactly those trials as OUTSIDE ('B-prime yields the intended small universe'). Which governs: (i) the literal criterion -- every trial with prospectively adjudicated MACE, safety-adjudication included; or (ii) the intended universe -- MACE as a prespecified efficacy/primary or key secondary endpoint of a CV outcome trial? Until answered, no GLP-1 concept record is screened to eligible. The first dual run (PICO-only prompt, ~1,124 calls) is VOID (outputs/k_gap/concept/glp1-ra-mace-t2d.dual.VOID_pico_only_prompt.json) and decides nothing.

## 2. Every active topic: axis sentence, literal-rule universe, proposed split

Literal universe = concept-search records NOT already held that the regex screen INCLUDES under the protocol's own P/I/C/design rule (with the fixed-rule overlay). It counts records, not trials. Topics marked 'pending' are still in the search queue; Europe PMC and EU CTR are being re-paged for the first 8 topics, so their counts can rise (the recall limit is recorded per source as `recall_limit`).

| topic | split | new records | literal-rule includes | search state |
|---|---|---|---|---|
| doac-vte-recurrence | a (at risk: phase-2 / biomarker trials admitted) | 5895 | 87 | EUROPEPMC TRUNCATED; EUCTR FIRST_PAGE_ONLY |
| noac-vs-warfarin-af-stroke | b (moved 9 Oct: dual screen admitted 41 incl. cognition / plaque / biomarker trials) | 6387 | 275 | EUROPEPMC TRUNCATED; EUCTR FIRST_PAGE_ONLY |
| tranexamic-acid-pph | a | pending | pending | queued |
| corticosteroids-covid19-mortality | a | pending | pending | queued |
| colchicine-recurrent-pericarditis | a | pending | pending | queued |
| melatonin-primary-insomnia-sol | a | pending | pending | queued |
| esketamine-trd-madrs | a | 1358 | 5 | EUCTR FIRST_PAGE_ONLY |
| semaglutide-obesity-weight | a | 9184 | 75 | EUROPEPMC TRUNCATED |
| glp1-ra-mace-t2d | b (B-prime amendment) | 7282 | 635 | EUROPEPMC TRUNCATED; EUCTR FIRST_PAGE_ONLY |
| dpp4-mace-t2d | b | 6674 | 530 | EUROPEPMC TRUNCATED; EUCTR FIRST_PAGE_ONLY |
| semaglutide-obesity-mace | b | 9111 | 19 | all COMPLETE |
| sglt2-hfref-hosp-cvdeath | b | 18277 | 181 | all COMPLETE |
| dapagliflozin-hfpef-hosp | b | 5113 | 12 | EUROPEPMC TRUNCATED; EUCTR FIRST_PAGE_ONLY |
| empagliflozin-hfpef-hosp | b | 5151 | 11 | EUROPEPMC TRUNCATED; EUCTR FIRST_PAGE_ONLY |
| finerenone-ckd-t2d-renal | b | 2029 | 34 | EUCTR FIRST_PAGE_ONLY |
| spironolactone-hfref-mortality | b | pending | pending | queued |
| denosumab-vertebral-fracture | b | 5043 | 35 | EUCTR FIRST_PAGE_ONLY |
| iv-iron-hfref-hosp | b | pending | pending | queued |
| sacubitril-valsartan-hfref | b | pending | pending | queued |
| sglt2-ckd-progression | b | pending | pending | queued |
| sglt2-primary-prevention-hf | b | pending | pending | queued |
| statins-primary-prevention-elderly | b | pending | pending | queued |

**Proposed rule.** (a) topics: a recorded dual codex screen with the protocol's eligibility text quoted verbatim decides eligibility. (b) topics: the literal-rule universe is reported here and NOT screened to eligible -- each protocol says eligibility is not on the outcome axis, so read literally every trial of the drug in the population is eligible, and 'eligible, not pooled' would flood with trials that never measured the outcome (the defect B-prime fixed for GLP-1). The Captain decides per topic: a B-prime-style amendment, or the literal universe. dpp4 is the clearest case: its search is UID queries for the 5 DPP-4 CVOTs, the same search-vs-eligibility mismatch B-prime fixed for GLP-1, and it has no amendment.

## 3. The axis paragraph of each protocol, verbatim

**doac-vte-recurrence**

> Eligibility is NOT on the outcome axis. Whether an eligible acute-treatment trial
> reports recurrent VTE, and whether it reports arm counts or only an effect plus
> confidence interval, is recorded at extraction. A published HR/RR plus 95% CI is
> a poolable input.

**noac-vs-warfarin-af-stroke**

> **Eligibility is NOT on the outcome axis.** Whether a trial reports stroke or systemic
> embolism, or gives a 2x2 table versus only an effect+CI, is recorded as target-result
> status at extraction - never as an exclusion. A published effect + CI is a poolable
> input when the fixed extractor can corroborate it from the abstract.

**tranexamic-acid-pph**

> Eligibility is NOT on the outcome axis. Whether a trial reports death due to bleeding,
> or gives arm counts versus only an effect plus CI, is recorded as target-result status
> at extraction and is never an exclusion. A published effect plus 95% CI is a poolable
> input.

**corticosteroids-covid19-mortality**

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> 28-day all-cause mortality in an abstract-extractable form is recorded as
> target-result status at extraction, never as an exclusion. A published effect
> plus 95% CI is a poolable input.

**colchicine-recurrent-pericarditis**

> **Eligibility is NOT on the outcome axis.** Whether a trial reports the recurrence
> outcome, or gives a 2×2 vs only an effect+CI, is recorded as *target-result status* at
> extraction — never as an exclusion. A published effect + 95% CI is a poolable input.

**melatonin-primary-insomnia-sol**

(no 'NOT on the outcome axis' sentence in this protocol)

**esketamine-trd-madrs**

(no 'NOT on the outcome axis' sentence in this protocol)

**semaglutide-obesity-weight**

(no 'NOT on the outcome axis' sentence in this protocol)

**glp1-ra-mace-t2d**

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives
> a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as
> an exclusion. A published effect + 95% CI is a poolable input.

**dpp4-mace-t2d**

> Eligibility is NOT on the outcome axis. Whether an eligible trial reports 3-point
> MACE, and whether it reports arm counts or only an effect plus confidence interval,
> is recorded at extraction. A published effect plus 95% CI is a poolable input.

**semaglutide-obesity-mace**

> **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives
> a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as
> an exclusion. A published effect + 95% CI is a poolable input.

**sglt2-hfref-hosp-cvdeath**

> **Eligibility is NOT on the outcome axis.** Whether a trial reports the composite
> endpoint, or gives a 2x2 vs only an effect+CI, is recorded as *target-result status* at
> extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

**dapagliflozin-hfpef-hosp**

(no 'NOT on the outcome axis' sentence in this protocol)

**empagliflozin-hfpef-hosp**

(no 'NOT on the outcome axis' sentence in this protocol)

**finerenone-ckd-t2d-renal**

> Eligibility is NOT on the outcome axis. Whether an eligible trial reports the kidney
> composite, and whether it reports arm counts or only an effect plus confidence interval,
> is recorded at extraction. A published effect plus 95% CI is a poolable input.

**spironolactone-hfref-mortality**

> **Eligibility is NOT on the outcome axis.** Whether a trial reports all-cause
> mortality, or gives a 2x2 vs only an effect+CI, is recorded as *target-result status*
> at extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

**denosumab-vertebral-fracture**

(no 'NOT on the outcome axis' sentence in this protocol)

**iv-iron-hfref-hosp**

> Eligibility is NOT on the outcome axis. Whether a trial reports heart-failure
> hospitalization, or gives a 2x2 vs only an effect+CI, is recorded as target-result
> status at extraction - never as an exclusion. A published effect + 95% CI is a
> poolable input. Composite cardiovascular-death/heart-failure-hospitalization effects
> are not treated as standalone heart-failure hospitalization for the primary outcome.

**sacubitril-valsartan-hfref**

(no 'NOT on the outcome axis' sentence in this protocol)

**sglt2-ckd-progression**

> Eligibility is NOT on the outcome axis. Whether an eligible trial reports CKD
> progression, and whether it reports arm counts or only an effect plus confidence
> interval, is recorded at extraction. A published effect plus 95% CI is a poolable
> input.

**sglt2-primary-prevention-hf**

> Eligibility is NOT on the outcome axis. Whether an eligible trial reports HHF,
> and whether it reports arm counts or only an effect plus confidence interval, is
> recorded at extraction. A published HR plus 95% CI is a poolable input; crude
> event counts from CT.gov or labels are not substituted for HRs.

**statins-primary-prevention-elderly**

> **Eligibility is NOT on the outcome axis.** Whether an included trial reports major
> vascular events, or gives a 2x2 table vs only an effect+CI, is recorded as
> target-result status at extraction - never as an exclusion. A published effect + 95% CI
> is a poolable input.

