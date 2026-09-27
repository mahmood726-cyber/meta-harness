# Dose regimen identity

Rule: NOAC-AF review, hash `f1867881`, 2026-09-27, retrospective, Dispatch under Mahmood's delegation. A regimen is **agent + dose per administration + frequency**. A daily total is not a regimen identifier.

## Census and scope

Source revision: **3876a62dca66764dff1b4f84d6b43356a1a9e3bb**. This census covers every operational `cache/*/records.json` (`records` abstracts and `ctgov` interventions), including records excluded by screening and topics without a served review, and every `cache/*/dose_selection.json`. It does not limit the denominator to pooled trials. Historical search snapshots are outside the operational denominator; the originating Weitz trial, found in a historical snapshot, is documented separately below. This is not an exhaustive census of all trials mentioned in superseded search snapshots or publications cited by reviews.

Read-only reproduction: `python evidence/dose_regimen/measure.py`. The script reads the pinned Git objects, not today's cache, and writes [census.json](census.json). No network, git writes, inferred trial identifiers, or effect estimates are needed.

* **38/38 operational record files** inspected: **3,330 publication rows + 750 registry rows = 4,080 rows**. Rows are the denominator, not independent trials.
* **104/4,080 rows** contain multiple frequency signals and were inspected as candidates. The broad search deliberately captures weekly visits, daily symptom reports, other drugs' schedules, and monthly schedules outside the parser's supported enum.
* **8/104 candidate rows (8/4,080 total rows)** establish same-agent randomized frequency alternatives: **six trial families**, all named below. Three canagliflozin publications share the source-backed NCT identifier and count as one family. These are descriptive counts, not estimates of sensitivity when an abstract or intervention label omits a schedule.
* **0/2 dose-selection entries state frequency** in their dose field (or their source/verification prose). Both are in the one operational dose-selection file, `cache/noac-vs-warfarin-af-stroke/dose_selection.json`. Neither belongs to a mixed-frequency trial in the held operational evidence.

| Trial / held record identifier | Source topic and field | Same-agent regimens in held bytes | Pinned served/held status |
| --- | --- | --- | --- |
| Romosozumab phase 2, PMID **24382002**, **NCT00896532** | `denosumab-vertebral-fracture`, abstract | 70/140/210 mg monthly; 140/210 mg every three months | Served screening excludes X2; held record retained |
| TAK-442 dose-finding, PMID **20886185** | `doac-vte-recurrence`, abstract | 40/80 mg QD; 10/20/40/80 mg BID | Served screening excludes X2; held record retained |
| DOAC Dosing Options in AntiCoagulation Prophylaxis, **NCT07005024** | `doac-vte-recurrence`, ctgov interventions | Apixaban 2.5 mg BID versus 5 mg QD; also no anticoagulation | Served screening excludes X2; registry reports no results |
| DURATION-5, PMID **21307137** | `sglt2-primary-prevention-hf`, abstract | Exenatide 2 mg QW versus 5 micrograms BID for four weeks then 10 micrograms BID | Served screening excludes X3; held record retained |
| Canagliflozin phase 2, **NCT00642278**; primary PMID **22492586**; bacteriuria PMID **22548646**; Candida PMID **22632452** | `sglt2-primary-prevention-hf`, all three abstracts and source record NCT fields | 50/100/200/300 mg QD versus 300 mg BID; also sitagliptin/placebo | All three held; served screening represents the family with PMID 22632452, excluded X-DESIGN |
| Daily Vitamin D for Sickle-cell Respiratory Complications, **NCT04170348** | `vitamin-d-acute-respiratory-infection`, ctgov interventions | Vitamin D3 3,333 IU daily versus 100,000 IU monthly; also placebo | Held registry record; no mg conversion invented |

Monthly, every-three-month and IU regimens belong in the census even though `parse_regimen` does not support their administration interval or convert IU to mg. Unsupported schedules remain unresolved and cannot pass the dose override.

## Originating historical trial

Weitz phase-2 edoxaban, PMID **20694273**, is held at:

`cache/noac-vs-warfarin-af-stroke/snapshots/2026-09-15-search_v2/records.json`, `records[id=20694273].abstract`, at the same pinned revision.

[weitz_held.json](weitz_held.json) preserves that record's title, identifier, source path and abstract. The new test checks its abstract against `git show` of the pinned source. It reports randomization to edoxaban **30 mg QD, 30 mg BID, 60 mg QD, 60 mg BID**, or warfarin, and explicitly distinguishes the bleeding experience of 30 mg BID from 60 mg QD despite their equal daily total. No bleeding effect from this trial is invented or pooled by the tests. This is **one additional historical trial**, not an extra operational record or a new dose-selection entry.

## Every dose-selection entry

