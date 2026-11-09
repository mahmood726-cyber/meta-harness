# Cross-repository benchmark v0.1 — research-stage, NOT a validation result

## Scope and custody

This is an **opt-in evidence transport boundary**. A separate synthetic canary can hand validated fixture counts to pinned RapidMeta; Meta-Harness production synthesis does not use this adapter. It checks preserved text source hashes, verbatim passages, unique study IDs, declared trial IDs, typed estimands and explicit blocking decisions. It cannot independently establish whether a publication is eligible, an estimate is correct, a PDF was parsed accurately, or a clinical answer is safe. Never convert its passing test into a scientific accuracy claim.

`manifest.json` pins four source repository commits as inspected on 23 October 2026. The Meta-Harness offline requirements lock is tracked at the pinned commit, with exact Git blob identity. All actual cross-platform installation results, runtime dependency versions, model IDs and external API identities are still **NOT VERIFIED**. Commits are source snapshots, not execution attestations. The synthetic fixture is clearly marked and used only for transport-level regression checks. External scientific and real-system evaluations are recorded separately in `coverage` with no synthetic input substituted for their required source data. `manifest.json` case statuses remain `NOT_RUN` until an identified test is executed against those exact pinned inputs, with exact SHA, job/run link and full success/failure evidence. Never mark a scenario PASS based on a different synthetic test or the existence of this document.

## How to run (from Meta-Harness root)

```sh
python -m pytest tests/test_exchange_v01.py -q
python -m harness.exchange_v01 benchmarks/cross_repo/v0.1/manifest.json
```

The first command tests a small standalone Python transport verifier. The second validates repository pins, fixture digests, the complete case list and status-bound execution records; it cannot independently prove remote commit existence or lockfile execution. The JSON Schemas describe interoperability constraints; Python additionally checks source bytes, line locations, uniqueness, complete case IDs and cross-record pin equality. Full acceptance equivalence is not claimed. Both PASS and FAIL require structured workflow-run evidence tied to the named repository's manifest commit and case input digest. The validator does **not** fetch Actions or certify the record truthful; spot-checking the job and exact checkout is still required.

## Reference workflows (functional benchmarks, not performance claims)

- Statistical parity: independent, version-matched R `metafor` and Cochrane RevMan output on identical study arms, estimands and model specifications. **NOT TESTED**.
- Screening/recall: ASReview documented simulations (known labelled corpora and held-out retrieval tasks). **NOT TESTED**.
- Review workflow: Cochrane/RevMan, Covidence and DistillerSR are feature references only; no direct comparative runs. **NOT TESTED**.
- Clean Ubuntu and Windows five-component install with Sentinel, Overmind/TruthCert, E156, Meta-Harness and signature failure injection. **NOT TESTED IN THIS BENCHMARK**.
- Prospective unseeded concept retrieval, blinded independent reviewer adjudication, accessibility/usability evaluation. **NOT TESTED**.

Reference docs: https://wviechtb.github.io/metafor/ ; https://documentation.cochrane.org/revman-kb/ ; https://asreview.nl/ ; https://www.covidence.org/ ; https://www.distillersr.com/ . External projects and their licensing must be reviewed before copying any source code. No external code was copied here.

## Ownership

Evidence Integration owns this versioned exchange and test-case identifiers (`CROSS-EXCH-*`). Statistical Parity owns `CROSS-R-*`, Starter Canary CI owns `CROSS-CANARY-*`, Prospective Validation owns `CROSS-DISCOVERY-*` and `CROSS-ADJUDICATION-*`. `CROSS-USABILITY-*` requires external evaluation. These IDs reserve boundaries, not successful tests. Do not change e156 AGENTS.md or human workbook fields. No Sentinel bypasses and no fabricated signed artefacts.

## Raw-JSON importer parity and duplicate-key custody

The **actual** `python -m harness.exchange_v01 manifest.json` entrypoint reads
raw UTF-8 bytes through the strict pre-parser; a matching Python API is
`from harness.exchange_v01.wire import validate_manifest_json, validate_exchange_json`.
Pass the original **raw bytes**, not a previously decoded `dict`. Standard
`json.loads` silently keeps the last repeated object member, including an
earlier `FAIL` status, `REFUSE` decision, source/trial ID or estimand. JSON Schema
cannot detect duplicates after parsing. The strict importer rejects repeated
keys at any nesting depth (including Unicode-escaped keys), malformed JSON,
BOM/invalid UTF-8 and nonstandard numeric constants before normal v0.1
structural checks. The optional package remains outside the historical certificate code scope;
its importable `main()` compatibility entrypoint also delegates to strict `wire.py`.
No historical certificate, release or served-page bytes are rewritten.

```sh
python -m pytest tests/test_exchange_v01_wire.py -q
python -m harness.exchange_v01 benchmarks/cross_repo/v0.1/manifest.json
```

These are **synthetic parser/refusal regressions only**, not completed
CROSS-EXCH-001..015 pinned producer→consumer executions, R-oracle parity,
signed cross-repository canaries or independently adjudicated science.

## Stacked validator contracts

The current package retains its existing duplicate-trial check and strict raw
JSON parser. The remaining contracts are enforced at both parsed-object and
raw-JSON entrypoints:

