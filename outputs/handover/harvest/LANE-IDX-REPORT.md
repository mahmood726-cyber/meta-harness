# LANE IDX report
No commit, reset, checkout, stash, push or network retrieval. The incoming LITX tree was preserved; IDX's pre-edit index is pinned in `.tmp/idx/index-before.py`. Replay used the existing empty `.tmp/empty_aact` directory through `AACT_DIR`. Python subprocesses inherited an external-network/DNS refusal guard; browser routes permitted localhost only. No project or submission status was promoted, so the portfolio index and protected workbook were not changed.

| Surface | Static | Dynamic source |
|---|---|---|
| Method display | Labels; canonical method description | `gate_scorecard.json` gate validation |
| Recovery | State vocabulary | Per-attempt IDs joined to primary review membership and screening; parity attribution check |
| Search recall | Historical measurement label | Recorded recalled/missed PMIDs; no invented recovery-state reclassification |
| Continuous result | Explanatory text | Primary result, claim.present, CI refusal, CI provenance and endpoints |
| Fix counts | Axis names | Recount of `fix_ledger.json.fixes`, not its summary |
| Comparator k | Comparable-count label | `parity.json.comparable_comparator_k` and status |

MEASURED below means a local file read, rendered output, or observed test result. INFERRED denotes interpretation of those objects. CLAIMED denotes historical prose retained as historical evidence, not independent verification. No new source-record validation or clinical conclusion is claimed.

## Candidate 1 — CONFIRMED

MEASURED: `docs/gate_scorecard.json.gates[gate_id=census.interval_provenance].computed`:

```text
{
  "adjudicated_precision": null,
  "adjudicated_production_refusals": 0,
  "adjudication_coverage": null,
  "adjudications": 1,
  "adjudicator_independence": 0.0,
  "external_auditor_adjudications": 0,
  "false_positive_production_refusals": 0,
  "miss_events": 0,
  "plant_events": 1,
  "plant_validations": 1,
  "production_refusals": 0,
  "production_status": "UNVALIDATED",
  "status_gap_events": 1,
  "true_misses": 0,
  "true_positive_production_refusals": 0,
  "unresolved": 1,
  "unvalidated": true,
  "validation": "UNVALIDATED"
}
```
The scorecard has one plant validation but no adjudicated production refusal; UNVALIDATED does not prove the gate never runs, but cannot support the universal banner. The index now reads its state. `harness/synth.py` was not edited: the shared-literal handoff is `.tmp/patches/synth.diff` for ELX.

Old sentence: `Validated vs metafor 5.0.1 (this canonical code path; every rendered interval is gate-checked to originate here).`

New sentence: `Interval provenance gate: UNVALIDATED.` Missing scorecards render UNPROVEN. Plant: `test_method_gate_state`, FAIL before / PASS after (see execution logs).

## Candidate 2 — REFUTED as an identity-based contradiction; historical-label ambiguity corrected

MEASURED: the row is from `search_recall_regression_corpus.json`, not `recovery_log.json.recall_denominator`:

```text
{
  "slug": "tranexamic-acid-pph",
  "query": "(\"tranexamic acid\"[tiab] OR txa[tiab]) AND (\"post-partum hemorrhage\"[tiab] OR \"postpartum hemorrhage\"[tiab] OR \"post-partum hemorrhage\"[tiab] OR \"postpartum hemorrhage\"[tiab]) AND (randomized controlled trial[pt] OR randomized[tiab] OR randomised[tiab] OR \"controlled trial\"[tiab])",
  "state": "RAN_OK",
  "error": null,
  "hits_in_boolean_set": 100,
  "fetched": 100,
  "known_eligible": {
    "pooled_primary": [
      "28456509"
    ],
    "eligible_declared_absent": [
      "32143721",
      "36243576"
    ],
    "unscorable_no_pmid": [
      "NCT02026297"
    ]
  },
  "denominator": 3,
  "recalled": 1,
  "recalled_pmids": [
    "32143721"
  ],
  "missed_pmids": [
    "28456509",
    "36243576"
  ],
  "recall": 0.333
}
```
The two Boolean-set misses are PMIDs 28456509 and 36243576. The scope refusals name different records:

```text
[
  {
    "trial": "WOMAN-2 (39461792), TRAAP (30134136), TRAAP-2 (33913639)",
    "verified": "citation chasing (Crossref) recovered all three PMIDs; all are double-blind RCTs (they pass our design gate)",
    "not_pooled_because": "OUTCOME mismatch: these are PPH-PREVENTION trials whose primary is peripartum blood loss (>=500-1000 mL) or bleeding in anaemia, not the topic's/comparator's 'death due to bleeding'. Reach \u2713, design \u2713, but they do not report the declared mortality-scale outcome to pool. Not a reach failure."
  }
]
```
Thus setting this row to zero missed would fabricate a measurement. The generator is `scripts/measure_regression_corpus_recall.py`; it requires network remeasurement and was not run. The historical object was preserved. Recovery attempts are now separately counted by their current linked review state, or their historical state if unlinked: POOLED, DECLARED_ABSENT, EXCLUDED, SCREENED_IN, and the recorded unresolved states. NOT_FOUND is explicitly distinguished from exclusion/declared absence.
Old row:
```text
tranexamic-acid-pphRAN_OK1001 of 3 (2 missed)
```
New row:
```text
tranexamic-acid-pphRAN_OK1001 of 3 (2 absent from historical Boolean set: 28456509, 36243576; not a current recovery-state count)
```
Plant: `test_recall_identifiers_are_not_scope_exclusions` passes both before and after. The source identifiers, not similarity of topic names, refute the proposed equivalence.

## Candidate 3 — CONFIRMED

MEASURED: `recovery_log.json.attempts[trial=Sarzaeem].topic` was `corticosteroids-covid19-mortality`. The parity row attributes `1 REACH (Sarzaeem 2014, no PMID/not in corpus)` to `colchicine-postop-af`. No identifier was invented. Search across `scripts` and `harness` found only the index reader for recovery_log.json, no generator: this is a hand-maintained correction to that one topic field. A render-time check additionally withholds inventory rows when their named trial occurs only in another parity topic. This textual match checks attribution; it does not establish trial identity or eligibility.
Old sentence:
```text
Sarzaeem → corticosteroids-covid19-mortality: UNVERIFIED name-only in the audit record; no confirmed PMID. Requires author/name search with uncertain yield (several likely small/non-English/registry-only). Recorded as a structural reach limit pending an identifier; not asserted eligible.
```
New sentence:
```text
Sarzaeem → colchicine-postop-af: UNVERIFIED name-only in the audit record; no confirmed PMID. Requires author/name search with uncertain yield (several likely small/non-English/registry-only). Recorded as a structural reach limit pending an identifier; not asserted eligible.
```
Plant: a Sarzaeem row assigned to `wrong` while parity names `right` must render `TOPIC_MISMATCH` and withhold `→ wrong`. FAIL before / PASS after.

## Candidate 4 — CONFIRMED, with a further source-state caveat

MEASURED: COCS PMID 36286314 has `screening.records[].decision="include"`; primary `declared_absent_trials[].state="COUNTS_PRESENT_NOT_CORROBORATED"`; its `reason_code_audit.verdict="REASON_FALSE_VALUE_HELD"`. Therefore neither BLOCKED_BY_MATCHER nor an unqualified percentage-only explanation is current. The held source span actually carries counts and an OR/CI; this lane does not repair extraction or admission. The renderer joins by PMID and reports the recorded decision, absence state and reason audit. The historical recovery row is retained for provenance, while its stale status no longer drives the display.
Old sentence:
```text
COCS → colchicine-postop-af: BLOCKED_BY_MATCHER eligible colchicine-vs-placebo POAF-prevention trial (POAF 21/... reported) excluded because the population matcher requires "atrial fibrillation" in the title, but AF is the OUTCOME not the population of a prevention trial
```
New sentence:
```text
COCS → colchicine-postop-af: DECLARED_ABSENT Current review: screening=include; state=COUNTS_PRESENT_NOT_CORROBORATED; reason audit=REASON_FALSE_VALUE_HELD
```
Plant: historical BLOCKED_BY_MATCHER plus a primary declared-absent record must render DECLARED_ABSENT and its state. FAIL before / PASS after.

