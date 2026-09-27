# External independent reproduction of the pooled result — agreement per quantity

A senior external reviewer computed the GLP-1 MACE pool independently, with no meta-harness code
imported (numpy/scipy only). Their script and `results.json` were supplied; this records the comparison
**per quantity, to the precision each side states**, for the release note.

**Their numbers are never copied into served content.** Everything we serve is derived by our pipeline.
This file is a cross-check, not a source.

## 1. Their script reproduces their own results on this host

Ran their `independent_sensitivity.py` here and compared every leaf of the output with their shipped
`results.json`:

    numeric leaves identical (tolerance 1e-12) : 78 of 78
    differing                                  :  0
    non-identical leaves                       : environment.numpy 2.3.5 -> 2.4.4
                                                 environment.python 3.13.5 -> 3.13.13
                                                 environment.scipy 1.17.0 -> 1.17.1

So the calculation is stable across those library versions. Worth stating because this project has
previously found a served bundle *not* byte-reproducible across platforms (a z quantile differing in the
last places); that class of drift does not appear here.

    their script  sha256 e5002cae13ebdb2d...
    their results sha256 0e08c4b064ae4726...

## 2. Their baseline against OUR pipeline

| quantity | theirs (independent) | ours (served) | ours (exact) | at served precision | at full precision |
|---|---|---|---|---|---|
| k | 8 | 8 | — | AGREE | — |
| HR | 0.8559934175938467 | 0.856 | 0.8559934175939847 | AGREE | AGREE |
| CI low | 0.8086248326601262 | 0.8086 | 0.8086248326603205 | AGREE | AGREE |
| CI high | 0.9061368157017332 | 0.9061 | 0.9061368157018077 | AGREE | AGREE |
| PI low | 0.8068929729549049 | 0.8069 | — | AGREE | — |
| PI high | 0.908081685580553 | 0.9081 | — | AGREE | — |
| tau^2 | 4.447972517261982e-05 | 4e-05 | 4.4479725147539284e-05 | AGREE | AGREE |
| I^2 % | 0.8599857615189983 | 0.9 | — | AGREE | — |
| Q | 7.060721196954361 | 7.06072 | — | AGREE | — |

    at the precision we publish : 9 of 9 agree
    at full float precision     : 4 of 4 agree (tolerance 5e-12)

Largest deviation on the pooled quantities, so the agreement is quantified rather than asserted:

    HR       abs 1.380e-13   rel 1.612e-13
    CI low   abs 1.943e-13   rel 2.403e-13
    CI high  abs 7.450e-14   rel 8.221e-14
    tau^2    abs 2.508e-14   rel 5.639e-10   (large RELATIVE only because tau^2 is ~4e-5)

This is floating-point noise between two implementations, not a method difference.

## 3. The estimator, and the trap both implementations avoided

Our page declares its estimator:

    ci_provenance: synth.pool:PM-tau2+HKSJ-t(k-1)+floor-max(1,Q/(k-1)):v1

Their run reports `hksj_variance_factor_after_floor: 1.0`. That matters: Q = 7.0607 against df = 7, so
**Q < k-1**, which is exactly the case where HKSJ would otherwise narrow the confidence interval *below*
DerSimonian-Laird. Both implementations applied the `max(1, Q/(k-1))` floor and landed on the same
interval. Two other standard errors are also avoided on both sides: the interval uses a **t(k-1)**
quantile rather than a normal one, and tau^2 is Paule-Mandel rather than DerSimonian-Laird.

## 4. A limitation of the prediction-interval convention, visible in their own output

Their `baseline_plus_FLOW` scenario returns I^2 = 0.0% with **PI 0.810-0.901, identical to its CI at
three decimals**. That is not an error: their script states it "retain[s] the inspected page's
prediction-interval convention for comparability". It is a property of the convention — with tau^2 = 0,
`sqrt(tau^2 + se^2)` collapses to `se`, so a t-based prediction interval *becomes* the confidence
interval and stops carrying predictive information.

**A prediction interval equal to its confidence interval must never be read as predictive certainty.**
The release note says so, next to the interval.

## 5. Their sensitivity scenarios — for context only, NOT for the page

    eight_trial_baseline          k= 8  HR 0.8560  CI 0.809-0.906  I2  0.9%  PI 0.807-0.908
    baseline_plus_FLOW            k= 9  HR 0.8540  CI 0.810-0.901  I2  0.0%  PI 0.810-0.901
    baseline_plus_ELIXA(rounded)  k= 9  HR 0.8632  CI 0.802-0.930  I2 37.0%  PI 0.737-1.012
    baseline_plus_FLOW_and_ELIXA  k=10  HR 0.8615  CI 0.807-0.920  I2 31.3%  PI 0.752-0.987
    plus FLOW+ELIXA+FREEDOM-CVO   k=11  HR 0.8675  CI 0.800-0.941  I2 43.9%  PI 0.704-1.069

Their point, which we adopt: **the average effect is stable across all five; the apparent homogeneity is
not.** I^2 moves 0.9% -> 43.9% and the prediction interval crosses 1 in two scenarios. So the fragile
claim in V1 is not the pooled estimate but the impression of consistency around it.

If the evidence lane's FLOW/ELIXA/FREEDOM adjudication settles before the freeze, these scenarios are
**generated through our own pipeline and derived, never typed**, and shown on the page. If it does not
settle, the page states that the sensitivity analysis is not yet computed — it does not quote the table
above.

## 6. Their verdict, quoted

> "a correct calculation, not yet a validated review"

Adopted as the framing for V1.
