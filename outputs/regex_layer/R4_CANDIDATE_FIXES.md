# R4 candidate fixes: seven harness/extract.py patterns, found by classifying their R2 disagreements

**Status: text only. Nothing here has been applied.** `harness/extract.py` and `harness/whole_numbers.py` are pinned
and were not changed. Before any candidate lands, **its served radius has to be measured**: which served rows,
effects, k values or scales change. Candidates change a pattern's own output on held sentences and nothing more
(see "Indicative reach" below). That count is not the served radius.

## How this was produced (2026-09-25)

* **Population.** Every labelled item for `_ARMP, _K, _MEAN_SD, _MED_IQR, _SUBGROUP, _RECURRENT_PERSONTIME, _ANCHOR_RX`
  in `registry/model_proposals/regex_label.json` and `regex_label_deep.json` (reader 1), plus their `_reader2`
  counterparts (reader 2). Each sentence was recovered by sha256 over `regex_layer.measure.held_sentences()`. The regex
  output was **recomputed with the served (WholeNumbers-wrapped) pattern** rather than read from the recorded
  `verification.regex`.
* **Disagreeing item.** An item whose regex output differs from **at least one** reader's label (a reader whose
  proposal was VERIFIER_REFUSED counts as disagreeing).
  N = `_ARMP` 20 of 80 · `_K` 41 of 80 · `_MEAN_SD` 31 of 80 · `_MED_IQR` 34 of 41 · `_SUBGROUP` 24 of 80 ·
  `_ANCHOR_RX` 14 of 80 · `_RECURRENT_PERSONTIME` 17 of 80.
* **Classes.** Every disagreeing item was read. An item can belong to more than one class, most often in `_MED_IQR`.
  The verdicts:
  * **REGEX** means the pattern fails a requirement of its spec. Each such class gets one requirement plant in
    `regex_layer/specs.py` and a strict-xfail `KNOWN_DEFECTS` entry (`RX-X<n>`) in `regex_layer/defects.py`.
  * **LABEL** means the labeller misread the sentence. This is a finding about the labeller, and the item is cited.
  * **AMBIGUOUS** means the spec does not decide the case, or the case is out of reach of a surface pattern. These
    classes are not planted.
* **Candidate check.** Each candidate below was compiled in a scratch process, with `extract.*` monkeypatched in memory
  only. It passes **every** plant of its pattern: the existing plants and the new ones. It was also scored against the
  labelled items of both readers (table at the end).

## Summary of located defects

