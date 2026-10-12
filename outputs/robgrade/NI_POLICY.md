# RoB 2 "No information" (NI) policy, pre-registered

Decision: Mahmood, 12 Oct 2026, option (b). The Cochrane Handbook and the RoB 2 guidance decide every point below.
Status: PRE-REGISTERED. The commit that first ADDS this file is the pre-registration. The scorer finds it from git
history itself; it is not a caller's choice: the TEST scoring
(`scripts/rob2_ni_score.py`) refuses to run unless this policy, its code and its tests are byte-identical to that commit.

## 1. What the guidance says (sources)
- Cochrane Handbook, chapter 8, section 8.2.3:
  - NI is used only when details are not reported AND a "probably" answer would be unreasonable without them.
  - Where a question checks for a problem, NI means no evidence of that problem; where an item is normally reported,
    its absence raises concern.
  - The algorithms map every answer combination, NI included, to a PROPOSED judgement. Review authors may change a
    proposal only with reasons given.
- RoB 2 full guidance (Higgins, Savovic, Page, Sterne; 22 August 2019): the mapping tables of answers to default
  judgements, NI included -- Table 4 (D1), Table 6 (D2), Table 10 (D3), Table 12 (D4), Table 14 (D5). Every domain
  algorithm in `robgrade/rob2_formal.py` is pinned to these rows (`tests/test_rob2_algorithm_guidance.py`).
- Sterne et al., BMJ 2019;366:l4898 (RoB 2):
  - Table 1 gives, for each signalling question, the response that indicates LOWER risk of bias.
  - The algorithms "include explicit mappings for situations where there is no information", and these "do not
    necessarily map to a negative assessment" (e.g. 1.3 NI leads to LOW).
  - Table 3 gives the overall judgement from the domain judgements.
  - Review authors are encouraged to report the answers to the signalling questions, with support.

## 2. The policy
P0. **The algorithms follow the guidance tables (engine v3.1).** The review found three branches that disagreed with the
    full guidance, and they are corrected before this policy is applied:
    - D2 part 1: 2.4 NI with 2.5 N/PN/NI gives High (Table 6).
    - D2 part 2: 2.7 NI after 2.6 N/PN/NI gives High (Table 6).
    - D4: 4.1 NI is grouped with N/PN, and only 4.2 NI sets the Some concerns floor (Table 12).
    These change judgements by themselves. That change is reported separately (v3 -> v3.1), never mixed into the
    NI-policy strata.
    - The response vocabulary is enforced at every entry (`normalize_answers`):
      - a question the branching skips is NA, whatever was supplied as NI (Table 1; Tables 6, 10, 12: `applicable()`);
      - NA on an ASKED question is read as NI: NA is only for a question the branching skips (the normalisation repeats
        to a fixpoint, since a correction can open a branch; proven idempotent);
      - an asked 3.2 that was not answered is N ("no evidence"; Table 1 offers no NI there).
      On admissible answers this is judgement-neutral, proven exhaustively over every Y/N/NI/NA combination. Correcting
      an NA given to an asked question CAN raise a judgement (e.g. 2.7 NA after 2.6 N becomes NI, so High, Table 6);
      that is a correction of an invalid input, reported within v3 -> v3.1.
    - D2 branching follows the full guidance (Box 6, Table 6), which differs from BMJ Table 1: 2.4 is asked only after
      2.3 Y/PY, and 2.5 after 2.4 Y/PY/NI.
    - The overall flag for "some concerns in multiple domains" is raised at two or more domains (it was three, an
      unsourced threshold). It remains a flag for a review author; a High is never automated.

