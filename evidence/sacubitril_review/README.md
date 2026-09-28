# Sacubitril-HFrEF review: presentation policy, strategy continuity

Rule hash `0d5f8f77`, 2026-09-28. **RETROSPECTIVE, decided by Dispatch under Mahmood's delegation.** Branch
`oc/v101-sacubitril` off candidate stack `c15ed111`. Nothing is landed; the served-text changes below await Mahmood's
hash-bound signature.

## (1) Presentation rule is not an evidence decision

At k=2, when the two point estimates straddle the null (PARADIGM-HF 0.80 vs PARALLEL-HF 1.09; ticagrelor: PLATO 0.84 vs
PHILO 1.47), the pooled row is **withheld under a conservative presentation policy**. `harness/k2.py` now records the
decision in three separate fields:

| field | value |
|---|---|
| `decision_type` | `PRESENTATION_POLICY` |
| `eligibility` | `ALL_ADMISSIBLE` (both trials; no trial is made inadmissible) |
| `model_validity` | `COMPUTED_VALID` (the PM + HKSJ computation, with Q, df=1, heterogeneity p and I^2) |

Both trials are shown as `named_results`. A pre-named single-trial "anchor" is never substituted for the pool to remove the
sign conflict: `anchor_substitution_refused` records the configured anchor when a topic has one.

**Served-text changes (for signature; numbers unchanged):**
- ticagrelor-vs-clopidogrel-acs (primary MACE): "Honest k=1 anchor: PLATO HR 0.84" is removed; the block now reads "Pooled
  result WITHHELD under a conservative presentation policy", lists both trials (19717846 HR 0.84 [0.77-0.92]; PHILO HR 1.47
  [0.88-2.44]) and states that the anchor substitution is refused.
- sacubitril-valsartan-hfref (primary): same wording; both trials named.

Rebuilt on `c15ed111` + this branch: ticagrelor, corticosteroids-cap-mortality and sacubitril show no numeric difference
against the candidate stack. Ticagrelor major bleeding (k 2 -> none) is an existing stack move (`moves_83495751.json`), not
this branch.

## (3) Strategy continuity

`harness/strategy_periods.py`: "longest follow-up" means the longest follow-up while the randomised strategies are
unchanged. A stated switch splits follow-up into periods, each with its own contrast and blinding; a result past the switch
is refused as `STRATEGY_CHANGED_DURING_FOLLOW_UP` (never the randomised contrast). A switch stated without its timing fails
closed as `CONTINUITY_NOT_ESTABLISHED`.

**Measured (held text only, pin 3876a62d):** 4 of 2,668 held abstracts state a switch.
- 2 with a stated switch point: 30800562 (open-label extension after a 16-week randomised period), 41879760 (6-month
  open-label extension after a 7-day randomised period).
- 2 with no timing: 40442449, 19853510.
- **0 of 127 served rows** are affected.

**Limits, stated plainly.**
- PIONEER-HF's switch text and its 12-week HR 0.69 are **not held**. The held registry record carries only the 8-week
  double-blind measures, so the detector cannot be exercised on PIONEER itself; its plant is synthetic PIONEER-like text.
- The recall probe found switch statements the first version missed (no week number; "crossed over to"; extension after a
  randomised period in days/months). Those phrasings are covered now. A switch phrased in some other way is still missed, and
  would read as `NOT_STATED`.
- A device change ("all participants switched from the PDS290 pen-injector to the DV3396", STEP 8) is not a change of
  strategy, and is not flagged.

## (2) Comparison-specific blinding

Codex slot 2 (`oc/cx-comparison-blinding`) is reviewed separately. Its record-fitted parser branches were removed before
commit (see that branch's evidence README).
