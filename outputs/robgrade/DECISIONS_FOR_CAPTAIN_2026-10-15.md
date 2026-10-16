# Six decisions for the Captain (Mahmood's delegation), robgrade lane, 15 Oct 2026

Each item needs a signature or a call; none is taken by the lane. Reply with the item number and the option. The lane
records the decision as relayed, as it did for "sign a2".

## 1. Amendment A4: the two latent defects in the frozen v3.1 dual reading
- **What:** the frozen replay reads a record without checking that its held prompt is the CURRENT prompt. Conflicting
  duplicate answer rows resolve by row order.
- **Measured** (outputs/robgrade/SIGNING_A4_REQUEST.md; request revised after second review in served-fixes ee3fe7a16): readers 0 of 138 stale; adjudicators 8 of 65
  stale (7 because typed rules added later now settle the question, 1 from A2's parser); served store 0 of 56;
  conflicting rows 0 found.
- **Effect:** no committed object or score changes, and the pre-registered frozen inputs stay byte-identical. BUT A4
  changes what a REPLAY produces for the 8 trials with stale adjudications (balanced crystalloids 6, IV iron 1,
  probiotics 1): their stale adjudications are no longer read, so every question still in dispute falls back to NI
  (2 to 10 questions per trial; listed in the request). To keep them adjudicated instead, the 8 adjudications must be
  re-made live (8 adjudicator calls; new answers need not match the old ones).
- **Also specified** (second review, codex + Claude Sonnet, Gemini owed): a reader whose held record does not answer the
  current prompt counts as missing -- no agreement is computed and nothing is sent to adjudication for it; any two
  different answers to one question (Y vs PY included) give NI flagged AMBIGUOUS_CONFLICTING_ROWS.
- **Options:** (a) sign A4 and re-make the 8 adjudications live once agy returns (~17 Oct), keeping those trials
  adjudicated; (b) sign A4 and accept NI on the disputed questions of those 8 trials; (c) leave A4 unapplied (the
  served driver already guards against both defects at its own layer; the frozen v3.1 replay keeps reading the 8
  stale adjudications).

## 2. Six closed-source spans in committed, pushed v3.1 objects (PUBLIC repository)
- **What:** reference-list article titles, author names and XML markup from non-CC full texts: PMIDs 29485925 and
  26376600 (in byte-frozen TEST-topic files) and 16769748 (metformin, not frozen). No judgement uses them. The frozen
  redactor misses typed_conflicts spans; the new current-replay outputs already redact them.
- **Options:** (a) redact them by a declared amendment and fix the frozen redactor (the same amendment could carry A4);
  (b) accept them as bibliographic metadata (titles and authors are listed in PubMed); (c) redact only the unfrozen
  metformin object now.

## 3. The second (Google) reader while agy is out of quota
- **What:** a real call (~19:30 UTC 14 Oct) returned "Individual quota reached ... Resets in 58h26m", i.e. about
  06:00 UTC 17 Oct. agy offers no other Google pool. Its Claude and GPT-OSS models are not an independent family
  (Claude orchestrates, codex is OpenAI).
- **Effect:** the served RoB 2 readings are 0 of 65 assessed until then. The 56 codex readers already held are reused.
- **Options:** (a) wait for the reset; (b) upgrade the agy subscription now.

## 4. Serving scope
- **What:** 5 pooled trials on served primary outcomes are identified only by an NCT number (esketamine 2,
  sacubitril-valsartan 1, tocilizumab 2); the served driver reads PMID-identified trials only. Separately, 11 trials
  appear only on NON-primary served outcomes.
- **Options:** (a) read the NCT-only trials from registry text alone (no abstract; most RoB 2 answers would be NI);
  (b) leave them "No formal RoB 2 assessment yet". For the 11: (c) extend the served reading to every served outcome;
  (d) primary outcome only.

## 5. MEMORY markers vs a shown "published report"
- **What:** a rationale that names the shown source as "the published report" is rejected as memory. Codex raised it in
  every review round 16-34; it changes the pre-registered rule, so it was declined as outside A2/A3.
- **Options:** (a) a further rule amendment, pre-registered and scored like the variants; (b) keep the rule.

## 6. A3's wording residual
- **What:** references to unseen documents and disclaimers are recognised by WORDING (document kinds, aliases,
  registers, trial identifiers, "another record"). A phrasing outside the patterns is not recognised. For an
  unrecognised reference the contextual answer stands (the readers' judgement); for an unrecognised disclaimer it is NI.
- **Options:** (a) accept the residual as stated; (b) narrow it (for example by a model-judged check, recorded and
  dual-read).
