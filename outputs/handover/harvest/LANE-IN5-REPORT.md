# LANE IN5 — cache-only AACT reproduction

Base and current HEAD: `04902ecfbb6d1a9ab7904062c8f1683dfd9e9db9`.
No commit, staging, push, deployment, or network retrieval was performed.
The new cache files are working-tree artifacts ready for review, not committed files.

## Baseline plant (MEASURED before edits)

Requested command, verbatim:

```text
mkdir .tmp/empty_aact; AACT_DIR=<abs path of it> python scripts/reproduce_review.py
```

PowerShell equivalent executed on the base:

```powershell
New-Item -ItemType Directory -Force .tmp/empty_aact | Out-Null
$env:AACT_DIR=(Resolve-Path .tmp/empty_aact).Path
python scripts/reproduce_review.py
```

MEASURED: 1 of 32 live review pages reproduced. `metformin-pcos-ovulation`
was the sole pass. Each of the other 31 failed both the review hash and
the re-rendered HTML comparison:

```text
balanced-crystalloids-vs-saline-mortality
colchicine-postop-af
colchicine-recurrent-pericarditis
colchicine-secondary-cv-prevention
corticosteroids-cap-mortality
corticosteroids-covid19-mortality
dapagliflozin-hfpef-hosp
denosumab-vertebral-fracture
doac-vte-recurrence
dpp4-mace-t2d
empagliflozin-hfpef-hosp
esketamine-trd-madrs
finerenone-ckd-t2d-renal
glp1-ra-mace-t2d
iv-iron-hfref-hosp
melatonin-primary-insomnia-sol
noac-vs-warfarin-af-stroke
omega3-cardiovascular-events
pcsk9-mace
probiotics-aad-prevention
sacubitril-valsartan-hfref
semaglutide-obesity-mace
semaglutide-obesity-weight
sglt2-ckd-progression
sglt2-hfref-hosp-cvdeath
sglt2-primary-prevention-hf
spironolactone-hfref-mortality
statins-primary-prevention-elderly
ticagrelor-vs-clopidogrel-acs
tocilizumab-covid19-mortality
tranexamic-acid-pph
```

## Read-path audit and implementation

MEASURED by repository-wide AACT/import/table-read searches and caller inspection:

| Reachable input | Before | After |
|---|---|---|
| `pipeline._annotate_completeness` | `aact.study_dates`, `studies.txt` | Topic cache `values.study_dates` |
| `funding.scan_pooled` | `aact.sponsor_records`, sponsor/responsible-party tables | Topic cache `values.sponsors`; standalone callers use review slug |
| `screen.run` → `armcontrast.build_arm_index` | Three snapshot tables | Topic cache `values.arm_index`; screening source/rules untouched |
| `census.build_review_dir` | Core and render consumers | No direct snapshot reader found |
| `harms`, `design_key`, `arm_object`, `design_variance`, `scope_identity`, `eligibility_chain`, `source_hierarchy`, `second_source`, `comparator_*`, `verified_inputs` | Existing committed inputs / passed objects | No additional live AACT read found in this base |

`aact_cache.cache_only_build` scopes the measured inputs to one build and resets
the context afterward. Neither cache loading nor absent-cache handling discovers
a snapshot. Missing, malformed, wrong-topic or hash-invalid measurements produce
`aact_status=AACT_NOT_MEASURED`, rendered as a visible page banner. The original
arm-index snapshot adapter is now explicitly named `measure_arm_index`; its
measurement-script caller was updated. `harness/aact.py` remains measure-time code.

`python scripts/aact_measure.py [<slug> ...]` measures the selected topics, or
all live topics when no slug is supplied. It preflights the six required source
tables and their columns, uses the original adapters, and writes
`cache/<slug>/aact_inputs.json` with derived values, requested NCT keys, snapshot
folder name, source table/row keys, canonical source-row SHA-256 hashes, and a
whole-document integrity hash. No off-tree path is stored in those caches.

MEASURED: all 32 of 32 live topics measured from the local snapshot folder
`F:\AACT-storage\AACT\2026-08-30`. This is the snapshot folder label, not a
claim that every underlying record was current on that date.

