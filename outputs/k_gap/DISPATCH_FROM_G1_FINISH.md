# Dispatch: g1/finish-line lane → captain

Branch `g1/finish-line`, rebased on acq/k-gap `825f154d1`. Code and recorded calls only: no tracker regeneration, no
served-number change. Every item below takes effect when you regenerate the tracker (union) and is yours to sign.

## Increment 1 (5 Oct): missing trials, per topic (n of N = matched of eligible, comparator N in brackets)

| topic | expected at your next union | what this branch adds | still open (why) |
|---|---|---|---|
| semaglutide-obesity-weight | **G1_MATCHED**, 2 of 2 eligible (N 4) | O'Neil 2018 named PROTOCOL_SCOPE_DIFFERENCE from its own abstract: once-daily 0.05–0.4 mg (protocol 2.4 mg weekly) and primary at week 52 (protocol Week 68 ± 8). `arm_object_difference`; an X-DOSE screen-out is named through it (main read SCREENED_OUT_UNAUDITED:X-DOSE) | – |
| empagliflozin-hfpef-hosp | **G1_MATCHED**, 1 of 1 (N 2) | nothing new needed: your k = 1 rule (f34580f9) compares EMPEROR-Preserved directly — meta 35338608 PRIMARY_VERIFIED HR 0.79 (0.69–0.90) vs comparator 0.79 (0.69–0.90): AGREE (checked on consolidate/g1-on-main's secondary registry). Its per-trial label now reads AGREE, not NOT_IN_OUR_POOL | – |
| iv-iron-hfref-hosp | 3 of 5 (N 5); RESULT_AGREES unmet (RESULT_DIFFERS) | **HEART-FID** (AGREE) and **AFFIRM-AHF** matched PRIMARY from posted AACT participant counts (registry/g1_acquired/iv-iron-hfref-hosp.json; gates below). AFFIRM-AHF DISAGREES, side named: the comparator's 217 vs 294 are the posted 'HF Hospitalisations' in **units Events** (NCT02937454 outcome 258897602), pooled over participant denominators; ours are the posted participants 142/558 vs 178/550 — a comparator row contradicted by the primary (your decision (2) territory) | FAIR-HF: no open source (NEJM; no posted results). EFFECT-HF: 11 vs 6 HF-hospitalised patients printed, arm sizes 86/86 only in other sentences — **decision for Mahmood: may counts and arm sizes stated in two verbatim sentences of the same report form one tuple?** |
| dpp4-mace-t2d | 4 of 5 (N 5); cannot be G1 (the comparator prints no pooled MACE) | **TECOS** matched PRIMARY: posted ITT 3-point MACE HR 0.99 (0.89, 1.1), two-sided 95% | EXAMINE: the posted HR has a one-sided 97.5% bound only; the abstract the same |
| corticosteroids-covid19-mortality | 4 of 5 (N 5), unchanged | none possible: CoDEX, CAPE COVID, REMAP-CAP, Metcovid have no posted results and **PMC serves only front matter ('the publisher does not allow downloading of the full text in XML form')** — now indexed PUBLISHER_DISALLOWS_XML (all 24 old FETCH_EMPTY entries were this), never scraped | REMAP-CAP: UNVERIFIED (two metas contradict; no primary). The 3 SECONDARY_SINGLE rows cannot be promoted from an open primary |
| colchicine-recurrent-pericarditis | 1 of 1 eligible after naming (N 5); cannot be G1 (CORP has no comparator row) | Finkelstein (12574898) and COPE (16186437) are named TRUE_SCOPE by our own screen + audit once your **members step fetches their two PubMed records** (title spans: postpericardiotomy prevention; conventional-therapy comparator, protocol placebo) | – |

Live ClinicalTrials.gov (API v2, cached + hashed by `ctgov_results_cached`) was checked too for the trials with no
source: CoDEX, CAPE COVID, REMAP-CAP, Metcovid, FAIR-HF, EFFECT-HF -- none has posted results.

## How the acquired rows are admitted (scripts/g1_trial_acquire.py → registry/g1_acquired/<slug>.json)

- One **recorded** codex call per trial (reproducible_ai.model_call_live; concurrency 3), the comparator's row never shown.
  Records leak-scanned: no file reads, no outside reads. The one full text sent (EFFECT-HF, PMC5642327) is CC BY 4.0.
- Admission is the 2 Oct one-primary-source decision (the rule of `single_primary_source`), by deterministic gates:
  text — quote verbatim in the whole text, every number in the quote, typed matcher beside the outcome terms;
  AACT — the tracker's binding gates (named / estimand / analysis set / composite), posted participant counts or a posted
  two-sided effect, one time frame. `g1_tracker.acquired_merge` reads ADMITTED rows only.
- Analysis population is recorded, not filtered: AFFIRM-AHF's counts are its full analysis set (randomised and dosed).

## Harness classes on the way (all with plants)

- registry binding: a posted two-sided effect on the protocol's estimand binds without arm counts; refused at ESTIMAND —
  per-protocol analysis set (protocol ITT), extended composite ('MACE Plus'), first-and-recurrent events, a composite that
  adds death to a single outcome; a one-sided bound is refused as such.
- 'HF' reads as heart failure in outcome names.
- per-trial agreement for a trial matched through a verified non-pool row is computed on that row.

## Still open on your side

- The privacy leak reported to Mahmood (INDEX.md head, rewrite-workbook text and his email in committed codex logs: 44
  files on main since aa8ed28a, 5 more records on acq/k-gap in 90478bed). This branch's `model_call_live` withholds
  outside reads; acq/k-gap's does not yet.
