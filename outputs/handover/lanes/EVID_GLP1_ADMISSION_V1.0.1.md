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
1. **BUNDLE and the ELIXA binding: a decision for the captain / Mahmood.**
   - `scripts/build_bundle.py` assumes every pooled row has a `records.json` abstract, so it refuses FLOW. It needs a branch for adjudicated rows, and `scripts/verify_bundle.py` needs the same branch.
   - Prototyped predicates:
     - **FLOW passes** P2 (located), P3 (tuple in clause), P4 (components) and P9 (target mention in the tuple's clause), against the FDA label text.
     - **ELIXA fails P9** with `AMBIGUOUS_ENDPOINT_BINDING`. The clause that carries the unrounded tuple — "The 95% confidence interval for the hazard ratio is (0.887, 1.172) with a point estimate of 1.02." — does not name the endpoint. This is the same property that makes the M2 hand binder abstain.
   - Options:
     - **(a)** Pool ELIXA's **Table 8** rendering, 1.02 (0.89–1.18). Its clause names "MACE endpoint (on-study)" and carries the counts 392 vs 400, and P9 **passes**. The result is identical at 3 dp: k=10, 0.8612 (0.807–0.919), PI 0.7539–0.9838. But 1.18 is a known mis-rounding of the text's 1.172, which is why the decision of record binds the unrounded interval. Choosing (a) changes a bound value, so the decision file gets a new version, a new pinned sha and a new signature bundle.
     - **(b)** Keep the unrounded interval and let P9 accept a signed adjudication's named definition witness plus its event counts as the target mention. That is a rule change to the independent verifier.
   - I did not pick one.
2. **Site-wide certificate refresh.**
   - Changing `harness/` moves `analysis_code_blobs` in **every** topic's certificate. `gate.check_certificate` and `test_stdlib_audit_reproduces_every_served_certificate` then refuse every other page until it is rebuilt. Pooled numbers do not change; the certificate moves.
   - This worktree holds only the GLP-1 cache (disk), so the other ~30 topics were not rebuilt here.
3. **Rebase** onto the captain's V1 candidate, then rebuild GLP-1 and regenerate the notice's `before` against it.
4. **Signature.**
   - Mahmood signs the result-change notice (`scripts/countersign_result_change.py`). Its `rendered_sha256` binds the page.
   - The lane's `SIGNATURE_REQUEST.md` bundle, `4bf8ec33` on `evid/evidence-records`, covers the decision files. If option (a) is taken it must be regenerated.
5. **Limitation.** The component parser reads "MACE+" as generic MACE. ELIXA's 3-point identity rests on the *named* definition witness, the FDA "defined as CV death, non-fatal MI and non-fatal stroke" span, and not on the parser.
