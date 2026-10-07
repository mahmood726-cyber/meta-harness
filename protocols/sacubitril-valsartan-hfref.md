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

## Amendment 2026-10-05 -- identification sources (search+screen audit)

- **A1 REVIEW_REFERENCE_LIST (standing identification source).** Added: the comparator's (PMID 36722326) backward reference list (PubMed elink and Europe PMC) and its forward citations, and the backward reference lists of 1 other open meta-analysis (PMID 41773097; rule: most trial rows read by the secondary-meta lane, ties to the newer). Rationale: the registered search identified 2 of 2 of the comparator's eligible trials; with this route and the full retrieval below, 2 of 2 (2 of 2 without the comparator's own reference list, which contains its trials by construction). The route retrieves 70 records (recorded: outputs/search_audit/rrl_probe.json). Identification only: every record still passes the registered screen.
- **A2 ClinicalTrials.gov retrieval.** The registered query {"cond": "Heart Failure With Reduced Ejection Fraction", "intr": "LCZ696"} is unchanged. It returns 60 studies; the earlier retrieval kept the first 30 (a one-page cap in harness.fetch, now paginated with the source's own total recorded).
- **A3 Concept query added** (union with the registered queries; none removed): `("Heart Failure"[Mesh] OR "Ventricular Dysfunction, Left"[Mesh] OR "heart failure"[tiab] OR "cardiac failure"[tiab] OR HFrEF[tiab] OR "HF-rEF"[tiab] OR "HFREF"[tiab] OR "systolic dysfunction"[tiab] OR "reduced ejection fraction"[tiab] OR "impaired ejection fraction"[tiab] OR "left ventricular dysfunction"[tiab]) AND ("sacubitril and valsartan sodium hydrate drug combination"[Supplementary Concept] OR "sacubitril"[Supplementary Concept] OR sacubitril[tiab] OR "sacubitril/valsartan"[tiab] OR "sacubitril-valsartan"[tiab] OR "valsartan/sacubitril"[tiab] OR LCZ696[tiab] OR "LCZ 696"[tiab] OR "LCZ-696"[tiab] OR Entresto[tiab] OR Vymada[tiab] OR ARNI[tiab] OR ARNIs[tiab] OR "angiotensin receptor neprilysin inhibitor*"[tiab] OR "angiotensin receptor neprilysin inhibition"[tiab] OR "angiotensin-neprilysin inhibitor*"[tiab] OR "angiotensin-neprilysin inhibition"[tiab] OR (angiotensin[tiab] AND neprilysin[tiab] AND inhibit*[tiab])) AND (randomized controlled trial[pt] OR controlled clinical trial[pt] OR randomized[tiab] OR randomised[tiab] OR placebo[tiab] OR drug therapy[sh] OR randomly[tiab] OR trial[tiab] OR groups[tiab]) NOT (animals[mh] NOT humans[mh])`. Proposed blind (the proposer saw the PICO and the current queries with their volumes, never the comparator's trials or our misses; recorded call mc-a1ad5b7859b292e3d4532cba8a7c0d48.json); returns 2470 records today; on the comparator's eligible trials the registered queries match 1 of 2 and the union 2 of 2. Limitation: the proposer may know well-known trials from training.