| id | pattern | class | n of N | reach |
|---|---|---|---|---|
| RX-X1 | _ARMP | `c of N patients (p%)` reads N as the count | 5 of 20 | reachable; masked by % corroboration |
| RX-X26 | _ARMP | `c/N (p%)` reads N as the count | 3 of 20 | reachable; masked likewise |
| RX-X2 | _ARMP | count spelled as a word (`nine (7.5%)`) | 3 of 20 | reachable (arm pair lost) |
| RX-X3 | _ARMP | event noun other than patients/cases (`324 hospital deaths (34.1%)`) | 2 of 20 | reachable |
| RX-X4 | _ARMP | digit of a hyphenated name (`Pro-2 (1.2%)`) | 1 of 20 | reachable |
| RX-X5 | _ARMP (whole_numbers) | U+2008 thousands separator gives the fragment `952` | 1 of 20 | reachable (1 held sentence) |
| RX-X6 | _K | any word before `RCTs` is taken as k (`for`, `Randomized`) | 28 of 41 | **reachable, served**: `_parse_k` returns None in 177 of 645 held abstracts with a later numeral match; K_SHADOW.json has 16 topics |
| RX-X7 | _K | adjective between the numeral and the noun (`six eligible RCTs`) | 1 of 41 | reachable |
| RX-X8 | _K | hyphenated numeral read by its tail (`Fifty-five` → `five`) | 1 of 41 | **reachable, served**: 25→5, 28→8 in 2 held abstracts |
| RX-X9 | _MEAN_SD | header `mean (SD)` followed by bare `X (Y)` | 12 of 31 | reachable |
| RX-X10 | _MEAN_SD | `%` on the mean (`45%±10%`) | 6 of 31 | reachable |
| RX-X11 | _MEAN_SD | unit word not in {days, hours, min, points} (`years (SD 9.8)`) | 2 of 31 | reachable |
| RX-X12 | _MEAN_SD | SD-marker punctuation (`[SD, 16]`, `(SD, 16.3)`, `(±5.0)`) | 5 of 31 | reachable |
| RX-X13 | _MEAN_SD | negative mean loses its sign | 2 of 31 | reachable; flips an MD's direction |
| RX-X14 | _MEAN_SD | `±` read as SD in a sentence that says SE / 95% CI | 3 of 31 | reachable |
| RX-X15 | _MEAN_SD | visit window `day 12 ± 2` | 1 of 31 | reachable |
| RX-X16 | _MED_IQR | header `median (IQR)` followed by bare `X (a-b)` | 12 of 34 | reachable |
| RX-X17 | _MED_IQR | unit other than days/hours/min/points (`years`, `months`, `%`, `mg/L`) | 12 of 34 | reachable |
| RX-X18 | _MED_IQR | `median` separated from the value (`median duration … was 19.4`) | 15 of 34 | reachable |
| RX-X19 | _MED_IQR | comma after the label (`IQR, 2-7`) | 9 of 34 | reachable |
| RX-X20 | _MED_IQR | unbracketed `, IQR a-b` | 2 of 34 | reachable |
| RX-X21 | _MED_IQR | negative values | 3 of 34 | reachable |
| RX-X22 | _MED_IQR | comma-separated bounds `(-0.1, 1.3)` | 2 of 34 | reachable |
| RX-X23 | _MED_IQR | thousands separators | 1 of 34 | reachable |
| RX-X24 | _MED_IQR | `median, 2 […]` | 1 of 34 | reachable |
| RX-X25 | _MED_IQR | `(IQR …)` with no `median` before the value (second arm) | 6 of 34 | reachable |
| RX-X37 | _MED_IQR | nested label `interquartile range (IQR) 47-70` | 2 of 34 | reachable |
| RX-X27 | _SUBGROUP | `among patients with/who` fires on the trial's own population | 12 of 24 | reachable (refuses the effect) |
| RX-X28 | _SUBGROUP | plural `sensitivity analyses` | 3 of 24 | reachable (9 held result sentences) |
| RX-X29 | _SUBGROUP | plural `subgroups` | 1 of 24 | reachable (123 held sentences) |
| RX-X30 | _ANCHOR_RX | plural `endpoints` / `outcomes` | 2 of 14 | reachable (178 held sentences) |
| RX-X31 | _RECURRENT_PERSONTIME | `N times` as a multiplier (`4 times more likely`, `1.38 times` via `38 times`) | 7 of 17 | reachable |
| RX-X32 | _RECURRENT_PERSONTIME | `N times` as a dosing frequency (`3 times a week`) | 4 of 17 | reachable |
| RX-X33 | _RECURRENT_PERSONTIME | `recurrent hospitalisations` (only `recurrent event(s)` read) | 1 of 17 | reachable |
| RX-X34 | _RECURRENT_PERSONTIME | `number of recurrences` | 1 of 17 | reachable |
| RX-X35 | _RECURRENT_PERSONTIME | person-time other than years (`per 100 patient-cycles`) | 1 of 17 | reachable |
| RX-X36 | _RECURRENT_PERSONTIME | `per 1000 patient-years` (found by the plant, not by a label) | 0 of 17 | reachable (19 held sentences) |

Plant ids are listed in `regex_layer/defects.py` under each RX-X id. The ids are not contiguous: RX-X26 and RX-X37
were split out of RX-X1 and RX-X16 after the first numbering.

---

## _ARMP (N = 20)

Current:
```
(\d+)\s+(?:patients?|participants?|cases?|subjects?)?\s*[\(\[]\s*(\d+(?:\.\d+)?)\s*%\s*[\)\]]
```

