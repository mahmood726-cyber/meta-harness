# Protocol - statins for primary prevention in older adults

**Registration.** The commit adding this file registers the review; its SHA is embedded
in the page's Protocol tab and Reproducibility tab. The protocol is committed before
the synthesis is run.

## PICO
- **P** - older adults (>=70 years) without established cardiovascular disease.
- **I** - statin therapy, including rosuvastatin, pravastatin, or atorvastatin.
- **C** - placebo, usual care, or no-statin control.
- **O (primary)** - major vascular events / major cardiovascular events.
- **O (harms)** - muscle symptoms/myopathy; new-onset diabetes.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), statin vs placebo/control.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial or randomised trial analysis;
- **I2** - title-level or registry-condition population is older/elderly adults;
- **I3** - title-level or registry intervention is a statin or statin name;
- **I4** - comparator is placebo, usual care, or control;
- **design** - randomised statin allocation; double-blinding is not required because
  usual-care trials are eligible.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, or PubMed record
  not indexed as a randomized controlled trial by the fixed screen);
- **X2** - wrong population (e.g. heart failure, atrial fibrillation, prior stroke,
  acute coronary syndrome, coronary disease, perioperative/non-cardiovascular disease);
- **X3** - wrong intervention/comparison (no statin-vs-placebo/usual-care/control contrast);
- **X5** - off-topic: a primary trial of another disease/topic in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether an included trial reports major
> vascular events, or gives a 2x2 table vs only an effect+CI, is recorded as
> target-result status at extraction - never as an exclusion. A published effect + 95% CI
> is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: focused statin-title searches for JUPITER older-person analyses, ALLHAT-LLT
  older-adult primary-prevention analyses, and STAREE older-adult atorvastatin reports.
- ClinicalTrials.gov: condition "Elderly", intervention "Atorvastatin".
- Comparator reference seeding is disabled for this topic because the resolved open-access
  comparator is an observational review; its reference list is not an RCT recall set for
  a randomized statin-vs-control harness.

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study
only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1
(<1e-6).

## Comparator (resolved; open-access confirmed)
Huang, Zhu, and Ya, *Reviews in Cardiovascular Medicine* 2022, "Statin use in older
people primary prevention on cardiovascular disease: an updated systematic review and
meta-analysis" (PMID 39076238, PMCID PMC11273788, DOI 10.31083/j.rcm2304114; Unpaywall
is_oa=true). It reports total cardiovascular events HR 0.75 (95% CI 0.66-0.85) in older
primary-prevention statin users versus no-statin users. This is an external benchmark,
not an RCT-only comparator; exact RCT-only elderly primary-prevention meta-analyses
found during resolution were not open access.

## Controls
- **Positive** - the search must recover and include the JUPITER older-person rosuvastatin
  analysis (PMID 20404379) and ALLHAT-LLT older-adult pravastatin analyses (PMIDs
  28531241 and 30251369).
- **Negative** - CORONA (rosuvastatin in older patients with systolic heart failure,
  PMID 17984166 - different disease/topic) must be recovered and EXCLUDED as wrong
  population.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 39076238) backward reference list (PubMed elink and Europe PMC) and its forward citations; no other open meta-analysis is held for this topic yet. Rationale: the registered search identified 0 of 0 of the comparator's eligible trials; with this route and the full retrieval below, 0 of 0 (0 of 0 without the comparator's own reference list, which contains its trials by construction). The route retrieves 51 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A3 Concept query: not adopted** (KEEP_CURRENT: no recall gain; recorded call mc-3d324a96f6a20f8241e1fd8fc6425fa6.json).

## Amendment 2026-10-07 -- search re-validated against the current comparator (active topics)

