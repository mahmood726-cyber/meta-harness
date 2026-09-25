# Handoff to Evidence lane two (evid2) from the evidence lane (evid) -- 2026-09-24

evid2 now owns the 34 count rows (typed per-arm observations) and the 53 P5 populations. This file lists what evid already produced on them so evid2 can build on it, re-check it, or discard it -- nothing here binds evid2. evid now works only on the served rows with no locatable source (U23).

## Where everything is (branch evid/evidence-records; landed on main except the newest commits)

- `evidence/worklist.json`: the 76 target rows (P53-01..53 = the 53 P5 rows in `evidence/inputs/the53.json` order; UA-* = the 23 unsourced rows)
- `evidence/packets/<KEY>.json`: every source held for a row, rendered by `evidence/scripts/textrep.py` (the one text a span is checked against; registry render is APPEND-ONLY)
- `evidence/adjudication/<KEY>.json`: the lane's ruling per row, every cited span pinned to held bytes (sha256); `python evidence/scripts/check_all.py` re-verifies all of them
- `evidence/second_adjudication/`: an independent codex (OpenAI-family) second adjudication of all 76, quotes gated; disagreements reconciled in each adjudication's `second_adjudication` block
- `evidence/gaps/` + `MANUAL.json`: analysis-set / follow-up / entry-age spans from newly held full texts (some local-only: `evidence/LOCAL_ACQUISITIONS.json`)
- `evidence/sweeps/entry_age_and_analysis_set.json`: uniform mechanical sweeps (adult age floor; served ITT label vs span), every contributing span read by eye
- `evidence/SIGNATURE_QUEUE.md`, `evidence/OPEN_QUESTIONS.md`: items for Mahmood; nothing landed

## On the 53 P5 rows (evid's state; hand to evid2)

- adjudicated 53 of 53; rulings: SERVED_CONFIRMED 52, CANDIDATE_REJECTED 1
- entry population (evid's lane ruling, from each trial's own text): ESTABLISHED 49, NOT_ESTABLISHED 1, PARTLY 3
- NOT established / PARTLY, with the reason recorded in each file: P53-05, P53-32, P53-48, P53-50
- queued for signature from the 53: P53-23 (RE-LY: RR 0.66 served on an HR-declared outcome; registry Cox HR 0.65, 0.52-0.81)
- open questions from the 53: P53-49 (EMPHASIS-HF timepoint), P53-05 (RECOVERY rate ratio pooled as risk ratio)
- known limits: rulings are one adjudicator's plus a second-family check; most sources are abstracts/registry; the analysis-set reader was revised after two eye passes (fixture `tests/test_evidence_records.py::EYE_LABELLED`)

## Count / mean rows among evid's 76 (23; evid2's 34 count rows may overlap)

- P53-01: balanced-crystalloids-vs-saline-mortality / PMID 35041780 (counts)
- P53-15: esketamine-trd-madrs / PMID 37025256 (means)
- P53-16: esketamine-trd-madrs / NCT02422186 (means)
- P53-19: metformin-pcos-ovulation / PMID 19522426 (counts)
- P53-20: metformin-pcos-ovulation / PMID 16769748 (counts)
- P53-21: metformin-pcos-ovulation / PMID 11172832 (counts)
- P53-32: probiotics-aad-prevention / PMID 32035998 (counts)
- P53-37: probiotics-aad-prevention / PMID 15740542 (counts)
- P53-38: probiotics-aad-prevention / PMID 11560298 (counts)
- P53-40: probiotics-aad-prevention / PMID 21165295 (counts)
- P53-41: probiotics-aad-prevention / PMID 18026577 (counts)
- UA-001: colchicine-postop-af / PMID 32720823 (counts)
- UA-002: colchicine-postop-af / PMID 25172965 (counts)
- UA-008: corticosteroids-cap-mortality / PMID 36942789 (counts)
- UA-009: corticosteroids-cap-mortality / PMID 25688779 (counts)
- UA-010: corticosteroids-cap-mortality / PMID 25688779 (counts)
- UA-014: esketamine-trd-madrs / PMID 31109201 (means)
- UA-027: melatonin-primary-insomnia-sol / PMID 20712869 (means)
- UA-030: omega3-cardiovascular-events / PMID 30146932 (counts)
- UA-032: semaglutide-obesity-weight / PMID 33625476 (means)
- UA-033: semaglutide-obesity-weight / PMID 33567185 (means)
- UA-044: tocilizumab-covid19-mortality / PMID 33631066 (counts)
- UA-045: tocilizumab-covid19-mortality / PMID 33332779 (counts)

## Stopped to avoid duplication

- evid's blind re-extraction extension over the other 56 rows was stopped on 2026-09-24 ~22:20 when evid2's scope was announced; the pre-registered 20-row test-retest result stands (`evidence/extractions/RETEST_RESULT.json`).

## Addendum 2026-09-25 (evid, day): P53 items found after the handoff
- **Served analysis-set labels:** 23 P53 rows are served as 'intention-to-treat' but the held source contradicts the label or does not state a set. They are listed row by row, with the bound span, in `evidence/LABEL_CORRECTIONS.md` (derived by `evidence/scripts/label_corrections.py`). They are labels only, and no number moves. They are yours to adopt or re-rule. evid has not changed any P53 ruling since the handoff.
- **Staleness gate:** `evidence/scripts/stale_check.py` (now condition 4 of `check_all.py`) says whether main has changed a served row since it was ruled on. All 53 P53 rulings match current main as of this addendum.
- **Scale rule:** the M-02 vs M-03/M-04 rule in `evidence/DECISIONS.md` ('Served scale != declared estimand') also bears on the P53-05 and P53-53 scale-label defects recorded earlier.
