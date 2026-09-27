# Reply to the second independent assessment (24 September 2026)

Written against `F:\mh-gate`, branch `enforcement-gate`, tip `1fa77f2c` plus an uncommitted parser landing.
Nothing in this reply has landed on `main`. No served number has moved. No countersignature has been applied.

## 1. What we accept without qualification

**The scope instruction.** We are not expanding the defect catalogue this cycle. Finding A (pool-input
linkage) and finding B (REWIND arm ownership) are the blockers; AMPLITUDE-O and FREEDOM go through the full
publication path after them. Defects found in passing are recorded and queued, not worked. This is a change of
direction for us: between the third pass and this assessment we found and wrote up three further defects. They
are parked, named, and listed in §5 so they are not lost — and not pursued.

**Five verdicts, not four.** `artifact integrity | state reproduction | INPUT LINKAGE | scientific admission |
publication eligibility`. We had implemented four, folding linkage into "arithmetic consistency", which is
precisely the conflation that let a correct calculation over the wrong rows read as a pass. Correcting this is
a reporting change in our case, not new detection: the refusals that constitute a linkage failure already exist
as distinct codes (see §2).

**A and B are different arrows.** We had not stated this clearly and it matters for how we sequence: certified-row
authority repairs A and leaves B untouched, because a single source of truth does not make a wrong row true.

**Your arithmetic.** Your independent calculation matches our producer to the digits we can compare: RR
**1.3920703685** (1.3260342677–1.4613950470) authentic, **0.7183544903** (0.6842776716–0.7541283241) reversed,
`se_log_ratio` **0.0247960569** identical in both directions. Our producer reports 1.3921 (1.3260, 1.4614) and
0.7184 (0.6843, 0.7541). We note the identical standard error across the reversal as the cleaner invariant —
it shows the swap is a pure relabelling, not a different computation.

We also accept your scoping of what the audit does *not* establish, including that an external trusted digest
for BUNDLE would detect the modified artifact, so this is a content-validation gap and not a cryptographic or
deployment compromise.

## 2. Finding A — status against your refinements

Our repair (lane POOL, `POOL.patch`, not landed) already satisfies most of what you specify, and we confirmed
each of these by reading the patch rather than from the lane's own summary:

- **Per-input agreement, not aggregate equality.** Enforced by row: `POOL_ROW_IDENTITY_MISMATCH` (trial id,
  report id, family id, analysis id), `POOL_SCALE_MISMATCH` (measure), `POOL_CONTRAST_MISMATCH` (orientation),
  `POOL_ANALYSIS_IDENTITY_MISMATCH` (analysis identity fields), `POOL_INPUT_TUPLE_MISMATCH` (estimate/CI).
- **Multiplicity validated BEFORE dict conversion.** The indexer records `POOL_INPUT_DUPLICATE` on the second
  occurrence and does not insert it, so a duplicate is evidence rather than an overwrite. This was the specific
  failure you warned about and the patch does not have it.
- **Unknown IDs and empty sets fail.** `POOL_INPUT_MEMBERSHIP_MISMATCH` reports `missing=` and `unknown=` in
  both directions, so an all-unknown substitution fails on membership rather than passing with zero admissible
  inputs.
- **Both comparisons.** `POOL_CERTIFIED_RESULT_DISAGREES` and `POOL_BUNDLE_RESULT_DISAGREES` are separate
  codes; the bundle list is treated as a checked copy, not an authority.

**What A still needs:** the verdict split (4 -> 5, with linkage separated), and an explicit identity and
declared multiplicity policy for the SELECTED set as an object distinct from the eligible candidates. We accept
your point that not every ADMISSIBLE candidate must be forced into every pool; our current structure derives
inputs from the primary outcome's rows, which is the selected set in practice but is not *named* as one.

## 3. Finding B — status, and where our repair is INCOMPLETE

