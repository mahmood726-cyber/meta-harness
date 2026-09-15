V-dpp4-mace-t2d VERDICTS: NEW 208; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 77; NOT_RCT 27; WRONG_* 27; DUPLICATE_OF_ACCOUNTED 17; UNDECIDABLE 0; NOT_VERIFIED_CAP 58; REGISTRY_ONLY 2
automated screen agreed on 77 of 150 verified

r2 includes 213 of 6457; already accounted for 5; NEW 208
MEASURED: legacy includes 5; pooled trials 3; declared-absent trials 2; accounted include records in r2 5.
MEASURED: NEW exceeded 150, so first 150 were verified by year desc, PMID; remaining 58 marked NOT_VERIFIED_CAP.

ELIGIBLE_RCT ids with titles:
- none MEASURED

DUPLICATE_OF_ACCOUNTED pairs:
- 33564423: Same trial as accounted CARMELINA / PMID 30418475.
- 32037653: Same trial as accounted CARMELINA / PMID 30418475.
- 32206483: Same trial as accounted CARMELINA / PMID 30418475.
- 32493335: Same trial as accounted EXAMINE / PMID 23992602.
- 30586723: Same trial as accounted CARMELINA / PMID 30418475.
- 31399442: Same trial as accounted CARMELINA / PMID 30418475.
- 29581078: Same trial as accounted EXAMINE / PMID 23992602.
- 27607571: Same trial as accounted TECOS / PMID 26052984.
- 28246236: Same trial as accounted EXAMINE / PMID 23992602.
- 28432745: Same trial as accounted TECOS / PMID 26052984.
- 27179720: Same trial as accounted EXAMINE / PMID 23992602.
- 27437883: Same trial as accounted TECOS / PMID 26052984.
- 27480840: Same trial as accounted EXAMINE / PMID 23992602.
- 27742728: Same trial as accounted TECOS / PMID 26052984.
- 25552421: Same trial as accounted SAVOR-TIMI 53 / PMID 23992601.
- 25765696: Same trial as accounted EXAMINE / PMID 23992602.
- 24279445: Same trial acronym as accounted SAVOR-TIMI 53 / PMID 23992601.

Commands run:
- `Get-Content -LiteralPath .\LANE_PROMPT.md -Raw`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80 } elseif (Test-Path -LiteralPath '.\LIVE_CONTEXT.md') { Get-Content -LiteralPath '.\LIVE_CONTEXT.md' -Raw }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 120 } elseif (Test-Path -LiteralPath '.\LIVE_CONTEXT.md') { Get-Content -LiteralPath '.\LIVE_CONTEXT.md' -Raw }`
- `git status --short`
- `Get-Content -LiteralPath .\protocols\dpp4-mace-t2d.md -Raw`
- `Get-Content -LiteralPath .\topics\dpp4-mace-t2d.json -Raw`
- `Get-Content -LiteralPath .\docs\reviews\dpp4-mace-t2d\review.json -Raw`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/dpp4-mace-t2d.json',encoding='utf-8')); d=json.load(open('cache/dpp4-mace-t2d/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python - <<'PY' ... (failed in PowerShell; bash heredoc syntax not supported)`
- `@' ... inspect snapshot structure ... '@ | python -`
- `@' ... extract review trials and declared_absent_trials ... '@ | python -`
- `@' ... compute legacy/r2 include/new counts ... '@ | python -`
- `@' ... count r2 include id types/years/interventions ... '@ | python -`
- `@' ... print first/new sorted records and cap boundary ... '@ | python -`
- `@' ... check empty abstracts, NCT-only rows, and truncation ... '@ | python -`
- `@' ... print concise 1-150 table ... '@ | python -`
- `@' ... print detailed first150 chunks 1-150 ... '@ | python -`
- `@' ... print title/PMID/NCT table for first150 ... '@ | python -`
- `@' ... inspect selected abstracts 24,25,26,27,29,41,43,47,49,73,75,79,93,95,101,103,109,112,116,121,122,123,128,136,138,139,141,146 ... '@ | python -`
- `@' ... inspect combination/pooled edge cases ... '@ | python -`
- `@' ... inspect full abstracts for indices 73-80, 101-110, 124-133 ... '@ | python -`
- `@' ... generate lane_v/dpp4-mace-t2d.json, fetch CT.gov raw bodies, and write report ... '@ | python -`

Static-vs-dynamic hardcode disclosure:
| Item | Status | Basis |
|---|---|---|
| Topic slug and snapshot path | Static by lane prompt | INFERRED from LANE_PROMPT.md target. |
| Counts and verdict totals | Dynamic/measured | MEASURED from JSON inputs and generated verdict objects. |
| Verdict decisions | Source-record adjudication | INFERRED from quoted title/abstract/registry spans, not outside trial knowledge. |
| Tail cap | Dynamic/measured | MEASURED NEW=208 > 150; rows 151-208 marked NOT_VERIFIED_CAP. |
