# G1 MATCH — status (acq/k-gap, 2026-09-29)

**G1:** our k and data match a published open-access meta **trial for trial**, with **result agreement on the same
trials**, methodologically accurate. This file is generated from `k_gap_table.json` and
`registry/model_proposals/k_gap_result_agreement{,.rebuilt}.json`; the per-topic table below is copied from that
output.

## Where G1 stands

- **Trial-for-trial set.**
  - **Closest topics:** semaglutide-obesity-weight (2 of 3 shared; the third is STEP 4, a withdrawal design);
    glp1-ra-mace-t2d (7 of 8; ELIXA refused for a 4-point MACE estimand); noac-vs-warfarin (3 of 3 resolved, all
    pooled; ROCKET AF honestly unresolved).
  - No topic is yet an exact, fully resolved trial-for-trial match.
- **Result agreement on shared trials:** 46 shared trials over 20 topics.
  - **44** are not comparable from the comparator's text: its per-trial numbers are only in forest-plot figures.
  - **2** are comparable, both semaglutide-weight:
    - on the **served** page both **DISAGREE**. We pooled CT.gov observed arm means; the comparator pooled each
      trial's published primary estimated treatment difference;
    - with this branch's extractor fix both **AGREE**: STEP 3 MD -10.3 (-12.0, -8.6); STEP 1 -12.4 (-13.4, -11.5)
      vs the comparator's -12.44 (-13.37, -11.51).
- **Supplements** (where per-trial data often live), measured 2026-09-29 over 32 comparators:
  - **Europe PMC `supplementaryFiles`** (one ZIP per OA article) works, with intermittent 503s.
    - Outcome: 20 comparators with typed supplement text, 1 with only a legacy .doc (melatonin), 1 with only
      images (balanced-crystalloids), 13 with no supplements, and 1 refused (noac). For noac, EPMC returns an
      errorBean with HTTP 200 for the NIHMS supplement; it is refused as NOT_A_ZIP and nothing is cached.
  - NCBI `oa.fcgi` returns 404: the service is retired, and `harness.fetch._pmc_oa_supplement_text` silently
    returns '' because of it.
  - PMC `articles/instance/<id>/bin/<file>` serves a JavaScript interstitial; it is not circumvented.
  - **Result:** the supplements move G1 result agreement by **0 of 44**. Codex re-read the 13 shared-trial topics
    with supplement text, and every answer is still NOT_REPORTED
    (`registry/model_proposals/k_gap_result_agreement.supp.json`). A deterministic cross-check of the NOT_REPORTED
    answers, which the quote gate cannot verify on its own:
    - on the first 11 topics re-read, 13 of their 22 shared-trial labels never occur in the supplement text;
    - where a label does occur (esketamine, probiotics), it is only in reference lists, PRISMA counts, or
      characteristics tables giving N and arm split, never a per-trial effect or event count;
    - the probiotics supplement files are the draft manuscript and reviewer-comment PDFs.

## Methodological defects G1 found, fixed on this branch (all need re-certification before landing)

1. **Reported mean difference was never read** (`extract.extract_md_effect`). For an MD outcome the ladder fell
   through to arm means, which for STEP 1/3 were CT.gov observed means, a different quantity from the trial's
   primary estimand. Fixed with a unit check: '-12.7 kg' is refused for a percent outcome.
2. **The MD estimand guard refused reported MDs**, and **`synth.yi_vi` took log(effect) for any reported effect**:
   a negative MD crashed and a positive one would be mis-scaled. A reported MD now pools on the raw scale with
   SE = (hi-lo)/(2z), in pipeline, rob_sensitivity and delegated_served_impact. A non-positive "ratio" now refuses
   loudly.
3. Served values change for **one** topic only: semaglutide-obesity-weight, pooled MD -11.84 -> -11.47. 31/32
   topics are value-identical.

## Identity defects G1 found and fixed (measurement tooling, `kgap/`, `scripts/k_gap_table.py`)

- A comparator table numbered one off from its reference list (omega-3) is now distrusted as a whole.
- Typographic hyphens truncated acronyms: DAPA-HF resolved to an unrelated registration.
- **Guilt by association**: a paper is no longer "the result" of a trial registered after it was published.
  About 13 comparator trials had been marked POOLED this way (Deftereos, COVERT-MI, COLCHICINE-PCI ...).
- A second PubMed record of the same article is matched by exact title (EMPA-REG).

## Per topic (confirmed comparator sets)

Columns: drug-specific resolved comparator trials | unresolved labels | shared (pooled by both) | missing |
deliberate (scope+measure) | non-deliberate missing | result agreement, served | result agreement, this branch

