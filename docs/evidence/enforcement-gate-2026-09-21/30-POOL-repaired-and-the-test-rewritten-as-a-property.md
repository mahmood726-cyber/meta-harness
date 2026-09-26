# POOL repaired: 4 of 4 controls publish, 5 of 5 attacks refuse exactly — and the test now asserts a property

Measured 2026-09-24 by lane F6C in `/f/mh-f6`, then amended by me. Nothing landed; no served number moved.

## The result

**`F6C_ACCEPTANCE PASS`** — the conjunction bar in
`29-decision-POOL-repair-and-codex-lane-ledger.md` is met, both halves:

    required controls publishing            4 of 4   baseline, reorder_records,
                                                     reorder_pool_records, freedom_decimal_normalisation
    named pool attacks refusing with the
      EXACT intended first refusal          5 of 5   rotated_ids            POOL_ROW_IDENTITY_MISMATCH
                                                     unknown_id / omitted_id POOL_INPUT_MEMBERSHIP_MISMATCH
                                                     duplicate_id            POOL_INPUT_DUPLICATE
                                                     altered_inputs_updated_aggregate
                                                                             POOL_INPUT_TUPLE_MISMATCH

19 of 19 ledger cases executed by the same producer -> renderer -> bundle -> local publication gate ->
independent verifier route, with a fresh baseline restoration after every case. No deployment, signing,
commit or push.

`rotated_ids` now refuses on `POOL_ROW_IDENTITY_MISMATCH` rather than the inexact
`POOL_INPUT_TUPLE_MISMATCH` it returned before, so it is credited this time.

## The repair, and why it is the right shape

    scripts/build_bundle.py:2404   RETAINS the check_pool_contract refusals
    scripts/build_bundle.py:2409   REMOVES the admission-only refusal
    scripts/verify_bundle.py:919   RETAINS independent admission computation
    scripts/verify_bundle.py:924   REMOVES admission from the publication conjunction
    harness/gate.py:1289           RETAINS the verification refusals

Admission is still computed, still reported, and still disclosed. What it no longer does is silently
convert into a publication refusal. That is the §F.5 rule applied: an evidence-state uncertainty is
adjudicated under a predeclared policy and disclosed, never turned into a scientific exclusion to make a
gate green. HARMONY is **not** special-cased, which was an explicit instruction.

## The test: rewritten from a behaviour record into a requirement

F6C's rewrite still named the trial:

    assert next(r for r in report["rows"] if r["pmid"] == "30291013")["predicates"]["P5_family_eligible"] is False

That is a behaviour record, and it fails the instruction to assert the property. It is also the same
defect class as the assertion it replaced: the original named `POOL_PUBLICATION_INELIGIBLE` and the PMID,
which **defended** the corpus-emptying behaviour — repairing that defect turned the suite red and looked
like a regression.

`test_verdicts_are_independent_and_an_inadmissible_row_is_disclosed` now asserts two properties, naming
no trial:

1. **Independence** — if `scientific_admission` is not PASS then some row must be named inadmissible,
   and `publication_eligibility` must still be `ELIGIBLE`. A failing admission may not by itself block
   publication.
2. **Disclosure** — every inadmissible row carries at least one failing predicate explaining why, and
   none is counted in the admissible total. The count generalises from `k - 1` to `k - len(refused)`.

The fixture carried the same defect and was fixed too: `seven_row_control` dropped `PMID 30291013` by
name. It now calls `refused_on_admission()`, which derives the ids from the verifier and asserts it found
at least one. **A control that names a trial stops controlling anything the day that trial's evidence
state changes** — which is precisely the `lessons.md` rule that a control must be synthetic or pinned,
never anchored to a live corpus row.

The only surviving mention of the PMID is in the docstring, explaining why it must not be asserted.

## A second test of mine had the same coupling, found by running the suite

`test_producer_emission_boundary_refuses_substitution` asserted `problems[0]`, the first problem
**overall**. On any patched tree that fails, because editing a pinned module changes the tree bytes and
`analysis_code_sha256` stops matching the certificate until the corpus is rebuilt — so an integrity
problem legitimately precedes the semantic one:

    'harness/gate.py: tree bytes give c82fe23c..., certificate declares 20a5ce33... (analysis_code_sha256)'

The contract is that the first **semantic** refusal names the defect, not that it is first overall, and
acceptance item (d) requires integrity and semantic checks to stay separate categories. The test now
filters integrity problems out and asserts the first remaining semantic problem is
`POOL_ROW_IDENTITY_MISMATCH`, with a guard that there is a semantic problem at all rather than only
integrity noise. That preserves the intent instead of weakening `startswith` to `in`, which would have
lost the first-refusal property the contract cares about.

## Status

POOL moves from **blocked, pending repair** back to a landing candidate. The corpus-wide question it was
always waiting on is still open and still gates it: **does `check_pool_contract` refuse any of the 32
served topics as they stand?** F6C establishes 1 of 32 (`glp1-ra-mace-t2d`, whose baseline now publishes).
A refusal on a served topic is a served-number change and therefore Mahmood's signature, not mine.

