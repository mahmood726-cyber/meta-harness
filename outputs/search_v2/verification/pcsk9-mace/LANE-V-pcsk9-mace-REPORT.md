V-pcsk9-mace VERDICTS: NEW 67; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 16; NOT_RCT 11; WRONG_* 1; DUPLICATE_OF_ACCOUNTED 22; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 17
automated screen agreed on 16 of 67 verified
r2 includes 69 of 5644; already accounted for 2; NEW 67
MEASURED: r2 include count, total records, already-accounted count, NEW count, verdict buckets, and screen-agreement count were computed from the JSON inputs on disk.
INFERRED: verdict labels are reviewer classifications from the quoted snapshot title, abstract, or registry fields; no outside trial knowledge was used.
MEASURED: PubMed new includes with empty/truncated snapshot abstracts = 0, so no PubMed efetch HTTP body was relied on; lane_v/pcsk9-mace-raw/ is intentionally empty.

## ELIGIBLE_RCT ids with titles
- none

## DUPLICATE_OF_ACCOUNTED pairs
- 41369622 -> PMID 28304224 (FOURIER): Obesity-Associated Cardiovascular Risk and Benefit From PCSK9 Inhibition: A Prespecified Analysis From FOURIER.
- 42291078 -> PMID 30403574 (ODYSSEY OUTCOMES): Small, dense LDL-C as a predictor of cardiovascular risk and benefit of alirocumab in patients with recent acute coronary syndrome receiving optimized statin treatment.
- 38960812 -> PMID 30403574 (ODYSSEY OUTCOMES): Alirocumab and cardiovascular outcomes according to sex and lipoprotein(a) after acute coronary syndrome: a report from the ODYSSEY OUTCOMES study.
- 39232634 -> PMID 30403574 (ODYSSEY OUTCOMES): Triglyceride Levels, Alirocumab Treatment, and Cardiovascular Outcomes After an Acute Coronary Syndrome.
- 39687787 -> PMID 30403574 (ODYSSEY OUTCOMES): Alirocumab and chest pain after acute coronary syndrome: An analysis of ODYSSEY OUTCOMES.
- 35378068 -> PMID 30403574 (ODYSSEY OUTCOMES): Metabolic risk factors and effect of alirocumab on cardiovascular events after acute coronary syndrome: a post-hoc analysis of the ODYSSEY OUTCOMES randomised controlled trial.
- 35644332 -> PMID 30403574 (ODYSSEY OUTCOMES): Alirocumab and Cardiovascular Outcomes in Patients With Previous Myocardial Infarction: Prespecified Subanalysis From ODYSSEY OUTCOMES.
- 35770629 -> PMID 30403574 (ODYSSEY OUTCOMES): Apolipoprotein B, Residual Cardiovascular Risk After Acute Coronary Syndrome, and Effects of Alirocumab.
- 36031810 -> PMID 28304224 (FOURIER): Long-Term Evolocumab in Patients With Established Atherosclerotic Cardiovascular Disease.
- 33197560 -> PMID 28304224 (FOURIER): Effect of Evolocumab on Complex Coronary Disease Requiring Revascularization.
- 33438437 -> PMID 30403574 (ODYSSEY OUTCOMES): Clinical Efficacy and Safety of Alirocumab After Acute Coronary Syndrome According to Achieved Level of Low-Density Lipoprotein Cholesterol: A Propensity Score-Matched Analysis of the ODYSSEY OUTCOMES Trial.
- 31948641 -> PMID 30403574 (ODYSSEY OUTCOMES): Effect of Alirocumab on Lipoprotein(a) and Cardiovascular Risk After Acute Coronary Syndrome.
- 32223446 -> PMID 30403574 (ODYSSEY OUTCOMES): Peripheral Artery Disease and Venous Thromboembolic Events After Acute Coronary Syndrome: Role of Lipoprotein(a) and Modification by Alirocumab: Prespecified Analysis of the ODYSSEY OUTCOMES Randomized Clinical Trial.
- 32347885 -> PMID 28304224 (FOURIER): Effect of Evolocumab on Type and Size of Subsequent Myocardial Infarction: A Prespecified Analysis of the FOURIER Randomized Clinical Trial.
- 32820320 -> PMID 30403574 (ODYSSEY OUTCOMES): Effect of alirocumab on major adverse cardiovascular events according to renal function in patients with a recent acute coronary syndrome: prespecified analysis from the ODYSSEY OUTCOMES randomized clinical trial.
- 30586750 -> PMID 28304224 (FOURIER): Lipoprotein(a), PCSK9 Inhibition, and Cardiovascular Risk.
- 30898609 -> PMID 30403574 (ODYSSEY OUTCOMES): Alirocumab in Patients With Polyvascular Disease and Recent Acute Coronary Syndrome: ODYSSEY OUTCOMES Trial.
- 31116355 -> PMID 28304224 (FOURIER): Effect of the PCSK9 Inhibitor Evolocumab on Total Cardiovascular Events in Patients With Cardiovascular Disease: A Prespecified Analysis From the FOURIER Trial.
- 31121022 -> PMID 30403574 (ODYSSEY OUTCOMES): Effects of alirocumab on types of myocardial infarction: insights from the ODYSSEY OUTCOMES trial.
- 31272931 -> PMID 30403574 (ODYSSEY OUTCOMES): Effects of alirocumab on cardiovascular and metabolic outcomes after acute coronary syndrome in patients with or without diabetes: a prespecified analysis of the ODYSSEY OUTCOMES randomised controlled trial.
- 29133605 -> PMID 28304224 (FOURIER): Low-Density Lipoprotein Cholesterol Lowering With Evolocumab and Outcomes in Patients With Peripheral Artery Disease: Insights From the FOURIER Trial (Further Cardiovascular Outcomes Research With PCSK9 Inhibition in Subjects With Elevated Risk).
- 28207168 -> PMID 28304224 (FOURIER): Design and rationale of the EBBINGHAUS trial: A phase 3, double-blind, placebo-controlled, multicenter study to assess the effect of evolocumab on cognitive function in patients with clinically evident cardiovascular disease and receiving statin background lipid-lowering therapy-A cognitive study of patients enrolled in the FOURIER trial.

