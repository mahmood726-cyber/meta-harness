# Amendment A4 -- REQUEST (not signed)

The frozen v3.1 dual reader (`scripts/rob2_dual.py`, contextual pre-registration
`2b3450d7`) has two defects identified during the served-driver review (round 28).
All five independent-review findings are accepted. This revision changes only the
request and its read-only measurement script. The frozen implementation, existing
behavioural tests, and frozen input objects remain unchanged.

## Defects and requested behaviour

1. **Stale-record reuse.** Replay checks NEITHER the manifest prompt hash nor the
   held record's own prompt against the current generated prompt. Live mode checks
   only the manifest hash. Require BOTH checks in BOTH modes, for Codex, Agy, and
   the adjudicator, before replaying any response bytes. This mirrors the contextual
   pipeline's `fresh` / `record_prompt_sha256` implementation (located in
   `scripts/rob2_contextual.py`; contextual answer verification is in
   `robgrade/contextual.py`). A stale record supplies no reading in replay mode;
   live mode must make a replacement call for the current prompt.
2. **Conflicting duplicate rows.** The frozen verifier retains the first row, so
   PY/PN conflicts depend on row order. Require NI with
   `AMBIGUOUS_CONFLICTING_ROWS` in either order.

## Measurement method and scope

`scripts/a4_measure.py` loads both manifests and their respective record stores.
It validates held-record integrity, regenerates reader prompts using
`rob2_dual.items` and `prompt_bytes`, and captures the adjudicator prompt built by
frozen `process` from the current verified readers' disagreements after typed
answers take precedence. No model is called and no record or assessment is written.
Manifest/current hash comparisons and held/current byte comparisons are distinct
from manifest/held hash comparisons. Counts of reply defects cover all successful
held records, including records not referenced by the current manifests; conflicting
rows use only parseable successful replies as their denominator. Unparseable replies
are explicitly named rather than counted as conflict-free.

For each mismatch the audit lists the manifest key, role and record ID, compares
held versus current verified readings, and tests the pre-A2 parser in memory.
Typed-rule precedence is reported separately from parser recovery. The frozen
driver is never patched on disk. A read-only replay spy records which responses
the frozen process actually reads; adjudicator evidence blocks are compared too.

Command (PowerShell, 2026-10-14):

```powershell
$env:TMP='C:/mh-lanes/tmp'; $env:TEMP='C:/mh-lanes/tmp'
$env:PYTHONDONTWRITEBYTECODE='1'
$env:ROBGRADE_LOCAL_FT='1'
$env:ROBGRADE_DEV_OPEN_CC='1'
$env:AACT_DIR='F:/AACT-storage/AACT/2026-08-30'
python scripts/a4_measure.py
```

## Measured impact (2026-10-14)

The measurement uses **ROBGRADE_LOCAL_FT=1 and ROBGRADE_DEV_OPEN_CC=1**
with the pinned AACT snapshot named above. DEV reads require the second flag.
The script accepts each flag only unset (disabled) or exactly "1" (enabled),
validates AACT_DIR, and prints the effective configuration. All other values,
including "0" and the empty string, are rejected before measurement: the frozen
driver enables any non-empty value. It supplies no implicit source-selection defaults.

| Measure (denominator) | Dual / rob2 | Served / rob2_served |
|---|---|---|
| Current prompts regenerated / manifest entries | 203/204 | 56/56 |
| Entries not consumed: no current adjudicator prompt / manifest entries | 1/204 | 0/56 |
| Manifest/current prompt hash mismatches / regenerated prompts | 8/203 | 0/56 |
| Held/current prompt byte mismatches / regenerated prompts | 8/203 | 0/56 |
| Reader held/current prompt byte mismatches / compared reader entries | 0/138 | 0/56 |
| Adjudicator held/current prompt byte mismatches / compared adjudicator entries | 8/65 | 0/0 (no adjudicator entries) |
| Manifest/held prompt hash mismatches / manifest entries | 0/204 | 0/56 |
| Successful records / all held records | 207/208 | 56/260 |
| Unparseable successful replies / successful records | 2/207 | 0/56 |
| Parseable successful replies / successful records | 205/207 | 56/56 |
| Conflicting duplicate replies / parseable successful replies | 0/205 | 0/56 |

