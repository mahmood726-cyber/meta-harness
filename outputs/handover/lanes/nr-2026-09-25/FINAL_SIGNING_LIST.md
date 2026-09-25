# FINAL signing list: result-change notices, 25 Sep 2026

**Mahmood: 17 to sign, 4 to hold, 2 need your ruling.** The other 18 of the 41 are **not** for signing: the
admission-check fix going into V1 removes 11 of them and changes 7.

Nothing here has been signed by anyone. A lane cannot sign these, and the delegated bulk acceptance does not cover
them.

## Run it on your laptop, in the clone `C:\mh-sign`
In Windows PowerShell, once:
```
git clone --filter=blob:none --no-checkout --branch nr/notice-anchors https://github.com/mahmood726-cyber/meta-harness.git C:\mh-sign
cd C:\mh-sign
git sparse-checkout set --no-cone '/*' '!/*/' '/harness/' '/scripts/' '/tests/' '/registry/' '/topics/' '/protocols/' '/docs/result_changes.json' '/docs/reviews/*/review.json' '/docs/reviews/*/index.html' '/cache/spironolactone-hfref-mortality/records.json'
git checkout nr/notice-anchors
git switch -c sign/mahmood-2026-09-25
python -m pip install -r requirements.txt
```

For each notice below:
1. Read it: `python scripts/sign_walk.py --notice NXX`. This prints the exact block you sign, its hash, and every
   finding.
2. If you accept it, run its one-line sign command, copied exactly. It prompts you for your own account of what
   you read (`--basis`). It refuses and writes nothing if the notice's hash or version anchor has moved.

When you have finished, push once:
```
git add docs/result_changes.json
git commit -m "Countersign result-change notices (Mahmood, laptop clone C:\mh-sign)"
git push -u origin sign/mahmood-2026-09-25
```
Then say "pushed". The lane checks every signature from the pushed bytes: hash, judgement and your basis.

## A. Sign (17): each notice is the same before and after the V1 fix

