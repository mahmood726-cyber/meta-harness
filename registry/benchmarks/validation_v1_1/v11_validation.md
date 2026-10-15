# v1.1 fresh validation

Single-reader model source adjudication of abstracts, relevant methods/results, with focused follow-up. Manual judgments saved before automated comparisons; no tuning after sample draw. Not blinded to first-failure stratum; not a dual-human audit. C3 accuracy scores pass/fail for size separately from exact k. C2 uses semantic randomized design equivalents (including randomized controlled studies and placebo-controlled trials).

Seed: 20261016. Burned audit PMCID intersection: zero. Instrument hash: `b4c5c7c87d1ac3aeac57f65593221402ba85dec644c474870105122f24c3f1d2`.

| Criterion | Correct | Wrong | Total |
|---|---:|---:|---:|
| C3 | 22 | 8 | 30 |
| C2 | 14 | 6 | 20 |

C3 exact-count agreement is also recorded in JSON; decision agreement alone does not establish correct trial attribution.

## Wrong decisions

### C3 ? PMC10857255

Non-Immersive Virtual Reality-Based Therapy Applied in Cardiac Rehabilitation: A Systematic Review with Meta-Analysis.

Expected pass: True; instrument pass: False. Expected k: 9; parsed k: None.

Included randomized trial count read from abstract/results; outcome subsets are not the review total.

> Nine RCT that met the inclusion criteria were included in the meta-analysis. The meta-analysis showed a moderate-to-large effect favoring niVR active videogames included in CR in increasing aerobic capacity and cardiovascular endurance (SMD = 0.74; 95% CI 0.11 to 1.37; p = 0.021) and reducing anxiety (SMD = −0.66; 95% CI −1.13 to −0.2; p = 0.006). Only 4.8% 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10857255/)

### C3 ? PMC12641133

Evaluating safety and quality of robotic-assisted gastric cancer surgery: meta-analysis and meta-regression.

Expected pass: True; instrument pass: False. Expected k: 3; parsed k: None.

Included randomized trial count read from abstract/results; outcome subsets are not the review total.

> The studies encompassed three RCTs and 87 non-randomized studies, with publication dates ranging from 2009 to 2025. The majority of studies originated from China, with 72 studies conducted in East Asia and 17 in Europe and America; 7% of the studies were industry supported. Fig. 1 Flow chart of the systematic review Table 1 Characteristics of studies include

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12641133/)

### C3 ? PMC9780048

Treatment- and immune-related adverse events of immune checkpoint inhibitors in esophageal or gastroesophageal junction cancer: A network meta-analysis of randomized controlled trials.

Expected pass: True; instrument pass: False. Expected k: 11; parsed k: None.

Included randomized trial count read from abstract/results; outcome subsets are not the review total.

> Eleven RCTs involving EPC (five RCTs) and GEJC (six RCTs) were included in the final meta-analysis. NMA showed that placebo was associated with the best safety ranking for grade 3–5 trAEs (SUCRA = 96.0%), followed by avelumab (78.6%), nivolumab (73.9%), ipilimumab (57.0%), and pembrolizumab (56.6%). Conventional pairwise meta-analysis (CPM) showed that ICIs 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9780048/)

### C3 ? PMC11523819

Individual and organizational interventions to reduce burnout in resident physicians: a systematic review and meta-analysis.

Expected pass: True; instrument pass: False. Expected k: 11; parsed k: None.

Included randomized trial count read from abstract/results; outcome subsets are not the review total.

> Eleven (33.3%) studies were randomized, controlled, concurrent trials [ 45 , 51 , 52 , 55 , 57 , 60 – 64 , 74 ]. Outcome measurements were conducted using various versions of the validated MBI. Specifically, 26 studies (78.7%) used the 22-item MBI [ 44 , 45 , 47 – 49 , 51 , 52 , 54 , 56 , 58 , 60 – 65 , 67 , 68 , 70 – 76 ], 5 studies (15.2%) employed the 9-i

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11523819/)

### C3 ? PMC10243628

Efficacy of nitrous oxide in adults undergoing puncture biopsy: A systematic review and meta-analysis of randomized controlled trials.

Expected pass: True; instrument pass: False. Expected k: 12; parsed k: None.

Review includes 12 RCTs; 11 pooled after one incompatible outcome exclusion. Review included count takes precedence.

> Twelve RCTs with 1070 patients were included in the qualitative review, of which eleven RCTs were included in the meta-analysis. Pooled analysis suggested that compared with the controls (placebo, lidocaine and midazolam), N 2 O had better analgesic effect (MD -1.12, 95% CI -2.12 to -0.13, P = 0.03; I 2 = 94%). In addition, N 2 O significantly alleviated pat

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10243628/)

### C3 ? PMC10511686

Microbiota signatures and mucosal healing in the use of enteral nutrition therapy &lt;i&gt;v&lt;/i&gt;. corticosteroids for the treatment of children with Crohn's disease: a systematic review and meta-analysis.

