# LANE HM2 report

**MEASURED:** 44 of 45 base harm-debt items resolved in held inputs; 1 remains unresolved. Four pages pass the full publication gate; GLP-1 and postoperative AF remain refused. No commit, push, network retrieval, or gate weakening.

`git rev-parse HEAD`: `f6f7b14c820bdadd258122ac0bb54c7e4d2a989a` (matches the supplied WIP base). The initial worktree contained only the untracked lane prompt/log/PID files.

## Per-page accounting

Denominator N is the base `result.known_reported_not_yet_extracted` trial × harm list, captured before changes in [HM2_base_debt.json](outputs/handover/HM2_base_debt.json). Counts describe source adjudications, not pooled k.

| Page | Resolved / N | Counts | Effect + CI | Typed refusal | Spurious signal | Unresolved |
|---|---:|---:|---:|---:|---:|---:|
| glp1-ra-mace-t2d | 14 / 15 | 1 | 0 | 11 | 2 | 1 |
| colchicine-recurrent-pericarditis | 6 / 6 | 1 | 0 | 5 | 0 | 0 |
| colchicine-secondary-cv-prevention | 6 / 6 | 0 | 0 | 6 | 0 | 0 |
| finerenone-ckd-t2d-renal | 6 / 6 | 0 | 0 | 6 | 0 | 0 |
| pcsk9-mace | 6 / 6 | 1 | 0 | 2 | 3 | 0 |
| colchicine-postop-af | 6 / 6 | 1 | 0 | 5 | 0 | 0 |

The postoperative END-AF Low Dose discontinuation count is extracted into verified input (one participant per arm, arm sizes 81/71), but the enforced analysis-set contract refuses its use in the synthesis. CORP-2 explicitly spells its GI counts as “nine”; transcription is 9/120 per arm. REWIND is 2347/4949 versus 1687/4952; ODYSSEY LONG TERM injection reactions are 91/1550 versus 33/788 from the local registry safety population. No count was obtained by multiplying a percentage by n.

No effect+CI was substituted for a broader composite harm: for example COCS reports diarrhea and abdominal-pain ORs separately, not a unique-patient overall GI outcome. Likewise serious/non-serious AACT event rows were not summed where participant overlap is unknown.

## Full gate results (verbatim)

Each page was rebuilt using `python scripts/build_topic.py <slug> --now 2026-09-11`, with outbound socket connections blocked in the build process, then checked with `harness.gate.gate_page`, the same function used by `verify_all.limb_gate_every_page`. The final pass used frozen code. Shared generated `docs/index.html` and `registry/blind_map.json` were restored byte-for-byte; only this lane’s canonical and corresponding blind pages remain changed.

```text
glp1-ra-mace-t2d: REFUSED
L1: HARMS_INCOMPLETE -- Adverse events leading to discontinuation: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (27295427) among 5 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
colchicine-recurrent-pericarditis: PASS
colchicine-secondary-cv-prevention: PASS
finerenone-ckd-t2d-renal: PASS
pcsk9-mace: PASS
colchicine-postop-af: REFUSED
L1: primary outcome 'Postoperative atrial fibrillation' has no pooled result (k=None) — a page whose primary claim is absent must not publish
```

## Before/after refusal plant

The planted fixture is explicitly synthetic and never enters review data. It was executed on the untouched base implementation before adding recovery support. The gate output was:

```text
BASE FIXTURE:
L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (1) among 1 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
```

After supplying a typed refusal with its verbatim narrative span, the same gate function returns no violations. The regression asserts both states and prints `RESOLVED FIXTURE: PASS`; full output is in [HM2_validation.json](outputs/handover/HM2_validation.json).

## Remaining GLP-1 item and source boundary

**UNRESOLVED — PMID 27295427 (LEADER), adverse events leading to discontinuation.** The abstract is narrative-only. Held publication full text `cache/glp1-ra-mace-t2d/ft_27295427.txt`, Table 2, contains liraglutide/placebo denominators 4668/4672 and any-adverse-event discontinuation counts 444/339. These were located on disk, not recalled. The lane’s GLP-1-specific instruction restricts evidence to a “level-1 span (abstract)” or the held FDA texts; no reply expanding that source scope was received. Therefore no narrative refusal was used to hide these known extractable full-text values, and the item remains unresolved. This is a source-scope blocker, not a claim that the counts are unavailable.

