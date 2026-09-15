W-sglt2-hfref-hosp-cvdeath VERDICTS: NEW 10; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 0; WRONG_* 1; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 9
automated screen agreed on 0 of 10 verified

Population
- r2 includes 163 of 8108; already accounted for 3; NEW 160. MEASURED.
- First-lane NOT_VERIFIED_CAP remainder 10; lane W verification denominator NEW 10. MEASURED.
- Legacy includes 3 (31535829, 32865377, NCT06229678); primary pooled 2 (31535829, 32865377); primary declared-absent 1 (NCT06229678). MEASURED.
- First-line category sum 10 equals lane denominator 10. MEASURED.

ELIGIBLE_RCT ids with titles
- None. MEASURED.

DUPLICATE_OF_ACCOUNTED pairs
- None by verdict. MEASURED.
- NCT03036124 and NCT03057977 are registry-only rows for DAPA-HF and EMPEROR-Reduced, but the lane prompt says NCT-only/no-PMID records get REGISTRY_ONLY_NO_PUBLICATION. INFERRED from titles plus served-review accounted trials.

Verdict table
- 29020355: WRONG_POPULATION; quote: "patients with type 2 diabetes (T2D) and established CV disease (CVD)"
- NCT03332212: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Heart Failure; interventions=Empagliflozin | Placebo"
- NCT03448419: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Heart Failure; interventions=Empagliflozin | Placebo"
- NCT03030222: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Heart Failure; interventions=Empagliflozin 10 mg Tab | Placebo Oral Tablet"
- NCT03036124: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Chronic Heart Failure With Reduced Ejection Fraction (HFrEF); interventions=Dapagliflozin | Placebo"
- NCT03057977: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Heart Failure; interventions=Empagliflozin | Placebo"
- NCT03128528: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Chronic Heart Failure; interventions=Empagliflozin 10mg | Placebo Oral Tablet"
- NCT03198585: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Heart Failure With Reduced Ejection Fraction; interventions=Empagliflozin 10 MG | Placebo"
- NCT03200860: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Heart Failure Acute | Heart Failure，Congestive | Heart Failure; With Decompensation; interventions=Empagliflozin 10 MG | Placebo Oral Tablet"
- NCT02653482: REGISTRY_ONLY_NO_PUBLICATION; quote: "overallStatus=COMPLETED; conditions=Chronic Heart Failure With Reduced Systolic Function; interventions=Dapagliflozin | Dapagliflozin matching placebo"

Validation
- JSON objects 10; required quotes present 10 of 10; raw CT.gov files present 9 of 9; NOT_VERIFIED_CAP remaining 0. MEASURED.
- No PubMed efetch was needed because the only PMID remainder record had a non-empty, decisive snapshot abstract. MEASURED.
- For NCT-only rows, quote_source remains `snapshot abstract` to match the lane schema and prior-lane shape; CT.gov overallStatus was fetched and saved because the normalized snapshot abstract was empty and the prompt required status. MEASURED.

Commands run
- `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
- `git status --short`
- `Test-Path -LiteralPath F:\ProjectIndex\INDEX.md`
- `Test-Path -LiteralPath F:\E156\rewrite-workbook.txt`
- `Get-Content -Raw -LiteralPath .\LIVE_CONTEXT.md (failed: file absent)`
- `rg --files`
- `Get-Content -LiteralPath F:\ProjectIndex\INDEX.md -TotalCount 80`
- `Get-Content -LiteralPath F:\E156\rewrite-workbook.txt -TotalCount 120`
- `Get-Content -Raw -LiteralPath .\protocols\sglt2-hfref-hosp-cvdeath.md`
- `Get-Content -Raw -LiteralPath .\topics\sglt2-hfref-hosp-cvdeath.json`
- `Get-Content -Raw -LiteralPath .\docs\reviews\sglt2-hfref-hosp-cvdeath\review.json`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/sglt2-hfref-hosp-cvdeath.json',encoding='utf-8')); d=json.load(open('cache/sglt2-hfref-hosp-cvdeath/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python -c summary command for denominators (failed: PowerShell newline quoting produced SyntaxError)`
- `@' ... '@ | python - (inline Python: measured legacy ids, review accounted ids, r2 records/includes, and first-lane NOT_VERIFIED_CAP ids)`
- `@' ... '@ | python - (inline Python: dumped full cap-record fields and screen decisions)`
- `rg --files .\cache\sglt2-hfref-hosp-cvdeath\snapshots\2026-09-15r2-search_v2`
- `@' ... '@ | python - (inline Python: printed NCT allocation, masking, and has_results fields)`
- `rg -n "NCT03332212|overall|status|Official|Brief" .\cache\sglt2-hfref-hosp-cvdeath\snapshots\2026-09-15r2-search_v2`
- `@' ... '@ | python - (inline Python: inspected snapshot raw/INDEX.json entries mentioning capped NCTs)`
- `Test-Path -LiteralPath .\cache\sglt2-hfref-hosp-cvdeath\snapshots\2026-09-15r2-search_v2\raw\ctgov_condition_intervention#1\001.json`
- `@' ... '@ | python - (inline Python: inspected retrieval_ledger records for capped NCT ids)`
- `@' ... '@ | python - (inline Python: fetched CT.gov API v2 JSON for nine capped NCT ids into lane_v/sglt2-hfref-hosp-cvdeath-raw/)`
- `@' ... '@ | python - (inline Python: inspected first-lane registry/duplicate object style and quote_source values)`
- `@' ... '@ | python - (inline Python: searched first-lane NCT cap records for DAPA-HF/EMPEROR/DEFINE tokens)`
- `rg -n "quote_source|REGISTRY_ONLY_NO_PUBLICATION|NOT_VERIFIED_CAP" .\harness .\scripts .\tests`
- `rg -n "REGISTRY_ONLY_NO_PUBLICATION|quote_source" C:\meta-harness\outputs\search_v2\verification\sglt2-hfref-hosp-cvdeath`
- `@' ... '@ | python - (inline Python: wrote lane_v JSON, wrote report, and validated counts/quotes/verdicts/raw files)`
- `@' ... '@ | python - (inline Python: cleaned report command log and revalidated report/JSON)`