**N02**: colchicine postop af, *Postoperative atrial fibrillation*
- Served now: RR 0.65 (0.21 to 2.05), 3 trials
- After: RR 0.82, no interval (2 trials)
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 42132185).
- Hash: `3690431114d72de2fa5a318f5963918028bfd930e9e491856dfd4e85d51c74fc`
- Version anchor: judgement `B2-N02`
```
python scripts/countersign_result_change.py sign 'colchicine-postop-af' 'Postoperative atrial fibrillation' --notice-index 14 --expect-digest 3690431114d72de2fa5a318f5963918028bfd930e9e491856dfd4e85d51c74fc --by 'Mahmood' --judgement B2-N02 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N03**: colchicine secondary cv prevention, *Trial-defined major coronary/cardiovascular composite*
- Served now: HR 0.81 (0.51 to 1.30), 3 trials
- After: HR 0.89, no interval (2 trials)
- Why: 1 trial(s) set aside: 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 32865380).
- Hash: `e3a424b71025d731310fb187708c9c070af75263f759604c414170d043f2b908`
- Version anchor: judgement `B2-N03`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Trial-defined major coronary/cardiovascular composite' --notice-index 15 --expect-digest e3a424b71025d731310fb187708c9c070af75263f759604c414170d043f2b908 --by 'Mahmood' --judgement B2-N03 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N04**: colchicine secondary cv prevention, *Gastrointestinal adverse effects*
- Served now: RR 5.38 (1.60 to 18.10), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 34876021).
- Hash: `1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e`
- Version anchor: judgement `B2-N04`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Gastrointestinal adverse effects' --notice-index 16 --expect-digest 1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e --by 'Mahmood' --judgement B2-N04 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N05**: colchicine secondary cv prevention, *Non-cardiovascular death*
- Served now: HR 1.51 (0.99 to 2.31), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 32865380).
- Hash: `c37ca3b953b5bb40d797d09b1a39e627877739cbed681cb43b2a1708c12fefdb`
- Version anchor: judgement `B2-N05`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Non-cardiovascular death' --notice-index 17 --expect-digest c37ca3b953b5bb40d797d09b1a39e627877739cbed681cb43b2a1708c12fefdb --by 'Mahmood' --judgement B2-N05 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N07**: corticosteroids covid19 mortality, *28-day all-cause mortality*
- Served now: RR 0.83 (0.75 to 0.93), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 32678530).
- Hash: `d614bce51c695ce4a03183ad619bcecb242cd338032e4f56df26177143ce4236`
- Version anchor: judgement `B2-N07`
```
python scripts/countersign_result_change.py sign 'corticosteroids-covid19-mortality' '28-day all-cause mortality' --notice-index 19 --expect-digest d614bce51c695ce4a03183ad619bcecb242cd338032e4f56df26177143ce4236 --by 'Mahmood' --judgement B2-N07 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N10**: denosumab vertebral fracture, *New vertebral fracture*
- Served now: RR 0.32 (0.26 to 0.41), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 19671655).
- Hash: `95dd9b4646712d4f3445a3aafe0021e2de9a3463cdddf28bce9f1074298aad96`
- Version anchor: judgement `B2-N10`
```
python scripts/countersign_result_change.py sign 'denosumab-vertebral-fracture' 'New vertebral fracture' --notice-index 22 --expect-digest 95dd9b4646712d4f3445a3aafe0021e2de9a3463cdddf28bce9f1074298aad96 --by 'Mahmood' --judgement B2-N10 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N11**: denosumab vertebral fracture, *Nonvertebral fracture*
- Served now: HR 0.80 (0.67 to 0.95), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 19671655).
- Hash: `4943555b8c1f964c6a0bbb14f76e51b31396a7f99223a0e4f9f08d4a288dae84`
- Version anchor: judgement `B2-N11`
```
python scripts/countersign_result_change.py sign 'denosumab-vertebral-fracture' 'Nonvertebral fracture' --notice-index 23 --expect-digest 4943555b8c1f964c6a0bbb14f76e51b31396a7f99223a0e4f9f08d4a288dae84 --by 'Mahmood' --judgement B2-N11 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N12**: denosumab vertebral fracture, *Hip fracture*
- Served now: HR 0.60 (0.37 to 0.97), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 19671655).
- Hash: `a54538da135fd19653552c00e6654557e8c4c9d7d85f5439a5c0fce0026507a1`
- Version anchor: judgement `B2-N12`
```
python scripts/countersign_result_change.py sign 'denosumab-vertebral-fracture' 'Hip fracture' --notice-index 24 --expect-digest a54538da135fd19653552c00e6654557e8c4c9d7d85f5439a5c0fce0026507a1 --by 'Mahmood' --judgement B2-N12 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N16**: doac vte recurrence, *Any bleeding*
- Served now: HR 0.69, no interval (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 2 because its registry record doesn't name the review's patient group (PMID 19966341, PMID 24344086).
- Hash: `0d8530a50a44be5e7a37a16e36379fef7d121f1eb1ec281930a542343248b736`
- Version anchor: judgement `B2-N16`
```
python scripts/countersign_result_change.py sign 'doac-vte-recurrence' 'Any bleeding' --notice-index 28 --expect-digest 0d8530a50a44be5e7a37a16e36379fef7d121f1eb1ec281930a542343248b736 --by 'Mahmood' --judgement B2-N16 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N22**: glp1 ra mace t2d, *3-point major adverse cardiovascular events*
- Served now: HR 0.86 (0.81 to 0.91), 8 trials
- After: HR 0.87 (0.81 to 0.92), 7 trials
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 30291013).
- Hash: `d08802f24fa082652dc45a011f29b08edd49030c2429d9c1b0062d27094ae694`
- Version anchor: judgement `B2-N22`
```
python scripts/countersign_result_change.py sign 'glp1-ra-mace-t2d' '3-point major adverse cardiovascular events' --notice-index 34 --expect-digest d08802f24fa082652dc45a011f29b08edd49030c2429d9c1b0062d27094ae694 --by 'Mahmood' --judgement B2-N22 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N24**: metformin pcos ovulation, *Ovulation with metformin added to clomifene*
- Served now: OR 2.07 (0.09 to 46.60), 3 trials
- After: no pooled result
- Why: 3 trial(s) set aside: 2 because no trial-registry record is linked to it (PMID 11172832, PMID 19522426); 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 16769748).
- Hash: `1c9acaf64e31e52cf02127e55758e702277c6e2f2e357b296a95ab8226aea944`
- Version anchor: judgement `B2-N24`
```
python scripts/countersign_result_change.py sign 'metformin-pcos-ovulation' 'Ovulation with metformin added to clomifene' --notice-index 36 --expect-digest 1c9acaf64e31e52cf02127e55758e702277c6e2f2e357b296a95ab8226aea944 --by 'Mahmood' --judgement B2-N24 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N31**: probiotics aad prevention, *Serious adverse events*
- Served now: RR 0.66 (0.19 to 2.28), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 34541475).
- Hash: `2cd6d6b932556d19c2545dc292f0ed279e8d770d3bd20b9337fcdd83cb1a7e31`
- Version anchor: judgement `B2-N31`
```
python scripts/countersign_result_change.py sign 'probiotics-aad-prevention' 'Serious adverse events' --notice-index 43 --expect-digest 2cd6d6b932556d19c2545dc292f0ed279e8d770d3bd20b9337fcdd83cb1a7e31 --by 'Mahmood' --judgement B2-N31 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N33**: semaglutide obesity mace, *3-point major adverse cardiovascular events*
- Served now: HR 0.80 (0.72 to 0.90), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 37952131).
- Hash: `53fbdc2855f72801f2ae3c421f3eecff3a7aac637ed697e5045666f4d3e9ac19`
- Version anchor: judgement `B2-N33`
```
python scripts/countersign_result_change.py sign 'semaglutide-obesity-mace' '3-point major adverse cardiovascular events' --notice-index 45 --expect-digest 53fbdc2855f72801f2ae3c421f3eecff3a7aac637ed697e5045666f4d3e9ac19 --by 'Mahmood' --judgement B2-N33 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N34**: semaglutide obesity mace, *Adverse events leading to permanent discontinuation*
- Served now: RR 2.03 (1.87 to 2.21), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 37952131).
- Hash: `e74270fdaec8ee61ff67a5896ec876bad4dfe4bbee5f869fdf917bd090c0112b`
- Version anchor: judgement `B2-N34`
```
python scripts/countersign_result_change.py sign 'semaglutide-obesity-mace' 'Adverse events leading to permanent discontinuation' --notice-index 46 --expect-digest e74270fdaec8ee61ff67a5896ec876bad4dfe4bbee5f869fdf917bd090c0112b --by 'Mahmood' --judgement B2-N34 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N36**: sglt2 primary prevention hf, *Lower-limb amputation*
- Served now: HR 1.97 (1.41 to 2.75), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 28605608).
- Hash: `79240a2fdba179f2d7fd25a21885eaebd6a0e92a9ab0dea6a6e4ebdada3dea57`
- Version anchor: judgement `B2-N36`
```
python scripts/countersign_result_change.py sign 'sglt2-primary-prevention-hf' 'Lower-limb amputation' --notice-index 48 --expect-digest 79240a2fdba179f2d7fd25a21885eaebd6a0e92a9ab0dea6a6e4ebdada3dea57 --by 'Mahmood' --judgement B2-N36 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N37**: spironolactone hfref mortality, *All-cause mortality*
- Served now: HR 0.73 (0.56 to 0.95), 3 trials
- After: HR 0.85 (0.53 to 1.36), 1 trial
- Why: 2 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 10471456); 1 because the registry record says it is not randomised (the record conflicts with the paper) (PMID 21073363).
- Note: The held PMID 21073363 abstract names NCT00232180 and describes randomised double-blind eplerenone versus placebo, while the page excludes that same family using NON_RANDOMIZED/SINGLE_GROUP registry design bytes. Resolve this identity/design conflict and PMID 10471456's unresolved registry parent; only if both families pass the unchanged admission checks can the old pool be restored by a rebuild.
- Hash: `6b0a23a030f53c9216f960a2af3ba7ca42a5d1bf6b70b6a03df9c079a2fd96e7`
- Version anchor: judgement `B2-N37`
```
python scripts/countersign_result_change.py sign 'spironolactone-hfref-mortality' 'All-cause mortality' --notice-index 49 --expect-digest 6b0a23a030f53c9216f960a2af3ba7ca42a5d1bf6b70b6a03df9c079a2fd96e7 --by 'Mahmood' --judgement B2-N37 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N41**: tocilizumab covid19 mortality, *28-day all-cause mortality*
- Served now: RR 0.85 (0.76 to 0.94), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 33933206).
- Hash: `dac4bf59ed5f659ed5e2fc8399c8a0de7d5543f9c006785f7c717bb20ccec970`
- Version anchor: judgement `B2-N41`
```
python scripts/countersign_result_change.py sign 'tocilizumab-covid19-mortality' '28-day all-cause mortality' --notice-index 53 --expect-digest dac4bf59ed5f659ed5e2fc8399c8a0de7d5543f9c006785f7c717bb20ccec970 --by 'Mahmood' --judgement B2-N41 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

