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

## Q3

```
PROPOSED OUTCOME-IDENTITY CHANGE ON A SERVED ROW -- for Mahmood's individual decision (derived by evid2; NOT landed)
Page: corticosteroids-covid19-mortality | Outcome: Serious adverse events (harm) | Trial: COVID STEROID, PMID 34138478, NCT04348305
SERVED: hydrocortisone 1/16 vs placebo 0/14, labelled "Serious adverse events" -- from the held abstract: "the number of
  serious adverse reactions 1/16 vs 0/14".
THE TRIAL'S OWN FULL TEXT (PMC8441888, free to read, not open access; held local-only, sha256 4b8347da3b75...):
  "The secondary outcomes were: Number of participants with one or more serious adverse reactions at day 14 defined as
  new episodes of septic shock, invasive fungal infection, clinically important gastrointestinal bleeding, or
  anaphylactic reaction." and "In total, there was 1 patient with one or more SARs in the trial (hydrocortisone: 1/16;
  placebo 0/14)."
So the served count is a prespecified 4-event composite of serious adverse REACTIONS at day 14, served under the broader
label serious adverse EVENTS; the trial reports no all-cause SAE count in the held or acquired text. The registry record
has no posted results. Found by the adversarial ownership audit (2026-09-25), then confirmed in the full text.
OPTIONS (Mahmood's decision): A. keep 1/16 vs 0/14 and relabel this trial's row "Serious adverse reactions (septic
shock, invasive fungal infection, GI bleeding, anaphylaxis; day 14)" -- the row then no longer pools with SAE rows;
B. keep it in the SAE pool with a derived notice that it is a narrower composite; C. set the row aside from the SAE
outcome. A or C changes the pooled SAE estimate, which must be recomputed by the pipeline. Nothing here is applied.
```

sha256 of the block above: `3522dc53556c3c7b07fec92f2927ea1da8c11598b4877e60f92f9cb6bed33be4`

## Q2a (addendum to Q2)

```
ADDENDUM TO Q2 (Q2 above is unchanged; its sha256 still binds it) -- derived by evid2, NOT landed
COVACTA's full text (PMC7953459, free to read, not open access; held local-only, sha256 909fd806e081...) establishes
the cause Q2 left open -- the ASSESSMENT WINDOW:
  "In the safety population, adverse events were reported in 77.3% of 295 patients in the tocilizumab group and in
  81.1% of 143 patients in the placebo group through day 28 ( Table 3 ); serious adverse events were reported in 34.9%
  and 38.5%, respectively." Table 3 (Safety Population): "Any serious adverse event ... Patients with >=1 event 103
  (34.9) 55 (38.5)". The paper also states: "The primary analysis was performed at day 28, and the final trial visit
  occurred at day 60."
So: served 103/295 vs 55/143 = serious adverse events through DAY 28 (publication); registry 116/295 vs 64/143 =
through DAY 60 (registry timeFrame "60 days"). Same safety population and denominators; both are correct for their
window. Q2's options stand; under A the served window changes from 28 to 60 days and must be stated; under B the row
should carry its window (28 days). Nothing here is applied.
```

sha256 of the block above: `5ed6bca548d662c73f435a9eb7f1c7ff2baa33c05385da417c11b4348cd0cae8`
