# Denosumab vs placebo for new vertebral fractures in postmenopausal osteoporosis

## PICO
- **Population:** postmenopausal women with osteoporosis.
- **Intervention:** denosumab, including AMG 162 or Prolia terminology.
- **Comparator:** placebo.
- **Primary outcome:** new vertebral fracture.

## Eligibility - P/I/C/design only
Include randomized controlled trials when all of the following are true:
- The population is postmenopausal women with osteoporosis, judged from the title or registry conditions.
- The randomized intervention is denosumab.
- The randomized comparator is placebo.
- The trial is double-blind or placebo-controlled.

Exclude records for wrong population, wrong intervention, wrong comparator, non-randomized design, reviews, extensions without randomized placebo comparison, protocol-only reports, men-only trials, mixed women-and-men osteoporosis trials, cancer-related bone loss, chronic kidney disease or renal insufficiency, pediatric populations, and trials focused on another osteoporosis drug.

Eligibility is not based on whether the abstract reports the target outcome. If an otherwise eligible trial does not report new vertebral fracture with an arm-level count or effect estimate plus 95% CI in the abstract or eligible structured registry results, it is declared absent rather than substituted with another endpoint.

## Outcomes
Primary outcome:
- New vertebral fracture, including phrasings such as new radiographic vertebral fracture, new or worsening vertebral fracture, incidence of new vertebral fracture, primary outcome, primary endpoint, and primary end point.

Secondary outcomes:
- Nonvertebral fracture.
- Hip fracture.

Harm outcomes:
- Serious adverse events.
- Serious infection.

## Analysis Method
The estimand is the risk ratio for denosumab versus placebo. The declared synthesis method is random-effects inverse-variance pooling on log risk ratios using Paule-Mandel tau^2 and HKSJ 95% confidence intervals on t(k-1), with the variance floor `max(1, Q/(k-1))`. Prediction intervals use `mu +/- t(k-1)*sqrt(tau^2+se^2)`. If only one eligible trial reports the outcome, the result is presented as that trial's own effect and no random-effects pooling, tau^2, HKSJ interval, or prediction interval is applicable.

## Comparator
The comparator is Wei et al., "Efficacy and safety of pharmacologic therapies for prevention of osteoporotic vertebral fractures in postmenopausal women," *Heliyon* 2023, PMID 36852077, DOI 10.1016/j.heliyon.2022.e11880, PMCID PMC9958453. It is open access and reports a network meta-analysis of randomized trials in postmenopausal women with osteoporosis; the abstract reports denosumab versus placebo for vertebral fractures as RR 0.33 with 95% CI 0.14 to 0.61.

## Controls
- Positive control: FREEDOM, PMID 19671655.
- Negative control: denosumab in men receiving androgen-deprivation therapy for prostate cancer, PMID 19671656.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 36852077) backward reference list (PubMed elink and Europe PMC) and its forward citations; no other open meta-analysis is held for this topic yet. Rationale: the registered search identified 0 of 0 of the comparator's eligible trials; with this route and the full retrieval below, 0 of 0 (0 of 0 without the comparator's own reference list, which contains its trials by construction). The route retrieves 41 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A3 Concept query: not adopted** (KEEP_CURRENT: no recall gain; recorded call mc-6ae38d94941fcc367b0a7e7746add468.json).

## Amendment 2026-10-07 -- search re-validated against the current comparator (active topics)

- **A6 Concept query added** (union; none removed): `(("Osteoporosis, Postmenopausal"[Mesh] OR ((osteoporos*[tiab] OR "bone loss"[tiab] OR "low bone mass"[tiab] OR "low bone mineral density"[tiab] OR "low BMD"[tiab]) AND (postmenopaus*[tiab] OR post-menopaus*[tiab] OR "post menopaus*"[tiab] OR menopaus*[tiab] OR climacteric*[tiab] OR "after menopause"[tiab])) OR ("Osteoporosis"[Mesh] AND ("Postmenopause"[Mesh] OR "Menopause"[Mesh] OR "Female"[Mesh]))) AND ("Denosumab"[Mesh] OR "Denosumab"[Supplementary Concept] OR denosumab[tiab] OR prolia[tiab] OR xgeva[tiab] OR "AMG 162"[tiab] OR AMG162[tiab] OR "anti RANKL"[tiab] OR "anti-RANKL"[tiab] OR "RANK ligand inhibitor*"[tiab] OR "RANKL inhibitor*"[tiab] OR "receptor activator of nuclear factor kappa B ligand inhibitor*"[tiab] OR "receptor activator of nuclear factor-kappa B ligand inhibitor*"[tiab])) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])`. Decided 2026-10-07 by the captain under Mahmood's delegation. Reason: against the CURRENT comparator (PMID 32492050) the registered queries identify 1 of 2 eligible comparator trials; this blind proposal (r2 (re-validated against the current comparator), recorded call mc-9d933dc98c4164d6570ccd8381889924.json; written without sight of any comparator trial) identifies 2 of 2 together with them, at 1360 records (cap 10,000). Run in full on 2026-10-07: 1360 records, 1340 not already held; rule screen of the new records: {'include': 22, 'exclude': 1287, 'dedup_collapsed': 30, 'no_decision': 0}. Eligible comparator trials identified: 1 -> 2 of 2 (0 of the 1 newly identified pass the rule screen). Recorded: outputs/search_audit/expanded/denosumab-vertebral-fracture.json. The standing REVIEW_REFERENCE_LIST route (A1) reads the topic's current comparator.
