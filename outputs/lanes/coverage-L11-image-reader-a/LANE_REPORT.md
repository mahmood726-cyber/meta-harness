# L11 lane report ? blocked at recorded Reader A

The source acquisition and reader implementation are complete. The requested live image readings are **not complete**: `codex login status` returned exit code 1, `Not logged in`. See `outputs/k_gap/image_reads/CLI_PREFLIGHT.json`. No commit or push was made.

## Source and image funnel

- 4 Europe PMC metadata/JATS/supplement packages acquired through the existing supplementaryFiles route; requests spaced at least 0.5 seconds, bounded retries.
- 130 topic-image entries; 84 distinct source-byte SHA256 values; 74 distinct images after exact-hash deduplication and selecting one JPEG per named GIF/JPEG pair. The pairs have different hashes; their hashes are retained separately, not falsely declared byte-identical.
- All source hashes match both the census and phase4 records. Hash refusals: 0. Licence refusals: 0.
- 50 TIFF files converted losslessly to PNG, with source and attached hashes retained and pixel equality checked.
- All four source PMID/PMCID pairs match their acquired JATS article identifiers.
- Distinct images ? successful reads: **0 of 74**.
- Successful reads ? images with ?1 row: **0 of 0**.
- Images with rows ? images naming a missing trial: **0 of 0**.
- Census trials with a candidate row: **0 of 11**.
- SECONDARY / SECONDARY_PROVISIONAL admissions: **0**.

## Calls and refusals

Completed record IDs: **none**. Completed lane-log entries: **0**. Three initial CLI launches were interrupted after the local authentication check failed; their exact image hashes are in `INTERRUPTED_ATTEMPTS.json`. They did not return completed records or model responses and are not counted as reads. All 74 images now have AUTH_REQUIRED state. The runner now checks authentication before launching any batch. No placeholder response, row, record ID or successful read was fabricated.

The 34484209 JATS grants CC BY in words but omits a licence URL. `harness.copy_licence.classify_permissions` alone returns NOT_OPEN for that shape. The lane uses the acquired Europe PMC metadata's `cc by` value through `harness.copy_licence.upw_open`, requires a Creative Commons grant in the JATS, and rejects restriction terms. The other three JATS pass the existing classifier directly. The metadata/JATS hashes and terms are recorded in READER_A.json.

## Implementation and handoff

`python scripts/lane_image_reader.py --run` resumes acquisition checks and Reader A after the local Codex CLI is authenticated. It reuses g1_forest_reader's builder and schema, passes only the image filename (no paper text), records through model_call_live.call, caps concurrent calls at three, and checkpoints outputs. Successful results stay READER_A_ONLY. Exact normalized-name matches can become candidates only; no author/title or trial-identifier inference is used.

A table-image addendum sits next to the forest prompt in `scripts/g1_forest_reader.py`. It permits explicitly printed study-row effects, CIs and arm counts, with null for unprinted fields and no calculation.

`outputs/k_gap/image_reads/READER_B_OWED.md` lists all 74 images, original and attached hashes, alternate renditions, and exact Gemini prompts for after the 17 October reset. Reader B must independently read the images. Nothing becomes SECONDARY_PROVISIONAL without both readings agreeing within printed rounding; further existing admission gates remain applicable.

## Verification

- Initial plants failed on the absent implementation module as intended.
- Final focused command: `python -m pytest -q tests/test_lane_image_reader.py` ? **8 passed**.
- Broader command: `python -m pytest -q tests/test_lane_image_reader.py tests/test_g1_forest_reader.py tests/test_copy_licence.py tests/test_copy_licence_d8.py` ? **71 passed, 4 xfailed, 2 failed** (before the eighth preflight test was added). Both failures concern absent pre-existing cache/JATS fixtures outside this lane; details in STUCK_FAILURES.md.
- Source/attachment hashes, identifier pairs, empty-record honesty and funnel arithmetic independently checked; evidence in `VALIDATION.json`.
- Image cache excluded from lane.patch. The patch includes code, tests, outputs and this report; there are no completed model records to include.

| Surface | Static configuration | Dynamic evidence |
|---|---|---|
| Scope | Four PMID values from LANE_PROMPT; three-call cap | Census and phase4 file lists/hashes |
| Licence gate | Existing copy_licence rules and narrow metadata fallback | Acquired metadata and JATS |
| Transcription | Existing schema/prompt plus table addendum | None yet: authentication blocked |
| Funnel | Counting logic; no admission path | Output states and census missing-trial labels |
