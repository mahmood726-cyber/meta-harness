# Cross-repository benchmark v0.1 — research-stage, NOT a validation result

## Scope and custody

This is an **opt-in evidence transport boundary**, not yet wired to Meta-Harness production synthesis or RapidMeta. It checks preserved text source hashes, verbatim passages, unique study IDs, declared trial IDs, typed estimands and explicit blocking decisions. It cannot independently establish whether a publication is eligible, an estimate is correct, a PDF was parsed accurately, or a clinical answer is safe. Never convert its passing test into a scientific accuracy claim.

`manifest.json` pins four source repository commits as inspected on 23 October 2026. The Meta-Harness offline requirements lock is tracked at the pinned commit, with exact Git blob identity. All actual cross-platform installation results, runtime dependency versions, model IDs and external API identities are still **NOT VERIFIED**. Commits are source snapshots, not execution attestations. The synthetic fixture is clearly marked and used only for transport-level regression checks. External scientific and real-system evaluations are recorded separately in `coverage` with no synthetic input substituted for their required source data. `manifest.json` case statuses remain `NOT_RUN` until an identified test is executed against those exact pinned inputs, with exact SHA, job/run link and full success/failure evidence. Never mark a scenario PASS based on a different synthetic test or the existence of this document.

## How to run (from Meta-Harness root)

```sh
python -m pytest tests/test_exchange_v01.py -q
python -m harness.exchange_v01 benchmarks/cross_repo/v0.1/manifest.json
```

The first command tests a small standalone Python transport verifier. The second validates that commit references have the correct 40-hex format and inputs match their SHA-256 digests; it cannot independently prove remote commit existence or lockfile execution. The JSON Schemas are interoperability descriptions; the Python validator is the authoritative executable subset currently tested. Comparing their full acceptance behaviour remains future work. The validator requires plausible structured workflow-run evidence before accepting a recorded PASS, but it does **not** independently fetch Actions or certify the record truthful; spot-checking the job and exact checkout is still required.

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
