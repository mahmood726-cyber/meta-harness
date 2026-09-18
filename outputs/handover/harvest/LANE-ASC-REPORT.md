# LANE ASC report

Base and final HEAD: `237e90946f5b257265b0a3b1c986a8907d12eded`. No commit. No network. No reset, checkout or stash. Tracked docs unchanged.

## MEASURED

Both plants fail on the checked-in served page and pass on the scratch rebuild. All 32 of 32 reviews rebuilt into `.tmp/asc/docs/` using direct committed-cache reads with sockets blocked and `AACT_DIR=.tmp/empty_aact` (existing and empty).

Ascertainment: 0 of 11 checked-in GLP-1 screening records carried the claimed state; 11 of 11 rebuilt records now carry UNRESOLVED with basis B-prime. Axis applicability is parsed by the existing protocol compiler. Undeclared axes are NOT_AN_AXIS; an unparsable clause is conservatively UNRESOLVED with an explicit code. Screening decisions are unchanged.

Funding: the prompt's assertion that the all-outcome union is 9 is contradicted by this base's actual outcomes. The union is 8 and the primary pool is 8. The stored funding list contains 9 rows, including PMID 26630143, absent from all current outcome pools. The new disclosure selects current pooled members, so it renders 8 of 8 known and 0 unknown. The stored funding evidence remains intact; the view excludes the stale row. This is a scope correction, not a change to any research result.

Source-level second pass: 11 of 11 GLP-1 screening identifiers map to committed records.json after removing the display-only acronym prefix. Outcome objects (including identifiers, dates and numeric results) are unchanged on 32 of 32 rebuilt reviews. Screening objects excluding the new axis field are unchanged on 32 of 32. See `.tmp/asc/second-pass.json`.

## INFERRED

The extra funding row is consistent with funding being scanned before a later outcome-membership gate removes that trial. The renderer now intersects funding evidence with final outcome membership, and supplies an explicit unknown entry if a current pooled member has no funding row.

## CLAIMED / limits

No ascertainment is claimed ESTABLISHED: the current machine-screen path consumes no held ascertainment adjudication. No establishment is inferred from result availability, trial status, or a generic screening span. Future establishment requires a verified held span; this lane does not invent an evidence adjudicator. No release, certification or Overmind PASS is claimed.

## Hardcode disclosure

| Item | Static / dynamic | Source and validation |
| --- | --- | --- |
| State vocabulary / fallback code | Static policy | UNRESOLVED, NOT_AN_AXIS; unparsable clause fails closed |
| Axis and basis | Dynamic | protocol_compiler.eligibility_clause; protocol applicability tests |
| n of N state sentence | Dynamic | screening.records; mixed/missing-state regression |
| All-outcome and primary denominators | Dynamic | normalized union of outcomes[].trials IDs; duplicate and stale-row regression |
| Funding classification | Existing source-derived evidence | Current-pool membership selects stored funding objects |
| Test fixtures | Static, explicitly synthetic | Only structural fixture IDs; never served research data |
| Replay date | Static build metadata | 2026-09-18; no study date changed |

## Plants: pre-fix failures

Command: `AACT_DIR=.tmp/empty_aact ASC_DOCS_ROOT=docs python -m pytest -q tests/test_screen_ascertainment_state.py tests/test_funding_denominator.py` (environment set with PowerShell).