| class | items | verdict |
|---|---|---|
| RX-X1: the denominator of `c of N patients (p%)` is read as the count | 5: bd52, d3c0, e037, f819, fbe8 | REGEX. The spec says "with the denominator elsewhere". Reader 2 labelled the numerator (`386`, 16.3) on 4 of these; reader 1 labelled nothing. Both readings rule out the regex's `2373`. |
| RX-X26: the same misreading after a slash | 3: 15d2, 2554, 96f2 | REGEX |
| RX-X2: a word count (`nine`, `four`, `two`) | 3: 244a, a352, ab60 | REGEX |
| RX-X3: an event noun (`hospitalisations`, `hospital deaths`) | 2: 0362, 4eac | REGEX |
| RX-X4: a digit inside a name (`Pro-2`) | 1: 1b00 | REGEX |
| RX-X5: a U+2008 grouped number (`11 952`) | 1: 37f5 | REGEX (in the wrapper `harness/whole_numbers.py`) |
| baseline or screening proportion (`1832 (21.8%) were women`, `27 (37.5%) met criteria`, `303 participants (17.9%)`) | 3: c96b, e7f0, c912 (split: r1 yes, r2 no) | AMBIGUOUS. The shape is the same as an event count. "Event" is a semantic property the caller has to supply (outcome keyword plus denominator corroboration), not a surface regex. |
| LABEL errors | e81e: both readers say "no event count" for `(59 [4.5%] vs. 5 [0.8%])` discontinuations; the regex is right. d28e: reader 1 missed six per-arm safety counts that reader 2 and the regex read. a352: reader 2 labelled nothing for `nine (7.5%) … 20 (17%) patients`. | LABEL |

Candidate. `OF_GUARD` refuses a number preceded by `<count> of `, which fixes RX-X1 without losing `a total of 334
patients (3.5%)`. An earlier draft used `(?<!\bof )` and lost exactly that sentence (pcsk9-mace 30403574 s8); the
labelled-item check caught it.
```
OF_GUARD = (?<!\d of )(?<!(?i:one) of )(?<!(?i:two) of ) … one lookbehind per number word … (?<!(?i:twenty) of )
(?<![/\w.-]) OF_GUARD (\d+|(?i:one|two|…|twenty))\s+
(?:(?:hospital\s+)?(?:patients?|participants?|cases?|subjects?|deaths?|events?|hospitali[sz]ations?|admissions?|women|men)\s*)?
[\(\[]\s*(\d+(?:\.\d+)?)\s*%\s*[\)\]]
```
RX-X5: in `harness/whole_numbers.py`, `SEP += "  "`. This change affects **every** wrapped pattern, so its
radius has to be measured across all eleven.
Downstream: `_arm_counts` does `int(m.group(1))`, so a word count needs the `_WORDNUM` mapping before RX-X2 can land.
Plants to pass: `_ARMP-accept-0..2`, `_ARMP-refuse-0..5`.

## _K (N = 41)

Current:
```
(\d+|[A-Za-z]+)\s+(?:randomi[sz]ed\s+(?:controlled\s+)?trials|controlled\s+(?:clinical\s+)?trials|RCTs)   (re.I)
```

| class | items | verdict |
|---|---|---|
| RX-X6: a non-number word is captured as k | 28 (04ba, 0a60, 155b, 2382, 258d, 2e58, 3257, 3bad, 4076, 4cec, 4ea5, 5af9, 720f, 77d1, 832a, 83c1, 9337, 97a5, a2fc, b032, b165, b1de, b884, b935, c1c4, d3b9, e654, f807) | REGEX. This is the served failure recorded in K_SHADOW.json. |
| RX-X7: an adjective between the numeral and the noun | 1 (c1c4) | REGEX |
| RX-X8: a hyphenated numeral read by its tail | 1 (9ada) | REGEX. **Serves a wrong k** (25→5, 28→8). |
| bare `N trials` with no "randomised" or "RCT" (`Fifteen trials were included`, `2 trials, 1770 participants`, `63 included trials`, `One trial`) | 8 (1454, 15c1, 5edb, 7fb7, 94fe, a1c5, bc64, c878) | AMBIGUOUS. The spec says "randomised (controlled) trials". Half of these are per-analysis counts (`2 trials, 1770 participants`), not the review's k, and the readers split on 4 of the 8. |
| sub-counts or anaphora (`41 with single strains, 22 …`; `(n = 5)`; `the remaining three`) | 3 (1f54, 6bf9, b993) | LABEL (reader 1 over-reach on 1f54 and 6bf9: sub-counts of a stated total). b993 is AMBIGUOUS. |
| reader 2 refused (wrong field name `number`) | 1 (ff00) | LABEL (schema). Reader 1 agrees with the regex. |

