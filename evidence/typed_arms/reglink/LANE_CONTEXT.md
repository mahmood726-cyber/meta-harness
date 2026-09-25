# LANE_CONTEXT — what this directory is

This directory is ONE isolated job from the meta-harness evidence lane `evid2` (typed arm observations).
It contains: this file, `BRIEF.md` (the task), `rows.json` (count-data rows of ONE registered trial, each with two arms)
and `registry_<NCT>.json` (the trial's ClinicalTrials.gov v2 record, verbatim, sha256 recorded by the lane).

**Nothing outside this directory is context.** Do not read, search, or open any file outside it -- not your home
directory, not any AGENTS.md / CLAUDE.md / index / workbook elsewhere, not the network. Write only `out.json` here.