```text
FF                                                                       [100%]
================================== FAILURES ===================================
_______________ test_served_ascertainment_claim_matches_records _______________

    def test_served_ascertainment_claim_matches_records():
        review, page = served_pair()
        text = visible_text(page)
        records = review["screening"]["records"]
        n = sum(row.get("outcome_ascertainment", {}).get("state") == "UNRESOLVED" for row in records)
        if "records as UNRESOLVED per record" in text:
>           assert n == len(records), f"served claim says per record, but UNRESOLVED is recorded on {n} of {len(records)}"
E           AssertionError: served claim says per record, but UNRESOLVED is recorded on 0 of 11
E           assert 0 == 11
E            +  where 11 = len([{'completeness_basis': 'CT.gov status/results dates from local AACT snapshot', 'completeness_state': 'eligible+comple...ness_state': 'eligible+completed+results_available', 'completion_date': '2018-03-14', 'decision': 'include', ...}, ...])

tests\test_screen_ascertainment_state.py:38: AssertionError
______________ test_served_funding_denominator_names_both_pools _______________

    def test_served_funding_denominator_names_both_pools():
        review, page = served_pair()
        outcomes = review["outcomes"]
        union = {str(t["id"]).removeprefix("PMID ").strip()
                 for o in outcomes for t in o.get("trials", [])}
        primary = next(o for o in outcomes if o.get("primary"))
        k = primary["result"]["k"]
        text = visible_text(page)
        expected = f"{len(union)} trials pooled across all outcomes; {k} in the primary pool"
>       assert expected in text, f"served funding sentence omits scope: expected {expected!r}"
E       AssertionError: served funding sentence omits scope: expected '8 trials pooled across all outcomes; 8 in the primary pool'
E       assert '8 trials pooled across all outcomes; 8 in the primary pool' in "GLP-1 receptor agonists vs placebo for 3-point MACE in type 2 diabetes *{box-sizing:border-box}body{font:15px/1.55 sy...gle('active',b.dataset.t===id)});} (function(){var f=document.querySelector('nav button');if(f)show(f.dataset.t);})();"

tests\test_funding_denominator.py:14: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_screen_ascertainment_state.py::test_served_ascertainment_claim_matches_records
FAILED tests/test_funding_denominator.py::test_served_funding_denominator_names_both_pools
2 failed in 5.32s
```

## Plants: post-fix pass

Same test files with `ASC_DOCS_ROOT=.tmp/asc/docs`; four additional structural regressions were added after planting the two failures.

```text
......                                                                   [100%]
6 passed in 17.85s
```

## Rendered sentences verbatim

Eligibility — old:

> The machine screen tests population, intervention, comparator and design; the registered B-prime clause adds prospective, systematic outcome ascertainment as an eligibility axis, which the screen records as UNRESOLVED per record until held evidence establishes it (never an exclusion); outcome result availability is not an axis; every record carries a rule id, a reason true of that record, and a verbatim span quoted from the record.

Eligibility — new:

> The machine screen tests population, intervention, comparator and design; the registered B-prime clause adds prospective, systematic outcome ascertainment as an eligibility axis, which the screen records as UNRESOLVED on 11 of 11 records until held evidence establishes it (never an exclusion); outcome result availability is not an axis; every record carries a rule id, a reason true of that record, and a verbatim span quoted from the record.

Funding — old:

> Including an industry drug-supply tie in an otherwise independently funded trial: 9 of 9 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's).

Funding — new:

> Including an industry drug-supply tie in an otherwise independently funded trial: 8 trials pooled across all outcomes; 8 in the primary pool. 8 of 8 known (0 unknown) pooled trials are industry-funded or industry-tied (the industry-funded proportion of trials with KNOWN funding — unknown-funding trials are reported separately below, not counted as independently funded — for comparison against a comparator's).

## Per-record field: all 11 of 11

```json
[
  {
    "id": "31185157",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "27633186",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "27295427",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "34215025",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "31189511",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "30291013",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "28910237",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "26630143",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "37952131",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "34526024",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  },
  {
    "id": "SOUL · 40162642",
    "outcome_ascertainment": {
      "state": "UNRESOLVED",
      "basis": "B-prime"
    }
  }
]
```

## Changed pages

Visible HTML text changed on 32 of 32 pages, including GLP-1. The other 31 slugs are listed below. Comparison strips markup, scripts and styles and normalizes whitespace; it includes the changed review-hash pin, so this is complete served-text impact, not an assertion that every prose section changed.

- balanced-crystalloids-vs-saline-mortality
- colchicine-postop-af
- colchicine-recurrent-pericarditis
- colchicine-secondary-cv-prevention
- corticosteroids-cap-mortality
- corticosteroids-covid19-mortality
- dapagliflozin-hfpef-hosp
- denosumab-vertebral-fracture
- doac-vte-recurrence
- dpp4-mace-t2d
- empagliflozin-hfpef-hosp
- esketamine-trd-madrs
- finerenone-ckd-t2d-renal
- iv-iron-hfref-hosp
- melatonin-primary-insomnia-sol
- metformin-pcos-ovulation
- noac-vs-warfarin-af-stroke
- omega3-cardiovascular-events
- pcsk9-mace
- probiotics-aad-prevention
- sacubitril-valsartan-hfref
- semaglutide-obesity-mace
- semaglutide-obesity-weight
- sglt2-ckd-progression
- sglt2-hfref-hosp-cvdeath
- sglt2-primary-prevention-hf
- spironolactone-hfref-mortality
- statins-primary-prevention-elderly
- ticagrelor-vs-clopidogrel-acs
- tocilizumab-covid19-mortality
- tranexamic-acid-pph

## Verification and unresolved blockers

- Scratch equivalent E2E contract: PASS on 32 of 32 locally routed browser pages; zero JavaScript errors. Absolute URLs use http://127.0.0.1:8000/ and browser requests are fulfilled from scratch files or aborted. See `.tmp/asc/inspection.txt`.
- Focused implementation suite: 34 passed, 1 failed. The failure is `tests/test_funding.py::test_funding_fraction_excludes_unknown_from_denominator`, whose expectation counts every stale funding row, rather than current pooled members. That test is outside lane ownership and was not edited.
- Initial repository-root `python -m pytest -q`: 1 collection error from duplicate test_search_v2_isrctn modules under outputs/ and tests/. The repository's verify_all.py uses tests/, so the full suite was rerun as `python -m pytest -q tests`.

Full-suite summary line:

```text
7 failed, 973 passed in 1345.07s (0:22:25)
```

Full-suite failure/skip summary (complete output in `.tmp/asc/full-suite-tests.txt`):

```text
FAILED tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden
FAILED tests/test_certificate.py::test_held_document_byte_mutation_refuses - ...
FAILED tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_funding.py::test_funding_fraction_excludes_unknown_from_denominator
FAILED tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
```

`python scripts/retraction_survival.py 237e9094` was NOT RUN: main(base) hardcodes the repository docs/reviews root and the CLI accepts only the base argument, with no scratch-root option. This follows the lane's explicit fallback.

`git diff --check`: PASS. Review hunks are limited to owned implementation and test files. `.tmp/patches/page.diff` contains the renderer patch; `.tmp/patches/manuscript.diff` is intentionally empty because manuscript.py describes the registered clause without repeating the unsupported recorded-state claim. No manuscript edit was needed.

The seven full-suite failures are recorded individually in STUCK_FAILURES.md. Committed-artifact/hash and ledger tests still inspect untouched docs; the funding test retains the obsolete unscoped-row expectation. This is not a green full-suite claim. The original renderer passes that funding test (1 passed in 5.32s), confirming the contract changed with the intended fix. No forbidden module or out-of-scope test was changed to silence a failure.

All 32 of 32 scratch reproduction files report deterministic rendering. The existing compat-direction test rewrote docs/compat_direction_sweep.json with CRLF; its content was verified identical after newline normalization and its exact HEAD bytes restored without checkout/reset. No tracked docs changes remain.

Files: harness/screen.py, harness/pipeline.py (new helper + one call), harness/funding.py, harness/page.py, tests/test_screen_ascertainment_state.py, tests/test_funding_denominator.py, this report and STUCK_FAILURES.md. Reproduction and verification helpers/logs are under .tmp/asc/. No portfolio or submission status changed; INDEX.md and the workbook were not edited.

Additional MEASURED diagnosis: the existing limitation consistency test still fails when its REVIEWS input points at the scratch rebuild (balanced-crystalloids-vs-saline-mortality). Source inspection found a separate old funding renderer in harness/limitations.py::_funding_block, fed by the unfiltered funding list. This file is outside lane ownership. Synchronizing that renderer is an unresolved integration requirement; refreshing artifacts alone will not repair this mismatch. The requested served-sentence plants pass, but cross-renderer limitation consistency does not.
