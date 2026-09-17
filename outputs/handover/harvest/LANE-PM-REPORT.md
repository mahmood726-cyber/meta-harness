# LANE PM report

Verification run finished; results below.

**MEASURED: 731 registered of 1238 whole-page nonstructural visible text units. 507 remain unregistered. Gate: REFUSED.**

The three prose-migration lanes are combined, GLP1 is rebuilt, and the requested measurement/verification evidence is recorded below. This is not a claim of full prose coverage, a green release gate, or submission readiness. No commit, push, deployment or network acquisition was performed.

## Base and scope

`git rev-parse HEAD`: `bf99a91652e74347e4e10cf6b9f1962aee4e596d`. Base `refs/lanes/landing4-wip-str`: `bf99a91652e74347e4e10cf6b9f1962aee4e596d`. Initial tracked worktree was clean; existing lane prompt/log/PID files were preserved. Session index/workbook context was checked without edits. The workbook and portfolio status were not changed.

Each lane's report was read first. Files were enumerated with `git status --short --untracked-files=all`, excluding lane logs/PIDs/prompts, `.tmp`, and `LANE-*`. Non-shared files were copied in A, B, C order. Shared source files were merged against `git show bf99a916:<path>`; generated GLP1 files were then rebuilt. The copy manifest is `.tmp/pm/copy-manifest.json`.

`harness/synth.py`, `harness/gate.py`, source identifiers/dates/effects, membership, search and screening engines, and other served pages were not edited. Search/screening *renderer bindings* from C were integrated as explicitly requested. Incidental test-generated changes outside the task were restored from the initially clean base.

## Every conflict resolution

The prompt's **CLAIMED** conflict count was 3 + 7. The initial raw Windows merge exposed six page hunks and a subsequent whole-file line-ending conflict. A and B page inputs had CRLF while the Git base and C had LF. **MEASURED after LF normalization:** A+B has one claimgraph conflict and zero page conflicts; AB+C has two claimgraph conflicts and zero page conflicts. Normalization changes line separators only; this was still a real base-relative `git merge-file` merge, not an overwrite with one lane's version.

The three semantic claimgraph resolutions:

1. A+B `review_graph`: retain A's `page_claims.register(review, graph)` and B's conditional `risk_prose.register` plus `manuscript.register`. Preserve B's `include_sections=False` recursion boundary and A's provenance-batch decorator.
2. AB+C `ClaimGraph.recompute`: retain B's `section_effect_display` and `section_text` dispatch and C's `ledger_field`, `selection_flow`, `harms_states`, `parity_consistency`, `retrieval_cell`, and `query_item` dispatch. These operations own different objects.
3. AB+C `review_graph`: retain all A/B registration above and add C's `register_sections(graph, review)`.

The seven raw page conflict resolutions/line-ending cases:

1. `_known_missing_sensitivity_panel`: retain A's typed `known_missing` dispatch; B's side is the old renderer.
2. `_overview` entry: retain A's typed overview branch; B has no replacement there.
3. `_trial_inputs`: retain A's `provenance_trial` branch and fallback; B has no replacement there.
4. `_outcome_block`: retain A's typed summary/details/harms dispatch and fallback; B has no replacement there.
5. `_riskofbias`: retain B's `risk_prose.render` replacement; A's side is the old renderer.
6. `render_page`: retain A's provenance-batch decorator and the function shared by both sides.
7. The AB+C whole-file CRLF/LF artifact: normalize merge inputs to LF and re-run the three-way merge, retaining C's limitation, retrieval, selection, family, harms, comparator and parity renderer bindings alongside A/B. There was no remaining semantic page conflict after normalization.

Source-level integration review found an additional conflict that Git did not flag: A's early overview return made C's limitations block unreachable. The existing C block was extracted to `_stated_limitations` and called by both overview paths (except neutral rendering), preserving C's three registered interpretations **and** its four unregistered limitations. The merge integration test checks their visibility and existing debt. The A-only census excludes `ul.limits` by its semantic ownership boundary; the whole-page and C censuses still count every limitation. No scanner exemption or prose whitelist was introduced.

Initial test authoring encountered BeautifulSoup's attribute reordering; the integration assertion now compares parsed span nodes, not raw attribute order. This correction did not change rendering. Raw and normalized merge evidence is under `.tmp/pm/`.

The first focused merged run reported `2 failed, 129 passed in 403.23s (0:06:43)`. Both failures were integration assumptions in A's tests: an apostrophe entity spelling superseded by B's text-node escaping, and an expectation for A's unused harms summary after C takes ownership of complete unpooled harms. The assertions now compare decoded text and the actual C harms renderer respectively; source tamper/refusal assertions remain. The final rerun is pasted below. An AST comparison (`.tmp/pm/merge-node-audit.json`) confirms every lane-modified page function matches its lane implementation except the deliberately combined Overview.

## Whole-page measurement

**N = 1238 nonstructural conservative visible prose/table text runs**, across the entire served GLP1 HTML, not just the three lanes' owned sections. These are not linguistic sentences or independent empirical claims. **V = 1342 visible text runs before the existing short-semantic-table-header rule.** Existing semantic headings/navigation are excluded by the scanner. No denominator is filtered according to whether a unit passes.

| Class | Registered units of N (N=1238) | Meaning |
|---|---:|---|
| FACT | 21 of 1238 | Matched registered renderings |
| TRANSFORMATION | 515 of 1238 | Matched registered renderings |
| JUDGEMENT | 183 of 1238 | Matched registered renderings |
| INTERPRETATION | 12 of 1238 | Matched registered renderings |
| STRUCTURAL | 104 of 1342 (V) | Existing semantic table-header rule; not registered claims |
| All nonstructural classes | 731 of 1238 | Registered whole-page coverage |
| Unregistered | 507 of 1238 | SENTENCE_WITHOUT_OBJECT; no class inferred |

Registered plus structural: **835 of 1342 visible units**. Unregistered units cannot honestly be assigned FACT/JUDGEMENT/etc. without objects, so the class rows use the named common denominator N rather than invented per-class totals. Registry object counts (different from repeated rendered occurrences): `{"FACT": 22, "INTERPRETATION": 11, "JUDGEMENT": 128, "TRANSFORMATION": 510}`.

Served and fresh-renderer census agree: **True**. The separate CGX3C census retains **451 registered of 488 nonstructural units**, with **37 unregistered of 488**; its numeric plant adds one deliberately unsupported unit. The other **470 unregistered units** are outside that C boundary. Whole-page debt includes strand membership/status tables, typed-effects disclosures, protocol/reporting/reproduction material and chrome as well as the C debt. The task's whole-page result is not 37 remaining.

`python scripts/claim_scope_sweep.py` ran as requested against the complete stored corpus. Its command output:

```text
UNVERIFIED_FACT: 27 of 38 verified_effects rows
Pages scanned: 32; scope_complete=false
```

The corpus sweep is a measurement, not a page rebuild or portfolio certification. `.tmp/pm/measurement.json` retains complete served/fresh scans, the plant, source audit and fresh strand calculations. `docs/claim_scope_sweep.json` is the requested broader census.

## Static-versus-dynamic hardcode disclosure

| Static/authored | Dynamic/source-derived | Limit |
|---|---|---|
| Renderer labels, operation dispatch, class rules and section boundaries | Registered inputs, provenance digests/spans, recomputed pools | No topic-result constants introduced |
| Editorial interpretations and explicit alternatives | Recorded decision fields and per-item states | Registration does not mean human adjudication |
| Display precision and existing estimator policy | Source FACT dependencies, HKSJ/PM pool and leave-one-out calculations | Uses unchanged statistical engine |
| Ledger formatting selectors | Stored retrieval fields and per-item selection/harms counts | A field projection is not an independent retrieval recount |
| Report layout and test selection | Measured counts, exact scanner violations, test/gate output | No simulated research data |

## Source/identifier/date/statistics second pass

**MEASURED:** all seven primary source IDs were found in held records; all seven FACT checks pass document digest, retrieval timestamp and located numeric-span validation. Typed-object violations: `[]`. Fresh primary: `{'k': 7, 'estimate': 0.8884, 'ci_low': 0.8284, 'ci_high': 0.9527, 'tau2': 0.0012, 'pi_low': 0.7959, 'pi_high': 0.9916}`. The source audit records the exact held document paths, metadata and verification results in `.tmp/pm/measurement.json`. Retrieval timestamps are evidence metadata, not inferred study dates. Input identifiers, study/source dates, effect values and membership were not edited.

Both strands were recomputed from registered FACT dependencies, not set to expected results:

| Strand | k | HR | 95% CI |
|---|---:|---:|---|
| CONVENTIONAL_GLP1RA | 7 | 0.8884 | 0.8284–0.9527 |
| GLP1RA_ANY_DELIVERY | 8 | 0.8984 | 0.8158–0.9894 |

## Build and reproduction — verbatim

`python scripts/build_topic.py glp1-ra-mace-t2d --now 2026-09-11`

```text
protocol_sha=bf99a91652e74347e4e10cf6b9f1962aee4e596d
PRIMARY: 3-point major adverse cardiovascular events  k=7  HR=0.8884 (0.8284-0.9527)  tau2=0.0012
included trials: ['31185157', '27633186', '27295427', '31189511', '28910237', '26630143', 'SOUL']
declared-absent trials: ['34215025', '30291013', 'FLOW']
comparator OA=True k=8
canonical: docs/reviews/glp1-ra-mace-t2d/index.html
```

`python scripts/reproduce_review.py glp1-ra-mace-t2d`

```text
OK  glp1-ra-mace-t2d

1/1 reproduce (all reproducible)
```

## Numeric plant — verbatim

One unsupported number was inserted inside the served page's main element in memory. It was never written to the source or served page. The scanner must refuse it; the assertion verifies that exact plant and code.

```text
PLANT: REFUSED (expected)
[
  {
    "code": "SENTENCE_WITHOUT_OBJECT",
    "kind": "unregistered",
    "claim_id": "",
    "detail": "The pooled hazard ratio is 0.123456.",
    "unit_id": "unit-1343",
    "context": "html/body/main/p"
  }
]
```

C's separate limitations plant also fires:

```text
search: 47 registered of 55; 13 structural
screening: 131 registered of 136; 10 structural
comparator: 3 registered of 23; 20 structural
harms: 266 registered of 266; 8 structural
limitations: 3 registered of 8; 0 structural
parity: 1 registered of 1; 0 structural
FAIL (expected plant): {"code": "SENTENCE_WITHOUT_OBJECT", "kind": "unregistered", "claim_id": "", "detail": "There were 987654 screened records.", "unit_id": "unit-0001", "context": "ul/li"}
```

## Focused tests — verbatim summary

The three lanes' tests, `tests/test_claimgraph*.py`, `tests/test_fact_provenance.py`, `tests/test_page.py`, lane-related regressions and the browser E2E contract were run together. Exact command:

```text
python -m pytest -q tests/test_pm_merge.py tests/test_page_claims.py tests/test_cgx3b_prose.py tests/test_cgx3c_sections.py tests\test_claimgraph.py tests\test_claimgraph_dispute.py tests\test_claimgraph_typed.py tests/test_fact_provenance.py tests/test_page.py tests/test_cgx2_prose.py tests/test_retrieval_render.py tests/test_harms_recovery.py tests/test_parity_relation.py tests/test_limitations.py tests/test_glp1_lane.py tests/test_glp1_ui.py tests/test_grade_unassessed.py tests/test_rob_sensitivity_predicate.py tests/test_incompatible_fail_closed.py tests/test_stage_additions.py::test_manuscript_limb_passes_on_every_live_review tests/test_stage_additions.py::test_manuscript_limb_REFUSES_a_fabricated_number tests/test_stage_additions.py::test_manuscript_renders_and_is_object_derived --tb=short
```

```text
........................................................................ [ 54%]
...........................................................              [100%]
131 passed in 407.46s (0:06:47)
```

## Full suite — verbatim summary

`python -m pytest -q --import-mode=importlib --tb=short`

Importlib mode permits collecting both the archived search-lane test and its canonical same-named test; no test directory is excluded. Python subprocesses use the copied lane offline socket guard, allowing only loopback for E2E.

```text
=========================== short test summary info ===========================
FAILED tests/test_fixstate.py::test_real_store_validates - AssertionError: do...
FAILED tests/test_gate.py::test_valid_page_passes_non_replay_limbs - Assertio...
FAILED tests/test_gate_scorecard.py::test_real_registry_passes - AssertionErr...
FAILED tests/test_integrity.py::test_committed_integrity_is_fresh_for_every_live_topic
FAILED tests/test_limitations_legacy_compare.py::test_legacy_absent_banner_blocks_match_limitation_objects_for_all_reviews
FAILED tests/test_override_audit.py::test_override_audit_covers_every_committed_override
FAILED tests/test_stage_additions.py::test_error_rate_is_fresh_against_current_pooled_population
7 failed, 955 passed in 1013.30s (0:16:53)
```

Complete outputs are `.tmp/pm/focused.txt` and `.tmp/pm/full.txt`. Failures are disclosed, not bypassed. No full-suite PASS is claimed unless the pasted result is green. Existing lane reports described repository-wide failures before this merge; that historical report is **CLAIMED context**, not a substitute for the current run or an isolated baseline reproduction. Unresolved blockers are recorded in `STUCK_FAILURES.md`.

**MEASURED current failure details:** stale fix-ledger/fix-state documents; a gate fixture with unregistered prose; missing scorecard entries for `gate.check_effect_types` and `gate.check_typed_renderings`; GLP1 integrity recording ten pooled trials against a union of seven; a balanced-crystalloids legacy test that assumes no claimgraph; missing override-audit entries for esketamine and SGLT2 reviews; and an error-rate sample missing GLP1 input 26630143. **INFERRED:** these are the persisting blockers described in the source lanes, based on matching failure identities/details and unchanged underlying out-of-scope inputs. No isolated full-base replay was performed by PM, and no broader repair or certification is claimed.

Final cleanup restored the four test/build-written `effect_types.json` caches (GLP1, NOAC, PCSK9 and probiotics) and `docs/compat_direction_sweep.json` to their clean session-start base bytes. The final GLP1 artifacts and requested scope census stayed byte-identical to their measured outputs throughout the tests. Protected engines remain unchanged; final `git diff --check` passes. HEAD is still the recorded base, and nothing is staged or committed.

## Exact gate verdict — verbatim

Called `scripts.verify_all.limb_gate_every_page('glp1-ra-mace-t2d')` on the merged output. It gates **1 of 1 requested pages**. Gate refusal is distinct from deterministic numerical reproduction.

