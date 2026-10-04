# G1 binding lane → Captain (lane v3): 4 topics where trials are missing or disagree

**Branch.** `g1/binding-4topics`, based on acq/k-gap `f34580f90` + g1/confirm-unverified. Code + typed findings only.
**Trackers are not regenerated.** The captain regenerates.

**Source order, as asked.** AACT posted results, then the trial's own held open text (PMC OA / Unpaywall / abstract),
then SECONDARY_SINGLE.

**Model calls.** One recorded `codex exec </dev/null` call per trial, concurrency 3, through the EXISTING
table-location machinery.
- The same prompt, schema, recorder, runs ledger and `harness.secondary_meta.gate_table_location`
  (`scripts/g1_binding_locate.py`).
- **Anti-circularity:** the comparator's numbers are never shown to the model.
- **Names:** every name in this report carries a rule and a span.

## n of N per topic (the named trials)

| Topic | Named trials | New verified rows | Typed findings | Blocked (named) |
|---|---|---|---|---|
| colchicine-secondary-cv-prevention | 8 (O'Keefe, Deftereos ×2, Hennessy, Mewton, Shah, Akrami, Tong) + COLCOT check | **0 of 8** | COLCOT F1 | 8 (below) |
| melatonin-primary-insomnia-sol | orientation (Wade [22] + 14 MD rows) | n/a | **F2 on 15 of 15 MD rows; F3 on Wade [22]** | — |
| esketamine-trd-madrs | Trial B, Trial E | **0 of 2** | Trial B F4, Trial E F5 | 2 |
| corticosteroids-cap-mortality | 7 NO_ROW | **0 of 7** | — | 7 |

## Findings (scripts/g1_binding_findings.py, outputs/k_gap/g1_binding/findings_*.json, 13 plants)

### F1, COLCOT (Tardif 2019, NCT02551094): "lands on the other side of no difference"

| | Value | Interval crosses 1? |
|---|---|---|
| Ours (the trial's primary composite) | HR 0.77 (0.61–0.96) | no |
| Comparator | RR 0.81 (0.64–1.03) from 114/2366 vs 141/2379 | yes |

**AACT 2026-08-30 posted results decide it.** The comparator's counts equal, in both arms, the SUM of three separately
posted outcomes:

| Posted outcome | Colchicine | Placebo |
|---|---|---|
| Cardiovascular Death | 20 | 24 |
| Myocardial Infarction | 89 | 98 |
| Stroke | 5 | 19 |
| **Sum = the comparator's row** | **114** | **141** |

The trial's own posted first-event composites are 131/170 (the PRIMARY) and 111/130 (CV death / arrest / MI / stroke).
Summed components count a patient with two events twice. **Our row stands; the comparator's row is not the trial's
composite.**

**Rule detail.**
- Arms are matched by posted N.
- Components are restricted to the trial's own declared components (topics/*.json trial_annotations). The real posted
  outcomes also hold a COINCIDENTAL decomposition (total death + angina + VTE + AF = 114/141), which the restriction
  excludes.
- Asserted only when the decomposition is unique.

### F2 + F3, melatonin: ours −17.4 vs theirs +11.2. **Neither sign is wrong.**

**F2: the conventions are mirrored.** The comparator (PMID 23691095) states its direction itself:
- "mean improvement in sleep onset latency";
- "efficacy in reducing sleep latency (weighted mean difference (WMD) = 7.06 minutes [95% CI 4.37 to 9.75])".

So a positive value means a reduction with melatonin, i.e. placebo minus melatonin. Ours is intervention minus control
(`harness/secondary_meta.py`: `md = mean_t - mean_c`). This holds for all 15 MD rows of the comparator. Any sign
comparison must mirror one side.

**F3: the magnitude gap is a different report of the same trial.**

| | Row label / report | PMID | Population |
|---|---|---|---|
| Comparator | "Wade AG, 2011 [21]": Curr Med Res Opin 2011, age cut-off analysis | 21091391 | 18–80 cohort and subsets |
| Ours | BMC Med 2010 | 20712869 | 65–80 subgroup, 3 weeks |

Both PubMed DataBank lists name **NCT00397189**: one trial, two analyses. The 17.4 vs 11.2 gap is a population /
report difference, not a value error.

### F4, esketamine Trial B (TRANSFORM-1, NCT02417064)

- **Registry:** 2 EXPERIMENTAL arms (56 mg, 84 mg) and 1 comparator.
- **Posted contrasts:** LS-mean (MMRM) 56 mg −4.1 (−7.67, −0.49) and 84 mg −3.2 (−6.88, 0.45).
- **Comparator:** −5.00 (−8.10, −1.90), equal to neither.
- **Rule:** the harness refuses the trial by its own rule, `harness/ctgov_results.py` MULTI-ARM GUARD ("esketamine
  56 mg / 84 mg / placebo ... the CANTOS/TRANSFORM-1 class").
- **Estimand:** the posted values are MMRM, while the topic estimand is observed-case Day-28 raw change.
- **Blocked:** MULTI_ARM_UNRESOLVED.

### F5, esketamine Trial E (SUSTAIN-2, NCT02497287)

- **AACT designs row 227554268:** allocation NA, SINGLE_GROUP, masking NONE; one EXPERIMENTAL group.
- **Consequence:** no randomised comparator exists, so no between-arm MD can come from it.
- **Proposed name:** NOT_ELIGIBLE by design (rule: protocol requires a randomised comparator; span: the designs row).

## Blocked trials, each with its reason

**colchicine**

| Trial | Reason |
|---|---|
| O'Keefe (PMID 1593057), Deftereos (25) (23500260), Deftereos (19) (26265659) | Paywalled; abstract only; NOT_REPORTED by arm in the abstract; no AACT results. Deftereos (19) NCT01936285 posts nothing. |
| Tong (COPS, 32862667) | Abstract prints "24 events … 38 events" without N: gate REFUSED INCOMPLETE. |
| Hennessy (31284074) | Unpaywall copy held: NOT_REPORTED. |
| Mewton (COVERT-MI, 34420373; NCT03156816 posts nothing) | PMC OA held: NOT_REPORTED. Its primary is infarct size. |
| Shah (COLCHICINE-PCI, 32295417) | PMC OA held: gate REFUSED INCOMPLETE. AACT NCT02594111 posts "All-cause Mortality, Non-fatal MI, or TVR" at six timepoints; abbreviated "MI" does not name the topic outcome, and the timepoint is not chosen. The PubMed record lists TWO registrations (NCT01709981, NCT02594111). |
| Akrami (34876021, BMC CC BY) | Gate REFUSED RATIO_DIRECTION_CONTRADICTS_ARM_EVENTS: HR 3.52 (1.60–7.74) quoted against 8 vs 28 events. |

**esketamine:** Trial B (F4 / multi-arm), Trial E (F5 / single arm).

**corticosteroids-CAP:** all 7 trials are paywalled with no OA copy, and the abstract does not report deaths by arm
(NOT_REPORTED).

| Trial | PMID | AACT |
|---|---|---|
| Confalonieri | 15557131 | — |
| Marik | 8339624 | — |
| Wagner 1956 BMJ | 4404939 | — |
| Snijders | 20133929 | NCT00170196, no posted results |
| Meijvis | 21636122 | NCT00471640, no posted results |
| Mikami | 17710485 | — |
| Blum | 25608756 | NCT00973154, no posted results |

**SECONDARY_SINGLE (sweep re-run, `--need=4`):**
- 0 new reads were due; all discovered metas' figures were already read or have no outcome figure.
- The read figures FAIL the self-reproduction gate, except one (PMID 30917856 Fig 2), whose rows are influenza
  observational studies; no join.
- The unread figure-only metas (colchicine 14, esketamine 10, corticosteroids 8) belong to the forest-reader lane
  (g1/forest-reader).

## Records

**Committed:** 13 of 16 new call records (evidence/model_calls/table_locator), plus the runs ledger. Their prompts hold
only PubMed abstracts, or a CC BY text (Akrami, BMC).

**Held locally, NOT committed:** 3 records whose prompts embed full texts under other or unclear licences. They are in
F:/claude-temp/held_records; the captain decides.

| Trial | Record |
|---|---|
| Mewton | mc-01fa07f5 |
| Hennessy | mc-9983ab25 |
| Trial B | mc-339ccd01 |
