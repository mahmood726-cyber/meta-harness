# Protocol - systemic corticosteroids for mortality in hospitalised community-acquired pneumonia

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs.

## PICO
- **P** - adults hospitalised with community-acquired pneumonia (CAP).
- **I** - systemic corticosteroids added to standard antimicrobial/supportive care.
- **C** - placebo, usual care, standard care, or conventional therapy.
- **O (primary)** - all-cause mortality at 30 days or in hospital.
- **O (harms)** - hyperglycaemia; gastrointestinal bleeding.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), systemic corticosteroid vs placebo/usual care.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - 30-day mortality preferred; in-hospital mortality accepted when
  that is the trial's reported short-term mortality window.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - adult hospitalised CAP or severe CAP population by title or registry conditions;
- **I3** - systemic corticosteroid vs placebo/usual/standard care;
- **design** - randomised comparison; double-blinding is not required because the
  target comparator includes placebo or standard-care controls.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational study, protocol-only);
- **X2** - wrong population (for example COVID-19/SARS-CoV-2 pneumonia, influenza,
  paediatric CAP, Pneumocystis pneumonia, scrub typhus pneumonitis, or ARDS without
  CAP as the title/condition population);
- **X3** - wrong intervention/comparison (no systemic corticosteroid-vs-control contrast);
- **X5** - off-topic: a primary trial of another topic/disease in this set
  (negative control).

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> 30-day or in-hospital all-cause mortality in an abstract-extractable form is
> recorded as target-result status at extraction, never as an exclusion. A
> published effect plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/corticosteroids-cap-mortality/records.json; screening replays offline)
- PubMed: targeted corticosteroid x community-acquired pneumonia x randomised
  placebo/control queries for hydrocortisone, methylprednisolone, prednisone, and
  dexamethasone trial reports.
- ClinicalTrials.gov: condition "community-acquired pneumonia", intervention
  "hydrocortisone".
- Comparator-reference seeding is disabled for this topic because the fixed NCT
  deduplication rule can let later secondary/subgroup reports replace the original
  trial report. Recall is instead checked with named positive controls.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells
of a study only if it has a zero cell. DerSimonian-Laird forbidden. Engine
validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
Wu et al., *Journal of Critical Care* 2024, "Efficacy and safety of corticosteroids
for the treatment of community-acquired pneumonia: A systematic review and
meta-analysis of randomized controlled trials" (PMID 38128217, DOI
10.1016/j.jcrc.2023.154507; Unpaywall is_oa=true; no direct PubMed Central full
text resolved). Its abstract reports 15 RCTs and all-cause mortality RR 0.69
(95% CI 0.53-0.89).

## Controls
- **Positive** - the search must recover and include CAPE COD hydrocortisone
  (PMID 36942789), Torres/JAMA methylprednisolone severe CAP (PMID 25688779),
  and STEP prednisone CAP (PMID 25608756).
- **Negative** - RECOVERY dexamethasone for COVID-19 (PMID 32678530) must be
  recovered and excluded as the wrong population.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 38128217) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 30917856, 31261585; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 7 of 10 of the comparator's eligible trials; with this route and the full retrieval below, 10 of 10 (9 of 10 without the comparator's own reference list, which contains its trials by construction). The route retrieves 110 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A3 Concept query: not adopted** (KEEP_CURRENT: volume 11936 > cap 5000; recorded call mc-79bfb69b43134dba745af5d5cd026bfb.json).

## Amendment 2026-10-06 -- identification sources, query audit round 2 (search+screen audit)

