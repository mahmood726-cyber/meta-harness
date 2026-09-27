# Semaglutide weight: why the k=2 pooled MD has no registered CI

Report-only audit, 2026-09-27. Historical served artifacts: commit
`3876a62dca66764dff1b4f84d6b43356a1a9e3bb`. Functions exercised in this worktree:
`oc/cx-fixtures-continuous`, HEAD `42a7163f`. No harness/test edits or commit.

**Finding:** the engine computes a finite CI. A later, explicit `K2_SINGLE_DF`
serving policy nulls it while retaining the pooled point estimate. This is
consistent with the harness's declared rule, but the topic protocol does not
declare that k=2 exception. The historical HTML explains the refusal; it is not
an unexplained missing interval. A separately labelled common-effect CI is shown.

## Exact path and recorded reason

Paths/line numbers below refer to HEAD unless a historical location is given.

1. `harness/synth.py:134` (`Study.yi_vi`) computes an arm-derived MD and variance:
   `mean1 - mean2`, `sd1**2/nc1 + sd2**2/nc2`.
   `synth.pool` at line 310 computes Paule–Mandel tau-squared and modified HKSJ
   uncertainty with `factor = max(1.0, Q_gen / (k - 1))` and the Student t
   quantile on `k-1` degrees of freedom. It returns numeric `ci_low/ci_high`.
2. `harness/pipeline.py:658`, `_pool_result`, calls that real `pool`, rounds its
   CI to four decimals, and retains it. Its own k=2 branch suppresses the
   **prediction interval**, not the confidence interval. It also retains the
   separately computed common-effect z-based sensitivity CI.
3. Later in `_build_outcome`, `pipeline.py:1843-1848`, a compatible k=2 result
   goes to `k2_mod.apply_k2_policy(out["result"], trials, ...)`.
   Historical locations: `_pool_result` line 656, policy call line 1614.
4. `harness/k2.py:176`, `apply_k2_policy`, checks for incompatible estimands and
   direction/interval conflict. Here `estmeasure.status == "homogeneous"`,
   canonical `MEAN_DIFFERENCE`, and `k2_trial_diagnostics.conflict == false`.
   Both MDs are negative and their individual CIs overlap. Therefore it reaches
   `return refuse_k2_ci(result)` at line 216, rather than refusing the whole pool.
5. `harness/k2.py:144`, `refuse_k2_ci`, records `pooled_ci_refused`, saves the
   numeric CI in `ci_hksj_unserved`, then explicitly executes at lines 160-161:

   ```python
   result["ci_low"] = None
   result["ci_high"] = None
   ```

`harness/k2.py` is byte-identical between the historical commit and HEAD.
The relevant mean/SD variance and k=2 PM/HKSJ computations are unchanged.

The exact historical JSON pointer is
`/outcomes/0/result/pooled_ci_refused` (outcome name: `Percent change in body weight`):

```json
{
  "code": "K2_SINGLE_DF",
  "detail": "Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here."
}
```

It also records:

```json
"ci_hksj_unserved": {
  "ci_low": -25.1318,
  "ci_high": 1.442,
  "method": "PM tau^2 + HKSJ on t(1)",
  "note": "computed for auditability only; not served as the registered interval at k=2"
}
```

There is no `result.reason`, `pool_refused`, or `suppressed_incompatible` flag
for this outcome. `result.claim.state` is `NO_POOLED_CLAIM_K2`, its
`refusal_code` is `K2_SINGLE_DF`, and its basis is:

> no significance/null-crossing claim is emitted for a refused k=2 HKSJ CI

High heterogeneity is **not the CI-null trigger**. `material_heterogeneity`
only appends the fixed-effect caveat when tau-squared > 0 and I-squared > 25%.
The blanket k=2 CI refusal also applies without material heterogeneity.

## Is suppression consistent with the declarations?

**Harness rule: yes.** The `harness/k2.py` module declaration says:

> The synthesis engine still computes PM/HKSJ exactly as registered. This module decides what may be served when k=2: no registered HKSJ CI is served, and a two-trial direction conflict refuses the pooled row entirely.

The first clause applies; the second does not. This report establishes policy
conformance, not an independent statistical endorsement of a blanket refusal.

**Topic protocol: not explicitly authorized/documented there.**
`protocols/semaglutide-obesity-weight.md`, Outcomes, says:

> The estimand is the mean difference (percentage points) in the Week-68 percent body-weight change, semaglutide 2.4 mg versus placebo. Pooling is random-effects inverse-variance on the mean difference; a single included trial is presented as that trial's own effect.

The complete protocol contains no k=2 CI-refusal rule, no HKSJ-specific
exception, and no replacement of the random-effects interval by a common-effect
interval. Thus the random-effects point computation matches the stated pooling
method, but the serving exception comes from global harness policy, not this
topic's declared protocol. The protocol does not explicitly demand a CI either;
this is an undeclared serving exception, not evidence that its literal text
expressly prohibits suppression. Protocol text is unchanged between 3876a62d
and HEAD.

There is also a distinct denominator mismatch in that protocol. Sources and
verification specifies:

> A single estimand is used consistently across trials (the ClinicalTrials.gov *in-trial / treatment-policy* observation-period row, all-randomized denominator, from baseline to Week 68)

The held registry population text for both trials actually distinguishes:

> Overall number of participants analyzed = full analysis set (FAS) which comprised all randomized participants. Number Analyzed = number of participants with available data.

The continuous-identity correction uses the observed class-level n associated
with the raw means/SDs. That fixes the variance-input identity; the unchanged
protocol's “all-randomized denominator” wording does not describe that corrected
calculation. This denominator issue does not cause the CI refusal. No claim is
made here that observed raw means equal the published adjusted treatment-policy
estimates.

## Source-backed inputs and numerical reproduction

The two rows are read from the historical served review, not invented fixtures.
Registry identifiers are cross-checked against its trial-family mappings and
the held `cache/semaglutide-obesity-weight/records.json` at the same commit.
The current real `extract_ctgov` returns the corrected class-level n from those
held records; `continuous_identity.typed_measure` confirms the observed/FAS
distinction and Week 0–68 timeframe.

| Trial / identifiers | Semaglutide mean (SD) | Placebo mean (SD) | Served n, semaglutide/placebo | Corrected observed n |
|---|---:|---:|---:|---:|
| STEP 1 / PMID 33567185 / NCT03548935 | -15.6 (10.1) | -2.8 (6.5) | 1306 / 655 | 1212 / 577 |
| STEP 3 / PMID 33625476 / NCT03611582 | -16.5 (10.1) | -5.8 (7.7) | 407 / 204 | 373 / 189 |

Method: real `synth.pool(studies, scale="MD", require_study_effect=True)`,
default alpha 0.05, Paule–Mandel random effects + modified HKSJ with variance
factor floor 1 and t(1); additive scale, units percentage points.

| Quantity | Served n | Corrected n |
|---|---:|---:|
| k | 2 | 2 |
| Random-effects pooled MD | -11.8449198881 | -11.8523330289 |
| Computed 95% PM/HKSJ CI (unserved) | [-25.1318086599, 1.4419688838] | [-25.1303349206, 1.4256688627] |
| PM tau-squared | 1.8630556893 | 1.8327104026 |
| Q | 6.4484184453 | 5.9228085180 |
| I-squared (pipeline rounding) | 84.5% | 83.1% |
| Common-effect MD (separate sensitivity) | -12.3620831569 | -12.3560989355 |
| Common-effect 95% z-based CI | [-13.0205648178, -11.7036014960] | [-13.0466097379, -11.6655881330] |
| CI fields after `apply_k2_policy` | null / null | null / null |
| Refusal | K2_SINGLE_DF | K2_SINGLE_DF |

Corrected minus served: pooled MD **-0.0074131409** percentage points; HKSJ lower
limit **+0.0014737393**, upper limit **-0.0163000211**. Both computed HKSJ
intervals cross zero. The fixed/common-effect CIs are not alternative bounds
around the random-effects point estimate: they use their own weights and point
estimate, and the page warns about the common-effect assumption here.

Executable reproduction, run from the repository root with Python (no writes):

