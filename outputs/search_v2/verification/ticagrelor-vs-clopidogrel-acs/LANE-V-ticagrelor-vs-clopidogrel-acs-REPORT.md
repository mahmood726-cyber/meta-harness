V-ticagrelor-vs-clopidogrel-acs VERDICTS: NEW 20; ELIGIBLE_RCT 1; ELIGIBLE_RCT_NO_PRIMARY 1; NOT_RCT 2; WRONG_* 1; DUPLICATE_OF_ACCOUNTED 6; UNDECIDABLE 0; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 9
automated screen agreed on 2 of 20 verified
r2 includes 23 of 5930; already accounted for 3; NEW 20
Number basis: MEASURED from snapshot records, screening decisions, legacy screen command, and served review JSON.
Verdicts and duplicate mappings are INFERRED from the quoted source spans under the protocol criteria; nothing is pooled in this lane.
N <= 150, so NOT_VERIFIED_CAP 0 and every NEW include was verified (MEASURED).

## ELIGIBLE_RCT ids
- 27471389: Efficacy and safety outcomes of ticagrelor compared with clopidogrel in elderly Chinese patients with acute coronary syndrome.

## DUPLICATE_OF_ACCOUNTED pairs
- 24830710 -> pooled PMID 19717846 (PLATO/NCT00391872)
- 22980299 -> pooled PMID 19717846 (PLATO/NCT00391872)
- 20079528 -> pooled PMID 19717846 (PLATO/NCT00391872)
- 21060072 -> pooled PMID 19717846 (PLATO/NCT00391872)
- 19332184 -> pooled PMID 19717846 (PLATO)
- 17980251 -> legacy/declared-absent PMID 17980250 (DISPERSE-2)

## Raw HTTP bodies relied on
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT03145194.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02792712.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02798874.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02293395.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02044146.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02415803.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT01294462.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02120092.ctgov.json
- lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT00391872.ctgov.json

