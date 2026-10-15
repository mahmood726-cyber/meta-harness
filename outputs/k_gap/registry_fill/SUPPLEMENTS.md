# Why we did not match the per-trial data in metas' SUPPLEMENTARY tables, and what changed (15 Oct 2026)

## In plain words, for Mahmood

You were right: many per-trial rows live in the metas' supplementary files, and **our pipeline never opened a
supplement of any meta other than a topic's own comparator.**
- The phase-4 engine (`g1_two_source_sweep.py` / `secondary_meta_build.py`) read only the tables inside each meta's
  article XML, and only when a table could re-create the meta's printed pooled result (its quality check).
- A supplement is a separate file (Word, PDF, Excel) downloaded from Europe PMC. That download existed, but it was
  wired only to the comparator.

So a meta like the Medicine corticosteroid review (PMID 34011029), whose Word **Supplemental Table S2** lists
**mortality n/N per trial for CoDEX, MetCOVID, REMAP-CAP and CAPE COVID**, was logged as "no per-trial table for the
outcome". The table was there; we never looked.

## The measurement (before building anything)

Of the **372** metas logged "no typed per-trial table for the outcome":
- **272** list supplementary files in their own article record (73%);
- the pipeline had **fetched 1** and parsed essentially none.

Metas holding at least one file of each format:

| format | metas |
|---|---|
| docx | 136 |
| pdf | 95 |
| doc | 35 |
| zip | 25 |
| image | 15 |
| xlsx/csv | 13 |
| other:eps | 3 |
| other:pptx | 1 |

**Five concrete active-topic metas** (fetched with the existing Europe PMC route):

| meta | topic | what its supplement holds | per-trial rows for a MISSING trial? |
|---|---|---|---|
| 34011029 (Medicine) | corticosteroids-covid | Table S1 characteristics; **Table S2 outcomes: mortality n/N per trial**; xlsx quality ratings | **YES**: CoDEX, MetCOVID, REMAP-CAP, CAPE COVID |
| 37632415 (EHJ) | iv-iron | Tables 3-5: per-trial CV hospitalisations and deaths | per-trial rows, but for CONFIRM-HF, AFFIRM-AHF, HEART-FID and IRONMAN only; our missing FAIR-HF and EFFECT-HF are cited, not included |
| 40159279 (Nature Medicine) | iv-iron | characteristics; its result tables and forest plots ship as **images** | invisible without OCR |
| 36823953 (EJHF) | iv-iron | figures only (images) | invisible without OCR |
| 38965691 (ESC Heart Failure) | iv-iron | definitions, sensitivity analyses, risk of bias | no |

n of N for the five: has supplement **5 of 5** -> fetched **5 of 5** -> parsed **5 of 5** (images skipped) -> per-trial
rows for a missing trial **1 of 5** (4 trials) -> admitted under the old pipeline **0 of 5**.

**Why the pipeline missed them, three causes:**
1. It never fetched a non-comparator meta's supplement.
2. "Cites the trial" is not "includes the trial": metas are found by citation, so many supplements simply do not hold
   our trials.
3. Where they do, they are often pictures (scanned tables, forest plots), which we do not OCR.

## What was built (Codex implemented from written specs; reviewed and tested here)

