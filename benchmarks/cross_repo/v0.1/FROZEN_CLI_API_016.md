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
- Frozen **accepted RR/ITT input** SHA-256: `514f659d51fd477f702cc25303d45c3a440c5282324de287ba1fab8d30385ce0`, computed with the frozen producer's canonical UTF-8 JSON `wire(produce("ALLOW"))`. The registered REFUSE and MANUAL_REVIEW wire hashes remain separately pinned. A passing two-OS transport comparison now independently checks the pooled ALLOW input bytes against this pre-registered identity, even if both producer archives, consumer-result input hashes and SHA receipts were changed in agreement. This is an input-integrity gate, **not** independent verification of the RR estimate or clinical effects.
- GitHub-hosted Ubuntu 24.04 **and** Windows 2025 as separately labelled runners; Python 3.13.7 and Node 22.14.0 on each. The runner refuses an OS label absent from the frozen registration, refuses a Windows label on Linux, and checks actual Ubuntu distro/version. Windows build attestation comes from GitHub job metadata; a caller-controlled environment variable alone is not trusted evidence.
- E156 and Starter commits recorded but roles explicitly `NOT_EXECUTED`.

The runner archives each exact raw input and outcome, source text, both actual git commits, runtime identities and SHA-256 index. The [Actions workflow](../../../.github/workflows/frozen-cli-api-016.yml) independently recalculates every archived digest, verifies CLI/API equality, checks true `ALLOW` invokes the **real pinned RapidMeta** engine, and checks that `REFUSE`, `MANUAL_REVIEW`, duplicate-member shadows, duplicate trial IDs, mismatched estimands, source SHA drift, malformed inputs and line failures never pool.

A source/trial identity mismatch is deliberately expected to **pass only the generic structural importer** and **fail at the specialised count bridge**, without an engine call. This guards against claiming that a text-span match alone proves a trial's clinical identity.

## Observed Windows integration defect and repair

The first actual two-OS candidate run [#40101381478](https://github.com/mahmood726-cyber/meta-harness/actions/runs/40101381478) had Ubuntu **PASS** but Windows **FAIL** after successfully executing the same 12 CLI/API→RapidMeta scenarios. The independent SHA-receipt verifier rejected the Windows index because Python's `str(Path.relative_to(...))` writes OS-native backslashes, while the archival contract expects portable forward-slash keys such as `inputs/refuse.json`. This was a **real Windows interoperability defect**, not a scientific effect difference. The runner now serialises all receipt paths with `.as_posix()`, with an explicit `PureWindowsPath` regression. Any later CI pass must be verified against the new exact PR head and cannot retroactively change that failed Windows run.

## Independent reproduction

Clone the repositories, check out the **exact** commits above into sibling directories named `meta/` and `rapidmeta/`. Check out the proposal/orchestration branch into `governance/` (the orchestration HEAD is not itself the pinned producer). Ensure exact runtimes. Set the registered runner label to match the actual OS (`ubuntu-24.04` or `windows-2025`). For a local Linux reproduction:

```bash
export BENCHMARK_RUNNER_IMAGE=ubuntu-24.04
python governance/benchmarks/cross_repo/v0.1/frozen_cli_api_handoff_016.py \
  --meta meta --rapidmeta rapidmeta --output handoff-016-evidence
```

To exercise the producer CLI directly:

```bash
(cd meta && python -m harness.exchange_v01 --exchange ../handoff-016-evidence/inputs/refuse.json --archive-root .)
```

This **must fail** for REFUSE. The `allow_rr_itt.json` input must pass raw importer checks; the runner additionally verifies that its real RapidMeta calculation runs. The OS-matrix CI produces **separate Windows and Ubuntu evidence artifacts** and independently verifies the same 12 registered acceptance/refusal expectations on each, including 11 pre-pooling refusals. Those independent behaviour assertions are not a cross-OS byte-for-byte equality claim for floating-point outputs; the later cross-OS archive comparator described below checks transport, refusal provenance and no-pool status only, not numerical equality. The published CI artifacts, if successful, permit independent rehashing; GitHub artifacts have retention limits and are not immutable long-term storage by themselves.

## Coverage and gates

The original historical Meta-Harness pin `a62cbc43416a94561b7bee3ec48bb659ac3286e2` does **not contain** the v0.1 exchange importer or the manifest paths. It is unsuitable for an executed exchange canary without an explicitly versioned re-pin; do not claim those cases can run as written. Original frozen `CROSS-EXCH-001…015` remain **15/15 NOT_RUN** and use a distinct historical Meta-Harness pin predating the exchange code. This runner tests only `CROSS-EXCH-016`; it does not silently update the v0.1 registry or previous frozen source. `CROSS-EXCH-017` and `-018` have separate bounded synthetic execution evidence. Common gate A (4 method-matched pinned R families), B (3 prospective scientific gates), C (2 signed cross-platform full ecosystems), D (2 independent usability/accessibility evaluations) remain **NOT TESTED / BLOCKED** until their own evidence exists.

Full `verify_all`, branch protection, review and merging requirements remain independent. Do not merge merely because this supplemental canary passes. No Sentinel bypass, E156 workbook mutation, human YOUR REWRITE/SUBMITTED alteration, external review, scientific accuracy or statistical effect change is involved.


## Independent comparison of actual Ubuntu and Windows matrix artifacts (draft PR #160)

The original two runner jobs independently rehash 25 input/output/source receipts
and assert expected refusal behavior, but **independent per-OS success does not
prove the raw wire bytes were identical between operating systems**. The
`compare-archived-os-results-016` dependent Actions job downloads **both
actual matrix-job archives from the same workflow execution**, verifies the
exact frozen registration SHA, original archived SHA receipts, source and engine
digests, and checks the 12 actual raw-input SHA values and observed
CLI/API/consumer outcomes for cross-OS agreement. REFUSE and MANUAL_REVIEW
must have `engine_invoked=false` on each OS.

Reproduce the exact comparison using a successful three-job Actions run.
With GitHub CLI access, locate the run's artifact names (the suffix is that
run's `github.sha`, which may be the PR merge-ref SHA, **not** the literal
checked-out candidate source HEAD). Substitute the two exact artifact names
from the *same* run:

