# Ordered-contrast census of every served topic's primary pool (V1.1, report only)

Nothing served is changed. `cross_topic_census.py` fetches each live `review.json` from Pages. It applies the V1 verifier's own
ordered-contrast and measure rules, loaded from `oc/ordered-contrast` @ 23642e0d (blob `d3fefa60…`), with each topic's own
vocabulary. It then classifies every trial row of the primary outcome. Output: `cross_topic.json`.

## Result: 41 of 81 ratio rows cannot have direction or estimator proven from an effect clause

The universe is 32 pages and 87 primary-outcome rows. Of these, 6 are continuous (MD/SMD) and fall outside a ratio-orientation
check, leaving 81 ratio rows.

| class | rows | meaning |
|---|---|---|
| PROVEN | 40 | the clause orders the arms (experimental is the numerator), states a measure equal to the label, and the rates do not contradict |
| COUNTS_DERIVED | 13 | the ratio is computed from arm counts: no stated estimator exists to prove |
| NO_CLAUSE_LOCATED | 13 | the row's own tuple is in neither `endpoint_result_span` nor the `source` quotation (converted CIs, derived effects) |
| UNORDERED | 8 | a clause holds the tuple, but its words name one arm or none ("ertugliflozin reduced risk (HR 0.70)", "The relative risk for AAD was 0.7") |
| REGISTRY_ANALYSIS | 5 | ClinicalTrials.gov results analyses: orientation is the registry's group order, not words |
| REVERSED | 1 | **a parser gap, not a served reversal** (below) |
| LABEL_MISMATCH | 1 | **a served mismatch** (below) |

GLP-1, the one bundled topic, is 8 of 8 PROVEN.

## The two rows that name a defect

- **LABEL_MISMATCH, served:** tocilizumab-covid19-mortality, PMID 33933206 (RECOVERY). The clause states "rate ratio 0.85
  (95% CI 0.76-0.94)"; the row is labelled `RR` (risk ratio). A rate ratio is not a risk ratio. Report only: this changes no
  served content.
- **REVERSED, a parser gap in lane OC's rules:** spironolactone-hfref-mortality, PMID 10471456 (RALES). "386 deaths in the placebo
  group (46 percent) and 284 in the spironolactone group (35 percent; relative risk of death, 0.70 …)". ORDER_OF_MENTION reads
  placebo first. The per-arm rates prove spironolactone/placebo, but the rate witness reads only "%", not "percent", so it was not
  informative. Only GLP-1 is bundled, so no served verdict is affected. Fix on branch `oc/v11-contrast-rules`.

## The other parser gaps and the vocabulary gap

- ticagrelor-vs-clopidogrel-acs, PMID 26376600: "… 9.0% and 6.3% of ticagrelor- and clopidogrel-treated patients, respectively
  (HR 1.47)". The rules treat "-treated" as a non-arm suffix (it was meant for "placebo-controlled"), so clopidogrel was never
  seen. Fix on `oc/v11-contrast-rules`.
- dpp4-mace-t2d, PMID 28893244: "omarigliptin" is not in the topic's intervention vocabulary although the trial is pooled. This is
  a vocabulary gap in `topics/dpp4-mace-t2d.json`; report only.

## How the census was made honest

The first pass reported 32 NO_CLAUSE rows. Every one of them lacked `endpoint_result_span` but carried its quotation in `source`.
The census now reads the quotation with its provenance labels stripped, since a label such as "(RR)" would otherwise pass for a
stated measure. The `basis` field on each row names which it used.
