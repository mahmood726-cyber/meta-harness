# LANE IN4 — stopped at the required page-build refusal

**MEASURED: partial integration; not a completed landing. The mandatory stop condition fired while rebuilding `colchicine-postop-af`. No gate was weakened. No commit, staging, network retrieval, push, or deployment.**

Base and final HEAD: `55b457f5b17f0959f3aa37d9ce6c6e29c45b678d`. `git diff --name-only --cached` is empty. The session index and workbook were read and not edited; no project/submission status was promoted.

## Mandatory stop — verbatim

Command: `python scripts/build_topic.py colchicine-postop-af --now 2026-09-11`.

The prompt says: “for any page the gate refuses, paste the violation verbatim and stop there — never weaken the gate.” The build's canonical-claim gate refused this page. Implementation, rebuilding and further verification stopped at that refusal. Subsequent commands only measured the existing artifacts for this report.

```text
Traceback (most recent call last):
  File "C:\mh-r-IN4\scripts\build_topic.py", line 106, in <module>
    main(args[0], now)
    ~~~~^^^^^^^^^^^^^^
  File "C:\mh-r-IN4\scripts\build_topic.py", line 68, in main
    manifest = build_review_dir(core, manifest_meta, review_dir, protocol_sha, from_cache=True)
  File "C:\mh-r-IN4\harness\census.py", line 211, in build_review_dir
    raise ValueError(
        "CLAIM-OBJECT CONTRADICTION (build refused): a rendered surface asserts a significance "
        "opposite to the canonical claim object -> " + json.dumps(_cc["contradictions"]))
ValueError: CLAIM-OBJECT CONTRADICTION (build refused): a rendered surface asserts a significance opposite to the canonical claim object -> [{"outcome": "Postoperative atrial fibrillation", "surface": "outcome block", "canonical": "not significant (neither the HKSJ nor the common-effect interval excludes the null)", "found": "asserts significant / excludes null"}]

```

INFERRED: the integrated rendered outcome block and canonical significance object disagree. This report does not attribute the defect to a particular lane without further investigation. The check was not relaxed, the canonical result was not overwritten, and the rendered assertion was not silently removed after refusal.

## Step 1: content verification, not count equality

Applied `git diff --binary f6f7b14c 2f8705a8` with `git apply --3way`. Patch bytes were written by Python, avoiding PowerShell redirection encoding. The sandbox makes `.git` read-only, so the three-way application used `.tmp/integration.index` and `.tmp/git-objects`, with the real object store as a read-only alternate. The real index remains unchanged.

MEASURED before importing later lanes: **186 of 186 delta paths exist; 176 of 186 are byte-identical to `git show 2f8705a8:<path>`**. The remaining 10 paths are listed below. This is exact byte comparison, not LF normalization. The patch produced 11 conflicted paths; four generated GLP-1 files were resolved to the incoming bytes, while three clean three-way merges also retain landing-3 differences. The number changed against the base was not used as a gate.

Evidence: `.tmp/wip9.patch`, `.tmp/apply.log`, `.tmp/wip9-files.txt`, `.tmp/step1-conflicts.json`, `.tmp/step1-byte-exceptions.json`, `.tmp/resolve_step1.py`.

