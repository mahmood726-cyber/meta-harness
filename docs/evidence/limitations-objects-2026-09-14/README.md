# Limitations as structured objects (2026-09-14)

**Fix state (five-state rule): LANDED** - object layer and byte-identical comparison; page rendering not yet switched (stages 3-7 outstanding).

Stage reached: object layer plus legacy byte/text comparison. The served review-page blocks remain rendered by page.py; review.json now carries structured limitations.

Integration note (session author, 2026-09-14): the lane built 21 emitters (452 objects on the 32 pages at a3872489). On the merged base (after 3aedba0e restored the Search provenance block) a 22nd kind, SEARCH_PROVENANCE, was added by the integrator (severity BLOCKS_CLAIM, evidence_state RETRACTED, rendered by page._search_provenance_html) and the two tables were regenerated from the tree by `python scripts/limitations_sweep.py`: 32 topics, 484 objects, 0 topics with unmatched blocks.

Captures:
- 01-object-counts-32.txt: object counts and enum breakdowns for all 32 review objects.
- 02-legacy-compare-32.txt: legacy absent/banner block comparison; all rows are n/n/n/0.
- 03-refusal-plants.txt: planted refusals for removed id, softened severity, softened evidence_state, and text drift.
- 04-free-text-objects.txt: named high-risk free-text objects from _absent_block reasons, declared strands, and definition audit.
