# Signature request, V1.0.1: the GLP-1 MACE primary pool gains FLOW and ELIXA (a served-number change), NOT LANDED

**Status: QUEUED for Mahmood's signature. Nothing served has changed.** Regenerated 2026-09-26 20:11Z by `make_signature_request.py` on branch `evid/v1.0.1-glp1-admission`, against the **V1.0 candidate** `3876a62dca66` (runbook step 0b): the bound `review.json` is byte-identical to the one V1.0 serves (checked; this script refuses otherwise). Tree at generation: `ba58067cddd8` plus this request.

## What the signature admits
Under the protocol's B-prime rules (`protocols/glp1-ra-mace-t2d.md` at `b10c53d3`), through the admission mechanism the build reads (`topics/glp1-ra-mace-t2d.json` `adjudicated_results` -> `harness/result_adjudication.py`):
- **FLOW** (semaglutide, T2D + CKD): 3-point MACE HR 0.82 (0.68–0.98), 212 vs 254. **Identified by its source row**: FDA label Table 10, row "Composite of cardiovascular death, non-fatal myocardial infarction, non-fatal stroke (time to first occurrence)" -- the label itself enumerates the three components; the kidney composite 0.76 in the same table is a different row. Class EXACT_TARGET.
- **ELIXA** (lixisenatide, T2D after ACS): 3-point MACE HR 1.02 (0.887–1.172), 400 vs 392. **Identified by its source row, never by its numbers**: FDA statistical review Table 8 "Analysis of the MACE Endpoint", row "MACE endpoint (on-study)", the definition of that label ("secondary MACE event (defined as CV death, non-fatal MI and non-fatal stroke)") and the event counts 400/392, which must also appear in the sentence carrying the tuple. Class EXACT_TARGET. The 4-point MACE+ primary is printed with the SAME numbers, HR 1.02 (0.89, 1.17), in the same review (Table 1, 406 vs 399); that row is **refused as DIFFERENT_OUTCOME** by the mechanism (its label MACE+ is defined with hospitalization for unstable angina), with a test.
- **FREEDOM-CVO** (ITCA 650): eligible only on `GLP1RA_ANY_DELIVERY`; **not** in the primary pool, not declared to the mechanism (a declaration naming the primary strand is refused, with a test).

**ELIXA prespecification dispute (disclosed on the page, in the result-change notice):** the FDA statistical review calls the 3-point MACE a secondary endpoint analysed by a pre-specified Cox model; the FDA summary review calls it a sensitivity analysis; the registry lists the 4-point primary and 5-/6-point secondaries but no 3-point MACE. The same statistical review renders the on-study interval three ways: (0.887, 1.172) in the section 3.3.4.3 text (bound), (0.89, 1.18) in Table 8, (0.89, 1.17) in the executive summary.

Every field carries a witness span re-verified against sha256-pinned held bytes at build time (6d959f775488 FLOW, 28277b88d557 ELIXA decision sha256 prefixes).

## Derived before -> after (production path; the recomputed BEFORE reproduces the V1.0 served result exactly; the primary AFTER's rows come from the admission mechanism)
| | pool |
|---|---|
| **before (V1.0 served)** | k=8, HR 0.856 (95% CI 0.8086–0.9061), prediction interval 0.8069–0.9081, tau² 4e-05 |
| **after: primary, + FLOW + ELIXA** | k=10, HR 0.8613 (95% CI 0.8069–0.9194), prediction interval 0.7531–0.9852, tau² 0.0027 |
| after, ELIXA at its Table 8 rendering (0.89–1.18) | k=10, HR 0.8612 (95% CI 0.807–0.919), prediction interval 0.7539–0.9838, tau² 0.00263 |
| alongside: ANY_DELIVERY, + FLOW + ELIXA + FREEDOM-CVO | k=11, HR 0.8673 (95% CI 0.7999–0.9404), prediction interval 0.7046–1.0675, tau² 0.00737 |

**Derived notice for the served page:** the pooled HR moves 0.856 -> 0.8613; direction and significance UNCHANGED. Heterogeneity is no longer ~0: tau² 4e-05 -> 0.0027; the prediction interval widens from 0.8069–0.9081 to 0.7531–0.9852. The k=8 result stays on the page as the previous result.

