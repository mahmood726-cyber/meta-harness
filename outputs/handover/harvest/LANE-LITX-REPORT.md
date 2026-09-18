# LANE LITX report

**READY-BEHIND-CHK for the owned source changes and prepared CHK patches. The working tree remains REFUSED, including additional defects outside this lane’s write ownership. No commit, checkout, reset, stash, push or network.**

MEASURED HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. Focused tests: **20 passed in 80.74s (0:01:20)**. Full-suite summary: **16 failed, 978 passed, 4 warnings in 1071.15s (0:17:51)**.

## Static versus dynamic disclosure

| Component | Static / authored | Dynamic / measured |
|---|---|---|
| Detector | AST rules and assertion vocabulary | Current Python files, literal SHA-256 and source hashes |
| Adjudications | Per-content verdict and source-review reason | Exact file/function/literal-hash lookup; no allowlist |
| Rendered prose | Conservative scope/refusal language | Pooled-row verification flags and existing record counts |
| Offline replay | Pinned 2026-09-11; empty AACT directory | Held caches; 32 actual builds; socket connections refused |
| Tests | Explicit synthetic plants | Pre/post detector output and pytest results |

MEASURED means recorded command output, source/hash comparisons and rendered bytes. INFERRED means the source-review judgment that a condition supports or fails to support an assertion. CLAIMED: no release certification, exhaustive semantic proof, current search completeness or independent accuracy. Memory was not used as evidence.

## Current sweep

218 Python files; 0 external templates. 311 reviewable occurrences. Identical literals in one function share a content identity.

| Class | n of N |
|---|---:|
| ASSERTION | 205 of 311 |
| CONDITIONED | 19 of 311 |
| COVERAGE_ASSERTION | 2 of 311 |
| FIXED_TIME | 7 of 311 |
| STATUS_CONSTANT | 78 of 311 |

| Verdict | n of N |
|---|---:|
| DEFENSIBLE-CONDITIONED | 166 of 311 |
| DESCRIPTIVE-METHOD | 87 of 311 |
| FALSE-POSITIVE | 16 of 311 |
| RETRACTION-MARKER | 8 of 311 |
| TRUE-DEFECT | 34 of 311 |

Clock inventory: 24 occurrences, separate from adjudication denominator.
The registry retains LIT2 content-bound adjudications; new content and new detector shapes were reviewed. Candidate-directed re-review corrected inherited verdicts where source conditions did not support the assertion. Fixed historical literals remain in resolved_adjudications; an asserted fix never suppresses a currently present TRUE-DEFECT.

## Gemini candidates — 25 grouped rows covering all 32 literal entries

The supplied file actually contains 32 `LINE:` entries. Seven pairs are fragments of one claim (census coverage, front-page gate, recall denominator, verification banner, held recoveries, definition audit and legacy integrity). They are grouped below to supply the requested 25 rows without dropping any entry. Full literal text, individual locations and content keys are in `.tmp/lit/candidates.json` and `docs/assertion_literal_validation.json`. Locations are on the requested base, before this lane’s edits.

| Candidate (input entry IDs) | Located at | Sweep verdict | Adjudication | Reason |
|---|---|---|---|---|
| 1,2: "surfaces_checked" / "claims_checked" | harness/census.py:100; harness/census.py:103 | CONFIRMED | TRUE-DEFECT | The claim count increments before render; render exceptions are swallowed and surfaces_checked always names all three surfaces, including unscanned primary surfaces. |
| 3: f"PICO-scoped registry census: {ghost_ub} of ~{completed} completed screened-eligible trials have no… | harness/grade.py:307 | CONFIRMED | DEFENSIBLE-CONDITIONED | Nonempty ghost and pico_scoped guard gate the branch; this function computes completed=enumerated-ongoing, ghost fraction and threshold downgrade before returning assessed. It describes this registry calculation, not independent adjudication or funnel-plot execution. |
| 4: f"machine-assessed domains only; D3 unassessed on {d3_unassessed_n} of {len(prim_trials)} trial(s)" | harness/grade.py:333 | CONFIRMED | DESCRIPTIVE-METHOD | Scope qualifier for partial machine GRADE. grade returns None without primary result, computes each domain and publishes unassessed_domains; it does not assert all domains/trials were assessed. |
| 5,6: "publishes each as a tabbed, auditable page. Every page here passed a two-limb gate:" / "it reproduces from a fresh clone with zero census failures and its served analysis" | harness/index.py:20; harness/index.py:21 | CONFIRMED | TRUE-DEFECT | Presence of pages/rows is insufficient: no gate-result read, ok==n guard, or explicit external-confirmation state supports the universal assertion. |
| 7: "assessments, and each pooled recovery was verified against source before it counted).</p>" | harness/index.py:80 | CONFIRMED | TRUE-DEFECT | The historical parity/recovery counts do not carry per-recovery verification or current-engine evidence sufficient for the blanket verification/current-miss assertion; replaced by a typed refusal while retaining the recorded counts. |
| 8,9: "&mdash; against the {_E(rd.get('clean_eligible_denominator'))} source-verified-eligible " / "missing trials. Every one is a confirmed miss of the current search; this is the honest " | harness/index.py:161; harness/index.py:162 | CONFIRMED | TRUE-DEFECT | The historical parity/recovery counts do not carry per-recovery verification or current-engine evidence sufficient for the blanket verification/current-miss assertion; replaced by a typed refusal while retaining the recorded counts. |
| 10: "Every recovery is source-verified (audit-relayed numbers are not sources); the vocabulary " | harness/index.py:171 | CONFIRMED | TRUE-DEFECT | The historical parity/recovery counts do not carry per-recovery verification or current-engine evidence sufficient for the blanket verification/current-miss assertion; replaced by a typed refusal while retaining the recorded counts. |
| 11: "</strong> confirmed by an outside party. Applying the same instrument to a comparator " | harness/index.py:324 | CONFIRMED | TRUE-DEFECT | Presence of pages/rows is insufficient: no gate-result read, ok==n guard, or explicit external-confirmation state supports the universal assertion. |
| 12,13: "<div class='banner'><h2>Every pooled number is verified against its source " / "(gate-enforced)</h2><p><strong>All {ok} of {n} pooled trial-outcome numbers</strong> across " | harness/index.py:403; harness/index.py:404 | CONFIRMED | TRUE-DEFECT | Presence of pages/rows is insufficient: no gate-result read, ok==n guard, or explicit external-confirmation state supports the universal assertion. |
| 14: "reaches, confirmed by a blind reader on full text. The judge also flagged real defects in our pages… | harness/index.py:872 | CONFIRMED | DEFENSIBLE-CONDITIONED, TRUE-DEFECT | The full-text comparison paragraph is reached only after _fair_numbers loads nonempty PRISMA and judge records and interpolates their scorable coverage. Presence of aggregate judge/prisma counters does not establish the stated universal domain split or a specific confirmation of parity. |
| 15: "verified.</strong> Every pooled number carries a verbatim source span and the whole review " | harness/index.py:1186 | CONFIRMED | TRUE-DEFECT | Static narrative asserts external superiority, verified recoveries and rating checks without reading per-claim evidence; replaced with explicit unproven state. |
| 16: "toward larger effects</em>: every eligible trial we have recovered and source-verified moved " | harness/index.py:1197 | CONFIRMED | TRUE-DEFECT | Static narrative asserts external superiority, verified recoveries and rating checks without reading per-claim evidence; replaced with explicit unproven state. |
| 17,18: "the recovered set is shown to be representative, not merely verified</strong> &mdash; the " / "verified trials are held pending a full search rebuild, and the incompleteness is stated on " | harness/index.py:1223; harness/index.py:1224 | CONFIRMED | TRUE-DEFECT | Static narrative asserts external superiority, verified recoveries and rating checks without reading per-claim evidence; replaced with explicit unproven state. |
| 19: "source-verified numbers.</p>" | harness/index.py:1241 | CONFIRMED | TRUE-DEFECT | Static narrative asserts external superiority, verified recoveries and rating checks without reading per-claim evidence; replaced with explicit unproven state. |
| 20: "inflating good ones. Every raised rating was checked individually against its evidence " | harness/index.py:1251 | CONFIRMED | TRUE-DEFECT | Static narrative asserts external superiority, verified recoveries and rating checks without reading per-claim evidence; replaced with explicit unproven state. |
| 21: f"assessed); every pooled number was extracted down a source ladder and verified against its " | harness/manuscript.py:372 | CONFIRMED | TRUE-DEFECT | Static prose claimed completed screening independence, source verification and arm checks without reading result states; replacement checks pooled verification flags and declines arm-assignment inference. |
| 22: "adjudication. Each pooled value was located in a committed source, its arms checked for correct " | harness/manuscript.py:396 | CONFIRMED | TRUE-DEFECT | Static prose claimed completed screening independence, source verification and arm checks without reading result states; replacement checks pooled verification flags and declines arm-assignment inference. |
| 23: `<p class='note'>Every effect source-verified; intervals from the canonical engine. The compatibilit… | harness/page.py:527 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 24: `<div class='banner'>This page offers <strong>greater auditability, not stronger evidence</strong>: … | harness/page.py:651 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 25,26: "families (Gemini via AGY, and Fable) re-read every pooled row and checked whether the extracted " / "per-number <strong>MAGNITUDE</strong> check (every pooled number located in its committed source " | harness/page.py:1805; harness/page.py:1810 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 27: "<p class='muted'>Trials we located and whose numbers we verified against source, " | harness/page.py:2150 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 28: "<p>These trials are verified in-scope under the registered PICO yet were absent from " | harness/page.py:2196 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 29: "Results tab + per-trial Source column — source hierarchy (abstract > CT.gov structured > full text … | harness/page.py:2291 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 30,31: <p class='note'><strong>Trial integrity:</strong> none of the {_e(integ.get('n_pooled'))} trials poo… /  (checked {_e(integ.get('checked_utc'))} via {_e(integ.get('source'))} + AACT dates).</p> | harness/page.py:991; harness/page.py:996 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |
| 32: <tr><td>Records identified (committed search)</td><td>{_e(n_identified)}</td></tr> | harness/page.py:1045 | CONFIRMED | TRUE-DEFECT | Container presence is the only relevant guard; it does not prove complete per-row verification, scan coverage, retrieval provenance or the asserted completed operation. See CHK patch for conservative recorded-state wording. |

