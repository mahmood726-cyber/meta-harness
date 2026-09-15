V-metformin-pcos-ovulation VERDICTS: NEW 45; ELIGIBLE_RCT 6; ELIGIBLE_RCT_NO_PRIMARY 8; NOT_RCT 7; WRONG_* 23; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 1
automated screen agreed on 14 of 45 verified
r2 includes 57 of 1885; already accounted for 12; NEW 45

Measurement notes: counts are MEASURED from the named JSON inputs and harness replay command. Verdict labels are RECORD-INFERRED from the quoted snapshot title/abstract or registry fields; no outside trial knowledge was used. No PubMed efetch or other HTTP call was needed, so the raw directory is present and empty.

ELIGIBLE_RCT ids with titles (pool-moving candidates; RECORD-INFERRED):
- 16352680 - Early effects of metformin in women with polycystic ovary syndrome: a prospective randomized, double-blind, placebo-controlled trial.
- 16316811 - Predictive value of glucose-insulin ratio in PCOS and profile of women who will benefit from metformin therapy: obese, lean, hyper or normoinsulinemic?
- 15302293 - A randomized, 48-week, placebo-controlled trial of intensive lifestyle modification and/or metformin therapy in overweight women with polycystic ovary syndrome: a pilot study.
- 15482765 - Effects of metformin and rosiglitazone, alone and in combination, in nonobese women with polycystic ovary syndrome and normal indices of insulin sensitivity.
- 11779598 - Metformin therapy improves ovulatory rates, cervical scores, and pregnancy rates in clomiphene citrate-resistant women with polycystic ovary syndrome.
- 10634377 - Metformin effects on clinical features, endocrine and metabolic profiles, and insulin sensitivity in polycystic ovary syndrome: a randomized, double-blind, placebo-controlled 6-month trial, followed by open, long-term clinical evaluation.

DUPLICATE_OF_ACCOUNTED pairs (MEASURED):
- none

Commands run (MEASURED):
- `Get-Content -LiteralPath 'LANE_PROMPT.md' -Raw`
- `if (Test-Path -LiteralPath 'F:\ProjectIndex\INDEX.md') { Get-Content -LiteralPath 'F:\ProjectIndex\INDEX.md' -TotalCount 80 } else { 'MISSING:F:\ProjectIndex\INDEX.md' }`
- `if (Test-Path -LiteralPath 'F:\E156\rewrite-workbook.txt') { Get-Content -LiteralPath 'F:\E156\rewrite-workbook.txt' -TotalCount 80 } else { 'MISSING:F:\E156\rewrite-workbook.txt' }`
- `git status --short`
- `Get-Content -LiteralPath 'protocols/metformin-pcos-ovulation.md' -Raw`
- `Get-Content -LiteralPath 'topics/metformin-pcos-ovulation.json' -Raw`
- `Get-Content -LiteralPath 'docs/reviews/metformin-pcos-ovulation/review.json' -Raw`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/metformin-pcos-ovulation.json',encoding='utf-8')); d=json.load(open('cache/metformin-pcos-ovulation/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `Get-Content -LiteralPath 'cache/metformin-pcos-ovulation/snapshots/2026-09-15r2-search_v2/records.json' -TotalCount 120`
- `@'...inspect snapshot/review structure and legacy includes...'@ | python -`
- `@'...measure r2 include denominator and print NEW candidates...'@ | python -`
- `@'...print NEW candidates 1-15...'@ | python -`
- `@'...print NEW candidates 8-15...'@ | python -`
- `@'...print NEW candidates 16-30...'@ | python -`
- `@'...print NEW candidates 31-45...'@ | python -`
- `@'...check abstract lengths for NEW candidates...'@ | python -`
- `@'...print NCT01115140 snapshot registry record...'@ | python -`
- `Get-ChildItem -Force -Name`
- `@'...validate verdict quotes and lengths...'@ | python -`
- `@'...write lane_v/metformin-pcos-ovulation.json, lane_v/metformin-pcos-ovulation-raw/, and LANE-V-metformin-pcos-ovulation-REPORT.md; validate counts and quotes...'@ | python -`
