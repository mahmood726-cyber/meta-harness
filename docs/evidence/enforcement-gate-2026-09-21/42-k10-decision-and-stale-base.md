# Mahmood's k=10 decision, and the stale candidate base caught by the signature's bound bytes

## 1. The decision

> **"ten trials please with old k on same page"** — Mahmood, 2026-09-25
>
> `decided_by: Mahmood`
> `decided_on: 2026-09-25`
> `how_it_reached_the_reviewer: "Dispatch chat relay"`
> `status: APPROVAL_OF_INTENT — NOT the hash-bound signature`

FLOW and ELIXA are **included in the primary pool**. They were adjudicated protocol-eligible with
source-bound 3-point MACE results, and omitting eligible trials would be outcome-driven selection.
The k=8 result stays **on the same page** as the previous published result, with its derived notice.

    primary candidate (k=10) : HR 0.8613 (95% CI 0.8069-0.9194), PI 0.7531-0.9852, tau^2 0.0027
    previous result (k=8)    : HR 0.856  (95% CI 0.8086-0.9061), PI 0.8069-0.9081, tau^2 4e-05

The derived notice must say what changed and why: FLOW and ELIXA added after adjudication;
direction and significance unchanged; **heterogeneity is no longer ~0** — tau^2 rises to 0.0027 and
the prediction interval widens. That last clause is the honest part of the change and must not be
dropped for brevity.

**This approval is not a signature.** Deploying k=10 still requires Mahmood's hash-bound signature
on bundle `170c692283a451d9f031ae39924aba23000116c59a867914ca96f076e0efce1e` (or its successor).
If it is not signed by deploy time, the k=8 candidate deploys with a clearly labelled **pending
result change** block: FLOW and ELIXA adjudicated eligible, inclusion awaiting sign-off, the k=10
result shown as *pending, not adopted*.

## 2. The candidate was being built on a stale base — caught by the bound bytes

The signature request binds specific files by sha256. Checking them against the candidate:

    docs/reviews/glp1-ra-mace-t2d/review.json
        bound by the signature : 3e374d6d...
        origin/main            : 3e374d6d...   MATCH
        d70bf183, c23a7e91     : 3e374d6d...   MATCH
        v1/candidate (d587d9aa): 79c3d009...   DIFFERS
    protocols/glp1-ra-mace-t2d.md                          MATCH
    outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md  MATCH

    v1/candidate vs origin/main : main has 57 commits the candidate lacks
                                  the candidate has 11 main lacks -- DIVERGED

Three consequences, stated rather than smoothed over:

1. **The "derived served-number diff vs HEAD" was not the deploy diff.** It compared the candidate
   against its own stale base. Its 10 count-chain moves are real relative to `d587d9aa`, but they
   are not the moves a deploy would cause, and were reported as though they were.
2. **A signature taken against that candidate would have bound bytes the release does not
   contain.** The bundle binds main's `review.json`; the candidate carried a different one.
3. The 57 missing commits include things being treated as still pending: `c23a7e91` (the tabs
   fix), `d70bf183` (the regenerated signature request), and the FLOW/ELIXA adjudication itself
   (`66852a57`, `5d34a666`).

**How it slipped through.** HEAD was checked for self-consistency — rebuilding
`noac-vs-warfarin-af-stroke` at HEAD reproduced its live page exactly — and that was treated as
sufficient. It answered "is HEAD consistent with its own code?" when the question was "is HEAD the
base we would deploy?". A check that returns exactly the value you expected is the most convincing
possible form of a check measuring the wrong thing.

**What made it catchable:** the signature pins content hashes rather than naming files. A request
that said "sign the current review.json" would have been silently satisfied by whichever version
happened to be on disk. This is the same lesson as anchoring a notice to the version it judged,
arriving from the other direction — and it is the argument for keeping hash-bound signatures even
when they are inconvenient.

## 3. Also corrected here

- **D3 trial identity (pva).** `NCT03030235` is **PRESERVED-HF** (PMID 34711976), whose registry
  condition is `Chronic Heart Failure With Preserved Systolic Function`. `NCT03619213` is
  **DELIVER** (PMID 36027570), condition `Heart Failure With Preserved Ejection Fraction`, which
  already matches the pre-specified vocabulary — DELIVER was never refused for population and never
  needed D3. Mahmood ruled on the *terms*, so the equivalence stands; only the trial names were
  wrong. Records 39 and 41, and `tests/test_population_clarification.py`, name DELIVER and are
  corrected. The config's `families_affected: ["NCT03030235"]` was always right.
  **N09 -> WITHDRAW is confirmed, and it is PRESERVED-HF.** nr must relabel `R-DELIVER` in
  `sign_session_plan.json`.
- **The manifest's missing `source` block is not a landed regression.** It is the build-provenance
  block (`identity`, `content_commit`, `generating_commit`) written by `scripts/build_bundle.py`,
  a stage *after* `build_topic.py`. The first regeneration ran only `build_topic.py` across all 32
  topics, so the block was stripped — an incomplete pipeline, not a dropped field. It also explains
  why only GLP-1 has a `BUNDLE.json`. Nothing for the signing list; the fix is to run the stage.

## 4. Corrected order of work

1. merge `origin/main` into the candidate (tabs, adjudication, current signature request)
2. re-apply the P5 + D3 + oc/POOL code patch
3. regenerate **including `scripts/build_bundle.py`**
4. recompute the served diff against **`origin/main`**, the deployable base
5. re-verify the signature's bound bytes after regeneration — if `review.json` moves, the request
   must be regenerated *before* Mahmood signs, not after
