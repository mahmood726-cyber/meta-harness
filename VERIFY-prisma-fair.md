# FAIR PRISMA Comparator Comparison

Comparator scoring uses OA full text body where obtainable, not PubMed abstracts. Topics with no obtainable comparator full text are excluded from the fair item counts.

- Topics built: 29
- Comparator full text obtained: 28
- Comparator full text unobtainable/excluded: 1
- Countable topic-item cells: 168
- Comparator-present cells: 94
- OURS present / comparator absent: 74
- Comparator present / OURS absent: 0

## Per-topic Summary

| slug | source | bytes | ours n/6 | comparator n/6 | ours-only | comparator-only |
|---|---:|---:|---:|---:|---:|---:|
| `balanced-crystalloids-vs-saline-mortality` | NCBI PMC efetch XML body: PMC6098635 | 17047 | 6 | 2 | 4 | 0 |
| `colchicine-postop-af` | NCBI PMC efetch XML body: PMC9438305 | 19123 | 6 | 4 | 2 | 0 |
| `colchicine-recurrent-pericarditis` | Unpaywall PDF: https://heart.bmj.com/content/heartjnl/98/14/1078.full.pdf | 25986 | 6 | 4 | 2 | 0 |
| `colchicine-secondary-cv-prevention` | NCBI PMC efetch XML body: PMC9512890 | 33931 | 6 | 4 | 2 | 0 |
| `corticosteroids-cap-mortality` | NONE | 0 | 6 | excluded | excluded | excluded |
| `corticosteroids-covid19-mortality` | Unpaywall HTML: https://hdl.handle.net/1983/3a2332f5-8bec-4650-92b6-0d04b05f6cfb | 22116 | 6 | 0 | 6 | 0 |
| `dapagliflozin-hfpef-hosp` | Unpaywall HTML: https://www.ncbi.nlm.nih.gov/pmc/articles/10123444 | 34670 | 6 | 4 | 2 | 0 |
| `denosumab-vertebral-fracture` | NCBI PMC efetch XML body: PMC9958453 | 25423 | 6 | 4 | 2 | 0 |
| `empagliflozin-hfpef-hosp` | NCBI PMC efetch XML body: PMC10545009 | 18452 | 6 | 5 | 1 | 0 |
| `finerenone-ckd-t2d-renal` | NCBI PMC efetch XML body: PMC9895809 | 21815 | 6 | 3 | 3 | 0 |
| `glp1-ra-mace-t2d` | NCBI PMC efetch XML body: PMC8442438 | 19849 | 6 | 2 | 4 | 0 |
| `iv-iron-hfref-hosp` | NCBI PMC efetch XML body: PMC11727542 | 23105 | 6 | 4 | 2 | 0 |
| `metformin-pcos-ovulation` | Unpaywall HTML: https://www.ncbi.nlm.nih.gov/pmc/articles/6915832 | 336474 | 6 | 5 | 1 | 0 |
| `noac-vs-warfarin-af-stroke` | NCBI PMC efetch XML body: PMC8800560 | 28946 | 6 | 1 | 5 | 0 |
| `omega3-cardiovascular-events` | NCBI PMC efetch XML body: PMC9333496 | 32203 | 6 | 4 | 2 | 0 |
| `pcsk9-mace` | NCBI PMC efetch XML body: PMC9755489 | 24056 | 6 | 4 | 2 | 0 |
| `probiotics-aad-prevention` | NCBI PMC efetch XML body: PMC8362734 | 34972 | 6 | 3 | 3 | 0 |
| `sacubitril-valsartan-hfref` | NCBI PMC efetch XML body: PMC10053170 | 23352 | 6 | 4 | 2 | 0 |
| `semaglutide-obesity-mace` | NCBI PMC efetch XML body: PMC11437580 | 35431 | 6 | 4 | 2 | 0 |
| `sglt2-ckd-progression` | Unpaywall HTML: https://research.rug.nl/en/publications/68eb83ac-626c-48c1-84b8-f2e0ef96eb0c | 17633 | 6 | 0 | 6 | 0 |
| `sglt2-hfref-hosp-cvdeath` | NCBI PMC efetch XML body: PMC8934917 | 11706 | 6 | 4 | 2 | 0 |
| `spironolactone-hfref-mortality` | NCBI PMC efetch XML body: PMC12434096 | 32101 | 6 | 4 | 2 | 0 |
| `statins-primary-prevention-elderly` | NCBI PMC efetch XML body: PMC11273788 | 44438 | 6 | 3 | 3 | 0 |
| `ticagrelor-vs-clopidogrel-acs` | NCBI PMC efetch XML body: PMC5435320 | 31334 | 6 | 2 | 4 | 0 |
| `tocilizumab-covid19-mortality` | Unpaywall HTML: https://research.rug.nl/en/publications/84f62a1c-8000-42fc-80a5-6f875f94ed80 | 18894 | 6 | 2 | 4 | 0 |
| `tranexamic-acid-pph` | NCBI PMC efetch XML body: PMC12197804 | 29347 | 6 | 4 | 2 | 0 |
| `esketamine-trd-madrs` | records.json comparator_fulltext (cached OA) | 58728 | 6 | 5 | 1 | 0 |
| `melatonin-primary-insomnia-sol` | records.json comparator_fulltext (cached OA) | 18777 | 6 | 3 | 3 | 0 |
| `semaglutide-obesity-weight` | records.json comparator_fulltext (cached OA) | 42376 | 6 | 6 | 0 | 0 |