## B. Hold (4): the notice exists, but its wording misstates the change. Don't sign until it's reworded

**N06**: corticosteroids cap mortality, *Hyperglycaemia*
- Served now: no pooled number (4 trials)
- After: RR 3.74, no interval (2 trials)
- Why: 2 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 21636122); 1 because its registered arms don't show the comparison (PMID 25608756).
- Hold because the notice is the only place on the page that shows a harm number (RR 3.74) the page otherwise withholds.

**N27**: omega3 cardiovascular events, *Atrial fibrillation*
- Served now: no pooled result
- After: RR 1.23 (0.98 to 1.54), 1 trial
- Why: 0 trial(s) set aside: .
- Hold because the notice is the only place on the page that shows RR 1.23, and it gives no cause (no trial entered or left).

**N28**: pcsk9 mace, *Major adverse cardiovascular events*
- Served now: HR 0.83, no interval (2 trials)
- After: HR 0.85 (0.78 to 0.93), 1 trial
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 28304224).
- Hold because it creates a new 'significant benefit' claim (HR 0.85, 0.78-0.93) but says 'direction unchanged'.

**N38**: statins primary prevention elderly, *Major vascular events*
- Served now: HR 0.68, no interval (2 trials)
- After: HR 0.70 (0.61 to 0.82), 1 trial
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 20404379).
- Hold because it creates a new 'significant benefit' claim (HR 0.70, 0.61-0.82) but says 'direction unchanged'.

