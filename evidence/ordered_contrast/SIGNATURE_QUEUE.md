# Lane OC signature queue: served changes held for Mahmood's hash-bound signature

Nothing in this file has landed on a served page. Each item names the exact bytes a signature would bind, what moves on the
served surface, and the notice a reader would see. Engineering decisions behind them are recorded in the lane report
(`C:\mh-lanes\oc\REPORT_2026-09-25.md`) and the commit messages on `oc/ordered-contrast`.

What already landed on the branch changes **no served number**. It adds fields to the GLP-1 `BUNDLE.json` (the ordered contrast,
the registered contrast read from the protocol, the normalisation policy), updates the served verifier mirror, and adds the
verifier's value checks. The structural diff against origin/main shows nothing changed under `pooled_reference` or any row's
`effect`, and every admission is unchanged. `review.json`, `index.html` and `CERTIFICATE.json` are untouched.

---

## OC-Q1 — page wording: "parser-confirmed contrast" claims eligibility, not direction

| | |
|---|---|
| bytes to sign | `evidence/ordered_contrast/QUEUED_page_wording.patch`, sha256 `dfb2109de4c9372259f9f9180ff609e3542e25c2eaf78dcea67982e8dc23f39b` |
| applies to | `origin/main` @ c9d665e0 (`git apply --check` passed); files `harness/page.py`, `harness/limitations.py`, `harness/armcontrast.py` |
| precondition | enforcement-gate lands first: its hunk in `page.py` (`@@ -2787`) sits beside `_AC_LABEL` and would conflict textually; rebase the patch after it |
| served reach | **32 of 32** live pages carry the phrase (`git grep -c "parser-confirmed contrast" origin/main -- docs/reviews/*/index.html`, list in `served_slugs_2026-09-25.txt`). `harness/armcontrast.py` and `harness/page.py` are certificate-pinned, so every page's `analysis_code_sha256` and `release_sha256` move, and the `contrast_status` basis string sits in each `review.json` (`review_sha256` moves) |
| numbers | none change. The patch edits three label strings and one sentence |
| re-render | every page, from its recorded commands; `verify_all.py` offline reproduction must then pass on the new bytes |

**Derived notice (one per page):**
> *Wording correction, no result changed.* The per-trial label "parser-confirmed contrast" claimed more than the check establishes.
> The check shows that the intervention of interest is part of the randomised difference (**eligibility**). It does not show which
> arm is the numerator of an effect. The label now reads "in the randomised difference (eligibility, not direction)". Which arm is
> the numerator is recorded and value-checked per row as the *ordered contrast* in `BUNDLE.json`. Every pooled estimate, confidence
> interval and admission on this page is unchanged.

---

## OC-Q2 — producer pooling refuses mixed or unidentified measures BEFORE any log is taken

The verifier now refuses these before calling `pool()` (landed; it moves no served number, because the one bundled pool is HR
throughout). The **producer** pools through `harness/synth.py::pool` (`Study.yi_vi` takes `math.log(self.effect)` whatever the
label), and `harness/pipeline.py` checks compatibility only **after** pooling (`estmeasure.pool_compatibility`, then suppression). Both
files are certificate-pinned, so any change is a re-release of every page.

**Measured exposure on the SERVED surface** (all 32 live `review.json`, fetched from Pages, not the repo; census script
`measure_census.py`, output `served_measure_census_2026-09-25.json` sha256 `e45b02bd89319bc6a299471f17b26a1f67ffa1347a91d37de5cb3879d985a891` (of the committed LF bytes; the first draft of this line bound the CRLF working copy, 6601498e..., which is not what git stores)):
97 outcomes, 51 pooled, 0 fetch errors.