## Commands run
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `Get-Content -LiteralPath .\LIVE_CONTEXT.md  # failed: file absent`
- `Get-Content -LiteralPath F:\ProjectIndex\INDEX.md  # output truncated by terminal tool`
- `Get-Content -LiteralPath F:\E156\rewrite-workbook.txt  # output truncated by terminal tool`
- `git status --short`
- `Get-Content -LiteralPath .\protocols\pcsk9-mace.md`
- `Get-Content -LiteralPath .\topics\pcsk9-mace.json`
- `Get-Content -LiteralPath .\docs\reviews\pcsk9-mace\review.json`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/pcsk9-mace.json',encoding='utf-8')); d=json.load(open('cache/pcsk9-mace/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python - <<'PY' ... PY  # failed: PowerShell does not support bash heredoc syntax`
- `python -c "exec('''...''')"  # failed: quoting produced unterminated triple-quoted string`
- `@' ... '@ | python -  # inspected r2/review schema, include IDs, accounted IDs`
- `@' ... '@ | python -  # inspected first NCT registry record keys/fields`
- `@' ... '@ | python -  # inspected r2 search_v2 metadata`
- `@' ... '@ | python -  # computed denominator and printed new include details`
- `@' ... '@ | python -  # printed compact ordered new-include table`
- `@' ... '@ | python -  # printed quote-relevant excerpts for all ordered rows; terminal truncated middle`
- `@' ... '@ | python -  # printed quote-relevant excerpts for rows 18-41`
- `@' ... '@ | python -  # inspected served-review pooled and declared-absent trial IDs`
- `@' ... '@ | python -  # checked PubMed new-include abstracts for empty/truncated snapshots`
- `Test-Path -LiteralPath .\lane_v`
- `if (Test-Path -LiteralPath .\lane_v) { Get-ChildItem -LiteralPath .\lane_v -Force | Select-Object -ExpandProperty Name }`
- `Test-Path -LiteralPath .\LANE-V-pcsk9-mace-REPORT.md`
- `@' ... '@ | python -  # failed generation: quote marker for PMID 28207168 did not match snapshot wording`
- `@' ... '@ | python -  # inspected PMID 28207168 title/abstract for exact EBBINGHAUS wording`
- `@' ... '@ | python -  # generated lane_v/pcsk9-mace.json, lane_v/pcsk9-mace-raw/, and LANE-V-pcsk9-mace-REPORT.md`
- `@' ... '@ | python -  # validation: JSON length, quotes, verdict values, report first-line sum`
- `git status --short`
