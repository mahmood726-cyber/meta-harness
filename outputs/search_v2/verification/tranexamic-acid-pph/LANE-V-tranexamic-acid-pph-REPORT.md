V-tranexamic-acid-pph VERDICTS: NEW 9; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 0; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 7; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 2
automated screen agreed on 0 of 9 verified
r2 includes 13 of 1162; already accounted for 4; NEW 9
Numbers in the first three lines are MEASURED from the r2 snapshot, legacy screen replay, and served-review primary-outcome accounted lists.
Verification cap: NOT_VERIFIED_CAP 0 because NEW 9 is below the 150-record cap (MEASURED).

## ELIGIBLE_RCT ids with titles
None (MEASURED).

## DUPLICATE_OF_ACCOUNTED pairs
| NEW id | Accounted trial | Basis |
|---|---|---|
| 31223662 | pooled PMID 28456509 | same NCT00872469/WOMAN; sub-study publication |
| 29879947 | pooled PMID 28456509 | same NCT00872469/WOMAN; exploratory subgroup analysis |
| 30345385 | pooled PMID 28456509 | same NCT00872469/WOMAN; WOMAN-ETAC sub-study |
| 27188698 | pooled PMID 28456509 | same NCT00872469/WOMAN; SAP/protocol update |
| NCT02805426 | declared-absent PMID 32143721 | same NCT02805426 oral TXA adjunct trial |
| 20398351 | pooled PMID 28456509 | same NCT00872469/WOMAN; protocol paper |
| NCT00872469 | pooled PMID 28456509 | same NCT00872469/WOMAN registry record |
Duplicate pairings are MEASURED from snapshot NCT/acronym fields plus the primary-outcome pooled/declared-absent lists; the label "sub-study" is INFERRED from the quoted abstract wording.

## Verdict Table
| id | verdict | screen_rule | screen_agrees | note |
|---|---|---|---|---|
| NCT07362992 | REGISTRY_ONLY_NO_PUBLICATION | INCLUDE | false | NCT-only r2 record with no PMID; this is a recruiting registry record, not a publication report. |
| NCT05448456 | REGISTRY_ONLY_NO_PUBLICATION | INCLUDE | false | NCT-only r2 record with no PMID; this is a completed registry record, not a publication report. |
| 31223662 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT00872469/WOMAN trial as pooled PMID 28456509; this is the WOMAN-ETAPlaT sub-study. |
| 29879947 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT00872469/WOMAN trial as pooled PMID 28456509; this is an exploratory subgroup analysis of the accounted trial. |
| 30345385 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT00872469/WOMAN trial as pooled PMID 28456509; this is the WOMAN-ETAC sub-study. |
| 27188698 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT00872469/WOMAN trial as pooled PMID 28456509; this is a protocol update and statistical analysis plan. |
| NCT02805426 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT02805426 trial as declared-absent PMID 32143721. |
| 20398351 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT00872469/WOMAN trial as pooled PMID 28456509; this is the protocol paper. |
| NCT00872469 | DUPLICATE_OF_ACCOUNTED | INCLUDE | false | Same NCT00872469/WOMAN trial as pooled PMID 28456509. |

## Raw HTTP bodies
- lane_v/tranexamic-acid-pph-raw/ctgov-NCT05448456.json (MEASURED saved HTTP body).
- lane_v/tranexamic-acid-pph-raw/ctgov-NCT07362992.json (MEASURED saved HTTP body).
- No PubMed efetch body was fetched because every NEW PubMed record had a non-empty snapshot abstract adequate for the verdict (MEASURED).

## Commands run
1. `Get-Content -LiteralPath .\LANE_PROMPT.md`
2. `Get-Content -LiteralPath .\LIVE_CONTEXT.md (failed: file not found)`
3. `Get-Content -LiteralPath F:\ProjectIndex\INDEX.md`
4. `Get-Content -LiteralPath F:\E156\rewrite-workbook.txt`
5. `git status --short`
6. `Get-Content -LiteralPath .\protocols\tranexamic-acid-pph.md`
7. `Get-Content -LiteralPath .\topics\tranexamic-acid-pph.json`
8. `Get-Content -LiteralPath .\docs\reviews\tranexamic-acid-pph\review.json`
9. `python -c "import json,sys; sys.path.insert(0,.\u001a); from harness import screen; from harness.pipeline import _dedup; ... print legacy includes"`
10. `python -c "... inspect r2/review JSON shape ..."`
11. `python -c "... measure r2 includes/accounted/NEW and list NEW records ..."`
12. `python -c "... inspect the 9 NEW records and screen decisions ..."`
13. `Get-ChildItem -LiteralPath .\cache\tranexamic-acid-pph\snapshots\2026-09-15r2-search_v2 -Force`
14. `Get-ChildItem -LiteralPath .\cache\tranexamic-acid-pph -Force`
15. `rg -n "overall_status|overallStatus|NCT07362992|NCT05448456|NCT02805426|NCT00872469" .\cache\tranexamic-acid-pph .\docs\reviews\tranexamic-acid-pph`
16. `Get-ChildItem -LiteralPath .\cache\tranexamic-acid-pph\snapshots\2026-09-15r2-search_v2\raw -Force`
17. `python -c "... print full snapshot abstracts for 31223662, 29879947, 30345385, 27188698, 20398351 ..."`
18. `python -c "... check NCT00872469/WOMAN tokens in NEW PMID abstracts ..."`
19. `python -c "... fetch CT.gov JSON for NCT05448456 and NCT07362992 into lane_v/tranexamic-acid-pph-raw/ ..."`
20. `python -c "... parse saved CT.gov raw bodies for overallStatus/conditions/interventions ..."`
21. `Test-Path -LiteralPath .\lane_v\tranexamic-acid-pph.json`
22. `Test-Path -LiteralPath .\LANE-V-tranexamic-acid-pph-REPORT.md`
23. `Get-ChildItem -LiteralPath .\lane_v -Force`
24. `@\'...\'@ | python -  (write final lane JSON and report)`
25. `python -c "... validate lane finish condition and report first-line sum ..."`
26. `git status --short`
