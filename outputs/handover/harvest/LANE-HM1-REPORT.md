# LANE HM1 report

MEASURED: **probiotics-aad-prevention: PASS** (full `harness.gate.gate_page`, unchanged gate).
MEASURED: **58 items resolved of 58** baseline trial × harm-outcome items:
**5 extracted (counts) / 0 extracted (effect+CI) / 36 typed refusal / 17 spurious signal**.
Unresolved baseline items: **0**. This measures resolution of the baseline debt, not
complete numerical safety evidence for every included trial. Refusals are not zero-risk claims.

MEASURED HEAD: `f6f7b14c820bdadd258122ac0bb54c7e4d2a989a`; matches lane base `refs/lanes/landing3-wip`.
No commit or push. No external network; build/test subprocesses blocked outbound Python
socket connections, with loopback allowed for the local browser test. Sources were held
abstracts, held XML, and local AACT snapshot `2026-08-30`.

## Evidence and scope

- Baseline denominator: [baseline-items.json](outputs/handover/hm1/baseline-items.json),
  read before edits from the base review: 33 Any adverse events + 25 Serious adverse events.
- Item-level exact spans, source references, reasoning and final states:
  [items.json](outputs/handover/hm1/items.json). The same spans are in
  `cache/probiotics-aad-prevention/verified_arms.json` and the override audit.
- [Held AACT inspection](outputs/handover/hm1/aact-held-review.json) retains the rows inspected
  from `reported_events`, `outcome_counts`, `result_groups`, `outcomes` and `outcome_measurements`.
  Event-category counts were not summed into unique participants. Registry tables did not
  provide an additional eligible aggregate harm extraction. No absent registry row was taken
  as evidence of zero harm. A questionable DERIVED link for PMID 10545590 was not used.
- MEASURED: screening and primary outcome result are byte-equivalent as parsed JSON to the
  baseline. No membership, search, screening, protocol, gate or synthesis edits.
- Only this lane's canonical page and its own harness blind page were regenerated; incidental
  shared index and blind-map writes were restored to their original bytes.

## Static versus dynamic disclosure

| Material | Type | Evidence / transformation / validation |
|---|---|---|
| Verified harm counts and refusals | Static source adjudication | Exact held spans; no percentage-derived or assumed denominators; span/audit tests |
| Baseline N and resolution split | Dynamic measurement | Baseline review list joined by outcome + PMID to rebuilt state |
| Pooled results | Dynamic computation | Existing synthesis engine; rebuilt using `--now 2026-09-11` |
| Gate/test verdicts | Dynamic measurement | Captured command output below |
| Planted fixture | Static synthetic test only | Explicit fixture; never inserted into clinical cache/page |
| Clinical interpretation of narrative/spurious signals | INFERRED adjudication | Item-specific reasons tied to verbatim source; no assertion of unobserved zero counts |
| Complete safety coverage / release certification | Not CLAIMED | Only baseline HM debt resolved; global audit test remains blocked outside this lane |

## Recovered counts and second-pass source review

All five extracted rows are marked `verified` after rebuilding. Count values below are
intervention events / safety n versus comparator events / safety n, read from each trial's
own held full text, not the comparator meta-analysis.

| PMID | Outcome | Source-backed counts | Source detail |
|---|---|---|---|
| 41699149 | Any adverse events | 64/125 vs 69/130 | Table 4, **people** with AEs; not 167 vs 185 event totals |
| 39529939 | Any adverse events | 7/285 vs 3/279 | Safety-analysis paragraph; not efficacy denominators 282/273 |
| 26973849 | Any adverse events | 18/245 vs 12/222 | AE paragraph; safety set excludes participants who took no study drug |
| 39529939 | Serious adverse events | 1/285 vs 0/279 | Table 2, Serious AE row; not Severe AE row |
| 34541475 | Serious adverse events | 4/181 vs 6/178 | Table 2, severe/SAE row, matching protocol harm keywords |

PMID 26973849 spells its numerator **“Eighteen”**. The stored span preserves that spelling
verbatim; integer 18 is a lexical conversion, not an estimated count. `verify._digits_in`
now recognizes spelled integers zero–nineteen, with a regression proving an incorrect
count still fails. Other numeric values are literal source digits. No harm effect+CI
matching these unresolved registered outcomes was identified for additional extraction.

Implementation: singleton verified inputs remain supported; per-PMID lists select the exact
outcome and reject duplicates. The override scanner and coverage test now include list entries.
Missing-effect enrichment refuses ambiguous multi-outcome entries. Explicit typed refusals
survive broad keyword reclassification only with a reason and an exact held-source span;
fabricated spans raise an error. `SIGNAL_SPURIOUS` maps to retrieved/refused, not certified
absence. Full-text provenance and document references are retained on recovered counts.

## Verification

