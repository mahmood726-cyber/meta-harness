# Citation-Chasing Reach Adapter Verification

Date: 2026-09-11

Scope: new adapter only, `harness/cites.py`. Comparator identifiers were read from
`docs/reviews/<slug>/review.json`.

Important source-status caveat: Europe PMC DOI/title search worked, but the Europe
PMC `MED/<pmid>/references` endpoint returned HTTP 503 for all four comparator PMIDs
during this run. Counts below therefore come from Crossref reference arrays plus
Europe PMC PMID resolution. This is a source error, not a zero-reference result.

## Counts

| Topic | Comparator PMID | Comparator DOI | Europe PMC refs | Crossref refs | Total refs fetched | Resolved to PMID | Unique PMIDs | Of-interest recovered |
|---|---:|---|---|---|---:|---:|---:|---:|
| omega3-cardiovascular-events | 35905212 | 10.1097/MD.0000000000029556 | RAN_ERROR: HTTP 503 | RAN_OK: 69 fetched, 66 resolved | 69 | 66 | 66 | 4/4 |
| colchicine-recurrent-pericarditis | 22442198 | 10.1136/heartjnl-2011-301306 | RAN_ERROR: HTTP 503 | RAN_OK: 17 fetched, 16 resolved | 17 | 16 | 16 | 2/2 |
| tranexamic-acid-pph | 39461793 | 10.1016/S0140-6736(24)02102-0 | RAN_ERROR: HTTP 503 | RAN_OK: 24 fetched, 22 resolved | 24 | 22 | 22 | 3/3 |
| probiotics-aad-prevention | 34385227 | 10.1136/bmjopen-2020-043054 | RAN_ERROR: HTTP 503 | RAN_OK: 74 fetched, 56 resolved | 74 | 56 | 56 | 9 registry-missed RCT citations recovered |

## Omega-3 Cardiovascular Events

Comparator: PMID 35905212.

| Trial | Recovered PMID | Title | Source |
|---|---:|---|---|
| DART | 2571009 | Effects of changes in fat, fish, and fibre intakes on death and myocardial reinfarction: diet and reinfarction trial (DART). | crossref |
| GISSI-Prevenzione | 10465168 | Dietary supplementation with n-3 polyunsaturated fatty acids and vitamin E after myocardial infarction: results of the GISSI-Prevenzione trial. Gruppo Italiano per lo Studio della Sopravvivenza nell'Infarto miocardico. | crossref |
| JELIS | 17398308 | Effects of eicosapentaenoic acid on major coronary events in hypercholesterolaemic patients (JELIS): a randomised open-label, blinded endpoint analysis. | crossref |
| GISSI-HF | 18757090 | Effect of n-3 polyunsaturated fatty acids in patients with chronic heart failure (the GISSI-HF trial): a randomised, double-blind, placebo-controlled trial. | crossref |

## Colchicine Recurrent Pericarditis

Comparator: PMID 22442198.

| Trial | Recovered PMID | Title | Source |
|---|---:|---|---|
| CORE | 16186468 | Colchicine as first-choice therapy for recurrent pericarditis: results of the CORE (COlchicine for REcurrent pericarditis) trial. | crossref |
| COPE | 16186437 | Colchicine in addition to conventional therapy for acute pericarditis: results of the COlchicine for acute PEricarditis (COPE) trial. | crossref |

## Tranexamic Acid PPH

Comparator: PMID 39461793.

| Trial | Recovered PMID | Title | Source |
|---|---:|---|---|
| WOMAN-2 | 39461792 | The effect of tranexamic acid on postpartum bleeding in women with moderate and severe anaemia (WOMAN-2): an international, randomised, double-blind, placebo-controlled trial. | crossref |
| TRAAP | 30134136 | Tranexamic Acid for the Prevention of Blood Loss after Vaginal Delivery. | crossref |
| TRAAP-2 | 33913639 | Tranexamic Acid for the Prevention of Blood Loss after Cesarean Delivery. | crossref |

## Probiotics AAD Prevention

Comparator: PMID 34385227.

Yes: citation chasing recovered large or multicentre registry-missed RCTs. The two
clearly large hits were PLACIDE (1493 intervention + 1488 placebo randomized in the
local abstract) and Ouwehand et al. (1127 randomized in the local abstract).

| Recovered PMID | Title | Source | Note |
|---:|---|---|---|
| 23932219 | Lactobacilli and bifidobacteria in the prevention of antibiotic-associated diarrhoea and Clostridium difficile diarrhoea in older inpatients (PLACIDE): a randomised, double-blind, placebo-controlled, multicentre trial. | crossref | Large, registry-missed |
| 32035998 | Do probiotics prevent antibiotic-associated diarrhoea? Results of a multicentre randomized placebo-controlled trial. | crossref | Large, registry-missed |
| 11560298 | Lack of effect of Lactobacillus GG on antibiotic-associated diarrhea: a randomized, placebo-controlled trial. | crossref | Registry-missed |
| 17356555 | Prevention of antibiotic-associated diarrhoea by a fermented probiotic milk drink. | crossref | Registry-missed |
| 18026577 | Effect of a fermented milk combining Lactobacillus acidophilus Cl1285 and Lactobacillus casei in the prevention of antibiotic-associated diarrhea: a randomized, double-blind, placebo-controlled trial. | crossref | Registry-missed |
| 21165295 | Effect of probiotic Lactobacillus (Lacidofil cap) for the prevention of antibiotic-associated diarrhea: a prospective, randomized, double-blind, multicenter study. | crossref | Registry-missed |
| 22472744 | Saccharomyces boulardii for the prevention of antibiotic-associated diarrhea in adult hospitalized patients: a single-center, randomized, double-blind, placebo-controlled trial. | crossref | Registry-missed |
| 24772726 | Randomised placebo-controlled double blind multicentric trial on efficacy and safety of Lactobacillus acidophilus LA-5 and Bifidobacterium BB-12 for prevention of antibiotic-associated diarrhoea. | crossref | Registry-missed |
| 7872284 | Prevention of beta-lactam-associated diarrhea by Saccharomyces boulardii compared with placebo. | crossref | Registry-missed |

Known registry-missed probiotic PMIDs 15740542, 18410562, and 18701826 were not
recovered from Crossref for this comparator DOI in this run. Because Europe PMC
references were unavailable with HTTP 503, I cannot honestly distinguish "not cited"
from "present only in the unavailable Europe PMC reference list."

## Commands Run

```powershell
python -m py_compile harness\cites.py
python -c "from harness.cites import cite_chase; print(callable(cite_chase))"
```

The live verification script called:

```python
from harness.cites import cite_chase_with_status
cite_chase_with_status(pmid=comparator["pmid"], doi=comparator["doi"])
```