| pooled measure mix | pools |
|---|---|
| homogeneous RISK_RATIO | 20 |
| homogeneous HAZARD_RATIO_FIRST_EVENT | 20 |
| homogeneous ODDS_RATIO | 3 |
| homogeneous MEAN_DIFFERENCE (raw scale, no log) | 3 |
| **compatible_labels HR + RR (pooled on one log scale)** | **5** |
| unidentified measure pooled | **0** |

The five mixed pools (4 of them primary):

| slug | outcome | k | labels |
|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | Mortality (primary) | 2 | HR + a 2x2-derived RR (label None) |
| doac-vte-recurrence | Symptomatic recurrent VTE (primary) | 6 | HR, RR |
| noac-vs-warfarin-af-stroke | Stroke or systemic embolism (primary) | 4 | HR, RR |
| spironolactone-hfref-mortality | All-cause mortality (primary) | 3 | HR, RR |
| ticagrelor-vs-clopidogrel-acs | Major bleeding | 2 | HR + a 2x2-derived RR (label None) |

**Proposed:** a pre-log guard in `synth.pool` that receives each study's identified measure. It refuses UNKNOWN (moves 0 served
pools) and refuses a mix of ratio measures (moves the 5 above). The mixed-measure half is a **served-number change**: each of the
five would be suppressed, or re-pooled on the single majority measure with the others listed, which is a methods decision. The HR+RR
"compatible_labels" policy was introduced deliberately and disclosed on the page, so it is not mine to overturn unsigned.
**Status: proposal only; no patch is prepared until the policy question is answered.** The unidentified-measure half is safe, but
`synth.py` is pinned, so even that half re-releases every page. It is held with the rest rather than landed alone.

**Derived notice (per affected page, if the mixed-measure half is signed):**
> *Result withdrawn pending a single-measure analysis.* This pooled estimate combined hazard ratios with risk ratios on one log scale.
> They estimate different quantities, and the harness now refuses to pool them before any logarithm is taken. The per-trial results
> are unchanged and still shown.

---

## OC-Q3 — the publication gate and estmeasure authenticate the CLAIMED estimator label

`harness/gate.py` has no estimator-identity check, and `harness/estmeasure.py` derives the canonical estimand from the claimed label
("the label already fixes the class"), with HR and RR in one class, `compatible_labels`. Both files are certificate-pinned.

**Reproduced before the fix** (`estimator_owner/repro_before_fix.json`). The real `gate_page` ran on the GLP-1 page with LEADER
relabelled RR (every certificate digest recomputed) and was compared differentially with the canonical page. Every new reason was
integrity or staleness (certificate, claimgraph `STALE_DEPENDENT`, census); none concerned the estimator. `estmeasure` reported
`compatible_labels`.

**Landed on the branch instead, with no pinned file touched:** estimator identity is source-bound in the bundle verifier and the
bundle producer (`P15_estimator_source_bound`), and it runs before the pool guard.

**Measured exposure on the SERVED surface** (all 32 live `review.json` from Pages; `estimator_label_census.py`, output
`served_estimator_label_census_2026-09-25.json`, sha256 `552898bc4dce3aa93a34d82abfd05fa9105eebbbf830fd452b7f9bea627de1f4` of the committed LF bytes). 111 pooled trial rows:

| kind | rows |
|---|---|
| MATCH (label = the measure the row's own clause states) | 41 |
| **LABEL_DISAGREES_WITH_CLAUSE** | **0** |
| NO_CLAUSE_LOCATED (no clause holds the row's tuple) | 35 |
| COUNTS_ONLY (the ratio is computed from a 2x2; no stated estimator to bind) | 28 |
| CONTINUOUS (outside this check) | 6 |
| CLAUSE_UNSTATED | 1 |

**Proposed:** a gate check that refuses **disagreement** (it would falsely refuse 0 of today's rows), and `estmeasure.classify` taking
the source-bound measure instead of the claimed label. **Status: proposal.** A check that *requires* a bound estimator would refuse
36 served rows; that is a policy choice about hand-extracted and count-derived rows, not a bug fix. Both files re-release every page.
