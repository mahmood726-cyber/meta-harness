# Trial-family storage

`family_registry.json` is an `aact-row-references-v1` manifest. Its `rows` and
`payload` fields name sibling deterministic gzip JSON files. The row catalogue
contains `{table, nct_id, row_key, row_sha256, snapshot, inline}` objects. The
snapshot identifier is `2026-08-30`; it is a folder identifier, not an independently
verified historical cutoff date. Surrogate row IDs are scoped to that snapshot.

Row hashes are SHA-256 of UTF-8 JSON with sorted keys, no insignificant whitespace,
and unescaped Unicode. All original columns participate. A row key is its `id`
when present, otherwise `nct_id`; ambiguity is refused. Registry evidence uses
`{"$row": index}` references into the catalogue instead of repeated verbatim rows.
Repeated JSON evidence is interned through `{"$object": index}` references.

`harness.family_compact.read_registry` expands the operational inline projection
without opening AACT. That projection supports the existing identity, eligibility,
and outcome annotation rules; it is not a newly validated source snapshot.
`read_families` expands the family evidence using the same catalogue. The ordinary
`families.json` keeps every value displayed by the family table inline; its evidence
is in `families.evidence.json.gz`. Gzip uses `mtime=0` for reproducible bytes.

Run `python scripts/build_families.py <slug>` to rebuild the full original registry
from local AACT through `harness.aact`. The command verifies every referenced row's
hash and inline projection before writing `.tmp/<slug>/family_registry.full.json`.
It refuses missing tables/rows, altered hashes or source values, ambiguous row keys,
and wrong snapshots with `NOT PRESERVED`. It performs no network retrieval and does
not overwrite the compact objects. `--snapshot` can select the exact local snapshot
folder; `--output` selects the full-registry output path.

`python scripts/verify_family_preservation.py --compare-dir <FN-worktree>` validates
the cohort in one pass per AACT table and compares reconstructed registries against
FN's originals. `python scripts/trial_family_sweep.py` replays the compact inputs,
checks membership and numeric results against this worktree's HEAD pipeline, and
keeps newly written family objects compact. The registry acquisition script also
writes the compact representation. `scripts/compact_families.py` migrates full FN
objects once and refuses already compact inputs.

Size accounting includes all `cache/<slug>/famil*` files, including gzip sidecars,
query, and discovery objects. Full regeneration outputs in `.tmp` are intentionally
outside the compact artifact set. No evidence rows are truncated to meet the limit.
