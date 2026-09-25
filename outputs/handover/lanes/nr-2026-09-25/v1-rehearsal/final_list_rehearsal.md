# FINAL signing list: result-change notices for V1

**Mahmood: 39 to sign, 1 to hold, 1 need your ruling.** Nothing here is signed. A lane
cannot sign these notices, and the delegated bulk acceptance does not cover them.

## Run it on your laptop, in the clone `C:\mh-sign-v1`
In Windows PowerShell, once:
```
git clone --filter=blob:none --no-checkout --branch nr/v1-sign-REHEARSAL https://github.com/mahmood726-cyber/meta-harness.git C:\mh-sign-v1
cd C:\mh-sign-v1
git sparse-checkout set --no-cone '/*' '!/*/' '/harness/' '/scripts/' '/tests/' '/registry/' '/topics/' '/protocols/' '/docs/result_changes.json' '/docs/reviews/*/review.json' '/docs/reviews/*/index.html' '/cache/spironolactone-hfref-mortality/records.json'
git checkout nr/v1-sign-REHEARSAL
git switch -c sign/mahmood-v1
python -m pip install -r requirements.txt
```
For each notice:
1. Read it: `python scripts/sign_walk.py --notice ID`
2. If you accept it, run its one-line command exactly as written below. It asks for your own account of what you
   read. It refuses, and writes nothing, if the notice's hash or version anchor has moved.

When you have finished, push once:
```
git add docs/result_changes.json
git commit -m "Countersign V1 result-change notices (Mahmood, laptop clone C:\mh-sign-v1)"
git push -u origin sign/mahmood-v1
```
Then say "pushed". Lane NR checks every signature from the pushed bytes.

## A. Sign (39)

