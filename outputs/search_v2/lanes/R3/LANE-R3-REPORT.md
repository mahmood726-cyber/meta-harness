R3 VERDICT: RESOLVED 15 of 20, AMBIGUOUS 1 of 20, UNRESOLVED 4 of 20; of the resolved, 10 of 15 are already in the r2 candidate set

## Coverage

`lane_r3/identifier_proposals.json` covers 20 of 20 identifier-less benchmark positives from `registry/search_benchmark.json`.

The benchmark was not edited. Raw HTTP response bodies used as evidence are saved under `lane_r3/raw/` as JSON or XML files.

Validation run before this report was written:

- Expected identifier-less positives: 20
- Proposal objects written: 20
- Same order as benchmark: true
- Counts: RESOLVED 15, AMBIGUOUS 1, UNRESOLVED 4
- Resolved already in r2 candidates: 10 of 15
- Missing evidence files: none
- Missing verbatim identifiers in evidence: none

## Proposals

| slug | trial | status | identifier | in_r2_candidates | evidence file |
|---|---|---|---|---|---|
| colchicine-postop-af | five audit-named trials | AMBIGUOUS | no single identifier; alternatives include PMID 29237033, PMID 23040570, PMID 24508207, PMID 27223641; Sarzaeem remains no-ID | false | `lane_r3/raw/006-pubmed-colchicine-postop-af-bessissow-efetch.xml` |
| colchicine-recurrent-pericarditis | ICAP | RESOLVED | PMID 23992557; NCT00128453; DOI 10.1056/NEJMoa1208536 | true | `lane_r3/raw/019-pubmed-colchicine-recurrent-pericarditis-icap-efetch.xml` |
| corticosteroids-cap-mortality | El-Ghamrawy | UNRESOLVED | null | false | `lane_r3/raw/099-pubmed-cap-el-ghamrawy-author-esearch.json` |
| corticosteroids-cap-mortality | McHardy | RESOLVED | PMID 4404939; DOI 10.1136/bmj.4.5840.569 | false | `lane_r3/raw/170-pubmed-mchardy-4404939-efetch.xml` |
| corticosteroids-cap-mortality | Mikami | RESOLVED | PMID 17710485; DOI 10.1007/s00408-007-9020-3 | true | `lane_r3/raw/028-pubmed-corticosteroids-cap-mortality-mikami-efetch.xml` |
| corticosteroids-cap-mortality | Nafae | RESOLVED | DOI 10.1016/j.ejcdt.2013.03.009 | false | `lane_r3/raw/175-doi-nafae-unixref.xml` |
| corticosteroids-cap-mortality | Sabry | RESOLVED | DOI 10.4236/pp.2011.22009 | false | `lane_r3/raw/176-doi-sabry-unixref.xml` |
| corticosteroids-cap-mortality | Snijders | RESOLVED | PMID 20133929; NCT00170196; DOI 10.1164/rccm.200905-0808OC | true | `lane_r3/raw/034-pubmed-corticosteroids-cap-mortality-snijders-efetch.xml` |
| corticosteroids-cap-mortality | SONIA | RESOLVED | PMID 41159889; DOI 10.1056/NEJMoa2507100 | true | `lane_r3/raw/036-pubmed-corticosteroids-cap-mortality-sonia-efetch.xml` |
| dpp4-mace-t2d | TECOS (3-point MACE from primary publication) | RESOLVED | PMID 26052984; NCT00790205; DOI 10.1056/NEJMoa1501352 | true | `lane_r3/raw/048-pubmed-dpp4-mace-t2d-tecos-efetch.xml` |
| empagliflozin-hfpef-hosp | EMPA-VISION | RESOLVED | PMID 37070436; NCT03332212; DOI 10.1161/CIRCULATIONAHA.122.062021 | true | `lane_r3/raw/052-pubmed-empagliflozin-hfpef-hosp-empa-vision-efetch.xml` |
| glp1-ra-mace-t2d | FLOW | RESOLVED | PMID 38785209; NCT03819153; DOI 10.1056/NEJMoa2403347 | true | `lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml` |
| glp1-ra-mace-t2d | FREEDOM-CVO | RESOLVED | PMID 34873344; NCT01455896; DOI 10.1038/s41591-021-01584-3 | true | `lane_r3/raw/139-pubmed-freedom-cvo-primary-34873344-efetch.xml` |
| iv-iron-hfref-hosp | IRON-HF | RESOLVED | PMID 23680589; NCT00386126; DOI 10.1016/j.ijcard.2013.04.181 | true | `lane_r3/raw/070-pubmed-iv-iron-hfref-hosp-iron-hf-efetch.xml` |
| iv-iron-hfref-hosp | Toblli 2007 | RESOLVED | PMID 17950147; DOI 10.1016/j.jacc.2007.07.029 | true | `lane_r3/raw/074-pubmed-iv-iron-hfref-hosp-toblli-2007-efetch.xml` |
| probiotics-aad-prevention | Helps 2015 | UNRESOLVED | null | false | `lane_r3/raw/081-pubmed-probiotics-aad-prevention-helps-2015-esearch.json` |
| probiotics-aad-prevention | Horosheva | RESOLVED | DOI 10.1099/jmmcr.0.004036 | false | `lane_r3/raw/177-doi-horosheva-unixref.xml` |
| probiotics-aad-prevention | Iamharit 2010 | UNRESOLVED | null | false | `lane_r3/raw/083-pubmed-probiotics-aad-prevention-iamharit-esearch.json` |
| probiotics-aad-prevention | Khanal 2015 | UNRESOLVED | null | false | `lane_r3/raw/084-pubmed-probiotics-aad-prevention-khanal-esearch.json` |
| probiotics-aad-prevention | Pirker 2012 | RESOLVED | DOI 10.1080/09540105.2012.689816 | false | `lane_r3/raw/178-doi-pirker-unixref.xml` |

