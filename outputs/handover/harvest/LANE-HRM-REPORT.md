# LANE HRM — served harms and adjustment corrections

Status: requested corrections and verification measurements complete; no commit. See the full gate verdict below.
No commit, push or deployment was performed. Builds and verification used held caches with Python remote socket connections blocked; browser page routes were limited to localhost.

## Scope and base

`git rev-parse HEAD` = `3cf73885ffc83f6fcc4db273c6510a5416cdcde0`, the requested base.
Local `origin/main` and its merge-base with HEAD are instead
`2304824034b4ba8677da2d2d2453352711ed2a9b`. No fetch was performed. The explicit
lane comparisons use the requested `3cf73885…`; `verify_all` retains its configured
older ratchet base and block-floor refs.
Initial worktree contained only the supplied lane prompt and lane runtime files.
Membership code and `harness/synth.py` are untouched. Changes to `harness/gate.py`
add only the two requested checks and their registration in `gate_page`.

## MEASURED

- Planted regressions were run before implementation: three failures. The base rendered
  a numerical harm result with a reporting-trial refusal, assigned `PUBLISHED_UNADJUSTED`
  without adjustment evidence, and lacked the new gate checks.
- The focused post-fix suite passed: **55 tests** (HRM plants, harms recovery, design key,
  page rendering, limitations and earlier HM contract tests updated for refusal-as-debt). The plants use explicitly synthetic inputs only in tests.
- **32 of 32 topics rebuilt**, using held caches with socket connections prohibited.
- Empty `AACT_DIR` reproduction: **32/32**; the final full verification also runs with this empty directory.
- Retraction survival against the exact base: **32 of 32**.
- **46 harm outcomes suppressed of 61**, affecting **27 of 32 pages**.
  This counts all incomplete outcome blocks, including ones already lacking a renderable result.
  **20 previously renderable numerical harm blocks on 16 pages** now lose their numerical synthesis;
  the other incomplete blocks gain or retain the explicit suppression ledger.
- Adjustment sweep: **95 rows relabelled UNRESOLVED of 95** published per-outcome trial rows;
  **0 with a span-backed status of 95**. This denominator excludes reconstructed estimates.
- The new checks reject the base's harms surfaces on **27 pages** and legacy adjustment
  labels on **28 pages**; both checks accept all **32 rebuilt pages**.
- The second pass compares every outcome against the base: contributing trial IDs,
  declared-absent IDs and refusal codes, and computed k/estimate/CI/tau²/scale are unchanged.
  Suppression changes what is served and what the canonical claim permits, not membership
  or the statistical calculation.

Evidence: [second-pass audit](outputs/hrm/second-pass-audit.json),
[adjustment sweep](docs/adjustment_label_sweep.json),
[harms sweep](docs/harms_recovery_sweep.json),
[build log](outputs/hrm/build.txt),
[empty-AACT reproduction](outputs/hrm/reproduce-empty-aact.txt),
[retraction survival](outputs/hrm/retraction.txt).

The previously stored harms sweep was stale (47 outcomes). The denominator of 61 above
is measured from the rebuilt 32 review objects; it is not copied from that old sweep.

## Implemented rules

An incomplete harm block renders **HARMS EXTRACTION INCOMPLETE — no class-level quantitative
safety conclusion issued** before its reporting-trial ledger. Typed refusals remain extraction
debt. Missing extraction spans also block synthesis. The ledger retains extracted rows, refusal
codes, reasons, spans and source-ladder obligations. Named adjudication documents are checked
for their held spans; unverified routes remain explicitly open. Complete harm panels retain
their ledger too. Individual source quotations and extracted trial inputs remain inspectable.
No pooled estimate, pooled interval, sensitivity pool, prediction interval, heterogeneity or
other quantitative synthesis is served by an incomplete harm block.

The canonical harm claim is also suppressed. This avoids treating a source quotation in the
ledger as a class-level pooled significance assertion. During integration, the old claim checker
otherwise rejected a ledger quotation because its source-level significance differed from the
unserved pooled result; this was fixed in the claim state, without weakening the checker.

Published estimator labels identify their scale (`PUBLISHED_HR`, `PUBLISHED_RR`, etc.). Adjustment
status is a separate typed axis. A resolved status requires a source, exact span and matching
start/end location in the selected source or a held repository document. Arbitrary occurrences
of `adjust`, including `unadjusted` and unrelated dose adjustment, do not assign a status.

## ELIXA source check

