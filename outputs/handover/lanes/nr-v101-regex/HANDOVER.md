# Lane NR, V1.0.1 regex fixes (colchicine-postop-af external review)

Branch `nr/v101-regex`, based on `v1/candidate` 3876a62d. Code commit 222d7647. Done in Claude directly; codex was
allowed but not used: two small, tightly coupled fixes whose correctness turned on reading each radius row by hand.

## (1) False refusal COUNTS_PRESENT_NOT_CORROBORATED: COCS (PMID 36286314)
- **Root cause.** It was not rounding, the "%" format, locale, or a table vs text source. The count sentence
  `POAF was observed in 21 (18.6%) patients of the colchicine group vs. 39 (30.7%) control patients` gives no
  denominators. The per-arm sizes are in another sentence, `The final analysis included 240 study subjects: 113 in the
  colchicine group and 127 in the placebo group`. `extract._arm_ns` has no pattern for `N in the <arm> group`: every
  pattern needs a noun such as "patients" or an allocation verb. So no denominator existed, and nothing could be
  corroborated. The percentages were always right: 21/113 = 18.58% and 39/127 = 30.71%.
- **Fix.** `_arm_ns_in_the_group` reads `N in the <arm> group|arm` only under all of these conditions:
  - both arms are named in ONE sentence;
  - that sentence declares a population (`_POP_SENT`: included / analysed / analysis / randomised / enrolled /
    allocated / assigned);
  - that sentence does not report events (`_EVENT_SENT`);
  - no other pattern already found either arm.

  The existing check, a count must corroborate its own arm's stated % within 1.0 point, is unchanged. A wrong % or
  swapped sizes still refuse (plants).
- **Admissibility is not decided by the extractor.** 267 were randomised and 240 analysed, with 19 vs 8
  post-randomisation exclusions; that is for risk of bias. The admission contract already reads COCS as MODIFIED_ITT,
  flags `COMPAT_MISMATCH` against the ITT contract, and discloses it on the page.

## (2) Wrong field link: Farzaneh (PMID 42132185)
- **Root cause: three readers bound the regimen sentence as the follow-up window.** The sentence is `... maintenance
  dose (0.5 mg daily if <70 kg; 1 mg daily if >=70 kg) for 14 days`, and the three readers are:
  - `compat_check._derive_follow_up`: a bare `\b14\s+days\b` rule, with the same blind spot for 21/56 days, "for 40
    months" and "median duration of supplementation";
  - `eligibility_chain._follow_up_value`: a hand row citing `maintenance dose ... for 14 days`, plus a bare-substring
    fallback. The same fallback's literal "1 month" also matched inside "11 months";
  - `eligibility_chain._endpoint_definition`: a hand row, `14-day regimen`.
- **Fix: `harness/window_evidence.py`.** `duration_role()` reads a duration's own clause and returns ASCERTAINMENT,
  DOSING or UNSTATED:
  - the words after it decide first: "of follow-up" or "after surgery" → ASCERTAINMENT; "of treatment" or "regimen"
    → DOSING;
  - then the word right before it: "at", "within", "until" → ASCERTAINMENT;
  - then the rest of the clause, where an ascertainment cue beats a dosing cue;
  - "followed by" is sequencing, not follow-up.

  Every follow-up reader now refuses a DOSING duration, hand rows included. When the only window-like statement is a
  regimen, the window is **UNRESOLVED**: compat returns `underivable`, and admission returns `not_stated` →
  `UNKNOWN` / `COMPAT_UNKNOWN`. The review's declared timepoint no longer stands in for the trial's own statement.
  Farzaneh states no ascertainment window anywhere (abstract or full text), so it is now unresolved.

## Plants
- `tests/test_nr_v101_regex.py`. **10 of 14 fired on the unmodified candidate** (`PLANTS_PRE_FIX.txt`). The other 4
  pass before and after the fix; they are the guards against false corroboration: a wrong %, swapped arm sizes, an
  event sentence posing as sizes, and a genuine "14 days of follow-up".