```text
REFUSED
TARGET verify_all.limb_gate_every_page: head=bf99a91652e74347e4e10cf6b9f1962aee4e596d base=none tree=dirty:31 files files=1 docs/reviews/glp1-ra-mace-t2d/review.json
glp1-ra-mace-t2d: L1: live census reproduced 1 failure(s): typed claim registry covers served prose and validates its objects; L1: SENTENCE_WITHOUT_OBJECT : Reproducible meta-analysis harness — auditability, not authority; L1: SENTENCE_WITHOUT_OBJECT : Pinned audit identity — content hash of the canonical review object (review_sha256) ad36eddb18fe10e4; exact served bytes are attested separately (html_sha256 in manifest.json and the production record on the production-records branch). Cite this hash when auditing; a different hash is a different version of this page.; L1: SENTENCE_WITHOUT_OBJECT : 31185157; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27633186; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27295427; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 31189511; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 28910237; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 26630143; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : SOUL; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : endpoint_components; L1: SENTENCE_WITHOUT_OBJECT : axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : FLOW; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : 31185157; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27633186; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 27295427; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 31189511; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 28910237; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 26630143; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : SOUL; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : FREEDOM-CVO; L1: SENTENCE_WITHOUT_OBJECT : POOLED; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : endpoint_components; L1: SENTENCE_WITHOUT_OBJECT : axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : FLOW; L1: SENTENCE_WITHOUT_OBJECT : REFUSED; L1: SENTENCE_WITHOUT_OBJECT : censoring; L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT glp1-freedom-sensitivity: [FACT] PMID 34873344: HR 1.36 (0.96, 1.92).; L1: SENTENCE_WITHOUT_OBJECT : Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.; L1: SENTENCE_WITHOUT_OBJECT : Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.; L1: SENTENCE_WITHOUT_OBJECT : Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.; L1: SENTENCE_WITHOUT_OBJECT : The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.; L1: SENTENCE_WITHOUT_OBJECT : bf99a91652e74347e4e10cf6b9f1962aee4e596d; L1: SENTENCE_WITHOUT_OBJECT : 2026-09-11; L1: SENTENCE_WITHOUT_OBJECT : Random-effects inverse-variance on the log ratio (log RR/OR/HR/IRR as configured for the outcome); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1 (this canonical code path; every rendered interval is gate-checked to originate here).; L1: SENTENCE_WITHOUT_OBJECT : Included iff ALL hold: a randomised controlled trial; population (in title/registry conditions) mentions one of ['type 2 diabetes', 'type 2 diabetic', 'type 2 diabetes mellitus', 'diabetes mellitus, type 2', 't2d', 't2dm']; and none of ['without diabetes', 'no diabetes', 'obesity without diabetes', 'overweight or obesity but without diabetes', 'type 1 diabetes', 'gestational diabetes']; randomised intervention is one of ['liraglutide', 'semaglutide', 'dulaglutide', 'albiglutide', 'efpeglenatide', 'exenatide', 'lixisenatide'] (named in title/conditions); a comparator among ['placebo']. Excluded (rule id + verbatim span on each record): X1 not an RCT · X2 wrong/off-topic population · X3 wrong intervention/comparator.; L1: SENTENCE_WITHOUT_OBJECT : # Protocol - GLP-1 receptor agonists for 3-point MACE in type 2 diabetes **Registration.** The commit that adds this file is the registration of this review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab. Committed BEFORE the synthesis is run. ## PICO - **P** - adults with type 2 diabetes. - **I** - GLP-1 receptor agonist therapy (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, or lixisenatide) added to usual care. - **C** - placebo added to usual care. - **O (primary)** - 3-point major adverse cardiovascular events, defined as cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. - **O (harms / secondary)** - gastrointestinal adverse events, discontinuation for adverse events, and any further harm outcome the resolved comparator reports. ## Estimand / population / timepoint - **Estimand** - hazard ratio (HR), GLP-1 receptor agonist vs placebo. - **Population** - intention-to-treat as randomised. - **Timepoint** - trial end / longest primary cardiovascular outcome follow-up. ## Eligibility - on P/I/C/DESIGN ONLY Include a record iff **all** hold: - **I1** - randomised controlled trial; - **I2** - population is adults with type 2 diabetes, judged from the title or registry conditions; - **I3** - a GLP-1 receptor agonist vs placebo contrast; - **design** - double-blind, placebo-controlled. Exclude (reason must be true of the record): - **X1** - not an RCT (review, guideline, observational, protocol-only); - **X2** - wrong population (e.g. obesity without diabetes, type 1 diabetes, or gestational diabetes); - **X3** - wrong intervention/comparison (no GLP-1 receptor agonist-vs-placebo contrast); - **X-DESIGN** - not double-blind and placebo-controlled; - **X5** - off-topic: a primary trial of another topic in this set (negative control). > **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives > a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as > an exclusion. A published effect + 95% CI is a poolable input. ## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline) - PubMed: exact-title sweeps for the large GLP-1 receptor agonist cardiovascular outcome trials in type 2 diabetes (LEADER, SUSTAIN-6, REWIND, HARMONY Outcomes, AMPLITUDE-O, PIONEER-6, EXSCEL, and ELIXA). - ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention "efpeglenatide". - Fixed-screen note: several PubMed abstracts for verified double-blind CVOTs do not use the literal phrase "double-blind"; the config therefore does not require that literal abstract/title string, while the protocol eligibility criterion remains double-blind placebo-controlled design. ## Synthesis method (DECLARED; served method must equal this - gate limb 1) Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI path on the same ratio/log scale; 2x2 extraction is available but is not required when a trial reports an HR + CI. ## Comparator (resolved; open-access confirmed) Giugliano et al., *Cardiovascular Diabetology* 2021, "GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs" (PMID 34526024, DOI 10.1186/s12933-021-01366-8; Unpaywall is_oa=true; PubMed Central PMC8442438). It reports pooled MACE HR 0.86 (95% CI 0.79-0.94) over 8 cardiovascular outcome trials. ## Controls - **Positive** - the search must recover and include LEADER, SUSTAIN-6, and REWIND. - **Negative** - SELECT (semaglutide, double-blind, placebo-controlled, but obesity without diabetes - another disease population) must be recovered and EXCLUDED by the population rule. ## Amendment 2026-09-16 (eligibility, estimand, effect measure, timepoint, screening, search, comparator, harms, RoB 2, GRADE -- "B-prime") Executable strand declarations (delivery boundaries only; all members must also pass P/I/C/design eligibility, held-source verification and binding effect axes): `CONVENTIONAL_GLP1RA` is primary and excludes PMID 34873344 (FREEDOM-CVO, continuous delivery); `GLP1RA_ANY_DELIVERY` is non-primary and has no delivery exclusions. These correspond to `membership_rule.exclude_ids: ["34873344"]` and `membership_rule.exclude_ids: []` in the topic JSON. Neither declaration overrides a refused binding axis. End-of-treatment sensitivity values are never pool candidates. Refused rows remain visible with their axis and reason. **Status: RETROSPECTIVE.** Registered under Mahmood's authority ("fix all in reproducible harness", 16 Sep 2026, via Dispatch) after an independent protocol audit of registration commit `4091958ce4af7f1ca9ed4c30e1021672b0c21223` found that the registered eligibility (a broad GLP-1 review; eligibility explicitly not on the outcome axis) and the registered search (exact-title sweeps for eight named cardiovascular outcome trials) define two different reviews. This amendment is appended before the page is rebuilt against it and does not rename the pinned slug/URL. **Both alternative answers were known when this rule was written**, and are disclosed below; that disclosure is the point of the RETROSPECTIVE label. - **Question.** Among adults with type 2 diabetes, what is the effect of GLP-1 receptor agonist therapy versus placebo on time to first adjudicated 3-point MACE? - **Eligibility (B-prime).** Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes **in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained** -- preferably with blinded or independent adjudication. Eligibility does **not** depend on the direction, statistical significance or published availability of the MACE result. **If MACE was measured but the result is unavailable, the trial is retained and the result is pursued** through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held. - **Alternatives disclosed.** Under **A** (the literal registered rule: outcome not an eligibility axis) the universe would additionally include SUSTAIN-1, PIONEER-1, AWARD-8, LEAD-2, Harmony 1, AMPLITUDE-M, GetGoal-P, GetGoal-L, GetGoal-Mono, FREEDOM-1 and others, entering screening and exiting on outcome availability. Under **B** ("large cardiovascular outcome trials") the universe would be the eight seeded CVOTs, with "large" and "CVOT" undefined. B-prime yields the intended small universe by a stated, executable criterion (prospective systematic ascertainment of the outcome), not by a label or by which results are convenient. FLOW (semaglutide, T2D with CKD; MACE prospectively adjudicated) is eligible under B-prime; FREEDOM-CVO (ITCA 650) is eligible under B-prime on the intervention-class strand that admits continuous delivery (see the class-boundary decision: `CONVENTIONAL_GLP1RA` primary strand, `GLP1RA_ANY_DELIVERY` rendered alongside); ELIXA (lixisenatide; 4-point primary, 3-point components prospectively ascertained) is eligible, its 3-point result pursued from the primary supplement or regulatory record, never from a secondary meta-analysis. - **Estimand.** Intention-to-treat effect of assignment to GLP-1 RA versus placebo on **time to first** occurrence of cardiovascular death, nonfatal myocardial infarction or nonfatal stroke during the prespecified randomised cardiovascular follow-up. Trial definitions that count **undetermined death as cardiovascular death** are accepted as each trial's prespecified adjudicated definition and recorded per trial in the compatibility key (`undetermined_death_counted_as_cv: yes/no/unstated`); no re-adjudication is attempted. - **Effect measure.** The primary analysis pools **log-HRs only** (published, or validly reconstructed from a time-to-event analysis). Ordinary RRs, ORs and IRRs do not enter the primary pool. Where only fixed-time counts are recoverable, a separate RR sensitivity analysis is reported. (Supersedes the registered synthesis sentence "random-effects inverse-variance on log(RR)", which contradicted the registered HR estimand.) - **Timepoint.** The trial's prespecified primary cardiovascular analysis **at the end of randomised, blinded follow-up**. Post-trial and extension follow-up are analysed separately and never substitute for the primary analysis. - **Screening.** The **clinical eligibility rule** (above) is separate from the **machine screening heuristic**. Title and registry-condition term matching is a first-pass heuristic only; final eligibility is decided from abstract, then registry record, then full text/protocol as needed, on a canonical trial object (trial / arm / drug / dose / route / background therapy / population / timepoint / analysis set). A trial must not become ineligible because a term is absent from its title. Every screening decision carries the source span it rests on. - **Search.** Independent concept search across all seven eligible agents in PubMed/MEDLINE and Europe PMC, **the Cochrane CENTRAL register** (free; carries Embase-derived records), ClinicalTrials.gov via the local AACT snapshot (queried symmetrically across agents, not only efpeglenatide), **WHO ICTRP** (non-US registries) and ISRCTN, plus citation chasing and the trial-family assembly of every report, registry record, supplement and regulatory document. **No trial-name seed list is the primary retrieval mechanism.** Every retrieved record carries `entered_via` (executed query / seeded identifier / manual addition) and the rejection trail (families retrieved and refused, each with a typed reason) is rendered. - **Declared scope boundary (not a defect): no Embase.** This review does not search Embase. Its unique contribution over MEDLINE is mainly conference abstracts and European/pharma-journal reports; for large registered cardiovascular outcome trials -- this topic -- the marginal yield is low because every such trial is MEDLINE-indexed and registered, and CENTRAL + registries recover part of Embase's unique yield. The completeness claim is therefore for **registered trials**; Embase-equivalent coverage of conference and grey literature is not claimed. (For topics dominated by small or older trials the gap matters considerably more; each topic's protocol states which kind it is.) - **Source hierarchy for every extracted value (recorded and rendered as `source_level`):** 1 the trial's own publication and supplement; 2 regulatory review (FDA, EMA) -- primary re-analysis of trial data; 3 registry results (ClinicalTrials.gov / AACT) -- sponsor-posted structured data; 4 HTA assessment (NICE); 5 older meta-analyses -- **pointers only, never the number itself** (several published reviews relabelled ELIXA's 4-point MACE as 3-point; a value found in a meta is traced to a level 1-4 source or refused). A label such as `PUBLISHED_UNADJUSTED` is assigned only after the estimator is read at the source. - **Full-text reachability ladder.** Before `abstract only` may be recorded the extractor tries, in order: PMC / Europe PMC deposits; supplementary appendices (where exact secondary endpoints such as ELIXA's and FREEDOM-CVO's 3-point MACE live); publisher open-access versions; author accepted manuscripts in institutional repositories; regulatory documents (FDA, EMA); ClinicalTrials.gov / AACT results. The route that succeeded is recorded; `abstract only` is replaced by `full text not reachable after N named attempts`, listing them. An unreachability claim with no attempt log is the same defect as an absence claim with no negative citation. - **Comparator.** The published comparator meta-analysis is resolved **only after the independent evidence search is locked**; published meta-analyses are used for reference checking, never for seeding. Parity compares the comparator's eligibility rules, not only its trial list. - **Harms.** Gastrointestinal adverse events and discontinuation due to adverse events are prespecified harm outcomes. Any further harm outcome a resolved comparator happens to report is **exploratory**, not prespecified, and is labelled so. - **Risk of bias.** Full outcome-specific RoB 2 on the primary result (effect of assignment): five domains, signalling questions, information sources (protocol, statistical analysis plan, registry record, primary publication and supplement), adjudication method (two assessors, disagreements recorded, not silently resolved), and a planned sensitivity analysis restricted to low-risk-of-bias trials. Registry-derived machine signals are rendered as `machine signal consistent with low risk; formal RoB 2 not assessed` until the sources above have been read; they are never rendered as RoB 2 judgements. - **GRADE.** Prespecified across all five domains (risk of bias, inconsistency, imprecision, indirectness, publication bias). **No certainty category is issued while any domain is unassessed**; the page renders `GRADE provisional -- not yet fully assessable` instead. Imprecision reflects whether the confidence interval permits materially different clinical conclusions, not a mechanical significance test; a prediction interval approaching 1 is not by itself grounds for downgrading. - **Pre-specified list (intervention agents).** liraglutide; semaglutide (subcutaneous and oral); dulaglutide; albiglutide; efpeglenatide; exenatide (immediate- and extended-release; ITCA 650 continuous subcutaneous delivery on the `GLP1RA_ANY_DELIVERY` strand); lixisenatide. ## Retrospective executable clarification — 2026-09-17 This states which existing B-prime rules bind effect-type unification; it changes no clinical rule. Endpoint components (3-point MACE), effect measure (HR, pooled on the log scale), and timepoint/censoring (end of randomised follow-up) are binding. Analysis set, adjustment, estimator, time origin, and follow-up length are disclosed, not binding. All other axes are non-binding. Unknown evidence remains UNKNOWN with its absence code; a missing binding value cannot be filled from this target. ```effect-type-binding { "schema_version": 1, "outcomes": { "3-point major adverse cardiovascular events": { "endpoint_components": [ "CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE" ], "effect_measure": "HR", "censoring": "end-of-study" } } } ```; L1: SENTENCE_WITHOUT_OBJECT : Snapshot: records_sha256 1e0282f5; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query retrieved which record was not recorded; every record's found_by names this single source.; L1: SENTENCE_WITHOUT_OBJECT : This page replays the committed retrieval snapshot; it is not a claim that the protocol SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present).; L1: SENTENCE_WITHOUT_OBJECT : No search was run for this topic: every PubMed source is a PMID enumeration.; L1: SENTENCE_WITHOUT_OBJECT : Citation chase: NOT_RUN · ClinicalTrials.gov: RAN_OK · Europe PMC (OA + metadata): RAN_OK · Legacy unrecorded retrieval: RAN_OK · PMC full text: NOT_RUN · PubMed: RAN_OK · Registry-first (AACT): RAN_OK — RAN_OK = ran and returned records; RAN_ZERO = ran, none matched; RAN_ERROR = attempted but failed; NOT_RUN = not attempted for this topic.; L1: SENTENCE_WITHOUT_OBJECT : KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this topic. an auditable screening ledger attached to an unauditable retrieval process.; L1: SENTENCE_WITHOUT_OBJECT : Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK; its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications (UID/PMID-anchored queries for pre-identified trials), which cannot discover an unknown eligible trial. A fetch of named identifiers is not a systematic search. We retract any claim of a registry-first or systematic search for this topic.; L1: SENTENCE_WITHOUT_OBJECT : Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.; L1: SENTENCE_WITHOUT_OBJECT : Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).; L1: SENTENCE_WITHOUT_OBJECT : Identifier scope: identifier leading token matches class term GLP-1RA. Verdict: NOT_APPLICABLE.; L1: SENTENCE_WITHOUT_OBJECT : Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.; L1: SENTENCE_WITHOUT_OBJECT : Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.; L1: SENTENCE_WITHOUT_OBJECT : Positive: Recovered & included the canonical trials ['27295427', '27633186', '31189511'] that a comparator includes; none missed.; L1: SENTENCE_WITHOUT_OBJECT : Negative: Cross-topic trial(s) ['37952131'] recovered by the search and correctly EXCLUDED ['37952131'] by rule (same drug/design, wrong topic).; L1: SENTENCE_WITHOUT_OBJECT : 5 of 25 declared-absent/refusal reason code(s) have a numeric value in a held source; 0 wrong-kind code(s); 0 not verifiable from held sources. Registered-outcome sweep: 6 of 33 included-trial/outcome pair(s) are held-but-not-extracted.; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : 3-point major adverse cardiovascular events; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : abstract:34215025; L1: SENTENCE_WITHOUT_OBJECT : During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p...; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : 3-point major adverse cardiovascular events; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : abstract:30291013; L1: SENTENCE_WITHOUT_OBJECT : The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i...; L1: SENTENCE_WITHOUT_OBJECT : 38785209; L1: SENTENCE_WITHOUT_OBJECT : 3-point major adverse cardiovascular events; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : abstract:38785209; L1: SENTENCE_WITHOUT_OBJECT : Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).; L1: SENTENCE_WITHOUT_OBJECT : 34873344; L1: SENTENCE_WITHOUT_OBJECT : Gastrointestinal adverse events; L1: SENTENCE_WITHOUT_OBJECT : OUTCOME_NOT_IN_SOURCE; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : abstract:34873344; L1: SENTENCE_WITHOUT_OBJECT : Adverse events were more frequent in the ITCA 650 group (72%, 1,491/2,074) than in the placebo group (63.9%, 1,325/2,070), mainly due to an increase in gastrointestinal events and disorders while on ITCA 650.; L1: SENTENCE_WITHOUT_OBJECT : 27295427; L1: SENTENCE_WITHOUT_OBJECT : Adverse events leading to discontinuation; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : REASON_FALSE_VALUE_HELD; L1: SENTENCE_WITHOUT_OBJECT : fulltext:27295427; L1: SENTENCE_WITHOUT_OBJECT : The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) than in the placebo group (694 of 4672 [14.9%]) (hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97; P&lt;0.00...; L1: SENTENCE_WITHOUT_OBJECT : 34215025; L1: SENTENCE_WITHOUT_OBJECT : PMID 34215025; L1: SENTENCE_WITHOUT_OBJECT : not extracted — the outcome's number IS in the source (extraction gap, not trial absence); L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : reason-code audit: REASON_FALSE_VALUE_HELD abstract:34215025: During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p...; L1: SENTENCE_WITHOUT_OBJECT : span: ( hazard ratio, 0.73; 95% confidence interval [CI], 0.58 to 0.92; P<0.001 for noninferiority; P = 0.007 for superiority).; L1: SENTENCE_WITHOUT_OBJECT : basis: EXTRACTION_NOT_PERFORMED: source span: "( hazard ratio, 0.73; 95% confidence interval [CI], 0.58 to 0.92; P<0.001 for noninferiority; P = 0.007 for superiority)."; effect=HR 0.73 [0.58, 0.92], class=FIRST_EVENT_RATIO, declared_class=FIRST_EVENT_RATIO; L1: SENTENCE_WITHOUT_OBJECT : completeness: eligible+completed+results_available; L1: SENTENCE_WITHOUT_OBJECT : completeness basis: CT.gov status/results dates from local AACT snapshot; L1: SENTENCE_WITHOUT_OBJECT : 30291013; L1: SENTENCE_WITHOUT_OBJECT : PMID 30291013; L1: SENTENCE_WITHOUT_OBJECT : not extracted — the outcome's number IS in the source (extraction gap, not trial absence); L1: SENTENCE_WITHOUT_OBJECT : axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : reason-code audit: REASON_FALSE_VALUE_HELD abstract:30291013: The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i...; L1: SENTENCE_WITHOUT_OBJECT : span: of 4732 patients at an incidence rate of 5.9 events per 100 person-years in the placebo group ( hazard ratio 0.78, 95% CI 0.68-0.90), which indicated that albiglutide was superior to placebo (p<0.000...; L1: SENTENCE_WITHOUT_OBJECT : basis: EXTRACTION_NOT_PERFORMED: source span: "of 4732 patients at an incidence rate of 5.9 events per 100 person-years in the placebo group ( hazard ratio 0.78, 95% CI 0.68-0.90), which indicated that albiglutide was superior to placebo (p<0.000..."; effect=HR 0.78 [0.68, 0.9], class=FIRST_EVENT_RATIO, declared_class=FIRST_EVENT_RATIO; L1: SENTENCE_WITHOUT_OBJECT : completeness: eligible+completed+results_available; L1: SENTENCE_WITHOUT_OBJECT : completeness basis: CT.gov status/results dates from local AACT snapshot; L1: SENTENCE_WITHOUT_OBJECT : FLOW; L1: SENTENCE_WITHOUT_OBJECT : PMID 38785209; L1: SENTENCE_WITHOUT_OBJECT : not extracted — the outcome's number IS in the source (extraction gap, not trial absence); L1: SENTENCE_WITHOUT_OBJECT : UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : EXTRACTION_NOT_PERFORMED; L1: SENTENCE_WITHOUT_OBJECT : reason-code audit: REASON_FALSE_VALUE_HELD abstract:38785209: Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).; L1: SENTENCE_WITHOUT_OBJECT : span: and for death from cardiovascular causes ( hazard ratio, 0.71; 95% CI, 0.56 to 0.89).; L1: SENTENCE_WITHOUT_OBJECT : basis: EXTRACTION_NOT_PERFORMED: source span: "and for death from cardiovascular causes ( hazard ratio, 0.71; 95% CI, 0.56 to 0.89)."; effect=HR 0.71 [0.56, 0.89], class=FIRST_EVENT_RATIO, declared_class=FIRST_EVENT_RATIO; L1: SENTENCE_WITHOUT_OBJECT : completeness: eligible+completed+results_available; L1: SENTENCE_WITHOUT_OBJECT : completeness basis: CT.gov status/results dates from local AACT snapshot; L1: SENTENCE_WITHOUT_OBJECT : Candidate rows, including type refusals.; L1: SENTENCE_WITHOUT_OBJECT : Protocol-declared binding axes: endpoint_components, effect_measure, censoring. All remaining axes are non-binding.; L1: SENTENCE_WITHOUT_OBJECT : 1. population; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 2. randomised_contrast; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 3. analysis_set; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: intention-to-treat; L1: SENTENCE_WITHOUT_OBJECT : record:31189511.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: intention-to-treat; L1: SENTENCE_WITHOUT_OBJECT : record:30291013.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: intention-to-treat; L1: SENTENCE_WITHOUT_OBJECT : record:28910237.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : ITT; L1: SENTENCE_WITHOUT_OBJECT : span: ITT; L1: SENTENCE_WITHOUT_OBJECT : record:26630143.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 4. endpoint_components; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome in a time-to-event analysis was the first occurrence of a major adverse cardiovascular event (death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke); L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary composite outcome in the time-to-event analysis was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome was the first major adverse cardiovascular event (MACE; a composite of nonfatal myocardial infarction, nonfatal stroke, or death from cardiovascular or undetermined causes); L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome was the first occurrence of the composite endpoint of non-fatal myocardial infarction, non-fatal stroke, or death from cardiovascular causes (including unknown causes), which was assessed in the intention-to-treat population; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED']; L1: SENTENCE_WITHOUT_OBJECT : span: We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: MACE, defined as cardiovascular death, non-fatal MI, and non-fatal stroke; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: The primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; L1: SENTENCE_WITHOUT_OBJECT : span: Number of Participants From Time of Randomization to Time to First Occurrence of a Major Adverse Cardiovascular Event (MACE): Acute Myocardial Infarction (Non Fatal); Non-fatal Stroke; and CV Death; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : 5. first_or_recurrent; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:31185157.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:27633186.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:27295427.source; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:31189511.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:30291013.source; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: first occurrence; L1: SENTENCE_WITHOUT_OBJECT : record:28910237.source; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : first; L1: SENTENCE_WITHOUT_OBJECT : span: time-to-first; L1: SENTENCE_WITHOUT_OBJECT : record:40162642.source; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 6. time_origin; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 7. follow_up; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : median follow-up was 3.8 years; L1: SENTENCE_WITHOUT_OBJECT : span: median follow-up was 3.8 years; L1: SENTENCE_WITHOUT_OBJECT : record:27295427.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : median follow-up of 1.81 years; L1: SENTENCE_WITHOUT_OBJECT : span: median follow-up of 1.81 years; L1: SENTENCE_WITHOUT_OBJECT : record:34215025.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : followed for a median of 3.2 years; L1: SENTENCE_WITHOUT_OBJECT : span: followed for a median of 3.2 years; L1: SENTENCE_WITHOUT_OBJECT : record:28910237.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : followed for a median of 25 months; L1: SENTENCE_WITHOUT_OBJECT : span: followed for a median of 25 months; L1: SENTENCE_WITHOUT_OBJECT : record:26630143.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : median follow-up was 3.4 years; L1: SENTENCE_WITHOUT_OBJECT : span: median follow-up was 3.4 years; L1: SENTENCE_WITHOUT_OBJECT : record:38785209.source/abstract; L1: SENTENCE_WITHOUT_OBJECT : 8. censoring; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: Number of participants experiencing a first event of a MACE, defined as cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke are presented. Results are based on the in-trial observation period which started at the date of randomisation, included the period after permanent trial product discontinuation, if any and ended at the date of the follow-up visit regardless of adherence to treatment.; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: Time from randomisation up to end of follow-up (scheduled at week 109); L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; events occurring after that visit were not included.; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/ft_27295427.txt; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: From randomization to first occurrence or death from any cause or study completion (Median Follow-Up of 5.4 Years); L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome.; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: The planned closeout of follow-up of the patients was from December 5, 2016, to May 11, 2017, after the prespecified required minimum of 1360 patients were confirmed to have had a primary composite outcome event.; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/ft_28910237.txt; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: MACE endpoint (on-study) 1.02 (0.89, 1.18) No. of patients with event (%) 392 (12.9%) 400 (13.2%) Total Person Year 6340.2 6368.7 Incidence Rate 6.18 6.28; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt; L1: SENTENCE_WITHOUT_OBJECT : end-of-study; L1: SENTENCE_WITHOUT_OBJECT : span: Number of participants with first occurrence of EAC (event adjudication committee) confirmed major adverse cardiovascular event (MACE), a composite end-point. i.e., from time of randomization to first occurrence of cardiovascular (CV) death, non-fatal myocardial infarction and non-fatal stroke combined data during in-trial period were reported. In-trial observation period was defined as the period from date of randomization to the first of (both inclusive): date of follow-up visit, date when participant withdrew consent, date of last contact with participant (for participant lost to follow-up), and date of death.; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/typg/outcomes.json; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : 9. effect_measure; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.79; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.74; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.87; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.73; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio [HR] 0·88, 95% CI 0·79-0·99; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio 0·78, 95% CI 0·68-0·90; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.91; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio is (0.887, 1.172) with a point estimate of 1.02.; L1: SENTENCE_WITHOUT_OBJECT : outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.86; L1: SENTENCE_WITHOUT_OBJECT : cache/glp1-ra-mace-t2d/records.json; L1: SENTENCE_WITHOUT_OBJECT : HR; L1: SENTENCE_WITHOUT_OBJECT : span: hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P&#x2009;=&#x2009;0.029); L1: SENTENCE_WITHOUT_OBJECT : outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml; L1: SENTENCE_WITHOUT_OBJECT : 10. adjustment; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 11. estimator; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN; L1: SENTENCE_WITHOUT_OBJECT : UNKNOWN: NO_ROW_EVIDENCE; L1: SENTENCE_WITHOUT_OBJECT : 12. report; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : {"document_sha256": "2fc31abdf24b1a27d1ee79dd424b3faac680c376e1c86b819c0d0f1bd6c89e40", "kind": "publication", "source_level": 1}; L1: SENTENCE_WITHOUT_OBJECT : rule: source_hierarchy:provenance:fulltext_verified; L1: SENTENCE_WITHOUT_OBJECT : PMID 31185157: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 27633186: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 27295427: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 34215025: UNKNOWN_FAILS_CLOSED — UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD; L1: SENTENCE_WITHOUT_OBJECT : PMID 31189511: MATCH — axis 1 unstated; axis 2 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 30291013: REFUSE — axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion; L1: SENTENCE_WITHOUT_OBJECT : PMID 28910237: MATCH — axis 1 unstated; axis 2 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 26630143: MATCH — axis 1 unstated; axis 2 unstated; axis 5 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 40162642: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated; L1: SENTENCE_WITHOUT_OBJECT : PMID 38785209: UNKNOWN_FAILS_CLOSED — UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR; L1: SENTENCE_WITHOUT_OBJECT : No declared coercions.; L1: SENTENCE_WITHOUT_OBJECT : GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs. (2021), Cardiovasc Diabetol; L1: SENTENCE_WITHOUT_OBJECT : PMID 34526024; L1: SENTENCE_WITHOUT_OBJECT : True; L1: SENTENCE_WITHOUT_OBJECT : https://doi.org/10.1186/s12933-021-01366-8; L1: SENTENCE_WITHOUT_OBJECT : Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94; L1: SENTENCE_WITHOUT_OBJECT : ✓ same question. Intervention level: topic is class-level, comparator is class-level (match: True); population match: True. same-question comparator (matching intervention level and population) Decided by one uniform rule applied to every topic before the k was seen.; L1: SENTENCE_WITHOUT_OBJECT : 7; L1: SENTENCE_WITHOUT_OBJECT : 8; L1: SENTENCE_WITHOUT_OBJECT : 6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina. Characteristics of trials and patients are reported, respectively, in Table 1 . The populations studied ranged in size from 3297 (SUSTAIN-6) to 14,752 (EXSCEL), were of similar age (mean age was 64.0 ± 1.97 years), 37,117 were mal; L1: SENTENCE_WITHOUT_OBJECT : 7; L1: SENTENCE_WITHOUT_OBJECT : SOUL; L1: SENTENCE_WITHOUT_OBJECT : ELIXA; L1: SENTENCE_WITHOUT_OBJECT : cached comparator text trial-set enumeration; L1: SENTENCE_WITHOUT_OBJECT : Comparator trial set was measured from cached comparator abstract/full text.; L1: SENTENCE_WITHOUT_OBJECT : MEASURED; L1: SENTENCE_WITHOUT_OBJECT : named table rows; L1: SENTENCE_WITHOUT_OBJECT : ELIXA, LEADER, SUSTAIN-6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6, AMPLITUDE-O; L1: SENTENCE_WITHOUT_OBJECT : COMPARATOR_PREDATES_POOLED_TRIAL(SOUL); L1: SENTENCE_WITHOUT_OBJECT : Comparator search ran to 2021-06-30; SOUL is a 2025 pooled trial.; L1: SENTENCE_WITHOUT_OBJECT : The comparator k above is auto-extracted from the comparator's own text and may reference a sub-analysis rather than its same-scope pooled total; the enumerated same-scope comparator k (scope-classified, the finishing metric) is the figure in the parity table, which governs where these differ.; L1: SENTENCE_WITHOUT_OBJECT : Compliance with the PRISMA 2020 reporting items, derived from the review object so it cannot drift from the page. Every item is rendered or declared absent with a reason.; L1: SENTENCE_WITHOUT_OBJECT : 5 Eligibility criteria; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.; L1: SENTENCE_WITHOUT_OBJECT : 6 Information sources + dates; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Search tab — PubMed, ClinicalTrials.gov; run 2026-09-11; AACT snapshot dated on the ghost/recall blocks.; L1: SENTENCE_WITHOUT_OBJECT : 7 Full search strategy, verbatim, every source; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Search tab — the exact PubMed and ClinicalTrials.gov queries are printed verbatim and are re-runnable.; L1: SENTENCE_WITHOUT_OBJECT : 8 Selection process (screeners, disagreement); L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Two independently-implemented rule screeners; disagreement rate 0.0% (0/13); rule-based adjudicates. CAVEAT: both rule sets share an author and the same criteria, so they are NOT statistically independent and this agreement overstates reliability — a genuinely independent model screener is the next step.; L1: SENTENCE_WITHOUT_OBJECT : 9 Data collection process; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Results tab + per-trial Source column — source hierarchy (abstract > CT.gov structured > full text > hand-verified AACT arms), round-trip validation on every extraction, outcome-identity gating; refuse on ambiguity.; L1: SENTENCE_WITHOUT_OBJECT : 15 Certainty assessment; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Results tab — the machine-computable certainty signals are shown: imprecision via the 95% CI and the prediction interval, inconsistency via tau^2. A PARTIAL, object-derived GRADE is now rendered on the Risk-of-bias tab (risk-of-bias, inconsistency and imprecision computed from committed fields; publication bias is NOT ASSESSED automatically; any registry ghost census is descriptive until a PICO-scoped denominator is available; indirectness left to human judgement) — a graded certainty label with each domain's basis, not a full hand-graded GRADE.; L1: SENTENCE_WITHOUT_OBJECT : 16a Flow with counts at every stage; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Screening tab — PRISMA flow: identified -> screened -> excluded-by-rule (counts) -> eligible -> pooled k -> declared-absent.; L1: SENTENCE_WITHOUT_OBJECT : 16b Exclusions with reasons; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Screening tab — every excluded record lists its rule id, a reason true of the record, and a verbatim span.; L1: SENTENCE_WITHOUT_OBJECT : 24a-c Registration & protocol; L1: SENTENCE_WITHOUT_OBJECT : ✓ present; L1: SENTENCE_WITHOUT_OBJECT : Protocol + Reproducibility tabs — the protocol first entered the repository inside a BUILD commit (SHA bf99a91652), so prospective precedence is NOT demonstrated here and protocol-SHA byte-for-byte reproduction is not claimed; eligibility is generated from the structured object.; L1: SENTENCE_WITHOUT_OBJECT : 0; L1: SENTENCE_WITHOUT_OBJECT : NOT demonstrated for this topic — no protocol-only commit exists; the protocol first entered the repository inside a build commit (bf99a91652e74347e4e10cf6b9f1962aee4e596d), so this repository's history does not show the protocol preceding synthesis. The PICO is still fixed and replay from the committed cache is deterministic; only prospective PRECEDENCE is unproven here.; L1: SENTENCE_WITHOUT_OBJECT : bf99a91652e74347e4e10cf6b9f1962aee4e596d; L1: SENTENCE_WITHOUT_OBJECT : ad36eddb18fe10e436b3f3ea6aac2e60e53ad16812f7feda77b27549a6f3f571; L1: SENTENCE_WITHOUT_OBJECT : True; L1: SENTENCE_WITHOUT_OBJECT : Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.; L1: SENTENCE_WITHOUT_OBJECT : Each stated result on this page — whether it is statistically significant, whether its interval spans no effect — is derived from a single claim object, not recomputed per surface. At build the rendered page and manuscript are scanned for any wording that asserts the opposite of that object; the build is refused on a contradiction. Claims checked: 3; contradictions caught: 0; scope: grade=1, outcome_result=1, rob_sensitivity=3, strand_pool=2; surfaces checked=3; not in scope: verbatim source quotations, external comparator prose.; L1: SENTENCE_WITHOUT_OBJECT : Beyond significance, the build also refuses object-backed proposition contradictions: publication-bias state, declared-vs-enforced eligibility, protocol-SHA byte replay, pooled/rated/retracted counts, search-found membership, and state-label collapses. Proposition contradictions caught: 0; scope: publication_bias_state=1, declared_equals_enforced=1, byte_reproducible=1, pooled_count=1, rated_count=1, retracted_count=1, search_found=0, state_collapsed=0; not in scope: verbatim source quotations, external comparator prose without a committed object row.; L1: SENTENCE_WITHOUT_OBJECT : The prose protocol and executable config agree on these checked dimensions: none. Compared as separate sources.; L1: SENTENCE_WITHOUT_OBJECT : RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.; L1: HARMS_INCOMPLETE -- Gastrointestinal adverse events: HARMS_INCOMPLETE -- 10 known reported outcome(s) unresolved (31185157, 27633186, 27295427, 34215025, 31189511, 30291013, 28910237, 26630143) among 10 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.; Adverse events leading to discontinuation: HARMS_INCOMPLETE -- 9 known reported outcome(s) unresolved (31185157, 27633186, 27295427, 31189511, 30291013, 28910237, 26630143, FLOW) among 9 source-reporting trial(s); extracted k=0. The page must not render this as harm absence.
```

