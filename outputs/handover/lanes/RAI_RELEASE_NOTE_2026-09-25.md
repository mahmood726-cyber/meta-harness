# Lane `rai` → main lane: state for the candidate release (2026-09-25)

Every item below is on `main` and was landed the same way: hook (all 11 limbs) → CI green on every step of that exact
SHA → pushed only when main was its ancestor → proved by `git ls-remote` plus raw-fetched blobs equal to the commit's.

## On main
| SHA | what | served effect |
|---|---|---|
| `ed0524d2` | **RAI-D7 / RAI-C9.** `harness/result_changes.signature_problem` refuses a DELEGATED_BULK_ACCEPTANCE by its record TYPE (status, typed fields, recorded basis); the phrase list is gone | none: 28 of 28 real served signatures still publish. 32 pages re-certified; invariance 32 of 32 |
| `c82e86bd` | **R1 + R4 in extract.py.** Typed values (NamedTuples); number fragments refused (`harness/whole_numbers.py`, new); `_NEQ` word boundary; RX-D1 | none: the extraction snapshot is byte-identical. On every page the only change is the certificate code map (2 new pinned modules, 82 → 84) |
| `c82e86bd` | **CODEX-2.** Every codex call is logged: `registry/model_calls/lane_log/rai.jsonl` | none |
| `6e0c7379`, on main via `9ee0b06b` (landed 2026-09-25 ~13:05; CI green every step; 5 of 5 fetched blobs equal) | **R3 complete.** 407 of 407 harness regex sites carry named plants; located defects are strict xfails | none (regex_layer/ and tests only) |

**Proven on current main (`f3034ecc`):** `tests/test_delegated_served_gate.py` 7 of 7. Its two plants returned `None`
before the fix, meaning the notice would have published.

## R1–R4 scorecard for the release note
Derived by `python -m regex_layer.scorecard` (`outputs/regex_layer/SCORECARD.md`, one row per pattern with its reason);
never hand-written. Scope: the 23 compiled patterns of `harness/extract.py`.

| property | on main now | after the pending pinned landing |
|---|---|---|
| R1 typed values | 8 of 23 (14 not applicable, 1 open: `_ARMP`) | 9 of 23 (14 not applicable, 0 open) |
| R2 precision / recall measured | 23 of 23 | 23 of 23 |
| R3 named plants | 23 of 23 | 23 of 23 |
| R4 fragment refusal | 11 of 23 (12 not applicable, 0 open) | 11 of 23 (12 not applicable, 0 open) |

- "Not applicable" always carries its reason: a classifier returns a bool (7), a dead pattern has no reader (4), or the
  value is one integer rather than a tuple (3, R1 only). `_EFFECT` is left out of R4 because other lanes' modules
  read it; 0 fragments were found in the held text.
- Harness-wide: R3 407 of 407 regex sites planted; R2 95 of 367 other sites measured.
- R2 is sampled recall, not population recall. `_RATE_EVPT` fired 0 times in its 55 labels, so its precision is
  undefined (0 of 0), not 100%.

## Touches your files: please read
- **`harness/result_changes.py` (yours).** RAI-D7 was ordered fixed at the served gate, so `signature_problem` gained a
  type check that runs first (`DELEGATED_STATUS`, `DELEGATED_BASIS`, `DELEGATION_FIELDS`, `_delegation_problem`).
  Mirrored to `docs/harness/`. Nothing else in the file changed.
- **Plants cover your files but never gate your commits.** `regex_layer/lanes.py`: a pattern you edit or remove is
  skipped as STALE, and a new site is reported, not refused. Checked both ways.
- **Located defects in your files:** `regex_layer/HANDOVER_MAIN_LANE.md`. Two are served now:
  - the blind comparator page ignores `comparator_k` (omega3 shows 8, verified 28), `pipeline.py` ≈ line 2286;
  - 16 review pages say the comparator count is "not stated" (RX-X6).

## Gate gap for the release captain: bundle staleness is invisible before a commit
`scripts/build_bundle.py:1280` records a producer as `HEAD:harness/target_endpoint.py`. As a result:
- any commit that changes that file makes the committed glp1 BUNDLE.json stale the moment it lands;
- the pre-commit hook compares against the old HEAD, so it passes, and only CI on the new SHA fails.

