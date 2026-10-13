# k-gap phase 2, EMA (EPARs held under EMA reuse terms, with acknowledgement)

Run 13 Oct 2026 by `scripts/g1_regulator_fill.py run EMA ...` over the 13 gap topics that hold EMA documents. Balanced-crystalloids has no EMA product and was not run (4 trials still missing there after phase 1). Trials already admitted in phase 1 are skipped.

| topic | missing after earlier phases | named in held EMA text | typed | read (codex+agy) | admitted |
|---|---|---|---|---|---|
| colchicine-postop-af | 2 | 0 | 0 | 0 | 0 |
| colchicine-secondary-cv-prevention | 6 | 0 | 0 | 0 | 0 |
| corticosteroids-cap-mortality | 7 | 0 | 0 | 0 | 0 |
| corticosteroids-covid19-mortality | 4 | 0 | 0 | 0 | 0 |
| iv-iron-hfref-hosp | 2 | 0 | 0 | 0 | 0 |
| melatonin-primary-insomnia-sol | 2 | 0 | 0 | 0 | 0 |
| metformin-pcos-ovulation | 30 | 0 | 0 | 0 | 0 |
| omega3-cardiovascular-events | 12 | 2 | 0 | 2 | 0 |
| pcsk9-mace | 9 | 7 | 0 | 7 | 0 |
| probiotics-aad-prevention | 27 | 0 | 0 | 0 | 0 |
| statins-primary-prevention-elderly | 5 | 0 | 0 | 0 | 0 |
| ticagrelor-vs-clopidogrel-acs | 14 | 0 | 0 | 0 | 0 |
| tocilizumab-covid19-mortality | 16 | 0 | 0 | 0 | 0 |
| **total** | 136 | 9 | 0 | 9 | 0 |

Funnel: 136 missing, 9 named in a held EMA text, 0 typed (deterministic table), 9 read by codex and agy, 0 admitted.

Every read ended with both readers giving `SOURCE_ABSENT`. Their recorded reasons, in short:
- pcsk9 (ODYSSEY COMBO I, LONG TERM, FH I, FH II, HIGH FH, JAPAN; DESCARTES): the EPAR windows hold design, baseline, PK/bioequivalence and pooled adverse-event tables. None holds a per-trial MACE count or HR for the randomised population.
- omega3 (OMEGA / Rauch, ASCEND): the trials are cited qualitatively ("generally null results"), with no trial-level numbers.

EMA Policy 0070 clinical-data packages need an account, which the lane does not hold. That is flagged to Mahmood.
