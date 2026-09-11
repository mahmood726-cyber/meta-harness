# Protocol - vitamin D for prevention of acute respiratory infection

**Registration.** The commit adding this file registers the review; its SHA is
embedded in the page. Committed before the synthesis runs.

## PICO
- **P** - general-population participants at risk of acute respiratory infection
  (children, adults, older adults, pregnancy/infancy cohorts, or other community
  populations), matched on title or registry conditions.
- **I** - vitamin D supplementation, including vitamin D3/cholecalciferol or
  vitamin D2/ergocalciferol.
- **C** - placebo, no active vitamin D, low-dose vitamin D, standard-dose vitamin D,
  or usual-control supplementation.
- **O (primary)** - at least one acute respiratory infection at trial end.
- **O (harms)** - hypercalcaemia; renal stones.

## Estimand / population / timepoint
- **Estimand** - odds ratio (OR), vitamin D vs placebo/control.
- **Population** - intention-to-treat as randomised.
- **Timepoint** - trial end or longest scheduled trial follow-up.

## Eligibility - on P/I/C/DESIGN ONLY
Include a record iff all hold:
- **I1** - randomised controlled trial;
- **I2** - title or registry conditions identify an acute respiratory infection,
  respiratory tract infection, upper respiratory infection, influenza, cold, or
  common-cold prevention population/question;
- **I3** - vitamin D supplementation is the randomised intervention by title or
  registry conditions;
- **I4** - placebo/control/low-dose/standard-dose comparison;
- **design** - randomised comparison; double-blinding is not required for this topic.

Exclude (reason must be true of the record):
- **X1** - not an RCT (review, guideline, observational study, protocol-only);
- **X2** - wrong population by title/conditions (for example COVID-19/SARS-CoV-2,
  tuberculosis, cystic fibrosis, sickle cell disease, osteoarthritis, knee pain,
  asthma, or post-COVID);
- **X3** - wrong intervention/comparison (no vitamin-D-vs-control contrast);
- **X5** - off-topic: a primary trial of another topic/disease in this set
  (negative control).

> Eligibility is NOT on the outcome axis. Whether an included trial reports
> at least one acute respiratory infection in an abstract-extractable form is
> recorded as target-result status at extraction, never as an exclusion. A
> published effect plus 95% CI is a poolable input.

## Search (fetch-once; raw results committed under cache/vitamin-d-acute-respiratory-infection/records.json; screening replays offline)
- PubMed: vitamin D x acute respiratory tract infection x randomised
  placebo/control trial query, plus targeted influenza/schoolchildren, VIDARIS,
  and older long-term-care searches to verify landmark trial recall.
- ClinicalTrials.gov: condition "acute respiratory infection", intervention
  "vitamin D".
- Comparator-reference seeding is enabled by the harness default to recover
  trials cited by the resolved IPD meta-analysis, then the same P/I/C/design
  rules screen them.

## Synthesis method (DECLARED = served)
Random-effects inverse-variance on log(OR); Paule-Mandel tau^2; HKSJ 95% CI on
`t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval
`mu +/- t_{k-1}*sqrt(tau^2+se^2)`. 0.5 continuity correction to all four cells
of a study only if it has a zero cell. DerSimonian-Laird forbidden. Engine
validated vs metafor 5.0.1 (<1e-6) for the same random-effects machinery.

## Comparator (resolved; open-access confirmed)
Martineau et al., *BMJ* 2017, "Vitamin D supplementation to prevent acute
respiratory tract infections: systematic review and meta-analysis of individual
participant data" (PMID 28202713, DOI 10.1136/bmj.i6583; PMCID PMC5310969;
Unpaywall is_oa=true). Its abstract reports 25 eligible RCTs, IPD for 10,933
participants, and adjusted OR 0.88 (95% CI 0.81-0.96) for acute respiratory
tract infection among all participants.

## Controls
- **Positive** - the search must recover and include Urashima seasonal influenza
  in schoolchildren (PMID 20219962), VIDARIS in healthy adults (PMID 23032549),
  and high-dose monthly vitamin D in older long-term-care residents
  (PMID 27861708).
- **Negative** - a vitamin D RCT in symptomatic knee osteoarthritis
  (PMID 23299607) must be recovered and excluded as the wrong population.
