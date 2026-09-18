# LANE INT8 — stopped at the mandatory search-currency gate

**MEASURED: REFUSED. Integration stopped at step 6, as required by LANE_PROMPT.md.**
This is not a completed landing, certification, or full-standard PASS. No commit,
reset, checkout, stash, push, network operation, or search rerun was performed.

HEAD stayed `3f8add72d50b84eae2000625387e3194137a06ea`. Initial status contained 747 changed/untracked paths;
the pre-report status contains 1156 paths (these counts include scratch paths
and are not portfolio counts). Raw inventories are in `.tmp/int8/initial-status.z`
and `.tmp/int8/final-status.z`. The final inventory precedes this report and checkpoint.
The F: ProjectIndex and rewrite workbook were checked; neither was edited.

## Mandatory stop — exact measurement

LANE_PROMPT.md step 6 says: “if AQ2's edits changed the blob, the measurement is no
longer current: STOP and report; do not re-run the search”. This condition occurred.

| Engine | Git blob |
|---|---|
| Required r4 measurement / initial FB engine | `d278c2f7f852679ca513178bed1bf8182678ee8b` |
| Integrated engine, preserving topic_id refactor and AQ2 held-source support | `c659dc309f210a8b945b6a4de629fa6ac1594d66` |

`harness.search_completeness.check(Path.cwd())` returned `False`:

```text
search completeness REFUSED: engine changed since the published search_v2 measurement (d278c2f7f852 -> c659dc309f21); re-run scripts/search_v2_run.py and re-publish before landing || states: RAN_OK 0 of 21; RAN_OK_WITH_SOURCE_ERRORS 21 of 21; RAN_ZERO 0 of 21; RAN_ERROR 0 of 21; NOT_RUN 0 of 21
```

The check's generic remediation text asks for a rerun; the lane's explicit stop
instruction prohibits that action in this session. The runner recorded the false
verdict as JSON; its shell exit 0 means the diagnostic completed, not that the gate passed.
Machine-readable evidence: `.tmp/int8/search-completeness.json`.
The exact source delta is `.tmp/int8/engine-diff.txt`.

MEASURED: 21 of 21 topics in the registered MEASUREMENT set have the stored state
RAN_OK_WITH_SOURCE_ERRORS; 0 of those 21 have each of the other four named states.
These are held r4 states, not a new run and not evidence of currency after the merge.
INFERRED: the new held-source function changes the engine identity, so the old
measurement cannot certify this integrated engine. The pin/check was not weakened.

## Harvest completed before the stop

| Lane | Listed paths | Harvest result before manual resolution |
|---|---:|---|
| RV1 | 586 | 82 new, 23 copied, 1 retained, 480 identical; no conflict |
| RV2 | 606 | 90 new, 118 copied, 18 retained, 1 merged, 4 conflicts, 375 identical |
| LIT2 | 33 | 8 new, 15 copied, 3 merged, 7 conflicts |
| AQ2 | 29 | 22 new, 2 copied, 2 merged, 3 conflicts |
| ROB2 | 25 | 25 new; no conflict |
| AUD1 (step 5b, before r4) | 516 | 11 new, 9 copied, 131 retained, 2 merged, 5 conflicts, 358 identical |
| r4 | 144 | 137 new, 5 copied, 1 merged, 1 conflict |

RV1/RV2 lists came from their working-tree status, excluding scratch, lane files,
generated review/blind pages, local agent configuration and progress/blocker files.
The snapshot base was materialized in `.tmp/int8/base`: snapshot bytes where present,
otherwise `git show 3f8add72:<path>`, as prescribed. Other lists/bases were the named
handover lists and refs. Source clones were read only.

Conflict decisions:

- RV2 owned modules and GLP1 comparator/envelope caches use RV2 versions. RV1's
  claim schema, page/manuscript rendering and executable eligibility block remain.
  The regulatory manifest retains the fuller ELIXA source-conflict record and its spans.
- Generated index, blind-map, claim-scope and conflicting sensitivity-cache views
  were retained provisionally from the integration side. They require regeneration;
  they are not measurements of the final integrated code. Conflict copies are saved
  under `.tmp/int8/`. No generated review page was harvested from RV1/RV2.
- LIT2 text files were remerged after normalizing source-code line endings for the
  merge; held document bytes were not normalized. Its literal corrections coexist
  with the typed rendering. The index retains live FACT re-verification and adopts
  LIT2's qualified methodological stance. Superseded page branches remain delegated
  to the typed modules; definition/refusal and manuscript verification boundaries
  were applied there. The typed RoB renderer already withholds the unsupported
  aggregate percentage and requires item-level audit evidence.