**All 138 reader entries match.** The previously reported 29 mismatches came from
running with LOCAL_FT alone: the reader mismatches were the DEV source
configuration, not stale reader records. Under both flags, the eight mismatches
are all adjudicator entries. Matching manifest and held hashes does not establish
freshness against the prompt the current code builds.

**The frozen replay READS these eight adjudications although the current readers
and typed precedence would show an adjudicator different readings/question sets.
That is exactly the defect A4 closes.** For seven entries the reader pairs
themselves are unchanged, but typed rules now remove questions from the adjudicator's
view. For PMID 35041780, A2 also changes the verified reader pairs and creates
different disagreements. These are prompt-input differences, not a claim that all
eight final assessment objects or reported scores change.

**A4 does not change the frozen v3.1 input objects, which the contextual
pre-registration byte-freezes. What A4 would change is any FUTURE replay of these
trials:** stale adjudicator responses would supply no reading in replay mode;
live mode would require replacement calls using the current prompts. This request
does not implement A4 or regenerate any frozen object.

**Configuration hazard:** replay under the wrong source configuration silently
changes prompts while the frozen driver still reuses held replies. A4's
manifest/current and held/current checks would catch that mismatch. Explicit
configuration in the audit prevents an accidental default; it does not make a
deliberately selected wrong configuration safe.

### The eight mismatching entries and their causes

Every row below has role **adjudicator**. Pairs are **Codex/Agy**, before any typed
override. "Removed" means the current prompt omits that question, not that the
reader reply disappeared. The other shown readings are unchanged except where
specified. The script compares full verified reading dictionaries, not just these
answer labels.

All eight responses were observed reaching frozen response replay, and all eight
held/current adjudicator evidence blocks are byte-identical in this configuration.

| Manifest key | Held record ID | Held readings versus current verified readings; why the prompt differs |
|---|---|---|
| `balanced-crystalloids-vs-saline-mortality::23732264::Mortality` | `mc-3e550a012a7359e3d1d4703748590f61` | 4.1 and 4.2 remain NI/N, but are removed: `outcome:all_cause_mortality_v1` settles them as N and PN. |
| `balanced-crystalloids-vs-saline-mortality::26444692::Mortality` | `mc-f9dbd6cadb9d6d41f825a86f22048a49` | 4.2 remains NI/N and 4.4 remains PN/NA, but are removed: the mortality rule settles them as PN and N. |
| `balanced-crystalloids-vs-saline-mortality::27604335::Mortality` | `mc-bf15f1803b5004350463ad4157ed4c05` | 4.1 and 4.2 remain NI/N; 4.4 remains NI/NA. All three are removed: the mortality rule settles them as N, PN, N. |
| `balanced-crystalloids-vs-saline-mortality::29485925::Mortality` | `mc-24711f02e81355eece48c404a88c3d0a` | 4.1, 4.2 and 4.4 remain NI/N. All three are removed: the mortality rule settles them as N, PN, N. |
| `balanced-crystalloids-vs-saline-mortality::34375394::Mortality` | `mc-019646819125733d246dcd10660e1d0a` | 4.1 and 4.2 remain NI/N, but are removed: the mortality rule settles them as N and PN. |
| `balanced-crystalloids-vs-saline-mortality::35041780::Mortality` | `mc-00a519a7b3fbed39f3ea0f67336c706b` | A2 recovers Agy's prose-surrounded JSON. 1.2 and 3.1 change PY/NI to PY/Y (same-side agreement); 2.3–2.5, 3.2–3.4, 4.4 and 4.5 change NA/NI to NA/NA. None remains a disagreement. Newly shown 2.6 and 2.7 verify to NI/Y and NI/NA. The mortality rule also settles 4.4 as N. Held question set: 1.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 4.4, 4.5; current set: 2.6, 2.7. |
| `iv-iron-hfref-hosp::25176939::Heart-failure hospitalization` | `mc-9262936e455e2edbca4ca1ad9bc6aca7` | 5.3 remains NI/PN, but is removed: `regex:sap_fixes_the_analysis_v1` settles it as PN. |
| `probiotics-aad-prevention::30439760::Antibiotic-associated diarrhoea` | `mc-0e7fc4f27d4dbc22bae1b9625540a252` | 1.1 remains NI/Y, but is removed: `regex:sequence_generation_v2` settles it as Y. |