An independent second pass streamed the original six tables and matched
10,448 of 10,448 distinct source rows by keys and SHA-256, covering 11,491
cached row references across the topic caches. Dates and registry identifiers
are covered by these whole-row hashes; no clinical values were hand-entered.

| Input / rule | Static or dynamic | Hardcode disclosure |
|---|---|---|
| Source-table names and required column names | Static schema | Interface contract, not research findings |
| Snapshot selection | Dynamic at explicit measurement | Existing AACT_DIR / adapter discovery; no new machine path in code |
| Dates, sponsors, arm sets, row hashes | Dynamic at measurement, then static cache | Derived from actual snapshot rows using original transformations |
| Review results and HTML | Dynamic build from static topic inputs | No hardcoded outputs or simulated research data |
| Absence code | Static typed state | AACT_NOT_MEASURED; no snapshot fallback |

## Reproduction and regression results

MEASURED:

| Check | Result |
|---|---|
| Empty-AACT replay | 32 of 32 live review pages reproduced |
| Snapshot-present replay | 32 of 32 live review pages reproduced |
| Review hash and HTML | Both runs match the existing base artifacts |
| Number movement | 0 of 32 live review pages; no review rebuild required |
| Targeted cache/funding/arm-contrast tests | 32 of 32 tests passed |
| Source-row second pass | 10,448 of 10,448 distinct source rows matched |
| Repeat measurement | 32 of 32 cache files byte-identical |
| Expanded targeted regression suite | 40 of 40 tests passed with empty AACT_DIR |

The targeted tests include a real-topic replay with all snapshot entry points
patched to raise, missing-cache rendering without snapshot access, invalid-hash
rejection, and provenance coverage for every live topic.

Local reproduction logs: `.tmp/replay-empty.log`, `.tmp/replay-snapshot.log`.
No `NUMBER MOVED` case was observed. Since both review cores and HTML remain
identical, no review artifact or statistical result was replaced.

## Playwright

All 3 of 3 test modules importing Playwright (`test_hm1_ui.py`,
`test_hm2_ui.py`, `test_in3_ui.py`) now call this before importing its API:

```python
pytest.importorskip("playwright", reason="browser E2E; not installed in CI")
```

Playwright is installed locally. A separate import-unavailable CI simulation
(with external pytest plugin autoload disabled, since the local Playwright
plugin also imports Playwright) measured 3 skipped of 3 selected browser modules:

```text
SKIPPED [1] tests/test_hm1_ui.py:8: browser E2E; not installed in CI
SKIPPED [1] tests/test_hm2_ui.py:10: browser E2E; not installed in CI
SKIPPED [1] tests/test_in3_ui.py:9: browser E2E; not installed in CI
3 skipped in 0.34s
```

No tests were removed or hidden behind try/except.

The first full verification also exposed three legacy tests reading off-tree
AACT directly: two D5 tests and the completeness-state test. The D5 tests now
re-derive from the existing `rob2.json` registered primary/secondary input
lists, not from saved verdicts. The completeness test reads the new measured
dates cache. Their assertions are unchanged. No screening implementation or
eligibility rule was changed.

## Protocol-identity blocker observed in full verification

MEASURED: 8 of 32 manifest protocol SHAs differ from `registration.protocol_sha`
on this base: colchicine-postop-af, colchicine-secondary-cv-prevention,
esketamine-trd-madrs, metformin-pcos-ovulation, noac-vs-warfarin-af-stroke,
probiotics-aad-prevention, sglt2-ckd-progression, sglt2-primary-prevention-hf.

For the NOAC gate regression, the manifest SHA is
`876acb8be1d610715286042396952dccb50942e1`, while current protocol history resolves
to `04902ecfbb6d1a9ab7904062c8f1683dfd9e9db9`. Rebuilding its core once with each
anchor changes only the `protocol` top-level field. Standalone reproduction
uses the manifest anchor; the publication gate uses current protocol history.
The protocol files, manifests, registration code and gate are untouched.
This pre-existing difference is reported, not hidden by changing the gate or
rebasing published review identities.

## Full verification

