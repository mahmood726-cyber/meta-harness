V-semaglutide-obesity-mace VERDICTS: NEW 5; ELIGIBLE_RCT 0; ELIGIBLE_RCT_NO_PRIMARY 0; NOT_RCT 0; WRONG_* 1; DUPLICATE_OF_ACCOUNTED 3; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 1
automated screen agreed on 0 of 5 verified
r2 includes 6 of 2845; already accounted for 1; NEW 5

Marks: every numeric count above is MEASURED from the local snapshot/review files and generated JSON. Verdict labels are source-verified from the quoted record spans; the STEP 8 wrong-population label is INFERRED from the record population/comparison against the protocol PICO.

## ELIGIBLE_RCT ids with titles
- None MEASURED.

## DUPLICATE_OF_ACCOUNTED pairs
- 38740993 -> PMID 37952131 / SELECT / NCT03574597 (same NCT; long-term weight-loss secondary analysis).
- 40156748 -> PMID 37952131 / SELECT / NCT03574597 (same NCT; number-needed-to-treat secondary analysis).
- 42610271 -> PMID 37952131 / SELECT / NCT03574597 (same NCT; prespecified hsCRP secondary analysis).

## Verdict Table
- 35015037 | WRONG_POPULATION | screen_rule=INCLUDE | screen_agrees=false | quote_source=snapshot abstract | quote="OBJECTIVE: To compare the efficacy and adverse event profiles of once-weekly subcutaneous semaglutide, 2.4 mg, vs once-daily subcutaneous liraglutide, 3.0 mg (both with diet and physical activity), in people with overweight or obesity."
- 38740993 | DUPLICATE_OF_ACCOUNTED | screen_rule=INCLUDE | screen_agrees=false | quote_source=snapshot abstract | quote="In the SELECT cardiovascular outcomes trial, semaglutide showed a 20% reduction in major adverse cardiovascular events in 17,604 adults with preexisting cardiovascular disease, overweight or obesity, without diabetes."
- 40156748 | DUPLICATE_OF_ACCOUNTED | screen_rule=INCLUDE | screen_agrees=false | quote_source=snapshot abstract | quote="This study is a secondary analysis of data from the randomized, double-blind SELECT trial (ClinicalTrials.gov NCT03574597) of once-weekly subcutaneous administration of semaglutide compared with placebo"
- 42610271 | DUPLICATE_OF_ACCOUNTED | screen_rule=INCLUDE | screen_agrees=false | quote_source=snapshot abstract | quote="In this prespecified SELECT substudy, we evaluated whether baseline hsCRP levels predicted MACE risk and examined the relationships between changes in hsCRP levels and time to first MACE"
- NCT03574597 | REGISTRY_ONLY_NO_PUBLICATION | screen_rule=INCLUDE | screen_agrees=false | quote_source=ctgov raw (lane_v/semaglutide-obesity-mace-raw/ctgov-NCT03574597.json) | quote="overallStatus: COMPLETED; conditions: Overweight, Obesity; interventions: Semaglutide, Placebo (semaglutide)"

## Raw HTTP Bodies Relied On
- lane_v/semaglutide-obesity-mace-raw/ctgov-NCT03574597.json

## Commands Run
- `Get-Content -Raw -LiteralPath '.\LANE_PROMPT.md'`
- `Get-Content -Raw -LiteralPath '.\LIVE_CONTEXT.md'` (failed: file not found)
- `Get-Content -Raw -LiteralPath 'F:\ProjectIndex\INDEX.md'`
- `Get-Content -Raw -LiteralPath 'F:\E156\rewrite-workbook.txt'`
- `git status --short`
- `Get-Content -Raw -LiteralPath '.\protocols\semaglutide-obesity-mace.md'`
- `Get-Content -Raw -LiteralPath '.\topics\semaglutide-obesity-mace.json'`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/semaglutide-obesity-mace.json',encoding='utf-8')); d=json.load(open('cache/semaglutide-obesity-mace/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python -c <inspected docs/reviews/semaglutide-obesity-mace/review.json top-level primary/absent fields>`
- `python -c <measured r2 snapshot record and screening decision counts>`
- `python -c <printed review outcomes/trials/declared_absent_trials>`
- `python -c <printed review screening block for context>`
- `python -c <listed r2 automated include records with decisions>`
- `python -c <printed full NEW include records and abstracts>`
- `rg --files -g '*LANE*REPORT*.md' -g '*.json' -g 'lane_*'`
- `python -c <printed NCT03574597 snapshot record keys and full local record>`
- `rg -n "overall_status|overallStatus|NCT03574597|Semaglutide Effects" cache topics docs protocols`
- `Get-Content -Raw -LiteralPath '.\LANE-S3-REPORT.md'`
- `Get-Content -Raw -LiteralPath '.\LANE-AE-REPORT.md'`
- `python -c "import pathlib, urllib.request; raw=pathlib.Path('lane_v/semaglutide-obesity-mace-raw'); raw.mkdir(parents=True, exist_ok=True); url='https://clinicaltrials.gov/api/v2/studies/NCT03574597'; req=urllib.request.Request(url, headers={'User-Agent':'lane-v-source-verify/1.0'}); body=urllib.request.urlopen(req, timeout=30).read(); (raw/'ctgov-NCT03574597.json').write_bytes(body); print(len(body))"`
- `python -c <extracted CT.gov status/conditions/interventions from saved raw body>`
- `python -c <listed accounted review trials and declared_absent trials>`
- `python -c <computed r2 includes/accounted/NEW counts and NEW ids>`
- `python -c @'<inline lane writer/validator>'@` (failed with SyntaxError before writing final JSON/report)
- `python -c <validate lane_v/semaglutide-obesity-mace.json, raw CT.gov body, and report first-line sum>`
- `git status --short`

No commit was made.
