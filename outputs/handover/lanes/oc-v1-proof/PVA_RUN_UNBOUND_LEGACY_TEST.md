# Lane OC -> pva: run this PRODUCER test in the release audit (UNBOUND_LEGACY fail-open)

`scripts/verify_bundle.py` is stdlib-only and imports nothing from the repo by design, so it cannot run producer code. The
producer invariant is therefore checked by a producer test, which the release audit should run on the candidate and record:

```bash
python -m pytest -q tests/test_unbound_legacy_failclosed.py -p no:cacheprovider
```

- **On a tree WITH the fix** (branch `oc/v101-unbound-failclosed` 7244e3b2): 11 passed.
  - LEADER 3-point is admitted.
  - ELIXA 4-point is refused, whether classified (NEAR_MATCH) or forced to DIFFERENT_OUTCOME.
  - ELIXA with its class deleted, None, or an unknown class abstains with ENDPOINT_IDENTITY_MISSING.
  - The plant is ADMITTED by the pre-fix producer (blob 1b309c5b), so it proves something.
- **On the V1 candidate 3876a62d or earlier (without the fix):** the file is absent. Record the limitation as *"producer admits a
  classless row as UNBOUND_LEGACY (BUNDLE L10); 65 of 127 served pooled rows on 22 of 32 topics are admitted only this way"*.
  The measurement is `evidence/unbound_legacy/README.md` on that branch.
- The test fails, never skips, if the pinned commit 3876a62d is missing from history. A shallow clone is a failure to record, not
  a pass.
- The fix is NOT landed. Its served-number moves (17 of 27 primary pools withdrawn, 2 cross null) await Mahmood's decision and
  signature.
