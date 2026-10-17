# Lane L8 — keep A7 to its scope: the 'N in the <arm> group' arm-size form serves the CONSISTENCY CHECK only

Context (coverage lane, 15 Oct). A7 part 2 added to `harness/extract._arm_ns` the pattern
`rf"(\d+)\s+in\s+the\s+{tl}\s+(?:group|arm)\b"` so that `percentage_implied_counts` can read PICU's arm sizes ('10 in the
LGG group and 9 in the placebo group'). Because `_arm_ns` also feeds the EXTRACTION count path, the same pattern admitted
a new trial into a served pool (colchicine-postop-af COCS: '113 in the colchicine group and 127 in the placebo group'),
and the full suite then (rightly) failed two gates for it: tests/test_arm_contrast_coverage.py and
tests/test_rob_coverage.py (a newly pooled trial has no arm-contrast status and no RoB assessment). That admission is
outside A7's scope (A7 = a typed disagreement that ADMITS NOTHING).

## Do
1. `_arm_ns(abstract, interv_terms, comp_terms, analysed_group_form=False)`: the 'N in the <arm> group/arm' pattern is
   tried ONLY when `analysed_group_form=True`. Every existing caller keeps the default (False) -- extraction is exactly as
   before A7 part 2. `percentage_implied_counts` calls `_arm_ns(..., analysed_group_form=True)`. Comment why.
2. Plants in `tests/test_a7_picu.py` / `tests/test_reported_vs_derived.py` (synthetic text only; SEE THEM FAIL first):
   - `extract._arm_ns("There were 113 in the colchicine group and 127 in the placebo group.", ["colchicine"], ["placebo"])`
     == {} (default), and == {"i": 113, "c": 127} with analysed_group_form=True;
   - a synthetic COCS-shaped abstract ("The final analysis included 240 study subjects: 113 in the colchicine group and 127
     in the placebo group. POAF was observed in 21 (18.6%) patients of the colchicine group vs. 39 (30.7%) control
     patients (OR 0.515; 95% Cl 0.281-0.943; p = 0.029).") with keywords ["poaf"], interv ["colchicine"], comp
     ["placebo", "control"], estimand "OR": `extract_trial` must NOT return counts 21/113 v 39/127 (it returns absent).
   - The existing test `test_arm_sizes_stated_as_n_in_the_group_are_read` asserts `_arm_ns(PICU) == {"i": 10, "c": 9}`; it
     reads cache/ which your clone lacks. Rewrite its assertion to call `_arm_ns(..., analysed_group_form=True)` and add a
     second assertion that the default returns {} for that abstract. (You cannot run it; say so in the report.)
3. `tests/test_regex_partial.py::test_every_extractor_is_covered_by_the_scan` asserts the extractor count == 15. A7 added
   three extractor-kind specs (_RATIO_VALUE, _NEXT_ESTIMATE, _PCT_PAIR). The coverage lane ran `regex_layer.partial.scan()`
   on the held corpus: each of the three yields 0 fragment groups in 35,673 held sentences (18 extractors scanned). Update
   the count to 18 and extend its comment with exactly that evidence (date 15 Oct, coverage lane).
4. Run `python -m pytest -q -p no:cacheprovider tests/test_reported_vs_derived.py tests/test_a7_oracle.py
   tests/test_regex_partial.py tests/test_regex_plants.py tests/test_regex_inventory.py` (tests needing cache/ will error
   in your clone -- list them, do not fabricate fixtures). No network. Touch only harness/extract.py and those test files.

## Finish condition / artefact
`LANE_REPORT.md` (each plant's failing output, the fix, passing output, what you could not run) and `lane.patch`.
Do not commit or push.
