# M2 battery — counterexamples through the real publication route

Topic `glp1-ra-mace-t2d`. Served tree = commit `8b1fb37d` (origin/main at the time; main has since moved to 8f14f411 with the PRE-RELEASE relabel). Repaired trees = the same commit plus branch `m2/bind-hand-rows` at two states: **step 1** (hand-row binder only; the parity hand status still a build refusal) and **final** (parity ruling, W1b, companion documents, locator refinements). Every row below is MEASURED: `scripts/build_topic.py` then `python -m harness.gate` on the real inputs, one committed input changed per case, exact byte restoration checked after every case (`restoration exact` = the four served files byte-equal the control rebuild). Runner: `scripts/m2_battery.py` (measured reports: `outputs/m2/battery_{served,step1,final}_report.json`; this table is rendered from them by `scripts/m2_battery_table.py`; the final column is the run on the landing bytes, 2026-09-21). The same 28 cases run in process under the gate's unit-test limb as `tests/test_m2_battery.py` (45 s).

**How to read the step-1 column.** Fifteen cases there show a PAIR: the first build refused the WHOLE topic (`PARITY-RELATION REFUSED: hand status 'SUPERSET' disagrees with computed relation OVERLAPPING`) because a row-level refusal moved the pool and the hand-written parity status went stale; the harness then re-declared the hand status to the computed relation and ran again, and the verdict after the arrow is that SECOND build. A verdict that required an edit to reach is the verdict plus the edit — those pairs are kept here as the record. In the final column the same cases refuse on the FIRST build (0 cascades): the parity ruling (computed status, hand text rendered stale, a recorded acknowledgement when the relation changes) removed the cause.

| id | class | change | served 8b1fb37d | step 1 (binder only) | final | restoration exact (all three) |
|---|---|---|---|---|---|---|
| W1a | wrong interval | SOUL hand entry: ci_high 0.96 -> 0.98 (source unchanged) | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W1b | wrong effect measure | SOUL hand entry: scale HR -> OR (source says hazard ratio) | WRONG_ADMISSION | WRONG_ADMISSION | REFUSED_CORRECT_REASON | True |
| W1c | wrong effect (incoherent) | SOUL hand entry: effect 0.86 -> 0.68 (source string unchanged) | GATE_REFUSED_CORRECT_REASON | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W1d | wrong effect (coherent lie) | SOUL hand entry: effect AND source string say 0.68; held abstract says 0.86 | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W1e | wrong effect (RR complement) | SOUL hand entry: effect 0.14 = 1-0.86 (source string says 0.14) | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W2a | wrong source location (document) | SOUL canonical entry cites LEADER's full text as the document holding its span | REFUSED_WHOLE_BUILD | REFUSED_WHOLE_BUILD | REFUSED_WHOLE_BUILD | True |
| W2b | wrong source location (trial) | SOUL's digits filed as an override under EXSCEL (28910237) | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W3a | wrong endpoint ownership | LEADER override: MI-only table row 0.86 (0.73-1.00) claimed as 3-point MACE | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W3b | wrong endpoint ownership (abstract) | ELIXA hand entry: HF-hospitalisation HR 0.96 claimed as 3-point MACE | WRONG_ADMISSION | REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W4a | excluded component treated as included | SOUL held abstract now says nonfatal stroke was EXCLUDED; hand entry still claims 3-point MACE | WRONG_ADMISSION | WRONG_ADMISSION | WRONG_ADMISSION | True |
| W4b | excluded component treated as included (machine route) | SUSTAIN-6 held abstract now says nonfatal stroke was EXCLUDED (abstract-extracted row) | WRONG_ADMISSION | WRONG_ADMISSION | WRONG_ADMISSION | True |
| W5a | stale approval | SOUL held abstract corrected to HR 0.88 (0.79-0.98); the 2026-09-13 approval still says 0.86 | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| W5b | stale approval (canonical span) | same erratum; SOUL entry carries a verbatim source_span that the held abstract no longer contains | REFUSED_WHOLE_BUILD | REFUSED_WHOLE_BUILD | REFUSED_WHOLE_BUILD | True |
| P1 | control | served inputs, no change | ADMITTED | ADMITTED | ADMITTED | True |
| P2 | representation variant | SOUL held abstract uses Lancet middle-dot decimals (0·86; 0·77 to 0·96) | ADMITTED | ADMITTED | ADMITTED | True |
| P3 | legitimate full-text prose override | LEADER override: primary composite 0.87 (0.78-0.97) quoted verbatim from the held full text | ADMITTED_UNCHECKED | ADMITTED | ADMITTED | True |
| P4 | canonical hand entry | SOUL entry carries its verbatim source_span + document_ref (records.json) | ADMITTED | ADMITTED | ADMITTED | True |
| P5 | documented decision on unresolved evidence | ELIXA typed refusal: 4-point composite, reviewer-signed, span held | DOCUMENTED_DECISION_RECORDED | DOCUMENTED_DECISION_RECORDED | DOCUMENTED_DECISION_RECORDED | True |
| L0 | control (table row) | LEADER override: Table 1 'Primary composite outcome' row 0.87 (0.78-0.97) | ADMITTED_UNCHECKED | ADMITTED | ADMITTED | True |
| L1 | wrong endpoint: MI row | LEADER override: 'Myocardial infarction' row 0.86 (0.73-1.00) as 3-point MACE | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L2 | wrong endpoint: stroke row | LEADER override: 'Stroke' row 0.86 (0.71-1.06) as 3-point MACE | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L3 | wrong endpoint: expanded composite | LEADER override: 'Expanded composite outcome' row 0.88 (0.81-0.96) as 3-point MACE | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L4 | wrong endpoint: CV death | LEADER override: 'Death from cardiovascular causes' row 0.78 (0.66-0.93) as 3-point MACE | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L5 | comparator direction (numbers) | LEADER override: inverted tuple 1.15 (1.03-1.28), declared placebo vs liraglutide | GATE_REFUSED_CORRECT_REASON | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L6 | comparator direction (declared) | LEADER override: held 0.87 tuple with comparator_direction 'placebo vs liraglutide' | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L7 | analysis set | LEADER override: held 0.87 tuple declared as the per-protocol analysis | WRONG_ADMISSION | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |
| L8 | declared harmless normalisation | LEADER override: Table 1 primary row, en dash, header-declared scale, ci_pct 95 | ADMITTED_UNCHECKED | ADMITTED | ADMITTED | True |
| L9 | ambiguity must ABSTAIN | LEADER override: point 0.86 only, span = whole Table 1 (0.86 sits in the MI row AND the stroke row) | REFUSED_OTHER_REASON | REFUSED_WHOLE_BUILD (PARITY-RELATION, hand status re-declared to OVERLAPPING) → REFUSED_CORRECT_REASON | REFUSED_CORRECT_REASON | True |