## C. Your ruling first (2): the check may be misreading the registry. The fix doesn't touch these

**N08**: corticosteroids covid19 mortality, *Serious adverse events*
- Served now: OR 2.81 (0.11 to 74.56), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registered arms don't show the comparison (PMID 34138478).
- Question: the control arm (saline) is registered as an active drug, so the check sees no contrast; the fix does not change this. Do you accept the registry's coding as grounds to set the trial aside?
- If you accept, sign with:
```
python scripts/countersign_result_change.py sign 'corticosteroids-covid19-mortality' 'Serious adverse events' --notice-index 20 --expect-digest 0598e8b7596d23b2e1549a5f70625e4ef9c0eb2f98f23c58f87c8eb554937bc8 --by 'Mahmood' --judgement B2-N08 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N23**: iv iron hfref hosp, *Heart-failure hospitalization*
- Served now: no pooled number (2 trials)
- After: HR 0.39 (0.19 to 0.82), 1 trial
- Why: 1 trial(s) set aside: 1 because its registered arms don't show the comparison (PMID 40159390).
- Question: the IV-iron arm is registered as plain 'iron' (not 'ferric carboxymaltose'); the fix does not change this. Do you accept that as grounds to set the trial aside?
- If you accept, sign with:
```
python scripts/countersign_result_change.py sign 'iv-iron-hfref-hosp' 'Heart-failure hospitalization' --notice-index 35 --expect-digest a756a601fe1512d95acf8ae7e652633c3202da441ee1b9f8aca80b7c7feb03a2 --by 'Mahmood' --judgement B2-N23 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

## Not on this list (18)
- **Removed by the V1 fix (11)**, because every trial they drop is readmitted: N09, N15, N17, N18, N19, N20, N21, N25, N32, N39, N40. The check was misreading data the site already holds.
- **Changed by the V1 fix (7)**, to be regenerated and re-judged: N01, N13, N14, N26, N29, N30, N35.
- **D01** (EMPHASIS-HF): not signable until you rule and the correction is made.
