# Shared component parser (DISPATCH_REVIEW29 P0): sweep, main a8a7c4b66 v this branch

G1-matched topics: dapagliflozin-hfpef-hosp, denosumab-vertebral-fracture, doac-vte-recurrence, dpp4-mace-t2d, empagliflozin-hfpef-hosp, esketamine-trd-madrs, finerenone-ckd-t2d-renal, glp1-ra-mace-t2d, noac-vs-warfarin-af-stroke, semaglutide-obesity-mace, semaglutide-obesity-weight, sglt2-hfref-hosp-cvdeath, spironolactone-hfref-mortality

## Pooled-row class changes (12 of 710 rows, 32 topics)

| G1 | topic | outcome | served as | trial | before | after |
|---|---|---|---|---|---|---|
| G1 | dapagliflozin-hfpef-hosp | Composite cardiovascular death or worsening heart failure | pooled | DELIVER (36027570) | EXACT_TARGET 0.88 | REFUSED NEAR_MATCH |
| G1 | noac-vs-warfarin-af-stroke | Stroke or systemic embolism | pooled | 21830957 (21830957) | EXACT_TARGET 0.88 | EXACT_TARGET 0.88 |
| G1 | noac-vs-warfarin-af-stroke | Stroke or systemic embolism | pooled | 19717844 (19717844) | EXACT_TARGET 0.91 | EXACT_TARGET 0.91 |
| G1 | noac-vs-warfarin-af-stroke | Stroke or systemic embolism | pooled | 21870978 (21870978) | EXACT_TARGET 0.79 | EXACT_TARGET 0.79 |
|  | balanced-crystalloids-vs-saline-mortality | New renal-replacement therapy | pooled | 35041780 (35041780) | REFUSED None | REFUSED DIFFERENT_OUTCOME |
|  | balanced-crystalloids-vs-saline-mortality | New renal-replacement therapy | declared_absent | 29485925 (29485925) | REFUSED None | REFUSED DIFFERENT_OUTCOME |
|  | balanced-crystalloids-vs-saline-mortality | New renal-replacement therapy | declared_absent | 27749094 (27749094) | REFUSED None | REFUSED DIFFERENT_OUTCOME |
|  | balanced-crystalloids-vs-saline-mortality | New renal-replacement therapy | declared_absent | 26444692 (26444692) | REFUSED None | REFUSED ENDPOINT_UNBOUND |
|  | omega3-cardiovascular-events | Major vascular events / MACE | pooled | 20929341 (20929341) | EXACT_TARGET 1.01 | REFUSED ENDPOINT_UNBOUND |
|  | omega3-cardiovascular-events | Major vascular events / MACE | declared_absent | 23656645 (23656645) | REFUSED NEAR_MATCH | REFUSED DIFFERENT_OUTCOME |
|  | pcsk9-mace | Major adverse cardiovascular events | declared_absent | 25773378 (25773378) | NEAR_MATCH 0.52 | NEAR_MATCH 0.52 |
|  | sglt2-primary-prevention-hf | Hospitalization for heart failure | pooled | 30415602 (30415602) | REFUSED ENDPOINT_UNBOUND | REFUSED DIFFERENT_OUTCOME |

## rob2 D5 level changes (17 of 96 trials; 38 further rows change method only)

| G1 | topic | pooled outcome | before | after | after basis |
|---|---|---|---|---|---|
| G1 | dapagliflozin-hfpef-hosp | Composite cardiovascular death or worsening heart failure | low (component_set) | not_assessable (umbrella_not_established) | registered-outcome identity not established: the selected outcome names an unspecified heart-failure event, which cannot be compared without a held definition w |
| G1 | empagliflozin-hfpef-hosp | Composite cardiovascular death or worsening heart failure | low (component_set) | not_assessable (umbrella_not_established) | registered-outcome identity not established: the selected outcome names an unspecified heart-failure event, which cannot be compared without a held definition w |
| G1 | spironolactone-hfref-mortality | All-cause mortality | some concerns (component_set) | low (label_identity) | the selected outcome is the trial's registered secondary outcome 'Number of Participants With With First Occurrence of All-Cause Mortality' (label_identity) |
|  | colchicine-postop-af | Postoperative atrial fibrillation | low (text_identity) | some concerns (no_match) | registered-outcome identity not established: the selected outcome matches no registered primary or secondary outcome of this trial (registered primary: 'Post-pe |
|  | colchicine-recurrent-pericarditis | Recurrent pericarditis | low (text_identity) | some concerns (no_match) | registered-outcome identity not established: the selected outcome matches no registered primary or secondary outcome of this trial (registered primary: 'Recurre |
|  | colchicine-recurrent-pericarditis | Recurrent pericarditis | low (text_identity) | some concerns (no_match) | registered-outcome identity not established: the selected outcome matches no registered primary or secondary outcome of this trial (registered primary: 'Recurre |
|  | colchicine-secondary-cv-prevention | Trial-defined major coronary/cardiovascular composite | some concerns (no_match) | low (role_primary) | the selected result is the trial's primary end point, its registered primary 'First Event of Cardiovascular Death, Resuscitated Cardiac Arrest, Acute Myocardial |
|  | colchicine-secondary-cv-prevention | Trial-defined major coronary/cardiovascular composite | some concerns (no_match) | low (role_primary) | the selected result is the trial's primary end point, its registered primary 'Composite of cardiovascular death, recurrent myocardial infarction, stroke, or unp |
|  | iv-iron-hfref-hosp | Heart-failure hospitalization | low (text_identity) | some concerns (no_match) | registered-outcome identity not established: the selected outcome matches no registered primary or secondary outcome of this trial (registered primary: 'Time-to |
|  | melatonin-primary-insomnia-sol | Sleep-onset latency | low (text_identity) | some concerns (no_match) | registered-outcome identity not established: the selected outcome matches no registered primary or secondary outcome of this trial (registered primary: 'The Cha |
|  | omega3-cardiovascular-events | Major vascular events / MACE | some concerns (component_set) | not_assessable (component_set_not_established) | registered-outcome identity not established: unrecognised component(s) ['nonfatal cardiovascular events'] in the selected outcome |
|  | omega3-cardiovascular-events | Major vascular events / MACE | low (text_identity) | some concerns (no_match) | registered-outcome identity not established: the selected outcome matches no registered primary or secondary outcome of this trial (registered primary: 'Bone: I |
|  | sacubitril-valsartan-hfref | Composite cardiovascular death or heart-failure hospitalization | some concerns (component_set) | low (component_set) | the selected outcome is the trial's registered primary outcome 'Number of Participants That Had First Occurrence of the Composite Endpoint, Which is Defined as  |
|  | sglt2-ckd-progression | Trial-defined primary cardiorenal composite | some concerns (no_match) | low (role_primary) | the selected result is the trial's primary end point, its registered primary 'Time to the First Occurrence of Any of the Components of the Composite: ≥50% Susta |
|  | sglt2-ckd-progression | Trial-defined primary cardiorenal composite | some concerns (no_match) | low (role_primary) | the selected result is the trial's primary end point, its registered primary 'Primary Composite Endpoint of Doubling of Serum Creatinine (DoSC), End-stage Kidne |
|  | statins-primary-prevention-elderly | Major vascular events | low (text_identity) | not_assessable (generic_not_established) | registered-outcome identity not established: the selected outcome is a generic label with no listed components or held definition, so it cannot be compared with |
|  | ticagrelor-vs-clopidogrel-acs | Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke | some concerns (no_match) | low (component_set) | the selected outcome is the trial's registered primary outcome 'Major Adverse Cardiac Events (MACE)' (component_set) |
