# LANE_CONTEXT — what this directory is

This directory is ONE isolated extraction job from the meta-harness evidence lane `evid2` (typed arm observations).
It contains: this file, `BRIEF.md` (the task), `row.json` (one served count-data row and the list of held documents),
and `doc_*` files (verbatim copies of held source documents, sha256-recorded by the lane).

**Nothing outside this directory is context.** Do not read, search, or open any file outside it — not your home
directory, not any AGENTS.md / CLAUDE.md / index / workbook elsewhere, not the network. If something you need is not
in this directory, say so in the output (`NOT_IN_PACKET`) rather than looking elsewhere.

The only file you may write is `out.json` in this directory.
