# Engineering decision: the estimand repair is restructured under §F.5, not shelved

Taken 2026-09-24 under delegated engineering authority. **This decision changes no served number by itself**;
the resulting change still needs Mahmood's signature, but it is now a 4-row change instead of a corpus-wide one.

## The blocker as it stood
The estimand repair (audit pass 2, `BND1.patch`, the SUSTAIN-6 / AMPLITUDE-O pair) was measured and QUEUED,
not landed, with the recorded reason that it "takes 42 of 46 served occurrences to ABSTAIN, which empties the
corpus and is Mahmood's decision, not an engineering one."

Measured, from `BND1/bnd1.json::blast_radius`:

    all served row occurrences            46
    occurrences moved                     46
    proposed combined states              ABSTAIN 42, INADMISSIBLE 4
    nonempty served result objects hit    29 of 29
    GLP-1 primary rows                    7 of 7 move

and BND1's own note: *"Retyping the held evidence in memory only, with no new evidence, leaves 7 of 7 GLP-1
primary rows ABSTAIN"* — i.e. the abstention is caused by the evidence not being observable, not by the rows
being wrong.

## Why §F.5 decides it
`ESTIMAND_UNOBSERVED` is, by its own name, an **evidence-state uncertainty**: the estimand cannot be observed
in the held bytes. §F.5 forbids converting that into removal from the analysis:

> "Do not turn an evidence-state uncertainty into a scientific exclusion merely to make the gate green.
> Recover or adjudicate the missing support and label assumption-dependent analysis explicitly."

and preserves the distinction that matters:

> "Unknown scientific facts can be legitimate data; an unknown enum spelling or missing mandatory object is a
> schema error, not permission to pass."

So the corpus-emptying was never the repair working — it was the forbidden move, at scale.

## The split, computed from BND1's own recorded per-row codes
    42 of 46   ESTIMAND_UNOBSERVED ALONE                     -> RETAIN, disclosed, assumption-dependent
     4 of 46   plus ESTIMAND_BASIS_DISAGREES,
               SEMANTIC_VALUE_MISMATCH, TIMEPOINT_MISMATCH   -> INADMISSIBLE (real defects, stay refused)

All 4 real defects are `glp1-ra-mace-t2d` rows: PMID 31185157, 27295427, 34215025, 40162642.

## The decision
1. `ESTIMAND_UNOBSERVED` **alone** does NOT refuse and does NOT abstain-and-drop. The row is retained, the
   outcome is marked assumption-dependent on the unobserved estimand, and the missing dimension is NAMED on
   the row so a reader can act on it. Same shape as the masking dispute policy landed today
   (`INCLUDE_MASKING_DISPUTED`).
2. A schema error or a semantic mismatch (`ESTIMAND_BASIS_DISAGREES`, `SEMANTIC_VALUE_MISMATCH`,
   `TIMEPOINT_MISMATCH`, malformed or missing mandatory identity) **remains INADMISSIBLE**. Uncertainty is
   retained; a defect is refused. Conflating the two in either direction is the error.
3. The served radius therefore becomes **4 of 46 refused**, each for a named semantic defect, instead of 42
   abstaining with 29 of 29 result objects emptied.

## What this decision does NOT claim
The split above is computed from the per-row codes BND1 RECORDED, not from a fresh build under the restructured
rule. It must be re-measured by rebuilding before anything lands; the number to confirm is 4, and the
prediction to falsify is that no row outside those 4 is refused. That rebuild is part of the §F.6
full-path run, and until it happens this is a prediction with a stated denominator, not a result.

Signatures on the resulting served-number change remain Mahmood's.
