# Landing: endpoint-span binding (wrong-endpoint acceptance) — 2026-09-18

Base: main `3f8add72`. Built and landed from a fresh clone (`C:\mh-land-a`) of the GitHub URL.
Defect: external review of served glp1 `edaf5f6b`, defect 1 (the highest-value one).

## The defect, measured PRE-fix on main 3f8add72 (`wrong_endpoint_plant_prefix_3f8add72.json`)
- Component-only plant: abstract whose primary outcome is 3-point MACE, no composite result, CV death alone
  HR 0.50 (0.30–0.80). `pipeline._build_outcome` POOLED it: HR 0.50, `EXACT_TARGET`, components
  CV death / MI / stroke, k=1 estimate 0.50. Cause: `target_endpoint._candidate_from_abstract` classified the
  WHOLE abstract and attached that class to a number read from ONE sentence.
- 4-point plant: primary composite adds unstable angina, HR 0.80. POOLED as `NEAR_MATCH` (k=1, 0.80) through
  `eligible = exact or near`, bypassing the composite-mismatch check that only guarded the legacy route.
- Live instances on the served corpus: LEADER (27295427) and EXSCEL (28910237) on glp1 were labelled
  `NEAR_MATCH` (extra: heart failure hospitalization) although both define the primary as CV death / nonfatal MI /
  nonfatal stroke — the abstract's SECONDARY outcome list had polluted the whole-document class. Same on dpp4 (SAVOR),
  finerenone (FIGARO), sacubitril (PARALLEL-HF registry row), ticagrelor (PLATO), colchicine.

## The fix (general, no page-specific code)
- `harness/target_endpoint.py`: every abstract effect is bound to its RESULT span (the sentence the number was read
  from) and the DEFINITION span it refers to (its own enumerated components, or the unique primary/secondary/MACE
  definition sentence it names; result sentences are never definitions). Class computed from the definition span only.
  Unbindable → `ENDPOINT_UNBOUND`. `select_target_endpoint`: eligible = EXACT, or NEAR only under an explicit
  declaration (`allow_near_match` / `component_compat_key` — pcsk9's protocol "MACE as defined by each trial") and
  never with a MISSING component; the best inadmissible candidate is returned as a typed REFUSAL with the refused
  number and both spans. `admissibility()` + `admit_rows()`: ONE mandatory verdict after EVERY route.
- `harness/pipeline.py`: the selector's refusal is honoured (no fall-through to legacy routes that would pool the
  same number without a class); `admit_rows` runs after all routes, before the eligibility contract.
- Vocabulary: "death from vascular causes"/"vascular death" = CV death (PLATO/PHILO/ASCEND/ORIGIN phrasing); TIA is a
  component; "major/serious vascular event(s)" are named endpoints; secondary qualifiers resolve to secondary
  definitions; "Trial-defined …" outcomes have no canonical set by declaration.
- `harness/ctgov_results.py`: `COUNT_OF_PARTICIPANTS` under an event-count title ("Number of Hospitalizations …") is
  typed `UNIT_CONFLICT_EVENTS_VS_PARTICIPANTS` and never reconstructed (HEART-FID: the paper calls 297/332
  hospitalisations). `target_endpoint`: "analysed as recurrent event" is a recurrent-event estimand (AFFIRM-AHF #2).
- `harness/page.py`: per pooled row: binding + definition/result spans + admissibility; per refusal row: the refused
  number and both spans. The reason-code audit table's silent `[:12]` cap removed (it hid a row whenever a refusal
  was added at the top — the marker count fell while the audit grew).
- `topics/sacubitril-valsartan-hfref.json`: explicit `components` (the name's hyphenated "heart-failure" does not
  parse; the general vocabulary fix is HELD — see next increment).

## Corpus effect (32 of 32 rebuilt under CI conditions: empty AACT, --now 2026-09-11; full-field diff)
- glp1: k=8, 0.856 [0.809–0.906] UNCHANGED; LEADER/EXSCEL `NEAR_MATCH` → `EXACT_TARGET`; all seven abstract rows now
  carry their definition span; SOUL (hand-verified) is labelled `unbound_legacy`. review_sha256 edaf5f6b → moved.
- Label-only corrections (numbers unchanged): dpp4 SAVOR, finerenone FIGARO (via the secondary qualifier),
  sacubitril PARALLEL-HF registry row, ticagrelor PLATO, colchicine LoDoCo2.
- omega3 (the one page whose numbers move): VITAL 0.97 [0.85–1.12] (CT.gov registry analysis) → 0.92 [0.80–1.06]
  (publication primary); STRENGTH 1.05 [0.93–1.19] → 0.99 [0.90–1.09]; the registry rows had outranked the
  publication only because the whole-document class demoted the papers to NEAR_MATCH. The blind census (2026-09-12)
  had matched the ABSTRACT numbers (provenance abstract, MATCH) — the registry values were a later drift the census
  could not see. ASCEND 0.97 refused: its "serious vascular event" composite adds transient ischemic attack;
  rendered with the refused number and both spans. k 7 → 6, 0.960 → 0.941.
- Gates: unit suite green on the static tree; honest ratchet 0 remaining after 6 signed acknowledgements (index ×3,
  omega3 ×3, chains for 3 older-base blocks); retraction survival 32 of 32; HM3 primary-baseline control superseded
  BY NAME for omega3 (pinned values untouched); error-rate census re-inventoried (147 pooled, ASCEND recorded in
  removed_by_census_fixes; no new independent verification claimed; refresh script now invalidates a row whose
  stored number moved and dates from the clock).
- Tests rewritten to the requirement (they pinned the defect): `test_verified_override` (ORIGIN's CV-death 0.98 is
  now REFUSED with the refused number, never pooled; an unflagged verified_effect still does not override).

## Held for the NEXT increment (named, not silently dropped)
1. Hyphen vocabulary ("heart-failure" → "heart failure") in `_fold`: general fix, but it makes iv-iron's canonical set
   non-empty and the selector then correctly admits AFFIRM-AHF's first-event registry row (#6, HR 0.73, 142/558 vs
   178/550) — a NEW pooled number that needs its RoB object, arm-contrast (measured: parser-confirmed from AACT
   2026-08-30), parity snapshot re-adjudication (2/3 OVERLAPPING → 3/3 IDENTICAL_SET), refusal-record update and a
   census entry. Reverted tonight; do as one increment with Mahmood's countersignature on the parity/refusal objects.
2. Hand-verified / override / full-text rows are LABELLED `unbound_legacy`, not span-bound (their `source` is a
   description, not a definition span; classifying it repeats the defect in reverse — ORIGIN would have been falsely
   refused). Binding them to held bytes is the FACT-object landing (landing 4).
3. `_components_from_text` matches "cardiovascular death" inside "non-cardiovascular death" (colchicine
   'Non-cardiovascular death' outcome); label-only tonight, unchanged number.
4. Census rows from the original blind audit carry no `stored` value, so a later drift of their pooled number is
   invisible to the refresh (VITAL/STRENGTH were exactly this); record `stored` for every row at the next census.
