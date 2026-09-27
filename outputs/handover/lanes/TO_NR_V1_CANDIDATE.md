# To lane NR: the V1.0 candidate, and what the signing list must contain

**Candidate SHA: `<filled in at push>`** on branch `v1/candidate`. Base: frozen `origin/main`
(`b284e085`). Gate: full `scripts/verify_all.py`, all 11 limbs, green — no limb weakened, skipped or
bypassed.

## What is in the candidate

    frozen main (69 commits)
    + oc/ordered-contrast (23642e0d) -- 9 files, taken as oc's exact bytes, not hand-merged
    + P5   nr's population fix: folds both sides, honours a trailing '*' as the protocol's
           truncation, reads MeSH inverted 'X, Y' as 'Y X'
    + D3   Mahmood's retrospective population-vocabulary clarification
    + 28 evidence records, the release note, the V1.0.1 rerun runbook

## What is NOT in it, and must be named on the page as a limitation

    POOL / five-verdicts / selected-set   oc's verify_bundle and POOL touch DISJOINT features of the
                                         same file (oc: pool_measure_guard; POOL: verdicts,
                                         check_pool_contract, POOL_CONTRAST_MISMATCH). Direct apply
                                         fails at verify_bundle.py:1728; a 3-way apply lands conflict
                                         markers. The admission file is not a place to hand-guess, so
                                         POOL is deferred with its tests, parked at
                                         C:/mh-artefacts/parked-tests-2026-09-26.
    k=10 (FLOW + ELIXA)                  adjudicated eligible, approved in intent by Mahmood, NOT
                                         served. No branch changes anything the build reads, so
                                         nothing admits them. Lands as V1.0.1 on signature.
    evid2 Q1/Q3 notices                  if cf46a790's CI was not green in time.

## The primary result the candidate serves

    k=8   HR 0.856 (95% CI 0.8086-0.9061), PI 0.8069-0.9081, tau^2 4e-05

with FLOW + ELIXA disclosed as a **pending, not adopted** result change (k=10, HR 0.8613,
CI 0.8069-0.9194, PI 0.7531-0.9852, tau^2 0.0027).

## The signing list — order and content

**First: the k=10 result change**, per Mahmood ("ten trials please with old k on same page",
Dispatch chat relay, approval of intent). It is the only item that changes a pooled estimate.

**Then the 10 count-chain changes** below. Derived diff of every served number and verdict against
frozen `origin/main`: **32 topics compared, 22 unchanged, 10 moved, and every delta is in the page
count chain — 0 pooled results moved, 0 pooled membership moved.**

| topic | eligible | unresolved |
|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 0 → 2 of 23 | 22 → 20 |
| **dapagliflozin-hfpef-hosp** | 3 → 4 of 22 | 12 → 11 |
| doac-vte-recurrence | 1 → 3 of 78 | 64 → 62 |
| dpp4-mace-t2d | 5 → 7 of 37 | 31 → 29 |
| noac-vs-warfarin-af-stroke | 0 → 12 of 33 | 26 → 14 |
| probiotics-aad-prevention | 0 → 10 of 61 | 59 → 48 |
| sacubitril-valsartan-hfref | 1 → 7 of 41 | 37 → 31 |
| sglt2-primary-prevention-hf | 6 → 7 of 95 | 80 → 79 |
| ticagrelor-vs-clopidogrel-acs | 0 → 2 of 10 | 10 → 8 |
| tranexamic-acid-pph | — | 31 → 30 of 39 |

Several also drop entries from `Contributing without established structural eligibility`.

**Attribution is only partly established, and must not be guessed on a list Mahmood signs.**
`dapagliflozin-hfpef-hosp` is D3 — measured, not assumed: NCT03030235 is the only family in any of
the 32 topics whose registry conditions mention "systolic function". The other nine come from P5
and/or oc and are **not separated per topic**.

## Notice status, from the 41 re-judged notices

    SIGN AS IS  34
    WITHDRAW     5   N09 N17 N18 N19 N29
    REISSUE      2   N30 N35   (still refused, but on a different stated ground, so the notice's
                               reason as drafted is now wrong)

Derived through the real `screen_family()`, with the pre-fix pass anchored: it reproduces the
eligibility cell stored in the held evidence **1220 of 1220**, so the "before" provably is the served
state.

## Two things NR must fix before Mahmood signs

1. **Relabel `R-DELIVER` → `R-PRESERVED-HF`** in `sign_session_plan.json`. `NCT03030235` is
   **PRESERVED-HF** (PMID 34711976), condition "Chronic Heart Failure With Preserved Systolic
   Function". **DELIVER** is `NCT03619213` (PMID 36027570), whose condition already matched the
   pre-specified vocabulary — it was never refused for population and never needed D3. Mahmood ruled
   on the terms, so the equivalence stands; the trial label was wrong. **N09 → WITHDRAW is confirmed
   and it is PRESERVED-HF.**
2. **Regenerate the FLOW/ELIXA signature request against THIS candidate SHA.** The current bundle
   `4bf8ec33…` binds `docs/reviews/glp1-ra-mace-t2d/review.json` as it exists on main; the candidate
   regenerated those bytes, so that hash binds content we do not serve. The hash has already moved
   three times (`3809ce76` → `170c6922` → `4bf8ec33`) because each main landing changed the
   reproduction block. **Do not let Mahmood sign a hash whose bound bytes are not the bytes we
   deploy** — that is the failure this binding exists to prevent, and it was caught once already
   today.