- Gate-scorecard rows were unioned by gate_id; there were no differing rows with
  the same gate_id requiring selection.
- AQ2 held-source support was merged with the existing topic_id refactor. Its
  retrieval details render through the existing typed retrieval cells; obligation
  rendering was retained on the page. GLP1 held-source and obligation fields were
  added while preserving the existing topic fields. Invalidation merged with RV2.
- ROB2 proposals remain held objects; no proposal-to-assessment page wiring was added.
- AUD1 source/admissibility changes and tests were harvested. ADJ-GLP1-005 was added
  to the reviewer adjudication list; other adjudications were retained.
- r4 drivers were taken as the base, retaining run-date and protocol-commit handling;
  LIT2 source-state derivation and qualified register wording were reapplied.
  CAPTIONS keys and fixes entries/events were unioned. The fixes registry has all
  94 pre-r4 fix IDs; r4 updates the existing measurement entry. The r4 search
  completeness registry and all 128 listed snapshot files were harvested.

## Verification actually performed

`rg -l '^<<<<<<< ' harness scripts tests` produced no matches before each subsequent
harvest. `python -m compileall -q harness scripts` passed after each resolved harvest,
including r4. The final source-marker audit found 0 conflict-bearing Python files.
These are syntax/merge checks, not a substitute for tests or the full standard.

| Check | Integrated-tree result |
|---|---|
| Seven post-harvest source compilation checks | PASS |
| Search-completeness currency | REFUSED, verbatim above |
| Full unit/UI tests | NOT RUN before mandatory stop |
| Rebuild all 32 reviews | NOT RUN before mandatory stop |
| Retraction survival, 32-review universe | NOT RUN on integrated tree |
| Empty-AACT replay, 32-review universe | NOT RUN on integrated tree |
| verify_all full table / page publication gates | NOT RUN on integrated tree |
| AUD1 five plants on integrated tree | NOT RUN |
| Claim-scope sweep | NOT RUN |
| Ratchet signature | NOT SIGNED |

There is no current `n pages PASS of 32` result, no integrated full-standard table,
and no integrated plant refusal trace to paste. Prior lane outputs are not relabelled
as integrated results. In particular, FB's saved `second-pass.json` actually says
`validated_bindings: 30`; the prompt's 31 and the older PROGRESS prose are historical
claims, not the measured field in that file. FB's saved gate/retraction/replay logs
were read as baseline evidence only.

## Not reached / required before any landing

1. Resolve the search-measurement currency conflict through a separately authorized
   measurement or revised integration instruction. Do not change the pin to pretend
   the held r4 measurement used this engine; do not drop AQ2 solely to match the pin.
2. Complete step 7's authoritative held-artefact copy and byte-integrity checks.
   Some held files came through lane lists, but that is not completion of step 7.
3. Fix partial-span legacy binding and rerun the binder. The dapagliflozin `n1i=162`
   and colchicine `effect=0.44` faults remain unresolved at this stop.
4. Fix regulatory path handling from the manifest at source. AUD1's reported
   FLOW/envelope path failure has not been repaired or retested here.
5. Regenerate every effect_types verdict and all 32 reviews with --now 2026-09-11;
   run the prescribed ordered renderers, five AUD1 plants, retraction survival,
   empty-AACT replay, full standard, publication gates and claim-scope sweep.
6. Report GLP1 strands, FACT precision split, panel states, sensitivity comparison,
   comparator relations and release-certificate fields from that successful rebuild.
   They are deliberately not reported as fresh measurements from stale served objects.
7. Address actual refusals at source, then sign the honest ratchet only when supported.
   No commit is authorized by this task.

## Static versus dynamic disclosure

| Item | Static policy/input | Dynamic evidence |
|---|---|---|
| Required engine identity | d278c2f7 prefix from lane instructions | Full r4/current blobs measured by git hash-object |
| Stop decision | Step 6 stop-on-mismatch rule | False check result and exact refusal above |
| Harvest scope | Named lane lists, bases and ownership rules | Working-tree status, merge outcomes, retained conflict files |
| Search counts | Named MEASUREMENT split | Stored r4 candidate topic states read by the existing check |
| Clinical results and release claims | None newly asserted | Rebuild and validation not reached |

CLAIMED lane findings, including prior sensitivity benchmarks and prior plant
successes, remain attributed to their source reports. No synthetic research output,
clinical estimate, timestamp, identifier validation, or completed release is invented.
