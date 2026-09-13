# Codex corpus-sweep queue (survives reset; banked reset expires 2026-09-21)

Rules: `</dev/null` on every exec; verify by model tokens + artefact never exit code; one lane per
worktree; concurrency 3; alternate lanes with gating; push every commit; test guards vs every topic's
positive controls; a plant must fire pre-fix. Each item: DEFECT / EVIDENCE / SAFE FIX / REGRESSION RISK.

## LANDED
- [x] Preregistration-vs-build SHA (harness) + gate limb + honest render (commit aaca0c5). 10/32 prospective, 22 not.
- [x] Effect-measure type system (748cb7c). Comparator atomic extraction (6e54ba1). Estimand HR-preference (cc81dc9).
- [x] Arm-contrast parser (7f3b552). Recall->positive-control-recovery rename (a42aa46). Eligible-vs-contributing (fd4aa4a).

## QUEUED (corpus-wide, parallelisable)
1. docs/sha_audit.json — classify every topic's displayed SHA prospective/build; n of N, N named. [Claude has data; emit artefact]
2. Substudy identifier through extraction->RoB->funding->GRADE; sweep every publication with >1 randomised comparison. [Codex lane: substudy_identity]
   DEFECT: RoB collapses to publication level, applying one substudy's design to another (EINSTEIN-DVT open-label vs -Extension double-blind, PMID 21128814).
   EVIDENCE: efficacy layer separates them; RoB does not. SAFE FIX: carry a trial/substudy id through all layers. REGRESSION RISK: id-collision changing pooled identity — test pooled-set unchanged.
3. D3 -> not-assessed by default corpus-wide; re-run low-risk sensitivities; report moved estimates/GRADE. [Codex lane: d3_impact analysis; Claude lands fix]
   DEFECT: D3 'low' from study-discontinuation proxy, not outcome-missingness (our own tooltip admits it). SAFE FIX: default not-assessed unless outcome-missingness evidence. REGRESSION RISK: over-broad not-assessed lowering coverage — check GRADE cap logic.
4. D5 semantic reconciliation of registered vs reported outcomes before selective-reporting concern. [Codex lane: d5_semantic]
5. Harms population from already-fetched abstracts corpus-wide (no new fetch). [Codex lane: harms_abstracts]
6. Comparator k from comparator abstract first sentence where stated. [Codex lane: comparator_k]
7. docs/k_ledger.json — per topic: our k, comparator k, their-trials-not-ours + reason code
   (not-found / screened-out / screened-in-unextractable / ineligible-under-protocol); aggregate. [Codex lane: k_ledger draft; Claude verifies+emits]
8. SEARCH REBUILD (network, CLAUDE-serialised, not Codex): concept-query reference universe; test set ~25 named
   missing trials; report how many found UNAIDED. Top Tier-1 metric.