All requested renderer commands completed with exit 0, in this order:
`render_fix_ledger.py`, `rewrite_fixstate_lines.py`, `build_evidence_index.py`,
`render_gate_gaps.py`, `render_gate_scorecard.py`, `external_agreement.py`,
`python -m harness.index docs`.

`python scripts/verify_all.py` completed with empty AACT_DIR and a task-local
external-socket/DNS prohibition (localhost remained allowed for browser tests).
MEASURED: 8 of 11 verification limbs PASS; 3 of 11 REFUSED, exit 1.

| Full verification limb | Result |
|---|---|
| Unit tests | REFUSED: initial run 4 failed, 909 passed; 0 skipped of 913 test outcomes |
| Offline reproduction | PASS: 32 of 32 live pages |
| Publication gate | REFUSED: 8 of 32 pages, protocol SHA mismatch |
| Index currency | PASS |
| Served-artifact leak scan | PASS |
| Held-out leak detector | PASS |
| Search completeness | PASS |
| Fix-state discipline | PASS |
| Honest-state ratchet | REFUSED: 3 page count reductions against its historical baseline |
| Gate scorecard | PASS |
| Gate gaps table | PASS |

The full local pytest run executed the browser tests (Playwright installed).
Three snapshot-dependent test failures were then fixed and passed the expanded
40-test regression run. The protocol-identity gate regression remains refused.
The final full pytest run with Playwright unavailable is recorded below.

Honest-ratchet output, verbatim from the full verification run:

```text
TARGET honest_ratchet: head=04902ecfbb6d1a9ab7904062c8f1683dfd9e9db9 base=2304824034b4ba8677da2d2d2453352711ed2a9b tree=dirty:53 files files=34 docs/index.html docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html docs/reviews/colchicine-postop-af/index.html ... base_resolution=merge-base origin/main pages=33 block_floor_refs=2304824034b4ba8677da2d2d2453352711ed2a9b,50f5a67b4fb19ada4716a0df6e6b68c2e4618304
docs/reviews/balanced-crystalloids-vs-saline-mortality/index.html: not_assessed: base count 10, new count 6
docs/reviews/esketamine-trd-madrs/index.html: declared_absent: base count 12, new count 11
docs/reviews/probiotics-aad-prevention/index.html: not_assessed: base count 34, new count 24
```

These pages are byte-identical to this lane's base, so the default ratchet's
reductions precede this lane. No ratchet acknowledgement or bypass was added.
Full output is retained in `.tmp/verify-7.log`; unresolved findings are also
recorded in `STUCK_FAILURES.md`.

Supplementary measured check: `python -m harness.honest_ratchet --base HEAD`
returned `honest-state ratchet: PASS` against
`04902ecfbb6d1a9ab7904062c8f1683dfd9e9db9`. This demonstrates no lane-local
disclosure regression; it does not replace the default-baseline REFUSED verdict.

INFERRED: once the reviewed new cache files are committed by the integrating
owner, they remove the off-tree AACT dependency from clean-checkout replay.
CLAIMED coverage is limited to the 32 live topics and checks listed above;
no clean-clone result at a new commit, release PASS or deployment is claimed.

## Final pytest and working-tree checks

MEASURED: complete suite with empty AACT_DIR, external networking blocked, Playwright unavailable via an import hook, and external pytest plugin autoload disabled:

```text
1 failed, 909 passed, 3 skipped in 331.97s (0:05:31)
```

3 skipped of 913 pytest test/collection outcomes (module-level browser skips count as collection outcomes). All three skips state `browser E2E; not installed in CI`. The sole remaining failure is `tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate`, the pre-existing protocol-anchor mismatch described above. No snapshot-read test remains failing.

The full verify_all table above is the actual complete run, not a synthesized PASS. Its three test-input failures were subsequently repaired and checked by the final full pytest run; the unit-test limb still refuses because the protocol gate test remains failing. Gate and ratchet refusals were not bypassed.

Final scope check: no diffs in review artifacts, synth.py, gate.py, screening, membership or search implementation; no staged changes; HEAD unchanged. Generated JSON files with only newline differences were restored to their original bytes. The substantive generated change is docs/fix_ledger.json, refreshed by the requested renderer.
