# Identifier Scope Evidence (2026-09-14)

**Fix state (orthogonal fields rule): LANDED / NONE / CORPUS / STALE** - generated from TRANCHE-identifier-scope; stale dependencies: harness/gate_scorecard.py, harness/invalidation.py, harness/page.py, +5 more

Base commit: `4a2283e9f6bca55101bc918bd5319a963ca7e4ec`.

Gate scorecard known-miss timestamp: `2026-09-14T23:30:00Z`.

This tranche adds a structural object-derived identifier-scope detector for the exact bug class where a page identifier names one intervention agent but the included pool is class-level. The page identifier remains unchanged; the page now carries an absent/STALE block when the object says the identifier is too narrow for the pool.

## Evidence Files

| File | What it shows |
| --- | --- |
| `01-prefix-detector-absent.txt` | Prefix proof that no identifier-scope detector/reason/block existed at the lane base. |
| `02-corpus-32.txt` | Object-derived 32-topic census after regeneration. |
| `03-spironolactone-page-marked.txt` | Spironolactone object, STALE reason, rendered identifier-scope block, and corrected search sentence. |
| `04-mis-attribution-corrected.txt` | Source before/after snippets for the J-EMPHASIS-HF and index wording corrections. |

## 32-Topic Census

Verdict counts: `MATCH`=16, `NOT_APPLICABLE`=15, `SINGLE_AGENT_OVER_CLASS_POOL`=1.

| Slug | Level | Identifier agent | Verdict | Pooled-agent summary | Unresolved |
| --- | --- | --- | --- | --- | ---: |
| balanced-crystalloids-vs-saline-mortality | CLASS | n/a | NOT_APPLICABLE | CLASS:balanced crystalloid=2; CLASS:balanced multielectrolyte=1; CLASS:balanced solution=1; CLASS:buffered crystalloid=1; plasma-lyte=3 | 0 |
| colchicine-postop-af | AGENT | colchicine | MATCH | colchicine=8 | 0 |
| colchicine-recurrent-pericarditis | AGENT | colchicine | MATCH | colchicine=3 | 0 |
| colchicine-secondary-cv-prevention | AGENT | colchicine | MATCH | colchicine=29 | 0 |
| corticosteroids-cap-mortality | CLASS | n/a | NOT_APPLICABLE | CLASS:corticosteroid=2; dexamethasone=2; hydrocortisone=3; methylprednisolone=1; prednisone=1 | 0 |
| corticosteroids-covid19-mortality | CLASS | n/a | NOT_APPLICABLE | dexamethasone=4; hydrocortisone=3; methylprednisolone=1 | 0 |
| dapagliflozin-hfpef-hosp | AGENT | dapagliflozin | MATCH | dapagliflozin=5 | 0 |
| denosumab-vertebral-fracture | AGENT | denosumab | MATCH | denosumab=1 | 0 |
| doac-vte-recurrence | CLASS | n/a | NOT_APPLICABLE | apixaban=1; dabigatran=2; edoxaban=1; rivaroxaban=2 | 0 |
| dpp4-mace-t2d | CLASS | n/a | NOT_APPLICABLE | CLASS:DPP-4=1; alogliptin=1; linagliptin=1; saxagliptin=1; sitagliptin=1 | 0 |
| empagliflozin-hfpef-hosp | AGENT | empagliflozin | MATCH | empagliflozin=4 | 0 |
| esketamine-trd-madrs | AGENT | esketamine | MATCH | esketamine=6 | 0 |
| finerenone-ckd-t2d-renal | AGENT | finerenone | MATCH | finerenone=6 | 0 |
| glp1-ra-mace-t2d | CLASS | n/a | NOT_APPLICABLE | albiglutide=1; dulaglutide=1; efpeglenatide=1; exenatide=1; liraglutide=1; lixisenatide=1; semaglutide=3 | 0 |
| iv-iron-hfref-hosp | CLASS | n/a | NOT_APPLICABLE | ferric carboxymaltose=7; ferric derisomaltose=1; iron sucrose=1 | 0 |
| melatonin-primary-insomnia-sol | AGENT | melatonin | MATCH | melatonin=9 | 0 |
| metformin-pcos-ovulation | AGENT | metformin | MATCH | metformin=9 | 0 |
| noac-vs-warfarin-af-stroke | CLASS | n/a | NOT_APPLICABLE | CLASS:NOAC=1; apixaban=1; dabigatran=2; edoxaban=4; rivaroxaban=1 | 0 |
| omega3-cardiovascular-events | CLASS | n/a | NOT_APPLICABLE | CLASS:n-3 fatty=6; CLASS:omega 3=1; CLASS:omega-3=6; CLASS:polyunsaturated fatty acid=6; fish oil=1; icosapent ethyl=2 | 0 |
| pcsk9-mace | CLASS | n/a | NOT_APPLICABLE | alirocumab=1; evolocumab=1 | 0 |
| probiotics-aad-prevention | CLASS | n/a | NOT_APPLICABLE | BIO-K=2; CLASS:probiotic=29; CLASS:synbiotic=1; bacillus=1; lactobacillus=19; saccharomyces=8 | 0 |
| sacubitril-valsartan-hfref | AGENT | sacubitril-valsartan | MATCH | sacubitril-valsartan=7 | 0 |
| semaglutide-obesity-mace | AGENT | semaglutide | MATCH | semaglutide=1 | 0 |
| semaglutide-obesity-weight | AGENT | semaglutide | MATCH | semaglutide=14 | 0 |
| sglt2-ckd-progression | CLASS | n/a | NOT_APPLICABLE | CLASS:SGLT2=3; canagliflozin=1; dapagliflozin=2; empagliflozin=2 | 0 |
| sglt2-hfref-hosp-cvdeath | CLASS | n/a | NOT_APPLICABLE | CLASS:SGLT2=1; dapagliflozin=1; empagliflozin=1 | 0 |
| sglt2-primary-prevention-hf | CLASS | n/a | NOT_APPLICABLE | CLASS:SGLT2=2; canagliflozin=2; dapagliflozin=8; empagliflozin=7; ertugliflozin=1 | 0 |
| spironolactone-hfref-mortality | AGENT | spironolactone | SINGLE_AGENT_OVER_CLASS_POOL | eplerenone=2; spironolactone=1 | 0 |
| statins-primary-prevention-elderly | CLASS | n/a | NOT_APPLICABLE | CLASS:statin=5 | 0 |
| ticagrelor-vs-clopidogrel-acs | AGENT | ticagrelor | MATCH | ticagrelor=3 | 0 |
| tocilizumab-covid19-mortality | AGENT | tocilizumab | MATCH | tocilizumab=12 | 0 |
| tranexamic-acid-pph | AGENT | tranexamic acid | MATCH | tranexamic acid=4 | 0 |

## Detector Limits

This detector is intentionally narrow. It does not validate population or outcome axes in the identifier, does not flag a class-level identifier over a single-agent pool, and depends on the intervention declaration authored in the topic config/protocol rather than an independent ontology.
