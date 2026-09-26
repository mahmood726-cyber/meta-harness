# Lane `rai` → main lane: state for the candidate release (2026-09-25)

Every item below is on `main` and was landed the same way: hook (all 11 limbs) → CI green on every step of that exact
SHA → pushed only when main was its ancestor → proved by `git ls-remote` plus raw-fetched blobs equal to the commit's.

## On main
| SHA | what | served effect |
|---|---|---|
| `ed0524d2` | **RAI-D7 / RAI-C9.** `harness/result_changes.signature_problem` refuses a DELEGATED_BULK_ACCEPTANCE by its record TYPE (status, typed fields, recorded basis); the phrase list is gone | none: 28 of 28 real served signatures still publish. 32 pages re-certified; invariance 32 of 32 |
| `c82e86bd` | **R1 + R4 in extract.py.** Typed values (NamedTuples); number fragments refused (`harness/whole_numbers.py`, new); `_NEQ` word boundary; RX-D1 | none: the extraction snapshot is byte-identical. On every page the only change is the certificate code map (2 new pinned modules, 82 → 84) |
| `c82e86bd` | **CODEX-2.** Every codex call is logged: `registry/model_calls/lane_log/rai.jsonl` | none |
| `6e0c7379`, on main via `9ee0b06b` (landed 2026-09-25 ~13:05; CI green every step; 5 of 5 fetched blobs equal) | **R3: every INVENTORIED regex site is planted** (407 of the 407 sites `regex_layer.inventory` finds). This is not every regex use in `harness/`: 19 call sites build their pattern at run time and are outside the inventory (see "R3 coverage, exactly" below). Located defects are strict xfails | none (regex_layer/ and tests only) |
| `e403573d` + `2012ff1d`, on main via `c62b6b12` (landed 2026-09-26 01:21; CI green on every step twice; 15 of 15 fetched blobs equal) | **R1 + R4 pinned landing.** Contents: typed values in screen.py / eligibility_chain.py and `ArmPercentHit`; the 7 owned regex defects fixed; 4 zero-radius R4 fixes; R4 ambiguity refusal at 9 sites; the lane-log attribution fix. Then the glp1 bundle was rebuilt on the code commit | none. Rebuild invariance vs `29f0a719`: 32 of 32, with 0 estimates, outcomes or text changed. pva P4: 0 of 224 served tuples changed. Layout tests 39 of 39. All 32 pages were regenerated on the tabs layout (B-9) |

**Proven on current main (`f3034ecc`):** `tests/test_delegated_served_gate.py` 7 of 7. Its two plants returned `None`
before the fix, meaning the notice would have published.

## R1–R4 scorecard for the release note
Derived by `python -m regex_layer.scorecard` (`outputs/regex_layer/SCORECARD.md`, one row per pattern with its reason);
never hand-written. Scope: the 23 compiled patterns of `harness/extract.py`.

| property | on main (`c62b6b12`), final |
|---|---|
| R1 typed values | **9 of 23** (14 not applicable, 0 open) |
| R2 precision / recall measured | **23 of 23** |
| R3 named plants | **23 of 23** |
| R4 fragment refusal | **11 of 23** (12 not applicable, 0 open) |

Beyond fragment refusal, R4 ambiguity refusal is in place at 9 extract.py sites, and 8 more are held for Mahmood (below).
The scorecard counts fragment refusal only.

- "Not applicable" always carries its reason: a classifier returns a bool (7), a dead pattern has no reader (4), or the
  value is one integer rather than a tuple (3, R1 only). `_EFFECT` is left out of R4 because other lanes' modules
  read it; 0 fragments were found in the held text.
- Harness-wide: R3 is 407 of 407 **inventoried** sites planted, and R2 is 95 of 367 other sites measured. The inventory
  is not the whole population; see below.

### R3 coverage, exactly (corrected 2026-09-26 after pva's flag)
The earlier line "407 of 407 regex sites planted" stated no N and hid the blind spot. The exact statement:

- **N = the sites `regex_layer.inventory.sites()` finds** (literal patterns in `re.*` calls and module-level compiles in
  `harness/`). Re-measured at `6e0c7379`, `9ee0b06b`, `c62b6b12` and `b284e085`:
  - 407 sites, 407 distinct site keys, 407 plant keys;
  - 407 of 407 sites have a plant, and 0 plants point outside the inventory.
  - The "407" is a site count. pva/audit's figure of **401** (RAI-C12) did not reproduce with the inventory's own code
    on any landed commit. I report the measured 407 and flag the disagreement to the auditor rather than adopt either
    number unmeasured.
- **Outside N (the blind spot): 29 `re.*` calls build their pattern at run time, and 19 of them are not in the
  inventory** (`python regex_layer/nonliteral_sites.py .`, an AST scan, on `b284e085`):
  - **9 build the pattern by `+` concatenation.** These are exactly RAI-C13: `comparator_panel.py:57 validate`,
    `hand_binding.py:204 _present`, `:259 _effect_pattern_ok`, `:481 _ci_pct_ok`,
    `lexicon.py:164 matches_only_as_subtype`, `trial_family.py:97 randomised_contrasts`, `:406` and `:421 prepare`,
    `verify.py:27 _digits_in`.
  - 3 search for `re.escape(term)` only: `comparator_second_pass.py:20/32`, `extract.py:473`.
  - 7 take a pattern variable whose source I have not traced: `comparator_truth.py:109`, `compat_check.py:68`,
    `extract.py:711`, `hand_binding.py:442/444`, `second_source.py:63`, `trial_family.py:58`. They may or may not
    reuse inventoried literals.
  - These 19 have **no plants**, so R3 says nothing about them.