## Every remaining unregistered unit, verbatim

The following is the complete served-page list, preserving repeated text units, scanner order, unit IDs and contexts. None is silently relabelled structural or source-validated. These are quotations of audit debt, **not endorsed research claims**. Every entry is `SENTENCE_WITHOUT_OBJECT`.

### 1. `unit-0001` — `html/body/header/div`

```text
Reproducible meta-analysis harness — auditability, not authority
```

### 2. `unit-0002` — `html/body/header/div`

```text
Pinned audit identity — content hash of the canonical review object (review_sha256) ad36eddb18fe10e4; exact served bytes are attested separately (html_sha256 in manifest.json and the production record on the production-records branch). Cite this hash when auditing; a different hash is a different version of this page.
```

### 3. `unit-0009` — `html/body/main/table/tr/td`

```text
31185157
```

### 4. `unit-0010` — `html/body/main/table/tr/td`

```text
POOLED
```

### 5. `unit-0011` — `html/body/main/table/tr/td`

```text
27633186
```

### 6. `unit-0012` — `html/body/main/table/tr/td`

```text
POOLED
```

### 7. `unit-0013` — `html/body/main/table/tr/td`

```text
27295427
```

### 8. `unit-0014` — `html/body/main/table/tr/td`

```text
POOLED
```