| Byte exception | Landing-3 content retained | Incoming content retained / explicit resolution |
|---|---|---|
| `cache/glp1-ra-mace-t2d/verified_effects.json` | Non-primary harm rows and typed refusals | Document-backed primary effects; combined by source identifier and outcome |
| `docs/evidence/hm3-held-source-audit/aact/manifest.json` | Corrected LF table digests and `hash_encoding` | Incoming old CRLF digests deliberately superseded, not combined into contradictory hashes |
| `docs/evidence/override-audit-2026-09-14/overrides.json` | Entries absent from incoming audit | Incoming entries merged on topic/file/trial/outcome |
| `harness/eligibility_chain.py` | `COMPAT_AXES` and compatibility checks | Topic-registry import and incoming logic |
| `harness/index.py` | Historical-only error-audit explanation and current-unrechecked numeral | Incoming index/provenance changes |
| `harness/manuscript.py` | Admission follow-up and endpoint evidence | Trial ID/label evidence text |
| `harness/page.py` | `AACT_NOT_MEASURED` warning | General strand rendering appended, not replacing the warning |
| `harness/pipeline.py` | Eligibility contract, outcome-specific verified-input selection, source import, cache-only decorator | Typed-effect targets/coercions and declared-strand machinery |
| `harness/verify.py` | Spelled integer normalization through nineteen | Incoming numeral matching; overlapping small-integer support retained |
| `tests/test_gate.py` | Deterministic synthetic harms-refusal plant | Incoming typed-effect gate plants |

The four generated `docs/reviews/glp1-ra-mace-t2d/{review.json,index.html,manifest.json,REPRODUCTION.json}` conflicts initially took incoming bytes pending rebuild. Those outputs were subsequently regenerated during the successful GLP-1 smoke build. The previous attempt's resolution script was inspected and reused; its erroneous changed-file-count stopping rule was not reused.

## Step 2: working-tree imports and hand resolutions

Each inventory was read from the source lane's `git status --short --untracked-files=all`, excluding only the specified lane runtime/prompt/temp paths. Reports were read first. The completion blocks of FIX1 and GS both contain `tokens used`, followed by the final response; both were imported. No superseded TYP lane import was added.

| Lane | Accounted paths of eligible status paths | Evidence |
|---|---:|---|
| CGX4 | 13 of 13 | `.tmp/CGX4/inventory.json` |
| FIX1 | 23 of 23 | `.tmp/FIX1/inventory.json` |
| FNC | 190 of 190 | `.tmp/FNC/inventory.json` |
| GS | 244 of 244 | `.tmp/GS/inventory.json` |

These counts mean every status path has an explicit copy/merge/port disposition, not that every final file is identical to an older lane. Source `STUCK_FAILURES.md` files were retained separately under `outputs/lane_reports/*-STUCK_FAILURES.md`. Working-tree bytes were the incoming side of three-way file merges, using each lane's HEAD as its baseline. Generated outputs were imported provisionally and are not all rebuilt.

Hand resolutions:

- CGX4 `page.py`: use registered absent-trial rendering while retaining landing-3 evidence fields in the decision object; append registered strand rendering after the AACT warning.
- FIX1 `absence.py`: retain landing-3 recognized-code/located-span refusal validation, followed by FIX1's binding-axis refusal classification.
- FNC `page.py`: retain the typed selection ledger; add the family count-chain record and family table; do not restore the older unregistered screening summary.
- FNC `glp1.py`: do not recreate the deleted page-named module. Port `_report_keys` to `strands.py`, retain source IDs in `pmid`, and use source/family aliases for declared membership and screening joins. Update the FNC join test to import `strands`.
- GS `claimgraph.py`: retain strict GRADE input validation plus upgrade arithmetic and named provisional domains.
- GS `grade.py`: replace old categorical caps with GS arithmetic/provisional handling; retain the existing conservative downgrade floor and family-aware RoB lookup.
- GS `page.py`: retain the newer typed `risk_prose` renderer, add a registered arithmetic record, and add GS validation and statistical-layer rendering.
- Pipeline integration: flatten dict/list verified-effect entries by outcome when constructing strand candidates; attach actual family IDs while keeping source-PMID joins. Persist freshly built GS cache objects. No primary numerical values or membership verdicts were assigned to match the prompt.
- Envelope/decomposer: reuse the existing topic-identifier registry instead of introducing page-slug literals. Add declared-strand all-candidate specifications labelled **censoring unverified; endpoint compatibility unverified**, retaining FACT checks. This last addition was not rebuilt on GLP-1 before the stop, so its numerical output is unmeasured.
- `claim_scope_sweep.py`: support the landing-3 dict-or-list verified-effect schema; every list row is counted and verified, none filtered out.

