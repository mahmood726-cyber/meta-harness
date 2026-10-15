# k-gap IDENTIFICATION step (external review, 13 Oct 2026): before phase 4

`scripts/g1_identify.py` (deterministic, source-linked; candidates are never adopted). **Identification gains and evidence
gains are reported separately.**

## A. Identification: the 61 PMID-bearing missing trials with no NCT

| route (strongest first) | ids found | NEW (not already held by phase 1) |
|---|---|---|
| A: PubMed record DataBank / OtherID (fresh efetch) | 2 | 0 (Young, Tong: ANZCTR ids phase 1 already held) |
| B: AACT study_references, the PMID as the study's OWN publication (exactly one) | 0 | 0 |
| C: CT.gov API v2, studies listing the PMID as a RESULT / DERIVED reference (exactly one) | 0 | 0 |
| E: the trial's OWN held full text states the registration (registration-cue sentence rule) | 2 | 2 |
| D: CT.gov title-word / acronym search | candidates only | never adopted |

**Newly identified: 2 of 61** (gained an NCT: 1).

| topic | trial | registry id | route | source |
|---|---|---|---|---|
| probiotics-aad-prevention | Evans et al50 | NCT01941160 | E_FULLTEXT_REGISTRATION | held full text (UNPAYWALL 10.1017/s0007114516001665; text sha256 0d73c4b51928d824) |
| probiotics-aad-prevention | Velasco et al27 | ISRCTN46764354 | E_FULLTEXT_REGISTRATION | held full text (UNPAYWALL 10.1097/mcg.0000000000001131; text sha256 47ff3350c72d739c) |

- **Ambiguous (1):** 6 [25] (ticagrelor-vs-clopidogrel-acs): MULTIPLE_OWN_REGISTRATIONS: AACT NCT02587260,NCT03881943; CT.gov NCT03881943,NCT02587260. Not adopted.
- **Why 57 stay unidentified:** of all 61, 25 were published before 2005 (ICMJE registration requirement) and 36 in 2005
  or later; none of the 57 has a registration stated in the PubMed record, AACT or CT.gov references, or (where held) the full text.
  Their next routes are the full text (phase 3 holds 6) and local registries.
- The D candidates (title / acronym searches) are recorded in IDENTIFICATION.json. By inspection none is the trial;
  none is source-linked.

## B. Phases 1-3 re-run for every trial that gained an NCT

- **Evans et al50** (probiotics-aad-prevention): {"aact": {"NCT01941160": "NO_POSTED_RESULTS"}, "phase1": "NO_POSTED_RESULTS", "phase2": {"FDA": "NOT_NAMED_IN_A_HELD_TEXT_DOCUMENT", "EMA": "NOT_NAMED_IN_A_HELD_TEXT_DOCUMENT", "NICE": "NOT_NAMED_IN_A_HELD_TEXT_DOCUMENT", "GBA": "NOT_NAMED_IN_A_HELD_TEXT_DOCUMENT"}}

Phase 3 is by PMID and had already run for these trials.

## C. Protocol and companion / primary-outcome publications (the 57 registered missing trials)

From the registry's own reference lists (AACT study_references RESULT / DERIVED; CT.gov referencesModule, response sha256
recorded):
- 34 trials have companion publications: **299 companion PMIDs**.
- 23 protocol / design papers.

Each companion went through the phase-3 pipeline (census, deterministic reader, copy gate, unit of analysis), with
population checks against the trial's OWN report:

| scope | companion PMIDs | open copy | text held | typed find | admitted |
|---|---|---|---|---|---|
| ACTIVE topics (corticosteroids-covid, iv-iron, statins), first | 84 | 75 | 58 | 0 | 0 |
| all topics | 299 | 257 | 139 | 0 | 0 |

- **CC BY companions eligible for a model read: 39, not read here.** The model stage reads the trial's own evidence
  set, not a companion's text.
- By title, the 9 on active topics report other domains or outcomes: REMAP-CAP immune-modulator and plasma domains, a
  GenHAT pharmacogenetic sub-study, ALLHAT adherence and its antihypertensive arms, CARDS CRP.
- A companion-text model stage is a follow-up if wanted.

## D. Evidence gains (reported separately)

| step | newly ADMITTED (n of N) |
|---|---|
| identification -> phases 1-2 re-run | **0 of 1** (Evans NCT01941160: no posted results; named in no regulator document) |
| companion publications -> phase 3 | **0 of 299** (1 typed tuple refused as a subpopulation: totals short of the trial's randomised N) |

**The k-gap fill stays 0 of 141 counted.**