Candidate:
```
(?<![\w-])(\d+|(?:(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-)?(?:one|two|three|four|five|six|seven|eight|nine)
          |ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)
\s+(?:(?:eligible|included|additional|large|larger|small|smaller|published|separate|individual)\s+)?
(?:randomi[sz]ed\s+(?:controlled\s+)?trials|controlled\s+(?:clinical\s+)?trials|RCTs)          (re.I)
```
Downstream: `_WORDNUM` must map the compounds (`fifty-five` → 55) and the tens.
Plants to pass: `_K-accept-0..2`, `_K-refuse-0..1`.

## _MEAN_SD (N = 31)

Current:
```
(\d+(?:\.\d+)?)\s*(?:days?|hours?|minutes?|min|points?)?\s*
(?:\(\s*(?:SD|standard deviation)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*\)|(?:±|\+/-|\+-)\s*(\d+(?:\.\d+)?))       (re.I)
```

| class | items | verdict |
|---|---|---|
| RX-X9: header `mean (SD)` / `mean [SD]` followed by bare `X (Y)` | 12 (24f9, 691e, 6b58, 7660, 81e8, 92f3, a7f1, b981, c1f4, ce79, dd70, ad61), plus later arms in ae0a, 616e, cbd1 | REGEX |
| RX-X10: `%` on the mean | 6 (23a1, 963e, 63d0, e987, cbd1, adbd) | REGEX |
| RX-X11: another unit word | 2 (ae0a, 616e) | REGEX |
| RX-X12: SD-marker punctuation | 5 (5bf8, dd4c, 616e, cbd1, adbd) | REGEX |
| RX-X13: the sign is dropped | 2 (0b8f, 8c9e) | REGEX |
| RX-X14: SE or CI after `±` | 3 (a4cc, bfe1, 21f5) | REGEX |
| RX-X15: visit window `day 12± 2` | 1 (089b) | REGEX |
| European decimal comma plus `DS` (`56,6 DS ± 16,7`) | 1 (2c40) | AMBIGUOUS. A decimal-comma reader risks thousands separators (see lessons: European decimal regex). |
| `difference 36 ± 11 m` with the dispersion unlabelled | 1 (c74e; r1 yes, r2 no) | AMBIGUOUS |
| LABEL errors | r2 missed b981, dd70, cbd1, e987 (all plain mean-SD); r1 missed 7660; r2 quoted the unit into the SD on 0ad7 (`0.96 mm`). Both readers said "no" on 8e5c `mean age was 72.4 (+/-14.0)`, which is a mean ± SD by the spec. | LABEL |

Candidate. There is one pattern, plus a served wrapper, because RX-X9 and RX-X14 need sentence context. A single
regex cannot express that context, and the plants are checked against the served object, which is already a wrapper
(WholeNumbers).
```
pattern  (?<!\bday )(?<!\bdays )((?:(?<![\w.])-)?\d+(?:\.\d+)?)\s*
         (?:%|days?|hours?|minutes?|min|points?|years?|months?|weeks?|mm\s?Hg|kg|cm|g/L|mg/dL)?\s*
         (?:[\(\[]\s*(?:SD|standard deviation)\s*[:=,]?\s*(\d+(?:\.\d+)?)\s*%?\s*[\)\]]
           |[\(\[]?\s*(?:±|\+/-|\+-)\s*(\d+(?:\.\d+)?))                                               (re.I)
wrapper  if the sentence matches  standard error|\bSEM?\b|(?:±|\+/-)\s*95\s*%  -> drop the ± matches (keep '(SD Y)')
         if the sentence matches  \bmean\b[^.;()\[\]]{0,20}[\(\[]\s*(?:±\s*)?(?:SD|standard deviation)\s*[\)\]]
            -> after it, also read  VAL\s*UNIT\s*[\(\[]\s*(\d+(?:\.\d+)?)\s*[\)\]]  as (mean, sd, None)
               ('119 [63.3%]' is excluded because '%' precedes the bracket close)
```
Plants to pass: `_MEAN_SD-accept-0..6`, `_MEAN_SD-refuse-0..2`.

## _MED_IQR (N = 34, all false negatives)