## Legacy prose migration and ratchet acknowledgement

`harness/integration_prose.py` supplies explicit INTERPRETATION objects with alternative formulations and recorded ledger judgements. It is registered through `remainder_prose.register`; there is no scanner whitelist, gate exemption, or auto-registration of arbitrary rendered text.

The sample-selection, partial-bias, dated-snapshot, enumeration, known-item-recovery, registry-landscape, correlated-screening, historical-integrity, dual-extraction and reproducibility boundaries were retained in qualified interpretations. Numeric ledger content remains in recorded objects; the comparator estimate is recorded metadata, not promoted to a newly verified FACT. The explicit `RETRACTED (round-2)` marker survives. No independent extraction/AI win or exhaustive publication claim is inferred.

Unsupported wording removed includes the entire AI-judged-win unit; “poolable unpublished data no published meta in this topic has”; and “No published meta-analysis reports an independent re-extraction of its own numbers.” Historical portfolio examples in the recall paragraph were not asserted as new evidence. The exact 12 old units replaced/removed are appended below so that the integrator can review the whole wording, including removed subordinate claims. **No ratchet acknowledgement was signed by this lane.**

## Builds and checks actually run

- `python -m compileall -q harness`: PASS after resolving imported conflict markers. A subsequent misplaced future-import edit initially failed compilation and was corrected before the successful GLP-1 build.
- GLP-1 smoke build: PASS after repairing the list-valued verified-effect integration error. This was before the final all-candidate envelope and GS-cache persistence changes.
- Ordered all-topic rebuild: balanced-crystalloids PASS; colchicine-postop-af REFUSED by the canonical-claim gate; sequence stopped. Thus **2 of 32 topics have a successful build in this lane**, counting the earlier GLP-1 smoke. This is not a full-current-tree rebuild claim.
- Focused command: `python -m pytest -q tests/test_strands.py tests/test_family_compact.py tests/test_lane_fix1.py tests/test_gs_layers.py --tb=short`: **34 passed, 4 failed**. It ran before completing the all-topic rebuild.

```text
FAILED tests/test_strands.py::test_harness_contains_no_topic_slugs
  eligibility_chain.py retains the landing-3 literal colchicine-postop-af.
FAILED tests/test_gs_layers.py::test_served_k8_numerical_reproduction_at_page_precision
  expected legacy k=8; rebuilt primary k=7.
FAILED tests/test_gs_layers.py::test_corpus_render_contract_and_tampered_sentence
  GLP-1 statistical layer/cache objects were not yet rebuilt after the latest integration.
FAILED tests/test_gs_layers.py::test_http_ui_contract
  the exact 'Unassessed domains:' presentation expected by GS is absent from the retained typed renderer.
4 failed, 34 passed in 49.57s
```

The synthetic two-strand refused-source plant passed in that run. The FIX1 tests passed. The failed tests were not weakened or marked skipped. UI/E2E is **FAIL**, not certified.

## Full standard run and ratchet output

**NOT RUN. There is no full `verify_all.py` table or ratchet output to paste.** The mandatory page-build refusal occurred first. Running onward or fabricating an 11-limb result would contradict the stop instruction or the evidence. All ordered renderer scripts, the index rebuild, the 32-page retraction-survival command and the full standard run remain unexecuted.

**Publication-gate pass count: unmeasured of 32 pages.** A successful build is not a full publication-gate PASS. One page-build gate refusal is measured; no claim that zero or any other number of full publication gates passed is made.

## Measured GLP-1 smoke artifacts

These numbers are read from the successful local smoke build, not the expected numbers in the prompt. They do not certify the latest working tree or the other pages.

| Strand | k | HR | 95% CI | tau² | PI |
|---|---:|---:|---|---:|---|
| CONVENTIONAL_GLP1RA | 7 | 0.88839568 | 0.82839280–0.95274475 | 0.00120019 | 0.79594142–0.99158916 |
| GLP1RA_ANY_DELIVERY | 8 | 0.89840832 | 0.81582303–0.98935368 | 0.00672622 | 0.72345850–1.11566527 |

