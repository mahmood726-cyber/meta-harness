# Protocol - Empagliflozin for cardiovascular death or worsening heart failure in HFmrEF/HFpEF

**Registration.** The commit that adds/updates this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with heart failure and mildly reduced or preserved ejection fraction
  (HFmrEF/HFpEF; operationally LVEF >40% or preserved-EF trial eligibility).
- **I** - Empagliflozin 10 mg daily, added to usual heart-failure therapy.
- **C** - placebo or matching placebo, added to usual heart-failure therapy.
- **O (primary)** - time to first composite cardiovascular death or worsening heart
  failure, where worsening heart failure includes hospitalization or urgent visit for
  heart failure as defined by the trial.
- **Estimand** - hazard ratio (HR) with 95% confidence interval.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **Population** - adult HFmrEF/HFpEF or preserved-EF heart-failure population,
  judged from the title, registry conditions, or trial acronym.
- **Intervention** - Empagliflozin is named in the title or registry condition/acronym.
- **Comparator** - placebo or matching placebo.
- **Design** - randomized, double-blind, placebo-controlled trial.

Exclude (reason must be true of the record):
- **X1** - not a randomized controlled trial.
- **X2** - wrong population, including HFrEF/LVEF <=40%, diabetes-only, CKD-only,
  myocardial-infarction, or other non-HFmrEF/HFpEF populations.
- **X3** - wrong intervention or comparator.
- **X-DESIGN** - not double-blind/placebo-controlled in the machine-readable record.

Eligibility is not decided by outcome reporting. An eligible Empagliflozin HFpEF trial
that reports symptoms, hemodynamics, or safety but not the target composite HR is kept
as target-result absent, not excluded.

## Outcomes
- **Primary efficacy outcome** - composite cardiovascular death or worsening heart
  failure; HR estimand; intention-to-treat/randomized population; longest
  trial-reported randomized follow-up.
- **Secondary outcomes** - none preregistered for this topic.
- **Harms** - none preregistered for this topic.

## Search
- PubMed: UID-anchored queries for EMPEROR-Preserved (PMID 34449189), PRESERVED-HF
  (PMID 34711976), and CAMEO-DAPA (PMID 37534453), plus configured comparator and
  negative-control PMIDs.
- ClinicalTrials.gov: condition "heart failure with preserved ejection fraction",
  intervention "Empagliflozin".
- Citation chasing: enabled and bounded; every reached record is still screened by
  the same P/I/C/design rules.

## Synthesis method
Random-effects inverse-variance on log(HR) using source-reported trial HRs and 95%
CIs only. Paule-Mandel tau^2; HKSJ 95% CI on t(k-1) with variance floor
max(1, Q/(k-1)); prediction interval mu +/- t(k-1)*sqrt(tau^2 + se^2). For k=1,
the result is reported as the single trial's own HR with no random-effects pooling.

## Comparator
Pal et al., *Indian Heart Journal* 2023, "SGLT2 inhibitors and cardiovascular outcomes
in heart failure with mildly reduced and preserved ejection fraction: A systematic
review and meta-analysis" (PMID 36914068, DOI 10.1016/j.ihj.2023.03.003; Unpaywall
is_oa=true). This comparator matches the HFmrEF/HFpEF population, placebo comparison,
composite cardiovascular-death/HF-worsening outcome, and HR estimand, but is class-level
SGLT2 inhibitor evidence rather than Empagliflozin-only evidence; the overlap tab must
therefore not claim an identical trial set.

## Controls
- **Positive** - EMPEROR-Preserved (PMID 34449189) must be recovered and included.
- **Negative** - DAPA-HF (PMID 31535829), a Empagliflozin/placebo trial with the same
  endpoint but HFrEF/LVEF <=40%, must be recovered and excluded as wrong population.