## Candidate 5 — REFUTED: the review supports refusal; conditional rendering hardened

MEASURED: `result.present` is not a field in the actual schema. The supported claim field is `result.claim.present=false`. Relevant primary result:

```text
{
  "k": 2,
  "estimate": -11.8449,
  "ci_low": null,
  "ci_high": null,
  "ci_provenance": "synth.pool:PM-tau2+HKSJ-t(k-1)+floor-max(1,Q/(k-1)):v1",
  "pooled_ci_refused": {
    "code": "K2_SINGLE_DF",
    "detail": "Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here."
  },
  "claim": {
    "present": false,
    "pooled_claim": false,
    "state": "NO_POOLED_CLAIM_K2",
    "refusal_code": "K2_SINGLE_DF",
    "significant": false,
    "crosses_null": null,
    "touches_null": null,
    "null": 0.0,
    "direction": null,
    "basis": "no significance/null-crossing claim is emitted for a refused k=2 HKSJ CI"
  },
  "ci_hksj_unserved": {
    "ci_low": -25.1318,
    "ci_high": 1.442,
    "method": "PM tau^2 + HKSJ on t(1)",
    "note": "computed for auditability only; not served as the registered interval at k=2"
  }
}
```
Parity's (-25.13, 1.44) is the unserved audit interval, not a served pooled claim. The old refusal sentence is supported. The renderer now additionally requires the present claim, provenance and both CI endpoints; it no longer unconditionally announces a loss of significance or assumes a displayed interval crosses zero. A future present interval uses signed endpoints and the recorded null-crossing state.
Old sentence:
```text
Semaglutide is the clearest single illustration of the standard: it went from k=4, a tight and statistically significant pool, to k=2, MD −11.84%; the registered PM/HKSJ CI is refused at k=2, so the index makes no pooled significance or null-crossing claim, after a timepoint-consistency guard refused to pool two Week-44 trials into a pre-registered Week-68 outcome. We gave up significance to keep the timepoints consistent. No comparator reports having made that trade. Together with the paragraph above this makes one claim: where we pool less, it is because of a stated bar — and the bar is shown, not asserted.
```
New sentence:
```text
Semaglutide is the clearest single illustration of the standard: it went from k=4, a tight and statistically significant pool, to k=2, MD -11.84%; the registered PM/HKSJ CI is unavailable for a served claim, so the index makes no pooled significance or null-crossing claim, after a timepoint-consistency guard refused to pool two Week-44 trials into a pre-registered Week-68 outcome. The served claim state comes from the primary outcome in review.json.
```
Plant: CI endpoints present but `claim.present=false` and no supported provenance must not produce a null-crossing claim. FAIL before / PASS after.

## Candidate 6 — CONFIRMED provenance/enforcement mismatch, not a 33-entry arithmetic error

MEASURED: the old banner read `error_coverage.json`: library_size=33, by_kind={GATE_LIMB:9, REGRESSION_TEST:12, RENDERED:12}, min_screened=32, max_screened=33. Those are a different instrument from the fix ledger. A rendered disclosure is not proof of enforcement. The replacement explicitly renders the ledger and makes no per-review screening claim; counts are recomputed from entries, so stale summary counters cannot control them.
Old sentence:
```text
Screened against a meta-analysis error library (measured, not asserted)Every documented meta-analysis mistake is converted into one of: a gate limb that refuses a finished review, a regression test with a plant that fires pre-fix, or a rendered disclosure when it is a judgement the harness cannot make. Of 33 documented errors catalogued (9 gate limbs, 12 regression tests, 12 rendered disclosures), 33 have an enforced mechanism, and every live review is screened against 32–33 of 33 of them. This is a claim no published meta-analysis makes about itself, and it is directly checkable (each entry names its mechanism in harness/error_library.py; the count regenerates via scripts/error_coverage.py).
```
New sentence:
```text
Fix ledger94 ledger entries, recounted from fix_ledger.json. These include findings and controls as well as fixes; ledger counts do not measure per-review screening or enforcement.kind: control: 7; external_finding: 21; finding: 3; fix: 60; result: 3implementation: LANDED: 74; REPORTED: 13; SPECIFIED: 7verification: INDEPENDENT: 1; INTERNAL: 38; NONE: 55scope: CORPUS: 6; INSTANCE: 88freshness: CURRENT: 18; STALE: 76
```
Object: `fix_ledger.json.fixes` has 94 entries; the recorded summary (independently recounted for display) is:

```text
{
  "by_implementation": {
    "SPECIFIED": 7,
    "REPORTED": 13,
    "LANDED": 74
  },
  "by_verification": {
    "NONE": 55,
    "INTERNAL": 38,
    "INDEPENDENT": 1
  },
  "by_scope": {
    "INSTANCE": 88,
    "REGRESSION_SET": 0,
    "CORPUS": 6,
    "HELD_OUT": 0
  },
  "by_freshness": {
    "CURRENT": 18,
    "STALE": 76
  },
  "by_kind": {
    "control": 7,
    "external_finding": 21,
    "finding": 3,
    "fix": 60,
    "result": 3
  }
}
```
Plant: two ledger entries versus an intentionally stale summary of 900 must render `2 ledger entries` and `NONE: 1`. FAIL before / PASS after.

## Candidate 7 — CONFIRMED k-label inconsistency; membership uncertainty preserved

MEASURED: the lower comparator table copied manifest overlap prose even where parity stated comparable k. It now uses parity's k and status, while retaining shared-set uncertainty: a stated size does not prove exact trial membership. Every parity-linked manifest checked below quotes its original `overlap.theirs_k` and replacement.

| Topic | Old manifest theirs_k | New comparable count/status |
|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 6 | 5 (comparable; parity status OVERLAPPING) |
| colchicine-postop-af | 9 | 7 (comparable; parity status OVERLAPPING) |
| colchicine-recurrent-pericarditis | 5 | 4 (comparable; parity status OVERLAPPING) |
| corticosteroids-covid19-mortality | not stated in the comparator abstract/full text | 5 (comparable; parity status OVERLAPPING) |
| esketamine-trd-madrs | 4 | 4 (comparable; parity status IDENTICAL_SET) |
| finerenone-ckd-t2d-renal | 2 | 2 (comparable; parity status IDENTICAL_SET) |
| glp1-ra-mace-t2d | 8 | 7 (comparable; parity status SUPERSET) |
| iv-iron-hfref-hosp | 6 | 3 (comparable; parity status OVERLAPPING) |
| melatonin-primary-insomnia-sol | not stated in the comparator abstract/full text | 15 (comparable; parity status OVERLAPPING) |
| noac-vs-warfarin-af-stroke | 4 | 4 (comparable; parity status IDENTICAL_SET) |
| omega3-cardiovascular-events | 28 | 15 (comparable; parity status OVERLAPPING) |
| pcsk9-mace | 12 | 12 (comparable; parity status DOMINANT_SUBSET) |
| probiotics-aad-prevention | 42 | 42 (comparable; parity status OVERLAPPING) |
| semaglutide-obesity-weight | not stated in the comparator abstract/full text | 2 (comparable; parity status IDENTICAL_SET) |
| sglt2-ckd-progression | 10 | 10 (comparable; parity status SUBSET) |
| sglt2-hfref-hosp-cvdeath | not stated in the comparator abstract/full text | 2 (comparable; parity status PARITY_REFUTED_BY_N) |
| spironolactone-hfref-mortality | 9 | 2 (comparable; parity status SUPERSET) |
| statins-primary-prevention-elderly | not stated in the comparator abstract/full text | 0 (comparable; parity status COMPARATOR_INVALID) |
| ticagrelor-vs-clopidogrel-acs | not stated in the comparator abstract/full text | 1 (comparable; parity status SUPERSET) |
| tranexamic-acid-pph | not stated in the comparator abstract/full text | 5 (comparable; parity status SUBSET) |

Plant: a manifest saying not stated plus parity k=7/SUBSET must display `7 (comparable; parity status SUBSET)`. FAIL before / PASS after.

## Verbatim plants and observed pre/post execution