## Repairs and ownership

| Source | Before | After |
|---|---|---|
| index._verification_section | “Every pooled number … All ok of n”, gated only by n > 0 | Computed ok of n positive verification states; no universal source/gate claim |
| index._FRONT / external findings | Every page passed; any non-NONE label called external confirmation | Explicit per-page inspection requirement; non-NONE labels counted as labels |
| index parity/recovery/audit/thesis banners | Unconditional source verification, current misses, independent errors and superiority | Recorded counters plus explicit unproven coverage/independence/currentness |
| manuscript | All pooled values verified and arms checked; absence inferred from missing result | Verification phrase reads all trial flags; arm checks unproven; missing result does not imply non-reporting |
| propositions / compat_check | checked=True | checked derives from remaining violations |
| limitations | Unconditional source coverage and independent span-check narrative | Scope-limited wording; historical counts do not establish independence/current coverage |
| CHK page patch | Strand/source/audit/refusal/legacy integrity/PRISMA/comparator claims from container presence | Recorded-state wording; no inferred all-trial retraction clearance or constant AACT check |
| CHK census patch | Render errors swallowed; all surfaces and premature counts reported checked | Render exceptions refuse; surfaces and claim counts reflect actual successful scans |

Exact owned-source before/after: `.tmp/lit/source-fixes.diff`. Exact pending changes: `.tmp/patches/page-1.diff`, `.tmp/patches/census-1.diff`. The integration patch is `.tmp/patches/verify_all_limb.diff`; its callable lives in `harness/assertion_literal_limb.py`. CHK-owned source files remain byte-identical to HEAD. Patches were checked with `git apply --check`; isolated proposed-code plants verify legacy integrity wording and render-error refusal.
The landing integrator must apply the CHK patches in the same commit, rerun the sweep and adjudicate replacement literals/changed coverage guards. The limb intentionally refuses this unpatched tree. Rebuild real docs only at integration; this lane generated scratch outputs only.
Both search date scripts, and all search_v2_run*.py files, were left alone. In particular measure_search_v2_measurement.RUN_DATE is the sealed first-run artefact date, not a live invocation timestamp. The known LIT2 date mis-repair was not ported. Other out-of-ownership defects remain blocking and are listed below; READY-BEHIND-CHK does not imply that CHK alone clears every blocker.

## Detector-gap plants, verbatim

```python
def render():
    return "Every page here passed a two-limb gate"
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [ASSERTION] render: 'Every page here passed a two-limb gate' — no enclosing branch reads a state field; surface-bound prose candidate
```

```python
def render():
    return "Every number traces to a committed source"
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [ASSERTION] render: 'Every number traces to a committed source' — no enclosing branch reads a state field; surface-bound prose candidate
```

```python
def render():
    return "No pooled trial is retracted"
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [ASSERTION] render: 'No pooled trial is retracted' — no enclosing branch reads a state field; surface-bound prose candidate
```

```python
def render():
    return "Records identified (committed search)"
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [ASSERTION] render: 'Records identified (committed search)' — no enclosing branch reads a state field; surface-bound prose candidate
```

```python
def render():
    return " + AACT dates).</p>"
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [ASSERTION] render: ' + AACT dates).</p>' — no enclosing branch reads a state field; surface-bound prose candidate
```

```python
def scan():
    return {"claims_checked": count, "surfaces_checked": surfaces}
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [COVERAGE_ASSERTION] scan: "'claims_checked': count" — reported scan coverage requires successful surface execution
plant.py:2 [COVERAGE_ASSERTION] scan: "'surfaces_checked': surfaces" — reported scan coverage requires successful surface execution
```

```python
def panel():
    items = [("method", True, "Every extraction was verified against source")]
    rows = []
    for label, ok, text in items:
        rows.append(text)
    return "<p>" + "".join(rows) + "</p>"
```
Pre-fix detector: silent (0 findings). Post-fix:
```text
plant.py:2 [ASSERTION] panel: 'Every extraction was verified against source' — no enclosing branch reads a state field; surface-bound prose candidate
```

## Tests and limb

`python -X utf8 -m pytest tests/test_assertion_literals.py -q -p no:cacheprovider`

20 passed in 80.74s (0:01:20)

`python -X utf8 -m pytest tests/ -q -p no:cacheprovider`

16 failed, 978 passed, 4 warnings in 1071.15s (0:17:51)

Logs: `.tmp/lit/focused-final-pytest.log`, `.tmp/lit/full-pytest.log`. The full run began before the final detector adjudication; the final focused run verifies the final detector/registry. Imported LIT2 integration tests assumed repairs outside this lane; their original text is retained in `.tmp/lit/imported-tests.py`. The lane tests now assert that those unfixed source literals remain TRUE-DEFECT and blocking, rather than pretending the unported repairs exist. The gate itself has not been relaxed.

Limb verdict on this tree (verbatim):
```text
REFUSED
harness/census.py:100 TRUE-DEFECT: "'surfaces_checked': surfaces"
harness/census.py:103 TRUE-DEFECT: "'claims_checked': checked_total"
harness/census.py:223 TRUE-DEFECT: 'True'
harness/consumer_consistency.py:473 TRUE-DEFECT: 'not stated in retrieved source'
harness/page.py:527 TRUE-DEFECT: "<p class='note'>Every effect source-verified; intervals from the canonical engine. The compatibility key keeps strands apart; a cross-strand pool is refused, not computed.</p></div>"
harness/page.py:651 TRUE-DEFECT: "<div class='banner'>This page offers <strong>greater auditability, not stronger evidence</strong>: every number traces to a committed source, every absence is declared, and any hand-edit breaks the reproduction census.</div>"
harness/page.py:991 TRUE-DEFECT: ' trials pooled across all outcomes on this page is retracted'
harness/page.py:996 TRUE-DEFECT: ' + AACT dates).</p>'
harness/page.py:1043 TRUE-DEFECT: "<h4>Study selection flow (PRISMA 2020)</h4><table class='recs'><tr><th>Stage</th><th>n</th></tr><tr><td>Records identified (committed search)</td><td>"
harness/page.py:1804 TRUE-DEFECT: "<div class='absent'><strong>Cross-family definition audit.</strong> Two independent model families (Gemini via AGY, and Fable) re-read every pooled row and checked whether the extracted result matches the outcome LABEL's definition &mdash; composite component set, timepoint, population, analysis set &mdash; not just the number. Rows flagged for this topic, with how each was resolved (refuse the trial / disclose the heterogeneity / relabel the timepoint / already disclosed). This is the endpoint-<strong>IDENTITY</strong> check &mdash; distinct from the per-number <strong>MAGNITUDE</strong> check (every pooled number located in its committed source span, gate-enforced). A number can pass magnitude and fail identity, which is exactly the class this audit catches; &lsquo;verified&rsquo; on this harness now means both:<table class='arms'><tr><th>Trial</th><th>Outcome</th><th>Finding</th><th>Resolution</th></tr>"
harness/page.py:1986 TRUE-DEFECT: 'k in the comparator (verified against its source text)'
harness/page.py:2149 TRUE-DEFECT: "<h4>Verified but not pooled (refusals, with reasons)</h4><p class='muted'>Trials we located and whose numbers we verified against source, yet deliberately did not pool. Honest k over inflated k: a named refusal is a result.</p><table class='arms'><tr><th>Trial</th><th>What was verified</th><th>Why it was not pooled</th></tr>"
harness/page.py:2195 TRUE-DEFECT: '<h4>Never considered (a fifth state — the true search gap)</h4><p>These trials are verified in-scope under the registered PICO yet were absent from EVERY identifier space in this review — not screened, not excluded, not declared absent, simply never retrieved. They are invisible to the STALE count, PRISMA and the declared-absent census unless named here:<ul>'
harness/page.py:2291 TRUE-DEFECT: 'Results tab + per-trial Source column — source hierarchy (abstract > CT.gov structured > full text > hand-verified AACT arms), round-trip validation on every extraction, outcome-identity gating; refuse on ambiguity.'
harness/page.py:2618 TRUE-DEFECT: ' model/registry-derived domain ratings independently checked by a different model family (Fable) against each trial abstract; '
scripts/build_iv_iron_strands.py:124 TRUE-DEFECT: 'iv-iron for heart-failure hospitalisation, expressed as THREE (here four) declared analyses rather than one forced pool. The compatibility key keeps strands apart: first-event HR, recurrent-event rate ratio, and participant-level risk are different estimands of different event processes and MUST NOT be pooled together. Within the recurrent rate ratios the ENDPOINT further splits them (HF-hosp alone vs HF-hosp+CV-death composite). Every number is source-verified with its verbatim span; no risk-of-bias or clinical judgement is added here.'
scripts/build_iv_iron_strands.py:131 TRUE-DEFECT: '2026-09-14'
scripts/build_search_benchmark.py:826 TRUE-DEFECT: '- python -m pytest tests/test_search_benchmark_isolation.py -q -> 2 passed'
scripts/build_search_benchmark.py:827 TRUE-DEFECT: '- python -m pytest tests/ -q -> 580 passed'
scripts/comparator_correctness_sweep.py:1732 TRUE-DEFECT: "This bundle applies the same five checks to each published comparator and to our matching pool: design key, estimand key, analysis-population check, compatibility key, and pooled-number reproduction. Comparator per-trial effect inputs were not machine-readable because the effects live in forest-plot figures, while characteristics tables made the design, analysis-population, and compatibility checks assessable where parsed. THEIRS findings are external claims with verification NONE; OURS findings are internal disclosures about this repository's pools."
scripts/dual_compare.py:63 TRUE-DEFECT: 'second independent extractor: Fable located each span independently; a served number AGREES if its digits are present in the model-located span. Model emitted no number; deterministic code did the comparison.'
scripts/entry_condition_sweep.py:17 TRUE-DEFECT: '2026-09-16'
scripts/hm3_report.py:16 TRUE-DEFECT: 'MEASURED: 50 of 50 baseline trial × harm items resolved from held sources: '
scripts/hm3_report.py:33 TRUE-DEFECT: 'Each page was built with `python scripts/build_topic.py <slug> --now 2026-09-11`, then checked with `harness.gate.gate_page`, the function used by `verify_all.limb_gate_every_page`. Every build exited 0. The runner blocks socket connections and restores shared index/blind-map bytes after builds.'
scripts/hm3_report.py:53 TRUE-DEFECT: '- `harness/gate.py`, `harness/synth.py`, search, screening, membership and other lane pages were not modified.'
scripts/hm3_report.py:55 TRUE-DEFECT: 'Local AACT was read through the adapter schema from snapshot folder `2026-08-30`; this is an archive locator, not a claim about source-record currency. Verbatim filtered rows and hashes are retained in [aact/](docs/evidence/hm3-held-source-audit/aact/), including reported_events, reported_event_totals, outcome_counts, outcomes, outcome_measurements and result_groups. No percentages were multiplied by an assumed denominator. Overlapping adverse-event categories were not summed.'
scripts/hm3_report.py:56 TRUE-DEFECT: 'Second-pass identity checks excluded embedded fulltext_by_pmid entries for melatonin PMID 33157425 (ARE/MLT study), semaglutide PMID 40825340 (review text), and esketamine PMID 31109201 (French prospective cohort). These texts were not used as numbers for the named trials; the held abstracts and matching primary sources were used. Source-cache repairs are outside this harm lane.'
scripts/measure_search_v2_measurement.py:862 TRUE-DEFECT: ' -- measured with the LEGACY concept-query engine (harness/acquisition.py, re-run because that file changed), NOT with search_v2, which has not been run against the sealed register; development topics excluded'
scripts/missing_effect_sweep.py:84 TRUE-DEFECT: '2026-09-16'
scripts/probiotics_search_diagnostic.py:31 TRUE-DEFECT: '2026-09-15'
scripts/reproduce_review.py:88 TRUE-DEFECT: 'True'
scripts/search_v2_run.py:43 TRUE-DEFECT: '2026-09-15'
scripts/search_v2_run.py:145 TRUE-DEFECT: 'RAN (development run; per-source states in its snapshot ledger)'
scripts/search_v2_run_evidence.py:202 TRUE-DEFECT: 'SEALED REGRESSION REGISTER -- measured ON search_v2 (run '
```

