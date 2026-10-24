# Cross-repository benchmark v0.1 — research-stage, NOT a validation result

## Scope and custody

This is an **opt-in evidence transport boundary**, not yet wired to Meta-Harness production synthesis or RapidMeta. It checks preserved text source hashes, verbatim passages, unique study IDs, declared trial IDs, typed estimands and explicit blocking decisions. The text verifier now also checks that a verbatim passage occurs at its **claimed 1-based line locator**, not merely somewhere in the archive. Acceptable locators are `line N` and inclusive `lines N-M`; malformed, unsupported PDF-style, out-of-range or forged locators fail closed. This does not validate PDF page/table locations, the quality of extraction, or external adjudication. It cannot independently establish whether a publication is eligible, an estimate is correct, a PDF was parsed accurately, or a clinical answer is safe. Never convert its passing test into a scientific accuracy claim.

`manifest.json` pins four source repository commits as inspected on 23 October 2026. The Meta-Harness offline requirements lock is tracked at the pinned commit, with exact Git blob identity. All actual cross-platform installation results, runtime dependency versions, model IDs and external API identities are still **NOT VERIFIED**. Commits are source snapshots, not execution attestations. The synthetic fixture is clearly marked and used only for transport-level regression checks. External scientific and real-system evaluations are recorded separately in `coverage` with no synthetic input substituted for their required source data. `manifest.json` case statuses remain `NOT_RUN` until an identified test is executed against those exact pinned inputs, with exact SHA, job/run link and full success/failure evidence. Never mark a scenario PASS based on a different synthetic test or the existence of this document.

## How to run (from Meta-Harness root)

```sh
python -m pytest tests/test_exchange_v01.py -q
python -m harness.exchange_v01 benchmarks/cross_repo/v0.1/manifest.json
```

The first command tests a small standalone Python transport verifier. The second validates that commit references have the correct 40-hex format and inputs match their SHA-256 digests; it cannot independently prove remote commit existence or lockfile execution. The JSON Schemas are interoperability descriptions; the Python validator is the authoritative executable subset currently tested. The benchmark CLI now reads raw bytes and rejects duplicate JSON members before parsing; consumers of raw manifests must call `validate_manifest_json` rather than `json.loads` followed by `validate_manifest`. Comparing their full acceptance behaviour remains future work. The validator requires plausible structured workflow-run evidence before accepting a recorded PASS, but it does **not** independently fetch Actions or certify the record truthful; spot-checking the job and exact checkout is still required.

## Reference workflows (functional benchmarks, not performance claims)

- Statistical parity: independent, version-matched R `metafor` and Cochrane RevMan output on identical study arms, estimands and model specifications. **NOT TESTED**.
- Screening/recall: ASReview documented simulations (known labelled corpora and held-out retrieval tasks). **NOT TESTED**.
- Review workflow: Cochrane/RevMan, Covidence and DistillerSR are feature references only; no direct comparative runs. **NOT TESTED**.
- Clean Ubuntu and Windows five-component install with Sentinel, Overmind/TruthCert, E156, Meta-Harness and signature failure injection. **NOT TESTED IN THIS BENCHMARK**.
- Prospective unseeded concept retrieval, blinded independent reviewer adjudication, accessibility/usability evaluation. **NOT TESTED**.

Reference docs: https://wviechtb.github.io/metafor/ ; https://documentation.cochrane.org/revman-kb/ ; https://asreview.nl/ ; https://www.covidence.org/ ; https://www.distillersr.com/ . External projects and their licensing must be reviewed before copying any source code. No external code was copied here.

## Ownership

Evidence Integration owns this versioned exchange and test-case identifiers (`CROSS-EXCH-*`). Statistical Parity owns `CROSS-R-*`, Starter Canary CI owns `CROSS-CANARY-*`, Prospective Validation owns `CROSS-DISCOVERY-*` and `CROSS-ADJUDICATION-*`. `CROSS-USABILITY-*` requires external evaluation. These IDs reserve boundaries, not successful tests. Do not change e156 AGENTS.md or human workbook fields. No Sentinel bypasses and no fabricated signed artefacts.

## New negative case: CROSS-EXCH-006

A SHA-256-matched text source can still carry a fabricated locator. The regression check takes the archived synthetic quote on line 2 and falsely claims it is on line 1: handoff must be refused despite the quotation appearing elsewhere in the document. Multi-line quotes must fall entirely inside their claimed inclusive line range. This is a local structural regression test, **not** a completed benchmark PASS in `manifest.json` or a real clinical source check. Unsupported PDF/page locators remain blocked until a source-aware span checker is independently specified and tested.

## New negative case: CROSS-EXCH-007 — one pooled row per trial identity