ELIXA’s FDA Table 55 gives separate symptom counts, not a deduplicated overall GI count. FDA Table 17’s discontinuation counts exclude MACE+; the inclusive outcome is percentages only. Both receive cited definition refusals. FREEDOM-CVO’s FDA document was inspected (including its CLP-107 disposition table) but FREEDOM-CVO is not in the base 15-item harm-debt list; no trial was added to membership.

| Held FDA document | Document SHA-256 from regulatory manifest | Measured extracted-text SHA-256 |
|---|---|---|
| FDA_NDA208471_StatR_2016 | `cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38` | `952b8088e14b457d97364f13bb0f9407803bf875faed5fa30d995972e2687a26` |
| FDA_NDA208471_MedR_2016 | `80d91f3cdaea588b845de18d3ef9b254936ec8768305bd91e554d9de3f39acc3` | `448150daf6667013259e6e4c741aba8a60153af651d5d04886455d3b8e595c22` |
| FDA_NDA209053_EMDAC_briefing_2023 | `719362393b2029c2d4a081ab1bc69647034b2168efe686808d419f16177f0103` | `e27b9985959e139b9c84f15b7e364d3c82a2fed861819e2b777f6b3f5aef963e` |

All three extracted-text hashes match `regulatory_sources_glp1.json`. The medical-review PDF hash is cited from that manifest; the off-tree PDF itself was not rehashed.

## Postoperative protocol enforcement

`topics/colchicine-postop-af.json` now executes the stated double-blind OR placebo-controlled requirement, retains ITT, restores the protocol’s in-hospital/index-admission window, and opts into pre-pool admission enforcement. The protocol prose is unchanged. No screening or membership implementation was edited. The required config change makes open-label candidates fail the existing screen.

| Primary trial row | Analysis set derived by existing chain | Follow-up derived by existing chain | Final row |
|---|---|---|---|
| 42132185 | AVAILABLE_CASE (FAIL) | 14 days / postoperative admission (FAIL) | `TRIAL_FAILS_CONTRACT` / `REFUSED_ON_EVIDENCE`; not pooled |
| 32720823 | not_stated (FAIL) | in-hospital / until discharge (PASS) | `TRIAL_FAILS_CONTRACT` / `REFUSED_ON_EVIDENCE`; not pooled |
| 25172965 | not_stated (FAIL) | 3 months (FAIL) | `TRIAL_FAILS_CONTRACT` / `REFUSED_ON_EVIDENCE`; not pooled |

Candidate analysis sets are rendered as **mixed / trial-defined**, with per-trial values and contract verdicts. There is no pooled compatibility key or primary estimate after those refusals. The chain’s divergences and pooled-trial failures are empty; the unchanged primary-result gate correctly refuses publication at k=0. The existing chain’s follow-up derivations were retained, not independently rewritten as new clinical claims.

## Input contract and tests

Verified arms/effects accept legacy singleton objects and exact-outcome lists per PMID. Duplicate same-outcome entries fail closed. Outcome selection occurs before override precedence; missing-primary enrichment explicitly selects the configured primary outcome. Typed adjudications preserve the cited span and code even when an efficacy-strand annotation changes `absent_kind`. Spurious signals remain refused but no longer inflate the source-reporting count. Written count words are recognized without percentage inversion.

Every new override has a matching audit judgment and evidence entry. The audit scanner and its test enumerate list entries as well as legacy singletons.

Required test command and verbatim result:

