# Hostile check of lane B (the re-judgement under Decision B)

Checked 2026-09-24 against `/f/mh-b`. Nothing landed, nothing signed, no served number moved.
Every number below was produced by my own code reading the same objects the lane wrote, not from the
lane's report.

## What Decision B bought — the two claims that justify its cost

Both are now proven by execution, and the pair is what makes either meaningful:

| probe | result |
|---|---|
| positive control | presents |
| **rebuild simulated on `review.json`** | **still presents** — a rebuild no longer detaches a notice |
| `judged_commit` absent | **refuses**, no working-tree fallback |
| recorded digest corrupted for the pinned path | **refuses** |
| malformed short-sha ref | **refuses** |

The rebuild probe alone would prove nothing (a walk that ignored the file would also "still present").
It is the digest-corruption probe that discriminates: changing the *file* leaves the walk presenting,
changing the *recorded digest of that same pinned path* makes it refuse. So it is reading the pinned
blob and checking it. The audit file was restored byte-identical after the run.

## Anchoring

    judged_commit present                     41 of 41   (= 1fa77f2c4852..., verified a real commit object)
    source_digests git-pinned                 78 of 78   (0 live working-tree paths; was 27 of 51)
    before_after_line present                 41 of 41
    before/after exact against the ledger     41 of 41   (keyed on slug+outcome+before+after, not slug+outcome)
    countersignatures altered                  0 of 41

## The signing hashes — and a defect in my own first check

I first reported `rendered_sha256` present on **0 of 41**. That was a property of my check, not of the
data: I searched for a key by a name I had assumed. The hash is recorded on 41 of 41 as
`page_evidence.html_sha256` and `page_evidence.notice_block_sha256`.

I then reported the notice text absent from the page on 0 of 41. That was also my check: I searched the
**raw HTML** for a string that is plainly de-tagged prose. Against rendered text it is present 41 of 41.
Both are the same class of error the second assessment warns about, committed twice in the verification
code rather than in the thing verified.

Verified properly, by recomputation rather than by reading what the lane recorded:

    html_sha256 recomputed from the pinned git blob      41 of 41 agree, 0 mismatch, 0 blob absent
    rendered_notice_text present in the rendered page    41 of 41
    exactly one block on the pinned page carries
      the recorded notice_block_sha256                   41 of 41
    that block carries the heading built from the
      notice's own outcome and when_utc                  41 of 41

Uniqueness is not automatic: the 24 pinned pages carry 1, 2, 3, 4 and 6 notice blocks. The heading test
is what binds the digest to the notice's identity; the digest test alone would be circular.

`notice_block_sha256` is sha256 of the rendered block **HTML**, whitespace-normalised
(`result_changes.rendered_sha256`, `harness/result_changes.py:149`) — not of the de-tagged text. That is
why my text-hash comparison missed on all 41.

## The three changed verdicts, and the direction they move in

    escalated (stricter)   3
    unchanged             38
    RELAXED (weaker)       0
    no previous_verdict    0

Recomputed from `previous_verdict`, which is an independent path from the lane's own `verdict_changes`.
No notice became easier to sign.

- **N27** omega3 / Atrial fibrillation: `NEEDS_MAHMOOD_JUDGEMENT` -> `UNJUDGEABLE`. Not signable: the
  result tuple and unchanged membership verify, but the mechanism cannot be judged from the pinned bytes.
- **N28** pcsk9-mace / MACE and **N38** statins-elderly / Major vascular events:
  `gate_requires_per_notice_signature` false -> true, triggers `AWAY_FROM_NULL` + `NEW_FAVOURABLE_CI`.

I first recomputed those two triggers as False and was wrong: the before-CI is `(None, None)`, so
"excludes the null" is *unknown*, not False. The lane's predicate (`scripts/rejudge_notices.py:93`) is
`favourable(after) and not favourable(before)`, and an outcome that previously had no interval and now
asserts one excluding the null is exactly a new favourable claim. Its `AWAY_FROM_NULL` is the
any-strengthening-signal bucket, not "the point moved away from the null" — in both cases the point moves
*toward* it. The name is misleading; the behaviour escalates, which is the safe direction.

## Parked, recorded, not worked (per the scope rule)

`scripts/rejudge_notices.py:175` sets the benefit direction as
`higher = name.lower().startswith('ovulation')` — a hardcoded single-outcome heuristic. If an outcome
where higher is better is ever added, `favourable()` inverts and a strengthening reads as a weakening,
which **suppresses an escalation** — a failure in the unsafe direction.

Checked on this corpus: of the 41 outcomes, exactly one is higher-is-better (N24, ovulation) and it is
the one the heuristic names. N34 "Adverse events leading to permanent dis**continuation**" was flagged
only by my own keyword filter and is correctly a harm. So `higher` is right on 41 of 41 today. The defect
is latent, not active, and is queued rather than worked.
