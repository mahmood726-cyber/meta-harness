# D3: "preserved systolic function" = "preserved ejection fraction" — implemented as a retrospective clarification, and a probe defect it exposed

## 1. The ruling, and how it is recorded

> **"yes same population"** — Mahmood, 2026-09-25, in answer to: *does "Chronic Heart Failure With
> Preserved Systolic Function" (the DELIVER registry condition) count as the same entry population
> as the protocol term "preserved ejection fraction"?*
>
> `how_it_reached_the_reviewer: "Dispatch chat relay, answer to a plain-language question"`

The decision was taken **after the data were seen**, so it is recorded as a
`RETROSPECTIVE_PROTOCOL_CLARIFICATION` and may never be presented as pre-specified.

**It is not added to `include.population_any`.** A term placed there is structurally
indistinguishable from the pre-registered vocabulary, and no amount of prose beside it would fix
that. Instead `topics/dapagliflozin-hfpef-hosp.json` gains a separate block:

    "population_vocabulary_clarifications": [{
      "id": "D3-preserved-systolic-function",
      "equivalent_to": "preserved ejection fraction",
      "terms": ["preserved systolic function"],
      "status": "RETROSPECTIVE_PROTOCOL_CLARIFICATION",
      "pre_specified": false,
      "decided_after_data_seen": true,
      "decided_by": "Mahmood",
      "decided_on": "2026-09-25",
      "how_it_reached_the_reviewer": "Dispatch chat relay, answer to a plain-language question",
      "raised_as": "P5/D3, notice N09",
      "families_affected": ["NCT03030235"]
    }]

`harness/trial_family.py` consults it **only after** the pre-specified vocabulary has failed, and a
family admitted this way carries `population_basis: RETROSPECTIVE_VOCABULARY_CLARIFICATION` plus
the full record in its eligibility cell — so the page can disclose it and a verifier can tell the
two kinds of match apart without reading prose.

`tests/test_population_clarification.py` (5 tests, passing) pins: the block is declared
retrospective; `population_any` has **not** absorbed the term; DELIVER is admitted and its cell says
the basis was retrospective; **removing the block restores `ENTRY_POPULATION_NOT_ESTABLISHED`** (so
the clarification is demonstrably what admits DELIVER, not some other drift); an unrelated
population is still refused; and a population on `population_none` stays **excluded** even when the
clarification matches one of its other conditions — a clarification must not become a loosening.

**Scope was measured, not assumed.** Across all 32 topics, exactly **one** family's registry
conditions mention "systolic function": NCT03030235. No other trial is touched.

## 2. A probe defect this exposed — mine, not the harness's

Implementing D3 made DELIVER return `BLINDING_NOT_PROVEN`, which was wrong: DELIVER was
double-blind. The cause was in my probe.

`families.evidence.json.gz` carries **two** kinds of reference. `family_compact.expand()` resolves
`{"$object": n}`. It does **not** resolve `{"$row": n}`, which points into the sibling
`family_registry.json` rows — and `registry_design.masking`, `.allocation` and
`.intervention_model` all sit behind a `$row`.

A caller that only expands hands `screen_family` a design of `{"$row": 489}`. That dict is
**truthy**, so it sails past the `if not design` guard, and then every design test reads `None`.
The output is a complete set of plausible, wrong absence codes, with no error anywhere.

Measured against the cells stored in the held evidence, using the pre-patch published mirror:

    $row NOT resolved :   880 of 1220
    $row resolved     : 1220 of 1220

**The harness was never wrong here.** `harness/family_compact.read_families()` already existed and
already did this correctly — expand, then `materialize()` against the registry rows, then restore
lifecycle order. My error was writing a loader instead of looking for the one the build uses. I
briefly compounded it by "fixing" the harness: I added a second `read_families` to the same module,
which Python simply overrode with the existing definition below it, so my addition was dead code
that never ran and the passing test was calling the real loader all along. That addition has been
removed; `harness/family_compact.py` is unmodified.

**Record 39's caveat is withdrawn.** Its conclusion — that the delta could not be computed by
recomputation — was correct at the time but for the wrong reason: the cause was my loader, not
drift between the cache and the configs. Loaded through `read_families`, the pre-patch mirror
reproduces **every one** of the 1220 stored eligibility cells, so the "before" is provably the
served state and the delta is trustworthy.

The lesson worth keeping is not about `$row`. It is that an unresolved reference was **truthy**,
so the guard written to catch a missing design passed it through. A guard that tests presence
rather than shape cannot distinguish "absent" from "not yet resolved".

## 3. Corrected signing list — 41 notices

Record 39 reported 1 withdrawal and 5 re-issues. That was computed with the broken loader. The
corrected result, from dumps whose BEFORE is anchored 1220 of 1220:

    SIGN AS IS  34
    WITHDRAW     5   N09 N17 N18 N19 N29
    REISSUE      2   N30 N35

| notice | trial | before → after |
|---|---|---|
| N09 | PMID 34711976 (DELIVER) | ENTRY_POPULATION_NOT_ESTABLISHED → **ELIGIBLE** — *retrospective D3* |
| N17 / N18 / N19 | PMID 30418475 (CARMELINA) | ENTRY_POPULATION_NOT_ESTABLISHED → **ELIGIBLE** |
| N29 | PMID 35727573 | ENTRY_POPULATION_NOT_ESTABLISHED → **ELIGIBLE** |
| N30 | PMID 39529939 | → INTERVENTION_CONTRAST_NOT_PROVEN (still refused, new ground) |
| N35 | PMID 26378978 | → INTERVENTION_CONTRAST_NOT_PROVEN (still refused, new ground) |

The earlier `BLINDING_NOT_PROVEN` verdicts on N17/N18/N19 were the loader artefact and are
withdrawn.

**Denominator closed.** 78 departing memberships = 58 screened + 20 that are not trial families.
Those 20 carry `REGISTRY_PARENT_UNRESOLVED`, which is set outside `screen_family` and is touched by
neither patch — checked, not assumed, so they are correctly SIGN_AS_IS rather than unexamined.

## 4. Served-number consequence of D3 — a new result-change notice

DELIVER is **already pooled** for the served Adverse events outcome (k=1), and the primary outcome
serves no pool (k=None). So no effect estimate moves. What moves is the count chain, which the page
states verbatim:

| served text, `docs/reviews/dapagliflozin-hfpef-hosp/` | before | after |
|---|---|---|
| `Unresolved eligibility N of 22.` | **12** of 22 | **11** of 22 |
| `Contributing without established structural eligibility: …` | `NCT03030235.` | *(list becomes empty — DELIVER was its only entry)* |
| eligible families | 3 | 4 |

This is a served-number change and belongs on Mahmood's signing list with the others, labelled as
arising from a **retrospective** clarification.

For completeness, the P5 fix moves four further topics' count chains (the same anchored dumps):

    dpp4-mace-t2d                eligible 5 -> 7    unresolved 31 -> 29  of 37
    probiotics-aad-prevention    eligible 0 -> 10   unresolved 59 -> 48  of 61
    sglt2-primary-prevention-hf  eligible 6 -> 7    unresolved 80 -> 79  of 95
    tranexamic-acid-pph          eligible 5 -> 5    unresolved 31 -> 30  of 39

57 of 1220 cells move in total; every one of them is currently refused for population and none is
newly refused.

Artefacts: `F:/claude-temp/{held.py, cells_dump.py, cells_before.json, cells_after.json,
nr_signing_list.py, nr_signing_status.json}`.
