# Pre-registered variant vcommonly: "commonly" in a rationale

Decision: Mahmood via Dispatch, 13 Oct 2026 (outputs/robgrade/SIGNING_RULE_CANDIDATES.md, candidate 3). This document
is committed BEFORE any computation on TEST under this variant. The commit that ADDS it is the variant's
pre-registration; the scorer refuses the variant score unless the rule files are unchanged since that commit.

## The variant (and nothing else)
The base is the contextual rule as amended by A2 and A3. The variant changes exactly ONE thing: the word "commonly" is
removed from the USUAL markers, the words that mark reasoning from what trials usually do. Every other USUAL marker
stays: usually, typically, generally, most trials/studies, standard practice, in general, as is usual/common, tend to,
are/is often, likely in most/such trials. Every other check still applies:
- only an asked NI question may become PY/PN;
- the quote is verbatim (8-300 characters) from the open source it names, and about the question (topic gate);
- the rationale refers to the quote;
- the rationale is not from memory (MEMORY markers);
- the rationale does not cite a source the readers were not shown (A3);
- two blind readers agree, or the adjudicator decides a real disagreement;
- up to 3 passes; every contextual answer is stored and shown with its quotes.
Code: robgrade/contextual.VARIANTS["vcommonly"], selected only by an explicit argument (never the default).

## Why (codex, A2 review rounds 14-15)
"Central web-based randomisation is commonly concealed" reasons from the trial's own quoted allocation method, about
what that method does. It does not assume an unreported procedure from what trials usually do, yet the base rule
rejects it on the word alone. The frozen round-6 test (tests/test_rob2_contextual.py) encodes the base behaviour and
stays as it is: the variant is scored beside the base, not instead of it.

## How it is scored
- Population: TEST (outputs/robgrade/split.json), the same 50 trials and 4 comparators as the base.
- Records: the variant OVERLAYS the base's run manifest. Every held base record whose prompt the variant builds is
  read, never replaced or omitted (the readers' prompts do not state the rule, so the variant changes none of them).
  New model calls are made only where the base has no record for the variant's prompt: an adjudication of a
  disagreement that exists only under the variant, or a reader call for a later pass whose question set differs from
  the base's. They are recorded in evidence/model_calls/rob2_ctx_vcommonly/, must postdate this pre-registration, and
  must all be read by the variant replay. The pipeline refuses to run the variant before this document is committed.
- Measure: agreement with the published per-trial judgements, n of N, in three columns (all; excluding NI-driven;
  NI-driven only), beside the A3 base. The judgements the variant moves are listed.
- Known when registered: the A2 TEST result (81/210, outputs/robgrade/CTX_SCORE.md). Under this variant NOTHING on
  TEST had been computed. Under A3 (the base), no agreement with any comparator had been computed. Two mechanical
  checks had run on TEST records: A2's 11 supersession proofs still hold, and a live A3 re-run needs no new model
  call (a lower bound).