## Offline scratch builds and per-page text changes

MEASURED: 32 of 32 builds passed with AACT_DIR=.tmp/empty_aact (directory exists and is empty). 32 of 32 outcome objects are identical to the held committed review objects, including IDs, dates and statistical values. These are consistency comparisons, not new external-source validation. All builds reside in `.tmp/lit/docs/reviews/`. Pending CHK changes are not applied to these outputs. Certificates/hashes can change as consequences of new prose.
The following changes are extracted from visible DOM text, not reconstructed from intended edits. Full arrays are in docs/assertion_literal_validation.json.

### balanced-crystalloids-vs-saline-mortality

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 0aaed1d0eb59e789

After: 80bdcecdbeb083d7

Before: 1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67

After: f3bc1e8a45a726d1a3075444609585ff074310903d0f21a8f648f3da81d9616f

Before: "release_sha256": "1fc4bb496a9ec2aeb2c5a2afab157a6bac7e02b0db3c64fc13f526f071a2ba67",

After: "release_sha256": "f3bc1e8a45a726d1a3075444609585ff074310903d0f21a8f648f3da81d9616f",

Before: "manuscript_sha256": "0055afbbc4e95ba7c02548990e151e19cf37c4e073c9302411e982c1da8ef5bb", / "review_sha256": "0aaed1d0eb59e7893f7ea1fd148569c97ca24f46a6d16b63f1666f330d106426",

After: "manuscript_sha256": "4b03432b7207e8313763fcada3fb971fba6137359db7281249022da6ff32e628", / "review_sha256": "80bdcecdbeb083d724ea2e63bda0134b90183960090a3c44c5757b30dc11b28b",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA f85737aa4710), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (29 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA f85737aa4710), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 29 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA f85737aa4710); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA f85737aa4710); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 0aaed1d0eb59e7893f7ea1fd148569c97ca24f46a6d16b63f1666f330d106426

After: 80bdcecdbeb083d724ea2e63bda0134b90183960090a3c44c5757b30dc11b28b

### colchicine-postop-af

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 6d2f3c808b0d6e9c

After: dc83fbc172e059ce

Before: 528d06ea91506c3f4a0df60036afd289b8ba199550a2523a34259adce384f12a

After: c80a959e1ba5108c41ef171ce125136e374855144619edb1c8a7548884a1d464

Before: "release_sha256": "528d06ea91506c3f4a0df60036afd289b8ba199550a2523a34259adce384f12a",

After: "release_sha256": "c80a959e1ba5108c41ef171ce125136e374855144619edb1c8a7548884a1d464",

Before: "manuscript_sha256": "ca02324a9fdf20e70d906dd4329d82c93f3c534525e898cb1971fc77c3af1947", / "review_sha256": "6d2f3c808b0d6e9c0c7e1e998130a9ca66d13719e21895c616112680cdc8ba7d",

After: "manuscript_sha256": "bf0eb1c0c8bc3a739ffa1d0cabf98d9496cb63cb73542e74593cc86b19962bd1", / "review_sha256": "dc83fbc172e059ce4ac544e0a433cd66a786e7b84733a0be663a1b879acce50c",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (67 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 67 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 6d2f3c808b0d6e9c0c7e1e998130a9ca66d13719e21895c616112680cdc8ba7d

After: dc83fbc172e059ce4ac544e0a433cd66a786e7b84733a0be663a1b879acce50c

### colchicine-recurrent-pericarditis

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 85c18ac1dd067214

After: 877cb0c4f38a73bf

Before: a4419f25558867c078f28ccc7e6060bd94ff4cf0c59257e9ab4457ec1e4fc95a

After: 06e16efcec4ca59a12d1695cab99a4d94230e5b34fdff57c0085c3ede6e7de5c

Before: "release_sha256": "a4419f25558867c078f28ccc7e6060bd94ff4cf0c59257e9ab4457ec1e4fc95a",

After: "release_sha256": "06e16efcec4ca59a12d1695cab99a4d94230e5b34fdff57c0085c3ede6e7de5c",

Before: "manuscript_sha256": "bb36b766ae72d9b7753dd5385b40a3201d91e61a86fbca125ebe83718094eab5", / "review_sha256": "85c18ac1dd0672146c4e77f28346f9569673947882ba837ec7d785bab7d9b72d",

After: "manuscript_sha256": "6d8d22ee42d484a4cb0620d49014a73d12669ea1d7ee7a100e13535e7739520b", / "review_sha256": "877cb0c4f38a73bf2f407aad36d0a9727dc31cc1c2b9450a8cc1677906efda59",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 34023da4e35f), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (53 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 34023da4e35f), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 53 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 34023da4e35f); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 34023da4e35f); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 85c18ac1dd0672146c4e77f28346f9569673947882ba837ec7d785bab7d9b72d

After: 877cb0c4f38a73bf2f407aad36d0a9727dc31cc1c2b9450a8cc1677906efda59

### colchicine-secondary-cv-prevention

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 7a6f8eb56cc435ba

After: f39499b21d51373c

Before: 54bc3b30d259f9d46aeabd58157c8dccf202f33868b8100de497b86692a40c67

After: 8ee7d3325afda2c4316b428a58a2cf4a32650b088847db8fb9a9286851d9d0fa

Before: "release_sha256": "54bc3b30d259f9d46aeabd58157c8dccf202f33868b8100de497b86692a40c67",

After: "release_sha256": "8ee7d3325afda2c4316b428a58a2cf4a32650b088847db8fb9a9286851d9d0fa",

Before: "manuscript_sha256": "a06a93b3193bb719778a61d1c5e0f3b66da531d64ec4c349de5283557991f1ff", / "review_sha256": "7a6f8eb56cc435ba1f6ad11a489d662a7e71e86066077e0d359adbd44ac4c74f",

