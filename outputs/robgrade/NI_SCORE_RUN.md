# How NI_SCORE.md was produced (run record, 12 Oct 2026)

1. Pre-registration: commit c2a27057db2222fdd1f56f0674a784c35ca4fa71 (hook: all 15 limbs PASS), pushed to
   origin/robgrade/d11-v3 before any TEST computation. It is the commit that first adds NI_POLICY.md (from git history).
2. Replay of the 50 TEST trials under engine v3.1:
   `python scripts/rob2_dual.py --calibration <the 4 comparators>` with ROBGRADE_LOCAL_FT=1. There were 208 model-call
   records before and 208 after, so no model call was made; the answers are the recorded ones. Then
   `python scripts/rob2_calibrate.py <the 4 comparators>`.
3. First scoring run: `python scripts/rob2_ni_score.py c2a27057d...` REFUSED with "balanced-crystalloids... 34375394 D3:
   answers differ from the pre-registration".
   - Cause, traced: the scorer's `_git()` decodes `git show` output in the Windows locale (cp1252), not UTF-8. The
     narrow no-break space (U+202F) in "11 052" was read as "â€¯" on the frozen side only.
   - The answers are identical. An independent comparison decoding both sides as UTF-8 found 0 differing answers in
     all 59 trials of the 4 topics.
   - The guard failed closed, as designed. Its plants mocked `frozen_object`, so none of them ran a real `git show`
     on non-ASCII text: a test gap.
4. Scored run: the SAME scorer, byte-identical to the pre-registration (`git diff --quiet c2a27057d -- scripts/
   rob2_ni_score.py`), run under Python's UTF-8 mode: `PYTHONUTF8=1 python scripts/rob2_ni_score.py c2a27057d...`.
   This changes how the runtime decodes text, not any comparison or scoring logic.
5. Not done: the scorer is not edited. It is a frozen policy file, so editing it would make the pre-registered scorer
   refuse forever. The fix (`encoding="utf-8"` in `_git`, plus a plant that runs a real `git show` on a non-ASCII
   object) is proposed as a declared AMENDMENT for Mahmood. It is not applied silently.

Also refused, correctly: `scripts/rob2_calibration_nofn.py` now refuses, because robgrade/rob2_formal.py changed after
the v3 freeze. CALIBRATION_NOFN.md therefore stays the v3 result as committed. The v3.1 numbers are in NI_SCORE.md.
CALIBRATION.md and calibration.json are regenerated with v3.1 and the corrected kappa statistics (defined whenever
pe < 1; non-null-variance CI).

6. Amendment A1 APPLIED (signed: Mahmood via Dispatch, 12 Oct, SIGNING_PACKET_NI.md item 4; outputs/robgrade/
   AMENDMENTS.json):
   - scripts/rob2_ni_score.py decodes git output as UTF-8;
   - it accepts a frozen file that differs from the pre-registration only through a signed declaration naming the
     file's git blob before (91ada050) and after (74b20011).
   Proof: the amended scorer, run WITHOUT UTF-8 mode, reproduces NI_SCORE.md and ni_score.json byte for byte.
   tests/test_rob2_ni_score_amendment.py (real git, no mocks) fails 5/5 on the pre-registered scorer and passes 5/5
   on the amended one.
