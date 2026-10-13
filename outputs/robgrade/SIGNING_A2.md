# Signing request: amendment A2 to the pre-registered contextual-answer rule (robgrade lane, via the Captain)

Pre-registration: 2b3450d7286197ebdaf0c5479b1b802ecfab058b (CONTEXTUAL_POLICY.md). The policy is unchanged by A2; the
amendment fixes an IMPLEMENTATION defect that the pre-registered scorer itself caught.

## What happened
- The recorded contextual re-read of the 50 TEST trials ran after the pre-registration: 59 trial objects, 158
  records, 0 failed calls (3 agy retry attempts, accounted for).
- The pre-registered scorer then REFUSED to score: "4.3: the readers agreed (PN): there was nothing to adjudicate".
- Root cause, measured: the pipeline parses a reply with scripts/rob2_dual.parse (strict JSON), while the scorer takes
  the JSON object in the reply. agy began 15 of its 58 contextual replies (26%) with a line of prose ("I am checking
  the workspace files..."). The pipeline read those 15 as unreadable, i.e. agy answering NI to everything. So agreements
  became "disagreements" and went to the adjudicator: 15 trial passes, 148 questions, 11 adjudications the defect may
  have caused.
- No score was produced. The gate worked as designed.
- The same strict parser in the v3.1 DUAL reading affected 1 of 69 agy replies: a DEVELOPMENT-set trial (PMID 35041780).
  The reported NI score on TEST (69/210) is NOT affected.

## Amendment A2 (to sign)
1. ONE parser for a reply (`robgrade/contextual.parse_reply`: the JSON object in the reply, prose before or after
   ignored), used by the pipeline, the scorer and the dual reading alike. The pipeline and scorer can then never
   disagree on what a model said.
2. The contextual scorer accepts declared, signed amendments (as amendment A1 does for the NI scorer).
3. Records made under the defect stay held and are listed in AMENDMENTS.json:
   - the adjudications it caused are SUPERSEDED (no longer read by the replay, because the readers in fact agreed);
   - where the readers genuinely disagree, a NEW adjudication is recorded (post-registration).
4. Re-run the TEST contextual pass in record-reuse mode: every fresh reader record is reused, with new calls only for
   genuine disagreements. Then score with the amended scorer.
   Every change: failing-first tests; codex + agy review of the amendment before it is applied.

## Signed
Signed by Mahmood, relayed by Dispatch, 13 Oct 2026. His words: "sign a2". The robgrade lane RECORDS this signature;
it did not sign.

[x] Amendment A2, all four parts: one reply parser everywhere; the contextual scorer accepts declared, signed
    amendments; the 11 adjudications are kept and marked superseded; the re-run from existing records. Failing-first
    tests and a codex/agy review come before it is applied; it is scored in the three columns as n of N.
