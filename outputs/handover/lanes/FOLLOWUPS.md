# Follow-up lane material (routed from mid-run audits; each becomes a second-pass lane on the landed base)

## SH2 (source hierarchy, second pass — after SH lands)
- omega3: STRENGTH (PMID 33190147) publishes HR 0.99 [0.90, 1.09]; harness reconstructs crude RR 0.9874 from 785/6539 vs 795/6539 while the other six rows keep published HRs — inconsistent WITHIN one page. Add to the regression set beside sglt2-hfref (both DAPA-HF 0.74 [0.65, 0.85] and EMPEROR-Reduced 0.75 [0.65, 0.86] published; served pools crude RRs; correct pool HR 0.745 [0.398, 1.395], MEASURED by integrator).
- Decide the estimand per outcome rather than letting FIRST_EVENT_RATIO erase it: trial-end cumulative risk → reconstruct RRs consistently; time-to-first-event → prefer published HRs consistently. Record the decision on the outcome object and apply it to every row.
- balanced-crystalloids: PLUS crude RR from counts + BaSICS published adjusted HR — strict on design (SMART/SALT/SPLIT refused) but permissive on effect measure; report as the asymmetry, apply the estimand decision.
- metformin-pcos: counts reconstructed from reported proportions — provenance must say so on the row.

## CP2 (comparator parity, second pass — after CP lands)
- omega3: main block cites Yu 2022 k=28, RR 0.94 [0.89, 1.00], overlap "not exactly verifiable"; Reproduction block asserts "comparable same-scope comparator k=15" with a decomposition that discusses OMEGA-REMODEL (clinical-outcomes publication 2024) against a comparator that searched only to Sept 2020 — the page itself notes the date elsewhere. The 0.94 is real; the trial-set relation is not trustworthy. Any decomposition naming a trial that postdates the comparator's search date is a violation.

## ACQ (acquisition lane — add to the trial list)
- omega3 OMEMI: eligible, unpooled, primary publication identifiable (1,027 elderly post-MI, 1.8 g/day EPA+DHA vs corn oil, composite ≈HR 1.08 [0.82, 1.41]); expected handling: retrieve → classify → probably REFUSE the primary efficacy pool on composite mismatch (includes all-cause death and HF hospitalisation) → adjudicate its AF harm (7.2% vs 4.0%, HR 1.84 [0.98, 3.45]).
- omega3 OMEGA: "not established — abstract only" but a double-blind post-MI trial reporting MACCE 10.4% vs 8.8%; resolve from publication, then reject on endpoint identity if it does not match.
- Extraction debt, not discovery debt: both were retrieved. Report them under EXTRACTION_DEBT.

## Phase 2A screening ground truth (probiotics; hold for the screening lane)
- False inclusions: 28057659 (protocol), 22559011 (PLACIDE protocol; trial 23932219 pooled), 22370839 and 34585011 (treatment of established AAD). False exclusion: 14627358 (yogurt for AAD prevention; no-probiotic control permitted).

## CG2 (claim graph, second pass — after CG lands) — plants added from audits
- glp1: the comparator-parity consumer ("our k=8 vs comparator k=7 — PARITY-effective, gap is ELIXA") must auto-STALE the moment `known_eligible_missing` (FLOW, FREEDOM-CVO) is set on the same page; pre-fix both coexist → plant.
- glp1 comparator scope "✓ same question" ignores the O in PICO: Giugliano 2021 has 7 trials on 3-point MACE and ELIXA on 4-point → classification must be "same population + same intervention class + near-matching outcome, one trial endpoint mismatch" (CP2).
- esketamine three-consumer split (EM lane owns the fix; CG2 plants it in the graph).
- Prose predicate 17 of 31 (FP lane owns fix; CG2 plants PROSE_PREDICATE_FALSE on all 17).

## CK — third instance for the harms axis
- glp1: both protocol harm outcomes render declared-absent/pending while pooled trials report the data (PIONEER 6 GI AEs leading to discontinuation; SUSTAIN-6 AE discontinuation + retinopathy complications HR 1.76 [1.11, 2.78]; SOUL GI disorders 5.0% vs 4.4%, serious AEs 47.9% vs 50.3%). State must read `known reported safety evidence awaiting extraction and harmonisation`, not absence.

