# Source verification of run r2's new automated includes (2026-09-15) -- Codex lanes, adjudicated mechanically; nothing pooled

**Fix state (orthogonal fields rule): LANDED / NONE / CORPUS / CURRENT** - generated from MEASURE-search-v2-recall-2026-09-15

Why: run r2 raised the candidate pool ~60x and the automated screen marked ~3,200 records `include` across 32 topics
(`11-before-after-32-r2.txt`). The handover rule is that every newly retrieved trial is source-verified before it pools.
One Codex lane (gpt-5.5, fresh sparse clone at f62eec27) per topic read each NEW include (r2 include not among the
legacy includes, the pooled trials or the declared-absent trials of the served review) against the protocol PICO and
gave a verdict with a verbatim quote; four remainder lanes verified the rows the first lanes capped at 150; a second,
blind lane (X) re-read every row a first lane called ELIGIBLE_RCT with four quoted facts each. The integrator never read
the lanes' prose: `scripts/verification_adjudicate.py` checks each JSON against the brief's finish condition and
RE-DERIVES N from the committed artefacts.

## Measured (01-adjudication.txt)
MEASUREMENT totals: 21 of 21 topics harvested, 6 of 21 clean; NEW 1998; ELIGIBLE_RCT 27 of 1998; ELIGIBLE_RCT_NO_PRIMARY 397; NOT_RCT 489; WRONG_* 288; DUPLICATE 255; UNDECIDABLE 53; NOT_VERIFIED_CAP 0; REGISTRY_ONLY 482; automated screen agreed 424 of 1998

DEVELOPMENT totals: 11 of 11 topics harvested, 6 of 11 clean; NEW 1162; ELIGIBLE_RCT 25 of 1162; ELIGIBLE_RCT_NO_PRIMARY 139; NOT_RCT 104; WRONG_* 104; DUPLICATE 128; UNDECIDABLE 1; NOT_VERIFIED_CAP 509; REGISTRY_ONLY 150; automated screen agreed 164 of 1162

Named limits: 15 of 32 lanes under-counted N by omitting registry-only (NCT, no PMID) includes -- counted here as
REGISTRY_ONLY, unverified; six lanes still differ from the re-derived N by 2-6 rows beyond that (listed per topic,
unexplained). DEVELOPMENT topics were capped at 150 per lane and NOT given remainder lanes (509 NOT_VERIFIED_CAP); the
capability number is the MEASUREMENT split. Verdicts are one model's reading of an abstract against a protocol; the
second opinion below measures how stable that reading is.

## Second opinion (02-second-opinion.md / .json)
X VERDICT: of 39 first-lane ELIGIBLE_RCT rows, second opinion ELIGIBLE_RCT 19, ELIGIBLE_RCT_NO_PRIMARY 18, other 2 (WRONG_POPULATION: 2)
Per verdict: {'ELIGIBLE_RCT': 19, 'ELIGIBLE_RCT_NO_PRIMARY': 18, 'WRONG_POPULATION': 2}. Of the rows one lane called poolable, a blind second lane upheld roughly half; the rest
mostly lacked the protocol's PRIMARY outcome in the abstract. A pool move needs the full text, not the abstract.

## What this settles and what it does not
It settles the size of the decision: on the 21 sealed topics the r2 corpus offers a few dozen candidate trials worth a
full-text read, not two thousand. It does not move any pool; `search_v2.pin()` was never called. The next step, if
taken, is a full-text verification of the ELIGIBLE_RCT rows upheld by both lanes -- Mahmood's call.