Current:
```
median\s*(?:of\s*)?(\d+(?:\.\d+)?)\s*(?:days?|hours?|minutes?|min|points?)?\s*
[\(\[]\s*(?:IQR|interquartile range)\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)             (re.I)
```

| class | items | verdict |
|---|---|---|
| RX-X16: header form | 12 (0035, 0de4, 2bec, 3ee2, 4271, 51d5, 5503, 9606, 9eef, c10e, e39c, f3f7) | REGEX |
| RX-X17: unit word | 12 (1502, 25b0, 6dd9, 767a, 8683, 8ebe, 9622, 9823, d333, fefe, b05d, baf2) | REGEX |
| RX-X18: `median` separated from the value | 15 (0b58, 1502, 25b0, 5885, 5a6c, 66a2, 67cf, 767a, 8683, 8f11, ce6e, fefe, 8ebe, 9622, b05d) | REGEX |
| RX-X19: comma after the label | 9 (1502, 5a6c, 67cf, 8683, 8f11, 940e, aa82, ce6e, fefe) | REGEX |
| RX-X20: unbracketed `, IQR` | 2 (b05d, baf2) | REGEX |
| RX-X21: negative values | 3 (9823, e39c, f3f7) | REGEX |
| RX-X22: comma-separated bounds | 2 (e39c, f3f7) | REGEX |
| RX-X23: thousands separators | 1 (5503) | REGEX |
| RX-X24: `median, 2` | 1 (aa82) | REGEX |
| RX-X25: `(IQR …)` without `median` before the value | 6 (0b58, 5a6c, 66a2, 8f11, ce6e, f263) | REGEX |
| RX-X37: nested `interquartile range (IQR)` | 2 (8ebe, f263) | REGEX |
| LABEL (format) | reader 2 quoted the unit or currency into the median field on 6 items (5503 `USD 41,102`, 5a6c `3 days`, 6dd9 `3.9 years`, 767a `76 years`, 940e `9 days`, 9622 `7.2%`). These stay disagreements under any regex. | LABEL |

Candidate. There is one pattern plus a header wrapper (RX-X16), as for `_MEAN_SD`. `median` becomes an optional
prefix because an explicit IQR label already marks the value as a median (RX-X25).
```
pattern  (?:median\b[^.;]{0,80}?)?
         ((?:(?<![\w.])-)?(?:\d{1,3}(?:,\d{3})+(?![\d.])|\d+(?:\.\d+)?))\s*
         (?:[A-Za-z%µ/][\w%µ/]*(?:\s+[A-Za-z][\w/]*)?)?\s*
         (?:[\(\[]|,)\s*(?:IQR|interquartile range(?:\s*\(IQR\))?)\s*[:=,]?\s*
         VAL\s*(?:-|–|to|,)\s*VAL                                                                        (re.I)
wrapper  if the sentence matches  \bmedian\b[^.;()\[\]]{0,30}[\(\[]\s*(?:IQR|interquartile range)\s*[\)\]]
            -> after it, also read  VAL\s*UNIT\s*[\(\[]\s*VAL\s*SEP\s*VAL\s*[\)\]]
```
Downstream: `extract_continuous` does `float()`, so RX-X23 needs the commas stripped first. RX-X25 relies on "IQR
implies median". On e0d2 (`13.0 (IQR, 8.0-25.3) %`) both readers said "not a median", so this step is itself
AMBIGUOUS and has to be part of the radius measurement.
Plants to pass: `_MED_IQR-accept-0..11`, `_MED_IQR-refuse-0`.

## _SUBGROUP (N = 24)

Current:
```
\bper[-\s]?protocol\b|\bpost[-\s]?hoc\b|\bsubgroup\b|\bsensitivity analysis\b|\bas[-\s]?treated\b|\blowest in\b|
\bhighest in\b|\bamong (?:those|patients) (?:with|who)\b|\brestricted to\b|\bexploratory analysis\b              (re.I)
```

