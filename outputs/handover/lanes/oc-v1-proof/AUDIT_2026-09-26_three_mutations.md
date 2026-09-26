# Auditor pass on the live release (57dcc327): three one-value LEADER mutations, run through REAL verifiers

These runs used the real `verify_bundle.py`, not the auditor's predicate reduction. The row is the real LEADER row (PMID 27295427).
Each run changes exactly one value of `BUNDLE.json` in memory. The canonical and restore controls PASS on every verifier. Probe:
`evidence/v11_identity_values/probe_real_verifier.py` on `oc/v11-contrast-rules`.

| mutation of LEADER | LIVE verifier d1ba9320 on live bytes | V1 input (oc/ordered-contrast 23642e0d) on its bytes | V1.1 (oc/v11-contrast-rules d62c09a3, not in V1) |
|---|---|---|---|
| canonical (control) | PASS | PASS | PASS |
| comparator_direction -> "placebo vs GLP-1 RA" | **PASS (undetected)** | **refused** `COMPARATOR_DIRECTION_MISMATCH` (P10) + `BOUND_TO_UNREGISTERED_ESTIMAND` (P11) | refused (same) |
| estimator -> "odds ratio" | **PASS (undetected)** | **refused** `ESTIMATOR_MISMATCH` (P10, P15 false); the pool refuses `POOL_MEASURE_UNIDENTIFIED` | refused (same, + `ANALYSIS_IDENTITY_KEY_MISMATCH`) |
| analysis_set value -> "per-protocol", basis stays REGISTERED_DEFAULT | **PASS (undetected)** | **PASS: still OPEN in V1** | refused `REGISTERED_DEFAULT_VALUE_MISMATCH` |
| analysis_identity_key edited alone | PASS | **PASS: still OPEN in V1** (the key is never recomputed for ordinary rows) | refused `ANALYSIS_IDENTITY_KEY_MISMATCH` |
| analysis_set.registered -> "per-protocol" | PASS | **PASS: still OPEN in V1** | refused `REGISTERED_DEFAULT_VALUE_MISMATCH` |
| restore (control) | PASS | PASS | PASS |

**The key omits comparator_direction.** This is true in live and in V1 (build_bundle 3.18). V1.1 adds it at format 3.19; the verifier
reads 3.18 with the legacy key.

**For the release note (pva):**
- V1 closes the comparator and estimator value checks.
- V1 does NOT check a REGISTERED_DEFAULT field's value against the registered default.
- V1 does NOT recompute analysis_identity_key, and the key does not include comparator direction.
- Both are fixed on a V1.1 branch, with plants that fire before the fix. They need a 3.19 bundle rebuild, which is a served change
  requiring signature.

**Still pending:** the same table on the CANDIDATE's verifier, and after deploy on the SERVED bytes. The V1 column above is the V1
integration input 23642e0d, not the candidate. It is re-run the moment the candidate is pushed.