After: "manuscript_sha256": "3221802ded513d695f5558055bdaed3abb1bc9bed5b35873e6d3771ddbd72b98", / "review_sha256": "f39499b21d51373cc0bde3926400bff6ddb206037270ed66a82557a760fc0463",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (120 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 120 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 7a6f8eb56cc435ba1f6ad11a489d662a7e71e86066077e0d359adbd44ac4c74f

After: f39499b21d51373cc0bde3926400bff6ddb206037270ed66a82557a760fc0463

### corticosteroids-cap-mortality

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 03e9b2b1a1e7f1b2

After: b71b45ac1824ea4e

Before: 6635e3e6ca5ab0802860a514012c3547584816f68ce50262c5983a4d5603be8c

After: 7bb59b935b871c86ec1ffa3b3656b13f778e0104fb3e5c640b409c8394a3e94a

Before: "release_sha256": "6635e3e6ca5ab0802860a514012c3547584816f68ce50262c5983a4d5603be8c",

After: "release_sha256": "7bb59b935b871c86ec1ffa3b3656b13f778e0104fb3e5c640b409c8394a3e94a",

Before: "manuscript_sha256": "8b3b68a69af82a61c96207c2eab8a682e988bb3ccc064c7ce5b3656d5b7013ff", / "review_sha256": "03e9b2b1a1e7f1b2c7aeb83d86d67a78893d90335cd184933f25f51f37e8c63f",

After: "manuscript_sha256": "f2995077f91decd3ff7f6b853264e3baa1b23a7c887bda84ded65f2314eab3d6", / "review_sha256": "b71b45ac1824ea4ec41225c5406c41006c2d3d1629c833a296912b69dcf7b072",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 036ee46c6c45), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (114 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 036ee46c6c45), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 114 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 036ee46c6c45); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 036ee46c6c45); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 03e9b2b1a1e7f1b2c7aeb83d86d67a78893d90335cd184933f25f51f37e8c63f

After: b71b45ac1824ea4ec41225c5406c41006c2d3d1629c833a296912b69dcf7b072

### corticosteroids-covid19-mortality

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 808ce59607f55828

After: 4bc671304437e3bf

Before: dd843eb8a28f8fafc8b469029270a758c79159a5929953b9f18216d6d2e2b408

After: c3d34e3947fa65120122794060baaf64c2adb5ccd8e5b16534c1aad9e1c1b3d7

Before: "release_sha256": "dd843eb8a28f8fafc8b469029270a758c79159a5929953b9f18216d6d2e2b408",

After: "release_sha256": "c3d34e3947fa65120122794060baaf64c2adb5ccd8e5b16534c1aad9e1c1b3d7",

Before: "manuscript_sha256": "1ba94ebd8b08b4ec5049591fb313d77f96415941f65ee41cdd4d75730fce192d", / "review_sha256": "808ce59607f55828abb8698fb4f59547cf9fb099c2495bc6264c9a4146c7248e",

After: "manuscript_sha256": "1e7cac72f90978f09019c645ffc01899380e552acb28e7699f84fc3ea3315b1a", / "review_sha256": "4bc671304437e3bf493464eaedd9c035bafee7fa04c398f130b5d2caa45be6a9",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA dce99b4135d9), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (56 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA dce99b4135d9), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 56 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA dce99b4135d9); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA dce99b4135d9); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 808ce59607f55828abb8698fb4f59547cf9fb099c2495bc6264c9a4146c7248e

After: 4bc671304437e3bf493464eaedd9c035bafee7fa04c398f130b5d2caa45be6a9

### dapagliflozin-hfpef-hosp

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 4f2385c6daeff067

After: 501dcca82a959156

Before: e70ec8cb8181760610162b042352310301993e6764b208de807f243504fd87b8

After: 7825502c6b2182cd55efe40d5e2a7a7707e78c97b98a0417b8208be4db170fe5

Before: "release_sha256": "e70ec8cb8181760610162b042352310301993e6764b208de807f243504fd87b8",

After: "release_sha256": "7825502c6b2182cd55efe40d5e2a7a7707e78c97b98a0417b8208be4db170fe5",

Before: "manuscript_sha256": "befdb0239f036d92de275c686b7840f05f2ce4a66ac2225bc781805aceab1b8f", / "review_sha256": "4f2385c6daeff06712d3d2512a518a86061e60e0fc0bad160f3764e3cf3f90ff",

After: "manuscript_sha256": "87be2bd7c046138a0684129da4998bb445437f7d57c1feb1cd6d63fbdd3bb0ad", / "review_sha256": "501dcca82a9591565fcb85324a6deee92400e9515946e6042f363331679ec9c3",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA a6788cc51802), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (97 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA a6788cc51802), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 97 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA a6788cc51802); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA a6788cc51802); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 4f2385c6daeff06712d3d2512a518a86061e60e0fc0bad160f3764e3cf3f90ff

After: 501dcca82a9591565fcb85324a6deee92400e9515946e6042f363331679ec9c3

### denosumab-vertebral-fracture

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: b9268f9ade0d17de

After: cc1d53757bc95870

Before: 6779cda163c4e4de4cfbb17617cb41034efcf8a4c751bc1cad7692bb0efc0ff3

After: 46655339d2d9549dd6db4af742f275eaa8e7ff006e414c742bf3755f1b6a8190

Before: "release_sha256": "6779cda163c4e4de4cfbb17617cb41034efcf8a4c751bc1cad7692bb0efc0ff3",

After: "release_sha256": "46655339d2d9549dd6db4af742f275eaa8e7ff006e414c742bf3755f1b6a8190",

Before: "manuscript_sha256": "394ad9ab8f3a2846a5cd1384e82b06b92529d3cc5ba6a8007bc2ebfd3558dec5", / "review_sha256": "b9268f9ade0d17de0d808d57236d3f876e95b5efa84f3416c621c504ba04f592",

After: "manuscript_sha256": "7e0f4cb22430eda8881872c29c782d44dc5b27f020d2ca6678df052309e67d8a", / "review_sha256": "cc1d53757bc95870a38ef6d16433cc30d0e5ddd26571f8774cfa664dc39c396a",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (71 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 71 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: b9268f9ade0d17de0d808d57236d3f876e95b5efa84f3416c621c504ba04f592

After: cc1d53757bc95870a38ef6d16433cc30d0e5ddd26571f8774cfa664dc39c396a

### doac-vte-recurrence

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 4de6d31eb9e95168

After: ef6c13213b6bfe1b

Before: 7c5fdb4b7c3f22b3773e318c3db3f40719cafda9272af178754949d607869eea

After: 0ff3f58f475eddb436203456c82fd0d50967f155a1a7841665cc69669437a98b

Before: "release_sha256": "7c5fdb4b7c3f22b3773e318c3db3f40719cafda9272af178754949d607869eea",

After: "release_sha256": "0ff3f58f475eddb436203456c82fd0d50967f155a1a7841665cc69669437a98b",

Before: "manuscript_sha256": "e74e63a3fdf032f6486fac075cae900491cd3da2c23f5dbfce9752aba0c7d9ec", / "review_sha256": "4de6d31eb9e95168f357b2ba06d0fc7a83f5cc03583a8ce51aed1f856790701a",

After: "manuscript_sha256": "4aef85c339a65b29ef4aba28594ce89d253ddcca50c5d67302a38d17c07e8c51", / "review_sha256": "ef6c13213b6bfe1b76c927efa5d6c436dbf5edbbbc0d72142f1469ad69fd48cf",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 4fc26adec9aa), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (234 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 4fc26adec9aa), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 234 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 4fc26adec9aa); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 4fc26adec9aa); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 4de6d31eb9e95168f357b2ba06d0fc7a83f5cc03583a8ce51aed1f856790701a

After: ef6c13213b6bfe1b76c927efa5d6c436dbf5edbbbc0d72142f1469ad69fd48cf

### dpp4-mace-t2d

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: d8c52fa18d2dc06e

After: f70fabeefa4b95b4

Before: 19c28388bac82f629d9fe13caef50d1e8b365061a83bd3483f7a72bce5d8ff6f

After: b5ce0cee039990e1184b443769f5d74be77762522ec37b4a66845f110c4c3605

Before: "release_sha256": "19c28388bac82f629d9fe13caef50d1e8b365061a83bd3483f7a72bce5d8ff6f",

After: "release_sha256": "b5ce0cee039990e1184b443769f5d74be77762522ec37b4a66845f110c4c3605",

Before: "manuscript_sha256": "fa4e78932be87cb13e265beaaf2c1ef68353c8f41dcc66b22429f58412b7c57b", / "review_sha256": "d8c52fa18d2dc06e1b1cd68f2628689785969ee01a6ff2ca3c401f4b6e41ab70",

After: "manuscript_sha256": "2c666dd70789befa4581742557dfd80766a907a7ce056740a564dfd232bd1ae6", / "review_sha256": "f70fabeefa4b95b4aaadf6eb01626cabe9b7b3ea4f5e21ade88a16ed7242dd5f",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 0fb7f9f4cd61), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (38 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 0fb7f9f4cd61), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 38 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 0fb7f9f4cd61); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 0fb7f9f4cd61); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: d8c52fa18d2dc06e1b1cd68f2628689785969ee01a6ff2ca3c401f4b6e41ab70

After: f70fabeefa4b95b4aaadf6eb01626cabe9b7b3ea4f5e21ade88a16ed7242dd5f

