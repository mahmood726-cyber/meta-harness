V-finerenone-ckd-t2d-renal VERDICTS: NEW 39; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 1; NOT_RCT 25; WRONG_* 4; DUPLICATE_OF_ACCOUNTED 6; UNDECIDABLE 3; NOT_VERIFIED_CAP 0
automated screen agreed on 1 of 39 verified
r2 includes 45 of 2794; already accounted for 6; NEW 39
Counts and identifiers on the preceding lines are MEASURED from the named JSON inputs.
INFERRED: verdict labels interpret the quoted title/abstract spans under the protocol PICO; no outside trial knowledge was used.
Raw HTTP bodies relied on: none (MEASURED); no PMID record had an empty or truncated snapshot abstract, and registry-only empty abstracts had no PMID to efetch.

ELIGIBLE_RCT ids with titles (could move the pool)
- none (MEASURED)

DUPLICATE_OF_ACCOUNTED pairs
- 36583355 -> Same NCT/acronym as the declared-absent ARTS-DN trial PMID 26325557.
- 28025025 -> Same ARTS-DN Japan trial already declared absent as NCT01968668.
- NCT02540993 -> Same NCT as pooled FIDELIO-DKD PMID 33264825.
- NCT02545049 -> Same NCT as pooled FIGARO-DKD PMID 34449181.
- 25591469 -> Same NCT/acronym as the declared-absent ARTS-DN trial PMID 26325557; this is a design/baseline article.
- NCT01874431 -> Same NCT/acronym as the declared-absent ARTS-DN trial PMID 26325557.

Commands run
- Get-Content -Raw -LiteralPath .\LANE_PROMPT.md
- if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md' } elseif (Test-Path -LiteralPath 'C:\ProjectIndex\INDEX.md') { Get-Content -Raw -LiteralPath 'C:\ProjectIndex\INDEX.md' } else { Write-Output 'INDEX_NOT_FOUND' }
- if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt' } elseif (Test-Path -LiteralPath 'C:\E156\rewrite-workbook.txt') { Get-Content -Raw -LiteralPath 'C:\E156\rewrite-workbook.txt' } else { Write-Output 'WORKBOOK_NOT_FOUND' }
- git status --short
- Get-Content -Raw -LiteralPath .\protocols\finerenone-ckd-t2d-renal.md
- Get-Content -Raw -LiteralPath .\topics\finerenone-ckd-t2d-renal.json
- Get-Content -Raw -LiteralPath .\docs\reviews\finerenone-ckd-t2d-renal\review.json
- python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/finerenone-ckd-t2d-renal.json',encoding='utf-8')); d=json.load(open('cache/finerenone-ckd-t2d-renal/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))\"
- python -c \"import json; p='cache/finerenone-ckd-t2d-renal/snapshots/2026-09-15r2-search_v2/records.json'; d=json.load(open(p,encoding='utf-8')); print top-level record and decision counts\"
- python -c \"import json; d=json.load(open('docs/reviews/finerenone-ckd-t2d-renal/review.json',encoding='utf-8')); print primary outcome trials and declared_absent_trials\"
- python -c \"import json; d=json.load(open('cache/finerenone-ckd-t2d-renal/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); print record_keys and decision_keys\"
- rg -n \"declared_absent|absent_trials|declared\" .\docs\reviews\finerenone-ckd-t2d-renal\review.json
- python -c \"import json; d=json.load(open('docs/reviews/finerenone-ckd-t2d-renal/review.json',encoding='utf-8')); print absent/trial top keys\"
- python -c \"import json; d=json.load(open('docs/reviews/finerenone-ckd-t2d-renal/review.json',encoding='utf-8')); print outcome-level trials and declared_absent_trials\"
- python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; print legacy include tuples with rule/span\"
- python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; compute accounted set and sorted NEW include list\"
- python -c \"import json,sys,textwrap; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; print all NEW include records with abstracts (first broad pass; output truncated by console)\"
- python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; print NEW include records 1-15 with full abstracts\"
- python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; print NEW include records 16-30 with full abstracts\"
- python -c \"import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; print NEW include records 31-39 with full abstracts\"
- python -c \"import json; snap=json.load(open('cache/finerenone-ckd-t2d-renal/snapshots/2026-09-15r2-search_v2/records.json',encoding='utf-8')); print records 38089437 and 34580995\"
- python -c \"import json,sys,re; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; print abstract tail checks for NEW include records\"
- python -c \"import json; d=json.load(open('cache/finerenone-ckd-t2d-renal/records.json',encoding='utf-8')); ids={...}; print matching legacy records\"  # failed: legacy cache shape was wrapped, not a bare list
- python -c \"import json; raw=json.load(open('cache/finerenone-ckd-t2d-renal/records.json',encoding='utf-8')); d=raw.get('records', raw) if isinstance(raw,dict) else raw; print matching legacy records\"
- if (Test-Path -LiteralPath .\lane_v) { Get-ChildItem -Recurse -Force -LiteralPath .\lane_v | Select-Object FullName,Length } else { Write-Output 'lane_v_absent' }
- PowerShell here-string piped to python - (artifact writer: recomputed population, asserted quotes/counts, wrote lane_v JSON/raw dir/report)
