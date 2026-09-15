V-esketamine-trd-madrs VERDICTS: NEW 20; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 13; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 2; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 5
automated screen agreed on 0 of 20 verified
r2 includes 33 of 1145; already accounted for 13; NEW 20
Counts are MEASURED from cache/esketamine-trd-madrs/snapshots/2026-09-15r2-search_v2/records.json, docs/reviews/esketamine-trd-madrs/review.json, and the legacy harness.screen command.

ELIGIBLE_RCT ids with titles:
- None MEASURED.

DUPLICATE_OF_ACCOUNTED pairs:
- 31290965 -> NCT02417064 / TRANSFORM-1 (accounted)
- 29282469 -> NCT01998958 / SYNAPSE declared-absent (accounted)

Verdict table:
| id | verdict | screen_agrees | note |
|---|---|---:|---|
| NCT07716098 | REGISTRY_ONLY_NO_PUBLICATION | false | NCT-only registry record; not a publication report. |
| 41245530 | NOT_RCT | false | secondary analysis using TRANSFORM-2 plus an rTMS trial; not an independent esketamine-vs-placebo RCT report. |
| 38557430 | NOT_RCT | false | secondary analysis of already-accounted TRANSFORM/SUSTAIN studies. |
| 36273682 | NOT_RCT | false | post hoc pooled analysis of already-accounted TRANSFORM-1/2 trials. |
| 37019044 | NOT_RCT | false | post hoc pooled predictor analysis of already-accounted trials. |
| 37158911 | NOT_RCT | false | secondary HRQoL analysis of accounted TRANSFORM-2. |
| 34973081 | NOT_RCT | false | post hoc sex subgroup analysis of already-accounted TRANSFORM trials. |
| 35441931 | NOT_RCT | false | post hoc item-level symptom analysis of accounted TRANSFORM-2. |
| 35596932 | NOT_RCT | false | exploratory factor analysis of an already-accounted Japanese trial. |
| 32860422 | NOT_RCT | false | benefit-risk post hoc analysis across accounted induction and maintenance studies. |
| 34235612 | NOT_RCT | false | nasal tolerability analysis across four accounted/maintenance studies, not an independent trial. |
| 34288609 | NOT_RCT | false | pooled post hoc analysis of TRANSFORM studies. |
| 34293233 | NOT_RCT | false | post hoc comorbid-anxiety analysis of accounted TRANSFORM-2. |
| 30685564 | NOT_RCT | false | assessment-method substudy of declared-absent NCT01998958, not an independent trial. |
| 31290965 | DUPLICATE_OF_ACCOUNTED | false | same trial as accounted TRANSFORM-1 / NCT02417064. |
| NCT03852160 | REGISTRY_ONLY_NO_PUBLICATION | false | NCT-only registry record; CT.gov status is withdrawn, so it cannot be a pooled publication report. |
| 29282469 | DUPLICATE_OF_ACCOUNTED | false | same trial as accounted declared-absent SYNAPSE / NCT01998958. |
| NCT03434041 | REGISTRY_ONLY_NO_PUBLICATION | false | NCT-only registry record for a trial already represented by a publication; the record itself is not a publication report. |
| NCT02918318 | REGISTRY_ONLY_NO_PUBLICATION | false | NCT-only registry record for the Japanese trial; the record itself is not a publication report. |
| NCT02418585 | REGISTRY_ONLY_NO_PUBLICATION | false | NCT-only registry record for TRANSFORM-2; the record itself is not a publication report. |

Commands run:
- `Get-Content -LiteralPath .\LANE_PROMPT.md -Raw` (MEASURED lane prompt).
- `if (Test-Path -LiteralPath .\LIVE_CONTEXT.md) { Get-Content -LiteralPath .\LIVE_CONTEXT.md -Raw } else { Write-Output 'LIVE_CONTEXT.md not found' }` (MEASURED local live context absence).
- `git status --short` (MEASURED initial dirty worktree).
- `Test-Path/Get-Content` checks for `F:\ProjectIndex\INDEX.md`, `F:\E156\rewrite-workbook.txt`, `C:\ProjectIndex\INDEX.md`, and `C:\E156\rewrite-workbook.txt` (MEASURED session-start context; read-only).
- `Get-Content -LiteralPath .\protocols\esketamine-trd-madrs.md -Raw` (MEASURED PICO/eligibility).
- `Get-Content -LiteralPath .\topics\esketamine-trd-madrs.json -Raw` (MEASURED topic config).
- `Get-Content -LiteralPath .\docs\reviews\esketamine-trd-madrs\review.json -Raw` (MEASURED review object; terminal output truncated, followed by structured reads).
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; ..."` (MEASURED legacy includes exactly as lane prompt requested).
- Three initial `python - <<'PY'` heredoc attempts failed under PowerShell before any data change (MEASURED shell incompatibility).
- `@'...'@ | python -` structured reads of review trials/declared_absent, snapshot shape, and legacy include count (MEASURED).
- `@'...'@ | python -` denominator computation for r2 includes/accounted/NEW (MEASURED).
- `@'...'@ | python -` candidate abstract dump for the 20 NEW records (MEASURED).
- `rg -n "NCT07716098|NCT03852160|NCT03434041|NCT02918318|NCT02418585" .\cache .\topics .\docs -g "*.json"` (MEASURED cache search for richer registry text).
- `@'...'@ | python -` focused abstract dump for PMIDs 32860422, 35441931, and 35596932 (MEASURED).
- `@'...'@ | python -` CT.gov API fetch for NCT07716098, NCT03852160, NCT03434041, NCT02918318, and NCT02418585; wrote HTTP bodies under `lane_v/esketamine-trd-madrs-raw/` (MEASURED).
- `@'...'@ | python -` CT.gov raw-body field spot-check for status/conditions/interventions (MEASURED).
- One artifact generation attempt stopped on a quote encoding mismatch before writing the report/JSON (MEASURED).
- `@'...'@ | python -` generated `lane_v/esketamine-trd-madrs.json` and this report from measured inputs plus manual verdict mapping (MEASURED counts; verdict interpretation INFERRED from quoted records).
- `@'...'@ | python -` finish-condition validation: JSON length, verdict vocabulary, non-empty quotes, first-line sum, and raw-file count (MEASURED PASS).
- `Get-Content -LiteralPath .\LANE-V-esketamine-trd-madrs-REPORT.md -TotalCount 40` (MEASURED report first lines/table preview).
- `Get-ChildItem -LiteralPath .\lane_v -Recurse | Select-Object FullName,Length` (MEASURED lane artifact/raw-body inventory).
- `git status --short` (MEASURED post-write dirty worktree).
- `Get-Content -LiteralPath .\LANE-V-esketamine-trd-madrs-REPORT.md -Tail 25` (MEASURED command-log tail before this report-only update).
- Final planned recheck after this command-log update: `@'...'@ | python -` validation plus `git status --short` and `Get-Content -LiteralPath .\LANE-V-esketamine-trd-madrs-REPORT.md -TotalCount 3` (MEASURED/expected).