The three named typed rules and the outcome argument to `typed_answers` were added
in `9aa0d65b5` (verified against its source diff). These account for the seven
unchanged-pair cases and the extra held 4.4 question in 35041780.
All eight held adjudicator records first appear in `15826a7da`, before that
typed-rule extension and the v3.1 engine change (verified with per-record git history).
[V31_REPRODUCIBILITY.md](V31_REPRODUCIBILITY.md) explains the separate assessment-object
comparison: A2 (`e83be9e07`) explains the committed 35041780 object's difference,
and older engine/normalisation/typed-rule changes explain the pre-v3.1 objects.
Its finding that restoring the old parser reproduces that **object** exactly must
not be confused with reproducing this earlier held **prompt**: restoring only the
old parser does not restore the pre-`9aa0d65b5` question set. The audit confirms
Agy's 35041780 reply is unreadable before A2 and readable now; both readers in the
other seven cases are readable with either parser.

The note's 12 object differences and this audit's eight prompt differences are
different populations and measurements. Its no-reported-score-change finding
concerns the explained object comparison, not an amended-versus-frozen A4 replay.
No A4 object or score equality is claimed.

The remaining dual entry,
`probiotics-aad-prevention::32944084::Antibiotic-associated diarrhoea`, has no
current adjudicator prompt: current readers and typed precedence leave no
disagreement, so the frozen process does not consume that adjudication. It is
excluded from the 203 compared entries, not classified as fresh. The two
unparseable successful replies are named in the output below and are excluded
from the conflicting-row denominator.

Exact measurement stdout (exit code 0):