```text
python -m pytest tests/test_harms_recovery.py tests/test_override_audit.py -q
....F                                                                    [100%]
================================== FAILURES ===================================
_____________ test_override_audit_covers_every_committed_override _____________

    def test_override_audit_covers_every_committed_override():
        audited = json.loads(AUDIT.read_text(encoding="utf-8"))
        audited_by_key = {_key(row): row for row in audited}
        required = {_key(row) for row in _override_rows_in_cache()}
    
        missing = sorted(required - set(audited_by_key))
        extra = sorted(set(audited_by_key) - required)
>       assert not missing, "override(s) missing from audit: " + repr(missing)
E       AssertionError: override(s) missing from audit: [('esketamine-trd-madrs', 'verified_arms.json', 'NCT02417064', 'Observed-case Day-28 raw change-score MADRS MD'), ('sglt2-ckd-progression', 'verified_effects.json', '32970396', 'Trial-defined primary cardiorenal composite'), ('sglt2-ckd-progression', 'verified_effects.json', '36331190', 'Trial-defined primary cardiorenal composite')]
E       assert not [('esketamine-trd-madrs', 'verified_arms.json', 'NCT02417064', 'Observed-case Day-28 raw change-score MADRS MD'), ('sg...osite'), ('sglt2-ckd-progression', 'verified_effects.json', '36331190', 'Trial-defined primary cardiorenal composite')]

tests\test_override_audit.py:35: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
1 failed, 4 passed in 3.52s
```

The only required-suite failure is the same three pre-existing out-of-lane audit omissions (esketamine-trd-madrs; sglt2-ckd-progression ×2). They were not edited because the prompt permits fixing those three only if they belong to this lane. The HM2-specific audit coverage test passes.

```text
python -m pytest tests/test_hm2_contract.py tests/test_missing_effect.py tests/test_source_hierarchy.py tests/test_source_hierarchy_regression.py tests/test_published_rate_verify.py tests/test_compat_underlying.py tests/test_eligibility_chain.py tests/test_page.py tests/test_honest_states_renderable.py tests/test_arm_object.py -q
........................................................................ [100%]
72 passed in 79.54s (0:01:19)
```

```text
python -m pytest tests/test_hm2_ui.py -q
.                                                                        [100%]
1 passed in 4.30s
```

```text
python -m pytest tests/test_hm2_contract.py -q -s
BASE FIXTURE:
L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 1 known reported outcome(s) unresolved (1) among 1 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
RESOLVED FIXTURE: PASS
.......
7 passed in 2.37s
```

```text
python -m pytest tests/test_hm2_contract.py tests/test_page.py -q
..............                                                           [100%]
14 passed in 2.45s
```

A broader run including `tests/test_gate.py` produced 47 passed / 1 failed: its real NOAC page replay test fails outside HM2. Read-only replay with every modified harness module replaced in memory by its HEAD version confirmed the identical baseline failure:

```json
{
  "slug": "noac-vs-warfarin-af-stroke",
  "baseline_replay_sha256": "3dc7e1968a5474d4b68fb4a77f9027dbab8ae8d01205699a13753b3498396dab",
  "committed_sha256": "ffb0f8086fbba765655c777aebb9665cb3914e3ca4d518e90478e4a46a9579ca"
}
```

Browser verification uses the locally installed browser, binds the test server to `127.0.0.1:8000`, blocks all nonlocal page requests, opens all six absolute review URLs, clicks each Harms tab, checks all base-debt PMIDs and JavaScript errors, and checks the postoperative mixed analysis-set table. The created browser is closed specifically; no global browser cleanup.

## Evidence and second-pass review

- [Per-item verbatim spans, typed decisions, provenance and document references](outputs/handover/HM2_item_evidence.json).
- [Base debt denominators and source signals](outputs/handover/HM2_base_debt.json).
- [Held-file hashes, local AACT table coverage and relevant rows](outputs/handover/HM2_source_inventory.json).
- [Raw build and gate outputs](outputs/handover/HM2_build_gate.json).
- [Validation outputs](outputs/handover/HM2_validation.json).

Second-pass review checked PMID/outcome identity against held records, arm direction and safety denominators, symptom-vs-overall definitions, refusal spans against source bytes, regulatory text digests, and source-level limits. AACT joins use each row’s NCT and group IDs within the same held snapshot; numeric IDs were not guessed. Source dates are retained as source facts; the requested build date is 2026-09-11, not a claim that all held sources existed then. No new research claim was inferred from another meta-analysis.

## Static versus dynamic disclosure

