FT VERDICT: 19 rows; PRIMARY_REPORTED_ARM_LEVEL 3; PRIMARY_REPORTED_EFFECT_ONLY 0; OUTCOME_SECONDARY_ONLY 0; OUTCOME_ABSENT 0; FULLTEXT_NOT_OPEN_ACCESS 16; DUPLICATE_OF_POOLED 0

Measured facts:
- ELIGIBLE_RCT rows in C:/meta-harness/outputs/search_v2/lanes/X/lane_x/second_opinion.json: 19.
- Raw files in lane_ft/raw after cleanup: 19, one per row.
- Duplicate-of-pooled check: 0/19 PMIDs matched the protocol primary outcome pooled trial IDs.

| slug | pmid | verdict | quote <= 200 chars |
|---|---:|---|---|
| colchicine-postop-af | 35268478 | PRIMARY_REPORTED_ARM_LEVEL | Table 3: Parameters Colchicine (n = 50) Placebo (n = 51) OR 95% CI p / POAF, n (%) 9 (18) 15 (29.4) 0.527 0.206?1.349 0.178 |
| corticosteroids-cap-mortality | 41159889 | PRIMARY_REPORTED_ARM_LEVEL | At day 30, 530 (24.3%) participants had died, 246 (22.6%) of 1089 in the glucocorticoid arm and 284 (26.0%) of 1091 in the standard care arm; Hazard Ratio, 0.84; 95% confidence interval (CI), 0.73 ... |
| denosumab-vertebral-fracture | 21927920 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"21927920","pmid":"21927920","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| doac-vte-recurrence | 25912695 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"25912695","pmid":"25912695","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| melatonin-primary-insomnia-sol | 8795804 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"8795804","pmid":"8795804","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| metformin-pcos-ovulation | 16352680 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"16352680","pmid":"16352680","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| metformin-pcos-ovulation | 16316811 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"16316811","pmid":"16316811","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| metformin-pcos-ovulation | 15302293 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"15302293","pmid":"15302293","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| metformin-pcos-ovulation | 15482765 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"15482765","pmid":"15482765","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| metformin-pcos-ovulation | 11779598 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"11779598","pmid":"11779598","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 28482385 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"28482385","pmid":"28482385","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 28592037 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"28592037","pmid":"28592037","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 23302558 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"23302558","pmid":"23302558","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 19652108 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"19652108","pmid":"19652108","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 17803164 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"17803164","pmid":"17803164","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 18252070 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"18252070","pmid":"18252070","pmcid":"PMC2084134","isOpenAccess":"N","inPMC":"Y"} |
| probiotics-aad-prevention | 14608267 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"14608267","pmid":"14608267","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| probiotics-aad-prevention | 12403254 | FULLTEXT_NOT_OPEN_ACCESS | Europe PMC search response: {"id":"12403254","pmid":"12403254","pmcid":"","isOpenAccess":"N","inPMC":"N"} |
| ticagrelor-vs-clopidogrel-acs | 27471389 | PRIMARY_REPORTED_ARM_LEVEL | Table 2: End points Clopidogrel (n=100) Ticagrelor (n=100) HR (95% CI) P-value / Composite of CV death/MI/stroke 22 (22%) 11 (11%) 0.473 (0.230?0.976) 0.043 |

Commands run:
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 160 } else { Write-Output 'F:\ProjectIndex\INDEX.md unavailable' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 160 } else { Write-Output 'F:\E156\rewrite-workbook.txt unavailable' }`
- `git status --short`
- `Get-ChildItem -Force`
- `if (Test-Path -LiteralPath 'C:\meta-harness\outputs\search_v2\lanes\X\lane_x\second_opinion.json') { Get-Item -LiteralPath 'C:\meta-harness\outputs\search_v2\lanes\X\lane_x\second_opinion.json' | Select-Object FullName,Length,LastWriteTime } else { Write-Output 'missing second_opinion.json' }`
- `rg --files`
- `Get-Content -LiteralPath .\lane.log -Tail 80`
- `python -c [count ELIGIBLE_RCT rows and print slug/pmid/title]`
- `python -c [summarize review protocol/outcomes/comparator/arm_contrast; failed on console encoding]`
- `python -X utf8 -c [summarize review outcomes/comparator/arm_contrast/protocol_config]`
- `python -X utf8 -c [print primary outcome names, estimands, pooled IDs, declared absent IDs]`
- `python -X utf8 -c [fetch Europe PMC search responses and OA fullTextXML into lane_ft/raw]`
- `python -X utf8 -c [inspect denosumab Europe PMC search response fields]`
- `python -X utf8 -c [search colchicine XML for primary outcome terms]`
- `python -X utf8 -c [search corticosteroids XML for primary outcome terms]`
- `python -X utf8 -c [search ticagrelor XML for primary outcome terms]`
- `python -X utf8 -c [extract ticagrelor XML tables]`
- `python -X utf8 -c [extract colchicine XML tables]`
- `python -X utf8 -c [extract corticosteroids XML tables]`
- `python -X utf8 -c [check each PMID against pooled primary-outcome trial IDs]`
- `Remove-Item -LiteralPath .\lane_ft\raw\01_colchicine-postop-af_35268478_europepmc_search.json, .\lane_ft\raw\02_corticosteroids-cap-mortality_41159889_europepmc_search.json, .\lane_ft\raw\19_ticagrelor-vs-clopidogrel-acs_27471389_europepmc_search.json`
- `python -X utf8 -c [write lane_ft/fulltext.json and LANE-FT-REPORT.md; first attempt failed before Python due PowerShell quoting]`
- `@' ... '@ | python -X utf8 - [write lane_ft/fulltext.json and LANE-FT-REPORT.md]`
- `python -X utf8 -c [validate 19 objects, allowed verdicts, nonempty quotes, raw paths exist, first-line sum, 19 raw files]`
- `git status --short`
