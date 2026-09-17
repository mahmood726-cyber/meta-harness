# Lane FN report

Base and final HEAD: `dcde90b139a8466b35b110162d160494d3bff05d`. No commit, staging, push, deployment, or external network request. Browser verification used loopback only. `harness/synth.py`, held `records.json` files, and search implementation files are unchanged.

**Implementation and verification: PASS, with the source limitations below.** 77 targeted tests passed, including live Chrome E2E. The final sweep passed for **32 of 32 held r3 topics**, preserving every primary/secondary/harms pooled row and its numeric result. The second-pass evidence audit passed **8999 field/source assertions**. This is not a claim that all clinical eligibility or outcome availability is resolved.

## Implementation

- Added `harness/trial_family.py`: registry-first family identity, deterministic synthetic IDs, typed publication roles, source spans/absence codes, registry arms and structural pair comparisons, population/analysis-set fields, lifecycle dates, retrieval origin, family eligibility, and the per-outcome ledger.
- Extended `harness/identity.py` rather than replacing PU. Acronyms alone cannot merge trials. Companion report links, DOI links, and supported held registry IDs are retained. PLATO's explicit acronym plus both registry drug arms provides a source-backed parent link.
- Multiple NCT mentions cannot bridge distinct trials. Ambiguous parents remain flagged. A unique AACT citation is rejected when a results publication predates the linked trial's start; conflicting citations remain inspectable in `source_records.identity_link_conflicts`.
- The pipeline builds family nodes from all held reports and registry records before screening, and annotates pooled rows with `family_id`. Existing pooling membership is preserved. Reports inherit the separately recorded family decision; legacy report decisions remain visibly labelled as legacy decisions.
- The page renders the family table, ledger states, lifecycle and generated count chain. Overview and PRISMA family counts use the same chain. The table scrolls within its container.
- Claim-graph identity and membership counts use family IDs. Report aliases preserve the existing RoB/GRADE source joins. These small related changes prevent family IDs from silently dropping previously held ratings.
- `scripts/trial_family_registry.py` reads local AACT only. `scripts/trial_family_sweep.py` generates the per-topic family caches and sweep. `scripts/trial_family_audit.py` independently checks held spans, dates, registry result values, and identifier separation.

Outputs: `cache/<slug>/families.json` and `family_registry.json` for the 32-topic cohort; `docs/trial_family_sweep.json`; `docs/trial_family_evidence_audit.json`; `docs/trial_family_held_plants.json`. GLP-1 also has `family_query.json` and `family_discovery.json`. Local preview: `.tmp/fn-glp1.html`; its review object is `.tmp/fn-glp1-review.json`.

## MEASURED: GLP-1 first consumer

13 publications screened + 234 registry records → 238 trial families → 143 eligible families → 8 contributing families. 143 trials met eligibility. 84 families have unresolved structural eligibility; existing pooling membership is preserved.

The expanded universe includes registry-only trials. The source inputs are the eleven current publications plus the six requested r3 entries, deduplicated to **13 publications**, and **234 independently queried registry records**. Giugliano `34526024` is classified HTA and creates no trial family. FLOW `38785209`, FREEDOM-CVO `34873344`, ELIXA `26630143`, SELECT `37952131`, and SOUL `40162642` are represented under held registry identifiers.

- Arm structures held: **11 of 11 requested GLP-1 registrations**. Source: the requested NCT set checked against `family_registry.json` and its held `design_groups`, `design_group_interventions`, and `interventions` rows.
- Typed structural proof on unchanged primary pooled rows: **0 of 8 before ? 8 of 8 after**. This metric concerns explicit family arm-pair evidence, not the absence of every older narrative contrast statement.
- Ledger coverage: **714 rows = 238 families ? 3 registered review outcomes**. Measured/reported/extractable YES: **14 of 714 outcome rows**; the rest remain UNKNOWN, not NO. A typed registry value is explicitly distinguished from a poolable randomised contrast or target HR.
- Exact current registration evidence is held for **18 of 714 outcome rows**. Prospective timing remains UNKNOWN without historical registry versions or dated protocol/SAP evidence. A current outcome entry is not proof of prespecification.
- **84 of 238 family eligibility decisions are UNKNOWN**. Harmony Outcomes remains in the unchanged pool while its family population match is unresolved; the discrepancy is exposed in `contributing_without_structural_eligibility`.

