# CHK full-verifier refusals

No release claim. Lane-specific tests pass; full verifier refuses.

## limb_unit_tests

```text
TARGET verify_all.limb_unit_tests: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:138 files files=158 tests/conftest.py tests/test_aact_cache.py tests/test_aact_recurrent_guard.py ...
..............................................                           [100%]
================================== FAILURES ===================================
__________________________ test_real_store_validates __________________________

    def test_real_store_validates() -> None:
        ok, reasons = fixstate.check(ROOT)
    
>       assert ok, "\n".join(reasons)
E       AssertionError: docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
E       assert False

tests\test_fixstate.py:457: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
1 failed, 981 passed in 491.70s (0:08:11)
```

## limb_fixstate

```text
TARGET verify_all.limb_fixstate: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=3 registry/fixes.json docs/fix_ledger.json scripts/render_fix_ledger.py
docs/fix_ledger.json is stale; run python scripts/render_fix_ledger.py
```

## limb_honest_ratchet

```text
TARGET verify_all.limb_honest_ratchet: head=237e90946f5b257265b0a3b1c986a8907d12eded base=none tree=dirty:141 files files=34 docs/index.html docs/ratchet_acknowledgements.json docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html ...
TARGET honest_ratchet: head=237e90946f5b257265b0a3b1c986a8907d12eded base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:141 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6
docs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11
docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
```

## limb_gate_gaps

```text
gate gaps table STALE: GATE_GAPS.md
```


Measured follow-up: the three ratchet marker counts are unchanged from served base 237e9094 (6, 11, 24 respectively). See .tmp/chk/ratchet-base.json. The older-base ratchet remains a refusal; no bypass.
