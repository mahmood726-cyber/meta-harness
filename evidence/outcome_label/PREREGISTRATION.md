# Harms and secondary outcomes not preregistered are EXPLORATORY (dapagliflozin HFmrEF/HFpEF review; branch only)

dapagliflozin-hfpef-hosp's protocol says "**Harms** - none preregistered for this topic", yet an "Adverse events" pool (k=1, RR
1.1579) was served with no label.

`outcome_tiers.preregistration()`:
- **PREREGISTERED** if the protocol names the outcome. All three styles the protocols use are read: `- **O (harms)** - ...`,
  `- **Harm outcomes** - ...` (ticagrelor), and a `Harm outcomes:` heading with bullets (denosumab). A general harms clause also
  counts ("any further harm outcome ...", GLP-1).
- **AMENDED** (with its date) if a dated amendment section names the outcome or its kind.
- Otherwise **NOT_PREREGISTERED**. The outcome is served as EXPLORATORY, titled "Exploratory (not preregistered): <name>", and the
  page's Tier row says why.
- No protocol text means nothing is shown preregistered except the primary. British and American spellings are equated.

**Measured at 3876a62d: 19 of 65** served non-primary outcomes are not preregistered; 11 of them serve a pooled number.
- dapagliflozin: adverse events.
- doac: 5 bleeding / adverse-event harms.
- dpp4: 4 harms.
- esketamine, melatonin: adverse events.
- semaglutide-weight: gastrointestinal adverse events.
- sglt2-primary-prevention: 4 harms.
- colchicine-recurrent-pericarditis: 2 efficacy secondaries.

A first pass said 25 of 65. It read only `**O (...)**` lines and missed the ticagrelor and denosumab styles, which preregister their
harms; this was corrected before reporting.

**Not verified end to end.** A real build_topic of dapagliflozin failed on a held document outside the sparse tree, and both drives
then sat below the 3 GB regeneration floor (C: 2.5 GB, F: 2.9 GB), so no further build was run. The rule, the pipeline wiring and the
page line are tested against every served protocol and outcome at unit level (`tests/test_preregistration.py`).

**Notices if landed:** 19 outcomes are re-titled EXPLORATORY (no number moves). A topic owner can instead record a dated amendment
that names the outcome.