The final lane instruction, P/I/C/design only, takes precedence over the protocol's outcome-ascertainment eligibility clause. Adult, parallel-group and double-blind requirements are read from the held B-prime declaration. MACE availability never determines eligibility. The 143 eligible families therefore describe this broader P/I/C/design universe, not an assertion that all are cardiovascular outcome trials or belong in the existing pool.

### Offline concept query

Source `aact_family_concept#1`, state `RAN_OK`, run `2026-09-17T09:53:38.605737+00:00`, snapshot folder label `2026-08-30`. The folder label is an identifier, not an independently verified historical cutoff date.

Verbatim executable query specification:

```json
{"conditions.name_contains_any": ["type 2 diabetes", "type 2 diabetic", "type 2 diabetes mellitus", "diabetes mellitus, type 2", "t2d", "t2dm"], "designs.allocation": "RANDOMIZED", "interventions.intervention_type": "drug", "interventions.name_contains_any": ["liraglutide", "semaglutide", "dulaglutide", "albiglutide", "efpeglenatide", "exenatide", "lixisenatide"], "interventions.placebo_name_contains": "placebo"}
```

Funnel: **8464 condition matches ? 650 agent matches ? 240 placebo-name matches ? 234 randomized registry records retained**. No result cap. All 650 agent-matched records have retained/refused decisions and supporting rows in `family_query.json`. The source supports NOT_RUN / RAN_OK / RAN_ZERO / RAN_ERROR; an unavailable table or missing column fails closed.

Review-A name linkage is measured against exact normalized held acronyms; absence of a name match is not evidence that the trial was absent from the snapshot:

| Protocol name | Held family ID / status |
|---|---|
| SUSTAIN 1 | NCT02054897 |
| PIONEER 1 | NCT02906930 |
| AWARD-8 | NCT01769378 |
| LEAD-2 | NCT00318461 |
| Harmony 1 | NAME_TO_REGISTRY_LINK_UNRESOLVED |
| AMPLITUDE-M | NCT03353350 |
| GetGoal-P | NAME_TO_REGISTRY_LINK_UNRESOLVED |
| GetGoal-L | NCT00715624 |
| GetGoal-Mono | NCT00688701 |
| FREEDOM-1 | NAME_TO_REGISTRY_LINK_UNRESOLVED |

## MEASURED: sweep and plants

The exact topic cohort comes from `outputs/search_v2/candidates-2026-09-15r3-all.json:candidates`.

- Non-primary reports counted by the base's screened-in rows: **0 of 271 base screened-in report/registry rows** under the sweep's declared role criterion. The base already contains several PU deduplication fixes; no invented reduction is claimed.
- Open-label/crossover extensions in those rows: **0 of 271**. Held r3 extension plants are tested separately from the served base corpus.
- NO_REGISTRY_RECORD: **1614 of 2857 generated family/candidate nodes** across the 32 topics. This is a resolution flag, not proof that the underlying study was never registered.
- Structural contrasts: **51 of 99 unchanged primary pooled rows** across the cohort.
- **24 unresolved multi-parent report nodes** are explicitly flagged. Source-declared secondary NCT IDs in AACT `id_information` are retained as documented aliases, not used to union independent trial records.