| Component | Static / dynamic | What is asserted |
|---|---|---|
| Item decisions and source-to-field transcription | Static, hand-adjudicated | Endpoint-specific reasons and explicit counts with verbatim held evidence |
| Base N, source hashes, source tables, rendered results and gate outputs | Dynamic, measured | Read from disk and regenerated offline |
| Admission values | Dynamic execution of existing chain | Existing chain includes PMID-specific derivations; these were not silently treated as newly source-validated clinical measurements |
| Regression plants | Static synthetic | Isolated test fixtures only; never scientific outputs |

**MEASURED:** tests, gate results, held spans/hashes and per-page accounting above. **INFERRED:** compatibility/definition judgments, explicitly explained per item. **CLAIMED:** no release readiness, no full source-retrieval completeness, no guarantee that a refused harm is absent from the trial.

## Item-by-item decisions

Every row below links through the companion evidence JSON to its full verbatim span. “Typed refusal” means the registered endpoint cannot be taken from that cited material; it does not mean zero events.

### glp1-ra-mace-t2d

| PMID | Outcome | Resolution | Source-backed reason |
|---|---|---|---|
| 31185157 | Gastrointestinal adverse events | typed refusal | The abstract reports more gastrointestinal events leading to discontinuation with oral semaglutide but gives no harm count or harm effect with confidence interval; registry-only values do not meet this lane's GLP-1 level-1-abstract/level-2-FDA requirement. |
| 27633186 | Gastrointestinal adverse events | typed refusal | The abstract describes more adverse-event discontinuations, mainly gastrointestinal, without arm-specific harm counts or a harm effect with confidence interval. |
| 27295427 | Gastrointestinal adverse events | typed refusal | The abstract identifies gastrointestinal events as the commonest reason for discontinuation, but neither it nor the held full-text discontinuation-only symptom rows supplies a unique-patient count for all gastrointestinal adverse events. |
| 34215025 | Gastrointestinal adverse events | typed refusal | The abstract says diarrhea, constipation, nausea, vomiting or bloating occurred more frequently with efpeglenatide but provides no gastrointestinal counts or harm effect with confidence interval. |
| 31189511 | Gastrointestinal adverse events | extracted (counts) | REWIND abstract explicitly states both randomized arm sizes and participants reporting a gastrointestinal adverse event; no percentage inversion. |
| 30291013 | Gastrointestinal adverse events | typed refusal | The abstract reports pancreatitis, cancers and other serious adverse events, not the registered overall gastrointestinal adverse-event outcome; those distinct event counts cannot be pooled as all gastrointestinal events. |
| 28910237 | Gastrointestinal adverse events | typed refusal | The abstract reports specific pancreatic events and serious adverse events, not overall gastrointestinal events; the held full text states that only serious adverse events were collected, so serious-only rows cannot represent all gastrointestinal events. |
| 26630143 | Gastrointestinal adverse events | typed refusal | FDA ELIXA Table 55 supplies separate nausea, vomiting, diarrhea and constipation counts, not a unique-patient overall gastrointestinal total; overlapping symptom counts cannot be added. |
| 31185157 | Adverse events leading to discontinuation | typed refusal | The abstract reports more gastrointestinal events leading to discontinuation with oral semaglutide but gives no harm count or harm effect with confidence interval; registry-only values do not meet this lane's GLP-1 level-1-abstract/level-2-FDA requirement. |
| 27633186 | Adverse events leading to discontinuation | typed refusal | The abstract describes more adverse-event discontinuations, mainly gastrointestinal, without arm-specific harm counts or a harm effect with confidence interval. |
| 27295427 | Adverse events leading to discontinuation | unresolved | Held publication full text Table 2 reports 444 versus 339 adverse-event discontinuations with denominators 4668/4672, but the abstract is narrative only; no entry is forced while the GLP-1-specific abstract/FDA source restriction excludes that full-text extraction. |
| 31189511 | Adverse events leading to discontinuation | spurious signal | The fired span reports gastrointestinal adverse-event incidence and mortality, not treatment discontinuation; the abstract provides no adverse-event discontinuation result. |
| 30291013 | Adverse events leading to discontinuation | spurious signal | The discontinuation sentence describes the scheduled final study visit after endpoint accrual, not discontinuation caused by adverse events. |
| 28910237 | Adverse events leading to discontinuation | typed refusal | The abstract gives only a general serious-adverse-event comparison, and held full-text discontinuation counts are restricted to serious adverse events rather than discontinuations from any adverse event. |
| 26630143 | Adverse events leading to discontinuation | typed refusal | FDA ELIXA Table 17 gives 347/3031 versus 217/3032 discontinuations excluding MACE+ events, whereas the inclusive definition is reported only as 13.7% versus 10.1%; the restricted count is not the registered any-adverse-event discontinuation outcome and inclusive counts cannot be inferred. |

