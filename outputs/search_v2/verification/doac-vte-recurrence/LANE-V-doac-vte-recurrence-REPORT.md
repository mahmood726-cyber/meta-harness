V-doac-vte-recurrence VERDICTS: NEW 78; ELIGIBLE_RCT 6; ELIGIBLE_RCT_NO_PRIMARY 3; NOT_RCT 17; WRONG_* 4; DUPLICATE_OF_ACCOUNTED 30; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 18
automated screen agreed on 9 of 78 verified
r2 includes 84 of 5342; already accounted for 6; NEW 78
MEASURED: legacy includes 6; primary pooled trials 6; primary declared_absent_trials 0; NEW denominator 78.
MEASURED: NCT snapshot records expose allocation, study_type, has_results, conditions, and interventions, but no overall_status field; registry-only quotes use those available record fields.
INFERRED: verdict labels are source-verification judgements from the quoted title/abstract/registry spans; no pooling decision is made here.

## ELIGIBLE_RCT ids
- 38346475 - Treatment of acute pulmonary embolism after catheter-directed thrombolysis with dabigatran vs warfarin: Results of a multicenter randomized RE-SPIRE trial.
- 27165711 - Magnetic resonance venography to assess thrombus resolution with edoxaban monotherapy versus parenteral anticoagulation/warfarin for symptomatic deep vein thrombosis: A multicenter feasibility study.
- 25912695 - Apixaban for the Treatment of Japanese Subjects With Acute Venous Thromboembolism (AMPLIFY-J Study).
- 18541000 - Efficacy and safety of the oral direct factor Xa inhibitor apixaban for symptomatic deep vein thrombosis. The Botticelli DVT dose-ranging study.
- 18621928 - A dose-ranging study evaluating once-daily oral administration of the factor Xa inhibitor rivaroxaban in the treatment of patients with acute symptomatic deep vein thrombosis: the Einstein-DVT Dose-Ranging Study.
- 17576867 - Treatment of proximal deep-vein thrombosis with the oral direct factor Xa inhibitor rivaroxaban (BAY 59-7939): the ODIXa-DVT (Oral Direct Factor Xa Inhibitor BAY 59-7939 in Patients With Acute Symptomatic Deep-Vein Thrombosis) study.

## DUPLICATE_OF_ACCOUNTED pairs
- 33890242 -> Duplicate/subanalysis of accounted AMPLIFY trial, PMID 23808982 / NCT00643201.
- 34255420 -> Duplicate follow-up of accounted RE-COVER trials, PMID 19966341 and PMID 24344086.
- 29248859 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 29940089 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 29974611 -> Duplicate/subanalysis of accounted RE-COVER trials, PMID 19966341 and PMID 24344086.
- 28151543 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 28689179 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 26403199 -> Duplicate pooled analysis of accounted RE-COVER trials, PMID 19966341 and PMID 24344086.
- 27132697 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 27411591 -> Duplicate pooled analysis of accounted RE-COVER trials, PMID 19966341 and PMID 24344086.
- 27440518 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 27535349 -> Duplicate/subanalysis of accounted EINSTEIN trials, PMID 21128814 and PMID 22449293.
- 27583311 -> Duplicate/subanalysis of accounted EINSTEIN-DVT, PMID 21128814 / NCT00440193.
- 27583312 -> Duplicate/subanalysis of accounted AMPLIFY trial, PMID 23808982 / NCT00643201.
- 25483215 -> Duplicate/subanalysis of accounted EINSTEIN-PE, PMID 22449293 / NCT00439777.
- 25676529 -> Duplicate/subanalysis of accounted EINSTEIN trials, PMID 21128814 and PMID 22449293.
- 25716463 -> Duplicate/subanalysis of accounted EINSTEIN-PE, PMID 22449293 / NCT00439777.
- 26179767 -> Duplicate/subanalysis of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 26627879 -> Duplicate/subanalysis of accounted AMPLIFY trial, PMID 23808982 / NCT00643201.
- 24432872 -> Duplicate/subanalysis of accounted EINSTEIN trials, PMID 21128814 and PMID 22449293.
- 23846019 -> Duplicate/subanalysis of accounted EINSTEIN-DVT, PMID 21128814 / NCT00440193.
- 24298731 -> Duplicate/report summary of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- 24341332 -> Duplicate/subanalysis of accounted EINSTEIN trials, PMID 21128814 and PMID 22449293.
- 20459411 -> Duplicate/report summary of accounted RE-COVER, PMID 19966341.
- NCT00986154 -> Registry duplicate of accounted Hokusai-VTE, PMID 23991658 / NCT00986154.
- NCT00643201 -> Registry duplicate of accounted AMPLIFY, PMID 23808982 / NCT00643201.
- NCT00680186 -> Registry duplicate of accounted RE-COVER II, PMID 24344086 / NCT00680186.
- NCT00439777 -> Registry duplicate of accounted EINSTEIN-PE, PMID 22449293 / NCT00439777.
- NCT00440193 -> Registry duplicate of accounted EINSTEIN-DVT, PMID 21128814 / NCT00440193.
- NCT00291330 -> Registry duplicate of accounted RE-COVER I, PMID 19966341 / NCT00291330.

## Commands run
- Get-Content -LiteralPath 'LANE_PROMPT.md'
- Get-Content -LiteralPath 'LIVE_CONTEXT.md' (failed: file missing in cwd)
- git status --short
- PowerShell Test-Path/Get-Content for F:\ProjectIndex\INDEX.md and F:\E156\rewrite-workbook.txt
- python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/doac-vte-recurrence.json',encoding='utf-8')); d=json.load(open('cache/doac-vte-recurrence/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"
- Get-Content -LiteralPath 'protocols/doac-vte-recurrence.md'
- Get-Content -LiteralPath 'topics/doac-vte-recurrence.json'
- Get-Content -LiteralPath 'docs/reviews/doac-vte-recurrence/review.json'
- Python stdin script: inspected snapshot/review keys, primary outcome trials, declared_absent_trials, and include IDs
- Python stdin script: measured r2 records/includes, accounted IDs, and NEW include list
- Python stdin script: inspected selected full records (38346475, 20459411, NCT06145269, NCT00291330, NCT03196349)
- Python stdin script: scanned PubMed records for empty/truncated abstract markers
- New-Item -ItemType Directory -Force -Path 'lane_v\doac-vte-recurrence-raw' | Out-Null; Invoke-WebRequest efetch PMID 20459411 (failed TLS receive error)
- Python stdin script: urllib efetch PMID 20459411 to lane_v/doac-vte-recurrence-raw/pubmed-20459411.xml
- Python stdin script: parsed lane_v/doac-vte-recurrence-raw/pubmed-20459411.xml for abstract/title/publication types
- Python stdin script: enumerated NCT snapshot keys
- Four Python stdin scripts: batched source-text inspection for all 78 NEW includes
- Python stdin script: full-abstract inspection for tricky RCT/subanalysis records
- Python stdin script: first generation attempt, failed before writing due quote needle mismatch on PMID 28151543
- Python stdin script: generated lane_v/doac-vte-recurrence.json and LANE-V-doac-vte-recurrence-REPORT.md with validation

## Output validation
- MEASURED: lane_v/doac-vte-recurrence.json contains 78 objects.
- MEASURED: first-line verdict counts sum to 78.
- MEASURED: every verified object has a non-empty quote not exceeding 300 characters.
- MEASURED: raw HTTP body relied on for empty PubMed abstract is lane_v/doac-vte-recurrence-raw/pubmed-20459411.xml.
