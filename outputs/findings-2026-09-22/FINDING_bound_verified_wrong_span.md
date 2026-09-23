# Finding: bindings that are LOCATED, verified, and point at the wrong span (found by lane F2, 2026-09-22)

Two per-trial values on served primary rows are bound to a span that exists in the held bytes, is located byte-exactly, and
does not answer the question the dimension asks. Every verification discipline in the harness (P2 span located, P3 tokens
in span, the LOCATED anchor status, the ratchet, the certificate) checks that a span EXISTS and CONTAINS the value. None
checks that the span is ABOUT the thing the value is claimed for. These two passed every check.

## The two instances (from `f2_measurement.json`, lane F2)
- **F2-V007 -- corticosteroids-cap-mortality, primary "All-cause mortality", dimension follow_up_window, trial PMID 36942789
  (CAPE COD, NCT02517489).** Bound value "14 days" from the abstract span (records.json#/records/7/abstract, normalized
  chars 423-649): "daily for either 4 or 7 days as determined by clinical improvement, followed by tapering for a total of 8
  or 14 days) or to receive placebo..." -- that is the hydrocortisone TAPER DURATION. The mortality follow-up in that trial
  is 28 days (and 90 days), neither of which is the bound value. Lineage INDEPENDENT_NOT_YET_VALIDATED, anchor LOCATED.
  The other trial on the row (25688779) has its window INHERITED from the config ("30-day or in-hospital"), so the row's
  compatibility check compared a taper duration with a config assertion and reported a discrepancy for the wrong reason.
- **F2-V019 -- melatonin-primary-insomnia-sol, primary "Sleep-onset latency", dimension analysis_set, trial PMID 20712869
  (NCT00397189).** Bound value "completers efficacy set" from the span (records.json#/records/84/abstract, chars 878-1107):
  "...PRM patients continued whereas placebo completers were re-randomized 1:1 to PRM or placebo for 26 weeks..." -- the
  word "completers" belongs to the EXTENSION-phase re-randomisation sentence, not to the 3-week age-subgroup effect the row
  pools. Same class as the phase-record failure (EMPHASIS-HF, STEP 4): a span from a later phase read as evidence about the
  randomized phase. Lane F2's own source-binding review says so verbatim.
- A third, weaker: F2-V002 (colchicine-recurrent-pericarditis) conflates an ITT analysis-set assertion with disease-stage
  wording and carries an inherited value beside it.

## What these bindings feed
The per-trial values are the `compat_check` "underlying" derivations (harness/compat_check.py, per-trial follow-up and
analysis-set extraction from abstract text) used to test the outcome-level compatibility assertion. They do NOT feed the
pooled estimate; the pooled number on both rows is unchanged by them. They feed the served compatibility label and the
pre-fix violation record -- so the served provenance is wrong, not the served number. That is the mild version of the
class. The severe version -- an EFFECT bound to a located span that reports a different endpoint, arm or phase -- is the
same failure and would pass the same checks; the M2 counterexample work (2026-09-20) was the only place it has been
looked for, and it looked at the effect-token match, not at what the surrounding sentence is about.

## How would we detect a third one?
**We would not. These two were found by a lane reading 35 spans for a different purpose (F2's severity classification),
not by any instrument.** No check in the harness fails when a located span is about the wrong thing. The gate, the
certificate, the ratchet and the bundle predicates all pass a wrong-span binding, because they were all designed against
the failure mode "no binding / unbound legacy / value not in span", and this is the complementary one: bound, located,
wrong.

The closest instrument is the bundle's `P9_span_target_mention` (the span must mention the target the value is claimed
for), which is bundle-only and not evaluated in-build, and is defined for effect spans, not for compatibility dimensions.
A P9-shaped check per dimension would have caught F2-V007 (the span contains no mortality / follow-up / death token) and
would NOT have caught F2-V019 without a phase-scope rule (the span mentions the outcome's trial and "placebo"; what is
wrong is which phase the sentence describes). So the detector for this class has two parts: (1) target-mention per
dimension, in-build; (2) phase-scope -- a span drawn from a sentence describing an extension / re-randomisation /
follow-on phase is not evidence about the randomized phase. Part (2) is the same rule lane PH is designing for registry
records; it applies to publication text too.

## Prevalence -- unknown, and the honest denominator is not 35
F2 read 35 compatibility records and found 2 (+1 weak). The compat producer derived per-trial values for every pooled row
on every keyed outcome (87 slots on 29 keys); the 52 slots with no pre-fix violation were not read, and a wrong-span
binding that happens to AGREE with the assertion produces no violation and was therefore never looked at. The effect
bindings (verified_effects, 46 pooled rows) have never been read for this class at all. A lane that reads every located
span on the corpus and answers "is this sentence about the dimension/endpoint/phase the value is claimed for" is the
only way to get a denominator; until then the count is "2 found, 0 searched for".

## Not decided here
Whether to make target-mention and phase-scope in-build predicates (a landing, with pre-fix plants: V007 and V019 are the
plants, already observed passing). Mahmood's.

## Prevalence measured (lane WS, 2026-09-22; both controls fired on every method version; ws.json 200 MB)
- Confirmed wrong-target provenance under served numbers: **12 of 46 served trial-outcome rows on 7 of 32 pages** (10 of 44
  excluding the two controls). Lower bound. 29 definite non-right contexts: WRONG_ENDPOINT_OR_ARM 17, WRONG_PHASE 9,
  WRONG_DIMENSION 3.
- **Severe case, verified from served bytes by the orchestrator:** spironolactone-hfref-mortality serves All-cause mortality
  HR 0.85 (0.53-1.36), k=1, J-EMPHASIS-HF PMID 28824029; the held abstract assigns that HR to the primary COMPOSITE (CV death
  or HF hospitalisation) and reports deaths 17/111 vs 10/110. Row: provenance "abstract", kind/verification/span None,
  admission MIGRATION_STATE_UNBOUND_LEGACY. Same class as wrong-target-composite 2026-09-19 (DELIVER, EMPEROR-Preserved);
  third page; flattering direction; live on main 38c04411.
- Denominator: only 23 of 46 served rows have a literally located effect/harm source; on the other 23 the class is
  UNASSESSABLE, not absent. Assessable contexts by kind in WS_REPORT.md.
- Answer to "rare or detector-limited": the method is semantic (referent vs consuming row), found 27 beyond the controls,
  and cannot see half the served rows because they cite no located span. Not rare; half unexamined by construction.
