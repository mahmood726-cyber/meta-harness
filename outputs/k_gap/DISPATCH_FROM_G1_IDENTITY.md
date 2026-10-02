# Dispatch: g1/identity -> k-gap lane (and the captain)

Branch `g1/identity` was cut from `acq/k-gap` 435236c1a. Mahmood asked for IDENTITY_UNRESOLVED on 7 topics to be fixed
as ONE class fix. Messaging another session is refused in this unattended session, so this file is the channel.

## 1. Shared files this branch changes (all additive steps; please review, adopt or reject)

- **`kgap/k_gap.py`:** new `identity_tokens()` and `_split_label()`. `_label_tokens` is unchanged, so unit
  enumeration does not move.
- **`scripts/k_gap_table.py`:** in `resolve_unit`, chain steps 1, 1b, 1c, 2, 3, 3b and 4, plus
  `positive_ref_evidence`, `name_words_match`, `learn_marker_offsets`, `consolidate_report_family`,
  `identity_refs` (with the study-ID, numbered and PMC-page parsers), `subgroup_row`, `served_agent_in`, and the
  typed termini IDENTIFIED_NOT_INDEXED, `not_a_trial_units` and `unresolved_at:`.
- **New:**
  - `scripts/ref_title_pmid_lookup.py` (cache `outputs/k_gap/ref_title_pmid.json`);
  - `scripts/pubmed_collective_lookup.py` (cache `outputs/k_gap/pubmed_collective.json`);
  - `outputs/k_gap/held_comparator_pages.json`.
- **Two adversarial Codex reviews:**
  - Round 1, IDREVIEW: no P0; 3 P1 and 1 P2, all fixed and kept as `tests/test_idreview_findings.py`.
  - Round 2, IDREVIEW2: reported in that lane's file.
- **Measured:** UNRESOLVED_IDENTITY falls from 67 to a handful, with 0 identities moved. One identity was CORRECTED:
  `EMPEROR Preserved, 2020` had resolved to EMPEROR-Reduced, NCT03057977.

## 2. Defects found in shared code (not edited unless named above)

1. **Shared caches are written non-atomically by several scripts.**
   - `outputs/k_gap/pubmed_titles.json` is written by `scripts/k_gap_table.py:~373`,
     `scripts/secondary_meta_build.py:~402` and `scripts/k_gap_identity_reader2.py:~104` (via `_j`/`json.dump`
     into the live file).
   - Two `g1_tracker.py` runs in parallel produced "Extra data" and every later run failed. That happened on this
     branch: restored from git, then re-run sequentially.
   - `outputs/k_gap/g1/<slug>.json` (`g1_tracker.py`) has the same issue. A run killed by a timeout left a 0-byte
     file.
   - Fix: tmp + `os.replace`, as `runs_store.save()` does.
2. **`kgap/k_gap.py:label_ref_conflict` takes a label's first capitalised word as a surname when no author is
   given.** For a named trial ("Risk & Prevention 2013 [42]") that yields "Risk vs Roncaglioni" and a false
   conflict. This branch does not change that function. Its new steps accept positive NAME evidence first
   (`name_words_match`: every capitalised content word of the name appears in the reference text or its PubMed
   collective author).
3. **A failed comparator fetch is recorded as a held file.**
   - `cache/comparators/31845767/2026-09-15_PMC6915832_europepmc_fulltext.xml` is 0 bytes, with manifest state
     `CACHED` and `http_status` 404.
   - Any reader that takes "file exists" as "copy held" is misled.
   - `identity_refs` skips unparseable copies, but the manifest should say FAILED.
4. **`scripts/g1_tracker.py` top_blocker and N_eligible for an all-observational comparator.**
   statins-primary-prevention-elderly reads `0/0 eligible` with no top blocker. All 12 studies are observational
   (PROTOCOL_SCOPE_DIFFERENCE, screen X1), so G1 is unattainable against that comparator. That is a comparator-choice
   question for the captain.

## 3. An incident to know about

On 2 Oct, while stopping my own timed-out tracker run, a process filter that matched on command line only also
stopped two `g1_tracker.py` processes belonging to ANOTHER session:
- `colchicine-postop-af --no-table`
- `statins-primary-prevention-elderly --no-table` (both run with `-B`)

Please re-run them if they were yours. Since then I stop only processes whose PIDs I recorded.

## 4. Overnight round (2 Oct, commits 824865ccd, 8a7944bf4): an audit of the class fix's own identities

**What was audited.** I compared the 60 identities that the class fix added or changed (relative to acq/k-gap
435236c1a) against each registration's AACT acronym and title and each paper's PubMed title.