## From topic 4 (colchicine-postop-af) — routed
- CK2 (executable eligibility chain): END-AF open-label pooled under a double-blind-OR-placebo protocol; Zarpelon two rationales; timepoint drift (COPPS-2 3-month vs key "in-hospital to 30 d"); ITT over available-case (2026 trial 163/172, COCS 240/267); harms four constructs; effect modifiers of the 2026 trial; vocabulary "myocardial revascularization" → cardiac surgery.
- KM: COCS + COPPS extraction debt → k=6 RR 0.6488 [0.4782, 0.8802] (MEASURED) — panel must carry `conclusion_effect = CHANGES_CI_NULL_CROSSING`; Sarzaeem = REACH_MISS (2B).
- CG2 plants: "such as the original COPPS trial … never found by the search" vs 22090167 screened in; parity "not a search/extraction failure" vs COCS "number IS in the source".
- RB2: END-AF rated low while D2 (blinding) unassessed — open-label trial cannot be "low" on masking-unassessed machine RoB.
- Phase 2B reach list: Sarzaeem 2014 (double-blind placebo CABG RCT, n=216, POAF 14.8% vs 30.6%, no PMID).
- Not to be done: adopting the exploratory k=8 ≈0.632 [0.501, 0.798]; regenerating the eligible set before the contract is fixed.

## From topic 12 (dpp4-mace-t2d, hash aaba73ab39328868) — routed
- **New rule → lane RO (refusal obligations), third wave**: every `estimand mismatch` / `incompatible` refusal emits a `RECOVERY_TASK` naming the compatible quantity and where to look (TECOS: abstract 4-point HR 0.98 [0.88, 1.09] correctly refused; strict 3-point secondary in primary full text HR 0.99 [0.89, 1.10], ITT, 745/7332 vs 746/7339 → ACQ item). A refusal that terminates is indistinguishable from a failure to look. Sweep every refusal: `n of N` where the compatible value exists in a held or reachable source.
- **EXAMINE CI-conversion policy** (RO/SH2 follow-up): 3-point MACE HR 0.96, one-sided NI upper 1.16; FDA two-sided 98% CI 0.80–1.16 → recover SE from statistical source, OR convert 98% → log-HR SE with the conversion declared on the page (render `derived`, never source-reported), OR protocol rule that NI intervals of this form are unsupported. "Not extracted forever" is not an option.
- **KM2**: third panel shape `TIGHTENS` — +TECOS k=4 ≈1.001 [0.900, 1.113] τ²=0; +TECOS+EXAMINE k=5 ≈0.995 [0.913, 1.083] vs served 1.007 [0.839, 1.209] (CLAIMED; compute only from committed sources once ACQ lands the full text).
- **CP3**: parity must require C and O, not only I and P — Patoulias 2021 pools individual events (not 3-point MACE) and includes CAROLINA (linagliptin vs glimepiride = X3 here); overlap IS readable from its references (SAVOR, CARMELINA, omarigliptin shared; TECOS, EXAMINE eligible-here-missing; CAROLINA comparator-only) — third page where "not machine-exposed" is false. The same C/O rule would have caught metformin (monotherapy vs add-on) and SMART-C.
- **HM2**: HF hospitalisation is the defining DPP-4 harm and is agent-specific: SAVOR-TIMI 53 HR 1.27 [1.07, 1.51]; TECOS 1.00 [0.83, 1.20]; EXAMINE ≈1.07–1.19; CARMELINA no excess; comparator pools RR 1.09 [0.92, 1.29], I²=65% → stratify by agent; "MACE ≈1.00 with no harms tab" invites the wrong inference.
- **D5-2 / CK2**: trial-conduct dimension the registry domains cannot see — omarigliptin CVOT terminated early (sponsor business decision, ~90% discontinued at cutoff; ITT HR 1.00 [0.77, 1.29] still usable) → `EARLY_TERMINATION`, `RUN_IN_ENRICHMENT` (LoDoCo2), `UNUSUAL_DISCONTINUATION` flagged for human adjudication, never "low on assessed domains".
- EN2 (running, corpus-wide): dpp4 key `CV_DEATH | NONFATAL_MI | NONFATAL_STROKE`; CARMELINA ≥1-dose FAS under `ITT / modified-ITT full-analysis CV population` superclass (5th ITT instance). EX (running): funding CARMELINA/omarigliptin unknown = abstract-depth, 3rd funding instance. CG2 (running): publication-bias contradiction 4th page; byte-reproducibility contradiction 2nd page.


