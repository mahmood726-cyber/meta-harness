V-iv-iron-hfref-hosp VERDICTS: NEW 30; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 7; NOT_RCT 18; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 4; UNDECIDABLE 1; NOT_VERIFIED_CAP 0
automated screen agreed on 7 of 30 verified
r2 includes 39 of 2274; already accounted for 9; NEW 30
All numbers above are MEASURED from the files named in LANE_PROMPT.md; no cap was applied because NEW <= 150 (MEASURED).

## ELIGIBLE_RCT ids with titles
- None (MEASURED).

## DUPLICATE_OF_ACCOUNTED pairs
- NCT02937454 -> Duplicate of declared-absent AFFIRM-AHF (PMID 33197395) by record acronym Affirm-AHF.
- NCT03037931 -> Duplicate of declared-absent HEART-FID (PMID 37632463) by record acronym HEART-FID.
- NCT01394562 -> Duplicate of declared-absent EFFECT-HF (PMID 28701470) by record acronym EFFECT-HF.
- NCT01453608 -> Duplicate of pooled CONFIRM-HF (PMID 25176939) by record acronym CONFIRM-HF.

## Verdict Notes
- Secondary-analysis links to accounted trials are INFERRED from the record's named trial/acronym/NCT text plus the served review's accounted PMID list; verdict categories and counts are MEASURED from the lane JSON.
- Empty raw-body directory is intentional: no PubMed efetch or other HTTP body was relied on; all decisive quotes came from the committed r2 snapshot title/abstract fields (MEASURED).

## Commands Run
- `Get-Content -LiteralPath .\LANE_PROMPT.md -Raw`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 120 } else { Write-Output 'MISSING:F:\ProjectIndex\INDEX.md' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 120 } else { Write-Output 'MISSING:F:\E156\rewrite-workbook.txt' }`
- `if (Test-Path -LiteralPath .\LIVE_CONTEXT.md) { Get-Content -LiteralPath .\LIVE_CONTEXT.md -Raw } else { Write-Output 'MISSING:LIVE_CONTEXT.md' }`
- `git status --short`
- `rg --files`
- `Get-Content -LiteralPath .\protocols\iv-iron-hfref-hosp.md -Raw`
- `Get-Content -LiteralPath .\topics\iv-iron-hfref-hosp.json -Raw`
- `Get-Content -LiteralPath .\docs\reviews\iv-iron-hfref-hosp\review.json -Raw`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/iv-iron-hfref-hosp.json',encoding='utf-8')); d=json.load(open('cache/iv-iron-hfref-hosp/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `PowerShell here-string piped to python - (review primary-outcome trials and declared_absent_trials extraction).`
- `PowerShell here-string piped to python - (r2 snapshot count and include-decision extraction).`
- `PowerShell here-string piped to python - (new-include population/detail extraction; diagnostic run failed after counts due string year sorting).`
- `PowerShell here-string piped to python - (new-include population/detail extraction rerun with explicit year parsing).`
- `PowerShell here-string piped to python - (full NCT record field inspection).`
- `PowerShell here-string piped to python - (full abstract inspection for PMIDs 35301854, 37051919, 37382961, 37592272, 37926238, 38115745, 40916716).`
- `PowerShell here-string piped to python - (full abstract inspection for PMIDs 38896006, 39938943, 40351678, 40582343, 40740027, 41027507, 41526605).`
- `PowerShell here-string piped to python - (first write attempt; stopped on quote-verbatim check for PMID 35687248).`
- `PowerShell here-string piped to python - (write lane_v/iv-iron-hfref-hosp.json, create lane_v/iv-iron-hfref-hosp-raw/, write LANE-V-iv-iron-hfref-hosp-REPORT.md).`
- `PowerShell here-string piped to python - (validate lane JSON/report counts and quote requirements).`
- `git status --short`
