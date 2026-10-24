# CROSS-EXCH-018 — executable effect-type refusal handoff

**Scope:** one synthetic, bounded, two-repository regression for **estimand typing at the evidence exchange boundary**. Not clinical validation, an R statistical oracle, or a four-repository ecosystem canary.

## Evidence gap and bounded change

The [previous frozen handoff (#152)](https://github.com/mahmood726-cyber/meta-harness/pull/152) proved that `REFUSE`, `MANUAL_REVIEW`, duplicate shadowed decisions, bad source hashes and mismatched trial IDs cannot invoke the actual RapidMeta consumer. It **did not execute the mismatched statistical-effect-type gate**. Such a mismatch could otherwise silently pool data under an inappropriate measure if the consumer did not preserve the producer's declared estimand.

This independent case **does not change the statistical engine or either frozen component**. The Meta-Harness producer, validator and transport-to-count bridge are loaded from exactly `05b8d45e2c534e038d3549d0b062cfa67e740f00`; the actual RapidMeta `PairwisePool.pool2x2` consumer is checked out at exactly `368137dc437543c721b98be39c14282c338f7797`. The synthetic source has SHA-256 `666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398`. Python `3.13.7`, Node `22.14.0`, Ubuntu `24.04`. See [frozen-estimand-018.json](frozen-estimand-018.json) for the versioned **NOT_RUN-at-registration** specification.

Two source-grounded synthetic exchanges are processed by the **unchanged pinned producer/consumer**:

1. A well-typed RR/ITT control with two synthetic trials **must execute** real pinned RapidMeta pooling.
2. The same source/trials/spans/counts, but with proposed-pool `measure=OR` while both study rows still declare `RR`, **must REFUSE before pooling**. A subprocess tripwire causes a CI failure if an attempted pooling subprocess is reached.

Both original wire inputs and both results, plus a copy of the immutable text source, are archived with five SHA-256 digests and the exact checked-out commits. A **separate workflow step** rehashes the captured bytes, rechecks the gate decisions and injects a one-byte digest mismatch. Inspect actual GitHub Actions conclusion before reporting any PASS.

## Reproduction

Checkout the orchestration branch containing [frozen_estimator_handoff_018.py](frozen_estimator_handoff_018.py), then independently checkout the pinned Meta-Harness producer and RapidMeta consumer commits in sibling directories `meta/` and `rapidmeta/`. With the exact runtimes:

```sh
python governance/benchmarks/cross_repo/v0.1/frozen_estimator_handoff_018.py \
  --meta meta --rapidmeta rapidmeta --output handoff-018-evidence
```

The [frozen-estimand-018.yml](../../../.github/workflows/frozen-estimand-018.yml) workflow performs all checkouts, pin verification, real producer/consumer execution, independently rechecks the evidence hashes and uploads an artifact (90-day retention). It does not replace, relax, or bypass the inherited `verify_all` job.

## Coverage accounting

This is a proposed **CROSS-EXCH-018**, kept separate from the unexecuted original v0.1 `CROSS-EXCH-001…015`, the reserved unimplemented `CROSS-EXCH-016` CLI/API equivalence proposal and `CROSS-EXCH-017` refusal canary. The earlier registry source SHA (`a62cbc...`) predates the v0.1 benchmark files: do not infer those fifteen cases were executable under that historical source pin or rewrite the original pin silently.

E156, starter and Sentinel are **NOT EXECUTED**. External R parity, prospective study discovery, blinded independent human adjudication, signed cross-platform ecosystem installation and independent usability are **NOT TESTED**. No published clinical outcomes or reviewer assessments are involved. Draft PR requires completed exact-head CI, inherited full verify and genuine repository review before merging.

[Public oversight ledger #148](https://github.com/mahmood726-cyber/meta-harness/issues/148).