## From topics 13-15 (added 2026-09-16 13:30)
- **XS2** (third wave): second-source corroboration requires outcome identity before magnitude. pcsk9: FOURIER "CT.gov RR 0.666 -- corroboration" against a primary whose crude RR is ~0.86 (1344 vs 1563); ODYSSEY 0.818 vs ~0.858 (903/9462 vs 1052/9462). Sweep every `cross_source` row in the corpus: `n of N` corroborations whose registry outcome title/components are not verified equal to the pooled outcome; a mismatch renders as `SECOND_SOURCE_DIFFERENT_ENDPOINT`, never as corroboration. Plant on aa8ed28a pcsk9 objects.
- **CP3**: comparator metadata truth (pcsk9: class-level comparator "alirocumab and evolocumab" recorded as single agent, match=True for the wrong reason); comparator completeness (spironolactone: Zhang 2025 omits J-EMPHASIS and includes EPHESUS which the protocol excludes -- superset, not parity; recency 2022 predates VESALIUS); parse comparator values from cached text instead of CP2's static per-slug profiles.
- **HM2 additions**: agent-stratified harms -- gynecomastia/breast pain RALES ~10% vs 1% (spironolactone) vs EMPHASIS 0.7% vs 1.0% (eplerenone) vs J-EMPHASIS 0 vs 0 must never pool as one MRA-class harm; hyperkalemia EMPHASIS 158/1336 vs 96/1340 and J-EMPHASIS 8/111 vs 6/110 (different definitions -> compatibility key); finerenone hyperkalemia FIDELIO 516/2827 vs 255/2833, FIGARO 396/3686 vs 193/3666 (+ ARTS-DN dose-response discontinuation 0/0/2.1/3.2/1.7%); pcsk9 injection-site reactions FOURIER ~280/13769 vs 213/13756, ODYSSEY 360/9460 vs 203/9458; AE discontinuation FOURIER 608/13769 vs 573/13756, ODYSSEY 343/9460 vs 324/9458. All CLAIMED until located in cached source text.
- **EN2/CK2**: `TIME_TO_FIRST_DEATH_COX_RATIO` class for spironolactone (RALES Cox "relative risk" is a hazard ratio); bidirectional assert-vs-underlying sweep reporting overstated-homogeneity and understated-compatibility separately (under-claim now on doac-vte, noac-af, spironolactone, finerenone); finerenone key literal `KIDNEY_FAILURE | SUSTAINED_EGFR_DECLINE_GE_40_PERCENT | RENAL_DEATH` for both trials.
- **SC/SE**: eligible screening misses PMID 8888663 (RALES dose-ranging 1996), PMID 20299607 (Udelson 2010) -> eligible, `outcome not appropriate for primary`; CONFIDENCE 2025 (finerenone + empagliflozin factorial; passes randomised-contrast test) -> screen in, refuse on outcome (paired plant with MIRO-CKD); fifth completeness state `eligible + surrogate-only design` (ARTS-DN, ARTS-DN Japan, FineCaRe, QUARTET-DKD).
- **KM2**: GRADE imprecision rationale must name the quantity it grades (k=2 HKSJ superpopulation width vs precision of the observed randomised evidence; finerenone ~13,000 participants, tau2=0, common-effect 0.84 [0.77, 0.92]); k=3 with a tiny discordant third trial (J-EMPHASIS 221 vs 1,663 + 2,737) stated as a method property; era heterogeneity (RALES NYHA III/IV, no beta-blockers; EMPHASIS NYHA II, ~87% beta-blockade) as visible effect-modifier dimensions.
- **Titles**: spironolactone -> "Steroidal mineralocorticoid receptor antagonists (spironolactone/eplerenone) versus placebo for all-cause mortality in chronic HFrEF."
- **EX**: funding depth -- J-EMPHASIS Pfizer-sponsored (designed, analysed, first draft) -> 2 of 3 known industry on spironolactone, fourth funding instance; ITT overstated FIDELIO 5,674 of 5,734, FIGARO 7,352 of 7,437 (sixth instance).
- **Positive controls (must-not-regress)**: FIDELIO published HR 0.82 [0.73, 0.93] overriding 504/2833 vs 600/2841 (SH2); FIGARO D5 = low on prespecified first-secondary renal composite (D5); DAPA-CKD/CREDENCE/EMPA-KIDNEY D5 low (D5).

