# Blind re-extraction -- result (pre-registered in `PREREG_blind_reextraction.md`, commit e1e72c2f)

**Primary (per arm, same arm_id, same (events, total)):** of the 70 arms of the 35 rows,
- **64 of 64** arms of the 32 BOUND rows agree exactly between the first pass (shown the served slots) and the blind
  pass (served slots, served source text and served spans removed);
- 4 arms: neither pass finds a printed number (metformin-pcos-ovulation 0-0 both arms; 0-1 events, both arms);
- 2 arms: the first pass set them aside (dapagliflozin-hfpef-hosp harm: no printed per-arm denominator), and the
  blind pass reports the same events with the same missing denominator.

**Secondary:** rows where the first pass is BOUND and the blind pass does not pass G1-G3/G5/G7: **0 of 32**. Rows the
first pass set aside that the blind pass binds: **0 of 3**.

**Classification of disagreements (pre-registered classes):** FIRST_PASS_ANCHORED 0, BLIND_PASS_WRONG_OUTCOME 0,
BOTH_DEFENSIBLE 0. No row changes state; nothing is queued.

## One correction made BECAUSE of this comparison, disclosed
The first run of the comparison reported 66 of 70 arms, with CD-probiotics-aad-prevention-2-0 disagreeing. Reading it:
both passes reported 4/181 and 6/178, but one pass labelled the arm "LcS group" and the other "LcS", and my
source-label arm ids kept the word "group" -- one arm, two ids. The defect was in the gate's id derivation, not in
either extraction; `source_label_id()` now drops group/arm (as the F4 schema's `arm_id` does) and every record was
regenerated (states unchanged, 32 / 3). The comparison was also corrected to count "neither pass finds a printed
number" separately instead of as agreement. Both corrections are instrument fixes; neither changes what counts as an
agreeing NUMBER.

## Limits
- Same model and settings as the first pass: this measures anchoring on the served numbers, not independence of model
  family.
- Agreement shows the bound numbers do not depend on showing the extractor the answer; it does not make them correct.
  Correctness rests on the gate (spans re-found in pinned bytes, G7 ownership) and on the eye review of every bound span.

Artefacts: `extractions_blind/<row>/{row.json,out.json}`, `CALL_LOG.blind.jsonl` (35 calls, 35 artefacts, 0 paths
outside a job dir; 4.86M input tokens, 36.8k output), `BLIND_COMPARISON.json`.
