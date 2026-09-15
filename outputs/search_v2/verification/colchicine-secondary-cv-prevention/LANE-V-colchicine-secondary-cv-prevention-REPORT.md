V-colchicine-secondary-cv-prevention VERDICTS: NEW 40; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 13; NOT_RCT 13; WRONG_* 5; DUPLICATE_OF_ACCOUNTED 6; UNDECIDABLE 2; NOT_VERIFIED_CAP 0
automated screen agreed on 14 of 40 verified
r2 includes 69 of 3726; already accounted for 29; NEW 40

Number status: all verdict and population counts above are MEASURED from the committed JSON inputs and harness screen command; duplicate pair labels are INFERRED from shared NCT/acronym/trial-name text in the snapshot/review records.
HTTP bodies fetched: 0 MEASURED; no PubMed efetch was needed because every new PubMed record had a non-empty, non-truncated snapshot abstract, and NCT-only registry rows had no PMID to efetch.
Quote-source note: for registry-only NCT rows with blank abstracts, `snapshot abstract` denotes the snapshot record source and the quoted span is from the snapshot title, as permitted by the lane prompt title-or-abstract quote rule.

## ELIGIBLE_RCT ids with titles
- 35881907: Preprocedural Colchicine in Patients With Acute ST-elevation Myocardial Infarction Undergoing Percutaneous Coronary Intervention: A Randomized Controlled Trial (PodCAST-PCI).

## DUPLICATE_OF_ACCOUNTED pairs
- NCT04848857 -> PMID 39166327 (COLOCT declared absent) [INFERRED from acronym/title match]
- NCT03048825 -> PMID 39555823 (CLEAR SYNERGY pooled) [INFERRED from acronym/title match]
- NCT03156816 -> PMID 34420373 (COVERT-MI declared absent) [INFERRED from acronym/title match]
- NCT02551094 -> PMID 31733140 (COLCOT pooled) [INFERRED from NCT/acronym match]
- NCT01936285 -> PMID 26265659 (acute-MI colchicine pilot declared absent) [INFERRED from NCT/title match]
- NCT02594111 -> PMID 32295417 (Colchicine-PCI declared absent) [INFERRED from NCT/acronym match]

## Verdict Table
| id | verdict | screen_agrees | note |
| --- | --- | --- | --- |
| 40908114 | NOT_RCT | false | Secondary benefit-risk analysis of accounted CLEAR SYNERGY trial PMID 39555823, not a new trial. |
| NCT07232069 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled candidate; no abstract or results report the primary MACE outcome. |
| NCT07569328 | WRONG_POPULATION | false | CABG graft-failure prevention falls under the protocol's cardiac-surgery/postoperative exclusion rather than coronary/MI secondary prevention. |
| 40004876 | ELIGIBLE_RCT_NO_PRIMARY | true | Eligible AMI placebo-controlled RCT, but the abstract reports biomarkers and echocardiography rather than MACE or protocol harms. |
| 40053073 | NOT_RCT | false | Sub-analysis of accounted LoDoCo2 trial PMID 32865380, not a new trial. |
| 40393691 | NOT_RCT | false | Cross-sectional imaging subanalysis of accounted LoDoCo2 trial PMID 32865380. |
| NCT04218786 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled MI candidate; no abstract or results report the primary MACE outcome. |
| NCT06930885 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled ASCVD candidate; no abstract or results report the primary MACE outcome. |
| 38181203 | NOT_RCT | false | Prespecified subgroup analysis of accounted COLCOT trial PMID 31733140. |
| 38233042 | NOT_RCT | false | Follow-up analysis of accounted COVERT-MI trial PMID 34420373. |
| 39200761 | NOT_RCT | false | The abstract labels the clinical component observational, so the record does not verify a double-blind placebo-controlled RCT. |
| NCT06095765 | UNDECIDABLE_FROM_RECORD | false | The snapshot abstract is blank and the title does not establish double-blind eligibility or a protocol outcome; the registry masking field is SINGLE. |
| NCT06217120 | WRONG_POPULATION | false | The title places the trial in HFpEF rather than coronary disease or recent-MI secondary prevention. |
| NCT06472908 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled coronary/PCI candidate; no abstract or results report the primary MACE outcome. |
| 36529304 | NOT_RCT | false | Secondary safety analysis of accounted LoDoCo2 trial PMID 32865380. |
| 37536200 | NOT_RCT | false | Follow-up analysis of accounted Colchicine-PCI trial PMID 32295417. |
| 37697278 | UNDECIDABLE_FROM_RECORD | false | The abstract verifies randomization but does not state the double-blind placebo-controlled design required by the protocol. |
| 37868776 | NOT_RCT | false | Subgroup analysis of accounted LoDoCo2 trial PMID 32865380. |
| NCT05618353 | WRONG_POPULATION | false | Peri-operative trial scope falls under the protocol's postoperative/cardiac-surgery population exclusion. |
| NCT06078904 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled coronary/PCI candidate; title points to hsCRP and no abstract reports primary MACE. |
| 35685430 | NOT_RCT | false | Substudy of COPE-PCI rather than a separate primary RCT. |
| 35716932 | NOT_RCT | false | Combined individual-patient-data analysis of accounted COLCOT and LoDoCo-MI trials. |
| 35739010 | NOT_RCT | false | Sub-study of accounted COPS trial PMID 32862667. |
| 35881907 | ELIGIBLE_RCT | true | New STEMI placebo-controlled randomized trial reports MACE as a secondary endpoint. |
| NCT05175274 | WRONG_POPULATION | false | Primary prevention is outside the protocol population of established coronary disease or recent-MI secondary prevention. |
| 34003667 | ELIGIBLE_RCT_NO_PRIMARY | true | Eligible coronary/PCI placebo-controlled RCT, but the abstract reports periprocedural myocardial injury rather than protocol MACE or harms. |
| 34420187 | ELIGIBLE_RCT_NO_PRIMARY | true | Eligible NSTEMI placebo-controlled RCT, but the abstract reports hsCRP rather than primary MACE or protocol harms. |
| NCT04848857 | DUPLICATE_OF_ACCOUNTED | false | Same COLOCT trial as accounted declared-absent PMID 39166327. |
| NCT05956145 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled CAD candidate; title points to platelet reactivity and no abstract reports primary MACE. |
| 32175647 | WRONG_POPULATION | false | Open-heart surgery/constrictive-physiology prevention is outside the coronary/MI secondary-prevention population. |
| 32860034 | NOT_RCT | false | Secondary timing analysis of accounted COLCOT trial PMID 31733140. |
| 30683457 | ELIGIBLE_RCT_NO_PRIMARY | true | Eligible CAD placebo-controlled RCT, but the abstract reports endothelial function and hsCRP rather than primary MACE or protocol harms. |
| NCT03048825 | DUPLICATE_OF_ACCOUNTED | false | Same CLEAR SYNERGY trial as accounted pooled PMID 39555823. |
| NCT03156816 | DUPLICATE_OF_ACCOUNTED | false | Same COVERT-MI trial as accounted declared-absent PMID 34420373. |
| NCT02366091 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled CAD candidate; title points to endothelial function and no abstract reports primary MACE. |
| NCT02551094 | DUPLICATE_OF_ACCOUNTED | false | Same COLCOT trial as accounted pooled PMID 31733140. |
| NCT02624180 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled CAD/HIV candidate; no abstract or results report primary MACE. |
| NCT01906749 | ELIGIBLE_RCT_NO_PRIMARY | true | Registry-only randomized placebo-controlled ACS candidate; no abstract or results report primary MACE. |
| NCT01936285 | DUPLICATE_OF_ACCOUNTED | false | Same acute-MI pilot trial as accounted declared-absent PMID 26265659. |
| NCT02594111 | DUPLICATE_OF_ACCOUNTED | false | Same Colchicine-PCI trial as accounted declared-absent PMID 32295417. |

