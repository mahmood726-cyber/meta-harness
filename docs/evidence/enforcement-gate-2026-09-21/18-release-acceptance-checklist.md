# Release acceptance checklist — adopted from the external audits of 2026-09-24

This is the checklist the "Page verifier and archive lane" scores our landings against. It is adopted verbatim in
substance from two external audit passes: the second (predicates reproduced in isolation) and the third (the auditor
authenticated the source bytes and ran the GENUINE verifier `d1ba9320` and the real producer). Items are acceptance
CRITERIA, not a description of current behaviour. Nothing on this list is claimed to be satisfied today.

## Wording that must not drift
- **`38c04411` is the known-defective reference that repairs are tested against.** Nobody calls it "semantically
  verified". The same applies to any later release until it passes this list.
- These are **controlled mutations**. No reversal is present in the live results, and a green verifier result cannot
  support a stronger scientific claim than the list below permits.
- Release identity moves: the audit's own `9fc4518a` was already stale when read — `main` was `b127522d` at
  2026-09-24T08:0xZ. **Every probe must name the exact release it ran against, and be re-run on the SERVED bytes of the
  release being accepted.**

## A. Acceptance matrix (second pass, items a–e)
- **(a) The authentic, correctly bound baseline still PASSES.** A repair that rejects everything is not a repair. Keep
  the valid-evidence positive controls passing.
- **(b) The named SUSTAIN-6 / AMPLITUDE-O / FREEDOM-CVO mutations FAIL, and fail FOR THE INTENDED REASON** — the
  refusal code must name the defect, not an incidental one.
- **(c) The numeric-prefix, mixed-tuple and identity-erasure mutations FAIL.**
- **(d) Semantic mutations run with internally consistent package digests and unchanged authentic sources**, so a
  checksum failure is never mistaken for a semantic rejection. **Integrity tests and semantic tests stay separate
  categories.**
- **(e) BOTH the producer route and the independent verifier enforce the decision.** No alternative pooling route may
  bypass the checker.

## B. Acceptance criteria (third pass, items 1–5)
1. Keep the authentic baseline and the valid-evidence positive controls passing.
2. Reject: pool substitutions; duplicate or missing IDs; contradictory or malformed estimand fields; FREEDOM mixed
   tuples; the REWIND arm swap.
3. Demonstrate each rejection through the **complete producer AND the publication gate**, not only the consumer.
4. **Report four verdicts separately: byte integrity, arithmetic consistency, scientific admissibility, publication
   eligibility** — and define which combination permits release.
5. Regenerate under a **new exact release identity** and re-run every probe on the served bytes.

## C. Why (4) is required, in one measured example
The verifier PASSes while HARMONY (PMID 30291013) fails P5 and remains in the k=8 pool; the admissible-only pool is
0.8664 (0.8142–0.9218), k=7. That was a deliberate migration state (`c164c876`), but it means a PASS today carries no
statement about scientific admissibility. Until the four verdicts are separated, "the verifier passed" must not be
reported as "the result is admissible".

## D. Repair order (the auditor's, adopted)
1. Generate pooling inputs directly from the certified, eligible rows.
2. Bind every number to its endpoint, arm and analysis.
3. Require complete, valid identity fields and check their meaning against the evidence.
4. Separate the integrity, arithmetic and admissibility verdicts.
5. Run the same deliberate-error tests through the full production and publication route.

## E. Standing constraints that outrank any item above
- **Anything that changes a served number waits for Mahmood's signature.** 41 result-change notices are OPEN; 33 need
  an individual signature because a conclusion changed.
- A signature the system applies to its own result change is a password, not a check.
- Every plant must be **observed failing before its fix exists**, with a positive control that keeps passing, and a
  restore.
- A recovery or radius claim is unproven until the real build is run and the first failing check observed per row
  (`outputs/findings-2026-09-22/HAZARD_reported_reason_vs_binding_constraint.md`).
- An exhaustive claim needs a positive control that would have fired
  (`outputs/findings-2026-09-22/HAZARD_exhaustive_claim_over_incomplete_representation.md`).
