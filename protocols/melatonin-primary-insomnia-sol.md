# Melatonin vs placebo for sleep-onset latency in primary insomnia

## PICO
- **Population:** adults with primary insomnia.
- **Intervention:** melatonin (including prolonged-release / controlled-release melatonin, or Circadin).
- **Comparator:** placebo.
- **Primary outcome:** sleep-onset latency (mean difference in minutes).

## Eligibility - P/I/C/design only
Include randomized controlled trials when all of the following are true:
- The population is adults with primary insomnia, judged from the title or registry conditions.
- The randomized intervention is melatonin (any release formulation).
- The randomized comparator is placebo.
- The trial is double-blind or placebo-controlled.

Exclude records for wrong population (children, adolescents, autism or neurodevelopmental disorders, shift work, jet lag, delayed sleep-phase disorder, dementia or Alzheimer's disease, intensive-care patients, benzodiazepine withdrawal), wrong intervention, wrong comparator, non-randomized design, reviews, protocol-only reports, and secondary/circadian populations outside primary insomnia.

Eligibility is not based on whether the abstract reports the target outcome. If an otherwise eligible trial does not report sleep-onset latency as a per-arm mean and standard deviation (in the abstract or in eligible structured registry results), it is declared absent rather than substituted with another endpoint or an imputed variance.

## Outcomes
Primary outcome:
- Sleep-onset latency, including phrasings such as sleep onset latency, sleep-onset latency, sleep latency, latency to sleep onset, polysomnographic sleep latency, and subjective sleep latency.

The estimand is the mean difference (minutes) in sleep-onset latency, melatonin versus placebo. Pooling is random-effects inverse-variance on the mean difference; a single included trial is presented as that trial's own effect, not a random-effects pool.

Where a trial's structured results report the outcome for a **pre-specified subgroup** (e.g. Wade et al. report sleep-onset latency for the pre-defined age 65-80 population, a co-primary analysis, N=137 melatonin / 144 placebo), the subgroup is disclosed on the page as the analysis population rather than presented as the whole trial. The pooled value is the **unadjusted** per-arm mean difference computed from the reported per-arm change-from-baseline means and SDs; the trial's own covariate-adjusted estimate (Wade: -15.6 minutes, 95% CI -25.3 to -6.0, baseline- and age-adjusted linear regression) is noted where it differs. The per-arm means and SDs are verified against both the ClinicalTrials.gov structured posted results and the published Table 3.

## Sources and verification
- Per-arm mean and standard deviation are taken verbatim from the trial's primary report or its structured ClinicalTrials.gov posted results (the AACT-equivalent), never imputed from a figure or a Kaplan-Meier curve.
- Every pooled number is verified against the committed source span before it is pooled; where per-arm variance is not reported in accessible text or structured results, the trial is declared absent with the reason named, rather than pooling an imputed SD.

## Comparator
- Published open-access meta-analysis of melatonin for primary insomnia (sleep-onset latency), for trial-set overlap and reporting comparison only. An identical estimate on an identical trial set is arithmetic, not corroboration; the overlap is stated on the page.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 23691095) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 36079069, 35185525; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 5 of 12 of the comparator's eligible trials; with this route and the full retrieval below, 12 of 12 (7 of 12 without the comparator's own reference list, which contains its trials by construction). The route retrieves 424 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A3 Concept query added** (union with the registered queries; none removed): `("Sleep Initiation and Maintenance Disorders"[Mesh] OR insomnia*[tiab] OR sleepless*[tiab] OR "difficulty falling asleep"[tiab] OR "difficulty initiating sleep"[tiab] OR "difficulty getting to sleep"[tiab] OR "sleep initiation disorder*"[tiab] OR "sleep onset disorder*"[tiab]) AND ("Melatonin"[Mesh] OR melatonin*[tiab] OR melatonergic[tiab] OR "melatonin receptor agonist*"[tiab] OR Circadin[tiab] OR Slenyto[tiab] OR Melaxen[tiab] OR Melatonex[tiab] OR "N-acetyl-5-methoxytryptamine"[tiab] OR "N acetyl 5 methoxytryptamine"[tiab]) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])`. Proposed blind (the proposer saw the PICO and the current queries with their volumes, never the comparator's trials or our misses; recorded call mc-e6d29df8cddc551c370734745aaacffa.json); returns 926 records today; on the comparator's eligible trials the registered queries match 5 of 12 and the union 11 of 12. Limitation: the proposer may know well-known trials from training.

## Amendment 2026-10-07 -- open search sources: OpenAlex and WHO ICTRP (additive)

- **A7 Open sources added** (decided 2026-10-07 by Mahmood: open sources only, no CENTRAL or Embase). (a) OpenAlex query (title_and_abstract.search; round 1 blind proposal, recorded call mc-fa5453b01330919da870dfd8963223e7.json, written without sight of any comparator trial): `(insomnia OR sleeplessness OR "difficulty sleeping" OR "difficulty falling asleep") AND (melatonin OR "N-acetyl-5-methoxytryptamine" OR Circadin OR Slenyto OR Melaxen) AND (randomized OR randomised OR randomly OR randomization OR randomisation OR placebo OR trial)` -- 872 records on 2026-10-07. Measured on the current comparator's eligible trials: OpenAlex alone 2 of 2, registered PubMed 2 of 2, together 2 of 2; no gain. (b) **WHO ICTRP** (trial registrations): registered; run by its open route, a person's Search Portal CSV/XML export (or WHO's full-dataset request form) ingested by scripts/g1_open_sources.py --ictrp-export. Automated querying is not used: trialsearch.who.int/robots.txt disallows all agents and WHO's web/crawling services are for agreed partners. Not yet run.
