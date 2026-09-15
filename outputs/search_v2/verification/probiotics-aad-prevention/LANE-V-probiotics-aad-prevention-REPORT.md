V-probiotics-aad-prevention VERDICTS: NEW 17; ELIGIBLE_RCT 8; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 0; WRONG_* 0; DUPLICATE_OF_ACCOUNTED 5; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 4
automated screen agreed on 8 of 17 verified
r2 includes 70 of 2072; already accounted for 53; NEW 17
All counts in the three lines above are MEASURED from the named repo inputs.

## ELIGIBLE_RCT ids with titles
- 28482385 ? [A multicenter randomized controlled study of Saccharomyces boulardii in the prevention of antibiotic-associated diarrhea in infants and young children].
- 28592037 ? [A prospective control study of Saccharomyces boulardii in prevention of antibiotic-associated diarrhea in the older inpatients].
- 23302558 ? [Multicenter, randomized, controlled clinical trial on preventing antibiotic-associated diarrhea in children with pneumonia using the live Clostridium butyricum and Bifidobacterium combined Powder].
- 19652108 ? A randomized clinical trial measuring the influence of kefir on antibiotic-associated diarrhea: the measuring the influence of Kefir (MILK) Study.
- 17803164 ? [Probiotics as prophylactic agents against antibiotic-associated diarrhea in hospitalized patients].
- 18252070 ? Does eating yogurt prevent antibiotic-associated diarrhoea? A placebo-controlled randomised controlled trial in general practice.
- 14608267 ? [Prevention of antibiotic-associated diarrhea with Lactobacillus sporogens and fructo-oligosaccharides in children. A multicentric double-blind vs placebo study].
- 12403254 ? Prevention of antibiotic-associated diarrhea in infants by probiotics.

## DUPLICATE_OF_ACCOUNTED pairs
- NCT03334604 ? Same NCT03334604 as pooled PMID 35727573.
- NCT02765217 ? Same NCT02765217 as pooled PMID 40488914.
- NCT02871908 ? Same NCT02871908 as declared-absent PMID 28057659.
- NCT01143272 ? Same NCT01143272 as pooled PMID 26973849.
- NCT00958308 ? Same NCT00958308 as declared-absent PMID 20145608.

## Registry-only rows
- NCT02462590 ? REGISTRY_ONLY_NO_PUBLICATION; INFERRED no publication from id_type=nct and empty pmid in the snapshot record.
- NCT01782755 ? REGISTRY_ONLY_NO_PUBLICATION; INFERRED no publication from id_type=nct and empty pmid in the snapshot record.
- NCT01972932 ? REGISTRY_ONLY_NO_PUBLICATION; INFERRED no publication from id_type=nct and empty pmid in the snapshot record.
- NCT01596829 ? REGISTRY_ONLY_NO_PUBLICATION; INFERRED no publication from id_type=nct and empty pmid in the snapshot record.

## Raw HTTP bodies
- No PubMed efetch or other HTTP retrieval was run for this lane; the raw-body directory is intentionally empty (MEASURED).

## Commands run
1. `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
2. `Get-Content -Raw -LiteralPath .\LIVE_CONTEXT.md (failed: file not found)`
3. `git status --short`
4. `Test-Path -LiteralPath F:\ProjectIndex\INDEX.md; if (Test-Path -LiteralPath F:\ProjectIndex\INDEX.md) { Get-Content -LiteralPath F:\ProjectIndex\INDEX.md -TotalCount 80 }`
5. `Test-Path -LiteralPath F:\E156\rewrite-workbook.txt; if (Test-Path -LiteralPath F:\E156\rewrite-workbook.txt) { Get-Content -LiteralPath F:\E156\rewrite-workbook.txt -TotalCount 80 }`
6. `Test-Path -LiteralPath C:\ProjectIndex\INDEX.md; if (Test-Path -LiteralPath C:\ProjectIndex\INDEX.md) { Get-Content -LiteralPath C:\ProjectIndex\INDEX.md -TotalCount 80 }`
7. `Test-Path -LiteralPath C:\E156\rewrite-workbook.txt; if (Test-Path -LiteralPath C:\E156\rewrite-workbook.txt) { Get-Content -LiteralPath C:\E156\rewrite-workbook.txt -TotalCount 80 }`
8. `Get-Content -Raw -LiteralPath .\protocols\probiotics-aad-prevention.md`
9. `Get-Content -Raw -LiteralPath .\topics\probiotics-aad-prevention.json`
10. `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/probiotics-aad-prevention.json',encoding='utf-8')); d=json.load(open('cache/probiotics-aad-prevention/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
11. `python -c review-json quick probe for top-level declared_absent_trials (failed: outcomes is list, not dict)`
12. `python -c review-json type/key probe`
13. `python -c r2 snapshot structure/count probe`
14. `python -c legacy records structure probe`
15. `python -c review outcomes/declared_absent probe`
16. `python -c legacy/r2 include count and first include probe`
17. `rg --files`
18. `python -c recursive review path probe for trials/declared_absent fields`
19. `python -c primary outcome pooled trial id extraction`
20. `python -c review screening object probe`
21. `python -c compute NEW includes (failed: def statement inside one-line -c syntax)`
22. `python -c primary declared_absent_trials extraction`
23. `PowerShell here-string piped to python: compute r2 include/accounted/NEW population and print NEW records`
24. `python -c print full NCT-only NEW snapshot records`
25. `python -c inspect r2 raw/INDEX.json`
26. `python -c inspect r2 retrieval_ledger.json`
27. `PowerShell here-string piped to python: find accounted records sharing NEW NCT ids`
28. `PowerShell here-string piped to python: check NEW PMID rows for accounted NCT duplicates`
29. `Test-Path -LiteralPath .\lane_v; if (Test-Path -LiteralPath .\lane_v) { Get-ChildItem -LiteralPath .\lane_v -Recurse | Select-Object FullName,Length }`
30. `python -c print full NEW PMID records and screening decisions`
31. `PowerShell here-string piped to python: write lane artifacts and validate finish condition (failed: quote guard for PMID 28482385)`
32. `PowerShell here-string piped to python: write lane_v/probiotics-aad-prevention.json, create lane_v/probiotics-aad-prevention-raw/, write LANE-V-probiotics-aad-prevention-REPORT.md, and validate finish condition`