An importer could previously accept two `ALLOW` rows with distinct `study_id` values but the same `trial_id`, even though the same trial might be represented in multiple reports or an unadjusted multi-arm comparison. The v0.1 validator now rejects the entire proposed pool as `duplicate trial_id`. It does **not** silently omit one row and does not pretend to solve multi-arm covariance or ambiguous registry aliases. Multiple reports should be reconciled to one study-level estimate upstream; where two comparisons are genuinely independent or a multi-arm adjustment is required, that must be represented through a future explicitly versioned and independently tested contract. No clinical studies are deduplicated here.

This follows the *Cochrane Handbook* principle of linking multiple reports to studies (Chapter 4, sections 4.6.1–4.6.2) and avoiding unit-of-analysis errors in multi-arm trials (Chapters 6 and 23):
https://training.cochrane.org/handbook/current/chapter-04
https://training.cochrane.org/handbook/current/chapter-06
https://training.cochrane.org/handbook/current/chapter-23

The synthetic negative test uses two rows referencing the same archive and trial ID while giving the second row a different study ID. This checks only contract refusal; it **cannot** discover duplicate trials with different identifiers, establish true study identity, or prove statistical correctness. Manifest status remains `NOT_RUN` until pin-matched executable evidence is recorded.

## New negative case: CROSS-EXCH-008 — reject whitespace aliases of study/trial IDs

A second synthetic row can bypass exact string-based `trial_id` duplicate checking if its identifier is padded with a leading or trailing space, tab, newline, nonbreaking space, C0/NEL whitespace or a boundary BOM (U+FEFF). The exchange validator now **refuses** any `study_id` or `trial_id` with outer whitespace before checking uniqueness; the JSON Schema constrains the same property. It does not silently trim and pool altered provenance identities. Internal whitespace remains permissible. Different spellings, case variants and registry aliases still require upstream reconciliation, and this check does not establish that reported trials genuinely match.

The regression uses fabricated identifiers solely to exercise the exchange boundary. `CROSS-EXCH-008` remains `NOT_RUN` in the benchmark manifest until pinned executable evidence is independently checked; local fixture testing is not independent clinical validation. No consumer integration or statistical effect computation is changed.

Python and JavaScript differ in their built-in whitespace categories (notably C0/NEL and U+FEFF). The executable helper and JSON Schema explicitly cover their union at the identity boundary. This does not detect all visually confusable IDs, such as zero-width characters, nor authenticate the asserted trial identity.


## New negative case: CROSS-EXCH-009 — reject unversioned transport fields

The published v0.1 JSON Schema forbids additional properties in the exchange
root, proposed pool, individual rows, archived source references and source
spans. The executable Python handoff previously accepted extra properties in
these locations. Different consumers could consequently disagree about whether
an extra pooling override, decision, or provenance field was meaningful. This
change makes the importer reject those fields before authorizing structural
handoff; it does **not** infer or execute any extra instructions.

Five synthetic negative regression scenarios cover those five object boundaries,
with a separate schema-closure assertion. The change is restricted to the
opt-in transport verifier, not production synthesis, statistical calculations
or clinical eligibility. The immutable source fixture and four original
repository source pins are unchanged. CROSS-EXCH-009 is reserved as **NOT_RUN**
until exact pinned-input run evidence is independently verified. The existing
refusals for `REFUSE`, `MANUAL_REVIEW`, `ADJUST`, and `ALLOW_WITH_LABEL`
remain unconditional. Unknown real-world semantic fields require an explicit
future contract version rather than silent acceptance.


## New negative case: CROSS-EXCH-010 — reject duplicate raw JSON object members

At the wire boundary, ordinary Python `json.loads` silently retains the last
value of a duplicate property. A source message containing
`"decision": "REFUSE", "decision": "ALLOW"` would therefore appear to be
an unqualified `ALLOW` row to a consumer that parsed it before enforcing
the transport gate. Duplicated trial identifiers, source hashes, estimand
measures and requested-pool flags can create similarly ambiguous provenance.
Other implementations can interpret duplicates differently.

Raw JSON consumers **must** invoke `validate_exchange_json(raw_bytes,
archive_root)` before any intermediary parser strips duplicate members.
The new entry point requires UTF-8 without a BOM, rejects any repeated decoded
object member (including Unicode-escaped aliases), and then delegates to the
existing v0.1 structural validator. A consumer handed only a previously parsed
Python dictionary cannot reconstruct whether overwritten keys once existed.
There is no claim that downstream repositories already use the new entry point;
such integration requires a separate cross-platform canary.

The added synthetic regression scenarios test last-value-wins ambiguity and
positive unique-member JSON, not clinical evidence. Existing pinned repository
commits and source fixture SHA-256 are unchanged; `CROSS-EXCH-010` remains
`NOT_RUN` pending independently inspected exact-head test evidence.