| Plant | Held publication count ? family count | Verified result |
|---|---|---|
| COLCOT primary + economic report | 2 ? 1 | NCT02551094; COST_EFFECTIVENESS companion. PU already collapsed these on the base. |
| LoDoCo2 primary + secondary report | 2 ? 1 | ACTRN12614000093684 from the held abstract; SUBGROUP role from the objective and interaction-analysis spans. PU already collapsed these on the base. |
| PLATO primary + diabetes subgroup | 2 ? 1 | NCT00391872 via held PLATO acronym and both named arms. Conflicting AACT link to the trial starting in 2016 is retained as a conflict. |
| STEP 6 PMID 40189961 | 1 held named report ? 1 registry-anchored family | NCT03811574; SECONDARY_ANALYSIS. No missing primary publication is invented. |
| EMPA-KIDNEY primary + held follow-up candidate | 2 ? 1 | NCT03594110. The held follow-up title alone leaves its actual role ROLE_UNRESOLVED. |
| FREEDOM extension / DIRECT extension | Each report + its registry parent ? 1 node | Held extension titles classify EXTENSION, open-label loss flag and standalone-pool refusal; synthetic tests separately exercise the rule. |
| FREEDOM-CVO | 1 report under NCT01455896 | PRIMARY, not EXTENSION. Its coded ITCA 650 arm is held; an exenatide contrast is not guessed from the code name. |
| Synthetic three-report family | 3 ? 1 | PRIMARY, SUBGROUP, PROTOCOL; fixtures never enter generated research caches. |

The initial LoDoCo2 pre-fix plant below expected a synthetic key because it checked only the absent NCT field. Source inspection subsequently found the held ACTRN identifier and corrected the final test expectation. The original failing output is preserved unchanged, rather than rewritten to conceal that correction.

## INFERRED / unresolved scope

Role classification and clinical eligibility are deterministic interpretations of the cited typed evidence. They are not human adjudication. No new clinical treatment-effect or certainty claim is made.

**CLAIMED scope:** verification covers the named held corpus and additive software contract. Exhaustive retrieval, fully adjudicated eligibility, and complete recovery of every outcome are not claimed.

- `harness/family_screen.py` is absent on this base. The local `screen_family` implements conservative structural checks and records unknown evidence. It does not silently replace the existing synthesis membership policy.
- SC3 arm objects are retained as abstract fallback evidence. They do not manufacture complete arm pairs when the held abstract cannot establish them. Dose, route, schedule and per-arm randomized N remain typed absences when not separately established.
- Local registry date values and their raw study rows are retained; no unobserved transition date or day-level publication date is invented. Publication years explicitly retain year precision.
- Historical prospective outcome specification cannot be established from the latest snapshot alone. UNKNOWN cells cannot be read as non-measurement, non-reporting, or exclusion.
- Harmony 1, GetGoal-P and FREEDOM-1 name-to-registration linkage remains unresolved in the queried set. The lexical agent query is exactly disclosed; it is not claimed to resolve every development-code synonym.
- Non-US identities are resolved only from held identifiers, with IDENTITY_FROM_HELD_TEXT. No external registry lookup was performed.
- The EMPA-KIDNEY follow-up's parent link is held, but its extension role/contrast preservation needs more than the held title. The generic post-trial role plant is explicitly synthetic.

## Hardcode disclosure

| Component | Static | Dynamic evidence / validation |
|---|---|---|
| Registry precedence and hash encoding | Named policy; canonical JSON of sorted primary-report IDs, or flagged report-ID fallback | Held IDs and source links; synthetic IDs carry absence/ambiguity flags |
| Role and structural rules | Explicit patterns, same-background arm comparison | Matched text spans and AACT row joins |
| Requested r3 coverage IDs | Targets from the lane brief | Each exists in held r3; registry anchors checked against held records/references |
| Clinical numbers and family counts | No hardcoded effect, sample size, p-value or research result | Existing pool inputs or held registry values; sweep asserts numeric invariance |
| Test plants | Explicit synthetic fixtures where labelled | Held-paper plants are separately source-backed |
| Query timestamps / snapshot identity | No fixed result counts | Written at local acquisition, then replayed from cache |

## Validation commands and artefacts