## From topic 19 (colchicine-recurrent-pericarditis, added 14:36)
- **RT lane (round-trip)**: CORP-2 prints RR 0.49 (0.24–0.65) against counts 26/120 vs 51/120 (crude RR 0.510, log-RR CI ≈0.34–0.76) — the published effect and the 2×2 do not round-trip, yet the source is rendered "verified". Sweep every page where both a published effect and reconstructable counts exist: `n of N` that fail round-trip and are marked verified; render `published effect and 2x2 reconstruction do not round-trip`. TE covers selection; RT covers the validator's verdict.
- CORE and COPE: randomised but open-label; protocol requires double-blind placebo-controlled → correct exclusion, add to the plant set (SC3/CK2). The double-blind universe really is CORP, CORP-2, ICAP — this page's small k is not a search failure.
- CP3: "same question ✓" immediately followed by "RELATED, BROADER comparator, not same-scope" (Heart 2012, five controlled trials mixing open-label/double-blind and stages, RR 0.40 [0.30, 0.54]); predates ICAP (2013) and CORP-2 (2014). Current RCT syntheses sit at 0.46–0.48.
- CK3/EN: `DISEASE_STAGE ∈ {FIRST_ACUTE, FIRST_RECURRENCE, MULTIPLE_RECURRENCE}` (ICAP / CORP / CORP-2 with ~65% prior colchicine), treatment duration 3 vs 6 months; PICO revised post hoc from recurrent-only to comparator scope (disclosed) → render the recurrent-only CORP/CORP-2 strand as the originally targeted question beside the exploratory all-stage pool; timepoint key "longest reported" while all three assess at 18 months (sixth under-claim).
- HM2: pericarditis-related hospitalisation ICAP 6/120 vs 17/120, CORP-2 2/120 vs 12/120 (≈RR 0.26 [0.10, 0.70]); AEs / GI / discontinuation on all three trials.
- FU second pass: CORP-2 funding statement (Azienda Sanitaria 3 Torino) is already on the page's own row while the summary says 0 known / 2 unknown; CORP Maria Vittoria Hospital + Acarpia drug supply; ICAP Turin health authority + Acarpia → `institutional with commercial drug-supply ties`. Sixth funding instance.

## Added 2026-09-16 14:42 — CG acceptance test (topic 20, `corticosteroids-cap-mortality`, hash `eb09279de9273db5`)
Five contradictions on one page; all must fire pre-fix on `ad5e7c66`: (1) Torres pooled vs "verified but not pooled"; (2) the Torres refusal cites "declared 28-day mortality" while the protocol says "30 days or in hospital"; (3) overview and manuscript say the seven non-pooled eligible trials are "declared absent" while the Results table has 5 abstract-only/absence-unproven, 1 "not extracted — the number IS in the source" (Meduri/ESCAPe), 1 genuinely declared absent — every aggregate state sentence must be generated from the per-trial states ("seven eligible trials were not pooled" + breakdown), never written; (4) byte-reproducible asserted and retracted; (5) publication bias assessed vs NOT ASSESSED. Sweep the corpus for hand-written aggregate state sentences (`n of N` summary sentences not derived from the membership object).

- RX second pass (topic 20): reason codes verified against the CURRENT protocol object, not only the cached source; Torres plant.
- Architectural statement for the report (Mahmood, topic 20): the single-source claim object does not yet control all rendered propositions — Results membership is right everywhere; overview, manuscript, refusal block and reproducibility text render independently from stale or hand-written copies. Fix = make those sections consumers of the one object, not more checking. Comparator scale: 15 RCTs / 3,252 participants RR 0.69 (0.53–0.89) vs our two.