### empagliflozin-hfpef-hosp

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 2f24c905416e8e6a

After: c6ea5386e1e6b322

Before: abfe303de01c151242bb926ad1faf8b2a4cc592a0f6ea84f626d3903740cf233

After: 4a8ccb0f7a89bd2d5f5b2292ea66f0a1d0e44b1127af6a1a42dcc172358c805d

Before: "release_sha256": "abfe303de01c151242bb926ad1faf8b2a4cc592a0f6ea84f626d3903740cf233",

After: "release_sha256": "4a8ccb0f7a89bd2d5f5b2292ea66f0a1d0e44b1127af6a1a42dcc172358c805d",

Before: "manuscript_sha256": "1a61f9b6ef4d2e6d43c8d9fc502c2caa02384e9c43d99329884a239172b05771", / "review_sha256": "2f24c905416e8e6adf13241a0027d60a77a6db5c16e53d79b72083957acb388b",

After: "manuscript_sha256": "0c7953c56d7437be644b8bc88ca7f47ea1d9a17de5eff6a97b8e126e33b7225c", / "review_sha256": "c6ea5386e1e6b322c5d6ed158ba3951963785989b989b30f6d7228f184b1c79c",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA c5dc828d141f), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (100 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA c5dc828d141f), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 100 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA c5dc828d141f); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA c5dc828d141f); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 2f24c905416e8e6adf13241a0027d60a77a6db5c16e53d79b72083957acb388b

After: c6ea5386e1e6b322c5d6ed158ba3951963785989b989b30f6d7228f184b1c79c

### esketamine-trd-madrs

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 3f8e48acfe109814

After: cb685f7cd493be0e

Before: badff899fa3cc12b0529fc78921b27d950965511a3ded96735f69286e9a855d4

After: a992f0da36dba99713fc972747da61b2c0216af86407475f74c8a311024b017a

Before: "release_sha256": "badff899fa3cc12b0529fc78921b27d950965511a3ded96735f69286e9a855d4",

After: "release_sha256": "a992f0da36dba99713fc972747da61b2c0216af86407475f74c8a311024b017a",

Before: "manuscript_sha256": "3cec43126f47962d33cb1af6f9e7ff09e668276180ee8274adbe9b62ee863b5c", / "review_sha256": "3f8e48acfe109814a1f3bb23909c45125d4c56ca0e18a4ac356897c393b384c9",

After: "manuscript_sha256": "3a3009e52eea20faf8f03a5b8dc3f388310904e23fd766de4d117f35522de743", / "review_sha256": "cb685f7cd493be0efb59ea5c9563c256caf5ed754632701af25eeefc00a52075",

Before: This review is prospectively registered: the protocol was committed in a protocol-only commit (registration SHA 5e2b43c6f3d8) before synthesis. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (136 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is prospectively registered: the protocol was committed in a protocol-only commit (registration SHA 5e2b43c6f3d8) before synthesis. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 136 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol (protocol-only commit 5e2b43c6f3d8) was committed before any synthesis ran; deterministic replay is from the committed cache, and protocol-SHA byte-for-byte replay is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol (protocol-only commit 5e2b43c6f3d8) was committed before any synthesis ran; deterministic replay is from the committed cache, and protocol-SHA byte-for-byte replay is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 3f8e48acfe109814a1f3bb23909c45125d4c56ca0e18a4ac356897c393b384c9

After: cb685f7cd493be0efb59ea5c9563c256caf5ed754632701af25eeefc00a52075

### finerenone-ckd-t2d-renal

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 51dd05507f17bff4

After: 854193e18ceb438f

Before: 522295c4e131abac403fe8520ce13b63c528a31ae1676257762bff93a7b21f54

After: d16e7345de730421fc45eeb5e6404a527828f8abc50db137190d69555e1b5970

Before: "release_sha256": "522295c4e131abac403fe8520ce13b63c528a31ae1676257762bff93a7b21f54",

After: "release_sha256": "d16e7345de730421fc45eeb5e6404a527828f8abc50db137190d69555e1b5970",

Before: "manuscript_sha256": "c3b0865eac59c07517616150b0362a1329cf7cf564b8e49e168eb3fcb4fcfe94", / "review_sha256": "51dd05507f17bff490f4590386e1a50e161efd1f20ae0be12cc32758d526f937",

After: "manuscript_sha256": "9ac08f3da1ccc8e46f2bf42d6ea63f562905909ed6b6309f67f2f4b6fa86db14", / "review_sha256": "854193e18ceb438f5129ab35bbcdd9e2c2b0450b3729a1042840d6ca864e326a",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 43f5f12e3671), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (23 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 43f5f12e3671), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 23 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 43f5f12e3671); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 43f5f12e3671); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 51dd05507f17bff490f4590386e1a50e161efd1f20ae0be12cc32758d526f937

After: 854193e18ceb438f5129ab35bbcdd9e2c2b0450b3729a1042840d6ca864e326a

### glp1-ra-mace-t2d

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 98726cc125e9fcc7

After: 0e98acc88cb6c155

Before: db4238e4abf61292c8955df5666e7b625323d12f7bf7bf8873d5db8dec56144a

After: 92a4a2f3ec861c5374862aed6d97bd281e0ed1668f063d6b991cb97be250e570

Before: "release_sha256": "db4238e4abf61292c8955df5666e7b625323d12f7bf7bf8873d5db8dec56144a",

After: "release_sha256": "92a4a2f3ec861c5374862aed6d97bd281e0ed1668f063d6b991cb97be250e570",

Before: "manuscript_sha256": "904d362f620f21e2106e060a249991535a6d06ec279c90183fc051448242bb5a", / "review_sha256": "98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7",

After: "manuscript_sha256": "4f873f5a5e22cd7e0ea40d1483e154fc80c088a606684c8c8d501c0419d29782", / "review_sha256": "0e98acc88cb6c1554ea7399b49a6b37d396d47513fcb5927bdab9f839c4d5117",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA b10c53d3783f), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (11 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA b10c53d3783f), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 11 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA b10c53d3783f); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility follows the registered B-prime clause: Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained -- preferably with blinded or independent adjudication. Eligibility does not depend on the direction, statistical significance or published availability of the MACE result. If MACE was measured but the result is unavailable, the trial is retained and the result is pursued through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held. Outcome ascertainment is an eligibility axis; outcome result availability is not. Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA b10c53d3783f); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility follows the registered B-prime clause: Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained -- preferably with blinded or independent adjudication. Eligibility does not depend on the direction, statistical significance or published availability of the MACE result. If MACE was measured but the result is unavailable, the trial is retained and the result is pursued through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held. Outcome ascertainment is an eligibility axis; outcome result availability is not. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 98726cc125e9fcc749601459bce442a9b581ef4cce81c60cf891fa6d643917f7

After: 0e98acc88cb6c1554ea7399b49a6b37d396d47513fcb5927bdab9f839c4d5117

### iv-iron-hfref-hosp

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 57765213e53cd302

After: 03b501cf214c65d2

Before: 18f7716d71b1030ef22be5daf9c6a88d7177c1f911b65a20c44fcdc211cc7d5b

After: cb6d1bfebb2ee4d06e1be5f4360babd561be10a312b3b0b68471399e2ab42f45

Before: "release_sha256": "18f7716d71b1030ef22be5daf9c6a88d7177c1f911b65a20c44fcdc211cc7d5b",

After: "release_sha256": "cb6d1bfebb2ee4d06e1be5f4360babd561be10a312b3b0b68471399e2ab42f45",

Before: "manuscript_sha256": "da3ad8edd6ba53b01d280d19ac62d1e84a89c1f5312c4c6a77d2bfcdd6738b52", / "review_sha256": "57765213e53cd302e967f18500e96b9f3b0b5f67cad16c9fefaa459d254fa0e3",

After: "manuscript_sha256": "bba27dda452e50a76f2bf7d401ef509950afe2773a81189dcc8fd18a7511f190", / "review_sha256": "03b501cf214c65d2ff262604d5437c7d8b76f79de6e26b9e2a8178fb4a22343a",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA a56039f46158), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (39 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA a56039f46158), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 39 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA a56039f46158); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA a56039f46158); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 57765213e53cd302e967f18500e96b9f3b0b5f67cad16c9fefaa459d254fa0e3

After: 03b501cf214c65d2ff262604d5437c7d8b76f79de6e26b9e2a8178fb4a22343a

### melatonin-primary-insomnia-sol

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: d12d22bde7323098

After: 4e3a96e8d07947ab

Before: 2bcb2a0f0ee1d4ea4194bd5dec9b001062ff3935ef27336e251ff8dc76b69ea3

After: eef47af52bc85f2a72e4d183ec11a3fa02e328b0321a9b3ea5b1aa20b7c06d32

Before: "release_sha256": "2bcb2a0f0ee1d4ea4194bd5dec9b001062ff3935ef27336e251ff8dc76b69ea3",

After: "release_sha256": "eef47af52bc85f2a72e4d183ec11a3fa02e328b0321a9b3ea5b1aa20b7c06d32",

Before: "manuscript_sha256": "a514dd5acee0955f80cc79c1e94a5c933786adb1bce04dedaecd3f6979e23587", / "review_sha256": "d12d22bde7323098e856f4d444bf518fa2186b69f17de26f503ea8254cd47809",