Exact membership/refusal objects: `.tmp/report-measurements.json`. The estimates reproduce the prompt to its shown precision.

- CONVENTIONAL_GLP1RA members: 31185157, 27633186, 27295427, 31189511, 28910237, 26630143, SOUL.
- GLP1RA_ANY_DELIVERY members: 31185157, 27633186, 27295427, 31189511, 28910237, 26630143, SOUL, FREEDOM-CVO.

Refused candidate axes from the first strand:

- `34215025` / 34215025: `censoring` — UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD.
- `30291013` / 30291013: `endpoint_components` — axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion.
- `38785209` / FLOW: `censoring` — UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR.

Sensitivity-only values:

- FREEDOM-CVO: effect 1.36, CI 0.96–1.92; pooled=False.

Measured family count chain in the smoke artifact: `{"publications_screened": 13, "registry_records_screened": 234, "trial_families": 238, "eligible_families": 143, "contributing": 7, "eligibility_unresolved": 84, "contributing_without_structural_eligibility": ["NCT01147250"]}`. Its contributing count describes the imported outcome-family attachment, not the union of all strand membership; no equality to eight is forced.

GLP-1 `claim_scope_sweep` served scan (current registry against the smoke artifact):

```json
{
  "rendered_units": 2741,
  "with_object": 846,
  "with_object_by_class": {
    "INTERPRETATION": 30,
    "TRANSFORMATION": 339,
    "JUDGEMENT": 451,
    "FACT": 26
  },
  "structural_units": [
    {
      "unit_id": "unit-0005",
      "text": "Trial",
      "context": "html/body/main/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0006",
      "text": "Recorded membership decision",
      "context": "html/body/main/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0027",
      "text": "Trial",
      "context": "html/body/main/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0028",
      "text": "Recorded membership decision",
      "context": "html/body/main/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0099",
      "text": "sha",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0101",
      "text": "committed utc",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0103",
      "text": "method declared",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0105",
      "text": "eligibility",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0108",
      "text": "databases",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0110",
      "text": "cache ref",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0112",
      "text": "run utc",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0117",
      "text": "Kind",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0118",
      "text": "Query",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0119",
      "text": "Run date",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0120",
      "text": "State",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0121",
      "text": "hits -> fetched -> retained",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0122",
      "text": "Cap",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0123",
      "text": "Discovery-capable",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0154",
      "text": "Verbatim query",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0155",
      "text": "Kind",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0156",
      "text": "Features fired",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0182",
      "text": "Family ID",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0183",
      "text": "Acronym",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0184",
      "text": "Reports by role",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0185",
      "text": "Arms",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0186",
      "text": "Contrasts",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0187",
      "text": "Eligibility",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0188",
      "text": "Lifecycle",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-0189",
      "text": "Per-outcome status",
      "context": "html/body/main/section/section/div/table/thead/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1950",
      "text": "Id",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1951",
      "text": "Id type",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1952",
      "text": "Decision",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1953",
      "text": "Rule id",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1954",
      "text": "Found by",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1955",
      "text": "Trial family id",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1956",
      "text": "Publication role",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1957",
      "text": "Completeness state",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1958",
      "text": "Reason",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-1959",
      "text": "Span",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2093",
      "text": "Trial",
      "context": "html/body/main/section/div/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2094",
      "text": "Outcome",
      "context": "html/body/main/section/div/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2095",
      "text": "Recorded assessment",
      "context": "html/body/main/section/div/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2171",
      "text": "Trial",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2172",
      "text": "Id",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2173",
      "text": "Input",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2174",
      "text": "Source",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2259",
      "text": "Axis",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2260",
      "text": "PMID 31185157",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2261",
      "text": "PMID 27633186",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2262",
      "text": "PMID 27295427",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2263",
      "text": "PMID 34215025",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2264",
      "text": "PMID 31189511",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2265",
      "text": "PMID 30291013",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2266",
      "text": "PMID 28910237",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2267",
      "text": "PMID 26630143",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2268",
      "text": "PMID 40162642",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2269",
      "text": "PMID 38785209",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2270",
      "text": "population",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2281",
      "text": "randomised_contrast",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2292",
      "text": "analysis_set",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2303",
      "text": "endpoint_components",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2314",
      "text": "first_or_recurrent",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2325",
      "text": "time_origin",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2336",
      "text": "follow_up",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2347",
      "text": "censoring",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2358",
      "text": "effect_measure",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2369",
      "text": "adjustment",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2380",
      "text": "estimator",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2391",
      "text": "report",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2414",
      "text": "Estimand",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2416",
      "text": "Estimand decision",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2418",
      "text": "Method",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2420",
      "text": "k",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2422",
      "text": "Single-trial effect",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2424",
      "text": "Note",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2426",
      "text": "Leave-one-out (influence)",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2428",
      "text": "Effect-measure class",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2430",
      "text": "Effect label",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2431",
      "text": "Effect-measure labels pooled",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2432",
      "text": "Endpoint",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2434",
      "text": "Endpoint canonical status",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2436",
      "text": "Endpoint canonical components",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2437",
      "text": "Follow-up window",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2438",
      "text": "Analysis set",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2439",
      "text": "Declared analysis set",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2440",
      "text": "Heterogeneous key dimensions",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2442",
      "text": "Parser-confirmed contrast",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2444",
      "text": "Dimension",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2445",
      "text": "Trial",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2446",
      "text": "Derived value",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2447",
      "text": "Source span",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2453",
      "text": "Trial",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2454",
      "text": "Id",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2455",
      "text": "Input",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2456",
      "text": "Source",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2488",
      "text": "Axis",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2489",
      "text": "PMID 31189511",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2490",
      "text": "population",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2492",
      "text": "randomised_contrast",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2494",
      "text": "analysis_set",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2496",
      "text": "endpoint_components",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2498",
      "text": "first_or_recurrent",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2500",
      "text": "time_origin",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2502",
      "text": "follow_up",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2504",
      "text": "censoring",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2506",
      "text": "effect_measure",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2508",
      "text": "adjustment",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2510",
      "text": "estimator",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2512",
      "text": "report",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2516",
      "text": "Estimand",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2518",
      "text": "Estimand decision",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2520",
      "text": "Method",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2522",
      "text": "k",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2524",
      "text": "Single-trial effect",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2526",
      "text": "Note",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2528",
      "text": "Leave-one-out (influence)",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2530",
      "text": "Effect-measure class",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2532",
      "text": "Effect label",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2533",
      "text": "Effect-measure labels pooled",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2534",
      "text": "Endpoint",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2536",
      "text": "Endpoint canonical status",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2538",
      "text": "Endpoint canonical components",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2539",
      "text": "Follow-up window",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2540",
      "text": "Analysis set",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2541",
      "text": "Declared analysis set",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2542",
      "text": "Heterogeneous key dimensions",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2544",
      "text": "Parser-confirmed contrast",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2546",
      "text": "Dimension",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2547",
      "text": "Trial",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2548",
      "text": "Derived value",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2549",
      "text": "Source span",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2555",
      "text": "Trial",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2556",
      "text": "Id",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2557",
      "text": "Input",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2558",
      "text": "Source",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2587",
      "text": "Axis",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2588",
      "text": "PMID 27295427",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2589",
      "text": "population",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2591",
      "text": "randomised_contrast",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2593",
      "text": "analysis_set",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2595",
      "text": "endpoint_components",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2597",
      "text": "first_or_recurrent",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2599",
      "text": "time_origin",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2601",
      "text": "follow_up",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2603",
      "text": "censoring",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2605",
      "text": "effect_measure",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2607",
      "text": "adjustment",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2609",
      "text": "estimator",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2611",
      "text": "report",
      "context": "html/body/main/section/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2615",
      "text": "name",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2617",
      "text": "year",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2619",
      "text": "journal",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2621",
      "text": "pmid",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2623",
      "text": "doi",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2625",
      "text": "open access",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2627",
      "text": "url",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2641",
      "text": "Trial",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2642",
      "text": "Overall",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2643",
      "text": "Randomisation",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2644",
      "text": "Deviations/blinding",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2645",
      "text": "Missing outcome data",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2646",
      "text": "Outcome measurement",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2647",
      "text": "Selective reporting",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2698",
      "text": "Stratum",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2699",
      "text": "Re-pooled estimate",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2700",
      "text": "Full pool (all pooled trials)",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2702",
      "text": "Excluding high risk of bias",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2704",
      "text": "Low risk of bias only",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2768",
      "text": "Source estimate",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2786",
      "text": "Reporting item",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2787",
      "text": "Field presence rule",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2788",
      "text": "5 Eligibility criteria",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2790",
      "text": "6 Information sources and dates",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2792",
      "text": "7 Search strategy",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2794",
      "text": "8 Selection process",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2796",
      "text": "9 Data collection",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2798",
      "text": "15 Certainty assessment",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2800",
      "text": "16a Selection flow",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2802",
      "text": "16b Exclusions",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2804",
      "text": "24 Registration and protocol",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2806",
      "text": "failures",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2808",
      "text": "preregistration",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2810",
      "text": "protocol sha",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2812",
      "text": "review sha256",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2814",
      "text": "from cache",
      "context": "html/body/main/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2825",
      "text": "Specification",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2826",
      "text": "Choice",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2827",
      "text": "Result (tau2 beside I2)",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2874",
      "text": "Single change",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2875",
      "text": "Result",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2916",
      "text": "Replay step",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2917",
      "text": "Attribution",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2918",
      "text": "Result",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    },
    {
      "unit_id": "unit-2919",
      "text": "Delta log effect (null = unidentified)",
      "context": "html/body/main/div/section/table/tr/th",
      "rule": "short-semantic-table-header"
    }
  ],
  "structural_count": 194,
  "visible_units_before_structural_rules": 2935,
  "unit_contract": "conservative visible prose/table text runs; not an exact linguistic sentence count",
  "violation_counts": {
    "SENTENCE_WITHOUT_OBJECT": 1895
  },
  "examples_of_violations": 1895
}
```

