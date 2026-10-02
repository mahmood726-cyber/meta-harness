# 44 — The 13 countersignatures on signing packet v2, and what they changed

2026-09-29. Recorded by the release captain, in a clean clone at `origin/main` `91f057a4`.

## What the reader should take from this record first

**These 13 notices were already countersigned.** Every one of them carried a
`reviewer_countersignature` dated 2026-09-21, in the same 5 batch / 8 individual split. This landing
did **not** add 13 signatures to unsigned notices. It replaced the **basis** of 13 existing
signatures with a stronger and more accurate one, and re-dated them.

That distinction is the whole content of this record, because the flattering summary — "13 result
changes signed by the reviewer" — was already true on 21 September, and repeating it here would hide
the only thing that actually moved.

## What the old basis said, in its own words

> relayed by the orchestrating lane, 2026-09-21; for each notice the figures, the departing trial(s)
> and the stated reason were conveyed in full, and the shared mechanism sentence was quoted verbatim;
> **the full rendered block was offered and not read letter-for-letter** for the seven first-shown
> notices

The old basis was honest about its own limit, and that limit is what packet v2 was built to close:
the reviewer had been told what each notice said, but had not been shown the bytes his signature
names. A signature names `rendered_sha256` of the rendered block. A reviewer who was given an
accurate summary of a block has not seen the block.

## What happened this time, in order

1. The release captain rendered all 13 notice blocks to visible text (HTML stripped) and published
   them in `outputs/SIGNING_PACKET_V2_2026-09-29.md`, each headed by its **full** `rendered_sha256`.
   Packet sha256 `daea634e11d274159ba7607f7d5385b4498628bd1edf48f2056b466cb34073fc`.
2. The packet passed `packet_guard.py` at base `91f057a4`: for all 13, a notice with that slug and
   outcome exists in `docs/result_changes.json` at that commit, its `rendered_sha256` recomputed by
   the harness's own renderer equals the hash printed beside the block, and the batch/individual
   split matches the tool's own `conclusion_changed` annotation rather than the captain's opinion.
3. Dispatch relayed the packet with all 13 blocks verbatim. The reviewer replied:
   **"I am happy to sign all"**.
4. Dispatch then sent an itemised signature list: one BATCH line covering MAIN-03, 06, 07, 09, 12,
   and eight individual NOTICE lines for MAIN-01, 02, 04, 05, 08, 10, 11, 13, each carrying its own
   `rendered_sha256` prefix, dated 29/09/26. The reviewer replied:
   **"I am can't cut and paste. I agree with above"**.
5. Dispatch asked him to name each. The reviewer replied: **"yes I sign"**.

**He did not type the per-notice signature lines.** He was on a phone and could not copy or paste.
The lines were recorded on his behalf by relay, on exactly the basis quoted above, and the basis
field of all 13 records says so in those words. There is no state in this harness for "agreed in
advance", and there is likewise no state for "typed it himself" — so the only defence against a
relayed signature being mistaken for a typed one is that the record says which it was.

## What was checked before anything was written

- the packet file present in the signing clone hashes to `daea634e…`, the digest the reviewer was
  shown — not merely a file with the same name;
- each notice's `rendered_sha256`, recomputed in the clean clone, equals the hash printed beside
  that block in the packet. **Drift on any one of them and that notice stays OPEN** — unsigned, not
  forced. Drift: **0 of 13**;
- the batch/individual split was taken from `countersign_result_change.py`'s own annotation. The
  tool refuses `--batch` on a notice that withdraws a conclusion, and it was allowed to refuse. It
  did not refuse any of the five presented as batchable.

After regeneration the 13 rendered hashes were recomputed once more and still match: the rendered
block excludes the countersignature paragraph by construction, so recording a signature cannot move
the hash that signature names.

## MAIN-14 is absent, and is meant to be

The spironolactone / all-cause-mortality correction (J-EMPHASIS bound to its composite endpoint) was
listed in packet **v1** and had **no derived notice** in `docs/result_changes.json` — its "notice
sha256" was computed over a record the packet generator had built by hand. It was withdrawn from
the packet rather than signed. `packet_guard.py` was planted with exactly this case and refuses any
packet that presents it: `GUARD REFUSED — MAIN-14 … NO DERIVED NOTICE at 91f057a4`, exit 1.

## What moved in the served bytes

Ten topics were regenerated: colchicine-postop-af, colchicine-recurrent-pericarditis, dpp4-mace-t2d,
esketamine-trd-madrs, noac-vs-warfarin-af-stroke, omega3-cardiovascular-events, pcsk9-mace,
probiotics-aad-prevention, tocilizumab-covid19-mortality, tranexamic-acid-pph.

A leaf-by-leaf comparison of every changed JSON against `origin/main` — not a reading of the diff —
classified each differing value by its key path:

| class | leaves |
|---|---|
| signature and digest fields (`when_utc`, `how_it_reached_the_reviewer`, `batch_id`, `rendered_sha256`, `html_sha256`) | 203 |
| `EXECUTION_RECORD.json` `tree.*` — which paths were dirty at build time | 2240 |
| `EXECUTION_RECORD.json` `command.cwd` | 10 |
| `registry/blind_map.json` — last-topic-built scratch | 9 |
| **anything else** | **0** |

**No pooled estimate, interval, k, τ², or trial list moved.** The `tree.*` bulk is the build
provenance changing because these pages were last generated in a dirty lane worktree
(`C:\mh-lanes\evid2-v101`, branch `evid2/v101-population`, 240 dirty paths) and are now generated in
a clean clone of `main`. That is the record becoming more honest about where it ran, not a result
changing.

The rebuild passes `--now 2026-09-11` explicitly, matching the argv recorded on `main`. The flag's
value is also `build_topic.py`'s hardcoded default, so replay is unaffected either way — but an
outsider replaying from the record should see the command that was run, not a shorter one that
happens to behave the same.