```sh
gh run download RUN_ID -n "frozen-cross-exch-016-ubuntu-24.04-GITHUB_EVENT_SHA" -D ubuntu-evidence
gh run download RUN_ID -n "frozen-cross-exch-016-windows-2025-GITHUB_EVENT_SHA" -D windows-evidence
git clone https://github.com/mahmood726-cyber/rapidmeta-kit rapidmeta
git -C rapidmeta checkout --detach 368137dc437543c721b98be39c14282c338f7797
python benchmarks/cross_repo/v0.1/compare_cross_os_016.py \
  --registration benchmarks/cross_repo/v0.1/frozen-cli-api-016.json \
  --ubuntu ubuntu-evidence --windows windows-evidence \
  --rapidmeta rapidmeta \
  --report cross-os-parity-report.json
```

The comparator rejects duplicate raw JSON members, missing/modified SHA
receipts, inconsistent OS declarations, source or engine identity differences,
**and engine receipts that do not equal the separately checked out immutable
RapidMeta git blob, even when both OS artifacts agree**,
unequal archived input bytes and mismatched acceptance/refusal outcomes.
A separate isolated synthetic unit suite intentionally simulates otherwise
internally consistent archives with differing wire inputs, refusal diagnostics
and consumer case identity and verifies this refuses. Those fixtures are **not** real producer/consumer executions; only
the downloaded-artifact dependent job can show actual executed comparison.

The report distinguishes **transport and no-pool parity** from untested
numerical cross-OS equality, R-oracle agreement, prospective discovery,
external adjudication, signed four-repo ecosystem and clinical accuracy.
Original common CROSS-EXCH-001–015 remain **NOT_RUN**. The 32 historical
certificate reproduction gate and repository review rules remain mandatory;
supplemental CI is not approval to merge.


## Fail-closed refusal-provenance parity (subsequent scoped draft)

Every archived case records `api_refusal` from the frozen import/API boundary
and, when refused downstream, `consumer.refusal` and `consumer.case` from
the pinned RapidMeta handoff. Earlier comparison counted only accepted/refused
**statuses** and engine invocation flags. Two operating systems could therefore
report identical refusal statuses yet disagree about *why* they refused, or
silently attach the refusal to a different case ID; both archives could have
internally valid SHA-256 receipts without the discrepancy being noticed.

The cross-OS comparator now requires nonempty refusal reasons on both refusing
boundaries, no refusal reason on accepted/pooled boundaries, the recorded
consumer case ID to match the input scenario, and literal matching refusal
reasons between Ubuntu and Windows. It checks this **after** independently
verifying each archive's raw-file receipts, so falsified diagnostics with
updated digests are also detected. The synthetic regression suite injects
missing/changed reasons and case-ID drift after recomputing archive receipts;
these fixtures demonstrate refusal-gate behaviour, **not** a new public
benchmark execution.

Replay *real* previously archived producer/consumer outputs by downloading
both distinct OS artifacts from [Actions run 40101688905](https://github.com/mahmood726-cyber/meta-harness/actions/runs/40101688905)
and using the comparator command above. The comparison script reports transport
and refusal-provenance agreement; **it does not rerun the producer or assert
numerical R parity**. GitHub's new exact-head CI on this draft must be checked
separately. Retain 15/15 historical cases NOT_RUN, the 32-certificate gate,
and all independent-review/merge requirements unchanged.
