# Preregistered PICO set (committed before any run)

The machine-readable list is [`pico.json`](pico.json) — **24 topics**. Committing
this file is the registration of the *set*: it prevents choosing topics after
seeing results. Each topic additionally gets its own `protocols/<id>.md`, committed
at the moment its search starts; **that per-topic commit SHA is the per-topic
registration** and is embedded in the page's Protocol tab.

## Why comparators are queries, not typed PMIDs
A hand-typed PMID risks a fabricated citation (a known failure mode). Each topic
pins its comparator by a **deterministic resolution query**; the harness resolves
the actual open-access systematic-review/meta-analysis, records its PMID/DOI, and
the **two-limb gate refuses** any page whose comparator is missing, non-open-access,
or lacks a stated trial-set overlap. The comparator is pinned *by identity of the
question* now, so it cannot be swapped for a flattering one after results are seen.

## Difficulty tiers (we deliberately include ones we expect to lose to)
| Tier | Meaning | Topics |
|---|---|---|
| EASY | small k, clean pairwise | colchicine-recurrent-pericarditis, colchicine-postop-af, zinc-common-cold-duration, melatonin-primary-insomnia-sol, metformin-pcos-ovulation |
| MODERATE | 5-15 trials, pairwise | corticosteroids-cap-mortality, azithromycin-copd-exacerbation, sglt2-hfref-hosp-cvdeath, iv-iron-hfref-hosp, finerenone-ckd-t2d-renal, colchicine-secondary-cv-prevention, prone-positioning-ards-mortality, tranexamic-acid-pph, statins-primary-prevention-elderly |
| LARGE_K | many trials | probiotics-aad-prevention, glp1-ra-mace-t2d, balanced-crystalloids-vs-saline-mortality, omega3-cardiovascular-events |
| IPD | comparator uses individual participant / prospective pooled data (we expect to lose) | corticosteroids-covid19-mortality, tocilizumab-covid19-mortality, vitamin-d-acute-respiratory-infection |
| NMA | comparator is a network meta-analysis (we expect to lose) | noac-vs-warfarin-af-stroke, hfnc-vs-conventional-o2-reintubation, antibiotics-vs-appendectomy-appendicitis |

## Controls
- **Positive** (per topic): the offline screen must recover every trial the resolved
  comparator includes; any miss is reported on the page, not hidden.
- **Negative** (per topic, from another topic): the primary trials of any *other*
  topic in this list must screen to EXCLUDE with an explicit rule id.

## Default method
Binary outcomes: pool `log(RR)` with **Paule-Mandel** random-effects `tau^2`; **HKSJ**
CI using `t_{k-1}` with variance floored at `max(1, Q/(k-1))`; prediction interval
`mu ± t_{k-1}·sqrt(tau2+se^2)`. **DerSimonian-Laird is forbidden for k<10.** Each
topic's protocol declares its method explicitly, and the served method must equal it
(gate limb 1). Continuous/HR/OR estimands follow the same discipline on their scale.
