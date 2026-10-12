# Signing packet item: RoB 2 "NI-driven" labels on the served RoB tab (robgrade lane, via the Captain)

For Mahmood's signature. Nothing below is served; this lane never edits docs/.

## The change proposed
On the RoB 2 tab of a served review, every domain and overall judgement that the pre-registered NI policy labels
NI-driven is shown with its label (outputs/robgrade/NI_POLICY.md, pre-registration commit
c2a27057db2222fdd1f56f0674a784c35ca4fa71). Examples from the previews:
- "Some concerns (NI-driven: 1.2 not reported; Low if reported favourably)"
- "High (NI-driven: 2.6, 2.7 not reported; Low if reported favourably)"
The judgement word itself is never changed. Rendered by robgrade/rob2_tab.py from the per-trial objects (6 plants);
previews for the 4 calibration topics are in outputs/robgrade/tab_preview/.

## What it rests on
- Engine v3.1: the RoB 2 algorithms are pinned to the full guidance's mapping tables. Three errors found in review are
  fixed (D2 2.4 NI, D2 2.7 NI, D4 4.1 NI). By themselves these moved 35 of 210 TEST judgements (31 D2 Some concerns ->
  High, the 2.7 NI branch; 4 D4 Some concerns -> Low). All-pairs agreement went from 71/210 (v3) to 69/210 (v3.1).
- The NI label is a sensitivity of the algorithm's output to the missing answers, not a causal claim (NI_POLICY P5).
- Pre-registered agreement with the published per-trial tables on TEST (50 trials, 4 comparators), n of N:

  | domain | all pairs | excluding NI-driven | NI-driven only |
  |---|---|---|---|
  | D1 | 25 / 45 | 3 / 5 | 22 / 40 |
  | D2 | 15 / 47 | 14 / 15 | 1 / 32 |
  | D3 | 12 / 37 | 8 / 9 | 4 / 28 |
  | D4 | 15 / 46 | 14 / 14 | 1 / 32 |
  | D5 | 2 / 35 | 0 / 0 | 2 / 35 |
  | all | 69 / 210 | 39 / 43 | 30 / 167 |

  - 167 of 210 judgements (80%) are NI-driven.
  - Where a judgement does not depend on missing information, it agrees with the published table 39 times in 43.
  - That stratum was expected to agree more, mechanically (stated before scoring). It shows the disagreement is about
    missing information, not about how the engine applies RoB 2 to what IS reported.
- Limits, stated:
  - Comparators are matched by PMID only, so result identity is not verified.
  - The tools of 3 comparators are not stated in their figures.
  - 40 records are excluded and 9 trials are unmatched (counted in NI_SCORE.md).
  - The score was run under PYTHONUTF8=1 after a false refusal (NI_SCORE_RUN.md).

## Scope
RoB objects exist for 4 calibration topics (and metformin). A served RoB tab across all 32 pages first needs the
served-pool RoB 2 readings: a separate, larger step, not included here.

## Signed
Signed by Mahmood, relayed by Dispatch, 12 Oct 2026. His words: "sign all four". The robgrade lane RECORDS this
signature; it did not sign.

[x] 1. Serve NI-driven labels on the RoB 2 tab as specified (when the RoB tab is served).
[x] 2. Engine v3.1 algorithm corrections (D2 2.4 NI, D2 2.7 NI, D4 4.1 NI).
[x] 3. Contextual PY/PN, in Mahmood's terms: "follow the Handbook (standing rule: the Handbook decides), i.e. allow
       documented contextual 'probably yes/no' answers per Handbook 8.2.3. Each such answer carries its quoted context
       and is labelled as contextual, never silent; NI remains where no context exists." Because it changes judgements,
       the contextual-answer rule is pre-registered before TEST is re-scored, reported n of N in the same three
       columns, and reviewed by codex and agy (outputs/robgrade/CONTEXTUAL_POLICY.md).
[x] 4. Scorer UTF-8 amendment, as a declared amendment: outputs/robgrade/AMENDMENTS.json, entry A1.
