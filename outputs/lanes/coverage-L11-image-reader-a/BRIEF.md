# Lane L11 — reader A (codex, recorded) on the open supplement images; reader B (Gemini) owed 17 Oct

Base: coverage/image-census-2026-10-15 (db9ff35e). It holds `outputs/k_gap/image_census/IMAGE_CENSUS.json` (the census),
`outputs/k_gap/registry_fill/phase4_supplements/*.json` (file names + sha256 per meta), `scripts/g1_supplement_rows.py`
(the Europe PMC supplement ZIP fetch route) and `scripts/g1_forest_reader.py` (the dual-model forest-plot reader: prompt,
schema, recorded calls via reproducible_ai.model_call_live). Logs in ./.codex_logs. Do NOT run git status or repo-wide
scans. Network: Europe PMC only, via the existing fetch route, >= 0.5 s between requests.

## Scope (from the census; D8: every meta below is CC BY, so a model may see its images)
OPEN_FOR_MODEL metas with unread SUPPLEMENT_* images: 34484209 (46 'Supplemental Figure' tif; shared by the two
corticosteroid topics), 40159279 (Nature Medicine, iv-iron: *_Fig5-9_ESM, *_Tab1-5_ESM, gif+jpg pairs), 37381009
(metformin, 14 'Supplementary Figure' jpg), 39076869 (omega3, Figure S1-S4 tif). Re-check each meta's licence with
harness.copy_licence on the acquired JATS/metadata before any model call; refuse (and record) anything not CC BY / CC0.

## Do
1. Fetch each meta's supplement with the existing route into ./.image_cache/<meta>/ (NOT committed). Verify every image's
   sha256 equals the census/phase4 record; a mismatch is recorded and that image is NOT read.
2. Dedupe by sha256 (the gif/jpg pairs and the cross-topic duplicate are one image each). TIFF -> PNG losslessly (Pillow),
   recording both sha256 values. Report distinct images n.
3. Reader A: for each distinct image, ONE recorded call through reproducible_ai.model_call_live.call(..., images=(path,))
   using g1_forest_reader's prompt and schema (reuse its builder; if a table image needs a table variant of the prompt,
   add it next to the forest prompt and say so). The prompt names the image file only; no other text from the paper.
   Records go where g1_forest_reader puts them (evidence/model_calls/forest/ or a sibling image_tables/ dir), each with
   its lane-log entry. At most 3 calls at once.
4. Output `outputs/k_gap/image_reads/READER_A.json` + `READER_A.md`: per image -> rows read (study label, measure, point,
   CI, arm counts when printed), the record id, and state READER_A_ONLY. Match rows to the meta's missing-trial labels
   in the census (`missing_trials`) by name only where the label is unambiguous; list matches as candidates, never
   admitted. Funnel n of N: distinct images -> read -> with >=1 row -> with a row naming a missing trial; trials with a
   candidate row n of the census's 11.
5. Write `outputs/k_gap/image_reads/READER_B_OWED.md`: the exact images (sha256) and prompts reader B (agy Gemini, the
   second family) must read after the 17 Oct reset. Nothing is SECONDARY_PROVISIONAL until both readers agree within the
   printed rounding.
6. Tests (synthetic, mocked runner -- plants first): sha mismatch -> not read; non-CC licence -> refused, no call; dedupe;
   READER_A_ONLY never counts as SECONDARY; tif->png keeps both hashes.

## Finish condition / artefact
LANE_REPORT.md (funnel numbers, record ids, any refusal) and lane.patch (code, tests, outputs, records; NOT the image
cache). Do not commit or push.