```text
environment: ROBGRADE_LOCAL_FT=1 ROBGRADE_DEV_OPEN_CC=1 AACT_DIR=F:/AACT-storage/AACT/2026-08-30
rob2: no current adjudicator prompt (not consumed): probiotics-aad-prevention::32944084::Antibiotic-associated diarrhoea / adjudicator
[rob2]
manifest entries with regenerated current prompts: 203/204
manifest entries not consumed (no current prompt): 1/204
manifest/current prompt hash mismatches: 8/203
held/current prompt byte mismatches: 8/203
manifest/held prompt hash mismatches: 0/204
reader held/current prompt byte mismatches: 0/138
adjudicator held/current prompt byte mismatches: 8/65
successful held records: 207/208
unparseable successful replies: 2/207
unparseable record IDs: mc-98d7ef55af2c4774d435f7d5d3d8dd50, mc-bcba1341c139cdccd11363141aac09ff
parseable successful replies: 205/207
replies with conflicting duplicate rows: 0/205 parseable successful replies
mismatching entries (key | role | record id):
balanced-crystalloids-vs-saline-mortality::23732264::Mortality | adjudicator | mc-3e550a012a7359e3d1d4703748590f61
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 2.6, 2.7, 3.1, 3.3, 3.4, 4.1, 4.2, 5.2
  current questions: 2.6, 2.7, 3.1, 3.3, 3.4, 5.2
  4.1: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  4.2: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: PN (outcome:all_cause_mortality_v1)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
balanced-crystalloids-vs-saline-mortality::26444692::Mortality | adjudicator | mc-f9dbd6cadb9d6d41f825a86f22048a49
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 1.2, 2.6, 2.7, 4.2, 4.3, 4.4, 5.2, 5.3
  current questions: 1.2, 2.6, 2.7, 4.3, 5.2, 5.3
  4.2: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: PN (outcome:all_cause_mortality_v1)
  4.4: held PN/NA; current verified PN/NA; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
balanced-crystalloids-vs-saline-mortality::27604335::Mortality | adjudicator | mc-bf15f1803b5004350463ad4157ed4c05
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5, 5.2, 5.3
  current questions: 3.1, 3.2, 4.3, 4.5, 5.2, 5.3
  4.1: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  4.2: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: PN (outcome:all_cause_mortality_v1)
  4.4: held NI/NA; current verified NI/NA; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
balanced-crystalloids-vs-saline-mortality::29485925::Mortality | adjudicator | mc-24711f02e81355eece48c404a88c3d0a
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 2.1, 2.2, 2.6, 2.7, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5, 5.2, 5.3
  current questions: 2.1, 2.2, 2.6, 2.7, 3.1, 3.2, 4.3, 4.5, 5.2, 5.3
  4.1: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  4.2: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: PN (outcome:all_cause_mortality_v1)
  4.4: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
balanced-crystalloids-vs-saline-mortality::34375394::Mortality | adjudicator | mc-019646819125733d246dcd10660e1d0a
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 2.6, 2.7, 4.1, 4.2, 5.2, 5.3
  current questions: 2.6, 2.7, 5.2, 5.3
  4.1: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: N (outcome:all_cause_mortality_v1)
  4.2: held NI/N; current verified NI/N; current shown False; changed fields none
    typed precedence: PN (outcome:all_cause_mortality_v1)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
balanced-crystalloids-vs-saline-mortality::35041780::Mortality | adjudicator | mc-00a519a7b3fbed39f3ea0f67336c706b
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 1.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 4.4, 4.5
  current questions: 2.6, 2.7
  1.2: held PY/NI; current verified PY/Y; current shown False; changed fields answer,quote,rationale,source_id,source_sha256
  2.3: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  2.4: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  2.5: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  2.6: held not shown; current verified NI/Y; current shown True; changed fields answer,quote,rationale,source_id,source_sha256
  2.7: held not shown; current verified NI/NA; current shown True; changed fields answer,rationale
  3.1: held PY/NI; current verified PY/Y; current shown False; changed fields answer,quote,rationale,source_id,source_sha256
  3.2: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  3.3: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  3.4: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  4.4: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
    typed precedence: N (outcome:all_cause_mortality_v1)
  4.5: held NA/NI; current verified NA/NA; current shown False; changed fields answer,rationale
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: False/True
iv-iron-hfref-hosp::25176939::Heart-failure hospitalization | adjudicator | mc-9262936e455e2edbca4ca1ad9bc6aca7
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 4.1, 4.2, 4.4, 4.5, 5.2, 5.3
  current questions: 4.1, 4.2, 4.4, 4.5, 5.2
  5.3: held NI/PN; current verified NI/PN; current shown False; changed fields none
    typed precedence: PN (regex:sap_fixes_the_analysis_v1)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
probiotics-aad-prevention::30439760::Antibiotic-associated diarrhoea | adjudicator | mc-0e7fc4f27d4dbc22bae1b9625540a252
  response read by frozen replay: True
  evidence bytes unchanged: True
  held questions: 1.1, 2.3, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5
  current questions: 2.3, 3.3, 3.4, 4.1, 4.2, 4.3, 4.4, 4.5
  1.1: held NI/Y; current verified NI/Y; current shown False; changed fields none
    typed precedence: Y (regex:sequence_generation_v2)
  pre-A2 parser reproduces held prompt: False
  codex reply parseable pre-A2/current: True/True
  agy reply parseable pre-A2/current: True/True
[rob2_served]
manifest entries with regenerated current prompts: 56/56
manifest entries not consumed (no current prompt): 0/56
manifest/current prompt hash mismatches: 0/56
held/current prompt byte mismatches: 0/56
manifest/held prompt hash mismatches: 0/56
reader held/current prompt byte mismatches: 0/56
adjudicator held/current prompt byte mismatches: 0/0
successful held records: 56/260
unparseable successful replies: 0/56
unparseable record IDs: none
parseable successful replies: 56/56
replies with conflicting duplicate rows: 0/56 parseable successful replies
mismatching entries (key | role | record id):
none
```

