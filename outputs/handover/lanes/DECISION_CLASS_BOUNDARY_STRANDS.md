# Decision — contested intervention-class boundaries become two declared strands (Mahmood, 2026-09-16 ~17:20)

Mahmood: "decide on sglt2 yourself but I think we could split into two metas to test it better." Adopted as the **general pattern**: where an intervention-class boundary is contested and a named trial sits on it, render both strands rather than choosing. A definitional question becomes an empirical one — agreement says the boundary does not matter for that outcome (with a number); disagreement is a real finding about the mechanism, not something hidden inside an eligibility rule. Same logic as kidney-only vs cardiorenal and no-baseline-HF vs whole-trial.

## SGLT2 (decided; applies to sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath, sglt2-primary-prevention-hf)
- **Strand A — `SELECTIVE_SGLT2`** (PRIMARY): empagliflozin, dapagliflozin, canagliflozin, ertugliflozin; sotagliflozin excluded.
- **Strand B — `SGLT_PATHWAY`**: A + dual SGLT1/2 agents (sotagliflozin: SCORED, SOLOIST-WHF).
- A is primary because it matches the class the slug names and guidelines treat as one — decided now, in writing, before either strand is computed on these pages.

## Discipline (all four, or this is a licence to report the flattering analysis)
1. Both strands declared in the protocol **before extraction**, with the SHA; labelled retrospective (we already know roughly what each contains).
2. **Both always rendered** — a strand computed and shown only when it agrees is worse than none.
3. Neither designated primary after seeing results — the primary is named at declaration.
4. State that both answers were known before the rule was written (standing rule for any methods choice whose yield can be anticipated).

## Interaction guard
SOLOIST-WHF sits on THREE axes at once: intervention class (dual agent), EF spectrum (broad; whole-trial vs prespecified HFrEF subgroup), and HF acuity (recent worsening HF). Strand B admits it on class only; its EF and acuity dispositions are separate typed decisions rendered on the row (`population_basis`, `hf_acuity`) — one strand decision never smuggles the other two through.

## Proposed strand pairs (to Mahmood for approval before implementation)
| Page | Strand A (primary — matches the slug) | Strand B | Pivot trial(s) |
|---|---|---|---|
| iv-iron-hfref-hosp | `FCM_ONLY` — ferric carboxymaltose (FAIR-HF, CONFIRM-HF, AFFIRM-AHF, HEART-FID, FAIR-HF2) | `ANY_IV_IRON` — + ferric derisomaltose (IRONMAN) and other IV formulations | IRONMAN |
| glp1-ra-mace-t2d | `CONVENTIONAL_GLP1RA` — injected and oral GLP-1RAs (the eight CVOTs, SOUL, FLOW if screened in) | `GLP1RA_ANY_DELIVERY` — + implanted continuous-delivery (ITCA 650, FREEDOM-CVO) | FREEDOM-CVO |
| spironolactone-hfref-mortality (MRA) | `STEROIDAL_MRA` — spironolactone, eplerenone (RALES, EMPHASIS-HF, J-EMPHASIS-HF) | `ANY_MRA` — + non-steroidal (finerenone) | none completed in HFrEF today (FINALITY-HF ongoing) → strand B declared, renders `NO_BOUNDARY_TRIAL_YET`; FINEARTS-HF is HFmrEF/HFpEF and stays a population refusal |
| corticosteroids-cap / -covid19 | `SYSTEMIC_CORTICOSTEROID_ANY_AGENT` (hydrocortisone, dexamethasone, methylprednisolone, prednisolone) — primary | `SYSTEMIC_ANY_DOSE_STRATIFIED` — same set, rendered by dose stratum (low vs high; COVID STEROID 2 / RECOVERY high-dose remain comparator refusals, not strand members) | none on the class boundary — the boundary here is DOSE and ROUTE (inhaled budesonide STOIC/PRINCIPLE stays `X-ROUTE`), so a dose-stratified render, not a class strand |
| colchicine-postop-af / -secondary / -pericarditis | single molecule; no class boundary | — | boundary is REGIMEN (loading dose, duration) → effect-modifier fields, not strands |
| tocilizumab-covid19 | `TOCILIZUMAB` — primary | `IL6_BLOCKADE` — + sarilumab (REMAP-CAP sarilumab arm, sarilumab RCTs) | REMAP-CAP (both arms), sarilumab trials |
| doac-vte / noac-af | `DOAC_ANY` — primary | none contested (dose strata are EN's dimension) | — |
| finerenone-ckd | `FINERENONE` — primary | `NONSTEROIDAL_MRA_ANY` — + esaxerenone/ocedurenone if any kidney-outcome RCT exists (none known) | none |

## Sweep (lane CB)
For every page, list trials in the screening universe or the register whose intervention is on a class boundary the protocol does not define; `n pages with ≥1 boundary trial of 32`, named, with the proposed strand pair — so we find these before an auditor does.
