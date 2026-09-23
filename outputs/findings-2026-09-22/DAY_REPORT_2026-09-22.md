# meta-harness, 2026-09-22 — what was found, what landed, what is waiting on a decision

All work measured on branch `enforcement-gate`. **`main` and the served site are unchanged at `38c04411`**; HTTP 200
confirmed today. Nothing an external auditor can open has changed. Detail and per-lane artefacts: [INDEX.md](INDEX.md).

---

## 1. Three findings with named victims

Everything else below is mechanism. These three are defects an auditor would care about, each with a named trial and a
served consequence.

### Zhao 2009 — a single-blind trial admitted under a double-blind protocol (live on `main`)
`omega3-cardiovascular-events`, PMID 20146881. `harness/screen.py::_double_blind` returns True on a third branch:
**the text contains the word "placebo"**. Two independent public reviews state the trial is single-blind (PMC3507701
Table 1 `"R, SB, PC"` and *"1 in a single-blind fashion [19]"*, bound to the PMID and DOI; Cambridge S0007114512001559
*"Prospective, single-blind, randomised, placebo controlled"*). The topic's own protocol requires "double-blind,
placebo-controlled **or** blinded inert-control" — single-blind fails even that disjunction.
**Served consequence:** included, unextracted, contributing to 0 of 3 pools. The eligible denominator is wrong by one;
no served number moves. **Prevalence, checked against public sources with a positive control run first:** of the 26
placebo-branch admissions, 21 confirmed on a public registry record, 4 on weaker public tiers (2 secondary-table-only,
1 authors' pooled report, 1 primary abstract), 0 silent, **1 contradicted**. Zhao is the only one.
Direction of the rule: **it errs both ways** — 2 of 15 blinding refusals are false by the parent trial's registry row.

### J-EMPHASIS-HF — a composite hazard ratio served as all-cause mortality, in the flattering direction (live on `main`)
`spironolactone-hfref-mortality`, PMID 28824029, NCT01115855, k=1. The page serves **All-cause mortality HR 0.85
(0.53–1.36)**. The held abstract assigns that tuple to the trial's **primary composite** (*"a composite of death from
cardiovascular causes or hospitalization for HF"*) and reports mortality separately: **17 of 111 vs 10 of 110**.
Re-binding to those counts gives **RR 1.685 (0.808–3.514)** — recomputed independently of the lane, exact agreement.
The served value reads as a mortality benefit; the correct value favours placebo.
**Root cause, found by turning an external auditor's method on ourselves:** the row binds correctly to its own table
row, then passes ownership because (a) `topics/spironolactone-hfref-mortality.json` lists `"primary outcome"`,
`"primary endpoint"`, `"primary end point"` among the keywords for an outcome named *All-cause mortality*, so any
trial's primary endpoint matches; and (b) `canonical_components(spec)` is `[]`, so the component comparison that would
catch "composite of CV death or HF hosp" ≠ "all-cause mortality" has nothing to compare and defaults to EXACT_TARGET.
**Not applied.** Draft notice with full derivation: [PROPOSED_NOTICE_j-emphasis-hf.json](PROPOSED_NOTICE_j-emphasis-hf.json).
Changing a served primary result and its scale is Mahmood's decision.

### Comparator direction — undefended, with a working attack
From an external safeguard audit (which could not reach our artefacts at all — `curl exit 6, Could not resolve host` on
all five URLs *and* on github.com; every harness claim in it is therefore INFERRED and was treated as such; our site is
reachable from here at HTTP 200). Its attacks, run through our real gate with authentic LEADER text:
- **Reversed direction label, number unchanged: admitted, zero objections.** No direction field exists on any of the 46
  served rows; no reciprocal transform exists anywhere in `harness/`.
- **Right endpoint name, wrong estimand** (LEADER's expanded-composite 0.88 under the 3-point MACE row, with its
  authentic span): **also undefended semantically**. It was refused only by `CERTIFICATE.json release_sha256` and
  claimgraph `STALE_DEPENDENT` — integrity checks that fire because a built file was edited and **that a legitimate
  rebuild regenerates consistently and therefore silences**. No check objected to the endpoint/estimand mismatch.
Their LEADER numbers were verified against our held full text before anything was built on them (3-point MACE
0.87/0.78–0.97 ✓, expanded composite 0.88/0.81–0.96 ✓, MI 0.86/0.73–1.00 ✓); their two later-paper claims are
unverifiable because we do not hold those papers. Their third audit's collision claim is confirmed and **denser than
reported**: LEADER's Table 1 carries 0.87 twice, **0.86 three times**, 0.88 twice and 0.78 twice.
Our row-aware binder (`harness/hand_binding.py`) **defends their attack** — the collision tuple binds to the
heart-failure row and classifies `DIFFERENT_OUTCOME` — but it does not defend the defect above, and the ownership test
it feeds is vacuous for **23 of 113 outcome specs** (generic keyword and no declared components).

---

## 2. The worked example: three defects stacked on one page

`spironolactone-hfref-mortality` is the whole argument in one page.

| what happened | cause | net effect |
|---|---|---|
| k=3 pooled mortality result **removed** (RR 0.7294, 0.5609–0.9486 → k=1) | two rows set aside on P5; one of them (EMPHASIS-HF) because the resolved registry record describes the trial's **open-label extension** (`NON_RANDOMIZED / SINGLE_GROUP`) while the held publication states randomised double-blind | a probably-correct result deleted |
| the surviving k=1 row is **the wrong endpoint** | the trial's primary **composite** HR served as mortality | a definitely-wrong result kept |
| it passed ownership | generic `"primary endpoint"` keyword + empty component set → EXACT_TARGET | the error is invisible to the gate |

**Net: the page deleted a result that was probably right and kept one that is definitely wrong, in the flattering
direction.** All three causes are defects with named mechanisms; none is a scientific judgement call.

---

## 3. Two hazards and one method

- **[An exhaustive claim over a representation that does not carry the data always succeeds](HAZARD_exhaustive_claim_over_incomplete_representation.md)** — five instances in one session, by three different actors, including one committed by the author of the file inside a report quoting it. Cure: *an exhaustive claim needs a positive control that would have fired, or it is not an exhaustive claim.* Trigger is syntactic: "0 of", "none", "all N", "appears nowhere".
- **[The reported reason is not the binding constraint](HAZARD_reported_reason_vs_binding_constraint.md)** — a lane reports the reason it was looking for; the build stops at the reason it hits first. Cure: a recovery claim is unproven until the real build runs and the first failing check is observed per row.
- **[Recovery claims by relaxation](METHOD_recovery_claims_by_relaxation.md)** — the positive counterpart, generalised from lane RLX: relax the recorded blocker, re-run, record the ordered chain, report **depth** not clearance, exclude by name rather than guess, stamp the downstream boundary on every count.

**What that method produced.** B53's inferred "48 of 53 bindable" and "7 of 11 pools at k≥2" became, measured:
**33 of 53 clear the screen — 22 at depth 1, 8 at depth 2, 2 at depth 3, 1 at depth 4 — and 20 of 53 excluded by name**
because any relaxation constructible for them would also have cleared other checks. Pools with ≥2 clear rows: **4 of 11
at depth 1, 5 of 11 at any depth**; metformin-pcos (0 of 3) and probiotics-aad (1 of 11) are effectively unreachable.
EMPHASIS-HF needs depth 4: `ALLOCATION_NOT_RANDOMIZED → INTERVENTION_CONTRAST_NOT_PROVEN → BLINDING_NOT_PROVEN →
PLACEBO_CONTROL_NOT_PROVEN → ELIGIBLE`.
**Planning statement:** 22 rows are one repair from eligible; 11 need two or more; 20 cannot be assessed without new
material. Three kinds of work, three confidence levels. Screen-only — P8, extraction, variance and compatibility are all
downstream and unevaluated.

---

## 4. Nine corrections, and their direction

Every figure below was relayed onward and then corrected. **Eight moved against the first pass being too confident in
the *flattering* direction. One moved the other way — an alarming claim I passed on without reading the code it
described.** That distinction matters: the tidier story would be nine errors all leaning the same way.

| # | first pass | corrected to | by | direction |
|---|---|---|---|---|
| 1 | placebo branch load-bearing for 5 of 19 served rows | **11 of 35** | lane DB | understated |
| 2 | 0 of 15 blinding refusals false | **2 of 15** | lane DB | understated |
| 3 | 17 empty-container findings | **7** confirmed and fresh-build reachable | lane E2b | overstated |
| 4 | 5 of 26 admissions unproven by held documents | **4 of 26** | lane U5 | overstated |
| 5 | 48 of 53 rows bindable | **36 of 53** strict, **33 of 53** measured | B53X, RLX | overstated |
| 6 | 27 of 33 trials need a full-text fetch | **14 of 33** | lane AS | overstated |
| 7 | 12 of 46 served rows carry wrong provenance | **1 wrong number + 11 wrong labels**, 7 in suppressed harm blocks | lane WSX | overstated |
| 8 | fixing the comparator takes 48→50 rows and 9→11 pools | **no change: both RECOVERY rows fail an earlier check** | lane CMP | overstated |
| 9 | six `sign` commands could countersign the **wrong notice** | **the CLI refuses ambiguous matches and exits** (`countersign_result_change.py:37`) | lane WALK | **alarming, not flattering** |

Plus one retraction of a finding that was not a finding: ME-09 reported as a claimed-but-unbuilt defence, from a grep
scoped to three directories. `tests/test_arm_identity.py` exists and passes; an audit of all 33 error-library entries
(positive control first) found **0 of 33 named files missing, 0 of 33 ids unreferenced**.

**The pattern is the useful result: a first-pass finding is a draft.** Every correction came from a second look, and the
second look was usually an adversarial re-read of a report already relayed.

---

## 5. What landed

| commit | what | where |
|---|---|---|
| `b25027e3` | the enforcement gate — the build reads the admission decision at pooling; RED by design on the 53 | branch `enforcement-gate`, **not main** |
| `9ff4c6b0` | the certified-families fix — an empty or malformed certified `families.json` can no longer switch off the page-vs-certified comparison; four plants observed failing first | branch `enforcement-gate`, **not main** |

`git ls-remote` at the time of writing: `9ff4c6b0` on `enforcement-gate`, **`38c04411` on main**. The pushed bytes were
verified by fetching `harness/gate.py` back from raw.githubusercontent (blob `d6e775b0`, matching the commit).
**Nothing visible to an external auditor changed today.** Both commits were made `--no-verify` under recorded exceptions
in `registry/authorised_exceptions.json`, each describing a refusal observed on the exact tree before it was recorded.

The second commit also records, rather than hides, that it made the first commit's fix-state read **STALE** (it edits two
files that fix's seal depends on).

---

## 6. What did not land, and why

Nothing below is blocked on engineering capacity; each is blocked on a decision or on work not yet started.

**Waiting on Mahmood — 10 decisions** (D01 J-EMPHASIS-HF disposition · D02 publication/restoration disposition · D03
analysis-set sourcing · D04 primary-report evidence rank · D05 publication-only identity · D06 secondary evidence rank ·
D07 JUPITER subgroup scope · D08 direction-contract rollout · D09 legacy/unanchored admission · D10 screening coverage),
each with the exact question, options, consequences in numbers, and a recommendation labelled as a recommendation.

**Waiting on Mahmood — 33 individual signatures** (41 OPEN notices; batch is refused wherever a conclusion changed).
Judgements and signature acts are different quantities: few of the first, many of the second.
`scripts/sign_walk.py` presents one notice per invocation and never signs; `sign --expect-digest` refuses if the block
changed between reading and signing; the basis field prompts for his own words rather than pre-writing them.
**Not committed.** Two blockers remain: the six duplicate `(slug, outcome)` pairs need the exact selector (they are
genuine successive changes, chained `after`→`before` 6 of 6, not duplicates), and D01 has no notice because the change
has not been made — it is shown as NOT SIGNABLE with the correct order.

**Work identified and not started:** the direction contract (with the external fixture's four states as plants); the
empty-component-set abstain fix (blast radius measured: 9 served rows on 5 pages, 3 of them primaries — so it carries
result changes and is Mahmood's); the generic-keyword removal (footprint measured: 1 row of 25 at-risk changes, and it
is J-EMPHASIS-HF — the same decision as D01, reached from the config side); declaring components for 113 outcome specs
(content work, not code work); the notice-generator fix (one mechanism sentence stamped on every notice — wrong for
N27, subtly wrong for N37); and the "no single served answer" sweep (omega3 AF holds a pooled RR in JSON, renders
UNKNOWN, and has its row marked unbound — four objects, each internally consistent, disagreeing about one outcome; the
count is cheap to get and no provenance figure should be quoted again until it is).

---

## 7. The caveat that travels with every number here

Only **23 of 46** served pooled rows carry a locatable numerical source at all; 21 of the other 23 are migration-marked
and 2 are `ADMISSIBLE` with no locatable source (REWIND, DAPA-HF). Every provenance figure in this report is computable
on those 23 and says nothing affirmative about the rest. And where the served objects disagree about an outcome, "the
served answer" is not defined at all.