The test plants below were written before implementation. `.tmp/idx/prefix.txt` records six failures and one passing identity-refutation test against the pinned incoming LITX index. The browser contract was added after the source repairs and is not claimed as a pre-fix plant.

```python
import json
from pathlib import Path

from harness import index as idx

DOCS = Path(__file__).resolve().parents[1] / 'docs'


def put(root, name, value):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding='utf8')


def test_method_gate_state():
    page = idx.build_index(str(DOCS))
    assert 'every rendered interval is gate-checked' not in page
    assert 'Interval provenance gate: UNVALIDATED' in page


def test_recovery_topic_mismatch_is_refused(tmp_path):
    put(tmp_path, 'recovery_log.json', {'attempts': [
        {'trial': 'Sarzaeem', 'topic': 'wrong', 'status': 'UNVERIFIED'}]})
    put(tmp_path, 'parity.json', [{'slug': 'right', 'reason': 'Sarzaeem 2014 reach limit'}])
    page = idx._recovery_section(str(tmp_path))
    assert 'TOPIC_MISMATCH' in page
    assert '&rarr; wrong' not in page


def test_recovery_uses_current_review(tmp_path):
    put(tmp_path, 'recovery_log.json', {'attempts': [
        {'trial': 'COCS', 'pmid': '36286314', 'topic': 'topic', 'status': 'BLOCKED_BY_MATCHER'}]})
    put(tmp_path, 'reviews/topic/review.json', {
        'screening': {'records': [{'id': '36286314', 'decision': 'include'}]},
        'outcomes': [{'primary': True, 'declared_absent_trials': [
            {'id': 'PMID 36286314', 'state': 'COUNTS_PRESENT_NOT_CORROBORATED'}]}]})
    page = idx._recovery_section(str(tmp_path))
    assert 'DECLARED_ABSENT' in page and 'COUNTS_PRESENT_NOT_CORROBORATED' in page
    assert '<code>BLOCKED_BY_MATCHER</code>' not in page


def test_recall_identifiers_are_not_scope_exclusions():
    row = next(r for r in json.loads((DOCS / 'search_recall_regression_corpus.json').read_text())['per_topic']
               if r['slug'] == 'tranexamic-acid-pph')
    assert set(row['missed_pmids']) == {'28456509', '36243576'}
    assert set(row['missed_pmids']).isdisjoint({'39461792', '30134136', '33913639'})


def test_semaglutide_refusal_and_missing_claim(tmp_path):
    result = {'k': 2, 'estimate': -1, 'ci_low': -2, 'ci_high': 1,
              'claim': {'present': False}, 'ci_provenance': 'untrusted'}
    put(tmp_path, 'reviews/semaglutide-obesity-weight/review.json',
        {'outcomes': [{'primary': True, 'result': result}]})
    page = idx._continuous_section(str(tmp_path))
    assert 'no pooled significance or null-crossing claim' in page
    assert 'interval that now crosses zero' not in page
    result['estimate'] = 1.25
    put(tmp_path, 'reviews/semaglutide-obesity-weight/review.json',
        {'outcomes': [{'primary': True, 'result': result}]})
    assert 'MD 1.25%' in idx._continuous_section(str(tmp_path))


def test_fix_ledger_counts_are_recounted(tmp_path):
    put(tmp_path, 'fix_ledger.json', {'fixes': [{'verification': 'NONE'}, {'verification': 'INTERNAL'}],
                                    'summary': {'by_verification': {'NONE': 900}}})
    page = idx._error_coverage_section(str(tmp_path))
    assert '2 ledger entries' in page
    assert 'NONE: 1' in page and '900' not in page


def test_comparator_k_uses_parity(tmp_path):
    put(tmp_path, 'reviews/topic/manifest.json', {'slug': 'topic', 'comparator': {
        'overlap': {'theirs_k': 'not stated in the comparator abstract/full text'}}})
    put(tmp_path, 'parity.json', [{'slug': 'topic', 'comparable_comparator_k': 7, 'status': 'SUBSET'}])
    page = idx.build_index(str(tmp_path))
    assert 'not stated in the comparator abstract/full text' not in page
    assert '7 (comparable; parity status SUBSET)' in page


```
`prefix-final.txt` measured result:
```text
6 failed, 1 passed, 1 deselected in 36.17s
```
`targeted.txt` measured result:
```text
1 failed, 33 passed in 142.76s (0:02:22)
```
`targeted-final.txt` measured result:
```text
35 passed in 180.46s (0:03:00)
```
`full-suite.txt` measured result:
```text
7 failed, 995 passed in 1323.57s (0:22:03)
```

