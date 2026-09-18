# LANE DEL — the DELETION INVARIANT as one landable increment on the SERVED harness (base 237e9094), plants proven pre-fix

Report file: `LANE-DEL-REPORT.md`. This clone is a fresh checkout of main at 237e9094 (the commit served at
https://mahmood726-cyber.github.io/meta-harness/ tonight). Record `git rev-parse HEAD`. Never reset/checkout/stash. No commit. No network.
Standing cadence (Mahmood, 2026-09-18): ONE defect -> land -> serve -> verify the hash moved -> next. This lane produces exactly one
increment: the deletion-invariant test family plus the SMALLEST harness change that makes it hold, inside existing modules
(`harness/pipeline.py`, `harness/page.py`, `harness/grade.py`, `harness/target_endpoint.py`, `harness/gate.py` or wherever the
refusal belongs). No parallel framework, no new module unless a refusal has no home.

## The invariant
*Within a fixed protocol and evidence snapshot, silently deleting support must never improve assurance.* Assurance = anything the page
or its manifest presents as a pass/verdict/certainty: gate results, `certainty`, admissibility verdicts (`EXACT_TARGET` etc., landed in
e3014d02), FACT/verified labels, the pooled k, the retraction/scope markings, the claim-check counts. For each support object below,
take a REAL committed review (`glp1-ra-mace-t2d` and one non-glp1 topic you choose and name), delete the object in a scratch copy of the
inputs (never edit the committed inputs), run the PRODUCTION route (`scripts/build_topic.py <slug> --now 2026-09-11` into a scratch
output dir, or the exact production function chain the builder calls -- name it), and assert ONE of exactly two outcomes:
(a) a TYPED refusal naming the deleted object (not "any exception"; assert the reason string / reason code), or
(b) the build completes and every assurance field is <= its pre-deletion value (no verdict improves, no k grows, no gate flips to PASS,
    certainty does not rise, no count of checked/verified claims rises).
Anything else -- a silent pass, an unrelated exception, an improved field -- is the defect.

## Support objects on THIS tree (verify each exists on 237e9094 before writing its case; drop with a reason if absent)
1. an effect's `definition_span` (landed in e3014d02; see `harness/target_endpoint.py::bind_result_span`, `classify_bound`);
2. an effect's `result_span`;
3. one `grade.domains.*` entry (e.g. indirectness) -- deleting a domain must not raise certainty or zero a downgrade;
4. one trial row from the verified/extracted effects cache for the topic (`cache/<slug>/verified_effects.json` or the file the
   builder actually reads -- name it) -- k must fall or the build must refuse, never "k unchanged, pooled estimate unchanged";
5. one registered-search candidate/denominator artefact the search gate reads (`registry/search_completeness.json` or the topic's
   snapshot record file -- name the exact path);
6. the retraction marking source for `sacubitril-valsartan-hfref` (find what generates 'We retract' / 'REPRODUCTION_RETRACTION' on that
   page; deleting that source must refuse or keep the marking count -- `scripts/retraction_survival.py` is the served instrument).
Two topics x six objects = 12 cases; report the honest table (which are real-object deletions, which need a labelled synthetic
supplement, which could not be constructed and why).

## Order of work (the plant is the deliverable; the fix is second)
1. Write `tests/test_deletion_invariant.py` FIRST and run it on the UNTOUCHED tree. Record per case: FIRED (defect found: silent pass or
   improved field), HELD (already refuses/does not improve), NOT_CONSTRUCTIBLE. Save the pre-fix pytest output to
   `.tmp/del/prefix_pytest.txt`. A family in which nothing fires is reported as such -- do not loosen a case to make it fire, and do not
   tighten one to make it pass.
2. For every FIRED case, the smallest fix in the existing module that owns the decision, with a typed reason. Re-run. Every case now
   (a) or (b). A fix that clears every failure is a loosened test -- re-read each assertion after the fix.
3. Run the unit tests that touch the modules you changed (`python -m pytest tests -q -x -p no:cacheprovider -k "endpoint or grade or
   pipeline or page or gate or deletion"`) and record counts. Then rebuild ONLY the two topics you used (`--now 2026-09-11`) into the real
   `docs/reviews/<slug>/` and record whether their `review_sha256` / `html_sha256` moved (`docs/reviews/<slug>/manifest.json`) -- a fix
   that changes no served byte is fine for this increment; say so.
4. `python scripts/retraction_survival.py 237e9094` -> must print `32 of 32`; STOP and report if not.

## Report (MEASURED / INFERRED / CLAIMED; `n of N`)
- the 12-case table with pre-fix state and post-fix state and the exact assertion each case makes;
- the diff summary of harness changes (files, +/- lines) and the typed reason codes introduced;
- the pytest counts pre-fix and post-fix, verbatim tail lines;
- which topics were rebuilt and whether their hashes moved;
- what this increment does NOT establish.
Never a backslash escape through a heredoc; write regexes to files. No commit.