Reproduced through the real producer: the authentic entry pools RR 1.3921; exchanging `ai<->ci` and
`n1i<->n2i` in the held hand entry — abstract, document digest and source span untouched — pools RR 0.7184
with the row still `EXACT_TARGET / verified / BOUND`. After our repair the swap is refused
(`ARM_OWNERSHIP_CONTRADICTED`), the authentic control pools unchanged, and a count absent from the source still
refuses as `ENDPOINT_UNBOUND`. The cause is that the held entry carries `{ai, n1i, ci, n2i}` with **no arm
label at all**, and `harness/verify.py:88` checks only that the digits OCCUR in the source.

**Our repair does not yet meet your contract, and we are not claiming it does.** You require each count and
denominator to be bound to the same source-supported **arm, outcome, analysis population and observation
window**. What we implemented binds the pair to an **arm** only — by minimum-cost matching of the two possible
assignments within the sentence carrying both numbers, which is order-independent and therefore not a
label-order check. It does **not** establish that the sentence belongs to the right outcome, the right analysis
population, or the right observation window. A trial reporting two harms with coincident denominators could
still bind from the wrong sentence. Closing B properly means carrying outcome, population and window into the
binding predicate, and we have not done that.

Measured before switching the refusal on: over all 35 held entries carrying a (count, denominator) or
(mean, SD) pair, **11 BOUND, 24 NO_ARM_EVIDENCE, 0 CONTRADICTED** — so refusing on CONTRADICTED moves no served
number today. **35 of 35 of those entries carry no arm identity, and 20 of them decide a row that is served.**
`NO_ARM_EVIDENCE` is deliberately not a refusal: it means the bytes the row is verified against never put both
numbers and both arm names in one sentence, so ownership is undetermined rather than wrong.

## 4. Where your §F.5 convicts a repair of ours

> "Do not turn an evidence-state uncertainty into a scientific exclusion merely to make the gate green."

We must disclose that a **different** repair of ours — the masking screen, unrelated to A and B — currently
does exactly this. Where the registry records a trial's masking as `NONE`/`SINGLE` while the abstract says
double-blind, we ABSTAIN, and that drops the trial. On the served corpus that is 2 of 127 rows:
EINSTEIN-DVT (PMID 21128814) and EMPHASIS-HF (PMID 21073363). The held bytes resolve the two in **opposite**
directions — EINSTEIN's abstract describes two studies, so the registry is right about the one its NCT names;
EMPHASIS-HF says "in this randomized, double-blind trial" with no open-label anywhere, so the registry entry is
wrong. Under your rule the correct behaviour is not abstention but adjudication under a **predeclared policy for
unresolved cases**, with assumption-dependent analysis labelled. We will restructure it that way rather than let
a checker disagreement remove a trial. The same rule governs SUSTAIN-6 and HARMONY and we accept it there.

## 5. Parked, not pursued (recorded so they are not lost)

Per §F.0 these are queued and explicitly NOT worked this cycle:
1. `harness/gate.py:158-160` — the overlap-k limb accepts every value 0..99 on 32 of 32 served pages and has
   never been capable of refusing. Its claim is false by construction on every page, because all 32 use the
   comparator panel, which suppresses the legacy numeric block by design.
2. `harness/honest_ratchet.py` — blocks are keyed into a SET by content digest, so adding a *second* instance
   of an existing disclosure is invisible while losing a unique one is visible.
3. `registry/notice_adjudication.json` — 51 of 78 pinned source paths and 41 of 41 notices were unanchored by a
   regeneration; the 27 that survived are exactly the commit-pinned `git:<sha>:<path>` entries.

## 6. Your correction to a fix we already landed

> "A table need not be one contiguous string if a verifiable multi-location witness establishes its relevant
> row, headers and context."

Accepted. Our table-binding repair (landed at `1fa77f2c`) refuses non-colocated table sources outright
(`TABLE_SOURCE_NOT_COLOCATED`), which is stricter than your contract and would reject a legitimate
multi-location witness. The admissible test is whether the witness establishes row, headers and context — not
whether the bytes are contiguous. Queued for after A and B, per the scope rule.