- **A4 Concept query added, round 2 (independent blind proposer)** (union; none removed): `((("Pneumonia"[Mesh] OR "Pneumonia, Bacterial"[Mesh] OR "Community-Acquired Infections"[Mesh] OR pneumonia[tiab] OR pneumonias[tiab] OR pneumonitis[tiab] OR "community acquired pneumonia"[tiab] OR "community-acquired pneumonia"[tiab] OR "community acquired pneumonias"[tiab] OR "community-acquired pneumonias"[tiab] OR CAP[tiab]) AND ("Community-Acquired Infections"[Mesh] OR "community acquired"[tiab] OR "community-acquired"[tiab] OR outpatient-acquired[tiab] OR "outpatient acquired"[tiab])) AND ("Adult"[Mesh] OR adult*[tiab] OR aged[tiab] OR elderly[tiab] OR inpatient*[tiab] OR in-patient*[tiab] OR hospitali*[tiab] OR hospital*[tiab] OR admitted[tiab] OR admission*[tiab] OR ward*[tiab])) AND ("Adrenal Cortex Hormones"[Mesh] OR "Glucocorticoids"[Mesh] OR "Hydrocortisone"[Mesh] OR "Methylprednisolone"[Mesh] OR "Prednisone"[Mesh] OR "Prednisolone"[Mesh] OR "Dexamethasone"[Mesh] OR corticosteroid*[tiab] OR cortico-steroid*[tiab] OR steroid*[tiab] OR glucocorticoid*[tiab] OR glucocorticosteroid*[tiab] OR "adrenal cortex hormone*"[tiab] OR hydrocortisone[tiab] OR cortisol[tiab] OR Solu-Cortef[tiab] OR SoluCortef[tiab] OR methylprednisolone[tiab] OR methyl-prednisolone[tiab] OR Medrol[tiab] OR "Solu-Medrol"[tiab] OR SoluMedrol[tiab] OR Depo-Medrol[tiab] OR DepoMedrol[tiab] OR Urbason[tiab] OR prednisone[tiab] OR prednisolone[tiab] OR Deltasone[tiab] OR Orasone[tiab] OR Meticorten[tiab] OR Pediapred[tiab] OR Prelone[tiab] OR Millipred[tiab] OR dexamethasone[tiab] OR Decadron[tiab] OR Dexasone[tiab] OR Hexadrol[tiab] OR betamethasone[tiab] OR Celestone[tiab] OR triamcinolone[tiab] OR Kenalog[tiab] OR Aristocort[tiab]) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])`. Proposed blind (recorded call mc-d30b9c5efab84c2bb4b42070e009aeee.json, model gpt-5.5); returns 274 records today; on the comparator's eligible trials the queries registered after the 2026-10-05 amendment match 7 of 10 and with this query 9 of 10. Limitation: the proposer may know well-known trials from training.
- **A4 Concept query added, precision variant (over-cap topic, volume target, still blind)** (union; none removed): `(("Pneumonia"[Mesh] AND "Community-Acquired Infections"[Mesh]) OR (("Pneumonia"[Mesh] OR pneumoni*[tiab] OR bronchopneumoni*[tiab]) AND ("community acquired"[tiab] OR "community-acquired"[tiab] OR "community onset"[tiab] OR "community-onset"[tiab] OR "community associated"[tiab] OR "community-associated"[tiab] OR "community contracted"[tiab] OR CAP[tiab])))) AND ("Adrenal Cortex Hormones"[Mesh] OR "Glucocorticoids"[Mesh] OR corticosteroid*[tiab] OR glucocorticoid*[tiab] OR glucocorticosteroid*[tiab] OR corticoid*[tiab] OR steroid*[tiab] OR "adrenal cortex hormone*"[tiab] OR hydrocortison*[tiab] OR cortisol[tiab] OR Cortef[tiab] OR "Solu-Cortef"[tiab] OR Efcortesol[tiab] OR Alkindi[tiab] OR Plenadren[tiab] OR methylprednisolon*[tiab] OR methylprednison*[tiab] OR "methyl prednisolone"[tiab] OR Medrol[tiab] OR "Solu-Medrol"[tiab] OR "Depo-Medrol"[tiab] OR Urbason[tiab] OR Metypred[tiab] OR prednison*[tiab] OR Deltasone[tiab] OR Rayos[tiab] OR Lodotra[tiab] OR Sterapred[tiab] OR Orasone[tiab] OR prednisolon*[tiab] OR Orapred[tiab] OR Prelone[tiab] OR Pediapred[tiab] OR Deltacortril[tiab] OR Solupred[tiab] OR dexamethason*[tiab] OR Decadron[tiab] OR Dexasone[tiab] OR Fortecortin[tiab] OR betamethason*[tiab] OR Celestone[tiab] OR Betnesol[tiab] OR Diprospan[tiab] OR cortison*[tiab] OR Cortone[tiab] OR triamcinolon*[tiab] OR Kenalog[tiab] OR Aristocort[tiab] OR deflazacort[tiab] OR Calcort[tiab] OR Emflaza[tiab] OR fludrocortison*[tiab] OR Florinef[tiab] OR paramethason*[tiab] OR meprednison*[tiab] OR fluocortolon*[tiab] OR cortivazol[tiab]) AND ("Randomized Controlled Trial"[pt] OR "Controlled Clinical Trial"[pt] OR randomized[tiab] OR randomised[tiab] OR placebo*[tiab] OR randomly[tiab] OR "Clinical Trials as Topic"[Mesh:noexp] OR trial[ti]) NOT (animals[Mesh] NOT humans[Mesh])`. Proposed blind (recorded call mc-e990029155e1e254fd55a5426264e960.json, model gpt-6-astra); returns 209 records today; on the comparator's eligible trials the queries registered after the 2026-10-05 amendment match 7 of 10 and with this query 9 of 10. Limitation: the proposer may know well-known trials from training.
