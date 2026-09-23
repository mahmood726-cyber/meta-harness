# Finding: the executable blinding rule accepts "placebo" as proof of double-blinding (screen.py:_double_blind)

## Headline -- two figures that must not be merged
- **On the served site (main 38c04411): the word "placebo" is the ONLY blinding evidence for 5 of the 19 pooled trials on the
  14 pages whose protocol requires double-blind AND placebo-controlled** (CLEAR SYNERGY, SAVOR-TIMI 53, VITAL, ASCEND,
  DAPA-HF), and for 26 of 92 included records with a held record across the 21 topics that carry the rule. There is no P5
  family gate on 38c04411. The rule is load-bearing for 5 served pooled rows today.
- **On branch enforcement-gate (b25027e3): 0 of 19.** Every one of the 19 carries a P5 ELIGIBLE stamp, which requires AACT
  masking DOUBLE/TRIPLE/QUADRUPLE on a registry record verified to be the randomized phase (39 of 39 pooled families
  corpus-wide; prior-phase detector proven on EMPHASIS-HF before use). That is a property of the landing, not of the rule.
- Zhao 2009 (PMID 20146881) is the first nameable wrong admission on the served site: single-blind, admitted by the placebo
  word (lane U5; see CORRECTION below). 
- Direction -- CORRECTED by lane DB (2026-09-22, full held evidence, not abstract text): the rule errs BOTH ways. Refusing
  side: 2 of 15 blinding refusals are false by the named parent trial's held registry masking (39320292 PARADIGM-HF post-hoc,
  33731544 PARALLEL-HF; both sacubitril-valsartan-hfref), plus 1 of 15 contradicted by a held secondary table (27223641).
  My earlier "0 of 15 false refusals" was true of abstract text only and is superseded.