## 7. What we have NOT done, and will not claim

The acceptance suite in §F.6 has **not** been run. No probe in this reply exercised the complete
producer -> renderer -> publication gate with integrity material regenerated through the legitimate build, and
nothing here has been re-checked on post-fix served bytes. Until that runs, our position is the narrower one you
state: selected bytes and calculations are reproducible; scientific admission is unresolved; "verified" is not
the word for it.

We will not credit a stale certificate, a missing baseline, or any unrelated first blocker as a semantic
refusal, and every acceptance run will log the selected records, the derived inputs, the first refusal, and the
restored acceptance.

---

# Addendum: the denominator finding, CONFIRMED on the real producer — and the live release has moved again

## Release identity
The live release is now **`4d712dfa`** (html `5d16b04a…`, release `6a04a3df…`, BUNDLE `75ffd8a2…`,
`hand_binding` blob `d48224ed…`). Our probes below were run on our own checkout, whose `_tuple_in` is
character-for-character identical to the reproduction supplied, so the defect is not specific to `4d712dfa`.
Earlier identities cited in this reply (`38c04411`, `9fc4518a`, `b127522d`, `a4e556e3`) are superseded as the
live release; they remain valid as the trees particular measurements were made on, and each measurement names
its own.

## The finding, and it widens B beyond the pair swap
`harness/hand_binding.py:225`, counts branch:

    den_ok = n is not None and (_present(t, _forms(n)) or _present(ctx, _forms(n)))
    pct_ok = n is not None and _present(t, _pct(ev, n))
    if not (den_ok or pct_ok): return False

We ran the supplied cases through the **real** `harness.hand_binding._tuple_in`, not a reproduction:

    VALID_CONTROL              (2347,4949,1687,4952) -> True
    WRONG_DENOMINATORS_ONLY    (2347,4956,1687,4940) -> True
    EVENT_COUNTS_ONLY_SWAPPED  (1687,4949,2347,4952) -> True
    DENOMINATORS_ONLY_SWAPPED  (2347,4952,1687,4949) -> True
    ABSENT_EVENT_CONTROL       (2348,4949,1687,4952) -> False

and confirmed `"4956" in sentence -> False`, `"4940" in sentence -> False`.

**`WRONG_DENOMINATORS_ONLY` is worse than the swap we had already confirmed.** The swap at least preserved the
true numbers; this binds a denominator reported NOWHERE, because `den_ok OR pct_ok` lets the displayed
one-decimal percentage stand in for the denominator. The percentage is a **denominator wildcard**: 47.4%
admits any n in 4947–4956 (10 values), 34.1% any n in 4940–4954 (15 values).

We accept the diagnosis in full, including that `_direction_ok` (`:448`) inspects only the order of arm names
and never sees the numbers, and that `bind_hand_row` (`:487`) has no count-to-arm association step.

## What this does to our own repair — stated plainly
The arm-ownership repair we reported closes the **pair swap** by binding counts to arms through sentence
structure. **It does not close the wrong-denominator case at all**, because the arm names still sit beside the
correct counts; only the denominator is false. Our repair and this finding are different arrows, exactly as
you said of A and B.

## What is being built now
Typed per-arm observations `{arm, events, n, outcome, population, window, span}` in the served extraction
object; each event count bound to its arm by source structure rather than name order; the denominator required
to be the reported randomised/analysed n bound to a span, or derived with its basis declared — **a rounded
percentage may corroborate a denominator and never substitute for one**. A corpus-wide sweep is running for
rows that currently bind only via the percentage route, to be reported as `n of N` with N named. All five
cases become plants through the real producer, each observed firing before the fix, and are added to the §F.6
acceptance suite.

