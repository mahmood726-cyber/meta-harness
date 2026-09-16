# LANE KM — a STALE evidence set must be shown beside a sensitivity to the NAMED missing trials: standard panel wherever `known_eligible_missing` is set

Report file: `LANE-KM-REPORT.md`.

## The failure (external audit of `glp1-ra-mace-t2d`, hash `d77d184aa10edacf`; CLAIMED until re-measured)

The page's invalidation object names FLOW and FREEDOM-CVO as eligible under the registered PICO and not pooled (`known_eligible_missing`) — and stops there: "we don't know what we're missing". The honest version is "here is what the named missing evidence would do":
- FLOW (semaglutide, T2D + CKD): secondary endpoint strict 3-point MACE, HR 0.82 [0.68, 0.98], 212 vs 254 events — satisfies every registered criterion (CLAIMED; verify against the cached record / full text if present; if the number is not in a committed source, the panel shows the trial as `NAMED, VALUE NOT IN COMMITTED SOURCE` and computes nothing for it).
- FREEDOM-CVO (ITCA 650): 4,156 randomised, double-blind, placebo; published 4-point MACE HR 1.21 [0.90, 1.63]; a strict 3-point ≈1.24 [0.90, 1.70] appears only in secondary syntheses — **do NOT import that; source-verify from full text/supplement or leave unresolved and say so.**
- Auditor's sensitivities under the page's own PM+HKSJ (CLAIMED; recompute with `harness.synth.pool`): +FLOW → k=9 ≈0.8540 [0.8095, 0.9008], τ²=0; +both → k=10 ≈0.8527 [0.7916, 0.9184], τ²≈0.0041.

`known_eligible_missing` is set on **6 of 32** pages (MEASURED by the integrator from served `invalidation.reasons`): colchicine-postop-af, corticosteroids-cap-mortality, dpp4-mace-t2d, empagliflozin-hfpef-hosp, glp1-ra-mace-t2d, iv-iron-hfref-hosp. Confirm the count and names yourself.

## What to build

1. A `known_missing_sensitivity` object per primary outcome, built in `harness/pipeline.py` after invalidation: for each trial named in `known_eligible_missing`, a row with `trial_key`, `name`, `why_eligible` (from the invalidation detail), `value_status` ∈ {`IN_COMMITTED_SOURCE` (effect+CI or counts on the target estimand found in cache, span quoted), `IN_SOURCE_DIFFERENT_ESTIMAND` (e.g. FREEDOM-CVO 4-point), `NOT_IN_COMMITTED_SOURCE`}, and — ONLY for `IN_COMMITTED_SOURCE` rows — the re-pool with each such trial added, and with all of them added, using the identical estimator (`synth.pool`, same scale, same method string), labelled SENSITIVITY, never replacing the primary. A row whose value is not in a committed source contributes no number and says so. Every number carries the same `verify_basis` machinery as pooled rows.
2. Render it as a standard panel "Known eligible trials not in this pool, and what they would do" directly under the primary result on every page where the flag is set; the STALE banner links to it. The panel is a dependent of the input-set version (coordinate with lane CG: stamp it with `claim_id`/`depends_on` if CG's `claimgraph.stamp_review` is present at integration; otherwise add the fields with the same names).
3. Gate: `harness/gate.py::check_known_missing_panel` — a page with `known_eligible_missing` set and no panel refuses; a panel row with a number but no committed-source span refuses.
4. Rebuild the 6 pages; `reproduce_review.py` each; quote each panel.
5. Also record the rendered endpoint for glp1 as the literal canonical object `CV_DEATH | NONFATAL_MI | NONFATAL_STROKE` (composite components per trial) if lane EN's `components` field is present at integration; otherwise add the field with that name.

## Plants (must fire pre-fix)

`tests/test_known_missing_panel.py`: pre-fix fixture copy of glp1 `review.json` → `known_eligible_missing` set, no panel → gate fires; post-fix → panel present with FLOW's status and FREEDOM-CVO's status as measured from the cache; synthetic: a missing trial whose value is only in an uncommitted source → row shows `NOT_IN_COMMITTED_SOURCE` and NO number (assert no numeric fields); a missing trial with committed counts → sensitivity computed and equals a direct `synth.pool` call.


## SECOND PLANT — the panel must be able to say "THIS CHANGES THE CONCLUSION", not only "robust" (colchicine-postop-af, hash `1d645bc2ec5d8f3c`)

Two recoverable trials sit on the page as extraction debt, NOT search debt: COCS (PMID 36286314) — marked "not extracted — the outcome's number IS in the source"; the cached abstract gives 21/113 vs 39/127 (OR 0.515 [0.281, 0.943]); COPPS (PMID 22090167) — screened in, unpooled as "abstract only"; abstract gives 12.0% vs 22.0% with recoverable denominators 20/169 vs 37/167. Integrator's MEASURED recompute with the page's own PM+HKSJ: served k=4 RR 0.6735 [0.3760, 1.2067]; with both added k=6 **RR 0.6488 [0.4782, 0.8802]**, τ²=0.02843, PI 0.382–1.102. The served CI crosses 1; the k=6 CI does not.

Requirements this adds:
- Each sensitivity row and the combined row carry `conclusion_effect` ∈ {`UNCHANGED`, `CHANGES_CI_NULL_CROSSING`, `CHANGES_DIRECTION`, `NOT_COMPUTABLE`} derived from the claim object (`harness/claim.py::derive`) on the primary vs the sensitivity — never from prose; the panel headline states it; the STALE banner on such a page must say the served conclusion is invalidated by named, in-source evidence.
- Distinguish, per missing trial, `EXTRACTION_DEBT` (in a committed source, number present: COCS, COPPS), `REACH_MISS` (never in the corpus: Sarzaeem 2014, no PMID — Phase 2B), `NOT_IN_COMMITTED_SOURCE`. Only EXTRACTION_DEBT rows with counts/effect in the cached source contribute a number.
- Do NOT pool COCS/COPPS into the primary — that is an evidence-set change and belongs to the protocol-first Phase 2 commit. The panel is where the number lives until then.
- Plant: pre-fix colchicine-postop-af object has `eligible_declared_absent` naming both PMIDs and no panel → gate fires; post-fix panel shows k=6 RR 0.6488 [0.4782, 0.8802] labelled SENSITIVITY with `conclusion_effect = CHANGES_CI_NULL_CROSSING`. glp1 stays the robustness control (`UNCHANGED` under +FLOW).

Do not touch: which trials are POOLED (the panel is a sensitivity), `harness/synth.py`, `harness/estmeasure.py`, search code, the extractor. No network.
