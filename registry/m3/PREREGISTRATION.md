# M3 PRE-REGISTRATION: blinded AI examination protocol (frozen text)

**Status: PROTOCOL REGISTERED; SUITE AND KEY NOT YET SEALED.**
- This file freezes the examination protocol BEFORE any held-out case, answer key or examiner exists.
- The sealed suite and answer-key commitments (sha256 only) are added later as dated amendments in
  `registry/m3/AMENDMENTS.md`. Every amendment is listed, and none rewrites this file.
- Any change to this text after this commit voids the registration.

## Registration facts
- Registered by: captain (Claude Opus 5.5), on Mahmood's decision "M3 can be blinded ai preferably codex high end model".
- Basis: protocol v2 answers, item by item, a separate codex critique of v1 (29 P0, 17 P1). The critique is reproduced
  in the appendix of this file.
- Coverage: 51 property rows. **Suite size: 102** (one independent challenge plus one matched admissible control per
  property), the conservative design from the coverage-matrix draft.
- **Defaults, each pending Mahmood's confirmation by a dated amendment.** If he changes any, the amendment records it
  BEFORE suite selection.
  1. The answer key is held and signed by Mahmood, prepared with a non-OpenAI model family, never the examiner.
  2. The registration commit sha is deposited by Mahmood himself (email to self) before launch. The captain cannot send
     it.
  3. Model: the highest codex model and effort available on run day, named exactly in the launch record.
  4. Suite size 102, as above.

---

# M3: blinded AI examination, protocol DRAFT v2 (captain, 12 Oct 2026)

