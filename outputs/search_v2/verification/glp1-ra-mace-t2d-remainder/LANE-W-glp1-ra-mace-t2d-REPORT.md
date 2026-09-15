W-glp1-ra-mace-t2d VERDICTS: NEW 451; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 143; NOT_RCT 43; WRONG_* 24; DUPLICATE_OF_ACCOUNTED 17; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 224
automated screen agreed on 143 of 451 verified
r2 includes 610 of 12243; already accounted for 9; NEW 601 (MEASURED overall by original lane definition)
first-lane NOT_VERIFIED_CAP remainder 451; JSON objects 451 (MEASURED remainder population for W-lane)
PubMed capped records with empty snapshot abstracts 0; PubMed efetch XML files written 0 (MEASURED)
All numeric counts above are MEASURED from the named JSON sources; verdict assignment is INFERRED from the quoted title/abstract/structured snapshot record text.

## ELIGIBLE_RCT ids with titles
- none (MEASURED)

## DUPLICATE_OF_ACCOUNTED pairs
- 31806653 -> EXSCEL accounted PMID 28910237; quote: Within-Trial Evaluation of Medical Resources, Costs, and Quality of Life Among Patients With Type 2 Diabetes Participating in the Exenatide Study of Cardiovascular Event Lowering (EXSCEL).
- 32132141 -> LEADER accounted PMID 27295427; quote: CLINICAL TRIAL REGISTRY NAME AND REGISTRATION NUMBER: ClinicalTrials.gov; NCT01179048 (https://clinicaltrials.gov/ct2/show/NCT01179048).
- 32227613 -> SUSTAIN-6 accounted PMID 27633186; quote: Clinicaltrials.gov: NCT01720446 (SUSTAIN 6).
- 32562683 -> REWIND accounted PMID 31189511; quote: The REWIND trial is registered with ClinicalTrials.gov, NCT01394952.
- 32744418 -> LEADER accounted PMID 27295427; quote: Effects of glucagon-like peptide-1 receptor agonists liraglutide and semaglutide on cardiovascular and renal outcomes across body mass index categories in type 2 diabetes: Results of the LEADER and SUSTAIN 6 trials.
- 33239067 -> REWIND accounted PMID 31189511; quote: Unique Identifier NCT01394952).
- 31189509 -> REWIND accounted PMID 31189511; quote: This trial is registered with ClinicalTrials.gov, number NCT01394952.
- 31399438 -> LEADER accounted PMID 27295427; quote: Effects of Liraglutide Compared With Placebo on Events of Acute Gallbladder or Biliary Disease in Patients With Type 2 Diabetes at High Risk for Cardiovascular Events in the LEADER Randomized Trial.
- 31721979 -> LEADER accounted PMID 27295427; quote: TRIAL REGISTRATION: ClinicalTrials.gov identifier: NCT01179048.
- 29898902 -> LEADER accounted PMID 27295427; quote: RESEARCH DESIGN AND METHODS: LEADER (NCT01179048) was an international, phase 3b, randomized, double-blind, controlled trial.
- 30072400 -> LEADER accounted PMID 27295427; quote: RESEARCH DESIGN AND METHODS: The LEADER trial (NCT01179048) was a randomized, double-blind, multicenter, CV outcomes trial assessing liraglutide (1.8 mg/day) versus placebo, in addition to standard of care, for up to 5 years.
- 30292589 -> ELIXA declared-absent PMID 26630143; quote: The ELIXA trial is registered with ClinicalTrials.gov, number NCT01147250, and is completed.
- 30566004 -> LEADER accounted PMID 27295427; quote: Unique identifier: NCT01179048.
- 30566006 -> LEADER accounted PMID 27295427; quote: Unique identifier: NCT01179048.
- 28476871 -> LEADER accounted PMID 27295427; quote: Amylase, Lipase, and Acute Pancreatitis in People With Type 2 Diabetes Treated With Liraglutide: Results From the LEADER Randomized Trial.
- 28854085 -> LEADER accounted PMID 27295427; quote: (Funded by Novo Nordisk and the National Institutes of Health; LEADER ClinicalTrials.gov number, NCT01179048 .).
- 25656058 -> LEADER accounted PMID 27295427; quote: LEADER 2: baseline calcitonin in 9340 people with type 2 diabetes enrolled in the Liraglutide Effect and Action in Diabetes: Evaluation of cardiovascular outcome Results (LEADER) trial: preliminary observations.