P1. **This policy never changes a judgement.** The served judgement remains the RoB 2 algorithm's output, NI included. Missing
    information is not a reason to override a proposal (Handbook 8.2.3), and the engine never invents a "probably"
    answer: an answer needs a verbatim span, or it is NI (Mahmood's standing instruction for this lane: "no information
    when the source is insufficient; never guess"). A review author may still override any proposal with reasons
    (Handbook 8.2.3); no override is automated, and none is made by this policy.

P2. **NI-driven, domain level** (`robgrade/rob2_formal.ni_label`): a domain judgement is NI-driven when re-running the
    same domain algorithm, with every ASKED NI answer in the domain replaced by the Table 1 lower-risk response, gives a
    less severe judgement. The replacement repeats while it opens a newly asked NI question. This is a
    sensitivity: the judgement CONDITIONALLY depends on the missing answers (see P5); it does not say a reported concern
    is absent.
    - The label carries:
      - the judgement if the NI answers were resolved favourably;
      - every NI question;
      - the decisive NI questions: those whose resolution alone lowers the judgement.
    - An unanswered question is NI.
    - 3.2 is never resolved: Table 1 offers no NI for it ("is there evidence..."), so no evidence is the answer N.
    - NI that the algorithm already maps to the favourable side (e.g. 1.3) never makes a domain NI-driven.

P3. **NI-driven, overall** (`overall_ni`): the overall judgement is NI-driven when Table 3's rule, applied to the
    domains' NI-resolved judgements, gives a less severe overall. It lists the NI-driven domains.

P4. **Not NI.** A domain that is INSUFFICIENT_OPEN_SOURCE (D8 kept the text from a model reader and no rule found the
    information) is not labelled (`ni: null`), and neither is an overall that is NOT_ESTABLISHED. That is a separate,
    already-served state.

P5. **What the label is, and is not.** It is the sensitivity of the algorithm's output to the missing answers. It is
    not a causal attribution: a resolution can also close a branch on which a reported problem was being weighed
    (e.g. D2, where awareness is NI but unbalanced deviations are reported, would be Low if participants had been
    unaware). The served label therefore says "would be X if <questions> were reported favourably", which is exactly
    what was computed (codex review).

P6. **Why this definition, not a count.** A count ("most answers NI") ignores the algorithm: three NI answers can leave
    a domain LOW, and one NI at 1.2 decides D1. The counterfactual re-uses the Handbook's own algorithm, so "driven by
    NI" means exactly "the algorithm's output depends on the missing information".

## 3. Our NI is stricter than the Handbook's (stated, not corrected)
The Handbook would answer "probably yes" in some cases where the engine says NI (e.g. a large trial run by a CTU that
does not report its sequence generation). The engine reads only the sources it is given and never infers. So our NI
means "not reported in the open sources read", and NI-driven judgements are expected to be common. That is the reason
for the label: the reader sees which concerns come from missing information.

## 4. Scoring (pre-registered, `robgrade/ni_policy.two_way`, run by `scripts/rob2_ni_score.py`)
- The scorer trusts no calibration file. It rebuilds every pair from the committed RoB objects and the recorded
  comparator transcriptions, and it refuses:
  - a pair whose judgement or label differs from a recomputation from its stored answers;
  - a non-TEST trial;
  - a duplicate pair.
  It scores all four registered comparators (no subset), and recomputes every stored judgement (a malformed one is
  refused, never silently excluded).
  It also refuses a changed cohort (a trial added or dropped), a domain whose INSUFFICIENT_OPEN_SOURCE status changed,
  and scored answers that differ from those committed at the pre-registration (v3.1 may re-judge answers,
  never change them), and any change to the split, the comparator transcriptions or the v3 baseline.
  It names each comparator's tool (a RoB 1 table mapped to RoB 2 domains is an approximation, Handbook 8.8), and it
  counts the excluded records and unmatched trials.
- Data: the 50 TEST trials of the four CC comparators (`outputs/robgrade/split.json`), with the v3 frozen engine
  (`outputs/robgrade/freeze_v3.json`). Their answers are already recorded: scoring is a replay and makes no model call.
- Agreement with the published per-trial domain judgements, as n of N, per domain and in total:
  1. ALL domain pairs;
  2. EXCLUDING pairs whose (our) domain judgement is NI-driven;
  3. the NI-driven pairs alone, reported beside (2), so nothing excluded disappears.
- The v3 -> v3.1 algorithm corrections (P0) are reported as their own line: the pairs they moved, and all-pairs
  agreement under v3 and under v3.1.
- Known limit, not fixed here: a comparator row is matched to our trial by PMID. That does not prove both judge the
  same outcome result; RoB 2 rates a result (codex review). The comparator's outcome is not stated per row in most
  figures.
- Expectation stated before scoring: (2) will exceed (1) partly mechanically, because the NI-driven pairs are where we
  are more severe. (2) is a stratum, not an improvement, and is never reported without (1) and (3).
- Disclosure: the v3 domain answers on TEST were already computed and seen in aggregate (judgement counts) before this
  policy was written. Neither the NI-driven split nor the v3.1 judgements on TEST were computed before
  pre-registration. The three algorithm corrections come from the review against the guidance tables, not from TEST
  data.

## 5. Served page (into the signing packet, not served until Mahmood signs)
- Every domain judgement and overall judgement that is NI-driven is shown as e.g. "Some concerns (NI-driven: 1.2 not
  reported; Low if reported favourably)", with the NI questions listed.
- The judgement itself is unchanged.
- Through the Captain: a served change enters the signing packet; this lane never edits docs/.

## 6. Review
- The policy, code and tests were reviewed by codex and agy, recorded and blind to each other, before the
  pre-registration commit (`outputs/robgrade/ni_policy_review/`).
- Five rounds, 40 findings, each answered in `RESPONSES.md` there: fixed (with a failing-first test), declined with its
  guidance basis, or escalated to Mahmood (contextual PY/PN). agy accepted round 5; codex's last finding was fixed.