Expected pass: True; instrument pass: False. Expected k: 3; parsed k: None.

Included randomized trial count read from abstract/results; outcome subsets are not the review total.

> Three RCT ( n 76) and sixteen cohort studies ( n 1104) compared EEN v . CS. With limited available data (one RCT), the effect on intestinal microbiome indicated a trend towards EEN regarding Shannon diversity. Based on two RCT, EEN achieved higher mucosal healing than CS (risk ratio (RR) 2·36, 95 % CI (1·22, 4·57), low certainty). Compared with CS, patients 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10511686/)

### C3 ? PMC10366781

A Systematic Review and Meta-Analysis of Exercise Beneficial for Locomotion in Community-Dwelling Elderly People with Sarcopenia.

Expected pass: True; instrument pass: False. Expected k: 10; parsed k: 2.

Ten eligible papers are the RCTs of this RCT-only review; no duplicate-trial reporting identified.

> Finally, ten papers were deemed eligible and included in our systematic review and meta-analysis [ 12 , 13 , 14 , 15 , 16 , 17 , 18 , 19 , 20 , 21 ]. Figure 1 Preferred Reporting Items for Systematic Reviews and Meta-Analysis (PRISMA) flow diagram. 3.2. Risk of Bias Assessment In our systematic review, a rigorous assessment of the risk of bias was conducted 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10366781/)

### C3 ? PMC12710616

Vitamin D supplementation for tuberculosis prevention: A meta-analysis.

Expected pass: True; instrument pass: False. Expected k: 6; parsed k: None.

Included randomized trial count read from abstract/results; outcome subsets are not the review total.

> Six RCTs, involving 15,677 participants, met our inclusion criteria. Compared to placebo, vitamin D supplementation did not significantly reduce the risk of tuberculosis infection (5 RCTs; OR: 0.95; 95% CI: 0.79–1.14; P ═ 0.55) or the development of active tuberculosis (4 RCTs; OR: 0.77; 95% CI: 0.56–1.05; P ═ 0.10). The certainty of evidence was moderate fo

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12710616/)

### C2 ? PMC10335801

New anti-diabetic agents for the treatment of non-alcoholic fatty liver disease: a systematic review and network meta-analysis of randomized controlled trials.

Expected pass: True; instrument pass: False. Expected k: None; parsed k: None.

Pairwise MA is explicit; acronym refers to meta-analysis, not an NMA-only review.

> A pairwise MA, stratified by presence or absence of T2DM, was performed if at least 3 studies compared outcomes between the same treatment pair. Treatment effects (i.e., unstandardized mean difference (USMD) for continuous outcomes and risk ratio (RR) for dichotomous outcomes) were estimated and pooled across studies using a random-effect model if heterogene

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC10335801/)

### C2 ? PMC8121296

The safety of nintedanib for the treatment of interstitial lung disease: A systematic review and meta-analysis of randomized controlled trials.

Expected pass: True; instrument pass: False. Expected k: None; parsed k: None.

Randomized controlled studies is semantically randomized trial design; title and methods corroborate. Under a strictly literal trials-only abstract reading this would instead fail.

> randomized controlled studies which compared nintedanib with a placebo in ILD patients. We estimated pooled odds ratios (ORs) and 95% confidence intervals (CIs) for adverse events using the DerSimonian–Laird random-effects model. Results Six studies with a total of 2,583 patients were included in the meta-analysis. The pooled estimates showed that patients t

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC8121296/)

### C2 ? PMC9648643

Is the injection of tramadol effective at control of pain after impacted mandibular third molar extractions? A systematic review and meta-analysis.

Expected pass: True; instrument pass: False. Expected k: None; parsed k: None.

Randomized placebo-controlled trials explicitly qualify; pairwise synthesis is stated.

> three randomized placebo-controlled trials were considered for analysis. The submucosal injection of 2 ml of tramadol adjacent to the impacted mandibular third molar was effective in controlling pain up to 6-hours after surgery, in increasing the onset of consumption of rescue analgesic and in reducing the total number of rescue analgesics used. Conclusions 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9648643/)

### C2 ? PMC12932438

Efficacy and safety of traditional Chinese classic prescriptions combined with metformin in the treatment of type 2 diabetes mellitus: a Bayesian network meta-analysis.

Expected pass: False; instrument pass: True. Expected k: None; parsed k: None.

NMA-only.

> The Bayesian NMA was performed using the gemtc package in R. We employed non-informative (vague) prior distributions (Normal distribution N (0, 10,000) for effects; Uniform distribution U (0, 5) for heterogeneity) to minimize the influence of initial assumptions. The simulation was set up with four chains, 50,000 iterations per chain, a thinning interval of 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12932438/)

### C2 ? PMC11551482

Fiber intake and fiber intervention in depression and anxiety: a systematic review and meta-analysis of observational studies and randomized controlled trials.

Expected pass: True; instrument pass: False. Expected k: None; parsed k: None.

