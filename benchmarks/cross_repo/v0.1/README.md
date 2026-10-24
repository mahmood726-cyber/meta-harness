# Cross-repository benchmark v0.1 — research-stage, NOT a validation result

## Scope and custody

This is an **opt-in evidence transport boundary**, not yet wired to Meta-Harness production synthesis or RapidMeta. It checks preserved text source hashes, verbatim passages, unique study IDs, declared trial IDs, typed estimands and explicit blocking decisions. The text verifier now also checks that a verbatim passage occurs at its **claimed 1-based line locator**, not merely somewhere in the archive. Acceptable locators are `line N` and inclusive `lines N-M`; malformed, unsupported PDF-style, out-of-range or forged locators fail closed. This does not validate PDF page/table locations, the quality of extraction, or external adjudication. It cannot independently establish whether a publication is eligible, an estimate is correct, a PDF was parsed accurately, or a clinical answer is safe. Never convert its passing test into a scientific accuracy claim.

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

## New negative case: CROSS-EXCH-006

A SHA-256-matched text source can still carry a fabricated locator. The regression check takes the archived synthetic quote on line 2 and falsely claims it is on line 1: handoff must be refused despite the quotation appearing elsewhere in the document. Multi-line quotes must fall entirely inside their claimed inclusive line range. This is a local structural regression test, **not** a completed benchmark PASS in `manifest.json` or a real clinical source check. Unsupported PDF/page locators remain blocked until a source-aware span checker is independently specified and tested.

## New negative case: CROSS-EXCH-007 — one pooled row per trial identity

An importer could previously accept two `ALLOW` rows with distinct `study_id` values but the same `trial_id`, even though the same trial might be represented in multiple reports or an unadjusted multi-arm comparison. The v0.1 validator now rejects the entire proposed pool as `duplicate trial_id`. It does **not** silently omit one row and does not pretend to solve multi-arm covariance or ambiguous registry aliases. Multiple reports should be reconciled to one study-level estimate upstream; where two comparisons are genuinely independent or a multi-arm adjustment is required, that must be represented through a future explicitly versioned and independently tested contract. No clinical studies are deduplicated here.

This follows the *Cochrane Handbook* principle of linking multiple reports to studies (Chapter 4, sections 4.6.1–4.6.2) and avoiding unit-of-analysis errors in multi-arm trials (Chapters 6 and 23):
https://training.cochrane.org/handbook/current/chapter-04
https://training.cochrane.org/handbook/current/chapter-06
https://training.cochrane.org/handbook/current/chapter-23

The synthetic negative test uses two rows referencing the same archive and trial ID while giving the second row a different study ID. This checks only contract refusal; it **cannot** discover duplicate trials with different identifiers, establish true study identity, or prove statistical correctness. Manifest status remains `NOT_RUN` until pin-matched executable evidence is recorded.