- A 15th plant pins a defect I found while reading the radius. A match that begins a sentence ("...failure).
  In-hospital mortality...") was inheriting the previous sentence's "treatment".
- Inventory: `_POP_SENT` and `_EVENT_SENT` have specs with accept and refuse plants in `regex_layer/specs.py`.

## Corpus-wide radius
Produced by `scripts/nr_v101_radius.py`. BEFORE is candidate 3876a62d; AFTER is this branch. Both dumps are included.
| reader | changes |
|---|---|
| `extract_trial`, every cached record × declared outcome | **1 of 10,520**. Refusals 10,022 → 10,021: COCS POAF goes from refused to 21/113 vs 39/127. Nothing goes from a value to a refusal. |
| `_arm_ns` | 4 of 3,330. Only COCS changes an extraction. |
| compat follow-up window (pooled + declared-absent rows) | **14 of 797 rows**, 5 trials: Farzaneh; probiotics 40548185 ("LA85 or placebo for 14 days"); omega-3 20929341 ("to receive for 40 months"); 21115589 ("median duration of supplementation 4.7 years"). Melatonin 27559258 stays at 14 days, now bound to "After 1, 7, 14 days, the patients were reviewed" instead of the dosing sentence. |
| admission follow-up window | **28 of 797 rows**, 9 trials. 6 are dosing durations now `not_stated`: 42132185 (its hand row), 23992557, 32862667, 11473953, 20146881, 40548185. In 3 only the cited span changes, values unchanged: 27559258, 19552097, 10545590. |
| admission surveillance window | 3 of 797 rows: 42132185 "14-day regimen" → not_stated. |

I read every changed row against its source (`RADIUS.json` lists each with its span). None goes from a genuine
ascertainment window to unresolved.

## Served changes: rebuilt with `scripts/build_topic_recorded.py <slug> --now 2026-09-11`
- **Control.** colchicine-postop-af was rebuilt from the candidate's own harness and reproduced the committed
  review.json with 0 differing fields. The rebuild method is sound.
- **One served NUMBER changes, and it needs a notice.** colchicine-postop-af / Postoperative atrial fibrillation:
  RR 0.6509 (0.2063 to 2.0538), k=3 → **RR 0.6459 (0.3595 to 1.1605), k=4**, as COCS enters; tau² 0.147 → 0.075.
  Direction is unchanged and the interval still spans 1.
- **omega3-cardiovascular-events: no pooled result moves.** The MACE follow-up compatibility finding changes from
  `COMPAT_ASSERTED_NOT_UNDERLYING` to `COMPAT_DIMENSION_UNDERIVABLE`: 20929341 and 21115589 now have an unresolved
  window. This is page wording, not a number.
- **Declared-absent rows only, 5 more topics.** colchicine-recurrent-pericarditis, colchicine-secondary-cv-prevention,
  melatonin-primary-insomnia-sol, metformin-pcos-ovulation and probiotics-aad-prevention change their follow-up cells.
  No number can move there, because the extraction radius is 1, in cpaf.

## For the release captain at V1.0.1 integration
1. Because harness blobs changed, **every** topic's certificate goes stale. Regenerate all 32, as for V1.0.
2. **HAZARD: `refresh_result_change_notices.py <base>` drops every notice whose outcome no longer differs from
   `<base>`.** Run on a copy with base 3876a62d, it reported DROPPED for all 13 signed notices. Do not point it at the
   candidate. Either append `NOTICE_TO_APPEND.json` to `docs/result_changes.json`, or run the refresher with the base
   the existing notices were built against.
3. `NOTICE_TO_APPEND.json` was built by the repo's own refresher from my rebuilt page, and its reason is rewritten by
   hand and `reason_locked`. The refresher's generated reason was its canned "hand-row binder" mechanism sentence,
   which is false for this change. The notice is OPEN; Mahmood countersigns after the page renders it.
4. Expected integration check: the re-derivation (`scripts/rederive_notices.py --prev <served> --cand <V1.0.1>`) shows
   this ONE served-number change, noticed, plus whatever other lanes bring.

## Found, not fixed (outside this change; for RoB or a later lane)
- `study_effect.analysis_population` defaults to "intention-to-treat" for count-reconstructed rows. The compat
  analysis_set then says ITT for COCS (240/267 analysed), while the admission contract correctly says MODIFIED_ITT.
- `compat_check._derive_follow_up` still falls back to `outcome.timepoint` (the review's promise) as a TRIAL's value
  whenever no rule matches. It now stops only when a dosing duration was refused. It is the same kind of wrong field
  link, but its radius is large, so it needs its own measured change.
- The COCS effect sentence writes "95% Cl" (lower-case L). `_EFFECT` needs "CI", so the round-trip against the paper's
  OR 0.515 is not run. The counts reproduce OR 0.515 exactly.
- `eligibility_chain._follow_up_value` matches bare substrings, so "3 months" also matches "13 months", as "1 month"
  matched "11 months". This is pre-existing and was only partly masked here.
