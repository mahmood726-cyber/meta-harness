# Protocol - marine omega-3 fatty acids for major cardiovascular events

**Registration.** The commit that adds this file is the registration of this review; its
SHA is embedded in the page's Protocol tab and its Reproducibility tab. Committed BEFORE
the synthesis is run.

## PICO
- **P** - adults at cardiovascular risk, including established cardiovascular disease,
  diabetes or dysglycemia, prior myocardial infarction, heart failure, coronary disease,
  dyslipidemia, hypertriglyceridemia, or other title-level cardiovascular-risk populations.
- **I** - marine omega-3 fatty acid supplementation, including EPA, DHA, EPA+DHA, fish oil,
  omega-3 carboxylic acids, or icosapent ethyl.
- **C** - placebo or inert control, including corn oil, olive oil, mineral oil, or usual-care
  control where the randomized comparison is otherwise eligible.
- **O (primary)** - major vascular events / MACE.
- **O (harms)** - atrial fibrillation; bleeding.

## Estimand / population / timepoint
- **Estimand** - risk ratio (RR), omega-3 vs placebo/control. Published ratio effects with
  95% CI are poolable when arm counts are not abstract-extractable.
- **Population** - intention-to-treat as randomized.
- **Timepoint** - trial end / longest randomized follow-up reported in the abstract.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **I1** - randomized controlled trial;
- **I2** - adult cardiovascular-risk population, judged from title or registry conditions;
- **I3** - marine omega-3 fatty acid supplement vs placebo/control;
- **design** - double-blind, placebo-controlled or blinded inert-control RCT.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational, protocol-only, subgroup-only report);
- **X2** - wrong population (for example depression, pregnancy, eye disease, dementia,
  inflammatory bowel disease, osteoarthritis, or atrial-fibrillation recurrence);
- **X3** - wrong intervention/comparison (no randomized marine omega-3-vs-control contrast);
- **X-DESIGN** - not double-blind and placebo/inert-control;
- **X5** - off-topic: a primary trial of another topic/disease in this set (negative control).

> **Eligibility is NOT on the outcome axis.** Whether a trial reports major vascular events
> / MACE, or gives a 2x2 vs only an effect+CI, is recorded as target-result status at
> extraction - never as an exclusion. A published effect + 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/<slug>/records.json; screening replays offline)
- PubMed: two deterministic title-word query blocks covering VITAL, ASCEND, REDUCE-IT,
  STRENGTH, Alpha Omega, ORIGIN, Risk and Prevention, GISSI-HF, and related omega-3
  cardiovascular trial records.
- ClinicalTrials.gov: condition "cardiovascular disease", intervention "omega-3 fatty acids".

## Synthesis method (DECLARED; served method must equal this - gate limb 1)
Random-effects inverse-variance on log(RR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells of a study
only if it has a zero cell. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1
(<1e-6).

## Comparator (resolved; open-access confirmed)
Li et al., *Medicine (Baltimore)* 2022, "Effects of omega-3 fatty acid on major
cardiovascular outcomes: A systematic review and meta-analysis" (PMID 35905212, PMCID
PMC9333496, DOI 10.1097/MD.0000000000029556; Unpaywall is_oa=true). It reports major
cardiovascular events RR 0.94 (95% CI 0.89-1.00) over 28 randomized controlled trials.
No comparator harm effect is declared because the fetched comparator abstract/PMC text
does not expose atrial-fibrillation or bleeding effects.

## Controls
- **Positive** - the search must recover and include landmark double-blind omega-3 trials:
  REDUCE-IT (PMID 30415628), STRENGTH (PMID 33190147), and ORIGIN omega-3 (PMID 22686415).
- **Negative** - Grenyer et al. fish oil for major depression (PMID 17659823; a different
  disease area) must be recovered and EXCLUDED as wrong population.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 35905212) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 31567003, 37031750; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 16 of 18 of the comparator's eligible trials; with this route and the full retrieval below, 18 of 18 (17 of 18 without the comparator's own reference list, which contains its trials by construction). The route retrieves 182 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "cardiovascular disease", "intr": "omega-3 fatty acids"} is unchanged. It returns 216 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query: not adopted** (KEEP_CURRENT: volume 21750 > cap 5000; recorded call mc-405714725befbbdb17db55863ce49c92.json).

## Amendment 2026-10-06 -- search volume cap raised to 10,000 (decision under Mahmood's delegation)