Separate RCT-vs-placebo pooling is explicit despite observational component.

> we conducted separate meta-analyses by study design (cross-sectional, longitudinal, case-control, and RCTs), using a random-effects model to account for heterogeneity between studies. Heterogeneity was assessed using the I 2 statistic, and an I 2 value greater than 75% was considered substantial heterogeneity. Forest plots were used to visualize the ESs and 

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11551482/)

### C2 ? PMC11523550

Steroid versus placebo injections and wrist splints in patients with carpal tunnel syndrome: a systematic review and network meta-analysis.

Expected pass: True; instrument pass: False. Expected k: None; parsed k: None.

Despite network title, methods report random-effects direct group comparisons; network consists of direct steroid/placebo and steroid/splint comparisons.

> Direct comparisons between the mean score change from the baseline of each treatment group to the follow-up period of interest were quantified through calculation of a mean difference and 95% confidence interval (CI). Mean differences were deemed statistically significant when p < 0.05. Results Our search identified 1265 articles: 393 from EMBASE; 266 from P

[Cached source article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11523550/)

## All adjudications

| Criterion | PMCID | Expected pass | Instrument pass | Expected k | Parsed k | Correct |
|---|---|---|---|---|---|---|
| C3 | PMC10857255 | True | False | 9 | None | False |
| C3 | PMC10511851 | False | False | None | None | True |
| C3 | PMC11771208 | True | True | 6 | 6 | True |
| C3 | PMC13109977 | True | True | 12 | 12 | True |
| C3 | PMC12641133 | True | False | 3 | None | False |
| C3 | PMC11427380 | False | False | 43 | None | True |
| C3 | PMC9780048 | True | False | 11 | None | False |
| C3 | PMC12300382 | True | True | 20 | 20 | True |
| C3 | PMC11523819 | True | False | 11 | None | False |
| C3 | PMC10243628 | True | False | 12 | None | False |
| C3 | PMC12857311 | True | True | 5 | 5 | True |
| C3 | PMC8478134 | True | True | 3 | 3 | True |
| C3 | PMC11798776 | False | False | None | None | True |
| C3 | PMC7341582 | True | True | 5 | 5 | True |
| C3 | PMC10511686 | True | False | 3 | None | False |
| C3 | PMC8134489 | True | True | 23 | 23 | True |
| C3 | PMC13328200 | True | True | 12 | 12 | True |
| C3 | PMC8758048 | False | False | None | None | True |
| C3 | PMC7306356 | False | False | None | None | True |
| C3 | PMC11061932 | True | True | 3 | 3 | True |
| C3 | PMC7512096 | False | False | 26 | None | True |
| C3 | PMC11285646 | True | True | 18 | 18 | True |
| C3 | PMC11730037 | True | True | 3 | 3 | True |
| C3 | PMC11757114 | True | True | 18 | 18 | True |
| C3 | PMC7558106 | True | True | 3 | 3 | True |
| C3 | PMC11412939 | False | False | None | None | True |
| C3 | PMC7231184 | True | True | 12 | 12 | True |
| C3 | PMC10366781 | True | False | 10 | 2 | False |
| C3 | PMC12053702 | True | True | 9 | 8 | True |
| C3 | PMC12710616 | True | False | 6 | None | False |
| C2 | PMC9064104 | False | False |  |  | True |
| C2 | PMC9369741 | True | True |  |  | True |
| C2 | PMC8026036 | False | False |  |  | True |
| C2 | PMC8668341 | False | False |  |  | True |
| C2 | PMC10335801 | True | False |  |  | False |
| C2 | PMC12527846 | False | False |  |  | True |
| C2 | PMC9410833 | True | True |  |  | True |
| C2 | PMC8121296 | True | False |  |  | False |
| C2 | PMC11879820 | False | False |  |  | True |
| C2 | PMC12256550 | False | False |  |  | True |
| C2 | PMC10795175 | False | False |  |  | True |
| C2 | PMC9648643 | True | False |  |  | False |
| C2 | PMC12272586 | False | False |  |  | True |
| C2 | PMC12932438 | False | True |  |  | False |
| C2 | PMC13617617 | False | False |  |  | True |
| C2 | PMC12313559 | False | False |  |  | True |
| C2 | PMC12718627 | False | False |  |  | True |
| C2 | PMC11551482 | True | False |  |  | False |
| C2 | PMC11523550 | True | False |  |  | False |
| C2 | PMC11660011 | False | False |  |  | True |

## Static versus dynamic disclosure

| Item | Type |
|---|---|
| seed, stratum sizes, rules | static/user specified |
| sample, hashes, parser predictions, summaries | dynamic/computed |
| gold decisions and quote anchors | manual source-backed annotations; not generated from parser decisions |

C2 wording sensitivity: under a strictly literal trials-only abstract rule, rejecting ?randomized controlled studies? yields 15 correct / 5 wrong instead of 14 / 6. The primary adjudication treats that phrase as an equivalent randomized design.