### colchicine-recurrent-pericarditis

| PMID | Outcome | Resolution | Source-backed reason |
|---|---|---|---|
| 24694983 | Adverse events (gastrointestinal) | extracted (counts) | CORP-2 explicitly reports nine gastrointestinal-intolerance patients in each group and 120 assigned per arm; nine is transcribed as integer 9. |
| 23992557 | Adverse events (gastrointestinal) | typed refusal | The abstract describes similar overall adverse-effect rates but gives no gastrointestinal-specific count or effect with confidence interval; no linked results rows are held in the local AACT snapshot. |
| 21873705 | Adverse events (gastrointestinal) | typed refusal | The abstract describes similar overall adverse-effect rates but gives no gastrointestinal-specific count or effect with confidence interval; no linked results rows are held in the local AACT snapshot. |
| 24694983 | Treatment discontinuation | typed refusal | The abstract describes similar study-drug discontinuation or withdrawal rates but provides no discontinuation count or effect with confidence interval; no linked results rows are held in the local AACT snapshot. |
| 23992557 | Treatment discontinuation | typed refusal | The abstract describes similar study-drug discontinuation or withdrawal rates but provides no discontinuation count or effect with confidence interval; no linked results rows are held in the local AACT snapshot. |
| 21873705 | Treatment discontinuation | typed refusal | The abstract describes similar study-drug discontinuation or withdrawal rates but provides no discontinuation count or effect with confidence interval; no linked results rows are held in the local AACT snapshot. |

### colchicine-secondary-cv-prevention

| PMID | Outcome | Resolution | Source-backed reason |
|---|---|---|---|
| 31733140 | Gastrointestinal adverse effects | typed refusal | The abstract reports diarrhea percentages only; local AACT contains separate diarrhea AE/SAE rows rather than a unique-patient total for all gastrointestinal adverse effects, so those component counts cannot stand for the registered outcome. |
| 40263680 | Gastrointestinal adverse effects | typed refusal | The abstract reports overall side effects as 21.6% versus 15%, not gastrointestinal-specific counts or an effect with confidence interval; counts are not reconstructed from percentages. |
| 34420373 | Gastrointestinal adverse effects | typed refusal | The abstract reports gastrointestinal adverse events as 34% versus 11% without explicit event counts or a harm effect with confidence interval; no linked local AACT results are held and counts cannot be inferred from rounded percentages. |
| 23500260 | Gastrointestinal adverse effects | typed refusal | The abstract says treatment-related adverse events were largely gastrointestinal but gives no gastrointestinal count or effect with confidence interval. |
| 1593057 | Gastrointestinal adverse effects | typed refusal | The abstract reports a 6.9% dropout rate due to unspecified side effects in the colchicine arm only, not per-arm gastrointestinal adverse events. |
| 39555823 | Gastrointestinal adverse effects | typed refusal | The abstract reports diarrhea percentages, not the overall gastrointestinal adverse-effect outcome or explicit harm counts; no linked local AACT results are held and percentages cannot supply an assumed count. |

### finerenone-ckd-t2d-renal