After: "manuscript_sha256": "ba3dc34fe4246f096c4a9bbd91f48f9f198c77d1e90465a395a57f1b72122fbe", / "review_sha256": "4e3a96e8d07947ab3c8b07849cd00cc230d7fb19594b3d71fcbb5f4f4864f216",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 146edbf72435), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (126 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 146edbf72435), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 126 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 146edbf72435); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 146edbf72435); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: d12d22bde7323098e856f4d444bf518fa2186b69f17de26f503ea8254cd47809

After: 4e3a96e8d07947ab3c8b07849cd00cc230d7fb19594b3d71fcbb5f4f4864f216

### metformin-pcos-ovulation

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 892696356460e125

After: 0951821c7912c55a

Before: 90ac6e7c5a22dd884baff4d81b401786731eb1f523a6ad78e7da05112b726869

After: ce892ba55309b13d33dab6224c999afa58068ed09d174a8e55c5ae3111ccfe41

Before: "release_sha256": "90ac6e7c5a22dd884baff4d81b401786731eb1f523a6ad78e7da05112b726869",

After: "release_sha256": "ce892ba55309b13d33dab6224c999afa58068ed09d174a8e55c5ae3111ccfe41",

Before: "manuscript_sha256": "9f7523a1622686ad22d2155e3606dde7483734ea458f17b3bdbcc97bffe06405", / "review_sha256": "892696356460e12563c0503a07f2d9f5d5aba44c7757661a383456c10a6c3b39",

After: "manuscript_sha256": "cb3517e3956b341949ec57771cb7daaef1b70928fa6573921b25e0a92784ef02", / "review_sha256": "0951821c7912c55a36e029476dbcb6db2698277b48d40dbe71fb3696c4314c12",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (154 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 154 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 892696356460e12563c0503a07f2d9f5d5aba44c7757661a383456c10a6c3b39

After: 0951821c7912c55a36e029476dbcb6db2698277b48d40dbe71fb3696c4314c12

### noac-vs-warfarin-af-stroke

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 91da662722bdb1f4

After: 7801d0a471794bbf

Before: 838a39d427d7f1048813605bed6877ca02f74b4ce074e855474c20d32a6379dc

After: 8cd0a981122d0b1bf4701faf481d3f884463f8947c08dc209c37903eb746da05

Before: "release_sha256": "838a39d427d7f1048813605bed6877ca02f74b4ce074e855474c20d32a6379dc",

After: "release_sha256": "8cd0a981122d0b1bf4701faf481d3f884463f8947c08dc209c37903eb746da05",

Before: "manuscript_sha256": "ac8159a6d02b9d9dcf5ef21892f19ac08d7f773c643c1c89cf5f239c81e621bc", / "review_sha256": "91da662722bdb1f494cfe525adaf5ce7b0f27e7fc99e7370ea84d973e98da806",

After: "manuscript_sha256": "343cef428b833dd960ecad6e2f80c1dec0bd9d3f922f3f2f9bf3b3f437f536ba", / "review_sha256": "7801d0a471794bbf9d40055eed4e9b989286e35a479c547c0ed5a8ac0b5bf29f",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (35 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 35 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 91da662722bdb1f494cfe525adaf5ce7b0f27e7fc99e7370ea84d973e98da806

After: 7801d0a471794bbf9d40055eed4e9b989286e35a479c547c0ed5a8ac0b5bf29f

### omega3-cardiovascular-events

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 954eb7b368fde760

After: 97b58f358e6654d0

Before: a5c5db5aa1651718bf54e2f5f761dde7a089fac3e7126a5adee17e7a53d58f6c

After: 3509e94561ac3532bf628f44f09042b279c4ba8c4336cac6c90815887e16d71a

Before: "release_sha256": "a5c5db5aa1651718bf54e2f5f761dde7a089fac3e7126a5adee17e7a53d58f6c",

After: "release_sha256": "3509e94561ac3532bf628f44f09042b279c4ba8c4336cac6c90815887e16d71a",

Before: "manuscript_sha256": "92040a4de97ad9dd71e90bd9ad2655283af2c428e50ceea957a24eca5916ba66", / "review_sha256": "954eb7b368fde760fb78a74044f05edcef6a1abb1f3b68f072b5d73ec5bfadcb",

After: "manuscript_sha256": "596db2c2c6edddc927d2a1c41dbe348c53d711c2ce5b7aa32440eee997bee9de", / "review_sha256": "97b58f358e6654d06e7593c3af660446e93bfe09a5bb7c92450699b2a0dc17d0",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 13c0136f93aa), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (114 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 13c0136f93aa), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 114 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 13c0136f93aa); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 13c0136f93aa); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 954eb7b368fde760fb78a74044f05edcef6a1abb1f3b68f072b5d73ec5bfadcb

After: 97b58f358e6654d06e7593c3af660446e93bfe09a5bb7c92450699b2a0dc17d0

### pcsk9-mace

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: e24c35bdbab85138

After: 40e6491b9d1f96fb

Before: 27008f3cecea4bad96563ce5deaa46dc474238796020fdf71d9c3ba6e078d144

After: f415e85f94d80793874a0e3ead2e1dba629b0147524b884ce38cd4f125c210a3

Before: "release_sha256": "27008f3cecea4bad96563ce5deaa46dc474238796020fdf71d9c3ba6e078d144",

After: "release_sha256": "f415e85f94d80793874a0e3ead2e1dba629b0147524b884ce38cd4f125c210a3",

Before: "manuscript_sha256": "01312539b6cea7409c2c9bb5de3c8cf79f75c024f9ad1a25337d28dbc4bd3d56", / "review_sha256": "e24c35bdbab85138918f26b26e5c1e20c2112fb0ad5749c72d452e651ea2f5a9",

After: "manuscript_sha256": "057ef7ae55b02bfae5c70f3b17bbfc4bb978828870e431365a8e5b566a808d75", / "review_sha256": "40e6491b9d1f96fb4d521682914f79501f610ae06e238a0f8bf7c82d12972ef7",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA dd2403f56a10), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (12 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA dd2403f56a10), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 12 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA dd2403f56a10); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA dd2403f56a10); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: e24c35bdbab85138918f26b26e5c1e20c2112fb0ad5749c72d452e651ea2f5a9

After: 40e6491b9d1f96fb4d521682914f79501f610ae06e238a0f8bf7c82d12972ef7

### probiotics-aad-prevention

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 9932877c8d3c3b68

After: e5f551658e57f176

Before: 74f14fb77425c98ff6784fb57f6dcfe8f1d1b04dddeeaab36585a4295020e162

After: 5c0be6e96ae51be12f9ffa918299b009789dec086173daa779bb8a82fb5e5991

Before: "release_sha256": "74f14fb77425c98ff6784fb57f6dcfe8f1d1b04dddeeaab36585a4295020e162",

After: "release_sha256": "5c0be6e96ae51be12f9ffa918299b009789dec086173daa779bb8a82fb5e5991",

Before: "manuscript_sha256": "724cfbfbe10ce55fe01a98e93bf54c33419eecdd112b754324b9956f38d768e9", / "review_sha256": "9932877c8d3c3b6813bb9a21068e7176f0bdace65d3fd09403689f5a10eac904",