- `python scripts/trial_family_registry.py` ? PASS, offline schema-checked ingredient collection.
- `python scripts/trial_family_sweep.py` ? PASS, 32 of 32 topics; affected topics were rechecked with `--topics` after source-identity corrections. Pool signatures exclude only claim IDs/dependency hashes, which legitimately change with family identity; input values and numeric result structures are compared.
- `python scripts/trial_family_audit.py` ? PASS, 8999 field/source assertions. `docs/trial_family_evidence_audit.json` records the exact scope.
- Targeted pytest run ? PASS, 77 tests, including family plants, identity, claim graph/disputes, RoB joins and coverage, GRADE, page contracts and `tests/test_trial_family_ui.py`. Captured final output: `.tmp/fn-final-tests.log`.
- Live Chrome E2E at `http://127.0.0.1:8000/` ? PASS: Screening tab, family table row count, headings, count-chain text, single FLOW/FREEDOM-CVO rows, no JavaScript errors. Local screenshot: `.tmp/fn-family-ui.png`.
- `python -m compileall -q` on the new module and scripts ? PASS. `git diff --check` ? PASS. HEAD remains the required base; no commit or release-state update was made.

### Per-topic measurement

Before counts are the base's deduplicated report/registry screening inputs. After counts include all held family inputs, plus the independently queried GLP-1 registry universe. These denominators differ intentionally and are separately named.

| Topic | Before publications + registry / families / eligible | After publications + registry / families / eligible / contributing | Structural proof n / pooled N |
|---|---|---|---|
| balanced-crystalloids-vs-saline-mortality | 13 + 16 / 26 / 7 | 14 + 19 / 26 / 0 / 2 | 0 / 2 |
| colchicine-postop-af | 63 + 4 / 67 / 8 | 67 + 6 / 47 / 4 / 4 | 2 / 4 |
| colchicine-recurrent-pericarditis | 47 + 6 / 53 / 3 | 50 + 10 / 41 / 3 / 2 | 2 / 2 |
| colchicine-secondary-cv-prevention | 94 + 26 / 118 / 25 | 95 + 30 / 101 / 12 / 4 | 2 / 3 |
| corticosteroids-cap-mortality | 110 + 4 / 114 / 9 | 112 + 6 / 96 / 3 / 3 | 2 / 2 |
| corticosteroids-covid19-mortality | 27 + 29 / 56 / 7 | 28 + 30 / 47 / 1 / 1 | 0 / 1 |
| dapagliflozin-hfpef-hosp | 80 + 17 / 97 / 5 | 80 + 20 / 79 / 3 / 1 | 1 / 1 |
| denosumab-vertebral-fracture | 71 + 0 / 71 / 1 | 71 + 0 / 54 / 0 / 1 | 1 / 1 |
| doac-vte-recurrence | 210 + 24 / 234 / 5 | 219 + 30 / 213 / 1 / 5 | 0 / 6 |
| dpp4-mace-t2d | 8 + 30 / 38 / 5 | 8 + 30 / 37 / 5 / 3 | 2 / 3 |
| empagliflozin-hfpef-hosp | 80 + 20 / 100 / 3 | 80 + 21 / 93 / 1 / 1 | 1 / 1 |
| esketamine-trd-madrs | 109 + 27 / 134 / 4 | 117 + 30 / 103 / 2 / 4 | 4 / 4 |
| finerenone-ckd-t2d-renal | 5 + 18 / 23 / 5 | 5 + 21 / 22 / 4 / 2 | 2 / 2 |
| glp1-ra-mace-t2d | 11 + 0 / 11 / 9 | 13 + 234 / 238 / 143 / 8 | 8 / 8 |
| iv-iron-hfref-hosp | 31 + 8 / 39 / 9 | 31 + 9 / 29 / 2 / 2 | 1 / 2 |
| melatonin-primary-insomnia-sol | 119 + 7 / 126 / 8 | 120 + 8 / 92 / 3 / 1 | 1 / 1 |
| metformin-pcos-ovulation | 125 + 29 / 153 / 7 | 125 + 30 / 85 / 8 / 3 | 0 / 3 |
| noac-vs-warfarin-af-stroke | 6 + 29 / 35 / 7 | 6 + 30 / 34 / 0 / 4 | 0 / 4 |
| omega3-cardiovascular-events | 84 + 30 / 113 / 20 | 86 + 30 / 105 / 2 / 7 | 3 / 7 |
| pcsk9-mace | 9 + 3 / 12 / 5 | 9 + 3 / 11 / 2 / 3 | 3 / 3 |
| probiotics-aad-prevention | 444 + 24 / 468 / 57 | 449 + 30 / 404 / 0 / 16 | 3 / 16 |
| sacubitril-valsartan-hfref | 52 + 29 / 81 / 7 | 57 + 30 / 68 / 1 / 2 | 0 / 2 |
| semaglutide-obesity-mace | 64 + 2 / 66 / 1 | 64 + 2 / 41 / 0 / 1 | 1 / 1 |
| semaglutide-obesity-weight | 115 + 28 / 143 / 7 | 120 + 30 / 104 / 20 / 2 | 2 / 2 |
| sglt2-ckd-progression | 5 + 30 / 35 / 9 | 5 + 30 / 34 / 7 / 3 | 3 / 3 |
| sglt2-hfref-hosp-cvdeath | 4 + 14 / 18 / 5 | 4 + 14 / 17 / 2 / 2 | 2 / 2 |
| sglt2-primary-prevention-hf | 276 + 18 / 294 / 6 | 300 + 30 / 270 / 6 / 4 | 2 / 4 |
| spironolactone-hfref-mortality | 219 + 7 / 226 / 3 | 221 + 7 / 203 / 1 / 3 | 1 / 3 |
| statins-primary-prevention-elderly | 6 + 22 / 28 / 4 | 6 + 23 / 27 / 1 / 2 | 1 / 2 |
| ticagrelor-vs-clopidogrel-acs | 30 + 2 / 32 / 3 | 30 + 2 / 25 / 0 / 2 | 0 / 2 |
| tocilizumab-covid19-mortality | 20 + 30 / 50 / 12 | 20 + 30 / 49 / 4 / 3 | 0 / 1 |
| tranexamic-acid-pph | 49 + 27 / 76 / 4 | 54 + 30 / 62 / 5 / 1 | 1 / 1 |

