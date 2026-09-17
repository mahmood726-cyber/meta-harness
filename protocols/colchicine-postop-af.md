# Protocol — colchicine for prevention of postoperative atrial fibrillation

**Registration.** The commit adding/updating this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs. Same machinery as topic 1.

## PICO
- **P** — adults undergoing cardiac (cardiothoracic) surgery.
- **I** — colchicine (peri-operative), added to usual care.
- **C** — placebo / usual care.
- **O (primary)** — postoperative atrial fibrillation (POAF).
- **O (harms)** — gastrointestinal adverse effects; treatment discontinuation.

## Estimand / population / timepoint
- RR of POAF, intention-to-treat, in-hospital / index-admission follow-up.

## Eligibility — P/I/C/DESIGN only
- **I1** RCT; **I2** cardiac-surgery population with POAF as an outcome; **I3** colchicine vs
  placebo/usual care; **design** double-blind OR placebo-controlled RCT.
- Exclude: **X1** not RCT; **X2** wrong population (ablation/pulmonary-vein-isolation AF,
  pericarditis, coronary-disease AF); **X3** no colchicine-vs-control contrast; **X5** off-topic
  (a primary trial of another topic in this set — negative control).
- Eligibility is NOT on the outcome axis; a published effect+CI is a poolable input.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(RR); Paule-Mandel τ²; HKSJ 95% CI on t_{k-1}
(floor max(1,Q/(k-1))); PI μ ± t_{k-1}·√(τ²+se²). DerSimonian-Laird forbidden. metafor-validated.
(Note: the comparator used DerSimonian-Laird; we report theirs as published and pool ours under the declared method.)

## Comparator (resolved; OA confirmed)
Zhao et al., *J Cardiothorac Surg* 2022, "A meta-analysis of colchicine in prevention of atrial
fibrillation following cardiothoracic surgery or cardiac intervention" (PMID 36050741,
PMC9438305, DOI 10.1186/s13019-022-01958-9; open access). Reports POAF RR 0.62 (0.52–0.74) over 9 RCTs.

## Controls
- **Positive** — the search recovers the colchicine-vs-placebo cardiac-surgery POAF RCTs the comparator pools.
- **Negative** — CORP (colchicine for recurrent pericarditis, PMID 21873705 — another topic in this set)
  must be recovered and EXCLUDED (wrong population).

## Retrospective executable-screen amendment (2026-09-16)
`PROTOCOL_CONFIG_DIVERGENCE`: known-answer screening audit SC found that the
cardiac-surgery population vocabulary missed "myocardial revascularization"
language in Zarpelon PMID 27223641. The config now treats myocardial
revascularization/revascularisation surgery as cardiac-surgery vocabulary and
accepts its randomized "control group" wording as the usual-care control. This
amendment changes screening only and does not make dose/timing-ambiguous or
multi-arm outcome data poolable.
