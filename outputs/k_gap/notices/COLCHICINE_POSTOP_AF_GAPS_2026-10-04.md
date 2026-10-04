# Notice for Mahmood: colchicine-postop-af, the two open eligible trials (2 of 4 matched)

Lane g1 (code branch g1/tocilizumab-finish), 2026-10-04. **A notice only.** No harness code was changed for this topic,
nothing was signed, and nothing was regenerated.

The resolution stands. On the merged acq e89dfe86 it reproduces exactly: DIFFERENT_CONCLUSION is
RESOLVED_AGAINST_COMPARATOR_ROW on COPPS-2 (Imazio [18]) (branch g1/sglt2-primary-prevention-hf, commit daec83da).

## 1. Sarzaeem [23]: identity resolved, outside our sources

- The comparator's own reference 23 (PMC9438305) is: Sarzaeem M, Shayan N, Bagheri J, Jebelli M, Mandegar M. "Low dose
  Colchicine in prevention of atrial fibrillation after coronary artery bypass graft: a double blind clinical trial".
  Tehran Univ Med J 2014;72:147-154. It has no PMID or DOI.
- Neither PubMed nor Europe PMC indexes it. A search for author "Sarzaeem" returns only orthopaedic papers.
- Our protocol's search sources (PubMed and CT.gov) therefore cannot retrieve it. It stays an OPEN gap and is NOT
  named out of scope: a retrieval limit is not an eligibility rule.

## 2. Imazio [19], the COPPS POAF substudy (PMID 22090167): screener architecture

- `_is_rct` refuses it on the title word "substudy" (X1). PubMed types it an RCT, and its abstract describes "the
  COPPS trial, a multicenter, double-blind, randomized trial". Its trial family NCT00128427 holds only this report.
- **Radius** (scripts/measure_x1_reason_evidence.py): 19 served X1 decisions contradict their own cited publication
  types. 12 of them are secondary-report titles across 9 topics.
- **Codex NR-C28** (read-only, logged) tested the narrow fix: admit a PubMed-RCT secondary report whose abstract says
  its patients were randomised, as its family's only report. **The fix is unsafe as stated:**
  - It would admit TRACES 41529541 (tranexamic-acid-pph). That report is a non-randomised biomarker comparison inside a
    randomised cohort.
  - It would admit 34637494 (colchicine-secondary-cv) and 26839075 (probiotics). Their randomised contrasts are a
    different intervention or a different population.
  - The regex misses the allocation wording of semaglutide 42503495 and 40189961.
  - "Missing family" must mean UNRESOLVED, never singleton.
- **What C28 recommends instead:** a family-report routing stage. In order:
  1. establish the parent randomised trial;
  2. establish the report's own randomised contrast against the topic's PICO;
  3. resolve family identity before assigning a pooling unit;
  4. pool once per family.
  It comes with P0 plants: TRACES, PLATO parent + subgroup, wrong-intervention controls, and title negatives.
- **Decision needed:** this changes the shared screener for every topic, so I have not done it. Until it exists,
  COPPS-POAF stays open and colchicine-postop-af cannot reach G1_MATCHED.
