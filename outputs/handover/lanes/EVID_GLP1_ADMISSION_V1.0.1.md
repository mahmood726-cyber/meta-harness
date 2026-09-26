# V1.0.1: the mechanism that admits FLOW and ELIXA into the GLP-1 primary pool (NOT LANDED, build held)

Branch `evid/v1.0.1-glp1-admission`, on **`v1/candidate` `3876a62d`** (the V1.0 cut). It lands only after Mahmood signs the request in `evidence/glp1_adjudication/SIGNATURE_REQUEST.md` (bundle `b51cff43…`). That request was regenerated against the candidate tree: runbook step 0b gives **MATCH**, meaning the bound `review.json` is byte-identical to what V1.0 serves.

**Held for disk (captain's instruction).** This branch holds the design, the records and the tests. It has not been built. The build is `outputs/V1_0_1_RERUN_RUNBOOK.md`, steps 2–7.

## The admission mechanism
- **Config.** `topics/glp1-ra-mace-t2d.json`, `primary_outcome.adjudicated_results`, declares FLOW and ELIXA. Each entry pins its decision file by sha256 and names strand `CONVENTIONAL_GLP1RA`. The config also pins the text renderer and the FDA PDF text extractions by sha256. FREEDOM-CVO is **not** declared.
- **`harness/result_adjudication.py`** runs at build time and fails closed. It requires:
  - the decision sha to match its pin;
  - trial, PMID and NCT to match the entry;
  - eligibility to start with `ELIGIBLE -- CONVENTIONAL_GLP1RA (primary)`, as an exact prefix;
  - every witness span to be verbatim in sha-pinned held bytes;
  - the tuple (estimate + both bounds) to sit in one witnessed span;
  - an **endpoint identity** (below).
- **Pipeline.** `pipeline._build_outcome` injects the rows. It clears only ELIXA's `machine_absent` entry, and it raises if a documented decision or a second route also claims the trial.
- **Admissibility.** `target_endpoint.admissibility` re-verifies the row, including its class.
- **Known-missing panel and invalidation.** The admitted trials drop out of both; FREEDOM-CVO stays in both.

## Endpoint identity: from the source row, never from the numbers
In ELIXA's FDA statistical review, the 3-point secondary MACE and the 4-point primary MACE+ are both printed as **HR 1.02 (0.89, 1.17)**. That is the auditor's attack fixture. Each decision's `bound_result.endpoint_identity` therefore carries:

1. **The identity row witness.** Its table header and row label must be verbatim in it.
   - ELIXA: Table 8 "Analysis of the MACE Endpoint", row "MACE endpoint (on-study)".
   - FLOW: label Table 10, row "Composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke (time to first occurrence)".
2. **The definition of that label.**
   - ELIXA: "secondary MACE event (defined as CV death, non-fatal MI and non-fatal stroke)". The label term `MACE` is matched as a whole token, so `MACE+` never matches it.
   - FLOW: the row label itself enumerates the components.
3. **The event counts.** They must appear in both the identity row and the span that carries the tuple: ELIXA 400/392, FLOW 212/254.

The class is computed from the label's own definition. Anything but EXACT_TARGET is refused with `endpoint_class = DIFFERENT_OUTCOME`. The harness's finer relation stays in the message; for ELIXA's 4-point row that is a NEAR_MATCH superset (+unstable angina), so the mapping to DIFFERENT_OUTCOME is stated here, not hidden. Admitted rows carry `target_endpoint_class EXACT_TARGET` and binding `signed_result_adjudication_witnesses`, so no UNBOUND_LEGACY route exists.

## Derived before → after, on the candidate tree
`compute_before_after.py` takes the primary scenario's rows from `result_adjudication.admitted_rows`. The typed values are a cross-check that must agree, and they do. BEFORE reproduces the V1.0 served result exactly.

| | k | HR (95% CI) | PI | tau² |
|---|---|---|---|---|
| **Before (V1.0 served)** | 8 | 0.856 (0.8086–0.9061) | 0.8069–0.9081 | 0.00004 |
| **After** | 10 | 0.8613 (0.8069–0.9194) | 0.7531–0.9852 | 0.0027 |

## Page: the previous result beside the primary result
`harness/page._previous_result_row` renders **"Previous result (k=8): HR 0.856 (0.809–0.906)"** in the primary result table. This is runbook Step 4, and Mahmood's request: "ten trials please with old k on same page".
- The values are read from the result-change notice's `before` object, never typed.
- The row renders only when the notice opts in with `show_previous_result: true`. Only the GLP-1 primary notice sets it, so no other page moves.
- The countersigned notice block does not read the opt-in, so its signed bytes do not change.
- `tests/test_previous_result_row.py`: 4 pass; 3 fired pre-fix.

## Tests
- **`tests/test_glp1_admission_identity.py`: 10/10 pass. Cache-free, so CI-runnable without pypdf.**
  - ELIXA admitted by row + label definition + counts, with explicit EXACT_TARGET.
  - **The 4-point MACE+ row with identical numbers is refused as DIFFERENT_OUTCOME.**
  - The 4-point row relabelled with the 3-point definition is refused.
  - The 3-point row with the 4-point counts is refused.
  - A decision with no identity block is refused.
  - A forged class is refused at admissibility.
  - FLOW's identity pointed at its kidney-composite row is refused.
  - FLOW is identified by its own row label.
  - **Hand-entered route.** A hand-extracted row HR 1.02 (0.89, 1.17) against the FDA review is never pooled, whichever row it cites (nothing, the 4-point Table 1 row, or either summary sentence).
    - The hand binder cannot separate the two by number, so it sets the row aside (ENDPOINT_UNBOUND). It does not name it DIFFERENT_OUTCOME.
    - ELIXA therefore enters only through the identity-bound adjudication.
- **Pre-fix run.** Six of the identity tests were written first and fired before the fix. The 4-point plant **did not raise**, so the earlier port would have admitted it. Recorded in `evidence/glp1_adjudication/ADMISSION_TESTS_PREFIX.txt`.
- **`tests/test_glp1_signed_admission.py`** (12 pipeline-level cases) needs `cache/` and has **not been run on this tree**. It passed 13/13 on the frozen-main branch before the identity change; the definition-witness plant has since moved to the identity file.

**Cache-free regression check** (20 existing test files that touch notices or page rendering, plus the new ones):
- **234 pass.**
- **11 fail identically on the base `3876a62d`** with this branch's changes removed. They need `cache/` (`hm2_contract`, `model_source` queues, `delegated_acceptance`), so they are environmental, not caused by this branch.
- **One real failure found and fixed.** Every notice must keep "the numbers are not asserted wrong" and "eligible evidence awaiting adjudication". The GLP-1 notice now states both, truthfully: the k=8 result is superseded by added evidence, not corrected, and FREEDOM-CVO remains eligible evidence awaiting adjudication of its strand.

## Open, in runbook order
1. **Build (held).** Topic, bundle, site-wide certificate refresh (harness code moved, so every topic's certificate moves), then Step 3–5 checks and `verify_all.py`. A Codex brief for this is ready at `F:\mh-lanes-wt\v101-codex\BRIEF.md`, not launched.
2. **Bundle verifier limit L14.** It covers PubMed records only and refuses the FDA-text rows. Lifting it is the captain's call.
3. **ELIXA rendering.** The bound value is the unrounded text interval (0.887–1.172). Table 8's (0.89–1.18) gives the same result to 3 dp. Changing it changes a bound file and the signature bundle.
4. **Signature.** Mahmood signs bundle `b51cff43…`. The result-change notice's reviewer countersignature is OPEN.