Full violations and fresh-render comparison: `.tmp/glp1-scope-at-stop.json`. Family and statistical-layer prose add new scan debt; no zero-unregistered claim is made.

## Per-page FACT measurement at the stop

Denominator **N = pooled outcome rows in each on-disk review object, across all outcomes**, not unique trials and not every strand/sensitivity row. Numerator is rows passing `claimgraph.verify_fact` against held bytes. Most artifacts are imported/provisional; these are read-only measurements of the mixed stopped tree, **not 32 fresh builds**. Failed provenance rows remain visible as `UNVERIFIED_FACT`; no binding-axis or FACT gate was relaxed.

| Page | FACT n of N rows |
|---|---|
| balanced-crystalloids-vs-saline-mortality | FACT 0 of 3 rows |
| colchicine-postop-af | FACT 0 of 5 rows |
| colchicine-recurrent-pericarditis | FACT 0 of 3 rows |
| colchicine-secondary-cv-prevention | FACT 0 of 5 rows |
| corticosteroids-cap-mortality | FACT 0 of 4 rows |
| corticosteroids-covid19-mortality | FACT 0 of 1 rows |
| dapagliflozin-hfpef-hosp | FACT 0 of 1 rows |
| denosumab-vertebral-fracture | FACT 0 of 3 rows |
| doac-vte-recurrence | FACT 0 of 6 rows |
| dpp4-mace-t2d | FACT 0 of 3 rows |
| empagliflozin-hfpef-hosp | FACT 0 of 1 rows |
| esketamine-trd-madrs | FACT 0 of 4 rows |
| finerenone-ckd-t2d-renal | FACT 0 of 2 rows |
| glp1-ra-mace-t2d | FACT 7 of 9 rows |
| iv-iron-hfref-hosp | FACT 0 of 2 rows |
| melatonin-primary-insomnia-sol | FACT 0 of 1 rows |
| metformin-pcos-ovulation | FACT 0 of 3 rows |
| noac-vs-warfarin-af-stroke | FACT 0 of 8 rows |
| omega3-cardiovascular-events | FACT 0 of 8 rows |
| pcsk9-mace | FACT 0 of 3 rows |
| probiotics-aad-prevention | FACT 0 of 16 rows |
| sacubitril-valsartan-hfref | FACT 0 of 2 rows |
| semaglutide-obesity-mace | FACT 0 of 2 rows |
| semaglutide-obesity-weight | FACT 0 of 2 rows |
| sglt2-ckd-progression | FACT 0 of 4 rows |
| sglt2-hfref-hosp-cvdeath | FACT 0 of 2 rows |
| sglt2-primary-prevention-hf | FACT 0 of 4 rows |
| spironolactone-hfref-mortality | FACT 0 of 3 rows |
| statins-primary-prevention-elderly | FACT 0 of 2 rows |
| ticagrelor-vs-clopidogrel-acs | FACT 0 of 3 rows |
| tocilizumab-covid19-mortality | FACT 0 of 3 rows |
| tranexamic-acid-pph | FACT 0 of 2 rows |

