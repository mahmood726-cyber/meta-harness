# The four codex rule candidates (A2 review, rounds 7-15) -- Mahmood's decision

Codex raised four findings in every round of the A2 review that A2's signature did not cover, because each changes
the pre-registered contextual RULE (outputs/robgrade/CONTEXTUAL_POLICY.md, pre-registered at 2b3450d7) or the frozen
served-tab renderer. They were recorded for Mahmood in outputs/robgrade/ctx_review/RESPONSES.md:

1. A rationale that relies on a source the readers were never shown ("the original manuscript confirms ...",
   "according to the protocol ...") passes the memory markers.
2. Question 4.3 (were outcome assessors aware of the intervention received?) is not setting-based. When participants
   report their own outcome, their awareness can follow from the interventions themselves, as at 2.1, but the topic
   gate requires the quote to name assessors or blinding.
3. "commonly" in a mechanism rationale ("central web-based randomisation is commonly concealed") counts as reasoning
   from what trials usually do, even when the rationale argues from the quoted method.
4. A contextual decision on a branch that a later contextual answer closed is stored but not rendered on the served tab.

## Signed

Signed by Mahmood, relayed by Dispatch, 13 Oct 2026. His words: "ok" to the four candidates; adopt 1 and 4 directly;
for 2 and 3, pre-register each before scoring, score them separately on TEST, and report n of N in the three
columns; failing-first tests and a codex/agy review. The robgrade lane RECORDS this decision; it did not sign.

[x] 1 and 4 -- adopted directly, as amendment A3 to the contextual rule and the served-tab renderer (declared in
    outputs/robgrade/AMENDMENTS.json like A2, bound to the reviewed patch).
[x] 2 -- the variant v43_setting, pre-registered in outputs/robgrade/CONTEXTUAL_VARIANT_v43_setting.md, scored
    separately on TEST.
[x] 3 -- the variant vcommonly, pre-registered in outputs/robgrade/CONTEXTUAL_VARIANT_vcommonly.md, scored
    separately on TEST.

The variants are never the default: the served rule is A3 unless Mahmood adopts a variant after seeing its score.

## Raised during the A3 review (NOT signed; for Mahmood)

5. Let the MEMORY markers yield when the named report is the shown source. "The published report describes ..." is
   rejected as memory even when that report was shown. Codex raised it in every round from 16 to 27; it changes the
   pre-registered rule, so it is not part of A3.
6. A3's wording residual. References and disclaimers are recognised by wording (documents, aliases, registers, trial
   identifiers, "another record"); a phrasing outside the patterns is not recognised (ctx_review/RESPONSES.md, round 27).
