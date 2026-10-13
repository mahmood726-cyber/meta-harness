# RoB 2 contextual "probably" answers, pre-registered

Decision: Mahmood, 12 Oct 2026, signing packet item 3 (relayed by Dispatch): "follow the Handbook (standing rule: the
Handbook decides), i.e. allow documented contextual 'probably yes/no' answers per Handbook 8.2.3. Each such answer
carries its quoted context and is labelled as contextual, never silent; NI remains where no context exists."
Status: PRE-REGISTERED. The commit that first ADDS this file is the pre-registration; `scripts/rob2_ctx_score.py`
finds it from git history and refuses to score unless this policy, its code and tests, and its frozen inputs are
unchanged from there.

## 1. What the guidance says
- Cochrane Handbook 8.2.3: NI is used only when insufficient details are reported AND, without them, a "probably"
  answer would be unreasonable. Example: for a large trial run by an experienced clinical trials unit, missing
  randomisation details may still justify "probably yes" (with the rationale in the free-text box).
- RoB 2 (Sterne et al., BMJ 2019): Y and PY have the same implication for risk of bias, as do N and PN; the rationale
  for a response is given in the free text.

## 2. The rule
C1. **Only NI changes.** A contextual pass reads ONLY the asked questions whose final v3.1 answer is NI. It never
    covers 3.2 (no NI option) or a domain that is INSUFFICIENT_OPEN_SOURCE. Every direct answer (typed rule, dual
    reading, adjudication) is kept exactly as it is.
C2. **Only PY or PN.** A contextual answer is PY or PN, never Y or N: it is a probability judgement from context, not
    a reported fact.