## Static-versus-dynamic hardcode disclosure

| Static input / policy | Dynamic measurement | Limit |
|---|---|---|
| Prompt commit references and lane order | Git object bytes, source status inventories, merge results | No ref substitution or count-equality fiction |
| Typed limitation wording and alternative formulations | Stored ledgers remain explicit recorded judgements | Editorial wording is not new clinical evidence |
| Family reference schema and PMID/family join rules | Held family ingredients and source IDs | Regeneration/cohort preservation not rerun before stop; upstream PASS remains an upstream claim |
| Existing gate and synthesis policy | Gate refusal, actual smoke estimates, focused tests | No thresholds relaxed; no expected estimates injected |
| Named one-axis-at-a-time specifications | Inputs taken from actual strand candidates | Added all-candidate outputs not yet rebuilt/measured |
| FACT provenance requirements | Per-row held-byte checks shown above | Does not establish independent clinical validity or current retraction status |

## Recovery and unfinished work

The tree intentionally remains uncommitted and is not release-ready. `PROGRESS.md` is already ignored by `.gitignore`. `STUCK_FAILURES.md` records the blocking page and exact refusal. A subsequent authorized continuation needs to investigate the rendered/canonical contradiction at source, review the four focused failures, finish the current-tree rebuild, run ordered renderers and retraction survival, then run the full unchanged standard and obtain the integrator's ratchet signature. No additional work was performed to bypass this turn's explicit stop condition.

The final source-level release review of all identifiers/dates/statistical claims remains incomplete; only the documented FACT checks and measured smoke objects were inspected. No Overmind PASS or certification is claimed.

## Verbatim old prose units replaced / removed

### tab-overview / unit-0037

```text
Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.
```

### tab-overview / unit-0038

```text
Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.
```

### tab-overview / unit-0039

```text
Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.
```

### tab-overview / unit-0041

```text
The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.
```

### tab-search / unit-0009

```text
No search was run for this topic: every PubMed source is a PMID enumeration.
```

### tab-search / unit-0063

```text
Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.
```

### tab-search / unit-0064

```text
Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).
```

### tab-screening / unit-0003

```text
Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.
```

### tab-screening / unit-0004

```text
Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.
```

### tab-comparator / unit-0015

```text
Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94
```

### tab-reproduction / unit-0013

```text
Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.
```

### tab-reproduction / unit-0017

```text
RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.
```