`scripts/g1_supplement_rows.py`:
1. For every missing trial, the metas that cite it (the comparator is never a source, under every id).
2. Their supplements are fetched (Europe PMC ZIP) and parsed: Word, PDF, Excel and CSV; images listed, not read.
3. **A deterministic per-trial row reader:**
   - the trial is named by sourced names (its report's title acronym, its registry acronym, its first author);
   - the outcome column comes from the table header;
   - the arms come from an arm header ("Steroids | SOC/placebo");
   - counts are read as n/N; effects (HR/RR/OR with a 95% CI) are read only with a stated measure and orientation.
4. **Verification:** a row becomes PRIMARY_VERIFIED only when its exact numbers are found in the trial's OWN held text
   beside the protocol's outcome terms (`verify_typed`). If that text's copy carries no licence, it waits on the
   Captain's ruling. Otherwise the row is SECONDARY_PROVISIONAL, which is queued and never counted for G1.
5. A model reads a supplement only when it is CC BY / CC0 and the deterministic reader found nothing: two readers
   plus an adjudicator, each answer gated verbatim.

**Fixed while running it, each with a test:**
- trial names: title-labelled trials had only the name "Effect";
- header lookup: a 6-line window lost the header of every row below the fifth;
- licence reading: a licence sentence was compared with short codes;
- a topic without a refreshed sweep file stopped the run;
- arm identity: a generic word ("Steroids") let a corticosteroid meta's REMAP-CAP row pass as the TOCILIZUMAB arm. The intervention column must now name the topic's own drug (planted).

## Result over all gap topics

| topic | metas citing a missing trial | with supplement | fetched | parsed | per-trial rows (trials) | PRIMARY_VERIFIED | pending ruling | SECONDARY_PROVISIONAL |
|---|---|---|---|---|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 22 | 16 | 16 | 14 | 0 (0) | 0 | 0 | 0 |
| colchicine-postop-af | 9 | 4 | 3 | 3 | 0 (0) | 0 | 0 | 0 |
| colchicine-secondary-cv-prevention | 27 | 20 | 20 | 19 | 0 (0) | 0 | 0 | 0 |
| corticosteroids-cap-mortality | 22 | 15 | 15 | 15 | 0 (0) | 0 | 0 | 0 |
| corticosteroids-covid19-mortality | 24 | 18 | 18 | 18 | 3 (3) | 0 | 3 | 0 |
| iv-iron-hfref-hosp | 12 | 10 | 10 | 10 | 0 (0) | 0 | 0 | 0 |
| melatonin-primary-insomnia-sol | 1 | 1 | 1 | 0 | 0 (0) | 0 | 0 | 0 |
| metformin-pcos-ovulation | 45 | 31 | 31 | 29 | 0 (0) | 0 | 0 | 0 |
| omega3-cardiovascular-events | 65 | 49 | 49 | 44 | 0 (0) | 0 | 0 | 0 |
| pcsk9-mace | 35 | 29 | 29 | 27 | 0 (0) | 0 | 0 | 0 |
| probiotics-aad-prevention | 36 | 19 | 19 | 16 | 0 (0) | 0 | 0 | 0 |
| statins-primary-prevention-elderly | 30 | 26 | 26 | 21 | 0 (0) | 0 | 0 | 0 |
| ticagrelor-vs-clopidogrel-acs | 22 | 12 | 12 | 9 | 0 (0) | 0 | 0 | 0 |
| tocilizumab-covid19-mortality | 38 | 30 | 30 | 29 | 0 (0) | 0 | 0 | 0 |
| **total** | 388 | 280 | 279 | 254 | 3 (3) | 0 | 3 | 0 |

Rows found:
- **Effect of Dexamethasone on Days Alive and Ventilator-Free in** (corticosteroids-covid19-mortality): from meta 34011029 supplement `medi-100-e25719-s003.docx`, row 'CoDEX', COUNTS; class **PRIMARY_VERIFY_PENDING_RULING**
- **Effect of Hydrocortisone on Mortality and Organ Support in P** (corticosteroids-covid19-mortality): from meta 34011029 supplement `medi-100-e25719-s003.docx`, row 'REMAP-CAP', COUNTS; class **PRIMARY_VERIFY_PENDING_RULING**
- **Methylprednisolone as Adjunctive Therapy for Patients Hospit** (corticosteroids-covid19-mortality): from meta 34011029 supplement `medi-100-e25719-s003.docx`, row 'MetCOVID', COUNTS; class **PRIMARY_VERIFY_PENDING_RULING**

Why the other attempts produced no row (by count): {'NO_OUTCOME_HEADER': 907, 'NO_TRIAL_ROW': 769, 'FEWER_THAN_TWO_COUNT_CELLS': 151, 'AMBIGUOUS_OUTCOME_COLUMNS': 76, 'COUNTS_NOT_ADJACENT_AT_OUTCOME': 12, 'NO_ARM_HEADER': 1}

Model-read supplements: {'WAITING_READER_UNAVAILABLE': 111, 'MODEL_REFUSED_LICENCE': 97}. Reader B (agy) ran out of quota on both its Gemini and its Claude pools tonight;
those attempts wait.

## What it means for k

| class | trials | counts for G1? |
|---|---|---|
| PRIMARY_VERIFIED | 0 | yes |
| pending the unlicensed-copy ruling (dispatch decision 1) | 3 | not until ruled |
| SECONDARY_PROVISIONAL | 0 | no, verification queue |

The corticosteroids-covid rows (an ACTIVE topic) would become PRIMARY_VERIFIED candidates the moment the Captain allows
deterministic checking against the trials' own free-to-read (unlicensed) copies, because those copies print the same
counts.

**Remaining levers:**
- OCR or a vision read of image tables and forest plots (a model reading an image needs CC BY / CC0);
- including, not merely citing, metas (from each meta's own included-studies list);
- the ruling on unlicensed copies.