## Commands run
- `Get-Content -LiteralPath .\LANE_PROMPT.md`
- `git status --short`
- `Get-Content -LiteralPath .\protocols\ticagrelor-vs-clopidogrel-acs.md`
- `Get-Content -LiteralPath .\topics\ticagrelor-vs-clopidogrel-acs.json`
- `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/ticagrelor-vs-clopidogrel-acs.json',encoding='utf-8')); d=json.load(open('cache/ticagrelor-vs-clopidogrel-acs/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `python -c "import json; p='docs/reviews/ticagrelor-vs-clopidogrel-acs/review.json'; d=json.load(open(p,encoding='utf-8')); print(json.dumps({'top_keys':list(d)[:20], 'primary':d.get('primary_outcome') or d.get('primary') or d.get('outcomes')}, ensure_ascii=False)[:12000])"`
- `python -c "<inline denominator script>" (failed with SyntaxError before any file writes)`
- `python -c "<multiline denominator/list NEW script>"`
- `python -c "<multiline source-record dump for all NEW records>"`
- `python -c "<multiline source-record dump for NCT02293395/NCT02044146/NCT02415803/22980299>"`
- `python -c "<fetch CT.gov JSON bodies for NCT-only NEW records into lane_v/ticagrelor-vs-clopidogrel-acs-raw/>"`
- `python -c "<check accounted DISPERSE-2 PMID 17980250 record>"`
- `python -c "<write lane_v JSON/report and validate finish condition>" (failed PowerShell parse before any file writes)`
- `@'<writer/validator script>'@ | python - (failed validation: quote too long for 22980299 before JSON/report writes)`
- `@'<writer/validator script with shortened 22980299 quote>'@ | python -`

## Verdict table
- 37351814: ELIGIBLE_RCT_NO_PRIMARY; screen_agrees=True; quote_source=snapshot abstract; quote="Overall, 142 patients with suspected ACS were randomly assigned to receive crushed or integral formulations of clopidogrel or ticagrelor. Platelet inhibition at baseline and 1 and 8 h was assessed using the VerifyNow assay."
- 32334703: WRONG_COMPARATOR; screen_agrees=False; quote_source=snapshot abstract; quote="Because 475 (95%) patients received ticagrelor in the ticagrelor or prasugrel group, we will refer to this group as the ticagrelor group."
- NCT03145194: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT03145194.ctgov.json); quote="overallStatus=UNKNOWN; conditions=ST Elevation Myocardial Infarction; interventions=Ticagrelor, Placebo"
- 26995378: NOT_RCT; screen_agrees=False; quote_source=snapshot abstract; quote="GEMINI-ACS-1 is a prospective, randomized, double-dummy, double-blind, active-controlled trial that will assess the safety of dual antithrombotic therapy (rivaroxaban [2.5 mg twice daily] + P2Y12 inhibitor) as compared with DAPT (aspirin [100 mg] + P2Y12 inhibitor)"
- 27471389: ELIGIBLE_RCT; screen_agrees=True; quote_source=snapshot abstract; quote="Ticagrelor was more effective than clopidogrel in decreasing the primary efficacy end point (cardiovascular death, myocardial infarction, and stroke, P<0.05)."
- NCT02792712: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02792712.ctgov.json); quote="overallStatus=UNKNOWN; conditions=Acute Coronary Syndrome; interventions=Ticagrelor, Clopidogrel"
- NCT02798874: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02798874.ctgov.json); quote="overallStatus=UNKNOWN; conditions=Cardiovascular Diseases; interventions=Ticagrelor, Clopidogrel"
- 24830710: DUPLICATE_OF_ACCOUNTED; screen_agrees=False; quote_source=snapshot abstract; quote="We performed a post-hoc analysis of cardiovascular and bleeding outcomes in PLATO according to reported PAD status at baseline."
- NCT02293395: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02293395.ctgov.json); quote="overallStatus=COMPLETED; conditions=Acute Coronary Syndrome; interventions=Acetylsalicylic acid, Rivaroxaban, Clopidogrel, Ticagrelor"
- NCT02044146: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02044146.ctgov.json); quote="overallStatus=COMPLETED; conditions=Acute Coronary Syndrome, Percutaneous Coronary Intervention; interventions=Ticagrelor, Prasugrel, Clopidogrel"
- NCT02415803: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02415803.ctgov.json); quote="overallStatus=UNKNOWN; conditions=Non ST Segment Elevation Acute Coronary Syndrome; interventions=low-dose ticagrelor, conventional-dose ticagrelor, Clopidogrel"
- 22980299: DUPLICATE_OF_ACCOUNTED; screen_agrees=False; quote_source=snapshot abstract; quote="In the PLATO trial, ticagrelor compared to clopidogrel in patients with acute coronary syndromes (ACS) reduced the primary composite end point of vascular death, myocardial infarction and stroke, without increasing overall rates of major bleeding."
- 21970081: NOT_RCT; screen_agrees=False; quote_source=snapshot abstract; quote="Clinical evaluation is mainly based on a double-blind randomised trial comparing ticagrelor + aspirin versus clopidogrel + aspirin in 18 624 patients"
- NCT01294462: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT01294462.ctgov.json); quote="overallStatus=COMPLETED; conditions=Acute Coronary Syndrome, Percutaneous Coronary Intervention; interventions=Ticagrelor, Clopidogrel, Acetylsalicylic acid ASA"
- 20079528: DUPLICATE_OF_ACCOUNTED; screen_agrees=False; quote_source=snapshot abstract; quote="At randomisation, an invasive strategy was planned for 13 408 (72.0%) of 18 624 patients hospitalised for acute coronary syndromes (with or without ST elevation)."
- 21060072: DUPLICATE_OF_ACCOUNTED; screen_agrees=False; quote_source=snapshot abstract; quote="This report concerns the 7544 ACS patients with STE or left bundle-branch block allocated to either ticagrelor 180-mg loading dose followed by 90 mg twice daily or clopidogrel 300-mg loading dose"
- NCT02120092: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT02120092.ctgov.json); quote="overallStatus=COMPLETED; conditions=Acute Coronary Syndrome; interventions=Clopidogrel, Ticagrelor, ASA, Placebo"
- 19332184: DUPLICATE_OF_ACCOUNTED; screen_agrees=False; quote_source=snapshot abstract; quote="The phase III PLATelet inhibition and patient Outcomes (PLATO) trial is designed to test the hypothesis that ticagrelor compared with clopidogrel will result in a lower risk of recurrent thrombotic events"
- 17980251: DUPLICATE_OF_ACCOUNTED; screen_agrees=False; quote_source=snapshot abstract; quote="In a substudy of DISPERSE (Dose confIrmation Study assessing anti-Platelet Effects of AZD6140 vs. clopidogRel in non-ST-segment Elevation myocardial infarction)-2, we compared the antiplatelet effects of AZD6140 and clopidogrel"
- NCT00391872: REGISTRY_ONLY_NO_PUBLICATION; screen_agrees=False; quote_source=ctgov api (lane_v/ticagrelor-vs-clopidogrel-acs-raw/NCT00391872.ctgov.json); quote="overallStatus=COMPLETED; conditions=Acute Coronary Syndrome; interventions=Ticagrelor, Clopidogrel"