---

# Verification of the amendment, and the landing candidate

## The suite

    tests/test_pool_binding.py    43 passed, 0 failed    (F:\mh-f6, base a4e556e3)

Getting there took three iterations and each one is worth recording, because two were my own defects:

1. `test_producer_emission_boundary_refuses_substitution` asserted `problems[0]` — the first problem
   **overall**. Editing a pinned module changes the tree bytes, so `analysis_code_sha256` stops matching
   the certificate and an integrity complaint legitimately precedes the semantic one.
2. My first fix filtered integrity problems by the prefixes `harness/` and `scripts/` and **missed the
   mirrored family** — `docs/harness/gate.py: mirrored bytes differ from the certificate input` starts
   with `docs/`. The filter now covers it, and the reason is written in the code so the next person does
   not rediscover it.

## The test can FAIL — proven, not assumed

A test that has only ever passed has not been shown to test anything. The defect it exists to catch was
planted in the real code: `publication_eligibility` was re-coupled to admission in
`scripts/verify_bundle.py:924` (`... and linkage and admission ...`). Result:

    FAILED test_verdicts_are_independent_and_an_inadmissible_row_is_disclosed
    E   - ELIGIBLE
    E   + REFUSED

— the exact independence violation, raised at the independence assertion. The plant was then reverted
(`grep -c PLANT` -> 0) and the suite returned to **43 passed**.

## The landing candidate