## Open before V1.0.1 can land (none of these changes a number in this request)
- **Build on the candidate tree** (held for disk; the captain's go): `build_topic.py glp1-ra-mace-t2d`, bundle, site-wide certificate refresh (harness code moved), the runbook's Step 3-6 checks and `verify_all.py`. The admission suite `tests/test_glp1_signed_admission.py` needs cache/ and has not been run on this tree; `tests/test_glp1_admission_identity.py` (cache-free) passes.
- **Bundle verifier limit L14** (PubMed records only) refuses the two FDA-text rows; lifting it is the captain's decision.
- **ELIXA rendering**: bound = the unrounded text interval; the Table 8 rendering gives the same result to 3 dp (row above). Changing it changes a bound file and this bundle.

## Bytes this signature binds (sha256)
```
6d959f7754880123beb4487869c887f4c50992dbf3086b8c9ba075486c141300  evidence/glp1_adjudication/FLOW.json
28277b88d557b03c9df546f19b53f2e449ef25fa6445d2792aeef555151bf667  evidence/glp1_adjudication/ELIXA.json
f593aa1ee0b5d9ae823778c40444c699633860aa676c7cc735eefe371f5589ef  evidence/glp1_adjudication/FREEDOM-CVO.json
3901e7d376197ce1fc5bd141a748aa7365a6db2f37e6b8f38f0cfad73427f069  evidence/glp1_adjudication/build_decisions.py
43421c0a30eb59140b6e85ac0344eca069e66917c94c1f6dec2d14ae55721d7b  evidence/glp1_adjudication/BEFORE_AFTER.json
822a15f4f7d31f3596632d05e2e01421763878ab90a0dab496e40b970f263e99  evidence/glp1_adjudication/compute_before_after.py
5bb383cb3d0baeff5d59fbe7f66b8b9759a88a5d3853deeddaf185f831e3e9f3  topics/glp1-ra-mace-t2d.json
ce322e0793bbfdc789a3a8a69c3ee310ffb0e8b4dee492f0301ebb1cc80bbf5c  harness/result_adjudication.py
09f5dd4777bf58e31b403c6fe5c0d3455ccce2b7b1798fa1976fbe4a91a1fcbc  harness/pipeline.py
5de4836da2a224a0479aad42a32d7850ef3697a01c4111811e7f6f2637a95db3  harness/target_endpoint.py
54a865bea44d8467bb2bb6c992af9773bdf58b692acc0dcf4d8962be52772a80  harness/known_missing.py
c49f8f855e2bdff52e9334e45bb32fbc2815a4459624debd6f33ef8479f27241  harness/invalidation.py
8f27b6a4df241745acb13d022d71aab7af7a7bf7bf88ca8efa83a2dbdfbc41c8  evidence/scripts/textrep.py
41889108fe1dc8c026a6efdc9bab3863c248af620ff79db07f6957439679c1b4  tests/test_glp1_admission_identity.py
b49329f42215a5bcfef98cb7c15ff7c87efde8315c3e4b438d1334c0b4022d71  tests/test_glp1_signed_admission.py
c5a1d09e271f7e9bbac5dfd2eabfd2ef33b56dbed85f6647b33017bc83848160  docs/reviews/glp1-ra-mace-t2d/review.json
d7208503c823d1b4f10fb8e356b69d30b3f25874420a8b678d25319811a7ae4c  protocols/glp1-ra-mace-t2d.md
7d9922c55c43a8732c8c2e666478b2ae507ad9f904434c45c6213109f99714bc  outputs/handover/lanes/DECISION_CLASS_BOUNDARY_STRANDS.md
```
**Bundle sha256 (sign this): `27df31f71102b2ecf7e9099de0559970d117e78e5369f47530d79862b5a9befe`**

Signature: `SIGNED-BY: ______  BUNDLE: 27df31f71102b2ecf7e9099de0559970d117e78e5369f47530d79862b5a9befe  DATE: ______` (unsigned: this request lands nothing)
