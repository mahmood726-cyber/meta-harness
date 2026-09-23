# Standing hazard: an exhaustive claim over a representation that does not carry the data always succeeds

FIVE instances on 2026-09-22, in one session, by three different actors (the orchestrator three times -- the fifth inside a
report that quoted this very file -- a lane once, a landed gate once). Every one was a sentence of the form "0 of N", "all held documents", "no families", "none found" -- an exhaustive
negative -- produced by a search over a VIEW of the corpus that did not contain the thing being searched for. The search
ran to completion, returned nothing, and the nothing was read as a fact about the corpus. In every case the claim was in the
comfortable direction.

## The instances

1. **The 43-id lookup (orchestrator, `andor_audit.py`).** 135 included screening records on the topics carrying the
   blinding rule; my index of `records.json` was keyed by `pmid`/`id`, so 43 ids held under the `ctgov` key or as
   display-labelled ids resolved to nothing. I reported "92 with a held record; 43 have no entry in records.json -- not
   examined" and computed 26 of 92. Lane DB: 0 of 43 lack a held row; the cohort is 135; the placebo branch is 30 of 135.
   The exhaustive claim: "43 have no row". The view: one key.
2. **The empty-fields phase pass (orchestrator, phase detector v1).** I read `family_registry.rows.json.gz` for eligibility
   criteria and ran a prior-phase phrase detector over 39 pooled families: 0 of 39 fired. The `eligibilities` rows in that
   file carry only the NCT id; the criteria text lives in the payload. The exhaustive claim: "0 of 39 phase signals". The
   view: a projection with the field empty. Caught only because EMPHASIS-HF ran as a positive control and did NOT fire.
3. **The certified-families empty map (landed gate, `gate.py:1354`, found by lanes E and E2b).** `check_admission_enforced`
   compares the page's families with the certified `cache/<slug>/families.json`; the guard is `if fam is not None and
   certified:`. A certified file holding `{"families": []}` -- which the real offline writer emits for empty records with a
   held registry -- loads as `{}` and the comparison is skipped. GATE PASS on a page the non-empty control refuses. The
   exhaustive claim: "no certified family disagrees with the page". The view: an empty map, indistinguishable from "no
   file" by truthiness.
4. **DB's held-document search (lane DB).** DB read "every held document" for 26 placebo-word admissions and reported 5
   with no masking evidence in any held document. U5 found, for melatonin 18036082, that `cache/melatonin-primary-insomnia-
   sol/ft_22346363.txt` -- a held full text of the authors' pooled analysis, not the trial's own record -- states "3-week
   randomized, double-blind treatment period" and cites 18036082 as reference 25. The exhaustive claim: "no held document
   proves it". The view: documents filed under the trial's own id.

Two near-misses of the same shape, same day, caught before relay: my `_double_blind` refusing-direction check read abstracts
only and returned "0 of 15 false refusals" (DB, reading the parent trial's registry row, found 2 of 15); and my "0 of 15
false refusals" itself was built on the 15 that carried the X-DESIGN id -- had the rule id been split differently the
denominator would have been wrong too.

## Why it is one hazard and not four bugs
- The search terminates normally. There is no error, no empty-input warning, no NaN. The output is a well-formed number.
- The number is zero or "all", which is the number a clean corpus would also produce. Nothing in the result distinguishes
  "searched and found none" from "searched nothing".
- The claim is exhaustive, so it closes the question. Nobody re-opens a "0 of N".
- It is biased in the flattering direction by construction: an absence check can only fail to find.
- It survives review: the reviewer sees the same zero and, absent a control, has no way to tell the two cases apart.

## The cure, operationally
**An exhaustive claim over a corpus needs a positive control that would have fired, or it is not an exhaustive claim.**
Before any sentence of the form "0 of N", "none of the held documents", "no X disagrees", "all N are Y":
1. Name ONE item that is known to be a positive (a planted one is fine; a real known instance is better) and show the
   same search finds it, in the same run, through the same code path and the same representation.
2. If no positive exists to plant, the claim is downgraded in the text to "not observed in <representation>" with the
   representation named -- never "clean", never "none".
3. Record the control's firing beside the number. A zero without its control is a reach figure.
4. For a gate: the empty-container case is a control too. A check that can be switched off by an empty input must be
   tested with that empty input and must REFUSE or state NOT_EVALUATED, never pass. (`if certified:` is wrong; `if
   certified_loaded:` plus "0 families certified -> refuse" is right.)
5. For a lookup: assert the join. `assert len(found) + len(not_found) == N` catches nothing; `assert not_found == []` or an
   explicit listing of the not-found ids by name, in the report, is what let DB find my 43.

Instance 2 is the template: the control was run, it did not fire, and that single fact converted "clean" into "unread"
before anything was relayed. Instances 1, 3 and 4 had no control and each shipped a wrong figure -- two of them to
Mahmood, retracted the same day.

## Trigger, syntactic
You are about to type "0 of", "none", "no ", "all N", "every held", or "exhaustive". Stop; name the positive control; if
you cannot, change the verb to "not observed in" and name the view.

## Fifth instance (2026-09-22, by the author of this file, inside a report that quoted this file)
Auditing the error library's ME-09 entry I ran `grep -rn "ME-09" tests/ scripts/ harness/ | grep -v error_library`,
got nothing, and wrote that ME-09 "appears nowhere outside the library" and that its named `test_arm_identity.py`
"does not exist in tests/". Both false. `git grep -n ME-09` returns the references at once -- they live in
`docs/error_coverage.json`, a path my three-directory grep never searched -- and `tests/test_arm_identity.py` exists,
98 lines, 5 tests, all passing. The claim was relayed onward as a finding and retracted the same hour. The subsequent
audit of all 33 entries (with ME-01 as a positive control that fires) found **0 of 33 named files missing and 0 of 33
ids unreferenced**: the library is not a catalogue of intentions.
**Why this instance is the instructive one: the author knew the rule, had written it down that morning, and quoted it
in the same report.** Knowing the rule is not the mechanism. The syntactic trigger IS the mechanism, and it would have
fired: the phrase typed was "appears nowhere", which is on the trigger list above. A rule you must remember to apply
is a preference; a rule attached to a phrase you are about to type is a check.
Practical addition for this shape: a grep whose scope is a hand-listed set of directories cannot support a
"nowhere" claim. Use the repo-wide tool (`git grep`) or state the scope in the sentence ("not in harness/, tests/,
scripts/").