Commands: `python -X utf8 -m pytest tests/test_index_derives_from_objects.py tests/test_index_numbers.py tests/test_assertion_literals.py -q`; `python scripts/assertion_literal_sweep.py --write`; `python -X utf8 -m pytest tests/ -q`; `python -m harness.index docs`. See `.tmp/idx/run.py` for the pinned environment and UTF-8 byte capture wrapper.

Literal sweep counts:

```text
{
  "DEFENSIBLE-CONDITIONED": 165,
  "DESCRIPTIVE-METHOD": 88,
  "FALSE-POSITIVE": 16,
  "RETRACTION-MARKER": 8,
  "TRUE-DEFECT": 23
}
```
The sweep is expected to refuse pre-existing TRUE-DEFECT findings; passing its regression tests is not a claim that the publication gate passes. Two inherited page literals were missing adjudications: `_reproduction` remains TRUE-DEFECT (historical inventory does not prove never retrieved); `_reporting` is DESCRIPTIVE-METHOD (explicit requirements, execution unproven). No page source edit was made. Index-introduced literals were inspected; none remains unadjudicated.

Second pass: the refused-CI branch now preserves the estimate's sign and a missing result explicitly suppresses claims. The final verbatim plants were rerun against the pinned incoming module (`prefix-final.txt`); the focused suite was rerun against final source. The full-suite run began before this last display hardening, so its line is a broad integration diagnostic, not certification of the final bytes. No full-suite PASS is claimed.

IDX changes: `harness/index.py`, the Sarzaeem topic field in hand-maintained `docs/recovery_log.json`, regenerated `docs/index.html`, `tests/test_index_derives_from_objects.py`, two inherited-literal adjudications in `registry/assertion_literal_adjudications.json`, generated assertion sweep JSON/HTML, this report, and local `.tmp/idx/` evidence plus `.tmp/patches/synth.diff`. The initial LITX edits to other harness files and verify_all.py were preserved. Scoped whitespace check passed; table tags balanced, no template placeholders or UTF-8 BOM; HEAD stayed at the supplied base.

Full-suite failed test lines:

```text
FAILED tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden
FAILED tests/test_certificate.py::test_held_document_byte_mutation_refuses - ...
FAILED tests/test_certificate.py::test_all_certificate_inputs_and_manuscript_match
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_real_review_reproduces_and_passes_full_gate
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
```
No publication, certification, source verification or full-suite PASS is inferred from targeted tests. Unresolved out-of-scope failures are recorded in `.tmp/idx/STUCK_FAILURES.md`. The synth change is an unapplied handoff patch. Report and local evidence are review artifacts; no commit was made.

## Final audit and blocker disposition

MEASURED: final index equals a fresh generator render; sweep source and adjudication digests are current; synth handoff passes git apply --check. The full suite changed only line endings in compat_direction_sweep.json; JSON equality was proved before restoring its original bytes. No root commit was made.

The seven full-suite failures comprise four review replay/certificate failures, one stale fix-ledger view, one missing scorecard registration for verify_all.limb_assertion_literals, and one legacy limitation/claimgraph comparison. These remain integration work; IDX does not rebuild other lanes’ review artifacts, register their gates, or change their tests. The displayed ledger counts describe its held object, not a fresh fix-state certification.

Evidence: [final audit](.tmp/idx/final-audit.json), [full test log](.tmp/idx/full-suite.txt), [final focused log](.tmp/idx/targeted-final.txt), [pre-fix plants](.tmp/idx/prefix-final.txt), [source delta against LITX](.tmp/idx/index.diff), [ELX handoff patch](.tmp/patches/synth.diff).
