You are a read-only engineer on the meta-harness project (living meta-analyses; pages at
https://mahmood726-cyber.github.io/meta-harness/). Your working directory is a READ-ONLY extract. Do not write files. Do
not use the network.

## Folder
- `harness/` -- the code that builds and renders reviews (page.py renders the page; limitations.py builds limitation
  objects; claim.py the canonical claim; pipeline.py computes results; comparator_panel.py etc.).
- `reviews/<slug>/review.json` -- the committed review object; `reviews/<slug>/index.html` -- the served page.
- `registry/`, `docs_result_changes.json` -- committed registry files.
- `HANDOVER.md` -- the list of open defects (H1-H19, A1). Your items are named below.

## Your items
H6, H7, H8, H9

## For EACH item, establish
1. ROOT CAUSE: the exact function and line(s) in harness/ that produce the wrong text (quote the code).
2. CLASS: does a correct fix change ONLY the rendered HTML (the review.json `outcomes`, `result`, `trials`, `claim`,
   `comparator*`, `limitations` objects and every registry file stay byte-identical) -> **PRESENTATION**; or does it
   change any field of review.json other than reproduction/certificate code identity, or any registry/result_changes
   record, or a served number -> **SERVED**. Prove it: name the field the fix would or would not touch. If the wrong text
   is stored inside review.json (e.g. a limitation's rendered_text, a comparator panel string), the fix changes
   review.json -> SERVED, even if it is only wording.
3. FIX: the minimal correct change (code), and a PLANT: a test input that FAILS on the current code and passes after.
4. Whether the defect is real at all: if the item is wrong, say so with evidence.

## Output
Your FINAL message is ONE JSON object matching the schema. Quote code and data EXACTLY (they are machine-checked
against the files). Be precise and brief.