After: "manuscript_sha256": "7978f6e02dfcd74181a505b5841a9c91111b04df81404560f5784734cdacd57a", / "review_sha256": "e5f551658e57f1764ced4a2f9e9765d86b06cda657dec2a06cc0254eee673934",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (468 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 468 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 9932877c8d3c3b6813bb9a21068e7176f0bdace65d3fd09403689f5a10eac904

After: e5f551658e57f1764ced4a2f9e9765d86b06cda657dec2a06cc0254eee673934

### sacubitril-valsartan-hfref

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 04b07291943df879

After: e8e461264febbeff

Before: 27e200e25ddb54fb68bd58bcbeaa47d0b260f583e21ebce573160dea44a5f868

After: 9f01ac96c65f01a8c7544fdb0a2968b8ad6d69c05dc270d89150d75694495787

Before: "release_sha256": "27e200e25ddb54fb68bd58bcbeaa47d0b260f583e21ebce573160dea44a5f868",

After: "release_sha256": "9f01ac96c65f01a8c7544fdb0a2968b8ad6d69c05dc270d89150d75694495787",

Before: "manuscript_sha256": "cd62e47fe8d55bc50f8240c3b8f2a6bbf6a28ef462f6e0a0c4fda03090a6349b", / "review_sha256": "04b07291943df879080bdfd052eaa56560a659a9cba5a849d614ebc95b79a9e1",

After: "manuscript_sha256": "d00b918aa3e4c13f0f034694f8a25c17111f3de64dbe9178d8d8042434a2082c", / "review_sha256": "e8e461264febbeff3d763a539ed25744d93f99dfa861a5ccf6562235c7e654ac",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (81 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status NOT_RUN); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 81 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 04b07291943df879080bdfd052eaa56560a659a9cba5a849d614ebc95b79a9e1

After: e8e461264febbeff3d763a539ed25744d93f99dfa861a5ccf6562235c7e654ac

### semaglutide-obesity-mace

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 3b2fa682fb561b63

After: 3e7ecf372b74cb06

Before: e9b73319d6e144ab0739dadd90b3a8ec9096adb9e70fff10bd597128ee3592c3

After: 273519693276d2eaf34bd4d151b65271a4c65ff1c7496d77a6c767df743016c9

Before: "release_sha256": "e9b73319d6e144ab0739dadd90b3a8ec9096adb9e70fff10bd597128ee3592c3",

After: "release_sha256": "273519693276d2eaf34bd4d151b65271a4c65ff1c7496d77a6c767df743016c9",

Before: "manuscript_sha256": "40090dfc117d29de12cbfbb16fa541ee28d161e63a2bf7b52797e67f01cd656c", / "review_sha256": "3b2fa682fb561b631f5ffe3b8f011419551cb08a2af324e0cc3773b661c39573",

After: "manuscript_sha256": "1db05a37a711a6b9b9f930d0d1178d98fbeac7c0d67ce1b7e4b99af94b18a712", / "review_sha256": "3e7ecf372b74cb06691eca47512a7de78dbcd178024ddda146a6787d0c8a39f3",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (66 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 66 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 3b2fa682fb561b631f5ffe3b8f011419551cb08a2af324e0cc3773b661c39573

After: 3e7ecf372b74cb06691eca47512a7de78dbcd178024ddda146a6787d0c8a39f3

### semaglutide-obesity-weight

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 2a54c7d191e172be

After: a6158d5c5a667bbc

Before: 5fe65e25486fbac51161e4804d19bba32f2a2685f7a61e756faa9cb467713030

After: f9ab157f47d3212a81b180aaca63062838fab8a053539582552314b04efc3eec

Before: "release_sha256": "5fe65e25486fbac51161e4804d19bba32f2a2685f7a61e756faa9cb467713030",

After: "release_sha256": "f9ab157f47d3212a81b180aaca63062838fab8a053539582552314b04efc3eec",

Before: "manuscript_sha256": "27de136c88e665f4d3381a77bf27fd9b3c8d81446aa4186d3f6cdec5fa0dfef8", / "review_sha256": "2a54c7d191e172be545c701c2d1d8891f71529648280582822eee62f0cc9bc18",

After: "manuscript_sha256": "72e0ceee7a9ece9fc094726bc9100e1c07d8d6e609ea2d840850e57a8547ca3f", / "review_sha256": "a6158d5c5a667bbcd4d0e96b761ab0a9b571db82ca2cbc7a3cb01fe912fbdc9e",

Before: This review is prospectively registered: the protocol was committed in a protocol-only commit (registration SHA fe53c76aad18) before synthesis. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (143 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is prospectively registered: the protocol was committed in a protocol-only commit (registration SHA fe53c76aad18) before synthesis. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 143 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol (protocol-only commit fe53c76aad18) was committed before any synthesis ran; deterministic replay is from the committed cache, and protocol-SHA byte-for-byte replay is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol (protocol-only commit fe53c76aad18) was committed before any synthesis ran; deterministic replay is from the committed cache, and protocol-SHA byte-for-byte replay is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 2a54c7d191e172be545c701c2d1d8891f71529648280582822eee62f0cc9bc18

After: a6158d5c5a667bbcd4d0e96b761ab0a9b571db82ca2cbc7a3cb01fe912fbdc9e

### sglt2-ckd-progression

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 2e8806d864a2828f

After: ee03ff6ac3fc9beb

Before: cf6a3558b44b9527f069ef74efc8acab815b10ddfcd4ef0aeaf98f7c4dd00a05

After: cc769f6a0d9e07b4b72f47805bf9f58de514acb477175accc65390cd46b6ae59

Before: "release_sha256": "cf6a3558b44b9527f069ef74efc8acab815b10ddfcd4ef0aeaf98f7c4dd00a05",

After: "release_sha256": "cc769f6a0d9e07b4b72f47805bf9f58de514acb477175accc65390cd46b6ae59",

Before: "manuscript_sha256": "5d17c76b803a5b9c69c305909995a88e3be741d0eaf4ade042301ce7eb4945c6", / "review_sha256": "2e8806d864a2828ff93306d6bc9a329bf5c4e3b527ab8d9894bc569dd98a61ce",

After: "manuscript_sha256": "7f3f6d2ead757210d7dc07d8e81ca86ee5bc0113467996f1087e8a90aca1c7e4", / "review_sha256": "ee03ff6ac3fc9beba653beff1408fa79d35fd40f86464b1bcee1ce44af54b1b0",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (35 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 35 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 2e8806d864a2828ff93306d6bc9a329bf5c4e3b527ab8d9894bc569dd98a61ce

After: ee03ff6ac3fc9beba653beff1408fa79d35fd40f86464b1bcee1ce44af54b1b0

### sglt2-hfref-hosp-cvdeath

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: bbee69a85a3b6014

After: 087d45204abad5fd

Before: 766715ba86c3a08fdb10e6805c0349d3401da17eaad45e5fce6dd32f5427a76f

After: d83c366b2b9d31c842eefad115e4283f8afed07035c639e3d252140f9c4b69a3

Before: "release_sha256": "766715ba86c3a08fdb10e6805c0349d3401da17eaad45e5fce6dd32f5427a76f",

After: "release_sha256": "d83c366b2b9d31c842eefad115e4283f8afed07035c639e3d252140f9c4b69a3",

Before: "manuscript_sha256": "cd03a23ed34995614d310741a37325646f10708fd225fb6c830f15237e4868ff", / "review_sha256": "bbee69a85a3b601474d28332cf436e9d0d021c276b38e739fe081cba70399551",

After: "manuscript_sha256": "90a3950d494604eb60f1ad89da6bb2ebd67df187004c13625d5084a1f5dc0522", / "review_sha256": "087d45204abad5fd3db9dfb5b83a7e244191c0b4824a2f1e96f00107529fb82e",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 43f5f12e3671), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (18 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 43f5f12e3671), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 18 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 43f5f12e3671); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 43f5f12e3671); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: bbee69a85a3b601474d28332cf436e9d0d021c276b38e739fe081cba70399551

After: 087d45204abad5fd3db9dfb5b83a7e244191c0b4824a2f1e96f00107529fb82e

### sglt2-primary-prevention-hf

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: e7fc12147d90a61b

After: d9c8417d381cf767

Before: b4b8d2abd3ce2c7b18f158dd61be5bb544e618e50d521af21aa5e8f743fea529

After: acacf4b55aac6850b3c2954cba0a8e824f02aab75ce0c478a61e6453e9a6df12

Before: "release_sha256": "b4b8d2abd3ce2c7b18f158dd61be5bb544e618e50d521af21aa5e8f743fea529",

After: "release_sha256": "acacf4b55aac6850b3c2954cba0a8e824f02aab75ce0c478a61e6453e9a6df12",

Before: "manuscript_sha256": "d92d57201a30ca2efd17a479d44dea3beac38e3936df94109ecd3d216db92b49", / "review_sha256": "e7fc12147d90a61b79e39b696cc780b62d633b2fcd06b79332b826c90c08f096",

After: "manuscript_sha256": "b9422abfdda3e0cda89dc0e505657af4fbb2f1635d4b4c3e68c9a737e622e9a4", / "review_sha256": "d9c8417d381cf7671491ad7d6b5211ecb6c46364f1ca528beb4e2cd928474059",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). Records were screened by two independent rule screeners with adjudication (294 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 04902ecfbb6d), so precedence of protocol over synthesis is not demonstrated here. The registry-first (AACT) adapter did NOT complete for this topic (status RAN_ERROR); the evidence set was assembled by known-item retrieval, NOT a completed registry-first or systematic search (retracted claim). The screening log contains 294 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 04902ecfbb6d); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: e7fc12147d90a61b79e39b696cc780b62d633b2fcd06b79332b826c90c08f096

After: d9c8417d381cf7671491ad7d6b5211ecb6c46364f1ca528beb4e2cd928474059

### spironolactone-hfref-mortality

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: c9fde106b731b623

After: 51b8c845c360b856

Before: d234d70245f495533720568fb27ea02868a025ca9bd82e3e1df4f7752c74751c

After: 39fd2da4d4b2e8211ab7a041ef3bc17698c0c07fdcd965937ec0bb274bf63cd1

Before: "release_sha256": "d234d70245f495533720568fb27ea02868a025ca9bd82e3e1df4f7752c74751c",

After: "release_sha256": "39fd2da4d4b2e8211ab7a041ef3bc17698c0c07fdcd965937ec0bb274bf63cd1",

Before: "manuscript_sha256": "75f758244fc4b454dfdeca59aa66c811c9b1438ce0d580b8058cb6d8afbef84e", / "review_sha256": "c9fde106b731b623e2be04b1f7af2258b029b0618c75d3fbeb8fbea4135d8ffe",

After: "manuscript_sha256": "9c5bd3181ecf86c522825b4772326c29b113e4f7d293fe290a8cf8d0cae2f2d7", / "review_sha256": "51b8c845c360b8568f39a0e7daebc46d24557a1dcb9740b6a7d8f55db4aa0655",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 768c98fb5399), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (226 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 768c98fb5399), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 226 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 768c98fb5399); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 768c98fb5399); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: c9fde106b731b623e2be04b1f7af2258b029b0618c75d3fbeb8fbea4135d8ffe

After: 51b8c845c360b8568f39a0e7daebc46d24557a1dcb9740b6a7d8f55db4aa0655

### statins-primary-prevention-elderly

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 019f28727ea36026

After: 04cb86e6e6010166

Before: a7a250d816b1fbadd7e4b52ea14a2f306581df209bc911dda66f3ca3674cd24b

After: b60e7194fd3f66302f864782cb9f537bdc58097ac76df61866a965e5afa99100

Before: "release_sha256": "a7a250d816b1fbadd7e4b52ea14a2f306581df209bc911dda66f3ca3674cd24b",

After: "release_sha256": "b60e7194fd3f66302f864782cb9f537bdc58097ac76df61866a965e5afa99100",

