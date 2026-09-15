V-statins-primary-prevention-elderly VERDICTS: NEW 47; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 10; NOT_RCT 10; WRONG_* 24; DUPLICATE_OF_ACCOUNTED 1; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 1
automated screen agreed on 11 of 47 verified
r2 includes 52 of 7086; already accounted for 5; NEW 47
All counts in the first three lines are MEASURED from the stated JSON inputs and the replayed legacy screen command.
Verdict classes are INFERRED from the quoted title, abstract, or saved CT.gov body spans in the JSON table; no pooling decision is made here.

ELIGIBLE_RCT ids with titles
- 8739021 - Effectiveness and safety of low-dose pravastatin and squalene, alone and in combination, in elderly patients with hypercholesterolemia.

DUPLICATE_OF_ACCOUNTED pairs
- NCT02099123 -> PMID 42670961 (STAREE); INFERRED from matching STAREE acronym/NCT in the accounted review object and the NCT snapshot title.

Commands run
- `Get-Content LANE_PROMPT.md`
- `preflight read F drive ProjectIndex INDEX or LIVE_CONTEXT fallback`
- `preflight read F drive E156 rewrite-workbook or LIVE_CONTEXT fallback`
- `git status --short`
- `Get-Content protocols/statins-primary-prevention-elderly.md`
- `Get-Content topics/statins-primary-prevention-elderly.json`
- `Get-Content docs/reviews/statins-primary-prevention-elderly/review.json`
- `python -c legacy include replay command from LANE_PROMPT.md`
- `python -c snapshot and review structure count extraction`
- `python heredoc new include inspection command failed in PowerShell before execution`
- `python -c new include inspection records 1-47`
- `python -c new include inspection records 8-39`
- `python -c new include inspection records 17-24`
- `python -c new include inspection records 25-33`
- `python -c compact title listing with f-string failed before writing files`
- `python -c compact title listing`
- `Get-ChildItem recursive LANE report discovery`
- `Get-Content LANE-AE-REPORT.md first 120 lines`
- `Get-Content LANE-S3-REPORT.md first 120 lines`
- `Get-ChildItem lane_v failed because lane_v did not exist yet`
- `python -c fetch ClinicalTrials.gov API v2 body for NCT01227330`
- `python -c check NEW records for empty or ellipsis-ended abstracts`
- `Get-Content lane_v/statins-primary-prevention-elderly-raw/NCT01227330.json first 20 lines`
- `python -c generate lane JSON and report failed on nested command-string quoting before writing JSON or report`
- `python -c generate lane JSON and report failed on STAREE narrow-space quote needle before writing JSON or report`
- `python -c generate lane JSON and report`
- `python -c validate lane JSON/report finish condition`
- `git status --short`

No commit was made.