### 9. `unit-0015` — `html/body/main/table/tr/td`

```text
31189511
```

### 10. `unit-0016` — `html/body/main/table/tr/td`

```text
POOLED
```

### 11. `unit-0017` — `html/body/main/table/tr/td`

```text
28910237
```

### 12. `unit-0018` — `html/body/main/table/tr/td`

```text
POOLED
```

### 13. `unit-0019` — `html/body/main/table/tr/td`

```text
26630143
```

### 14. `unit-0020` — `html/body/main/table/tr/td`

```text
POOLED
```

### 15. `unit-0021` — `html/body/main/table/tr/td`

```text
SOUL
```

### 16. `unit-0022` — `html/body/main/table/tr/td`

```text
POOLED
```

### 17. `unit-0023` — `html/body/main/table/tr/td`

```text
34215025
```

### 18. `unit-0024` — `html/body/main/table/tr/td`

```text
REFUSED
```

### 19. `unit-0025` — `html/body/main/table/tr/td`

```text
censoring
```

### 20. `unit-0026` — `html/body/main/table/tr/td`

```text
UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD
```

### 21. `unit-0027` — `html/body/main/table/tr/td`

```text
30291013
```

### 22. `unit-0028` — `html/body/main/table/tr/td`

```text
REFUSED
```

### 23. `unit-0029` — `html/body/main/table/tr/td`

```text
endpoint_components
```

### 24. `unit-0030` — `html/body/main/table/tr/td`

```text
axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion
```

### 25. `unit-0031` — `html/body/main/table/tr/td`

```text
FLOW
```

### 26. `unit-0032` — `html/body/main/table/tr/td`

```text
REFUSED
```

### 27. `unit-0033` — `html/body/main/table/tr/td`

```text
censoring
```

### 28. `unit-0034` — `html/body/main/table/tr/td`

```text
UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR
```

### 29. `unit-0039` — `html/body/main/table/tr/td`

```text
31185157
```

### 30. `unit-0040` — `html/body/main/table/tr/td`

```text
POOLED
```

### 31. `unit-0041` — `html/body/main/table/tr/td`

```text
27633186
```

### 32. `unit-0042` — `html/body/main/table/tr/td`

```text
POOLED
```

### 33. `unit-0043` — `html/body/main/table/tr/td`

```text
27295427
```

### 34. `unit-0044` — `html/body/main/table/tr/td`

```text
POOLED
```

### 35. `unit-0045` — `html/body/main/table/tr/td`

```text
31189511
```

### 36. `unit-0046` — `html/body/main/table/tr/td`

```text
POOLED
```

### 37. `unit-0047` — `html/body/main/table/tr/td`

```text
28910237
```

### 38. `unit-0048` — `html/body/main/table/tr/td`

```text
POOLED
```

### 39. `unit-0049` — `html/body/main/table/tr/td`

```text
26630143
```

### 40. `unit-0050` — `html/body/main/table/tr/td`

```text
POOLED
```

### 41. `unit-0051` — `html/body/main/table/tr/td`

```text
SOUL
```

### 42. `unit-0052` — `html/body/main/table/tr/td`

```text
POOLED
```

### 43. `unit-0053` — `html/body/main/table/tr/td`

```text
FREEDOM-CVO
```

### 44. `unit-0054` — `html/body/main/table/tr/td`

```text
POOLED
```

### 45. `unit-0055` — `html/body/main/table/tr/td`

```text
34215025
```

### 46. `unit-0056` — `html/body/main/table/tr/td`

```text
REFUSED
```

### 47. `unit-0057` — `html/body/main/table/tr/td`

```text
censoring
```

### 48. `unit-0058` — `html/body/main/table/tr/td`

```text
UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD
```

### 49. `unit-0059` — `html/body/main/table/tr/td`

```text
30291013
```

### 50. `unit-0060` — `html/body/main/table/tr/td`

```text
REFUSED
```

### 51. `unit-0061` — `html/body/main/table/tr/td`

```text
endpoint_components
```

### 52. `unit-0062` — `html/body/main/table/tr/td`

```text
axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion
```

### 53. `unit-0063` — `html/body/main/table/tr/td`

```text
FLOW
```

### 54. `unit-0064` — `html/body/main/table/tr/td`

```text
REFUSED
```

### 55. `unit-0065` — `html/body/main/table/tr/td`

```text
censoring
```

### 56. `unit-0066` — `html/body/main/table/tr/td`

```text
UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR
```

### 57. `unit-0067` — `html/body/main/span`

```text
[FACT] PMID 34873344: HR 1.36 (0.96, 1.92).
```

### 58. `unit-0104` — `html/body/main/section/ul/li`

```text
Favourable topic sample. Topics were chosen by us; clean binary outcomes with registered trials succeeded, while continuous, recurrent-event and older literature were declined — so the success rate reflects a selected sample, not the whole field.
```

### 59. `unit-0105` — `html/body/main/section/ul/li`

```text
Risk of bias is partial. Registry-machine-signal-restricted domains are computed from machine-available registry fields; domains needing human reading are marked not-assessed.
```

### 60. `unit-0106` — `html/body/main/section/ul/li`

```text
Registry snapshot is dated. AACT is a fixed local snapshot; trials registered, or results posted, after it are invisible to the registry-first recall, ghost and registry-machine-signal-restricted signals (the snapshot date is shown on those blocks). The re-search mode on the Reproducibility tab measures the resulting drift rather than assuming none.
```

### 61. `unit-0108` — `html/body/main/section/ul/li`

```text
The blind comparison is judged by an AI, and transparency is what we optimise for. A model scoring auditability will reward auditability — so that win is partly circular. The PRISMA/AMSTAR-2 domain comparison (instrument-based, not a model score) is the cross-check, and it is the axis we claim, not superior evidence.
```

### 62. `unit-0110` — `html/body/main/section/table/tr/td`

```text
bf99a91652e74347e4e10cf6b9f1962aee4e596d
```

### 63. `unit-0112` — `html/body/main/section/table/tr/td`

```text
2026-09-11
```

### 64. `unit-0114` — `html/body/main/section/table/tr/td`

```text
Random-effects inverse-variance on the log ratio (log RR/OR/HR/IRR as configured for the outcome); Paule-Mandel tau^2; HKSJ 95% CI on t_{k-1} (variance floor max(1,Q/(k-1))); prediction interval mu +/- t_{k-1}*sqrt(tau2+se^2). Validated vs metafor 5.0.1 (this canonical code path; every rendered interval is gate-checked to originate here).
```

### 65. `unit-0116` — `html/body/main/section/table/tr/td`