## Correction to §3 of this reply, which is now stale
§3 said the four-dimension binding (arm, outcome, population, window) was NOT done. It has since been built
and measured over all 35 held pair-entries: **arm 11 BOUND, outcome 1, population 0, window 0; 0 CONTRADICTED
in every dimension.** Population and window have **no evidence anywhere in the held bytes**, so those two
dimensions are implemented and, on this corpus, inert — UNEXERCISED rather than satisfied. Closing them for
real needs richer held sources, not a better rule. §3's statement of the gap stands as a record of what was
true when written; this is the current state.

---

# Correction to the release identity above, measured from the SERVED bytes (2026-09-24, 19:2xZ)

The addendum above states the live release is `4d712dfa`. **That is not what is being served**, and `main`
is not being served either. Measured by fetching the bytes rather than by reading a branch:

    GET .../reviews/pcsk9-mace/index.html        sha256 d823c243e4d07c80…  (177,345 bytes)
    GET .../reviews/pcsk9-mace/CERTIFICATE.json  sha256 9ee44c50aa173122…  (14,176 bytes)
                                                 release_sha256 3c631ae8f98fcd32…

    git blob 752e9c1f:docs/reviews/pcsk9-mace/index.html        d823c243e4d07c80…   MATCH
    git blob 752e9c1f:docs/reviews/pcsk9-mace/CERTIFICATE.json  9ee44c50aa173122…   MATCH

    git blob d10b0d24:…/index.html  20ddcd1ca4c5d0ee…   NOT served
    git blob 41f3e2d0:…/index.html  20ddcd1ca4c5d0ee…   NOT served   (41f3e2d0 IS the tip of main)
    main tip CERTIFICATE release_sha256  87c025b0f0d418ea…              NOT served

So: **the newest commit consistent with the served bytes is `752e9c1f` (2026-09-24 18:05Z).** The two
commits after it — `d10b0d24` (the 4th re-certification, which rebuilt all 32 pages) and `41f3e2d0` (the
bundle re-stamp, the tip of main) — **are on GitHub and are NOT live.**

Two honest qualifications:

1. The served page bytes are byte-identical across **13** commits (`1d4b4b3f` … `752e9c1f`), because the
   page did not change across them. The served bytes therefore cannot single out which of the 13 produced
   them; `752e9c1f` is the newest they are consistent with. What they *do* establish exactly is the
   negative: everything after `752e9c1f` is not served.
2. `4d712dfa` is one of those 13, so the addendum's claim is not contradicted by the page bytes — it is
   merely unidentified by them, and it is no longer the newest served candidate.

A first attempt at this used the string `commit 6b1039cd` scraped from the live index page. That is a
**narrative mention inside body prose** about an unrelated past incident, not an identity field, and
`6b1039cd` is 145 commits behind main. The identity had to come from the certificate artefact. Recorded
because it is the same error class as the rest of this reply: a scan reporting where it looked.

---

# Correction: the percentage wildcard is WIDER than we reported, and the exposure is now measured

## The equivalence classes we quoted were too small
The addendum states 47.4% admits any n in 4947–4956 (10 values) and 34.1% any n in 4940–4954 (15 values).
Those are the classes for the *displayed one-decimal* percentage only. The legacy predicate is wider:
`_pct` (`harness/hand_binding.py:212`) also emits an integer form and a two-decimal form, and `_present`
(`:216`) permits an integer prefix before a decimal point. A rounded zero therefore matches `0.xxx`
anywhere in the span — including an unrelated P value — so **for any positive event count every
n > 200 × events satisfies the predicate**. Measured across the exposed rows: the legacy class is
**unbounded for 10 of 14 count-arm slots** and finite for 4 of 14. REWIND's is one of the unbounded ones.
Our earlier figure understated the defect; we are correcting it rather than leaving the smaller number
standing.

## Exposure, measured through the real admission producer
N = **34** held count extractions (all in `verified_arms.json`; 259 held verified entries in total, the
other 225 carry no count fields). The partitions are disjoint:

    percentage-route only (exposed)           7 of 34
    locally denominator-backed ("safe today") 2 of 34
    abstained already                        20 of 34
    legacy admissions, hand binding not run   5 of 34

