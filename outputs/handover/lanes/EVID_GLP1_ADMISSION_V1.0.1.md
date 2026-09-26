# V1.0.1: the mechanism that admits FLOW and ELIXA into the GLP-1 primary pool (NOT LANDED)

Branch `evid/glp1-admission`, based on frozen main `6260e70c`. It is to be rebased onto the captain's V1 candidate once that SHA is known. It lands only after Mahmood's hash-bound signature. Until then the gate refuses it by design: the result-change notice's reviewer countersignature is `OPEN`.

## What it does
- **Config.** `topics/glp1-ra-mace-t2d.json` gives `primary_outcome.adjudicated_results` two entries (FLOW, ELIXA). Each entry carries:
  - the decision file (`evidence/glp1_adjudication/{FLOW,ELIXA}.json`) and its pinned sha256;
  - `strand: CONVENTIONAL_GLP1RA`;
  - the witness that defines the outcome.

  The config also pins the text renderer (`evidence/scripts/textrep.py`) and the two FDA PDF text extractions by sha256. FREEDOM-CVO is **not** declared.
- **`harness/result_adjudication.py`** verifies every declared admission at build time, and **fails closed**:
  - The decision bytes must match their pinned sha, and the decision must name the same trial, PMID and NCT.
  - The eligibility decision must start with `ELIGIBLE -- CONVENTIONAL_GLP1RA (primary)`. This is an exact prefix, because FREEDOM-CVO's decision *names* the strand in order to exclude itself.
  - Every witness `{ref, sha256, span}` must name held bytes with that sha, and its span must be verbatim in their render. That is 16 witnesses for FLOW and 10 for ELIXA.
  - The estimate and both bounds must sit together in one witnessed span.
  - The named definition witness's components must equal the outcome's canonical three.