## New negative case: CROSS-EXCH-011 — pin-bound PASS evidence

The v0.1 manifest previously accepted a plausible PASS record from an
unrelated GitHub repository or an arbitrary 40-hex checkout SHA, despite
advertising exact four-repository source pins. The offline validator now
requires the Actions URL to identify one of the four pinned repositories
under `mahmood726-cyber`, a positive canonical run ID, and a
`commit_sha` identical to that repository's frozen manifest commit.
The existing input SHA-256 equality check remains mandatory.

Six synthetic negative instances exercise wrong ownership, unpinned repo,
invalid run ID, URL query appendage, unrelated commit, and another pinned
repository's SHA. One structurally consistent synthetic PASS object is
accepted *inside tests only* to avoid vacuous rejection. It is deliberately
fictional and never recorded as a real benchmark PASS: the manifest still
marks CROSS-EXCH-011 `NOT_RUN`, and no external accuracy or real
four-repository canary is claimed.

**Limit:** the validator does not call the GitHub API to verify that an
Actions run exists, checked out the claimed SHA, ran the named tests or
passed. That requires an independently inspected job and artifact chain.
Do not promote a case based on this offline check alone; all five
external-coverage categories remain untested.



## New negative case: CROSS-EXCH-012 — preserve the benchmark case registry

