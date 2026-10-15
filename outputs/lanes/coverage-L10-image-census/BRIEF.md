# Lane L10 — census of image-only per-trial data in meta supplements (deterministic, BEFORE any model read)

Base: origin/kgap/g1-explained @ b28fcf25996852823f9348a073bfdff3921f61d3 (the acquisition lane's branch; read its outputs, change none of them).
Inputs: outputs/k_gap/registry_fill/phase4_supplements/<slug>.json (each: metas{pmid: {licence, files[{file, format,
skipped, sha256, bytes}]}}, attempts[{trial, meta, file, reasons}]) and outputs/k_gap/G1_FOREST_READER.md (figures the
dual-model forest reader ALREADY read: topic, meta PMID, figure label). No network. Logs in ./.codex_logs. Do NOT run
git status or repo-wide scans.

The captain's note says "fifteen metas ship image files". The records say otherwise: 276 metas carry 3,008 image files
(skipped 'image (no OCR)'). Most are probably the ARTICLE's own figures bundled in the Europe PMC supplement ZIP, which the
forest reader already read. Build the census that separates them, as n of N at every step.

## Build scripts/g1_image_census.py (+ tests/test_g1_image_census.py on synthetic records)
For every (topic, meta) with image files:
1. classify each image file by its NAME, with the rule written as a table in the module and every pattern planted:
   ARTICLE_FIGURE (e.g. '*_Fig1_HTML.*', 'pone.*.g00N', 'CD*-fig-*', 'jcm-*-f00N', '*-F2', 'fig1', 'f0015', 'Fig2'),
   SUPPLEMENT_TABLE_IMAGE (e.g. '*_Tab4_ESM.*', 'Table S2', 'eTable', '*-T1-*' only when an ESM/supplement marker is
   present), SUPPLEMENT_FIGURE_IMAGE ('*_Fig8_ESM.*', 'eFigure', 'Figure S', 'mmc*', 'Data_Sheet*' pages),
   UNKNOWN_IMAGE (anything else -- listed, never guessed);
2. ALREADY_READ when the (meta, figure label) is in G1_FOREST_READER.md;
3. licence: OPEN_FOR_MODEL only for the meta's licence 'cc-by' / 'cc0' / 'cc by' / public domain; NC / ND / SA /
   other / missing -> DETERMINISTIC_ONLY (a model may not read it);
4. gap relevance: the meta appears in attempts[] with a missing trial -> list those trials.
Output outputs/k_gap/image_census/IMAGE_CENSUS.json + IMAGE_CENSUS.md with the funnel:
  metas with images -> with >=1 SUPPLEMENT_* image -> OPEN_FOR_MODEL -> citing >=1 missing trial ->
  supplement images not ALREADY_READ; and trials affected (n of the missing trials), PER TOPIC and overall.
Every count states its denominator. List UNKNOWN_IMAGE files by name (do not drop them).

## Tests (synthetic, plants FIRST): each naming class, ALREADY_READ matching, each licence branch (cc-by-nc -> not open),
a meta with no missing trial, an UNKNOWN name kept and listed, and that the funnel's counts are monotone.
Run python -m pytest -q -p no:cacheprovider tests/test_g1_image_census.py, then run the census on the real records.

## Finish condition / artefact
LANE_REPORT.md (the funnel numbers, the naming table, every UNKNOWN pattern seen with a count) and lane.patch (new
files). Do not commit or push.