```python
import copy, json, subprocess
from pathlib import Path
from harness.synth import Study, pool
from harness.pipeline import _pool_result
from harness.k2 import apply_k2_policy
from harness.ctgov_results import extract_ctgov

commit = "3876a62dca66764dff1b4f84d6b43356a1a9e3bb"
slug = "semaglutide-obesity-weight"
def held(path):
    return json.loads(subprocess.check_output(["git", "show", f"{commit}:{path}"]))

review = held(f"docs/reviews/{slug}/review.json")
outcome = next(o for o in review["outcomes"]
               if o["name"] == "Percent change in body weight")
sources = held(f"cache/{slug}/records.json")
topic = json.loads(Path(f"topics/{slug}.json").read_text(encoding="utf-8"))
for scenario in ("served", "corrected"):
    rows = copy.deepcopy(outcome["trials"])
    if scenario == "corrected":
        for row in rows:
            extracted = extract_ctgov(
                sources["ctgov_results"][row["trial_family_id"]],
                topic["primary_outcome"]["keywords"],
                topic["intervention_terms"], topic["comparator_terms"])
            for key in ("mean1", "sd1", "mean2", "sd2"):
                assert extracted[key] == row[key]
            row["nc1"], row["nc2"] = extracted["nc1"], extracted["nc2"]
    studies = [Study(**{k: v for k, v in row.items()
                       if k in Study.__dataclass_fields__}) for row in rows]
    # Refresh the diagnostic SE as well as the actual variance inputs.
    for row, study in zip(rows, studies):
        row["study_effect"]["standard_error"] = study.yi_vi()[1] ** 0.5
    raw = pool(studies, scale="MD", require_study_effect=True)
    result = _pool_result(studies, "MD", require_study_effect=True)
    assert (result["ci_low"], result["ci_high"]) == (
        round(raw.ci_low, 4), round(raw.ci_high, 4))
    apply_k2_policy(result, rows)
    assert result["ci_low"] is None and result["ci_high"] is None
    assert result["pooled_ci_refused"]["code"] == "K2_SINGLE_DF"
    assert result["k2_trial_diagnostics"]["conflict"] is False
    if scenario == "served":
        for key, value in result.items():
            assert outcome["result"][key] == value, key
    print(scenario, raw.estimate, raw.ci_low, raw.ci_high,
          raw.estimate_fixed, raw.ci_low_fixed, raw.ci_high_fixed)
    print(json.dumps(result, indent=2))
```

## What the reader sees at 3876a62d

Evidence is the historical `docs/reviews/semaglutide-obesity-weight/index.html`
itself, read via `git show`; HTML text nodes were extracted with the standard
library HTML parser, excluding scripts/styles. This is inspection of generated
reader-facing HTML, not a claim of a browser E2E run.

Overview and Results both show the label:

> Pooled point estimate (registered CI refused)

with value:

> -11.84 (MD); no pooled significance/null-crossing claim

and a “Registered PM/HKSJ CI” row containing:

> REFUSED (K2_SINGLE_DF): Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here.

Results additionally has this visible refusal block:

> Registered pooled CI REFUSED at k=2. Registered PM/HKSJ uses t(1)=12.71 at k=2; the interval is not served as a pooled confidence interval because a single degree of freedom is not reliable here. The point estimate may be displayed, but no pooled significance/null-crossing claim is emitted.

The separate “Common-effect sensitivity (z-based; not the registered interval)”
row begins:

> -12.36 (MD), 95% CI -13.02--11.7

Its caveat says the common-effect interval “assumes one common effect and is not
a robustness sensitivity to the registered random-effects model.” The manuscript
text embedded in the page also explains the t(1)=12.71 refusal. Therefore the
page does not merely display a point estimate with no interval and no reason.

Renderer path: `page._effect_rows` (line 381) switches on `pooled_ci_refused`;
`_outcome_block` calls `_k2_ci_refusal_block` at line 1728, and
`_common_effect_row` at line 391 renders the labelled sensitivity and caveat.
The renderer discloses the existing policy decision; it does not null the CI.

## Scope and verification

| Component | Static versus dynamic disclosure |
|---|---|
| Artifact anchor and outcome name | Explicit static audit selection, not inferred current served state |
| Trial identifiers, means, SDs, served n | Dynamically read from anchored review and checked against held registry records |
| Corrected n | Dynamically extracted from the anchored registry records by current real extractor |
| Estimates, intervals, heterogeneity | Real `synth.pool` and `_pool_result` computations, not hardcoded research output |
| Refusal threshold and rationale | Static harness policy; applied dynamically to the two real rows |
| Report tables and quotations | Static transcription of the executed results and inspected source/HTML |

PASS: real-function replay reproduces every returned served-result field checked
against the historical JSON; corrected-n replay retains `K2_SINGLE_DF`; source
extraction confirms both corrected n pairs; historical HTML contains the refusal
explanation. This is a scoped analytical replay, not a full topic rebuild or
release certification. No harness/tests were edited or new tests added.
