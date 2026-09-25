# Decisions on evid2 signature queue Q1, Q2/Q2a, Q3 and the local-only texts -- 25 Sep 2026

**Decider:** Dispatch, acting under Mahmood's delegation, 25 Sep 2026.
**How the decision reached the decider:** evid2 pasted the full text of Q1, Q2, Q2a and Q3 into its reply in the evid2
Claude Code session: each question with its options, evid2's recommendation, and whether it changes a served number.
That text is the same as the sha256-bound blocks in `SIGNATURE_QUEUE.md` (Q1 `04bf291d...`, Q2 `8a8e7d12...`,
Q2a `5ed6bca5...`, Q3 `3522dc53...`). The decisions below came back as a user message in that same session and are
recorded verbatim in substance.
**What this record is NOT:** a countersignature. Q1 and Q3 change served results, so each goes to the signing list
(nr) as a derived notice. Nothing is served until the notice is signed and the release captain's candidate build
carries it.

## Q1 -- EMPA-KIDNEY, Diabetic ketoacidosis (sglt2-ckd-progression): option A
Keep the label "Diabetic ketoacidosis" and serve the registry's diabetic-only count: empagliflozin **5/3,304** vs
placebo **1/3,305**. Add a note that the paper's "ketoacidosis 6 vs 1" includes 1 non-diabetic ketoacidosis event.
- **Witness:** ClinicalTrials.gov NCT03594110 posted results, `adverseEventsModule.seriousEvents`, term "Diabetic
  ketoacidosis": EG001 "Empagliflozin 10 mg" numAffected 5 / numAtRisk 3304; EG000 "Placebo" 1 / 3305. Term
  "Ketoacidosis": EG001 1 / 3304; EG000 0 / 3305. Held: `evidence/typed_arms/registry/NCT03594110.json`.
- **Changes a served number:** yes. Derived notice below.

## Q2 / Q2a -- COVACTA, Serious adverse events (tocilizumab-covid19-mortality): option B
Keep the paper's day-28 counts, **103/295 vs 55/143**, which are from the primary-analysis time. State the 28-day window
on the row, and show the registry's day-60 figures, **116/295 vs 64/143**, beside them.
- **Witnesses:** the day-28 counts are in the full text (PMC7953459, Table 3 and the text "through day 28"). The
  day-60 counts are in ClinicalTrials.gov NCT04320615 `adverseEventsModule`, timeFrame "60 days".
- **Changes a served number:** no. Only an annotation (window, plus the registry figures beside the row) is added.

## Q3 -- COVID STEROID, Serious adverse events (corticosteroids-covid19-mortality): option A
Rename the row "Serious adverse reactions (septic shock, invasive fungal infection, GI bleeding, anaphylaxis; day 14)".
Keep 1/16 vs 0/14 visible, and remove it from the SAE pool, because it is a different outcome.
- **Root cause:** `topics/corticosteroids-covid19-mortality.json` declares the harm outcome "Serious adverse events"
  with keywords ["serious adverse reactions", "serious adverse reaction"], so the reactions composite was routed
  into SAE by configuration.
- **Changes a served number:** yes. Derived notice below.

## Local-only full texts (metformin, PMIDs 16769748 and 19522426)
Keep them LOCAL (copyright). 27 of 34 count rows stands; 2 rows are disclosed as "witnessed locally".

## V1.1 discovery
Stays on `evid2/v11-discovery-glp1` (8481d3c9). The release note cites it as V1.1 work in progress.

---

## Derived notice D-Q1 (for the signing list)
**Page:** sglt2-ckd-progression. **Outcome:** Diabetic ketoacidosis (harm, RR). k = 1 (EMPA-KIDNEY only).
- **Served now:** RR 6.00 (0.72 to 49.82) from 6/3,304 vs 1/3,305. These are the paper's "ketoacidosis" counts, served
  under the diabetic-ketoacidosis label.
- **After:** RR 5.00 (0.58 to 42.79) from 5/3,304 vs 1/3,305, the registry's "Diabetic ketoacidosis" counts. It carries
  a note: "The trial paper reports ketoacidosis 6 vs 1; that count includes 1 non-diabetic ketoacidosis event
  (registry term 'Ketoacidosis', empagliflozin 1 vs placebo 0)."
- **How "after" was computed:** `harness.synth.pool([Study(ai=5, n1i=3304, ci=1, n2i=3305)], scale="RR")` on main
  29f0a719. The same call on the served counts returns exactly the served 6.0018 (0.7230 to 49.8250). The value is
  EXPECTED until the candidate build computes it.
- **Why:** outcome identity. The label names diabetic ketoacidosis; the registry reports that term separately.

## Derived notice D-Q3 (for the signing list)
**Page:** corticosteroids-covid19-mortality. **Outcome:** Serious adverse events (harm, OR).
- **Served now:** OR 2.81 (0.11 to 74.56), k = 1 (COVID STEROID, 1/16 vs 0/14). Harm synthesis is flagged suppressed
  (`harms_synthesis_suppressed: true`).
- **After:** Serious adverse events has **no pooled result** (k = 0), because its only trial row is removed. A new
  harm outcome, "Serious adverse reactions (septic shock, invasive fungal infection, GI bleeding, anaphylaxis;
  day 14)", shows COVID STEROID 1/16 vs 0/14 as a single-trial row. Its estimate is whatever the candidate build
  computes. evid2 did not reproduce the served OR with a plain `synth.pool` call (that call gives 2.65), because the
  page applies a zero-cell rule evid2 has not traced, so no estimate is stated here.
- **Why:** the served count is a prespecified 4-event composite of serious adverse REACTIONS at day 14, not
  all-cause serious adverse events. The trial reports no all-cause SAE count.

---

## Change specification for the release captain (candidate build)
1. **Q1:** `cache/sglt2-ckd-progression/verified_arms.json`, key "36331190":
   - set `ai` from 6 to 5;
   - source the counts from the registry's AE term "Diabetic ketoacidosis" (groups EG001/EG000), witness
     `evidence/typed_arms/registry/NCT03594110.json`;
   - add the note above.
   The row is currently `fulltext_verified_arms`, bound by `harness/hand_binding.py` to held prose. A registry-AE
   source needs whichever registry binder the pipeline admits, so the route is the captain's call. Do not hand-set
   the estimate.
2. **Q3:**
   - `topics/corticosteroids-covid19-mortality.json` `harm_outcomes`: remove "serious adverse reaction(s)" from the
     keywords of "Serious adverse events", and declare a new harm outcome, "Serious adverse reactions (septic shock,
     invasive fungal infection, GI bleeding, anaphylaxis; day 14)", with those keywords (estimand OR).
   - `cache/corticosteroids-covid19-mortality/verified_arms.json`, key "34138478": set `outcome` to the new name.
3. **Q2:** no count change. Carry on the COVACTA SAE row (`tocilizumab-covid19-mortality`, PMID 33631066):
   - window "through day 28 (primary analysis)";
   - registry figures "ClinicalTrials.gov NCT04320615, through day 60: 116/295 vs 64/143".
   The row is machine-extracted from the abstract, not a verified_arms row, so where the annotation renders is the
   captain's call.
