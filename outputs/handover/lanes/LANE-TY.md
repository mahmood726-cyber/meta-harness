# LANE TY — the TYPE SYSTEM for effects and compatibility: an effect is a typed object on twelve axes; pooling is unification; UNKNOWN fails closed; a coercion is a permanent cited decision object. General machinery; GLP-1 first consumer.

Report file: `LANE-TY-REPORT.md`. Base: the landing-3 commit named in LANE_BASE.txt beside this file (record `git rev-parse HEAD`). Read first and extend, never fork: `harness/compat.py`, `harness/compat_check.py`, `harness/compat_direction.py`, `harness/endpoint_canonical.py`, `harness/design_key.py`, `harness/design_variance.py`, `harness/target_endpoint.py`, `harness/source_hierarchy.py`, `harness/known_missing.py`, `harness/synth.py` (read only — do not touch), `harness/gate.py`, `harness/page.py`. New module: `harness/effect_type.py`. Design owner: the integrator (this brief); you implement and report; you do not decide policy.

## The object (`EffectType`) — one per candidate pooled row, committed per topic as `cache/<slug>/effect_types.json`
Twelve axes, each `{value, basis: span | rule_id | absence_code}`; a field with no span and no rule is `UNKNOWN`, never a default:
1. `population` (entry condition + declared phenotype fields from the protocol)
2. `randomised_contrast` (drug-of-interest present in exactly one arm; background equal) — from the arm structure (SC3 arm object / AACT design_groups)
3. `analysis_set` ∈ {ITT, mITT, PP, on-treatment, unstated}
4. `endpoint_components` (canonical set, e.g. {CV_DEATH, NONFATAL_MI, NONFATAL_STROKE}); a composite including UA_HOSP is a different type
5. `first_or_recurrent`
6. `time_origin`
7. `follow_up` (median, or the timepoint rule the protocol names)
8. `censoring` ∈ {on-study, on-treatment, end-of-study, end-of-treatment, unstated} — the FREEDOM-CVO lesson: two genuine rows in one FDA document differ only here (1.24 vs 1.36)
9. `effect_measure` ∈ {HR, RR, OR, RD, MD, SMD}
10. `adjustment` (stratification factors / covariates named, or unstated)
11. `estimator` (Cox PH, log-binomial, ... or unstated)
12. `report` ∈ {publication, supplement, regulatory FDA/EMA, registry results, HTA, older meta pointer} = `source_level` 1–5 with `document_sha256` when the document is held

## Unification (the pooling decision), per protocol target type
`unify(target, effect) -> MATCH | MATCH_WITH_DECLARED_COERCION(coercion_id) | REFUSE(axis, reason) | UNKNOWN_FAILS_CLOSED(axis)`. A coercion (e.g. 4-point → 3-point where UA events are 0.3%; RR → HR at low event rate; end-of-treatment → end-of-study) is a **permanent decision object** `{coercion_id, who, why, evidence spans, date, consequence, signed_by}` in `cache/<slug>/coercions.json`; without one the row is REFUSED, and a coercion is never authored by this lane — you write the schema, the check, and the plants; you may propose coercions in the report only. `UNKNOWN` on any axis the protocol declares as binding → the row does not pool (fail closed) and renders `UNTYPED — axis <n> unknown` with the reason; the page's k and the count chain reflect it.

## Plants — write them FIRST in `tests/test_effect_type.py`, run on the base BEFORE any harness change, paste the failing output verbatim into the report under "Plants fired pre-fix"; then build; then paste the passing output. A plant that only passes post-fix proves nothing.
1. Two genuine FREEDOM-CVO rows (from `outputs/handover/glp1_regulatory/regulatory_sources_glp1.json` and `outputs/handover/glp1_reviewerB/reviewB_extraction.json`: 1.24 end-of-study vs 1.36 end-of-treatment) → `unify` against the B-prime target (end of randomised follow-up) MATCHes 1.24 and REFUSEs 1.36 on axis 8 with the reason; pre-fix the base has no axis and would pool either.
2. ELIXA 4-point primary (1.02 [0.89, 1.17]) vs the 3-point target → REFUSE on axis 4 without a coercion object; with a fixture coercion object → MATCH_WITH_DECLARED_COERCION rendered with the citation.
3. A row with `analysis_set: unstated` where the protocol declares analysis set binding → `UNKNOWN_FAILS_CLOSED` and the row leaves the pool; where the protocol does not declare it binding → MATCH with `axis 3 unstated` shown.
4. The current glp1 8-row pool: report per row which axes are UNKNOWN today (MEASURED: `n axes known of 12` per trial) — the honest baseline; do not fill axes from names or memory.

## Consumers (additive)
`harness/pipeline.py`: build effect types after extraction, before pooling; the pooled rows carry `effect_type_id` and the unification verdict. `harness/page.py`: a "Typed effects" table (12 axes × pooled rows, class mark per cell: span / rule / UNKNOWN) and the coercion register. `harness/gate.py`: refuses a pooled row whose verdict is not MATCH or MATCH_WITH_DECLARED_COERCION. Sweep `scripts/effect_type_sweep.py` → `docs/effect_type_sweep.json`: for all 32 topics, `n pooled rows fully typed of N`, `n rows with ≥1 UNKNOWN binding axis of N`, `n rows that would be refused of N` — report before/after; do NOT change any page's membership yourself (the gate's refusals are rendered as such on rebuild; membership policy is the integrator's).

Do not touch `harness/synth.py`, search, screening membership. No network. No commit. MEASURED/INFERRED/CLAIMED; `n of N` with N named. Never a backslash escape through a heredoc: write regexes to files.

## Cannot-build-today, say so if hit
Axes 6, 7, 10, 11 are usually absent from abstracts; expect most rows UNKNOWN there — that is the measurement, not a failure. Say so per row.