Build command: `python scripts/build_topic.py probiotics-aad-prevention --now 2026-09-11`

```text
protocol_sha=f6f7b14c820bdadd258122ac0bb54c7e4d2a989a
PRIMARY: Antibiotic-associated diarrhoea  k=16  RR=0.6907 (0.5193-0.9187)  tau2=0.169
included trials: ['40488914', '39529939', '35727573', '34541475', '32035998', '26973849', '24772726', '23932219', '18701826', '18410562', '15740542', '11560298', '7872284', '24456384', '21165295', '18026577']
declared-absent trials: ['42608299', '41699149', '40716758', '40548185', '39935568', '39497860', '39467682', '39429834', '38258024', '33032474', '30912409', '30439760', '30149135', '28871492', '27169634', '22472744', '21552138', '18949181', '17356555', '16572062', '10547243', '10545590', '9570649', '2184848', '24044687', '23618760', '22371721', '21871144', '20145608', '19138244', '16292090', '14627358', 'PROBIO', 'NCT04529980', 'NCT02993419', 'NCT02722993', 'NCT03516409', 'YOBIOTIC', 'Probiotics', 'NCT07234448', 'PANDA']
comparator OA=True k=42
canonical: docs/reviews/probiotics-aad-prevention/index.html
blind: docs/m/m586876fa/  docs/m/m7d28b3cd/
```

Full gate command: `python -m harness.gate docs/reviews/probiotics-aad-prevention`
(calls the same `gate_page` as `verify_all.limb_gate_every_page`, this page only).

```text
probiotics-aad-prevention: PASS
GATE PASS  docs/reviews/probiotics-aad-prevention
```

Planted before implementation on base HEAD: `python -m pytest tests/test_hm1_lane.py -q`.
The intentionally incorrect assertion that an unresolved fixture passes failed as follows
(verbatim observed output):

```text
F                                                                        [100%]
================================== FAILURES ===================================
_______________________________ test_hm1_plant ________________________________

tmp_path = WindowsPath('C:/mh-r-HM1/.tmp/pytest-of-mahmo/pytest-0/test_hm1_plant0')

    def test_hm1_plant(tmp_path):
        spec = {"name": "Any adverse events", "keywords": ["adverse events"]}
        records = {"fixture": {"abstract": "Adverse events were similar between groups."}}
        outcome = {"name": spec["name"], "kind": "harm", "trials": [],
                   "declared_absent_trials": [{"id": "fixture", "reason_code": "OUTCOME_NOT_IN_SOURCE"}],
                   "result": {"present": False}}
        harms.annotate_outcome(outcome, spec, [{"id": "fixture"}], records)
        (tmp_path / "review.json").write_text(json.dumps({"outcomes": [outcome]}), encoding="utf-8")
>       assert gate.check_harms_complete(str(tmp_path)) == []
E       AssertionError: assert ['L1: HARMS_I...arm absence.'] == []
E         
E         Left contains one more item: 'L1: HARMS_INCOMPLETE -- Any adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (fixture) among 1 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.'
E         Use -v to get more diff

tests\test_hm1_lane.py:14: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_hm1_lane.py::test_hm1_plant - AssertionError: assert ['L1: ...
1 failed in 3.57s
```

The final `test_hm1_plant` asserts the refusal first, applies a held-span typed refusal to
that same fixture and then asserts the unchanged harm gate passes. It is in the final
passing regression run. The local browser test served the rebuilt page on
`http://127.0.0.1:8000`, clicked Harms and checked visible outcomes, recovered trial IDs,
refusal states, absence of HARMS_INCOMPLETE, and no browser script errors.

Regression command:
`python -m pytest tests/test_hm1_lane.py tests/test_hm1_ui.py tests/test_verified_override.py tests/test_verified_effects.py tests/test_absence_ontology.py tests/test_missing_effect.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py tests/test_honest_states_renderable.py -q`

```text
...................................................                      [100%]
51 passed in 24.48s
```

Required command: `python -m pytest tests/test_harms_recovery.py tests/test_override_audit.py -q`

```text
....F                                                                    [100%]
================================== FAILURES ===================================
_____________ test_override_audit_covers_every_committed_override _____________

    def test_override_audit_covers_every_committed_override():
        audited = json.loads(AUDIT.read_text(encoding="utf-8"))
        audited_by_key = {_key(row): row for row in audited}
        required = {_key(row) for row in _override_rows_in_cache()}
    
        missing = sorted(required - set(audited_by_key))
        extra = sorted(set(audited_by_key) - required)
>       assert not missing, "override(s) missing from audit: " + repr(missing)
E       AssertionError: override(s) missing from audit: [('esketamine-trd-madrs', 'verified_arms.json', 'NCT02417064', 'Observed-case Day-28 raw change-score MADRS MD'), ('sglt2-ckd-progression', 'verified_effects.json', '32970396', 'Trial-defined primary cardiorenal composite'), ('sglt2-ckd-progression', 'verified_effects.json', '36331190', 'Trial-defined primary cardiorenal composite')]
E       assert not [('esketamine-trd-madrs', 'verified_arms.json', 'NCT02417064', 'Observed-case Day-28 raw change-score MADRS MD'), ('sg...osite'), ('sglt2-ckd-progression', 'verified_effects.json', '36331190', 'Trial-defined primary cardiorenal composite')]

tests\test_override_audit.py:35: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
1 failed, 4 passed in 3.79s
```

