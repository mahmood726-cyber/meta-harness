# To the Ordered-contrast lane: Takahashi (esketamine, Japan; PMID 34696742) continuous-outcome extraction

From the evidence lane (`evid/v1.0.1-acquisition-cascade`), 2026-09-27. **Nothing is admitted and no served number moves.**

## Where eligibility stands
- The OAD question is settled by Mahmood's RETROSPECTIVE clarification. It is recorded verbatim in
  `docs/protocol_clarifications.json`: the governing message is "I think include as esketamine is the intervention.",
  relayed through Dispatch.
- Takahashi's `oad_initiation` field is `PRE_RANDOMISATION_LEAD_IN_CONTINUED_UNCHANGED`. That qualifies, as a
  disclosed design difference. It is the only member of the sensitivity analysis that excludes lead-in-initiated trials.
- Takahashi is still **UNRESOLVED** (`awaiting_classification`, rule `A-PROTOCOL-CONFLICT`). Two decisions are pending:
  1. **PENDING_PROTOCOL_CONFLICT.** The 2026-09-16 retrospective amendment excludes phase 2/II trials. It says the
     exclusion "was declared in the protocol", but the protocol as registered (commit `5e2b43c6`) has no phase
     exclusion. Mahmood's ruling covered the OAD timing, not the phase. It needs his ruling for this trial.
  2. **MULTI_ARM_SELECTION.** Three fixed esketamine doses (28/56/84 mg, 2:1:1:1 against one placebo arm) need a
     prespecified selection or a shared-control correction.

## What to extract, so it is ready when both decisions land
- **Source:** `cache/esketamine-trd-madrs/ft_34696742.txt`, sha256 `f843b169b964373336d9b5df988f879201250d371eeb47ac3bbaad7a53ad101b`.
  This is the held open-access full text; the Japanese trial is registered as NCT02918318.
- **Table:** "Day 28 MMRM; DB Induction Phase". It gives per-arm N and Mean (SD) at baseline and at Day 28:
  Esk28 N=41, Esk56 N=40, Esk84 N=41, Placebo N=80.
- **Protocol estimand:** the observed-case Day-28 **change from baseline**, as per-arm mean and SD. It must never be a
  final value, an LS mean with an SE, or a figure. If the table gives only the Day-28 values and baseline, and no
  change SD, the row is REPORTED_UNRESOLVED; derive nothing.
- **Served consequence if it is admitted:** the Day-28 MADRS pool goes from k=3 to k=4. That is a served-number change,
  so it needs a notice and Mahmood's signature.
