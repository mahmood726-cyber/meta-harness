# Protocol - systemic corticosteroids for 28-day mortality in hospitalised COVID-19

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs.

## PICO
- **P** - adults hospitalised with COVID-19.
- **I** - systemic corticosteroids, including dexamethasone, hydrocortisone,
  methylprednisolone, prednisone, or prednisolone.
- **C** - usual care, standard care, standard treatment, no hydrocortisone, or placebo.
- **O (primary)** - 28-day all-cause mortality.
- **O (harms)** - serious adverse events.

## Estimand / population / timepoint
- **Estimand** - odds ratio (OR), systemic corticosteroid vs usual care/placebo.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - 28 days.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - hospitalised, severe, ICU, hypoxic, or pneumonia/ARDS COVID-19 population by
  title or registry conditions;
- **I3** - systemic corticosteroid vs usual care, standard care, no hydrocortisone, or
  placebo;
- **design** - randomised comparison; double-blinding is not required because the
  target comparator includes open-label usual-care trials as well as placebo trials.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, meta-analysis, guideline, observational study, or
  protocol-only);
- **X2** - wrong population (for example post-COVID sequelae, non-COVID community-
  acquired pneumonia, influenza, paediatric MIS-C, pericarditis, or atrial fibrillation);
- **X3** - wrong intervention/comparison (no systemic corticosteroid-vs-control
  contrast, or a steroid-dose/active-steroid comparison without usual-care/placebo
  control);
- **X5** - off-topic: a primary trial of another topic/disease in this set
  (negative control).

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> 28-day all-cause mortality in an abstract-extractable form is recorded as
> target-result status at extraction, never as an exclusion. A published effect
> plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/corticosteroids-covid19-mortality/records.json; screening replays offline)
- PubMed: targeted trial-report queries for dexamethasone, hydrocortisone, and
  methylprednisolone COVID-19 randomised trials.
- ClinicalTrials.gov: condition "COVID-19", intervention "dexamethasone".
- Comparator-reference seeding is enabled so the WHO REACT trial references are
  replayed through the same P/I/C/design screen.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on the configured log ratio scale; for the primary
outcome this is log(OR). Paule-Mandel tau^2; HKSJ 95% CI on `t_{k-1}` with variance
floor `max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`.
0.5 continuity correction to all four cells of a study only if it has a zero cell.
DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6).

## Comparator (resolved; open-access confirmed)
WHO REACT Working Group, *JAMA* 2020, "Association Between Administration of
Systemic Corticosteroids and Mortality Among Critically Ill Patients With COVID-19:
A Meta-analysis" (PMID 32876694, DOI 10.1001/jama.2020.17023; Unpaywall
is_oa=true; PubMed Central PMCID PMC7489434). Its abstract reports 7 randomised
clinical trials and 28-day all-cause mortality summary OR 0.66 (95% CI 0.53-0.82)
by fixed-effect meta-analysis, with a random-effects OR 0.70 (95% CI 0.48-1.01).

## Controls
- **Positive** - the search must recover and include RECOVERY dexamethasone
  (PMID 32678530), REMAP-CAP hydrocortisone (PMID 32876697), and METCOVID
  methylprednisolone (PMID 32785710).
- **Negative** - Torres/JAMA methylprednisolone for severe community-acquired
  pneumonia (PMID 25688779) must be recovered and excluded as the wrong population.

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 32876694) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 2 other open meta-analyses (PMID 35343397, 33612824; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 5 of 5 of the comparator's eligible trials; with this route and the full retrieval below, 5 of 5 (5 of 5 without the comparator's own reference list, which contains its trials by construction). The route retrieves 1757 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "COVID-19", "intr": "dexamethasone"} is unchanged. It returns 110 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query: not adopted** (KEEP_CURRENT: no recall gain; recorded call mc-fbfe463a4102ba28e27d3cfb29fd561a.json).

## Amendment 2026-10-07 -- open search sources: OpenAlex and WHO ICTRP (additive)

- **A7 Open sources added** (decided 2026-10-07 by Mahmood: open sources only, no CENTRAL or Embase). (a) OpenAlex query (title_and_abstract.search; round 1 blind proposal, recorded call mc-54b6a4faf4965d6a0b19415d8293a16d.json, written without sight of any comparator trial): `("COVID-19" OR COVID19 OR "COVID 19" OR "SARS-CoV-2" OR "SARS CoV 2" OR "2019-nCoV" OR "coronavirus disease 2019" OR "2019 novel coronavirus") AND (corticosteroid OR glucocorticoid OR steroid OR dexamethasone OR hydrocortisone OR methylprednisolone OR "methyl prednisolone" OR prednisolone OR prednisone OR betamethasone OR triamcinolone OR cortisone OR deflazacort OR Decadron OR Dexasone OR Fortecortin OR Oradexon OR Cortef OR "Solu-Cortef" OR Medrol OR "Solu-Medrol" OR "Depo-Medrol" OR Medrone OR "Solu-Medrone" OR Urbason OR Metypred OR Deltacortril OR Deltasone OR Rayos OR Lodotra OR Celestone OR Diprospan OR Kenalog OR Calcort OR Emflaza) AND (randomized OR randomised OR randomly OR randomization OR randomisation OR placebo OR trial)` -- 4932 records on 2026-10-07. Measured on the current comparator's eligible trials: OpenAlex alone 5 of 5, registered PubMed 5 of 5, together 5 of 5; no gain. (b) **WHO ICTRP** (trial registrations): registered; run by its open route, a person's Search Portal CSV/XML export (or WHO's full-dataset request form) ingested by scripts/g1_open_sources.py --ictrp-export. Automated querying is not used: trialsearch.who.int/robots.txt disallows all agents and WHO's web/crawling services are for agreed partners. Not yet run.