Before: "manuscript_sha256": "3a01d56600124de5a5d5bdffc8596e9cedfdbb724bc1b2b662346c48682badd0", / "review_sha256": "019f28727ea36026b97c3d77a1f93df21c146637a06902bfbf836e7cd3edc720",

After: "manuscript_sha256": "2f1d6887d3f7ce405c1daaf5d5a44cc738318e9f4dc98fe1fd331e2dc00080d9", / "review_sha256": "04cb86e6e6010166bbb35e3728a74c30b3b482968704f90e5559c1edb31702cd",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 036ee46c6c45), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (28 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 036ee46c6c45), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 28 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 036ee46c6c45); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 036ee46c6c45); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 019f28727ea36026b97c3d77a1f93df21c146637a06902bfbf836e7cd3edc720

After: 04cb86e6e6010166bbb35e3728a74c30b3b482968704f90e5559c1edb31702cd

### ticagrelor-vs-clopidogrel-acs

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 759ecb61f51056be

After: ce7e0d4dc32d2f28

Before: 65c91750d3a26100f0bfbf2a9d41f23b553cb27dce715b2e338c9e33607c0d52

After: 33f4c2d7afed33490ba8ab282e3a12d04a75ac776879146ff8e116786ba24dc8

Before: "release_sha256": "65c91750d3a26100f0bfbf2a9d41f23b553cb27dce715b2e338c9e33607c0d52",

After: "release_sha256": "33f4c2d7afed33490ba8ab282e3a12d04a75ac776879146ff8e116786ba24dc8",

Before: "manuscript_sha256": "0df0f075536cf3665555413dae238757ee5b8de7af0340e6bc3bbe74d4bd3471", / "review_sha256": "759ecb61f51056be428d32ad1bc86868c333b88df1f32288d1388c17060f5492",

After: "manuscript_sha256": "2e8e3b0f17ef9372fcfde97c5d7e7eca202e808962fa60c841fd5fec2d2a4e4a", / "review_sha256": "ce7e0d4dc32d2f28f83fe85d3aafd1788b153501ec01e4e3940acf8cb241747e",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (32 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 3fb64a1e0143), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 32 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 3fb64a1e0143); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 759ecb61f51056be428d32ad1bc86868c333b88df1f32288d1388c17060f5492

After: ce7e0d4dc32d2f28f83fe85d3aafd1788b153501ec01e4e3940acf8cb241747e

### tocilizumab-covid19-mortality

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: bc9c2fc12ed92a37

After: 97be93ad858368fe

Before: a767b6ba0d7385ce304a1020b77e4ee7423b6c23b5ed2756cf261cc1bf272049

After: f0684b777863b2a89005628a6fe23eb9e99ad227a980f62df03ccbbc4d35e090

Before: "release_sha256": "a767b6ba0d7385ce304a1020b77e4ee7423b6c23b5ed2756cf261cc1bf272049",

After: "release_sha256": "f0684b777863b2a89005628a6fe23eb9e99ad227a980f62df03ccbbc4d35e090",

Before: "manuscript_sha256": "58a6d3279a41d67cfb05beeeb330e898e514dde269f4687db78b5fd42d436765", / "review_sha256": "bc9c2fc12ed92a37f397360318e516699dcf40d408184975a0bcdfb79b8e9071",

After: "manuscript_sha256": "9468e75ea76107977a62b3580dca5068a3b07a55f18571719ef81708c1e89068", / "review_sha256": "97be93ad858368fe44c5cc34e30b9f1f1e5bf1ab2d350820b7b908d786f0e856",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 38478f5e060a), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (50 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA 38478f5e060a), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 50 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 38478f5e060a); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA 38478f5e060a); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: bc9c2fc12ed92a37f397360318e516699dcf40d408184975a0bcdfb79b8e9071

After: 97be93ad858368fe44c5cc34e30b9f1f1e5bf1ab2d350820b7b908d786f0e856

### tranexamic-acid-pph

Build exit: 0; outcome objects identical: True. Changed top-level fields: reproduction, limitations.

Before: 1e61ef3c48229b43

After: be4f1da221cd65d2

Before: e145c9cd7f774084546b78016c2093b60f3727f0a4711a37167f425f5a9c3c21

After: a97bcc321f7ab18a5d846735063c5e58cfffe2ccf64e6460c6fd0dd1341acbf1

Before: "release_sha256": "e145c9cd7f774084546b78016c2093b60f3727f0a4711a37167f425f5a9c3c21",

After: "release_sha256": "a97bcc321f7ab18a5d846735063c5e58cfffe2ccf64e6460c6fd0dd1341acbf1",

Before: "manuscript_sha256": "ecbe9d87b35f4f27f262aa40162574949d9ce90e7a273dbc13e1079aaf313eb3", / "review_sha256": "1e61ef3c48229b4306a6caa352667870fcb39b1b2c239d28a106e5b371099088",

After: "manuscript_sha256": "71f8797dcac7e6a282d50b9a87ca0f3f5ed9263b3ef7c3eea8b29693439acd6d", / "review_sha256": "be4f1da221cd65d2ce8ba78f5cbb0d06eb626324d5afe673ae5e9a51e30ba3b7",

Before: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA dcb1b98082b6), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. Records were screened by two independent rule screeners with adjudication (76 records assessed); every pooled number was extracted down a source ladder and verified against its committed source. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

After: This review is NOT prospectively registered in this repository: the protocol first entered the repository inside a build commit (SHA dcb1b98082b6), so precedence of protocol over synthesis is not demonstrated here. The evidence set was assembled from PubMed/ClinicalTrials.gov retrieval. The screening log contains 76 records. Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. (Deterministic replay establishes that the same committed cache produces the same page; it does not validate search completeness or extraction, and byte-for-byte reproduction from the protocol SHA is not currently claimed — see Data availability.)

Before: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA dcb1b98082b6); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Two independently implemented rule screeners ran with adjudication. Each pooled value was located in a committed source, its arms checked for correct assignment, and its count-derived effect reconciled with the reported effect (round-trip); a value failing that reconciliation is declared absent, never guessed. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

After: This manuscript is generated deterministically from the review object; every number below is interpolated from a committed field. Deterministic replay is from the committed cache; protocol-commit byte reproduction is not claimed. The protocol first entered the repository inside a build commit (SHA dcb1b98082b6); the PICO is fixed, but this repository's history does not demonstrate that the protocol preceded synthesis, and byte-for-byte reproduction from that SHA is not currently claimed. Eligibility is by population, intervention, comparator and design (the registered rule) -- never on whether a trial reported the outcome (non-reporters are declared absent, not screened out). Every pooled row carries a positive source-digit verification state. This does not establish correct arm assignment, outcome identity or independent verification. ARM_ASSIGNMENT_UNPROVEN: the manuscript does not infer arm assignment or round-trip reconciliation from a source-digit verification flag. Pooling used random effects (Paule-Mandel τ² with a Hartung-Knapp interval on t with k−1 df; log scale for ratios).

Before: 1e61ef3c48229b4306a6caa352667870fcb39b1b2c239d28a106e5b371099088

After: be4f1da221cd65d2ce8ba78f5cbb0d06eb626324d5afe673ae5e9a51e30ba3b7

## Files changed

- `harness/index.py`
- `harness/manuscript.py`
- `harness/limitations.py`
- `harness/propositions.py`
- `harness/compat_check.py`
- `scripts/assertion_literal_sweep.py`
- `tests/test_assertion_literals.py`
- `registry/assertion_literal_adjudications.json`
- `harness/assertion_literal_limb.py`
- `docs/assertion_literal_sweep.json` and `docs/assertion_literal_validation.json`
- `.tmp/lit/` evidence, logs, scripts and scratch output; `.tmp/patches/` handoff diffs
- `LANE-LITX-REPORT.md`; ignored `PROGRESS.md` checkpoint

No project status or submission state was promoted. The portfolio index and protected rewrite workbook were read, not changed. No commit.

## Final validation notes

0 of 311 findings are UNADJUDICATED.
The full run exposed five index-display regressions from overly terse replacement prose. Computed PRISMA cells, judge margins, exact-match ratios and definition-audit ratios were restored with explicit historical-record attribution. Rerun: `python -X utf8 -m pytest tests/test_index_numbers.py tests/test_stage_additions.py::test_error_rate_banner_numbers_are_object_derived tests/test_stage_additions.py::test_definition_audit_index_numbers_derived -q -p no:cacheprovider` → **9 passed in 26.18s**. This is a targeted rerun, not a new full-suite green claim.
Remaining blockers and exact full-suite failed test names: `.tmp/lit/STUCK_FAILURES.md`. Browser tests were blocked by the strict socket guard. Served-page/certificate mismatches require the integrator’s real regeneration; a stale fix-ledger snapshot is separately reported. The full test run rewrote only line endings in docs/compat_direction_sweep.json; its original HEAD bytes were restored.
The read-only reference detector disappeared during the session after the initial import comparison. Its pre-change source was reconstructed by reversing only the recorded detector edits and verified against imported source SHA-256 `f5f154e7f3701ef9f0de4ae36165325723251fa323ad81514eccb2ee674cad8e` before executing pre-fix plants. Pin: `.tmp/lit/detector-before.py`.
The front-page preview is `.tmp/lit/docs/index.html`; its measured visible-text diff is `.tmp/lit/index-text-changes.json`. It uses the held docs sidecars and never writes docs/index.html.