| PMID | Outcome | Resolution | Source-backed reason |
|---|---|---|---|
| 33264825 | Hyperkalemia | typed refusal | The abstract reports hyperkalemia-related discontinuation rather than all hyperkalemia; local AACT splits serious and non-serious hyperkalemia with possible participant overlap, so their counts cannot be summed into a unique-patient total. |
| 34449181 | Hyperkalemia | typed refusal | The abstract reports hyperkalemia-related discontinuation rather than all hyperkalemia; local AACT splits serious and non-serious hyperkalemia with possible participant overlap, so their counts cannot be summed into a unique-patient total. |
| 26325557 | Hyperkalemia | typed refusal | The abstract reports hyperkalemia-related discontinuation across several finerenone doses with a shared placebo, including zero at 10 mg and percentages at other doses; no prespecified dose selection or compatible overall hyperkalemia total is supplied. |
| 33264825 | Hyperkalemia-related treatment discontinuation | typed refusal | The abstract reports hyperkalemia-related discontinuation percentages without event counts or a harm effect with confidence interval; AACT event rows describe hyperkalemia severity, not discontinuation, and rounded percentages cannot be inverted to counts. |
| 34449181 | Hyperkalemia-related treatment discontinuation | typed refusal | The abstract reports hyperkalemia-related discontinuation percentages without event counts or a harm effect with confidence interval; AACT event rows describe hyperkalemia severity, not discontinuation, and rounded percentages cannot be inverted to counts. |
| 26325557 | Hyperkalemia-related treatment discontinuation | typed refusal | The abstract reports hyperkalemia-related discontinuation across several finerenone doses with a shared placebo, including zero at 10 mg and percentages at other doses; no prespecified dose selection or compatible overall hyperkalemia total is supplied. |

### pcsk9-mace

| PMID | Outcome | Resolution | Source-backed reason |
|---|---|---|---|
| 28304224 | Injection-site reactions | typed refusal | The abstract gives injection-site reaction percentages without event counts or a harm effect with confidence interval; local AACT either omits this below-threshold non-serious outcome or supplies only serious reactions, not the overall outcome. |
| 30403574 | Injection-site reactions | typed refusal | The abstract gives injection-site reaction percentages without event counts or a harm effect with confidence interval; local AACT either omits this below-threshold non-serious outcome or supplies only serious reactions, not the overall outcome. |
| 25773378 | Injection-site reactions | extracted (counts) | Local AACT reports explicit injection-site reaction participant counts and safety denominators with arm labels; no percentage inversion. |
| 28304224 | Adverse events leading to discontinuation | spurious signal | The fired sentence compares adverse-event incidence and injection-site reactions, not adverse events causing treatment discontinuation; no discontinuation result is stated in the abstract or linked outcome tables. |
| 30403574 | Adverse events leading to discontinuation | spurious signal | The fired sentence compares adverse-event incidence and injection-site reactions, not adverse events causing treatment discontinuation; no discontinuation result is stated in the abstract or linked outcome tables. |
| 25773378 | Adverse events leading to discontinuation | spurious signal | The fired sentence describes tolerated background statin therapy before randomization, not adverse events leading to discontinuation of randomized alirocumab or placebo. |

### colchicine-postop-af

| PMID | Outcome | Resolution | Source-backed reason |
|---|---|---|---|
| 42132185 | Gastrointestinal adverse effects | typed refusal | The held abstract and abstract-only JATS report gastrointestinal events as 25.9% versus 8.5% without explicit event counts or a gastrointestinal effect with confidence interval; the POAF RR is a different endpoint. |
| 36286314 | Gastrointestinal adverse effects | typed refusal | The abstract gives diarrhea OR 2.578 (95% CI 1.300-5.111) and abdominal-pain OR 4.762 (1.010-22.91), but no overall gastrointestinal adverse-effect estimate or unique-patient total; the symptom effects cannot be relabelled as the overall outcome. |
| 32720823 | Gastrointestinal adverse effects | typed refusal | The abstract reports two diarrhea cases per arm, but diarrhea is only one component of gastrointestinal adverse effects and no overall gastrointestinal count or effect with confidence interval is reported. |
| 25172965 | Gastrointestinal adverse effects | typed refusal | The abstract reports 36 versus 21 patients with any adverse event, not gastrointestinal-specific events; it gives no gastrointestinal count or effect with confidence interval. |
| 32720823 | Treatment discontinuation | extracted (counts) | The abstract states one patient in each group discontinued treatment and supplies both arm sizes; one is transcribed as integer 1. |
| 25172965 | Treatment discontinuation | typed refusal | The abstract says discontinuation rates were similar but gives no discontinuation counts or effect with confidence interval; the 36 versus 21 counts refer to adverse events. |

## Diff check

`git diff --check`: exit 0.


No commit was made. `harness/gate.py`, `harness/synth.py`, membership/search/screening implementations, protocol text and other lanes’ pages were left unchanged.
