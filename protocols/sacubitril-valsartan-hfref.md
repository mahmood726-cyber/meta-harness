# Protocol - sacubitril/valsartan for cardiovascular death or heart-failure hospitalization in HFrEF

**Registration.** The commit that adds/updates this file is the registration of this
review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab.
Committed BEFORE the synthesis is run.

## PICO
- **P** - adults with heart failure with reduced ejection fraction (HFrEF).
- **I** - sacubitril/valsartan, also reported as sacubitril, LCZ696, or ARNI.
- **C** - an ACE inhibitor or ARB active comparator, usually enalapril; ramipril is also eligible where used as the active renin-angiotensin-system comparator.
- **O (primary)** - composite cardiovascular death or heart-failure hospitalization.
- **O (secondary)** - cardiovascular death; heart-failure hospitalization.
- **O (harms)** - hypotension; hyperkalemia.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff **all** hold:
- **P** - adult HFrEF / reduced-ejection-fraction heart-failure population, judged from title or registry conditions.
- **I** - sacubitril/valsartan, sacubitril, LCZ696, ARNI, or a title-level angiotensin-neprilysin-inhibition phrase.
- **C** - enalapril, ACE inhibitor, ARB, ramipril, or another explicit RAS-inhibitor active comparator. Standalone valsartan text inside sacubitril/valsartan does not satisfy this criterion.
- **Design** - randomized, double-blind active-controlled trial.

Eligibility is not on the outcome axis. Whether an included trial reports the primary
composite, or gives a 2x2 table versus only an effect plus CI, is recorded as target-result
status at extraction and is never an exclusion.

## Outcomes
- **Primary** - composite cardiovascular death or heart-failure hospitalization, estimand HR, intention-to-treat population, trial end / longest randomized follow-up.
- **Secondary** - cardiovascular death; heart-failure hospitalization, estimand HR where reported.
- **Harms** - hypotension; hyperkalemia, estimand RR when arm-level counts are extractable.

## Analysis Method
Random-effects inverse-variance on the configured log ratio scale; for the primary outcome
this is log(HR) when an abstract-reported HR with 95% CI is machine-extractable. Paule-Mandel
tau^2; HKSJ 95% CI on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. If only one trial reports the outcome, the estimate is
reported as that trial's own effect, with no tau^2, HKSJ interval, or prediction interval.

## Comparator
Ji et al., *ESC Heart Failure* 2023, "The cardiovascular effects of SGLT2 inhibitors,
RAS inhibitors, and ARN inhibitors in heart failure" (PMID 36722326, DOI
10.1002/ehf2.14298; open access with PMC10053170 available). The comparator is a published
network meta-analysis of randomized trials and reports the assigned HFrEF composite endpoint
for ARNI versus RAS inhibitors as RR 0.83 (95% CI 0.77-0.89).