```text
Included iff ALL hold: a randomised controlled trial; population (in title/registry conditions) mentions one of ['type 2 diabetes', 'type 2 diabetic', 'type 2 diabetes mellitus', 'diabetes mellitus, type 2', 't2d', 't2dm']; and none of ['without diabetes', 'no diabetes', 'obesity without diabetes', 'overweight or obesity but without diabetes', 'type 1 diabetes', 'gestational diabetes']; randomised intervention is one of ['liraglutide', 'semaglutide', 'dulaglutide', 'albiglutide', 'efpeglenatide', 'exenatide', 'lixisenatide'] (named in title/conditions); a comparator among ['placebo']. Excluded (rule id + verbatim span on each record): X1 not an RCT · X2 wrong/off-topic population · X3 wrong intervention/comparator.
```

### 66. `unit-0117` — `html/body/main/section`

```text
# Protocol - GLP-1 receptor agonists for 3-point MACE in type 2 diabetes **Registration.** The commit that adds this file is the registration of this review; its SHA is embedded in the page's Protocol tab and its Reproducibility tab. Committed BEFORE the synthesis is run. ## PICO - **P** - adults with type 2 diabetes. - **I** - GLP-1 receptor agonist therapy (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, or lixisenatide) added to usual care. - **C** - placebo added to usual care. - **O (primary)** - 3-point major adverse cardiovascular events, defined as cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke. - **O (harms / secondary)** - gastrointestinal adverse events, discontinuation for adverse events, and any further harm outcome the resolved comparator reports. ## Estimand / population / timepoint - **Estimand** - hazard ratio (HR), GLP-1 receptor agonist vs placebo. - **Population** - intention-to-treat as randomised. - **Timepoint** - trial end / longest primary cardiovascular outcome follow-up. ## Eligibility - on P/I/C/DESIGN ONLY Include a record iff **all** hold: - **I1** - randomised controlled trial; - **I2** - population is adults with type 2 diabetes, judged from the title or registry conditions; - **I3** - a GLP-1 receptor agonist vs placebo contrast; - **design** - double-blind, placebo-controlled. Exclude (reason must be true of the record): - **X1** - not an RCT (review, guideline, observational, protocol-only); - **X2** - wrong population (e.g. obesity without diabetes, type 1 diabetes, or gestational diabetes); - **X3** - wrong intervention/comparison (no GLP-1 receptor agonist-vs-placebo contrast); - **X-DESIGN** - not double-blind and placebo-controlled; - **X5** - off-topic: a primary trial of another topic in this set (negative control). > **Eligibility is NOT on the outcome axis.** Whether a trial reports 3-point MACE, or gives > a 2x2 vs only an effect+CI, is recorded as target-result status at extraction - never as > an exclusion. A published effect + 95% CI is a poolable input. ## Search (fetch-once; raw results committed under cache/<slug>/search.json; screening replays offline) - PubMed: exact-title sweeps for the large GLP-1 receptor agonist cardiovascular outcome trials in type 2 diabetes (LEADER, SUSTAIN-6, REWIND, HARMONY Outcomes, AMPLITUDE-O, PIONEER-6, EXSCEL, and ELIXA). - ClinicalTrials.gov: condition "type 2 diabetes cardiovascular", intervention "efpeglenatide". - Fixed-screen note: several PubMed abstracts for verified double-blind CVOTs do not use the literal phrase "double-blind"; the config therefore does not require that literal abstract/title string, while the protocol eligibility criterion remains double-blind placebo-controlled design. ## Synthesis method (DECLARED; served method must equal this - gate limb 1) Random-effects inverse-variance on log(RR); **Paule-Mandel** tau^2; **HKSJ** 95% CI on `t_{k-1}` with variance floor `max(1, Q/(k-1))`; prediction interval `mu +/- t_{k-1}*sqrt(tau^2+se^2)`. DerSimonian-Laird forbidden. Engine validated vs metafor 5.0.1 (<1e-6). For this topic, the poolable input is the published HR + 95% CI path on the same ratio/log scale; 2x2 extraction is available but is not required when a trial reports an HR + CI. ## Comparator (resolved; open-access confirmed) Giugliano et al., *Cardiovascular Diabetology* 2021, "GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs" (PMID 34526024, DOI 10.1186/s12933-021-01366-8; Unpaywall is_oa=true; PubMed Central PMC8442438). It reports pooled MACE HR 0.86 (95% CI 0.79-0.94) over 8 cardiovascular outcome trials. ## Controls - **Positive** - the search must recover and include LEADER, SUSTAIN-6, and REWIND. - **Negative** - SELECT (semaglutide, double-blind, placebo-controlled, but obesity without diabetes - another disease population) must be recovered and EXCLUDED by the population rule. ## Amendment 2026-09-16 (eligibility, estimand, effect measure, timepoint, screening, search, comparator, harms, RoB 2, GRADE -- "B-prime") Executable strand declarations (delivery boundaries only; all members must also pass P/I/C/design eligibility, held-source verification and binding effect axes): `CONVENTIONAL_GLP1RA` is primary and excludes PMID 34873344 (FREEDOM-CVO, continuous delivery); `GLP1RA_ANY_DELIVERY` is non-primary and has no delivery exclusions. These correspond to `membership_rule.exclude_ids: ["34873344"]` and `membership_rule.exclude_ids: []` in the topic JSON. Neither declaration overrides a refused binding axis. End-of-treatment sensitivity values are never pool candidates. Refused rows remain visible with their axis and reason. **Status: RETROSPECTIVE.** Registered under Mahmood's authority ("fix all in reproducible harness", 16 Sep 2026, via Dispatch) after an independent protocol audit of registration commit `4091958ce4af7f1ca9ed4c30e1021672b0c21223` found that the registered eligibility (a broad GLP-1 review; eligibility explicitly not on the outcome axis) and the registered search (exact-title sweeps for eight named cardiovascular outcome trials) define two different reviews. This amendment is appended before the page is rebuilt against it and does not rename the pinned slug/URL. **Both alternative answers were known when this rule was written**, and are disclosed below; that disclosure is the point of the RETROSPECTIVE label. - **Question.** Among adults with type 2 diabetes, what is the effect of GLP-1 receptor agonist therapy versus placebo on time to first adjudicated 3-point MACE? - **Eligibility (B-prime).** Parallel-group randomised, double-blind, placebo-controlled trials of the prespecified GLP-1 RAs (liraglutide, semaglutide, dulaglutide, albiglutide, efpeglenatide, exenatide, lixisenatide) in adults with type 2 diabetes **in which 3-point MACE, or its exact three components, was prospectively specified and systematically ascertained** -- preferably with blinded or independent adjudication. Eligibility does **not** depend on the direction, statistical significance or published availability of the MACE result. **If MACE was measured but the result is unavailable, the trial is retained and the result is pursued** through full text, registry results, regulatory documents or investigators, with an OPEN recovery obligation rendered until it is held. - **Alternatives disclosed.** Under **A** (the literal registered rule: outcome not an eligibility axis) the universe would additionally include SUSTAIN-1, PIONEER-1, AWARD-8, LEAD-2, Harmony 1, AMPLITUDE-M, GetGoal-P, GetGoal-L, GetGoal-Mono, FREEDOM-1 and others, entering screening and exiting on outcome availability. Under **B** ("large cardiovascular outcome trials") the universe would be the eight seeded CVOTs, with "large" and "CVOT" undefined. B-prime yields the intended small universe by a stated, executable criterion (prospective systematic ascertainment of the outcome), not by a label or by which results are convenient. FLOW (semaglutide, T2D with CKD; MACE prospectively adjudicated) is eligible under B-prime; FREEDOM-CVO (ITCA 650) is eligible under B-prime on the intervention-class strand that admits continuous delivery (see the class-boundary decision: `CONVENTIONAL_GLP1RA` primary strand, `GLP1RA_ANY_DELIVERY` rendered alongside); ELIXA (lixisenatide; 4-point primary, 3-point components prospectively ascertained) is eligible, its 3-point result pursued from the primary supplement or regulatory record, never from a secondary meta-analysis. - **Estimand.** Intention-to-treat effect of assignment to GLP-1 RA versus placebo on **time to first** occurrence of cardiovascular death, nonfatal myocardial infarction or nonfatal stroke during the prespecified randomised cardiovascular follow-up. Trial definitions that count **undetermined death as cardiovascular death** are accepted as each trial's prespecified adjudicated definition and recorded per trial in the compatibility key (`undetermined_death_counted_as_cv: yes/no/unstated`); no re-adjudication is attempted. - **Effect measure.** The primary analysis pools **log-HRs only** (published, or validly reconstructed from a time-to-event analysis). Ordinary RRs, ORs and IRRs do not enter the primary pool. Where only fixed-time counts are recoverable, a separate RR sensitivity analysis is reported. (Supersedes the registered synthesis sentence "random-effects inverse-variance on log(RR)", which contradicted the registered HR estimand.) - **Timepoint.** The trial's prespecified primary cardiovascular analysis **at the end of randomised, blinded follow-up**. Post-trial and extension follow-up are analysed separately and never substitute for the primary analysis. - **Screening.** The **clinical eligibility rule** (above) is separate from the **machine screening heuristic**. Title and registry-condition term matching is a first-pass heuristic only; final eligibility is decided from abstract, then registry record, then full text/protocol as needed, on a canonical trial object (trial / arm / drug / dose / route / background therapy / population / timepoint / analysis set). A trial must not become ineligible because a term is absent from its title. Every screening decision carries the source span it rests on. - **Search.** Independent concept search across all seven eligible agents in PubMed/MEDLINE and Europe PMC, **the Cochrane CENTRAL register** (free; carries Embase-derived records), ClinicalTrials.gov via the local AACT snapshot (queried symmetrically across agents, not only efpeglenatide), **WHO ICTRP** (non-US registries) and ISRCTN, plus citation chasing and the trial-family assembly of every report, registry record, supplement and regulatory document. **No trial-name seed list is the primary retrieval mechanism.** Every retrieved record carries `entered_via` (executed query / seeded identifier / manual addition) and the rejection trail (families retrieved and refused, each with a typed reason) is rendered. - **Declared scope boundary (not a defect): no Embase.** This review does not search Embase. Its unique contribution over MEDLINE is mainly conference abstracts and European/pharma-journal reports; for large registered cardiovascular outcome trials -- this topic -- the marginal yield is low because every such trial is MEDLINE-indexed and registered, and CENTRAL + registries recover part of Embase's unique yield. The completeness claim is therefore for **registered trials**; Embase-equivalent coverage of conference and grey literature is not claimed. (For topics dominated by small or older trials the gap matters considerably more; each topic's protocol states which kind it is.) - **Source hierarchy for every extracted value (recorded and rendered as `source_level`):** 1 the trial's own publication and supplement; 2 regulatory review (FDA, EMA) -- primary re-analysis of trial data; 3 registry results (ClinicalTrials.gov / AACT) -- sponsor-posted structured data; 4 HTA assessment (NICE); 5 older meta-analyses -- **pointers only, never the number itself** (several published reviews relabelled ELIXA's 4-point MACE as 3-point; a value found in a meta is traced to a level 1-4 source or refused). A label such as `PUBLISHED_UNADJUSTED` is assigned only after the estimator is read at the source. - **Full-text reachability ladder.** Before `abstract only` may be recorded the extractor tries, in order: PMC / Europe PMC deposits; supplementary appendices (where exact secondary endpoints such as ELIXA's and FREEDOM-CVO's 3-point MACE live); publisher open-access versions; author accepted manuscripts in institutional repositories; regulatory documents (FDA, EMA); ClinicalTrials.gov / AACT results. The route that succeeded is recorded; `abstract only` is replaced by `full text not reachable after N named attempts`, listing them. An unreachability claim with no attempt log is the same defect as an absence claim with no negative citation. - **Comparator.** The published comparator meta-analysis is resolved **only after the independent evidence search is locked**; published meta-analyses are used for reference checking, never for seeding. Parity compares the comparator's eligibility rules, not only its trial list. - **Harms.** Gastrointestinal adverse events and discontinuation due to adverse events are prespecified harm outcomes. Any further harm outcome a resolved comparator happens to report is **exploratory**, not prespecified, and is labelled so. - **Risk of bias.** Full outcome-specific RoB 2 on the primary result (effect of assignment): five domains, signalling questions, information sources (protocol, statistical analysis plan, registry record, primary publication and supplement), adjudication method (two assessors, disagreements recorded, not silently resolved), and a planned sensitivity analysis restricted to low-risk-of-bias trials. Registry-derived machine signals are rendered as `machine signal consistent with low risk; formal RoB 2 not assessed` until the sources above have been read; they are never rendered as RoB 2 judgements. - **GRADE.** Prespecified across all five domains (risk of bias, inconsistency, imprecision, indirectness, publication bias). **No certainty category is issued while any domain is unassessed**; the page renders `GRADE provisional -- not yet fully assessable` instead. Imprecision reflects whether the confidence interval permits materially different clinical conclusions, not a mechanical significance test; a prediction interval approaching 1 is not by itself grounds for downgrading. - **Pre-specified list (intervention agents).** liraglutide; semaglutide (subcutaneous and oral); dulaglutide; albiglutide; efpeglenatide; exenatide (immediate- and extended-release; ITCA 650 continuous subcutaneous delivery on the `GLP1RA_ANY_DELIVERY` strand); lixisenatide. ## Retrospective executable clarification — 2026-09-17 This states which existing B-prime rules bind effect-type unification; it changes no clinical rule. Endpoint components (3-point MACE), effect measure (HR, pooled on the log scale), and timepoint/censoring (end of randomised follow-up) are binding. Analysis set, adjustment, estimator, time origin, and follow-up length are disclosed, not binding. All other axes are non-binding. Unknown evidence remains UNKNOWN with its absence code; a missing binding value cannot be filled from this target. ```effect-type-binding { "schema_version": 1, "outcomes": { "3-point major adverse cardiovascular events": { "endpoint_components": [ "CV_DEATH", "NONFATAL_MI", "NONFATAL_STROKE" ], "effect_measure": "HR", "censoring": "end-of-study" } } } ```
```

### 67. `unit-0124` — `html/body/main/section/div/p`

```text
Snapshot: records_sha256 1e0282f5; retrieved_utc 2026-09-11; mode LEGACY_UNRECORDED: a pre-ledger fetch; which query retrieved which record was not recorded; every record's found_by names this single source.
```

### 68. `unit-0125` — `html/body/main/section/div/p`

```text
This page replays the committed retrieval snapshot; it is not a claim that the protocol SHA alone regenerates the page byte-for-byte. A live re-search is a separate, dated event (see Re-search below if present).
```

### 69. `unit-0126` — `html/body/main/section/div`

```text
No search was run for this topic: every PubMed source is a PMID enumeration.
```

### 70. `unit-0162` — `html/body/main/section/p`

```text
Citation chase: NOT_RUN · ClinicalTrials.gov: RAN_OK · Europe PMC (OA + metadata): RAN_OK · Legacy unrecorded retrieval: RAN_OK · PMC full text: NOT_RUN · PubMed: RAN_OK · Registry-first (AACT): RAN_OK — RAN_OK = ran and returned records; RAN_ZERO = ran, none matched; RAN_ERROR = attempted but failed; NOT_RUN = not attempted for this topic.
```

### 71. `unit-0163` — `html/body/main/section/div/p`

```text
KNOWN-ITEM RETRIEVAL — NOT A SYSTEMATIC SEARCH We retract any claim of a registry-first or systematic search for this topic. an auditable screening ledger attached to an unauditable retrieval process.
```