| class | items | verdict |
|---|---|---|
| RX-X27: `among patients with/who` names the trial's own population | 12 (0a03, 1285, 35ca, 673e, 6b91, 967d, 9b83, a001, afd6, de1c, f34e, f3dc), both readers agreeing on all 12 | REGEX |
| RX-X28: plural `sensitivity analyses` | 3 (1fe1, 5657, b1f0) | REGEX. Caveat: all three are methods sentences, and reader 1 is inconsistent here (yes on these, no on fc53 and f071). |
| RX-X29: plural `subgroups` | 1 (f140, reader 2 only) | REGEX for the form |
| methods or aim sentence naming such an analysis, no result (`subgroup analyses … were performed`, `reserved for sensitivity analysis`, `restricted to those with …`, `in these subgroup of patients`) | 4 (fc53, f071, 019e, ffb8): r1 no, r2 yes | AMBIGUOUS. The spec is about results. For the guard's use (refusing an effect), firing on these is harmless. |
| reader 2 only, no pattern keyword (`among participants on statin therapy`, `in patients with PCR-proven COVID-19`, `trials enrolling vitamin D-deficient women`, `primary exploratory efficacy outcome`) | 4 (1785, 7307, d56a, d97e) | AMBIGUOUS. 7307 leans LABEL: it describes a trial population. |

Candidate:
```
\bper[-\s]?protocol\b|\bpost[-\s]?hoc\b|\bsubgroups?\b|\bsensitivity analys[ie]s\b|\bas[-\s]?treated\b|\blowest in\b|
\bhighest in\b|\bamong those (?:with|who)\b|\brestricted to\b|\bexploratory analys[ie]s\b                        (re.I)
```
Honest cost: dropping `among patients (with|who)` also loses a genuine subgroup written that way (`Among patients with
diabetes, the HR was …` inside a non-diabetes trial). No surface token separates the two. The radius measurement must
count the served effects the current guard refuses through this alternative, and the effects the candidate would let
through. 9b83 (`… and among those who are not`, a background sentence) still fires under the candidate.
Plants to pass: `_SUBGROUP-accept-0..2`, `_SUBGROUP-refuse-0..1`.

## _ANCHOR_RX (N = 14)

Current:
```
\b(?:co-?primary|primary)\s+(?:composite\s+|study\s+|efficacy\s+|main\s+|clinical\s+)*(?:outcome|end[\s-]?point)\b   (re.I)
```

| class | items | verdict |
|---|---|---|
| RX-X30: plural `endpoints` / `outcomes` | 2 (855c, fb67), both readers | REGEX |
| a result or narrative sentence that mentions the primary outcome (`the effect … on the primary outcome was consistent`, `for the primary endpoint, …`, `the primary end point occurred in 5.5%`) | 10 (2d71, 4eb7, 58b5, 5b95, 61c8, 6407, 6787, 868d, e523; ec9c split) | LABEL against the literal spec, or the spec wording is AMBIGUOUS. The readers took "names the primary outcome" to mean "defines it". The pattern's role is `conjunct:_DEF_CUE` in extract.py; target_endpoint.py reads it standalone to learn that a result concerns the primary. Firing on these sentences is the intended behaviour, so they are not a regex defect. |
| `primary exploratory efficacy outcome` | 1 (d97e) | AMBIGUOUS: it is the primary *exploratory* outcome. |
| `1 primary event (symptomatic ICH)` | 1 (658c, reader 2) | LABEL: this counts an event; it does not name the outcome. |

Candidate: `…(?:outcome|end[\s-]?point)s?\b`. Under the readers' "defines" reading this **adds** two disagreements
(0633 `336 primary endpoints (22.4 per 100 patient-years)` and 65fa `the 2 co-primary outcomes`) and resolves the two
RX-X30 items. The net labelled score does not move (14 → 14). The case for the fix rests on the plant, not on the
labels.
Plants to pass: `_ANCHOR_RX-accept-0..1`, `_ANCHOR_RX-refuse-0`.

## _RECURRENT_PERSONTIME (N = 17)

Current:
```
\b\d[\d,]*\s+times\b|per\s+(?:100\s+)?(?:patient|person)[-\s]?years?|
\btotal\s+(?:number\s+of\s+)?[\w\s]{0,30}?(?:hospitali[sz]ation|event)s\b|recurrent[-\s]events?\b                 (re.I)
```

