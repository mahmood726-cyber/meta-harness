# Complete reviews in RapidMeta tabbed form + external audit pack (pva lane, 8 Oct 2026)

Job (Mahmood, relayed 8 Oct): every topic's complete review at its stable URL with fully transparent tabs, each showing its
provenance; then an external audit pack. Presentation only -- no served number may move.

## What this branch contains (code; the Captain regenerates the served artefacts)
| file | what |
|---|---|
| harness/review_tabs.py (new) | the new tabs and additions, the tab contract checker; every value read from the review object or a named committed registry file |
| harness/page.py | 16 tabs (the 11 required + Overview, Harms, Manuscript, Reporting, Verify); ARIA tablist; arrow / Home / End keys; deep links into tabs; status banner |
| harness/provenance_class.py (new) | the provenance census's served-row rule, shared by gate and page; the record-store lookup is injected (a pinned module never names the store) |
| harness/manuscript.py | forest_for any outcome; count rows in the pooled scale's measure; mixed-measure axis label; k = 1 not called pooled; contrast |
| harness/index.py | Status column (ACTIVE / ABANDONED BY DECISION from registry/g1_abandoned.json); link to the audit pack |
| scripts/build_audit_pack.py (new) | docs/audit/ generator, pre-registered sample (seed 20261008, n 40; committed before the draw); `--check` |
| scripts/review_tab_inventory.py (new) | per topic x tab: COMPLETE / REASONED / PRESENT / MISSING |
| scripts/provenance_census.py | uses the shared rule; output identical to main's census code on the same tree |
| tests/test_review_tabs*.py (new), tests/test_result_change_notice.py | the contract with plants; one regression per codex-found defect, each shown to FAIL on the pre-fix commit |

## Required tabs -> page tabs
Protocol (PICO, dated amendments, decisions in force) | Search (+ identification count, link to the one PRISMA flow) |
Screening | **Included studies** | **Data extraction** | Risk of bias & GRADE (+ D11 status) | **Analysis** |
Results & conclusions (+ the canonical claim object) | Comparison with published meta-analysis (+ /g1/ row) |
**Changes & signatures** | Reproduce (+ one-command replay, bundle or stated reason). **Bold** = new tab.

## Evidence
- **No number moved.** After regeneration, across the 32 review.json files the only changed paths are the certificate's
  code identity (analysis_code_blobs / analysis_code_sha256 / release_sha256 / certificate_scope) and manuscript_sha256
  (31; forest colour and the count-row fix in the primary figure). A control rebuild on main's code moved nothing else.
- **Inventory on the regenerated pages: 352 of 352 cells COMPLETE or REASONED; 0 PRESENT, 0 MISSING.** Reasoned (stated on
  the page with the file looked in): D11 sign-off x32 (decision recorded NOT YET APPLIED); evidence bundle x31 (only glp1
  has one); protocol amendment x21 (none registered); withdrawals/reinstatements (none recorded); iv-iron Analysis and
  Data extraction (every outcome withheld by the gate).
- **Codex (gpt-6-astra, read-only, 5 concurrent), 3 rounds x 7 jobs = 21 recorded calls, 1.81 M tokens**
  (codex_review_tabs/: prompts, outputs, call log with prompt/input/output sha256, span-gate results). Findings 56 / 22 / 9,
  all span-verified. New-tab defects fixed: 10 + 6 + 2; legacy-tab defects handed over (REVIEW_TABS_HANDOVER.md, H1-H19).
- **Accessibility:** every CSS colour pair measured (WCAG AA >= 4.5:1; the forest axis label was 3.35:1, fixed); heading
  order h1 > h2 > h3 > h4; tablist / tab / tabpanel roles, aria-selected, roving tabindex; Arrow / Home / End verified with
  real key presses in a browser; no-JS fallback shows every panel.

## For the Captain
1. Merge the code, then regenerate in a FULL checkout (a sparse checkout without cache/*/snapshots records wrong
   directory listings in registry/build_deps and a false fix-ledger staleness):
   `python scripts/incremental_rebuild.py run` -> `python scripts/generate_replay.py` -> write_index ->
   `python scripts/build_audit_pack.py` -> `python scripts/verify_all.py`.
2. All 32 CERTIFICATE.json are reissued (page.py is in the pinned closure). No served number changes, so no notice.
3. Decisions for Mahmood: H1 (noac primary pool vs D7); whether to build evidence bundles for the other 31 topics
   (PubMed acquisitions, up to ~15 MB each under docs/acquisitions); whether to publish the handover list in the audit pack.
