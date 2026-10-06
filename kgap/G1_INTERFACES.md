# G1 shared machinery on `acq/k-gap`: interfaces for the topic lanes

Owner: the acq/k-gap lane. Lanes building on it: NOAC (Evidence binding), tocilizumab (Evidence two), the recorded
forest-plot reader (Reproducible AI). These contracts are pinned by `tests/test_g1_interfaces.py`. Keys may be **added**.
Renaming or removing a state, route, key or parameter is an announced interface change, never a side effect.

## 1. Source hierarchy and verification routes (`harness/secondary_meta.py`)

States: `SECONDARY_UNVERIFIED`, `PRIMARY_VERIFIED`, `TWO_SOURCE_VERIFIED`, `MISMATCH`, `BLOCKED_CROSSCHECK`, `REFUSED`.

Primary sources (decision 2 Oct):
- **a.** posted CT.gov results from a versioned AACT snapshot;
- **b.** open full text (PMC / Europe PMC / Unpaywall).

Secondary sources (**c.**) are rows printed by a meta. A meta's rows are used only if they reproduce its own pooled
result (`positive_control`).

`row.verification["route"]` on a verified row names the route:

| route | how |
|---|---|
| `PRIMARY_TEXT` | `verify_typed`: the meta's exact printed numbers found by regex in a held primary text, with the measure word and the outcome nearby |
| `PRIMARY_REGISTRY` | `verify_typed` / `typed_match_registry`: found in posted results (also carries `registry_fields` and `registry_vs_publication`) |
| `PRIMARY_EXTRACTION` | `verify_against_primary`: equal to our own extraction of the trial's report |
| `TWO_SOURCE` | `two_source`: two **independent** metas print the same typed tuple (state `TWO_SOURCE_VERIFIED`) |

`route_of(row)` collapses these for reporting: `PRIMARY` / `TWO_SOURCE` / `UNVERIFIED`.

**Registry differences.** `registry_vs_publication` lists differences in timepoint length and analysis-population class
(SAFETY / PER_PROTOCOL / MITT / ITT). It records them and never reconciles them, and never changes the verdict.

**Independence** (`independence(a, b, refs_of, known_metas)`) is fail-closed. Two metas are NOT independent when:
- they are the same meta;
- they are the same bytes;
- the citation set is unknown (no JATS reference list);
- one cites the other;
- both cite a meta of this topic.

`refs_of(meta_pmid)` returns a set of cited PMIDs/DOIs, or `None`. The build's `refs_of` reads the meta's held JATS
(`cited_ids_from_jats`).

**Anti-circularity.** `g1_countable(rows, {comparator})` never counts a row sourced from the comparator. A two-source
row counts against comparator X only if an independent pair **without X** supports it.

**Queue invariant.** `queue_complete(rows)` must be empty: every unverified row carries a typed `queue_reason`.

## 2. AACT snapshot adapter (`kgap/aact_adapter.py`)

```python
from kgap import aact_adapter
aact_adapter.ensure(["NCT..."])      # index missing NCTs: one streaming pass; {"added","rebuilt_stale","held","snapshot"}
aact_adapter.registry_for("NCT...")  # {"_snapshot","outcomes","analyses","groups","group_titles"} or None
aact_adapter.snapshot()              # {"id","digest","files"}; digest cached in outputs/k_gap/aact_snapshot_digest.json
```

- **Snapshot:** `$AACT_SNAPSHOT` (default `F:/AACT-storage/AACT/2026-08-30`). A missing snapshot raises; it is never
  an empty registry.
- **Index:** `$KGAP_AACT_INDEX` (default `outputs/k_gap/_aact_results.json`, gitignored). Lanes on this PC can point
  `KGAP_AACT_INDEX` at one shared file to skip the ~13-minute first pass.
- **Snapshot mixing:** entries from a different snapshot digest are rebuilt, never mixed.
- **Counts:** `groups[outcome_id]` = `[{group, count, n}]` takes only uncategorised COUNT/NUMBER measurements paired
  with the "measure" N. A Kaplan–Meier percentage is not a count.

## 3. Run ledger (`kgap/runs_store.py`)

- **Layout:** recorded model calls of the secondary tier, one file per topic: `registry/secondary_meta/runs/<slug>.json`.
- **Keys:** `"<slug>::<meta_pmid>"` (forest read) and `"locate::<slug>::<pmid>"` (locator).
- **API:** `load()` merges all topics. `save(runs, slugs={...})` writes only those topics, so lanes never conflict on the
  ledger.
- **Retired:** the single `runs.json` was migrated losslessly (85 keys) and removed.

## 4. Tracker (`scripts/g1_tracker.py`)

