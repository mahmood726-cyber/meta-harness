# POOL closes the attacks and breaks every control — it must not land as written

Measured 2026-09-24 by lane F6B in `/f/mh-f6`, on base `a4e556e3` with `POOL_F2_F3.patch` applied
unmodified, through the same complete producer -> renderer -> publication gate route as the pre-fix run.
19 of 19 pre-fix ledger cases re-executed. Pre-fix files preserved. Nothing landed.

## The verdict

**Acceptance FAIL. 0 of 4 required controls retain publication acceptance.**
4 of 5 claimed pool attacks return the exact requested first refusal.

| | pre-fix | post-fix | first blocker |
|---|---|---|---|
| `baseline` | PASS | **REFUSED** | `POOL_PUBLICATION_INELIGIBLE` |
| `reorder_records` | PASS | **REFUSED** | `POOL_PUBLICATION_INELIGIBLE` |
| `reorder_pool_records` | PASS | **REFUSED** | `POOL_PUBLICATION_INELIGIBLE` |
| `freedom_decimal_normalisation` | PASS | **REFUSED** | `POOL_PUBLICATION_INELIGIBLE` |
| `unknown_id` | published | REFUSED | `POOL_INPUT_MEMBERSHIP_MISMATCH` — exact |
| `duplicate_id` | published | REFUSED | `POOL_INPUT_DUPLICATE` — exact |
| `omitted_id` | published | REFUSED | `POOL_INPUT_MEMBERSHIP_MISMATCH` — exact |
| `altered_inputs_updated_aggregate` | published | REFUSED | `POOL_INPUT_TUPLE_MISMATCH` — exact |
| `rotated_ids` | published | REFUSED | `POOL_INPUT_TUPLE_MISMATCH` — expected `POOL_ROW_IDENTITY_MISMATCH`, so **not credited** |

## The mechanism, from the real captured output

    stage  : bundle
    code   : POOL_PUBLICATION_INELIGIBLE
    message: REFUSED -- bundle not written
             POOL_PUBLICATION_INELIGIBLE certified primary contains inadmissible rows: ['PMID 30291013']

PMID **30291013 is HARMONY**, and it has been INADMISSIBLE all along: the pre-fix F6 run recorded
`scientific_admission: FAIL` on **every reached case including the baseline**, for exactly this row. That
state was inert before, because publication did not depend on it.

My patch makes it fatal. In `scripts/build_bundle.py`:

    inadmissible = [r["trial"]["id"] for r in vrows if r["admission"]["final"] != "ADMISSIBLE"]
    if inadmissible:
        problems.append(f"POOL_PUBLICATION_INELIGIBLE certified primary contains inadmissible rows: {inadmissible}")

The bundle is then not written at all, which cascades: the gate additionally reports
`ARTEFACT_DIGEST_MISMATCH`, `SUPPORTING_FILE_DIGEST_MISMATCH`, `CERTIFICATE_MISMATCH` and
`EXECUTION_RECORD_MISMATCH` — all downstream of the missing bundle, not independent failures.

## This is the same §F.5 violation I ruled on for BND1, committed again in a second patch

`21-decision-estimand-repair-under-F5.md` ruled that BND1's `ESTIMAND_UNOBSERVED` must not stand, because
abstaining on 42 of 46 served occurrences turned an evidence-state uncertainty into a corpus-emptying
scientific exclusion. I then wrote a different patch that converts a pre-existing
`scientific_admission` state into a hard refusal to write the bundle. Owning the rule is not the rule
firing.

The irony is specific and worth stating plainly: the whole purpose of the five-verdict split was to STOP
collapsing distinct verdicts into one pass/fail. My implementation separates them and then immediately
**re-collapses** them, by making `publication_eligibility` a function of `scientific_admission`. The
reviewer's instruction was that these be *reported separately*, not that admission become a publication
blocker.

## And my own test defends the defect

`POOL_F2_F3.patch` line 444:

    assert any("POOL_PUBLICATION_INELIGIBLE" in reason and "30291013" in reason for reason in reasons), reasons

That asserts the corpus-emptying behaviour by name and by PMID. Repairing it will make my own suite go
red and will look like a regression. This is `lessons.md` "A test can DEFEND a defect" — an assertion
encoding what the code happened to do, with no requirement behind it — and it is in code I wrote after
recording that lesson.

## What the patch does get right, and must not lose

The linkage enforcement works and is the thing worth keeping: `unknown_id`, `duplicate_id`, `omitted_id`
and `altered_inputs_updated_aggregate` each return their exact intended first refusal, where pre-fix all
five published with `first_refusal: null`. The five verdicts are now returned natively — the gate output
shows `{'artifact_integrity': 'FAIL', 'state_reproduction': 'PASS', 'input_linkage': 'PASS',
'scientific_admission': 'FAIL', 'publication_eligibility': 'REFUSED'}`, where pre-fix `input_linkage` did
not exist at all.

`rotated_ids` refuses, but on the tuple rather than the row identity. F6B declines to credit it, per the
rule that an inexact first blocker is not a semantic pass. That is the correct call.

## Required repair before POOL is landable

1. `publication_eligibility` must be driven by **linkage and integrity** failures, not by a pre-existing
   `scientific_admission` state. Report admission separately, as the contract asks.
2. Delete or rewrite the line-444 assertion as a requirement rather than a behaviour record, and add the
   negative: the baseline and the three reorder/normalisation controls must still publish.
3. Make `rotated_ids` refuse on `POOL_ROW_IDENTITY_MISMATCH`, so the code names the defect it found.
4. Re-run the full 19-case acceptance and require **4 of 4 controls publishing** and **5 of 5 attacks
   refused with exact codes** before landing.

Until then the landing sequence in `26-landing-sequence-after-decision-B.md` is amended: POOL moves from
"evidenced, pending a corpus gate" to **blocked, pending repair**. The corpus-wide question it was
waiting on ("does POOL refuse any of the 32 served topics?") is now answered in the worst way for a
single topic — it refuses the baseline of `glp1-ra-mace-t2d` — so that question is moot until the repair
lands.
