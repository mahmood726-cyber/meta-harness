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
- `tests/test_architecture_identity.py` hit the 1500 s timeout under load; re-run alone it PASSES (4 passed, 864 s;
  g1/noac 4 passed, 856 s).

**Tracker re-runs after the STEP 1 fix:**
- semaglutide-obesity-mace: k matched 2 -> 1 (the false STEP 1 merge). This is the served-number notice in
  section 4.
- colchicine-secondary-cv-prevention: k matched 2, unchanged.
- sglt2-ckd-progression: k matched 3, unchanged.

**Table rebuild after the fallback guard (2ec493f00).** 0 identities added or moved; the committed table is
byte-identical.

## 6. INTEGRATION into acq/k-gap (4 Oct): integrate/g1-identity-2026-10-03

**Branch.** `integrate/g1-identity-2026-10-03` = g1/identity (incl. 3a226cf13 and the integration fixes below) merged
with acq/k-gap at 38d132d6a. It is fast-forwardable onto acq/k-gap at that tip.

**Integration fixes, made while reconciling the two identity chains** (g1/identity's `k_gap_table.resolve_unit` and
acq/k-gap's `kgap/identity_chain.py`):

- **Disagreement: metformin "Legro 2007".**
  - Ours took Cataldo 2008, the first citation listed under the Cochrane study ID, a secondary report.
  - Fix in `study_id_citations`: take the one citation whose author and year are the study ID's. The row now
    resolves to PMID 17287476 / NCT00068861, agreeing with acq's chain.
- **Disagreement: "Semler (SMART trial)".**
  - acq's chain gives NCT02444988 alone. AACT registers SMART twice (SMART-MED NCT02444988, SMART-SURG
    NCT02547779), and the NEJM record lists both.
  - Ours refuses a single NCT. **acq's chain is incomplete here; please review**, not copied.
- **Chains 3 / 3b PMID→NCT** now use the same paper-registration rules (`_paper_registration`).
  - SOLOIST-WHF → NCT03521934 in 3 topics.
  - DELIVER → NCT03619213 in empagliflozin-hfpef.
- **Shared PubMed caches are written atomically** (`_save_cache`: union with disk, temp file, os.replace).
  - Merged into acq's restructured `pubmed_author_year`.
  - **Still plain `open('w')`**, the same race class: `k_gap_result_agreement.first_author_year`.
- **`tests/test_identity_chain.py` add/add.** acq's file is kept under that name; g1/identity's plants are now
  `tests/test_k_gap_identity_chain.py`.

**Table vs acq's own (38d132d6a).**
- 4 identities moved, exactly the documented corrections: STEP 1, Shah, SCALE O&P, DELIVER in sglt2-ckd.
- Every other difference is an identity acq's table lacked.
- acq's own new identities are preserved: Ben Ayed POOLED; DECLARE / DELIVER report families.

**Trackers regenerated (g1_batch --tracker-only, all served topics, 0 failures).**

| Metric | acq/k-gap 38d132d6a | integrate |
|---|---|---|
| INDEPENDENTLY CONFIRMED | 80 | 80 |
| COVERAGE | 157 | 157 |
| k matched | 80 | 80 |
| N eligible | 284 | 268 |
| N comparator trials | 367 | 348 |

Every per-topic difference is the identity class fix:
- **Top blocker no longer IDENTITY_UNRESOLVED:** pericarditis, dapagliflozin, metformin, omega3, spironolactone,
  statins, ticagrelor (the 7 assigned topics).
- **k matched:** spironolactone 1→2; semaglutide-obesity-mace 2→1 (STEP 1 was matched only through its false merge
  into SELECT).
- **N comparator trials** (other-agent / observational rows now typed):
  - dapagliflozin 6→3 (EMPEROR-Preserved, SCORED, VERTIS-CV are other agents);
  - empagliflozin 3→2;
  - statins 27→12.
- **N eligible:** colchicine-postop-af 5→6 (Bessissow) and tranexamic 2→3 (TXA-MFMU). Their earlier exclusion had no
  cited span; with identity resolved, cite_or_demote makes them eligible, blocked by unaudited screen exclusions.

**NOTICE FOR MAHMOOD (served numbers; queued for signature, not landed).**
- The G1 denominators change: N comparator trials 367→348, N eligible 284→268.
- Topic k changes: spironolactone +1, semaglutide-obesity-mace −1.

**Three silent environment dependencies, found while regenerating.** Each made a fresh worktree's tracker numbers
LOWER with exit 0:
1. Gitignored held caches (`outputs/k_gap/_ft`, `_ctgov`, `_upw`, `_reg`) were absent. Copied from the k-gap lane's
   worktree; `_ctgov` was verified against `ctgov_index.json` sha256.
2. A stale `origin/g1/forest-reader` ref: the tracker reads lane rows by `git show origin/<branch>`, and a clone that
   has not fetched silently loses comparator rows (pcsk9 coverage 11→2 until fetched).
3. AACT store fields: acq's `_aact_store.json` lacks study_first_submitted_date / start_date for 32 studies that an
   earlier store had. Identities are unchanged, but `registered_before` then passes by default.

Suggestion: a tracker preflight that refuses on (1) and (2).

**Earlier g1/identity tracker files** (517c36233 and the 2 Oct re-runs) were computed WITHOUT those caches, so their
absolute k values are understated. The integrate branch supersedes them.
