# Comparison-specific blinding

Retrospective sacubitril-HFrEF review, rule hash `0d5f8f77`, 2026-09-28,
Dispatch under Mahmood's delegation. Local edits only; no commit, rebuild,
publication, or change to served artifacts.

## Source and denominator

Corpus pin: `3876a62dca66764dff1b4f84d6b43356a1a9e3bb`.
Pre-change screening implementation: `c15ed11156de6be09fe516cdf348aa247b07ea13`.
All **38 operational topic JSON files**, and both `records` and `ctgov` arrays
in each corresponding held `records.json`, were enumerated with `git ls-tree`
and read with `git show`. No network retrieval or memory-based trial metadata.

**N = 4,080 topic-record occurrences: 3,330 publication records and 750 CT.gov
records.** This is a screening-corpus denominator, not a count of unique trials
or a portfolio count. Repeated records across topics would count separately.

**9 / 4,080** records describe differently blinded randomized comparisons in
an individual trial or primary report. All nine are publication records; **0 /
750** held CT.gov rows explicitly describe this shape. Another **2 / 4,080**
are review abstracts aggregating open-label and double-blind RCTs without
mapping the blinding to individual comparisons. Thus the broad record-level
census is **11 / 4,080**, with the nine directly interpretable reports below
kept separate from those two aggregate reports.

The reproducible broad search yields **59 candidates**. It searches title,
abstract, conditions, interventions and acronym for open-label/unblinded/
unmasked/not-blinded/non-blinded wording plus blind/mask wording, and also
single/partial versus double blinding. Masking metadata alone is not textual
comparison evidence. Full abstracts were read to distinguish comparisons from
run-ins, extensions, outcome-assessor blinding, and incidental wording.
`measurement.json` retains every candidate's full held abstract, source title,
served row, baseline/current screening decisions, parser output, per-topic
denominators and source-cache SHA-256 hashes.

## Every directly interpretable record

“Eligible contrast” below means the topic's intervention/comparator axis;
population, publication-type and title gates can still exclude the record.
BLINDED denotes the reported allocation blinding, not a newly inferred number
of blinded parties. An open arm makes a comparison against a blinded arm
OPEN_LABEL, not BLINDED.

| Topic | Held record / trial | Differently blinded comparisons in held text | Topic contrast's blinding | Pinned served decision |
|---|---|---|---|---|
| denosumab-vertebral-fracture | PMID **27533157**, ACTIVE | Abaloparatide/placebo injections blinded; teriparatide open-label | **No denosumab contrast**; NOT_STATED / not applicable to this topic. Abaloparatide vs placebo BLINDED; teriparatide vs either OPEN_LABEL | **X2**, excluded population term `abaloparatide` |
| doac-vte-recurrence | PMID **21128814**, oral rivaroxaban report | Acute DVT: rivaroxaban vs enoxaparin followed by VKA open-label. Separate continued-treatment study: rivaroxaban vs placebo double-blind | Rivaroxaban vs VKA **OPEN_LABEL**. The placebo comparison is a different contrast | **INCLUDE**, unchanged: topic does not require double blinding |
| doac-vte-recurrence | PMID **20886185**, TAK-442 dose-finding | TAK-442 doses blinded as to dose; enoxaparin open-label | **No configured DOAC-vs-VKA contrast**; NOT_STATED / not applicable. TAK-442 vs enoxaparin OPEN_LABEL | **X2**, surgery population |
| melatonin-primary-insomnia-sol | PMID **42637255**, MELODY protocol | Melatonin vs placebo blinded; digital CBT-I arm open-label | Melatonin vs placebo **BLINDED** | **X1**, protocol |
| noac-vs-warfarin-af-stroke | PMID **19717844**, dabigatran vs warfarin | Dabigatran doses blinded; adjusted-dose warfarin unblinded | Dabigatran vs warfarin **OPEN_LABEL** | **INCLUDE**, unchanged: topic does not require double blinding |
| probiotics-aad-prevention | PMID **30439760**, probiotic yogurt trial | Probiotic yogurt vs placebo-yogurt blinded; no-yogurt control unblinded | Probiotic yogurt vs placebo-yogurt **BLINDED**; comparison against no yogurt OPEN_LABEL | **INCLUDE**, unchanged |
| probiotics-aad-prevention | PMID **35418412**, Botswana factorial trial | Test-and-treat results not blinded; participants and staff blinded to L. reuteri/placebo assignment | Probiotic vs placebo **BLINDED**; diagnostic-strategy factor OPEN_LABEL | **X2**, acute gastroenteritis rather than antibiotic-associated diarrhea |
| sacubitril-valsartan-hfref | PMID **41912806**, XXB750, **NCT06142383** | ACEi/ARB-background stratum: XXB750 doses/placebo blinded, sacubitril/valsartan open-label. Sacubitril/valsartan-background stratum: XXB750 doses/placebo blinded | Sacubitril/valsartan vs placebo on ACEi/ARB **OPEN_LABEL**. The second stratum is background-only for this topic | **X3**, sacubitril absent from title; unchanged |
| semaglutide-obesity-weight | PMID **42473259**, TTT1, **NCT03899402** | Period 1 semaglutide + insulin vs standard insulin open-label; Period 2 dapagliflozin vs placebo double-blind, with semaglutide background | Semaglutide vs insulin **OPEN_LABEL**, but insulin is not this topic's configured placebo comparator. Period 2 supplies no semaglutide contrast | **X2**, diabetes population |