`POOL_REPAIRED.patch` — 103,464 bytes, **10 files**, secured at `C:\mh-artefacts\patches\`
(sha256 `48f69167e416b614…`, verified identical on both copies).

    harness/gate.py                scripts/build_bundle.py      scripts/build_topic.py
    scripts/f6_acceptance.py       scripts/f6_report.py         scripts/verify_bundle.py
    tests/test_bundle_verifier.py  tests/test_f6_harness.py     tests/test_gate.py
    tests/test_pool_binding.py

**A first attempt at this patch was wrong and would have shipped incomplete.** `git diff` omits untracked
files, and four of the ten — including `tests/test_pool_binding.py`, which carries the entire rewritten
property test — are new files. That patch was 33,303 bytes and silently contained none of them. Caught by
listing the files in the artefact rather than trusting the command; regenerated with `git add -N`.

Applies clean to pristine `a4e556e3`, verified by stashing the working tree and running
`git apply --check` against the bare commit, then restoring.

Occurrences of `30291013` added by the patch: **1**, and it is the docstring sentence explaining why the
PMID must not be asserted.

## Still the gate on landing

Unchanged from `26-landing-sequence-after-decision-B.md`: does `check_pool_contract` refuse any of the
**32 served topics** as they stand? F6C establishes 1 of 32 (`glp1-ra-mace-t2d`, whose baseline now
publishes). A refusal on a served topic is a served-number change, and therefore Mahmood's signature.

---

# The landing gate, answered: POOL moves no served number

Measured on `F:\mh-gate` (the GitHub clone), 2026-09-24. `26-landing-sequence-after-decision-B.md`
recorded this as **UNMEASURED** and refused to let it pass as a finding. It is now measured.

`check_bundle_pool` (`harness/gate.py:1289`) treats a review three ways, so the population has three
kinds and a single count would hide the one that matters:

    A  has BUNDLE.json                                   -> the full contract runs
    B  no BUNDLE.json, manifest has source.served_blob_git_sha1
                                                         -> POOL_BUNDLE_REQUIRED, a REFUSAL on a
                                                            page that publishes today
    C  no BUNDLE.json, no such marker                    -> [] , legacy gates retained

Result over all 32 served review directories:

    A  has BUNDLE.json, full contract runs        :  1 of 32   (glp1-ra-mace-t2d)
    B  NO bundle but manifest requires one        :  0 of 32
    C  NO bundle, no requirement, legacy retained : 31 of 32
    ?  manifest unreadable                        :  0 of 32

**0 of 32 would newly refuse.** The single bundled topic is `glp1-ra-mace-t2d`, and its baseline
**publishes** after the repair — that is one of F6C's 4 of 4 controls. The other 31 keep their existing
gates untouched, which is the documented intent: *"Unbundled pages retain their existing gates; this is
not portfolio-wide coverage."*

## A denominator mistake of mine, caught by the rule that exists for it

My first attempt ran the verifier over every directory containing a `BUNDLE.json` and reported
**"topics with ANY POOL_* code: 0 of 1"**. That number is true and answers nothing: the filter had
silently reduced 32 to 1, and I had asked a question about 32. It is the `lessons.md` trigger verbatim —
*before reporting any count, list the KINDS of item in the population, not just the number*. The
measurement above names three kinds precisely because the first one did not.

## What this changes

POOL moves **no served number**, so landing it is an engineering decision under delegated authority
rather than a change requiring Mahmood's signature. The blast radius is one topic, and that topic
publishes.

Two limits stated rather than glossed: this measures the bundle-pool limb specifically, on the tree as it
stands today; and a topic that is *later* bundled enters kind A and gets the full contract, which is the
intended behaviour and not a regression.

---

# CORRECTION: "POOL moves no served number" was WRONG, and my property test had a hole

An adversarial lane was briefed to break five claims we were about to rely on. It **refuted three**, two
of which were mine. Recorded here because the landing conclusion above depended on one of them.

## The landing conclusion is withdrawn

Above I wrote: *"POOL moves no served number, so landing it is an engineering decision under delegated
authority rather than a change requiring Mahmood's signature."* **That is withdrawn.**

The measurement it rested on is still correct as far as it went — of 32 served review directories, 1 has
a `BUNDLE.json`, 0 have a manifest requiring one without it, 31 retain legacy gates, so **0 of 32 newly
refuse via a `POOL_*` code.** What it missed is a different refusal path entirely:

> **Applying POOL edits pinned modules, so `analysis_code_sha256` no longer matches the certificate, and
> the served page's full gate goes PASS -> REFUSE until the corpus is recertified.**

The probe found exactly one full-gate before/after comparison — `glp1-ra-mace-t2d` — changing from PASS
to REFUSE, with certificate refusal emitted at `harness/certificate.py:254` and publication calling the
certificate and POOL checks separately at `harness/gate.py:1330` and `:1331`. The other 31 were not run
before/after, so their regression count is **UNTESTED**, not zero.

**So landing POOL requires a 32-topic regeneration and recertification, which changes served artefacts
and is Mahmood's signature, not mine.** The same applies to every other source patch in this stack.

This is not new knowledge. It is recorded in my own notes as *"any pinned edit = rebuild 32/32"*, and I
hit it twice today — it is why `test_producer_emission_boundary_refuses_substitution` needed the
integrity/semantic split earlier in this very file. I had the rule, applied it to a test, and failed to
apply it to the landing decision. Owning a rule is not the rule firing.

Claim 1 fell the same way: the four controls publish **at the verifier boundary**, which is what F6C
measured, but the full publication gate refuses the baseline on the certificate. 0 of 1 tested full-gate
controls publish; the other three were tested at the verifier boundary only and are UNTESTED at the full
gate.

## My property test could be passed by a report that hid a row

The probe confirmed the vacuity case I had worried about is **not** a hole — hiding the inadmissible row
while admission still fails does trip the assertion. But this passed:

> remove the inadmissible row, falsely declare `scientific_admission: PASS`, and set `admissible_rows`
> back to the original `k`.

The independence branch is skipped (admission reads PASS), the disclosure loop is vacuous (nothing
refused), and `admissible_rows == k - len(refused)` compares **two report-supplied numbers to each
other** — nothing tied the report's rows back to the certified pool.

Fixed by anchoring to something the report cannot shrink unnoticed:

    assert len(report["rows"]) == report["pool"]["recomputed"]["k"]

Verified against the lane's exact defective report:

    authentic                            PASS
    hidden row + false admission PASS    REFUSED -- "report carries 7 rows for a certified pool of 8"
    hidden row, admission still FAIL     REFUSED -- "no row is named as inadmissible"

## One claim was UNTESTED because I mis-briefed it

Claim 4 (witness injectivity) came back UNTESTED: *"No `ARM_WITNESS_NOT_INJECTIVE` implementation or
injectivity test was found."* Correct — that work is lane F4G's and lives in `F:\mh-f4`, while the probe
ran in `F:\mh-f6`. I put a claim about one tree into a lane running in another. The lane was right to
refuse to confirm it from source reading, and right not to build a toy checker to test it with.

## What stands

Claim 3 is **CONFIRMED**: FREEDOM-2's five negative cases return the exact intended first semantic
refusal in both independently supplied routes.

## The true blast radius: 32 of 32, not 0 of 32

The adversarial lane demonstrated one served page going PASS -> REFUSE and left the other 31 UNTESTED.
Measured directly, by reading what each served certificate pins:

    served review directories (N)                              32
    certificates pinning at least one POOL-edited module  32 of 32
      -- all 32 pin ['harness/gate.py', 'scripts/build_topic.py']
    certificates pinning none of them                      0 of 32
    directories with no CERTIFICATE.json                   0 of 32

POOL edits `harness/gate.py` and `scripts/build_topic.py`, and **every** served certificate pins both.
So applying POOL invalidates `analysis_code_sha256` on **32 of 32** served pages, and each one refuses at
the full gate until the corpus is regenerated and recertified.

    new POOL_* refusals on served pages        0 of 32   (the measurement above, still correct)
    served pages refusing on the CERTIFICATE   32 of 32  (the path that measurement did not consider)

The mechanism is confirmed on all 32 by what the certificates pin; the resulting PASS -> REFUSE behaviour
is confirmed by execution on 1 (`glp1-ra-mace-t2d`). The remaining 31 follow from the same pinning, but
their before/after gates were not run and that is stated rather than implied.

**Conclusion: no patch in this stack is landable without a 32-topic regeneration and recertification.**
That is a served-artefact change and needs Mahmood's signature. This applies to POOL, ARM_final, MASKING,
F4G and FREEDOM-2 alike — REGSPAN is the sole exception, because it touches only a test file and pins
nothing.