### 72. `unit-0179` — `html/body/main/section/div`

```text
Search provenance — not a completed systematic search. The registry-first (AACT) adapter status for this topic is RAN_OK; its evidence set was assembled by KNOWN-ITEM RETRIEVAL of named publications (UID/PMID-anchored queries for pre-identified trials), which cannot discover an unknown eligible trial. A fetch of named identifiers is not a systematic search. We retract any claim of a registry-first or systematic search for this topic.
```

### 73. `unit-0180` — `html/body/main/section/p`

```text
Positive-control recovery: the committed registry query re-found 6/7 of this topic's PRE-SPECIFIED known trials (pooled + declared positive controls; enumerated 708; status RAN_OK). Reachable ceiling 7/7: 1 trial(s) are registered but not enumerated by the committed query (registry vocabulary limit — improvable). Missed: 30291013. Measured 2026-09-11T23:39:14Z. This is not systematic-review recall. It measures whether the committed registry query re-finds the trials ALREADY KNOWN to the build; a trial that was never in the known set is not in the denominator, so a high value does not mean the search is complete ? external audits found eligible trials (J-EMPHASIS-HF, an eplerenone trial, for the MRA topic published under the identifier spironolactone-hfref-mortality, PHILO for ticagrelor) entirely absent precisely because they were never in a known set. True recall needs an INDEPENDENTLY-GENERATED reference universe (concept query + registry enumeration, not the seed list); that rebuild is in progress. Recovery is also search REACH, not inclusion — whether a recovered trial is eligible/poolable is the screen's and extractor's job.
```

### 74. `unit-0181` — `html/body/main/section/p`

```text
Of 708 registry records matching the query (broad — reach, not precision): 397 have a linked publication; 62 have posted CT.gov results but no publication (poolable unpublished data no published meta in this topic has); 118 are completed ≥12 months ago with neither results nor a linked publication — a loose upper bound on non-publication, inflated by the broad enumeration and by NCT→PMID linkage misses, not a publication-bias claim. AACT 2026-08-30 (local snapshot).
```

### 75. `unit-0186` — `html/body/main/section/p`

```text
Identifier scope: identifier leading token matches class term GLP-1RA. Verdict: NOT_APPLICABLE.
```

### 76. `unit-0188` — `html/body/main/section/p`

```text
Two independently-implemented rule screeners over 13 records: agreement 13/13, disagreement 0.0% (0 records). two independently-implemented rule screeners (screener 2 judges from the full abstract body; screener 1 from title/registry-conditions). Adjudicator: screener 1. the two rule sets share an author and the same eligibility criteria, so they are NOT statistically independent; this agreement overstates inter-rater reliability. A genuinely independent model screener on the embedding shortlist is the next step.
```

### 77. `unit-0189` — `html/body/main/section/p`

```text
Trial integrity: 7 of 7 pooled trials covered by the historical PubMed check. No retraction was recorded in that checked set. Current integrity status unassessed for PMID 26630143, 38785209; the offline source set does not establish a current retraction check.
```

### 78. `unit-0330` — `html/body/main/section/ul/li`

```text
Positive: Recovered & included the canonical trials ['27295427', '27633186', '31189511'] that a comparator includes; none missed.
```

### 79. `unit-0331` — `html/body/main/section/ul/li`

```text
Negative: Cross-topic trial(s) ['37952131'] recovered by the search and correctly EXCLUDED ['37952131'] by rule (same drug/design, wrong topic).
```

### 80. `unit-0332` — `html/body/main/section/div/p`

```text
5 of 25 declared-absent/refusal reason code(s) have a numeric value in a held source; 0 wrong-kind code(s); 0 not verifiable from held sources. Registered-outcome sweep: 6 of 33 included-trial/outcome pair(s) are held-but-not-extracted.
```

### 81. `unit-0338` — `html/body/main/section/div/table/tr/td`

```text
34215025
```

### 82. `unit-0339` — `html/body/main/section/div/table/tr/td`

```text
3-point major adverse cardiovascular events
```

### 83. `unit-0340` — `html/body/main/section/div/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 84. `unit-0341` — `html/body/main/section/div/table/tr/td`

```text
REASON_FALSE_VALUE_HELD
```

### 85. `unit-0342` — `html/body/main/section/div/table/tr/td`

```text
abstract:34215025
```

### 86. `unit-0343` — `html/body/main/section/div/table/tr/td`

```text
During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p...
```

### 87. `unit-0344` — `html/body/main/section/div/table/tr/td`

```text
30291013
```

### 88. `unit-0345` — `html/body/main/section/div/table/tr/td`

```text
3-point major adverse cardiovascular events
```

### 89. `unit-0346` — `html/body/main/section/div/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 90. `unit-0347` — `html/body/main/section/div/table/tr/td`

```text
REASON_FALSE_VALUE_HELD
```

### 91. `unit-0348` — `html/body/main/section/div/table/tr/td`

```text
abstract:30291013
```

### 92. `unit-0349` — `html/body/main/section/div/table/tr/td`

```text
The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i...
```

### 93. `unit-0350` — `html/body/main/section/div/table/tr/td`

```text
38785209
```

### 94. `unit-0351` — `html/body/main/section/div/table/tr/td`

```text
3-point major adverse cardiovascular events
```

### 95. `unit-0352` — `html/body/main/section/div/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 96. `unit-0353` — `html/body/main/section/div/table/tr/td`

```text
REASON_FALSE_VALUE_HELD
```

### 97. `unit-0354` — `html/body/main/section/div/table/tr/td`

```text
abstract:38785209
```

### 98. `unit-0355` — `html/body/main/section/div/table/tr/td`

```text
Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).
```

### 99. `unit-0356` — `html/body/main/section/div/table/tr/td`

```text
34873344
```

### 100. `unit-0357` — `html/body/main/section/div/table/tr/td`

```text
Gastrointestinal adverse events
```

### 101. `unit-0358` — `html/body/main/section/div/table/tr/td`

```text
OUTCOME_NOT_IN_SOURCE
```

### 102. `unit-0359` — `html/body/main/section/div/table/tr/td`

```text
REASON_FALSE_VALUE_HELD
```

### 103. `unit-0360` — `html/body/main/section/div/table/tr/td`

```text
abstract:34873344
```

### 104. `unit-0361` — `html/body/main/section/div/table/tr/td`

```text
Adverse events were more frequent in the ITCA 650 group (72%, 1,491/2,074) than in the placebo group (63.9%, 1,325/2,070), mainly due to an increase in gastrointestinal events and disorders while on ITCA 650.
```

### 105. `unit-0362` — `html/body/main/section/div/table/tr/td`

```text
27295427
```

### 106. `unit-0363` — `html/body/main/section/div/table/tr/td`

```text
Adverse events leading to discontinuation
```

### 107. `unit-0364` — `html/body/main/section/div/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 108. `unit-0365` — `html/body/main/section/div/table/tr/td`

```text
REASON_FALSE_VALUE_HELD
```

### 109. `unit-0366` — `html/body/main/section/div/table/tr/td`

```text
fulltext:27295427
```

### 110. `unit-0367` — `html/body/main/section/div/table/tr/td`

```text
The primary outcome occurred in significantly fewer patients in the liraglutide group (608 of 4668 patients [13.0%]) than in the placebo group (694 of 4672 [14.9%]) (hazard ratio, 0.87; 95% confidence interval [CI], 0.78 to 0.97; P&lt;0.00...
```

### 111. `unit-0483` — `html/body/main/section/table/tr/td`

```text
34215025
```

### 112. `unit-0484` — `html/body/main/section/table/tr/td`

```text
PMID 34215025
```

### 113. `unit-0485` — `html/body/main/section/table/tr/td`

```text
not extracted — the outcome's number IS in the source (extraction gap, not trial absence)
```

### 114. `unit-0486` — `html/body/main/section/table/tr/td`

```text
UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD
```

### 115. `unit-0487` — `html/body/main/section/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 116. `unit-0488` — `html/body/main/section/table/tr/td`

```text
reason-code audit: REASON_FALSE_VALUE_HELD abstract:34215025: During a median follow-up of 1.81 years, an incident MACE occurred in 189 participants (7.0%) assigned to receive efpeglenatide (3.9 events per 100 person-years) and 125 participants (9.2%) assigned to receive placebo (5.3 events per 100 p...
```

### 117. `unit-0489` — `html/body/main/section/table/tr/td`

```text
span: ( hazard ratio, 0.73; 95% confidence interval [CI], 0.58 to 0.92; P<0.001 for noninferiority; P = 0.007 for superiority).
```

### 118. `unit-0490` — `html/body/main/section/table/tr/td`

```text
basis: EXTRACTION_NOT_PERFORMED: source span: "( hazard ratio, 0.73; 95% confidence interval [CI], 0.58 to 0.92; P<0.001 for noninferiority; P = 0.007 for superiority)."; effect=HR 0.73 [0.58, 0.92], class=FIRST_EVENT_RATIO, declared_class=FIRST_EVENT_RATIO
```

### 119. `unit-0491` — `html/body/main/section/table/tr/td`

```text
completeness: eligible+completed+results_available
```

### 120. `unit-0492` — `html/body/main/section/table/tr/td`

```text
completeness basis: CT.gov status/results dates from local AACT snapshot
```

### 121. `unit-0493` — `html/body/main/section/table/tr/td`

```text
30291013
```

### 122. `unit-0494` — `html/body/main/section/table/tr/td`

```text
PMID 30291013
```

### 123. `unit-0495` — `html/body/main/section/table/tr/td`

```text
not extracted — the outcome's number IS in the source (extraction gap, not trial absence)
```

### 124. `unit-0496` — `html/body/main/section/table/tr/td`

```text
axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion
```

### 125. `unit-0497` — `html/body/main/section/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 126. `unit-0498` — `html/body/main/section/table/tr/td`

```text
reason-code audit: REASON_FALSE_VALUE_HELD abstract:30291013: The primary composite outcome occurred in 338 (7%) of 4731 patients at an incidence rate of 4.6 events per 100 person-years in the albiglutide group and in 428 (9%) of 4732 patients at an incidence rate of 5.9 events per 100 person-years i...
```

### 127. `unit-0499` — `html/body/main/section/table/tr/td`

```text
span: of 4732 patients at an incidence rate of 5.9 events per 100 person-years in the placebo group ( hazard ratio 0.78, 95% CI 0.68-0.90), which indicated that albiglutide was superior to placebo (p<0.000...
```

### 128. `unit-0500` — `html/body/main/section/table/tr/td`

```text
basis: EXTRACTION_NOT_PERFORMED: source span: "of 4732 patients at an incidence rate of 5.9 events per 100 person-years in the placebo group ( hazard ratio 0.78, 95% CI 0.68-0.90), which indicated that albiglutide was superior to placebo (p<0.000..."; effect=HR 0.78 [0.68, 0.9], class=FIRST_EVENT_RATIO, declared_class=FIRST_EVENT_RATIO
```

### 129. `unit-0501` — `html/body/main/section/table/tr/td`

```text
completeness: eligible+completed+results_available
```

### 130. `unit-0502` — `html/body/main/section/table/tr/td`

```text
completeness basis: CT.gov status/results dates from local AACT snapshot
```

### 131. `unit-0503` — `html/body/main/section/table/tr/td`

```text
FLOW
```

### 132. `unit-0504` — `html/body/main/section/table/tr/td`

```text
PMID 38785209
```

### 133. `unit-0505` — `html/body/main/section/table/tr/td`

```text
not extracted — the outcome's number IS in the source (extraction gap, not trial absence)
```

### 134. `unit-0506` — `html/body/main/section/table/tr/td`

```text
UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR
```

### 135. `unit-0507` — `html/body/main/section/table/tr/td`

```text
EXTRACTION_NOT_PERFORMED
```

### 136. `unit-0508` — `html/body/main/section/table/tr/td`

```text
reason-code audit: REASON_FALSE_VALUE_HELD abstract:38785209: Results were similar for a composite of the kidney-specific components of the primary outcome (hazard ratio, 0.79; 95% CI, 0.66 to 0.94) and for death from cardiovascular causes (hazard ratio, 0.71; 95% CI, 0.56 to 0.89).
```

### 137. `unit-0509` — `html/body/main/section/table/tr/td`

```text
span: and for death from cardiovascular causes ( hazard ratio, 0.71; 95% CI, 0.56 to 0.89).
```

### 138. `unit-0510` — `html/body/main/section/table/tr/td`

```text
basis: EXTRACTION_NOT_PERFORMED: source span: "and for death from cardiovascular causes ( hazard ratio, 0.71; 95% CI, 0.56 to 0.89)."; effect=HR 0.71 [0.56, 0.89], class=FIRST_EVENT_RATIO, declared_class=FIRST_EVENT_RATIO
```

### 139. `unit-0511` — `html/body/main/section/table/tr/td`

```text
completeness: eligible+completed+results_available
```

### 140. `unit-0512` — `html/body/main/section/table/tr/td`

```text
completeness basis: CT.gov status/results dates from local AACT snapshot
```

### 141. `unit-0513` — `html/body/main/section/section/p`

```text
Candidate rows, including type refusals.
```

### 142. `unit-0514` — `html/body/main/section/section/p`

```text
Protocol-declared binding axes: endpoint_components, effect_measure, censoring. All remaining axes are non-binding.
```

### 143. `unit-0526` — `html/body/main/section/section/table/tr/th`

```text
1. population
```

### 144. `unit-0527` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 145. `unit-0528` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 146. `unit-0529` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 147. `unit-0530` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 148. `unit-0531` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 149. `unit-0532` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 150. `unit-0533` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 151. `unit-0534` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 152. `unit-0535` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 153. `unit-0536` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 154. `unit-0537` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 155. `unit-0538` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 156. `unit-0539` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 157. `unit-0540` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 158. `unit-0541` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 159. `unit-0542` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 160. `unit-0543` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 161. `unit-0544` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 162. `unit-0545` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 163. `unit-0546` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 164. `unit-0547` — `html/body/main/section/section/table/tr/th`

```text
2. randomised_contrast
```

### 165. `unit-0548` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 166. `unit-0549` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 167. `unit-0550` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 168. `unit-0551` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 169. `unit-0552` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 170. `unit-0553` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 171. `unit-0554` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 172. `unit-0555` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 173. `unit-0556` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 174. `unit-0557` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 175. `unit-0558` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 176. `unit-0559` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 177. `unit-0560` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 178. `unit-0561` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 179. `unit-0562` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 180. `unit-0563` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 181. `unit-0564` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 182. `unit-0565` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 183. `unit-0566` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 184. `unit-0567` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 185. `unit-0568` — `html/body/main/section/section/table/tr/th`

```text
3. analysis_set
```

### 186. `unit-0569` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 187. `unit-0570` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 188. `unit-0571` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 189. `unit-0572` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 190. `unit-0573` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 191. `unit-0574` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 192. `unit-0575` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 193. `unit-0576` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 194. `unit-0577` — `html/body/main/section/section/table/tr/td`

```text
ITT
```