## Excluded From Fair Count

- `corticosteroids-cap-mortality`: PDF fetch failed from https://orca.cardiff.ac.uk/id/eprint/165120/1/1-s2.0-S0883944123002563-main.pdf: GET failed after 2 tries: https://orca.cardiff.ac.uk/id/eprint/165120/1/1-s2.0-S0883944123002563-main.pdf; HTTP Error 403: Forbidden

## Item Detail

### balanced-crystalloids-vs-saline-mortality

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | N |  |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 29 records: agreement 29/29 , disagreement 0.0% | Y | independently and separately extracted the data into a predesigned form from the included studies. Any disagreement was solved |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 29 Records screened (deduplicated) 29 Excluded at | Y | Flow diagram of literature search and study selection based on Preferred Reporting Items for Systematic Reviews and Meta-Analyses |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 29 records: agreement 29/29 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) f85737aa471079fa1ef93da4ca0caf21c83b77e8 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### colchicine-postop-af

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy and inclusion criteria A systematic search for eligible studies was conducted, and relevant articles were retrieved |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 9.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 67 records: agreement 61/67 , disagreement 9.0% | Y | Two authors (Jing C. and Hong Z.) independently reviewed the 149 identified articles. Finally, we included 9 RCTs |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 67 Records screened (deduplicated) 67 Excluded at | Y | studies involving 2031 patients were finally included in our analysis [ 15 – 23 ] (Fig. 1 ). |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 67 records: agreement 61/67 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 17664842dc5363f3aec2ddee42828835bad05ef6 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | registration number: INPLASY202190004) [ 13 , 14 ]. Moreover, the screening and the review of the full text |

### colchicine-recurrent-pericarditis

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search strategy We included any randomised clinical trial on phar- macological prevention of pericarditis. Potentially relevant studies published |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 9.4% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 53 records: agreement 48/53 , disagreement 9.4% | Y | independent reviewers (DF and SF), with divergences resolved by consensus. Study evaluation included general methodological quality features, including |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 53 Records screened (deduplicated) 53 Excluded at | Y | Flow diagram of included studies. Table 1 Mean features of included studies Study Location/year Design Setting Therapeutic class |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 53 records: agreement 48/53 | Y | excluded from analysis because 52 of 163 patients (31.9%) were excluded from subsequent outcome assessment for side effects |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 34023da4e35f9094f846361cefb31c8a6655e678 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### colchicine-secondary-cv-prevention

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy The search strategy was conducted in accordance with the Participant, Intervention, Comparison, Outcome, and Study Design |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 14.2% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 120 records: agreement 103/120 , disagreement 14.2% | Y | disagreements in the quality assessment are resolved through discussion between the two evaluators and, if necessary, the involvement |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 120 Records screened (deduplicated) 120 Excluded at | Y | Flow diagram of the study selection process. TABLE 1 Main characteristics of included RCTs. Study Country Study design |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 120 records: agreement 103/120 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 9355c4b9d8482a5cf6f6ad3d4884d97f695f2a6d Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO database 1 with Registration Number 42022332170. Search strategy The search strategy was conducted in accordance with the |

### corticosteroids-cap-mortality

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | NA |  |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.9% | NA |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 114 records: agreement 113/114 , disagreement 0.9% | NA |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 114 Records screened (deduplicated) 114 Excluded at | NA |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 114 records: agreement 113/114 | NA |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 036ee46c6c45cb5c10607def1eeda86ba536d750 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | NA |  |