```
python scripts/g1_tracker.py <your-slug>    # writes outputs/k_gap/g1/<your-slug>.json (commit only your topic's file)
python scripts/g1_tracker.py --table        # regenerates outputs/k_gap/G1_TRACKER.md from all g1/*.json
```

**Schema** (`schema_version` 1):
- `N_comparator_trials`, `k_matched`, `k_ours_total`;
- `routes`: PRIMARY / TWO_SOURCE / SECONDARY_SINGLE / UNVERIFIED / NO_ROW, summing to N (SECONDARY_SINGLE: a
  non-comparator meta row, Mahmood decision 3 Oct; g1_tracker.is_matched already counts it);
- `trials[]`, each with `route`, `basis` and `agreement_with_comparator_row`;
- `per_trial_agreement`;
- `same_trials`: ours vs the comparator's rows pooled on exactly the shared trials, by the method the comparator's
  positive control reproduced;
- `ours`, `comparator`, `ours_not_in_comparator`.

`G1_TRACKER.md` is generated. On a merge conflict, run `--table` rather than hand-merging it.

## 5. Build (`scripts/secondary_meta_build.py SLUG [--run]`)

Order per topic:
1. typed tables;
2. recorded figure reads (the forest-plot lane owns the reader: `k_gap_forest_plot.gate`, `model_call_live.call(images=...)`);
3. admit / consolidate / cross-check;
4. **deterministic** `verify_typed` over every held primary text and the registry;
5. our extraction and the recorded locator;
6. `two_source`;
7. the queue invariant.

Writes `registry/secondary_meta/<slug>.json`, which also carries `"registry": {state, snapshot}`. If the snapshot was
unavailable it records `SNAPSHOT_UNAVAILABLE`. It is never a silent empty registry.

## 6. Changes since first publication (additive except where marked)

**Typed tuples and independence**
- `two_source` requires the **same typed tuple** (`same_tuple`). That means the same value, and no *stated* difference
  in timepoint length, population class or arm dose. Unstated on one side is not a difference.
- `independence` treats the same PMID **or the same DOI** as `SAME_META`.
- `known_metas` may be alias groups (`[{pmid, doi}, ...]`); the build passes `meta_aliases(pmid)`. A meta cited by PMID
  in one reference list and by DOI in another is one meta.
- `verification["independent_pair_ids"]` carries every id of both metas. `g1_countable` removes the comparator by any
  id, case-insensitively.

**Registry matching**
- `typed_match_registry` needs two **distinct** result groups for the two arms, and ignores `None` counts.
- `_days` reads fractional lengths ("0.5 years").

**Pooling and typed tables**
- `row_yi_vi` refuses reversed, zero-width or point-outside-CI rows.
- **Arm-level MD rows:** `SecondaryRow` gains `mean_t, sd_t, mean_c, sd_c, findings`. A RevMan-style table's mean (SD)
  and N per arm are read when the header names the control column, and the MD is pooled **from the arms**.
  `arm_ci_discrepancy` records a printed CI that contradicts the row's own arms as a `ROW_CI_NOT_FROM_ARMS` finding.
- Count tables take arm order from the header. An unknown order is recorded as `ARM_ORDER_FROM_COLUMN_ORDER`.
- Table cells fold U+2212 and other typographic dashes to ASCII.
- **Table outcome identity by the meta's own words:** `pooled_sentence` finds the sentence that prints the table's
  pooled row and names a registered outcome term. The term must end within 60 characters before the numbers, with no
  clause break between them. The build records `identity_basis` (`CAPTION` or `POOLED_SENTENCE: ...`) and `pooled` on
  the meta.

**AACT adapter** (`INDEX_RULES = 2`; entries built under older rules are rebuilt)
- An arm count is an **integral** value in **people** units (participants / subjects / patients). Its N is a "measure"
  count in people units. A percentage, proportion, rate, eyes, or patient-months is never a count or an N.
- The tag is `{id, digest, rules}`.
- The digest cache is keyed by a hash of the snapshot directory (`dir_sha256`), never a local path.

**Run ledger**
- `save()` **merges** with what is on disk: a stale caller cannot delete entries saved in between. Writes are atomic.
- The build saves the ledger even when a topic's build raises.

**Tracker**
- It compares against the comparator's own printed row **whatever its admission state**.
- It records `our_refusal`, `comparator_row`, `comparator_row_findings` and `comparator_basis`.
- If the served review typed no comparator result, it uses the comparator's typed, positive-controlled table pooled row.

**Refuted review finding:** "agreement should use the comparator's printed precision." When a trial prints 0.8, a
comparator's 0.84 is consistent with it. Agreement is judged at the coarser printed precision on purpose.
