# GI safety-outcome taxonomy: corpus re-binding

**9 of 520 harms rows re-bound corpus-wide** (55 of them are served under a GI taxonomy outcome; 30 pages carry harms).

Outcomes: GI_ANY (unique-patient total required), DIARRHOEA, GI_HOSPITALISATION, GI_DISCONTINUATION. Every result is bound by its source label to exactly one; percentages alone are RECONSTRUCTED candidates, never pooled.

| transition | n |
|---|---|
| GI_ANY/REFUSED -> GI_ANY/RECONSTRUCTED | 5 |
| GI_ANY/REFUSED -> DIARRHOEA/RECONSTRUCTED | 2 |
| GI_ANY/REFUSED -> DIARRHOEA/ADMISSIBLE | 1 |
| GI_ANY/INCLUDED -> DIARRHOEA/ADMISSIBLE | 1 |

Limits: ADMISSIBLE here means the result binds to its outcome with exact counts or an effect+CI; whether an OR can pool with an RR is still the pool gate's decision. Counts printed as 'n (x%)' take their arm denominators from the served row. Only GI harms are in the taxonomy; the other harm rows are counted in N and left as served. LoDoCo2's GI-hospitalisation result is not in any held source, so it cannot re-bind until the source is held (the plant uses a labelled fixture).

## Notices (served changes; none applied here)

| page | served outcome | trial | before | after | status | source label |
|---|---|---|---|---|---|---|
| colchicine-postop-af | Gastrointestinal adverse effects | 42132185 | REFUSED | GI_ANY | RECONSTRUCTED | Gastrointestinal events, primarily diarrhea, were more common with colchicine (25.9% vs. 8.5%, p = 0.003) |
| colchicine-postop-af | Gastrointestinal adverse effects | 36286314 | REFUSED | DIARRHOEA | ADMISSIBLE | the incidence of diarrhea in the colchicine group was 25.7% vs. 11.8% in the placebo group (OR 2.578 |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 34876021 | INCLUDED | DIARRHOEA | ADMISSIBLE | In colchicine group, it was found that at the end of the enrollment, 15 (12.5%) patients had a history of gastrointestinal adverse effects c |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 31733140 | REFUSED | DIARRHOEA | RECONSTRUCTED | Diarrhea was reported in 9.7% of the patients in the colchicine group and in 8.9% of those in the placebo group (P = 0.35). |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 34420373 | REFUSED | GI_ANY | RECONSTRUCTED | The incidence of gastrointestinal adverse events during the treatment period was greater with colchicine than with placebo (34% versus 11%,  |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 32862667 | REFUSED | GI_ANY | RECONSTRUCTED | they were predominantly gastrointestinal symptoms (colchicine, 23.0% versus placebo, 20.8%). |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 32295417 | REFUSED | GI_ANY | RECONSTRUCTED | gastrointestinal symptoms (6.3%), which occurred more frequently in the colchicine (9.3%) versus placebo (3.2%) group. |
| colchicine-secondary-cv-prevention | Gastrointestinal adverse effects | 39555823 | REFUSED | DIARRHOEA | RECONSTRUCTED | Diarrhea occurred in a higher percentage of patients with colchicine than with placebo (10.2% vs. 6.6% |
| semaglutide-obesity-weight | Gastrointestinal adverse events | 33625476 | REFUSED | GI_ANY | RECONSTRUCTED | Gastrointestinal adverse events were more frequent with semaglutide (82.8%) vs placebo (63.2%). |

## Harms-only RoB check: 13 harms-only contributions lack an outcome-specific RoB entry

| page | trial | outcome | flag |
|---|---|---|---|
| colchicine-secondary-cv-prevention | 34876021 | Gastrointestinal adverse effects | HARMS_ONLY_NO_ROB_ENTRY |
| corticosteroids-cap-mortality | 21636122 | Hyperglycaemia | HARMS_ONLY_NO_ROB_ENTRY |
| corticosteroids-cap-mortality | 25608756 | Hyperglycaemia | HARMS_ONLY_NO_ROB_ENTRY |
| corticosteroids-cap-mortality | 33446608 | Hyperglycaemia | HARMS_ONLY_NO_ROB_ENTRY |
| corticosteroids-covid19-mortality | 34138478 | Serious adverse events | HARMS_ONLY_NO_ROB_ENTRY |
| dapagliflozin-hfpef-hosp | 34711976 | Adverse events | HARMS_ONLY_NO_ROB_ENTRY |
| dpp4-mace-t2d | 26052984 | Hospitalization for heart failure | HARMS_ONLY_NO_ROB_ENTRY |
| omega3-cardiovascular-events | 30146932 | Atrial fibrillation | HARMS_ONLY_ROB_NOT_OUTCOME_SPECIFIC |
| probiotics-aad-prevention | 34541475 | Serious adverse events | HARMS_ONLY_ROB_NOT_OUTCOME_SPECIFIC |
| probiotics-aad-prevention | 39529939 | Any adverse events | HARMS_ONLY_ROB_NOT_OUTCOME_SPECIFIC |
| probiotics-aad-prevention | 41699149 | Any adverse events | HARMS_ONLY_NO_ROB_ENTRY |
| tocilizumab-covid19-mortality | 33332779 | Serious adverse events | HARMS_ONLY_NO_ROB_ENTRY |
| tocilizumab-covid19-mortality | 33631066 | Serious adverse events | HARMS_ONLY_NO_ROB_ENTRY |