## Commands Run
- `Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md'`
- `Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt'`
- `Get-Content -LiteralPath 'LANE_PROMPT.md' -Raw`
- `Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80`
- `Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 120`
- `git status --short`
- `Get-Content -LiteralPath 'protocols\glp1-ra-mace-t2d.md' -Raw`
- `Get-Content -LiteralPath 'topics\glp1-ra-mace-t2d.json' -Raw`
- `Get-Content -LiteralPath 'docs\reviews\glp1-ra-mace-t2d\review.json' -Raw`
- `Get-Content -LiteralPath 'C:\meta-harness\outputs\search_v2\verification\glp1-ra-mace-t2d\glp1-ra-mace-t2d.json' -Raw`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; ... print legacy includes"`
- `python -c "... summarize r2 snapshot keys/counts ..."`
- `python -c "... summarize served review outcomes/declared_absent ..."`
- `python -c "... count previous lane verdicts and NOT_VERIFIED_CAP ids ..."`
- `python -c "... count cap id_type/year distribution ..."`
- `python -c "... inspect primary outcome trials and declared_absent_trials ..."`
- `python -c "... count r2 screening decisions ..."`
- `python -c "... confirm all cap ids exist in r2 records ..."`
- `PowerShell here-string piped to python - (inspect representative NCT/PMID records; print first 80 cap rows; count empty PubMed abstracts)`
- `python -c '... first compact cap table attempt ...' (failed due PowerShell quoting; no files written)`
- `PowerShell here-string piped to python - (print first 80 cap records)`
- `PowerShell here-string piped to python - (print all capped PMID titles/pubtypes)`
- `PowerShell here-string piped to python - (print capped PMID titles for 2017-2013)`
- `PowerShell here-string piped to python - (draft classifier counts/samples)`
- `PowerShell here-string piped to python - (debug over-broad NOT_RCT term hits)`
- `PowerShell here-string piped to python - (refined classifier counts/all PMID decisions)`
- `PowerShell here-string piped to python - (debug standalone MACE false positives and active comparators)`
- `PowerShell here-string piped to python - (final refined counts for wrong/duplicate/not-rct classes)`
- `Get-ChildItem -Force -LiteralPath 'lane_v' -ErrorAction SilentlyContinue`
- `PowerShell here-string piped to python - (first generation attempt; failed closed on accounted-label assertion; no files written)`
- `PowerShell here-string piped to python - (debug measured counts/accounted identifiers after failed generation)`
- `PowerShell here-string piped to python - (generate lane_v/glp1-ra-mace-t2d.json, lane_v/glp1-ra-mace-t2d-raw/, and this report)`
- `PowerShell here-string piped to python - (validate lane JSON/report counts, quotes, schema, and empty raw dir)`
- `Get-Content -LiteralPath 'LANE-W-glp1-ra-mace-t2d-REPORT.md' -TotalCount 12`
- `apply_patch (record the report first-lines inspection command in Commands Run)`
- `PowerShell here-string piped to python - (final validation after report command-list update)`
- `git status --short`

## Verification Notes
- `lane_v/glp1-ra-mace-t2d.json` contains exactly the 451 previous-lane `NOT_VERIFIED_CAP` objects, with no `NOT_VERIFIED_CAP` verdicts remaining.
- `lane_v/glp1-ra-mace-t2d-raw/` was created; no PubMed XML was fetched because every capped PubMed record had a non-empty snapshot abstract.