Mahmood's decision: "M3 can be blinded ai preferably codex high end model".
- v1 was critiqued by a separate codex instance: 29 P0, 17 P1. The critique is kept verbatim in
  `M3_PROTOCOL_CODEX_CRITIQUE.md`; item numbers [#n] below refer to it.
- Nothing here has been run. M3 runs only after M1 and M2 are met, on the SAME release [#1].

## 0. What M3 claims, and what it does not [#9, #37]
- M3 is an **AI examination by a fresh, blinded codex instance. It is not a human examination.**
  - Codex has reviewed this harness throughout development.
  - Blinding removes local history and session context. It cannot remove training exposure or the shared model family.
- The conclusion is bounded: the observed behaviour of ONE frozen release on ONE named, sealed case suite under this
  procedure. It is not a population error rate.
- Outcome taxonomy, fixed in advance:
  - **PASS**: every criterion established with complete evidence.
  - **FAIL**: a property is violated.
  - **INCONCLUSIVE**: the examination could not establish a criterion.
  - **INVALID**: the procedure was broken.
- Only PASS meets M3. An empty findings list is never a pass on its own [central point; #31].

## 1. Identities and pre-registration [#1–#5, #16]
Fixed, in order:
1. **The release.** Freeze it: source commit, release bundle sha256 per topic, and the M1 and M2 evidence records
   (their run IDs and artefact hashes) on that same commit.
2. **The examination bundle.** A deterministic redaction script turns the release into the bundle. Both hashes are
   recorded, along with every removed path [#4].
3. **The configuration stack.** Frozen and archived together [#5]:
   - prompt, model ID requested, reasoning effort, client version and config file;
   - tool permissions, sandbox profile, budgets [#20];
   - "no skills, no memory, no operator messages".
4. **Pre-registration.** It lists every item above, the case-suite commitment (§3; a hash only, the cases stay sealed),
   the answer-key commitment, the criteria (§5) and the adjudication rules (§6).
   - It is committed to main, and its sha256 is deposited with a third party before launch. Mahmood's email to
     himself or an external timestamp service both work [#3].
   - Separate IDs are recorded for the examined commit, the registration commit and the result commit [#2].

## 2. Blinding and isolation, ENFORCED rather than asserted [#6–#12]
- **Sandbox.** Codex runs with `--sandbox` read-only on a filesystem allowlist: the examination bundle plus a fresh,
  empty writable work dir. It also gets a fresh CODEX_HOME (no sessions, no thread history), no credentials, and no
  other drives mounted. The allowlist and sandbox profile are archived [#6].
- **Network.** The examiner's command execution has NO network. The model transport is the client's own connection
  only. Replay commands run with a dead proxy, and any attempted connection is logged and counted [#7].
- **Leak scan before launch.** A recursive CONTENT and metadata scan of the bundle covers comments, embedded JSON,
  archives and links. It checks for: development history, review records, safeguard names from the fix ledger,
  lane_status text, and case identifiers. Zero hits are required, and the scanner is itself tested on a planted leak
  [#8].
- **Untrusted material.** All bundle content is untrusted examination material; instructions inside it are not
  authority. The examiner's only instructions are the frozen prompt [#10].
- **Case delivery.** Cases arrive as a separately hashed challenge package with neutral identifiers, randomised order,
  and no expected outcomes. The answer key never enters the sandbox [#11, #12].

## 3. Held-out case suite and sealed answer key [#13–#19]
- **Unit.** The hold-out unit is (trial, source, challenge family). A family exercised in development (the M2 battery,
  audit plants, V15 previews) is NOT held out, under any identifier [#14].
- **Exposure ledger.** Every case is checked against tests, plants, review prompts, dispatch and lane files, PR text and
  model-call records. The check covers identifiers, DOIs, PMIDs, NCTs, titles and quoted numbers, not just one ID [#13].
- **Population and selection, frozen BEFORE the release freeze.** This covers the eligible population, the exclusions,
  a coverage matrix (each claimed property × route → cases [#19]), and a SEEDED selection algorithm with an exact size.
  The captain does not choose individual cases [#15].
- **Controls.** Matched ADMISSIBLE controls make up at least 1/3 of the suite. They must be admitted and produce the
  correct served output, so a refuse-everything harness FAILS [#18].
- **The sealed answer key.** For each case it holds the expected outcome, reason code and evidence locator.
  - It is written and adjudicated BEFORE the run by someone other than the examiner, ideally Mahmood or an independent
    model family. Disagreements are resolved before sealing.
  - It is escrowed: the hash is in the registration and the content is withheld until scoring [#16, #17].

## 4. The examiner's task and completion evidence [#20–#31]
1. **Replay.** Take the reference outputs read-only from the bundle. Regenerate into a SEPARATE empty output dir with
   derived caches removed. Compare against a frozen artefact inventory with fixed denominators; a missing file is a
   failure, never omitted [#21, #22].
2. **Attack each case** through every in-scope entry point (inventoried, overrides included) [#25].
   - "Admitted", "pooled" and "served" are defined operationally by the outputs checked: the pool object, review.json
     and index.html.
   - After every refusal, the persisted state and every downstream output are checked, so no partial admission
     survives [#24, #26].
   - Cases run from a reset baseline, plus pre-registered stateful sequences [#27].
3. **Capture execution OUTSIDE the examiner** [#30, #43, #44]. A wrapper logs every command, its working directory,
   input hashes, exit code, and full stdout and stderr. This goes to append-only storage during the run, independently
   of the model's prose.
4. **Output.** A complete per-case × per-criterion ledger: completion status (attempted / completed / blocked), outcome,
   reason code and evidence reference. An untested case is INCONCLUSIVE, never absent [#31].
   - Malformed inputs, crashes and dependency failures are INVALID_TEST, never a "successful refusal" [#23].
   - Reason codes are scored against the sealed key, and source evidence is required [#28].

## 5. Acceptance criteria (pre-registered)
| Criterion | Pass if |
|---|---|
| A1. Replay | The full frozen inventory is byte-identical, regenerated into a separate dir, with no network and no hand input |
| A2. Admission | 0 inadmissible cases admitted, pooled or served on any in-scope route; every admissible control admitted with correct output |
| A3. Refusal | Every inadmissible case is refused with the KEY's reason code and evidence |
| A4a. Extracted values | Every served extracted number has semantic identity with its source: trial, arm, contrast, endpoint, timepoint, unit, denominator [#33]. The inventory is independently derived [#32] |
| A4b. Derived values | Every pooled or derived number is re-computed independently (audit/independent_recompute.py) [#34] |
| A5. Licence | One operational rule: no NC, ND, SA or unknown-licence text in any model-facing artefact of the bundle (the PR #94 rule) [#35] |
| Integrity | Any execution-integrity or evidence-tampering finding outside A1–A5 is FAIL. A pre-registered severity rubric maps each finding to a criterion [#36] |

## 6. Adjudication and reruns [#38–#42]
- **Roles.** Developer and case selector are separate from answer-key custodian, examiner operator and adjudicator.
  Where one person must hold two roles, it is recorded [#40].
- **Outcome of each finding:** CONFIRMED, NOT_REPRODUCED, UNRESOLVED or INVALID_TEST.
  - Reproduction runs FIRST on an immutable clone of the examined environment, with the original inputs and state
    [#39].
  - Non-reproduction alone never overturns an execution captured by the wrapper. UNRESOLVED counts as INCONCLUSIVE
    [#38].
- **Infrastructure failure.** Invalidation conditions are defined before launch. A run that recorded a finding is never
  re-labelled "infrastructure" [#41].
- **Campaigns.** A FAIL means fix, then a new release and a new campaign from §1 with a NEW sealed suite. The exposed
  cases join development material. Every campaign is reported, and none replaces another [#42].

## 7. Record [#43–#46]
- **Streamed during the run** (append-only, independent of the model): the wrapper log, the full client event stream
  (tool calls, messages, file changes, retries, truncation), resolved model metadata, effective effort, and the
  environment (OS, locale, clock, resources) [#45].
- **The final manifest** links: registration → examined release → examination bundle → sealed suite and key → wrapper
  log → findings → adjudication → result. It is committed with a sha256 for each [#46].

## Still open for Mahmood
1. Who holds the answer key (you, or an independent model family under your signature).
2. The third-party timestamp for the registration.
3. The model: pin the ID now, or take the highest available at run time.
4. The suite size, after the coverage matrix is drafted.

---

## Appendix: the codex critique of protocol v1 (verbatim)

# Codex critique of M3_BLINDED_EXAM_PROTOCOL_DRAFT v1 (verbatim)

Model: codex-cli 0.153.4, model_reasoning_effort=high, read-only sandbox, run 12 Oct 2026.
Prompt: F:/captain3-tmp/codex_jobs/m3crit/PROMPT.md (sha256 4d8cf6da4b145d1b...).

**The draft does not yet support a defensible M3 pass.** Its central weakness is that “no executed findings” can mean either “the property held” or “the examiner failed to test it.” Blinding, held-out status, adjudication, and reruns also depend on assertions that the proposed record cannot independently verify.

Severity here means:

- **P0:** Can directly produce a pass despite a material defect, compromised examination, or prior failure.
- **P1:** Substantially weakens the examination or prevents verification of its claims.
- **P2:** Creates ambiguity or limits interpretation and reproducibility.

These are protocol vulnerabilities, not findings that any misconduct or leakage has occurred.

**Pre-registration and release identity**

| ID | Severity | Exact section | False-pass scenario | Concrete amendment |
|---|---|---|---|---|
| 1 | P0 | Opening: “runs ONLY after M1 … and M2 … are met” | M1/M2 passed on an earlier release, or their status is merely asserted. M3 examines a different release while inheriting their passes. | Require immutable M1/M2 evidence references, completion dates, and tested artifact hashes. Establish that they apply to the exact M3 release; otherwise repeat affected prerequisites. |
| 2 | P1 | §1(a): “the main commit” | “Main” moves. The commit containing pre-registration may differ from the examined code commit, without a defined relationship. A later record points to whichever commit is convenient. | Record separate immutable IDs for the examined source commit, pre-registration commit, and final record commit. Explicitly define their relationship. Do not use branch names as identities. |
| 3 | P0 | §1: “committed before the examiner sees anything” | A Git commit alone does not establish that registration preceded examiner exposure. A registration can be created after an informal trial and presented with an earlier author date. | Publish or deposit a timestamped registration commitment with an independent custodian before any examiner exposure. Record release/case access events and prohibit unregistered pilot examinations of the scored release. |
| 4 | P1 | §1(a): bundle hashes; §2: excluded artifacts | Redacting the release for blinding changes what is examined. The tested bundle can differ materially from the release later claimed to have passed. | Specify the deterministic redaction/build procedure. Hash both original and examination bundles, record every removal/transformation, and establish that executable behavior, sources, and scored outputs are preserved. |
| 5 | P0 | §1: “examiner prompt is frozen”; §1(c) | Only the visible task prompt is frozen. Client defaults, injected instructions, skills, tool permissions, compaction, operator messages, or configuration change the examination. | Freeze and archive the complete controllable instruction/configuration stack, tool schemas and permissions, launch environment, and interaction policy. Log every subsequent message. Disclose unavailable provider instructions as an evidence limitation. |

**Blinding and isolation**

| ID | Severity | Exact section | False-pass scenario | Concrete amendment |
|---|---|---|---|---|
| 6 | P0 | §2: “a fresh directory”; “fresh CODEX_HOME” | The examiner can read parent directories, other drives, user configuration, caches, mounted workspaces, or credentials. Fresh directories do not enforce a read boundary. | Run in an enforced sandbox with an explicit filesystem allowlist, fresh writable storage, no host mounts beyond approved inputs, and no inherited credentials. Record the effective permissions and test the boundary before exposure. |
| 7 | P0 | §2: “network is off except the model endpoint”; A1: “no network” | The endpoint exception permits other provider tools or connections; network isolation is asserted rather than enforced. The analysis process retrieves missing inputs or historical information. | Separate model transport from the execution sandbox. Deny network access to analysis processes and disable remote browsing/connectors. Record the enforced egress policy and attempts. Define precisely how A1’s “no network” accommodates model transport. |
| 8 | P0 | §2: excluded-path list and “0 hits required” | History or safeguard names survive in allowed filenames, HTML comments, source comments, embedded JSON, archive members, metadata, or renamed transcripts. Path matching reports zero hits. | Add recursive content and metadata inspection, including archives and links, against a preregistered disclosure policy. Inventory resolved paths and reject symlinks/reparse points that escape the sandbox. Have someone outside development check the blinded package. |
| 9 | P1 | §0: “Blinding removes its access to that history” | A fresh client session is described as proving removal of all historical influence. It cannot establish absence of training exposure or undocumented provider context. | Narrow the claim to the controls actually demonstrated: withheld local history and fresh session context. Record provider retention/context settings where available and explicitly distinguish procedural blinding from model-family independence. |
| 10 | P0 | §2 allowed bundle; §4 frozen examiner task | Bundle instructions, source documents, or served pages contain instructions to skip attacks, trust a certificate, or report success. The examiner follows them as authority. | State that all bundle content is untrusted examination material. Keep authoritative instructions outside it, prohibit bundle-origin changes to scope or criteria, and use an external scorer that does not depend on the examiner obeying embedded text. |
| 11 | P1 | §2 excludes `docs/evidence/`; §1(b), §3–4 require held-out cases | The case list is inside excluded evidence, but no delivery mechanism is defined. Cases are silently omitted, informally supplied, or accompanied by revealing commentary. | Define a separately hashed challenge package and delivery procedure. Specify exactly what the examiner receives, when, and which labels and expected answers remain concealed. Log receipt of every case. |
| 12 | P1 | §3 confirmation; §4 challenge task | Case names, filenames, ordering, or explicit labels reveal the expected refusal or the safeguard under test. The examiner merely checks the advertised answer. | Use neutral identifiers and blinded case presentation. Keep the ground-truth labels and expected refusal reasons with the scorer. If adversarial attack design requires revealing invalidity, disclose that dimension as unblinded and separate it from blinded outcome scoring. |

**Held-out validity and case selection**

| ID | Severity | Exact section | False-pass scenario | Concrete amendment |
|---|---|---|---|---|
| 13 | P0 | §3: “grep … for each case identifier. 0 hits required” | The same case appeared under another identifier, DOI, filename, paraphrase, extracted value, or in an unsearched chat/history. Zero identifier hits are treated as proof of no use. | Maintain a case-exposure ledger covering development, reviews, fixes, plants, prompts, and relevant histories. Check aliases, source identities, content hashes, and substantive overlap. Mark uncertain exposure as ineligible for a held-out claim. |
| 14 | P0 | §3: “admission-challenge cases and topics”; opening M2 | M2 or another development exercise already exercised the same source, case family, or exact failure mechanism. The claimed holdout is only a renamed variant. | Define the holdout unit: exact case, source, trial, topic, and/or challenge family. Specify allowable overlap with M2 and development. Report these overlap levels separately; do not claim topic-level holdout from case-level separation. |
| 15 | P0 | §3: “captain proposes ≥ 3 topics and ≥ 20 admission challenges” | The developer selects easy challenges after seeing which safeguards work. A minimum size does not prevent cherry-picking, substitution, or optional stopping. | Freeze the eligible population, exclusions, selection algorithm, exact sample size, strata, and replacement rules. Prefer independent selection or a committed random draw. Publish every excluded/replaced candidate and its reason. |
| 16 | P1 | §1(b), §3: list and SHA256 committed to main | Public filenames and hashes reveal the held-out set before the run. Developers or operators can inspect the cases and adapt the release or instructions. Hashes are commitments, not confidentiality controls. | Freeze the release first; then select and escrow cases under an independent custodian. Publish a salted commitment or sealed manifest before the run, revealing cases and salts afterward. Log access and prohibit release changes after selection. |
| 17 | P0 | §3; A2–A3: “non-admissible”; “should be refused”; “named reason” | No authoritative answer key exists. A challenge’s validity or expected reason is decided after seeing the harness response, so an erroneous decision becomes “correct.” | Preregister independently adjudicated ground truth for each case: source-backed eligibility, relevant population/contrast/timepoint/unit, admissible values, acceptable reason codes, and uncertainty. Conceal the answer key from the examiner and harness. |
| 18 | P0 | A2–A3 | A harness that refuses everything passes all negative challenges. A broken parser or permanently closed gate can appear perfectly safe. | Include matched admissible controls that must complete admission and produce correct outputs. Define required sensitivity as well as refusal performance, including mixed batches and valid cases adjacent to invalid ones. |
| 19 | P1 | §3 minimum sizes; §4(2) examples | Twenty challenges cover only easy or redundant cases. Difficult numerical extraction, multi-report trials, interacting defects, or topic-specific logic go untested while M3 is reported broadly. | Preregister a coverage matrix linking each claimed property and route to cases. Include boundary cases, combinations, duplicates across reports, numerical errors, and source-access failures. Limit the conclusion to demonstrated coverage. |
| 20 | P1 | §4: examiner task | An examiner spends nearly all its budget on replay or makes one weak attack per case. Exhaustion is treated as no finding. | Freeze time/token/tool budgets, minimum required operations per case, stopping rules, and completion evidence. Distinguish “attack attempted,” “test completed,” and “property satisfied.” Incomplete work cannot pass. |

**Execution and scoring**

| ID | Severity | Exact section | False-pass scenario | Concrete amendment |
|---|---|---|---|---|
| 21 | P0 | §4(1); A1: replay “from the bundle” | Replay copies bundled `review.json`/`index.html`, uses cached results, or compares files with themselves. Byte identity holds without re-running extraction or analysis. | Keep reference outputs read-only and separate from a clean replay output directory. Remove derived caches, document allowed inputs, and record the executed dependency chain. An external process must compare newly generated outputs against frozen references. |
| 22 | P1 | §4(1): “n of 32”; A1: “32 of 32 served review.json and index.html” | It is unclear whether there are 32 files, 32 pairs, or 32 topics. Missing files disappear from a glob and the remaining files are all declared identical. | Freeze the exact expected artifact inventory and denominator. Require every expected file, reject missing/unexpected outputs, and report per-file hashes and comparisons for both file types. |
| 23 | P0 | §4(2): “through the REAL route”; A2–A3 | A test fails before screening because of malformed input, missing dependencies, permissions, or a crash. The case is nevertheless recorded as a successful refusal. | Require valid challenge submission and instrumented evidence for each relevant route transition. Score crashes, setup failures, and unreached checks as errors/incomplete, not domain refusals. Validate the instrumentation with admissible controls. |
| 24 | P0 | §4(2); A2: “into a served pool” | Only an internal return value is checked. Invalid data appear in the actual served artifact, a cached page, a later pool, or an alternate endpoint without being observed. | Define “admitted,” “pooled,” and “served” operationally. Identify every in-scope output boundary and inspect the actual served artifacts after each attack, including persisted/cached state. Trace challenge inputs to any downstream contribution. |
| 25 | P1 | §4(2): screen → bind → extract → pool → gate | The tested path is safe, but production supports imports, resumes, manual overrides, alternate topic handlers, or direct pooling routes that bypass it. | Inventory all supported entry points and bypass/override behavior. Test each relevant route or explicitly exclude it from the M3 claim and disable it in the evaluated deployment. |
| 26 | P0 | §4(2–3); A2–A3 | A refusal is printed while the candidate or value has already been persisted and later contributes to a pool. The examiner counts the message as success. | Require transactional rejection: no prohibited persisted state or downstream numerical contribution. Check stores and outputs after rejection and after a subsequent valid run. |
| 27 | P1 | §4; A2–A3 | Earlier cases change state so later attacks are blocked for incidental reasons; stale caches mask a defect. Only the favorable execution order is observed. | Freeze case order and reset policy. Run isolated cases from a known baseline, plus preregistered stateful sequences where persistence is part of the claim. Record state hashes and cleanup results. |
| 28 | P0 | A3: “refused WITH its named reason” | The harness echoes a reason from case metadata, returns a generic refusal, or gives the expected reason despite evaluating the wrong population/endpoint. | Remove expected labels from inputs. Score machine-readable reason codes against the sealed answer key and require source-linked decision evidence. Permit only preregistered alternative reasons and precedence rules. |
| 29 | P0 | §4(3): “Unexecuted claims … not counted”; A2 | A serious suspected defect cannot be executed because the tool is unavailable, the budget ends, or the case requires an unsupported step. Excluding it makes the overall result pass. | Separate “confirmed defects” from “unresolved observations” and “incomplete required tests.” An unresolved observation material to A1–A5 must block a pass until tested or independently resolved under fixed rules. |
| 30 | P0 | §4(3–4): finding JSON and replay table | Examiner prose says a command ran, but it did not; output is truncated, fabricated, or associated with another command. A record of claims is mistaken for execution evidence. | Capture tool execution outside the examiner: exact arguments, working directory, input hashes, timestamps, exit codes, stdout/stderr, and output hashes. Require every finding and pass assertion to reference these immutable events. |
| 31 | P0 | §4 output schema; §5 A1–A5 | Findings-only JSON contains no entry for an untested case. An empty finding list is accepted as a complete examination. The examiner also grades its own work. | Require a complete per-case/per-criterion result ledger with fixed denominators, completion status, evidence references, and errors. Use a separately implemented scorer to compute the final outcome from evidence rather than examiner declarations. |

**Acceptance criteria and what they establish**

| ID | Severity | Exact section | False-pass scenario | Concrete amendment |
|---|---|---|---|---|
| 32 | P0 | A4: “0 served numbers whose recorded source does not contain them” | The examiner checks only some numbers, or lets the bundle define the inventory. Omitted numbers—including dynamically rendered ones—escape verification. | Create an independently checked inventory of all served numeric claims, including tables, plots, tooltips, and downloadable data. Give every claim an evidence/derivation ID and require complete accounting; unknown or unchecked items block A4. |
| 33 | P0 | A4 | A source contains the same numeral, but for another arm, endpoint, timepoint, unit, or population. A4 literally passes. | Validate semantic identity, not numeral occurrence: source/version and locator, trial/report identity, arm/contrast, endpoint, timepoint, units, denominator, and uncertainty. Require explicit reconciliation of multiple reports. |
| 34 | P0 | A4; A1 | Derived estimates need not literally appear in a source. Implementers either exempt them from A4 or provide a generated “source,” allowing incorrect pooling/statistics to pass; replay faithfully reproduces the error. | Split A4 into extracted-value correctness and derived-result correctness. For derivations, require traceable inputs, formulas, estimator/options, units, and independent recomputation with fixed tolerances. State that byte reproducibility alone does not establish statistical validity. |
| 35 | P1 | §2: “D8: no NC/ND/SA text”; A5: “0 non-CC BY / CC0 texts … prompt-bearing records” | The two rules differ. “Prompt-bearing” is undefined, so incompatible or unknown-license text is placed elsewhere, then read by the examiner. OA availability is substituted for the specified license test. | Use one operational license policy with exact allowed identifiers/versions and explicit treatment of unknown status. Inventory every text actually exposed to the model, including tool output and embedded material; retain source-specific license evidence. Define separately any policy for bundled but unexposed material. |
| 36 | P1 | §4 finding severity; §5 acceptance; §6 “real defect” | Severity has no rubric, and a serious execution-integrity or evidence-tampering defect falls outside A1–A5. It is recorded without preventing a pass. Conversely, §6 suggests every defect forces a rerun. | Preregister a severity rubric, mapping of defects to criteria, and global invalidation conditions. Define how out-of-scope findings affect the result. Evidence compromise, incomplete execution, and broken isolation must invalidate the examination. |
| 37 | P1 | §5: “M3 is MET” | Zero detected failures on a small, selected set becomes a claim that the harness generally prevents invalid admissions or has no provenance errors. | State a bounded conclusion: observed performance on the named frozen suite under the named procedure. If population-level error bounds are intended, preregister the sampling model, sample-size rationale, uncertainty method, and treatment of correlated cases. |

**Adjudication, reruns, and the permanent record**

| ID | Severity | Exact section | False-pass scenario | Concrete amendment |
|---|---|---|---|---|
| 38 | P0 | §6: CONFIRMED or NOT_REPRODUCED | A real intermittent defect is not reproduced once by the captain and effectively disappears. Missing context or an adjudicator error produces the same outcome. | Add `UNRESOLVED` and `INVALID_TEST` with evidence requirements. Non-reproduction alone cannot overturn original execution evidence. Unresolved material findings block a pass; define a bounded investigation and independent tie-break process. |
| 39 | P0 | §6: captain reproduces “by hand” | Reproduction uses a patched release, different inputs, altered state, or a simplified command. The original defect no longer appears and is discounted. | Reproduce first on an immutable clone of the original examined environment with the original inputs and state. Archive exact reproduction steps and differences. Test fixes only in a separately identified release. |
| 40 | P1 | §3 captain proposes; §6 captain adjudicates | The person responsible for the implementation also selects challenges and decides whether defects count. Favorable selection and interpretation can compound without an audit trail. | Separate developer, case custodian, examiner operator, and adjudicator roles where feasible. At minimum require independent adjudication of disputed/material findings and disclose all overlapping roles and conflicts. |
| 41 | P0 | §1(e): “failed infrastructure run … exactly one re-run” | A run detects a defect and later times out. It is labelled infrastructure failure; the cleaner retry replaces it. “Exactly one” can also be interpreted as one retry per failure. | Define infrastructure invalidation conditions before launch and a fixed total attempt limit. Preserve defects observed before interruption. Distinguish harness failures from external infrastructure failures. Record every attempt and prohibit choosing the best result. |
| 42 | P0 | §1(e) versus §6: “fixed … new release, then M3 runs again from §1” | Repeated fix-and-rerun cycles are presented as one successful examination. Previously held-out cases become development material but continue to count as held out. | Define attempts, campaigns, and release-level outcomes. Every failed campaign remains a failure in the record. Fixes require a newly registered campaign with fresh unexposed holdouts; old cases become regression tests. Report the complete campaign history alongside any later pass. |
| 43 | P0 | §7: “full examiner output, stdout and stderr, unedited” | Only final model prose or a terminal transcript survives. Omitted tool messages, operator interventions, file changes, retries, and truncation prevent reconstruction of what happened. | Preserve the complete accessible conversation/tool-event stream, all operator messages, process events, file changes, and artifacts. Detect and declare truncation. Record input/output associations and evidence locations for every scored result. |
| 44 | P0 | §7: record “committed … after the run” | Failed starts or unfavorable intermediate evidence are omitted before the final commit. Git proves the contents committed, not that the record is complete or contemporaneous. | Stream records to append-only storage or an independent custodian during execution. Issue a run ID before launch, log every start/abort/resume, and anchor hash-chained events externally. Preserve unsuccessful attempts as well as the final record. |
| 45 | P1 | §7 record fields; §1(c) | Model aliases, effort fallbacks, package changes, shell differences, clock/locale, or resource limits alter behavior. Recorded client version and CODEX_HOME path are insufficient to reconstruct or assess the run. | Record the resolved model identity/provider metadata where available, effective effort, request/session IDs, client configuration, environment image, dependencies, OS/runtime, hardware-relevant settings, locale, clock/seeds, limits, and all artifact hashes. Mark unobservable fields explicitly; do not infer them from requested settings. |
| 46 | P1 | §7; §5 “M3 is MET” | The final record contains a pass label without a mechanically checkable link between registration, executed release, cases, findings, adjudication, and served release. Later readers cannot prove which release passed. | Publish a final result manifest linking all those identities and each criterion’s evidence. Include a standalone verifier that checks completeness, hashes, denominators, unresolved findings, and outcome computation. Bind the pass claim to the exact evaluated release only. |

**Additional requirements an outside methodologist would expect**

Several requirements cut across individual fixes:

- **A defined research question and claim boundary.** Is M3 testing reproducibility, adversarial defect discovery, admission accuracy, source fidelity, or statistical correctness? These require different evidence. Define each separately and explain what the combined pass means.
- **A blinding matrix and timeline.** For each role, show access to development history, challenge identities, ground truth, release content, interim results, and final adjudication. State when any blinding ends.
- **A justified test population.** Explain topic selection, eligibility, challenge construction, representativeness, and the unit of analysis. Twenty challenges across three topics is a size specification, not a methodological justification.
- **Examiner qualification and assay sensitivity.** Demonstrate on separate, non-held-out material that the configured examiner can execute the required tools and detect representative known defects. Passing qualification must not expose the scored cases or silently train the scored session.
- **Independent validation of the test machinery.** Validate the comparator, route instrumentation, result parser, provenance checker, and final scorer. A common bug in the harness and its scorer must not certify itself.
- **An explicit outcome taxonomy.** Use `PASS`, `FAIL`, `INCONCLUSIVE`, and `INVALID`, with fixed decision rules. Require complete evidence for a pass; distinguish a violated property from an examination that could not establish it.
- **An amendment and deviation policy.** Preserve every registration version. Define which deviations invalidate a run, which require a new campaign, and how all deviations appear in the final report.
- **A statistical analysis plan where generalization is intended.** Define primary outcomes, denominators, clustering, uncertainty, and any treatment of multiple criteria. Avoid numerical generalization from purposively selected adversarial cases.
- **A complete reporting and retention plan.** Specify storage, access, retention, lawful availability of source materials, redaction rules, and how an outside reviewer can inspect restricted evidence without receiving a selectively reconstructed record.
- **A distinction between computational and examiner reproducibility.** The deterministic harness may be replayable while a hosted model examination is not exactly repeatable. Record enough to audit the original examination without promising identical future model behavior.

The most consequential amendment is to make **complete, independently verified execution evidence** the basis of passing. An empty findings list, a refusal message, or a later unsuccessful reproduction cannot substitute for that evidence.