## From topic 22 (ticagrelor-vs-clopidogrel-acs, hash 78a62bbd717ce0cc; added 15:00) — audit complete, 22 of 22
- **KM2 second pass / GRADE inconsistency**: from the two inputs Q ≈ 4.49, df 1, p ≈ 0.034, I² ≈ 77.7%, τ ≈ 0.349 (log-HR); PLATO 0.84 (0.77–0.92) vs PHILO 1.47 (0.88–2.44) opposite directions; page says "Inconsistency — not downgraded" citing τ²=0.12171 alone. The GRADE object must separate genuine disagreement (direction conflict, Q p) from the t₁ penalty; a small-k τ² is never reassurance. Plant on the ad5e7c66 ticagrelor objects (this page is the DIRECTION_CONFLICT_K2 refusal on this base — the GRADE rationale must cite that refusal).
- **RX primary test case — retrieval failure vs compatibility refusal**: PHILO major bleeding reason code says no corroborated counts/effect in the abstract; the abstract reports major bleeding 10.3% vs 6.8%, HR 1.54 (0.94–2.53). Correct state: `effect extracted, incompatible with this pool (HR vs reconstructed RR)` — not absence. DISPERSE-2 (PMID 17980250, 990 pts, double-blind; 12-week composite clopidogrel 17 / 90 mg 19 / 180 mg 11 events; 180 mg HR 0.65 [0.30, 1.38]) → unextracted-outcome sweep: `HELD_NOT_EXTRACTED` if the full text is held, with a shared-control multi-arm modelling decision owed (not an absence).
- **CG2/CG3 state collapse**: DISPERSE-2 "declared absent" (Overview, manuscript) vs "not extracted — the number IS in the source" (Results). Results is right; generate the aggregate sentences from the per-trial states (same class as topic 20).
- **Stale RoB with the largest inferential consequence — HEADLINE EXAMPLE for the report**: RoB table shows PLATO and PHILO both rated low ("2 of 2 assessed"); the sensitivity says "1 of 2 pooled trials have a rating" and runs PLATO alone at 0.84 (0.77–0.92) — non-significant → significant purely on a stale membership state; GRADE repeats 1-of-2; manuscript says RoB not assessed for every pooled trial. On aa8ed28a this is the ticagrelor row in the stale-RoB class (fixed in 768c98fb by the trial_key join; the sensitivity is now refused with the pooled row).
- **CP3**: comparator "PARITY" false — its composite analysis has 5 studies / 33,258 participants and its table includes DISPERSE-2, which this review itself classifies eligible; "one valid RCT (PLATO) = ours" cannot stand. Byte-reproducibility asserted and retracted (eighth).