| class | items | verdict |
|---|---|---|
| RX-X31: multiplier `N times more/higher` (and `1.38 times` read as `38 times`) | 7 (1f11, 396c, 5880, 6696, c0ec, d450, d838) | REGEX |
| RX-X32: dosing frequency | 4 (2509, 3291, 6d4d, 9392) | REGEX |
| RX-X33: `recurrent hospitalisations` | 1 (8a87) | REGEX |
| RX-X34: `number of recurrences` | 1 (03c0) | REGEX |
| RX-X35: `per 100 patient-cycles` | 1 (c293) | REGEX |
| RX-X36: `per 1000 patient-years` | 0 labelled | REGEX (found by the plant; 19 held sentences) |
| `total gastrointestinal adverse events` as a category name | 1 (fb23) | AMBIGUOUS. Tightening `total …` to `total number of` would also lose `total HF hospitalisations (first and recurrent)`. |
| `rates of recurrence of acute bronchitis`; `number, site, duration of infection` | 2 (67cc, 7e44) | AMBIGUOUS. The readers quoted different spans on 7e44. |

Candidate:
```
(?<![\d.,])\d[\d,]*\s+times\b(?!\s+(?:more|less|higher|lower|greater|smaller|larger|as|stronger|weaker|a|an|per|daily|weekly|monthly|each|every)\b)
|per\s+(?:1[,\s]?000\s+|100\s+|10[,\s]?000\s+)?(?:patient|person)[-\s]?(?:years?|months?|cycles?|days?)
|\btotal\s+(?:number\s+of\s+)?[\w\s]{0,30}?(?:hospitali[sz]ation|event)s\b
|recurrent[-\s](?:events?|hospitali[sz]ations?|admissions?|exacerbations?|episodes?)\b
|\bnumber\s+of\s+(?:recurrences|exacerbations|episodes|relapses)\b                                               (re.I)
```
Residuals: 1f11 (`more than 20 and 2 times`) still fires. The candidate stops firing on db44 (`SC 1.6 times/day`),
which both readers marked as a per-time rate. That item is AMBIGUOUS (a stool-frequency mean, not an IRR footprint),
but it is a labelled item the candidate newly disagrees with. The consumer only consults this pattern for a `rate
ratio` / RR label (`_effect_from_match`, `absence.py:184`), so its radius is the set of served effects whose IRR-vs-RR
scale changes.
Plants to pass: `_RECURRENT_PERSONTIME-accept-0..4`, `_RECURRENT_PERSONTIME-refuse-0..2`.

---

## Candidates scored on the labelled items (scratch run, 2026-09-26)

"Any" means the regex differs from at least one reader. "Every" means it differs from all readers who answered.

| pattern | disagree-any: current → candidate | disagree-every: current → candidate | labelled items newly disagreeing |
|---|---|---|---|
| _ARMP | 20 → 10 | 18 → 3 | 0 |
| _K | 40 → 13 | 34 → 7 | 0 |
| _MEAN_SD | 31 → 11 | 24 → 5 | 1: 8e5c, a label error (see above) |
| _MED_IQR | 34 → 8 | 34 → 2 | 1: e0d2, ambiguous (RX-X25) |
| _SUBGROUP | 24 → 10 | 15 → 1 | 0 |
| _RECURRENT_PERSONTIME | 17 → 5 | 17 → 5 | 1: db44, ambiguous |
| _ANCHOR_RX | 14 → 14 | 12 → 12 | 2: 0633, 65fa (readers' "defines" reading) |

The `_K` total here is 40 rather than 41 because the scratch scorer skips VERIFIER_REFUSED proposals (ff00).
Everything that still disagrees after a candidate belongs to a LABEL or AMBIGUOUS class listed above. These are
**labelled-item** figures and are not the served radius.

## Indicative reach (NOT the served radius)

These are held abstract sentences (35,673 distinct) whose own pattern output changes under the candidate:
`_ARMP` 207 · `_K` 868 · `_MEAN_SD` 129 · `_MED_IQR` 105 · `_SUBGROUP` 286 · `_RECURRENT_PERSONTIME` 63 ·
`_ANCHOR_RX` 179. Each still has to be pushed through the consumer (`_arm_counts`, `_parse_k`, `extract_continuous`,
`_is_subgroup_sentence`, `_effect_from_match`/`absence.py`, `_effective_kws`/`target_endpoint.py`) and diffed on
served rows **before** it lands. RX-X5 changes `whole_numbers.SEP` and so touches all eleven wrapped patterns.
