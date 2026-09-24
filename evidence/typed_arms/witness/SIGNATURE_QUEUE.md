# evid2 signature queue (proposals only; each block's sha256 binds what was proposed)

## Q1

```
PROPOSED RESULT CHANGE -- for Mahmood's individual signature (derived by evid2; NOT landed, NOT applied)
Page: sglt2-ckd-progression | Outcome: Diabetic ketoacidosis (harm) | Trial: EMPA-KIDNEY, PMID 36331190, NCT03594110
SERVED: empagliflozin 6/3304 vs placebo 1/3305 (RR 6.00). Source of the served count: the full text's sentence
  "Ketoacidosis occurred in 6 patients in the empagliflozin group versus 1 patient in the placebo group" -- the broader
  term KETOACIDOSIS, served under the label DIABETIC ketoacidosis.
HELD REGISTRY (ClinicalTrials.gov NCT03594110, posted results, adverseEventsModule.seriousEvents; acquired record
  evidence/typed_arms/registry/NCT03594110.json):
  "Diabetic ketoacidosis": EG001 Empagliflozin 10 mg 5/3304, EG000 Placebo 1/3305
  "Ketoacidosis":          EG001 Empagliflozin 10 mg 1/3304, EG000 Placebo 0/3305
The two readings are consistent (5 + 1 = 6; 1 + 0 = 1): the served count is the union, the outcome label names one part.
OPTIONS (Mahmood's decision; evid2 recommends nothing that changes a number without his signature):
  A. keep the label "Diabetic ketoacidosis" and serve 5/3304 vs 1/3305 (RR 5.00), owned by registry groupIds;
  B. keep 6/3304 vs 1/3305 and relabel the outcome "Ketoacidosis (any, including diabetic)".
Either changes a served page (A the number, B the outcome identity); the pooled estimate for this outcome must be
recomputed by the pipeline, not by hand. Nothing here is applied.
```

sha256 of the block above: `04bf291dd1faae45c461e9c00927a1563e13bfc81a0b910e6ecb60a4543b981e`
