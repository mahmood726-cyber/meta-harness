# CROSS-EXCH-017: frozen synthetic two-repository refusal canary

**Scope:** research-stage *synthetic* evidence integration, **not** independent clinical validation, method-matched R parity, externally adjudicated screening, or a signed five-component installation.

## Source-backed gap

The earlier [scoped candidate PR #150](https://github.com/mahmood726-cyber/meta-harness/pull/150) executed a real pinned RapidMeta consumer but checked out the **moving candidate Meta-Harness branch** as the producer/validator. Its archive reported that moving checkout honestly. It was not a frozen **two-sided** execution, so the old CROSS-EXCH-001…015 common benchmark cases must not be promoted.

This scoped addition supplies an immutable *producer* checkout too: Meta-Harness `05b8d45e2c534e038d3549d0b062cfa67e740f00`; RapidMeta `368137dc437543c721b98be39c14282c338f7797`. The producer already contains the raw JSON duplicate-key refusal gate and a concrete two-row, archive-span-verifiable, synthetic-only `PairwisePool.pool2x2` smoke consumer path. The pinned source text SHA-256 is `666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398`.

## Registration and executed evidence are different objects

`frozen-handoff-017.json` is the **versioned proposed pin specification**, initially `NOT_RUN`. It records all four repo identities, but E156 and Starter are explicitly `NOT_EXECUTED`. The original 15-case v0.1 registry and its fixed common pin `a62cbc...` are unchanged and **NOT_RUN**; proposed ASReview-derived `CROSS-EXCH-016` remains reserved and **NOT IMPLEMENTED**. CROSS-EXCH-017 is a separate, bounded two-repo case, not a claimed full-system benchmark.

The isolated [workflow](../../../.github/workflows/frozen-refusal-017.yml) checks out the **exact** earlier Meta-Harness commit alongside exact RapidMeta, separately from the moving orchestration/manifest branch. It refuses a mismatching git HEAD before execution and verifies Python `3.13.7`, Node `22.14.0`, source digest and declared scenario IDs. The CI contains an intentional *wrong-commit* negative check and a one-byte artifact-tampering negative check; both must be refused. The executable pinned runner exercises six exact raw-input scenarios: one `ALLOW` synthetic engine smoke and five `REFUSE`/ `MANUAL_REVIEW`/shadowed decision/hash/trial mismatches that must never invoke Node. A separate workflow step independently rehashes all twelve raw input/output records, verifies their refusal/engine-invocation flags, and writes `frozen-execution.json` with both checkout SHAs, run URL, specification hash, digest-index hash, and the actual orchestration checkout. Its `local_canary_status=PASS` records only the step's own checks; inspect the completed GitHub Actions conclusion before reporting a verified run.

To repeat on clean Ubuntu 24.04, check out *both* producer and consumer at the above exact commits and use Python 3.13.7 plus Node 22.14.0:

```sh
python meta/benchmarks/cross_repo/v0.1/pinned_pairwise_canary.py \
  --rapidmeta rapidmeta --output a-fresh-nonexisting-directory
```

To verify the frozen two-sided provenance and archive digests **rather than merely invoking this command**, run `frozen-refusal-017.yml` and download the complete `frozen-cross-exch-017-<workflow SHA>` artifact. Recompute each `index.json` digest from the captured bytes and compare both `frozen-execution.json` git identities with the published `frozen-handoff-017.json`. The Actions retention period is 90 days; preserving external durable evidence remains an open need.

## Honest limits and merge gate

The source text and pairwise counts are artificial. Raw source hashes and locators establish *transport custody*, not authenticity of published trial data. The canary-only text count grammar must never be applied to clinical evidence. No live Meta-Harness prospective concept search, blinded human adjudication, publisher signing, native pinned `metafor` comparison, Windows canary, or end-to-end four-repo installer exists in this scope.

The parent Meta-Harness `verify_all` workflow **failed** at [run #40085246467](https://github.com/mahmood726-cyber/meta-harness/actions/runs/40085246467) even though the dedicated candidate canary [passed](https://github.com/mahmood726-cyber/meta-harness/actions/runs/40085246362). This extra workflow does **not** replace or weaken `verify_all`. Keep the proposal as a draft and unmerged until mandatory full verification and independent repository review are satisfied. Leave Sentinel, `e156/AGENTS.md` and human `YOUR REWRITE/SUBMITTED` fields untouched.

Scorecard source: [public oversight issue #148](https://github.com/mahmood726-cyber/meta-harness/issues/148).
