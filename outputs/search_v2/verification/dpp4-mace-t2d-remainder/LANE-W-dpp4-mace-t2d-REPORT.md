W-dpp4-mace-t2d VERDICTS: NEW 58; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 51; NOT_RCT 3; WRONG_* 1; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 3
automated screen agreed on 51 of 58 verified

MEASURED full r2 population: r2 includes 213 of 6457; already accounted for 5; NEW 208.
MEASURED W-lane remainder: first-lane NOT_VERIFIED_CAP objects 58; this report verifies all 58.
MEASURED first-lane source: C:/meta-harness/outputs/search_v2/verification/dpp4-mace-t2d/dpp4-mace-t2d.json contained 58 NOT_VERIFIED_CAP rows.

ELIGIBLE_RCT ids with titles (could move the pool):
- None MEASURED.

DUPLICATE_OF_ACCOUNTED pairs:
- None MEASURED.

Verdict notes:
- MEASURED ELIGIBLE_RCT_NO_PRIMARY rows are eligible DPP-4/placebo RCT records whose abstracts report glycemic, pharmacodynamic, renal, endothelial, pharmacokinetic, tolerability, or safety endpoints rather than protocol 3-point MACE.
- MEASURED NOT_RCT rows: 21323504, 21680990, 20463416.
- MEASURED WRONG_* row: 20637971 (healthy-volunteer phase I population).
- MEASURED REGISTRY_ONLY rows: NCT01703286, NCT00614939, NCT00870194; CT.gov API JSON saved in lane_v/dpp4-mace-t2d-raw/.
- INFERRED: no pooling decision is made here; any pool movement is left to the integrator.

Commands run:
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `git status --short`
- `Get-Content -LiteralPath F:\ProjectIndex\INDEX.md`
- `Get-Content -LiteralPath F:\E156\rewrite-workbook.txt`
- `Get-Content -LiteralPath .\protocols\dpp4-mace-t2d.md`
- `Get-Content -LiteralPath .\topics\dpp4-mace-t2d.json`
- `Get-Content -LiteralPath .\docs\reviews\dpp4-mace-t2d\review.json`
- `Get-Content -LiteralPath C:\meta-harness\outputs\search_v2\verification\dpp4-mace-t2d\dpp4-mace-t2d.json`
- `python - (measured legacy includes, r2 includes, accounted trials, first-lane NOT_VERIFIED_CAP count)`
- `python - (inspected all first-lane NOT_VERIFIED_CAP records against r2 snapshot abstracts)`
- `rg -n "NCT01703286|NCT00614939|NCT00870194" .`
- `Get-ChildItem -LiteralPath .\cache\dpp4-mace-t2d -Recurse -File | Select-Object -ExpandProperty FullName`
- `python - (checked retrieval_ledger.json for NCT registry metadata)`
- `python - (checked raw/INDEX.json for CT.gov raw call metadata)`
- `python - (checked outputs/search_v2/candidates-2026-09-15r2-all.json and r3-all for NCT status fields)`
- `python - (checked first-lane registry-only encoding convention)`
- `python - (fetched CT.gov API JSON for NCT01703286, NCT00614939, NCT00870194 to lane_v/dpp4-mace-t2d-raw/)`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/dpp4-mace-t2d.json',encoding='utf-8')); d=json.load(open('cache/dpp4-mace-t2d/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python - (generated lane_v/dpp4-mace-t2d.json and LANE-W-dpp4-mace-t2d-REPORT.md)`
- `python - (validated JSON length, quote presence, verdict enum, first-line sum, and report/JSON count agreement)`
- `Get-Content -LiteralPath .\LANE-W-dpp4-mace-t2d-REPORT.md -TotalCount 120`
- `Get-ChildItem -LiteralPath .\lane_v\dpp4-mace-t2d-raw -File | Select-Object Name,Length`
- `python - (final sanity sample of generated rows)`

Number marks: every number in this report is MEASURED from the cited files or generated lane artifacts. Non-numeric interpretation is source-backed by the quoted spans; no external trial knowledge was used for verdicts.