## Commands Run

Long PowerShell here-string Python commands are recorded by purpose and generated raw range.

1. `Get-Content -Raw -LiteralPath .\LANE_PROMPT.md`
2. `Get-Content -Raw -LiteralPath F:\ProjectIndex\INDEX.md`
3. `Get-Content -Raw -LiteralPath F:\E156\rewrite-workbook.txt`
4. `git status --short`
5. `rg --files`
6. `Get-Content -Raw -LiteralPath .\registry\search_benchmark.json`
7. `Get-Content -Raw -LiteralPath .\registry\search_benchmark_split.json`
8. `Get-Content -Raw -LiteralPath .\outputs\search_v2\candidates-2026-09-15r2-all.json`
9. `python -c "<list NAME_ONLY positives from registry/search_benchmark.json>"`
10. `Get-Content -Raw -LiteralPath .\topics\colchicine-postop-af.json`
11. `Get-Content -Raw -LiteralPath .\topics\colchicine-recurrent-pericarditis.json`
12. `Get-Content -Raw -LiteralPath .\topics\corticosteroids-cap-mortality.json`
13. `Get-Content -Raw -LiteralPath .\topics\dpp4-mace-t2d.json`
14. `Get-Content -Raw -LiteralPath .\topics\empagliflozin-hfpef-hosp.json`
15. `Get-Content -Raw -LiteralPath .\topics\glp1-ra-mace-t2d.json`
16. `Get-Content -Raw -LiteralPath .\topics\iv-iron-hfref-hosp.json`
17. `Get-Content -Raw -LiteralPath .\topics\probiotics-aad-prevention.json`
18. `Get-Content -Raw -LiteralPath .\protocols\colchicine-postop-af.md`
19. `Get-Content -Raw -LiteralPath .\protocols\colchicine-recurrent-pericarditis.md`
20. `Get-Content -Raw -LiteralPath .\protocols\corticosteroids-cap-mortality.md`
21. `Get-Content -Raw -LiteralPath .\protocols\dpp4-mace-t2d.md`
22. `Get-Content -Raw -LiteralPath .\protocols\empagliflozin-hfpef-hosp.md`
23. `Get-Content -Raw -LiteralPath .\protocols\glp1-ra-mace-t2d.md`
24. `Get-Content -Raw -LiteralPath .\protocols\iv-iron-hfref-hosp.md`
25. `Get-Content -Raw -LiteralPath .\protocols\probiotics-aad-prevention.md`
26. `Get-Content -Raw -LiteralPath .\docs\known_eligible_missing.json`
27. `rg -n "audit|five audit|audit-named|El-Ghamrawy|McHardy|Mikami|Nafae|Sabry|Snijders|SONIA|EMPA-VISION|IRON-HF|Toblli|FREEDOM-CVO|FLOW|TECOS|Helps|Horosheva|Iamharit|Khanal|Pirker" docs registry topics protocols`
28. `Get-Content -Raw -LiteralPath .\docs\evidence\probiotics-search-diagnostic-2026-09-15\01-their-42.txt`
29. `Get-Content -Raw -LiteralPath .\docs\reviews\colchicine-postop-af\review.json`
30. `rg -n "k=3->8|Sarzaeem|Zarpelon|Bessissow|Deftereos|COCS|COPPS AF|29237033|27223641|five audit-named" docs\reviews\colchicine-postop-af docs\known_eligible_missing.json registry\search_benchmark.json`
31. `python -c "<inspect docs/reviews/colchicine-postop-af/review.json primary keys>"`
32. `python -c "<inspect review missing fields for selected slugs>"`
33. `python -c "<check r2 candidate hits for known identifiers>"`
34. `Test-Path -LiteralPath .\lane_r3`
35. `Get-ChildItem -LiteralPath . -Force | Select-Object Name,Mode,Length`
36. `@'<HTTP capture pass for PubMed, Europe PMC, and CT.gov; saved lane_r3/raw/001-097>'@ | python -`
37. `Get-ChildItem -LiteralPath .\lane_r3\raw | Select-Object Name,Length | Format-Table -AutoSize`
38. `(Get-ChildItem -LiteralPath .\lane_r3\raw | Measure-Object).Count`
39. `git status --short`
40. `@'<parse lane_r3/raw records; initial broad output>'@ | python -`
41. `@'<parse CAP/DPP4/EMPA/GLP1/IV raw records>'@ | python -`
42. `@'<parse subset lane_r3/raw/047-068>'@ | python -`
43. `Test-Path -LiteralPath .\cache\corticosteroids-cap-mortality\comparator_fulltext.txt`
44. `rg -n "El-Ghamrawy|Ghamrawy|McHardy|Mikami|Nafae|Sabry|Snijders|SONIA|Confalonieri|Meijvis|Blum|Torres|CAPE COD|Meduri|Fernandez" cache\corticosteroids-cap-mortality docs\reviews\corticosteroids-cap-mortality docs\evidence registry topics protocols`
45. `rg -n "FREEDOM-CVO|ITCA|exenatide|NCT01455896|Intarcia|cardiovascular outcomes" cache\glp1-ra-mace-t2d docs\reviews\glp1-ra-mace-t2d registry topics protocols`
46. `Get-ChildItem -LiteralPath .\cache\corticosteroids-cap-mortality | Select-Object Name,Length | Format-Table -AutoSize`
47. `Get-Content ... | Select-Object -Index 60..130` (failed: PowerShell range passed as string)
48. `Get-Content ... | Select-Object -Index 40..55` (failed: PowerShell range passed as string)
49. `python -c "<inspect docs/reviews/corticosteroids-cap-mortality/review.json screened-in CAP IDs/outcomes>"`
50. `python -c "<search cache/corticosteroids-cap-mortality/records.json for CAP surnames>"`
51. `@'<HTTP capture pass for targeted PubMed, Europe PMC, CT.gov, Crossref; saved lane_r3/raw/098-138>'@ | python -`
52. `@'<parse lane_r3/raw/098-138>'@ | python -`
53. `@'<parse subset lane_r3/raw/123-134>'@ | python -`
54. `git status --short`
55. `(Get-ChildItem -LiteralPath .\lane_r3\raw | Measure-Object).Count`
56. `Get-ChildItem -LiteralPath .\lane_r3\raw | Select-Object -Last 15 Name,Length | Format-Table -AutoSize`
57. `@'<HTTP capture pass for exact-title checks, Crossref/OpenAlex unresolved checks, and FREEDOM-CVO PubMed EFetch; saved lane_r3/raw/139-169>'@ | python -`
58. `@'<parse lane_r3/raw/130-169>'@ | python -` (failed: Windows cp1252 UnicodeEncodeError)
59. `@'<parse lane_r3/raw/139-169 with ASCII escaping>'@ | python -`
60. `rg -n "34873344|s41591|ArticleId|AbstractText|ClinicalTrials" .\lane_r3\raw\139-pubmed-freedom-cvo-primary-34873344-efetch.xml`
61. `@'<parse article-level identifiers from lane_r3/raw/139-pubmed-freedom-cvo-primary-34873344-efetch.xml>'@ | python -`
62. `@'<check proposed IDs against outputs/search_v2/candidates-2026-09-15r2-all.json>'@ | python -`
63. `Get-ChildItem -LiteralPath .\lane_r3 -Force | Select-Object Name,Mode,Length | Format-Table -AutoSize`
64. `Get-Content -Raw -LiteralPath .\registry\search_benchmark.json | python -c "<one-liner positive count>"` (failed: SyntaxError from literal newlines)
65. `@'<fetch PubMed EFetch PMID 4404939; saved lane_r3/raw/170-pubmed-mchardy-4404939-efetch.xml>'@ | python -`
66. `@'<parse lane_r3/raw/170-pubmed-mchardy-4404939-efetch.xml>'@ | python -`
67. `@'<inspect registry/search_benchmark.json top-level shape>'@ | python -`
68. `@'<naive benchmark positive loop>'@ | python -` (failed: AttributeError on top-level metadata)
69. `@'<correct benchmark NAME_ONLY positive loop through topics>'@ | python -`
70. `rg -n "five audit-named|k=3->8|audit-named|Sarzaeem|Zarpelon|Bessissow|Deftereos|COCS|COPPS AF|COPPS" docs registry topics protocols cache outputs`
71. `@'<inspect docs/known_eligible_missing.json root shape>'@ | python -`
72. `@'<inspect docs/known_eligible_missing.json topics.colchicine-postop-af>'@ | python -`
73. `@'<parse colchicine ambiguous candidate raw files 006, 008, 011, 014, 015, 017>'@ | python -`
74. `@'<parse probiotic raw files 081-097 and 129-133>'@ | python -` (failed after useful output: Windows cp1252 UnicodeEncodeError)
75. `@'<print query translations for unresolved PubMed/Europe PMC searches>'@ | python -`
76. `@'<validate lane_r3/identifier_proposals.json against benchmark and evidence>'@ | python -` (first validation found escaped/missing identifier issues)
77. `rg -n "10.1016|ejcdt|10\\.1016|10\\/1016|10.4236|4236|10.1002/ehf2.13374|10.1016/j.ijcard.2006.12.006" .\lane_r3\raw\125-crossref-cap-nafae-crossref.json .\lane_r3\raw\126-crossref-cap-sabry-crossref.json .\lane_r3\raw\160-crossref-cap-sabry-author-title.json .\lane_r3\raw\161-crossref-cap-sabry-bibliographic.json .\lane_r3\raw\056-ctgov-empagliflozin-hfpef-hosp-empa-vision.json .\lane_r3\raw\079-ctgov-iv-iron-hfref-hosp-iron-hf.json`
78. `@'<print snippets around DOI strings in selected raw files>'@ | python -`
79. `Get-ChildItem -LiteralPath .\lane_r3\raw | Where-Object { [int]($_.Name.Substring(0,3)) -ge 069 -and [int]($_.Name.Substring(0,3)) -le 080 } | Select-Object Name,Length | Format-Table -AutoSize`
80. `@'<parse EMPA-VISION and IRON-HF design/result PubMed XML files>'@ | python -`
81. `@'<DOI CSL JSON content-negotiation capture; saved lane_r3/raw/171-174>'@ | python -`
82. `rg -n "DOI|10\\.1016|10\\.4236|10\\.1099|10\\.1080|ejcdt|pp.2011|jmmcr|09540105" .\lane_r3\raw\171-doi-doi-nafae-csl.json .\lane_r3\raw\172-doi-doi-sabry-csl.json .\lane_r3\raw\173-doi-doi-horosheva-csl.json .\lane_r3\raw\174-doi-doi-pirker-csl.json`
83. `@'<print snippets from lane_r3/raw/171-174>'@ | python -`
84. `@'<DOI Crossref UNIXREF XML content-negotiation capture; saved lane_r3/raw/175-178>'@ | python -`
85. `@'<validate lane_r3/identifier_proposals.json against benchmark, r2 candidates, raw-file existence, and verbatim identifiers>'@ | python -`

## File Edits

- Added `lane_r3/identifier_proposals.json`.
- Patched `lane_r3/identifier_proposals.json` after validation to add DOI UNIXREF evidence and correct two design-paper alternative DOIs.
- Added `LANE-R3-REPORT.md`.