- **`pipeline._build_outcome`**
  - It injects the verified rows before admissibility.
  - It clears only a `machine_absent` entry for the same trial (ELIXA's).
  - It raises if a documented human decision, or another route, also claims the trial.
- **`target_endpoint.admissibility`** re-verifies any row that claims the `signed_result_adjudication` provenance. A forged or edited row is refused.
- **Known-missing panel and invalidation.** Pooled trials leave both. FREEDOM-CVO stays in both.

## Result: derived by the real build, not by hand
`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`

| | k | HR (95% CI) | PI | tau² |
|---|---|---|---|---|
| **Before (served V1)** | 8 | 0.856 (0.8086–0.9061) | 0.8069–0.9081 | 0.00004 |
| **After** | 10 | 0.8613 (0.8069–0.9194) | 0.7531–0.9852 | 0.0027 |

The page shows: *"Previously served: k = 8, 0.86 (0.81 to 0.91). Now: k = 10, 0.86 (0.81 to 0.92)… Entered the pool: PMID 26630143, PMID 38785209."* It also carries the full **ELIXA prespecification dispute**, quoting three sources: the FDA statistical review says "pre-specified" secondary; the FDA summary review says sensitivity analysis; the registry lists no 3-point MACE. Both are in the locked reason of the `docs/result_changes.json` notice. The countersignature is **OPEN**.

## Tests
- **`tests/test_glp1_signed_admission.py`: 13 of 13 pass.**
  - Before k=8 equals the served result.
  - After k=10 is 0.861 (0.807–0.919), through `pipeline.outcome_inputs` + `_build_outcome` + `synth.pool`.
  - FREEDOM-CVO is still excluded.
  - Ten plants, each paired with a control:
    - FREEDOM declared on the primary strand;
    - decision bytes changed;
    - tuple edited and re-pinned;
    - one witness span digit transposed;
    - held source byte changed;
    - forged or edited row at admissibility;
    - renderer swapped;
    - documented absent decision conflict;
    - second route for an admitted trial;
    - definition witness naming another composite.
- **Pre-fix run.** The tests were committed before the mechanism and run against that tree: 9 fired, all on `k=8 != 10` at their control, and the k=8 before-test passed. The run is recorded in `evidence/glp1_adjudication/ADMISSION_TESTS_PREFIX.txt`.
- **Existing tests I updated,** because they asserted the pre-admission state:
  - `test_held_source_never_not_in_committed_source.py`: "primary k=8 unchanged" and "FLOW held but not admitted" became the new requirement. The held spans stay verified, FLOW and ELIXA pool only by signed adjudication, FREEDOM stays out, and the pool recomputes from its rows.
  - `test_m2_battery.py`: the fixture strips `adjudicated_results`, because the battery tests the hand-row route.
- **Green:** the admission suite, the battery, and the held-source file.

## Not done: needs a decision or a site-wide step before V1.0.1 can land
1. **BUNDLE: DONE on the builder side; two decisions left.**
   - `scripts/build_bundle.py` now evidences an adjudicated row by its witnessed tuple span in the committed FDA text extraction. Every predicate is computed on that text, unchanged.
   - The regenerated `BUNDLE.json` shows **8 of 10 rows admissible**:
     - FLOW passes all predicates.
     - HARMONY fails P5, as it did in V1.
     - **ELIXA fails three predicates**, all genuine findings:
       - **P5** — its certified family object (`cache/glp1-ra-mace-t2d/families.json`, NCT01147250) says eligibility UNKNOWN, while the lane's decision says ELIGIBLE.
       - **P9** — the clause carrying the unrounded tuple, "The 95% confidence interval for the hazard ratio is (0.887, 1.172) with a point estimate of 1.02.", does not name the endpoint.
       - **P11** — the carrier passage names on-study *and* on-treatment analyses, so the estimand is UNRESOLVED.
   - **Independent verifier.** `scripts/verify_bundle.py` is deliberately unchanged, and it refuses both FDA-text rows as `UNSUPPORTED_REPRESENTATION` under its declared limit L14 ("binds pooled rows to PubMed records only"). The pool itself reproduces to 1e-9 (k=10, 0.86134).
   - **Decision A: lift L14 for committed regulatory text extractions?** That is a scope change to the independent checker.
   - **Decision B: which ELIXA rendering to bind?**
     - **(a)** The Table 8 rendering, 1.02 (0.89–1.18). Its row names "MACE endpoint (on-study)" and carries the counts 392 vs 400. P9 passes, and the result is identical at 3 dp: k=10, 0.8612 (0.807–0.919). But 1.18 mis-rounds the text's 1.172, and the decision file changes, so its sha and the signature bundle `4bf8ec33` must be regenerated.
     - **(b)** Keep the unrounded interval, and let P9 accept a signed adjudication's named definition witness plus its event counts.
   - Either way, ELIXA's P5 needs its family eligibility object to be repaired (UNKNOWN → ELIGIBLE, per the B-prime decision) or accepted as a finding.
2. **Site-wide certificate refresh.**
   - Changing `harness/` moves `analysis_code_blobs` in **every** topic's certificate. `gate.check_certificate` and `test_stdlib_audit_reproduces_every_served_certificate` then refuse every other page until it is rebuilt. Pooled numbers do not change; the certificate moves.
   - This worktree holds only the GLP-1 cache (disk), so the other ~30 topics were not rebuilt here.
3. **Rebase** onto the captain's V1 candidate, then rebuild GLP-1 and regenerate the notice's `before` against it.
4. **Signature.**
   - Mahmood signs the result-change notice (`scripts/countersign_result_change.py`). Its `rendered_sha256` binds the page.
   - The lane's `SIGNATURE_REQUEST.md` bundle, `4bf8ec33` on `evid/evidence-records`, covers the decision files. If option (a) is taken it must be regenerated.
5. **Limitation.** The component parser reads "MACE+" as generic MACE. ELIXA's 3-point identity rests on the *named* definition witness, the FDA "defined as CV death, non-fatal MI and non-fatal stroke" span, and not on the parser.