| topic | theirs | unresolved | shared | missing | deliberate | open gap | agreement (served) | agreement (branch) |
|---|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 5 | 2 | 0 | 5 | 3 | 2 | {} | {} |
| colchicine-postop-af | 8 | 1 | 2 | 6 | 0 | 6 | {'NOT_REPORTED_BY_COMPARATOR': 2} | {'NOT_REPORTED_BY_COMPARATOR': 2} |
| colchicine-recurrent-pericarditis | 1 | 4 | 1 | 0 | 0 | 0 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| colchicine-secondary-cv-prevention | 15 | 0 | 2 | 13 | 0 | 13 | {'NOT_REPORTED_BY_COMPARATOR': 2} | {'NOT_REPORTED_BY_COMPARATOR': 2} |
| dapagliflozin-hfpef-hosp | 2 | 4 | 0 | 2 | 0 | 2 | {} | {} |
| esketamine-trd-madrs | 6 | 0 | 2 | 4 | 2 | 2 | {'NOT_REPORTED_BY_COMPARATOR': 2} | {'NOT_REPORTED_BY_COMPARATOR': 2} |
| finerenone-ckd-t2d-renal | 4 | 0 | 2 | 2 | 0 | 2 | {'NOT_REPORTED_BY_COMPARATOR': 2} | {'NOT_REPORTED_BY_COMPARATOR': 2} |
| glp1-ra-mace-t2d | 8 | 0 | 7 | 1 | 0 | 1 | {'NOT_REPORTED_BY_COMPARATOR': 7} | {'NOT_REPORTED_BY_COMPARATOR': 7} |
| iv-iron-hfref-hosp | 5 | 0 | 1 | 4 | 1 | 3 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| melatonin-primary-insomnia-sol | 19 | 0 | 1 | 18 | 0 | 18 | {} | {} |
| metformin-pcos-ovulation | 24 | 17 | 2 | 22 | 1 | 21 | {'NOT_REPORTED_BY_COMPARATOR': 2} | {'NOT_REPORTED_BY_COMPARATOR': 2} |
| noac-vs-warfarin-af-stroke | 3 | 1 | 3 | 0 | 0 | 0 | {'NOT_REPORTED_BY_COMPARATOR': 3} | {'NOT_REPORTED_BY_COMPARATOR': 3} |
| omega3-cardiovascular-events | 23 | 5 | 4 | 19 | 0 | 19 | {'NOT_REPORTED_BY_COMPARATOR': 4} | {'NOT_REPORTED_BY_COMPARATOR': 4} |
| pcsk9-mace | 12 | 0 | 2 | 10 | 3 | 7 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| probiotics-aad-prevention | 36 | 5 | 7 | 29 | 1 | 28 | {'NOT_REPORTED_BY_COMPARATOR': 7} | {'NOT_REPORTED_BY_COMPARATOR': 7} |
| sacubitril-valsartan-hfref | 9 | 0 | 1 | 8 | 1 | 7 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| semaglutide-obesity-mace | 10 | 0 | 2 | 8 | 0 | 8 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| semaglutide-obesity-weight | 3 | 0 | 2 | 1 | 0 | 1 | {'DISAGREE': 2} | {'AGREE': 2} |
| sglt2-hfref-hosp-cvdeath | 3 | 1 | 2 | 1 | 0 | 1 | {'NOT_REPORTED_BY_COMPARATOR': 2} | {'NOT_REPORTED_BY_COMPARATOR': 2} |
| sglt2-primary-prevention-hf | 8 | 0 | 3 | 5 | 0 | 5 | {'NOT_REPORTED_BY_COMPARATOR': 3} | {'NOT_REPORTED_BY_COMPARATOR': 3} |
| spironolactone-hfref-mortality | 3 | 5 | 1 | 2 | 1 | 1 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| statins-primary-prevention-elderly | 12 | 15 | 0 | 12 | 0 | 12 | {} | {} |
| ticagrelor-vs-clopidogrel-acs | 15 | 7 | 2 | 13 | 5 | 8 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |
| tranexamic-acid-pph | 5 | 0 | 1 | 4 | 0 | 4 | {'NOT_REPORTED_BY_COMPARATOR': 1} | {'NOT_REPORTED_BY_COMPARATOR': 1} |

## What would move G1 next (data-based)

1. **Land the MD fix** (captain, re-certification). That makes semaglutide-obesity-weight's shared trials agree
   (2/2); STEP 4 is then the only set difference.
2. **Resolve ROCKET AF** (noac): our own record never self-names it and AACT's acronym field is empty, so it needs
   a curated identity or an adjudicated alias, not a looser rule.
3. **Per-trial comparator numbers**: supplements are now exhausted (20 read, 0 of 44 moved). G1 result agreement
   for 44/46 shared trials needs numbers that exist only in forest-plot figures, which this lane will not OCR
   (a number never comes from a model). The remaining levers are captain decisions:
   - prefer comparators that print per-trial effects in text or tables;
   - or add a separately labelled check against each trial's OWN primary publication. That is not G1, because
     it does not test the comparator's extraction.