- Served-site figure CORRECTED by lane DB: on 38c04411 the AND pages carry 35 pooled trial-page pairs (the 53 set-asides were
  pooled then), and the placebo word is the only in-screen blinding evidence for **11 of 35**, not 5 of 19 (the 5 of 19 is
  the branch's pooled set). Included cohort is 135, not 92: the 43 ids I could not find are all held in records.json under the
  `ctgov` key / display labels -- my lookup, not a gap. Placebo branch: 30 of 135; of those, 3 of 135 CONTRADICT DOUBLE+ in
  their own registry row (0 of 35 pooled); of the 26 direct-key placebo admissions, 21 are masking-proven elsewhere (19 by
  primary/registry, 2 by a secondary table only), 5 UNPROVEN by any held document, 0 open-label-with-placebo-word.
  **CORRECTION (lane U5, 2026-09-22, both figures previously relayed):** "5 of 26 unproven by any held document" -> **4 of 26**
  -- melatonin 18036082 is proven by a HELD full text DB did not read (`ft_22346363.txt`, the authors' pooled analysis:
  "3-week randomized, double-blind treatment period", citing 18036082 as ref 25). "0 of 26 open-label-with-placebo-word" ->
  **1 of 26 CONTRADICTED**: Zhao 2009, PMID 20146881, omega3-cardiovascular-events, single-blind per two independent public
  reviews (PMC3507701 Table 1 "R, SB, PC" and "1 in a single-blind fashion [19]"; Cambridge S0007114512001559 "Prospective,
  single-blind, randomised, placebo controlled"). Zhao is the first nameable WRONG ADMISSION on the served site 38c04411:
  included under a protocol requiring double-blind, by the placebo word alone; not pooled (included-but-unextracted), so no
  served number moves; the eligible denominator is wrong by one. The other 4 of the 5 are OBTAINABLE from public documents
  (TCTR registry; ClinicalTrials.gov NCT00764010 TRIPLE; NCT00729430 TRIPLE + PMC4328790), so the "permanent disclosure"
  class is empty on this sample. Only 5 of 26 were checked against public sources; lane Z25 is checking the other 25 --
  "1 of 26" is a lower bound until it reports.
- Pre-fix plant observed (lane DB): a synthetic open-label record with "placebo run-in" and no registry masking travels the
  real `screen.run` and is INCLUDED; the paired control with "lead-in period" instead is excluded X-DESIGN.
- Method note, transferable: the first pass of the phase check read a representation whose eligibility rows carry no
  criteria text. The positive control (EMPHASIS-HF) did NOT fire, which is what showed the pass was reading empty fields.
  An absence check against a representation that does not carry the data always succeeds; the positive control is what
  distinguishes "clean" from "unread". No number from that pass was relayed.

Measured on branch `enforcement-gate` = b25027e3 (landed tree) on 2026-09-22; script `andor_audit.py` (scratchpad) plus the
two follow-up probes recorded below. Independent of lane F1's protocol-contract design; this is a defect in the screen as it
runs today, on every commit including main 38c04411 (served).

## The rule
`harness/screen.py:225-233` `_double_blind(rec, text)` returns True if (a) the registry masking field contains DOUBLE/TRIPLE/
QUADRUPLE, or (b) the text contains "double-blind"/"double blind"/"masked", or (c) **the text contains "placebo"** ("a
placebo-controlled RCT is inherently blinded"). Branch (c) makes `include.design_double_blind=true` execute as
"double-blind OR placebo-controlled". `harness/protocol_compiler.py:209-216` knows this and emits DESIGN_MASKING_ANDOR when the
prose says "double-blind, placebo-controlled" (AND) -- on **14 of 32 pages** (colchicine-recurrent-pericarditis,
colchicine-secondary-cv-prevention, dapagliflozin-hfpef-hosp, dpp4-mace-t2d, empagliflozin-hfpef-hosp, finerenone-ckd-t2d-renal,
omega3-cardiovascular-events, pcsk9-mace, semaglutide-obesity-mace, sglt2-ckd-progression, sglt2-hfref-hosp-cvdeath,
sglt2-primary-prevention-hf, spironolactone-hfref-mortality, tranexamic-acid-pph). The divergence is recorded and consumed by
nothing (lane S F1). "masked" is also a substring of "unmasked" (branch b) -- no instance on the corpus, see below.

## Permissive direction (admits what the prose forbids) -- measured
- Topics carrying the rule: **21 of 32**. Included screening records on those topics: 92 with a held record (43 further
  included ids have no entry in `cache/<slug>/records.json` -- registry-only entries; not examined). Branch that admitted them:
  TEXT double-blind 63 of 92, registry masking 3 of 92, **placebo-only 26 of 92**. "unmasked" substring: 0 of 92; "open-label"
  together with placebo-only: 0 of 92.
- Pooled trials on the 14 AND/OR pages: **19 of 19** (unique per page). Admitted by: text double-blind 11, registry masking 3,
  **placebo-only 5** (CLEAR SYNERGY 39555823, SAVOR-TIMI 53 23992601, VITAL 30415637, ASCEND 30146932, DAPA-HF 31535829).
- **Is the bug load-bearing on the landed tree?** For all 19 of 19 pooled trials the P5 family verdict (from the row's
  `admission_verdict` stamp) is ELIGIBLE, and `screen_family` (trial_family.py:351) returns ELIGIBLE only when the AACT
  masking is DOUBLE/TRIPLE/QUADRUPLE. Registry masking for the 5 placebo-only admissions: QUADRUPLE, QUADRUPLE, TRIPLE,
  QUADRUPLE, QUADRUPLE. So on b25027e3 **0 of 19** pooled trials rest on branch (c) alone.
- **On main / the served site (38c04411) there is no P5 gate**, so branch (c) was the ONLY blinding evidence for those
  **5 of 19** pooled trials on the AND/OR pages, and for 26 of 92 included records corpus-wide. The reassurance holds for
  the branch only because the enforcement gate landed; it is not a property of the rule.
- Demonstrated false positive of the chain's abstract reading (lane F1): TECOS (PMID 26052984) read as `open_label` from
  "Open-label use of antihyperglycemic therapy was encouraged" -- background therapy, not masking. This is the eligibility
  chain's regex, a sibling of the same rule family: masking inferred from abstract words.

## Refusing direction (refuses what the prose allows) -- measured
- X-DESIGN exclusions on the 32 pages: 32 on 7 pages, of which **15 are the blinding branch** (the other 17 are
  `design_any` context rules sharing the X-DESIGN id -- a second overload: one rule id, two rules).
- Of the 15: 2 mention "blind" -- JELIS 17398308 and 25305703, both "open-label, blinded endpoint" (PROBE), **correctly
  refused**. The other 13 have no blinding word and no registry masking (or NONE/SINGLE): refused with the reason printed --
  fail-closed, not demonstrably wrong. **0 of 15 false refusals detectable from held text.** The rule errs in one direction
  on this corpus.

## What the fix is (one sentence each; not implemented)
1. Branch (c) goes: "placebo" is evidence of a placebo comparator (X3 territory), not of masking. Masking is proven by the
   registry masking field, by an explicit masking word, or by a hand record; absent all three the decision is
   BLINDING_NOT_PROVEN (typed, printed), not "include".
2. `_double_blind` should test "masked" as a word, not a substring.
3. Split the X-DESIGN id: blinding refusals and context refusals are different rules and must be countable apart.
4. Plant (pre-fix observation needed before any fix lands): a record whose text says "open-label ... placebo run-in" with no
   registry masking -> today included; after the fix -> BLINDING_NOT_PROVEN.

## Not decided here
Whether the 14 protocols mean AND (then the config is wrong and the fix above makes the screen agree with the prose) or the
prose is stale (then 14 dated amendments). Mahmood's. Either way branch (c) is wrong as a *rule*: a placebo word does not
prove masking.

## Addendum 2026-09-22 -- "proven by the registry route" checked against the phase-record failure (EMPHASIS-HF)
The reassurance "19 of 19 pooled trials on the AND/OR pages have registry masking DOUBLE+" assumed the registry record is the
randomized phase. Checked: for all 39 pooled trial-page pairs on the served corpus (19 on the 14 AND/OR pages), the resolved
family's AACT designs row is allocation RANDOMIZED (39 of 39), masking DOUBLE/TRIPLE/QUADRUPLE (39 of 39), intervention
model PARALLEL 36 / FACTORIAL 3; a prior-phase phrase detector (proven on the EMPHASIS-HF criteria as positive control
before use: fires on "participated in the") finds 0 of 19 on the AND/OR pages and 1 of 39 corpus-wide -- STEP 4
NCT03548935, whose criteria list an "Extension phase" addendum while its design row is the main randomized phase (not the
failure). First pass of this check read the compact rows file, whose eligibilities rows carry no criteria text: the positive
control did NOT fire, so that pass measured empty fields and was discarded; criteria come from
`trial_family.prepare()[..]['population']['criteria']['value']`.
Prevalence of the class (non-randomized design row + randomised publication): 7 of 634 families with a design row, all 7
unpooled; lane PH reads them. See CONVERGENCE note.

## Prevalence of wrong admissions through the placebo branch (lane Z25, 2026-09-22)
Positive control run and recorded FIRST (Zhao found single-blind in a freshly fetched public review, bound to reference B19
by exact PMID and DOI) -- then the other 25 checked against public registry records, PMC/Europe PMC full texts and
independent review design/RoB tables. Result: **25 of 25 CONFIRMED_DOUBLE_BLIND, 0 PUBLIC_CONTRADICTS_HELD, 0 PUBLIC_SILENT,
0 HELD_EVIDENCE_WRONG_TARGET; with the control, 25 of 26 confirmed and 1 of 26 contradicted.** "1 of 26" survives a public
check of the whole cohort. Coverage limit stated by the lane: an independent review table covering the exact report or its
linked randomized parent was readable for 23 of 25; the 2 gaps (COLCAD 41605493, DO-HEALTH 38199870) have affirmative
registry/primary masking evidence instead. Counts are report-page pairs, not distinct trials (GISSI-HF reports share a
parent; CANVAS combines component trials).
Zhao's served consequence, from the 38c04411 bytes: included, unextracted, contributing to 0 of 3 outcome pools (all three
list OUTCOME_NOT_IN_SOURCE). The wrong admission is in the eligible denominator, not in any served number.
NOTE the lane's correction of my brief: the omega3 protocol's design line is "double-blind, placebo-controlled OR blinded
inert-control RCT" -- so for THIS topic the prose itself is a disjunction, and Zhao's single-blind status is the violation,
not the placebo branch's AND/OR gap. The AND/OR finding stands for the 14 pages whose prose says AND; omega3 is not one of
them.
