# V1 release note — GLP-1 RA MACE reference release (draft, 2026-09-26)

## What this is, and what it is not

**A reproducible, source-bound synthesis of pre-identified GLP-1 receptor agonist cardiovascular
outcome trials, with an explicit audit trail. It is not a completed systematic review.**

A senior external reviewer, who reproduced the pooled result independently, put it as:

> "a correct calculation, not yet a validated review"

That framing is adopted rather than softened. The arithmetic, the provenance and the refusals are
the product; the systematic-review claim is not made.

### Specifically disclosed

- **Retrieval is known-item, not exhaustive.** The trials were pre-identified. The search
  machinery exists and is measured, but V1 does not claim a systematic search that would find a
  trial nobody named.
- **Risk of bias is partial and not outcome-specific.** RoB 2 is applied, but not per outcome.
- **Adjudication status is stated per trial**, including the trials whose inclusion was decided
  during this release (below).
- **Sensitivity scenarios are derived through this pipeline**, never hand-copied from another
  implementation.

## The primary result

**k = 10** — HR **0.8613** (95% CI 0.8069–0.9194), prediction interval 0.7531–0.9852, τ² 0.0027.

Shown on the same page, as the previous published result:

**k = 8** — HR **0.856** (95% CI 0.8086–0.9061), prediction interval 0.8069–0.9081, τ² 4e-05.

**What changed and why:** FLOW and ELIXA were adjudicated protocol-eligible with source-bound
3-point MACE results and added to the primary pool. Direction and significance are unchanged.
**Heterogeneity is no longer ≈0**: τ² rises from 4e-05 to 0.0027 and the prediction interval widens
from 0.8069–0.9081 to 0.7531–0.9852. That is the honest content of the change and is stated beside
the result, not buried.

Decision: **Mahmood, 2026-09-25 — "ten trials please with old k on same page"**,
`how_it_reached_the_reviewer: "Dispatch chat relay"`. Deployment of the k=10 result is bound to his
signature over bundle `170c692283a451d9f031ae39924aba23000116c59a867914ca96f076e0efce1e`.

**A prediction interval equal to its confidence interval carries no predictive information.** With
τ² = 0, `sqrt(τ² + se²)` collapses to `se`, so a t-based prediction interval *becomes* the
confidence interval. The k=9 "+FLOW only" scenario shows exactly this (PI = CI = 0.8095–0.9008). It
is a property of the declared convention, not an error, and it must never be read as precision.

## Independent reproduction — the k=8 baseline only

An external reviewer computed the pool with no meta-harness code imported (numpy/scipy only).
Against our pipeline, **at the precision we publish, 9 of 9 quantities agree; at full float
precision, 4 of 4 agree** within 5e-12. Largest relative deviation 2.4e-13 — floating-point noise
between two implementations, not a method difference. Both implementations independently applied the
`max(1, Q/(k-1))` HKSJ variance floor, which matters because Q = 7.0607 against df = 7, exactly the
case where HKSJ would otherwise narrow the interval below DerSimonian–Laird.

**This claim is made for the k=8 baseline only.** On the k=10 scenario the two sides differ in the
third and fourth decimals (HR 0.8613 vs 0.8615, PI high 0.9852 vs 0.9873) because the reviewer
pooled the *published rounded* FLOW and ELIXA effects while we bound FDA label and statistical-review
values. Same reading, different inputs. Their numbers are a cross-check and are **never** copied into
served content.

## Decisions taken during this release, with attribution

| id | decision | who | served number moves |
|---|---|---|---|
| k=10 | FLOW + ELIXA into the primary pool, k=8 retained on the page | Mahmood, Dispatch chat relay | **yes** |
| D3 | "preserved systolic function" = "preserved ejection fraction" | Mahmood, Dispatch chat relay | **yes** |
| Q1 | EMPA-KIDNEY DKA: serve registry `5/3,304 vs 1/3,305`, note the paper's `6 vs 1` | Dispatch under delegation | **yes** |
| Q2 | COVACTA SAE: keep day-28 `103/295 vs 55/143`, label the window, show day-60 beside | Dispatch under delegation | no |
| Q3 | COVID STEROID: rename to the named day-14 composite, keep `1/16 vs 0/14` visible, remove from the SAE pool | Dispatch under delegation | **yes** |