- `CROSS-EXCH-006`: a quotation must fit the claimed `line N` or inclusive
  `lines N-M` range in the pinned UTF-8 text. Forged, malformed, reversed,
  unsupported PDF-style and out-of-range locators refuse handoff.
- `CROSS-EXCH-007` / `008`: one row per trial identity, with no outer whitespace
  in either study or trial IDs. Python and schema patterns include C0/NEL
  whitespace and BOM. IDs are never silently trimmed; internal spaces remain
  allowed. Different registry aliases still require upstream reconciliation.
- `CROSS-EXCH-009` / `010`: unknown exchange fields and duplicate raw JSON
  members refuse handoff. Estimand objects retain their existing exact-key gate.
- `CROSS-EXCH-011`: execution URLs must name one of the four pinned repositories
  under `mahmood726-cyber`, have a canonical positive run ID, and match that
  repository's frozen commit. The case input SHA-256 must also match.
- `CROSS-EXCH-012`: all case IDs `001` through `015` are required in the
  `CROSS-EXCH` namespace. Future three-digit additions must be contiguous;
  ordering does not matter. Schema declares the namespace and minimum count;
  Python enforces the complete set.
- `CROSS-EXCH-013`: root, repository, case and coverage objects reject unknown
  fields. Purpose, dependency identity and case description are required;
  optional dependency-lock blob identities must be lowercase 40-hex strings.
- `CROSS-EXCH-014`: both PASS and FAIL require complete, closed execution
  evidence. NOT_RUN and BLOCKED must omit `run_evidence`, including empty or null
  values. Malformed status and coverage values raise validation errors.
- `CROSS-EXCH-015`: the raw manifest boundary rejects duplicate decoded members
  before status, pin, case identity or source-digest validation. The parser was
  already present on main; this port registers the case and raises the required
  contiguous case count to 15. Every case remains `NOT_RUN`.

The added manifest rows preserve the original source fixture, four repository
pins and external coverage entries. Every case remains `NOT_RUN`. The fictional
PASS/FAIL records in tests are local structural controls, never benchmark results.

The regressions are `tests/test_exchange_v01_validators.py` and
`tests/test_exchange_v01_schema.py`. The schema suite
uses the test-only `jsonschema` package (Draft 2020-12); without it that suite is
explicitly skipped. Runtime validation adds no dependency.

## Synthetic handoff runners and archived refusal replay

The current raw importer is
`from harness.exchange_v01.wire import import_exchange_json`. It returns the
validated object after the same strict decoding and validation used by
`validate_exchange_json`; the compatibility verifier still returns `None`.
`harness.exchange_v01.import_exchange_json` delegates to that implementation.
No second exchange parser is introduced. The CLI accepts either the existing
manifest argument or this evidence mode:

```sh
python -m harness.exchange_v01 --exchange raw-exchange.json --archive-root archive
```

The CLI validates raw evidence and never pools. The
[candidate handoff canary](PINNED_HANDOFF_CANARY.md) alone converts the two
committed synthetic source lines into binary arms. It checks source/trial
identity before invoking the pinned engine and checks the engine's worktree
bytes against its committed Git blob. Linked engine paths refuse handoff.

Three separate frozen registrations retain their original repository commits,
source hashes, runtime versions and `NOT_RUN` registration statuses:

- [016: CLI/API handoff](FROZEN_CLI_API_016.md) defines 12 wire scenarios on
  Ubuntu 24.04 and Windows 2025, with one synthetic engine control and 11
  refusals. `frozen_cli_api_handoff_016.py` archives portable POSIX receipt keys.
- [017: frozen producer/consumer handoff](FROZEN_HANDOFF_017.md) executes the
  historical producer with one synthetic control and five refusals.
- [018: frozen estimand handoff](FROZEN_ESTIMAND_018.md) exercises an RR control
  and an OR-versus-RR refusal through `frozen_estimator_handoff_018.py`.

`compare_cross_os_016.py` verifies archived input/result receipts, case labels,
refusal diagnostics, JSON Boolean engine flags and independent engine custody.
It binds registered positive and negative wires to their frozen hashes, refuses
symlink/junction/traversal aliases and unsupported clinical-status promotion,
and compares finite synthetic `mu_log` and nonnegative `tau2` with the unchanged
`rel_tol=1e-12`, `abs_tol=1e-12` tolerances.

`replay_archived_refusal_016.py` independently replays six archived cases from
each OS: `refuse`, `manual_review`, `source_trial_mismatch`, `duplicate_shadow`,
`estimand_mismatch`, and `source_sha_tamper`. It rechecks input, result and index
custody after comparison, verifies producer/importer Git blobs, and installs
process-launch tripwires before importing the frozen consumer. The source/trial
case intentionally passes the generic importer and refuses at the synthetic
count bridge. Exact refusal provenance must match the archived record.

The workflows and reproduction instructions require real pinned checkouts,
Python 3.13.7, Node 22.14.0, and actual downloaded OS artifacts. They are retained
for CI, **not executed or attested by this port**. Synthetic fixture tests do not
establish cross-OS execution, independent R parity, clinical accuracy, human
adjudication or a signed four-repository benchmark. See [port and test
boundaries](PORTING_NOTES.md) for local verification limits.