C3. **Quoted context, open sources only.** Each contextual answer quotes, verbatim, the context it rests on (8-300
    characters) from ONE source the reader was shown. That source is open for a prompt (D8 is unchanged), and the quote
    is verified mechanically like every other quote. The rationale states the inference in one sentence, using
    words from the quote: a rationale that does not refer to the quoted context is discarded. An empty
    rationale, or one that reasons from what trials usually do ("usually", "typically", "standard practice", "most
    trials", ...), is not context, nor is memory: the answer stays NI.
    RELEVANCE GATE (codex review round 3): the quote must contain at least one topic stem of its signalling question
    (robgrade/contextual.QUESTION_TERMS, pre-registered here). E.g. 1.2: conceal / allocation / central / envelope /
    pharmacy / interactive / randomi...; 5.1: plan / protocol / prespecif / regist / statistical analysis. 1.1 and 1.2
    also take TRIAL-CONDUCT context (trials unit / CTU / regulator / coordinating centre / multicentre / sponsor):
    the Handbook's own 8.2.3 example. A context that does not name the question's topic stays NI.
    SETTING-BASED questions, per the RoB 2 guidance (codex rounds 5-6): 2.1/2.2 (awareness can follow from the
    interventions themselves, e.g. surgery v physiotherapy) and 3.3/3.4 (whether missingness could, or is likely to,
    depend on the outcome's true value: reason about the clinical setting). For these four, the topic gate and the
    "usual practice" markers are not applied: quoted context about the setting, with a rationale referring to it, is
    context. Memory and outside-source markers apply to EVERY question. Every other question needs a quote about its
    own topic, and "what trials usually do" is not context for it.
    Residual, stated: within a relevant quote, whether the inference holds is the readers' judgement. Two blind readers
    must agree (or the adjudicator decides), every reader's quote is shown with its source, and the scorer re-verifies
    every recorded reply.
C4. **Two readers, blind, then an adjudicator.** codex and agy each answer the listed questions without seeing each
    other.
    - Both PY or both PN, each with a verified quote (they may cite different sources): the answer is contextual
      PY/PN, stored with BOTH readers' contexts.
    - Both NI: NI, and never adjudicated (agreement is not overridden).
    - Two different verified answers: the recorded adjudicator, under the same rules, sees both readings and decides
      PY, PN or NI. Its decision, an NI included, is recorded as its own.
    - A reader whose record is missing or failed VOIDS the pass: no contextual answer, and no adjudication between one
      reader and nobody.
    - Anything else stays NI.
    - A recorded call is used only for the exact prompt it answered (its prompt sha256, the run file's AND the held
      record's own); a stale record is not replayed.
    - Both readers see the same registered prompt (blind to each other); the adjudicator sees exactly the two verified
      readings, under its registered prompt.
    - A contextual answer can close a branch (a question no longer asked becomes NA; a direct answer there stays as
      answered) or open one (a newly asked question is NI, never guessed). Up to THREE passes: a newly opened NI
      question gets its own contextual pass; a question decided in a pass is never re-asked.
    - Both readers' prompts are rebuilt by the scorer with the pipeline's own prompt builder and must match it byte
      for byte.
C5. **Never silent.** A contextual answer is stored with basis "contextual", its quote, source id and sha256, both
    readers' record ids, and the rationale. The served label names it, e.g. "Low (contextual: 1.2 probably yes)", with
    the quote shown beside it.
C6. **NI remains where no context exists.** The NI policy (NI_POLICY.md) applies unchanged to the answers that stay
    NI; a contextual answer is not NI.

## 3. Scoring (pre-registered, `scripts/rob2_ctx_score.py`, `robgrade/ni_policy.two_way`)
- Data: the same 50 TEST trials and 4 comparators.
- Baseline: the v3.1 objects and calibration as committed at the pre-registration (outputs/robgrade/rob2/,
  calibration_v31.json).
- Agreement n of N, in the same three columns: all pairs, excluding NI-driven pairs, NI-driven pairs alone.
- Also reported:
  - the number of contextual answers, by question;
  - the pairs whose judgement moved from v3.1;
  - the v3.1 three-column table beside it.
- The scorer REPLAYS the registered pipeline (scripts/rob2_contextual.py, replay mode, no model call) from the v3.1
  objects, the run manifest, the held records and the AUTHORITATIVE trial sources. The scored objects must equal the
  regenerated ones exactly.
  - Every held post-registration RAN_OK record must be one the replay READ (consumed); a RAN_ERROR retry attempt is
    accounted for, not refused.
  - Every record the replay read must postdate the pre-registration, NI-deciding ones included.
- The scorer also refuses:
  - any answer that differs from the v3.1 baseline other than an NI that became a contextual PY/PN;
  - a contextual answer whose RECORDS do not verify it: both readers' records (and the adjudicator's when it
    decided) must be held and RAN_OK; the deciding reply must say this answer from this source; the quote must be
    verbatim in the source the recorded prompt showed; that source's sha256 must be an input of the call; and the
    records must not predate the pre-registration;
  - a deleted or added answer, a changed trial, outcome or domain set, or a changed INSUFFICIENT status;
  - any stored judgement, NI label or overall that differs from its recomputation;
  - any change to the policy files, split, comparator transcriptions or baseline.
  It also carries over every refusal of the NI scorer (no subset, the cohort, duplicates). The freeze covers every
  file the score depends on: the rule, the scorer and their tests, plus pairing (rob2_calibrate), evidence (rob2_dual),
  typed answers (rob2_typed), licences (prompt_licence), and the served label (rob2_tab and its tests).
- Expectation, stated before scoring: a judgement can move in EITHER direction, and in pairs that were not NI-driven
  too. A contextual PY or PN replaces an NI that the algorithm may have treated as favourable (e.g. 1.3), so it can
  raise severity as well as lower it (codex review round 2).
- Known limits, unchanged: result identity is unverified (PMID matching); some comparators' tools are not stated.

## 4. Review
- Reviewed by codex and agy, recorded and blind, before the pre-registration commit (outputs/robgrade/ctx_review/).
- Every finding is answered with a failing-first test, or declined with its guidance basis
  (outputs/robgrade/ctx_review/RESPONSES.md).