**D3 is a RETROSPECTIVE protocol clarification** — decided after the data were seen — and is recorded
as one: `status: RETROSPECTIVE_PROTOCOL_CLARIFICATION`, `pre_specified: false`. It is declared in a
separate `population_vocabulary_clarifications` block, deliberately **not** added to
`include.population_any`, where it would be structurally indistinguishable from the pre-registered
vocabulary. A family admitted through it carries
`population_basis: RETROSPECTIVE_VOCABULARY_CLARIFICATION` in its eligibility cell.

**Correction on D3's scope:** the affected trial is **PRESERVED-HF** (NCT03030235, PMID 34711976),
whose registry condition is "Chronic Heart Failure With Preserved Systolic Function". It is **not
DELIVER** (NCT03619213), whose condition already matched the pre-specified vocabulary and which
never needed the clarification. The question was relayed to the reviewer as "DELIVER"; his ruling was
about the *terms*, so the equivalence stands, but the trial labelling was wrong and is corrected
here. Across all 32 topics exactly one family carries that condition string.

## ELIXA — an estimand dispute, disclosed rather than resolved

ELIXA's 3-point MACE is called a **"prespecified secondary"** endpoint in one FDA review and a
**"sensitivity analysis"** in the FDA summary review; the **registry records neither**. The
inclusion stands — the protocol accepts the exact three components and the pooled value is
unaffected by which label is correct — and ELIXA carries a RoB **"some concerns"** flag.

Worth recording how the row was identified: by its **definition sentence and event counts**
(`400 vs 392`), never by its number. The 4-point MACE+ primary rounds to the *same* 1.02 (0.89–1.17)
with `406 vs 399`, so a number-based match would have selected the wrong row.

## Known limitations carried into V1

1. **Tag stripping deletes text after a literal `<`.** `<[^>]+>` treats `P<0.001` as a tag opening.
   Measured: **84 of 892** held text fields containing a `<` are damaged, across 26 topics, losing up
   to 474 characters including whole effect sentences. Tested against all **433** declared-absent
   entries with a not-found reason: **zero** have their effect+CI or arm counts inside the deleted
   text, with both detectors proven to fire first (660 and 390 abstracts). So it is a real defect with
   **no demonstrated wrong served number** on this corpus. V1.1.
2. **`gitblob.blob_shas` falls back to one process per file** when the target is not a git toplevel —
   938 spawns in one test. Correct but slow; `--stdin-paths` works outside a repository and would make
   it two. V1.1.
3. **An ordered-contrast guard compares a long prose sentence by exact equality**, so it cannot
   distinguish "the direction is wrong" from "someone reworded the sentence". It should compare a
   typed direction token. V1.1.
4. **FREEDOM-CVO's strand pair is still marked "proposed"** in the class-boundary document. If it is
   not approved, its delivery-route question reverts to UNRESOLVED. The primary pool is unaffected
   either way.

## Build provenance

Every served page carries a provenance block (`identity`, `content_commit`, `generating_commit`)
written by `scripts/build_bundle.py`. `content_commit: PENDING_COMMIT` means the served bytes are not
yet committed — informational, and **not** the identity of the bytes, which is content-addressed by
`served_blob_git_sha1`.

## Reproducing this release

    python scripts/build_topic.py <slug>          # rebuild one topic from committed cache
    python scripts/build_bundle.py glp1-ra-mace-t2d
    python scripts/verify_all.py                  # the full gate: 11 limbs, the same as CI

The gate refuses rather than warns, and a limb that cannot execute is **not** a pass.
