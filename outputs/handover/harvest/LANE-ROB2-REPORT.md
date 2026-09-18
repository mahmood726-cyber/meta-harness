# LANE ROB2 report

**Lane work complete with the explicitly permitted UNREADABLE exception. Everything remains PROPOSED; adjudicator OWED (Mahmood).** No assessment, commit, reset, checkout, stash, push, deployment or network acquisition was performed. The only browser traffic was the offline test at `http://127.0.0.1:8000/`.

Base: `3f8add72d50b84eae2000625387e3194137a06ea`. The inherited regulatory manifest modification and supplied inputs were preserved. Project/submission status is unchanged; INDEX and the rewrite workbook were not edited.

## MEASURED: algorithm transcription

The held full guidance identifies its version as 22 August 2019. PDF and extracted-text SHA-256 values match `outputs/handover/rob2_method/SOURCES.json` for both guidance and cribsheet. The substantive comparison uses full-guidance criteria and mapping tables, not remembered rules or unreadable diagram arrows.

`outputs/handover/glp1_rob2/algorithm_transcription_check.json` holds verbatim Low / Some concerns / High criteria for each domain, page numbers and zero-based Unicode character offsets in the unnormalised UTF-8 text. Each audited branch has its own verbatim mapping-row/prose span, page, offset, `agrees` and `fix_applied`. Offsets are not PDF byte offsets.

**44 of 45 audited branches agree after correction; 0 of 45 disagree; 1 of 45 is UNREADABLE.** The denominator is 37 domain mapping/prose branches, 3 D2 combination branches, 1 unresolved D3 branch and 4 overall-rule checks. Twelve of the 44 readable rows required corrections. `agrees` records the corrected implementation; `fix_applied` records the baseline discrepancy. Criteria quotes are supporting evidence, not additional branch-count units.

| Domain/rule | Agree of N | Disagree of N | UNREADABLE of N |
|---|---:|---:|---:|
| D1 | 7 of 7 | 0 of 7 | 0 of 7 |
| D2 | 12 of 12 | 0 of 12 | 0 of 12 |
| D3 | 5 of 6 | 0 of 6 | 1 of 6 |
| D4 | 10 of 10 | 0 of 10 | 0 of 10 |
| D5 | 6 of 6 | 0 of 6 | 0 of 6 |
| overall | 4 of 4 | 0 of 4 | 0 of 4 |

Corrections: D1 allows NI for sequence/baseline information when concealment is adequate and routes baseline imbalance with adequate concealment to Some concerns. D2 routes outcome-unlikely or balanced deviations to Some concerns and follows the table’s NI routes for deviation impact and analysis. D3 follows the table’s NI routes at 3.3/3.4 when 3.2 is N/PN. D4 no longer infers Low from masking alone when between-group ascertainment differences are NI, and follows the NI routes through awareness/influence. D5 and the worst-domain overall default required no change.

**UNREADABLE: `D3.robust_NI`**, meaning 3.1 N/PN/NI with 3.2 NI. Table 10 on page 47 has no such row, and the arrows of Figure 4 on page 48 are absent from extracted text. Question 3.2 does not list NI as a response option; the evidence schema nevertheless preserves unsupported questions as NI. This implementation does not silently recode NI to N: this named path retains a provisional Some concerns proposal. It is reached in 11 of 11 trial D3 proposals. The renderer names exactly this unresolved algorithm path. Other figure arrows are also absent, but their mappings are readable in the tables; those equivalent branches are checked rather than labelled UNREADABLE.

Mapping-pattern tests expand Y/PY and N/PN alternatives and NI, including unused-node combinations. All nine D2 part-rating combinations and all 243 five-domain overall combinations are checked. These are source-table conformance checks, not published trial worked examples; published worked-example validation remains NOT_RUN / OWED.

Overall rule, verbatim from held page 4 (same exact span is stored against the four overall audit branches):

```text
Low risk of bias The study is judged to be at low risk of bias for all domains for this 
result. 
Some concerns  The study is judged to raise some concerns in at least one domain 
for this result, but not to be at high risk of bias for any domain. 
High risk of bias The study is judged to be at high risk of bias in at least one domain 
for this result. 
Or 
The study is judged to have some concerns for multiple domains 
in a way that substantially lowers confidence in the result.
```

The default overall proposal uses the worst domain. Whether multiple Some concerns substantially lower confidence remains an explicit human judgement; no count-based escalation is applied.

## MEASURED: canonical membership and proposals

