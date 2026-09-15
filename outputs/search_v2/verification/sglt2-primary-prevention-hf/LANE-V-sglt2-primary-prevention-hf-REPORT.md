V-sglt2-primary-prevention-hf VERDICTS: NEW 523; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 52; NOT_RCT 42; WRONG_* 29; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 0; NOT_VERIFIED_CAP 373; REGISTRY_ONLY 27
automated screen agreed on 52 of 150 verified

r2 includes 543 of 15569; already accounted for 20; NEW 523 (MEASURED)
cap rule applied: first 150 by (year desc, pmid/nct/doi/id) verified; 373 marked NOT_VERIFIED_CAP (MEASURED)
All numbers in this report are MEASURED from the stated cache/review files; non-numeric verdict interpretation is INFERRED from the quoted record spans.

## ELIGIBLE_RCT ids with titles
- None (MEASURED 0).

## DUPLICATE_OF_ACCOUNTED pairs
- None (MEASURED 0).

## Category Counts
- ELIGIBLE_RCT: 0 (MEASURED)
- ELIGIBLE_RCT_NO_PRIMARY: 52 (MEASURED)
- NOT_RCT: 42 (MEASURED)
- WRONG_POPULATION: 18 (MEASURED)
- WRONG_INTERVENTION: 10 (MEASURED)
- WRONG_COMPARATOR: 1 (MEASURED)
- WRONG_OUTCOME_ONLY: 0 (MEASURED)
- DUPLICATE_OF_ACCOUNTED: 0 (MEASURED)
- UNDECIDABLE_FROM_RECORD: 0 (MEASURED)
- NOT_VERIFIED_CAP: 373 (MEASURED)
- REGISTRY_ONLY_NO_PUBLICATION: 27 (MEASURED)

## Commands Run
1. `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
2. `if (Test-Path -LiteralPath .\LIVE_CONTEXT.md) { Get-Content -Raw -LiteralPath .\LIVE_CONTEXT.md }`
3. `Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md'`
4. `Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt'`
5. `git status --short`
6. `Get-Content -Raw -LiteralPath .\protocols\sglt2-primary-prevention-hf.md`
7. `Get-Content -Raw -LiteralPath .\topics\sglt2-primary-prevention-hf.json`
8. `Get-Content -Raw -LiteralPath .\docs\reviews\sglt2-primary-prevention-hf\review.json`
9. `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/sglt2-primary-prevention-hf.json',encoding='utf-8')); d=json.load(open('cache/sglt2-primary-prevention-hf/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
10. `python -c "...compute new includes and print first records..." (failed: PowerShell quoting produced a Python SyntaxError)`
11. `python -c @' ... '@ (failed: PowerShell stripped f-string quotes)`
12. `$code = @' print("quote test") '@; python -c $code (failed: PowerShell stripped quotes)`
13. `python -c 'print("quote test")' (failed: PowerShell stripped quotes)`
14. `python -c "print('quote test')" with shell=cmd (failed: command quoting mismatch)`
15. `cmd /c python -c "print('quote test')"`
16. `$code here-string -> base64 -> cmd /c python -c "import base64;exec(...)" quote-preservation test`
17. `base64-wrapped Python diagnostic: compute N, print first 150 capped records with abstracts`
18. `base64-wrapped Python diagnostic: print structured fields for first NCT-only records`
19. `base64-wrapped Python diagnostic: print capped records 1-80`
20. `base64-wrapped Python diagnostic: print capped records 31-60`
21. `base64-wrapped Python diagnostic: print capped records 61-100`
22. `base64-wrapped Python diagnostic: print capped records 101-150`
23. `base64-wrapped Python diagnostic: reprint capped records 26-30 and 123-124`
24. `base64-wrapped Python diagnostic: check first-150 PubMed abstracts needing efetch`
25. `rg --files -g "*.json" lane_v .`
26. `PowerShell here-string piped to cmd /c python - stdin quote-preservation test`
27. `PowerShell here-string piped to cmd /c python - (this artefact writer and self-validator)`

## Raw HTTP Bodies
- No PubMed efetch was needed: all first-150 PubMed records had non-empty, non-truncated snapshot abstracts (MEASURED).
- No new HTTP body was relied on; `lane_v/sglt2-primary-prevention-hf-raw/` was created empty for the lane artefact contract (MEASURED).