These nine judgments are readings of the complete held abstracts, not trial-ID
rules in the executable screener. The bounded reader does not claim to extract
every possible arm syntax. Unsupported mixed prose remains MIXED and fails
closed if a double-blind topic reaches the design gate.

## The two aggregate records

Both are in `colchicine-recurrent-pericarditis`, and both remain served **X1**
(review/meta-analysis). Neither permits attribution of blinding to a named
eligible comparison from its abstract; the contrast-level reading is **MIXED**.

| PMID | Held title | What the text distinguishes |
|---|---|---|
| **25000255** | Colchicine for the prevention of pericarditis: what we know and what we do not know in 2014 - systematic review and meta-analysis | Double-blind RCTs and open-label RCTs |
| **22442198** | Efficacy and safety of colchicine for pericarditis prevention. Systematic review and meta-analysis | Double-blind RCTs and open-label RCTs |

## Remaining search candidates: why they are not the comparison shape

Every remaining candidate is accounted for here; its title, complete abstract
and served decision are in `measurement.json`.

| Interpretation | Named PMIDs |
|---|---|
| Open-label treatment with blinded endpoints/adjudication/analysis; not differently blinded randomized treatment comparisons | 34414298 (CONVINCE), 34921756 (MICHELLE), 40023651 (RENOVE), 37675613 (rivaroxaban cerebral venous thrombosis), 31479105 (RE-SPECT CVT), 32589230 (apixaban/enoxaparin), 36347265 (IRONMAN), 17398308 (JELIS), 25305703 (early EPA), 38873793 (RESPECT-EPA), 20609969 (DURATION-3), 41311237 (SMARTEST), 41735586 (canagliflozin CMR), 38569758 (dapagliflozin acute HF) |
| Open-label run-in, extension, follow-up, subsequent treatment or escape from assigned therapy | 27825009 (AIRTRIP), 28892457 (romosozumab/alendronate), 40442449 (ENABLE-Hip), 34696742 (Japanese esketamine), 31734084 (TRANSFORM-3), 38523183 (oral esketamine), 41879760 (GH001), 30132686 (PedPRM follow-up), 16963472 (PEP-CHF), 41772149 (bimagrumab/semaglutide), 30800562 (IOLITE) |
| Single-blind placebo run-in/run-out, with a double-blind randomized comparison | 21091391, 20712869, 19584739, 17875243 (melatonin) |
| Open-label concomitant/background/rescue treatment, not the randomized contrast | 26052984 (sitagliptin cardiovascular outcomes), 22238392 (dapagliflozin on metformin), 40803720 (ASTEROIDS protocol) |
| Blinded randomized efficacy trials combined with additional open-label studies not stated to be randomized | 22346363 (melatonin pooled analysis), 32656217 (Enterococcus faecium SF68 reports) |
| Analysis-display blinding, risk of functional unblinding, or an unmasked statistician; no second differently blinded treatment comparison | 33261932, 41310599, 40736734 (depression reports); 34051877 (COLCORONA) |
| Open/unblinded treatment only; broad search also matches negated “blinded”, mask devices, or unmasked allocation | 33948176 (nosocomial C. difficile), 42035781 (glucose monitoring), 40574561 (CPAP), 37543437 (postoperative HFNO), 25003980 (NHF/Venturi), 38477006 (oxygen devices), 25981908 (FLORALI), 34066244 (HFNC flow settings), 23497557 (NIV after extubation) |
| Proposed future blinded trial, not another comparison in this study | 33080005 (tocilizumab) |

## Implementation and plant

`harness/comparison_blinding.py` reads source spans into allocation groups with
arm labels, background stratum and BLINDED / OPEN_LABEL / NOT_STATED / MIXED.
`comparison_blinding(text, experimental_arm, comparator_arm, background=...)`
answers an ordered pair. Pairs are formed within an allocation sentence, never
across background strata. Prefix/suffix “in a ... fashion”, explicitly labelled
arm groups, dose blinding, and factorial-assignment wording are supported.

The screening gate checks the topic's intervention versus its comparator.
Placebo on a stated comparator background can be that comparator. Interest
present as background in both arms is X-CONTRAST. An explicitly open eligible
pair is X-DESIGN with the comparison named. An unresolved mixed allocation is
X-DESIGN, never rescued by record-level masking. A valid blinded eligible pair
can coexist with an unrelated open-label arm. Uniform blinded trials and the
legacy masking fallback for text without allocation-blinding evidence remain
supported. Both screeners use the new gate.

The registry-form XXB750 test is a **metamorphic plant**, not a claim that an
XXB750 registry row exists in the pinned cache. It preserves PMID 41912806's
complete held abstract and source-backed NCT identity, sets registry-form
allocation/interventions and masking `DOUBLE`, and proves:

- `c15ed111` screen: **INCLUDE**.
- Fixed screen: **X-DESIGN**, “OPEN_LABEL eligible comparison:
  sacubitril/valsartan treatment vs placebo (background angiotensin-converting
  enzyme inhibitor or angiotensin receptor blocker)”.
- Held abstract form: **X3** before and after.
- Held PARADIGM-HF **NCT01035255** and PIONEER-HF **NCT02554890** registry rows:
  **INCLUDE**, with their complete screening tuples unchanged.

The requested `abstract_arms` and `arm_based_comparator` functions are absent
from this branch's pre-change `arm_parse.py`; existing `parse_arm`, exposure
semantics and ordered contrasts were retained rather than importing a different
stack or altering existing tests.

## Served impact and reproduction

**Every served INCLUDE decision changed by this rule: none.** No held record's
primary `screen_record` decision/rule changes versus the pinned pre-change
implementation. This isolates this patch's effect from older differences
between source configs and built pages. It does not claim a full page rebuild.
The hypothetical registry plant is the demonstrated INCLUDE-to-X-DESIGN change.
An additional direct gate audit matches **269 / 269 served INCLUDE rows** to
held source records, including display-prefixed identifiers such as
`PIONEER-HF · NCT02554890`; **0** are refused by the comparison-specific gate.
The measurement records the matched denominator, unmatched IDs (none), and
gate refusals (none) separately from the baseline/current replay delta.

The pin contains served `review.json` screening rows for **32 of the 38** topics.
The six without one are antibiotics-vs-appendectomy-appendicitis,
azithromycin-copd-exacerbation, hfnc-vs-conventional-o2-reintubation,
prone-positioning-ards-mortality, vitamin-d-acute-respiratory-infection and
zinc-common-cold-duration. Their held records were included in the census and
re-screened, but no served decision is invented for them. All nine directly
interpretable mixed-comparison records have pinned served decisions.

Reproduce the census and comparison of the adjudicating rule gate:

```text
python evidence/comparison_blinding/measure.py
```

Validation command (only the requested files):

`	ext
python -m pytest -q -p no:cacheprovider tests/test_comparison_blinding.py tests/test_matched_placebo.py tests/test_screen_contrast_and_ledger.py tests/test_screen_entry.py tests/test_screen_no_outcome_axis.py tests/test_screen_span.py
`

Only the requested pytest files were run. Before edits: **51 passed, 3 failed**.
After edits: **76 passed, 3 failed**, including **25 / 25** new comparison-blinding tests. The same three absent-artifact failures occurred without this change. An intermediate uniform-design evidence-span regression was fixed; its existing test now passes. Existing tests were not edited.
The three baseline failures are documented in `STUCK_FAILURES.md`; they fail
because two pre-existing docs artifacts are absent from this worktree.

## Static versus dynamic disclosure

| Item | Static or dynamic | Evidence / boundary |
|---|---|---|
| Corpus/code pins and reader grammar | Static | Explicit commit hashes and syntax rules; no trial-ID eligibility overrides |
| Nine direct reports, two aggregate reports, candidate adjudications | Static, manually reviewed | Full held abstracts retained in measurement; these classifications do not drive screening |
| Denominators, hashes, candidate search, served rows, replay deltas | Dynamic offline reads | Recomputed by `measure.py` from pinned git objects and current code |
| Registry-form XXB750 and small syntax test cases | Synthetic test inputs, explicitly labelled | Never added to held data, census denominators, served pages or research outputs |
| Effect sizes, trial dates, sample sizes, pooled results | Not modified or newly estimated | This change concerns screening and blinding evidence only |

## Review corrections before commit (Claude, 2026-09-28)

The parser Codex delivered contained branches shaped to the wording of the same nine records this census reads: "which was
blinded as to dose, or to open-label" (TAK-442), "results were not blinded, but ... blinded to X/Y assignment"
(Botswana factorial), "blinded study groups combined" (probiotic yogurt), an `INTERVENTIONS: Blinded ...;` list, and
"Safety measures ... additional ... studies". A parser's agreement with records it was written against is in-sample
and measures nothing, so those branches were **removed** (38 lines). Comparisons the remaining bounded grammar cannot read
now fail closed (`!= BLINDED`); `test_unread_held_shapes_fail_closed` states this, and the table above remains a set of
hand READINGS, not parser validation.

Removing the "Safety measures" branch flipped one served include (melatonin 22346363 -> fail-closed MIXED). Its open-label
cue describes "three additional single-blind and open-label PRM studies", i.e. a different study set. It is replaced by a
GENERAL rule: a cue inside a phrase naming additional/other/further/separate studies or trials, in a sentence with no
allocation verb, is not about this record's comparisons. That rule was written after reading 22346363, so its agreement
there is in-sample; corpus-wide it changes **2 of 4,080** readings, both named: 22346363 (MIXED -> BLINDED) and zinc
15499830 ("10 other double-blind ... trials": BLINDED -> NOT_STATED).

After the corrections: **0 of 4,080** screening decisions change and **0 of 269** served includes change. The XXB750
registry plant (INCLUDE -> X-DESIGN, naming the open-label sacubitril/valsartan comparison) still fires.