- **A6 Concept query added** (union; none removed): `((("Aged"[Mesh] OR "Aged, 80 and over"[Mesh] OR aged[tiab] OR elderly[tiab] OR elder*[tiab] OR geriatric*[tiab] OR "older adult"[tiab] OR "older adults"[tiab] OR "older person"[tiab] OR "older persons"[tiab] OR "older people"[tiab] OR senior*[tiab] OR septuagenarian*[tiab] OR octogenarian*[tiab] OR nonagenarian*[tiab] OR "70 years"[tiab] OR "70 year"[tiab] OR "75 years"[tiab] OR "75 year"[tiab]) AND ("Primary Prevention"[Mesh] OR "primary prevention"[tiab] OR "primary prevent*"[tiab] OR "without cardiovascular disease"[tiab] OR "without CVD"[tiab] OR "no cardiovascular disease"[tiab] OR "no CVD"[tiab] OR "free of cardiovascular disease"[tiab] OR "free from cardiovascular disease"[tiab] OR "cardiovascular disease-free"[tiab] OR "apparently healthy"[tiab] OR asymptomatic[tiab])) AND ("Hydroxymethylglutaryl-CoA Reductase Inhibitors"[Mesh] OR statin*[tiab] OR "hmg coa reductase inhibitor*"[tiab] OR "hmg-coa reductase inhibitor*"[tiab] OR "3-hydroxy-3-methylglutaryl coenzyme a reductase inhibitor*"[tiab] OR atorvastatin[tiab] OR Lipitor[tiab] OR rosuvastatin[tiab] OR Crestor[tiab] OR pravastatin[tiab] OR Pravachol[tiab] OR Selektine[tiab] OR simvastatin[tiab] OR Zocor[tiab] OR fluvastatin[tiab] OR Lescol[tiab] OR lovastatin[tiab] OR Mevacor[tiab] OR Altoprev[tiab] OR pitavastatin[tiab] OR Livalo[tiab] OR Livazo[tiab] OR Zypitamag[tiab] OR cerivastatin[tiab] OR Baycol[tiab] OR Lipobay[tiab]))) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR randomly[tiab] OR placebo[tiab] OR trial[tiab] OR groups[tiab] OR drug therapy[sh]) NOT (animals[mh] NOT humans[mh])`. Decided 2026-10-07 by the captain under Mahmood's delegation. Reason: against the CURRENT comparator (PMID 32529863) the registered queries identify 2 of 6 eligible comparator trials; this blind proposal (r2 (re-validated against the current comparator), recorded call mc-13762549ec47d042ce8c97345e2769cc.json; written without sight of any comparator trial) identifies 4 of 6 together with them, at 1300 records (cap 10,000). Run in full on 2026-10-07: 1300 records, 1296 not already held; rule screen of the new records: {'include': 8, 'exclude': 1221, 'dedup_collapsed': 64, 'no_decision': 0}. Eligible comparator trials identified: 2 -> 4 of 6 (1 of the 2 newly identified pass the rule screen). Recorded: outputs/search_audit/expanded/statins-primary-prevention-elderly.json. Not adopted, over the cap: r1 (mc-3d324a96f6a20f8241e1fd8fc6425fa6.json) 36095 records, recall 6 of 6; precise10k (mc-4905cf1d32b06df5622c3a9a22cdc355.json) 10119 records, recall 6 of 6. The standing REVIEW_REFERENCE_LIST route (A1) reads the topic's current comparator.

## Amendment 2026-10-07 -- open search sources: OpenAlex and WHO ICTRP (additive)

- **A7 Open sources added** (decided 2026-10-07 by Mahmood: open sources only, no CENTRAL or Embase). (a) OpenAlex query (title_and_abstract.search; precise blind proposal, recorded call mc-cd7055088a23688d1a66f169e604b22b.json, written without sight of any comparator trial): `(older OR elderly OR aged OR aging OR ageing OR geriatric OR septuagenarian OR octogenarian OR nonagenarian OR "70 years" OR "75 years" OR "80 years") AND ("primary prevention" OR "without cardiovascular disease" OR "without established cardiovascular disease" OR "no cardiovascular disease" OR "no history of cardiovascular disease" OR "free of cardiovascular disease" OR "without coronary heart disease" OR "without coronary artery disease" OR "without coronary disease" OR "no coronary heart disease" OR "without vascular disease" OR "without atherosclerotic cardiovascular disease" OR "apparently healthy") AND (statin OR statins OR "HMG-CoA reductase inhibitor" OR "HMG CoA reductase inhibitor" OR "hydroxymethylglutaryl coenzyme A reductase inhibitor" OR atorvastatin OR rosuvastatin OR pravastatin OR simvastatin OR lovastatin OR fluvastatin OR pitavastatin OR cerivastatin OR Lipitor OR Crestor OR Ezallor OR Pravachol OR Lipostat OR Zocor OR FloLipid OR Mevacor OR Altoprev OR Lescol OR Livalo OR Livazo OR Zypitamag OR Baycol OR Lipobay) AND (randomized OR randomised OR randomly OR randomization OR randomisation OR placebo OR trial)` -- 4638 records on 2026-10-07. Measured on the current comparator's eligible trials: OpenAlex alone 5 of 6, registered PubMed 4 of 6, together 5 of 6; gain: ASCOT-LLA older (Collier 2011). Not adopted, over the 10,000 cap: round 1 14843 records. (b) **WHO ICTRP** (trial registrations): registered; run by its open route, a person's Search Portal CSV/XML export (or WHO's full-dataset request form) ingested by scripts/g1_open_sources.py --ictrp-export. Automated querying is not used: trialsearch.who.int/robots.txt disallows all agents and WHO's web/crawling services are for agreed partners. Not yet run.