This happened to my pinned landing (CI run 36148266505). It was fixed by rebuilding the bundle in a follow-up commit.
Anyone changing a file that build_bundle.py reads by `HEAD:` needs the same second commit.

## For the evidence lane: your codex calls were logged under `rai` (my defect, fixed)
- `model_call_live.LANE` was hard-coded to `"rai"`. The 53 calls made by `evidence/scripts/codex_job.py` (caller
  lane `evid/evidence-records`, 2026-09-25 06:20–07:16Z) were therefore written into
  `registry/model_calls/lane_log/rai.jsonl` with `"lane": "rai"`.
- The fix (next landing) logs each call under its caller's lane:
  - `registry/model_calls/lane_log/evid__evidence-records.jsonl` for yours;
  - `unattributed.jsonl` for a caller that names none (`scripts/outcome_judgments.py` names none).
- Plant: `tests/test_lane_log_attribution.py`, which failed 4 of 4 on the old code.
- The 53 existing lines stay where they are; the log is append-only and I don't rewrite another lane's records. Their
  own `caller.lane` field says whose they are.

## In flight (my files; will land the same way)
- **R1** in `screen.py` (`ScreenDecision`) and `eligibility_chain.py` (`Reading`), and the last extract.py tuple
  (`ArmPercentHit`).
- **Seven owned-defect fixes:** RX-TE1..3 (CV death across a conjunction; non-vascular / non-fatal), RX-EC1/EC2
  (`**Population:**` and em-dash headers), RX-EC3 ('children and adults').
  - RX-EC2 will make colchicine-recurrent-pericarditis compile its follow-up-window criterion.
- **Four zero-radius R4 fixes:** `_ANCHOR_RX` plural, `_SUBGROUP`, `_RECURRENT_PERSONTIME`, U+2007/U+2008 separators.
- **R4 ambiguity, 9 sites:** when a site's candidates disagree, the site returns its existing absent result and never a
  new guess (`r4_ambiguity_step.py`). The 9 plants failed before the step and pass after.
- **The lane-log attribution fix** described above.
- **These are pinned.** The landing will rebuild all 32 pages and carry the rebuild-invariance report. Any served
  change appears there and is held for Mahmood, not landed.

## Waits on Mahmood (nothing served changes until he decides)
- **Screening delegated acceptance:** 132 of 269 accepted, 137 of 269 unresolved.
  - Before → after if applied: 14 records leave the screened-in set; statins "Major vascular events" goes from HR 0.68
    (k = 2) to no estimate.
- **Comparator counts:** 38 recorded proposals, 4 of 4 controls agree; individual signatures needed.
- **Candidate regex fixes that move served text:** `_K` (14 review pages + 13 blind pages). Before → after is in
  `outputs/regex_layer/RADIUS_fix_k.json`.
- **R4 ambiguity refusals that move served output (8 sites, held).** The audit found 17 sites in extract.py that
  silently take the first of several candidates that disagree:
  - 9 have zero served radius and land in the pinned package (18 of 10,098 extractions become absent, 0 served
    rows; the 32-page rebuild confirms it);
  - `defn_window` was measured as 0 served, but the 32-page rebuild showed a served change, so it is held.
    statins-primary-prevention-elderly would lose its "Composite heterogeneity" note and the compatibility-audit
    "Endpoint definition" row. The estimate is unchanged. The radius missed it because it measured `extract_trial`,
    not `extract.composite_heterogeneity` via the pipeline;
  - 7 would move served values, each to absent. Measured before → after:
    - `effect_first`: 6 rows (dpp4 23992601 HR 1.00 → 1.02, a NEW guess from a fallback; this must be fixed
      before it could land);
    - `sent_hr`: 10 rows, e.g. glp1 27633186 HR 0.74;
    - `sent_effect`: 2 rows;
    - `eio_first`: 14 comparator effects;
    - `arm_pairs`: 2 rows;
    - `k_first`: 2 comparator k;
    - `arm_ns`: a fallback reads a new denominator (14/82 → 14/81).
  - The full list is in `outputs/regex_layer/RADIUS_r4_comparator.json` and `RADIUS_r4_*.json`.
  - Each is a strict xfail in `tests/test_r4_ambiguity.py`.
  - Coverage caveat: 58 of 127 served rows do not come from `extract_trial`, so this radius cannot see them.
