# Preregistration — expansion tier (batch, committed before any of it runs)

Registered as one batch on 2026-09-12. The commit that adds this file is the registration timestamp for
every topic below; **no topic here has been fetched, screened, or synthesised at registration time.** Each
will be built by a single end-to-end lane (protocol → registry-first fetch → dual screen → extract down the
source ladder → synth → two-limb gate → live → parity → blind judge). **A topic that cannot meet the bar is
declined and recorded with its reason — that still counts as output.** The bar is unchanged: every pooled
number verified to a committed source span, refuse on ambiguity, every decline named, gate-enforced,
byte-reproducible.

## Deliberate selection criteria (using what the audit measured works)
- **Prefer LARGER evidence bases (8–40 eligible trials)** — the direct answer to "21 of 29 at k≤2"; larger
  pools are informative and make the parity comparison meaningful.
- Clean **binary or time-to-event** primary outcomes with **registered trials and posted results**.
- Continuous topics only where the literature reports **raw per-arm mean±SD** (most report LSM±SE → decline).
- **Include hard ones on purpose** — declared below — so the tier is not stacked to win.

## Expansion topics

### Larger evidence base (expected k ≥ 5), clean binary/TTE
1. **dpp4-mace-t2d** — In adults with T2D, do DPP-4 inhibitors vs placebo change 3-point MACE? cond=type 2
   diabetes, intr=DPP-4 inhibitor (sitagliptin/saxagliptin/alogliptin/linagliptin). Estimand HR. Pivotal
   TECOS (NCT00790205). CVOTs: SAVOR-TIMI 53, EXAMINE, TECOS, CARMELINA, CAROLINA (~5, all posted). Comparator: a DPP-4 CVOT meta.
2. **sglt2-primary-prevention-hf** — In T2D/at-risk adults, do SGLT2 inhibitors vs placebo reduce heart-
   failure hospitalization? cond=type 2 diabetes, intr=SGLT2 inhibitor. Estimand HR. Pivotal DECLARE-TIMI 58
   (NCT01730534). EMPA-REG, CANVAS, DECLARE, VERTIS-CV (~4–5, posted). Comparator: SGLT2 CVOT HF meta.
3. **ics-copd-exacerbation** — In COPD, do inhaled corticosteroids vs non-ICS reduce moderate-to-severe
   exacerbations? cond=COPD, intr=inhaled corticosteroid. Estimand RR/rate ratio. Pivotal TORCH
   (NCT00268216). Many RCTs (≥10). DELIBERATE HARD: exacerbation definitions and ICS-vs-LABA vs ICS-vs-placebo
   comparators vary → expect scope/definition declines.
4. **statin-secondary-prevention-mace** — In established CVD, do statins vs placebo/less-intensive reduce
   major vascular events? cond=cardiovascular disease, intr=statin. Estimand RR. Pivotal 4S / CTT-class.
   Many (≥10) but several PRE-REGISTRATION era → DELIBERATE REACH-HARD.
5. **doac-vte-recurrence** — In acute VTE, do DOACs vs warfarin change recurrent VTE? cond=venous
   thromboembolism, intr=DOAC (rivaroxaban/apixaban/dabigatran/edoxaban). Estimand RR/HR. Pivotal EINSTEIN-PE
   (NCT00439777). RE-COVER, EINSTEIN, AMPLIFY, Hokusai (~5–6, posted).
6. **ppi-stress-ulcer-icu** — In critically ill adults, do PPIs vs placebo/H2RA change clinically important GI
   bleeding? cond=critical illness, intr=proton pump inhibitor. Estimand RR. Pivotal SUP-ICU (NCT02467621).
   Several large ICU RCTs (≥6, posted). DELIBERATE: mortality vs bleeding endpoint care.
7. **thrombectomy-acute-stroke-outcome** — In acute ischemic stroke with large-vessel occlusion, does
   endovascular thrombectomy vs medical care change functional independence (mRS 0–2)? cond=ischemic stroke,
   intr=thrombectomy. Estimand RR/OR. Pivotal MR CLEAN (NCT01804634). MR CLEAN/ESCAPE/SWIFT-PRIME/EXTEND-IA/
   REVASCAT (~5+, HERMES set).

### Deliberate hard / expected declines or losses (registered in advance so the tier is honest)
8. **aspirin-primary-prevention-mace** — In adults without CVD, does aspirin vs placebo change MACE?
   cond=cardiovascular disease prevention, intr=aspirin. Estimand HR/RR. ASPREE/ARRIVE/ASCEND (~3–4 recent,
   posted). DELIBERATE near-null with a bleeding-harm counterweight; expect a null primary.
9. **beta-blocker-post-mi-mortality** — After acute MI, do beta-blockers vs placebo reduce mortality?
   cond=myocardial infarction, intr=beta blocker. Estimand RR. Classic (BHAT, ISIS-1, many) but PRE-
   REGISTRATION era → DELIBERATE REACH-HARD (registry-first will miss most; citation-chasing tested; likely a
   named reach gap, not a win).
10. **ace-inhibitor-hfref-mortality** — In HFrEF, do ACE inhibitors vs placebo reduce mortality? cond=heart
    failure, intr=ACE inhibitor. Estimand RR/HR. SOLVD-Treatment, CONSENSUS (old) → DELIBERATE REACH-HARD.
11. **tirzepatide-obesity-weight** — In obesity without diabetes, how much more does tirzepatide vs placebo
    reduce body weight at the primary timepoint? cond=obesity, intr=tirzepatide. Estimand MD (%).
    SURMOUNT-1..4. DELIBERATE CONTINUOUS-HARD: results are typically LSM±SE (ANCOVA) → expect a decline unless
    raw per-arm mean±SD is posted.
12. **canagliflozin-amputation-harm** — In T2D, does canagliflozin vs placebo increase lower-limb amputation?
    cond=type 2 diabetes, intr=canagliflozin. Estimand HR/RR. CANVAS/CREDENCE. DELIBERATE HARMS topic (harms
    rows are our least-scrutinised class) — small counts, expect wide CIs.

### Moderate evidence base
13. **remdesivir-covid19-mortality** — In hospitalized COVID-19, does remdesivir vs control change 28-day
    mortality? cond=COVID-19, intr=remdesivir. Estimand RR. ACTT-1, SOLIDARITY, WHO, DisCoVeRy (~4–5, posted).
14. **intensive-bp-control-mace** — Does intensive vs standard blood-pressure control change MACE?
    cond=hypertension, intr=intensive blood pressure control. Estimand HR. SPRINT (NCT01206062), ACCORD-BP,
    STEP (~3–4 large). DELIBERATE: population/target heterogeneity.
15. **vitamin-d-fracture** — Does vitamin D vs placebo change fractures in community-dwelling adults?
    cond=fracture, intr=vitamin D. Estimand RR. VITAL, D-Health, many (≥8). DELIBERATE near-null; dose/
    co-calcium heterogeneity → expect definition declines.

## Execution note
Built one lane per topic; fetch is **serialised** (a throttled 429 degrades the cache — never run fetch-heavy
lanes in parallel). Offline steps (screen/extract/synth/gate) parallelise. Each build is verified against
source before it is counted live (a generated config is a hypothesis, not a specification — the standing
verify-before-build rule). Declines are recorded here with their reason as they are determined.
