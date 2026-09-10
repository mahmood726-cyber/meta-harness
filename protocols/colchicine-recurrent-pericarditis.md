# Protocol — colchicine for recurrent pericarditis

**Registration.** The commit that adds this file is the registration of this review.
It is committed BEFORE any search is run. Its SHA is embedded in the page's Protocol tab.

## PICO
- **P** — adults with recurrent pericarditis (>=1 recurrence after a first episode).
- **I** — colchicine added to conventional anti-inflammatory therapy (aspirin/NSAID +/- steroid).
- **C** — placebo added to conventional therapy.
- **O (primary)** — recurrent pericarditis during follow-up.
- **O (secondary / harms)** — match every outcome the resolved open-access comparator
  reports (see Outcome policy); carry adverse events / treatment discontinuation.

## Estimand / population / timepoint
- **Estimand** — risk ratio (RR) of recurrence, colchicine vs placebo.
- **Population** — intention-to-treat as randomised.
- **Timepoint** — longest recurrence follow-up each trial reports (>=12-18 months where available).
- Continuous outcomes (e.g., symptom persistence) reported on their own scale if the comparator uses them.

## Eligibility rules (each screened record gets exactly one rule id; the reason must be TRUE of the record)
Include:
- **I1** — randomised controlled trial.
- **I2** — population is recurrent pericarditis (not acute/first-episode-only, not post-pericardiotomy prophylaxis).
- **I3** — compares colchicine vs placebo/control on top of conventional therapy.
- **I4** — reports recurrence (or an outcome the comparator reports) with extractable arm data.
Exclude:
- **X1** — not an RCT (review, guideline, observational, editorial, protocol-only).
- **X2** — wrong population (acute/first-episode pericarditis only; post-op AF; other).
- **X3** — wrong intervention/comparison (no colchicine arm; no control arm).
- **X4** — duplicate / superseded report of an already-included trial.
- **X5** — off-topic (primary trial of another PICO topic in this set → negative control).

## Search strategy (fetch-once; raw results cached in-repo under cache/<slug>/ and committed)
- PubMed: `colchicine AND (pericarditis) AND (recurrent OR recurrence) AND (randomized OR randomised OR trial)`,
  plus a broadened `colchicine pericarditis randomized controlled trial` sweep.
- ClinicalTrials.gov: condition "recurrent pericarditis", intervention "colchicine".
- Screening reads ONLY the committed cache (offline, reproducible).

## Synthesis method (DECLARED; the served method must equal this — gate limb 1)
Pool `log(RR)` with **Paule-Mandel** random-effects `tau^2`; **HKSJ** CI on `t_{k-1}`
with variance floored at `max(1, Q/(k-1))`; prediction interval `mu ± t_{k-1}·sqrt(tau2+se^2)`.
0.5 continuity correction to all four cells of a study only if that study has a zero cell.
DerSimonian-Laird forbidden. (Engine validated vs metafor 5.0.1 to <1e-6.)

## Outcome policy (both limbs of "equal")
Report **every outcome the resolved comparator reports, not fewer**, on the same estimand/
population/timepoint, with arm-level counts where the sources give them; carry harms. Any
outcome the comparator reports but we cannot populate is **declared absent with a reason**,
never left blank.

## Comparator (pinned by resolution query; PMID/DOI + open-access confirmed at build)
Resolution query: *systematic review / meta-analysis of colchicine vs placebo for recurrent
pericarditis, open-access full text, most trials included; tie-break most recent.* The gate
refuses the page unless a real open-access comparator with PMID/DOI and a stated trial-set
overlap is present.

## Controls (both required)
- **Positive** — the offline screen must recover every trial the resolved comparator includes;
  any miss is reported on the page.
- **Negative** — a primary trial of another topic in this set (e.g. a colchicine **post-op AF**
  trial, or an SGLT2-HF trial) must be present in the fetched records and screen to EXCLUDE
  via X2/X5.

## Provenance / source hierarchy for extraction
Per field, prefer in order: **(1)** ClinicalTrials.gov results section → **(2)** the trial's
primary publication (PMC full text if OA, else abstract) → **(3)** the comparator's reported
extraction. Every extracted number records which source it came from.
