# Protocol — Zinc vs placebo for common-cold duration

**PICO.** Adults with the common cold; zinc (lozenges/acetate/gluconate) vs placebo; outcome =
duration of the common cold (days); estimand = mean difference (days).

**Eligibility (P/I/C/design only).** Randomised, double-blind, placebo-controlled trials of zinc
in the common cold, reporting cold duration. Excludes pneumonia/COVID/influenza/diarrhoea/malaria
populations. Screening is on P/I/C/design; whether duration is reported is decided at extraction.

**Outcomes.** Primary: duration of the common cold (days), mean difference.

**Analysis.** Random-effects inverse-variance on the mean difference (raw scale); Paule-Mandel
tau^2; HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); prediction interval
mu ± t_{k-1}·sqrt(tau2+se^2). Validated vs metafor 5.0.1. Only trials reporting per-arm mean±SD
(or median/IQR convertible via Wan 2014) with per-arm n are pooled; others declared-absent.

**Comparator.** A published open-access meta-analysis of zinc for common-cold duration.
