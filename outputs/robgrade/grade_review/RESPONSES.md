# Review of the GRADE preview source tiers (scripts/grade_formal_build.py), 14-15 Oct 2026

Mahmood (via Dispatch, 14 Oct): codex and agy implement, test and cross-review overnight; Claude judges and adjudicates.
agy is out of quota ("Individual quota reached ... Resets in 58h26m", real probe 14 Oct ~19:30 UTC), so the
cross-review is by a SEPARATE codex session (read-only), not the implementing one. agy's review is PENDING and is to be
done when agy returns.

| round | reviewer | verdict | findings | response |
|---|---|---|---|---|
| 1 | codex (read-only, fresh) | REVISE | 2 MAJOR, 2 MINOR (round1_codex.txt) | all 4 ACCEPTED, each fixed with a failing-first test: (1) an object of ANOTHER outcome is never used (object outcome as well as file outcome); (2) an object of ANOTHER trial is never attributed (object trial vs key); (3) sources recorded for POOLED trials only; (4) the production tier order is pinned by a contract test. |
| 2 | codex (read-only, fresh) | ACCEPT | none (round2_codex.txt) | -- |

Claude's adjudication: finding 1 was a regression the implementer's brief (written by Claude) introduced -- the old
code checked each object's outcome; the brief specified only the file's. It was held back from the reviewer to keep
the review independent, and the reviewer found it.

Verified independently by Claude: 63 GRADE tests pass. The GRADE previews are NOT regenerated in this change: the
current code's replay does not reproduce 12 of the 69 committed v3.1 objects, and the previews would use some of them
(diagnosis in progress).

## Rounds 3-4 (15 Oct): GRADE draws only on objects the CURRENT code produces

Claude's decision (adjudication): outputs/robgrade/V31_REPRODUCIBILITY.md shows the current code reproduces only 57 of
69 committed v3.1 objects (metformin and DEV objects predate the v3.1 engine). So the GRADE preview reads served A3 >
A3 > a CURRENT REPLAY of the v3.1 store (new scripts/rob2_current.py, no model call, refusing unless both source
settings are exactly "1"); the committed v3.1 tiers are dropped (those files stay frozen and untouched).

| round | verdict | findings | response |
|---|---|---|---|
| 3 | REVISE | 2 HIGH (round3_codex.txt) | both ACCEPTED. (1) Quotations from non-CC full texts survived in typed_conflicts spans: the FROZEN redactor misses them, and the committed, pushed v3.1 objects carry six such spans (reference-list titles, author names, XML; PMIDs 29485925, 26376600 in frozen TEST-topic files; 16769748 in the metformin file). rob2_current now redacts them (any string, any length); a leak check over every string finds none. The committed files need Mahmood's signature to change. (2) Melatonin's "provisional -> moderate" was arithmetic, not a rating: certainty stays provisional while a domain is PARTIAL or a judgement flag is unresolved; the arithmetic stays in certainty_from_assessed_domains_only. |
| 4 | ACCEPT | none (round4_codex.txt) | -- |

Claude's adjudication of a legacy test: test_certainty_is_provisional_while_a_domain_is_unassessed asserted "high"
for a fixture with no arm counts, where imprecision is only PARTIAL. Its requirement stands (rated once every domain
is assessed); its fixture now passes arm counts, so imprecision is genuinely ASSESSED and "high" is earned. 87 GRADE
tests pass (verified by Claude). agy's review is pending (out of quota).

## Rounds 5-6 (15 Oct): the served RoB 2 + GRADE tab PREVIEW (scripts/tab_preview_build.py)

| round | verdict | findings | response |
|---|---|---|---|
| 5 | REVISE | 2 P2, tests only (round5_tab_codex.txt); the output itself verified correct for 32 topics, 96 trial rows, 5 NCT-only rows | both ACCEPTED: per-trial-row assertions parsed from the HTML (distinct judgements; separate unassessed PMID and NCT rows); writes confined to the output directory by an allowlist; no external resources. A planted label swap fails the new tests. |
| 6 | ACCEPT | none (round6_tab_codex.txt) | -- |

Found by Claude while checking: 5 of the 96 pooled trials on served primary outcomes are identified ONLY by an NCT
number (esketamine 2, sacubitril-valsartan 1, tocilizumab 2). The served RoB 2 driver reads PMID-identified trials
only, so these stay "No formal RoB 2 assessment yet" even after the served readings run -- a scope decision for Mahmood.

