# UNBOUND_LEGACY binding campaign (lane rai, 2026-09-28/29)

Proposals only: no served review is edited. Each of the 65 served pooled rows with `endpoint_binding: unbound_legacy` (served
reviews pinned at `6260e70c`) got a proposed endpoint binding. The proposals came from held text only (codex, four jobs, concurrency 3).
Every proposal was then verified by artefact with `scripts/verify_bindings.py`.

## Result: 48 of 65 rows bound, 17 honestly unbound

| binding | n | | admissibility | n |
|---|---|---|---|---|
| named endpoint resolved to a definition span | 20 | | EXACT_TARGET | 29 |
| result span enumerates its components | 22 | | NEAR_MATCH_DECLARED | 17 |
| registry outcome measure (ClinicalTrials.gov) | 6 | | DIFFERENT_ENDPOINT | 2 |
| REMAINS_UNBOUND | 17 | | UNBOUND | 17 |

`CAMPAIGN.json` holds every row: quotes, admissibility, `what_differs`, and the job that proposed it.

## What the verifier checks

For each proposal, `scripts/verify_bindings.py` checks the following:
- every quote is an EXACT substring of the named held text;
- the result span contains the row's served numbers. For an MD it may instead contain the two arm means whose difference is the served
  effect. Lancet `0·85` and U+2212 minus are read as numbers;
- the binding kind is valid, and there is one proposal per row;
- a named endpoint carries a definition span;
- an enumerating span lists its components;
- a registry binding carries a tie: a quote from the trial's own record naming that NCT, or that record's `nct` field. The `nct` field is
  PubMed's DataBank accession, which `harness/fetch.py` reads from `<DataBank>/<AccessionNumber>`.

The verifier was shown to fail on planted copies of the proposals:
- a fabricated quote;
- a result span without the numbers;
- a tie taken from another trial's record;
- a missing tie.

## Open, for a decision

- Two tocilizumab serious-AE rows (33631066, 33332779) are unbound only because no held text defines "serious". Can a standard
  regulatory category bind with no trial-specific definition?
- CORP 21873705 serves RR 0.44, while the held text reports a relative risk reduction of 0.56. The two are the same quantity, but the
  campaign never converts a number, so the row stays unbound.