**Remaining global blocker:** the required suite is not fully green. Its only failure is
the same three missing audit rows observed before edits: esketamine NCT02417064 and
sglt2-ckd PMIDs 32970396 / 36331190. None belongs to this lane. The lane prompt explicitly
limits fixing those baseline rows to this lane's pages, so they remain unchanged and are
logged in `STUCK_FAILURES.md`. Every HM1 override is audited; the full coverage test's
missing list contains no HM1 row. No test was skipped or weakened to hide this failure.

The first browser attempt was blocked by the offline guard denying Windows' loopback
socketpair. Allowing loopback only fixed the test infrastructure; external connections
remain blocked. The final run above passed. No gate/synthesis rule was loosened.

## Item-by-item disposition

Exact unabridged verbatim spans and final states are in [items.json](outputs/handover/hm1/items.json)
and the verified inputs; each row below uses the same `(outcome, PMID)` key.

| PMID | Harm | Disposition | Source-backed reason |
|---|---|---|---|
| 42608299 | Any adverse events | typed refusal | Only a between-group significance statement is held for adverse events; no per-arm participant counts or harm effect with CI are supplied. |
| 40716758 | Any adverse events | spurious signal | The signal describes background antibiotic-associated diarrhoea and abdominal pain, not this trial's aggregate adverse-event outcome. |
| 40548185 | Any adverse events | typed refusal | The source states no serious adverse events but does not quantify participants with any adverse event; the serious subset cannot substitute for the aggregate outcome. |
| 40488914 | Any adverse events | spurious signal | The signal is background antibiotic-associated diarrhoea, the efficacy endpoint, rather than a report of the trial's aggregate adverse events. |
| 39935568 | Any adverse events | typed refusal | The narrative gives no arm-specific safety-analysis denominator and leaves reporting versus attribution to LGG ambiguous; the efficacy completers cannot be assumed to be the safety population. |
| 39429834 | Any adverse events | spurious signal | The signal concerns antibiotic-associated diarrhoea as background and efficacy, not aggregate adverse events in this trial; full-text numerical adverse-event comparisons cite other studies. |
| 35727573 | Any adverse events | typed refusal | Only a narrative comparison of adverse events is held; neither arm-specific adverse-event counts nor a harm effect with CI is given. |
| 34541475 | Any adverse events | typed refusal | The zero statement is restricted to intervention-related events and the held table reports only severe events; neither establishes the number with any adverse event. |
| 33032474 | Any adverse events | typed refusal | Well tolerated is a narrative judgment without arm-specific adverse-event counts or a harm effect with CI. |
| 32035998 | Any adverse events | spurious signal | The signal is background antibiotic-associated diarrhoea, the efficacy endpoint, not a report of this trial's aggregate adverse events. |
| 30149135 | Any adverse events | typed refusal | The narrative states similarity but gives no per-arm adverse-event counts or harm effect with CI. |
| 27169634 | Any adverse events | typed refusal | The narrative significance statement provides no per-arm adverse-event counts or harm effect with CI. |
| 24772726 | Any adverse events | typed refusal | The source gives event counts and a percentage without arm-specific safety denominators or an unambiguous participant numerator; no denominator is inferred from 2.0%. |
| 21552138 | Any adverse events | typed refusal | Safe and well tolerated is narrative only and does not provide per-arm adverse-event counts or a harm effect with CI. |
| 18701826 | Any adverse events | typed refusal | The narrative zero statement does not explicitly specify arm-specific safety-analysis denominators; randomized group sizes are not asserted to be the observed safety population. |
| 18410562 | Any adverse events | typed refusal | The narrative zero statement does not present a per-arm adverse-event table or explicitly identify safety-analysis denominators; efficacy ITT denominators are not substituted. |
| 16572062 | Any adverse events | typed refusal | No serious side effects is a narrower narrative outcome and does not quantify participants with any adverse event. |
| 15740542 | Any adverse events | typed refusal | The narrative zero statement gives no safety denominators, while randomized and analysed group sizes differ; neither population is assumed to be the safety population. |
| 10545590 | Any adverse events | spurious signal | The safety record refers to prior knowledge of the strain, not adverse-event results from this trial. |
| 9570649 | Any adverse events | typed refusal | The narrative excludes effects attributed to S. boulardii, not all adverse events, and supplies no arm-specific safety counts. |
| 7872284 | Any adverse events | typed refusal | No serious adverse reactions is a narrower narrative statement and does not quantify participants with any adverse event. |
| 2184848 | Any adverse events | typed refusal | The source qualitatively compares individual gastrointestinal symptoms without an aggregate participant count or a harm effect with CI. |
| 20145608 | Any adverse events | typed refusal | Well tolerated is narrative only across a three-arm dose-ranging trial and does not give adverse-event counts or a harm effect with CI. |
| 19138244 | Any adverse events | typed refusal | The source describes tolerability and major side effects leading to discontinuation, not the aggregate number of participants with any adverse event. |
| 18026577 | Any adverse events | typed refusal | The held abstract and abstract-only XML report tolerability narratively without adverse-event counts or a harm effect with CI. |
| 16292090 | Any adverse events | typed refusal | The source reports only a significance comparison, without per-arm adverse-event counts or a harm effect with CI. |
| 23932219 | Any adverse events | typed refusal | The source reports a pooled total of participants with serious events, with neither arm-specific counts nor a harm effect with CI; this also does not identify the aggregate any-event outcome. |
| 30912409 | Any adverse events | typed refusal | The held source states no adverse effects in either arm but reports only completer efficacy denominators after loss to follow-up, without explicitly identifying the safety-analysis population. |
| 21165295 | Any adverse events | typed refusal | The source lists abdominal discomfort and skin eruption separately without their participant overlap; these symptom counts cannot be summed into participants with any adverse event. |
| 22371721 | Any adverse events | typed refusal | The source reports participants with non-serious events separately from serious event totals, without participant overlap or the aggregate number with any event. |
| 26973849 | Any adverse events | extracted (counts) | Participant numerators and corresponding safety denominators are reported by arm in the held source. |
| 39529939 | Any adverse events | extracted (counts) | Participant numerators and corresponding safety denominators are reported by arm in the held source. |
| 41699149 | Any adverse events | extracted (counts) | Participant numerators and corresponding safety denominators are reported by arm in the held source. |
| 42608299 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 41699149 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 40716758 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 40548185 | Serious adverse events | typed refusal | No serious adverse events is a narrative zero statement without explicit per-arm safety-analysis denominators; the planned sample size is not a safety denominator. |
| 40488914 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 39935568 | Serious adverse events | typed refusal | The narrative gives no arm-specific safety-analysis denominator and leaves reporting versus attribution to LGG ambiguous; the efficacy completers cannot be assumed to be the safety population. |
| 39429834 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 35727573 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 32035998 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 30149135 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 27169634 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 26973849 | Serious adverse events | typed refusal | The source gives numbers of serious events, not numbers of participants with at least one serious event; repeated events cannot be treated as binomial participant counts. |
| 24772726 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 18701826 | Serious adverse events | typed refusal | The narrative zero statement does not explicitly specify arm-specific safety-analysis denominators; randomized group sizes are not asserted to be the observed safety population. |
| 18410562 | Serious adverse events | typed refusal | The narrative zero statement does not present a per-arm adverse-event table or explicitly identify safety-analysis denominators; efficacy ITT denominators are not substituted. |
| 16572062 | Serious adverse events | typed refusal | No serious side effects is narrative only, without explicit arm-specific safety denominators; the reported AAD completers are not assumed to be the safety population. |
| 15740542 | Serious adverse events | typed refusal | The narrative zero statement gives no safety denominators, while randomized and analysed group sizes differ; neither population is assumed to be the safety population. |
| 9570649 | Serious adverse events | typed refusal | The narrative excludes effects attributed to S. boulardii, not all adverse events, and supplies no arm-specific safety counts. |
| 2184848 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 22371721 | Serious adverse events | typed refusal | The source reports 15 versus 23 serious events, not unique participants with a serious event, so a participant-level risk ratio is not identified. |
| 19138244 | Serious adverse events | typed refusal | No major side effects that necessitated discontinuation is a narrower outcome than all serious adverse events and gives no arm-specific serious-event counts. |
| 16292090 | Serious adverse events | spurious signal | The signal concerns background effects or adverse events without a seriousness classification; the held passage does not report the registered serious-adverse-event outcome. |
| 23932219 | Serious adverse events | typed refusal | The source reports 578 participants with serious adverse events pooled across both groups, without per-arm numerators or a serious-harm effect with CI. |
| 34541475 | Serious adverse events | extracted (counts) | Participant numerators and corresponding safety denominators are reported by arm in the held source. |
| 39529939 | Serious adverse events | extracted (counts) | Participant numerators and corresponding safety denominators are reported by arm in the held source. |