So among rows that actually BOUND, the exposed share is **7 of 9**. At arm-slot level that is 14 of 68
count-arm slots; **12 of 14 of those denominators do appear elsewhere in the resolved held source, and
2 of 14 appear nowhere in it.** The single row whose denominator is absent from its source is
dapagliflozin-hfpef-hosp, PMID 34711976, Adverse events, claimed n = 162/162 — the abstract reports 324
total and neither arm's n. Its entry cites a registry basis that is not present in this tree, so that
basis is **UNMEASURED**, and we do not claim n = 162 is scientifically wrong.

## Plants, through the real producer
All five cases were observed through `pipeline.build_outcome_from_inputs` to pooling with no gate
disabled, before any repair source existed, plus a restore:

    before:  WRONG_DENOMINATORS_ONLY    BOUND, pooled, estimate 1.3867   (authentic 1.3921)
    after:   WRONG_DENOMINATORS_ONLY    ABSTAIN, COUNT_DENOMINATOR_MISMATCH
    before/after: ABSENT_EVENT_CONTROL  ABSTAIN, ENDPOINT_UNBOUND        (correct refusal preserved)
    restore: producer output identical, input hashes unchanged

One expectation in our own brief was wrong and the lane corrected it: we predicted all three malicious
cases would pool before the fix. **Two of the three were already stopped downstream** by the arm-ownership
repair (`ARM_OWNERSHIP_CONTRADICTED`) even though the binder said BOUND. Only the wrong-denominator case
pooled — which is exactly the arrow the arm repair does not close, as §"What this does to our own repair"
above states.

## Admission cost — this one moves served numbers, so it is not ours to land
After the repair, **4 of 34 have admissible typed observations and 30 of 34 abstain**. Of the 7 exposed
rows, 3 still admit (their denominators are bound by structure: glp1-ra-mace-t2d, semaglutide-obesity-mace,
spironolactone-hfref-mortality) and **4 would now refuse**. That is a served-number change. It stays
unlanded and goes to Mahmood for signature; nothing in this section has moved a published pool.

---

# Correction to §7: the §F.6 acceptance suite HAS now been run, pre-fix — and it publishes finding A

§7 above says the acceptance suite "has **not** been run". It has now, against the unrepaired checkout
`a4e556e3`, through the real production entry points (`scripts/build_topic.py:43`,
`scripts/build_bundle.py:2400`, `harness/gate.py:1289`, then the independent
`scripts/verify_bundle.py --root docs --slug glp1-ra-mace-t2d --json`). No producer, renderer, predicate,
gate or verifier was edited; original bytes restored (`original_bytes_restored: true`).

**Lane acceptance: FAIL — 15 of 19 cases lack complete acceptance proof.** 17 of 19 reached the local
publication gate; 2 stopped at the producer's own schema refusal, which is credited at the producer
boundary only, with downstream enforcement unproven.

## Finding A, demonstrated end to end rather than argued

Five pool-linkage attacks reach publication with **no refusal anywhere**:

    rotated_ids · unknown_id · duplicate_id · omitted_id · altered_inputs_updated_aggregate

For `unknown_id`, quoted from the recorded command output:

    publication_gate   python -m harness.gate docs/reviews/glp1-ra-mace-t2d
                       returncode 0   stdout "GATE PASS  docs\reviews\glp1-ra-mace-t2d"
    independent verifier                     returncode 0
    first_refusal                            null
    linkage audit      UNKNOWN_INPUT_ID F6_SYNTHETIC_UNKNOWN_ID
                       OMITTED_INPUT_ID PMID 31185157

The gate returns PASS on a pool carrying an input ID that exists nowhere while a real trial is dropped.
This is the conflation you named: a correct calculation over the wrong rows reading as a pass.

