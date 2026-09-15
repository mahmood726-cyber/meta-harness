W-noac-vs-warfarin-af-stroke VERDICTS: NEW 112; ELIGIBLE_RCT 6; ELIGIBLE_RCT_NO_PRIMARY 1; NOT_RCT 73; WRONG_* 12; DUPLICATE_OF_ACCOUNTED 0; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 20
automated screen agreed on 7 of 112 verified

r2 includes 272 of 12238; already accounted for 10; NEW 262 (MEASURED)
prior lane NOT_VERIFIED_CAP remainder 112 (MEASURED); this artefact verifies those 112 objects per LANE_PROMPT.md (MEASURED).
Generic r2 NEW minus prior-lane remainder = 150 already verified by the prior lane (MEASURED).
The two header count lines are MEASURED from lane_v/noac-vs-warfarin-af-stroke.json; verdict rationales are INFERRED from the quoted record spans and the protocol rules.

ELIGIBLE_RCT ids with titles (pool-moving candidates; MEASURED):
- 23929423 ? Prevention of stroke and systemic embolism with rivaroxaban compared with warfarin in Chinese patients with atrial fibrillation.
- 22664783 ? Rivaroxaban vs. warfarin in Japanese patients with atrial fibrillation – the J-ROCKET AF study –.
- 22664798 ? Randomized, multicenter, warfarin-controlled phase II study of edoxaban in Japanese patients with non-valvular atrial fibrillation.
- 21136011 ? Safety of edoxaban, an oral factor Xa inhibitor, in Asian patients with non-valvular atrial fibrillation.
- 21670542 ? Safety and efficacy of the oral direct factor xa inhibitor apixaban in Japanese patients with non-valvular atrial fibrillation. -The ARISTOTLE-J study-.
- 17950801 ? Dabigatran with or without concomitant aspirin compared with warfarin alone in patients with nonvalvular atrial fibrillation (PETRO Study).

ELIGIBLE_RCT_NO_PRIMARY ids with titles (declared-absent candidates; MEASURED):
- 20694273 ? Randomised, parallel-group, multicentre, multinational phase 2 study comparing edoxaban, an oral factor Xa inhibitor, with warfarin for stroke prevention in patients with atrial fibrillation.

DUPLICATE_OF_ACCOUNTED pairs (MEASURED):
- none

Commands run:
- Get-Content -Raw -LiteralPath .\LANE_PROMPT.md
- Get-Content -Raw -LiteralPath .\LIVE_CONTEXT.md (failed: file absent)
- git status --short
- PowerShell Test-Path for F:\ProjectIndex\INDEX.md, F:\E156\rewrite-workbook.txt, C:\ProjectIndex\INDEX.md, C:\E156\rewrite-workbook.txt
- Get-Content -TotalCount 120 -LiteralPath F:\ProjectIndex\INDEX.md
- Get-Content -TotalCount 120 -LiteralPath F:\E156\rewrite-workbook.txt
- Get-ChildItem -Force
- PowerShell Test-Path/Get-Item for C:\meta-harness\outputs\search_v2\verification\noac-vs-warfarin-af-stroke\noac-vs-warfarin-af-stroke.json
- Get-Content -Raw -LiteralPath .\protocols\noac-vs-warfarin-af-stroke.md
- Get-Content -Raw -LiteralPath .\topics\noac-vs-warfarin-af-stroke.json
- Get-Content -Raw -LiteralPath .\docs\reviews\noac-vs-warfarin-af-stroke\review.json
- python -c first-lane verdict counter
- python -c legacy/snapshot/review denominator inspection (failed: SyntaxError from inline def quoting)
- PowerShell here-string | python - : legacy include count, r2 snapshot counts, review trials/declared-absent paths
- PowerShell here-string | python - : compare r2 NEW set with prior-lane NOT_VERIFIED_CAP remainder
- PowerShell here-string | python - : capped-record abstract/NCT-field audit
- PowerShell here-string | python - : PubMed efetch PMID 19845524 to lane_v/noac-vs-warfarin-af-stroke-raw/pubmed_19845524.xml
- PowerShell here-string | python - : capped records 1-40 inspection
- PowerShell here-string | python - : capped records 41-80 inspection
- PowerShell here-string | python - : capped records 57-68 reinspection after clipped output
- PowerShell here-string | python - : capped records 81-112 inspection
- PowerShell here-string | python - : capped records 13-28 reinspection after clipped output
- PowerShell here-string | python - : prior-lane non-capped verdict-style samples
- PowerShell here-string | python - : NCT snapshot key inspection
- PowerShell here-string | python - : prior-lane NCT object inspection
- PowerShell here-string | python - : parse lane_v/noac-vs-warfarin-af-stroke-raw/pubmed_19845524.xml title/publication types
- PowerShell here-string | python - : full abstracts for selected eligible/wrong-comparator candidates
- PowerShell here-string | python - : capped PMID title list
- PowerShell here-string | python - : generate lane JSON/report and validate counts/quotes (this command)