### 195. `unit-0578` — `html/body/main/section/section/table/tr/td`

```text
span: intention-to-treat
```

### 196. `unit-0579` — `html/body/main/section/section/table/tr/td`

```text
record:31189511.source/abstract
```

### 197. `unit-0580` — `html/body/main/section/section/table/tr/td`

```text
ITT
```

### 198. `unit-0581` — `html/body/main/section/section/table/tr/td`

```text
span: intention-to-treat
```

### 199. `unit-0582` — `html/body/main/section/section/table/tr/td`

```text
record:30291013.source/abstract
```

### 200. `unit-0583` — `html/body/main/section/section/table/tr/td`

```text
ITT
```

### 201. `unit-0584` — `html/body/main/section/section/table/tr/td`

```text
span: intention-to-treat
```

### 202. `unit-0585` — `html/body/main/section/section/table/tr/td`

```text
record:28910237.source/abstract
```

### 203. `unit-0586` — `html/body/main/section/section/table/tr/td`

```text
ITT
```

### 204. `unit-0587` — `html/body/main/section/section/table/tr/td`

```text
span: ITT
```

### 205. `unit-0588` — `html/body/main/section/section/table/tr/td`

```text
record:26630143.source/abstract
```

### 206. `unit-0589` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 207. `unit-0590` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 208. `unit-0591` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 209. `unit-0592` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 210. `unit-0593` — `html/body/main/section/section/table/tr/th`

```text
4. endpoint_components
```

### 211. `unit-0594` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 212. `unit-0595` — `html/body/main/section/section/table/tr/td`

```text
span: The primary outcome in a time-to-event analysis was the first occurrence of a major adverse cardiovascular event (death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke)
```

### 213. `unit-0596` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 214. `unit-0597` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 215. `unit-0598` — `html/body/main/section/section/table/tr/td`

```text
span: The primary composite outcome was the first occurrence of cardiovascular death, nonfatal myocardial infarction, or nonfatal stroke
```

### 216. `unit-0599` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 217. `unit-0600` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 218. `unit-0601` — `html/body/main/section/section/table/tr/td`

```text
span: The primary composite outcome in the time-to-event analysis was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke
```

### 219. `unit-0602` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 220. `unit-0603` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 221. `unit-0604` — `html/body/main/section/section/table/tr/td`

```text
span: The primary outcome was the first major adverse cardiovascular event (MACE; a composite of nonfatal myocardial infarction, nonfatal stroke, or death from cardiovascular or undetermined causes)
```

### 222. `unit-0605` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 223. `unit-0606` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 224. `unit-0607` — `html/body/main/section/section/table/tr/td`

```text
span: The primary outcome was the first occurrence of the composite endpoint of non-fatal myocardial infarction, non-fatal stroke, or death from cardiovascular causes (including unknown causes), which was assessed in the intention-to-treat population
```

### 225. `unit-0608` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 226. `unit-0609` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED']
```

### 227. `unit-0610` — `html/body/main/section/section/table/tr/td`

```text
span: We hypothesised that albiglutide would be non-inferior to placebo for the primary outcome of the first occurrence of cardiovascular death, myocardial infarction, or stroke, which was assessed in the intention-to-treat population
```

### 228. `unit-0611` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 229. `unit-0612` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 230. `unit-0613` — `html/body/main/section/section/table/tr/td`

```text
span: The primary composite outcome was the first occurrence of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke
```

### 231. `unit-0614` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 232. `unit-0615` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 233. `unit-0616` — `html/body/main/section/section/table/tr/td`

```text
span: MACE, defined as cardiovascular death, non-fatal MI, and non-fatal stroke
```

### 234. `unit-0617` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt
```

### 235. `unit-0618` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 236. `unit-0619` — `html/body/main/section/section/table/tr/td`

```text
span: The primary outcome was major adverse cardiovascular events (a composite of death from cardiovascular causes, nonfatal myocardial infarction, or nonfatal stroke), assessed in a time-to-first-event analysis
```

### 237. `unit-0620` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 238. `unit-0621` — `html/body/main/section/section/table/tr/td`

```text
['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']
```

### 239. `unit-0622` — `html/body/main/section/section/table/tr/td`

```text
span: Number of Participants From Time of Randomization to Time to First Occurrence of a Major Adverse Cardiovascular Event (MACE): Acute Myocardial Infarction (Non Fatal); Non-fatal Stroke; and CV Death
```

### 240. `unit-0623` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/typg/outcomes.json
```

### 241. `unit-0624` — `html/body/main/section/section/table/tr/th`

```text
5. first_or_recurrent
```

### 242. `unit-0625` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 243. `unit-0626` — `html/body/main/section/section/table/tr/td`

```text
span: first occurrence
```

### 244. `unit-0627` — `html/body/main/section/section/table/tr/td`

```text
record:31185157.source
```

### 245. `unit-0628` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 246. `unit-0629` — `html/body/main/section/section/table/tr/td`

```text
span: first occurrence
```

### 247. `unit-0630` — `html/body/main/section/section/table/tr/td`

```text
record:27633186.source
```

### 248. `unit-0631` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 249. `unit-0632` — `html/body/main/section/section/table/tr/td`

```text
span: first occurrence
```

### 250. `unit-0633` — `html/body/main/section/section/table/tr/td`

```text
record:27295427.source
```

### 251. `unit-0634` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 252. `unit-0635` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 253. `unit-0636` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 254. `unit-0637` — `html/body/main/section/section/table/tr/td`

```text
span: first occurrence
```

### 255. `unit-0638` — `html/body/main/section/section/table/tr/td`

```text
record:31189511.source
```

### 256. `unit-0639` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 257. `unit-0640` — `html/body/main/section/section/table/tr/td`

```text
span: first occurrence
```

### 258. `unit-0641` — `html/body/main/section/section/table/tr/td`

```text
record:30291013.source
```

### 259. `unit-0642` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 260. `unit-0643` — `html/body/main/section/section/table/tr/td`

```text
span: first occurrence
```

### 261. `unit-0644` — `html/body/main/section/section/table/tr/td`

```text
record:28910237.source
```

### 262. `unit-0645` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 263. `unit-0646` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 264. `unit-0647` — `html/body/main/section/section/table/tr/td`

```text
first
```

### 265. `unit-0648` — `html/body/main/section/section/table/tr/td`

```text
span: time-to-first
```

### 266. `unit-0649` — `html/body/main/section/section/table/tr/td`

```text
record:40162642.source
```

### 267. `unit-0650` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 268. `unit-0651` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 269. `unit-0652` — `html/body/main/section/section/table/tr/th`

```text
6. time_origin
```

### 270. `unit-0653` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 271. `unit-0654` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 272. `unit-0655` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 273. `unit-0656` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 274. `unit-0657` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 275. `unit-0658` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 276. `unit-0659` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 277. `unit-0660` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 278. `unit-0661` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 279. `unit-0662` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 280. `unit-0663` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 281. `unit-0664` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 282. `unit-0665` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 283. `unit-0666` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 284. `unit-0667` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 285. `unit-0668` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 286. `unit-0669` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 287. `unit-0670` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 288. `unit-0671` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 289. `unit-0672` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 290. `unit-0673` — `html/body/main/section/section/table/tr/th`

```text
7. follow_up
```

### 291. `unit-0674` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 292. `unit-0675` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 293. `unit-0676` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 294. `unit-0677` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 295. `unit-0678` — `html/body/main/section/section/table/tr/td`

```text
median follow-up was 3.8 years
```

### 296. `unit-0679` — `html/body/main/section/section/table/tr/td`

```text
span: median follow-up was 3.8 years
```

### 297. `unit-0680` — `html/body/main/section/section/table/tr/td`

```text
record:27295427.source/abstract
```

### 298. `unit-0681` — `html/body/main/section/section/table/tr/td`

```text
median follow-up of 1.81 years
```

### 299. `unit-0682` — `html/body/main/section/section/table/tr/td`

```text
span: median follow-up of 1.81 years
```

### 300. `unit-0683` — `html/body/main/section/section/table/tr/td`

```text
record:34215025.source/abstract
```

### 301. `unit-0684` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 302. `unit-0685` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 303. `unit-0686` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 304. `unit-0687` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 305. `unit-0688` — `html/body/main/section/section/table/tr/td`

```text
followed for a median of 3.2 years
```

### 306. `unit-0689` — `html/body/main/section/section/table/tr/td`

```text
span: followed for a median of 3.2 years
```

### 307. `unit-0690` — `html/body/main/section/section/table/tr/td`

```text
record:28910237.source/abstract
```

### 308. `unit-0691` — `html/body/main/section/section/table/tr/td`

```text
followed for a median of 25 months
```

### 309. `unit-0692` — `html/body/main/section/section/table/tr/td`

```text
span: followed for a median of 25 months
```

### 310. `unit-0693` — `html/body/main/section/section/table/tr/td`

```text
record:26630143.source/abstract
```

### 311. `unit-0694` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 312. `unit-0695` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 313. `unit-0696` — `html/body/main/section/section/table/tr/td`

```text
median follow-up was 3.4 years
```

### 314. `unit-0697` — `html/body/main/section/section/table/tr/td`

```text
span: median follow-up was 3.4 years
```

### 315. `unit-0698` — `html/body/main/section/section/table/tr/td`

```text
record:38785209.source/abstract
```

### 316. `unit-0699` — `html/body/main/section/section/table/tr/th`

```text
8. censoring
```

### 317. `unit-0700` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 318. `unit-0701` — `html/body/main/section/section/table/tr/td`

```text
span: Number of participants experiencing a first event of a MACE, defined as cardiovascular death, non-fatal myocardial infarction, or non-fatal stroke are presented. Results are based on the in-trial observation period which started at the date of randomisation, included the period after permanent trial product discontinuation, if any and ended at the date of the follow-up visit regardless of adherence to treatment.
```

### 319. `unit-0702` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/typg/outcomes.json
```

### 320. `unit-0703` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 321. `unit-0704` — `html/body/main/section/section/table/tr/td`

```text
span: Time from randomisation up to end of follow-up (scheduled at week 109)
```

### 322. `unit-0705` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/typg/outcomes.json
```

### 323. `unit-0706` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 324. `unit-0707` — `html/body/main/section/section/table/tr/td`

```text
span: All the patients who underwent randomization were included in the primary and exploratory analyses, and data from the patients who completed or discontinued the trial without having an outcome were censored from the day of their last visit; events occurring after that visit were not included.
```

### 325. `unit-0708` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/ft_27295427.txt
```

### 326. `unit-0709` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 327. `unit-0710` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD
```

### 328. `unit-0711` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 329. `unit-0712` — `html/body/main/section/section/table/tr/td`

```text
span: From randomization to first occurrence or death from any cause or study completion (Median Follow-Up of 5.4 Years)
```

### 330. `unit-0713` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/typg/outcomes.json
```

### 331. `unit-0714` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 332. `unit-0715` — `html/body/main/section/section/table/tr/td`

```text
span: On Nov 8, 2017, it was determined that 611 primary endpoints and a median follow-up of at least 1·5 years had accrued, and participants returned for a final visit and discontinuation from study treatment; the last patient visit was on March 12, 2018. These 9463 patients, the intention-to-treat population, were evaluated for a median duration of 1·6 years and were assessed for the primary outcome.
```

### 333. `unit-0716` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 334. `unit-0717` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 335. `unit-0718` — `html/body/main/section/section/table/tr/td`

```text
span: The planned closeout of follow-up of the patients was from December 5, 2016, to May 11, 2017, after the prespecified required minimum of 1360 patients were confirmed to have had a primary composite outcome event.
```

### 336. `unit-0719` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/ft_28910237.txt
```

### 337. `unit-0720` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 338. `unit-0721` — `html/body/main/section/section/table/tr/td`

```text
span: MACE endpoint (on-study) 1.02 (0.89, 1.18) No. of patients with event (%) 392 (12.9%) 400 (13.2%) Total Person Year 6340.2 6368.7 Incidence Rate 6.18 6.28
```

### 339. `unit-0722` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt
```

### 340. `unit-0723` — `html/body/main/section/section/table/tr/td`

```text
end-of-study
```

### 341. `unit-0724` — `html/body/main/section/section/table/tr/td`

```text
span: Number of participants with first occurrence of EAC (event adjudication committee) confirmed major adverse cardiovascular event (MACE), a composite end-point. i.e., from time of randomization to first occurrence of cardiovascular (CV) death, non-fatal myocardial infarction and non-fatal stroke combined data during in-trial period were reported. In-trial observation period was defined as the period from date of randomization to the first of (both inclusive): date of follow-up visit, date when participant withdrew consent, date of last contact with participant (for participant lost to follow-up), and date of death.
```

### 342. `unit-0725` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/typg/outcomes.json
```

### 343. `unit-0726` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 344. `unit-0727` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR
```

### 345. `unit-0728` — `html/body/main/section/section/table/tr/th`

```text
9. effect_measure
```

### 346. `unit-0729` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 347. `unit-0730` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.79
```

### 348. `unit-0731` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 349. `unit-0732` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 350. `unit-0733` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.74
```

### 351. `unit-0734` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 352. `unit-0735` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 353. `unit-0736` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.87
```

### 354. `unit-0737` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 355. `unit-0738` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 356. `unit-0739` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.73
```

### 357. `unit-0740` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 358. `unit-0741` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 359. `unit-0742` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio [HR] 0·88, 95% CI 0·79-0·99
```

### 360. `unit-0743` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 361. `unit-0744` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 362. `unit-0745` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio 0·78, 95% CI 0·68-0·90
```

### 363. `unit-0746` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 364. `unit-0747` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 365. `unit-0748` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.91
```

### 366. `unit-0749` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 367. `unit-0750` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 368. `unit-0751` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio is (0.887, 1.172) with a point estimate of 1.02.
```

### 369. `unit-0752` — `html/body/main/section/section/table/tr/td`

```text
outputs/handover/glp1_regulatory/208471Orig1s000StatR.pdf.txt
```

### 370. `unit-0753` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 371. `unit-0754` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.86
```

### 372. `unit-0755` — `html/body/main/section/section/table/tr/td`

```text
cache/glp1-ra-mace-t2d/records.json
```

### 373. `unit-0756` — `html/body/main/section/section/table/tr/td`

```text
HR
```

### 374. `unit-0757` — `html/body/main/section/section/table/tr/td`

```text
span: hazard ratio, 0.82; 95% CI, 0.68 to 0.98; P&#x2009;=&#x2009;0.029)
```

### 375. `unit-0758` — `html/body/main/section/section/table/tr/td`

```text
outputs/search_v2/lanes/R3/lane_r3/raw/058-pubmed-glp1-ra-mace-t2d-flow-efetch.xml
```

### 376. `unit-0759` — `html/body/main/section/section/table/tr/th`

```text
10. adjustment
```

### 377. `unit-0760` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 378. `unit-0761` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 379. `unit-0762` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 380. `unit-0763` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 381. `unit-0764` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 382. `unit-0765` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 383. `unit-0766` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 384. `unit-0767` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 385. `unit-0768` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 386. `unit-0769` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 387. `unit-0770` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 388. `unit-0771` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 389. `unit-0772` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 390. `unit-0773` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 391. `unit-0774` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 392. `unit-0775` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 393. `unit-0776` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 394. `unit-0777` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 395. `unit-0778` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 396. `unit-0779` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 397. `unit-0780` — `html/body/main/section/section/table/tr/th`

```text
11. estimator
```

### 398. `unit-0781` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 399. `unit-0782` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 400. `unit-0783` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 401. `unit-0784` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 402. `unit-0785` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 403. `unit-0786` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 404. `unit-0787` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 405. `unit-0788` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 406. `unit-0789` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 407. `unit-0790` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 408. `unit-0791` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 409. `unit-0792` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 410. `unit-0793` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 411. `unit-0794` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 412. `unit-0795` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 413. `unit-0796` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 414. `unit-0797` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 415. `unit-0798` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 416. `unit-0799` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN
```