**N04**: colchicine secondary cv prevention, *Gastrointestinal adverse effects*
- Served now: RR 5.38 (1.60 to 18.10), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 34876021).
- Hash: `1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e`
- Version anchor: judgement `B3-N04`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Gastrointestinal adverse effects' --notice-index 16 --expect-digest 1bb44d92ecc82e639f8ec3f39ba4624cfc9b60556b76e061574deda42a98ec4e --by 'Mahmood' --judgement B3-N04 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N05**: colchicine secondary cv prevention, *Non-cardiovascular death*
- Served now: HR 1.51 (0.99 to 2.31), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 32865380).
- Hash: `c37ca3b953b5bb40d797d09b1a39e627877739cbed681cb43b2a1708c12fefdb`
- Version anchor: judgement `B3-N05`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Non-cardiovascular death' --notice-index 17 --expect-digest c37ca3b953b5bb40d797d09b1a39e627877739cbed681cb43b2a1708c12fefdb --by 'Mahmood' --judgement B3-N05 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N09**: dapagliflozin hfpef hosp, *Adverse events*
- Served now: RR 1.16 (0.80 to 1.69), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 34711976).
- Hash: `edf44d6a7f4379e2d843d69bc4b364d10d5d8814e7b8e71a2b96760ca44eba28`
- Version anchor: judgement `B3-N09`
```
python scripts/countersign_result_change.py sign 'dapagliflozin-hfpef-hosp' 'Adverse events' --notice-index 21 --expect-digest edf44d6a7f4379e2d843d69bc4b364d10d5d8814e7b8e71a2b96760ca44eba28 --by 'Mahmood' --judgement B3-N09 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N13**: doac vte recurrence, *Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)*
- Served now: HR 0.91 (0.75 to 1.10), 6 trials
- After: no pooled result
- Why: 6 trial(s) set aside: 3 because its registry record doesn't name the review's patient group (PMID 19966341, PMID 23808982, PMID 24344086); 1 because no trial-registry record is linked to it (PMID 21128814); 2 because its registered arms don't show the comparison (PMID 22449293, PMID 23991658).
- Hash: `31026af2f4b7dd5c743a81d36d65d685e8e1bdfc72c3776a82ae21660f2baef2`
- Version anchor: judgement `B3-N13`
```
python scripts/countersign_result_change.py sign 'doac-vte-recurrence' 'Symptomatic recurrent VTE (DVT / nonfatal PE / fatal PE or VTE-related death)' --notice-index 25 --expect-digest 31026af2f4b7dd5c743a81d36d65d685e8e1bdfc72c3776a82ae21660f2baef2 --by 'Mahmood' --judgement B3-N13 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N17**: dpp4 mace t2d, *3-point major adverse cardiovascular events*
- Served now: HR 1.01 (0.84 to 1.21), 3 trials
- After: HR 1.00 (0.89 to 1.12), 1 trial
- Why: 2 trial(s) set aside: 1 because its registered arms don't show the comparison (PMID 28893244); 1 because its registry record doesn't name the review's patient group (PMID 30418475).
- Hash: `2fa781b661905c03ea0708a0ff7b0676ad93a4dc1e40a30bcec59f6f94e1bd11`
- Version anchor: judgement `B3-N17`
```
python scripts/countersign_result_change.py sign 'dpp4-mace-t2d' '3-point major adverse cardiovascular events' --notice-index 29 --expect-digest 2fa781b661905c03ea0708a0ff7b0676ad93a4dc1e40a30bcec59f6f94e1bd11 --by 'Mahmood' --judgement B3-N17 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N19**: dpp4 mace t2d, *Hypoglycemia*
- Served now: RR 1.01 (0.94 to 1.08), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 30418475).
- Hash: `0930b057ff6a2a11d6b5c7335055d6ebf1b674b303b1c6dad59945d6af6fb854`
- Version anchor: judgement `B3-N19`
```
python scripts/countersign_result_change.py sign 'dpp4-mace-t2d' 'Hypoglycemia' --notice-index 31 --expect-digest 0930b057ff6a2a11d6b5c7335055d6ebf1b674b303b1c6dad59945d6af6fb854 --by 'Mahmood' --judgement B3-N19 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N21**: esketamine trd madrs, *Adverse events*
- Served now: RR 1.35 (1.20 to 1.52), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 37025256).
- Hash: `13f747773d3ace542789ecd24483b3bd3121dc9cc97a11df0ce2b7541d8beed2`
- Version anchor: judgement `B3-N21`
```
python scripts/countersign_result_change.py sign 'esketamine-trd-madrs' 'Adverse events' --notice-index 33 --expect-digest 13f747773d3ace542789ecd24483b3bd3121dc9cc97a11df0ce2b7541d8beed2 --by 'Mahmood' --judgement B3-N21 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N20**: esketamine trd madrs, *Observed-case Day-28 raw change-score MADRS MD*
- Served now: MD -3.10 (-7.33 to 1.13), 3 trials
- After: MD -4.40 (-8.03 to -0.77), 1 trial
- Why: 2 trial(s) set aside: 2 because its registry record doesn't name the review's patient group (NCT02422186, PMID 37025256).
- Hash: `c798e39df2834a16d461a646b8512469f51228ce41fd2088d7156bbf78d9ec46`
- Version anchor: judgement `B3-N20`
```
python scripts/countersign_result_change.py sign 'esketamine-trd-madrs' 'Observed-case Day-28 raw change-score MADRS MD' --notice-index 32 --expect-digest c798e39df2834a16d461a646b8512469f51228ce41fd2088d7156bbf78d9ec46 --by 'Mahmood' --judgement B3-N20 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N23**: iv iron hfref hosp, *Heart-failure hospitalization*
- Served now: no pooled number (2 trials)
- After: HR 0.39 (0.19 to 0.82), 1 trial
- Why: 1 trial(s) set aside: 1 because its registered arms don't show the comparison (PMID 40159390).
- Hash: `a756a601fe1512d95acf8ae7e652633c3202da441ee1b9f8aca80b7c7feb03a2`
- Version anchor: judgement `B3-N23`
```
python scripts/countersign_result_change.py sign 'iv-iron-hfref-hosp' 'Heart-failure hospitalization' --notice-index 35 --expect-digest a756a601fe1512d95acf8ae7e652633c3202da441ee1b9f8aca80b7c7feb03a2 --by 'Mahmood' --judgement B3-N23 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N24**: metformin pcos ovulation, *Ovulation with metformin added to clomifene*
- Served now: OR 2.07 (0.09 to 46.60), 3 trials
- After: no pooled result
- Why: 3 trial(s) set aside: 2 because no trial-registry record is linked to it (PMID 11172832, PMID 19522426); 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 16769748).
- Hash: `1c9acaf64e31e52cf02127e55758e702277c6e2f2e357b296a95ab8226aea944`
- Version anchor: judgement `B3-N24`
```
python scripts/countersign_result_change.py sign 'metformin-pcos-ovulation' 'Ovulation with metformin added to clomifene' --notice-index 36 --expect-digest 1c9acaf64e31e52cf02127e55758e702277c6e2f2e357b296a95ab8226aea944 --by 'Mahmood' --judgement B3-N24 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N26**: omega3 cardiovascular events, *Major vascular events / MACE*
- Served now: HR 0.94 (0.77 to 1.14), 5 trials
- After: HR 0.92 (0.80 to 1.06), 1 trial
- Why: 4 trial(s) set aside: 3 because its registered arms don't show the comparison (PMID 20929341, PMID 30415628, PMID 33190147); 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 21115589).
- Hash: `4321fe0612f041924e2fd562a27c8f76fc19e463cb5347a1ef921d6a524b9623`
- Version anchor: judgement `B3-N26`
```
python scripts/countersign_result_change.py sign 'omega3-cardiovascular-events' 'Major vascular events / MACE' --notice-index 38 --expect-digest 4321fe0612f041924e2fd562a27c8f76fc19e463cb5347a1ef921d6a524b9623 --by 'Mahmood' --judgement B3-N26 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**V1-01**: pcsk9 mace, *Major adverse cardiovascular events*
- Served now: HR 0.83, no interval (2 trials)
- After: HR 0.84 (0.78 to 0.93), 1 trial
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 28304224).
- New in V1: it replaces N28, which the V1 fix changed.
- Hash: `243edd576999bcaf39523ebf86dac6a8070ace60bab52a1b24a67a1391645050`
- Version anchor: judgement `B3-V1-01`
```
python scripts/countersign_result_change.py sign 'pcsk9-mace' 'Major adverse cardiovascular events' --notice-index 40 --expect-digest 243edd576999bcaf39523ebf86dac6a8070ace60bab52a1b24a67a1391645050 --by 'Mahmood' --judgement B3-V1-01 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N29**: probiotics aad prevention, *Antibiotic-associated diarrhoea*
- Served now: RR 0.69 (0.48 to 0.98), 11 trials
- After: no pooled result
- Why: 11 trial(s) set aside: 9 because no trial-registry record is linked to it (PMID 11560298, PMID 15740542, PMID 18026577, PMID 18410562, PMID 18701826, PMID 21165295, PMID 24772726, PMID 32035998, PMID 7872284); 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 23932219); 1 because its registry record doesn't name the review's patient group (PMID 35727573).
- Hash: `f7e6067da30ae61a647d04f07e01607869533ff71f658c7277044bac317f1367`
- Version anchor: judgement `B3-N29`
```
python scripts/countersign_result_change.py sign 'probiotics-aad-prevention' 'Antibiotic-associated diarrhoea' --notice-index 41 --expect-digest f7e6067da30ae61a647d04f07e01607869533ff71f658c7277044bac317f1367 --by 'Mahmood' --judgement B3-N29 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N34**: semaglutide obesity mace, *Adverse events leading to permanent discontinuation*
- Served now: RR 2.03 (1.87 to 2.21), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 37952131).
- Hash: `e74270fdaec8ee61ff67a5896ec876bad4dfe4bbee5f869fdf917bd090c0112b`
- Version anchor: judgement `B3-N34`
```
python scripts/countersign_result_change.py sign 'semaglutide-obesity-mace' 'Adverse events leading to permanent discontinuation' --notice-index 46 --expect-digest e74270fdaec8ee61ff67a5896ec876bad4dfe4bbee5f869fdf917bd090c0112b --by 'Mahmood' --judgement B3-N34 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N36**: sglt2 primary prevention hf, *Lower-limb amputation*
- Served now: HR 1.97 (1.41 to 2.75), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 28605608).
- Hash: `79240a2fdba179f2d7fd25a21885eaebd6a0e92a9ab0dea6a6e4ebdada3dea57`
- Version anchor: judgement `B3-N36`
```
python scripts/countersign_result_change.py sign 'sglt2-primary-prevention-hf' 'Lower-limb amputation' --notice-index 48 --expect-digest 79240a2fdba179f2d7fd25a21885eaebd6a0e92a9ab0dea6a6e4ebdada3dea57 --by 'Mahmood' --judgement B3-N36 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N38**: statins primary prevention elderly, *Major vascular events*
- Served now: HR 0.68, no interval (2 trials)
- After: HR 0.70 (0.61 to 0.82), 1 trial
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 20404379).
- Hash: `6f503cd8fe2fc65b64343441de1a22a7d7047f962740dfbf081b4143d5383a1a`
- Version anchor: judgement `B3-N38`
```
python scripts/countersign_result_change.py sign 'statins-primary-prevention-elderly' 'Major vascular events' --notice-index 50 --expect-digest 6f503cd8fe2fc65b64343441de1a22a7d7047f962740dfbf081b4143d5383a1a --by 'Mahmood' --judgement B3-N38 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N40**: ticagrelor vs clopidogrel acs, *Major bleeding*
- Served now: HR 1.17, no interval (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 2 because its registered arms don't show the comparison (PMID 19717846, PMID 26376600).
- Hash: `4b9137866f1904beed6c1a1eedc01d07b3720f7b196560c6443ac24703f4a697`
- Version anchor: judgement `B3-N40`
```
python scripts/countersign_result_change.py sign 'ticagrelor-vs-clopidogrel-acs' 'Major bleeding' --notice-index 52 --expect-digest 4b9137866f1904beed6c1a1eedc01d07b3720f7b196560c6443ac24703f4a697 --by 'Mahmood' --judgement B3-N40 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N01**: balanced crystalloids vs saline mortality, *Mortality*
- Served now: HR 0.98, no interval (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 1 because its registered arms don't show the comparison (PMID 34375394); 1 because its registry record doesn't name the review's patient group (PMID 35041780).
- Hash: `2b86cd169fad9d8097b14067fdb5ce1653e77297870530e20eae588bdadf80b2`
- Version anchor: judgement `B3-N01`
```
python scripts/countersign_result_change.py sign 'balanced-crystalloids-vs-saline-mortality' 'Mortality' --notice-index 13 --expect-digest 2b86cd169fad9d8097b14067fdb5ce1653e77297870530e20eae588bdadf80b2 --by 'Mahmood' --judgement B3-N01 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N07**: corticosteroids covid19 mortality, *28-day all-cause mortality*
- Served now: RR 0.83 (0.75 to 0.93), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 32678530).
- Hash: `d614bce51c695ce4a03183ad619bcecb242cd338032e4f56df26177143ce4236`
- Version anchor: judgement `B3-N07`
```
python scripts/countersign_result_change.py sign 'corticosteroids-covid19-mortality' '28-day all-cause mortality' --notice-index 19 --expect-digest d614bce51c695ce4a03183ad619bcecb242cd338032e4f56df26177143ce4236 --by 'Mahmood' --judgement B3-N07 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N10**: denosumab vertebral fracture, *New vertebral fracture*
- Served now: RR 0.32 (0.26 to 0.41), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 19671655).
- Hash: `95dd9b4646712d4f3445a3aafe0021e2de9a3463cdddf28bce9f1074298aad96`
- Version anchor: judgement `B3-N10`
```
python scripts/countersign_result_change.py sign 'denosumab-vertebral-fracture' 'New vertebral fracture' --notice-index 22 --expect-digest 95dd9b4646712d4f3445a3aafe0021e2de9a3463cdddf28bce9f1074298aad96 --by 'Mahmood' --judgement B3-N10 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N11**: denosumab vertebral fracture, *Nonvertebral fracture*
- Served now: HR 0.80 (0.67 to 0.95), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 19671655).
- Hash: `4943555b8c1f964c6a0bbb14f76e51b31396a7f99223a0e4f9f08d4a288dae84`
- Version anchor: judgement `B3-N11`
```
python scripts/countersign_result_change.py sign 'denosumab-vertebral-fracture' 'Nonvertebral fracture' --notice-index 23 --expect-digest 4943555b8c1f964c6a0bbb14f76e51b31396a7f99223a0e4f9f08d4a288dae84 --by 'Mahmood' --judgement B3-N11 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N12**: denosumab vertebral fracture, *Hip fracture*
- Served now: HR 0.60 (0.37 to 0.97), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 19671655).
- Hash: `a54538da135fd19653552c00e6654557e8c4c9d7d85f5439a5c0fce0026507a1`
- Version anchor: judgement `B3-N12`
```
python scripts/countersign_result_change.py sign 'denosumab-vertebral-fracture' 'Hip fracture' --notice-index 24 --expect-digest a54538da135fd19653552c00e6654557e8c4c9d7d85f5439a5c0fce0026507a1 --by 'Mahmood' --judgement B3-N12 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N14**: doac vte recurrence, *Major bleeding*
- Served now: HR 0.62 (0.31 to 1.25), 3 trials
- After: no pooled result
- Why: 3 trial(s) set aside: 2 because its registry record doesn't name the review's patient group (PMID 19966341, PMID 24344086); 1 because its registered arms don't show the comparison (PMID 22449293).
- Hash: `81e8c9bb43e75c896680f56f2754e70e4386e58f93ff1d1be7fa7b7064a7d8f3`
- Version anchor: judgement `B3-N14`
```
python scripts/countersign_result_change.py sign 'doac-vte-recurrence' 'Major bleeding' --notice-index 26 --expect-digest 81e8c9bb43e75c896680f56f2754e70e4386e58f93ff1d1be7fa7b7064a7d8f3 --by 'Mahmood' --judgement B3-N14 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N15**: doac vte recurrence, *Major or clinically relevant nonmajor bleeding*
- Served now: HR 0.85, no interval (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 2 because its registered arms don't show the comparison (PMID 22449293, PMID 23991658).
- Hash: `b1c40017b581d6f7ddf3d4f79c5c1f37a91ee39a3156c9105dec97768cfade7e`
- Version anchor: judgement `B3-N15`
```
python scripts/countersign_result_change.py sign 'doac-vte-recurrence' 'Major or clinically relevant nonmajor bleeding' --notice-index 27 --expect-digest b1c40017b581d6f7ddf3d4f79c5c1f37a91ee39a3156c9105dec97768cfade7e --by 'Mahmood' --judgement B3-N15 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N16**: doac vte recurrence, *Any bleeding*
- Served now: HR 0.69, no interval (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 2 because its registry record doesn't name the review's patient group (PMID 19966341, PMID 24344086).
- Hash: `0d8530a50a44be5e7a37a16e36379fef7d121f1eb1ec281930a542343248b736`
- Version anchor: judgement `B3-N16`
```
python scripts/countersign_result_change.py sign 'doac-vte-recurrence' 'Any bleeding' --notice-index 28 --expect-digest 0d8530a50a44be5e7a37a16e36379fef7d121f1eb1ec281930a542343248b736 --by 'Mahmood' --judgement B3-N16 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N18**: dpp4 mace t2d, *Adverse events*
- Served now: RR 0.99 (0.96 to 1.01), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 30418475).
- Hash: `51bce4eea7aa71923e858e04fc137157c35652c561de87bb83cb273bcb237eb3`
- Version anchor: judgement `B3-N18`
```
python scripts/countersign_result_change.py sign 'dpp4-mace-t2d' 'Adverse events' --notice-index 30 --expect-digest 51bce4eea7aa71923e858e04fc137157c35652c561de87bb83cb273bcb237eb3 --by 'Mahmood' --judgement B3-N18 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N25**: noac vs warfarin af stroke, *Stroke or systemic embolism*
- Served now: HR 0.81 (0.66 to 0.98), 4 trials
- After: no pooled result
- Why: 4 trial(s) set aside: 4 because its registered arms don't show the comparison (PMID 19717844, PMID 21830957, PMID 21870978, PMID 24251359).
- Hash: `96bb274b31cd7b87ad1c6b915c825ebb01c6714de82dde2a22df8c10566bc301`
- Version anchor: judgement `B3-N25`
```
python scripts/countersign_result_change.py sign 'noac-vs-warfarin-af-stroke' 'Stroke or systemic embolism' --notice-index 37 --expect-digest 96bb274b31cd7b87ad1c6b915c825ebb01c6714de82dde2a22df8c10566bc301 --by 'Mahmood' --judgement B3-N25 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N31**: probiotics aad prevention, *Serious adverse events*
- Served now: RR 0.66 (0.19 to 2.28), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 34541475).
- Hash: `2cd6d6b932556d19c2545dc292f0ed279e8d770d3bd20b9337fcdd83cb1a7e31`
- Version anchor: judgement `B3-N31`
```
python scripts/countersign_result_change.py sign 'probiotics-aad-prevention' 'Serious adverse events' --notice-index 43 --expect-digest 2cd6d6b932556d19c2545dc292f0ed279e8d770d3bd20b9337fcdd83cb1a7e31 --by 'Mahmood' --judgement B3-N31 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N33**: semaglutide obesity mace, *3-point major adverse cardiovascular events*
- Served now: HR 0.80 (0.72 to 0.90), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 37952131).
- Hash: `53fbdc2855f72801f2ae3c421f3eecff3a7aac637ed697e5045666f4d3e9ac19`
- Version anchor: judgement `B3-N33`
```
python scripts/countersign_result_change.py sign 'semaglutide-obesity-mace' '3-point major adverse cardiovascular events' --notice-index 45 --expect-digest 53fbdc2855f72801f2ae3c421f3eecff3a7aac637ed697e5045666f4d3e9ac19 --by 'Mahmood' --judgement B3-N33 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N41**: tocilizumab covid19 mortality, *28-day all-cause mortality*
- Served now: RR 0.85 (0.76 to 0.94), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 33933206).
- Hash: `dac4bf59ed5f659ed5e2fc8399c8a0de7d5543f9c006785f7c717bb20ccec970`
- Version anchor: judgement `B3-N41`
```
python scripts/countersign_result_change.py sign 'tocilizumab-covid19-mortality' '28-day all-cause mortality' --notice-index 53 --expect-digest dac4bf59ed5f659ed5e2fc8399c8a0de7d5543f9c006785f7c717bb20ccec970 --by 'Mahmood' --judgement B3-N41 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N02**: colchicine postop af, *Postoperative atrial fibrillation*
- Served now: RR 0.65 (0.21 to 2.05), 3 trials
- After: RR 0.82, no interval (2 trials)
- Why: 1 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 42132185).
- Hash: `3690431114d72de2fa5a318f5963918028bfd930e9e491856dfd4e85d51c74fc`
- Version anchor: judgement `B3-N02`
```
python scripts/countersign_result_change.py sign 'colchicine-postop-af' 'Postoperative atrial fibrillation' --notice-index 14 --expect-digest 3690431114d72de2fa5a318f5963918028bfd930e9e491856dfd4e85d51c74fc --by 'Mahmood' --judgement B3-N02 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N03**: colchicine secondary cv prevention, *Trial-defined major coronary/cardiovascular composite*
- Served now: HR 0.81 (0.51 to 1.30), 3 trials
- After: HR 0.89, no interval (2 trials)
- Why: 1 trial(s) set aside: 1 because it is registered outside ClinicalTrials.gov, which the check cannot read (PMID 32865380).
- Hash: `e3a424b71025d731310fb187708c9c070af75263f759604c414170d043f2b908`
- Version anchor: judgement `B3-N03`
```
python scripts/countersign_result_change.py sign 'colchicine-secondary-cv-prevention' 'Trial-defined major coronary/cardiovascular composite' --notice-index 15 --expect-digest e3a424b71025d731310fb187708c9c070af75263f759604c414170d043f2b908 --by 'Mahmood' --judgement B3-N03 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N22**: glp1 ra mace t2d, *3-point major adverse cardiovascular events*
- Served now: HR 0.86 (0.81 to 0.91), 8 trials
- After: HR 0.87 (0.81 to 0.92), 7 trials
- Why: 1 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 30291013).
- Hash: `d08802f24fa082652dc45a011f29b08edd49030c2429d9c1b0062d27094ae694`
- Version anchor: judgement `B3-N22`
```
python scripts/countersign_result_change.py sign 'glp1-ra-mace-t2d' '3-point major adverse cardiovascular events' --notice-index 34 --expect-digest d08802f24fa082652dc45a011f29b08edd49030c2429d9c1b0062d27094ae694 --by 'Mahmood' --judgement B3-N22 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N35**: sglt2 primary prevention hf, *Hospitalization for heart failure*
- Served now: HR 0.70 (0.58 to 0.84), 4 trials
- After: HR 0.70 (0.54 to 0.90), 1 trial
- Why: 3 trial(s) set aside: 2 because its registry record doesn't name the review's patient group (PMID 26378978, PMID 30415602); 1 because no trial-registry record is linked to it (PMID 28605608).
- Hash: `76fc6c707cac742d9b0ab8d04fd69ef2b6a21e231ba1bec09b9c4f5af37a2704`
- Version anchor: judgement `B3-N35`
```
python scripts/countersign_result_change.py sign 'sglt2-primary-prevention-hf' 'Hospitalization for heart failure' --notice-index 47 --expect-digest 76fc6c707cac742d9b0ab8d04fd69ef2b6a21e231ba1bec09b9c4f5af37a2704 --by 'Mahmood' --judgement B3-N35 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N06**: corticosteroids cap mortality, *Hyperglycaemia*
- Served now: no pooled number (4 trials)
- After: RR 3.74, no interval (2 trials)
- Why: 2 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 21636122); 1 because its registered arms don't show the comparison (PMID 25608756).
- Hash: `5b493d9239d46094aa01528209915e28849c4185fde007a16a31dc35b09b08a3`
- Version anchor: judgement `B3-N06`
```
python scripts/countersign_result_change.py sign 'corticosteroids-cap-mortality' 'Hyperglycaemia' --notice-index 18 --expect-digest 5b493d9239d46094aa01528209915e28849c4185fde007a16a31dc35b09b08a3 --by 'Mahmood' --judgement B3-N06 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N30**: probiotics aad prevention, *Any adverse events*
- Served now: no pooled number (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 1 because its registry record doesn't name the review's patient group (PMID 39529939); 1 because no trial-registry record is linked to it (PMID 41699149).
- Hash: `a5083e8448a338085d16c78d004a89cb7ba9228227536aa8acfdd47b8d01a6f8`
- Version anchor: judgement `B3-N30`
```
python scripts/countersign_result_change.py sign 'probiotics-aad-prevention' 'Any adverse events' --notice-index 42 --expect-digest a5083e8448a338085d16c78d004a89cb7ba9228227536aa8acfdd47b8d01a6f8 --by 'Mahmood' --judgement B3-N30 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N32**: sacubitril valsartan hfref, *Composite cardiovascular death or heart-failure hospitalization*
- Served now: no pooled number (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 2 because its registered arms don't show the comparison (NCT02468232, PMID 25176015).
- Hash: `c0bf1e693beaf2b104af3e8391085c2236c2e1831c6b6740aa1add22e9176260`
- Version anchor: judgement `B3-N32`
```
python scripts/countersign_result_change.py sign 'sacubitril-valsartan-hfref' 'Composite cardiovascular death or heart-failure hospitalization' --notice-index 44 --expect-digest c0bf1e693beaf2b104af3e8391085c2236c2e1831c6b6740aa1add22e9176260 --by 'Mahmood' --judgement B3-N32 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N37**: spironolactone hfref mortality, *All-cause mortality*
- Served now: HR 0.73 (0.56 to 0.95), 3 trials
- After: HR 0.85 (0.53 to 1.36), 1 trial
- Why: 2 trial(s) set aside: 1 because no trial-registry record is linked to it (PMID 10471456); 1 because the registry says it is not randomised (PMID 21073363).
- Hash: `6b0a23a030f53c9216f960a2af3ba7ca42a5d1bf6b70b6a03df9c079a2fd96e7`
- Version anchor: judgement `B3-N37`
```
python scripts/countersign_result_change.py sign 'spironolactone-hfref-mortality' 'All-cause mortality' --notice-index 49 --expect-digest 6b0a23a030f53c9216f960a2af3ba7ca42a5d1bf6b70b6a03df9c079a2fd96e7 --by 'Mahmood' --judgement B3-N37 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

**N39**: ticagrelor vs clopidogrel acs, *Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke*
- Served now: no pooled number (2 trials)
- After: no pooled result
- Why: 2 trial(s) set aside: 2 because its registered arms don't show the comparison (PMID 19717846, PMID 26376600).
- Hash: `11cf90c04c148e604be8007ccd191118952aeac795271eeef0cee5a18e98ffcf`
- Version anchor: judgement `B3-N39`
```
python scripts/countersign_result_change.py sign 'ticagrelor-vs-clopidogrel-acs' 'Major adverse cardiovascular events: cardiovascular death, myocardial infarction, or stroke' --notice-index 51 --expect-digest 11cf90c04c148e604be8007ccd191118952aeac795271eeef0cee5a18e98ffcf --by 'Mahmood' --judgement B3-N39 --basis (Read-Host 'Describe how this notice reached you and what you read')
```

## B. Hold (1): don't sign these yet

**N27**: omega3 cardiovascular events, *Atrial fibrillation*
- Served now: no pooled result
- After: RR 1.23 (0.98 to 1.54), 1 trial
- Why: the pooled number changed with no trial entering or leaving; read the notice's own reason.
- Hold because: rehearsal hold

## C. Your ruling first (1)

**N08**: corticosteroids covid19 mortality, *Serious adverse events*
- Served now: OR 2.81 (0.11 to 74.56), 1 trial
- After: no pooled result
- Why: 1 trial(s) set aside: 1 because its registered arms don't show the comparison (PMID 34138478).
- Question: rehearsal ruling?
- If you accept, sign with:
```
python scripts/countersign_result_change.py sign 'corticosteroids-covid19-mortality' 'Serious adverse events' --notice-index 20 --expect-digest 0598e8b7596d23b2e1549a5f70625e4ef9c0eb2f98f23c58f87c8eb554937bc8 --by 'Mahmood' --judgement B3-N08 --basis (Read-Host 'Describe how this notice reached you and what you read')
```
