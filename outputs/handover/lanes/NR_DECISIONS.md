# Lane NR: decision B on the 41 result-change notices, engineering decisions

Lane NR, branch `nr/notice-anchors`, cut from `origin/enforcement-gate` at `1fa77f2c`. The lane never signs a
notice. These are served-number changes, so the delegated bulk acceptance of 2026-09-24 does not cover them. That
acceptance covers AI screening proposals only.

## The decision being implemented
Decision B was taken by Dispatch under Mahmood's delegation on 2026-09-24. Before this lane it was recorded
nowhere in the repository; this file is its record.
1. Every notice anchor records the exact version it judged (`git:<commit>:<path>`). The `sign_walk` and
   `--expect-digest` guards stay strict. A refusal on a detached anchor stays a refusal, and nothing is re-pointed
   without re-judgement.
2. All 41 notices are re-judged once against the current served pages. Codex does the bulk comparison and the lane
   checks each notice hostilely. The before, after and departing lists are revalidated against the ledger and the
   pages.
3. Each notice gets a one-line before → after, its hash and how_it_reached_the_reviewer, queued for Mahmood's
   signature.

## Engineering decisions (the lane's, recorded)
- **E1. Branch, not main.** The 41 notices, `sign_walk.py` and `registry/notice_adjudication.json` exist only on
  `enforcement-gate`, which is held and RED by design. Main's ledger has 13 notices, all signed. Landing on main
  would drag the whole gate in. Work lands on `nr/notice-anchors`, a child of `enforcement-gate`, so the main lane
  can merge it or cherry-pick it. The lane does not push to `enforcement-gate` or `main`.
- **E2. No `harness/` edit.** Every `harness/*.py` blob is in the certificates' `analysis_code` closure (checked in
  `docs/reviews/*/CERTIFICATE.json`). Editing one re-certifies all 32 pages, which would itself detach every
  anchor. The anchor logic therefore lives in `scripts/notice_anchor.py`, and the re-judgement in
  `scripts/notice_rejudge.py`.
- **E3. What "served" means.** Readers are served `origin/main`. On main, none of the 41 transitions has happened:
  main shows the `before`. A judgement therefore pins two versions:
  - `served`: main at `c9d665e0`. Verified pinned; never compared with the working tree.
  - `proposed`: the gate page that carries the notice, `1fa77f2c`. Verified pinned and compared live.
  The renderer sources (`harness/result_changes.py`, `page.py`, `harms.py`) are pinned live as `code`. The N37
  conflict's cache record is pinned live as `held`. The ledger is pinned but not live-compared (`record`), because
  a countersignature is itself a ledger write. The ledger fields are still required equal field by field.
- **E4. Live comparison uses git blob ids** (`git hash-object --path`), not raw bytes. `harness/gitblob.py`
  documents that CRLF checkouts break raw-byte identity.
- **E5. Append-only.** A judgement is appended, never edited (`notice_anchor.append_only_problem`). The pre-B
  working-tree digests are kept under `superseded_anchors`. `source_digests` must equal exactly the anchors of the
  current judgements, or the walker refuses.
- **E6. A verdict is bound to bytes.** `notice_rejudge.py append` refuses unless each verdict names exactly the
  anchor digests the command recomputes. This parallels `sign --expect-digest`.
- **E7. `sign` defence in depth.** For an audited notice, `sign` requires `--expect-digest` and `--judgement`,
  verifies every anchor, refuses if the notice is DETACHED, and records `judgement_id` in the signature.
- **E8. HOLDS_WITH_DEFECT.** A notice can record the transition correctly while its rendered words are wrong. Such
  a judgement attaches, and the walker prints the defect above the signing command. It is never a recommendation
  to sign. DIFFERS refuses.
- **E9. The audit's `page_evidence.notice_block_sha256` is not used.** No committed version reproduces it: 0 of
  41, across eleven candidate derivations at four commits. Nothing in the repository reads it. The judgement
  records the digest `sign --expect-digest` checks instead (`result_changes.rendered_sha256` of the canonical
  block), plus proof that the page carries that exact block.
- **E10. Rebuilds no longer detach; substance still refuses.** An anchor is DETACHED only when its pinned bytes
  cannot be verified: the commit is absent from the clone, the path is absent, or the blob or sha256 differs from
  what was recorded. That is a refusal, and it stays one. Separately, `notice_anchor.guard` refuses a notice as
  STALE when the tree presenting it no longer serves what was judged:
  - a different result tuple, or a different pooled membership, for the outcome;
  - a different signing digest;
  - an `index.html` that no longer carries the exact rendered block.
  Byte churn elsewhere on a rebuilt page is disclosed on the walk ("Rebuilt since judgement") and is not a
  refusal on its own. Merging main into `enforcement-gate` (main's page-verifier block, four re-certifications)
  therefore does not detach the 41. A merge that moved a served number would make the notice STALE.
- **E11. A correction to this lane's own first design.** My first implementation compared every live anchor with
  the working tree byte for byte. That made every rebuild detach every notice again, which is the breakage B was
  ordered to remove. It was replaced before landing, after the F4 lane's handover (dropped into this lane's local working directory at 08:20, read as data) stated the intent plainly: a rebuild no longer detaches. Its evidence is in
  `nr-2026-09-25/observe_first.txt`. The pre-B walker was observed first. A churn-only rebuild REFUSED it. The old
  recovery, refreshing the digest, then let a notice whose served number had moved (0.85 → 0.84) present with a
  signing command. The B walker presents the first with a disclosure and refuses the second as STALE.
