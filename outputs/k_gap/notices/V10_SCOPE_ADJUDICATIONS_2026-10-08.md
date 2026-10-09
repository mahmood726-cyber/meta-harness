# V10 proposals: two protocol-text scope adjudications (k-gap, 8 Oct 2026). Proposed, not applied

The rule is the one in `registry/scope_adjudications.json`, decisions 2 and 3 (5 Oct): a comparator trial is named PROTOCOL_SCOPE_DIFFERENCE only when our registered protocol's own text excludes it.
- The protocol span must be verbatim in `protocols/<slug>.md`.
- The trial span must be verbatim in the trial's held record.
- Being listed by the comparator is never a reason.

Both entries below were checked by script against `origin/main`:
- protocol file (sha256 recorded);
- held record `outputs/k_gap/member_records.json` (abstract sha256 recorded).

The ready-to-paste JSON is `V10_SCOPE_ADJUDICATIONS_2026-10-08.json`. Adding either entry to the registry is the captain's decision under Mahmood's delegation.

## 1. denosumab-vertebral-fracture: Bone 2008 (PMID 18381571, NCT00091793, Amgen study 20040132)

| | Span |
|---|---|
| Protocol | "postmenopausal women with osteoporosis." (the Population line) |
| Trial (held abstract) | "Subjects included 332 postmenopausal women with lumbar spine BMD T-scores between -1.0 and -2.5." |

- **Population.** A lumbar spine T-score between -1.0 and -2.5 is the WHO low-bone-mass (osteopenia) band, not osteoporosis.
  - The EMA Prolia EPAR (held, EMA reuse with acknowledgement) describes 20040132 the same way: "women with PMO and basal lumbar spine BMD T-score between -1.0 and -2.5". It calls it a prevention study.
- **Why it is NO_ROW today.** The tracker's blocker is INSUFFICIENT_RECORD:POPULATION_NOT_STATED_IN_RECORD. That is a screener miss: the record states the population, but in T-score terms the screen does not read.
- **Effect.** RESULT_AGREES is already met on FREEDOM. Naming Bone 2008 makes it eligible 1 of 1, matched 1 of 1, with the divergence named.
  - **denosumab-vertebral-fracture would flip to G1_MATCHED.** This is FLIP-READY on this decision alone.
- **Every open route tried for a count** (`cache/denosumab-vertebral-fracture/routes_ledger.json`):
  - AACT: BMD outcomes only.
  - The EMA Prolia EPAR names 20040132 seven times but prints no fracture count for it.
  - PMDA's only English denosumab review is Pralia's 2017 rheumatoid-arthritis review, which doesn't name the study. Its Japanese original has no text layer.
  - The OA copy (OUP) answered with a bot challenge.
  - ANZCTR and CADTH answered with bot challenges; jRCT refused the TLS handshake; TGA was unreachable.
  - CORE needs an account.

## 2. semaglutide-obesity-mace: O'Neil 2018 (PMID 30122305, NCT02453711)

| | Span |
|---|---|
| Protocol | "once-weekly subcutaneous semaglutide 2.4 mg added to standard care." (the I line) |
| Trial (held abstract) | "All treatment doses were delivered once-daily via subcutaneous injections." |

- **Correction to the CLOSE-4 premise.** No protocol amendment is needed. The registered sema-MACE protocol already fixes the dose and regimen in its I line.
  - semaglutide-obesity-weight names this trial by the same protocol-text route (decision 2, axis INTERVENTION_DOSE_AND_REGIMEN). It does not use an arm-object rule.
- **Difference from the weight topic.** The weight protocol also has an exclusion line naming "a different semaglutide dose". sema-MACE's X3 says only "no semaglutide-vs-placebo contrast". This entry rests on the I line alone.
- **Effect.** It meets ALL_ELIGIBLE_MATCHED and names the divergence. RESULT_AGREES still needs SELECT's MACE counts (binding) and D12 COUNTS_FOR_MATCHING (Mahmood), so it is **not flip-ready alone**.
