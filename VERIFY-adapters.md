# VERIFY Adapters

Date: 2026-09-11

Scope: live reach-adapter probes only. I did not run `build_topic`, did not edit existing
`harness/*.py`, did not mutate caches, and did not commit.

## Source Posture

| Source | Access used by adapter | Completeness posture |
|---|---|---|
| openFDA drug label | `https://api.fda.gov/drug/label.json` JSON API | Good for current FDA labels and label-posted clinical-study/outcome sections; not a trial registry. |
| Drugs@FDA via openFDA | `https://api.fda.gov/drug/drugsfda.json` JSON API with application document URLs | Good for FDA approval/effectiveness documents where openFDA exposes them; not expected to contain non-FDA diet/supplement trials. |
| ISRCTN | `https://www.isrctn.com/api/query/format/who` XML API | Open API; parsed directly. |
| EU-CTR | `https://www.clinicaltrialsregister.eu/ctr-search/search?query=...` public HTML | No stable JSON API used; parsed as best-effort HTML. |
| ICTRP | `https://trialsearch.who.int/?q=...` public HTML | WHO documents a web service/crawling route, but not as an unauthenticated open endpoint for this harness; public HTML probe only. |

## Static vs Dynamic Disclosure

| Item | Static or dynamic | Disclosure |
|---|---|---|
| Adapter endpoint roots | Static | Hardcoded public endpoint roots only; no secrets or local paths. |
| Query variants | Static transform | US/UK spellings for haemorrhage/hemorrhage, postpartum/post-partum, and caesarean/cesarean are generated in code. |
| Trial records below | Dynamic | Retrieved live on 2026-09-11; reruns may differ if registries update. |
| Negative findings | Dynamic | "0" means no record was returned by the probed source/query on 2026-09-11, not proof the trial does not exist. |

## omega3-cardiovascular-events

### FDA / openFDA

Probe: `fda_trials("Vascepa")` and `fda_trials("icosapent ethyl")`.

Reached:

| Source | ID | Title | URL |
|---|---|---|---|
| openFDA label | NCT01492361 | REDUCE-IT: Prevention of Cardiovascular Events | https://api.fda.gov/drug/label.json?search=id%3A%2286b35fe3-d1cf-478e-849b-2ea0c87bda33%22&limit=1 |
| Drugs@FDA | NDA202057-SUPPL35-61277 | Drugs@FDA Label for NDA202057 SUPPL35 | http://www.accessdata.fda.gov/drugsatfda_docs/label/2019/202057s035lbl.pdf |
| Drugs@FDA | NDA202057-ORIG1-43379 | Drugs@FDA Review for NDA202057 ORIG1 | http://www.accessdata.fda.gov/drugsatfda_docs/nda/2012/202057_vascepa_toc.html |

Outcome data observed in the openFDA label: the REDUCE-IT clinical-study section reports the
cardiovascular-outcomes table. The primary composite endpoint row reports 705/4089 on Vascepa
vs 901/4090 on placebo, HR 0.75 (95% CI 0.68 to 0.83), in the source URL above.

Not reached by FDA: DART, GISSI-P/GISSI Prevenzione, JELIS, and GISSI-HF. This is expected:
these are old/non-FDA omega-3 cardiovascular outcome trials, not Vascepa approval-label trials.

### Registries

Probe: `registry_multi_with_status("cardiovascular events", "icosapent ethyl")`.

Status returned:

| Registry | Status | Count |
|---|---:|---:|
| ISRCTN | RAN_OK | 2 |
| EU-CTR | RAN_OK | 1 |
| ICTRP | RAN_ZERO | 0 |

Reached:

| Registry | ID | Title | URL |
|---|---|---|---|
| EU-CTR | 2011-004726-10 | A Multi-Center, Prospective, Randomized, Double-Blind, Placebo-Controlled, Parallel-Group Study to Evaluate the Effect of AMR101 on Cardiovascular Health and Mortality in Hypertriglyceridemic Patients with Cardiovascular Disease or at High Risk for Cardiovascular Disease: REDUCE-IT (Reduction of Cardiovascular Events with EPA - Intervention Trial) | https://www.clinicaltrialsregister.eu/ctr-search/trial/2011-004726-10/results |
| ISRCTN | ISRCTN64669648 | NLRP3 and SASP in Vazkepa therapy in patients with heart disease with or without type 2 diabetes | https://www.isrctn.com/ISRCTN64669648 |
| ISRCTN | ISRCTN15140257 | Effect of Icosapent ethyl on inflammation in the vessel wall assessed by the Fat Attenuation Index Score (IRIS-FAI) | https://www.isrctn.com/ISRCTN15140257 |

Probe: `registry_multi_with_status("cardiovascular events", "omega-3")`.

Notable returns:

| Registry | ID | Title | URL |
|---|---|---|---|
| EU-CTR | 2014-001069-28 | A Long-Term Outcomes Study to Assess STatin Residual Risk Reduction with EpaNova in HiGh Cardiovascular Risk PatienTs with Hypertriglyceridemia (STRENGTH) | https://www.clinicaltrialsregister.eu/ctr-search/trial/2014-001069-28/results |
| ISRCTN | ISRCTN41926726 | Supplementation with Folate (and vitamins B6 and B12) and/or Omega 3 Fatty Acids on the prevention of recurrent ischaemic events in patients who have already experienced a coronary or cerebrovascular event | https://www.isrctn.com/ISRCTN41926726 |
| ISRCTN | ISRCTN60635500 | ASCEND: A study of cardiovascular events in diabetes | https://www.isrctn.com/ISRCTN60635500 |

Named missed-trial probes:

| Trial target | ISRCTN | EU-CTR | ICTRP public search |
|---|---:|---:|---:|
| DART / Diet and Reinfarction Trial | 0 | 0 | 0 |
| GISSI-P / GISSI Prevenzione | 0 | 0 | 0 |
| JELIS / Japan EPA Lipid Intervention Study | 0 | 0 | 0 |
| GISSI-HF | 0 | 0 | 0 |

Interpretation: the FDA adapter is useful for FDA-approved icosapent ethyl evidence and
posted REDUCE-IT outcomes; EU-CTR also reaches REDUCE-IT. The registry adapter does not recover
the older DART/GISSI/JELIS/GISSI-HF comparator trials in these probes.

## tranexamic-acid-pph

Probe: `registry_multi_with_status("postpartum haemorrhage", "tranexamic acid")`.

Queries generated: `tranexamic acid postpartum haemorrhage`,
`tranexamic acid postpartum hemorrhage`, `tranexamic acid post-partum haemorrhage`,
`tranexamic acid post-partum hemorrhage`.

Status returned:

| Registry | Status | Count |
|---|---:|---:|
| ISRCTN | RAN_OK | 8 |
| EU-CTR | RAN_OK | 7 |
| ICTRP | RAN_OK | 1 |

Reached requested/near-requested records:

| Target | Registry | ID | Title | URL |
|---|---|---|---|---|
| WOMAN-2 | ISRCTN | ISRCTN62396133 | World maternal antifibrinolytic trial-2 | https://www.isrctn.com/ISRCTN62396133 |
| WOMAN-2 cross-ID | ClinicalTrials.gov | NCT03475342 | World Maternal Antifibrinolytic Trial_2 | https://clinicaltrials.gov/study/NCT03475342 |
| WOMAN | ISRCTN | ISRCTN76912190 | WOrld Maternal ANtifibrinolytic Trial | https://www.isrctn.com/ISRCTN76912190 |
| WOMAN | EU-CTR | 2008-008441-38 | Tranexamic acid for the treatment of postpartum haemorrhage: An international randomised, double blind, placebo controlled trial | https://www.clinicaltrialsregister.eu/ctr-search/trial/2008-008441-38/results |
| TRAAP | EU-CTR | 2014-001748-39 | TRAnexamic Acid for Preventing postpartum hemorrhage following a vaginal delivery: a multicenter randomised, double blind placebo controlled trial | https://www.clinicaltrialsregister.eu/ctr-search/trial/2014-001748-39/results |
| TRAAP cross-ID | ClinicalTrials.gov | NCT02302456 | Tranexamic Acid for Preventing Postpartum Haemorrhage Following a Vaginal Delivery | https://clinicaltrials.gov/study/NCT02302456 |
| TRAAP-2 | EU-CTR | 2017-001144-36 | TRAnexamic Acid for Preventing postpartum hemorrhage following a Cesarean Delivery: a multicenter randomised, double blind placebo controlled trial (TRAAP2) | https://www.clinicaltrialsregister.eu/ctr-search/trial/2017-001144-36/results |
| TRAAP-2 cross-ID | ClinicalTrials.gov | NCT03431805 | TRAnexamic Acid for Preventing Postpartum Hemorrhage Following a Cesarean Delivery | https://clinicaltrials.gov/study/NCT03431805 |

Other source returns from the same registry_multi probe:

| Registry | ID | Title | URL |
|---|---|---|---|
| ICTRP | NCT04733157 | The Efficacy of Tranexamic Acid in Preventing Postpartum Haemorrhage After Caesarean Section | https://trialsearch.who.int/Trial2.aspx?TrialID=NCT04733157 |
| ISRCTN | ISRCTN12590098 | Intramuscular tranexamic acid to prevent heavy bleeding after childbirth in women at higher risk | https://www.isrctn.com/ISRCTN12590098 |
| ISRCTN | ISRCTN11204890 | Use of tranexamic acid for the prevention of blood loss in cesarean delivery: the EPTAC trial | https://www.isrctn.com/ISRCTN11204890 |
| ISRCTN | ISRCTN09968140 | A study to measure the efficacy of tranexamic acid to reduce post partum haemorrhage volume | https://www.isrctn.com/ISRCTN09968140 |

FDA check: `fda_trials("tranexamic acid")` returned heavy-menstrual-bleeding label/application
evidence, not postpartum-haemorrhage trials. It returned no WOMAN, WOMAN-2, TRAAP, or TRAAP-2
PPH-like records in the title/indication scan.