- **E12. Relation to the F4 lane's unpushed patch** (`B.patch`, sha256 1dc05db7…, held locally by F4). Both lanes
  pinned the same page commit, `1fa77f2c`. The F4 registry's 41 recomputed signing digests equal this lane's 41
  exactly. Both lanes independently escalated N27, N28 and N38. This lane also:
  - pins the served page (main `c9d665e0`) and proves 41 of 41 `before` tuples are what main serves today;
  - records the codex bulk reader;
  - records judgements append-only;
  - binds each verdict to its digests;
  - found five rendered-wording defects F4 did not report (N30, N32, N39, N06, N17).
  The F4 patch is not landed, so the branch carries one implementation, not two.

- **E13. Judgement B2: why each trial actually left.** Every notice's "why" says a trial's family eligibility is
  "not established by the held record". I tested that sentence against the held rows for all 78 departing
  memberships. Only 18 of 78 are rows that genuinely do not establish the population or contrast, plus 1
  INELIGIBLE.
  - **34 are the check misreading rows the site holds:**
    - 16 ACTIVE_COMPARATOR: `randomised_contrasts` only records a contrast when two arms differ by the agent
      alone, so drug-vs-active-drug trials can never pass. That covers all 4 NOAC-vs-warfarin trials, PLATO,
      PARADIGM-HF and the DOAC-vs-VKA trials.
    - 10 TERM_FORM_MISMATCH: 'Diabetes Mellitus, Type 2' against 'type 2 diabetes', and
      'Depressive Disorder, Treatment-Resistant' against 'treatment-resistant depression'.
    - 2 WILDCARD_NOT_HONOURED: `antibiotic-associated diarr*` is tested as a literal substring.
    - 4 CONTROL_CODED_AS_ACTIVE.
    - 2 LEXICON_GAP.
  - **25 are sources the check cannot read:** 20 have no registry parent linked, and 5 are anchored to a
    registry other than ClinicalTrials.gov, while the check reads AACT rows only.
  - **How the labels were checked:**
    - The labels were recorded before a blind second read (`b2-binding/lane_classes.json`, sha256 346c8d4b…).
    - A Claude subagent agreed on 70 of 78 labels and 75 of 78 buckets. It is the same model family as the lane:
      codex NR-C02 on the same packet hit its usage limit.
    - Seven cases were executed on `harness.trial_family.screen_family` with only the blamed field changed: DELIVER,
      CARMELINA, TRANSFORM, a probiotics trial, ROCKET AF, PLATO and PARADIGM-HF. All 7 became ELIGIBLE. The control,
      which re-derives contrasts and changes nothing, stayed NOT_PROVEN (`b2-binding/screen_plants.txt`).
  - **What this means for signing.** For 12 notices every departure is a misread by both readers: N08, N09, N15,
    N17, N18, N19, N20, N21, N25, N32, N39 and N40. For N23 it is a misread by the lane's label only. N20 is the
    case that matters most: its newly significant benefit exists only because a word-order mismatch removed two
    trials.
  - Each notice records accurately what the gate did. The lane's recommendation, which is not a decision, is to
    fix the check (a `harness/` change, re-certification and new notices) before countersigning these.
  - B2 re-pins the same bytes as B1. It is appended and B1 is unchanged; the walker prints each trial's binding
    constraint above the command.

## Measured facts (2026-09-25)
- Anchors: all 78 intact at `1fa77f2c`. Against served main `c9d665e0`: 53 broken (26 review.json, 24 index.html,
  3 harness sources) and 25 intact (24 `git:38c04411:` plus one cache record). The brief said 51 / 27, measured at
  an earlier main.
- Main changed no admission input since `38c04411`: no diff under `cache/`, `topics/` or `protocols/`, and the
  `harness/` diff is `extract.py` (R1+R4, documented as byte-identical extraction), `extract_values.py`,
  `whole_numbers.py`, `page.py` (the page-verifier block) and `result_changes.py` (DELEGATED_IS_NOT_A_SIGNATURE).
  So the gate's `after` values are not expected to move when it is rebased. Not proven: rebuilding needs a 1.9 GB
  checkout on a disk with 2.4 GB free.