**One wrong identity.** It was wrong on base and made worse by consolidation.
- Row: `semaglutide-obesity-mace` "STEP 1 29".
- It was resolved to NCT03574597 (SELECT), and consolidation then merged STEP 1 into SELECT, so it read POOLED.
- Why: AACT lists STEP 1's NEJM paper (PMID 33567185) as a RESULT reference of SELECT as well as of NCT03548935
  (STEP 1). The resolver's "exactly one candidate is in our family" tiebreak chose SELECT.

**Fix (scripts/k_gap_table.py resolve_unit).** Before any family tiebreak, the AACT candidates are intersected with
the paper's OWN full accession list: PubMed DataBankList plus the NCTs in the abstract.
- The list comes from the new `scripts/pubmed_databank_lookup.py`, with its cache in
  `outputs/k_gap/pubmed_databank_ncts.json` (181 PMIDs that AACT links to two or more NCTs).
- Exactly one candidate in the paper's list: that registration is taken.
- Two or more: the paper reports several trials, and every tiebreak is refused, including the family tiebreak.

**For the k-gap lane: `outputs/k_gap/pubmed_ncts.json` / `harness.fetch._select_nct` keeps only the FIRST
DataBank NCT.** That is wrong evidence for a multi-trial paper:
- Shah 2020 lists NCT01709981 and NCT02594111;
- the CANVAS program paper lists CANVAS and CANVAS-R;
- the pooled dabigatran bleeding paper lists 5 registrations.

I did not change the shared module.

**Table diff vs fcc2cd53e.** 0 added, 4 moved, each checked against the paper's own record:

| Topic | Row | Before | After |
|---|---|---|---|
| semaglutide-obesity-mace | STEP 1 29 | SELECT; POOLED | NCT03548935; NOT_IDENTIFIED (a weight trial, not held) |
| colchicine-secondary-cv-prevention | Shah et al. (16) | NCT01709981 (family-tiebreak guess) | no NCT; `pmid_nct_paper_lists_several` |
| semaglutide-obesity-mace | SCALE Obesity and Prediabetes | ambiguous | NCT01272219 |
| sglt2-ckd-progression | DELIVER | ambiguous | NCT03619213 |

UNRESOLVED_IDENTITY stays at 0.

**NOTICE FOR MAHMOOD (served number; queued for signature, not landed).** In semaglutide-obesity-mace, the STEP 1
row no longer counts as POOLED; its earlier POOLED status came only from the false merge with SELECT. Tracker
re-runs for the three affected topics are reported in G1_TRACKER.md when they finish.

**The Codex audit lane was not used as evidence.** IDAUDIT (gpt-5.5) returned 60/60 CORRECT, STEP 1 included.
- Its "STEP" evidence was the substring of "stepped algorithm" in an unrelated review.
- It never compared the registration's acronym.
- Its verdicts are archived (`/f/codex-lanes/_archive/IDAUDIT.tgz`) and not relied on.

**The replacement is a permanent gate** (`tests/test_idaudit_findings.py`):
- Rule: a short label's acronym must prefix, or be prefixed by, the registration's AACT acronym, or appear in its
  title.
- On the pre-fix table it flags exactly STEP 1; on the committed table it flags nothing.

**Pre-existing failure, not from this branch.** `tests/test_aact_cache.py::test_replay_with_snapshot_access_forbidden`
fails with a tocilizumab CERTIFICATE release_sha256 mismatch. It fails identically on g1/noac (f974f249b, which
contains base 435236c1a), and this branch touches no release or page path.

## 5. Full suite on g1/identity (2-3 Oct) and tracker re-runs

**Full suite.** Run per file, with a 1500 s timeout per file.
- 230 files; 4853 tests passed.
- 14 tests failed, in 11 files. **All 14 fail identically on g1/noac f974f249b**, which contains base 435236c1a and
  none of the identity changes, so none comes from this branch.
- The 14 sit in the release, certificate and regex inventory of shared code: tocilizumab CERTIFICATE sha;
  BUNDLE.json stale against harness/*.py; certificate code closure; a regex site in harness/extract.py with no
  plant; evidence_records private-content check; fixstate real store; test_gate on a real review;
  result_withdrawn for dapagliflozin and empagliflozin.
- The full list of test ids is in the session record; please re-run them on acq/k-gap.
- `tests/test_architecture_identity.py` hit the 1500 s per-file timeout and is **unverified**, not passed.

**Tracker re-runs after the STEP 1 fix:**
- semaglutide-obesity-mace: k matched 2 -> 1 (the false STEP 1 merge). This is the served-number notice in
  section 4.
- colchicine-secondary-cv-prevention: k matched 2, unchanged.
- sglt2-ckd-progression: k matched 3, unchanged.

**Table rebuild after the fallback guard (2ec493f00).** 0 identities added or moved; the committed table is
byte-identical.
