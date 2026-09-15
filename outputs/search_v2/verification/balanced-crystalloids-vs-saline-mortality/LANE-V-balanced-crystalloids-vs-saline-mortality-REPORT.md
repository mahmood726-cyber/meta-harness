V-balanced-crystalloids-vs-saline-mortality VERDICTS: NEW 20; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 1; WRONG_* 4; DUPLICATE_OF_ACCOUNTED 10; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 5
automated screen agreed on 0 of 20 verified
r2 includes 28 of 1991; already accounted for 8; NEW 20
All counts on the first three lines are MEASURED.
Verdicts are INFERRED from the quoted snapshot abstracts or saved CT.gov raw registry bodies; no outside trial knowledge and no pooling decision was used.
No PubMed efetch was run because every new PMID record had a non-empty snapshot abstract that did not visibly end mid-record.

## ELIGIBLE_RCT ids with titles
(none)

## DUPLICATE_OF_ACCOUNTED pairs
- 35349397 -> PMID 34375394 (BaSICS; same NCT02875873; secondary exploratory analysis).
- 32882244 -> PMID 29485925 (SMART; secondary analysis of SMART data set).
- 33546622 -> PMID 29485925 (SMART; ancillary biomarker study, NCT02444988).
- 33263702 -> PMID 34375394 (BaSICS statistical analysis plan).
- 31454263 -> PMID 29485925 (SMART sepsis secondary analysis, NCT02444988).
- 28302179 -> PMID 29485925 (SMART protocol article).
- 28651514 -> PMID 34375394 (BaSICS protocol article, NCT02875873).
- 28774642 -> PMID 26444692 (SPLIT post hoc subgroup analysis).
- 28866974 -> PMID 35041780 (PLUS protocol article).
- 25437221 -> PMID 26444692 (SPLIT protocol article).

## Registry-only raw bodies
- NCT03630224: overallStatus=TERMINATED; hasResults=False; conditions=Severe Trauma Patients, Acute Kidney Injury; interventions=Plasmalyte Viaflo, NaCl 0.9% (ctgov api (lane_v/balanced-crystalloids-vs-saline-mortality-raw/NCT03630224.json)).
- NCT03685214: overallStatus=UNKNOWN; hasResults=False; conditions=Sepsis, Acute Kidney Injury, Septic Shock, Sepsis, Severe; interventions=0.9% saline, lactated Ringer's solution (ctgov api (lane_v/balanced-crystalloids-vs-saline-mortality-raw/NCT03685214.json)).
- NCT02875873: overallStatus=COMPLETED; hasResults=False; conditions=Critical Illness, Acute Kidney Injury; interventions=Plasma-Lyte, Saline 0.9%, Slow infusion speed, Fast Infusion Speed (ctgov api (lane_v/balanced-crystalloids-vs-saline-mortality-raw/NCT02875873.json)).
- NCT03277677: overallStatus=COMPLETED; hasResults=False; conditions=Sepsis, Septic Shock, Acute Kidney Injury; interventions=Normal saline, Ringer's Acetate (ctgov api (lane_v/balanced-crystalloids-vs-saline-mortality-raw/NCT03277677.json)).
- NCT01270854: overallStatus=COMPLETED; hasResults=False; conditions=Wounds and Injuries, Multiple Trauma, Disorder of Fluid Balance; interventions=Plasmalyte A, Normal Saline (ctgov api (lane_v/balanced-crystalloids-vs-saline-mortality-raw/NCT01270854.json)).

## Commands run
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `if (Test-Path -LiteralPath F:\ProjectIndex\INDEX.md) { Get-Content -LiteralPath F:\ProjectIndex\INDEX.md -TotalCount 120 } else { Write-Output 'MISSING:F:\ProjectIndex\INDEX.md' }`
- `if (Test-Path -LiteralPath F:\E156\rewrite-workbook.txt) { Get-Content -LiteralPath F:\E156\rewrite-workbook.txt -TotalCount 120 } else { Write-Output 'MISSING:F:\E156\rewrite-workbook.txt' }`
- `if (Test-Path -LiteralPath .\LIVE_CONTEXT.md) { Get-Content -LiteralPath .\LIVE_CONTEXT.md -TotalCount 160 } else { Write-Output 'MISSING:.\LIVE_CONTEXT.md' }`
- `git status --short`
- `Get-Content -LiteralPath .\protocols\balanced-crystalloids-vs-saline-mortality.md`
- `Get-Content -LiteralPath .\topics\balanced-crystalloids-vs-saline-mortality.json`
- `python -c review.json key inspection (failed: outcomes is list, not dict)`
- `python -c legacy include computation using harness.screen and harness.pipeline._dedup`
- `python -c r2 snapshot record/decision count summary`
- `python -c review outcomes inspection (failed: PowerShell newline quoting)`
- `python -c review search/screening/invalidation key inspection`
- `python -c review primary outcome trials/declared_absent extraction`
- `PowerShell here-string piped to python -: compute legacy/accounted/r2 NEW include list (failed first attempt due newline quoting)`
- `PowerShell here-string piped to python -: compute legacy/accounted/r2 NEW include list (success)`
- `PowerShell here-string piped to python -: full new-record dump for title/abstract/screen decisions`
- `PowerShell here-string piped to python -: selected PMID abstract dumps for clipped records`
- `PowerShell here-string piped to python -: NCT snapshot field dump`
- `PowerShell here-string piped to python -: selected PMID abstract dumps for comparator/secondary records`
- `PowerShell here-string piped to python -: selected PMID abstract dumps for protocol/animal records`
- `rg -n "REGISTRY_ONLY_NO_PUBLICATION|NOT_VERIFIED_CAP|quote_source|lane_v" .`
- `rg -n "LANE-[A-Z].*VERDICTS|VERDICTS: NEW|automated screen agreed" .`
- `PowerShell here-string piped to python -: fetch CT.gov v2 JSON for NCT03630224, NCT03685214, NCT02875873, NCT03277677, NCT01270854 into lane_v raw directory`
- `PowerShell here-string piped to python -: parse CT.gov raw status/conditions/interventions/allocation/study type`
- `PowerShell here-string piped to python -: check all new PMID snapshot abstracts non-empty and not visibly truncated`
- `PowerShell here-string piped to python -: attempt to write lane_v JSON/report with assertions (failed quote assertion for 28302179)`
- `PowerShell here-string piped to python -: inspect 28302179 quote around SMART is`
- `PowerShell here-string piped to python -: inspect 28302179 quote around cluster-level/Isotonic/being conducted/SMART`
- `PowerShell here-string piped to python -: write lane_v JSON and this report with assertion checks`