The offline manifest verifier previously accepted a shortened `cases` array
(or a case renamed to a different lane's ID) as long as the remaining records
had unique IDs and valid fixture SHA-256 values. This allowed a benchmark to
silently lose its earlier refusal and source-integrity scenarios while still
producing a successful structural manifest check.

The v0.1 manifest now registers `CROSS-EXCH-012`. The Python validator requires
all transport IDs `CROSS-EXCH-001` through `CROSS-EXCH-012`, rejects cross-lane
names, and requires any future three-digit `CROSS-EXCH-*` additions to be
gap-free. The JSON Schema declares a 12-case floor and the matching namespace;
the Python validator remains authoritative for cross-record completeness.
Case ordering is not significant.

Negative tests remove early, middle and latest IDs; substitute `CROSS-R-012`;
and rename the last case to create a gap. A synthetic, contiguous future ID
is accepted as a structure-only control. **No individual benchmark scenario
has been executed against the four frozen source pins by these tests.**
All entries remain `NOT_RUN`; neither CI success on this patch nor these
fixture tests demonstrate R parity, live discovery, human adjudication, or
full-system interoperability.


## New negative case: CROSS-EXCH-013 — manifest/schema provenance parity

The JSON Schema already forbids extra manifest fields and requires descriptions,
benchmark purpose and dependency-identity declarations. The executable manifest
validator previously accepted unversioned extra keys at the manifest root,
individual repository pins, cases and external-coverage entries, and omitted
some mandatory provenance fields. A different consumer could interpret a forged
field (for example an extra gate override) while the Python verifier reported
successful structural validation. An invalid optional dependency-lock blob was
also accepted by the Python code despite its schema pattern.

The validator now refuses unknown fields at these four boundaries and requires
the declared purpose, case descriptions and dependency identities. An optional
lock blob, if declared, must have canonical 40-character lowercase Git-blob
syntax. A non-object coverage record yields an explicit refusal instead of an
uncaught attribute error. Existing four Git commit pins, source SHA-256 and
scientific outcomes are unchanged. This checks schema shape only: it does not
resolve Git blobs, install dependencies, verify remote Actions jobs, execute
R, or run a cross-repository consumer.

Fifteen synthetic negative/positive test instances were added to guard the
contract. **CROSS-EXCH-013 remains NOT_RUN** until independently reviewed,
exact-pinned benchmark-case execution is recorded; repository pytest is not a
four-repository benchmark or external scientific validation.


## New negative case: CROSS-EXCH-014 — status-bound run evidence

The v0.1 manifest accepted a case changed from `NOT_RUN` to `FAIL` without
any execution record. It also accepted `run_evidence` attached to a
`NOT_RUN` or `BLOCKED` case, allowing contradictory public state.
This is an audit-status integrity defect, not a statistical-engine issue.

`validate_manifest` now requires complete, source-pin-matched
`run_evidence` for **both** `PASS` and `FAIL`, and refuses any
`run_evidence` on `NOT_RUN` or `BLOCKED`. Unknown run-evidence fields
and non-string case statuses are rejected. The published v0.1 JSON Schema
states the same conditional contract. Coverage of external research disciplines
remains separately `NOT_RUN` or `BLOCKED`.

The recorded run evidence is checked **only for structural consistency** with
the declared commit and input SHA-256. The offline validator **does not**
retrieve GitHub's actual run conclusion, checkout, steps or artifacts; an
invented but well-formed URL could still pass this structural check.
Consequently a reviewer must independently inspect exact-head GitHub Actions
before interpreting a `FAIL` or `PASS` as an observed benchmark result.
The synthetic positive and negative tests are not a real benchmark run.
**CROSS-EXCH-014 remains `NOT_RUN`**, and all prior case IDs, frozen
repository commit pins, archived source bytes and coverage claims are unchanged.


## New negative case: CROSS-EXCH-015 — refuse shadowed manifest JSON keys

The previous CLI used ordinary json.loads when reading a benchmark manifest.
For raw JSON containing duplicate object keys, Python silently retains only
the last member. For example, a case with a first status FAIL followed by a
second status NOT_RUN would look unexecuted after parsing, concealing the
contradictory failure state. Earlier duplicate commit, input SHA-256, case ID
or benchmark version members could likewise disappear before structural checks.

The CLI now calls validate_manifest_json(raw_bytes, manifest_dir), which
rejects duplicate decoded object members at **every nesting level**, including
Unicode-escaped duplicate names. Non-UTF-8, UTF-8 BOM and malformed JSON are
also rejected. The existing validate_manifest continues to validate already
decoded objects, but callers using it are responsible for proving their own
JSON parser has not discarded members. This input-integrity issue is not
expressible by JSON Schema alone.

Regression tests demonstrate the old last-key-wins ambiguity, exercise
status, commit, case identity and hash shadows, malformed encodings, the
positive fixture, and actual CLI refusal. They do not execute the four pinned
repositories. All 15 transport cases, including CROSS-EXCH-015, remain
**NOT_RUN** until independently checkable benchmark-case execution is recorded.
The immutable synthetic fixture hash and four repository commit/dependency
identities remain unchanged. No independent human review, R oracle, prospective
discovery, real consumer integration, or usability test is claimed.


## CROSS-EXCH-016 — independently replay archived MANUAL_REVIEW through frozen source

The integration-owned CI benchmark is **synthetic and two-repository only**.
The separate producer jobs execute 12 registered wire cases on Ubuntu 24.04
and Windows 2025 and upload all raw inputs, outputs and SHA-256 receipts.
The comparison job downloads **those jobs' artifacts**, verifies the complete
12-case cross-OS refusal/identity matrix, and now re-executes the archived
`manual_review` raw input from **each** OS through the frozen Meta-Harness
importer (`ea2fac35a212a330dfe27f7b710347e9ef69a12a`). It also checks
out the pinned RapidMeta source
(`368137dc437543c721b98be39c14282c338f7797`) and checks the
archived engine-file SHA-256 against the actual pinned file. A subprocess
tripwire proves no engine subprocess is invoked on these replayed refusals.
The independently observed refusal string must match each archived result.
If either OS disagrees, CI fails, even if archive receipts were recomputed.

**Refusal replay extension:** the independent comparator now re-executes *both*\nregistered `refuse` and `manual_review` wire inputs from each OS (four frozen\nimporter calls), checks the exact case identities and recorded refusal reasons,\nand rejects every unexpected engine invocation. This is still a synthetic\ntwo-repository check, not a four-repository public benchmark PASS.\n\nWith the frozen source and consumer checked out locally, and the two actual
Actions job artifacts unzipped under `frozen-artifacts/`, reproduce with:

```sh
python benchmarks/cross_repo/v0.1/compare_cross_os_016.py \
  --registration benchmarks/cross_repo/v0.1/frozen-cli-api-016.json \
  --ubuntu frozen-artifacts/ubuntu-24.04 \
  --windows frozen-artifacts/windows-2025 \
  --report parity-report/cross-os-016.json
python benchmarks/cross_repo/v0.1/replay_archived_refusal_016.py \
  --registration benchmarks/cross_repo/v0.1/frozen-cli-api-016.json \
  --ubuntu frozen-artifacts/ubuntu-24.04 \
  --windows frozen-artifacts/windows-2025 \
  --meta meta --rapidmeta rapidmeta \
  --report parity-report/frozen-manual-review-replay-016.json
```

Use **Python 3.13.7 and Node 22.14.0**, and inspect GitHub job metadata and
artifact identity; local replays alone cannot attest the original Windows
runner. The replay report records frozen checkout SHAs, archived/replayed raw
SHA-256s and refusal outcomes. All original common CROSS-EXCH-001–015
remain `NOT_RUN` against their different frozen pins. This additional
`CROSS-EXCH-016` subcheck neither uses clinical trial data nor establishes
independent R parity, prospective discovery, human adjudication, four-repo
signed canaries or numerical equivalence. No merge is authorised by this
isolated workflow while the full certificate and review gates are failing.