## Static versus dynamic disclosure

| Ingredient | Static or dynamic | Disclosure |
|---|---|---|
| Test evidence, PMID 1, quote, answers, timestamps | Static synthetic fixtures | Offline behavioural plants only; no research finding |
| Store/manifest names and audit labels | Static configuration | Repository-relative, no research result constants |
| Pre-A2 parser comparator | Static historical implementation | Copied from the parent of e83be9e07 for in-memory diagnosis only |
| Source-selection environment | Explicit runtime configuration | Caller leaves flags unset or supplies exactly "1", and supplies AACT_DIR; effective settings printed with each run |
| Current prompts and disagreement sets | Dynamic | Generated by current frozen code from held sources and readings |
| Record hashes, parseability, conflicting rows, counts | Dynamic | Derived from validated files on disk; no hardcoded measured outputs |
| Request's captured output | Static snapshot of a dynamic run | Exact output of the command above |

## Behavioural verification

The tests write realistic, integrity-valid JSON records with
`reproducible_ai.model_source.write_record` into `tmp_path`, redirect `rd.REC_DIR`,
and spy on `model_source.replay` while preserving its real response validation and
parsing. No invented helper on `rd` is used. Live calls use an offline `_call` spy
and synchronous pool. Fresh reader agreement and fresh adjudication controls retain
PY in both replay and live modes without replacement calls.

All defect cases retain the same `xfail(strict=True)` reason. Strict xfail is a
**temporary behavioural regression marker**, NOT signature enforcement: an unexpected
pass fails the normal run, but an unrelated exception can still count as xfailed.
Therefore `--runxfail` assertions must also be inspected.

With TMP/TEMP as above, verification used:

```powershell
python -m pytest -s -q -p no:cacheprovider tests/test_rob2_dual_a4.py --runxfail --tb=short --basetemp=C:/mh-lanes/tmp/a4-revision-runxfail-20261014
python -m pytest -s -q -p no:cacheprovider tests/test_rob2_dual_a4.py tests/test_rob2_dual.py --basetemp=C:/mh-lanes/tmp/a4-revision-normal-20261014
```

The default pytest temporary subdirectory was inaccessible; these fresh explicit
basetemp directories resolved that setup failure. The successful diagnostic run
reported **11 failed, 4 passed** with no setup errors:

- Duplicate PY/PN and PN/PY: returned `(PY, None)` and `(PN, None)` respectively,
  rather than `(NI, AMBIGUOUS_CONFLICTING_ROWS)`.
- Held-prompt stale replay, individually for Codex, Agy, adjudicator: the spy saw
  that stale record ID reach response replay.
- Manifest stale replay, individually for Codex, Agy, adjudicator: the spy likewise
  saw the stale record ID reach response replay.
- Live stale held record, individually for Codex, Agy, adjudicator: no replacement
  call for that role/current prompt occurred.
- All four unmarked fresh controls passed on the frozen implementation.

Normal combined suite: **11 passed, 11 xfailed** (four A4 controls plus seven
existing dual-reader tests passed).

This request finalisation reran that combined suite with
`--basetemp=C:/mh-lanes/tmp/a4-final-normal-20261014`: **11 passed, 11 xfailed**.
The audit now accepts an omitted `ROBGRADE_DEV_OPEN_CC` as disabled and rejects
values other than unset or exactly "1" with an explicit configuration message
and exit code 1, before measurement.

## Application after signature

Review the concrete implementation patch by Codex and Agy, declare the amendment
in `outputs/robgrade/AMENDMENTS.json` bound to that reviewed patch, and remove the
regression xfail marks. Compare amended and frozen replay objects and scores before
claiming output invariance. That comparison is not performed by this request-only
revision; prompt agreement alone is not proof of identical amended outputs.

## Signature

[ ] A4 -- Mahmood (to be relayed by Dispatch; the lane records, it does not sign)