### 417. `unit-0800` — `html/body/main/section/section/table/tr/td`

```text
UNKNOWN: NO_ROW_EVIDENCE
```

### 418. `unit-0801` — `html/body/main/section/section/table/tr/th`

```text
12. report
```

### 419. `unit-0802` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 420. `unit-0803` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 421. `unit-0804` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 422. `unit-0805` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 423. `unit-0806` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 424. `unit-0807` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 425. `unit-0808` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 426. `unit-0809` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 427. `unit-0810` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 428. `unit-0811` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 429. `unit-0812` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 430. `unit-0813` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 431. `unit-0814` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 432. `unit-0815` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 433. `unit-0816` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "cf2b3ef92247b85e7be7c3b56c3cc4fc0af007b3950acee95eea9c995653db38", "kind": "publication", "source_level": 1}
```

### 434. `unit-0817` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 435. `unit-0818` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "1d6aa330b31138916d05f14c939d6e621dc711b0f41cc9089e9263b2ab973750", "kind": "publication", "source_level": 1}
```

### 436. `unit-0819` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 437. `unit-0820` — `html/body/main/section/section/table/tr/td`

```text
{"document_sha256": "2fc31abdf24b1a27d1ee79dd424b3faac680c376e1c86b819c0d0f1bd6c89e40", "kind": "publication", "source_level": 1}
```

### 438. `unit-0821` — `html/body/main/section/section/table/tr/td`

```text
rule: source_hierarchy:provenance:fulltext_verified
```

### 439. `unit-0822` — `html/body/main/section/section/ul/li`

```text
PMID 31185157: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated
```

### 440. `unit-0823` — `html/body/main/section/section/ul/li`

```text
PMID 27633186: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated
```

### 441. `unit-0824` — `html/body/main/section/section/ul/li`

```text
PMID 27295427: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated
```

### 442. `unit-0825` — `html/body/main/section/section/ul/li`

```text
PMID 34215025: UNKNOWN_FAILS_CLOSED — UNTYPED — axis 8 unknown: NO_HELD_EFFECT_SPECIFIC_OBSERVATION_PERIOD
```

### 443. `unit-0826` — `html/body/main/section/section/ul/li`

```text
PMID 31189511: MATCH — axis 1 unstated; axis 2 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated
```

### 444. `unit-0827` — `html/body/main/section/section/ul/li`

```text
PMID 30291013: REFUSE — axis 4: ['CV_DEATH', 'MI_FATALITY_UNSTATED', 'STROKE_FATALITY_UNSTATED'] differs from target ['CV_DEATH', 'NONFATAL_MI', 'NONFATAL_STROKE']; no valid declared coercion
```

### 445. `unit-0828` — `html/body/main/section/section/ul/li`

```text
PMID 28910237: MATCH — axis 1 unstated; axis 2 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated
```

### 446. `unit-0829` — `html/body/main/section/section/ul/li`

```text
PMID 26630143: MATCH — axis 1 unstated; axis 2 unstated; axis 5 unstated; axis 6 unstated; axis 10 unstated; axis 11 unstated
```

### 447. `unit-0830` — `html/body/main/section/section/ul/li`

```text
PMID 40162642: MATCH — axis 1 unstated; axis 2 unstated; axis 3 unstated; axis 6 unstated; axis 7 unstated; axis 10 unstated; axis 11 unstated
```

### 448. `unit-0831` — `html/body/main/section/section/ul/li`

```text
PMID 38785209: UNKNOWN_FAILS_CLOSED — UNTYPED — axis 8 unknown: FLOW_COMPOSITE_ON_TREATMENT_NOT_LINKED_TO_ABSTRACT_HR
```

### 449. `unit-0832` — `html/body/main/section/section/p`

```text
No declared coercions.
```

### 450. `unit-1108` — `html/body/main/section/table/tr/td`

```text
GLP-1 receptor agonists and cardiorenal outcomes in type 2 diabetes: an updated meta-analysis of eight CVOTs. (2021), Cardiovasc Diabetol
```

### 451. `unit-1110` — `html/body/main/section/table/tr/td`

```text
PMID 34526024
```

### 452. `unit-1112` — `html/body/main/section/table/tr/td`

```text
True
```

### 453. `unit-1114` — `html/body/main/section/table/tr/td`

```text
https://doi.org/10.1186/s12933-021-01366-8
```

### 454. `unit-1115` — `html/body/main/section/p`

```text
Major adverse cardiovascular events: 0.86 (HR), 95% CI 0.79–0.94
```

### 455. `unit-1116` — `html/body/main/section/p`

```text
✓ same question. Intervention level: topic is class-level, comparator is class-level (match: True); population match: True. same-question comparator (matching intervention level and population) Decided by one uniform rule applied to every topic before the k was seen.
```

### 456. `unit-1118` — `html/body/main/section/table/tr/td`

```text
7
```

### 457. `unit-1120` — `html/body/main/section/table/tr/td`

```text
8
```

### 458. `unit-1122` — `html/body/main/section/table/tr/td`

```text
6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6 and AMPLITUDE-O was a three-point MACE, whereas ELIXA used a four-point MACE, including also hospital admission for unstable angina. Characteristics of trials and patients are reported, respectively, in Table 1 . The populations studied ranged in size from 3297 (SUSTAIN-6) to 14,752 (EXSCEL), were of similar age (mean age was 64.0 ± 1.97 years), 37,117 were mal
```

### 459. `unit-1124` — `html/body/main/section/table/tr/td`

```text
7
```

### 460. `unit-1126` — `html/body/main/section/table/tr/td`

```text
SOUL
```

### 461. `unit-1128` — `html/body/main/section/table/tr/td`

```text
ELIXA
```

### 462. `unit-1130` — `html/body/main/section/table/tr/td`

```text
cached comparator text trial-set enumeration
```

### 463. `unit-1132` — `html/body/main/section/table/tr/td`

```text
Comparator trial set was measured from cached comparator abstract/full text.
```

### 464. `unit-1134` — `html/body/main/section/table/tr/td`

```text
MEASURED
```

### 465. `unit-1136` — `html/body/main/section/table/tr/td`

```text
named table rows
```

### 466. `unit-1138` — `html/body/main/section/table/tr/td`

```text
ELIXA, LEADER, SUSTAIN-6, EXSCEL, HARMONY Outcomes, REWIND, PIONEER 6, AMPLITUDE-O
```

### 467. `unit-1142` — `html/body/main/section/table/tr/td`

```text
COMPARATOR_PREDATES_POOLED_TRIAL(SOUL)
```

### 468. `unit-1144` — `html/body/main/section/table/tr/td`

```text
Comparator search ran to 2021-06-30; SOUL is a 2025 pooled trial.
```

### 469. `unit-1149` — `html/body/main/section/p`

```text
The comparator k above is auto-extracted from the comparator's own text and may reference a sub-analysis rather than its same-scope pooled total; the enumerated same-scope comparator k (scope-classified, the finishing metric) is the figure in the parity table, which governs where these differ.
```

### 470. `unit-1296` — `html/body/main/section/p`

```text
Compliance with the PRISMA 2020 reporting items, derived from the review object so it cannot drift from the page. Every item is rendered or declared absent with a reason.
```

### 471. `unit-1300` — `html/body/main/section/table/tr/td`

```text
5 Eligibility criteria
```

### 472. `unit-1301` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 473. `unit-1302` — `html/body/main/section/table/tr/td`

```text
Protocol tab - eligibility is rendered from the structured include object; the proposition object records no protocol/config divergence on checked dimensions, so declared == enforced is backed.
```

### 474. `unit-1303` — `html/body/main/section/table/tr/td`

```text
6 Information sources + dates
```

### 475. `unit-1304` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 476. `unit-1305` — `html/body/main/section/table/tr/td`

```text
Search tab — PubMed, ClinicalTrials.gov; run 2026-09-11; AACT snapshot dated on the ghost/recall blocks.
```

### 477. `unit-1306` — `html/body/main/section/table/tr/td`

```text
7 Full search strategy, verbatim, every source
```

### 478. `unit-1307` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 479. `unit-1308` — `html/body/main/section/table/tr/td`

```text
Search tab — the exact PubMed and ClinicalTrials.gov queries are printed verbatim and are re-runnable.
```

### 480. `unit-1309` — `html/body/main/section/table/tr/td`

```text
8 Selection process (screeners, disagreement)
```

### 481. `unit-1310` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 482. `unit-1311` — `html/body/main/section/table/tr/td`

```text
Two independently-implemented rule screeners; disagreement rate 0.0% (0/13); rule-based adjudicates. CAVEAT: both rule sets share an author and the same criteria, so they are NOT statistically independent and this agreement overstates reliability — a genuinely independent model screener is the next step.
```

### 483. `unit-1312` — `html/body/main/section/table/tr/td`

```text
9 Data collection process
```

### 484. `unit-1313` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 485. `unit-1314` — `html/body/main/section/table/tr/td`

```text
Results tab + per-trial Source column — source hierarchy (abstract > CT.gov structured > full text > hand-verified AACT arms), round-trip validation on every extraction, outcome-identity gating; refuse on ambiguity.
```

### 486. `unit-1315` — `html/body/main/section/table/tr/td`

```text
15 Certainty assessment
```

### 487. `unit-1316` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 488. `unit-1317` — `html/body/main/section/table/tr/td`

```text
Results tab — the machine-computable certainty signals are shown: imprecision via the 95% CI and the prediction interval, inconsistency via tau^2. A PARTIAL, object-derived GRADE is now rendered on the Risk-of-bias tab (risk-of-bias, inconsistency and imprecision computed from committed fields; publication bias is NOT ASSESSED automatically; any registry ghost census is descriptive until a PICO-scoped denominator is available; indirectness left to human judgement) — a graded certainty label with each domain's basis, not a full hand-graded GRADE.
```

### 489. `unit-1318` — `html/body/main/section/table/tr/td`

```text
16a Flow with counts at every stage
```

### 490. `unit-1319` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 491. `unit-1320` — `html/body/main/section/table/tr/td`

```text
Screening tab — PRISMA flow: identified -> screened -> excluded-by-rule (counts) -> eligible -> pooled k -> declared-absent.
```

### 492. `unit-1321` — `html/body/main/section/table/tr/td`

```text
16b Exclusions with reasons
```

### 493. `unit-1322` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 494. `unit-1323` — `html/body/main/section/table/tr/td`

```text
Screening tab — every excluded record lists its rule id, a reason true of the record, and a verbatim span.
```

### 495. `unit-1324` — `html/body/main/section/table/tr/td`

```text
24a-c Registration & protocol
```

### 496. `unit-1325` — `html/body/main/section/table/tr/td`

```text
✓ present
```

### 497. `unit-1326` — `html/body/main/section/table/tr/td`

```text
Protocol + Reproducibility tabs — the protocol first entered the repository inside a BUILD commit (SHA bf99a91652), so prospective precedence is NOT demonstrated here and protocol-SHA byte-for-byte reproduction is not claimed; eligibility is generated from the structured object.
```

### 498. `unit-1328` — `html/body/main/section/table/tr/td`

```text
0
```

### 499. `unit-1330` — `html/body/main/section/table/tr/td`

```text
NOT demonstrated for this topic — no protocol-only commit exists; the protocol first entered the repository inside a build commit (bf99a91652e74347e4e10cf6b9f1962aee4e596d), so this repository's history does not show the protocol preceding synthesis. The PICO is still fixed and replay from the committed cache is deterministic; only prospective PRECEDENCE is unproven here.
```

### 500. `unit-1332` — `html/body/main/section/table/tr/td`

```text
bf99a91652e74347e4e10cf6b9f1962aee4e596d
```

### 501. `unit-1334` — `html/body/main/section/table/tr/td`

```text
ad36eddb18fe10e436b3f3ea6aac2e60e53ad16812f7feda77b27549a6f3f571
```

### 502. `unit-1336` — `html/body/main/section/table/tr/td`

```text
True
```

### 503. `unit-1338` — `html/body/main/section/p`

```text
Of this page's pooled numbers, a blind second extractor agreed or reconciled on 5 of 5 that are checkable from the abstract (0 identical, 5 same-result-different-statistic, 0 conflict; 2 not stated in the abstract). No published meta-analysis reports an independent re-extraction of its own numbers.
```

### 504. `unit-1339` — `html/body/main/section/p`

```text
Each stated result on this page — whether it is statistically significant, whether its interval spans no effect — is derived from a single claim object, not recomputed per surface. At build the rendered page and manuscript are scanned for any wording that asserts the opposite of that object; the build is refused on a contradiction. Claims checked: 3; contradictions caught: 0; scope: grade=1, outcome_result=1, rob_sensitivity=3, strand_pool=2; surfaces checked=3; not in scope: verbatim source quotations, external comparator prose.
```

### 505. `unit-1340` — `html/body/main/section/p`

```text
Beyond significance, the build also refuses object-backed proposition contradictions: publication-bias state, declared-vs-enforced eligibility, protocol-SHA byte replay, pooled/rated/retracted counts, search-found membership, and state-label collapses. Proposition contradictions caught: 0; scope: publication_bias_state=1, declared_equals_enforced=1, byte_reproducible=1, pooled_count=1, rated_count=1, retracted_count=1, search_found=0, state_collapsed=0; not in scope: verbatim source quotations, external comparator prose without a committed object row.
```

### 506. `unit-1341` — `html/body/main/section/p`

```text
The prose protocol and executable config agree on these checked dimensions: none. Compared as separate sources.
```

### 507. `unit-1342` — `html/body/main/section/div`

```text
RETRACTED (round-2): reproducibility claim not currently supported. We previously claimed that re-running from the registration SHA on a fresh clone regenerates this page byte-for-byte. Direct testing falsified that: running the advertised command changed several canonical output files, and running it AT the registered SHA produced an essentially empty review because the build consumes MUTABLE POST-REGISTRATION STATE (later caches, extraction state, adapter outputs) that is NOT pinned in any committed manifest. Until every build input is pinned in a committed manifest with hashes and the build runs from that manifest, this page does NOT claim byte-for-byte reproduction from the protocol SHA — only that the analysis is deterministic given the committed cache as-is. Independent REPEATABILITY (a fresh search retrieving the same set) was never claimed and is not claimed now.
```