| Held entry | Literal dose field | Frequency stated in entry? | Frequency evidence and resolution |
| --- | --- | --- | --- |
| RE-LY, PMID **19717844**, NCT00262600 | `dabigatran 150 mg (approved higher dose)` | No | Held abstract METHODS gives 110 mg or 150 mg **twice daily**. Resolve 150 mg per administration, BID, 300 mg/day. |
| ENGAGE AF-TIMI 48, PMID **24251359**, NCT00781391 | `edoxaban 60 mg (approved higher dose)` | No | Held abstract METHODS and CONCLUSIONS explicitly describe **two once-daily regimens**. Resolve the existing curated 60 mg selection to QD, 60 mg/day. The abstract itself does not supply the numeric high dose; the existing dose entry supplies it. |

The entries and their effect, interval and scale are unchanged. The pipeline now attaches the resolved regimen and the held text used for frequency. This change verifies regimen identity; it does not independently revalidate the pre-existing effect or interval transformations.

## Boundary adjudications

The following are not additional randomized same-agent frequency comparisons:

* SPR720, PMID **41720869**, `azithromycin-copd-exacerbation`: randomized arms are 500 mg QD, 1000 mg QD and placebo. The abstract separately mentions three open-label patients receiving 1000 mg QD or 500 mg BID. Retain this mixed-frequency exposure warning; the text does not establish randomization of the BID alternative.
* COPPS-2 **25172965**, CORP-2 **24694983**, ICAP **23992557**, and pediatric rivaroxaban **32246743**: frequency varies by body weight within the active strategy, not independently randomized frequency arms.
* Colchicine **42132185**, **32175647**, COLCORONA **34051877**, COPS **32862667**, rivaroxaban EINSTEIN **22449293** / **21128814**, and vitamin C protocol **42054676**: loading/maintenance or sequential schedules within a strategy. They must not be reduced to a single regimen by assuming one frequency.
* **NCT03433248**: `Gliclazide 30 mg QD/BID` is one listed intervention, not two randomized frequency arms; the other arms contain empagliflozin/linagliptin.
* Pooled RECORD analysis **21136019**, Enterococcus SF68 **32656217**, indirect semaglutide comparison **42225300** (held in two topics), and zinc **22435439**: schedules differ across studies or historical comparators, not proven randomized alternatives within the same trial.
* Folic acid in **30847561** is shared across combination arms, but the text does not unambiguously state its frequency in every arm. No same-agent frequency contrast is inferred.
* Other candidates describe different agents (for example apixaban BID versus enoxaparin QD), measurement/follow-up schedules, reviews, or general daily dosing prose. Every candidate is named with its complete held abstract/intervention list in `census.json`; no candidate is silently treated as a positive solely because two frequency words occur.

## Implementation and hardcode disclosure

| Item | Static or dynamic | Basis / limitation |
| --- | --- | --- |
| Frequency spellings, rates per day, strict identity keys | Static parser vocabulary | QD/BID/TID/QW only; unknown is not a match. Weekly daily_mg is an arithmetic average, not daily administration. |
| Agent, dose, frequency, regimen refusal | Dynamic | Derived from the supplied label and held trial text; no per-trial runtime whitelist. |
| Legacy mg-only selection | Dynamic | Accepted only with one held frequency for that agent; mixed/missing schedules return AMBIGUOUS_REGIMEN before the effect can enter trials. |
| Corpus denominator and candidate rows | Dynamic from pinned Git bytes | Reproduced by measure.py; frequency signals are a candidate search, not proof of randomization. |
| Family grouping and boundary adjudications | Static human-readable source review | Identifiers and schedules checked against held records; no registry ID guessed for records lacking one. |
| Two-arm equal-total test plant | Static, explicitly synthetic | Tests identity only; the pipeline plumbing fixture reuses a held ENGAGE effect and explicitly does not label it a Weitz effect. |
| Weitz historical record | Static copy of pinned held text | Test verifies exact abstract equality with the Git object. |

`same_regimen` requires known agent, per-administration dose and frequency. Two unknown frequencies do not prove equality. `60 mg/day` alone has no per-administration dose and no frequency. Explicit `60 mg once daily` can match only QD, never `30 mg twice daily`. The arm object's displayed dose retains its frequency, including `NOT_STATED` when unknown. Selection refusals do not fall through to another effect source.

## Verification

Only the requested test files were run. No existing test was edited. No git write command was run.

Before code edits, the default pytest temporary directory produced **38 passed, one setup error**: Windows denied access to `F:\claude-temp\pytest-of-mahmo`. This failure therefore also occurs without this change. Re-running the two existing files with `--basetemp=.tmp-dose-baseline` gave **39 passed**.

Final command:

```text
python -m pytest -q -p no:cacheprovider --basetemp=.tmp-dose-final tests/test_dose_regimen.py tests/test_arm_object.py tests/test_matched_placebo.py
```

Result: **67 passed** (28 new regimen cases, 39 existing cases). No code/test failure remains. No broader suite, release, push, or deployment was run.