The held FDA statistical review, `outputs/handover/glp1_reviewerB/sources/FDA_NDA208471_StatR.txt`,
states on page 8 that the primary time-to-event Cox model uses treatment and region as factors.
The second-pass audit records the exact span, character offsets, document SHA-256, and the
matching held PubMed record (PMID 26630143). This supports an **ADJUSTED** status for that
primary MACE+ model. There is **no selected ELIXA estimate row** in any of the 32 review objects.
The current GLP-1 target is 3-point MACE; its ELIXA primary row is declared absent. That membership
and its reason code were preserved. No status was transferred from MACE+ to a different endpoint.

## Full verification

Command: `python scripts/verify_all.py`, with empty `AACT_DIR` and the offline socket guard.
All eleven result rows below are pasted from the final run, without omitting refusals.

```text
  [             PASS] unit tests (pytest tests/)  (389s)
  [             PASS] offline reproduction (every live page replays from committed cache)  (62s)
  [          REFUSED] publication gate on every live review page  (58s)
  [             PASS] index currency (generated == committed docs/index.html)  (2s)
  [             PASS] served-artefact leak scan (docs/*.json)  (0s)
  [             PASS] held-out leak detector (registry/heldout_sealed.json)  (309s)
  [             PASS] search completeness (search_v2 measurement current; every state explicit; no zero from an exit code)  (3s)
  [             PASS] fix-state discipline (registry/fixes.json)  (85s)
  [          REFUSED] honest-state ratchet (no page may get quieter)  (14s)
  [             PASS] gate scorecard (every gate accounted for)  (1s)
  [             PASS] gate gaps table (sealed what-it-would-not-stop rows)  (6s)
VERIFY-ALL: REFUSED -- 2 of 11 limbs not PASS. Fix the harness, never the gate.
```

Full output: [final verification log](outputs/hrm/verify-all-complete.txt).
Browser contract: [all 32 harm panels](outputs/hrm/ui-final.txt) — PASS.

The unchanged legacy `check_harms_complete` still refuses unresolved extraction debt even when the numerical surface is suppressed. The new `check_harms_synthesis_gated` accepts the suppressed ledger. The honest-state ratchet also refuses changed harm blocks; no acknowledgement, baseline reset, or gate bypass was introduced. Remaining refusals are recorded in `STUCK_FAILURES.md`.

Integration maintenance: updated four older tests that wrongly treated typed refusals as extraction completion; registered the two checks with no invented adjudication events; regenerated the fix ledger, gate scorecard and index. The first full run and its superseded failures remain in [the initial log](outputs/hrm/verify-all.txt). The second run reached 920 passing tests but the HTTP browser test saw zero gated blocks where the local file had two; [that run](outputs/hrm/verify-all-final.txt) is retained. The final static-page browser contract supplies the exact generated HTML bytes through a Playwright route at the absolute loopback URL, blocking all other requests. It tests DOM visibility, every reporting row, numerical suppression, estimator labels and JavaScript errors; it does not certify a deployment or a shared HTTP server. A shared-port checkout mismatch is an inference from the divergent DOM and passing exact-file test, not a separately proven diagnosis.

## Static versus dynamic disclosure

| Component | Static configuration | Dynamic evidence / transformation |
|---|---|---|
| Harms rule | Requested suppression message; existing refusal ontology | Reporting rows, source spans, extraction debt and page counts read from rebuilt objects |
| Adjustment rule | `ADJUSTED`, `UNADJUSTED`, `UNRESOLVED`; published-scale prefix | Located typed axes validated against source text; corpus labels measured by sweep |
| Statistics | No added research constants or effect estimates | Existing pipeline calculations preserved and compared with the base |
| ELIXA audit | Source-document identity and endpoint-specific review | Span, offsets, SHA-256 and selected-row absence measured from held files |
| Regression plants | Explicitly synthetic test fixtures | Base failures and post-fix gate refusals executed locally |

## INFERRED / CLAIMED

**INFERRED:** withholding synthesis while any reporting trial remains unresolved prevents a
partial harms extraction from being presented as a class-level quantitative safety conclusion.
It does not establish that the harms evidence is complete, or establish safety.

**CLAIMED:** only the implementation and measured coverage above. No release certification,
complete literature search, recovered missing harm estimates, new trial membership, or clinical
safety conclusion is claimed. The full publication gate remains refused for extraction debt, and
the honest-state ratchet remains refused for changed blocks.