### corticosteroids-covid19-mortality

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | N |  |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.8% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 56 records: agreement 55/56 , disagreement 1.8% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 56 Records screened (deduplicated) 56 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 56 records: agreement 55/56 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) dce99b4135d953e0363d519ff078bc6e1311289c Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### dapagliflozin-hfpef-hosp

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | searched PubMed/MEDLINE, Embase, Web of Science databases and clinical trial registries using appropriate keywords till August 28, 2022, |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 97 records: agreement 96/97 , disagreement 1.0% | Y | independently assessed by two investigators (MB and KN). Any discrepancy was solved by discussion with a third senior |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 97 Records screened (deduplicated) 97 Excluded at | Y | PRISMA flow-chart describing the study selection process has been given in sFig. 1 . Relevant data from two |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 97 records: agreement 96/97 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) a6788cc518027a2b1b2aa9e94ac45b393a13efca Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO database (CRD42022356582). 2.1. Search strategy “PubMed/MEDLINE”, “Embase”, and “Web of Science” databases and clinical trial registries were |

### denosumab-vertebral-fracture

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | electronic databases, including PubMed, Embase and the Cochrane Library, were searched with no language limitations ( eTable 1 |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.4% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 71 records: agreement 70/71 , disagreement 1.4% | Y | two reviewers to independently evaluate the included studies for potential bias. Disagreements between the two investigators were resolved |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 71 Records screened (deduplicated) 71 Excluded at | Y | Studies had been published between 1990 and 2018. In the included RCTs, the mean age was in the |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 71 records: agreement 70/71 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 3fb64a1e01434eb6ee9ea8a764a84c749270dfff Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO (CRD42020201167). 2.2 Data sources and searches The Cochrane and PROSPERO databases were independently searched by two reviewers |

### empagliflozin-hfpef-hosp

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy We conducted a systematic literature search in PubMed, Embase, and Cochrane Library using predefined MESH terms |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.0% | Y | MESH terms by using “AND” and “OR.” The following search terms were used: ((((((((((((heart failure[MeSH Terms]) OR (diastolic |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 100 records: agreement 99/100 , disagreement 1.0% | Y | Two investigators (A.I. and J.C.) independently appraised the potential risk of bias for a randomized controlled trial using |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 100 Records screened (deduplicated) 100 Excluded at | Y | PRISMA flowchart of the search strategy for systematic review and meta-analysis. 3.2. Study and patient characteristics Six studies |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 100 records: agreement 99/100 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) c5dc828d141fe01e81ce46b9a9e29863c2a01918 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO (CRD42023388472). 2.1. Search strategy We conducted a systematic literature search in PubMed, Embase, and Cochrane Library using |

### finerenone-ckd-t2d-renal

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search strategy is available in Supplementary Appendix 1 . Figure 1 The study selection process. Any citation that |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 8.7% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 23 records: agreement 21/23 , disagreement 8.7% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 23 Records screened (deduplicated) 23 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 23 records: agreement 21/23 | Y | excluded because it was not conducted on patients with diagnosed T2D ( 10 ). The study by Bakris |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 43f5f12e367109bebd37936a8177ef00c6dcf1f6 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO (CRD42022360003) ( 14 ). 2.1 Literature searches, search strategies and eligibility criteria The web search was conducted |

### glp1-ra-mace-t2d

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy and study selection This systematic review was based on PRISMA (Preferred Reporting Items for Systematic Reviews |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 10 records: agreement 10/10 , disagreement 0.0% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 10 Records screened (deduplicated) 10 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 10 records: agreement 10/10 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 4091958ce4af7f1ca9ed4c30e1021672b0c21223 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | Reviews and Meta-Analyses) guidelines [ 9 ]. The protocol has not been registered in any platform. We searched |

### iv-iron-hfref-hosp

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search Strategy A comprehensive search was conducted across multiple databases, including MEDLINE, Google Scholar, the Cochrane Library, ClinicalTrials.gov, |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 5.1% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 39 records: agreement 37/39 , disagreement 5.1% | Y | Two authors (IP and SAS) independently classified the risk of bias for each study into three categories: low, |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 39 Records screened (deduplicated) 39 Excluded at | Y | studies included align with the specified criteria for analysis and interpretation. 3.2. Characteristics of the Included Studies The |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 39 records: agreement 37/39 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) a56039f46158272c40c9565150903cf87db37c3c Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | Reviews and Meta-Analysis (PRISMA) statement [ 12 , 13 ]. The study protocol was preregistered on the Open |

### metformin-pcos-ovulation

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search Strategy for identifying randomised trials, which appears in the Cochrane Handbook of Systematic Reviews of Interventions ( |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.6% | Y | MESH DESCRIPTOR Polycystic Ovary Syndrome EXPLODE ALL TREES 1267 #2 (PCOS or PCOD):TI,AB,KY 1964 #3 (polycystic ovar*):TI,AB,KY 2383 |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 154 records: agreement 153/154 , disagreement 0.6% | Y | independently assessed studies for eligibility and bias. Primary outcomes were live birth rate and gastrointestinal adverse effects. Secondary |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 154 Records screened (deduplicated) 154 Excluded at | Y | flow diagram 2019 update Data extraction and management Two review authors (ANS and LCM) independently extracted data from |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 154 records: agreement 153/154 | Y | Reason for exclusion Abuelghar 2013 HCG hormone was used as an ovulation trigger, which may have added additional |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 4091958ce4af7f1ca9ed4c30e1021672b0c21223 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### noac-vs-warfarin-af-stroke

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | N |  |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 8.6% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 35 records: agreement 32/35 , disagreement 8.6% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 35 Records screened (deduplicated) 35 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 35 records: agreement 32/35 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 38478f5e060a9d63bcb073cb652d0e6f70d27c58 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO (CRD42020178771). For these analyses, a standard-dose DOAC treatment strategy was defined as dabigatran 150mg twice daily (RE-LY), |

### omega3-cardiovascular-events

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search strategy, and selection criteria The Preferred Reporting Items for Systematic Reviews and Meta-Analysis Statement was used to |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.8% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 114 records: agreement 112/114 , disagreement 1.8% | Y | Two reviewers independently performed the literature search and study selection. Inconsistencies between reviewers were resolved by group discussion. |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 114 Records screened (deduplicated) 114 Excluded at | Y | PRISMA flowchart for the literature search and trial selection. 3.2. Characteristics of the included studies Table 1 shows |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 114 records: agreement 112/114 | Y | excluded because of insufficient data (n = 89), absence of an RCT design (n = 76), and other |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 13c0136f93aa1d9c52aabf01cc34ef2cc27a677d Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### pcsk9-mace

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search strategy and selection criteria We systematically reviewed the literature according to the PRISMA (Preferred Reporting Items for |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 9 records: agreement 9/9 , disagreement 0.0% | Y | Two investigators (HW and YM) independently collected data with the pre-specified data collection forms and settled any discrepancies |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 9 Records screened (deduplicated) 9 Excluded at | Y | flow diagram for study selection. ( 27 – 37 ). 1,738 records were identified by literature search (Web |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 9 records: agreement 9/9 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 38478f5e060a9d63bcb073cb652d0e6f70d27c58 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO, CRD42022344908). Research strategy and selection criteria We systematically reviewed the literature according to the PRISMA (Preferred Reporting |

### probiotics-aad-prevention

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search strategy A comprehensive electronic title search ( online supplemental file 1 ) was performed of CINAHL Plus, |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 9.4% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 468 records: agreement 424/468 , disagreement 9.4% | Y | independently assessed each study for inclusion in the review. Discrepancies were resolved through discussion. Data collection process and |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 468 Records screened (deduplicated) 468 Excluded at | Y | PRISMA flow of studies. The characteristics of each included study are presented in table 1 . Table 1 |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 468 records: agreement 424/468 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 43f5f12e367109bebd37936a8177ef00c6dcf1f6 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### sacubitril-valsartan-hfref

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | searched PubMed, Embase, and the Cochrane Library from inception to 19 November 2022. The following keywords were applied: |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.2% | Y | MeSH) OR ‘SGLT‐2 inhibitor’ OR ‘SGLT‐2’ OR ‘empagliflozin’ OR ‘dapagliflozin’ OR ‘canagliflozin’ OR ‘luseogliflozin’ OR ‘ertugliflozin’] OR [‘angiotensin‐converting |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 81 records: agreement 80/81 , disagreement 1.2% | Y | independently extracted by two reviewers. Any disagreements were discussed and evaluated by a third reviewer. For each study, |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 81 Records screened (deduplicated) 81 Excluded at | Y | studies included in the network meta‐analysis. Table 1 Basic characteristics of included studies Type of HF First author, |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 81 records: agreement 80/81 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 3fb64a1e01434eb6ee9ea8a764a84c749270dfff Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### semaglutide-obesity-mace

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search terms: “glucagon-like peptide-1 receptor agonist,” “dual GLP-1/GIP receptor agonists,” “semaglutide,” “lixisenatide,” “exenatide,” “albiglutide,” “liraglutide,” “dulaglutide,” “tirzepatide,” “randomized |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 66 records: agreement 66/66 , disagreement 0.0% | Y | independent reviewers (M.-I.S., L.P.) searched for published randomized placebo-controlled trials testing GLP-1 RAs or GIP/GLP-1 RA in adults |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 66 Records screened (deduplicated) 66 Excluded at | Y | PRISMA flowchart of the meta-analysis is presented. Table 1. Main characteristics of randomized-controlled trials ( n = 16) |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 66 records: agreement 66/66 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 3fb64a1e01434eb6ee9ea8a764a84c749270dfff Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO database (CRD42024515966). All supporting data are available within the article and its Supplemental Files . Data sources |

### sglt2-ckd-progression

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | N |  |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 8.6% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 35 records: agreement 32/35 , disagreement 8.6% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 35 Records screened (deduplicated) 35 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 35 records: agreement 32/35 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 38478f5e060a9d63bcb073cb652d0e6f70d27c58 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### sglt2-hfref-hosp-cvdeath

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy and selection criteria We searched MEDLINE and EMBASE from inception until September 2021 using groups of |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 11.1% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 18 records: agreement 16/18 , disagreement 11.1% | Y | Two reviewers independently extracted data on study characteristics, baseline patient demographics, intervention, and outcomes. Risk of bias was |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 18 Records screened (deduplicated) 18 Excluded at | Y | PRISMA Flow Diagram. Figure S2. Forest plot demonstrating composite renal outcomes between patients on SGLT2 inhibitors versus placebo/control |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 18 records: agreement 16/18 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 43f5f12e367109bebd37936a8177ef00c6dcf1f6 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | protocol for this systematic review and meta‐analysis was not registered. The data underlying this article are available in |

### spironolactone-hfref-mortality

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy, selection criteria, and data extraction A systematic search was performed in PubMed, Web of Science, WANGFANG |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.4% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 225 records: agreement 224/225 , disagreement 0.4% | Y | independently reviewed by the same two investigators. Any discrepancies were resolved by consensus. Two authors extracted data from |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 225 Records screened (deduplicated) 225 Excluded at | Y | flow diagram. Flowchart showing a systematic review process. Initially, 10,963 records were identified through database searching and none |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 225 records: agreement 224/225 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 5d75f715df8176e9e9153fb477848176b84a0e6b Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO: CRD 42022304966) and followed the guidelines outlined in the PRISMA statement for conducting this meta-analysis ( Table |

### statins-primary-prevention-elderly

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy We reviewed Pubmed, EMBASE, Cochrane Library and Web of Science for related literatures from the inception |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 10.7% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 28 records: agreement 25/28 , disagreement 10.7% | Y | Two authors independently screened the studies’ titles and abstracts, then reviewed the full texts of potentially eligible studies. |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 28 Records screened (deduplicated) 28 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 28 records: agreement 25/28 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 036ee46c6c45cb5c10607def1eeda86ba536d750 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | protocol is consistent with a previous study [ 14 ], and has been registered on the INPLASY website |

### ticagrelor-vs-clopidogrel-acs

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy and eligibility criteria for study selection Randomized controlled trials comparing the clinical efficacy of ticagrelor and |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 6.5% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 31 records: agreement 29/31 , disagreement 6.5% | Y | Two investigators (QT and SX) independently screened the articles and extracted the data from the included studies using |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 31 Records screened (deduplicated) 31 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 31 records: agreement 29/31 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 3fb64a1e01434eb6ee9ea8a764a84c749270dfff Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### tocilizumab-covid19-mortality

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | electronic databases between October 2020 and January 2021. Searches were not restricted by trial status or language. Additional |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 0.0% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 50 records: agreement 50/50 , disagreement 0.0% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 50 Records screened (deduplicated) 50 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 50 records: agreement 50/50 | N |  |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 38478f5e060a9d63bcb073cb652d0e6f70d27c58 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO Identifier: CRD42021230155. Original language English Pages (from-to) 499-518 Number of pages 20 Journal JAMA Volume 326 Issue |

### tranexamic-acid-pph

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy and selection criteria This systematic review with IPD meta-analysis was prospectively registered on PROSPERO (CRD42022345775), and |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 1.3% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 76 records: agreement 75/76 , disagreement 1.3% | Y | disagreements between the two authors in the extracted data or risk of bias assessments were resolved through discussion. |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 76 Records screened (deduplicated) 76 Excluded at | N |  |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 76 records: agreement 75/76 | Y | excluded because they were ongoing, had an unclear or ineligible trial design, or did not assess tranexamic acid. |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) dcb1b98082b6416b68ee073b09460626cfe07f0a Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO (CRD42022345775), and the protocol has been published previously. 4 We report this systematic review and IPD meta-analysis |

### esketamine-trd-madrs

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | search strategy PubMed/MEDLINE, Embase, the Cochrane Library, PsycINFO, ClinicalTrials.gov, and the WHO ICTRP were searched from inception to |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 8.8% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 136 records: agreement 124/136 , disagreement 8.8% | Y | two reviewers independently screened titles and abstracts, followed by full-text assessment of potentially eligible reports. Disagreements were resolved |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 136 Records screened (deduplicated) 136 Excluded at | Y | PRISMA 2020 flow diagram ( 29 ). Eligibility criteria Eligibility criteria were predefined using the Population–Intervention–Comparator–Outcome–Study design (PICOS) |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 136 records: agreement 124/136 | Y | Reasons for exclusion at full-text stage were recorded. The selection process was summarized in the PRISMA 2020 flow |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 5e2b43c6f3d8a70d86a8150e0984d22c73ffd9f7 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | review was not prospectively registered. The study selection process was documented using a revised PRISMA 2020 flow diagram |

### melatonin-primary-insomnia-sol

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | PubMed was searched by two reviewers (AQ and EFO) using the terms “Melatonin” and “Sleep Disorder”. The search |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 12.7% | N |  |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 126 records: agreement 110/126 , disagreement 12.7% | N |  |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 126 Records screened (deduplicated) 126 Excluded at | Y | PRISMA 2009 Flow Chart. Flow Diagram. Flow chart showing the selection of studies for this review. (DOC) Click |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 126 records: agreement 110/126 | Y | studies were selected. A total of 249 manuscripts were excluded for the following reasons: 123 were not randomized |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) 146edbf724354bd40134ccaeae7719aebdf9f5f8 Committed (UTC) 2026-09-11 Declared analysis method Random-effects inverse-variance on the log ratio (log | N |  |

### semaglutide-obesity-weight

| item | ours | ours quote | comparator | comparator quote |
|---|---:|---|---:|---|
| 7 search strategy | Y | Full search strategy, verbatim, every source ✓ present Search tab — the exact PubMed and ClinicalTrials.gov queries are | Y | Search strategy This systematic review and meta-analysis was conducted in accordance with the Preferred Reporting Items for Systematic |
| 7 verbatim re-runnable | Y | verbatim and are re-runnable. 8 Selection process (screeners, disagreement) ✓ present Two independently-implemented rule screeners; disagreement rate 6.3% | Y | [MeSH] and Emtree terms where applicable) with free-text keywords and Boolean operators. The following search terms and their |
| 8 dual independent screening | Y | Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 143 records: agreement 134/143 , disagreement 6.3% | Y | Two reviewers independently screened titles, abstracts, and full-text articles according to the predefined eligibility criteria. A total of |
| 16a flow diagram | Y | Study selection flow (PRISMA 2020) Stage n Records identified (committed search) 143 Records screened (deduplicated) 143 Excluded at | Y | PRISMA flowchart. PRISMA = Preferred Reporting Items for Systematic Reviews and Meta-Analyses. 3.2. Study characteristics The analysis included |
| 16b exclusions-with-reasons | Y | exclusions with reasons). Dual independent screening (PRISMA item 8) Two independently-implemented rule screeners over 143 records: agreement 134/143 | Y | full-text articles to be evaluated for eligibility. Of these, 5 were excluded for reasons such as involving patients |
| 24 registration/PROSPERO | Y | Registration (protocol commit SHA) fe53c76aad18c0fd8369e3c1fe171406c0f85e7f Committed (UTC) 2026-09-12 Declared analysis method Random-effects inverse-variance on the log ratio (log | Y | PROSPERO or any other systematic review registry. 2.2. Search strategy This systematic review and meta-analysis was conducted in |
