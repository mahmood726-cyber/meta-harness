# acq/k-gap — STEP 2 report: adapters, measured by counterfactual (2026-09-29)

**Method.** Each adapter is measured before any corpus-moving pin. `scripts/k_gap_counterfactual.py` rebuilds a
topic's review core **in memory** from its pinned cache, adds what the adapter would acquire (records, full text,
registry results), and runs the unchanged screen -> extract -> admission gate. Nothing is written to `cache/` or
`docs/`.

- **Comparability.** The baseline build (no additions) reproduces the served page on **32/32** topics, at VALUE
  level: every pooled estimate/CI and every trial's effect or arm counts. 81 of 87 served trials carry a
  populated value, so the comparison has something to compare.
- **Valid k only.** A gain counts only if the pool it lands in stays valid. `k_valid` is 0 when the pool is
  suppressed (e.g. INCOMPATIBLE estimands). Plant: `tests/test_k_gap.py::test_a_larger_k_in_a_suppressed_pool_is_not_a_gain`.

## Adapter 1 — comparator-member seeding (identification): **+1 valid k of 71**

The report each comparator cited, for its 71 never-identified members, was put through our screener. Per member
trial: **61 screened out**, 7 declared absent (outcome not in abstract), **1 pooled** (sglt2-primary-prevention-hf
PMID 28284707, k 4->5), 2 not fetched. Screen rules: X2 population 26, X1 design 18, X3 comparator 15, X-DESIGN 2.

**Second reader on the 75 excluded records** (18 recorded Codex calls; pilot screening instrument +
`verify_screening`; 75/75 gate-pass): agree with the exclusion **48**, cannot tell from the abstract **23**,
disagree **4**. The 4 are:

- metformin 11238496 and 11821265: X3 comparator wording (`placebo (n = 16) groups`);
- metformin 15302293: X-DESIGN context;
- melatonin 19225268: X2 population ("sleep disorder complaints").

Measured, in memory only: adding bare "placebo" to metformin's comparator wording screens both X3 members in, but
both are then OUTCOME_NOT_IN_SOURCE. It also admits **PMID 18681789 from our existing corpus**, a genotype CC-vs-GG
odds ratio, not metformin vs placebo. The narrow registered wording is load-bearing.

**Reading.** The identification gap is mostly a SCOPE difference: the comparators are broader than our registered
PICO (children, delayed sleep phase, active or add-on comparators, T2D populations). It is not a search miss.

## Adapter 2 — PMC OA full text for declared-absent trials: **+2 valid k**

- 126 declared-absent trials (PMID), 34 with PMC OA full text (via `harness.fetch._pmc_fulltext`, with supplements).
- **On the served extractor** the full-text rung admitted 7, and **3 were wrong**:
  - PMID 32295417: a baseline-characteristics table read as 202/206 vs 193/194 outcome events;
  - PMID 39497860: a baseline age table read as the AAD mean difference;
  - PMID 34541475: a PPI-subgroup RR 0.53 taken as the trial result.
- **Root causes (fixed in the flagged extractor commit, each with a real-text plant that fails pre-fix):**
  1. the TABLES section had no sentence breaks, so it was read as one "sentence";
  2. `<body>` itertext carries every table inline in the "prose";
  3. reported-effect candidates had no subgroup guard, and the source-hierarchy selector preferred the subgroup
     candidate over the refused ITT extraction.
- **After the fix:**
  - valid gains 2: probiotics 39529939 (RR 0.36, 26/282 vs 69/273, primary outcome); omega-3 DO-HEALTH 38199870
    (HR 1.00, factorial main effect — flag for review);
  - right number, wrong measure 2: COCS 36286314 OR, CAP 35723686 OR. Either admission suppresses its RR pool.
    An RR from their counts is an extraction-core decision;
  - wrong: 0.
- **Served values unchanged by the fix: 32/32.** The fix does change the code blobs that each page's
  CERTIFICATE binds, so landing it requires re-certification (the captain's landing step).

## Adapter 3 — CT.gov posted results for declared-absent trials: **+1 valid k**

- 94 declared-absent NCTs not already in our `ctgov_results` cache. 22 have posted results (via
  `harness.fetch._ctgov_results`). No silent loss: every NCT that AACT shows with posted results was returned.
- **On the served rung**, 3 were admitted and **2 were wrong**:
  - EXAMINE 23992602: MACE posted as a PERCENTAGE (11.3 vs 11.8) was read as 11 events of 2701. The measure type
    was computed and never gated on;
  - COLCHICINE-PCI 32295417: "Peri-procedural Myocardial Infarction" was admitted as the major cardiovascular
    COMPOSITE (a component matched a composite keyword).
- **Fix (flagged extractor commit, real-registry plants):** the rung takes a 2x2 only for COUNT_OF_PARTICIPANTS,
  and for a declared composite only from a registry title that is itself a composite (one pattern per clinical
  component, so "Myocardial Infarction (MI)" and "Hospitalization for heart failure (HHF)" each count once).
  A refused rung falls through to the lower rungs.
- After the fix: +1 valid — probiotics Ehrhardt 26973849, 21/246 vs 19/231. Its abstract says "21 and 19 AADs" with
  HR 1.02; the counts give RR 1.03, consistent.

## All adapters together (`counterfactual_all.json`, measured, not summed)

**Summed valid k 81 -> 80.**

- **+4 valid:** probiotics +2 (11->13), omega-3 +1, sglt2-primary-prevention-hf +1.
- **-5:** the two OR admissions suppress two RR pools (colchicine-postop-af 3->0 valid, CAP 2->0 valid).

The adapters must NOT be landed naively. A measure-incompatible admission has to be held out, or converted from
counts (an extraction-core decision), before a pin.

## Tests

- Repo tests over every file that imports the changed modules (42 files + the new ones): **2413 passed, 4 failed,
  68 xfailed.**
- 3 of the 4 are certificate / bundle code-closure bindings (`test_bundle_is_current`,
  `test_pinned_blob_identities_are_what_git_stores`, `test_stdlib_audit_reproduces_every_served_certificate`).
  The certified extractor blobs changed, so these clear at re-certification. **Served values are identical
  32/32.**
- The 4th (`test_certificate_scope_names_its_limits`) was caused by this lane putting `k_gap.py` in `harness/`.
  Fixed by moving it to `kgap/`: measurement tooling stays out of the certified scope.
- The full suite was not completed: two full runs (branch and a `main` worktree) were stopped when C: reached
  0 bytes free. See the disk note below.

## Disk note

C: reached **0 bytes free** at ~02:40. It crashed two counterfactual runs mid-way and blocked a file edit (the
file was checked: intact, all modules parse). This lane freed 2.0 GB by removing its own `main` reference worktree
and stopped its own four pytest processes. Other lanes' processes were not touched. C: stood at 5.8 GB free after.

## Leads recorded, not acted on (outside this lane or needing a decision)

- The abstract extractor accepted a genotype-contrast OR (PMID 18681789) as an effect when screening let it
  through. Screening is currently the only guard.
- Cross-sentence arm counts are not extracted (39497860's real outcome: "31 out of 170 ... developed AAD. In
  contrast, the placebo group had 53 out of 170"). The trial stays declared absent.
- `harness/fetch.py` fetches full text only for `config["fulltext"]` topics, and then for the FIRST 40 records in
  fetch order, not the included trials. Only 3 of 32 topics hold any full text.
- 2 of 32 held comparator texts are a different article (step 1).