The generator now reads `cache/glp1-ra-mace-t2d/families.json`: select PRIMARY reports and exclude SELECT, which is outside this T2D review’s scope. This yields **11 of 11 required trial families**. The complete PRIMARY set contains 12 families including SELECT. Exact PMID/NCT pair equality with the eligible reviewB set was asserted: **11 of 11 pairs match; 0 canonical-only and 0 reviewB-only pairs**. ReviewB supplies display names, not membership. A mismatch is recorded explicitly and canonical membership wins.

All 11 PMID/NCT pairs were checked against held publication source headers and PRIMARY reports; available records.json identifiers/abstracts were rechecked. The supplied compressed registry rows also contain all 11 NCTs; their held `id_information` values and the compressed-file digest are recorded in `verification.json`. No dates or clinical effect estimates were re-entered or inferred from aliases.

**55 of 55 domains and 242 of 242 questions generated.** The question denominator is 22 per trial (D1 3, D2 7, D3 4, D4 5, D5 3). **42 of 242 answers are Y/PY/PN/N; 200 of 242 are NI. Zero of 55 domains and zero of 11 trials are adjudicated.** Every rating below is PROPOSED. L = Low; SC = Some concerns; H = High.

| Trial (PMID; NCT) | Y/PY/PN/N counts | Answered of 22 | NI of 22 | D1 | D2 | D3 | D4 | D5 | Overall |
|---|---|---:|---:|---|---|---|---|---|---|
| ELIXA (26630143; NCT01147250) | 0/2/2/1 | 5 of 22 | 17 of 22 | SC | SC | SC | SC | SC | SC |
| LEADER (27295427; NCT01179048) | 0/2/2/1 | 5 of 22 | 17 of 22 | SC | SC | SC | SC | SC | SC |
| SUSTAIN-6 (27633186; NCT01720446) | 0/1/1/0 | 2 of 22 | 20 of 22 | SC | H | SC | H | SC | H |
| EXSCEL (28910237; NCT01144338) | 2/1/2/1 | 6 of 22 | 16 of 22 | L | SC | SC | SC | SC | SC |
| Harmony Outcomes (30291013; NCT02465515) | 0/3/3/0 | 6 of 22 | 16 of 22 | L | L | SC | SC | SC | SC |
| PIONEER 6 (31185157; NCT02692716) | 0/1/1/0 | 2 of 22 | 20 of 22 | SC | H | SC | H | SC | H |
| REWIND (31189511; NCT01394952) | 1/1/2/0 | 4 of 22 | 18 of 22 | SC | L | SC | H | SC | H |
| AMPLITUDE-O (34215025; NCT03496298) | 0/1/3/0 | 4 of 22 | 18 of 22 | SC | H | SC | SC | SC | H |
| FREEDOM-CVO (34873344; NCT01455896) | 0/1/1/0 | 2 of 22 | 20 of 22 | SC | H | SC | H | SC | H |
| FLOW (38785209; NCT03819153) | 0/1/1/0 | 2 of 22 | 20 of 22 | SC | H | SC | H | SC | H |
| SOUL (40162642; NCT03914326) | 0/1/3/0 | 4 of 22 | 18 of 22 | SC | H | SC | SC | SC | H |

Seven of 11 overall proposals are now High under the corrected default tables. This is a deterministic algorithm output, often driven by NI routing in D2/D4, not a claim that trial misconduct or bias was observed. All 44 of 44 D3 questions and all 33 of 33 D5 questions remain NI. Missing vital status, completion or discontinuation information was not converted into a MACE-completeness answer.

## FLOW: MEASURED spans and INFERRED limits

FLOW increased from 1 of 22 to **2 of 22 substantive answers**, with 20 of 22 NI. Random assignment supports 1.1 PY. EAC-confirmed MACE supports a proposed 4.1 PN (probably not an inappropriate measurement method). This latter answer is a disclosed interpretation of the regulatory claim, requiring adjudication.

The S-025 label PDF and text hashes match the held regulatory manifest. The following exact excerpts are stored in FLOW evidence (source: `outputs/handover/glp1_regulatory/209637s025lbl.pdf.txt`):

Page 24, character offset 76171:

```text
FLOW (NCT03819153) was a randomized, double-blind, placebo-controlled, event driven trial in adults with
```

Page 24, character offset 77030:

```text
A total of 3,533 patients were randomized to receive OZEMPIC 1 mg once weekly or placebo and were 
followed for a median of 41 months.
```

Page 25, character offset 79057:

```text
Table 10: Analyses of the Primary and Secondary Endpoints and their Individual Components in FLOW 
Trial 
Placebo 
N=1766 (%) 
OZEMPIC 
1 mg 
N=1767 
(%) 
Hazard
```

Page 27, character offset 81972:

```text
Cumulative incidence estimates are based on time from randomization to first EAC-confirmed MACE with non-CV death modelled as 
competing risk.
```

The held text does not support the prompt’s stronger premise of role-specific masking and an explicit FLOW assignment-analysis definition. “Double-blind” does not identify participant/provider roles: 2.1 and 2.2 remain NI. EAC-confirmed does not state EAC blinding: 4.3 remains NI. The two table denominators total the stated randomised population, and the curve uses time from randomisation, but neither proves analysis in assigned groups regardless of adherence: 2.6 remains NI. The explicit ITT definitions elsewhere in this label concern other trials and were not borrowed for FLOW. The supplied FLOW registry design says QUADRUPLE but does not carry explicit role flags in its inline fields; this was not converted into role-specific answers.

## CLAIMED versus observed conduct

Held publication, registry and regulatory statements are source claims about trial conduct. Exact quotation and digest validation establish what those documents say; they do not independently establish that masking, randomisation or adjudication operated as intended. Y/PY/PN/N proposals interpret those claims. No signed clinical risk-of-bias judgement is claimed.

## MEASURED: locator, refusal, tests and preservation

Exact locator replay passed for **52 of 52 stored evidence occurrences**, including NI context quotes; every substantive answer has evidence. Evidence SHA-256, offsets and parent registry-extract lineage are rechecked by `validate`. Guidance spans are also rechecked against the held text by the test suite.

Planted paraphrase:

```text
Every participant had complete MACE follow-up and allocation was perfectly concealed.
```

Actual refusal (pasted from execution):

```text
REFUSED: span not located verbatim in cache/glp1-ra-mace-t2d/ft_27295427.txt
```

Required test command:

```text
python -m pytest tests/test_rob2_evidence.py tests/test_rob2_proposals_ui.py -q
52 passed in 14.03s
```

The browser contract checked 11 trial headings, 55 domain headings, 242 collapsed evidence controls, PROPOSED/NOT ASSESSED wording, named algorithm uncertainty, canonical membership and quote expansion. The screenshot was visually inspected. Network routes outside localhost were blocked; no browser download occurred.

Replay command `python -X utf8 scripts/rob2_verify_lane.py` passed: regenerated proposal JSON, draft HTML and algorithm audit are byte-identical to the stored artifacts. SHA-256 values are in `verification.json`. `git diff --check` passed. Five of five protected production files match HEAD after checkout newline normalisation: harness/rob2.py, harness/grade.py, cached rob2.json, served review.json and served index.html. No production wiring was added.

## Static versus dynamic hardcode disclosure

| Item | Static input | Dynamic measurement/transformation |
|---|---|---|
| Membership | PRIMARY-report rule; SELECT exclusion for T2D scope | PMID/NCT pairs from families.json, equality with reviewB, held header/registry checks |
| Algorithms | Hand-transcribed 2019 criteria/table patterns; one named unresolved NI path | Expanded-vector comparisons, 9 part combinations, 243 overall combinations and computed proposals |
| Evidence | Curated source anchors and explicitly labelled interpretation rules | Exact spans, source/page offsets, SHA-256, refusal on missing quotation |
| Clinical data | No invented effect sizes, dates, identifiers or completeness rates | Existing held values only; unsupported answers remain NI |
| Report/UI | PROPOSED and adjudicator-OWED contract; 5 domains/22 questions | Trial coverage, ratings, branch counts and artifact digests computed from files |
| Test inputs | Hypothetical vectors and one planted paraphrase, not clinical evidence | Source-backed table comparisons, tamper rejection and offline E2E checks |

## Artifacts and remaining OWED work

Required report: `LANE-ROB2-REPORT.md`. Audit: `outputs/handover/glp1_rob2/algorithm_transcription_check.json`. Re-derived proposals: `cache/glp1-ra-mace-t2d/rob2_proposals.json`. Isolated renderer draft: `outputs/handover/glp1_rob2/rob2_draft.html`. Evidence/replay proof: `outputs/handover/glp1_rob2/verification.json`.

`STUCK_FAILURES.md` now distinguishes the resolved source-supply blockers from D3.robust_NI and the still-unsupported FLOW answers. Human adjudication and any multiple-concerns override remain OWED. No Overmind PASS, certification, SHIP status or published-example validation is claimed.
