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

## Q2

```
REGISTRY-VS-PUBLICATION DIFFERENCE ON A SERVED ROW -- for Mahmood's individual decision (derived by evid2; NOT landed)
Page: tocilizumab-covid19-mortality | Outcome: Serious adverse events (harm) | Trial: COVACTA, PMID 33631066, NCT04320615
SERVED: tocilizumab 103/295 vs placebo 55/143 -- from the held abstract: "103 of 295 patients (34.9%) in the tocilizumab group" / "55 of 143 patients (38.5%) in the placebo group"
REGISTRY (ClinicalTrials.gov NCT04320615 posted results, adverseEventsModule.eventGroups, timeFrame "60 days",
  safety-evaluable population grouped by treatment first received; acquired record
  evidence/typed_arms/registry/NCT04320615.json):
  EG001 "Tocilizumab (TCZ) Arm (Safety-Evaluable Population)" seriousNumAffected 116 / seriousNumAtRisk 295
  EG000 "Placebo Arm (Safety-Evaluable Population)"           seriousNumAffected  64 / seriousNumAtRisk 143
Same denominators, different counts (116 vs 103; 64 vs 55). evid2 has NOT established why: the publication's
assessment window is not stated in the held abstract; the registry's is 60 days. Under the new ownership rule
(registry groupIds where posted results exist) the registry reading would be the witnessed one, which would change a
served number. Options (Mahmood's decision): A. serve the registry counts 116/295 vs 64/143 with its window stated;
B. keep the publication counts and record the registry difference beside them; C. set the row aside until the full
text resolves the window. The pooled estimate must be recomputed by the pipeline under A. Nothing here is applied.
```

sha256 of the block above: `8a8e7d12fd2f8b28bbb5b4c9c923bdf808031ea8f5e111763efb578618d9955c`