## Rounds 7-8 (15 Oct): second review by codex + Claude Sonnet while agy is out of quota (Gemini pass OWED)
Per Mahmood (15 Oct): agy is out until ~06:00 UTC 17 Oct, so second reviews are codex + a Claude Sonnet reader; the
Gemini pass on these rounds is owed and will be run when agy returns.

| round | reviewer | verdict | findings | response |
|---|---|---|---|---|
| 7 | Claude Sonnet | REVISE | 1 major, 5 minor (round7_sonnet.txt) | 1 ACCEPTED: any NOT_ESTABLISHED weight makes risk of bias PARTIAL (certainty provisional). 2 PARTLY: redaction matches whitespace-normalised closed text; DECLINED: text also in an open source stays published (open text is publishable). 3 ACCEPTED: closed spans under 20 characters publish no hash/offset/length. 4 ACCEPTED: the preview refuses GRADE whose rob_sources differ from the current sources. 5 ACCEPTED: tier objects must carry their own outcome and trial (all 59 contextual + 69 current objects already did). 6 VERIFIED, kept: at k=1 the flag compares the declared outcome with extracted trial values (melatonin: declared ITT vs completers), so it is a real, conservative judgement flag; relabelled. Implemented by codex, each test failing first. |
| 8 | Claude Sonnet | ACCEPT | 1 nit (round8_sonnet.txt) | regenerated GRADE checked by execution: risk of bias ASSESSED -> PARTIAL in 4 topics (iv-iron-hfref-hosp, metformin-pcos-ovulation, probiotics-aad-prevention, ticagrelor-vs-clopidogrel-acs), all already provisional; no certainty, downgrade or flag changed. |
| 8 | codex | REVISE | 1 minor (round8_codex.txt; an earlier attempt was blocked by codex's sandbox, round8a_codex_blocked.txt, and rerun with the diff inline) | ACCEPTED (same as Sonnet's nit): the frozen-redactor metadata path measured RAW length, metadata() NORMALISED length; a whitespace-padded short span kept its hash. Now both measure the normalised source slice. Failing first (1 failed, 1 passed), then passing; no rob2_current output changed. |

Verified by Claude: 115 GRADE/preview tests passed (20 min run) before the round-8 fix; tests/test_rob2_current.py +
tests/test_model_inventory.py 30 passed after it; closed-text leak check over outputs/robgrade/rob2_current: 6 raw hits,
5 are /outcome strings (open) and 1 is PMID 39529939 (CC) -> 0 closed spans published. No certainty changed: all 32
served topics remain provisional.

## Rounds 9-10 (15 Oct night): provenance-gated optimal information size (OIS) -- codex + Claude Sonnet (Gemini OWED)
Non-model work while agy is out. Audit (outputs/robgrade/grade_ois_audit.json): of the 13 topics with "OIS not
computable", 1 has complete provenanced arm counts (corticosteroids-covid19-mortality); 8 are time-to-event with no
structured counts; 2 continuous (esketamine, melatonin) have counts but no declared MID -- no MID is invented; probiotics
has 7 of 13 trials provenanced (one HAND_ENTERED sibling row excluded). Claude rejected codex's first attempt, which
also made OIS gate CI-decided domains (6 topics ASSESSED -> PARTIAL): under GRADE (handbook 5.2.2) a CI crossing the
decision threshold is rated down whatever the OIS; OIS gates only when the CI excludes it. Restored; OIS recorded as
information there. A CI crossing only the null with N below half a computable OIS raises VERY_SERIOUS_FOR_JUDGEMENT
(flag only, review policy).

| round | reviewer | verdict | response |
|---|---|---|---|
| 9 | codex (inline) | REVISE, 2 medium | ACCEPTED: duplicate pooled trial ids fail closed (failed first: OIS 1806 from a doubled N); the new imprecision mock removed from an existing test. |
| 9 | Claude Sonnet | ACCEPT, 2 low | ACCEPTED: unknown pool size fails closed (failed first: OIS 1806); the mock (same as codex). Verified by execution: corticosteroids OIS 1320 vs N 6425; spot-checked counts equal their source fields and are EXTRACTOR / RECORDED_MODEL_CALL. |
| 10 | codex | ACCEPT | -- |
| 10 | Claude Sonnet | ACCEPT (by execution) | -- |

Net effect vs 07b46be35: corticosteroids-covid19-mortality imprecision PARTIAL -> ASSESSED (OIS met); no other state,
downgrade or certainty changed (all 32 topics remain provisional). Verified by Claude: 157 passed (ten GRADE/RoB 2 files).
