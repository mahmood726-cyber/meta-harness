# LANE W-sglt2-primary-prevention-hf — the REMAINDER: verify the new includes the first lane capped as NOT_VERIFIED_CAP for topic `sglt2-primary-prevention-hf` (evidence for the pool-moving decision; nothing is pooled)

Fresh clone of meta-harness at f62eec27 (detached). Python 3.13, network on (PubMed E-utilities, Europe PMC). Do NOT
commit. Do NOT edit anything under `harness/`, `scripts/`, `registry/`, `docs/`, `cache/`, `topics/`, `protocols/`.
NEVER stop, kill or signal any process on this machine (no Stop-Process, taskkill, kill); other lanes and the integrator share it.
You write exactly: `lane_v/sglt2-primary-prevention-hf.json`, `lane_v/sglt2-primary-prevention-hf-raw/`, and `LANE-W-sglt2-primary-prevention-hf-REPORT.md`.
The first lane's output is at `C:/meta-harness/outputs/search_v2/verification/sglt2-primary-prevention-hf/sglt2-primary-prevention-hf.json` (read-only): YOUR population is exactly its objects with verdict `NOT_VERIFIED_CAP` (N = their count; state it). Verify every one of them; there is NO cap this time. Registry-only (NCT, no PMID) records get `REGISTRY_ONLY_NO_PUBLICATION` with the CT.gov status quoted.

## What this is for
Run r2 (snapshot `cache/sglt2-primary-prevention-hf/snapshots/2026-09-15r2-search_v2/`) retrieved a candidate set ~60x the pinned legacy
cache and the automated screen (`harness/screen.py`, decisions in that snapshot's `records.json` -> `screening.decisions`)
marked many more records `include`. None of them is pooled. The handover rule is: source-verify EVERY newly retrieved
trial before it pools -- representativeness, not just per-number. You are the verifier for one topic. The integrator
will read your verdict table and decide; you decide nothing about pooling.

## Inputs (read them; do not paraphrase from memory)
- `protocols/sglt2-primary-prevention-hf.md` -- the PICO and eligibility (the `## PICO` block and any inclusion/exclusion text).
- `topics/sglt2-primary-prevention-hf.json` -- `include` (population_any / population_none / intervention_any / comparator ...), `design`,
  `pivotal_trials`, `comparator_pmid`.
- `cache/sglt2-primary-prevention-hf/records.json` + its `harness.screen` decisions: compute the LEGACY includes with
  `python -c "import json,sys; sys.path.insert(0,'.'); from harness import screen; from harness.pipeline import _dedup; cfg=json.load(open('topics/sglt2-primary-prevention-hf.json',encoding='utf-8')); d=json.load(open('cache/sglt2-primary-prevention-hf/records.json',encoding='utf-8')); m=_dedup(d, cfg.get('pivotal_trials')); print(sorted(x['id'] for x in screen.run(m,cfg)['decisions'] if x['decision']=='include'))"`
- `cache/sglt2-primary-prevention-hf/snapshots/2026-09-15r2-search_v2/records.json`: `records` (each with id, id_type, pmid, nct, doi,
  title, abstract, journal, year, pubtypes, found_by) and `screening.decisions` (decision, rule_id, reason, span).
- `docs/reviews/sglt2-primary-prevention-hf/review.json` -> the primary outcome's `trials` (pooled) and `declared_absent_trials`: the
  trials the served page already accounts for.

## Define the population
NEW INCLUDES = r2 records whose screening decision is `include` AND whose pmid (or nct when there is no pmid, or doi
when neither) is NOT among: the legacy includes, the pooled trials, or the declared-absent trials of the served review.
State the counts on the first lines of the report: `r2 includes {n_inc} of {n_records}; already accounted for {n_old};
NEW {N}`. Verify ALL N; `NOT_VERIFIED_CAP` is not available to you.

## For EACH new include, one object in `lane_v/sglt2-primary-prevention-hf.json`:
```
{"id": ..., "id_type": ..., "pmid": ..., "nct": ..., "title": ..., "year": ...,
 "verdict": one of
    "ELIGIBLE_RCT"            -- a randomised trial of the topic's intervention vs its comparator in its population, reporting on the primary outcome or a secondary of the protocol
    "ELIGIBLE_RCT_NO_PRIMARY" -- eligible design/PICO but the record's abstract does not report the protocol's primary outcome (would be a declared-absent candidate, not a pooled one)
    "NOT_RCT"                 -- observational, review, protocol, editorial, pooled/secondary analysis of an already-accounted trial (name it), sub-study, model, etc.
    "WRONG_POPULATION" | "WRONG_INTERVENTION" | "WRONG_COMPARATOR" | "WRONG_OUTCOME_ONLY"
    "DUPLICATE_OF_ACCOUNTED"  -- same trial (same NCT / same acronym) as a pooled or declared-absent trial; name which
    "UNDECIDABLE_FROM_RECORD" -- the record (title+abstract, plus a PubMed efetch if the snapshot abstract is empty) does not settle it; say what is missing
    "REGISTRY_ONLY_NO_PUBLICATION" -- an NCT-only record (id_type "nct", no pmid): a registration, not a report; quote its CT.gov overall status / conditions / interventions from the record. These ARE in N (the first lanes dropped them and shrank their own denominator; the integrator re-derives N and will count the omission against you)
 , "quote": "<verbatim span from the title or abstract that decides the verdict, <= 300 chars>",
 "quote_source": "snapshot abstract" | "pubmed efetch (lane_v/sglt2-primary-prevention-hf-raw/<file>)",
 "screen_rule": "<rule_id the automated screen fired>",
 "screen_agrees": true|false,
 "note": "<one sentence, only if needed>"}
```
A verdict with no quote is not a verdict: if you cannot quote, the verdict is UNDECIDABLE_FROM_RECORD. Do not use
outside knowledge of a trial to decide; the record decides. Fetch the PubMed abstract (efetch, save the XML under
`lane_v/sglt2-primary-prevention-hf-raw/`) only when the snapshot abstract is empty or truncated.

## Report (`LANE-W-sglt2-primary-prevention-hf-REPORT.md`)
First line exactly: `W-sglt2-primary-prevention-hf VERDICTS: NEW {N}; ELIGIBLE_RCT {a}; ELIGIBLE_RCT_NO_PRIMARY {b}; NOT_RCT {c}; WRONG_* {d}; DUPLICATE_OF_ACCOUNTED {e}; UNDECIDABLE {f}; NOT_VERIFIED_CAP {g}; REGISTRY_ONLY {h}` (the eight numbers sum to N).
Second line: `automated screen agreed on {x} of {N} verified` (agreed = verdict starts with ELIGIBLE).
Then: the population lines above; the list of ELIGIBLE_RCT ids with titles (these are the ones that could move the pool);
the DUPLICATE_OF_ACCOUNTED pairs; every command run. Marks: every number is MEASURED; anything else say INFERRED.

## Finish condition
`lane_v/sglt2-primary-prevention-hf.json` has exactly N objects, each with a verdict from the list and a non-empty quote (or verdict
UNDECIDABLE_FROM_RECORD / NOT_VERIFIED_CAP), and the report's first line sums to N. If the topic has no new includes,
the report says `V-sglt2-primary-prevention-hf VERDICTS: NEW 0` and the JSON is `[]`.
