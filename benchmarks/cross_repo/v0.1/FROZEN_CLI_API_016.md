# CROSS-EXCH-016 — frozen raw JSON CLI/API parity and no-pool handoff

**Status: proposed draft; execution evidence must be checked in GitHub Actions.** This is a *synthetic-only*, **two-repository** version-pinned transport/consumer test. It is **not** an R oracle, clinical accuracy assessment, four-repository canary or independent adjudication. It implements the [LEARN-20261024-ASREVIEW-001 proposed parity practice](https://github.com/mahmood726-cyber/meta-harness/issues/148) without copying ASReview source code.

## Defect and scope

The v0.1 interchange exposed an in-process `validate_exchange_json` verifier but did not expose an equivalent raw evidence **CLI importer**, while the pinned synthetic RapidMeta bridge separately parsed already-validated wire JSON. A user could mistakenly import pre-decoded objects after duplicate members were discarded. This PR defines **one strict raw importer** (`import_exchange_json`) used by the CLI, compatibility verifier, and bounded real RapidMeta consumer. JSON Schema cannot reject duplicated raw object members: checking after ordinary `json.loads` is too late.

The imported object is *structurally* validated against source hash, line-quoted spans, trial uniqueness, refusal and estimand contracts. This does **not** independently decide trial eligibility. The specialised synthetic count bridge separately checks trial ID against the frozen source-line grammar; the general text validator cannot infer that identity from arbitrary prose.

## Frozen input and execution

The [registration](frozen-cli-api-016.json) fixes:

- Meta-Harness **source code**: `ea2fac35a212a330dfe27f7b710347e9ef69a12a`.
- RapidMeta **real JS pooling consumer**: `368137dc437543c721b98be39c14282c338f7797`.
- Synthetic text source SHA-256: `666a0354b2668dd0f90780becff303eab28a007fa895650ba09793732d374398`.
- Ubuntu 24.04, Python 3.13.7, Node 22.14.0.
- E156 and Starter commits recorded but roles explicitly `NOT_EXECUTED`.

The runner archives each exact raw input and outcome, source text, both actual git commits, runtime identities and SHA-256 index. The [Actions workflow](../../../.github/workflows/frozen-cli-api-016.yml) independently recalculates every archived digest, verifies CLI/API equality, checks true `ALLOW` invokes the **real pinned RapidMeta** engine, and checks that `REFUSE`, `MANUAL_REVIEW`, duplicate-member shadows, duplicate trial IDs, mismatched estimands, source SHA drift, malformed inputs and line failures never pool.

A source/trial identity mismatch is deliberately expected to **pass only the generic structural importer** and **fail at the specialised count bridge**, without an engine call. This guards against claiming that a text-span match alone proves a trial's clinical identity.

## Independent reproduction

Clone the repositories, check out the **exact** commits above into sibling directories named `meta/` and `rapidmeta/`. Check out the proposal/orchestration branch into `governance/` (the orchestration HEAD is not itself the pinned producer). Ensure exact runtimes. Then:

```bash
python governance/benchmarks/cross_repo/v0.1/frozen_cli_api_handoff_016.py \
  --meta meta --rapidmeta rapidmeta --output handoff-016-evidence
```

To exercise the producer CLI directly:

```bash
(cd meta && python -m harness.exchange_v01 --exchange ../handoff-016-evidence/inputs/refuse.json --archive-root .)
```

This **must fail** for REFUSE. The `allow_rr_itt.json` input must pass raw importer checks; the runner additionally verifies that its real RapidMeta calculation runs. The published CI artifact, if successful, permits byte-for-byte independent rehashing; GitHub artifacts have retention limits and are not immutable long-term storage by themselves.

## Coverage and gates

Original frozen `CROSS-EXCH-001…015` remain **15/15 NOT_RUN** and use a distinct historical Meta-Harness pin predating the exchange code. This runner tests only `CROSS-EXCH-016`; it does not silently update the v0.1 registry or previous frozen source. `CROSS-EXCH-017` and `-018` have separate bounded synthetic execution evidence. Common gate A (4 method-matched pinned R families), B (3 prospective scientific gates), C (2 signed cross-platform full ecosystems), D (2 independent usability/accessibility evaluations) remain **NOT TESTED / BLOCKED** until their own evidence exists.

Full `verify_all`, branch protection, review and merging requirements remain independent. Do not merge merely because this supplemental canary passes. No Sentinel bypass, E156 workbook mutation, human YOUR REWRITE/SUBMITTED alteration, external review, scientific accuracy or statistical effect change is involved.
