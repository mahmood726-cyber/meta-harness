# Evidence lane report: 2026-09-23

Branch `evid/evidence-records` @ `0ee8a40b`; main `38c04411` unchanged by this lane. Every count below is computed by `evidence/scripts/report.py` from the committed records.

## P53: N = 53 (pooled primary rows inadmissible on P5 at 38c04411)

- adjudicated: **53 of 53**; not yet: 0 (none)
- rulings (of 53 adjudicated): SERVED_CONFIRMED 53
- entry population, lane ruling (of 53): ESTABLISHED 47, NOT_ESTABLISHED 2, PARTLY 4
- analysis set as the source states it (of 48 drafted from extractions): ITT_STATED 20, NOT_STATED 15, OTHER_SET_STATED 13
- rows carrying a recorded label defect (number unchanged): 3

  - P53-05 SERVED_CONFIRMED / entry PARTLY: RECOVERY dexamethasone: hospitalised patients with suspected or confirmed SARS-CoV-2. Entry is ESTABLISHED for COVID hospitalisation but PARTLY for 'adults': the held full text removed the age floor during recruitment. Comparator is usual care, which the quest
  - P53-18 SERVED_CONFIRMED / entry PARTLY: FAIR-HF2: LVEF <=45% with iron deficiency. The question says HFrEF, and a 45% ceiling includes mildly reduced EF (41-45%), so entry is PARTLY. Served IRR 0.80 (0.60-1.06) for total HF hospitalisations is printed as a rate ratio (recurrent events) in the full t
  - P53-22 SERVED_CONFIRMED / entry ESTABLISHED: ROCKET AF: non-valvular AF at increased stroke risk; the registry minimum age is 18 (ELIGIBILITY AGE/SEX line). Served HR 0.88 (0.74-1.03) is the ITT result as printed. TYPED LABEL DEFECT: the served analysis_set reads 'per-protocol' although the number is the
  - P53-32 SERVED_CONFIRMED / entry NOT_ESTABLISHED: L. casei DN114001 in patients over 55 (UK multicentre). The held abstracts never state antibiotic receipt as an ENTRY criterion; it is implied only by the outcome's name. The full text is not open access and was not acquired. Served counts 106/549 vs 103/577 p
  - P53-46 SERVED_CONFIRMED / entry PARTLY: EMPA-REG OUTCOME: T2D at high CV risk (registry title). Served HHF HR 0.65 (0.50-0.85) printed in the registry (All Empagliflozin vs Placebo). The question's trial-level property (participants WITH and WITHOUT baseline HF) is not stated in held text, hence PAR
  - P53-47 SERVED_CONFIRMED / entry PARTLY: DECLARE-TIMI 58: T2D with or at risk for ASCVD, 17,160, median 4.2 years. Served HHF HR 0.73 (0.61-0.88) printed. The with/without-baseline-HF property is not stated in held text, hence PARTLY. Analysis set NOT STATED.
  - P53-49 SERVED_CONFIRMED / entry ESTABLISHED: EMPHASIS-HF: NYHA II, EF <=35%, registry minimum age 55. Served HR 0.76 (0.62-0.93) is printed in the abstract and equals the registry's cut-off analysis HR 0.761 (0.622-0.932), 171 vs 213. The complete-DB counts (205 vs 253) carry no HR, so the extractor's 'l
  - P53-50 SERVED_CONFIRMED / entry NOT_ESTABLISHED: JUPITER, age >=70 subgroup (5695 of 17,802). The number is right: HR 0.61 (0.46-0.82) printed. But the row's population is NOT a randomised entry population: the age cut-point was chosen AFTER trial completion (exploratory), and the served label calls it 'pre-

## U23: N = 23 (served rows lane UA found with no locatable source)

