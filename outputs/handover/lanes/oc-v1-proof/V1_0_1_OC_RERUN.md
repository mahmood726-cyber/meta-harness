# Lane OC -> release captain: the clean OC rerun for V1.0.1

**Take `oc/v101-on-candidate` @ 887fea85.** Its single parent is `v1/candidate` 3876a62d (frozen main + P5 + D3). CI `verify` is green
(run 36262092418); the full-standard step itself succeeded.

- **Do not `git merge` OC onto 3876a62d.** It records oc's d587d9aa as a parent but carries none of OC's code or tests, so git would
  treat most of OC as already merged and silently drop it. This branch takes OC's files by path instead: 11 differ from the candidate.
  P5 and D3 touch none of OC's modified files, so nothing of theirs is overwritten.
- 3876a62d's commit message says it contains "oc's ordered-contrast repairs". Its tree does not.
- **The tests fixed** (your CERTIFICATE_MISMATCH): `test_ordered_contrast.py` no longer replays historical served files into a newer
  tree.
  - The pre-fix leg runs the old verifier binary on the CURRENT tree, differentially: a plant must move nothing in its report.
  - A control proves the check can see a defect, and a missing pre-fix blob is now a failure, not a skip.
  - The other three files needed no change.
  - The 4 files give 83 passed, with all 8 plants firing pre-fix and refused for their own code.
- **Nothing served moves against the candidate.** The 8 GLP-1 rows have identical admission and effects (7 of 8; HARMONY 30291013
  inadmissible from P5, as in the candidate). The pool is identical: 0.856 (0.809-0.906). The canonical verify PASSes.
- The same fix on frozen main alone: `oc/v101-combined` 758f65f2, CI green (run 36243726820).