**`input_linkage` is `NOT_IMPLEMENTED` on this tree**, and the run says so rather than inventing the
verdict. The five-column ledger is explicitly labelled a projection of real command output, with
`verdict_provenance` recorded per verdict; the linkage column is a harness oracle ("exact ID multiset and
ID-owned tuple comparison"), never a native refusal. That is the honest reading of our own §F.2 gap.

## The repair maps onto all five, verified against the patch text

    rotated_ids                        POOL_ROW_IDENTITY_MISMATCH
    unknown_id / omitted_id            POOL_INPUT_MEMBERSHIP_MISMATCH  (reports missing= and unknown=)
    duplicate_id                       POOL_INPUT_DUPLICATE
    altered_inputs_updated_aggregate   POOL_INPUT_TUPLE_MISMATCH

`POOL_INPUT_DUPLICATE` is appended on the `elif ident in indexed` branch, before `indexed[ident] = row`
in the `else` — so a duplicate is recorded as evidence and never silently overwrites. That is the
validate-before-dict-conversion property you required, confirmed in the patch rather than in a summary.

## What this run does NOT establish

- It is the **local topic publication gate**, not the repository-wide `verify_all` / GitHub Actions gate
  (`.github/workflows/verify.yml:60`), which was not run. No served release was changed or reverified.
- `scientific_admission` reads FAIL on **every** reached case including the baseline, because the verifier
  returns HARMONY (PMID 30291013) INADMISSIBLE. A column that is constant across all cases discriminates
  nothing; it records checker output, not a clinical conclusion.
- The four FREEDOM cases and `rewind_arm_swap` are `UNPROVEN`, because the first refusal encountered was
  unrelated or inexact. Per your rule we do **not** credit an unrelated first blocker as a semantic
  refusal, so they are not counted as passes.
- Two cases (`estimand_missing`, `schema_detector_control`) stopped at the producer, so their downstream
  stages are `NOT_REACHED` — recorded as such, not as enforcement.

---

# Your REWIND follow-up: correction accepted, core defect confirmed, and one retraction of ours

Live release re-checked by fetching the bytes: the served `reviews/pcsk9-mace/index.html` now hashes to
`20ddcd1c…`, which is the blob at **`41f3e2d0`**. Your identity is current. Our earlier note that the last
two main commits were "on GitHub and not live" was true when measured at 19:2xZ and has been overtaken by
the deploy landing; it is superseded, not withdrawn.

## 1. Your correction is right, and we confirmed it on the real path as you asked

Not a reproduction — the real `harness.verify.verify_pooled`, imported from the module, on the real held
REWIND record and the real held abstract:

    VALID_CONTROL            (2347,4949,1687,4952)  -> verified   -> gate PASS
    AUTHENTIC_PAIR_SWAP      (1687,4952,2347,4949)  -> verified   -> gate PASS
    UNREPORTED_DENOMINATORS  (2347,4956,1687,4940)  -> not-yet    -> gate REFUSE
    ABSENT_EVENT_CONTROL     (2348,4949,1687,4952)  -> not-yet    -> gate REFUSE

`harness/verify.py:89` requires each of ai/n1i/ci/n2i as exact digits in the checked text;
`harness/gate.py:329 check_pooled_verified`, called at `gate.py:1309`, refuses any status that is not
`verified`/`verified_handchecked`. In the held abstract `"4956"` and `"4940"` occur 0 times each, while
`"4949"` occurs once and `"4952"` twice.

**So the percentage wildcard in `_tuple_in` is a binder defect and NOT a publication-path defect for
absent numbers.** We accept the narrowing. Our earlier addendum presented the wrong-denominator case as
the more serious of the two; that ordering was wrong and this supersedes it.

One qualification that survives: our lane F4B observed the wrong-denominator plant *pooling* (estimate
1.3867 against the authentic 1.3921). That is true of the route it exercised —
`pipeline.build_outcome_from_inputs` through pooling — which does not include `check_pooled_verified`.
Two different routes, two correct observations; the publication path is the one that decides, and it
refuses.

## 2. The narrowed core defect — confirmed, and it is corpus-wide, not REWIND-specific

`AUTHENTIC_PAIR_SWAP` passes every layer, exactly as you state. All three of your structural reasons
verify on `origin/main`:

- `comparator_direction` appears in `harness/pipeline.py:423` only as a **field name in a copy list**, so
  when the record lacks it nothing is copied and the direction predicate never runs.
- `harness/gate.py:900 check_arm_object_contract` is about which trials are ELIGIBLE — its own docstring
  says it "catches stale pages or hand-edited pools where a refused trial survived" — not which numbers
  belong to which arm.
- The served BUNDLE marks REWIND GI `evaluated_by_bundle: false`; `NOT_ASSESSED_BY_BUNDLE` occurs **47**
  times in it.

**Corpus sweep, run through the real `verify_pooled` over all 18 held `verified_arms.json`:**

    held rows carrying all four count fields (N)                  34
    rows carrying NO comparator_direction                         34 of 34
    rows reaching publication (check_pooled_verified PASS)        34 of 34
      of which verified 29, verified_handchecked 5
    rows refused downstream                                        0 of 34

The kinds of row in that population, stated before the number: 14 `fulltext_verified_arms`,
8 `abstract_verified`, 6 `abstract_verified_arms`, 3 `aact_verified`, 2 `published_rate`,
1 `registry_verified`.

So the swap is undetectable on **every** held count row, not only REWIND, and no existing row is refused
downstream — which also means the binder defect has **no publication-path exposure on the current
corpus**, consistent with §1.

Your regression is now being built to that specification: typed `{arm_id, events, total}` linked to a
named arm by a source witness; original PASS -> whole-object swap with arm_ids fixed
ARM_OWNERSHIP_MISMATCH -> restore PASS; plus the deliberate whole-contrast reversal as a second control,
so the fix cannot degenerate into "first number = treatment"; through the complete producer -> renderer ->
publication gate.

## 3. A retraction of our own, before you find it

We reported a hand-confirmed corpus instance of a fabricated denominator: `dapagliflozin-hfpef-hosp`
PMID 34711976, n = 162 per arm, "an assumed half of the randomised 324, stated nowhere". **That is
withdrawn.** The entry's `source` span is 645 characters and we inspected a 300-character prefix of it.
The truncated remainder is an AACT denominator source citing
`outputs/handover/in3/aact/reported_event_totals.txt` with per-arm-group totals of 162 for NCT03030235 —
a file that is present and tracked on main. Additionally that row's provenance is
`abstract_verified_arms`, which is **not** in the abstract branch at `harness/verify.py:73`, so the check
runs against the source span and whether 162 appears in the *abstract* is irrelevant to it. We reported a
property of the whole from a prefix, and checked a text the verifier never consults.

Our own lane F4B had stated the basis was UNMEASURED in its partial tree and explicitly declined to claim
n = 162 was wrong. It was right and we over-read it. There is consequently **no hand-confirmed corpus
instance** of a denominator absent from the bytes the verifier checks, and our exposure figure of 7 of 34
percentage-route rows still rests on a single measurement by the lane that built the repair.

## 4. Parked, not pursued (§F.0), but recorded with its number

`harness/verify.py:73` sends the digit check to the **source span** rather than the held abstract for any
provenance outside `("abstract","pmc_fulltext","abstract_verified")`. That is **26 of 34** held count
rows. The function's own comment says a hand-verified row must be checked against the held bytes "never
against the hand-written description that carries the same digits (that is not a check)" — and for those
26 rows the span *is* the hand-written description. We are not working this in this cycle, per your scope
rule; it is named here so it is not lost.

## 5. Accepted without qualification

The new manifest's `CLEAN_EXCEPT_OWN_OUTPUTS` build state is a real provenance improvement and we take
the credit as given rather than restating it.

---

# Your two arm-ownership passes: both reproduced, both repaired, and three things you should know

## 1. The non-injective witness — reproduced exactly

Real modules, real held abstract, no reproduction:

    AUTHENTIC                       RR 1.3921   verify_pooled=verified   gate PASS
    NON_INJECTIVE (ai -> 1687)      RR 1.0006   verify_pooled=verified   gate PASS

`"1687"` occurs **once** and witnesses both arm slots. We accept it in full, including that the invariant
is not "the numbers must differ": equal arm values are legitimate and a real served row proves it —
`PMID 35041780, Mortality, ai=530 ci=530` with denominators 2433 and 2413.

**A correction to our own rule before you find it.** We first wrote injectivity as *four distinct witness
coordinates*. Measured against the data lane's 32 authentic rows, that would have refused **25 of 32**,
because their witnesses are recorded at sentence granularity. At **token** granularity it is exactly
right: `"530"` occurs twice in that abstract so equal values pass, `"1687"` once in REWIND so the attack
refuses. The rule now reads: the coordinate locates the field's own numeric token.

**And a second correction, from an adversarial probe: shape validation is not the defence — replay is.**
Off-by-one slices, partial overlaps, nested intervals and two table-alias forms all present four
*distinct* coordinates and pass the injectivity check; they are caught only when the witness is replayed
against held source. Four distinct coordinates is necessary and nowhere near sufficient.

## 2. The CT.gov architecture — confirmed verbatim, and the object now reaches BUNDLE

    target_endpoint.py:759  classifies the groupIds      :788  returns intervention_arm/comparator_arm
    target_endpoint.py:875  projects to bare ai/n1i/ci/n2i    :877  names survive only in a PROSE span
    target_endpoint.py:1014 the row carries only the four numbers

Searched `harness/` and `scripts/`: those two fields appear **only** in `target_endpoint.py`. Nothing
downstream reads them.

The typed role object now survives **extraction -> candidate -> row -> verify_pooled -> gate -> BUNDLE**,
proven on the **real** topic `glp1-ra-mace-t2d` with the data lane's real rows.
`COUNT_ARM_OBJECTS_MISSING` cleared on 2 of 2 rows. Your regression set returns the intended verdicts —
`ARM_EVENT_OWNER_MISMATCH` for the event-only change with group_id kept, `CONTRAST_REVERSED_POLICY` for
the whole-object reversal (refused by predeclared policy, not silently relabelled), and PASS for equal
values with distinct witnesses on three separate routes.

## 3. Two consumers do NOT enforce what the producer now carries

    the SERVED verifier   0 of 3 mutating FREEDOM cases refused; reports BOUND, fails only on
                          CERTIFICATE_MISMATCH
    the BUNDLE route      0 of 3 bundle-only ownership attacks refused, using the authentic served
                          envelope and the exact production-generated count field

Your item (e) is therefore **not satisfied** on either route. We are not claiming otherwise, and we did
not credit the full-build FAILs on those cases as ownership refusals — they were unrelated
artifact/certificate mismatches, and counting them would be the inexact-first-blocker error your contract
forbids.

## 4. A NEW defect of the same family, found by attacking our own repair

> A denominator explicitly belonging to **headache** is accepted for **nausea** — through shape, replay,
> admission (`EXACT_TARGET`), verification (`verified`), and the real hand-override producer.

Years, PMIDs, percentages and CI bounds are all refused. The cause:
`count_observations.py:113 denominators(doc, terms)` takes the document and the **arm terms**; the
outcome is not a parameter. `outcome` is carried in the observation and compared as a value, but never
constrains where a denominator may be located.

This is finding B one step along: **occurrence is not ownership** became **arm ownership is not outcome
ownership**. Per your scope rule it is recorded and queued, not worked.

## 5. What gates all of it

    certificates pinning a POOL-edited module   32 of 32  (all pin harness/gate.py and build_topic.py)
    new POOL_* refusals on served pages          0 of 32
    served pages refusing on the CERTIFICATE    32 of 32

No source patch here is landable without a 32-topic regeneration and recertification. That is a
served-artefact change and it is Mahmood's signature, not ours. We had earlier stated POOL moved no
served number and could land under delegated authority; that was wrong, and it is withdrawn.