## Addenda that missed their lane's launch (second passes owed; the text is in the LANE-*.md handover copies)
- CS (launched 13:52; addendum 13:58): CRUSADERS state 4, FISSH `COMPLETED_UNPUBLISHED(registry)`, design-refused trials are not completeness states; STEP 5/11 timepoint refusals, STEP 6 trial-vs-report.
- CP3 (launched 13:54; addendum 13:58): semaglutide comparator not-same-question (O'Neil daily dosing; STEP 4 withdrawal design) → `DIFFERENT_EVIDENCE_SAME_NEIGHBOURHOOD`; balanced-crystalloids BEST-Living 2024 as principal comparator.
- RX (launched 13:56; addendum 13:58): balanced PRISMA `retrieved_refused` vs `not_retrieved`; BaSICS renal factorial-guard `REASON_FALSE_VALUE_HELD`; semaglutide GI counts and STEP 3 funding code audit.
- SC3 (launched 14:20; addendum 14:42): positive-control exclusions CORE/COPE, Meduri/ESCAPe, STEP 11.

## From topic 23 — colchicine-secondary-cv-prevention second pass (hash d85056d5b0ba682b; added 15:10). Audits remain open.
- **CG3 (raise priority — aggregate state sentences from per-trial states)**: Overview + manuscript say 26 non-pooled eligible trials "declared absent"; the Results object has ZERO in the genuine no-outcome-data state and four states (not extracted / abstract-only absence-unproven / excluded on evidence / genuine absence); PMID 32407460 "not extracted — the number IS in the source". Third page (corticosteroids 7-vs-3-states, ticagrelor 1-vs-not-extracted, here 26-vs-none) — worst instance; make it the CG3 primary plant. Sweep: `n hand-written aggregate state sentences of N aggregate sentences on 32 pages`.
- **KM2/GI second pass — GRADE inconsistency logic REPLACED, not tuned**: Q ≈ 9.06, df 2, p ≈ 0.0108, I² ≈ 77.9%, τ² 0.0267; the page's rationale "PI not markedly wider than the CI" while CI 0.51–1.30 and PI 0.35–1.90 — the rule's premise is false on its own rendered numbers. With ticagrelor (Q 4.49, I² 77.7%, opposite directions), two pages. New rule: inconsistency judged from Q p-value, I² with its Q-profile CI, direction conflict, and PI/CI width ratio, each MEASURED and rendered; the rationale sentence generated from those numbers; a rationale whose premise contradicts a rendered value is `RATIONALE_PREMISE_FALSE` (claim-graph violation). Plants: ticagrelor (ad5e7c66 objects) and this page.
- **RX/RO — self-inconsistent refusals**: COPS refused for (a) "ambiguous events, no HR/CI" — false, time-to-first-event HR 0.65 (0.38–1.09) is reported; (b) "broader composite" — while COLCOT (5-component), LoDoCo2 (4) and CLEAR SYNERGY (4) are pooled with differing component sets. A refusal reason that would also exclude a pooled trial is `REFUSAL_SELF_INCONSISTENT(reason, pooled_trials_it_would_exclude=[...])`. Sweep: `n refusals whose stated rule, executed, excludes ≥1 pooled trial on the same page of N refusals`. Whatever excludes COPS must be explicit, executable, applied to the pool too.
- **Refused-pool rendering must be systemic**: iv-iron renders reason code + per-trial compatibility keys + counterfactual estimate; this page's "Verified but not pooled" (COPS, Akrami, COColchicine-PCI) is prose only. Sweep `n refusals rendering the full structure of N refusals corpus-wide` — must be N of N; route the renderer into the claim-graph refusal object (CG3 / RO).
- Confirms topic 10: RoB 3/3 vs sensitivity+GRADE 2/3 with CLEAR SYNERGY displayed low and silently dropped (k=2 0.7215 = COLCOT + LoDoCo2) — fixed class in 768c98fb (trial_key join; MEASURE post-landing); publication bias NOT ASSESSED vs "assessed" (CG2); definition audit "OWED a consumer" still unconsumed (CG2/CG3: an owed consumer is an OPEN obligation, RO's object).

## Search/screening audit #1 (ticagrelor; 15:30) — new open stream
- Lane SF (queued after ST, RO): implicit-criterion sweep (included set narrower than the protocol rule without the rule requiring it), publication→trial-family→one decision, counts re-derived as `publications screened → trial families → eligible trial families`. TICAKOREA, TREAT, POPular AGE added to NAMED_MISSING_REGISTER.md (26 reach-misses on 12 pages; 9 held-unconsumed; 7 false includes; 6 protected refusals). Phase 2B (`search_v2.pin()` onto r3) consumes the register as its acquisition list.

## Search/screening audit #5 (dpp4; 15:50)
- SF: primary≠eligible endpoint rule (one rule, D5 + screening); CAROLINA comparator control (P/I/C/O coverage complete); entered_via blocking for 2B. Register unchanged at 31 reach-misses / 13 pages.

## Search/screening audit #6 (iv-iron; 16:00)
- SF: LVEF_THRESHOLD / HF_ACUITY / FORMULATION executable fields; primary!=eligible endpoint second instance; FAIR-HF2 + wider family to register (38 trials / 14 pages); FERRIC-HF, PRACTICE-ASIA-HF controls (7 controls: P I C O design size).

## Search/screening audit #7 (corticosteroids-cap; 16:15)
- SF: REMAP-CAP register; comparator equivalence class (bare 'vs placebo' sweep); severity/influenza axes; SLUG_AXIS_NOT_IN_CONFIG rule; paediatric control; Torres primary!=eligible third instance. Register >=42 trials / 15 pages; 8 controls; 5 unwritten-rule pages.

## Search/screening audits #8 (corticosteroids-covid19) and #9 (tocilizumab-covid19; k=1 vs 19) — 16:25
- SF: REACT steroid + tocilizumab sets as hard search benchmarks; comparator axis first-class rebuild (three failure directions); CASE_CONFIRMATION axis; early termination never eligibility; platform arm extraction; controls STOIC/PRINCIPLE/sarilumab/observational. Register >=63 named / 17 pages.

## Search/screening audit #10 (sacubitril-valsartan; 16:40)
- SF: re-derive all nine k=1 pages; PIONEER-HF ESCALATED (retrieved, outcome-excluded, result-changing; population decision owed to Mahmood); comparator ACEI/ARB vs enalapril; EF-phenotype controls. Register >=68 / 18 pages; 17 controls; 8 unwritten-rule pages.

## Search/screening audit #11 (sglt2-ckd; 16:50)
- SF: rendered rejection trail; kidney-specific vs cardiorenal screening fields (same lane as the EN2 construct fix); SCORED class-boundary decision; six CVOT/HF controls. Register >=69 / 19 pages; 23 controls; 9 unwritten-rule pages.

## Search/screening audit #12 (sglt2-hfref; 17:00) + architecture follow-ups
- Lane EP (queued FIRST after the four recoveries): precision of the cosine>=0.45 registry-outcome decider in rob2_build.py, n of N by hand adjudication, false matches quoted, pages whose RoB rests on one; no code change.
- PHASE_2A_DESIGN.md: the two lists (model-source targets vs keep-deterministic) + gate limb + acceptance set.
- SF: axes 8/9, broader-composite-never-excludes rule, DAPA ACT HF mandatory retrieval, DELIVER/EMPEROR-Preserved controls. Register >=72 / 19 pages; 25 controls; 10 unwritten-rule pages.

## Search/screening audit #13 (sglt2-primary-prevention-hf; 17:15) — convergence with page audit topic 7
- Lane PP (queued behind ST, RO): no-HF subgroup pool via protocol amendment; PRIMARY_PREVENTION=OF_HF executable; slug-term ambiguity sweep; six established-HF controls; CREDENCE required.
- DECISION FOR MAHMOOD (one question, three pages: sglt2-ckd SCORED, sglt2-hfref SOLOIST-WHF, sglt2-pp SCORED): is the SGLT2 intervention class SELECTIVE SGLT2 inhibitors only, or the SGLT-pathway including dual SGLT1/2 agents (sotagliflozin)? Register >=74 / 20 pages; 31 controls; 11 unwritten-rule pages.

## Decision 17:20 — class boundaries = two strands (Mahmood). Lane CB queued after PP; strand pairs for iv-iron, glp1, tocilizumab, MRA proposed in DECISION_CLASS_BOUNDARY_STRANDS.md pending Mahmood's approval; corticosteroids and colchicine are dose/regimen (effect-modifier fields), not class strands.

## Search/screening audit #14 (dapagliflozin-hfpef; 17:30)
- SF: k=1 three-state re-derivation; phenotype keyword veto MEASURED 8 of 38 configs (DELIVER survives by phrase luck); HFpEF slug term; three controls + DAPA-HF. Register >=77 / 21 pages; 35 controls; 12 unwritten-rule pages.
- Report correction: k=1 pages -> 'unproven until the rejection trail renders', not 'our failure' (2 of 3 our failure, 1 of 3 candidate legitimate).

## Search/screening audit #15 (empagliflozin-hfpef; 17:40)
- SF: paired generalisation test with #14; k=1 split now 2 of 4 clear failures / 2 of 4 likely defensible / 5 unaudited. Register >=80 / 22 pages; 37 controls; 13 unwritten-rule pages.

## Audits #16 denosumab, #17 statins (17:05)
- CORRECTION: STAREE already pooled (auditor error); flips now 3 (VESALIUS MEASURED, STEP 8, ICAP). ST lane corrected in flight via INTEGRATOR_CORRECTION.md.
- Design axis: 0 of 97 pooled rows non-randomised (MEASURED); statins observational element = comparator, already refused.
- k=1 tally: 3 wrongly thin / 2 likely legitimate / 4 unaudited. DIRECT to register; extraction-order failure mode -> TE mechanism + sweep; extensions as family+contrast failures; 'elderly' + sex-composition axes; POPULATION_BASIS records the defining characteristic.

## Search/screening audit #18 (tranexamic-acid-pph; 17:20)
- Indication decision NOT owed: protocol prospectively says treatment (MEASURED). SF: indication read from the population object, not keyword veto; retrieve-and-exclude the prevention family (26+4 trials) with trail; Ducloy-Bouthors X-DESIGN control; route/timing rules only if prospective. Register >=118 / 24 pages; 41 controls.