- adjudicated: **23 of 23**; not yet: 0 (none)
- rulings (of 23 adjudicated): CANDIDATE_REJECTED 3, SERVED_CONFIRMED 20
- entry population, lane ruling (of 23): ESTABLISHED 22, PARTLY 1
- analysis set as the source states it (of 15 drafted from extractions): ITT_STATED 4, NOT_STATED 7, OTHER_SET_STATED 4
- rows carrying a recorded label defect (number unchanged): 3

  - UA-027 SERVED_CONFIRMED / entry PARTLY: Wade 2010 (PMC OA): adults 18-80 with primary insomnia. The served row is the 65-80 subgroup: arm means -19.1 vs -1.7 (SD 47.3/47.8, n 137/144), which differ from the paper's ADJUSTED difference -15.6 (-25.3 to -6.0). Raw arm means are a legitimate input and t
  - UA-032 CANDIDATE_REJECTED / entry ESTABLISHED: The served row pools CT.gov observed in-trial arm means (-16.5 vs -5.8) with n = 407/204, the full-analysis-set totals. The registry states that the number analysed is those with available data, and the class-level denominators for the in-trial period are 373/
  - UA-033 CANDIDATE_REJECTED / entry ESTABLISHED: Same defect as STEP 3 (UA-032). The served row pools observed in-trial means (-15.6 vs -2.8) with n = 1306/655 (FAS), while the registry's class-level denominators for those means are 1212/577 (participants with available data). The declared estimand is treatm
  - UA-042 CANDIDATE_REJECTED / entry ESTABLISHED: The served 'All-cause mortality' row carries HR 0.85 (0.53-1.36). The abstract gives that HR for the PRIMARY COMPOSITE (cardiovascular death or HF hospitalisation), not for all-cause death. The registry record of the same trial (NCT01115855) reports a separate
  - UA-044 SERVED_CONFIRMED / entry ESTABLISHED: COVACTA: adults with severe COVID-19 pneumonia. Served SAE counts 103/295 vs 55/143 printed. LABEL DEFECT: served 'modified intention-to-treat'; the source set is the SAFETY population (by first agent received). Number unchanged.
  - UA-045 SERVED_CONFIRMED / entry ESTABLISHED: EMPACTA (PMC OA): hospitalised adults >=18 with COVID-19 pneumonia. Served SAE counts 38/250 vs 25/127 printed. LABEL DEFECT: served 'modified intention-to-treat'; the source set is the SAFETY population (by actual agent). Number unchanged.

## Queued for Mahmood's signature (derived, NOT landed)

- UA-032: semaglutide-obesity-weight / Percent change in body weight / PMID 33625476 (STEP 3): MD from -16.5 (SD 10.1, n=407) vs -5.8 (SD 7.7, n=204), labelled treatment-policy -> A: MD -10.27 (-11.97 to -8.57) treatment-policy; or B: same means with n=373/189 relabelled observed-case
- UA-033: semaglutide-obesity-weight / Percent change in body weight / PMID 33567185 (STEP 1): MD from -15.6 (SD 10.1, n=1306) vs -2.8 (SD 6.5, n=655), labelled treatment-policy -> A: MD -12.44 (-13.37 to -11.51) treatment-policy; or B: same means with n=1212/577 relabelled observed-case
- UA-042: spironolactone-hfref-mortality / All-cause mortality / PMID 28824029 (J-EMPHASIS-HF): HR 0.85 (0.53-1.36) -- the primary composite, mis-attributed -> HR 1.77 (0.81-3.87) -- registry all-cause mortality analysis

Blocks with sha256: `evidence/SIGNATURE_QUEUE.md`.

## Extraction pipeline

- codex extractions verified against held bytes: 75 of 76; failing (candidates, not claims): UA-002

## Limits (stated so a clean count cannot imply more than it measured)

- Every ruling is ONE adjudicator's (this lane, Anthropic family); the extractor was codex (OpenAI family). Spans are machine-verified against held bytes, but the SEMANTIC rulings (entry ESTABLISHED/PARTLY, which candidate a served endpoint means) have had no second, independent adjudicator.
- 'Entry ESTABLISHED' means the trial's own text states an entry population inside the question. It is evidence for Mahmood's D04, not an admission; no route that admits a row exists or was created.
- Most held sources are abstracts or registry records; open-access full text was held or acquired for a minority. 'Analysis set NOT STATED' usually means 'not in an abstract', not 'not in the paper'.
- One source is held LOCAL-ONLY (not redistributable): URL and sha256 in evidence/LOCAL_ACQUISITIONS.json.