## Pre-fix behavioral plants (verbatim)

Command: `python -m pytest tests/test_trial_family.py -q --tb=short`

```text
FFFFFFFFFFF                                                              [100%]
================================== FAILURES ===================================
_ test_held_companion_attaches_to_registry_parent[colchicine-secondary-cv-prevention-32407460-31733140] _
tests\test_trial_family.py:35: in test_held_companion_attaches_to_registry_parent
    assert fs[0]['family_id'] == parent_record['nct']
E   AssertionError: assert 'COLCOT' == 'NCT02551094'
E     
E     - NCT02551094
E     + COLCOT
_ test_held_companion_attaches_to_registry_parent[colchicine-secondary-cv-prevention-34446156-32865380] _
tests\test_trial_family.py:37: in test_held_companion_attaches_to_registry_parent
    assert fs[0]['family_id'].startswith('SYN-')
E   AssertionError: assert False
E    +  where False = <built-in method startswith of str object at 0x000001624F0BC420>('SYN-')
E    +    where <built-in method startswith of str object at 0x000001624F0BC420> = 'LoDoCo2'.startswith
______________ test_synthetic_three_reports_one_node_three_roles ______________
tests\test_trial_family.py:45: in test_synthetic_three_reports_one_node_three_roles
    assert {r['role'] for r in fs[0]['reports']} == {'PRIMARY', 'SUBGROUP', 'PROTOCOL'}
E   AssertionError: assert {'primary', 'protocol'} == {'PRIMARY', '...', 'SUBGROUP'}
E     
E     Extra items in the left set:
E     'primary'
E     'protocol'
E     Extra items in the right set:
E     'SUBGROUP'
E     'PRIMARY'
E     'PROTOCOL'
E     Use -v to get more diff
____ test_publication_role_plants[FREEDOM open-label extension-EXTENSION] _____
tests\test_trial_family.py:58: in test_publication_role_plants
    assert r['role'] == expected
E   AssertionError: assert 'primary' == 'EXTENSION'
E     
E     - EXTENSION
E     + primary
_ test_publication_role_plants[DIRECT 3-year open-label continuation-EXTENSION] _
tests\test_trial_family.py:58: in test_publication_role_plants
    assert r['role'] == expected
E   AssertionError: assert 'primary' == 'EXTENSION'
E     
E     - EXTENSION
E     + primary
_ test_publication_role_plants[FREEDOM-CVO randomized controlled trial-PRIMARY] _
tests\test_trial_family.py:58: in test_publication_role_plants
    assert r['role'] == expected
E   AssertionError: assert 'primary' == 'PRIMARY'
E     
E     - PRIMARY
E     + primary
__ test_publication_role_plants[STEP 6 post-hoc analysis-SECONDARY_ANALYSIS] __
tests\test_trial_family.py:58: in test_publication_role_plants
    assert r['role'] == expected
E   AssertionError: assert 'secondary' == 'SECONDARY_ANALYSIS'
E     
E     - SECONDARY_ANALYSIS
E     + secondary
_______ test_publication_role_plants[PLATO subgroup analysis-SUBGROUP] ________
tests\test_trial_family.py:58: in test_publication_role_plants
    assert r['role'] == expected
E   AssertionError: assert 'primary' == 'SUBGROUP'
E     
E     - SUBGROUP
E     + primary
__ test_publication_role_plants[EMPA-KIDNEY post-trial follow-up-EXTENSION] ___
tests\test_trial_family.py:58: in test_publication_role_plants
    assert r['role'] == expected
E   AssertionError: assert 'primary' == 'EXTENSION'
E     
E     - EXTENSION
E     + primary
______________________ test_unknown_role_is_not_primary _______________________
tests\test_trial_family.py:63: in test_unknown_role_is_not_primary
    assert build([{'id': 'fixture-unknown'}])[0]['reports'][0]['role'] == 'ROLE_UNRESOLVED'
E   AssertionError: assert 'primary' == 'ROLE_UNRESOLVED'
E     
E     - ROLE_UNRESOLVED
E     + primary
___________ test_acronym_without_shared_arms_does_not_merge_trials ____________
tests\test_trial_family.py:66: in test_acronym_without_shared_arms_does_not_merge_trials
    assert len(build([{'id':'fixture-a','acronym':'SAME'}, {'id':'fixture-b','acronym':'SAME'}])) == 2
E   AssertionError: assert 1 == 2
E    +  where 1 = len([{'family_id': 'SAME', 'reports': [{'report_id': 'fixture-a', 'role': 'primary'}, {'report_id': 'fixture-b', 'role': 'primary'}]}])
E    +    where [{'family_id': 'SAME', 'reports': [{'report_id': 'fixture-a', 'role': 'primary'}, {'report_id': 'fixture-b', 'role': 'primary'}]}] = build([{'acronym': 'SAME', 'id': 'fixture-a'}, {'acronym': 'SAME', 'id': 'fixture-b'}])
=========================== short test summary info ===========================
FAILED tests/test_trial_family.py::test_held_companion_attaches_to_registry_parent[colchicine-secondary-cv-prevention-32407460-31733140]
FAILED tests/test_trial_family.py::test_held_companion_attaches_to_registry_parent[colchicine-secondary-cv-prevention-34446156-32865380]
FAILED tests/test_trial_family.py::test_synthetic_three_reports_one_node_three_roles
FAILED tests/test_trial_family.py::test_publication_role_plants[FREEDOM open-label extension-EXTENSION]
FAILED tests/test_trial_family.py::test_publication_role_plants[DIRECT 3-year open-label continuation-EXTENSION]
FAILED tests/test_trial_family.py::test_publication_role_plants[FREEDOM-CVO randomized controlled trial-PRIMARY]
FAILED tests/test_trial_family.py::test_publication_role_plants[STEP 6 post-hoc analysis-SECONDARY_ANALYSIS]
FAILED tests/test_trial_family.py::test_publication_role_plants[PLATO subgroup analysis-SUBGROUP]
FAILED tests/test_trial_family.py::test_publication_role_plants[EMPA-KIDNEY post-trial follow-up-EXTENSION]
FAILED tests/test_trial_family.py::test_unknown_role_is_not_primary - Asserti...
FAILED tests/test_trial_family.py::test_acronym_without_shared_arms_does_not_merge_trials
11 failed in 1.13s
```
