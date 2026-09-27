# Re-derivation of the 41 notices under the fixed P5 population check — nr's signing list

> **CORRECTED by record 41 (2026-09-25).** The per-notice statuses below were computed with a
> loader that resolved `$object` but not `$row`, so `screen_family` saw an empty registry design
> for every family and returned plausible but wrong codes. The corrected list is **34 sign-as-is,
> 5 withdraw (N09 N17 N18 N19 N29), 2 re-issue (N30 N35)**; the `BLINDING_NOT_PROVEN` verdicts
> here are withdrawn. Section "What this record does NOT establish" is also superseded: with
> `$row` resolved the pre-patch mirror reproduces all 1220 stored cells, so the served delta IS
> computable and is given in record 41.

nr's P5 patch (`harness/trial_family.py`, `population_matches`) replaces a literal substring test
with one that folds both sides, honours a trailing `*` as a prefix, and reads a MeSH inverted
condition `X, Y` as `Y X`. This re-derives every departing membership in the 41 notices through
the **real** `screen_family()`, not a reimplementation of it.

## The probe, and the control that makes it readable

`F:/claude-temp/rederive_p5.py` loads each topic's held families from
`cache/<slug>/families.evidence.json.gz` (object-interned; expanded with
`harness.family_compact.expand`), then calls `trial_family.screen_family(family, config)` twice —
once with the pre-patch substring matcher restored, once with the patched one.

    CONTROL  pre-fix pass reproduces the recorded absence_code
             on the 29 ENTRY_POPULATION memberships : 29 of 29

That control matters because the first run of this probe returned **0 of 29**. The cell key is
`absence_code`, not `code`; reading the wrong key made every membership look unresolved. A probe
that cannot reproduce what the notices recorded is not measuring the notices, and the first run's
output was discarded rather than reported.

## Result — 6 of 78 departing memberships move, touching 6 of 41 notices

    departing memberships examined : 78
    unchanged                      : 72
    changed                        :  6

    per recorded code
      ENTRY_POPULATION_NOT_ESTABLISHED   29   23 unchanged, 6 changed
      INTERVENTION_CONTRAST_NOT_PROVEN   23   unchanged  (nr's D1, not this patch)
      REGISTRY_PARENT_UNRESOLVED         20   unchanged  (addressed by neither fix)
      INSUFFICIENT_PICD_EVIDENCE          5   unchanged
      (none)                              1   unchanged

Every moved membership is one of the two classes nr predicted, and nothing else moved:

| notice | trial | family | registry condition | before → after |
|---|---|---|---|---|
| N17/N18/N19 | PMID 30418475 | NCT01897532 | `Diabetes Mellitus, Type 2` | ENTRY_POPULATION_NOT_ESTABLISHED → **BLINDING_NOT_PROVEN** |
| N35 | PMID 26378978 | NCT01131676 | `Diabetes Mellitus, Type 2` | ENTRY_POPULATION_NOT_ESTABLISHED → **INTERVENTION_CONTRAST_NOT_PROVEN** |
| N30 | PMID 39529939 | NCT05607056 | `Antibiotic-associated Diarrhea` | ENTRY_POPULATION_NOT_ESTABLISHED → **INTERVENTION_CONTRAST_NOT_PROVEN** |
| N29 | PMID 35727573 | NCT03334604 | `Antibiotic-associated Diarrhea` | ENTRY_POPULATION_NOT_ESTABLISHED → **ELIGIBLE** |

The first four rows are the MeSH inversion (`type 2 diabetes` vs `Diabetes Mellitus, Type 2`); the
last two are the protocol truncation `antibiotic-associated diarr*`.

**The negative control holds.** N09 (DELIVER, NCT03030235) keeps
`ENTRY_POPULATION_NOT_ESTABLISHED`: `Chronic Heart Failure With Preserved Systolic Function`
against `preserved ejection fraction` shares no vocabulary, and no folding rule invents the
equivalence. That is nr's D3 and it is a protocol question for Mahmood, not a code defect. The fix
does not paper over it.

## Status per notice, for the signing list

    SIGN AS IS                 35
    RE-ISSUE, CORRECTED GROUND  5   N17 N18 N19 N30 N35
    WITHDRAW                    1   N29

Only N29 changes whether a trial is refused at all. The other five stay refused — but on a
**different stated ground**, so they cannot be signed as written. `BLINDING_NOT_PROVEN` on
CARMELINA is worth naming when re-issuing: the trial was double-blind; the registry design row we
hold carries no `masking` value. The refusal is about our holdings, not about the trial.

N29's trial is **already pooled** (`outcome.membership.pooled` in
`docs/reviews/probiotics-aad-prevention/review.json`). So the fix reconciles a discrepancy the
conservative structural contract was raising against a membership legacy screening had retained —
which is exactly what that contract's docstring says it is for.

## What this record does NOT establish

I tried to compute the served-count delta by recomputation — the pages state
`Unresolved eligibility N of M` and a list of families `contributing without established
structural eligibility`, both derived from these cells. **That attempt failed its own control and
is not reported as a result.** Screening every held trial family with the published mirror
(`docs/harness/`, the pre-patch code the live pages were built from) reproduces the eligibility
cell stored in the held evidence only **880 of 1220**, and the live page's own numbers **7 of 32**.
Something in the screening inputs has drifted from what produced the cache — the cache was rebuilt
2026-09-25 10:44 while `topics/*.json` and `protocols/*.md` are 09-21 — and until that is
explained, any delta computed this way is a number about my probe.

So the question "does the P5 fix move a served number?" is **open**, and it is answered by the
scheduled candidate regeneration and derived diff, not by recomputation. What is known:

- one family flips to ELIGIBLE on `probiotics-aad-prevention`, which feeds the count-chain
  sentence on that page, so a move there is expected and must be listed for signature;
- the refusal-code strings are themselves served (the rendered pages carry
  `ENTRY_POPULATION_NOT_ESTABLISHED` 53×, 18× and 55× on the three affected topics), so the five
  re-coded notices are a served-text change even where no count moves.

Artefacts: `F:/claude-temp/rederive_p5.{py,json}`, `F:/claude-temp/nr_signing_status.json`,
`F:/claude-temp/screen_cells.py`, `cells_mirror.json`, `cells_live.json`.