## Commands Run
- `Get-Location`
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `Get-Content -LiteralPath .\LIVE_CONTEXT.md` (failed: file absent) [MEASURED]
- `git status --short`
- `Test-Path -LiteralPath F:\ProjectIndex\INDEX.md; Test-Path -LiteralPath F:\E156\rewrite-workbook.txt; Test-Path -LiteralPath C:\ProjectIndex\INDEX.md; Test-Path -LiteralPath C:\E156\rewrite-workbook.txt`
- `Get-ChildItem -LiteralPath . -Force | Select-Object Name,Mode,Length`
- `if (Test-Path -LiteralPath F:\ProjectIndex\INDEX.md) { Get-Content -LiteralPath F:\ProjectIndex\INDEX.md -TotalCount 80 } elseif (Test-Path -LiteralPath C:\ProjectIndex\INDEX.md) { Get-Content -LiteralPath C:\ProjectIndex\INDEX.md -TotalCount 80 }`
- `if (Test-Path -LiteralPath F:\E156\rewrite-workbook.txt) { Get-Content -LiteralPath F:\E156\rewrite-workbook.txt -TotalCount 80 } elseif (Test-Path -LiteralPath C:\E156\rewrite-workbook.txt) { Get-Content -LiteralPath C:\E156\rewrite-workbook.txt -TotalCount 80 }`
- `Get-Content -LiteralPath .\protocols\colchicine-secondary-cv-prevention.md`
- `Get-Content -LiteralPath .\topics\colchicine-secondary-cv-prevention.json`
- `Get-Content -LiteralPath .\docs\reviews\colchicine-secondary-cv-prevention\review.json`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/colchicine-secondary-cv-prevention.json',encoding='utf-8')); d=json.load(open('cache/colchicine-secondary-cv-prevention/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `@' ... r2/review schema inspection Python ... '@ | python -`
- `@' ... measured NEW population Python ... '@ | python -`
- `@' ... full new-include snapshot dump Python ... '@ | python -`
- `@' ... chunked new-include inspection Python for rows 1-14 ... '@ | python -`
- `@' ... chunked new-include inspection Python for rows 15-28 ... '@ | python -`
- `@' ... chunked new-include inspection Python for rows 29-40 ... '@ | python -`
- `@' ... PubMed snapshot abstract ending check Python ... '@ | python -`
- `@' ... final artefact writer attempt; failed before writing because one copied quote had shell encoding substitution ... '@ | python -`
- `@' ... final artefact writer attempt; failed before writing because whitespace normalization broke a non-breaking-space quote ... '@ | python -`
- `@' ... final artefact writer and finish-condition validator Python ... '@ | python -`
