V-glp1-ra-mace-t2d VERDICTS: NEW 601; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 33; NOT_RCT 35; WRONG_* 13; DUPLICATE_OF_ACCOUNTED 18; UNDECIDABLE 0; NOT_VERIFIED_CAP 451; REGISTRY_ONLY 50
automated screen agreed on 34 of 150 verified
r2 includes 610 of 12243; already accounted for 9; NEW 601
legacy includes 9; pooled primary trials 8; declared-absent primary trials 1
All numbers in the lines above are MEASURED. Interpretive verdict notes are INFERRED from the quoted record text.
Cap applied: verified first 150 by (year desc, pmid/id); marked remaining 451 records NOT_VERIFIED_CAP. MEASURED.

ELIGIBLE_RCT ids with titles (could move the pool):
- 38785209: Effects of Semaglutide on Chronic Kidney Disease in Patients with Type 2 Diabetes.

DUPLICATE_OF_ACCOUNTED pairs:
- 39602568: Same HARMONY Outcomes trial as accounted PMID 30291013.
- 41380027: Same SOUL trial as accounted PMID 40162642.
- 41627802: Same SOUL trial as accounted PMID 40162642.
- 41879791: Same SOUL trial as accounted PMID 40162642.
- 39381950: Same EXSCEL trial as accounted PMID 28910237.
- 40154887: Same EXSCEL trial as accounted PMID 28910237.
- 40156843: Same SOUL trial as accounted PMID 40162642.
- 38271596: Same HARMONY Outcomes trial as accounted PMID 30291013.
- 39188242: Same SUSTAIN 6 trial as accounted PMID 27633186.
- 36700460: Same EXSCEL trial as accounted PMID 28910237.
- 36802715: Same AMPLITUDE-O trial as accounted PMID 34215025.
- 34775781: Same AMPLITUDE-O trial as accounted PMID 34215025.
- 34903039: Pooled analysis of already accounted SUSTAIN 6 PMID 27633186 and LEADER PMID 27295427.
- 34984808: Same REWIND trial as accounted PMID 31189511.
- 35582947: Same SUSTAIN 6/PIONEER 6 trials as accounted PMIDs 27633186 and 31185157.
- 36053803: Same HARMONY Outcomes trial as accounted PMID 30291013.
- 34153269: Same REWIND trial as accounted PMID 31189511.
- 34563178: Same REWIND trial as accounted PMID 31189511.

Raw HTTP bodies saved:
- lane_v/glp1-ra-mace-t2d-raw/pubmed_efetch_35415938.xml (PubMed efetch for PMID 35415938; no AbstractText was present, title used for verdict quote).

Commands run:
- Get-Content -Raw -LiteralPath 'LANE_PROMPT.md'
- if (Test-Path 'F:\ProjectIndex\INDEX.md') { Get-Content -Raw 'F:\ProjectIndex\INDEX.md' } else { 'MISSING:F:\ProjectIndex\INDEX.md' }
- if (Test-Path 'F:\E156\rewrite-workbook.txt') { Get-Content -Raw 'F:\E156\rewrite-workbook.txt' } else { 'MISSING:F:\E156\rewrite-workbook.txt' }
- git status --short
- Get-Content -Raw -LiteralPath 'protocols/glp1-ra-mace-t2d.md'
- Get-Content -Raw -LiteralPath 'topics/glp1-ra-mace-t2d.json'
- python -c legacy include command from LANE_PROMPT.md
- python review primary-trials probe (returned None for guessed keys)
- python review/outcomes and rg probes for primary trials and declared_absent_trials
- python r2 snapshot structure/count probes
- python denominator command (first attempt failed: one-line def SyntaxError)
- python denominator command (lambda rerun): measured r2 records/includes/accounted/NEW
- python first-150 header command (first f-string attempt failed in PowerShell quoting)
- python quoting smoke tests: python -c variable failed, pipeline to python - succeeded
- python first-150 header table command
- python abstract inspection commands for ranges 1-30, 8-24, 31-60, 38-52, 61-90, 73-77, 91-120, 101-107, 121-150, 130-142
- python full-record probe for NCT07172867 structured CT.gov fields
- python PubMed efetch for PMID 35415938 -> lane_v/glp1-ra-mace-t2d-raw/pubmed_efetch_35415938.xml
- python parse lane_v/glp1-ra-mace-t2d-raw/pubmed_efetch_35415938.xml for AbstractText
- python generate lane_v/glp1-ra-mace-t2d.json and LANE-V-glp1-ra-mace-t2d-REPORT.md
- python validation command for JSON count, quote exceptions, and report sum
- git status --short
