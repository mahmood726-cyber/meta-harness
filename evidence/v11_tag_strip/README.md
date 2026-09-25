# V1.1: '<' and '>' in scientific text survive markup stripping (lane OC)

**Branch `oc/v11-tag-strip`. It is NOT for the Saturday freeze and is not to be merged before Sat 15:00 unless the release captain
asks.**

## The defect (reproduced before the fix)

Every source-text strip site used `<[^>]+>`, which deletes from a literal `P<` to the next `>`. "(P<0.001), HR 0.82 (95% CI 0.70 to
0.96; P>0.2)" loses the whole effect tuple.

Sites fixed, all now `harness.markup.strip_markup`:
- `absence._strip_markup` (declared-absent classification)
- `reason_audit._plain` (the reason-code audit and the unextracted-value audit)
- `hand_binding._plain` and its JATS prose strip
- `cites._clean_text` and `registry_multi._clean_text` (API values)

Sites **not** changed, because they strip the harness's OWN rendered HTML, where a `<` in data is already `&lt;`: gate, index,
honest_ratchet, rob2, comparator_panel.

`strip_markup` treats `<` as markup only when real markup syntax follows: `<name …>`, `</name>`, comments, CDATA, processing
instructions, `<!DOCTYPE`. A `<` followed by a digit, space, `.`, `=` or `-` is text.

## Plants that fire before the fix (`tests/test_markup_strip.py`)

All 7 failed on the pre-fix code, and all 13 tests pass after the fix:
- the effect tuple between `P<` and `P>`, run through each of the five sites;
- a decision-level plant: pre-fix, `absence.classify` returned an absence claim for an outcome whose counts and HR sat after a `P<`;
- a corpus plant: every held abstract containing `<` must keep every token an independent reference parser (stdlib `html.parser`)
  reads as text.

## Re-measurement (`measure_damage.py` → `damage_before_after.json`)

Rule: TOKEN, meaning a word or number the independent reference keeps as prose is missing from the output. Tokens that occur only
inside tag syntax are excluded both before and after.

| held text (all 38 topic caches) | fields containing `<` | damaged BEFORE | damaged AFTER |
|---|---|---|---|
| record abstracts | 891 | **81** (26 topics); **84** by the CHARS rule | **0** |
| `fulltext_by_pmid` full texts | 85 | 58 (3 topics) | **0** |
| `comparator_fulltext` | 30 | 19 | **0** |
| `ft_<pid>.txt` held full texts | 61 | 0 | 0 (8 markup-only residues are shown and classified) |

The main lane's figure was "84 of 892 across 26 topics". This measurement finds 891 abstracts containing `<` and 84 damaged by the
CHARS rule, or 81 by the independent TOKEN rule. The one-field difference in the denominator is not explained here and is stated
rather than rounded.

## Declared-absent entries (`rederive_declared_absent.py`, `rederive_audit_surfaces.py`)

Re-run through the pipeline's own functions on the 32 live pages (`review.json` from Pages), before vs after, identical inputs:
- **670** declared-absent rows. **433** of them assert absence: OUTCOME_NOT_IN_SOURCE 297, SOURCE_NOT_RETRIEVED 134,
  outcome_not_reported 1, outcome_post_hoc_not_pooled 1.
- Rows whose held text the old regex damaged: **7 of 670**, **3 of 433**. This independently reproduces the PVA lane's "7 of 670".
- `classify_reason` code/state changes: **0 of 670**. Values newly visible in held sources: **0**.
- `reason_code_audit` verdicts changed: **0 of 670**. `unextracted_outcome_audit` rows changed: **0 of 797**. This null is backed
  by a positive control (`audit_surfaces_POSITIVE_CONTROL.json`): a stripper that deletes all held text changes 14 of 32 and 2 of
  45 rows on two pages, so the comparison can see a change.
- **Declared-absent entries that would gain a poolable result: 0 of 433** (0 of 670). Extraction (`harness/extract.py`) reads the
  raw abstract and never passes through a stripper, and `classify_reason` is documented never to make a value poolable. Pooled
  numbers cannot move through this fix.
- Two omega3 MACE rows (PMID 23656645, one of the 433; PMID 38184150) cannot be re-run from served rows. `classify_reason` raises
  on its typed-refusal branch, which returns before any stripping, so the fix cannot reach them. They are listed, not counted.

## What merging costs

The five changed modules are certificate-pinned. `harness/markup.py` is new and becomes part of every certificate's import
closure. **V1.1 therefore re-releases all 32 pages**, with no number moving (see above). Until they are re-certified, CI on this
branch refuses the certificate, reproduction and gate limbs; that is expected. In this sparse tree, 195 existing tests fail
identically on the pre-fix and post-fix code (missing served files), so the fix causes none of them.