## Tallies (28 cases)

- served: WRONG_ADMISSION 16, ADMITTED 3, ADMITTED_UNCHECKED 3, GATE_REFUSED_CORRECT_REASON 2, REFUSED_WHOLE_BUILD 2, DOCUMENTED_DECISION_RECORDED 1, REFUSED_OTHER_REASON 1
- step 1: REFUSED_CORRECT_REASON 16, ADMITTED 6, WRONG_ADMISSION 3, REFUSED_WHOLE_BUILD 2, DOCUMENTED_DECISION_RECORDED 1; parity cascades 15
- final: REFUSED_CORRECT_REASON 17, ADMITTED 6, REFUSED_WHOLE_BUILD 2, WRONG_ADMISSION 2, DOCUMENTED_DECISION_RECORDED 1; parity cascades 0

## Named misses in the final column (not fixed here, by decision)

- W4a / W4b — an excluded component treated as included: the layer-1 exclusion relation, not this object.
- W2a / W5b — a canonical `source_span` no longer in the held document: `verified_inputs._validate` raises at load and the whole topic dies (right check, wrong scope; design note §3).

## Verdict vocabulary

WRONG_ADMISSION — the changed row was pooled and the gate passed. REFUSED_CORRECT_REASON — the row was set aside or refused with the named semantic code (`ENDPOINT_UNBOUND` abstain, `RESULT_INCOMPATIBLE`), the trial stays visible, the page publishes. GATE_REFUSED_CORRECT_REASON — right reason, page scope (row still pooled, page withheld). REFUSED_WHOLE_BUILD — the build raised. ADMITTED / ADMITTED_UNCHECKED — a positive pooled with / without a binding. DOCUMENTED_DECISION_RECORDED — a signed typed refusal rendered as such.