- **A5 Volume cap 10,000 (was 5,000) for this topic; concept query added** (union; none removed): `(("Cardiovascular Diseases"[Mesh] OR "Risk Factors"[Mesh] OR "Diabetes Mellitus"[Mesh] OR "Hypertension"[Mesh] OR "Dyslipidemias"[Mesh] OR "Obesity"[Mesh] OR "Smoking"[Mesh] OR "Metabolic Syndrome"[Mesh] OR "Renal Insufficiency, Chronic"[Mesh] OR cardiovascular[tiab] OR coronary[tiab] OR atherosclero*[tiab] OR arteriosclero*[tiab] OR "vascular disease*"[tiab] OR "vascular risk*"[tiab] OR "cardiac disease*"[tiab] OR "heart disease*"[tiab] OR "heart failure"[tiab] OR "myocardial infarct*"[tiab] OR "ischemic heart"[tiab] OR "ischaemic heart"[tiab] OR stroke*[tiab] OR cerebrovascular[tiab] OR "transient ischemic attack*"[tiab] OR "transient ischaemic attack*"[tiab] OR "peripheral arter*"[tiab] OR diabet*[tiab] OR prediabet*[tiab] OR dysglyc*[tiab] OR "impaired glucose"[tiab] OR "insulin resistance"[tiab] OR hypertens*[tiab] OR "high blood pressure"[tiab] OR dyslipid*[tiab] OR hyperlipid*[tiab] OR hypertriglycerid*[tiab] OR hypercholesterol*[tiab] OR "elevated triglyceride*"[tiab] OR "high triglyceride*"[tiab] OR "elevated cholesterol"[tiab] OR "high cholesterol"[tiab] OR "metabolic syndrome"[tiab] OR obes*[tiab] OR overweight[tiab] OR smok*[tiab] OR "chronic kidney disease"[tiab] OR "chronic renal insufficiency"[tiab] OR "risk factor*"[tiab] OR "high risk"[tiab] OR "increased risk"[tiab] OR "primary prevention"[tiab] OR "secondary prevention"[tiab]) AND ("Fatty Acids, Omega-3"[Majr] OR "Fish Oils"[Mesh] OR "Eicosapentaenoic Acid"[Mesh] OR "Docosahexaenoic Acids"[Mesh] OR "omega-3"[tiab] OR "omega 3"[tiab] OR omega3[tiab] OR "n-3"[tiab] OR "n 3"[tiab] OR n3[tiab] OR "fish oil*"[tiab] OR "marine oil*"[tiab] OR "marine fatty acid*"[tiab] OR "marine lipid*"[tiab] OR "marine polyunsaturated fatty acid*"[tiab] OR "krill oil*"[tiab] OR "algal oil*"[tiab] OR "algae oil*"[tiab] OR "microalgal oil*"[tiab] OR "cod liver oil*"[tiab] OR eicosapentaenoic[tiab] OR icosapentaenoic[tiab] OR eicosapentaenoate*[tiab] OR icosapentaenoate*[tiab] OR docosahexaenoic[tiab] OR docosahexaenoate*[tiab] OR EPA[tiab] OR DHA[tiab] OR icosapent[tiab] OR eicosapent[tiab] OR "ethyl EPA"[tiab] OR "ethyl eicosapentaenoate"[tiab] OR "ethyl icosapentate"[tiab] OR "omega-3-acid ethyl ester*"[tiab] OR "omega-3 carboxylic acid*"[tiab] OR "omega-3 free fatty acid*"[tiab] OR "omega-3 triglyceride*"[tiab] OR Vascepa[tiab] OR Vazkepa[tiab] OR Lovaza[tiab] OR Omacor[tiab] OR Omtryg[tiab] OR Epanova[tiab] OR MaxEPA[tiab] OR "Max EPA"[tiab] OR Eskim[tiab] OR Seacor[tiab] OR Zodin[tiab]) AND ("Randomized Controlled Trial"[Publication Type] OR ((randomized[tiab] OR randomised[tiab] OR randomly[tiab] OR "Random Allocation"[Mesh]) AND (trial[tiab] OR placebo*[tiab] OR control*[tiab] OR blind*[tiab] OR mask*[tiab])))) NOT (animals[Mesh] NOT humans[Mesh])`. Decided 2026-10-06 by the captain under Mahmood's delegation. Reason: the blind query audit (query_audit_precise.json, recorded call mc-e31a4f03e30901604155c63eebbe1d3c.json) measured a recall gain on the comparator's eligible trials -- registered queries 12 of 18, with this query 18 of 18 -- at 5251 records, above the old 5,000 cap. Run in full on 2026-10-06: 5251 records, 5213 not already held; rule screen of the new records: {'include': 308, 'exclude': 4693, 'dedup_collapsed': 180, 'no_decision': 0}. Eligible comparator trials identified: 9 -> 18 of 18 (4 of the 9 newly identified pass the screen). Recorded: outputs/search_audit/expanded/omega3-cardiovascular-events.json.