- **One of the 9 reads number fragments (PVA-D12, confirmed here):** `hand_binding._present` refuses a digit after the
  number but not a `.` or `,`.
  - `_forms(1.0)` includes `"1"`, which is found inside "1.03"; `"10"` is found inside "10,033".
  - pva measured **0 of 132** served hand-bound values that depend on a fragment (on the 39 served hand-bound rows).
    It is latent today, with no served consequence.
  - `hand_binding.py` is not this lane's file, so the fix is yours: the `whole_numbers` separator rule used in
    extract.py would close it.
- **Update (blind spot closed where honest, post-freeze):**
  - `regex_layer.inventory` now counts built patterns as sites (kind `built:*`), so N is **426**. The plant for the
    change failed on the old inventory.
  - Function-level plants (`regex_layer/specs_built.py`, `tests/test_built_plants.py`) call the harness function that
    builds each pattern. **R3 is now 423 of 426.** The 3 unplanted sites need on-disk fixtures to reach:
    `comparator_panel.validate` (raises, and reads a hash-pinned document) and `trial_family.prepare` :406 and :421
    (read `cache/<slug>/family_*.json`).
  - The plants found **3 more instances of the PVA-D12 fragment class, all in your files.** Each is a strict xfail,
    and each was confirmed by calling the function:
    - `hand_binding._effect_pattern_ok("HR 1.03 (95% CI 0.5-2)", {effect 1, ci 0.5–2})` → True;
    - `verify._digits_in("HR 1.03", 1)` → True;
    - `comparator_truth.span_or_not_held("The HR was 1.03 overall.", 1)` → FOUND.
  - `hand_binding._ci_pct_ok` does not have the defect.
  - The served impact of these three is **not measured**. pva's 0 of 132 covers `_present` only.
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

## B-9 (pva): answered: the re-certification is rebuilt on the tabs layout
- The old branch head `e67d5b97` was based on pre-tabs main. It is superseded, never to be merged, and none of its
  generated pages are used.
- The R1/R4 code was re-applied by its 5 step scripts onto a clean reset to `29f0a719`, which contains the tabs commit
  `c23a7e91`. All 32 pages were then regenerated from each page's recorded command on the new layout.
- Rebuild invariance vs `29f0a719`: 32 of 32 PASS, with 0 primary estimates changed, 0 outcomes moved, 0 served text
  changes, and 0 blocks lost or added.
- `tests/test_page_tabs_layout.py` + `tests/test_certificate_ui.py` on the regenerated tree: 39 of 39.
- pva's P4 served-number probe (`pva/v1/v1_accept.py --source git --only P4`, run from a copy with `REPO` pointed at
  the rai clone) on the code commit `e403573d` vs `29f0a719`: **PASS**, with 224 tuples before and 224 after, 0 changed
  and 0 unsigned. P1 served == committed PASS. B-9 asked for 0 of 256; this probe counts 224 tuples for this
  release pair, and that is the number reported here.

## Gate gap for the release captain: bundle staleness is invisible before a commit
`scripts/build_bundle.py:1280` records a producer as `HEAD:harness/target_endpoint.py`. As a result:
- any commit that changes that file makes the committed glp1 BUNDLE.json stale the moment it lands;
- the pre-commit hook compares against the old HEAD, so it passes, and only CI on the new SHA fails.

This happened to my pinned landing (CI run 36148266505). It was fixed by rebuilding the bundle in a follow-up commit.
Anyone changing a file that build_bundle.py reads by `HEAD:` needs the same second commit.

## Gate observability: a killed hook leaves no trace (`scripts/verify_all.py:21`, yours)
- `verify_all.py` re-wraps `sys.stdout` in a `TextIOWrapper` without `line_buffering` or `write_through`. Its output
  is therefore held in an 8 KB buffer when stdout is a file or pipe, and `PYTHONUNBUFFERED` does not help.
- If the hook's process tree dies mid-run, the log holds only "GATE: running the full standard": no limb results and no
  REFUSED line.
- This happened to 3 of my hook runs on 2026-09-25, each 40–75 min in. Under a stack dump, the process was verifiably
  in the unit-test limb.
- Suggested fix (yours to make): `io.TextIOWrapper(..., line_buffering=True)`. A dead gate then says how far it got.
- The gate still fails closed: no commit is made. So this is observability, not safety.

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

## What the R1 + R4 pinned landing (`c62b6b12`) contains
- **R1** in `screen.py` (`ScreenDecision`) and `eligibility_chain.py` (`Reading`), and the last extract.py tuple
  (`ArmPercentHit`).
- **Seven owned-defect fixes:** RX-TE1..3 (CV death across a conjunction; non-vascular / non-fatal), RX-EC1/EC2
  (`**Population:**` and em-dash headers), RX-EC3 ('children and adults').
  - RX-EC2 lets colchicine-recurrent-pericarditis compile its follow-up-window criterion; the rebuild shows no served
    text change from it.
- **Four zero-radius R4 fixes:** `_ANCHOR_RX` plural, `_SUBGROUP`, `_RECURRENT_PERSONTIME`, U+2007/U+2008 separators.
- **R4 ambiguity, 9 sites:** when a site's candidates disagree, the site returns its existing absent result and never a
  new guess (`r4_ambiguity_step.py`). The 9 plants failed before the step and pass after.
- **The lane-log attribution fix** described above.
- **Pinned:** all 32 pages were rebuilt from their recorded commands on the tabs layout. The invariance report
  (32 of 32, no served change) is in the commit message. The one step that did change served text (`defn_window`)
  was taken out and is held below.

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
